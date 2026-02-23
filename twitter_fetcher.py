"""
Nitter RSS를 사용하여 X(트위터) 계정의 최신 트윗을 수집하는 모듈
완전 무료, API 키 불필요
Nitter는 X의 오픈소스 미러 서비스로 RSS 피드를 제공합니다.
"""

import subprocess
import xml.etree.ElementTree as ET
import time
import logging
import re
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional
from config import ACCOUNTS, FETCH_HOURS

logger = logging.getLogger(__name__)
logger.propagate = True  # 루트 로거로 전파

# Nitter 인스턴스 목록 (우선순위 순)
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

# 현재 사용 중인 인스턴스 인덱스
_current_instance_idx = 0

# 요청 간 딜레이 (초) - Nitter 서버 부하 방지
REQUEST_DELAY = 1.5


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
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        if result.returncode == 0 and result.stdout and "<rss" in result.stdout:
            return result.stdout
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
            title = item.findtext("title", "")
            description = item.findtext("description", "")
            link = item.findtext("link", "")
            pub_date = item.findtext("pubDate", "")

            # HTML 태그 제거
            clean_desc = re.sub(r'<[^>]+>', '', description).strip()
            # 중복 공백 제거
            clean_desc = re.sub(r'\s+', ' ', clean_desc).strip()

            # 트윗 ID 추출
            tweet_id = ""
            if "/status/" in link:
                tweet_id = link.split("/status/")[-1].split("#")[0].strip()

            # 날짜 파싱
            created_at = ""
            if pub_date:
                try:
                    # RSS 날짜 형식: "Sat, 22 Feb 2026 12:00:00 GMT"
                    dt = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %Z")
                    dt = dt.replace(tzinfo=timezone.utc)
                    created_at = dt.strftime("%a %b %d %H:%M:%S +0000 %Y")
                except ValueError:
                    created_at = pub_date

            # 좋아요/리트윗 수 파싱 (RSS에는 없으므로 0으로 설정)
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

    # 여러 인스턴스 순서대로 시도
    instances_to_try = (
        NITTER_INSTANCES[_current_instance_idx:] +
        NITTER_INSTANCES[:_current_instance_idx]
    )

    for instance in instances_to_try:
        rss_content = get_nitter_rss(username, instance)
        if rss_content:
            tweets = parse_rss_tweets(rss_content, username)
            if tweets:
                # 성공한 인스턴스를 현재 인스턴스로 설정
                _current_instance_idx = NITTER_INSTANCES.index(instance)
                return tweets
            # RSS는 받았지만 트윗이 없는 경우 (비공개 계정 등)
            logger.debug(f"@{username}: {instance}에서 트윗 없음")
            return []

    logger.warning(f"@{username}: 모든 Nitter 인스턴스 실패")
    return []


def parse_tweet_time(created_at_str: str) -> Optional[datetime]:
    """트윗 날짜 문자열을 datetime 객체로 변환합니다."""
    if not created_at_str:
        return None
    # 형식 1: RSS 파싱 후 저장 형식 "Sat Feb 22 12:00:00 +0000 2026"
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
    # 형식 2: ISO 8601
    try:
        return datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
    except Exception:
        return None


