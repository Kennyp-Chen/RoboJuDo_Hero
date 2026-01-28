# BeyondMimic Real Robot Deployment Guide

## 📋 概述

`g1_beyondmimic_real` 配置用于在真实 Unitree G1 机器人上部署 BeyondMimic 动作模仿策略。

## ⚠️ 安全警告

**在真实机器人上运行动作模仿策略前，请务必：**

1. ✅ 确保机器人周围有足够的空间（至少 2m x 2m）
2. ✅ 清除周围所有障碍物
3. ✅ 准备好紧急停止按钮（ESC 键）
4. ✅ 有人在旁边监督，随时准备按紧急停止
5. ✅ 先在模拟器中测试动作（`g1_beyondmimic`）
6. ✅ 从简单、幅度小的动作开始测试（如 Jump_wose）
7. ⚠️ **不要**在机器人附近站立或放置贵重物品
8. ⚠️ **不要**在不平坦的地面上运行

## 🚀 快速开始

### 1. 准备工作

```bash
# 确保在 robojudo 环境中
conda activate robojudo

# 进入项目目录
cd ~/chenyupeng/sim2real/RoboJuDo

# 检查网络接口（确认机器人连接的网卡）
ifconfig
# 如果不是 eth0，需要修改配置文件中的 net_if
```

### 2. 先在模拟器中测试

```bash
# 在模拟器中测试动作
python scripts/run_pipeline.py -c g1_beyondmimic

# 观察动作是否正常
# 按 ESC 退出
```

### 3. 准备真实机器人

