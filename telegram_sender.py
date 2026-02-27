"""
텔레그램 프리미엄 계정(Telethon)을 통해 커스텀 이모지가 포함된
뉴스 브리핑을 채널에 발송하는 모듈
"""

import asyncio
import logging
import subprocess
import json
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)
logger.propagate = True

KST = timezone(timedelta(hours=9))

# ─────────────────────────────────────────────
# TG iOS & macOS Icons (tgmacicons) 커스텀 이모지 ID
# ─────────────────────────────────────────────
CE = {
    # ── X 플랫폼 마크 (Twitter X | @Emoji_Club) ──
    "x_platform":  5440699506389695146,   # X 플랫폼 로고 (@Emoji_Club)
    # ── 카테고리 헤더 (TG iOS & macOS Icons) ──
    "globe":      5323404142809467476,   # ☀  → 글로벌/지구 대체
    "chart":      5321323841782790219,   # 📈  경제
    "flag_us":    5258334469152054985,   # ➡  트럼프 (방향)
    "coin":       5258368777350816286,   # 🪙  암호화폐
    "news":       5258430848218176413,   # 📣  뉴스/브리핑
    # ── 공통 UI ──
    "clock":      5260348422266822411,   # 🕔  시간
    "check":      5257965810634202885,   # ✅  완료
    "link":       5257963315258204021,   # 🔗  링크
    "pin":        5258453452631056344,   # 📌  분석
    "refresh":    5258391252914676042,   # 🔄  다음 업데이트
    "summary":    5258226313285607065,   # 🗂  요약
    "note":       5257965174979042426,   # 📝  메모
    "chart_up":   5323761960829862762,   # 📈  상승
    "info":       5296348778012361146,   # ℹ   정보
    "lightning":  5258152182150077732,   # ⚡  속보
    "eye":        5316727448644103237,   # 👀  주목
    "hourglass":  5429411030960711866,   # ⏳  대기
    "separator":  5258289810082111221,   # ↔  구분선
}

# 카테고리별 커스텀 이모지 매핑
CATEGORY_CUSTOM_EMOJI = {
    "지정학": CE["globe"],
    "경제":   CE["chart_up"],
    "트럼프": CE["lightning"],
    "암호화폐": CE["coin"],
}

CATEGORY_FALLBACK_EMOJI = {
    "지정학": "🌍",
    "경제":   "💹",
    "트럼프": "🇺🇸",
    "암호화폐": "🪙",
}

CATEGORY_DESCRIPTIONS = {
    "지정학": "지정학적 이슈",
    "경제":   "경제 & 금융",
    "트럼프": "트럼프 & 미국 정치",
    "암호화폐": "암호화폐 & 블록체인",
}

# 카테고리별 분석 앞 색깔 이모지
CATEGORY_ANALYSIS_EMOJI = {
    "지정학": "🔴",   # 빨강 - 긴장/위기
    "경제":   "🟡",   # 노랑 - 경제 지표
    "트럼프": "🔵",   # 파랑 - 정치
    "암호화폐": "🟢", # 초록 - 시장
}


def _ce(emoji_id: int, fallback: str = "●") -> str:
    """커스텀 이모지 태그 대신 안전한 유니코드 폴백을 반환합니다.
    환경에서 Telethon/프리미엄 이모지 전송이 불안정하므로, 빠른 복구를 위해
    항상 fallback 유니코드 이모지를 사용하도록 변경합니다.
    """
    # 안전 모드: 커스텀 tg-emoji 태그 대신 유니코드 폴백만 사용
    return fallback


def _send_via_bot(text: str) -> bool:
    """봇 API를 통한 폴백 발송"""
    from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHANNEL_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    payload_json = json.dumps(payload, ensure_ascii=False)
    cmd = ["curl", "-s", "--max-time", "30", "-X", "POST", url,
           "-H", "Content-Type: application/json; charset=utf-8",
           "-d", payload_json]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=35)
        stdout = (result.stdout or '').strip()
        stderr = (result.stderr or '').strip()
        logger.debug(f"curl stdout: {stdout}")
        if stderr:
            logger.debug(f"curl stderr: {stderr}")
        if result.returncode == 0 and stdout:
            try:
                response = json.loads(stdout)
                if not response.get("ok", False):
                    logger.warning(f"봇 API 응답 오류: {response}")
                return response.get("ok", False)
            except Exception as e:
                logger.error(f"봇 API 응답 파싱 실패: {e} - raw: {stdout}")
                return False
    except Exception as e:
        logger.error(f"봇 API 발송 실패: {e}", exc_info=True)
    return False


