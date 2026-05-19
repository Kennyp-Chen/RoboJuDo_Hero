# Unitree G1 Sim2Sim配置文档

## 概述
本文档提供Unitree G1机器人强化学习策略的sim2sim迁移所需的核心配置信息。

## 1. 模型基本信息

### 1307策略模型
- **文件路径**: `models/1307/1307.pt`
- **机器人型号**: Unitree G1 (29-DOF)
- **任务类型**: Motion Tracking (站立姿态)
- **动作内容**: **Taichi武术动作** ⭐
- **观测空间**: Actor 154维
- **动作空间**: 29维 (关节位置控制)

**📋 Taichi动作说明**:
- **动作文件**: `src/assets/motions/g1/1307.npz`
- **动作类型**: 传统武术太极拳动作序列
- **训练目标**: 复现复杂的武术动作轨迹
- **应用场景**: 武术表演、动作展示、文化传承

## 2. Actor观测空间配置

### 标准Standing配置 (160维)
| 观测项 | 维度 | 描述 |
|--------|------|------|
| command | 58 | 运动命令 |
| motion_anchor_pos_b | 3 | 运动锚点位置(身体坐标系) |
| motion_anchor_ori_b | 6 | 运动锚点方向(身体坐标系) |
| base_lin_vel | 3 | 基座线速度 |
| base_ang_vel | 3 | 基座角速度 |
| joint_pos | 29 | 关节位置 |
| joint_vel | 29 | 关节速度 |
| actions | 29 | 上一步动作 |
| **总计** | **160** | |

### 1307模型配置 (154维) ⭐
| 观测项 | 维度 | 描述 |
|--------|------|------|
| command | 58 | 运动命令 |
| motion_anchor_ori_b | 6 | 运动锚点方向(身体坐标系) |
| base_ang_vel | 3 | 基座角速度 |
| joint_pos | 29 | 关节位置 |
| joint_vel | 29 | 关节速度 |
| actions | 29 | 上一步动作 |
| **总计** | **154** | |

### 📋 配置差异说明

**1307模型剔除的观测项**:
- ❌ `motion_anchor_pos_b` (3维): 运动锚点位置
- ❌ `base_lin_vel` (3维): 基座线速度

## 3. 动作空间配置 (29维)

### 关节位置控制
- **控制方式**: PD位置控制
- **动作缩放**: 每个关节独立缩放 (见下表)
- **默认偏移**: 使用机器人默认关节位置

### 关节参数映射表

