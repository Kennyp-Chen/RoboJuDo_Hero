# G1 手柄监听服务设置指南

## 文件说明

- **`robojudo_listener.py`** - 主要的手柄监听脚本
- **`start_gamepad_listener.sh`** - 启动管理脚本
- **`gamepad_listener.service`** - systemd服务文件
- **`setup_gamepad_service.sh`** - 一键安装脚本

## 功能特性

✅ **L1 + R1 + A** - 启动 `run_pipeline_serv.py`  
✅ **L1 + R1 + B** - 关闭进程并关机PC2  
✅ **开机自启动** - 通过systemd自动运行  
✅ **进程监控** - 自动检测任务状态  
✅ **日志记录** - 详细的运行日志  

## 安装步骤

### 1. 一键安装（推荐）
```bash
./setup_gamepad_service.sh
```

### 2. 手动安装
```bash
# 设置权限
chmod +x start_gamepad_listener.sh
chmod +x robojudo_listener.py

# 安装systemd服务
sudo cp gamepad_listener.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable gamepad_listener.service
sudo systemctl start gamepad_listener.service
```

## 使用方法

### 服务管理
```bash
# 查看服务状态
sudo systemctl status gamepad_listener

# 查看服务日志
sudo journalctl -u gamepad_listener -f

# 重启服务
sudo systemctl restart gamepad_listener

# 停止服务
sudo systemctl stop gamepad_listener
```

### 手动控制
```bash
# 启动监听
./start_gamepad_listener.sh start

# 停止监听
./start_gamepad_listener.sh stop

# 重启监听
./start_gamepad_listener.sh restart

# 查看状态
./start_gamepad_listener.sh status
```

### 查看日志
```bash
# 查看详细日志
tail -f gamepad_listener.log

# 查看最近的日志
tail -20 gamepad_listener.log
```

## 手柄操作

| 按键组合 | 功能 |
|---------|------|
| L1 + R1 + A | 启动机器人任务脚本 |
| L1 + R1 + B | 停止并关机PC2 |

## 故障排除

### 1. 服务无法启动
```bash
# 检查服务状态
sudo systemctl status gamepad_listener

# 查看错误日志
sudo journalctl -u gamepad_listener --no-pager
```

### 2. 手柄未检测到
- 确保手柄已正确连接到机器人
- 检查机器人是否开机
- 确认网络连接正常

### 3. 任务启动失败
```bash
# 检查conda环境
conda activate robojudo

# 手动测试任务脚本
python scripts/run_pipeline_serv.py
```

### 4. 卸载服务
```bash
# 停止并禁用服务
sudo systemctl stop gamepad_listener
sudo systemctl disable gamepad_listener

# 删除服务文件
sudo rm /etc/systemd/system/gamepad_listener.service
sudo systemctl daemon-reload
```

## 技术细节

- **Python环境**: conda robojudo
- **手柄检测**: evdev库
- **进程管理**: psutil库
- **系统服务**: systemd
- **日志位置**: `./gamepad_listener.log`

## 更新说明

如需更新脚本：
```bash
# 停止服务
sudo systemctl stop gamepad_listener

# 更新文件后重启服务
sudo systemctl start gamepad_listener
```