def filter_recent_tweets(tweets: List[Dict], hours: int = 4) -> List[Dict]:
    """최근 N시간 이내의 트윗만 엄격하게 필터링합니다. (기본 4시간)
    
    - 날짜 정보가 없거나 파싱 불가능한 트윗은 제외
    - cutoff_time 이전 트윗은 모두 제외 (전날, 그 이전 포함)
    """
    now_utc = datetime.now(timezone.utc)
    # FETCH_HOURS 대신 명시적으로 4시간을 사용하거나 config 값을 따름
    cutoff_time = now_utc - timedelta(hours=hours)
    recent_tweets = []
    excluded_count = 0

    for tweet in tweets:
        created_at_str = tweet.get("createdAt", "")

        # 날짜 정보 없으면 제외 (불확실한 트윗은 포함하지 않음)
        if not created_at_str:
            excluded_count += 1
            continue

        tweet_time = parse_tweet_time(created_at_str)

        # 날짜 파싱 실패 시 제외
        if tweet_time is None:
            logger.debug(f"날짜 파싱 실패, 제외: {created_at_str}")
            excluded_count += 1
            continue

        # 미래 날짜 보정 (시계 오차 최대 5분 허용)
        if tweet_time > now_utc + timedelta(minutes=5):
            logger.debug(f"미래 날짜 트윗 제외: {created_at_str}")
            excluded_count += 1
            continue

        # cutoff_time 이후 트윗만 포함 (엄격한 4시간 필터링)
        if tweet_time >= cutoff_time:
            tweet["_created_at_dt"] = tweet_time  # datetime 객체 저장
            tweet["_age_hours"] = (now_utc - tweet_time).total_seconds() / 3600
            recent_tweets.append(tweet)
        else:
            excluded_count += 1
            logger.debug(
                f"시간 초과 제외 ({tweet.get('_account','?')}): "
                f"{tweet_time.strftime('%Y-%m-%d %H:%M UTC')} "
                f"(cutoff: {cutoff_time.strftime('%Y-%m-%d %H:%M UTC')})"
            )

    if excluded_count > 0:
        logger.info(f"시간 필터: {excluded_count}개 제외, {len(recent_tweets)}개 통과 (기준: {hours}시간 이내)")

    return recent_tweets


def calculate_engagement_score(tweet: Dict) -> float:
    """트윗의 참여도 점수를 계산합니다.
    Nitter RSS는 좋아요/리트윗 수를 제공하지 않으므로
    계정 중요도와 최신성으로 점수를 부여합니다.
    """
    like_count = tweet.get("likeCount", 0) or 0
    retweet_count = tweet.get("retweetCount", 0) or 0
    reply_count = tweet.get("replyCount", 0) or 0
    quote_count = tweet.get("quoteCount", 0) or 0
    view_count = tweet.get("viewCount", 0) or 0

    score = (
        like_count * 1.0 +
        retweet_count * 2.0 +
        reply_count * 1.5 +
        quote_count * 2.5 +
        view_count * 0.01
    )

    # 텍스트 길이 기반 보정 (더 긴 트윗 = 더 많은 내용)
    text_len = len(tweet.get("text", ""))
    score += min(text_len / 10, 20)

    return score


def fetch_all_tweets() -> List[Dict]:
    """모든 계정의 최신 트윗을 수집합니다."""
    all_tweets = []

    logger.info(f"총 {len(ACCOUNTS)}개 계정에서 트윗 수집 시작 (Nitter RSS 방식)...")

    for i, account in enumerate(ACCOUNTS):
        logger.info(f"[{i+1}/{len(ACCOUNTS)}] @{account} 수집 중...")

        tweets = get_user_last_tweets(account)
        recent_tweets = filter_recent_tweets(tweets)

        # 트윗에 계정 정보 및 메타데이터 추가
        for tweet in recent_tweets:
            tweet["_account"] = account
            tweet["_engagement_score"] = calculate_engagement_score(tweet)
            # URL이 없으면 생성
            if not tweet.get("_url"):
                tweet_id = tweet.get("id", "")
                if tweet_id:
                    tweet["_url"] = f"https://x.com/{account}/status/{tweet_id}"
                else:
                    tweet["_url"] = f"https://x.com/{account}"

        all_tweets.extend(recent_tweets)
        logger.info(
            f"  -> {len(recent_tweets)}개 최신 트윗 수집 "
            f"(전체 {len(tweets)}개 중)"
        )

        # 서버 부하 방지를 위한 딜레이
        if i < len(ACCOUNTS) - 1:
            time.sleep(REQUEST_DELAY)

    logger.info(f"총 {len(all_tweets)}개 트윗 수집 완료")
    return all_tweets


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # 테스트: 5개 계정
    import config
    original_accounts = config.ACCOUNTS
    config.ACCOUNTS = ["Reuters", "KobeissiLetter", "Cointelegraph", "FoxNews", "zerohedge"]

    print("테스트: 5개 계정 트윗 수집 (Nitter RSS)")
    tweets = fetch_all_tweets()
    print(f"\n총 수집: {len(tweets)}개 트윗")
    for t in tweets[:5]:
        score = t.get("_engagement_score", 0)
        print(f"  [@{t['_account']}][{score:.0f}점] {t.get('text', '')[:80]}...")
        print(f"    URL: {t.get('_url', '')}")

    config.ACCOUNTS = original_accounts
