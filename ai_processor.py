"""
OpenAI 호환 API를 통해 Gemini를 호출하여 트윗을 분류, 요약, 랭킹 처리하는 모듈
모델 자동 우회: gemini-2.0-flash → gemini-1.5-flash → gemini-1.5-flash-8b → 키워드 폴백
모든 출력은 반드시 한국어로 처리됩니다.
"""

import json
import logging
import os
import time
from typing import List, Dict, Optional

# Google Translate 폴백용
try:
    from googletrans import Translator
    _translator = Translator()
except Exception:
    _translator = None

# LibreTranslate 폴백 (공개 인스턴스 사용)
try:
    import requests
    _libre_url = os.environ.get('LIBRETRANSLATE_URL', 'https://libretranslate.de/translate')
except Exception:
    requests = None
    _libre_url = None

logger = logging.getLogger(__name__)

# config에서 상수 import (실패 시 기본값 사용)
try:
    from config import OPENAI_API_KEY, MAX_NEWS_PER_CATEGORY, MIN_NEWS_PER_CATEGORY
except Exception:
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
    MAX_NEWS_PER_CATEGORY = 10
    MIN_NEWS_PER_CATEGORY = 5

# Gemini 모델 우회 순서 (한도 초과 시 자동으로 다음 모델 시도)
GEMINI_MODELS_FALLBACK = [
    "gemini-2.0-flash",
    "gemini-1.5-flash",
    "gemini-1.5-flash-8b",
    "gemini-1.0-pro",
]

# 환경변수로 첫 번째 모델 오버라이드 가능
_env_model = os.environ.get("AI_MODEL", "")
if _env_model and _env_model not in GEMINI_MODELS_FALLBACK:
    GEMINI_MODELS_FALLBACK.insert(0, _env_model)
elif _env_model:
    # 지정된 모델을 맨 앞으로
    GEMINI_MODELS_FALLBACK = [_env_model] + [m for m in GEMINI_MODELS_FALLBACK if m != _env_model]

# Gemini OpenAI 호환 엔드포인트
GEMINI_BASE_URL = os.environ.get(
    "OPENAI_BASE_URL",
    "https://generativelanguage.googleapis.com/v1beta/openai/"
)

# OpenAI 클라이언트 초기화
_openai_client = None
try:
    from openai import OpenAI
    api_key = OPENAI_API_KEY or os.environ.get("OPENAI_API_KEY", "")
    if api_key:
        _openai_client = OpenAI(api_key=api_key, base_url=GEMINI_BASE_URL)
        logger.info(f"Gemini 클라이언트 초기화 성공 (모델 우회 순서: {GEMINI_MODELS_FALLBACK})")
    else:
        logger.info("OPENAI_API_KEY 미설정 - 키워드 기반 폴백 사용")
except Exception as e:
    logger.warning(f"OpenAI 클라이언트 초기화 실패, 폴백으로 동작: {e}")
    _openai_client = None


