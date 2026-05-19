# Skill: 从 RL 训练项目中提取 RoboJuDo 部署所需配置

从外部机器人 RL 训练项目中提取策略部署所需的全部配置信息，生成标准化文档供 `add-new-policy` skill 消费。

## 触发条件

用户要求从某个 RL 训练项目中提取/分析/总结策略配置信息，用于 RoboJuDo 部署。

## 第一步：询问用户

在做任何事之前，**必须先向用户确认**：

```
请提供以下信息：

1. **源项目路径**：RL 训练项目的本地路径或 GitHub URL
   例如：/home/hero/Projects/Robotics/RL/KungFuAthleteBot
   或：https://github.com/xxx/yyy

2. **目标机器人平台**：g1 / h1（默认 g1）

3. **策略名称**（如果已知）：例如 KungFuAthlete
```

获得路径后再开始分析。**不要猜测路径，不要跳过询问。**

---

## 分析流程

### Phase 1：项目结构侦察

拿到 `SOURCE_PATH` 后，按优先级依次搜索以下文件：

**最高优先级 — 部署/推理脚本（已实现 sim2sim 的核心参考）：**
```
{SOURCE_PATH}/**/play.py              # 通常包含完整的推理流程和 obs 构建
{SOURCE_PATH}/**/play_*.py            # play 变体
{SOURCE_PATH}/**/deploy*.py           # 部署脚本
{SOURCE_PATH}/**/inference*.py        # 推理脚本
{SOURCE_PATH}/**/sim2sim*.py          # sim2sim 迁移脚本
{SOURCE_PATH}/**/eval*.py             # 评估脚本
{SOURCE_PATH}/**/export*.py           # 模型导出脚本
```

> **重点提示：`play.py` 类脚本通常已经实现了 sim2sim 的完整流程，包含 observation 构建顺序、action 后处理、模型加载方式等关键信息，是最重要的参考对象。**

**高优先级 — 环境和配置：**
```
{SOURCE_PATH}/**/env_cfg*.py          # 环境配置（obs/action 定义）
{SOURCE_PATH}/**/*_env*.py            # 环境实现
{SOURCE_PATH}/**/agent_cfg*.py        # Agent 配置
{SOURCE_PATH}/**/deploy.yaml          # 部署配置
{SOURCE_PATH}/**/config*.yaml         # 训练配置
```

**中优先级 — 机器人定义：**
```
{SOURCE_PATH}/**/*robot*.py           # 机器人定义
{SOURCE_PATH}/**/*_const*.py          # 机器人常量（关节名、参数）
{SOURCE_PATH}/**/*actuator*.py        # 执行器配置
{SOURCE_PATH}/**/*joint*.py           # 关节定义
```

**辅助 — 模型文件：**
```
{SOURCE_PATH}/**/*.onnx               # ONNX 模型
{SOURCE_PATH}/**/*.pt                 # PyTorch 模型
{SOURCE_PATH}/**/*.jit                # TorchScript 模型
```

### Phase 2：提取关键信息

从找到的文件中提取以下 7 类信息。每类都必须有明确来源（文件路径 + 行号）。

#### 2.1 基础信息

| 项目 | 提取来源 | 说明 |
|---|---|---|
| 项目名称 | README / pyproject.toml / setup.py | 源项目正式名称 |
| 机器人型号 | 环境配置 / 机器人常量 | G1 / H1 等 |
| 关节数量 | 机器人常量 / DoF 配置 | 总自由度数 |
| 控制频率 | 环境配置 / deploy.yaml | Hz，通常 50 或 100 |
| 仿真步长 | 环境配置 | dt，通常 0.005 或 0.02 |
| decimation | 环境配置 | 控制步与仿真步之比 |

#### 2.2 关节配置

提取完整的关节列表，包含：

```python
# 关节名称列表（必须按源项目的实际顺序）
joint_names: list[str] = [...]

# 默认关节角度（HOME / INIT 姿态）
default_pos: list[float] = [...]

# PD 控制参数
stiffness: list[float] = [...]   # 精度：3 位小数
damping: list[float] = [...]     # 精度：3 位小数

# 力矩限制（如有）
torque_limits: list[float] = [...]

# 动作缩放（精度：6 位小数）
action_scale: list[float] = [...]
```

**常见 action_scale 计算公式：**
- `scale = 0.25 × effort_limit / stiffness`（IsaacLab 系列）
- `scale = constant`（直接标量）
- `scale = per_joint_list`（每关节独立值）

**提取位置提示：**
- IsaacLab 项目：看 `actuator` 配置中的 `stiffness`、`damping`、`effort_limit`
- Legged Gym 项目：看 `LeggedRobotCfg` 中的 `control` 字段
- deploy.yaml：直接提供部署参数
- play.py：可能在初始化阶段设置这些参数

#### 2.3 Observation 空间（Actor）

**这是最关键的部分。** 必须精确到：
- 每个 obs 项的名称
- 维度
- 拼接顺序（必须与训练完全一致）
- 缩放系数（obs_scales）
- 噪声范围（如有）