async def _send_via_telethon(messages: List[str]) -> bool:
    """Telethon(프리미엄 계정)을 통한 커스텀 이모지 메시지 발송"""
    try:
        from telethon import TelegramClient
        from telethon.sessions import StringSession
        from config import (TELEGRAM_API_ID, TELEGRAM_API_HASH,
                            TELEGRAM_SESSION, TELEGRAM_CHANNEL_ID)

        channel_id = int(TELEGRAM_CHANNEL_ID)

        async with TelegramClient(StringSession(TELEGRAM_SESSION),
                                  TELEGRAM_API_ID, TELEGRAM_API_HASH) as client:
            for msg in messages:
                await client.send_message(
                    entity=channel_id,
                    message=msg,
                    parse_mode="html",
                    link_preview=False
                )
                await asyncio.sleep(1)
        return True
    except Exception as e:
        logger.error(f"Telethon 발송 실패: {e}", exc_info=True)
        return False


def send_telegram_message(text: str) -> bool:
    """단일 메시지 발송 (봇 API 사용)"""
    return _send_via_bot(text)


def format_summary_header(ranked_news: Dict[str, List[Dict]]) -> str:
    """전체 요약 헤더 메시지 생성 (커스텀 이모지 포함)"""
    now_kst = datetime.now(KST)
    time_str = now_kst.strftime("%Y년 %m월 %d일 %H:%M")
    total_news = sum(len(items) for items in ranked_news.values())

    lines = []
    lines.append(f'{_ce(CE["x_platform"], "𝕏")} <b>글로벌 뉴스 브리핑</b>')
    lines.append(f'{_ce(CE["clock"], "🕐")} {time_str} (KST)')
    lines.append("━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("")
    lines.append(f'{_ce(CE["summary"], "🗂")} <b>이번 브리핑 요약</b>')

    for category, items in ranked_news.items():
        if items:
            ce_id = CATEGORY_CUSTOM_EMOJI.get(category)
            fb = CATEGORY_FALLBACK_EMOJI.get(category, "●")
            emoji_tag = _ce(ce_id, fb) if ce_id else fb
            lines.append(f"  {emoji_tag} {category}: {len(items)}건")

    lines.append("")
    lines.append(f'{_ce(CE["note"], "🗒")} 총 <b>{total_news}건</b>의 주요 소식')

    return "\n".join(lines)


def format_category_message(category: str, news_items: List[Dict]) -> str:
    """카테고리별 뉴스 메시지 생성 (커스텀 이모지 포함)"""
    ce_id = CATEGORY_CUSTOM_EMOJI.get(category)
    fb = CATEGORY_FALLBACK_EMOJI.get(category, "●")
    emoji_tag = _ce(ce_id, fb) if ce_id else fb
    desc = CATEGORY_DESCRIPTIONS.get(category, category)
    analysis_emoji = CATEGORY_ANALYSIS_EMOJI.get(category, "🔹")

    now_kst = datetime.now(KST)
    time_str = now_kst.strftime("%Y.%m.%d %H:%M KST")

    lines = []
    lines.append(f"{emoji_tag} <b>[{desc}]</b>")
    lines.append(f'<i>{_ce(CE["clock"], "🕐")} {time_str} 기준 주요 소식</i>')
    lines.append("")

    for i, item in enumerate(news_items, 1):
        headline = item.get("_headline", "")
        summary  = item.get("_summary", "")
        analysis = item.get("_analysis", "")
        url      = item.get("_url", "")
        account  = item.get("_account", "")

        # 헤드라인 (항상 노출)
        lines.append(f"<b>{i}. {headline}</b>")

        # 상세 내용을 Expandable Blockquote로 감싸기
        # <blockquote expandable> ... </blockquote> 형식
        detail_lines = []

        if summary:
            summary_lines = [f"- {s.strip()}" for s in summary.split(". ") if s.strip()]
            detail_lines.extend(summary_lines[:3])

        if analysis:
            detail_lines.append(f'{analysis_emoji} {_ce(CE["pin"], "📌")} <i>{analysis}</i>')

        if url:
            detail_lines.append(f'{_ce(CE["link"], "🔗")} <a href="{url}">원문 보기</a> (@{account})')

        if detail_lines:
            inner = "\n".join(detail_lines)
            lines.append(f"<blockquote expandable>{inner}</blockquote>")

        lines.append("")

    return "\n".join(lines)


def send_news_report(ranked_news: Dict[str, List[Dict]]) -> bool:
    """전체 뉴스 보고서를 텔레그램으로 발송"""
    total_news = sum(len(items) for items in ranked_news.values())

    if total_news == 0:
        logger.warning("발송할 뉴스가 없습니다.")
        no_news_msg = (
            f'{_ce(CE["news"], "📣")} <b>글로벌 뉴스 브리핑</b>\n'
            f'{_ce(CE["clock"], "🕐")} {datetime.now(KST).strftime("%Y년 %m월 %d일 %H:%M")} (KST)\n'
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f'{_ce(CE["info"], "ℹ")} 최근 4시간 내 주요 소식이 없습니다.'
        )
        return _send_telethon_or_bot([no_news_msg])

    messages = []

    # 1. 헤더
    messages.append(format_summary_header(ranked_news))

    # 2. 카테고리별
    category_order = ["지정학", "경제", "트럼프", "암호화폐"]
    for category in category_order:
        items = ranked_news.get(category, [])
        if not items:
            continue
        msg = format_category_message(category, items)
        if len(msg) > 4096:
            mid = len(items) // 2
            messages.append(format_category_message(category, items[:mid]))
            messages.append(format_category_message(category, items[mid:]))
        else:
            messages.append(msg)

    # 3. 마무리
    footer = (
        f'{_ce(CE["check"], "✅")} <b>브리핑 완료</b>\n'
        f'{_ce(CE["refresh"], "🔄")} 다음 업데이트: 4시간 후'
    )
    messages.append(footer)

    return _send_telethon_or_bot(messages)


def _send_telethon_or_bot(messages: List[str]) -> bool:
    """Bot API 전용 모드: Telethon 경로를 우회하고 봇 API로만 발송합니다.
    (환경에서 Telethon 실행이 불안정하므로 안전하게 Bot API만 사용)
    """
    # 봇 API로 직접 발송
    success_count = 0
    for msg in messages:
        try:
            if _send_via_bot(msg):
                success_count += 1
        except Exception as e:
            logger.error(f"봇 API 발송 중 예외: {e}")
    logger.info(f"봇 API로 {success_count}/{len(messages)}개 메시지 발송")
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
                "_engagement_score": 5000
            }
        ],
        "경제": [
            {
                "_headline": "미국 12월 무역적자 703억 달러로 확대",
                "_summary": "미국의 12월 무역 적자는 703억 달러로 늘어났으며 전체 적자 역시 사상 최대치 수준. 무역 불균형 심화.",
                "_analysis": "수입 급증과 달러 강세가 복합적으로 작용한 결과.",
                "_url": "https://x.com/KobeissiLetter/status/456",
                "_account": "KobeissiLetter",
                "_engagement_score": 3000
            }
        ],
        "트럼프": [],
        "암호화폐": [
            {
                "_headline": "비트코인 9만 달러 지지선 테스트",
                "_summary": "비트코인이 9만 달러 지지선을 테스트하며 변동성 확대. 기관 매수세 유입 지속.",
                "_analysis": "ETF 자금 유입 감소와 매크로 불확실성이 하방 압력 요인.",
                "_url": "https://x.com/CoinTelegraph/status/789",
                "_account": "CoinTelegraph",
                "_engagement_score": 2000
            }
        ]
    }

    print("테스트 발송 시작...")
    result = send_news_report(sample_news)
    print(f"발송 결과: {'성공' if result else '실패'}")
