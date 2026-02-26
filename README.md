# X 뉴스 자동 수집 & 텔레그램 브리핑 봇

## 개요

X(트위터) **60개 주요 계정**의 포스팅을 **4시간마다** 자동 수집하여 **Gemini AI를 통한 심층 분석**으로 지정학, 경제, 트럼프, 암호화폐 4개 대주제로 분류·요약하고 텔레그램 채널에 **완벽한 한국어**로 자동 발송하는 시스템입니다.

### 주요 특징
- ✅ **Gemini API 기반 AI 분석:** OpenAI 대신 Google Gemini를 사용하여 무료로 운영
- ✅ **완벽한 한국어 지원:** 모든 분석과 요약이 자연스러운 한국어로 제공
- ✅ **4시간 필터링:** 최근 4시간 이내의 최신 뉴스만 엄격하게 선별
- ✅ **심층 분석:** 단순 요약을 넘어 시장 영향, 연관성, 긴급성을 평가
- ✅ **GitHub Actions 자동화:** 별도의 서버 없이 GitHub Actions로 자동 실행

---

## 시스템 구성

```
/home/ubuntu/x-news-bot-actions/
├── config.py                # 설정 파일 (계정 목록, 카테고리 등)
├── twitter_fetcher.py       # X 트윗 수집 모듈 (Nitter RSS 사용)
├── ai_processor.py          # AI 분류·요약·랭킹 처리 모듈 (Gemini API)
├── telegram_sender.py       # 텔레그램 발송 모듈
├── security_manager.py      # 보안 및 환경변수 관리 모듈
├── main.py                  # 메인 실행 스크립트
├── .github/workflows/
│   └── main.yml             # GitHub Actions 워크플로우 (4시간 주기)
├── logs/                    # 로그 파일 디렉토리
│   ├── news_bot.log         # 뉴스봇 실행 로그
│   └── last_result.json     # 마지막 실행 결과
└── README.md                # 이 파일
```

---

## 사전 요구사항

### 1. Google Gemini API 키 (필수)

**[중요]** 이 시스템은 무료 Google Gemini API를 사용합니다.