| 关节索引 | 关节名称 | 执行器类型 | stiffness (Nm/rad) | damping (Nm·s/rad) | action_scale |
|----------|----------|------------|-------------------|-------------------|-------------|
| 0 | left_hip_pitch_joint | 7520_14 | 40.179 | 2.558 | 0.547546 |
| 1 | left_hip_roll_joint | 7520_22 | 99.098 | 6.309 | 0.350661 |
| 2 | left_hip_yaw_joint | 7520_14 | 40.179 | 2.558 | 0.547546 |
| 3 | left_knee_joint | 7520_22 | 99.098 | 6.309 | 0.350661 |
| 4 | left_ankle_pitch_joint | 5020_ankle | 28.501 | 1.814 | 0.438577 |
| 5 | left_ankle_roll_joint | 5020_ankle | 28.501 | 1.814 | 0.438577 |
| 6 | right_hip_pitch_joint | 7520_14 | 40.179 | 2.558 | 0.547546 |
| 7 | right_hip_roll_joint | 7520_22 | 99.098 | 6.309 | 0.350661 |
| 8 | right_hip_yaw_joint | 7520_14 | 40.179 | 2.558 | 0.547546 |
| 9 | right_knee_joint | 7520_22 | 99.098 | 6.309 | 0.350661 |
| 10 | right_ankle_pitch_joint | 5020_ankle | 28.501 | 1.814 | 0.438577 |
| 11 | right_ankle_roll_joint | 5020_ankle | 28.501 | 1.814 | 0.438577 |
| 12 | waist_yaw_joint | 7520_14 | 40.179 | 2.558 | 0.547546 |
| 13 | waist_roll_joint | 5020_waist | 28.501 | 1.814 | 0.438577 |
| 14 | waist_pitch_joint | 5020_waist | 28.501 | 1.814 | 0.438577 |
| 15 | left_shoulder_pitch_joint | 5020 | 14.251 | 0.907 | 0.438577 |
| 16 | left_shoulder_roll_joint | 5020 | 14.251 | 0.907 | 0.438577 |
| 17 | left_shoulder_yaw_joint | 5020 | 14.251 | 0.907 | 0.438577 |
| 18 | left_elbow_joint | 5020 | 14.251 | 0.907 | 0.438577 |
| 19 | left_wrist_roll_joint | 5020 | 14.251 | 0.907 | 0.438577 |
| 20 | left_wrist_pitch_joint | 4010 | 16.778 | 1.068 | 0.074501 |
| 21 | left_wrist_yaw_joint | 4010 | 16.778 | 1.068 | 0.074501 |
| 22 | right_shoulder_pitch_joint | 5020 | 14.251 | 0.907 | 0.438577 |
| 23 | right_shoulder_roll_joint | 5020 | 14.251 | 0.907 | 0.438577 |
| 24 | right_shoulder_yaw_joint | 5020 | 14.251 | 0.907 | 0.438577 |
| 25 | right_elbow_joint | 5020 | 14.251 | 0.907 | 0.438577 |
| 26 | right_wrist_roll_joint | 5020 | 14.251 | 0.907 | 0.438577 |
| 27 | right_wrist_pitch_joint | 4010 | 16.778 | 1.068 | 0.074501 |
| 28 | right_wrist_yaw_joint | 4010 | 16.778 | 1.068 | 0.074501 |

### 参数列表（按关节索引顺序）

```python
stiffness: list[float] | None = [
    40.179, 99.098, 40.179, 99.098, 28.501, 28.501,  # 左腿
    40.179, 99.098, 40.179, 99.098, 28.501, 28.501,  # 右腿
    40.179, 28.501, 28.501,                            # 腰部
    14.251, 14.251, 14.251, 14.251, 14.251,          # 左臂
    16.778, 16.778,                                    # 左手腕
    14.251, 14.251, 14.251, 14.251, 14.251,          # 右臂
    16.778, 16.778                                     # 右手腕
]

damping: list[float] | None = [
    2.558, 6.309, 2.558, 6.309, 1.814, 1.814,        # 左腿
    2.558, 6.309, 2.558, 6.309, 1.814, 1.814,        # 右腿
    2.558, 1.814, 1.814,                              # 腰部
    0.907, 0.907, 0.907, 0.907, 0.907,              # 左臂
    1.068, 1.068,                                      # 左手腕
    0.907, 0.907, 0.907, 0.907, 0.907,              # 右臂
    1.068, 1.068                                       # 右手腕
]

action_scale: list[float] | None = [
    0.547546, 0.350661, 0.547546, 0.350661, 0.438577, 0.438577,  # 左腿
    0.547546, 0.350661, 0.547546, 0.350661, 0.438577, 0.438577,  # 右腿
    0.547546, 0.438577, 0.438577,                                  # 腰部
    0.438577, 0.438577, 0.438577, 0.438577, 0.438577,            # 左臂
    0.074501, 0.074501,                                          # 左手腕
    0.438577, 0.438577, 0.438577, 0.438577, 0.438577,            # 右臂
    0.074501, 0.074501                                             # 右手腕
]
```

## 4. 模型加载方式

