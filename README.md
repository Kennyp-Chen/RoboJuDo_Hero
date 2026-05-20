# RoboJuDo_Hero

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)

**A modular robotics simulation framework based on RoboJuDo, enhanced with additional policies and features**

</div>

> **[中文版](README_CN.md)**

---

## 📖 Overview

RoboJuDo_Hero is a fork and extended version of [RoboJuDo](https://github.com/HansZ8/RoboJuDo), a modular robotics simulation framework. This project extends the original framework with additional policies, improved simulation capabilities, and enhanced real robot integration.

### Original RoboJuDo

The original RoboJuDo framework provides a modular architecture for robotics simulation and deployment, supporting multiple robot platforms (Unitree G1, H1) and various policies (BeyondMimic, ASAP, KungfuBot, etc.).

### RoboJuDo_SAR Branch Features

The **RoboJuDo_SAR** (SimAndReal) branch includes the following new features:

- **Simulation on Real Robot Branch**: Successfully integrated and tested simulation capabilities on the real robot deployment branch
- **BFMZero Policy**: Added support for [BFMZero](https://github.com/OpenBMB/BFMZero) project with multiple modes (Tracking, Reward, Goal)
- **GentleHumanoid Policy**: Added support for [GentleHumanoid](https://github.com/GentleHumanoid/gentleHum) project with motion tracking and compliance control
- **Multiple GVHMR2GMR2BeyondMimic Policies**: See my [Video2Mimic](https://github.com/Kennyp-Chen/Video2Mimic) for GVHMR+GMR workflow
- **UnitreeMJLab Policy**: Added support for [UnitreeMJLab](https://github.com/unitreerobotics/unitree_rl_mjlab) project for Unitree robot control

### Real Robot Deployment Improvements

- **Automatic PC2 Exit**: When the `run_pipeline_real` script exits on Unitree G1 PC2, it automatically releases PC2 control and returns to PC1's official zero-torque mode
- **Joystick Listener**: Added a listener that allows the robot to automatically monitor joystick commands after one-time network (Ethernet/WiFi) configuration:
  - `L1 + R1 + A`: Start `run_pipeline_real`
  - `L1 + R1 + B`: Exit PC2 control and return to PC1 control
- **Sitting Position Startup**: Implemented sitting position startup, eliminating the need for sling/hanging startup. The robot can now start directly from a chair

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/Kennyp-Chen/RoboJuDo_Hero.git
cd RoboJuDo_Hero/

# Pull model files managed by Git LFS
# (Required: model .onnx, .pt, .pkl files are stored via Git LFS)
git lfs install
git lfs pull

# Create a Python environment
conda create -n robojudo_sar python=3.11 -y
conda activate robojudo_sar

# Install dependencies
pip install -e .
```

### Running Simulations

```bash
# BFMZero Policy - Tracking mode
python scripts/run_pipeline_sim.py -c g1_bfmzero_tracking

# BFMZero Policy - Reward mode
python scripts/run_pipeline_sim.py -c g1_bfmzero_reward

# BFMZero Policy - Goal mode
python scripts/run_pipeline_sim.py -c g1_bfmzero_goal

# GentleHumanoid Policy
python scripts/run_pipeline_sim.py -c g1_gentle

# Multiple BeyondMimic Policies
python scripts/run_pipeline_sim.py -c g1_locomimic_sim

# UnitreeMJLab Policy
python scripts/run_pipeline_sim.py -c g1_unitree_mjlab_velocity

# KungFuAthlete Policy (motion tracking)
python scripts/run_pipeline_sim.py -c g1_kungfuathlete
```

### Running on Real Robot

**Installation**

UnitreeCpp has been installed in the `packages` directory. No need to clone again. To install:

```bash
cd packages/unitree_cpp
pip install -e .
```

**Configuration**

Configure the network interface in `robojudo/config/g1/g1_custom_cfg.py`:

```python
class g1_real_locomimic(g1):
    env: G1RealEnvCfg = G1RealEnvCfg(
        env_type="UnitreeCppEnv",
        unitree=G1UnitreeCfg(
            net_if="eth0",  # Change to your network interface
        ),
    )
```

**Running**

After completing the interface configuration, run the following command in the project directory:

```bash
python scripts/run_pipeline_real.py -c g1_real_locomimic
```

This configuration combines **Unitree RL MJLab Velocity** policy with **BeyondMimic** policy.

The robot will enter a sitting position.

**Gamepad Listener Setup (Optional)**

To enable automatic joystick monitoring on G1 PC2:

```bash
# 1. Run the setup script
sh setup_gamepad_service.sh

# 2. Edit sudoers file
sudo visudo

# 3. Add the following line at the end of the file
unitree ALL=(ALL) NOPASSWD: /bin/systemctl stop gamepad_listener, /bin/systemctl start gamepad_listener

# 4. Save and exit
```

After setup, the listener will automatically start and monitor for joystick commands:
- `L1 + R1 + A`: Start `run_pipeline_real`
- `L1 + R1 + B`: Exit PC2 control and return to PC1 control

## 📋 New Policies

| Policy | Simulation | Real Robot | Project Link | Description |
|--------|-----------|------------|--------------|-------------|
| **BFMZero** | 🖥️ 🤖 | - | [BFMZero](https://github.com/LeCAR-Lab/BFM-Zero) | Multi-mode policy with Tracking, Reward, and Goal modes |
| **GentleHumanoid** | 🖥️ 🤖 | - | [GentleHumanoid](https://github.com/Axellwppr/gentle-humanoid) | Motion tracking with compliance control |
| **UnitreeMJLab** | 🖥️ 🤖 | - | [UnitreeMJLab](https://github.com/unitreerobotics/unitree_rl_mjlab) | Unitree robot velocity control policy |
| **BeyondMimic (GVHMR2GMR)** | 🖥️ 🤖 | - | [BeyondMimic](https://github.com/HybridRobotics/whole_body_tracking) | Multiple motion tracking policies (see [Video2Mimic](https://github.com/Kennyp-Chen/Video2Mimic) for GVHMR+GMR workflow) |
| **KungFuAthlete** | 🖥️ 🤖 | - | [KungFuAthleteBot](https://github.com/NPCLEI/KungFuAthleteBot) | Martial arts motion tracking dataset & policy (Tai Chi, fist, saber, acrobatics) with fall recovery |

🖥️ means policy is ready for simulation, while 🤖 means policy has been tested on real robot.

## 🔧 Configuration

All new policy configurations are located in `robojudo/config/g1/g1_custom_cfg.py`:

- `g1_bfmzero_tracking` - BFMZero tracking mode
- `g1_bfmzero_reward` - BFMZero reward mode
- `g1_bfmzero_goal` - BFMZero goal mode
- `g1_gentle` - GentleHumanoid policy
- `g1_locomimic_sim` - Multiple BeyondMimic policies
- `g1_unitree_mjlab_velocity` - UnitreeMJLab velocity control
- `g1_kungfuathlete` - KungFuAthlete motion tracking

## 📚 Documentation

For detailed documentation on the original RoboJuDo framework, please refer to [README_RoboJuDo.md](README_RoboJuDo.md).

### AI Coding with AGENTS.MD & Policy Skills

This repository provides structured documentation to assist AI coding agents when extending the framework with new policies:

- **[AGENTS.MD](AGENTS.MD)** — The first file AI agents should read when working in this repo. It defines the project's architecture, hard rules, code conventions, and verification flow. This file originates from the [RoboJuDo project](https://github.com/HansZ8/RoboJuDo/blob/dev/agent-init/AGENTS.md) by HansZ8, adapted for this fork. We thank the RoboJuDo author for this foundational reference that enables consistent AI-assisted development.

- **[docs/add-new-policy.md](docs/add-new-policy.md) / [English](docs/add-new-policy-en.md)** — A step-by-step guide for adding a new humanoid robot RL policy (Actor NN) to the RoboJuDo framework. Covers the full workflow: config creation, DoF setup, policy implementation, registration, pipeline config, and verification.

- **[docs/extract-policy-config.md](docs/extract-policy-config.md) / [English](docs/extract-policy-config-en.md)** — A guide for extracting configuration information from external RL training projects, producing a standardized summary that can be consumed by the `add-new-policy` workflow.

**Recommended workflow for AI-assisted policy integration:**
1. Read [AGENTS.MD](AGENTS.MD) to understand project conventions
2. Use [docs/extract-policy-config.md](docs/extract-policy-config.md) to extract config from a training project
3. Use [docs/add-new-policy.md](docs/add-new-policy.md) to generate the policy implementation code

## 🤝 Contributing

This project is based on [RoboJuDo](https://github.com/HansZ8/RoboJuDo) by HansZ8. We welcome contributions to extend the framework with additional policies and features.

## 📄 License

This project inherits the MIT license from the original RoboJuDo project. See [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- [RoboJuDo](https://github.com/HansZ8/RoboJuDo) - The original modular robotics simulation framework
- [BFMZero](https://github.com/OpenBMB/BFMZero) - BFMZero project
- [GentleHumanoid](https://github.com/GentleHumanoid/gentleHum) - GentleHumanoid project
- [UnitreeRlMjLab](https://github.com/unitreerobotics/unitree_rl_mjlab) - Unitree robot learning lab
- [BeyondMimic](https://github.com/HybridRobotics/whole_body_tracking) - Whole body motion tracking
- [KungFuAthleteBot](https://github.com/NPCLEI/KungFuAthleteBot) - KungFuAthlete motion tracking project
