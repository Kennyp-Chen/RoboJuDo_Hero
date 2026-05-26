#!/bin/bash

# G1手柄监听服务安装脚本
# 自动检测 conda python 路径、systemctl 路径，自动配置 sudo 免密
# 无硬编码路径，所有用户可直接使用

set -e

echo "=== G1 Gamepad Listener Service Setup ==="

# 检查是否为root用户
if [ "$EUID" -eq 0 ]; then
    echo "请不要使用root用户运行此脚本（它会自动用sudo提权）"
    exit 1
fi

# 获取当前用户名和项目目录
USER=$(whoami)
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
echo "当前用户: $USER"
echo "项目目录: $PROJECT_DIR"

# --------------------------------------------------
# 自动检测 conda python 路径
# --------------------------------------------------
echo ""
echo ">>> 检测 conda 环境 'robojudo'..."

CONDA_PYTHON=""

# 方法1: 通过 conda run 检测
if command -v conda &>/dev/null; then
    CONDA_PYTHON=$(conda run -n robojudo which python 2>/dev/null || true)
fi

# 方法2: 搜索常见 conda 安装位置
if [ -z "$CONDA_PYTHON" ]; then
    for base in "$HOME/miniconda3" "$HOME/anaconda3" "/opt/miniconda3" "/opt/anaconda3" "$HOME/conda"; do
        if [ -f "$base/envs/robojudo/bin/python" ]; then
            CONDA_PYTHON="$base/envs/robojudo/bin/python"
            break
        fi
    done
fi

# 方法3: 检查 CONDA_PREFIX 环境变量
if [ -z "$CONDA_PYTHON" ] && [ -n "$CONDA_PREFIX" ]; then
    if [ -f "$CONDA_PREFIX/bin/python" ]; then
        CONDA_PYTHON="$CONDA_PREFIX/bin/python"
    fi
fi

# 方法4: 检查 CONDA_DEFAULT_ENV 指向的环境
if [ -z "$CONDA_PYTHON" ] && [ -n "$CONDA_DEFAULT_ENV" ]; then
    CONDA_ENV_PATH=$(conda info --base 2>/dev/null || true)
    if [ -n "$CONDA_ENV_PATH" ] && [ -f "$CONDA_ENV_PATH/envs/$CONDA_DEFAULT_ENV/bin/python" ]; then
        CONDA_PYTHON="$CONDA_ENV_PATH/envs/$CONDA_DEFAULT_ENV/bin/python"
    fi
fi

if [ -z "$CONDA_PYTHON" ]; then
    echo "❌ 错误: 找不到 conda 环境 'robojudo' 的 python 路径"
    echo ""
    echo "请确认已安装 conda 并创建了 robojudo 环境："
    echo "  conda create -n robojudo python=3.11"
    echo "  conda activate robojudo"
    echo "  pip install -e ."
    exit 1
fi

echo "✅ 检测到: $CONDA_PYTHON"

# --------------------------------------------------
# 自动检测 systemctl 路径
# --------------------------------------------------
SYSTEMCTL=$(command -v systemctl 2>/dev/null || echo "/usr/bin/systemctl")
echo "systemctl 路径: $SYSTEMCTL"

# --------------------------------------------------
# 生成服务文件
# --------------------------------------------------
echo ""
echo ">>> 生成 systemd 服务文件..."

TMP_SERVICE=$(mktemp)
sed -e "s|__PROJECT_DIR__|$PROJECT_DIR|g" \
    -e "s|__USER__|$USER|g" \
    -e "s|__CONDA_PYTHON__|$CONDA_PYTHON|g" \
    gamepad_listener.service > "$TMP_SERVICE"

echo "服务文件内容预览:"
echo "----------------------------------------"
cat "$TMP_SERVICE"
echo "----------------------------------------"

# 设置脚本权限
chmod +x start_gamepad_listener.sh
chmod +x robojudo_listener.py

# --------------------------------------------------
# 安装到 systemd
# --------------------------------------------------
echo ""
echo ">>> 安装 systemd 服务..."
sudo cp "$TMP_SERVICE" /etc/systemd/system/gamepad_listener.service
rm -f "$TMP_SERVICE"

sudo "$SYSTEMCTL" daemon-reload
sudo "$SYSTEMCTL" enable gamepad_listener.service
sudo "$SYSTEMCTL" start gamepad_listener.service

# --------------------------------------------------
# 配置 sudo 免密
# --------------------------------------------------
echo ""
echo ">>> 配置 sudo 免密..."

SUDOERS_FILE="/etc/sudoers.d/gamepad_listener"
SUDOERS_RULE="$USER ALL=(ALL) NOPASSWD: $SYSTEMCTL stop gamepad_listener, $SYSTEMCTL start gamepad_listener"

if [ ! -f "$SUDOERS_FILE" ] || ! grep -q "$SYSTEMCTL stop gamepad_listener" "$SUDOERS_FILE" 2>/dev/null; then
    echo "$SUDOERS_RULE" | sudo tee "$SUDOERS_FILE" > /dev/null
    sudo chmod 440 "$SUDOERS_FILE"
    echo "✅ sudo 免密配置完成"
else
    echo "✅ sudo 免密已存在，跳过"
fi

# 验证 sudo 免密
echo "验证 sudo 免密..."
sudo -n "$SYSTEMCTL" is-active gamepad_listener &>/dev/null && echo "✅ sudo免密验证通过" || echo "⚠️  sudo免密验证失败，请检查配置"

# --------------------------------------------------
# 完成
# --------------------------------------------------
echo ""
echo ">>> 检查服务状态..."
"$SYSTEMCTL" status gamepad_listener.service --no-pager || true

echo ""
echo "============================================"
echo "✅ 安装完成！"
echo "============================================"
echo ""
echo "服务已设置为开机自启动并已启动运行"
echo ""
echo "常用命令:"
echo "  查看服务状态: sudo $SYSTEMCTL status gamepad_listener"
echo "  查看服务日志: sudo journalctl -u gamepad_listener -f"
echo "  查看详细日志: tail -f gamepad_listener.log"
echo "  停止服务:    sudo $SYSTEMCTL stop gamepad_listener"
echo "  重启服务:    sudo $SYSTEMCTL restart gamepad_listener"
echo "  禁用自启动:  sudo $SYSTEMCTL disable gamepad_listener"
echo ""
echo "手动控制:"
echo "  启动监听: ./start_gamepad_listener.sh start"
echo "  停止监听: ./start_gamepad_listener.sh stop"
echo "  重启监听: ./start_gamepad_listener.sh restart"
echo "  查看状态: ./start_gamepad_listener.sh status"
echo ""
echo "手柄操作:"
echo "  L1 + R1 + A = 启动任务"
echo "  L1 + R1 + B = 停止监听，交还控制权给PC1"
