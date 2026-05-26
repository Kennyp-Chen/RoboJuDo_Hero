# G1 手柄监听服务设置指南

## 文件说明

- **`robojudo_listener.py`** - 主要的手柄监听脚本
- **`start_gamepad_listener.sh`** - 手动启动管理脚本
- **`gamepad_listener.service`** - systemd 服务模板（含 `__PROJECT_DIR__`、`__USER__`、`__CONDA_PYTHON__` 占位符）
- **`setup_gamepad_service.sh`** - 一键安装脚本（自动检测路径并替换占位符）

## 功能特性

✅ **L1 + R1 + A** - 启动 `run_pipeline_real.py`  
✅ **L1 + R1 + B** - 停止监听，交还控制权给 PC1  
✅ **开机自启动** - 通过 systemd 自动运行  
✅ **进程监控** - 自动检测任务状态  
✅ **日志记录** - 详细的运行日志  
✅ **权限管理** - 自动配置 sudo 免密  
✅ **跨机器部署** - 无硬编码路径，安装脚本自动检测

---

## 安装步骤

### 前提条件

- 已安装 conda 并创建了 `robojudo` 环境
- 已在 `robojudo` 环境中安装了项目依赖：`pip install -e .`
- 已编译安装 `unitree_cpp`（`cd packages/unitree_cpp && pip install -e .`）

### 一键安装（推荐）

```bash
./setup_gamepad_service.sh
```

安装脚本会自动完成：
1. ✅ 检测 `robojudo` conda 环境的 python 路径
2. ✅ 检测 systemctl 路径
3. ✅ 生成并安装 systemd 服务文件
4. ✅ 启用并启动服务
5. ✅ 配置 sudo 免密（NOPASSWD）

### 手动安装（不推荐）

```bash
# 1. 设置权限
chmod +x start_gamepad_listener.sh
chmod +x robojudo_listener.py

# 2. 手动生成服务文件并安装
sed -e "s|__PROJECT_DIR__|$(pwd)|g" \
    -e "s|__USER__|$(whoami)|g" \
    -e "s|__CONDA_PYTHON__|$(conda run -n robojudo which python)|g" \
    gamepad_listener.service | sudo tee /etc/systemd/system/gamepad_listener.service

# 3. 重载并启用
sudo systemctl daemon-reload
sudo systemctl enable gamepad_listener.service
sudo systemctl start gamepad_listener.service

# 4. 配置 sudo 免密
echo "$(whoami) ALL=(ALL) NOPASSWD: /usr/bin/systemctl stop gamepad_listener, /usr/bin/systemctl start gamepad_listener" | sudo tee /etc/sudoers.d/gamepad_listener
sudo chmod 440 /etc/sudoers.d/gamepad_listener
```

---

## 使用方法

### 服务管理

```bash
# 查看服务状态
systemctl status gamepad_listener

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
# 查看监听器日志
tail -f gamepad_listener.log

# 查看任务运行日志
tail -f run.log
```

---

## 手柄操作

| 按键组合 | 功能 |
|---------|------|
| L1 + R1 + A | 启动机器人任务脚本 |
| L1 + R1 + B | 停止监听，交还控制权给 PC1 |

---

## 故障排除

### 1. 服务无法启动

```bash
# 检查服务状态
systemctl status gamepad_listener

# 查看错误日志
sudo journalctl -u gamepad_listener --no-pager
```

### 2. 安装脚本找不到 conda 环境

```bash
# 手动指定 conda 路径后重新运行
conda activate robojudo
CONDA_PREFIX=$(conda info --base)/envs/robojudo ./setup_gamepad_service.sh
```

### 3. 手柄未检测到

- 确保手柄已正确连接到机器人
- 检查机器人是否开机
- 确认网络连接正常

### 4. 任务启动失败

```bash
# 检查任务日志
tail -f run.log

# 手动测试任务脚本
python scripts/run_pipeline_real.py
```

### 5. 手柄按键无法停止服务（sudo 免密问题）

```bash
# 检查免密配置
cat /etc/sudoers.d/gamepad_listener

# 手动修复
echo "$(whoami) ALL=(ALL) NOPASSWD: /usr/bin/systemctl stop gamepad_listener, /usr/bin/systemctl start gamepad_listener" | sudo tee /etc/sudoers.d/gamepad_listener
sudo chmod 440 /etc/sudoers.d/gamepad_listener
```

### 6. 卸载服务

```bash
# 停止并禁用服务
sudo systemctl stop gamepad_listener
sudo systemctl disable gamepad_listener

# 删除服务文件
sudo rm /etc/systemd/system/gamepad_listener.service
sudo rm /etc/sudoers.d/gamepad_listener
sudo systemctl daemon-reload
```

---

## 技术细节

- **Python 环境**: conda `robojudo`
- **手柄检测**: Unitree 机器人接口
- **进程管理**: psutil 库 + systemd
- **系统服务**: systemd `Type=simple`
- **权限控制**: `/etc/sudoers.d/gamepad_listener`
- **日志位置**: `./gamepad_listener.log`（监听器），`./run.log`（任务）

---

## 工作原理

1. **开机自启动**: systemd 在系统启动时自动运行监听服务
2. **手柄监听**: 通过 Unitree 机器人接口获取手柄数据
3. **按键检测**: 监听特定组合键 (L1+R1+A/B)
4. **服务控制**: 使用 systemctl 命令管理服务生命周期
5. **路径自动检测**: 安装脚本自动检测 conda python 路径，跨机器可移植

---

## 跨机器部署说明

本项目所有路径相关配置均通过 `setup_gamepad_service.sh` 自动检测，无硬编码路径。在任何 Unitree G1 机器人上部署的步骤：

```bash
# 1. 克隆项目
git clone <your-repo-url>
cd RoboJuDo_SAR

# 2. 安装依赖
conda activate robojudo  # 或 robojudo_sar
pip install -e .
cd packages/unitree_cpp && pip install -e . && cd ../..

# 3. 一键安装手柄监听服务
./setup_gamepad_service.sh
```

如果需要修改 conda 环境名称（如使用 `robojudo_sar` 而非 `robojudo`），请确保：
1. 激活正确的环境后再运行安装脚本
2. 或者手动指定环境：`CONDA_DEFAULT_ENV=robojudo_sar ./setup_gamepad_service.sh`

---

## 更新说明

如需更新脚本：

```bash
# 停止服务
sudo systemctl stop gamepad_listener

# 拉取最新代码
git pull

# 重新运行安装脚本（会自动处理更新）
./setup_gamepad_service.sh
```
