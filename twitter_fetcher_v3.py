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

# Nitter 인스턴스 목록
NITTER_INSTANCES = [
    "nitter.net",
    "nitter.privacyredirect.com",
    "nitter.poast.org",
    "xcancel.com",
    "nitter.space",
    "lightbrd.com",
    "nitter.catsarch.com",
    "nuku.trabun.org",
]

_current_instance_idx = 0
REQUEST_DELAY = 0.3  # 요청 간 딜레이 단축


def get_nitter_rss(username: str, instance: str) -> Optional[str]:
    """Nitter RSS 피드를 가져옵니다."""
    url = f"https://{instance}/{username}/rss"
    cmd = [
        "curl", "-sL", "--max-time", "15",
        "-H", "User-Agent: RSS-Reader/1.0",
        "-H", "Accept: application/rss+xml, application/xml, text/xml",
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

            # 설명 정리
            desc = (desc_elem.text or "").strip() if desc_elem is not None else ""
            clean_desc = re.sub(r'<[^>]+>', '', desc).strip()

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


def get_user_last_tweets(username: str) -> List[Dict]:
    """특정 사용자의 최신 트윗을 Nitter RSS로 가져옵니다."""
    global _current_instance_idx

    instances_to_try = (
        NITTER_INSTANCES[_current_instance_idx:] +
        NITTER_INSTANCES[:_current_instance_idx]
    )

    for instance in instances_to_try:
        rss_content = get_nitter_rss(username, instance)
        if rss_content:
            tweets = parse_rss_tweets(rss_content, username)
            if tweets:
                _current_instance_idx = NITTER_INSTANCES.index(instance)
                return tweets
            logger.debug(f"@{username}: {instance}에서 트윗 없음")
            return []

    logger.warning(f"@{username}: 모든 Nitter 인스턴스 실패")
    return []


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
    logger.info(f"총 {len(ACCOUNTS_FLAT)}개 계정에서 트윗 수집 시작 (Nitter RSS 방식)...")
    
    all_tweets = []
    
    for idx, account in enumerate(ACCOUNTS_FLAT, 1):
        logger.info(f"[{idx}/{len(ACCOUNTS_FLAT)}] @{account} 수집 중...")
        
        try:
            tweets = get_user_last_tweets(account)
            recent_tweets = filter_recent_tweets(tweets)
            
            if recent_tweets:
                logger.info(f"  -> {len(recent_tweets)}개 최신 트윗 수집")
                all_tweets.extend(recent_tweets)
            else:
                logger.debug(f"  -> 최근 트윗 없음")
            
            time.sleep(REQUEST_DELAY)
            
        except Exception as e:
            logger.error(f"@{account} 수집 오류: {e}")
            continue
    
    logger.info(f"총 {len(all_tweets)}개 트윗 수집 완료")
    return all_tweets


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    tweets = fetch_all_tweets()
    print(f"수집된 트윗: {len(tweets)}개")
    for tweet in tweets[:3]:
        print(f"  - {tweet['_account']}: {tweet['text'][:50]}")
