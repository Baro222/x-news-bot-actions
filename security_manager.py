"""
보안 관리 모듈
- 민감 정보 암호화/복호화 (AES-256 기반 Fernet)
- API 키 및 개인정보 마스킹
- GitHub 업로드 전 보안 검사
- 보안 폴더 관리
"""

import os
import re
import json
import base64
import hashlib
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# 보안 폴더 경로
SECURE_DIR = Path(__file__).parent / ".secure"
KEY_FILE   = SECURE_DIR / ".master.key"
VAULT_FILE = SECURE_DIR / ".vault.enc"

# GitHub 업로드 시 검사할 민감 패턴
SENSITIVE_PATTERNS = [
    # API 키 / 토큰
    (r'[0-9]{8,10}:[A-Za-z0-9_\-]{30,50}',        "텔레그램 봇 토큰"),
    (r'[0-9]{7,10}',                                "텔레그램 API ID (숫자)"),
    (r'[a-f0-9]{32}',                               "텔레그램 API Hash"),
    (r'new1_[a-f0-9]{32}',                          "twitterapi.io API 키"),
    (r'sk-[A-Za-z0-9]{40,}',                        "OpenAI API 키"),
    (r'1BVts[A-Za-z0-9_\-=]{100,}',                "Telethon 세션 문자열"),
    # 전화번호
    (r'\+82\d{9,11}',                               "한국 전화번호"),
    (r'\+\d{1,3}\d{9,12}',                          "국제 전화번호"),
    # 비밀번호 패턴 (변수명 기반)
    (r'(?i)(password|passwd|pwd|secret)\s*[=:]\s*["\'][^"\']{4,}["\']', "비밀번호"),
    # 이메일
    (r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}', "이메일 주소"),
]

# 마스킹 처리 시 보존할 글자 수
MASK_VISIBLE_CHARS = 4


def _get_or_create_key() -> bytes:
    """마스터 암호화 키 생성 또는 로드"""
    SECURE_DIR.mkdir(mode=0o700, exist_ok=True)
    if KEY_FILE.exists():
        with open(KEY_FILE, "rb") as f:
            return f.read()
    # 새 키 생성
    from cryptography.fernet import Fernet
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as f:
        f.write(key)
    os.chmod(KEY_FILE, 0o600)
    logger.info("새 마스터 암호화 키 생성 완료")
    return key


def encrypt_vault(data: Dict[str, Any]) -> bool:
    """민감 정보를 암호화하여 vault 파일에 저장"""
    try:
        from cryptography.fernet import Fernet
        key = _get_or_create_key()
        f = Fernet(key)
        plaintext = json.dumps(data, ensure_ascii=False).encode("utf-8")
        encrypted = f.encrypt(plaintext)
        with open(VAULT_FILE, "wb") as fp:
            fp.write(encrypted)
        os.chmod(VAULT_FILE, 0o600)
        logger.info(f"보안 vault 암호화 저장 완료 ({len(data)}개 항목)")
        return True
    except Exception as e:
        logger.error(f"vault 암호화 실패: {e}")
        return False


def decrypt_vault() -> Optional[Dict[str, Any]]:
    """암호화된 vault 파일에서 민감 정보 복호화"""
    try:
        if not VAULT_FILE.exists():
            return None
        from cryptography.fernet import Fernet
        key = _get_or_create_key()
        f = Fernet(key)
        with open(VAULT_FILE, "rb") as fp:
            encrypted = fp.read()
        plaintext = f.decrypt(encrypted)
        return json.loads(plaintext.decode("utf-8"))
    except Exception as e:
        logger.error(f"vault 복호화 실패: {e}")
        return None


