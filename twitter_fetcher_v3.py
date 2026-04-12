"""
X(트위터) 뉴스 수집 모듈 v3
Nitter RSS + Selenium 기반 좋아요/조회수 수집
"""

import subprocess
import xml.etree.ElementTree as ET
import time
import logging
import re
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional
from config import ACCOUNTS_FLAT, FETCH_HOURS

logger = logging.getLogger(__name__)
logger.propagate = True

# Nitter 인스턴스 목록 (우선순위 순서)
NITTER_INSTANCES = [
    "nitter.net",
    "nitter.space",
    "nitter.privacyredirect.com",
    "nitter.poast.org",
    "lightbrd.com",
    "nitter.catsarch.com",
    "xcancel.com",  # 화이트리스트 문제 있음 - 마지막에 시도
    "nuku.trabun.org",
]

_current_instance_idx = 0
REQUEST_DELAY = 0.3  # 요청 간 딜레이


def get_nitter_rss(username: str, instance: str) -> Optional[str]:
    """Nitter RSS 피드를 가져옵니다."""
    url = f"https://{instance}/{username}/rss"
    cmd = [
        "curl", "-sL", "--max-time", "15",
        "-H", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "-H", "Accept: application/rss+xml, application/xml, text/xml, */*",
        "-H", "Accept-Language: en-US,en;q=0.9",
        url
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=False, timeout=20)
        if result.returncode == 0 and result.stdout:
            try:
                out = result.stdout.decode('utf-8', errors='replace')
            except Exception:
                out = result.stdout.decode('latin-1', errors='replace')
            out = out.lstrip('\ufeff')
            
            # 화이트리스트 에러 필터링
            if "RSS reader not yet whitelist" in out or "Plain request with just the ID" in out:
                logger.warning(f"RSS 화이트리스트 에러 ({instance}/{username})")
                return None
            
            first_lt = out.find('<')
            if first_lt > 0:
                out = out[first_lt:]
            out = out.replace('\x00', '')
            if "<rss" in out or "<?xml" in out:
                return out
        return None
    except Exception:
        return None


def parse_rss_tweets(rss_content: str, username: str) -> List[Dict]:
    """RSS XML을 파싱하여 트윗 목록을 반환합니다."""
    tweets = []
    try:
        root = ET.fromstring(rss_content)
        channel = root.find("channel")
        if channel is None:
            return []

        items = channel.findall("item")
        for item in items:
            title_elem = item.find("title")
            desc_elem = item.find("description")
            link_elem = item.find("link")
            pub_date_elem = item.find("pubDate")

            title = (title_elem.text or "").strip() if title_elem is not None else ""
            link = (link_elem.text or "").strip() if link_elem is not None else ""
            pub_date = (pub_date_elem.text or "").strip() if pub_date_elem is not None else ""

            if not link:
                continue

            # 트윗 ID 추출
            match = re.search(r'/status/(\d+)', link)
            tweet_id = match.group(1) if match else ""

            # 설명 정리 - 에러 메시지 필터링
            desc = (desc_elem.text or "").strip() if desc_elem is not None else ""
            
            # HTML 태그 제거
            clean_desc = re.sub(r'<[^>]+>', '', desc).strip()
            
            # 에러 메시지 필터링
            if "RSS reader not yet whitelist" in clean_desc or "Plain request with just the ID" in clean_desc:
                logger.warning(f"에러 메시지 필터링 ({username}): {clean_desc[:50]}")
                continue
            
            # 빈 내용 필터링
            if not clean_desc and not title:
                continue

            # 날짜 파싱
            created_at = pub_date
            if pub_date:
                try:
                    dt = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %Z")
                    dt = dt.replace(tzinfo=timezone.utc)
                    created_at = dt.strftime("%a %b %d %H:%M:%S +0000 %Y")
                except ValueError:
                    created_at = pub_date

            # 트윗 객체 생성 (좋아요/조회수는 나중에 Selenium으로 수집)
            tweet = {
                "id": tweet_id,
                "text": clean_desc if clean_desc else title,
                "createdAt": created_at,
                "likeCount": 0,
                "retweetCount": 0,
                "replyCount": 0,
                "quoteCount": 0,
                "viewCount": 0,
                "_url": link.replace("nitter.net", "x.com")
                             .replace("xcancel.com", "x.com")
                             .replace("nitter.space", "x.com")
                             .replace("lightbrd.com", "x.com")
                             .replace("nitter.privacyredirect.com", "x.com")
                             .replace("nitter.poast.org", "x.com")
                             .replace("nitter.catsarch.com", "x.com")
                             .replace("nuku.trabun.org", "x.com"),
                "_account": username,
            }
            tweets.append(tweet)

    except ET.ParseError as e:
        logger.warning(f"RSS XML 파싱 오류 ({username}): {e}")
    except Exception as e:
        logger.warning(f"RSS 처리 오류 ({username}): {e}")

    return tweets


