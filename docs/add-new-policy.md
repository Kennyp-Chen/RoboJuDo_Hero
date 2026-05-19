# Skill: Add New Policy to RoboJuDo

为 RoboJuDo 框架添加新的人形机器人 RL 策略（Actor NN）的标准化流程。

## 触发条件

用户要求添加/接入/集成新的机器人强化学习策略（Policy）到 RoboJuDo 框架。

## 需要向用户确认的信息

在开始前，必须确认以下信息（如果用户未提供则询问）：

| 参数 | 说明 | 示例 |
|---|---|---|
| `POLICY_NAME` | 策略名称（PascalCase） | `MyAwesome` |
| `SOURCE_PROJECT` | 源项目（GitHub URL 或本地路径） | `https://github.com/xxx/yyy` |
| `MODEL_FORMAT` | 模型格式：`onnx` 或 `pt` (PyTorch JIT) | `onnx` |
| `ROBOT` | 机器人平台 | `g1`（目前主要支持 g1） |
| `DOF_COUNT` | 自由度数量 | `23` 或 `29` |
| `MODEL_DIR` | 模型子目录名 | `my_awesome` |
| `MODEL_FILENAME` | 模型文件名（无后缀） | `policy` |

## 命名约定（强制）

根据 `POLICY_NAME`（例如 `MyAwesome`）自动推导：

```
策略类名:         MyAwesomePolicy
基础配置类名:     MyAwesomePolicyCfg
G1配置类名:       G1MyAwesomePolicyCfg
DoF配置类名:      G1MyAwesomeDoF
策略文件名:       robojudo/policy/my_awesome_policy.py
G1策略配置文件名: robojudo/config/g1/policy/g1_my_awesome_policy_cfg.py
pipeline配置名:   g1_my_awesome
snake_case名:     my_awesome
```

## 执行流程（6步）

### 前置：阅读参考文件

在动手前必须阅读以下文件以理解现有模式：

```
robojudo/policy/base_policy.py          # Policy 基类，了解抽象方法
robojudo/policy/policy_cfgs.py          # PolicyCfg 基类 + 所有现有配置
robojudo/policy/__init__.py             # policy_registry 注册方式
robojudo/config/config_class.py         # Config 基类（pydantic BaseModel）
robojudo/tools/tool_cfgs.py             # DoFConfig 定义
robojudo/config/g1/g1_custom_cfg.py     # pipeline 注册方式
```

如果用户提供了源项目，还需阅读源项目的：
- 训练配置（observation 构成、action 处理方式）
- 部署脚本（推理流程、obs/action 维度）
- 模型导出脚本（输入输出格式）

---

### Step 1: 在 `robojudo/policy/policy_cfgs.py` 添加基础策略配置类

在文件末尾添加。继承 `PolicyCfg`，定义策略级别的配置（不含机器人特定的 DoF）。

**模板：**

```python
class {POLICY_NAME}PolicyCfg(PolicyCfg):
    """
    {POLICY_NAME} Policy Configuration
    Source: {SOURCE_PROJECT}
    """
    policy_type: str = "{POLICY_NAME}Policy"
    policy_name: str = "{MODEL_FILENAME}"

    @property
    def policy_file(self) -> str:
        policy_file = ASSETS_DIR / f"models/{{self.robot}}/{MODEL_DIR}/{{self.policy_name}}.{MODEL_FORMAT}"
        return policy_file.as_posix()

    # ======= ACTION CONFIGURATION =======
    action_scale: float = 1.0          # 从源项目的训练配置中提取
    action_clip: float | None = None   # 从源项目的训练配置中提取
    action_beta: float = 1.0           # 动作平滑因子，1.0=不平滑
    freq: int = 50                     # 控制频率（Hz），从源项目提取

    # ======= POLICY SPECIFIC CONFIGURATION =======
    # 根据源项目需要添加特有参数，例如：
    # obs_scales: ObsScalesCfg = ObsScalesCfg()
    # history_length: int = 0
    # commands_map: list[list[float]] = [...]
    # max_cmd: list[float] = [...]
```

**关键引用**（已在文件顶部导入）：
- `ASSETS_DIR` 从 `robojudo.config` 导入
- `Config` 从 `robojudo.config` 导入
- `DoFConfig` 从 `robojudo.tools.tool_cfgs` 导入
- 验证器从 `pydantic` 导入：`field_validator`, `model_validator`

