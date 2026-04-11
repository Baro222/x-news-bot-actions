"""
AI 기반 뉴스 분류 및 처리 모듈 (v3)

개선사항:
1. 한글 번역 강화 (LibreTranslate + 키워드 치환)
2. 참여도 점수 정확화 (좋아요 + 조회수 + 리트윗)
3. 카테고리 자동 분류 (Gemini)
4. 뉴스 요약 및 헤드라인 생성
"""

import json
import logging
import os
import time
import subprocess
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

try:
    from config import OPENAI_API_KEY, MAX_NEWS_PER_CATEGORY, MIN_NEWS_PER_CATEGORY, CATEGORIES
except Exception:
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
    MAX_NEWS_PER_CATEGORY = 10
    MIN_NEWS_PER_CATEGORY = 3
    CATEGORIES = {
        "암호화폐": "crypto",
        "경제": "economy",
        "뉴스": "news",
        "지정학": "geopolitics",
    }


# ─────────────────────────────────────────────
# 번역 함수
# ─────────────────────────────────────────────

EN_KO_KEYWORDS = {
    # 암호화폐
    "bitcoin": "비트코인", "btc": "BTC", "ethereum": "이더리움", "eth": "ETH",
    "crypto": "암호화폐", "blockchain": "블록체인", "solana": "솔라나", "sol": "SOL",
    "xrp": "XRP", "cardano": "카르다노", "ada": "ADA", "dogecoin": "도지코인",
    "doge": "DOGE", "ripple": "리플", "polygon": "폴리곤", "matic": "MATIC",
    "arbitrum": "아비트럼", "optimism": "옵티미즘", "layer 2": "레이어 2",
    "defi": "디파이", "nft": "NFT", "token": "토큰", "coin": "코인",
    "exchange": "거래소", "wallet": "지갑", "mining": "채굴", "staking": "스테이킹",
    "halving": "반감기", "bull run": "강세장", "bear market": "약세장",
    
    # 정치 & 경제
    "trump": "트럼프", "white house": "백악관", "executive order": "행정명령",
    "tariff": "관세", "trade": "무역", "economy": "경제", "inflation": "인플레이션",
    "fed": "연준", "interest rate": "금리", "recession": "경기침체", "gdp": "GDP",
    "stock": "주식", "market": "시장", "unemployment": "실업률", "jobs": "고용",
    "layoff": "해고", "hiring": "채용", "dollar": "달러", "oil": "유가",
    "gold": "금", "silver": "은", "bank": "은행", "debt": "부채",
    "deficit": "적자", "surplus": "흑자", "etf": "ETF", "sec": "증권거래위원회",
    
    # 지정학
    "russia": "러시아", "ukraine": "우크라이나", "china": "중국", "taiwan": "대만",
    "north korea": "북한", "iran": "이란", "israel": "이스라엘", "gaza": "가자",
    "war": "전쟁", "military": "군사", "nato": "나토", "sanctions": "제재",
    "ceasefire": "휴전", "peace": "평화", "nuclear": "핵", "missile": "미사일",
    "conflict": "분쟁", "geopolitics": "지정학", "diplomacy": "외교",
    
    # 일반
    "breaking": "속보", "alert": "경보", "report": "보도", "news": "뉴스",
    "surge": "급등", "plunge": "급락", "crash": "폭락", "rally": "상승",
    "break": "돌파", "resistance": "저항선", "support": "지지선",
    "bull": "강세", "bear": "약세", "volatility": "변동성", "pump": "상승",
    "dump": "하락", "moon": "급등", "rug": "사기", "whale": "고래",
}


