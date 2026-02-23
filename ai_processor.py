"""
OpenAI GPT를 사용하여 트윗을 분류, 요약, 랭킹 처리하는 모듈
4개 대주제: 지정학, 경제, 트럼프, 암호화폐
"""

import json
import logging
import os
from typing import List, Dict, Optional, Tuple
from openai import OpenAI
from config import OPENAI_API_KEY, MAX_NEWS_PER_CATEGORY, MIN_NEWS_PER_CATEGORY

logger = logging.getLogger(__name__)

# OpenAI 클라이언트 초기화
client = OpenAI(base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"))  # OPENAI_API_KEY 환경변수에서 자동으로 가져옴


CATEGORY_KEYWORDS = {
    "지정학": [
        "war", "conflict", "military", "nato", "russia", "ukraine", "china", "taiwan",
        "north korea", "iran", "israel", "gaza", "sanctions", "geopolitical", "troops",
        "missile", "nuclear", "diplomacy", "alliance", "invasion", "territory",
        "전쟁", "분쟁", "군사", "러시아", "우크라이나", "중국", "대만", "북한", "이란", "이스라엘",
        "제재", "지정학", "외교", "동맹", "침공", "영토", "나토"
    ],
    "경제": [
        "economy", "gdp", "inflation", "fed", "interest rate", "recession", "market",
        "stock", "bond", "dollar", "trade", "tariff", "deficit", "unemployment",
        "jobs", "cpi", "ppi", "housing", "mortgage", "bank", "financial", "fiscal",
        "경제", "금리", "인플레이션", "연준", "경기침체", "시장", "주식", "채권", "달러",
        "무역", "관세", "적자", "실업", "고용", "주택", "은행", "재정"
    ],
    "트럼프": [
        "trump", "maga", "white house", "executive order", "administration",
        "doge", "elon musk", "republican", "democrat", "congress", "senate",
        "트럼프", "백악관", "행정명령", "공화당", "민주당", "의회", "상원"
    ],
    "암호화폐": [
        "bitcoin", "btc", "ethereum", "eth", "crypto", "blockchain", "defi",
        "nft", "altcoin", "binance", "coinbase", "solana", "xrp", "ripple",
        "stablecoin", "usdt", "usdc", "web3", "token", "mining", "halving",
        "비트코인", "이더리움", "암호화폐", "블록체인", "디파이", "솔라나", "토큰"
    ]
}


def classify_tweet_simple(tweet_text: str) -> Optional[str]:
    """키워드 기반으로 트윗을 빠르게 분류합니다."""
    text_lower = tweet_text.lower()
    
    scores = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw.lower() in text_lower)
        if score > 0:
            scores[category] = score
    
    if not scores:
        return None
    
    return max(scores, key=scores.get)


def classify_and_summarize_batch(tweets: List[Dict]) -> List[Dict]:
    """GPT를 사용하여 트윗 배치를 분류하고 요약합니다."""
    if not tweets:
        return []
    
    # 트윗 텍스트 준비 (최대 50개씩 처리)
    batch_size = 30
    results = []
    
    for i in range(0, len(tweets), batch_size):
        batch = tweets[i:i+batch_size]
        batch_results = _process_batch(batch)
        results.extend(batch_results)
    
    return results


