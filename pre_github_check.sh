#!/bin/bash
# ============================================================
# GitHub 업로드 전 보안 검사 스크립트
# 사용법: bash pre_github_check.sh
# ============================================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "============================================================"
echo "  GitHub 업로드 전 보안 검사"
echo "============================================================"
echo ""

PASS=0
FAIL=0

check() {
    local desc="$1"
    local result="$2"
    if [ "$result" = "PASS" ]; then
        echo -e "  ${GREEN}✅ PASS${NC}  $desc"
        ((PASS++))
    else
        echo -e "  ${RED}❌ FAIL${NC}  $desc"
        ((FAIL++))
    fi
}

# 1. 민감 파일 존재 여부 확인
echo "[1] 민감 파일 존재 여부 확인"
[ ! -f ".env" ]         && check ".env 파일 없음 (또는 .gitignore 처리됨)" "PASS" || check ".env 파일 발견 - 업로드 금지!" "FAIL"
[ ! -d ".secure" ]      && check ".secure 폴더 없음 (또는 .gitignore 처리됨)" "PASS" || check ".secure 폴더 발견 - 업로드 금지!" "FAIL"
[ ! -f "*.session" ]    && check "세션 파일 없음" "PASS" || check "세션 파일 발견 - 업로드 금지!" "FAIL"
echo ""

# 2. config.py 민감 정보 패턴 검사
echo "[2] config.py 민감 정보 패턴 검사"
if [ -f "config.py" ]; then
    # 실제 API 키 패턴 검사
    if grep -qE '[0-9]{8,10}:[A-Za-z0-9_\-]{30,50}' config.py 2>/dev/null; then
        check "config.py 봇 토큰 패턴" "FAIL"
    else
        check "config.py 봇 토큰 패턴 없음" "PASS"
    fi
    if grep -qE 'new1_[a-f0-9]{32}' config.py 2>/dev/null; then
        check "config.py twitterapi 키 패턴" "FAIL"
    else
        check "config.py twitterapi 키 패턴 없음" "PASS"
    fi
    if grep -qE '1BVts[A-Za-z0-9_\-=]{50,}' config.py 2>/dev/null; then
        check "config.py Telethon 세션 패턴" "FAIL"
    else
        check "config.py Telethon 세션 패턴 없음" "PASS"
    fi
fi
echo ""

# 3. Python 파일 전체 스캔
echo "[3] Python 파일 민감 정보 스캔"
FOUND=$(grep -rE '(\+82[0-9]{9,11}|sk-[A-Za-z0-9]{40,}|new1_[a-f0-9]{32})' --include="*.py" . 2>/dev/null | grep -v ".secure" | wc -l)
if [ "$FOUND" -eq 0 ]; then
    check "Python 파일 민감 패턴 없음" "PASS"
else
    check "Python 파일에서 민감 패턴 $FOUND건 발견" "FAIL"
fi
echo ""

# 4. .gitignore 존재 확인
echo "[4] .gitignore 설정 확인"
[ -f ".gitignore" ] && check ".gitignore 파일 존재" "PASS" || check ".gitignore 파일 없음" "FAIL"
grep -q ".secure" .gitignore 2>/dev/null && check ".secure 폴더 gitignore 등록" "PASS" || check ".secure 폴더 gitignore 미등록" "FAIL"
grep -q ".env" .gitignore 2>/dev/null && check ".env 파일 gitignore 등록" "PASS" || check ".env 파일 gitignore 미등록" "FAIL"
echo ""

# 최종 결과
echo "============================================================"
echo -e "  결과: ${GREEN}PASS ${PASS}건${NC} / ${RED}FAIL ${FAIL}건${NC}"
echo "============================================================"

if [ "$FAIL" -gt 0 ]; then
    echo -e "\n  ${RED}⚠  보안 검사 실패! GitHub 업로드 전 민감 정보를 제거하세요.${NC}"
    echo "  GitHub 안전 복사본 생성: python3.11 security_manager.py"
    exit 1
else
    echo -e "\n  ${GREEN}✅ 보안 검사 통과! GitHub 업로드 가능합니다.${NC}"
    exit 0
fi