输出格式：

```markdown
| # | 观测项 | 维度 | 缩放系数 | 噪声范围 | 说明 |
|---|--------|------|----------|----------|------|
| 1 | base_ang_vel | 3 | 0.25 | ±0.2 | 基座角速度 (body frame) |
| 2 | projected_gravity | 3 | 1.0 | ±0.05 | 重力投影 |
| 3 | commands | 3 | 1.0 | 无 | 速度指令 [vx, vy, yaw_rate] |
| 4 | dof_pos - default_pos | N | 1.0 | ±0.01 | 相对关节角度 |
| 5 | dof_vel | N | 0.05 | ±1.5 | 关节角速度 |
| 6 | last_action | N | 1.0 | 无 | 上一步动作 |
| **Total** | | **X** | | | |
```

**提取位置提示：**
- `play.py` 中的 obs 构建代码（最可靠）
- `env_cfg.py` 中的 `observations.policy.xxx` 或 `ObservationsCfg`
- 环境实现中的 `_get_observations()` 或 `compute_observations()` 方法
- 注意：某些项目的 obs 包含历史帧，需要标注 `history_length`

#### 2.4 Action 空间

| 项目 | 说明 |
|---|---|
| 维度 | 通常等于受控关节数 |
| 物理含义 | 目标关节位置 / 关节力矩 / 位置增量 |
| 后处理 | clip → scale → offset（按实际顺序记录） |
| action_beta | 动作平滑因子（EMA） |

**Action 后处理流程必须精确记录：**
```python
# 典型流程（记录源项目的实际流程）
action = model(obs)                          # 原始输出
action = clip(action, -clip_val, clip_val)   # 裁剪
action = action * action_scale               # 缩放
target_pos = action + default_pos            # 加偏移（如果有）
```

#### 2.5 四元数格式

确认源项目使用的四元数格式：
- `[x, y, z, w]`（scipy / IsaacLab 默认）
- `[w, x, y, z]`（PyBullet / 部分项目）

**RoboJuDo 使用 `[x, y, z, w]`。如果不一致需要记录转换。**

#### 2.6 模型文件信息

| 项目 | 说明 |
|---|---|
| 模型格式 | `.onnx` / `.pt` / `.jit` |
| 模型路径 | 相对源项目根目录 |
| 文件大小 | 字节或 MB |
| 输入名称 | ONNX: `session.get_inputs()` |
| 输出名称 | ONNX: `session.get_outputs()`，注意多输出时哪个是 action |
| 加载方式 | JIT / ONNX Runtime / checkpoint |

#### 2.7 特殊配置（如有）

- 历史观测（history_length、history_obs_size）
- 运动参考数据（motion tracking / reference motion）
- 速度指令映射（commands_map、max_cmd）
- 柔顺控制（compliance）
- 多模态输入（视觉、力传感器等）

---

### Phase 3：生成输出文档

将提取的信息整理为标准化 Markdown 文档，保存到 RoboJuDo 项目中：

**输出路径**：`docs/SummaryNewPolicy/{POLICY_NAME}_policy_config.md`

**文档结构：**

```markdown
# {POLICY_NAME} - RoboJuDo 部署配置

> 源项目：{SOURCE_PROJECT}
> 提取时间：{DATE}
> 目标平台：Unitree {ROBOT}

## 1. 基础信息
[基础配置表格]

## 2. 关节配置
[关节名称、default_pos、stiffness、damping、action_scale — 表格 + Python 列表格式]

## 3. Observation 空间
[详细观测项表格，包含拼接顺序、维度、缩放、噪声]

## 4. Action 空间
[维度、含义、后处理流程]

## 5. 模型文件
[格式、路径、加载方式]

## 6. 关键源文件
[列出所有参考文件的路径]

## 7. RoboJuDo 集成注意事项
[四元数转换、关节顺序映射、特殊处理等]
```

### Phase 4：验证清单

生成文档后，逐项自检：

- [ ] 关节数量与源项目代码一致
- [ ] observation 维度总和与模型输入维度一致
- [ ] action 维度与模型输出维度一致
- [ ] 关节顺序与源项目完全一致（不是字母排序）
- [ ] 所有数值列表长度等于关节数
- [ ] stiffness/damping/action_scale 精度满足要求
- [ ] 四元数格式已标注
- [ ] action 后处理流程已完整记录
- [ ] 模型文件存在且可访问

---

## 与 add-new-policy 的协作

本 skill 的输出文档是 `add-new-policy` skill 的输入。典型工作流：

```
1. /extract-policy-config   → 生成 docs/SummaryNewPolicy/XXX_policy_config.md
2. /add-new-policy           → 读取上述文档 + 源项目代码，生成 RoboJuDo 策略代码
```

用户也可以一步完成：
```
帮我把 /home/hero/Projects/RL/MyProject 的策略集成到 RoboJuDo
```
此时 agent 应先加载 `extract-policy-config` 提取信息，再加载 `add-new-policy` 生成代码。
