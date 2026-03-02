#!/usr/bin/env python3
"""
GitHub Secrets 업데이트를 위한 변경사항 커밋
새로운 텔레그램 채널 ID: -1003683270211
"""

import os
import json

# 변경사항 기록 파일
changes = {
    "channel_change": {
        "old_channel_id": "-1001645099595",
        "new_channel_id": "-1003683270211",
        "timestamp": "2026-03-01T16:20:00Z",
        "reason": "채널 변경 요청",
        "action": "GitHub Secrets에서 TELEGRAM_CHANNEL_ID를 -1003683270211로 변경 필요"
    }
}

# 변경사항 저장
with open("CHANNEL_UPDATE.json", "w") as f:
    json.dump(changes, f, indent=2, ensure_ascii=False)

print("✅ 변경사항 기록 생성: CHANNEL_UPDATE.json")
print(json.dumps(changes, indent=2, ensure_ascii=False))
