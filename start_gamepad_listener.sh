#!/bin/bash

# G1 PC2 手柄监听启动脚本

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 日志文件
LOG_FILE="$SCRIPT_DIR/gamepad_listener.log"

# 启动函数
start_listener() {
    echo "$(date): 启动G1手柄监听服务..." >> "$LOG_FILE"
    
    # 激活conda环境并启动监听
    # 使用conda run来确保环境正确激活
    conda run -n robojudo python3 robojudo_listener.py >> "$LOG_FILE" 2>&1 &
    
    # 获取进程ID
    PID=$!
    echo "$(date): 手柄监听服务已启动，PID=$PID" >> "$LOG_FILE"
    echo $PID > "$SCRIPT_DIR/gamepad_listener.pid"
    
    echo "手柄监听服务已启动"
    echo "日志文件: $LOG_FILE"
    echo "进程ID: $PID"
}

# 停止函数
stop_listener() {
    if [ -f "$SCRIPT_DIR/gamepad_listener.pid" ]; then
        PID=$(cat "$SCRIPT_DIR/gamepad_listener.pid")
        if kill -0 "$PID" 2>/dev/null; then
            kill "$PID"
            echo "$(date): 手柄监听服务已停止，PID=$PID" >> "$LOG_FILE"
            echo "手柄监听服务已停止"
        else
            echo "进程不存在或已停止"
        fi
        rm -f "$SCRIPT_DIR/gamepad_listener.pid"
    else
        echo "找不到PID文件，服务可能未运行"
    fi
}

# 状态检查函数
status_listener() {
    if [ -f "$SCRIPT_DIR/gamepad_listener.pid" ]; then
        PID=$(cat "$SCRIPT_DIR/gamepad_listener.pid")
        if kill -0 "$PID" 2>/dev/null; then
            echo "手柄监听服务正在运行，PID=$PID"
            echo "最近日志:"
            tail -10 "$LOG_FILE"
        else
            echo "服务已停止，但PID文件仍存在"
        fi
    else
        echo "手柄监听服务未运行"
    fi
}

# 主逻辑
case "$1" in
    start)
        start_listener
        ;;
    stop)
        stop_listener
        ;;
    restart)
        stop_listener
        sleep 2
        start_listener
        ;;
    status)
        status_listener
        ;;
    *)
        echo "用法: $0 {start|stop|restart|status}"
        echo "  start   - 启动手柄监听服务"
        echo "  stop    - 停止手柄监听服务"
        echo "  restart - 重启手柄监听服务"
        echo "  status  - 查看服务状态"
        exit 1
        ;;
esac
