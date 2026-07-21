# RoboJuDo_Hero

<div align="center">

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC_BY_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)

**基于 RoboJuDo 的模块化机器人仿真框架，扩展了更多策略与功能**

</div>

> **[English Version](README.md)**

---

## 📖 概述

RoboJuDo_Hero 是基于 [RoboJuDo](https://github.com/HansZ8/RoboJuDo) (作者 HansZ8) 的衍生项目，RoboJuDo 是一个模块化机器人仿真框架。本项目在原框架基础上扩展了更多的策略、改进的仿真能力以及增强的真实机器人集成。

### 原始 RoboJuDo

原始 RoboJuDo 框架提供模块化架构用于机器人仿真与部署，支持多种机器人平台（Unitree G1、H1）和多种策略（BeyondMimic、ASAP、KungfuBot 等）。

### RoboJuDo_SAR 分支特性

**RoboJuDo_SAR**（SimAndReal，仿真与真实）分支包含以下新特性：

- **真实机器人分支仿真**：在真实机器人部署分支上成功集成并测试了仿真能力
- **BFMZero 策略**：添加了对 [BFMZero](https://github.com/OpenBMB/BFMZero) 项目的支持，包含多种模式（Tracking、Reward、Goal）
- **GentleHumanoid 策略**：添加了对 [GentleHumanoid](https://github.com/GentleHumanoid/gentleHum) 项目的支持，包含运动跟踪与柔顺控制
- **多种 GVHMR2GMR2BeyondMimic 策略**：查看我的 [Video2Mimic](https://github.com/Kennyp-Chen/Video2Mimic) 了解 GVHMR+GMR 工作流
- **UnitreeMJLab 策略**：添加了对 [UnitreeMJLab](https://github.com/unitreerobotics/unitree_rl_mjlab) 项目的支持，用于 Unitree 机器人控制
- **GMR-AMP 策略**：添加了对 [legged_lab](https://github.com/zitongbai/legged_lab) 基于 AMP 的行走策略支持。包含 walk 和 run 两种变体（目前在仿真和真机上效果均不佳）

### 真实机器人部署改进

- **自动退出 PC2**：当 `run_pipeline_real` 脚本在 Unitree G1 PC2 上退出时，自动释放 PC2 控制权，返回 PC1 的官方零力矩模式
- **摇杆监听器**：添加了监听器，一次性配置网络（以太网/WiFi）后即可自动监控摇杆命令：
  - `L1 + R1 + A`：启动 `run_pipeline_real`
  - `L1 + R1 + B`：退出 PC2 控制，返回 PC1 控制
- **坐姿启动**：实现了坐姿启动，无需吊挂启动，机器人可直接从椅子上启动

## 🚀 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/Kennyp-Chen/RoboJuDo_Hero.git
cd RoboJuDo_Hero/

# 从 HuggingFace 下载模型文件
# （模型文件因体积过大已迁移至 HuggingFace）
# 下载到 assets/ 目录，最终结构为：
#   assets/models/  （来自 HuggingFace）
huggingface-cli download Kennyp-Chen/robojudo_sar-assets --local-dir assets/ --repo-type dataset

# 创建 Python 环境
conda create -n robojudo_sar python=3.11 -y
conda activate robojudo_sar

# 安装依赖
pip install -e .
```

> **关于 conda 环境名称**：项目默认期望 conda 环境名为 `robojudo_sar`。导入 `robojudo` 时，会通过 `CONDA_DEFAULT_ENV` 环境变量检查当前激活的环境。如果使用了不同的环境名称，会显示一条警告。
>
> 如需使用其他环境名称并消除警告，请修改 `robojudo/__init__.py` 中的 `_REQUIRED_CONDA_ENV` 变量：
> ```python
> _REQUIRED_CONDA_ENV = "your_env_name"
> ```

### 运行仿真

```bash
# BFMZero 策略 - Tracking 模式
python scripts/run_pipeline_sim.py -c g1_bfmzero_tracking

# BFMZero 策略 - Reward 模式
python scripts/run_pipeline_sim.py -c g1_bfmzero_reward

# BFMZero 策略 - Goal 模式
python scripts/run_pipeline_sim.py -c g1_bfmzero_goal

# GentleHumanoid 策略
python scripts/run_pipeline_sim.py -c g1_gentle

# 多种 BeyondMimic 策略
python scripts/run_pipeline_sim.py -c g1_locomimic_sim

# UnitreeMJLab 策略
python scripts/run_pipeline_sim.py -c g1_unitree_mjlab_velocity

# KungFuAthlete 策略（运动跟踪）
python scripts/run_pipeline_sim.py -c g1_kungfuathlete

# GMR-AMP 行走策略（实验性）
python scripts/run_pipeline_sim.py -c g1_amp
```

### 在真机上运行

**安装（在 Unitree G1 PC2 上）**

UnitreeCpp 已安装在 `packages` 目录中，无需再次克隆。安装前，请确保 PC2 上已安装以下依赖：

- **Unitree SDK2**（参见 [unitree_sdk2](https://github.com/unitreerobotics/unitree_sdk2)）
- **Cyclone DDS**（ddsc / ddscxx）

然后进入 `unitree_cpp` 目录，编译并安装 Python 绑定：

```bash
cd packages/unitree_cpp
pip install -e .
```

> `pip install` 命令会通过 `scikit-build-core` **触发 CMake 编译**，构建 C++ pybind11 模块，确保与机器人通信时的实时性能。

**配置**

在 `robojudo/config/g1/g1_custom_cfg.py` 中配置网络接口：

```python
class g1_real_locomimic(g1):
    env: G1RealEnvCfg = G1RealEnvCfg(
        env_type="UnitreeCppEnv",
        unitree=G1UnitreeCfg(
            net_if="eth0",  # 更改为你的网络接口
        ),
    )
```

**运行**

完成接口配置后，在项目目录下运行以下命令：

```bash
python scripts/run_pipeline_real.py -c g1_real_locomimic
```

此配置结合了 **Unitree RL MJLab Velocity** 策略和 **BeyondMimic** 策略。

机器人将进入坐姿。

**游戏手柄监听器设置（可选）**

要在 G1 PC2 上启用自动摇杆监控：

```bash
# 1. 运行设置脚本
sh setup_gamepad_service.sh

# 2. 编辑 sudoers 文件
sudo visudo

# 3. 在文件末尾添加以下行
unitree ALL=(ALL) NOPASSWD: /bin/systemctl stop gamepad_listener, /bin/systemctl start gamepad_listener

# 4. 保存并退出
```

设置完成后，监听器将自动启动并监控摇杆命令：
- `L1 + R1 + A`：启动 `run_pipeline_real`
- `L1 + R1 + B`：退出 PC2 控制，返回 PC1 控制

**新增策略的真机部署配置**

以下真机配置已添加至 `robojudo/config/g1/g1_cfg.py`：

| 配置名 | 策略 | 控制器支持 |
|--------|------|-----------|
| `g1_bfmzero_tracking_real` | BFMZero Tracking | Unitree 手柄 + SSH 键盘 |
| `g1_bfmzero_reward_real`   | BFMZero Reward   | Unitree 手柄 + SSH 键盘 |
| `g1_bfmzero_goal_real`     | BFMZero Goal     | Unitree 手柄 + SSH 键盘 |
| `g1_kungfuathlete_real` | KungFuAthlete | Unitree 手柄 + SSH 键盘 |
| `g1_amp_real` | GMR-AMP Walk | Unitree 手柄（摇杆）+ SSH 键盘 |
| `g1_wbc_amp_real` | WBC FSM AMP Loco | Unitree 手柄（摇杆）+ SSH 键盘 |
| `g1_wbc_dance_real` | WBC FSM Dance | Unitree 手柄 + SSH 键盘 |

**Unitree 手柄操作指南**

所有配置使用相同的按键约定。按住 **L1 + R1 + L2** 进入命令模式，然后按对应按钮触发功能：

| 按钮 | BFMZero | KungFuAthlete | AMP / WBC AMP | WBC Dance |
|------|---------|---------------|---------------|-----------|
| **A** | 🛑 紧急停止 | 🛑 紧急停止 | 🛑 紧急停止 | 🛑 紧急停止 |
| **B** | ▶ 开始动作 | ⏸ 暂停动作 | — | ⏹ 停止动作 |
| **X** | 🔄 重置停止状态 | ▶ 开始/恢复动作 | — | ▶ 开始动作 |
| **Y** | ⏭ 下一个 Reward/Goal | 🔄 重置动作进度 | — | 🔄 重置动作 |
| **R2** | ⏹ 动作归零（安全用） | — | — | — |
| **上 (↑)** | — | ⏭ 加载下一个动作 | — | — |
| **下 (↓)** | — | ⏮ 加载上一个动作 | — | — |
| **左摇杆** | — | — | 前后/左右移动速度 | — |
| **右摇杆** | — | — | 转向速度 | — |

> **⚠️ 安全提醒**：以上策略（BFMZero、KungFuAthlete、GMR-AMP、WBC FSM）均仅在**仿真中测试过**，**尚未在真机上验证**。请谨慎使用，确保随时可触发急停（A 按钮或 Esc 键）。

## 📋 新策略一览

| 策略 | 仿真 | 真机 | 项目链接 | 描述 |
|--------|-----------|------------|--------------|-------------|
| **BFMZero** | 🖥️ | - | [BFMZero](https://github.com/LeCAR-Lab/BFM-Zero) | 多模式策略，支持 Tracking、Reward、Goal 模式 |
| **GentleHumanoid** | 🖥️ | - | [GentleHumanoid](https://github.com/Axellwppr/gentle-humanoid) | 带柔顺控制的运动跟踪 |
| **UnitreeMJLab** | 🖥️ | 🤖 | [UnitreeMJLab](https://github.com/unitreerobotics/unitree_rl_mjlab) | Unitree 机器人速度控制策略 |
| **BeyondMimic (GVHMR2GMR)** | 🖥️ | 🤖 | [BeyondMimic](https://github.com/HybridRobotics/whole_body_tracking) | 多种运动跟踪策略（查看 [Video2Mimic](https://github.com/Kennyp-Chen/Video2Mimic) 了解 GVHMR+GMR 工作流） |
| **KungFuAthlete** | 🖥️ | - | [KungFuAthleteBot](https://github.com/NPCLEI/KungFuAthleteBot) | 武术动作运动跟踪数据集与策略（太极拳、拳术、刀剑、技巧翻跃），支持跌倒恢复 |
| **GMR-AMP** | 🖥️ | - | [legged_lab](https://github.com/zitongbai/legged_lab) | 基于 AMP 的 GMR 行走策略（含 walk 与 run 变体，目前在仿真和真机上效果均不佳） |
| **WBC FSM (AMP Loco)** | 🖥️ | - | [wbc_fsm](https://github.com/ccrpRepo/wbc_fsm) | WBC FSM AMP 行走策略，4 帧历史输入，支持跌倒恢复，仿真已验证 |
| **WBC FSM (Dance)** | 🖥️ | - | [wbc_fsm](https://github.com/ccrpRepo/wbc_fsm) | WBC FSM 舞蹈动作跟踪策略，使用 LAFAN1 参考动作数据，支持跌倒恢复，仿真已验证 |

🖥️ 表示策略已准备好用于仿真，🤖 表示已在真机上测试过。

## 🔧 配置

所有新策略配置位于 `robojudo/config/g1/`：

仿真配置（位于 `g1_custom_cfg.py` 和 `g1_cfg.py`）：
- `g1_bfmzero_tracking` — BFMZero tracking 模式
- `g1_bfmzero_reward` — BFMZero reward 模式
- `g1_bfmzero_goal` — BFMZero goal 模式
- `g1_gentle` — GentleHumanoid 策略
- `g1_locomimic_sim` — 多种 BeyondMimic 策略
- `g1_unitree_mjlab_velocity` — UnitreeMJLab 速度控制
- `g1_kungfuathlete` — KungFuAthlete 运动跟踪
- `g1_amp` — GMR-AMP 行走策略（实验性）
- `g1_wbc_amp` — WBC FSM AMP Loco 行走策略（4 帧历史，支持跌倒恢复）
- `g1_wbc_dance` — WBC FSM Dance 舞蹈动作跟踪策略（需 LAFAN1 参考动作数据）

真机部署配置（位于 `g1_cfg.py`）：
- `g1_bfmzero_tracking_real` — BFMZero Tracking 真机部署
- `g1_bfmzero_reward_real` — BFMZero Reward 真机部署
- `g1_bfmzero_goal_real` — BFMZero Goal 真机部署
- `g1_kungfuathlete_real` — KungFuAthlete 真机部署
- `g1_amp_real` — GMR-AMP 真机部署
- `g1_wbc_amp_real` — WBC FSM AMP Loco 真机部署
- `g1_wbc_dance_real` — WBC FSM Dance 真机部署

## 📚 文档

关于原始 RoboJuDo 框架的详细文档，请参考 [README_RoboJuDo.md](README_RoboJuDo.md)。

### AI Coding：AGENTS.MD 与策略 Skill 文档

本仓库提供了结构化的文档，用于辅助 AI 编码代理在扩展新策略时使用：

- **[AGENTS.MD](AGENTS.MD)** — AI 代理在本仓库工作时首先应阅读的文件。它定义了项目的架构、硬性规则、代码规范以及验证流程。该文件源自 HansZ8 的 [RoboJuDo 项目](https://github.com/HansZ8/RoboJuDo/blob/dev/agent-init/AGENTS.md)，已针对本分支进行适配。感谢 RoboJuDo 作者提供这一基础性参考文档，使得 AI 辅助开发能够保持一致性。

- **[docs/add-new-policy.md](docs/add-new-policy.md) / [English](docs/add-new-policy-en.md)** — 向 RoboJuDo 框架添加新人形机器人 RL 策略（Actor NN）的分步指南。涵盖完整工作流：配置创建、自由度设置、策略实现、注册、流水线配置和验证。

- **[docs/extract-policy-config.md](docs/extract-policy-config.md) / [English](docs/extract-policy-config-en.md)** — 从外部 RL 训练项目中提取配置信息的指南，生成标准化摘要供 `add-new-policy` 工作流使用。

**推荐的 AI 辅助策略集成工作流：**
1. 阅读 [AGENTS.MD](AGENTS.MD) 了解项目规范
2. 使用 [docs/extract-policy-config.md](docs/extract-policy-config.md) 从训练项目中提取配置
3. 使用 [docs/add-new-policy.md](docs/add-new-policy.md) 生成策略实现代码

## 🤝 贡献

本项目基于 HansZ8 的 [RoboJuDo](https://github.com/HansZ8/RoboJuDo)。欢迎贡献，扩展更多策略与功能。

## 📄 许可证

本项目继承了原始 RoboJuDo 项目的 CC BY 4.0 许可证。详情请见 [LICENSE](LICENSE)。

## 🙏 致谢

- [RoboJuDo](https://github.com/HansZ8/RoboJuDo) — 原始模块化机器人仿真框架
- [BFMZero](https://github.com/LeCAR-Lab/BFM-Zero) — BFMZero 项目（LeCAR-Lab）
- [GentleHumanoid](https://github.com/GentleHumanoid/gentleHum) — GentleHumanoid 项目
- [UnitreeRlMjLab](https://github.com/unitreerobotics/unitree_rl_mjlab) — Unitree 机器人学习实验室
- [BeyondMimic](https://github.com/HybridRobotics/whole_body_tracking) — 全身运动跟踪
- [KungFuAthleteBot](https://github.com/NPCLEI/KungFuAthleteBot) — KungFuAthlete 运动跟踪项目
- [legged_lab](https://github.com/zitongbai/legged_lab) — GMR-AMP 行走策略
- [wbc_fsm](https://github.com/ccrpRepo/wbc_fsm) — WBC FSM 行走与舞蹈策略
