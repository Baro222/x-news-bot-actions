# X 뉴스 자동 수집 & 텔레그램 브리핑 봇

## 개요

X(트위터) 48개 주요 계정의 포스팅을 2시간마다 자동 수집하여 **지정학, 경제, 트럼프, 암호화폐** 4개 대주제로 분류·요약하고 텔레그램 채널에 자동 발송하는 시스템입니다.

---

## 시스템 구성

```
/home/ubuntu/x_news_bot/
├── config.py           # 설정 파일 (API 키, 계정 목록, 카테고리 등)
├── twitter_fetcher.py  # X 트윗 수집 모듈 (twitterapi.io 사용)
├── ai_processor.py     # AI 분류·요약·랭킹 처리 모듈 (GPT-4.1-mini)
├── telegram_sender.py  # 텔레그램 발송 모듈
├── main.py             # 메인 실행 스크립트 (1회 실행)
├── daemon.py           # 2시간 주기 데몬 (백그라운드 실행)
├── scheduler.py        # cron 방식 스케줄러
├── manage.sh           # 데몬 관리 스크립트
├── .env                # 환경변수 (OPENAI_API_KEY)
└── logs/               # 로그 파일 디렉토리
    ├── daemon.log      # 데몬 로그
    ├── news_bot.log    # 뉴스봇 실행 로그
    └── last_result.json # 마지막 실행 결과
```

---

## 사전 요구사항

### 1. twitterapi.io 크레딧 충전 (필수)

**[중요]** 현재 twitterapi.io 계정의 크레딧이 소진되었습니다.

1. [twitterapi.io 대시보드](https://twitterapi.io) 접속
2. 로그인 후 크레딧 충전
3. 비용 구조:
   - 트윗 1,000건 조회: **$0.15**
   - 48개 계정 × 20트윗 = 960건 → 약 **$0.144/회**
   - 2시간 주기 × 12회/일 = **약 $1.73/일** (약 $52/월)

### 2. 환경변수 확인

```bash
cat /home/ubuntu/x_news_bot/.env
# OPENAI_API_KEY=sk-...
```

---

## 실행 방법

### 즉시 1회 실행

```bash
cd /home/ubuntu/x_news_bot
python3.11 main.py
```

### 데몬 시작 (2시간 자동 반복)

```bash
cd /home/ubuntu/x_news_bot
bash manage.sh start
```

### 데몬 상태 확인

```bash
bash manage.sh status
```

### 데몬 중지

```bash
bash manage.sh stop
```

### 데몬 재시작

```bash
bash manage.sh restart
```

---

## 출력 형식 예시

텔레그램 채널에 다음과 같은 형식으로 발송됩니다:

```
━━━━━━━━━━━━━━━━━━━━━━
📡 글로벌 뉴스 브리핑
🕐 2026년 02월 22일 22:00 (KST)
━━━━━━━━━━━━━━━━━━━━━━

📋 이번 브리핑 요약
  🌍 지정학: 5건
  📊 경제: 4건
  🇺🇸 트럼프: 3건
  ₿ 암호화폐: 6건

총 18건의 주요 소식
━━━━━━━━━━━━━━━━━━━━━━

---

🌍 [지정학적 이슈]
📅 2026.02.22 22:00 KST 기준 주요 소식

1. 러시아 우크라이나 동부 대규모 공세 개시
  - 러시아가 우크라이나 동부에서 대규모 공세 개시
  - NATO 동맹국들이 긴급 회의 소집하여 대응 방안 모색
  📌 지역 갈등 심화와 국제 안보 긴장 고조 배경
  🔗 원문 보기 (@Reuters)

...
```

---

## 설정 변경

### 계정 추가/제거

`config.py`의 `ACCOUNTS` 리스트 수정:

```python
ACCOUNTS = [
    "계정명1",
    "계정명2",
    ...
]
```

### 수집 시간 범위 변경

`config.py`의 `FETCH_HOURS` 수정 (기본값: 2시간):

```python
FETCH_HOURS = 2  # 최근 2시간 이내 트윗만 수집
```

### 카테고리별 최대 뉴스 수 변경

`config.py`의 `MAX_NEWS_PER_CATEGORY` 수정 (기본값: 10):

```python
MAX_NEWS_PER_CATEGORY = 10  # 카테고리별 최대 10건
```

---

## 비용 구조

| 항목 | 비용 |
|------|------|
| twitterapi.io | ~$1.73/일 (2시간 주기 기준) |
| OpenAI GPT-4.1-mini | ~$0.05/회 (22트윗 기준) |
| **총 예상 비용** | **~$2/일 (약 $60/월)** |

---

## 문제 해결

### "Credits is not enough" 오류

→ twitterapi.io 대시보드에서 크레딧 충전 필요

### 텔레그램 발송 실패

→ 봇이 채널의 관리자로 등록되어 있는지 확인
→ 채널 ID가 올바른지 확인 (`-1000000000000`)

### 트윗 수집 0건

→ 해당 계정이 최근 2시간 내 트윗을 올리지 않았을 수 있음
→ `FETCH_HOURS`를 늘려서 테스트

---

## 로그 확인

```bash
# 실시간 로그 확인
tail -f /home/ubuntu/x_news_bot/logs/daemon.log

# 마지막 실행 결과
cat /home/ubuntu/x_news_bot/logs/last_result.json
```
