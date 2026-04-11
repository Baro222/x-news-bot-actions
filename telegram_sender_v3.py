"""
텔레그램 봇 API를 통해 뉴스를 발송하는 모듈 (v3)

개선사항:
1. 각 주제별 TOP 1은 별도 메시지로 발송 (브레이킹 뉴스 스타일)
2. 나머지는 카테고리별 그룹 메시지로 발송
3. 한글 포스팅 형식 최적화
4. 참여도 점수 기반 우선순위 표시
"""

import subprocess
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)
logger.propagate = True

KST = timezone(timedelta(hours=9))


def _send_via_bot(text: str, parse_mode: str = "HTML") -> bool:
    """봇 API를 통한 메시지 발송"""
    from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHANNEL_ID,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": True
    }
    payload_json = json.dumps(payload, ensure_ascii=False)
    cmd = ["curl", "-s", "--max-time", "30", "-X", "POST", url,
           "-H", "Content-Type: application/json; charset=utf-8",
           "-d", payload_json]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=35)
        stdout = (result.stdout or '').strip()
        if result.returncode == 0 and stdout:
            try:
                response = json.loads(stdout)
                if not response.get("ok", False):
                    logger.warning(f"봇 API 응답 오류: {response}")
                return response.get("ok", False)
            except Exception as e:
                logger.error(f"봇 API 응답 파싱 실패: {e}")
                return False
    except Exception as e:
        logger.error(f"봇 API 발송 실패: {e}", exc_info=True)
    return False


def format_top_news_message(category: str, news_item: Dict) -> str:
    """각 주제별 TOP 1 뉴스 - 브레이킹 뉴스 스타일"""
    headline = news_item.get("_headline", "")
    summary = news_item.get("_summary", "")
    url = news_item.get("_url", "")
    account = news_item.get("_account", "")
    engagement_score = news_item.get("_engagement_score", 0)
    
    category_emoji = {
        "암호화폐": "🪙",
        "경제": "💹",
        "뉴스": "📰",
        "지정학": "🌍",
    }.get(category, "📢")
    
    lines = []
    lines.append(f"<b>{category_emoji} 【{category}】 속보</b>")
    lines.append("")
    lines.append(f"<b>{headline}</b>")
    lines.append("")
    
    if summary:
        lines.append(f"<i>{summary}</i>")
        lines.append("")
    
    # 참여도 표시
    if engagement_score > 0:
        engagement_bar = "▓" * min(int(engagement_score / 10), 10) + "░" * (10 - min(int(engagement_score / 10), 10))
        lines.append(f"참여도: [{engagement_bar}] {engagement_score:.1f}")
        lines.append("")
    
    lines.append(f"📌 @{account}")
    
    if url:
        lines.append(f"<a href=\"{url}\">원문 보기</a>")
    
    return "\n".join(lines)


def format_category_news_message(category: str, news_items: List[Dict]) -> str:
    """카테고리별 그룹 뉴스 메시지"""
    if not news_items:
        return ""
    
    category_emoji = {
        "암호화폐": "🪙",
        "경제": "💹",
        "뉴스": "📰",
        "지정학": "🌍",
    }.get(category, "📢")
    
    lines = []
    lines.append(f"<b>{category_emoji} 【{category}】 뉴스 모음</b>")
    lines.append("")
    
    for idx, item in enumerate(news_items[1:], 2):  # TOP 1 제외
        headline = item.get("_headline", "")[:80]
        account = item.get("_account", "")
        engagement_score = item.get("_engagement_score", 0)
        
        # 참여도 표시
        engagement_bar = "▓" * min(int(engagement_score / 10), 5) + "░" * (5 - min(int(engagement_score / 10), 5))
        
        lines.append(f"<b>{idx}.</b> {headline}")
        lines.append(f"   [{engagement_bar}] @{account}")
        lines.append("")
    
    return "\n".join(lines)


def send_news_report_v3(ranked_news: Dict[str, List[Dict]]) -> bool:
    """뉴스 발송 (v3 형식)"""
    total_sent = 0
    
    # 1단계: 각 카테고리 TOP 1 별도 발송
    for category in sorted(ranked_news.keys()):
        items = ranked_news[category]
        if not items:
            continue
        
        top_news = items[0]
        message = format_top_news_message(category, top_news)
        
        if _send_via_bot(message):
            total_sent += 1
            logger.info(f"[{category}] TOP 1 발송 완료")
        else:
            logger.error(f"[{category}] TOP 1 발송 실패")
    
    # 2단계: 각 카테고리 나머지 뉴스 그룹 발송
    for category in sorted(ranked_news.keys()):
        items = ranked_news[category]
        if len(items) <= 1:
            continue
        
        message = format_category_news_message(category, items)
        if message and _send_via_bot(message):
            total_sent += 1
            logger.info(f"[{category}] 그룹 뉴스 발송 완료")
    
    logger.info(f"뉴스 발송 완료: {total_sent}개 메시지 발송")
    return total_sent > 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # 테스트
    test_news = {
        "암호화폐": [
            {
                "_headline": "비트코인 신고가 돌파",
                "_summary": "비트코인이 역사적 신고가를 기록했습니다",
                "_url": "https://x.com/test",
                "_account": "Cointelegraph",
                "_engagement_score": 85.5,
            },
            {
                "_headline": "이더리움 상승세 지속",
                "_summary": "이더리움이 계속 상승하고 있습니다",
                "_url": "https://x.com/test2",
                "_account": "WuBlockchain",
                "_engagement_score": 42.0,
            },
        ]
    }
    
    send_news_report_v3(test_news)
