#!/bin/bash
# X 뉴스봇 데몬 관리 스크립트

BOT_DIR="/home/ubuntu/x_news_bot"
PID_FILE="$BOT_DIR/bot.pid"
LOG_FILE="$BOT_DIR/logs/daemon.log"

start() {
    if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
        echo "뉴스봇이 이미 실행 중입니다. (PID: $(cat $PID_FILE))"
        return 1
    fi
    
    echo "뉴스봇 시작 중..."
    cd "$BOT_DIR"
    
    # OPENAI_API_KEY 환경변수 확인
    if [ -z "$OPENAI_API_KEY" ]; then
        # .env 파일에서 읽기
        if [ -f "$BOT_DIR/.env" ]; then
            export $(cat "$BOT_DIR/.env" | xargs)
        fi
    fi
    
    nohup /usr/bin/python3.11 "$BOT_DIR/daemon.py" >> "$LOG_FILE" 2>&1 &
    echo $! > "$PID_FILE"
    echo "뉴스봇 시작 완료 (PID: $!)"
    echo "로그: $LOG_FILE"
}

stop() {
    if [ ! -f "$PID_FILE" ]; then
        echo "PID 파일이 없습니다. 뉴스봇이 실행 중이지 않을 수 있습니다."
        return 1
    fi
    
    PID=$(cat "$PID_FILE")
    if kill -0 "$PID" 2>/dev/null; then
        echo "뉴스봇 종료 중... (PID: $PID)"
        kill "$PID"
        rm -f "$PID_FILE"
        echo "뉴스봇 종료 완료"
    else
        echo "프로세스가 이미 종료되었습니다."
        rm -f "$PID_FILE"
    fi
}

status() {
    if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
        echo "✅ 뉴스봇 실행 중 (PID: $(cat $PID_FILE))"
        echo "최근 로그:"
        tail -20 "$LOG_FILE" 2>/dev/null || echo "로그 없음"
    else
        echo "❌ 뉴스봇 실행 중이지 않음"
    fi
}

restart() {
    stop
    sleep 2
    start
}

run_once() {
    echo "즉시 한 번 실행..."
    cd "$BOT_DIR"
    /usr/bin/python3.11 "$BOT_DIR/main.py"
}

case "$1" in
    start)   start ;;
    stop)    stop ;;
    status)  status ;;
    restart) restart ;;
    run)     run_once ;;
    *)
        echo "사용법: $0 {start|stop|status|restart|run}"
        echo "  start   - 데몬 시작 (2시간 주기 자동 실행)"
        echo "  stop    - 데몬 중지"
        echo "  status  - 실행 상태 확인"
        echo "  restart - 데몬 재시작"
        echo "  run     - 즉시 한 번 실행"
        exit 1
        ;;
esac
