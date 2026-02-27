
import os
from openai import OpenAI

# 환경 변수에서 API 키 로드
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    print("OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")
else:
    try:
        client = OpenAI(api_key=api_key)
        # 간단한 모델 리스트 호출로 API 키 유효성 검증
        client.models.list()
        print("OPENAI_API_KEY가 유효합니다.")
    except Exception as e:
        print(f"OPENAI_API_KEY가 유효하지 않습니다: {e}")
