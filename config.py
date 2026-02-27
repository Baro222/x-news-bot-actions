# 설정 파일
# 모든 민감 정보는 환경변수 또는 GitHub Secrets에서 가져옵니다.
# 로컬 실행 시: .env 파일에 설정 (절대 GitHub에 업로드 금지)

import os

# twitterapi.io API 키
TWITTER_API_KEY = os.environ.get("TWITTER_API_KEY", "")

# 텔레그램 봇 토큰
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")

# 텔레그램 채널 ID
TELEGRAM_CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID", "")

# 텔레그램 프리미엄 계정 (Telethon - 커스텀 이모지 사용)
TELEGRAM_API_ID = int(os.environ.get("TELEGRAM_API_ID", "0") or "0")
TELEGRAM_API_HASH = os.environ.get("TELEGRAM_API_HASH", "")
TELEGRAM_SESSION = os.environ.get("TELEGRAM_SESSION", "")

# OpenAI API 키
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

# 모니터링할 X 계정 목록
ACCOUNTS = [
    "GONOGO_Korea",
    "hiwhaledegen",
    "visegrad24",
    "ralralbral",
    "dons_korea",
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
    "TrumpTruthOnX",
    "zerohedge",
    "financialjuice",
    "wallstengine",
    "faststocknewss",
    "Barchart",
    "StockMKTNewz",
    "marketsday",
    "BitMNR",
    "_MAGA_NEWS_",
    "EleanorTerrett",
    "saylor",
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
    "pizzintwatch",
    "Busanaz1",
    "cz_binance",
    "FirstSquawk",
    "lookonchain",
    "CryptoHayes",
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