**注意事项：**
- 如果需要 `ObsScalesCfg`，定义为内部类继承 `Config`
- `action_scale` 可以是 `float` 或 `list[float]`（每个关节独立缩放）
- 如果策略使用非标准模型加载（如多文件），设置 `disable_autoload: bool = True`
- 如果需要历史观测，设置 `history_length` 并可选覆盖 `history_obs_size` 属性

**现有参考：**
- ONNX 推理型：`BFMZeroPolicyCfg`, `UnitreeMjlabVelocityPolicyCfg`
- PyTorch 推理型：`UnitreePolicyCfg`, `SmoothPolicyCfg`
- 动作模仿型：`BeyondMimicPolicyCfg`, `AsapPolicyCfg`（通常 `disable_autoload=True`）
- 复杂观测型：`GentlePolicyCfg`（带 motion tracking、compliance）

---

### Step 2: 创建 G1 机器人 DoF 配置 + 策略配置

**文件**: `robojudo/config/g1/policy/g1_{snake_case}_policy_cfg.py`

**模板：**

```python
from robojudo.policy.policy_cfgs import {POLICY_NAME}PolicyCfg
from robojudo.tools.tool_cfgs import DoFConfig


class G1{POLICY_NAME}DoF(DoFConfig):
    """G1 robot joint configuration for {POLICY_NAME} policy."""
    joint_names: list[str] = [
        # === 根据源项目的关节顺序填写 ===
        # 以下为 G1 标准 29DoF 关节顺序（如果是 23DoF 去掉标注的 6 个）
        'left_hip_pitch_joint',
        'left_hip_roll_joint',
        'left_hip_yaw_joint',
        'left_knee_joint',
        'left_ankle_pitch_joint',
        'left_ankle_roll_joint',
        'right_hip_pitch_joint',
        'right_hip_roll_joint',
        'right_hip_yaw_joint',
        'right_knee_joint',
        'right_ankle_pitch_joint',
        'right_ankle_roll_joint',
        'waist_yaw_joint',
        'waist_roll_joint',       # 23DoF 时移除
        'waist_pitch_joint',      # 23DoF 时移除
        'left_shoulder_pitch_joint',
        'left_shoulder_roll_joint',
        'left_shoulder_yaw_joint',
        'left_elbow_joint',
        'left_wrist_roll_joint',
        'left_wrist_pitch_joint',  # 23DoF 时移除
        'left_wrist_yaw_joint',    # 23DoF 时移除
        'right_shoulder_pitch_joint',
        'right_shoulder_roll_joint',
        'right_shoulder_yaw_joint',
        'right_elbow_joint',
        'right_wrist_roll_joint',
        'right_wrist_pitch_joint', # 23DoF 时移除
        'right_wrist_yaw_joint',   # 23DoF 时移除
    ]
    default_pos: list[float] | None = [
        # 从源项目训练配置中提取默认关节角度
        # 长度必须与 joint_names 一致
    ]
    stiffness: list[float] | None = None   # PD 控制刚度，从源项目提取
    damping: list[float] | None = None     # PD 控制阻尼，从源项目提取


class G1{POLICY_NAME}PolicyCfg({POLICY_NAME}PolicyCfg):
    """G1-specific configuration for {POLICY_NAME} policy."""
    robot: str = "g1"
    obs_dof: DoFConfig = G1{POLICY_NAME}DoF()
    action_dof: DoFConfig = G1{POLICY_NAME}DoF()  # 如果 action DoF 与 obs DoF 不同则单独定义

    # 覆盖基类的默认值（如需要）
    # action_scale: float = 0.25
    # max_cmd: list[float] = [1.0, 0.5, 1.5]
    # commands_map: list[list[float]] = [...]
```

**关节顺序注意事项：**
- 源项目的关节顺序可能与 G1 标准顺序不同，必须对齐
- 如果需要 29DoF → 23DoF 转换，使用 `from robojudo.tools.tool_cfgs import convert_29dof_to_23dof`
- 关节名必须与 MuJoCo 模型中的关节名完全一致
- `default_pos`、`stiffness`、`damping` 长度必须与 `joint_names` 一致（DoFConfig 的 model_validator 会检查）

---

### Step 3: 创建策略推理实现

**文件**: `robojudo/policy/{snake_case}_policy.py`

**模板（ONNX 推理型）：**