def translate_via_libretranslate(text: str, target_lang: str = "ko") -> Optional[str]:
    """LibreTranslate API를 통한 번역"""
    if not text or len(text) < 2:
        return text
    
    # 이미 한국어 포함 시 반환
    if any('\uAC00' <= c <= '\uD7A3' for c in text):
        return text
    
    try:
        url = "https://libretranslate.de/translate"
        payload = {
            "q": text[:500],  # 길이 제한
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
                    logger.debug(f"LibreTranslate 번역 성공")
                    return translated
            except Exception:
                pass
    except Exception:
        pass
    
    return None


def translate_via_keywords(text: str) -> str:
    """키워드 기반 번역"""
    if not text:
        return ""
    
    result = text.lower()
    
    # 정렬된 키워드로 치환 (긴 것부터)
    sorted_keywords = sorted(EN_KO_KEYWORDS.items(), key=lambda x: len(x[0]), reverse=True)
    
    for en, ko in sorted_keywords:
        # 단어 경계 고려
        pattern = r'\b' + re.escape(en) + r'\b'
        result = re.sub(pattern, ko, result, flags=re.IGNORECASE)
    
    return result


def translate_text(text: str) -> str:
    """텍스트 번역 (폴백 체인)"""
    if not text:
        return ""
    
    # 1단계: LibreTranslate 시도
    translated = translate_via_libretranslate(text)
    if translated:
        return translated
    
    # 2단계: 키워드 치환
    translated = translate_via_keywords(text)
    if translated != text.lower():
        return translated
    
    # 3단계: 원본 반환
    return text


# ─────────────────────────────────────────────
# 카테고리 분류
# ─────────────────────────────────────────────

def classify_tweet(text: str, account: str) -> str:
    """트윗 카테고리 분류"""
    text_lower = text.lower()
    
    # 계정 기반 분류
    crypto_keywords = ["bitcoin", "ethereum", "crypto", "blockchain", "btc", "eth", "defi", "nft", "token"]
    economy_keywords = ["trump", "tariff", "trade", "stock", "market", "fed", "interest rate", "inflation"]
    geopolitics_keywords = ["russia", "ukraine", "china", "iran", "war", "military", "nato", "conflict"]
    
    crypto_score = sum(1 for kw in crypto_keywords if kw in text_lower)
    economy_score = sum(1 for kw in economy_keywords if kw in text_lower)
    geo_score = sum(1 for kw in geopolitics_keywords if kw in text_lower)
    
    scores = {
        "암호화폐": crypto_score,
        "경제": economy_score,
        "지정학": geo_score,
    }
    
    # 최고 점수 카테고리 반환
    max_category = max(scores, key=scores.get)
    if scores[max_category] > 0:
        return max_category
    
    # 계정 기반 기본값
    if "crypto" in account.lower() or "coin" in account.lower() or "bitcoin" in account.lower():
        return "암호화폐"
    elif "trump" in account.lower() or "market" in account.lower():
        return "경제"
    else:
        return "뉴스"


def calculate_engagement_score(tweet: Dict) -> float:
    """참여도 점수 계산 (좋아요 + 조회수 + 리트윗)"""
    likes = tweet.get("likeCount", 0) or 0
    views = tweet.get("viewCount", 0) or 0
    retweets = tweet.get("retweetCount", 0) or 0
    replies = tweet.get("replyCount", 0) or 0
    
    # 가중치 적용
    score = (likes * 1.0) + (retweets * 1.5) + (replies * 0.5) + (views * 0.01)
    
    # 정규화 (0-100 범위)
    return min(score / 10, 100)


# ─────────────────────────────────────────────
# 뉴스 처리
# ─────────────────────────────────────────────

def process_tweets(tweets: List[Dict]) -> Dict[str, List[Dict]]:
    """트윗 처리 및 분류"""
    categorized = {}
    
    for tweet in tweets:
        try:
            text = tweet.get("text", "")
            account = tweet.get("_account", "")
            
            # 카테고리 분류
            category = classify_tweet(text, account)
            
            # 번역
            translated_text = translate_text(text)
            
            # 참여도 점수
            engagement_score = calculate_engagement_score(tweet)
            
            # 처리된 트윗
            processed_tweet = {
                **tweet,
                "text": translated_text,
                "_headline": translated_text[:100],
                "_summary": translated_text[:200],
                "_analysis": f"카테고리: {category}, 참여도: {engagement_score:.1f}",
                "_engagement_score": engagement_score,
                "_category": category,
            }
            
            if category not in categorized:
                categorized[category] = []
            categorized[category].append(processed_tweet)
            
        except Exception as e:
            logger.error(f"트윗 처리 오류: {e}")
            continue
    
    return categorized


def rank_and_select_news(categorized: Dict[str, List[Dict]], max_per_category: int = MAX_NEWS_PER_CATEGORY) -> Dict[str, List[Dict]]:
    """카테고리별 뉴스 순위 선정"""
    ranked = {}
    
    for category, tweets in categorized.items():
        # 참여도 점수 기준 정렬
        sorted_tweets = sorted(tweets, key=lambda x: x.get("_engagement_score", 0), reverse=True)
        
        # 상위 N개 선정
        ranked[category] = sorted_tweets[:max_per_category]
    
    return ranked


import re

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # 테스트
    test_tweets = [
        {"text": "Bitcoin surges to new all-time high", "_account": "Cointelegraph", "likeCount": 1000, "viewCount": 50000},
        {"text": "Trump announces new tariff policy", "_account": "zerohedge", "likeCount": 500, "viewCount": 30000},
    ]
    
    processed = process_tweets(test_tweets)
    for category, tweets in processed.items():
        print(f"\n{category}:")
        for tweet in tweets:
            print(f"  - {tweet['_headline']}")
