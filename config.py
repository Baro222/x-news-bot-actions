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

# 모니터링할 X 계정 목록 (총 73개)
ACCOUNTS = {
    # 🪙 암호화폐 & 블록체인 (28개)
    "crypto": [
        "GONOGO_Korea",
        "hiwhaledegen",
        "visegrad24",
        "ralralbral",
        "dons_korea",
        "bloomingbit_io",
        "WuBlockchain",
        "zoomerfied",
        "MarioNawfal",
        "martypartymusic",
        "InsiderWire",
        "yang_youngbin",
        "Future__Walker",
        "KobeissiLetter",
        "DegenerateNews",
        "DeItaone",
        "BMNRBullz",
        "CryptoRank_io",
        "CryptosR_Us",
        "coinbureau",
        "BitcoinMagazine",
        "Eddie9132151",
        "top7ico",
        "JA_Maartun",
        "Darkfost_Coc",
        "Cointelegraph",
        "cz_binance",
        "CryptoHayes",
    ],
    # 📊 정치 & 경제 (11개)
    "economy": [
        "TrumpTruthOnX",
        "zerohedge",
        "financialjuice",
        "wallstengine",
        "faststocknewss",
        "Barchart",
        "StockMKTNewz",
        "marketsday",
        "BitMNR",
        "MAGA_NEWS",
        "EleanorTerrett",
    ],
    # 📰 주요 뉴스 매체 (16개)
    "news": [
        "nytimes",
        "washingtonpost",
        "CNN",
        "FoxNews",
        "axios",
        "Reuters",
        "BBCNews",
        "BBCWorld",
        "BBCBreaking",
        "MSNBC",
        "guardian",
        "WSJ",
        "AP",
        "business",
        "NBCNews",
        "ABC",
    ],
    # 추가 계정
    "geopolitics": [
        "saylor",
        "FirstSquawk",
        "lookonchain",
        "pizzintwatch",
        "Busanaz1",
    ],
}

# 평탄화된 계정 목록 (호환성)
ACCOUNTS_FLAT = []
for category_accounts in ACCOUNTS.values():
    ACCOUNTS_FLAT.extend(category_accounts)

# 카테고리 정의
CATEGORIES = {
    "암호화폐": "crypto",
    "경제": "economy",
    "뉴스": "news",
    "지정학": "geopolitics",
}

# 수집 시간 범위 (시간) - 24시간으로 확대
FETCH_HOURS = 24

# 카테고리별 최대 뉴스 수
MAX_NEWS_PER_CATEGORY = 10
MIN_NEWS_PER_CATEGORY = 3