CATEGORY_KEYWORDS = {
    "지정학": [
        "war", "conflict", "military", "nato", "russia", "ukraine", "china", "taiwan",
        "north korea", "iran", "israel", "gaza", "sanctions", "geopolitical", "troops",
        "missile", "nuclear", "diplomacy", "alliance", "invasion", "territory",
        "전쟁", "분쟁", "군사", "러시아", "우크라이나", "중국", "대만", "북한", "이란", "이스라엘",
        "제재", "지정학", "외교", "동맹", "침공", "영토", "나토", "ceasefire", "peace talks",
        "tariff", "trade war", "sanctions", "embargo"
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


def _call_gemini_with_fallback(prompt: str, system_prompt: str) -> Optional[str]:
    """Gemini API를 호출하며, 429(한도 초과) 시 지수 백오프 후 재시도하고, 모델 간 우회합니다.

    백오프 시퀀스: 2s -> 4s -> 8s -> 16s (모델 변경 전 재시도 포함)
    각 요청에 timeout=30 초를 적용합니다.
    """
    if _openai_client is None:
        return None

    backoff_base = 2
    for model in GEMINI_MODELS_FALLBACK:
        attempt = 0
        while attempt < 4:
            try:
                logger.info(f"Gemini 모델 시도: {model} (attempt {attempt+1})")
                response = _openai_client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=4000,
                    timeout=30
                )
                result = response.choices[0].message.content
                logger.info(f"Gemini 모델 성공: {model}")
                return result
            except Exception as e:
                err_str = str(e)
                # 429 관련이면 지수 백오프
                if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str or "quota" in err_str.lower():
                    wait = backoff_base * (2 ** attempt)
                    logger.warning(f"모델 {model} 한도 초과 (429) - {wait}s 후 재시도...")
                    time.sleep(wait)
                    attempt += 1
                    continue
                elif "404" in err_str or "not found" in err_str.lower():
                    logger.warning(f"모델 {model} 미지원 - 다음 모델로 우회...")
                    break
                else:
                    logger.error(f"모델 {model} 오류: {e}")
                    break
        # 다음 모델로 넘어감
        logger.info(f"다음 모델로 우회합니다")

    logger.error("모든 Gemini 모델 한도 초과 또는 오류 - 키워드 폴백 사용")
    return None


def classify_and_summarize_batch(tweets: List[Dict]) -> List[Dict]:
    """AI를 사용하여 트윗 배치를 분류하고 요약합니다."""
    if not tweets:
        return []

    # Tuneable via environment for emergency mitigation
    batch_size = int(os.environ.get('AI_BATCH_SIZE', '3'))
    request_delay = float(os.environ.get('AI_REQUEST_DELAY', '2.0'))
    results = []
    for i in range(0, len(tweets), batch_size):
        batch = tweets[i:i + batch_size]
        try:
            batch_results = _process_batch(batch)
            results.extend(batch_results)
        except Exception as e:
            logger.warning(f"배치 처리 중 오류 발생, 해당 배치 스킵: {e}")
        if i + batch_size < len(tweets):
            time.sleep(request_delay)  # API 레이트 리밋 방지
    return results


def _process_batch(tweets: List[Dict]) -> List[Dict]:
    """트윗 배치를 AI로 처리합니다."""
    tweet_list = []
    for idx, tweet in enumerate(tweets):
        text = tweet.get("text", "")
        account = tweet.get("_account", "unknown")
        engagement = tweet.get("_engagement_score", 0)
        url = tweet.get("_url", "")
        tweet_list.append(f"[{idx}] @{account} (참여도:{engagement:.0f})\n{text}\nURL: {url}")

    tweets_text = "\n\n---\n\n".join(tweet_list)

    system_prompt = (
        "당신은 글로벌 뉴스와 금융 시장을 전문적으로 분석하는 한국어 뉴스 큐레이터입니다. "
        "반드시 JSON 형식으로만 응답하고, 모든 텍스트는 반드시 한국어로 작성하세요. "
        "영어 트윗은 반드시 한국어로 번역하여 요약하세요."
    )

    prompt = f"""다음 트윗들을 분석하여 각각을 분류하고 한국어로 요약해주세요.

분류 기준:
- 지정학: 전쟁, 분쟁, 군사, 외교, 국제관계, 지역갈등, 무역전쟁 등
- 경제: 경제지표, 금융시장, 무역, 통화정책, 기업실적, 고용 등
- 트럼프: 트럼프 관련 정책, 발언, 행정부 소식 등
- 암호화폐: 비트코인, 이더리움, 크립토 시장, 블록체인 등
- 기타: 위 4가지에 해당하지 않는 경우

각 트윗에 대해 다음 JSON 형식으로 응답하세요:
{{
  "results": [
    {{
      "index": 0,
      "category": "경제",
      "headline": "헤드라인 (20자 이내, 한국어, 명사형으로 끝내기)",
      "summary": "핵심 내용 요약 (2-3문장, 한국어, 명사형으로 끝내기)",
      "analysis": "간단한 배경/원인 분석 (1-2문장, 한국어, 명사형으로 끝내기)",
      "importance": 5
    }}
  ]
}}

중요 규칙:
1. 헤드라인, 요약, 분석은 반드시 한국어로 작성
2. 영어 트윗은 반드시 한국어로 번역하여 요약
3. 명사형으로 끝내기 (예: "~비판", "~발표", "~확대", "~하락", "~급등")
4. "했습니다", "합니다", "됩니다" 등 서술형 종결어미 사용 금지
5. 중요도(importance)는 1~10 정수 (파급력·시장 영향·사회적 관심도 기준)

트윗 목록:
{tweets_text}"""

    result_text = _call_gemini_with_fallback(prompt, system_prompt)

    if result_text is None:
        logger.info("AI 응답 없음 - 키워드 기반 폴백 분류 사용")
        return _fallback_classify(tweets)

    try:
        # JSON 블록 추출
        if "```json" in result_text:
            result_text = result_text.split("```json")[1].split("```")[0].strip()
        elif "```" in result_text:
            result_text = result_text.split("```")[1].split("```")[0].strip()

        result_data = json.loads(result_text)
        ai_results = result_data.get("results", [])

        processed_tweets = []
        for ai_result in ai_results:
            idx = ai_result.get("index", -1)
            if 0 <= idx < len(tweets):
                tweet = tweets[idx].copy()
                tweet["_category"] = ai_result.get("category", "기타")
                tweet["_headline"] = ai_result.get("headline", "")
                tweet["_summary"] = ai_result.get("summary", "")
                tweet["_analysis"] = ai_result.get("analysis", "")
                tweet["_importance"] = int(ai_result.get("importance", 5))
                processed_tweets.append(tweet)

        logger.info(f"AI 처리 완료: {len(processed_tweets)}/{len(tweets)}개 트윗")
        return processed_tweets

    except json.JSONDecodeError as e:
        logger.error(f"AI 응답 JSON 파싱 오류: {e}")
        return _fallback_classify(tweets)
    except Exception as e:
        logger.error(f"AI 처리 오류: {e}")
        return _fallback_classify(tweets)


# 간단한 영어→한국어 키워드 번역 매핑 (폴백용)
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
    # 추가 확장 키워드
    "ipo": "기업공개", "merger": "인수합병", "acquisition": "인수", "earnings": "실적", "revenue": "매출",
    "sec": "미 SEC", "fed rate": "연준금리", "fed minutes": "연준회의록", "cpi": "소비자물가지수",
    "etf": "상장지수펀드", "bloomberg": "블룸버그", "biden": "바이든", "china economy": "중국 경제",
}