### 标准rsl_rl加载方法 (基于play.py实现)
```python
from mjlab.rl import MjlabOnPolicyRunner
from mjlab.envs import ManagerBasedRlEnv
from mjlab.envs.wrappers import RslRlVecEnvWrapper

# 创建环境和配置
env = ManagerBasedRlEnv(cfg=env_cfg, device=device)
env = RslRlVecEnvWrapper(env, clip_actions=agent_cfg.clip_actions)

# 创建runner并加载模型
runner = MjlabOnPolicyRunner(env, agent_cfg, device=device)
runner.load(
    "models/1307/1307.pt", 
    load_cfg={"actor": True}, 
    strict=True, 
    map_location=device
)

# 获取推理策略
policy = runner.get_inference_policy(device=device)

# 推理
actions = policy(observations)
```

### 关键差异分析

| 方面 | 标准rsl_rl方法 | 简化PyTorch方法 |
|------|----------------|----------------|
| **依赖** | 需要完整rsl_rl环境 | 仅需PyTorch |
| **环境创建** | ManagerBasedRlEnv + RslRlVecEnvWrapper | 无需环境 |
| **模型加载** | runner.load() | torch.load() |
| **策略获取** | runner.get_inference_policy() | 自定义函数 |
| **观测处理** | 自动标准化 | 手动标准化 |
| **动作处理** | 自动clip_actions | 无clip处理 |
| **复杂度** | 高 (完整框架) | 低 (纯PyTorch) |

### 简化PyTorch加载方法
```python
import torch

# 加载checkpoint
checkpoint = torch.load("models/1307/1307.pt", map_location=device)
model_state_dict = checkpoint["model_state_dict"]

# 提取actor权重 (旧版格式使用actor.前缀)
actor_weights = {}
for key, value in model_state_dict.items():
    if key.startswith("actor."):
        new_key = key.replace("actor.", "")
        actor_weights[new_key] = value

# 提取观测标准化参数 (旧版格式)
obs_normalizer_mean = model_state_dict["actor_obs_normalizer._mean"]
obs_normalizer_std = model_state_dict["actor_obs_normalizer._std"]

# 创建推理函数
def simple_policy_inference(obs):
    # 观测标准化
    obs_norm = (obs - obs_normalizer_mean) / obs_normalizer_std
    
    # MLP前向传播 (3层隐藏层: 512->256->128->29)
    x = obs_norm
    for i in range(0, 6, 2):  # 6层权重: 0,1,2,3,4,5,6
        weight_key = f"{i}.weight"
        bias_key = f"{i}.bias"
        weight = actor_weights[weight_key]
        bias = actor_weights[bias_key]
        x = torch.nn.functional.elu(x @ weight.T + bias)
    
    # 输出层
    action = x @ actor_weights["6.weight"].T + actor_weights["6.bias"]
    return action

# 使用示例
obs = torch.randn(1, 154).to(device)
action = simple_policy_inference(obs)
print(f"输入观测: {obs.shape}, 输出动作: {action.shape}")
```

## 5. 迁移所需文件

### 必需文件
```
# 项目根目录: /home/hero/Projects/Robotics/RL/KungFuAthleteBot
unitree_rl_mjlab/models/1307/1307.pt                    # 训练好的策略模型
unitree_rl_mjlab/src/assets/motions/g1/1307.npz         # 参考运动文件
unitree_rl_mjlab/src/assets/motions/g1/robot_init_states_8192.pth  # 机器人初始状态
```

### 机器人配置文件
```
unitree_rl_mjlab/src/assets/robots/unitree_g1/g1_constants.py    # 关节常量和动作缩放
unitree_rl_mjlab/src/assets/robots/unitree_g1/g1_joint_order.yaml  # 关节顺序定义
```

### Command计算方法

#### 运动Command生成 (58维)
```python
def generate_motion_command(current_time, motion_data):
    """
    生成58维运动command
    
    Args:
        current_time: 当前时间
        motion_data: 运动数据 (从1307.npz加载)
    
    Returns:
        command: 58维向量
    """
    # Command结构 (58维):
    # [0-2]:   目标位置 (x, y, z) 
    # [3-6]:   目标方向四元数 (w, x, y, z)
    # [7-57]:  运动序列参数 (具体结构取决于运动数据)
    
    # 从运动文件中插值获取当前时刻的目标
    target_pos = interpolate_position(motion_data, current_time)
    target_ori = interpolate_orientation(motion_data, current_time)
    motion_params = interpolate_motion_params(motion_data, current_time)
    
    command = np.concatenate([
        target_pos,      # 3维
        target_ori,      # 4维 (四元数)
        motion_params    # 51维
    ])
    
    return command
```

