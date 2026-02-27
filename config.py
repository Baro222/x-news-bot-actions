# 설정 파일

# twitterapi.io API 키
TWITTER_API_KEY = "new1_23710e6a69be4ad68f60d24285c99a2f"

# 텔레그램 봇 토큰
TELEGRAM_BOT_TOKEN = "8237707628:AAHQRzAzayLpSsgKpSe1KO3nBeGS8KY_RHU"

# 텔레그램 채널 ID (앞에 -100 추가)
TELEGRAM_CHANNEL_ID = "-1001645099595"

# 텔레그램 프리미엄 계정 (Telethon - 커스텀 이모지 사용)
TELEGRAM_API_ID = 39695050
TELEGRAM_API_HASH = "1107f6b4296cf6fcf30ab09604e85111"
TELEGRAM_SESSION = "1BVtsOIIBu1SJGtmzYt3ox3qiB2st_IcdOPR2RKs4wqgGcaez1xbYP65TI8zSVHbAKVjg85tzkyfU2gBZjRRiBTApuiHGt-LTxrMUlBThVyH4g703lQ7GKylKUvuS6N-utGZhpw1v6IaiqOEaBOHllm7IZt4Kiwx_-sGEjkRIdPSbKGc61skoBVf62td5-ffY9n3ys7MLC2_SdyMRIvFTcwvg_l1vZtrRciTe1ytTMew-w02Az47ZMHXxE0Gs3NuF1GazJjLUF-GwlD5gKkkCj_kIX2sjvrzbKlmcxN52mvBS_au419TJ229Q4OEtthf0cZEsxUDxVN5ujSUwlfdTcbI8PbYM8kU="

# OpenAI API 키 (환경변수에서 가져옴)
import os
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