CATEGORY_KO = {
    "지정학": "지정학", "경제": "경제", "트럼프": "트럼프", "암호화폐": "암호화폐",
    "geopolitics": "지정학", "economy": "경제", "crypto": "암호화폐", "기타": "기타"
}


def _translate_headline(text: str) -> str:
    """영어 텍스트를 한국어로 변환하는 2단계 전략 (폴백용)

    1) 빠른 키워드 치환: EN_KO_KEYWORDS 매핑을 사용하여 핵심 용어를 치환
    2) 문장 번역 필요 시(영어 비중이 높으면): googletrans를 사용하여 전체 문장 번역
    """
    if not text:
        return ""

    # 1) 키워드 치환
    result = text
    for en, ko in EN_KO_KEYWORDS.items():
        result = result.replace(en.upper(), ko).replace(en.capitalize(), ko).replace(en, ko)

    # 2) 영어 비중 판단: 영어 알파벳 수 / 전체 문자 수
    letters = sum(1 for c in text if ('a' <= c.lower() <= 'z'))
    total = max(1, len(text))
    eng_ratio = letters / total

    # 영어 비중이 30% 이상이면 googletrans로 전체 문장 번역 시도 (정확도 우선)
    if eng_ratio >= 0.3:
        if _translator is not None:
            try:
                translated = _translator.translate(text, dest='ko')
                if getattr(translated, 'text', None):
                    return translated.text
            except Exception as e:
                logger.warning(f"googletrans 번역 실패: {e} - 다음 폴백 시도")
        # googletrans가 없거나 실패하면 Hugging Face Inference API 시도 (환경변수 HF_API_TOKEN 필요)
        hf_token = os.environ.get('HF_API_TOKEN')
        if hf_token:
            try:
                hf_headers = {'Authorization': f'Bearer {hf_token}'}
                # 모델 선택: Helsinki 또는 다른 적합한 번역 모델
                hf_model = os.environ.get('HF_TRANSLATE_MODEL', 'Helsinki-NLP/opus-mt-en-ko')
                hf_url = f'https://api-inference.huggingface.co/models/{hf_model}'
                hf_resp = requests.post(hf_url, headers=hf_headers, json={'inputs': text}, timeout=20)
                if hf_resp.status_code == 200:
                    hf_j = hf_resp.json()
                    if isinstance(hf_j, dict) and 'error' in hf_j:
                        raise Exception(hf_j['error'])
                    # HF inference returns list or dict depending on model
                    if isinstance(hf_j, list) and len(hf_j) and 'translation_text' in hf_j[0]:
                        return hf_j[0]['translation_text']
                    if isinstance(hf_j, dict) and 'translation_text' in hf_j:
                        return hf_j['translation_text']
            except Exception as e:
                logger.warning(f"HuggingFace 번역 실패: {e} - 다음 폴백 시도")
        # googletrans가 없거나 실패하면 LibreTranslate 공개 인스턴스 시도
        if requests is not None and _libre_url:
            try:
                resp = requests.post(_libre_url, data={
                    'q': text,
                    'source': 'en',
                    'target': 'ko',
                    'format': 'text'
                }, timeout=10)
                # Guard against non-JSON or empty responses
                if resp.status_code == 200 and resp.text and resp.headers.get('Content-Type','').lower().startswith('application/json'):
                    j = resp.json()
                    if isinstance(j, dict) and 'translatedText' in j:
                        return j['translatedText']
                    # some instances return {'translatedText': ...} or simple string
                    if isinstance(j, str) and j.strip():
                        return j
                else:
                    logger.warning(f"LibreTranslate 응답 비정상(status={resp.status_code}, len={len(resp.text)}), 헤더={resp.headers.get('Content-Type')}")
            except Exception as e:
                logger.warning(f"LibreTranslate 번역 실패: {e} - 키워드 치환 결과 사용")

    # 결과 길이 제한
    if len(result) > 200:
        result = result[:197] + '...'
    return result


