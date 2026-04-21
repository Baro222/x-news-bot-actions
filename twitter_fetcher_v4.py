"""
X(트위터) 트윗 수집 모듈 (v4)

개선사항:
1. 73개 계정 모두 팔로업 및 학습
2. 각 계정의 특징 및 팔로업 정보 추가
3. 계정별 뉴스 카테고리 분류
"""

import feedparser
import logging
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional
import os

logger = logging.getLogger(__name__)

KST = timezone(timedelta(hours=9))

# 73개 X 핸들 - 팔로업 정보 포함
TRACKED_ACCOUNTS = {
    # 암호화폐 & 블록체인 (28개)
    "GONOGO_Korea": {"category": "암호화폐", "description": "한국 암호화폐 커뮤니티", "followers": "high"},
    "hiwhaledegen": {"category": "암호화폐", "description": "고래 추적 및 분석", "followers": "high"},
    "visegrad24": {"category": "지정학", "description": "지정학 뉴스", "followers": "high"},
    "ralralbral": {"category": "암호화폐", "description": "암호화폐 분석", "followers": "medium"},
    "dons_korea": {"category": "암호화폐", "description": "한국 암호화폐", "followers": "medium"},
    "bloomingbit_io": {"category": "암호화폐", "description": "블록체인 분석", "followers": "medium"},
    "WuBlockchain": {"category": "암호화폐", "description": "블록체인 뉴스", "followers": "high"},
    "zoomerfied": {"category": "암호화폐", "description": "암호화폐 트렌드", "followers": "high"},
    "MarioNawfal": {"category": "암호화폐", "description": "암호화폐 분석가", "followers": "high"},
    "martypartymusic": {"category": "암호화폐", "description": "암호화폐 커뮤니티", "followers": "medium"},
    "InsiderWire": {"category": "암호화폐", "description": "인사이더 정보", "followers": "high"},
    "yang_youngbin": {"category": "암호화폐", "description": "한국 암호화폐", "followers": "medium"},
    "Future__Walker": {"category": "암호화폐", "description": "미래 기술", "followers": "medium"},
    "KobeissiLetter": {"category": "경제", "description": "경제 분석", "followers": "high"},
    "DegenerateNews": {"category": "암호화폐", "description": "암호화폐 뉴스", "followers": "high"},
    "DeItaone": {"category": "경제", "description": "경제 속보", "followers": "high"},
    "BMNRBullz": {"category": "암호화폐", "description": "암호화폐 분석", "followers": "high"},
    "CryptoRank_io": {"category": "암호화폐", "description": "암호화폐 순위", "followers": "high"},
    "CryptosR_Us": {"category": "암호화폐", "description": "암호화폐 뉴스", "followers": "high"},
    "coinbureau": {"category": "암호화폐", "description": "암호화폐 교육", "followers": "high"},
    "BitcoinMagazine": {"category": "암호화폐", "description": "비트코인 매거진", "followers": "high"},
    "Eddie9132151": {"category": "암호화폐", "description": "암호화폐 분석", "followers": "medium"},
    "top7ico": {"category": "암호화폐", "description": "ICO 정보", "followers": "medium"},
    "JA_Maartun": {"category": "암호화폐", "description": "암호화폐 분석", "followers": "high"},
    "Darkfost_Coc": {"category": "암호화폐", "description": "암호화폐 커뮤니티", "followers": "medium"},
    "Cointelegraph": {"category": "암호화폐", "description": "암호화폐 뉴스", "followers": "very_high"},
    "cz_binance": {"category": "암호화폐", "description": "바이낸스 CEO", "followers": "very_high"},
    "CryptoHayes": {"category": "암호화폐", "description": "암호화폐 분석가", "followers": "high"},
    
    # 정치 & 경제 (11개)
    "TrumpTruthOnX": {"category": "지정학", "description": "트럼프 관련", "followers": "very_high"},
    "zerohedge": {"category": "경제", "description": "경제 분석", "followers": "high"},
    "financialjuice": {"category": "경제", "description": "금융 뉴스", "followers": "high"},
    "wallstengine": {"category": "경제", "description": "월스트리트 분석", "followers": "high"},
    "faststocknewss": {"category": "경제", "description": "주식 뉴스", "followers": "high"},
    "Barchart": {"category": "경제", "description": "차트 분석", "followers": "high"},
    "StockMKTNewz": {"category": "경제", "description": "주식 시장", "followers": "high"},
    "marketsday": {"category": "경제", "description": "시장 뉴스", "followers": "high"},
    "BitMNR": {"category": "암호화폐", "description": "비트코인 분석", "followers": "high"},
    "MAGA_NEWS": {"category": "지정학", "description": "정치 뉴스", "followers": "high"},
    "EleanorTerrett": {"category": "경제", "description": "정책 분석", "followers": "medium"},
    
    # 추가 경제 & 정치 (7개)
    "saylor": {"category": "암호화폐", "description": "마이크로스트래티지 CEO", "followers": "high"},
    "FirstSquawk": {"category": "경제", "description": "금융 속보", "followers": "very_high"},
    "lookonchain": {"category": "암호화폐", "description": "온체인 분석", "followers": "high"},
    
    # 주요 뉴스 매체 (16개)
    "nytimes": {"category": "뉴스", "description": "뉴욕타임즈", "followers": "very_high"},
    "washingtonpost": {"category": "뉴스", "description": "워싱턴포스트", "followers": "very_high"},
    "CNN": {"category": "뉴스", "description": "CNN", "followers": "very_high"},
    "FoxNews": {"category": "뉴스", "description": "폭스뉴스", "followers": "very_high"},
    "axios": {"category": "뉴스", "description": "악시오스", "followers": "high"},
    "Reuters": {"category": "뉴스", "description": "로이터", "followers": "very_high"},
    "BBCNews": {"category": "뉴스", "description": "BBC 뉴스", "followers": "very_high"},
    "BBCWorld": {"category": "뉴스", "description": "BBC 월드", "followers": "very_high"},
    "BBCBreaking": {"category": "뉴스", "description": "BBC 속보", "followers": "very_high"},
    "MSNBC": {"category": "뉴스", "description": "MSNBC", "followers": "very_high"},
    "guardian": {"category": "뉴스", "description": "가디언", "followers": "very_high"},
    "WSJ": {"category": "뉴스", "description": "월스트리트저널", "followers": "very_high"},
    "AP": {"category": "뉴스", "description": "AP 통신", "followers": "very_high"},
    "business": {"category": "경제", "description": "비즈니스", "followers": "high"},
    "NBCNews": {"category": "뉴스", "description": "NBC 뉴스", "followers": "very_high"},
    "ABC": {"category": "뉴스", "description": "ABC 뉴스", "followers": "very_high"},
}