```python
import logging

import numpy as np
import onnxruntime as ort

from robojudo.policy import Policy, policy_registry
from robojudo.policy.policy_cfgs import {POLICY_NAME}PolicyCfg
from robojudo.utils.util_func import get_gravity_orientation

logger = logging.getLogger(__name__)


@policy_registry.register
class {POLICY_NAME}Policy(Policy):
    """{POLICY_NAME} Policy implementation.
    Source: {SOURCE_PROJECT}
    """

    cfg_policy: {POLICY_NAME}PolicyCfg

    def __init__(self, cfg_policy: {POLICY_NAME}PolicyCfg, device: str = "cpu"):
        super().__init__(cfg_policy=cfg_policy, device=device)

        # Load ONNX model
        providers = ["CPUExecutionProvider"]
        if device == "cuda":
            providers.insert(0, "CUDAExecutionProvider")

        self.session = ort.InferenceSession(
            cfg_policy.policy_file, providers=providers
        )
        self.input_names = [i.name for i in self.session.get_inputs()]
        self.output_names = [o.name for o in self.session.get_outputs()]

        logger.info(f"Loaded {POLICY_NAME} ONNX model: {cfg_policy.policy_file}")

        self.reset()

    def reset(self):
        """Reset policy state."""
        self.timestep = 0
        self.last_action = np.zeros(self.num_actions, dtype=np.float32)
        # 如果使用历史观测，在此初始化历史缓冲区
        # self._init_history(np.zeros(self.cfg_policy.history_obs_size))

    def get_observation(self, env_data, ctrl_data) -> tuple[np.ndarray, dict]:
        """Compute observation vector.

        必须严格按照源项目的训练配置构建 observation，顺序和缩放必须一致。
        """
        # === 从 env_data 获取传感器数据 ===
        # env_data.base_quat       - 基座四元数 [x, y, z, w]（scipy 格式）
        # env_data.base_ang_vel    - 基座角速度 [wx, wy, wz]（body frame）
        # env_data.base_pos        - 基座位置 [x, y, z]（world frame）
        # env_data.dof_pos         - 关节角度 (num_dofs,)
        # env_data.dof_vel         - 关节角速度 (num_dofs,)

        # === 重力投影（常用） ===
        gravity_orientation = get_gravity_orientation(env_data.base_quat)

        # === 构建 observation ===
        obs = np.concatenate([
            # 按源项目的 observation 构成顺序拼接
            # 例如：
            # env_data.base_ang_vel * obs_scales.ang_vel,
            # gravity_orientation * obs_scales.gravity,
            # commands * obs_scales.command,
            # (env_data.dof_pos - self.default_dof_pos) * obs_scales.dof_pos,
            # env_data.dof_vel * obs_scales.dof_vel,
            # self.last_action,
        ])

        extras = {
            "timestep": self.timestep,
        }

        return obs, extras

    def get_action(self, obs: np.ndarray) -> np.ndarray:
        """Run ONNX inference and post-process action."""
        ort_inputs = {
            self.input_names[0]: obs.astype(np.float32)[None, :]  # 添加 batch 维度
        }
        ort_outputs = self.session.run(self.output_names, ort_inputs)
        action = ort_outputs[0].squeeze(0).astype(np.float32)

        # 动作平滑
        action = (1 - self.action_beta) * self.last_action + self.action_beta * action
        self.last_action = action.copy()

        # 动作裁剪
        if self.action_clip is not None:
            action = np.clip(action, -self.action_clip, self.action_clip)

        # 动作缩放
        action = action * np.asarray(self.action_scale)

        self.timestep += 1
        return action

    def post_step_callback(self, commands: list[str] | None = None):
        """Handle post-step commands."""
        for command in commands or []:
            match command:
                case "[RESET]":
                    self.reset()
```

**模板（PyTorch JIT 推理型）：**