def mask_sensitive(value: str, label: str = "") -> str:
    """민감 정보 마스킹 처리"""
    if not value:
        return value
    visible = min(MASK_VISIBLE_CHARS, len(value) // 4)
    masked = value[:visible] + "*" * (len(value) - visible * 2) + value[-visible:] if visible > 0 else "*" * len(value)
    return f"[{label}:{masked}]" if label else masked


def scan_file_for_secrets(filepath: str) -> list:
    """파일에서 민감 정보 패턴 스캔 (GitHub 업로드 전 검사용)"""
    findings = []
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        lines = content.splitlines()
        for lineno, line in enumerate(lines, 1):
            for pattern, label in SENSITIVE_PATTERNS:
                matches = re.findall(pattern, line)
                for match in matches:
                    findings.append({
                        "file": filepath,
                        "line": lineno,
                        "label": label,
                        "preview": mask_sensitive(match if isinstance(match, str) else match[0], label)
                    })
    except Exception as e:
        logger.warning(f"파일 스캔 오류 {filepath}: {e}")
    return findings


def scan_directory_for_secrets(directory: str, exclude_dirs: list = None) -> Dict:
    """디렉토리 전체 보안 스캔"""
    exclude_dirs = exclude_dirs or [".secure", ".git", "__pycache__", "logs"]
    all_findings = []
    scanned_files = 0

    for root, dirs, files in os.walk(directory):
        # 제외 폴더 처리
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for filename in files:
            if filename.endswith((".py", ".env", ".json", ".yaml", ".yml", ".txt", ".sh", ".md")):
                filepath = os.path.join(root, filename)
                findings = scan_file_for_secrets(filepath)
                all_findings.extend(findings)
                scanned_files += 1

    return {
        "scanned_files": scanned_files,
        "total_findings": len(all_findings),
        "findings": all_findings
    }


def create_github_safe_copy(src_dir: str, dst_dir: str) -> bool:
    """GitHub 업로드용 안전한 복사본 생성 (민감 정보 제거/마스킹)"""
    import shutil

    # 제외할 파일/폴더
    EXCLUDE = {".secure", ".env", ".git", "bot.pid", "logs",
               "gen_session.py", "search_emoji_packs.py", "get_emoji_ids.py",
               "fxtwitter_research.md", "__pycache__"}

    # 민감 정보가 포함된 파일에서 치환할 패턴
    REPLACEMENTS = [
        (r'(TELEGRAM_BOT_TOKEN\s*=\s*)["\'][^"\']+["\']',     r'\1"YOUR_BOT_TOKEN_HERE"'),
        (r'(TELEGRAM_API_ID\s*=\s*)\d+',                       r'\1YOUR_API_ID_HERE'),
        (r'(TELEGRAM_API_HASH\s*=\s*)["\'][^"\']+["\']',       r'\1"YOUR_API_HASH_HERE"'),
        (r'(TELEGRAM_SESSION\s*=\s*)["\'][^"\']+["\']',        r'\1"YOUR_SESSION_STRING_HERE"'),
        (r'(TELEGRAM_CHANNEL_ID\s*=\s*)["\'][^"\']+["\']',     r'\1"YOUR_CHANNEL_ID_HERE"'),
        (r'(TWITTER_API_KEY\s*=\s*)["\'][^"\']+["\']',         r'\1"YOUR_TWITTERAPI_KEY_HERE"'),
        (r'(OPENAI_API_KEY\s*=\s*)["\'][^"\']+["\']',          r'\1"YOUR_OPENAI_API_KEY_HERE"'),
        (r'(TELEGRAM_API_ID\s*=\s*)\d+',                       r'\1000000000'),
        (r'\+82\d{9,11}',                                       '+821000000000'),
    ]

    try:
        dst = Path(dst_dir)
        if dst.exists():
            shutil.rmtree(dst)
        dst.mkdir(parents=True)

        src = Path(src_dir)
        for item in src.iterdir():
            if item.name in EXCLUDE or item.name.startswith("."):
                continue
            dst_item = dst / item.name
            if item.is_dir():
                shutil.copytree(item, dst_item, ignore=shutil.ignore_patterns(
                    "__pycache__", "*.pyc", "*.log"))
            else:
                shutil.copy2(item, dst_item)
                # 텍스트 파일 민감 정보 치환
                if item.suffix in (".py", ".env", ".json", ".yaml", ".yml", ".sh", ".md", ".txt"):
                    with open(dst_item, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                    for pattern, replacement in REPLACEMENTS:
                        content = re.sub(pattern, replacement, content)
                    with open(dst_item, "w", encoding="utf-8") as f:
                        f.write(content)

        logger.info(f"GitHub 안전 복사본 생성 완료: {dst_dir}")
        return True
    except Exception as e:
        logger.error(f"GitHub 안전 복사본 생성 실패: {e}")
        return False


def initialize_vault():
    """현재 config.py의 민감 정보를 vault에 암호화 저장"""
    sensitive_data = {
        "TELEGRAM_BOT_TOKEN":  "8237707628:AAHQRzAzayLpSsgKpSe1KO3nBeGS8KY_RHU",
        "TELEGRAM_CHANNEL_ID": "-1001645099595",
        "TELEGRAM_API_ID":     39695050,
        "TELEGRAM_API_HASH":   "1107f6b4296cf6fcf30ab09604e85111",
        "TELEGRAM_SESSION":    "1BVtsOIIBu1SJGtmzYt3ox3qiB2st_IcdOPR2RKs4wqgGcaez1xbYP65TI8zSVHbAKVjg85tzkyfU2gBZjRRiBTApuiHGt-LTxrMUlBThVyH4g703lQ7GKylKUvuS6N-utGZhpw1v6IaiqOEaBOHllm7IZt4Kiwx_-sGEjkRIdPSbKGc61skoBVf62td5-ffY9n3ys7MLC2_SdyMRIvFTcwvg_l1vZtrRciTe1ytTMew-w02Az47ZMHXxE0Gs3NuF1GazJjLUF-GwlD5gKkkCj_kIX2sjvrzbKlmcxN52mvBS_au419TJ229Q4OEtthf0cZEsxUDxVN5ujSUwlfdTcbI8PbYM8kU=",
        "TWITTER_API_KEY":     "new1_23710e6a69be4ad68f60d24285c99a2f",
        "PHONE_NUMBER":        "+8201034553075",
        "TWITTERAPI_IO_KEY":   "new1_23710e6a69be4ad68f60d24285c99a2f",
    }
    return encrypt_vault(sensitive_data)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    print("=" * 60)
    print("보안 시스템 초기화")
    print("=" * 60)

    # 1. vault 초기화
    print("\n[1] 민감 정보 암호화 vault 생성...")
    if initialize_vault():
        print("  ✅ vault 암호화 완료")
        vault = decrypt_vault()
        if vault:
            print(f"  ✅ vault 복호화 검증 완료 ({len(vault)}개 항목)")
            for k, v in vault.items():
                val = str(v)
                print(f"     {k}: {mask_sensitive(val, k)}")

    # 2. 디렉토리 보안 스캔
    print("\n[2] 프로젝트 보안 스캔...")
    result = scan_directory_for_secrets("/home/ubuntu/x_news_bot")
    print(f"  스캔된 파일: {result['scanned_files']}개")
    print(f"  발견된 민감 정보: {result['total_findings']}건")
    if result['findings']:
        for f in result['findings'][:5]:
            print(f"  ⚠  {f['file'].split('/')[-1]}:{f['line']} - {f['label']}: {f['preview']}")
        if len(result['findings']) > 5:
            print(f"  ... 외 {len(result['findings'])-5}건")

    # 3. GitHub 안전 복사본 생성
    print("\n[3] GitHub 안전 복사본 생성...")
    if create_github_safe_copy("/home/ubuntu/x_news_bot", "/home/ubuntu/x_news_bot_github"):
        print("  ✅ /home/ubuntu/x_news_bot_github 생성 완료")
        print("  (민감 정보 마스킹 처리됨)")

    print("\n✅ 보안 시스템 초기화 완료")
