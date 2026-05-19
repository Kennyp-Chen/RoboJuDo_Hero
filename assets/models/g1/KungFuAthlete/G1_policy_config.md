# G1机器人策略输入输出文档 (29DOF版本)

## 策略输出 (Actions)

**维度**: 29维（G1机器人关节数）

**含义**: 每个关节的目标位置控制指令

**控制方法**: 
- 使用`JointPositionActionCfg`实现关节位置控制
- PD控制器跟踪目标位置
- 每个关节有独立的action scale
- scale = 0.25 × effort_limit / stiffness

## Actor观测输入（带噪声）

| 观测项 | 维度 | 描述 | 噪声范围 |
|--------|------|------|----------|
| command | 58 | 运动命令参数 | 无 |
| motion_anchor_pos_b | 3 | 锚点位置(机器人坐标系) | ±0.25 |
| motion_anchor_ori_b | 6 | 锚点方向(旋转矩阵前两行) | ±0.05 |
| base_lin_vel | 3 | 基座线速度 | ±0.5 |
| base_ang_vel | 3 | 基座角速度 | ±0.2 |
| joint_pos | 29 | 关节位置(相对) | ±0.01 |
| joint_vel | 29 | 关节速度 | ±0.5 |
| actions | 29 | 上一步动作 | 无 |

**总维度**: 160维

## 观测处理流程

1. **观测收集**: 各观测函数从环境传感器获取数据
2. **噪声添加**: 对指定观测项添加均匀噪声
3. **拼接**: 将所有观测项拼接成单一向量
4. **标准化**: 应用观测标准化参数

## 动作处理流程

1. **策略输出**: 神经网络输出29维动作向量
2. **动作缩放**: 应用G1_ACTION_SCALE缩放因子
3. **PD控制**: 转换为电机力矩指令
4. **环境执行**: MuJoCo仿真执行物理更新

## Sim2Sim迁移所需配置信息

### 机器人关节配置
- **关节数量**: 29个
- **关节类型**: 位置控制
- **关节名称列表**:
  ```python
  joint_names = [
      "left_hip_pitch_joint", "left_hip_roll_joint", "left_hip_yaw_joint",
      "left_knee_joint", "left_ankle_pitch_joint", "left_ankle_roll_joint",
      "right_hip_pitch_joint", "right_hip_roll_joint", "right_hip_yaw_joint", 
      "right_knee_joint", "right_ankle_pitch_joint", "right_ankle_roll_joint",
      "waist_yaw_joint", "waist_roll_joint", "waist_pitch_joint",
      "left_shoulder_pitch_joint", "left_shoulder_roll_joint", "left_shoulder_yaw_joint",
      "left_elbow_joint", "left_wrist_roll_joint", "left_wrist_pitch_joint", "left_wrist_yaw_joint",
      "right_shoulder_pitch_joint", "right_shoulder_roll_joint", "right_shoulder_yaw_joint",
      "right_elbow_joint", "right_wrist_roll_joint", "right_wrist_pitch_joint", "right_wrist_yaw_joint"
  ]
  ```
- **默认位置** (HOME_KEYFRAME):
  ```python
  joint_pos = {
      ".*_hip_pitch_joint": -0.1,
      ".*_knee_joint": 0.3,
      ".*_ankle_pitch_joint": -0.2,
      ".*_shoulder_pitch_joint": 0.35,
      ".*_elbow_joint": 0.87,
      "left_shoulder_roll_joint": 0.18,
      "right_shoulder_roll_joint": -0.18,
  }
  ```

### 执行器参数
#### 5020电机 (肘部、肩部、手腕)
- **stiffness**: 14.251 Nm/rad
- **damping**: 0.907 Nm·s/rad
- **effort_limit**: 25.0 Nm
- **动作缩放**: 0.438577

#### 7520_14电机 (髋部俯仰、偏航，腰部偏航)
- **stiffness**: 40.179 Nm/rad
- **damping**: 2.558 Nm·s/rad
- **effort_limit**: 88.0 Nm
- **动作缩放**: 0.547546

#### 7520_22电机 (髋部横滚、膝部)
- **stiffness**: 99.098 Nm/rad
- **damping**: 6.309 Nm·s/rad
- **effort_limit**: 139.0 Nm
- **动作缩放**: 0.350661

#### 4010电机 (手腕俯仰、偏航)
- **stiffness**: 16.778 Nm/rad
- **damping**: 1.068 Nm·s/rad
- **effort_limit**: 5.0 Nm
- **动作缩放**: 0.074501

#### 踝部执行器 (4杆机构，双5020电机)
- **stiffness**: 28.501 Nm/rad (14.251 × 2)
- **damping**: 1.814 Nm·s/rad (0.907 × 2)
- **effort_limit**: 50.0 Nm (25.0 × 2)
- **动作缩放**: 0.438577

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

### 计算公式
- **自然频率**: 10Hz → NATURAL_FREQ = 10 × 2π = 62.832 rad/s
- **阻尼比**: DAMPING_RATIO = 2.0
- **刚度**: STIFFNESS = ARMATURE × NATURAL_FREQ²
- **阻尼**: DAMPING = 2.0 × DAMPING_RATIO × ARMATURE × NATURAL_FREQ
- **动作缩放**: scale = 0.25 × effort_limit / stiffness

### 碰撞配置
- **脚部接触**: condim=3, friction=0.6
- **其他碰撞**: condim=1
- **自碰撞**: 启用

### 观测噪声参数
- **位置相关**: ±0.25 (锚点位置), ±0.01 (关节位置)
- **方向相关**: ±0.05 (锚点方向)
- **速度相关**: ±0.5 (线速度、关节速度), ±0.2 (角速度)

## 关键文件

- `src/tasks/tracking/tracking_env_cfg.py`: 观测和动作配置
- `src/tasks/tracking/mdp/observations.py`: 观测函数实现
- `src/assets/robots/unitree_g1/g1_constants.py`: 机器人常量和动作缩放