按照 [Unitree 官方指南](https://github.com/unitreerobotics/unitree_rl_gym/blob/main/deploy/deploy_real/README.md#startup-process) 准备机器人：

1. 打开机器人电源
2. 等待机器人初始化完成
3. 确保机器人处于站立状态
4. 确保急停开关未按下

### 4. 运行部署

```bash
# 使用 SSH X11 转发连接（如果需要键盘控制）
# 在本地电脑上：
ssh -X unitree@<jetson-ip>

# 在 Jetson 上运行
cd ~/chenyupeng/sim2real/RoboJuDo
python scripts/run_pipeline.py -c g1_beyondmimic_real
```

## 🎮 控制说明

### 键盘控制

| 按键 | 功能 | 说明 |
|------|------|------|
| `ESC` | 紧急停止 | 立即进入阻尼模式，机器人关节变软 |
| `Shift + <` | 开始/继续播放 | 开始执行动作或继续暂停的动作 |
| `Shift + >` | 暂停播放 | 暂停当前动作 |
| `Shift + \|` | 重置进度 | 将动作重置到开始位置 |
| `` ` `` | 重生（仅模拟） | 在真实机器人上无效 |

### 注意事项

- ⚠️ **动作会自动循环播放**，需要手动按 ESC 停止
- ⚠️ **ESC 键是紧急停止**，机器人会立即进入阻尼模式
- ⚠️ 动作播放期间**无法**用 WASD 控制移动

## 🎭 可用动作

在配置文件中修改 `policy_name` 来选择不同的动作：

```python
# 编辑 RoboJuDo/robojudo/config/g1/g1_cfg.py
# 找到 g1_beyondmimic_real 配置

policy: G1BeyondMimicPolicyCfg = G1BeyondMimicPolicyCfg(
    # 选择一个动作：
    policy_name="Jump_wose",      # 跳跃（推荐首次测试）
    # policy_name="Dance_wose",   # 舞蹈
    # policy_name="Violin",       # 拉小提琴
    # policy_name="Waltz",        # 华尔兹
    
    # 其他参数保持不变
    without_state_estimator=True,
    use_modelmeta_config=True,
    use_motion_from_model=True,
    max_timestep=140,  # 根据动作长度调整
)
```

### 动作特点

| 动作名称 | 难度 | 空间需求 | 建议 max_timestep | 说明 |
|---------|------|----------|------------------|------|
| `Jump_wose` | ⭐ 简单 | 小 | 140 | 原地跳跃，推荐首次测试 |
| `Dance_wose` | ⭐⭐ 中等 | 中 | 200-300 | 舞蹈动作，需要更多空间 |
| `Violin` | ⭐⭐⭐ 复杂 | 中 | 500 | 拉小提琴动作，上肢为主 |
| `Waltz` | ⭐⭐⭐ 复杂 | 大 | 850 | 华尔兹舞步，需要大空间 |

## 🔧 配置说明

### 网络接口配置

如果机器人连接的网卡不是 `eth0`，需要修改：

```python
env: G1RealEnvCfg = G1RealEnvCfg(
    env_type="UnitreeCppEnv",
    unitree=G1UnitreeCfg(
        net_if="eth0",  # 改为实际的网卡名称，如 "enp2s0"
    ),
)
```

### 动作时长配置

不同动作需要不同的 `max_timestep`：

```python
policy: G1BeyondMimicPolicyCfg = G1BeyondMimicPolicyCfg(
    policy_name="Waltz",
    max_timestep=850,  # 华尔兹需要更长的时间
    # ...
)
```

### 使用不同的 SDK

如果想使用 `unitree_sdk2py` 而不是 `unitree_cpp`：

```python
env: G1RealEnvCfg = G1RealEnvCfg(
    env_type="UnitreeEnv",  # 使用 Python SDK
    unitree=G1UnitreeCfg(
        net_if="eth0",
    ),
)
```

## 📊 运行流程

1. **初始化阶段**（约 2 秒）
   - 加载 ONNX 模型
   - 连接机器人
   - 初始化控制器

2. **准备阶段**（约 2 秒）
   - 机器人移动到初始姿势
   - 等待稳定

3. **执行阶段**
   - 自动开始播放动作
   - 动作循环执行
   - 实时监控安全状态

4. **停止阶段**
   - 按 ESC 或检测到危险
   - 进入阻尼模式
   - 程序继续运行（需要 Ctrl+C 完全退出）

## 🐛 故障排除

### 问题 1：连接失败

```
Error: Failed to connect to robot
```

**解决方案：**
1. 检查网线是否连接
2. 检查网卡名称是否正确（`ifconfig`）
3. 检查机器人是否开机
4. 尝试 ping 机器人 IP

### 问题 2：键盘不响应

```
Error: failed to acquire X connection
```

**解决方案：**
使用 SSH X11 转发：
```bash
ssh -X unitree@<jetson-ip>
```

### 问题 3：机器人动作异常

**解决方案：**
1. 立即按 ESC 停止
2. 检查地面是否平坦
3. 检查周围是否有障碍物
4. 先在模拟器中测试动作
5. 尝试更简单的动作（Jump_wose）

### 问题 4：帧率下降

```
Warning: frame drop -> -0.15
```

**解决方案：**
1. 这是正常的，Jetson 性能有限
2. 如果帧率下降超过 -0.2，程序会自动停止
3. 关闭其他占用 CPU 的程序

### 问题 5：模型文件缺失

```
Error: Model file not found
```

**解决方案：**
确保模型文件存在：
```bash
ls assets/models/g1/beyondmimic/
# 应该看到：Jump_wose.onnx, Dance_wose.onnx, Violin.onnx, Waltz.onnx
```

## 📝 最佳实践

### 首次部署流程

1. ✅ 在模拟器中测试：`python scripts/run_pipeline.py -c g1_beyondmimic`
2. ✅ 选择简单动作：使用 `Jump_wose`
3. ✅ 准备环境：清空 2m x 2m 空间
4. ✅ 准备急停：手放在键盘 ESC 键上
5. ✅ 开始测试：`python scripts/run_pipeline.py -c g1_beyondmimic_real`
6. ✅ 观察动作：确认动作正常
7. ✅ 逐步尝试：成功后再尝试复杂动作

### 安全检查清单

- [ ] 机器人周围 2m 内无障碍物
- [ ] 地面平坦、干燥
- [ ] 有人在旁边监督
- [ ] 手放在 ESC 键上
- [ ] 已在模拟器中测试过动作
- [ ] 了解紧急停止流程
- [ ] 机器人电量充足（>30%）

## 🔗 相关配置

- `g1_beyondmimic` - 模拟器版本（用于测试）
- `g1_beyondmimic_with_ctrl` - 使用外部动作控制器
- `g1_switch_beyondmimic` - 多动作切换（模拟器）
- `g1_real` - 基础运动控制（真实机器人）

## 📚 参考资料

- [BeyondMimic 论文](https://github.com/HybridRobotics/whole_body_tracking)
- [Unitree G1 文档](https://github.com/unitreerobotics/unitree_rl_gym)
- [RoboJuDo 文档](../README.md)

---

**记住：安全第一！** 在真实机器人上运行任何动作前，请务必做好充分准备和安全措施。
