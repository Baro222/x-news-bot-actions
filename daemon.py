"""
X 뉴스봇 데몬 - 2시간마다 자동으로 뉴스를 수집하고 텔레그램에 발송합니다.
실행: nohup python3.11 /home/ubuntu/x_news_bot/daemon.py &
"""

import schedule
import time
import logging
import sys
import os
import signal
from datetime import datetime, timezone, timedelta

# 작업 디렉토리 설정
os.chdir("/home/ubuntu/x_news_bot")
sys.path.insert(0, "/home/ubuntu/x_news_bot")

# .env 파일 로드
def load_env():
    env_file = "/home/ubuntu/x_news_bot/.env"
    if os.path.exists(env_file):
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    if key and value and not os.environ.get(key):
                        os.environ[key] = value

load_env()

# 로깅 설정
LOG_DIR = "/home/ubuntu/x_news_bot/logs"
os.makedirs(LOG_DIR, exist_ok=True)

# 루트 로거 핸들러 완전 초기화 후 설정 (중복 방지)
root_logger = logging.getLogger()
for handler in root_logger.handlers[:]:
    root_logger.removeHandler(handler)
root_logger.setLevel(logging.INFO)

# 파일 핸들러만 사용 (stdout 제외 - nohup 리다이렉션으로 인한 중복 방지)
_file_handler = logging.FileHandler(f"{LOG_DIR}/daemon.log", encoding='utf-8')
_file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
root_logger.addHandler(_file_handler)

logger = logging.getLogger(__name__)

KST = timezone(timedelta(hours=9))

# 종료 플래그
running = True


def signal_handler(signum, frame):
    global running
    logger.info(f"종료 신호 수신 ({signum}). 데몬 종료 중...")
    running = False


def job():
    """4시간마다 실행되는 뉴스 수집 작업"""
    logger.info(f"스케줄 작업 시작: {datetime.now(KST).strftime('%Y-%m-%d %H:%M KST')}")
    try:
        from main import run_news_cycle
        success = run_news_cycle()
        logger.info(f"스케줄 작업 완료: {'성공' if success else '실패'}")
    except Exception as e:
        logger.error(f"스케줄 작업 오류: {e}", exc_info=True)


def main():
    global running
    
    # 종료 신호 핸들러 등록
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    logger.info("=" * 50)
    logger.info("X 뉴스봇 데스 시작")
    logger.info(f"시작 시간: {datetime.now(KST).strftime('%Y-%m-%d %H:%M KST')}")
    logger.info("실행 주기: 4시간마다 (00:00, 04:00, 08:00, 12:00, 16:00, 20:00 KST)")
    logger.info("=" * 50)
    
    # 4시간마다 실행 (KST 기준)
    # 스케줄러는 UTC 기준이므로 KST-9시간 적용
    # KST 00:00 = UTC 15:00 (전날)
    # KST 04:00 = UTC 19:00 (전날)
    # KST 08:00 = UTC 23:00 (전날)
    # KST 12:00 = UTC 03:00
    # KST 16:00 = UTC 07:00
    # KST 20:00 = UTC 11:00
    schedule.every().day.at("15:00").do(job)  # KST 00:00
    schedule.every().day.at("19:00").do(job)  # KST 04:00
    schedule.every().day.at("23:00").do(job)  # KST 08:00
    schedule.every().day.at("03:00").do(job)  # KST 12:00
    schedule.every().day.at("07:00").do(job)  # KST 16:00
    schedule.every().day.at("11:00").do(job)  # KST 20:00
    
    # 시작 시 즉시 한 번 실행
    logger.info("시작 시 즉시 실행...")
    job()
    
    # 다음 실행 시간 안내
    next_run = schedule.next_run()
    if next_run:
        logger.info(f"다음 실행 예정: {next_run.strftime('%Y-%m-%d %H:%M')}")
    
    # 스케줄 루프
    while running:
        schedule.run_pending()
        time.sleep(30)  # 30초마다 스케줄 체크
    
    logger.info("X 뉴스봇 데몬 종료")


if __name__ == "__main__":
    main()
