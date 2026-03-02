#!/usr/bin/env python3
"""
텔레그램 채널 변경 테스트
새로운 채널 ID: -1003683270211
"""

import os
import sys
import json
from datetime import datetime

# 새로운 채널 ID 설정
NEW_CHANNEL_ID = "-1003683270211"
os.environ["TELEGRAM_CHANNEL_ID"] = NEW_CHANNEL_ID

# 기존 환경변수 확인
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_SESSION = os.environ.get("TELEGRAM_SESSION", "")
TELEGRAM_API_ID = os.environ.get("TELEGRAM_API_ID", "")
TELEGRAM_API_HASH = os.environ.get("TELEGRAM_API_HASH", "")

print("=" * 60)
print("텔레그램 채널 변경 테스트")
print("=" * 60)
print(f"\n✅ 새로운 채널 ID: {NEW_CHANNEL_ID}")
print(f"✅ 봇 토큰: {'설정됨' if TELEGRAM_BOT_TOKEN else '❌ 미설정'}")
print(f"✅ API ID: {'설정됨' if TELEGRAM_API_ID else '❌ 미설정'}")
print(f"✅ API Hash: {'설정됨' if TELEGRAM_API_HASH else '❌ 미설정'}")
print(f"✅ Session: {'설정됨' if TELEGRAM_SESSION else '❌ 미설정'}")

# telegram_sender 모듈 임포트
try:
    from telegram_sender import send_news_report
    print("\n✅ telegram_sender 모듈 로드 성공")
    
    # 테스트 뉴스 데이터
    test_news = [
        {
            "_category": "지정학",
            "_headline": "이란 군사 작전 계속",
            "_summary": "트럼프: 이란에 대한 군사 작전이 계속될 것",
            "_analysis": "중동 정세 긴장",
            "_importance": 9,
            "text": "Trump on Iran: Military operations will continue",
            "_url": "https://x.com/test"
        },
        {
            "_category": "경제",
            "_headline": "UAE 시장 거래 중단",
            "_summary": "UAE 자본 시장 당국이 거래를 일시 중단",
            "_analysis": "시장 안정성 우려",
            "_importance": 8,
            "text": "UAE Capital Market Authority suspends trading",
            "_url": "https://x.com/test"
        },
        {
            "_category": "암호화폐",
            "_headline": "비트코인 급등",
            "_summary": "비트코인이 새로운 고점을 기록",
            "_analysis": "시장 강세",
            "_importance": 7,
            "text": "Bitcoin reaches new all-time high",
            "_url": "https://x.com/test"
        }
    ]
    
    print(f"\n📤 테스트 뉴스 3개 발송 중...")
    print(f"   채널: {NEW_CHANNEL_ID}")
    
    # 발송 시도
    result = send_news_report(test_news)
    
    if result:
        print(f"\n✅ 텔레그램 발송 성공!")
        print(f"   발송된 메시지 수: {result}")
    else:
        print(f"\n⚠️ 텔레그램 발송 결과: {result}")
    
except Exception as e:
    print(f"\n❌ 오류 발생: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
