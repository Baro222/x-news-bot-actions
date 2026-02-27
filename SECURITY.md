# 보안 규칙 및 운영 정책

> 이 문서는 X 뉴스봇 프로젝트의 보안 규칙과 민감 정보 관리 정책을 정의합니다.

---

## 1. 개인정보 및 기밀 정보 유출 금지

모든 API 키, 세션 토큰, 전화번호, 비밀번호 등 민감 정보는 **절대 외부에 공개하거나 전송하지 않습니다.**

보호 대상 정보 목록:

| 항목 | 설명 | 보관 위치 |
|------|------|-----------|
| 텔레그램 봇 토큰 | 봇 인증 토큰 | `.secure/.vault.enc` (암호화) |
| 텔레그램 API ID/Hash | 프리미엄 계정 API 자격증명 | `.secure/.vault.enc` (암호화) |
| Telethon 세션 문자열 | 프리미엄 계정 세션 | `.secure/.vault.enc` (암호화) |
| 텔레그램 채널 ID | 채널 식별자 | `.secure/.vault.enc` (암호화) |
| twitterapi.io 키 | X 데이터 수집 API 키 | `.secure/.vault.enc` (암호화) |
| OpenAI API 키 | AI 처리 API 키 | `.env` (로컬 전용) |
| 전화번호 | 계정 인증용 | `.secure/.vault.enc` (암호화) |

---

## 2. 보안 폴더 구조

민감 정보는 `.secure/` 폴더에 **AES-256 암호화(Fernet)** 방식으로 저장됩니다.

```
x_news_bot/
├── .secure/           # 보안 폴더 (chmod 700 - 소유자만 접근)
│   ├── .master.key    # 마스터 암호화 키 (chmod 600)
│   └── .vault.enc     # 암호화된 민감 정보 vault
├── .gitignore         # .secure/, .env 등 GitHub 제외 목록
├── .env               # 환경 변수 (로컬 전용, GitHub 제외)
├── .env.example       # 환경 변수 템플릿 (GitHub 업로드 가능)
└── security_manager.py  # 보안 관리 모듈
```

vault 접근 방법:
```python
from security_manager import decrypt_vault
secrets = decrypt_vault()
# secrets['TELEGRAM_BOT_TOKEN'] 등으로 접근
```

---

## 3. GitHub 업로드 보안 규칙

GitHub에 코드를 업로드하기 전에 반드시 아래 절차를 따릅니다.

### 3-1. 업로드 전 보안 검사
```bash
cd /home/ubuntu/x_news_bot
bash pre_github_check.sh
```

검사 항목:
- `.env`, `.secure/` 등 민감 파일 존재 여부
- `config.py` 내 API 키/토큰 패턴 검사
- Python 파일 전체 민감 정보 스캔

### 3-2. GitHub 안전 복사본 생성
```bash
python3.11 security_manager.py
# → /home/ubuntu/x_news_bot_github/ 생성 (민감 정보 마스킹 처리됨)
```

마스킹 처리 내용:
- 모든 API 키 → `YOUR_*_HERE` 플레이스홀더로 대체
- 전화번호 → `+821000000000` 으로 대체
- 세션 문자열 → `YOUR_SESSION_STRING_HERE` 으로 대체

### 3-3. .gitignore 필수 항목
```
.secure/
.env
*.session
*.key
*.enc
logs/
bot.pid
```

---

## 4. API 키 전달 규칙

새로운 API 키 또는 민감 정보를 전달할 때는 다음 규칙을 따릅니다.

1. **전달 경로**: `/home/ubuntu/x_news_bot/.secure/` 폴더를 통해 전달
2. **형식**: `security_manager.py`의 `encrypt_vault()` 함수로 즉시 암호화
3. **채팅 기록**: 민감 정보가 포함된 메시지는 전달 후 삭제 권장
4. **마스킹 확인**: 전달 후 `decrypt_vault()`로 복호화 검증

---

## 5. 보안 사고 예방 체크리스트

### 정기 점검 항목
- [ ] `.secure/` 폴더 권한 확인: `ls -la .secure/` → `drwx------` 이어야 함
- [ ] `.master.key` 권한 확인: `ls -la .secure/.master.key` → `-rw-------` 이어야 함
- [ ] 로그 파일에 민감 정보 포함 여부 확인: `grep -i "token\|key\|password" logs/daemon.log`
- [ ] GitHub 업로드 전 보안 검사 실행

### 위협 시나리오별 대응

| 위협 | 예방 조치 | 대응 방법 |
|------|-----------|-----------|
| API 키 유출 | vault 암호화, .gitignore | 즉시 키 재발급 후 vault 업데이트 |
| 세션 탈취 | 세션 파일 암호화 저장 | 텔레그램에서 세션 강제 종료 |
| 전화번호 노출 | 마스킹 처리 | 해당 채팅 기록 삭제 |
| 봇 토큰 유출 | vault 암호화 | @BotFather에서 토큰 재발급 |
| 서버 침해 | 파일 권한 700/600 설정 | 모든 키 재발급, 세션 초기화 |

---

## 보안 모듈 사용법

```bash
# 보안 시스템 초기화 (vault 생성 + 스캔 + GitHub 복사본 생성)
python3.11 security_manager.py

# GitHub 업로드 전 보안 검사
bash pre_github_check.sh

# vault 내용 확인 (마스킹 처리된 상태로 출력)
python3.11 -c "from security_manager import decrypt_vault, mask_sensitive; v=decrypt_vault(); [print(f'{k}: {mask_sensitive(str(val), k)}') for k,val in v.items()]"
```