def _fallback_classify(tweets: List[Dict]) -> List[Dict]:
    """키워드 기반 폴백 분류 — 모든 헤드라인/요약을 한국어로 변환하여 반환"""
    fallback_results = []
    for tweet in tweets:
        text = tweet.get("text", "")
        category = classify_tweet_simple(text) or "기타"
        tweet_copy = tweet.copy()
        tweet_copy["_category"] = category

        raw_text = text.strip().replace('\n', ' ')
        # 헤드라인: _translate_headline으로 강제 한글 변환
        headline = _translate_headline(raw_text[:120])
        tweet_copy["_headline"] = headline if headline else raw_text[:50]

        # 요약: _translate_headline으로 한글 변환
        summary_raw = raw_text[:400]
        tweet_copy["_summary"] = _translate_headline(summary_raw) if summary_raw else ""
        tweet_copy["_analysis"] = "(AI 폴백 자동 분류)"
        tweet_copy["_importance"] = 5
        fallback_results.append(tweet_copy)
    return fallback_results


def extract_keywords_from_text(text: str) -> List[str]:
    """텍스트에서 의미있는 키워드를 추출합니다."""
    import re
    words = re.findall(r'[a-zA-Z가-힣]{2,}', text.lower())
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
    """같은 카테고리 내 다른 트윗들과의 키워드 중복도 점수를 계산합니다."""
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
        intersection = tweet_keywords & other_keywords
        union = tweet_keywords | other_keywords
        if union:
            jaccard = len(intersection) / len(union)
            overlap_score += jaccard * len(intersection)

    return overlap_score