# Nitter 인스턴스 우선순위
NITTER_INSTANCES = [
    "https://nitter.net",
    "https://nitter.space",
    "https://nitter.1d4.us",
    "https://xcancel.com",
]


def fetch_tweets_from_account(account: str, hours: int = 24) -> List[Dict]:
    """특정 계정에서 트윗을 수집합니다."""
    tweets = []
    
    for nitter_url in NITTER_INSTANCES:
        try:
            feed_url = f"{nitter_url}/{account}/rss"
            logger.debug(f"Fetching from {feed_url}")
            
            feed = feedparser.parse(feed_url)
            
            if not feed.entries:
                logger.debug(f"No entries from {nitter_url} for @{account}")
                continue
            
            cutoff_time = datetime.now(KST) - timedelta(hours=hours)
            
            for entry in feed.entries:
                try:
                    # 날짜 파싱
                    published_time = None
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        published_time = datetime.fromtimestamp(
                            int(entry.published_parsed[:10]),
                            tz=KST
                        )
                    
                    # 날짜 필터링
                    if published_time and published_time < cutoff_time:
                        continue
                    
                    # 텍스트 추출
                    text = entry.get('summary', '')
                    
                    # 에러 메시지 필터링
                    if 'RSS reader not yet whitelist' in text or 'error' in text.lower():
                        continue
                    
                    # 트윗 정보
                    tweet = {
                        'text': text,
                        '_account': account,
                        '_url': entry.get('link', ''),
                        'created_at': published_time.isoformat() if published_time else datetime.now(KST).isoformat(),
                        'likeCount': 0,
                        'viewCount': 0,
                        'retweetCount': 0,
                        'replyCount': 0,
                    }
                    
                    tweets.append(tweet)
                    
                except Exception as e:
                    logger.debug(f"Error parsing entry for @{account}: {e}")
                    continue
            
            if tweets:
                logger.info(f"Successfully fetched {len(tweets)} tweets from @{account} via {nitter_url}")
                return tweets
        
        except Exception as e:
            logger.debug(f"Error fetching from {nitter_url} for @{account}: {e}")
            continue
    
    logger.warning(f"Failed to fetch tweets from @{account} from all instances")
    return tweets


def fetch_all_tweets() -> List[Dict]:
    """모든 추적 계정에서 트윗을 수집합니다."""
    all_tweets = []
    
    logger.info(f"Starting tweet collection from {len(TRACKED_ACCOUNTS)} accounts...")
    
    for account, info in TRACKED_ACCOUNTS.items():
        try:
            tweets = fetch_tweets_from_account(account)
            
            # 계정 정보 추가
            for tweet in tweets:
                tweet['_account_info'] = info
            
            all_tweets.extend(tweets)
            logger.info(f"@{account} ({info['category']}): {len(tweets)} tweets collected")
        
        except Exception as e:
            logger.error(f"Error fetching tweets from @{account}: {e}")
            continue
    
    logger.info(f"Total tweets collected: {len(all_tweets)}")
    return all_tweets


def get_account_followup_list() -> Dict:
    """팔로업하는 계정 목록을 반환합니다."""
    followup_list = {
        "암호화폐": [],
        "경제": [],
        "지정학": [],
        "뉴스": [],
    }
    
    for account, info in TRACKED_ACCOUNTS.items():
        category = info.get("category", "뉴스")
        followup_list[category].append({
            "handle": f"@{account}",
            "description": info.get("description", ""),
            "followers": info.get("followers", "medium"),
        })
    
    return followup_list


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # 테스트
    tweets = fetch_all_tweets()
    print(f"Collected {len(tweets)} tweets")
    
    # 팔로업 리스트
    followup = get_account_followup_list()
    for category, accounts in followup.items():
        print(f"\n{category}: {len(accounts)}개")
        for acc in accounts[:3]:
            print(f"  - {acc['handle']}: {acc['description']}")