def rotate_instance() -> str:
    """다음 Nitter 인스턴스로 로테이션합니다."""
    global _current_instance_idx
    _current_instance_idx = (_current_instance_idx + 1) % len(NITTER_INSTANCES)
    return NITTER_INSTANCES[_current_instance_idx]


def fetch_tweets_from_account(username: str) -> List[Dict]:
    """계정에서 최신 트윗을 수집합니다."""
    tweets = []
    
    # 여러 인스턴스 시도
    for attempt in range(len(NITTER_INSTANCES)):
        instance = NITTER_INSTANCES[attempt]
        
        rss_content = get_nitter_rss(username, instance)
        if rss_content:
            parsed_tweets = parse_rss_tweets(rss_content, username)
            if parsed_tweets:
                tweets.extend(parsed_tweets)
                logger.info(f"  -> {len(parsed_tweets)}개 최신 트윗 수집 ({instance})")
                break
        
        time.sleep(REQUEST_DELAY)
    
    if not tweets:
        logger.warning(f"  -> 트윗 수집 실패 (모든 인스턴스)")
    
    return tweets


def parse_tweet_time(created_at_str: str) -> Optional[datetime]:
    """트윗 날짜 문자열을 datetime 객체로 변환합니다."""
    if not created_at_str:
        return None
    for fmt in [
        "%a %b %d %H:%M:%S +0000 %Y",
        "%a, %d %b %Y %H:%M:%S %Z",
        "%a, %d %b %Y %H:%M:%S +0000",
    ]:
        try:
            dt = datetime.strptime(created_at_str, fmt)
            return dt.replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
    except Exception:
        return None


def filter_recent_tweets(tweets: List[Dict], hours: int = FETCH_HOURS) -> List[Dict]:
    """최근 N시간 이내의 트윗만 필터링합니다."""
    now_utc = datetime.now(timezone.utc)
    cutoff_time = now_utc - timedelta(hours=hours)
    recent_tweets = []

    for tweet in tweets:
        created_at_str = tweet.get("createdAt", "")
        dt = parse_tweet_time(created_at_str)
        
        # 날짜 파싱 실패 시 포함 (안전한 기본값)
        if dt is None:
            recent_tweets.append(tweet)
        elif dt >= cutoff_time:
            recent_tweets.append(tweet)

    return recent_tweets


def fetch_all_tweets() -> List[Dict]:
    """모든 계정에서 최신 트윗을 수집합니다."""
    all_tweets = []
    total_accounts = len(ACCOUNTS_FLAT)
    
    logger.info(f"===== 트윗 수집 시작: {total_accounts}개 계정 =====")
    
    for idx, account in enumerate(ACCOUNTS_FLAT, 1):
        logger.info(f"[{idx}/{total_accounts}] @{account} 수집 중...")
        
        tweets = fetch_tweets_from_account(account)
        all_tweets.extend(tweets)
        
        time.sleep(REQUEST_DELAY)
    
    # 최근 트윗만 필터링
    recent_tweets = filter_recent_tweets(all_tweets)
    
    logger.info(f"총 {len(recent_tweets)}개 트윗 수집 완료")
    return recent_tweets


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    tweets = fetch_all_tweets()
    print(f"수집된 트윗: {len(tweets)}개")
    for tweet in tweets[:3]:
        print(f"  - {tweet.get('_account')}: {tweet.get('text', '')[:50]}")
