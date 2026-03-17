# G1 手柄监听服务设置指南

## 文件说明

- **`robojudo_listener.py`** - 主要的手柄监听脚本
- **`start_gamepad_listener.sh`** - 启动管理脚本
- **`gamepad_listener.service`** - systemd服务文件
- **`setup_gamepad_service.sh`** - 一键安装脚本

## 功能特性

✅ **L1 + R1 + A** - 启动 `run_pipeline_serv.py`  
✅ **L1 + R1 + B** - 停止监听，交还控制权给PC1  
✅ **开机自启动** - 通过systemd自动运行  
✅ **进程监控** - 自动检测任务状态  
✅ **日志记录** - 详细的运行日志  
✅ **权限管理** - 支持sudo免密配置  

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

# 配置sudo免密（重要！）
sudo visudo
# 在文件末尾添加：
# unitree ALL=(ALL) NOPASSWD: /bin/systemctl stop gamepad_listener, /bin/systemctl start gamepad_listener

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
| L1 + R1 + B | 停止监听，交还控制权给PC1 |

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

### 4. 手柄按键无法停止服务
```bash
# 检查sudo免密配置
sudo -n systemctl stop gamepad_listener

# 如果提示需要密码，重新配置sudo免密：
sudo visudo
# 确保包含：
# unitree ALL=(ALL) NOPASSWD: /bin/systemctl stop gamepad_listener, /bin/systemctl start gamepad_listener
```

### 5. 手动配置sudo免密（详细教程）
如果自动配置失败，请按以下步骤手动配置：

#### 步骤1：编辑sudoers文件
```bash
sudo visudo
```

#### 步骤2：在文件末尾添加以下行
```
unitree ALL=(ALL) NOPASSWD: /bin/systemctl stop gamepad_listener, /bin/systemctl start gamepad_listener
```

#### 步骤3：保存并退出
- 在vi/vim中：按 `Esc`，然后输入 `:wq` 并回车
- 在nano中：按 `Ctrl+X`，然后按 `Y` 确认，最后按回车

#### 步骤4：验证配置
```bash
# 测试是否需要密码（应该没有任何输出）
sudo -n systemctl stop gamepad_listener

# 如果成功，重新启动服务
sudo systemctl start gamepad_listener
```

### 6. 卸载服务
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
- **手柄检测**: Unitree机器人接口
- **进程管理**: psutil库 + systemd
- **系统服务**: systemd (系统级)
- **权限控制**: sudo免密配置
- **日志位置**: `./gamepad_listener.log`

## 工作原理

1. **开机自启动**: systemd在系统启动时自动运行监听服务
2. **手柄监听**: 通过Unitree机器人接口获取手柄数据
3. **按键检测**: 监听特定组合键 (L1+R1+A/B)
4. **服务控制**: 使用systemctl命令管理服务生命周期
5. **状态持久化**: 重启后服务自动恢复，无需手动干预

## 更新说明

如需更新脚本：
```bash
# 停止服务
sudo systemctl stop gamepad_listener

# 更新文件后重启服务
sudo systemctl start gamepad_listener
```
