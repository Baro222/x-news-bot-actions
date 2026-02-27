"""
Google Gemini API를 사용하여 트윗을 분류, 요약, 랭킹 처리하는 모듈
4개 대주제: 지정학, 경제, 트럼프, 암호화폐
2중 한국어 강제 로직 포함: AI 응답 후 영어 비중 검사 및 재번역
"""

import json
import logging
import os
import requests
from typing import List, Dict, Optional, Tuple
from config import OPENAI_API_KEY, MAX_NEWS_PER_CATEGORY, MIN_NEWS_PER_CATEGORY

logger = logging.getLogger(__name__)

# Gemini API 설정
GEMINI_API_KEY = os.getenv("OPENAI_API_KEY")  # 기존 환경변수 이름을 그대로 사용 (GitHub Secrets 호환성)
GEMINI_MODEL = "gemini-2.5-flash"
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"


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


def is_korean_text(text: str) -> bool:
    """텍스트가 한국어인지 확인합니다."""
    korean_count = sum(1 for c in text if ord(c) >= 0xAC00 and ord(c) <= 0xD7A3)
    english_count = sum(1 for c in text if c.isalpha() and ord(c) < 128)
    
    # 한국어가 30% 이상이면 한국어로 간주
    total_chars = korean_count + english_count
    if total_chars == 0:
        return True
    
    return korean_count / total_chars >= 0.3


def translate_to_korean_if_needed(text: str) -> str:
    """영어 비중이 높으면 한국어로 재번역합니다 (2중 방어)."""
    if is_korean_text(text):
        return text
    
    # 영어가 많으면 재번역 요청
    logger.warning(f"영어 비중이 높은 텍스트 감지, 한국어 재번역 시도: {text[:100]}")
    
    try:
        # Gemini를 사용한 긴급 재번역
        prompt = f"""다음 텍스트를 한국어로 번역하세요. 반드시 한국어로만 응답하세요:

{text}

한국어 번역:"""
        
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "systemInstruction": {
                "parts": [{
                    "text": "당신은 전문 번역가입니다. 모든 응답은 100% 한국어로만 작성하세요. 영어나 다른 외국어를 절대 사용하면 안 됩니다."
                }]
            },
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 2000
            }
        }
        
        response = requests.post(GEMINI_API_URL, json=payload, timeout=30)
        response.raise_for_status()
        
        result_data = response.json()
        translated = result_data['candidates'][0]['content']['parts'][0]['text'].strip()
        logger.info(f"재번역 완료: {translated[:100]}")
        return translated
        
    except Exception as e:
        logger.error(f"재번역 실패: {e}, 원본 텍스트 반환")
        return text


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
    """Gemini를 사용하여 트윗 배치를 분류하고 요약합니다."""
    if not tweets:
        return []
    
    # 트윗 텍스트 준비 (최대 30개씩 처리)
    batch_size = 30
    results = []
    
    for i in range(0, len(tweets), batch_size):
        batch = tweets[i:i+batch_size]
        batch_results = _process_batch(batch)
        results.extend(batch_results)
    
    return results


