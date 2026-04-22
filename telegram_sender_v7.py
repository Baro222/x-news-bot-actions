"""
텔레그램 봇 API를 통해 뉴스를 발송하는 모듈 (v7 - 최종)

포스팅 형식:
1. 각 주제별 TOP 1: stockhubkr 스타일 (단일 포스팅)
2. 나머지 뉴스: saveticker 스타일 (랭크 포스팅)
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


def get_sentiment_emoji(engagement_score: float) -> str:
    """참여도 점수에 따른 감정 이모지"""
    if engagement_score >= 50:
        return "🟢"  # 매우 긍정적
    elif engagement_score >= 25:
        return "🟡"  # 중립
    else:
        return "🔴"  # 부정적


def format_stockhubkr_style(category: str, news_item: Dict) -> str:
    """stockhubkr 스타일 - TOP 1 뉴스 (단일 포스팅)"""
    headline = news_item.get("_headline", "")
    summary = news_item.get("_summary", "")
    analysis = news_item.get("_analysis", "")
    account = news_item.get("_account", "")
    engagement_score = news_item.get("_engagement_score", 0)
    
    category_emoji = {
        "암호화폐": "🪙",
        "경제": "💹",
        "뉴스": "📰",
        "지정학": "🌍",
        "트럼프": "🗽",
    }.get(category, "📢")
    
    now_kst = datetime.now(KST)
    timestamp = now_kst.strftime("%Y.%m.%d %H:%M KST")
    
    lines = []
    lines.append(f"<b>{category_emoji} 【{category}】 속보</b>")
    lines.append("")
    lines.append(f"<b>{headline}</b>")
    lines.append("")
    
    # 요약
    if summary:
        lines.append(f"<i>{summary}</i>")
        lines.append("")
    
    # 분석
    if analysis:
        lines.append(f"💡 <b>분석:</b> {analysis}")
        lines.append("")
    
    # 메타 정보
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append(f"📌 출처: @{account}")
    lines.append(f"🕐 {timestamp}")
    
    if engagement_score > 0:
        engagement_bar = "▓" * min(int(engagement_score / 10), 10) + "░" * (10 - min(int(engagement_score / 10), 10))
        lines.append(f"참여도: [{engagement_bar}] {engagement_score:.1f}")
    
    return "\n".join(lines)


def format_saveticker_style(category: str, news_items: List[Dict]) -> str:
    """saveticker 스타일 - 카테고리별 랭크 포스팅"""
    if not news_items:
        return ""
    
    category_emoji = {
        "암호화폐": "🪙",
        "경제": "💹",
        "뉴스": "📰",
        "지정학": "🌍",
        "트럼프": "🗽",
    }.get(category, "📢")
    
    now_kst = datetime.now(KST)
    timestamp = now_kst.strftime("%Y.%m.%d %H:%M KST")
    
    lines = []
    lines.append(f"<b>【{category_emoji} {category}】</b>")
    lines.append(f"<i>{timestamp} 기준</i>")
    lines.append("")
    
    # 각 뉴스 항목
    for idx, item in enumerate(news_items, 1):
        headline = item.get("_headline", "")[:70]
        summary = item.get("_summary", "")
        analysis = item.get("_analysis", "")
        account = item.get("_account", "")
        engagement_score = item.get("_engagement_score", 0)
        
        # 번호 + 제목
        lines.append(f"<b>{idx}. {headline}</b>")
        
        # 요약 (bullet points)
        if summary:
            summary_lines = summary.split('\n')[:2]  # 최대 2줄
            for summary_line in summary_lines:
                if summary_line.strip():
                    lines.append(f"  • {summary_line.strip()[:80]}")
        
        # 분석 의견 (감정 이모지 포함)
        sentiment = get_sentiment_emoji(engagement_score)
        if analysis:
            analysis_text = analysis[:100]
            lines.append(f"{sentiment} <i>{analysis_text}</i>")
        
        # 출처
        lines.append(f"출처: @{account}")
        lines.append("")
    
    return "\n".join(lines)


def send_news_report_v7(ranked_news: Dict[str, List[Dict]]) -> bool:
    """뉴스 발송 (v7 최종 형식)"""
    total_sent = 0
    
    logger.info("뉴스 발송 시작 (v7 형식: stockhubkr TOP 1 + saveticker 랭크)")
    
    # 1단계: 각 카테고리 TOP 1 (stockhubkr 스타일)
    logger.info("1단계: 각 카테고리 TOP 1 뉴스 발송 (stockhubkr 스타일)")
    for category in sorted(ranked_news.keys()):
        items = ranked_news[category]
        if not items:
            continue
        
        top_news = items[0]
        message = format_stockhubkr_style(category, top_news)
        
        if _send_via_bot(message):
            total_sent += 1
            logger.info(f"[{category}] TOP 1 뉴스 발송 완료")
        else:
            logger.error(f"[{category}] TOP 1 뉴스 발송 실패")
    
    # 2단계: 각 카테고리 나머지 뉴스 (saveticker 스타일)
    logger.info("2단계: 카테고리별 나머지 뉴스 발송 (saveticker 스타일)")
    for category in sorted(ranked_news.keys()):
        items = ranked_news[category]
        if len(items) <= 1:
            continue
        
        # TOP 1 제외한 나머지
        remaining_items = items[1:]
        
        message = format_saveticker_style(category, remaining_items)
        if message and _send_via_bot(message):
            total_sent += 1
            logger.info(f"[{category}] 나머지 뉴스 발송 완료 ({len(remaining_items)}개)")
        else:
            logger.error(f"[{category}] 나머지 뉴스 발송 실패")
    
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
                "_analysis": "암호화폐 시장의 강세 신호",
                "_account": "Cointelegraph",
                "_engagement_score": 85.5,
            },
            {
                "_headline": "이더리움 상승세 지속",
                "_summary": "이더리움이 계속 상승하고 있습니다",
                "_analysis": "알트코인 랠리 진행 중",
                "_account": "WuBlockchain",
                "_engagement_score": 42.0,
            },
        ]
    }
    
    send_news_report_v7(test_news)
