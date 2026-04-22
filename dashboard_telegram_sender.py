"""
대시보드 데이터를 텔레그램으로 송출하는 모듈

기능:
1. GitHub에서 processed_news.json 다운로드
2. 텔레그램 메시지 생성
3. 텔레그램 봇 API로 발송
"""

import json
import subprocess
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional
import requests

logger = logging.getLogger(__name__)
logger.propagate = True

KST = timezone(timedelta(hours=9))

GITHUB_RAW_URL = "https://raw.githubusercontent.com/Baro222/x-news-bot-actions/main/dashboard/public/processed_news.json"


def fetch_dashboard_data() -> Optional[Dict]:
    """GitHub에서 대시보드 데이터 다운로드"""
    try:
        response = requests.get(GITHUB_RAW_URL, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Failed to fetch dashboard data: {e}")
        return None


def format_telegram_message(data: Dict) -> str:
    """대시보드 데이터를 텔레그램 메시지로 포맷"""
    if not data or "news" not in data:
        return "데이터를 불러올 수 없습니다."

    news_items = data.get("news", [])
    system_status = data.get("systemStatus", {})

    lines = []

    # 헤더
    lines.append("🚀 <b>X News Dashboard Report</b>")
    lines.append("")

    # 시스템 상태
    lines.append("📊 <b>시스템 상태</b>")
    lines.append(f"상태: {system_status.get('systemHealth', 'unknown')}")
    lines.append(f"가동시간: {system_status.get('uptime', 'N/A')}")
    lines.append(f"팔로업 계정: {system_status.get('totalAccounts', 0)}개")
    lines.append(f"수집된 뉴스: {system_status.get('aiAnalysisCount', 0)}개")
    lines.append("")

    # TOP 5 뉴스
    lines.append("🔥 <b>주요 뉴스 TOP 5</b>")
    lines.append("")

    for idx, news in enumerate(news_items[:5], 1):
        title = news.get("title", "")[:60]
        source = news.get("source", "unknown")
        engagement = news.get("engagement", {})
        score = engagement.get("score", 0)
        category = news.get("category", "")

        # 색상 이모지
        emoji = "🟢" if score >= 70 else "🟡" if score >= 40 else "🔴"

        lines.append(f"{idx}. {emoji} {title}")
        lines.append(f"   출처: {source} | 참여도: {score:.1f}")
        lines.append("")

    # 카테고리별 통계
    lines.append("<b>카테고리별 뉴스 수</b>")
    category_counts: Dict[str, int] = {}
    for news in news_items:
        cat = news.get("category", "기타")
        category_counts[cat] = category_counts.get(cat, 0) + 1

    for cat, count in sorted(category_counts.items()):
        lines.append(f"  • {cat}: {count}개")

    lines.append("")

    # 풋터
    timestamp = datetime.now(KST).strftime("%Y.%m.%d %H:%M KST")
    lines.append(f"📅 {timestamp}")
    lines.append("🔗 <a href=\"https://xnewsdash-6tbs7ebv.manus.space/dashboard\">대시보드 보기</a>")

    return "\n".join(lines)


def send_to_telegram(message: str) -> bool:
    """텔레그램 봇 API로 메시지 발송"""
    from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": TELEGRAM_CHANNEL_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }

    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()

        if result.get("ok"):
            logger.info("대시보드 메시지 발송 완료")
            return True
        else:
            logger.error(f"텔레그램 API 오류: {result}")
            return False

    except Exception as e:
        logger.error(f"텔레그램 발송 실패: {e}")
        return False


def send_dashboard_report() -> bool:
    """대시보드 리포트 발송"""
    logger.info("대시보드 리포트 발송 시작...")

    # 1. 데이터 다운로드
    data = fetch_dashboard_data()
    if not data:
        logger.error("대시보드 데이터 다운로드 실패")
        return False

    # 2. 메시지 포맷
    message = format_telegram_message(data)

    # 3. 텔레그램 발송
    success = send_to_telegram(message)

    if success:
        logger.info("대시보드 리포트 발송 완료")
    else:
        logger.error("대시보드 리포트 발송 실패")

    return success


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    send_dashboard_report()