#### 观测项计算方法

**motion_anchor_pos_b (3维)**:
```python
def compute_motion_anchor_pos_b(robot_state, motion_data):
    """计算运动锚点位置(身体坐标系)"""
    # 获取运动参考点在世界坐标系的位置
    anchor_world = get_motion_anchor_position(motion_data)
    # 转换到机器人身体坐标系
    robot_body_transform = get_robot_body_transform(robot_state)
    anchor_body = transform_to_body_frame(anchor_world, robot_body_transform)
    return anchor_body
```

**motion_anchor_ori_b (6维)**:
```python
def compute_motion_anchor_ori_b(robot_state, motion_data):
    """计算运动锚点方向(身体坐标系)"""
    # 获取运动参考方向在世界坐标系的表示
    anchor_world_quat = get_motion_anchor_orientation(motion_data)
    # 转换到机器人身体坐标系 (6维: 3轴角+3轴角速度)
    robot_body_quat = get_robot_body_orientation(robot_state)
    relative_quat = quaternion_multiply(anchor_world_quat, quaternion_inverse(robot_body_quat))
    return quat_to_axis_angle(relative_quat)  # 转换为6维表示
```

**base_lin_vel (3维)** & **base_ang_vel (3维)**:
```python
def compute_base_velocities(robot_state):
    """计算基座线速度和角速度"""
    base_lin_vel = robot_state['base_linear_velocity']  # 3维
    base_ang_vel = robot_state['base_angular_velocity'] # 3维
    return base_lin_vel, base_ang_vel
```

**joint_pos (29维)** & **joint_vel (29维)**:
```python
def compute_joint_states(robot_state):
    """计算关节位置和速度"""
    joint_pos = robot_state['joint_positions']   # 29维
    joint_vel = robot_state['joint_velocities']  # 29维
    return joint_pos, joint_vel
```

**actions (29维)**:
```python
def compute_last_actions(action_history):
    """获取上一步动作"""
    if len(action_history) > 0:
        return action_history[-1]  # 29维
    else:
        return np.zeros(29)        # 初始动作
```

## 6. Sim2Sim迁移步骤

### 1. 环境准备
```python
# 加载运动文件
motion_data = np.load('1307.npz')
robot_init_states = torch.load('robot_init_states_8192.pth')

# 设置机器人初始状态
robot.set_joint_positions(robot_init_states['joint_pos'][0])
robot.set_base_pose(robot_init_states['base_pose'][0])
```

### 2. 观测构建
```python
def build_observation(robot_state, motion_data, current_time, last_action):
    """构建154维观测向量"""
    
    # 计算各观测项
    command = generate_motion_command(current_time, motion_data)
    anchor_pos = compute_motion_anchor_pos_b(robot_state, motion_data)
    anchor_ori = compute_motion_anchor_ori_b(robot_state, motion_data)
    base_lin_vel, base_ang_vel = compute_base_velocities(robot_state)
    joint_pos, joint_vel = compute_joint_states(robot_state)
    
    # 构建154维观测
    observation = np.concatenate([
        command,        # 58维
        anchor_pos,     # 3维  
        anchor_ori,     # 6维
        base_lin_vel,   # 3维
        base_ang_vel,   # 3维
        joint_pos,      # 29维
        joint_vel,      # 29维
        last_action     # 29维
    ])
    
    return observation  # 总计154维
```

### 3. 动作执行
```python
# 获取策略输出
action = policy_inference(observation)

# 应用动作缩放
scaled_action = action * action_scale

# 设置目标关节位置
robot.set_joint_positions(scaled_action)

# 保存动作历史
action_history.append(action)
```
