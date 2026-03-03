# 설정 파일
# 모든 민감 정보는 환경변수 또는 GitHub Secrets에서 가져옵니다.
# 로컬 실행 시: .env 파일에 설정 (절대 GitHub에 업로드 금지)

import os

# twitterapi.io API 키 (현재 미사용 - Nitter RSS 방식)
TWITTER_API_KEY = os.environ.get("TWITTER_API_KEY", "")

# 텔레그램 봇 토큰
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")

# 텔레그램 채널 ID
TELEGRAM_CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID", "-1003683270211")

# 텔레그램 프리미엄 계정 (Telethon - 커스텀 이모지 사용)
# TELEGRAM_API_ID 안전한 변환 (숫자가 아닌 경우 0으로 설정)
try:
    api_id_str = os.environ.get("TELEGRAM_API_ID", "0") or "0"
    TELEGRAM_API_ID = int(api_id_str) if api_id_str.isdigit() else 0
except (ValueError, TypeError):
    TELEGRAM_API_ID = 0
TELEGRAM_API_HASH = os.environ.get("TELEGRAM_API_HASH", "")
TELEGRAM_SESSION = os.environ.get("TELEGRAM_SESSION", "")

# OpenAI 호환 API 키 (Gemini, OpenAI, 기타 호환 서비스)
# Gemini 사용 시: OPENAI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

# AI 모델명 (환경변수로 오버라이드 가능)
AI_MODEL = os.environ.get("AI_MODEL", "gemini-2.0-flash")

# 모니터링할 X 계정 목록 (테스트용 5개로 극도로 축소 - GitHub Actions 타임아웃 방지)
ACCOUNTS = [
    "visegrad24",           # 지정학
    "TrumpTruthOnX",        # 트럼프
    "zerohedge",            # 경제
    "Cointelegraph",        # 암호화폐
    "nytimes",              # 뉴스
]

# 카테고리 정의
CATEGORIES = {
    "지정학": "geopolitics",
    "경제": "economy",
    "트럼프": "trump",
    "암호화폐": "crypto",
}

# 수집 시간 범위 (시간)
FETCH_HOURS = 4

# 카테고리별 최대 뉴스 수
MAX_NEWS_PER_CATEGORY = 10
MIN_NEWS_PER_CATEGORY = 5