1. [Google AI Studio](https://aistudio.google.com/) 접속
2. 로그인 후 **"Create API Key"** 클릭
3. 생성된 API 키를 복사
4. GitHub 저장소의 `Settings > Secrets and variables > Actions`에서 `OPENAI_API_KEY` Secret에 등록

**비용:** 완전 무료 (월 1,500만 토큰까지 무료 사용 가능)

### 2. 텔레그램 봇 설정 (필수)

1. Telegram에서 [@BotFather](https://t.me/botfather)와 대화
2. `/newbot` 명령으로 새 봇 생성
3. 생성된 봇 토큰을 GitHub Secrets의 `TELEGRAM_BOT_TOKEN`에 등록
4. 봇을 텔레그램 채널의 관리자로 추가
5. 채널 ID를 GitHub Secrets의 `TELEGRAM_CHANNEL_ID`에 등록 (형식: `-1001234567890`)

### 3. GitHub Actions 설정

GitHub 저장소의 `Settings > Secrets and variables > Actions`에 다음을 등록:

| Secret 이름 | 설명 | 예시 |
|---|---|---|
| `OPENAI_API_KEY` | Google Gemini API 키 | `AIzaSyCOPl...` |
| `TELEGRAM_BOT_TOKEN` | Telegram 봇 토큰 | `123456:ABC-DEF...` |
| `TELEGRAM_CHANNEL_ID` | 텔레그램 채널 ID | `-1001234567890` |

---

## 실행 방법

### GitHub Actions 자동 실행 (권장)

시스템은 GitHub Actions를 통해 **매 4시간마다 자동으로 실행**됩니다.

- **실행 시간:** 매일 00:00, 04:00, 08:00, 12:00, 16:00, 20:00 (UTC 기준)
- **실행 시간:** 약 3-5분

### 수동 실행 (테스트용)

GitHub 저장소의 `Actions` 탭에서:

1. **"X News Bot 4-Hour Update"** 워크플로우 선택
2. **"Run workflow"** 클릭
3. **"Run workflow"** 버튼 클릭

### 로컬 환경에서 실행

```bash
# 저장소 클론
git clone https://github.com/Baro222/x-news-bot-actions.git
cd x-news-bot-actions

# 환경변수 설정
export OPENAI_API_KEY="your_gemini_api_key"
export TELEGRAM_BOT_TOKEN="your_bot_token"
export TELEGRAM_CHANNEL_ID="your_channel_id"

# 의존성 설치
pip install -r requirements.txt

# 실행
python3 main.py
```

---

## 수집 대상 계정 (60개)

### 암호화폐 & 블록체인
@GONOGO_Korea, @hiwhaledegen, @visegrad24, @ralralbral, @dons_korea, @bloomingbit_io, @WuBlockchain, @zoomerfied, @MarioNawfal, @martypartymusic, @InsiderWire, @yang_youngbin, @Future__Walker, @KobeissiLetter, @DegenerateNews, @DeItaone, @BMNRBullz, @CryptoRank_io, @CryptosR_Us, @coinbureau, @BitcoinMagazine, @Eddie9132151, @top7ico, @JA_Maartun, @Darkfost_Coc, @Cointelegraph, @cz_binance, @CryptoHayes

### 정치 & 경제
@TrumpTruthOnX, @zerohedge, @financialjuice, @wallstengine, @faststocknewss, @Barchart, @StockMKTNewz, @marketsday, @BitMNR, @_MAGA_NEWS_, @EleanorTerrett, @saylor, @FirstSquawk, @lookonchain

### 주요 뉴스 매체
@nytimes, @washingtonpost, @CNN, @FoxNews, @axios, @Reuters, @BBCNews, @BBCWorld, @BBCBreaking, @MSNBC, @guardian, @WSJ, @AP, @business, @NBCNews, @ABC, @pizzintwatch, @Busanaz1

---

## 출력 형식 예시

텔레그램 채널에 다음과 같은 형식으로 발송됩니다:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📡 X 뉴스 자동 브리핑
🕐 2026년 02월 26일 16:50 (KST)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 이번 브리핑 요약
  🌍 지정학: 5건
  📊 경제: 4건
  🇺🇸 트럼프: 3건
  ₿ 암호화폐: 8건

총 20건의 주요 소식
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🌍 [지정학적 이슈]
📅 2026.02.26 16:50 KST 기준 주요 소식

1. 러시아-우크라이나 분쟁 심화
  - 러시아가 우크라이나 동부에서 대규모 공세 개시
  - NATO 동맹국들이 긴급 회의 소집하여 대응 방안 모색
  📌 지역 갈등 심화와 국제 안보 긴장 고조
  🔗 원문: @Reuters

...
```

---

## 설정 변경

### 수집 대상 계정 추가/제거

`config.py`의 `ACCOUNTS` 리스트 수정:

```python
ACCOUNTS = [
    "@계정명1",
    "@계정명2",
    ...
]
```

### 수집 시간 범위 변경

`config.py`의 `FETCH_HOURS` 수정 (기본값: 4시간):

```python
FETCH_HOURS = 4  # 최근 4시간 이내 트윗만 수집
```

### 카테고리별 최대 뉴스 수 변경

`config.py`의 `MAX_NEWS_PER_CATEGORY` 수정 (기본값: 10):

```python
MAX_NEWS_PER_CATEGORY = 10  # 카테고리별 최대 10건
MIN_NEWS_PER_CATEGORY = 5   # 카테고리별 최소 5건
```

---

## 비용 구조

| 항목 | 비용 | 비고 |
|------|------|------|
| **Google Gemini API** | **무료** | 월 1,500만 토큰까지 무료 |
| **Nitter RSS (트윗 수집)** | **무료** | 공개 서비스 |
| **Telegram Bot API** | **무료** | 공개 서비스 |
| **GitHub Actions** | **무료** | 월 2,000분까지 무료 |
| **총 예상 비용** | **$0/월** | 완전 무료 |

---

## 문제 해결

### Gemini API 오류 (400 Bad Request)

→ GitHub Secrets의 `OPENAI_API_KEY`가 올바른 Gemini API 키인지 확인
→ API 키가 만료되지 않았는지 확인

### 트윗 수집 0건

→ 해당 계정이 최근 4시간 내 트윗을 올리지 않았을 수 있음
→ `FETCH_HOURS`를 늘려서 테스트

### 텔레그램 발송 실패

→ 봇이 채널의 관리자로 등록되어 있는지 확인
→ 채널 ID가 올바른지 확인 (형식: `-1001234567890`)
→ 봇 토큰이 유효한지 확인

### 한국어 번역 오류

→ Gemini API 프롬프트의 한국어 지시가 정상인지 확인
→ GitHub Actions 로그에서 AI 응답 내용 확인

---

## 로그 확인

### GitHub Actions 로그 확인

1. GitHub 저장소의 `Actions` 탭 방문
2. 원하는 워크플로우 실행 선택
3. `update-news` Job 클릭
4. `Run News Bot` 섹션에서 상세 로그 확인

### 로컬 로그 확인

```bash
# 실시간 로그 확인
tail -f /home/ubuntu/x-news-bot-actions/logs/news_bot.log

# 마지막 실행 결과
cat /home/ubuntu/x-news-bot-actions/logs/last_result.json
```

---

## 기술 스택

| 항목 | 기술 |
|------|------|
| **뉴스 수집** | Nitter RSS Feed |
| **AI 분석** | Google Gemini API |
| **메시징** | Telegram Bot API |
| **자동화** | GitHub Actions (Cron) |
| **언어** | Python 3.11 |
| **배포** | GitHub Actions (서버리스) |

---

## 향후 개선 사항

- [ ] FxTwitter API 연동으로 트윗 수집 안정성 향상
- [ ] 사용자 정의 카테고리 추가 기능
- [ ] 뉴스 필터링 규칙 고도화
- [ ] 다국어 지원 (영어, 중국어 등)
- [ ] 웹 대시보드 추가

---

## 라이선스

MIT License

---

## 문의 및 지원

문제가 발생하거나 기능 개선 요청이 있으시면 GitHub Issues를 통해 알려주세요.

---

**마지막 업데이트:** 2026년 02월 26일
**시스템 상태:** ✅ 정상 작동 중
