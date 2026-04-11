"""
텔레그램 봇 API를 통해 뉴스를 발송하는 모듈 (v2)

개선사항:
1. 각 주제별 TOP 1은 별도 메시지로 발송 (브레이킹 뉴스 스타일)
2. 나머지는 카테고리별 그룹 메시지로 발송
3. 한글 포스팅 형식 (예시: stockhubkr, coinaiai_report 스타일)
4. 좋아요/조회수 기반 우선순위 표시
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
    """각 주제별 TOP 1 뉴스 - 브레이킹 뉴스 스타일 포스팅"""
    headline = news_item.get("_headline", "")
    summary = news_item.get("_summary", "")
    analysis = news_item.get("_analysis", "")
    url = news_item.get("_url", "")
    account = news_item.get("_account", "")
    
    # 카테고리 이모지
    category_emoji = {
        "지정학": "🌍",
        "경제": "💹",
        "트럼프": "🇺🇸",
        "암호화폐": "🪙",
    }.get(category, "📰")
    
    lines = []
    lines.append(f"<b>{category_emoji} [{category}] 속보</b>")
    lines.append("")
    lines.append(f"<b>{headline}</b>")
    lines.append("")
    
    if summary:
        lines.append(f"<i>📰 {summary}</i>")
        lines.append("")
    
    if analysis:
        lines.append(f"💡 {analysis}")
        lines.append("")
    
    # 참여도 정보
    likes = news_item.get("likeCount", 0)
    views = news_item.get("viewCount", 0)
    if likes or views:
        engagement = []
        if likes:
            engagement.append(f"👍 {likes:,}개")
        if views:
            engagement.append(f"👁️ {views:,}개")
        lines.append(f"<i>반응: {' | '.join(engagement)}</i>")
        lines.append("")
    
    if url:
        lines.append(f"🔗 <a href=\"{url}\">원문 보기</a> (@{account})")
    
    return "\n".join(lines)


def format_category_news_group(category: str, news_items: List[Dict]) -> str:
    """카테고리별 나머지 뉴스 - 그룹 포스팅"""
    if not news_items:
        return ""
    
    category_emoji = {
        "지정학": "🌍",
        "경제": "💹",
        "트럼프": "🇺🇸",
        "암호화폐": "🪙",
    }.get(category, "📰")
    
    now_kst = datetime.now(KST)
    time_str = now_kst.strftime("%m월 %d일 %H:%M")
    
    lines = []
    lines.append(f"<b>{category_emoji} [{category}] 주요 뉴스</b>")
    lines.append(f"<i>📅 {time_str} 기준</i>")
    lines.append("")
    
    for i, item in enumerate(news_items, 1):
        headline = item.get("_headline", "")
        summary = item.get("_summary", "")
        url = item.get("_url", "")
        account = item.get("_account", "")
        
        lines.append(f"<b>{i}. {headline}</b>")
        
        if summary:
            # 요약을 짧게 (최대 100자)
            summary_short = summary[:100] + ("..." if len(summary) > 100 else "")
            lines.append(f"<i>{summary_short}</i>")
        
        if url:
            lines.append(f"🔗 <a href=\"{url}\">보기</a>")
        
        lines.append("")
    
    return "\n".join(lines).strip()


def send_news_report_v2(ranked_news: Dict[str, List[Dict]]) -> bool:
    """
    개선된 뉴스 보고서 발송
    
    1. 각 카테고리 TOP 1 → 별도 메시지 (브레이킹 뉴스 스타일)
    2. 나머지 → 카테고리별 그룹 메시지
    3. 마무리 메시지
    """
    total_news = sum(len(items) for items in ranked_news.values())
    
    if total_news == 0:
        logger.warning("발송할 뉴스가 없습니다.")
        no_news_msg = (
            "📣 <b>글로벌 뉴스 브리핑</b>\n"
            f"🕐 {datetime.now(KST).strftime('%Y년 %m월 %d일 %H:%M')} (KST)\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "ℹ️ 최근 4시간 내 주요 소식이 없습니다."
        )
        return _send_via_bot(no_news_msg)
    
    messages = []
    success_count = 0
    
    # 1. 헤더 메시지
    now_kst = datetime.now(KST)
    time_str = now_kst.strftime("%Y년 %m월 %d일 %H:%M")
    header = (
        "📣 <b>글로벌 뉴스 브리핑</b>\n"
        f"🕐 {time_str} (KST)\n"
        "━━━━━━━━━━━━━━━━━━━━━━"
    )
    if _send_via_bot(header):
        success_count += 1
    
    # 2. 카테고리별 TOP 1 발송 (브레이킹 뉴스 스타일)
    category_order = ["지정학", "경제", "트럼프", "암호화폐"]
    for category in category_order:
        items = ranked_news.get(category, [])
        if not items:
            continue
        
        # TOP 1 메시지
        top_msg = format_top_news_message(category, items[0])
        if _send_via_bot(top_msg):
            success_count += 1
        
        # 나머지 뉴스 (2개 이상 있을 때만)
        if len(items) > 1:
            group_msg = format_category_news_group(category, items[1:])
            if group_msg and _send_via_bot(group_msg):
                success_count += 1
    
    # 3. 마무리 메시지
    footer = (
        "✅ <b>브리핑 완료</b>\n"
        "🔄 다음 업데이트: 4시간 후"
    )
    if _send_via_bot(footer):
        success_count += 1
    
    logger.info(f"뉴스 발송 완료: {success_count}개 메시지 발송")
    return success_count > 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')
    
    # 테스트 발송
    sample_news = {
        "지정학": [
            {
                "_headline": "러시아-우크라이나 휴전 협상 재개",
                "_summary": "미국의 중재로 양측 협상 테이블 복귀. 30일 내 임시 휴전 가능성 제기.",
                "_analysis": "트럼프 행정부의 외교적 압박이 협상 재개의 주요 동인.",
                "_url": "https://x.com/Reuters/status/123",
                "_account": "Reuters",
                "likeCount": 5000,
                "viewCount": 50000
            },
            {
                "_headline": "나토, 동유럽 방어력 강화",
                "_summary": "나토가 폴란드, 발트 3국에 추가 병력 배치 결정.",
                "_analysis": "러시아의 위협 증가에 대한 대응 조치.",
                "_url": "https://x.com/NATO/status/456",
                "_account": "NATO",
                "likeCount": 3000,
                "viewCount": 30000
            }
        ],
        "경제": [
            {
                "_headline": "미국 12월 무역적자 703억 달러로 확대",
                "_summary": "미국의 12월 무역 적자는 703억 달러로 늘어났으며 전체 적자 역시 사상 최대치 수준.",
                "_analysis": "수입 급증과 달러 강세가 복합적으로 작용한 결과.",
                "_url": "https://x.com/KobeissiLetter/status/789",
                "_account": "KobeissiLetter",
                "likeCount": 3000,
                "viewCount": 25000
            }
        ],
        "트럼프": [],
        "암호화폐": [
            {
                "_headline": "비트코인 9만 달러 지지선 테스트",
                "_summary": "비트코인이 9만 달러 지지선을 테스트하며 변동성 확대. 기관 매수세 유입 지속.",
                "_analysis": "ETF 자금 유입 감소와 매크로 불확실성이 하방 압력 요인.",
                "_url": "https://x.com/CoinTelegraph/status/101",
                "_account": "CoinTelegraph",
                "likeCount": 2000,
                "viewCount": 20000
            },
            {
                "_headline": "이더리움 스테이킹 보상률 상승",
                "_summary": "이더리움 스테이킹 보상률이 3.5%로 상승하며 참여 증가.",
                "_analysis": "네트워크 활동 증가와 검증자 수 감소의 결과.",
                "_url": "https://x.com/ethereum/status/202",
                "_account": "ethereum",
                "likeCount": 1500,
                "viewCount": 15000
            }
        ]
    }
    
    print("테스트 발송 시작...")
    result = send_news_report_v2(sample_news)
    print(f"발송 결과: {'성공' if result else '실패'}")