```python
import logging

import numpy as np
import torch

from robojudo.policy import Policy, policy_registry
from robojudo.policy.policy_cfgs import {POLICY_NAME}PolicyCfg
from robojudo.utils.util_func import get_gravity_orientation

logger = logging.getLogger(__name__)


@policy_registry.register
class {POLICY_NAME}Policy(Policy):
    """{POLICY_NAME} Policy implementation.
    Source: {SOURCE_PROJECT}
    """

    cfg_policy: {POLICY_NAME}PolicyCfg

    def __init__(self, cfg_policy: {POLICY_NAME}PolicyCfg, device: str = "cpu"):
        # base_policy.__init__ 会自动加载 torch.jit 模型到 self.model
        super().__init__(cfg_policy=cfg_policy, device=device)
        logger.info(f"Loaded {POLICY_NAME} JIT model: {cfg_policy.policy_file}")
        self.reset()

    def reset(self):
        """Reset policy state."""
        self.timestep = 0
        self.last_action = np.zeros(self.num_actions, dtype=np.float32)

    def get_observation(self, env_data, ctrl_data) -> tuple[np.ndarray, dict]:
        """Compute observation vector."""
        gravity_orientation = get_gravity_orientation(env_data.base_quat)

        obs = np.concatenate([
            # 按源项目的 observation 构成顺序拼接
        ])

        extras = {"timestep": self.timestep}
        return obs, extras

    # get_action 使用基类默认实现（torch.jit 推理），除非需要自定义后处理

    def post_step_callback(self, commands: list[str] | None = None):
        """Handle post-step commands."""
        self.timestep += 1
```

**关键实现要点：**

1. **`@policy_registry.register` 装饰器是必须的**，否则策略无法通过 policy_type 查找
2. **observation 顺序必须与训练完全一致**，这是最常见的错误来源
3. **`env_data.base_quat` 是 `[x, y, z, w]` 格式**（scipy 默认），某些源项目使用 `[w, x, y, z]`，需要转换
4. **`get_gravity_orientation()` 是框架提供的工具函数**，位于 `robojudo.utils.util_func`
5. **基类 `get_action()` 实现了标准的 torch.jit 推理 + action smoothing + clip + scale**，如果逻辑一致则无需覆盖
6. ONNX 推理型必须覆盖 `get_action()`，因为基类默认用 torch.jit

---

### Step 4: 注册策略类到 `robojudo/policy/__init__.py`

在文件末尾的注册列表中添加一行：

```python
policy_registry.add("{POLICY_NAME}Policy", ".{snake_case}_policy")
```

**格式说明：**
- 第一个参数：策略类名（必须与 `policy_cfgs.py` 中 `policy_type` 字段一致）
- 第二个参数：模块的相对路径（相对于 `robojudo.policy` 包，以 `.` 开头）

---

### Step 5: 在 `robojudo/config/g1/g1_custom_cfg.py` 中注册 pipeline 配置

**5.1 添加 import**（在文件顶部的 import 区域）：

```python
from .policy.g1_{snake_case}_policy_cfg import G1{POLICY_NAME}PolicyCfg
```

**5.2 添加 pipeline 配置类**（在文件的配置区域）：

```python
@cfg_registry.register
class g1_{snake_case}(RlPipelineCfg):
    """
    G1 robot with {POLICY_NAME} policy.
    Source: {SOURCE_PROJECT}
    """
    robot: str = "g1"
    env: G1_23MujocoEnvCfg = G1_23MujocoEnvCfg()  # 23DoF 用 G1_23MujocoEnvCfg，29DoF 用 G1MujocoEnvCfg

    ctrl: list[KeyboardCtrlCfg] = [
        KeyboardCtrlCfg(
            triggers_extra={
                # 添加策略特有的键盘快捷键（可选）
            }
        )
    ]

    policy: G1{POLICY_NAME}PolicyCfg = G1{POLICY_NAME}PolicyCfg()
```

**可用环境配置：**
- `G1MujocoEnvCfg` — 29DoF MuJoCo 仿真
- `G1_23MujocoEnvCfg` — 23DoF MuJoCo 仿真
- `G1_12MujocoEnvCfg` — 12DoF MuJoCo 仿真
- `G1RealEnvCfg` — 真机环境

**可用控制器配置：**
- `KeyboardCtrlCfg` — 键盘控制（标准）
- `JoystickCtrlCfg` — 游戏手柄控制
- `BFMKeyboardCtrlCfg` — BFM 专用键盘控制
- `G1BeyondmimicCtrlCfg` — BeyondMimic 动作源控制

**如果需要加入 locomimic 多策略系统**（可选）：

在 `g1_locomimic_sim` 类中的 `mimic_policies` 列表添加，需同时更新类型注解：

```python
mimic_policies: list[... | G1{POLICY_NAME}PolicyCfg] = [
    # 现有策略...
    G1{POLICY_NAME}PolicyCfg(
        # 覆盖参数
    ),
]
```

---

### Step 6: 放置模型文件 + 验证

**6.1 放置模型文件：**

```
assets/models/g1/{MODEL_DIR}/
├── {MODEL_FILENAME}.onnx  # 或 .pt
├── config.yaml            # 可选：训练配置
└── ...                    # 其他需要的文件
```

