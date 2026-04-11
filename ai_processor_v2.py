"""
AI 기반 뉴스 분류 및 처리 모듈 (v2)

개선사항:
1. LibreTranslate API 추가 (Gemini 404 에러 우회)
2. 번역 폴백 체인: Gemini → LibreTranslate → 키워드 치환
3. 좋아요/조회수 기반 우선순위 계산
4. 한글 출력 강화
"""

import json
import logging
import os
import time
import subprocess
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

# config에서 상수 import
try:
    from config import OPENAI_API_KEY, MAX_NEWS_PER_CATEGORY, MIN_NEWS_PER_CATEGORY
except Exception:
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
    MAX_NEWS_PER_CATEGORY = 10
    MIN_NEWS_PER_CATEGORY = 5


# ─────────────────────────────────────────────
# 번역 함수 (LibreTranslate)
# ─────────────────────────────────────────────

def translate_via_libretranslate(text: str, target_lang: str = "ko") -> Optional[str]:
    """LibreTranslate API를 통한 번역"""
    if not text or len(text) < 2:
        return text
    
    # 이미 한국어가 포함된 경우 그대로 반환
    if any('\uAC00' <= c <= '\uD7A3' for c in text):
        return text
    
    try:
        # LibreTranslate 공개 API 사용
        url = "https://libretranslate.de/translate"
        payload = {
            "q": text,
            "source": "en",
            "target": target_lang
        }
        
        cmd = ["curl", "-s", "--max-time", "10", "-X", "POST", url,
               "-H", "Content-Type: application/json",
               "-d", json.dumps(payload)]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0 and result.stdout:
            try:
                response = json.loads(result.stdout)
                translated = response.get("translatedText", "")
                if translated:
                    logger.debug(f"LibreTranslate 번역 성공: {text[:50]} → {translated[:50]}")
                    return translated
            except Exception as e:
                logger.debug(f"LibreTranslate 응답 파싱 오류: {e}")
    except Exception as e:
        logger.debug(f"LibreTranslate 번역 실패: {e}")
    
    return None


# ─────────────────────────────────────────────
# 키워드 기반 번역 (폴백)
# ─────────────────────────────────────────────

EN_KO_KEYWORDS = {
    "bitcoin": "비트코인", "btc": "BTC", "ethereum": "이더리움", "eth": "ETH",
    "crypto": "암호화폐", "blockchain": "블록체인", "solana": "솔라나",
    "trump": "트럼프", "white house": "백악관", "executive order": "행정명령",
    "tariff": "관세", "trade": "무역", "economy": "경제", "inflation": "인플레이션",
    "fed": "연준", "interest rate": "금리", "recession": "경기침체",
    "stock": "주식", "market": "시장", "gdp": "GDP", "unemployment": "실업률",
    "russia": "러시아", "ukraine": "우크라이나", "china": "중국", "taiwan": "대만",
    "north korea": "북한", "iran": "이란", "israel": "이스라엘", "gaza": "가자",
    "war": "전쟁", "military": "군사", "nato": "나토", "sanctions": "제재",
    "ceasefire": "휴전", "peace": "평화", "nuclear": "핵",
    "dollar": "달러", "oil": "유가", "gold": "금", "silver": "은",
    "bank": "은행", "debt": "부채", "deficit": "적자", "surplus": "흑자",
    "jobs": "고용", "layoff": "해고", "hiring": "채용",
    "etf": "ETF", "spot": "현물", "sec": "증권거래위원회",
    "rally": "상승", "surge": "급등", "plunge": "급락", "crash": "폭락",
    "break": "돌파", "resistance": "저항선", "support": "지지선",
    "bull": "강세", "bear": "약세", "volatility": "변동성",
}


def translate_via_keywords(text: str) -> str:
    """키워드 기반 간단한 번역"""
    if not text:
        return ""
    
    # 이미 한국어가 포함된 경우 그대로 반환
    if any('\uAC00' <= c <= '\uD7A3' for c in text):
        return text
    
    result = text
    for en, ko in EN_KO_KEYWORDS.items():
        # 대소문자 구분 없이 치환
        result = result.replace(en.upper(), ko)
        result = result.replace(en.capitalize(), ko)
        result = result.replace(en, ko)
    
    return result


def translate_text(text: str) -> str:
    """
    텍스트 번역 (우선순위: LibreTranslate → 키워드 치환)
    """
    if not text or len(text) < 2:
        return text
    
    # 이미 한국어면 그대로 반환
    if any('\uAC00' <= c <= '\uD7A3' for c in text):
        return text
    
    # 1. LibreTranslate 시도
    translated = translate_via_libretranslate(text)
    if translated:
        return translated
    
    # 2. 키워드 기반 폴백
    return translate_via_keywords(text)


# ─────────────────────────────────────────────
# 분류 및 랭킹
# ─────────────────────────────────────────────

