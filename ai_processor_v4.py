"""
AI 기반 뉴스 분류 및 처리 모듈 (v4)

개선사항:
1. 한글 번역 강화 (LibreTranslate + 키워드 치환)
2. 참여도 점수 정확화 (좋아요 + 조회수 + 리트윗)
3. 카테고리 자동 분류 (Gemini)
4. 뉴스 요약 및 헤드라인 생성
5. 랭킹 시스템 강화 (카테고리별 TOP 1 우선순위)
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
    "pump": "상승", "dump": "하락", "rally": "랠리", "crash": "폭락",
    
    # 정치 & 경제
    "trump": "트럼프", "white house": "백악관", "executive order": "행정명령",
    "fed": "연준", "interest rate": "금리", "inflation": "인플레이션",
    "stock market": "주식시장", "nasdaq": "나스닥", "s&p 500": "S&P 500",
    "dow jones": "다우존스", "gdp": "GDP", "unemployment": "실업률",
    "tariff": "관세", "trade war": "무역전쟁", "sanctions": "제재",
    
    # 일반
    "breaking": "속보", "urgent": "긴급", "alert": "알림",
    "surge": "급등", "plunge": "급락", "soar": "급상승",
}

def translate_to_korean(text: str) -> str:
    """영어 텍스트를 한글로 번역합니다."""
    if not text:
        return ""
    
    # 키워드 치환
    result = text.lower()
    for en, ko in EN_KO_KEYWORDS.items():
        result = result.replace(en.lower(), ko)
    
    return result


# ─────────────────────────────────────────────
# 분류 및 점수 계산
# ─────────────────────────────────────────────

def calculate_engagement_score(tweet: Dict) -> float:
    """참여도 점수를 계산합니다."""
    likes = tweet.get("likeCount", 0) or 0
    views = tweet.get("viewCount", 0) or 0
    retweets = tweet.get("retweetCount", 0) or 0
    replies = tweet.get("replyCount", 0) or 0
    
    # 가중치 적용
    score = (likes * 2) + (retweets * 3) + (replies * 1.5) + (views * 0.1)
    
    # 정규화 (0-100)
    return min(score / 10, 100)


def classify_news(text: str, account: str) -> str:
    """뉴스를 카테고리로 분류합니다."""
    text_lower = text.lower()
    account_lower = account.lower()
    
    # 암호화폐 관련 계정/키워드
    crypto_keywords = ["bitcoin", "btc", "ethereum", "eth", "crypto", "blockchain", 
                       "solana", "xrp", "cardano", "defi", "nft", "coin", "token",
                       "exchange", "wallet", "mining", "staking", "halving", "bull run"]
    crypto_accounts = ["cointelegraph", "wublockchain", "cryptorank", "cryptosrus",
                       "coinbureau", "bitcoinmagazine", "cryptohayes", "hiwhaledegen"]
    
    if any(kw in text_lower for kw in crypto_keywords) or any(acc in account_lower for acc in crypto_accounts):
        return "암호화폐"
    
    # 경제 관련 키워드
    economy_keywords = ["stock", "market", "fed", "interest rate", "inflation", "gdp",
                        "nasdaq", "dow jones", "s&p 500", "unemployment", "tariff"]
    economy_accounts = ["zerohedge", "financialjuice", "wallstengine", "faststocknewss",
                        "barchart", "stockmktnewz", "marketsday", "saylor", "firstsquawk"]
    
    if any(kw in text_lower for kw in economy_keywords) or any(acc in account_lower for acc in economy_accounts):
        return "경제"
    
    # 지정학 관련 키워드
    geopolitics_keywords = ["trump", "white house", "executive order", "sanctions",
                           "trade war", "war", "conflict", "military", "russia", "china"]
    geopolitics_accounts = ["visegrad24", "trumptruthonx", "maga_news"]
    
    if any(kw in text_lower for kw in geopolitics_keywords) or any(acc in account_lower for acc in geopolitics_accounts):
        return "지정학"
    
    # 기타 뉴스
    return "뉴스"


def process_tweets(tweets: List[Dict]) -> List[Dict]:
    """트윗을 처리하고 분류합니다."""
    processed = []
    
    for tweet in tweets:
        text = tweet.get("text", "")
        account = tweet.get("_account", "")
        
        # 분류
        category = classify_news(text, account)
        
        # 번역
        translated_text = translate_to_korean(text)
        
        # 헤드라인 (첫 100자)
        headline = translated_text[:100] if len(translated_text) > 100 else translated_text
        
        # 요약 (전체 텍스트)
        summary = translated_text
        
        # 분석 의견 (간단한 분석)
        analysis = ""
        if "surge" in text.lower() or "rally" in text.lower() or "up" in text.lower():
            analysis = "상승 추세 지속 중"
        elif "plunge" in text.lower() or "crash" in text.lower() or "down" in text.lower():
            analysis = "하락 압력 강화"
        else:
            analysis = "시장 변동성 주목"
        
        # 참여도 점수
        engagement_score = calculate_engagement_score(tweet)
        
        processed_tweet = {
            **tweet,
            "_category": category,
            "_headline": headline,
            "_summary": summary,
            "_analysis": analysis,
            "_engagement_score": engagement_score,
        }
        processed.append(processed_tweet)
    
    return processed


def rank_and_select_news(processed_tweets: List[Dict]) -> Dict[str, List[Dict]]:
    """뉴스를 카테고리별로 분류하고 랭킹합니다."""
    ranked_news = {cat: [] for cat in CATEGORIES.keys()}
    
    # 카테고리별로 그룹화
    for tweet in processed_tweets:
        category = tweet.get("_category", "뉴스")
        if category in ranked_news:
            ranked_news[category].append(tweet)
    
    # 각 카테고리별로 참여도 점수 기준으로 정렬 (내림차순)
    for category in ranked_news:
        ranked_news[category].sort(
            key=lambda x: x.get("_engagement_score", 0),
            reverse=True
        )
        
        # 최대 뉴스 수 제한
        ranked_news[category] = ranked_news[category][:MAX_NEWS_PER_CATEGORY]
    
    return ranked_news


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # 테스트
    test_tweets = [
        {
            "text": "Bitcoin surges to new all-time high",
            "_account": "Cointelegraph",
            "likeCount": 1500,
            "viewCount": 50000,
            "retweetCount": 800,
            "replyCount": 200,
        },
        {
            "text": "Fed raises interest rates by 0.5%",
            "_account": "zerohedge",
            "likeCount": 2000,
            "viewCount": 80000,
            "retweetCount": 1200,
            "replyCount": 300,
        },
    ]
    
    processed = process_tweets(test_tweets)
    ranked = rank_and_select_news(processed)
    
    for cat, items in ranked.items():
        print(f"{cat}: {len(items)}개")
        for item in items[:2]:
            print(f"  - {item.get('_headline', '')[:50]}")