**6.2 验证清单：**

```bash
# 1. Lint 检查
ruff check robojudo/policy/{snake_case}_policy.py
ruff check robojudo/policy/policy_cfgs.py
ruff check robojudo/config/g1/policy/g1_{snake_case}_policy_cfg.py
ruff check robojudo/config/g1/g1_custom_cfg.py

# 2. 格式检查
ruff format --check robojudo/policy/{snake_case}_policy.py
ruff format --check robojudo/config/g1/policy/g1_{snake_case}_policy_cfg.py

# 3. 导入测试
python -c "import robojudo; print('Import OK')"

# 4. 配置注册测试
python -c "from robojudo.config import cfg_registry; print('g1_{snake_case}' in cfg_registry.types)"

# 5. 策略注册测试
python -c "from robojudo.policy import policy_registry; print('{POLICY_NAME}Policy' in policy_registry.types)"

# 6. 仿真运行测试
python scripts/run_pipeline_sim.py -c g1_{snake_case}
```

---

## 架构速查

### 类继承关系

```
pydantic.BaseModel
└── Config (robojudo/config/config_class.py)
    ├── PolicyCfg (robojudo/policy/policy_cfgs.py)
    │   └── {POLICY_NAME}PolicyCfg
    │       └── G1{POLICY_NAME}PolicyCfg (robojudo/config/g1/policy/...)
    ├── DoFConfig (robojudo/tools/tool_cfgs.py)
    │   └── G1{POLICY_NAME}DoF
    └── RlPipelineCfg (robojudo/pipeline/pipeline_cfgs.py)
        └── g1_{snake_case} (robojudo/config/g1/g1_custom_cfg.py)

ABC
└── Policy (robojudo/policy/base_policy.py)
    └── {POLICY_NAME}Policy (robojudo/policy/{snake_case}_policy.py)
```

### 注册机制

```
cfg_registry  (robojudo/config/__init__.py)   ← pipeline 配置，用 @cfg_registry.register 装饰器
policy_registry (robojudo/policy/__init__.py)  ← 策略类，用 policy_registry.add() 懒加载注册
```

### 必须修改的文件清单

| # | 文件 | 操作 |
|---|---|---|
| 1 | `robojudo/policy/policy_cfgs.py` | 末尾添加 `{POLICY_NAME}PolicyCfg` 类 |
| 2 | `robojudo/config/g1/policy/g1_{snake_case}_policy_cfg.py` | **新建**：DoF + G1 配置 |
| 3 | `robojudo/policy/{snake_case}_policy.py` | **新建**：策略实现 |
| 4 | `robojudo/policy/__init__.py` | 末尾添加 `policy_registry.add(...)` |
| 5 | `robojudo/config/g1/g1_custom_cfg.py` | 添加 import + `@cfg_registry.register` |
| 6 | `assets/models/g1/{MODEL_DIR}/` | 放置模型文件 |

### env_data 可用属性

```python
env_data.base_pos       # np.ndarray (3,)  - 基座世界坐标 [x, y, z]
env_data.base_quat      # np.ndarray (4,)  - 基座四元数 [x, y, z, w]（scipy 格式）
env_data.base_ang_vel   # np.ndarray (3,)  - 基座角速度 body frame [wx, wy, wz]
env_data.dof_pos        # np.ndarray (N,)  - 关节位置
env_data.dof_vel        # np.ndarray (N,)  - 关节速度
```

### 常见 util 函数

```python
from robojudo.utils.util_func import get_gravity_orientation  # base_quat → projected gravity
from robojudo.utils.util_func import command_remap            # 摇杆值重映射
from robojudo.tools.tool_cfgs import convert_29dof_to_23dof   # 29DoF → 23DoF 转换
```

## 常见错误

1. **observation 顺序不对** — 最常见问题。必须与训练时完全一致，包括缩放系数
2. **四元数格式不对** — `env_data.base_quat` 是 `[x,y,z,w]`，有些项目用 `[w,x,y,z]`
3. **关节顺序不对** — 源项目的关节顺序可能与 G1 标准顺序不同
4. **忘记注册** — `policy_registry.add()` 和 `@cfg_registry.register` 缺一不可
5. **ONNX 输出索引错误** — 某些模型有多个输出，需确认哪个是 action（打印 output_names 检查）
6. **action_scale 维度不匹配** — 如果用 `list[float]`，长度必须等于 action DoF 数量