def rank_and_filter_by_category(processed_tweets: List[Dict]) -> Dict[str, List[Dict]]:
    """카테고리별로 트윗을 랭킹하고 필터링합니다."""
    categorized: Dict[str, List[Dict]] = {
        "지정학": [],
        "경제": [],
        "트럼프": [],
        "암호화폐": [],
    }

    for tweet in processed_tweets:
        category = tweet.get("_category", "기타")
        if category in categorized:
            categorized[category].append(tweet)

    ranked: Dict[str, List[Dict]] = {}
    for category, tweets in categorized.items():
        if not tweets:
            ranked[category] = []
            continue

        for tweet in tweets:
            importance = tweet.get("_importance", 5)
            engagement = tweet.get("_engagement_score", 0)

            keyword_score = calculate_keyword_overlap_score(tweet, tweets)
            keyword_score_normalized = min(keyword_score * 5, 50)
            importance_score = importance * 4
            age_hours = tweet.get("_age_hours", 4.0)
            recency_score = max(0, 20 - (age_hours / 4.0) * 20)
            engagement_score = min(engagement / 100, 10)

            tweet["_final_score"] = (
                keyword_score_normalized +
                importance_score +
                recency_score +
                engagement_score
            )
            tweet["_keyword_score"] = keyword_score_normalized
            tweet["_recency_score"] = recency_score

        sorted_tweets = sorted(tweets, key=lambda x: x.get("_final_score", 0), reverse=True)
        ranked[category] = sorted_tweets[:MAX_NEWS_PER_CATEGORY]

        logger.info(f"  [{category}] TOP {len(ranked[category])}개 선정:")
        for i, t in enumerate(ranked[category][:3], 1):
            logger.info(
                f"    {i}. [{t.get('_final_score', 0):.1f}점] "
                f"키워드:{t.get('_keyword_score', 0):.1f} "
                f"중요도:{t.get('_importance', 0) * 4:.0f} "
                f"최신:{t.get('_recency_score', 0):.1f} | "
                f"{t.get('_headline', '')[:40]}"
            )

    return ranked


def process_tweets(tweets: List[Dict]) -> Dict[str, List[Dict]]:
    """트윗 전체 처리 파이프라인: 분류 -> 요약 -> 랭킹"""
    logger.info(f"총 {len(tweets)}개 트윗 AI 처리 시작...")

    relevant_tweets = []
    for tweet in tweets:
        text = tweet.get("text", "")
        category = classify_tweet_simple(text)
        if category:
            tweet["_pre_category"] = category
        else:
            tweet["_pre_category"] = "미분류"
        relevant_tweets.append(tweet)

    logger.info(f"AI 분류·요약 처리 중... ({len(relevant_tweets)}개)")

    processed = classify_and_summarize_batch(relevant_tweets)

    filtered = [t for t in processed if t.get("_category") in ["지정학", "경제", "트럼프", "암호화폐"]]

    logger.info(f"분류 완료: {len(filtered)}개 (기타 제외)")

    ranked = rank_and_filter_by_category(filtered)

    for cat, items in ranked.items():
        logger.info(f"  {cat}: {len(items)}개")

    return ranked


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
            "text": "Trump signs executive order imposing 25% tariffs on all imports from Canada and Mexico starting March 1.",
            "_account": "Reuters",
            "_engagement_score": 8000,
            "_url": "https://x.com/Reuters/status/789"
        },
    ]

    result = process_tweets(test_tweets)
    for cat, items in result.items():
        print(f"\n[{cat}] {len(items)}건:")
        for item in items:
            print(f"  - {item.get('_headline', '')} | {item.get('_summary', '')[:50]}")
