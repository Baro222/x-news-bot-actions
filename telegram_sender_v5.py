"""
텔레그램 봇 API를 통해 뉴스를 발송하는 모듈 (v5)

개선사항:
1. wojaklisting 스타일 - 단일 뉴스 포스팅 (TOP 1, 공지형)
2. baroBTC 스타일 - 카테고리별 요약 리스트
3. 전체 요약 포스팅
4. 한글 포스팅
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


def format_wojaklisting_style(category: str, news_item: Dict) -> str:
    """wojaklisting 스타일 - 단일 뉴스 포스팅 (공지형)"""
    headline = news_item.get("_headline", "")
    summary = news_item.get("_summary", "")
    account = news_item.get("_account", "")
    engagement_score = news_item.get("_engagement_score", 0)
    url = news_item.get("_url", "")
    
    category_emoji = {
        "암호화폐": "🪙",
        "경제": "💹",
        "뉴스": "📰",
        "지정학": "🌍",
    }.get(category, "📢")
    
    now_kst = datetime.now(KST)
    timestamp = now_kst.strftime("%Y. %m. %d. %H:%M KST")
    
    lines = []
    lines.append(f"<b>{category_emoji} 【{category} 속보】</b>")
    lines.append("")
    lines.append(f"<b>{headline}</b>")
    lines.append("")
    
    # 요약
    if summary:
        lines.append(f"<i>{summary[:200]}</i>")
        lines.append("")
    
    # 정보 박스
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append(f"📌 출처: @{account}")
    lines.append(f"🕐 시간: {timestamp}")
    if engagement_score > 0:
        engagement_bar = "▓" * min(int(engagement_score / 10), 10) + "░" * (10 - min(int(engagement_score / 10), 10))
        lines.append(f"참여도: [{engagement_bar}] {engagement_score:.1f}")
    
    if url:
        lines.append(f"<a href=\"{url}\">원문 보기</a>")
    
    return "\n".join(lines)


def format_barobtc_summary_style(ranked_news: Dict[str, List[Dict]]) -> str:
    """baroBTC 스타일 - 전체 요약 리스트"""
    now_kst = datetime.now(KST)
    timestamp = now_kst.strftime("%Y년 %m월 %d일 %H:%M (KST)")
    
    lines = []
    lines.append("<b>🤖 X 뉴스 봇 브리핑</b>")
    lines.append(timestamp)
    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("")
    
    # 카테고리별 요약
    total_news = 0
    for category in sorted(ranked_news.keys()):
        items = ranked_news[category]
        if items:
            count = len(items)
            total_news += count
            lines.append(f"📊 {category}: <b>{count}건</b>")
    
    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append(f"<b>총 {total_news}개의 주요 소식</b>")
    
    return "\n".join(lines)


def format_category_summary_style(category: str, news_items: List[Dict]) -> str:
    """카테고리별 요약 - baroBTC 스타일"""
    if not news_items:
        return ""
    
    category_emoji = {
        "암호화폐": "🪙",
        "경제": "💹",
        "뉴스": "📰",
        "지정학": "🌍",
    }.get(category, "📢")
    
    now_kst = datetime.now(KST)
    timestamp = now_kst.strftime("%Y년 %m월 %d일 %H:%M (KST)")
    
    lines = []
    lines.append(f"<b>{category_emoji} 【{category} 뉴스 브리핑】</b>")
    lines.append(timestamp)
    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("")
    
    # TOP 1 제외한 나머지 뉴스
    for idx, item in enumerate(news_items[1:], 1):
        headline = item.get("_headline", "")[:80]
        account = item.get("_account", "")
        engagement_score = item.get("_engagement_score", 0)
        url = item.get("_url", "")
        
        # 번호 + 제목
        lines.append(f"<b>{idx}. {headline}</b>")
        
        # 출처 + 참여도
        if engagement_score > 0:
            engagement_bar = "▓" * min(int(engagement_score / 10), 5) + "░" * (5 - min(int(engagement_score / 10), 5))
            lines.append(f"📌 @{account} | 참여도: [{engagement_bar}]")
        else:
            lines.append(f"📌 @{account}")
        
        if url:
            lines.append(f"<a href=\"{url}\">원문 보기</a>")
        
        lines.append("")
    
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append(f"<b>총 {len(news_items)}개 뉴스</b>")
    
    return "\n".join(lines)


def send_news_report_v5(ranked_news: Dict[str, List[Dict]]) -> bool:
    """뉴스 발송 (v5 형식)"""
    total_sent = 0
    
    # 1단계: 각 카테고리 TOP 1 별도 발송 (wojaklisting 스타일)
    logger.info("1단계: TOP 1 뉴스 발송 (wojaklisting 스타일)")
    for category in sorted(ranked_news.keys()):
        items = ranked_news[category]
        if not items:
            continue
        
        top_news = items[0]
        message = format_wojaklisting_style(category, top_news)
        
        if _send_via_bot(message):
            total_sent += 1
            logger.info(f"[{category}] TOP 1 발송 완료")
        else:
            logger.error(f"[{category}] TOP 1 발송 실패")
    
    # 2단계: 각 카테고리 나머지 뉴스 요약 발송 (baroBTC 스타일)
    logger.info("2단계: 카테고리별 요약 발송 (baroBTC 스타일)")
    for category in sorted(ranked_news.keys()):
        items = ranked_news[category]
        if len(items) <= 1:
            continue
        
        message = format_category_summary_style(category, items)
        if message and _send_via_bot(message):
            total_sent += 1
            logger.info(f"[{category}] 요약 발송 완료")
    
    # 3단계: 전체 요약 발송
    logger.info("3단계: 전체 요약 발송")
    summary_message = format_barobtc_summary_style(ranked_news)
    if summary_message and _send_via_bot(summary_message):
        total_sent += 1
        logger.info("전체 요약 발송 완료")
    
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
    
    send_news_report_v5(test_news)
