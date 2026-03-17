#!/bin/bash

# G1手柄监听服务安装脚本

echo "=== G1 Gamepad Listener Service Setup ==="

# 检查是否为root用户
if [ "$EUID" -eq 0 ]; then
    echo "请不要使用root用户运行此脚本"
    exit 1
fi

# 获取当前用户名
USER=$(whoami)
echo "当前用户: $USER"

# 更新服务文件中的用户名
sed -i "s/User=unitree/User=$USER/g" gamepad_listener.service
sed -i "s/Group=unitree/Group=$USER/g" gamepad_listener.service

# 设置脚本权限
chmod +x start_gamepad_listener.sh
chmod +x robojudo_listener.py

# 复制服务文件到systemd目录
echo "安装systemd服务..."
sudo cp gamepad_listener.service /etc/systemd/system/

# 重新加载systemd
echo "重新加载systemd..."
sudo systemctl daemon-reload

# 启用服务
echo "启用开机自启动..."
sudo systemctl enable gamepad_listener.service

# 立即启动服务
echo "启动服务..."
sudo systemctl start gamepad_listener.service

# 检查服务状态
echo "检查服务状态..."
sudo systemctl status gamepad_listener.service --no-pager

echo ""
echo "=== 安装完成 ==="
echo "服务已设置为开机自启动"
echo ""
echo "常用命令:"
echo "  查看服务状态: sudo systemctl status gamepad_listener"
echo "  查看服务日志: sudo journalctl -u gamepad_listener -f"
echo "  查看详细日志: tail -f gamepad_listener.log"
echo "  停止服务: sudo systemctl stop gamepad_listener"
echo "  重启服务: sudo systemctl restart gamepad_listener"
echo "  禁用自启动: sudo systemctl disable gamepad_listener"
echo ""
echo "手动控制:"
echo "  启动监听: ./start_gamepad_listener.sh start"
echo "  停止监听: ./start_gamepad_listener.sh stop"
echo "  重启监听: ./start_gamepad_listener.sh restart"
echo "  查看状态: ./start_gamepad_listener.sh status"