CATEGORY_KEYWORDS = {
    "지정학": [
        "war", "conflict", "military", "nato", "russia", "ukraine", "china", "taiwan",
        "north korea", "iran", "israel", "gaza", "sanctions", "geopolitical", "troops",
        "missile", "nuclear", "diplomacy", "alliance", "invasion", "territory",
        "전쟁", "분쟁", "군사", "러시아", "우크라이나", "중국", "대만", "북한", "이란", "이스라엘",
        "제재", "지정학", "외교", "동맹", "침공", "영토", "나토", "ceasefire", "peace talks",
    ],
    "경제": [
        "economy", "gdp", "inflation", "fed", "interest rate", "recession", "market",
        "stock", "bond", "dollar", "trade", "tariff", "deficit", "unemployment",
        "jobs", "cpi", "ppi", "housing", "mortgage", "bank", "financial", "fiscal",
        "경제", "금리", "인플레이션", "연준", "경기침체", "시장", "주식", "채권", "달러",
        "무역", "관세", "적자", "실업", "고용", "주택", "은행", "재정", "earnings", "revenue",
        "profit", "loss", "ipo", "acquisition", "merger", "layoff", "hiring"
    ],
    "트럼프": [
        "trump", "maga", "white house", "executive order", "administration",
        "doge", "elon musk", "republican", "democrat", "congress", "senate",
        "트럼프", "백악관", "행정명령", "공화당", "민주당", "의회", "상원",
        "oval office", "mar-a-lago", "tariff", "immigration", "border", "deportation",
        "vance", "rubio", "bessent", "lutnick"
    ],
    "암호화폐": [
        "bitcoin", "btc", "ethereum", "eth", "crypto", "blockchain", "defi",
        "nft", "altcoin", "binance", "coinbase", "solana", "xrp", "ripple",
        "stablecoin", "usdt", "usdc", "web3", "token", "mining", "halving",
        "비트코인", "이더리움", "암호화폐", "블록체인", "디파이", "솔라나", "토큰",
        "dogecoin", "doge", "shib", "bnb", "avax", "polygon", "matic",
        "etf", "spot etf", "sec crypto", "crypto regulation"
    ]
}


def classify_tweet_simple(tweet_text: str) -> Optional[str]:
    """키워드 기반으로 트윗을 분류합니다."""
    text_lower = tweet_text.lower()
    scores = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw.lower() in text_lower)
        if score > 0:
            scores[category] = score
    
    if not scores:
        return None
    
    return max(scores.items(), key=lambda x: x[1])[0]


def calculate_engagement_score(tweet: Dict) -> float:
    """좋아요/조회수 기반 참여도 점수 계산"""
    likes = float(tweet.get("likeCount", 0))
    views = float(tweet.get("viewCount", 0))
    
    # 가중치: 조회수 70%, 좋아요 30%
    score = (likes * 0.3 + views * 0.7) / 1000
    
    return max(0, score)


def rank_news_by_engagement(tweets: List[Dict]) -> List[Dict]:
    """좋아요/조회수 기반으로 뉴스를 정렬"""
    for tweet in tweets:
        tweet["_engagement_score"] = calculate_engagement_score(tweet)
    
    return sorted(tweets, key=lambda x: x.get("_engagement_score", 0), reverse=True)


def process_tweets(tweets: List[Dict]) -> List[Dict]:
    """
    트윗 처리 (분류 + 번역 + 랭킹)
    
    1. 각 트윗 분류
    2. 헤드라인/요약 번역
    3. 참여도 점수 계산
    4. 정렬
    """
    processed = []
    
    for tweet in tweets:
        text = tweet.get("text", "")
        
        # 1. 분류
        category = classify_tweet_simple(text) or "기타"
        
        # 2. 헤드라인 (영어면 번역)
        headline = text.strip().replace('\n', ' ')[:100]
        headline_ko = translate_text(headline)
        
        # 3. 요약 (원문 앞부분 + 번역)
        summary = text.strip().replace('\n', ' ')[:200]
        summary_ko = translate_text(summary)
        
        # 4. 분석 (간단한 분석)
        analysis = f"X (@{tweet.get('_account', 'unknown')})에서 공유된 주요 소식"
        
        # 5. 참여도 점수
        engagement_score = calculate_engagement_score(tweet)
        
        processed_tweet = tweet.copy()
        processed_tweet.update({
            "_category": category,
            "_headline": headline_ko,
            "_summary": summary_ko,
            "_analysis": analysis,
            "_engagement_score": engagement_score,
            "_importance": min(10, max(1, int(engagement_score / 1000 * 10)))
        })
        
        processed.append(processed_tweet)
    
    return processed


def rank_and_select_news(processed_tweets: List[Dict], max_per_category: int = 10) -> Dict[str, List[Dict]]:
    """
    카테고리별로 뉴스를 정렬하고 상위 N개 선정
    """
    ranked_by_category = {}
    
    for category in ["지정학", "경제", "트럼프", "암호화폐"]:
        category_tweets = [t for t in processed_tweets if t.get("_category") == category]
        
        # 참여도 점수로 정렬
        sorted_tweets = sorted(
            category_tweets,
            key=lambda x: x.get("_engagement_score", 0),
            reverse=True
        )
        
        # 상위 N개 선정
        ranked_by_category[category] = sorted_tweets[:max_per_category]
    
    return ranked_by_category


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')
    
    # 테스트
    test_tweets = [
        {
            "text": "Bitcoin surges to $95,000 as institutional investors increase holdings",
            "_account": "CoinTelegraph",
            "likeCount": 5000,
            "viewCount": 50000
        },
        {
            "text": "Trump announces new tariff policy on Chinese imports",
            "_account": "TrumpTruthOnX",
            "likeCount": 3000,
            "viewCount": 30000
        },
        {
            "text": "Russia and Ukraine peace talks resume with US mediation",
            "_account": "Reuters",
            "likeCount": 2000,
            "viewCount": 20000
        }
    ]
    
    print("테스트 처리 시작...")
    processed = process_tweets(test_tweets)
    for p in processed:
        print(f"\n분류: {p['_category']}")
        print(f"헤드라인: {p['_headline']}")
        print(f"요약: {p['_summary']}")
        print(f"참여도: {p['_engagement_score']:.2f}")