def _process_batch(tweets: List[Dict]) -> List[Dict]:
    """트윗 배치를 GPT로 처리합니다."""
    
    # 트윗 목록 준비
    tweet_list = []
    for idx, tweet in enumerate(tweets):
        text = tweet.get("text", "")
        account = tweet.get("_account", "unknown")
        engagement = tweet.get("_engagement_score", 0)
        url = tweet.get("_url", "")
        tweet_list.append(f"[{idx}] @{account} (참여도:{engagement:.0f})\n{text}\nURL: {url}")
    
    tweets_text = "\n\n---\n\n".join(tweet_list)
    
    prompt = f"""다음 트윗들을 분석하여 각각을 분류하고 요약해주세요.

분류 기준:
- 지정학: 전쟁, 분쟁, 군사, 외교, 국제관계, 지역갈등 등
- 경제: 경제지표, 금융시장, 무역, 통화정책, 기업실적 등
- 트럼프: 트럼프 관련 정책, 발언, 행정부 소식 등
- 암호화폐: 비트코인, 이더리움, 크립토 시장, 블록체인 등
- 기타: 위 4가지에 해당하지 않는 경우

각 트윗에 대해 다음 JSON 형식으로 응답하세요:
{{
  "results": [
    {{
      "index": 0,
      "category": "경제",
      "headline": "헤드라인 (20자 이내, 명사형으로 끝내기)",
      "summary": "핵심 내용 요약 (2-3문장, 명사형으로 끝내기)",
      "analysis": "간단한 배경/원인 분석 (1-2문장, 명사형으로 끝내기)",
      "importance": 1~10 (중요도 점수)
    }}
  ]
}}

중요 규칙:
1. 헤드라인과 요약은 반드시 명사형으로 끝내야 합니다 (예: "~비판", "~발표", "~확대", "~하락")
2. "했습니다", "합니다", "됩니다" 등 서술형 종결어미 사용 금지
3. 영어 트윗은 한국어로 번역하여 요약
4. 중요도는 파급력, 시장 영향, 사회적 관심도를 기준으로 평가

트윗 목록:
{tweets_text}"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "당신은 글로벌 뉴스와 금융 시장을 전문적으로 분석하는 뉴스 큐레이터입니다."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
            max_tokens=4000
        )
        
        result_text = response.choices[0].message.content
        result_data = json.loads(result_text)
        ai_results = result_data.get("results", [])
        
        # 원본 트윗 데이터와 AI 결과 합치기
        processed_tweets = []
        for ai_result in ai_results:
            idx = ai_result.get("index", -1)
            if 0 <= idx < len(tweets):
                tweet = tweets[idx].copy()
                tweet["_category"] = ai_result.get("category", "기타")
                tweet["_headline"] = ai_result.get("headline", "")
                tweet["_summary"] = ai_result.get("summary", "")
                tweet["_analysis"] = ai_result.get("analysis", "")
                tweet["_importance"] = ai_result.get("importance", 5)
                processed_tweets.append(tweet)
        
        return processed_tweets
        
    except Exception as e:
        logger.error(f"GPT 처리 오류: {e}")
        # 폴백: 키워드 기반 분류
        fallback_results = []
        for tweet in tweets:
            text = tweet.get("text", "")
            category = classify_tweet_simple(text) or "기타"
            tweet_copy = tweet.copy()
            tweet_copy["_category"] = category
            tweet_copy["_headline"] = text[:50] + "..."
            tweet_copy["_summary"] = text[:200]
            tweet_copy["_analysis"] = ""
            tweet_copy["_importance"] = 5
            fallback_results.append(tweet_copy)
        return fallback_results


def extract_keywords_from_text(text: str) -> List[str]:
    """텍스트에서 의미있는 키워드를 추출합니다."""
    import re
    # 소문자 변환 후 단어 추출 (2글자 이상)
    words = re.findall(r'[a-zA-Z가-힣]{2,}', text.lower())
    # 불용어 제거
    stopwords = {
        'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
        'should', 'may', 'might', 'shall', 'can', 'need', 'dare', 'ought',
        'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by', 'from', 'as',
        'into', 'through', 'during', 'before', 'after', 'above', 'below',
        'between', 'out', 'off', 'over', 'under', 'again', 'then', 'once',
        'and', 'but', 'or', 'nor', 'so', 'yet', 'both', 'either', 'neither',
        'not', 'no', 'only', 'own', 'same', 'than', 'too', 'very', 'just',
        'that', 'this', 'these', 'those', 'it', 'its', 'he', 'she', 'they',
        'we', 'you', 'i', 'my', 'your', 'his', 'her', 'our', 'their',
        'what', 'which', 'who', 'whom', 'when', 'where', 'why', 'how',
        'all', 'each', 'every', 'few', 'more', 'most', 'other', 'some',
        'such', 'up', 'if', 'about', 'also', 'new', 'now', 'said', 'say',
        '이', '그', '저', '것', '수', '등', '및', '또', '더', '이런', '그런',
        '하는', '있는', '없는', '된', '한', '에서', '으로', '에게', '에', '을', '를',
    }
    return [w for w in words if w not in stopwords and len(w) >= 2]


def calculate_keyword_overlap_score(tweet: Dict, all_tweets_in_category: List[Dict]) -> float:
    """같은 카테고리 내 다른 트윗들과의 키워드 중복도 점수를 계산합니다.
    
    많은 계정이 동시에 언급하는 키워드일수록 높은 점수를 부여합니다.
    """
    tweet_text = tweet.get('text', '') + ' ' + tweet.get('_headline', '') + ' ' + tweet.get('_summary', '')
    tweet_keywords = set(extract_keywords_from_text(tweet_text))
    
    if not tweet_keywords:
        return 0.0
    
    overlap_score = 0.0
    for other_tweet in all_tweets_in_category:
        if other_tweet is tweet:
            continue
        other_text = other_tweet.get('text', '') + ' ' + other_tweet.get('_headline', '') + ' ' + other_tweet.get('_summary', '')
        other_keywords = set(extract_keywords_from_text(other_text))
        
        if not other_keywords:
            continue
        
        # Jaccard 유사도 기반 중복도
        intersection = tweet_keywords & other_keywords
        union = tweet_keywords | other_keywords
        if union:
            jaccard = len(intersection) / len(union)
            # 중복 키워드 수에 비례한 가중치
            overlap_score += jaccard * len(intersection)
    
    return overlap_score


def rank_and_filter_by_category(processed_tweets: List[Dict]) -> Dict[str, List[Dict]]:
    """카테고리별로 트윗을 랭킹하고 필터링합니다.
    
    랭킹 기준 (우선순위):
    1. 키워드 중복도: 여러 계정이 동시에 언급하는 주제일수록 높은 점수
    2. AI 중요도: GPT가 평가한 뉴스 중요도 (1~10)
    3. 최신성: 최근에 올라온 포스팅일수록 높은 점수
    4. 참여도: 좋아요/리트윗 등 (Nitter RSS에서는 0이므로 보조 지표)
    """
    from datetime import datetime, timezone
    
    # 카테고리별 분류
    categorized = {
        "지정학": [],
        "경제": [],
        "트럼프": [],
        "암호화폐": [],
    }
    
    for tweet in processed_tweets:
        category = tweet.get("_category", "기타")
        if category in categorized:
            categorized[category].append(tweet)
    
    # 각 카테고리별 랭킹
    ranked = {}
    for category, tweets in categorized.items():
        if not tweets:
            ranked[category] = []
            continue
        
        now_utc = datetime.now(timezone.utc)
        
        for tweet in tweets:
            importance = tweet.get("_importance", 5)
            engagement = tweet.get("_engagement_score", 0)
            
            # 1. 키워드 중복도 점수 (0~50점) - 가장 중요한 지표
            keyword_score = calculate_keyword_overlap_score(tweet, tweets)
            keyword_score_normalized = min(keyword_score * 5, 50)
            
            # 2. AI 중요도 점수 (0~40점)
            importance_score = importance * 4
            
            # 3. 최신성 점수 (0~20점) - 최근일수록 높음
            age_hours = tweet.get("_age_hours", 4.0)
            recency_score = max(0, 20 - (age_hours / 4.0) * 20)  # 4시간 기준 선형 감소
            
            # 4. 참여도 점수 (0~10점, 보조 지표)
            engagement_score = min(engagement / 100, 10)
            
            # 최종 복합 점수
            tweet["_final_score"] = (
                keyword_score_normalized +
                importance_score +
                recency_score +
                engagement_score
            )
            tweet["_keyword_score"] = keyword_score_normalized
            tweet["_recency_score"] = recency_score
        
        # 점수 내림차순 정렬
        sorted_tweets = sorted(tweets, key=lambda x: x.get("_final_score", 0), reverse=True)
        
        # 5~10개로 제한
        ranked[category] = sorted_tweets[:MAX_NEWS_PER_CATEGORY]
        
        # 랭킹 상위 항목 로그
        logger.info(f"  [{category}] TOP {len(ranked[category])}개 선정:")
        for i, t in enumerate(ranked[category][:3], 1):
            logger.info(
                f"    {i}. [{t.get('_final_score',0):.1f}점] "
                f"키워드:{t.get('_keyword_score',0):.1f} "
                f"중요도:{t.get('_importance',0)*4:.0f} "
                f"최신:{t.get('_recency_score',0):.1f} | "
                f"{t.get('_headline','')[:40]}"
            )
    
    return ranked


def process_tweets(tweets: List[Dict]) -> Dict[str, List[Dict]]:
    """트윗 전체 처리 파이프라인: 분류 -> 요약 -> 랭킹"""
    logger.info(f"총 {len(tweets)}개 트윗 AI 처리 시작...")
    
    # 기타 카테고리 제외하고 관련 트윗만 처리
    # 먼저 키워드로 빠르게 필터링
    relevant_tweets = []
    for tweet in tweets:
        text = tweet.get("text", "")
        category = classify_tweet_simple(text)
        if category:
            tweet["_pre_category"] = category
            relevant_tweets.append(tweet)
        else:
            # 키워드 없어도 GPT에게 판단 맡김
            tweet["_pre_category"] = "미분류"
            relevant_tweets.append(tweet)
    
    logger.info(f"AI 분류·요약 처리 중... ({len(relevant_tweets)}개)")
    
    # GPT로 분류 및 요약
    processed = classify_and_summarize_batch(relevant_tweets)
    
    # 기타 제외하고 4개 카테고리만 필터링
    filtered = [t for t in processed if t.get("_category") in ["지정학", "경제", "트럼프", "암호화폐"]]
    
    logger.info(f"분류 완료: {len(filtered)}개 (기타 제외)")
    
    # 카테고리별 랭킹
    ranked = rank_and_filter_by_category(filtered)
    
    # 결과 요약 로그
    for cat, items in ranked.items():
        logger.info(f"  {cat}: {len(items)}개")
    
    return ranked


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # 테스트 데이터
    test_tweets = [
        {
            "text": "US housing market activity has rarely been weaker: The US Pending Home Sales Index fell -0.8% MoM in January, to 70.9, an all-time low.",
            "_account": "KobeissiLetter",
            "_engagement_score": 2913,
            "_url": "https://x.com/KobeissiLetter/status/123"
        },
        {
            "text": "Bitcoin surges past $100,000 as institutional demand continues to grow. ETF inflows hit record levels.",
            "_account": "CoinTelegraph",
            "_engagement_score": 1500,
            "_url": "https://x.com/CoinTelegraph/status/456"
        },
        {
            "text": "Trump signs executive order on immigration, expanding border enforcement measures significantly.",
            "_account": "FoxNews",
            "_engagement_score": 3000,
            "_url": "https://x.com/FoxNews/status/789"
        },
        {
            "text": "Russia launches major offensive in eastern Ukraine, NATO allies call emergency meeting.",
            "_account": "Reuters",
            "_engagement_score": 5000,
            "_url": "https://x.com/Reuters/status/101"
        }
    ]
    
    print("AI 처리 테스트 시작...")
    result = process_tweets(test_tweets)
    
    for category, items in result.items():
        print(f"\n=== {category} ({len(items)}개) ===")
        for i, item in enumerate(items, 1):
            print(f"{i}. {item.get('_headline', 'N/A')}")
            print(f"   요약: {item.get('_summary', 'N/A')[:100]}")
            print(f"   분석: {item.get('_analysis', 'N/A')[:80]}")
            print(f"   링크: {item.get('_url', 'N/A')}")