def _process_batch(tweets: List[Dict]) -> List[Dict]:
    """트윗 배치를 Gemini로 처리합니다."""
    
    # 트윗 목록 준비
    tweet_list = []
    for idx, tweet in enumerate(tweets):
        text = tweet.get("text", "")
        account = tweet.get("_account", "unknown")
        engagement = tweet.get("_engagement_score", 0)
        url = tweet.get("_url", "")
        tweet_list.append(f"[{idx}] @{account} (참여도:{engagement:.0f})\n{text}\nURL: {url}")
    
    tweets_text = "\n\n---\n\n".join(tweet_list)
    
    # ★★★ 극단적 한국어 강제 프롬프트 ★★★
    prompt = f"""당신은 글로벌 금융, 암호화폐, 정치 시장 분석 전문가입니다. 다음 트윗들을 심층 분석하여 각각을 분류하고 요약해주세요.

★★★ 절대 준수 규칙 (CRITICAL - 이 규칙을 어기면 안 됩니다) ★★★
1. 모든 응답은 반드시 100% 한국어로만 작성되어야 합니다.
2. 어떠한 경우에도 영어, 중국어, 일본어, 기타 외국어를 사용하면 안 됩니다.
3. 영어 트윗이 입력되면 반드시 한국어로 번역한 후 분석하세요.
4. JSON 필드의 모든 값(value)도 100% 한국어여야 합니다.
5. 번역되지 않은 영어 단어나 문장이 있으면 절대 안 됩니다.
6. 회사명, 인물명, 기술용어도 한국어로 표기하세요 (예: 비트코인, 이더리움, 연준, 나스닥).
7. 응답에 영어가 1글자라도 포함되면 실패입니다.

분류 기준:
- 지정학: 전쟁, 분쟁, 군사, 외교, 국제관계, 지역갈등, 제재, 동맹 등
- 경제: 경제지표, 금융시장, 무역, 통화정책, 기업실적, 인플레이션, 금리, 주식시장 등
- 트럼프: 트럼프 정책, 발언, 행정부 소식, 대선 관련 뉴스 등
- 암호화폐: 비트코인, 이더리움, 크립토 시장, 블록체인, 규제, 거래소 뉴스 등

각 트윗에 대해 다음 JSON 형식으로 응답하세요 (모든 값은 한국어):
{{
  "results": [
    {{
      "index": 0,
      "category": "암호화폐",
      "headline": "비트코인 사상 최고가 돌파 (15-20자, 명사형으로 끝내기)",
      "summary": "비트코인이 사상 최고가를 경신했으며, 기관투자자들의 수요 증가가 주요 요인. 이더리움 등 주요 알트코인도 동반 상승 추세 보임.",
      "analysis": "연방준비제도의 금리 인하 신호와 인플레이션 완화 기대감이 암호화폐 시장에 긍정적 영향. 기관투자자들의 진입 확대로 시장 구조 변화 가속화.",
      "importance": 9,
      "market_impact": "암호화폐 전체 시장에 강한 긍정 신호. 기관투자자 진입 가속화 예상"
    }}
  ]
}}

응답 작성 규칙:
1. 헤드라인: 15-20자, 명사형으로 끝내기 (예: "~상승", "~발표", "~규제", "~하락")
2. 요약: 2-3문장, 핵심 내용과 시장 영향 포함, 명사형으로 끝내기
3. 분석: 1-2문장, 원인/배경/시장 영향 분석, 명사형으로 끝내기
4. market_impact: 시장에 미치는 실질적 영향을 명확하게 기술
5. 중요도: 파급력(1~3점), 시장 영향(4~6점), 긴급성(7~10점) 기준 평가
6. 모든 외국어 트윗은 먼저 한국어로 번역한 후 분석하세요.
7. 내용이 중복되거나 매우 유사한 트윗들은 가장 정보가 많은 것만 선택하세요.
8. 응답에 영어가 포함되면 안 됩니다. 모든 내용을 한국어로 번역하세요.
9. 마지막 확인: 응답을 다시 읽고 영어가 있는지 확인하세요. 영어가 있으면 한국어로 수정하세요.

트윗 목록:
{tweets_text}"""
    
    try:
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "systemInstruction": {
                "parts": [{
                    "text": "당신은 글로벌 금융, 암호화폐, 정치 시장 분석 전문가입니다. ★★★ 중요: 모든 응답은 100% 한국어로만 작성하세요. 영어나 다른 외국어를 절대 사용하면 안 됩니다. 회사명, 인물명, 기술용어도 모두 한국어로 표기하세요. 응답에 영어가 1글자라도 포함되면 안 됩니다. ★★★"
                }]
            },
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 4000,
                "responseMimeType": "application/json"
            }
        }
        
        response = requests.post(GEMINI_API_URL, json=payload, timeout=60)
        response.raise_for_status()
        
        result_data = response.json()
        result_text = result_data['candidates'][0]['content']['parts'][0]['text']
        
        # ★★★ 2중 방어: 응답 전체 한국어 검증 ★★★
        logger.info(f"Gemini 원본 응답 (처음 200자): {result_text[:200]}")
        
        if not is_korean_text(result_text):
            logger.warning(f"영어 비중이 높은 응답 감지, 재번역 시도")
            result_text = translate_to_korean_if_needed(result_text)
        
        # JSON 파싱
        ai_data = json.loads(result_text)
        ai_results = ai_data.get("results", [])
        
        # 원본 트윗 데이터와 AI 결과 합치기 (중복 제거 포함)
        processed_tweets = []
        seen_headlines = set()
        
        for ai_result in ai_results:
            idx = ai_result.get("index", -1)
            headline = ai_result.get("headline", "").strip()
            
            # ★ 각 필드 한국어 재검증 ★
            if not is_korean_text(headline):
                headline = translate_to_korean_if_needed(headline)
            
            summary = ai_result.get("summary", "").strip()
            if not is_korean_text(summary):
                summary = translate_to_korean_if_needed(summary)
            
            analysis = ai_result.get("analysis", "").strip()
            if not is_korean_text(analysis):
                analysis = translate_to_korean_if_needed(analysis)
            
            market_impact = ai_result.get("market_impact", "").strip()
            if not is_korean_text(market_impact):
                market_impact = translate_to_korean_if_needed(market_impact)
            
            # 헤드라인 기준 중복 제거
            if not headline or headline in seen_headlines:
                continue
            
            if 0 <= idx < len(tweets):
                tweet = tweets[idx].copy()
                tweet["_category"] = ai_result.get("category", "기타")
                tweet["_headline"] = headline
                tweet["_summary"] = summary
                tweet["_analysis"] = analysis
                tweet["_market_impact"] = market_impact
                tweet["_importance"] = ai_result.get("importance", 5)
                
                processed_tweets.append(tweet)
                seen_headlines.add(headline)
        
        logger.info(f"처리 완료: {len(processed_tweets)}개 트윗 (모두 한국어)")
        return processed_tweets
        
    except Exception as e:
        logger.error(f"Gemini 처리 오류: {e}")
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
            tweet_copy["_market_impact"] = ""
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
    2. AI 중요도: Gemini가 평가한 뉴스 중요도 (1~10)
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
                f"    {i}. [{t.get('_final_score', 0):.1f}점] "
                f"키워드:{t.get('_keyword_score', 0):.1f} "
                f"중요도:{t.get('_importance', 0)*4:.0f} "
                f"최신:{t.get('_recency_score', 0):.1f} | "
                f"{t.get('_headline', '')[:40]}"
            )
    
    return ranked


def process_tweets(tweets: List[Dict]) -> Dict[str, List[Dict]]:
    """트윗 목록을 처리하여 카테고리별 랭킹된 뉴스를 반환합니다."""
    # 1. AI를 사용한 분류 및 요약
    processed_tweets = classify_and_summarize_batch(tweets)
    
    # 2. 카테고리별 랭킹 및 필터링
    ranked_news = rank_and_filter_by_category(processed_tweets)
    
    return ranked_news
