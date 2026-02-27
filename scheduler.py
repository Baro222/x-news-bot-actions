"""
2시간 주기 스케줄러 - cron 방식으로 실행
crontab에 추가: 0 */2 * * * /usr/bin/python3.11 /home/ubuntu/x_news_bot/scheduler.py
"""

import logging
import sys
import os

# 작업 디렉토리 설정
os.chdir("/home/ubuntu/x_news_bot")
sys.path.insert(0, "/home/ubuntu/x_news_bot")

# 로깅 설정
LOG_DIR = "/home/ubuntu/x_news_bot/logs"
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"{LOG_DIR}/scheduler.log", encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("스케줄러 실행 시작")
    from main import run_news_cycle
    success = run_news_cycle()
    logger.info(f"스케줄러 실행 완료: {'성공' if success else '실패'}")
    sys.exit(0 if success else 1)
