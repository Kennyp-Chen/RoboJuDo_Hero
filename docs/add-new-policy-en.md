# Skill: Add New Policy to RoboJuDo

Standardized workflow for integrating a new humanoid robot RL policy (Actor NN) into the RoboJuDo framework.

## Trigger

User requests to add / integrate / deploy a new reinforcement learning policy into RoboJuDo.

## Required Information

Confirm the following before starting (ask if not provided):

| Parameter | Description | Example |
|---|---|---|
| `POLICY_NAME` | Policy name (PascalCase) | `MyAwesome` |
| `SOURCE_PROJECT` | Source project (GitHub URL or local path) | `https://github.com/xxx/yyy` |
| `MODEL_FORMAT` | Model format: `onnx` or `pt` (PyTorch JIT) | `onnx` |
| `ROBOT` | Robot platform | `g1` (primary platform) |
| `DOF_COUNT` | Degrees of freedom | `23` or `29` |
| `MODEL_DIR` | Model subdirectory name | `my_awesome` |
| `MODEL_FILENAME` | Model filename (without extension) | `policy` |

## Naming Conventions (Mandatory)

All names are derived from `POLICY_NAME` (e.g. `MyAwesome`):

```
Policy class:          MyAwesomePolicy
Base config class:     MyAwesomePolicyCfg
G1 config class:       G1MyAwesomePolicyCfg
DoF config class:      G1MyAwesomeDoF
Policy file:           robojudo/policy/my_awesome_policy.py
G1 policy config file: robojudo/config/g1/policy/g1_my_awesome_policy_cfg.py
Pipeline config name:  g1_my_awesome
snake_case name:       my_awesome
```

## Workflow (6 Steps)

### Prerequisite: Read Reference Files

Read these files before making any changes to understand existing patterns:

```
robojudo/policy/base_policy.py          # Policy base class, abstract methods
robojudo/policy/policy_cfgs.py          # PolicyCfg base class + all existing configs
robojudo/policy/__init__.py             # policy_registry registration pattern
robojudo/config/config_class.py         # Config base class (pydantic BaseModel)
robojudo/tools/tool_cfgs.py             # DoFConfig definition
robojudo/config/g1/g1_custom_cfg.py     # Pipeline registration pattern
```

If a source project is provided, also read:
- Training config (observation composition, action processing)
- Deployment script (inference flow, obs/action dimensions)
- Model export script (input/output format)

---

### Step 1: Add Base Policy Config Class to `robojudo/policy/policy_cfgs.py`

Append at end of file. Inherits `PolicyCfg`, defines policy-level config (no robot-specific DoF).

**Template:**

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
        policy_file = ASSETS_DIR / f"models/{self.robot}/{MODEL_DIR}/{self.policy_name}.{MODEL_FORMAT}"
        return policy_file.as_posix()

    # ======= ACTION CONFIGURATION =======
    action_scale: float = 1.0          # Extract from source project training config
    action_clip: float | None = None   # Extract from source project training config
    action_beta: float = 1.0           # Action smoothing factor, 1.0 = no smoothing
    freq: int = 50                     # Control frequency (Hz), extract from source project

    # ======= POLICY SPECIFIC CONFIGURATION =======
    # Add policy-specific parameters as needed, e.g.:
    # obs_scales: ObsScalesCfg = ObsScalesCfg()
    # history_length: int = 0
    # commands_map: list[list[float]] = [...]
    # max_cmd: list[float] = [...]
```

**Key imports** (already at top of file):
- `ASSETS_DIR` from `robojudo.config`
- `Config` from `robojudo.config`
- `DoFConfig` from `robojudo.tools.tool_cfgs`
- Validators from `pydantic`: `field_validator`, `model_validator`

**Notes:**
- If `ObsScalesCfg` is needed, define as inner class inheriting `Config`
- `action_scale` can be `float` or `list[float]` (per-joint scaling)
- For non-standard model loading (e.g. multi-file), set `disable_autoload: bool = True`
- For historical observations, set `history_length` and optionally override `history_obs_size` property

**Existing references:**
- ONNX inference: `BFMZeroPolicyCfg`, `UnitreeMjlabVelocityPolicyCfg`
- PyTorch inference: `UnitreePolicyCfg`, `SmoothPolicyCfg`
- Motion imitation: `BeyondMimicPolicyCfg`, `AsapPolicyCfg` (typically `disable_autoload=True`)
- Complex observation: `GentlePolicyCfg` (with motion tracking, compliance)

---

### Step 2: Create G1 Robot DoF Config + Policy Config

**File**: `robojudo/config/g1/policy/g1_{snake_case}_policy_cfg.py`

**Template:**

```python
from robojudo.policy.policy_cfgs import {POLICY_NAME}PolicyCfg
from robojudo.tools.tool_cfgs import DoFConfig


class G1{POLICY_NAME}DoF(DoFConfig):
    """G1 robot joint configuration for {POLICY_NAME} policy."""
    joint_names: list[str] = [
        # === Fill in according to source project joint order ===
        # Below is G1 standard 29DoF joint order (remove marked 6 joints for 23DoF)
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
        'waist_roll_joint',       # Remove for 23DoF
        'waist_pitch_joint',      # Remove for 23DoF
        'left_shoulder_pitch_joint',
        'left_shoulder_roll_joint',
        'left_shoulder_yaw_joint',
        'left_elbow_joint',
        'left_wrist_roll_joint',
        'left_wrist_pitch_joint',  # Remove for 23DoF
        'left_wrist_yaw_joint',    # Remove for 23DoF
        'right_shoulder_pitch_joint',
        'right_shoulder_roll_joint',
        'right_shoulder_yaw_joint',
        'right_elbow_joint',
        'right_wrist_roll_joint',
        'right_wrist_pitch_joint', # Remove for 23DoF
        'right_wrist_yaw_joint',   # Remove for 23DoF
    ]
    default_pos: list[float] | None = [
        # Extract default joint angles from source project training config
        # Length must match joint_names
    ]
    stiffness: list[float] | None = None   # PD control stiffness, extract from source project
    damping: list[float] | None = None     # PD control damping, extract from source project


class G1{POLICY_NAME}PolicyCfg({POLICY_NAME}PolicyCfg):
    """G1-specific configuration for {POLICY_NAME} policy."""
    robot: str = "g1"
    obs_dof: DoFConfig = G1{POLICY_NAME}DoF()
    action_dof: DoFConfig = G1{POLICY_NAME}DoF()  # Define separately if action DoF differs from obs DoF

    # Override base class defaults as needed
    # action_scale: float = 0.25
    # max_cmd: list[float] = [1.0, 0.5, 1.5]
    # commands_map: list[list[float]] = [...]
```

**Joint order notes:**
- Source project joint order may differ from G1 standard order — must be aligned
- For 29DoF to 23DoF conversion, use `from robojudo.tools.tool_cfgs import convert_29dof_to_23dof`
- Joint names must exactly match MuJoCo model joint names
- `default_pos`, `stiffness`, `damping` lengths must match `joint_names` (DoFConfig's model_validator enforces this)

---

### Step 3: Create Policy Inference Implementation

**File**: `robojudo/policy/{snake_case}_policy.py`

**Template (ONNX inference):**

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
        # If using history observations, initialize history buffer here
        # self._init_history(np.zeros(self.cfg_policy.history_obs_size))

    def get_observation(self, env_data, ctrl_data) -> tuple[np.ndarray, dict]:
        """Compute observation vector.

        Must strictly match source project training config — order and scaling must be identical.
        """
        # === Sensor data from env_data ===
        # env_data.base_quat       - Base quaternion [x, y, z, w] (scipy convention)
        # env_data.base_ang_vel    - Base angular velocity [wx, wy, wz] (body frame)
        # env_data.base_pos        - Base position [x, y, z] (world frame)
        # env_data.dof_pos         - Joint positions (num_dofs,)
        # env_data.dof_vel         - Joint velocities (num_dofs,)

        # === Projected gravity (commonly used) ===
        gravity_orientation = get_gravity_orientation(env_data.base_quat)

        # === Build observation ===
        obs = np.concatenate([
            # Concatenate in exact order matching source project observation composition
            # Example:
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
            self.input_names[0]: obs.astype(np.float32)[None, :]  # Add batch dimension
        }
        ort_outputs = self.session.run(self.output_names, ort_inputs)
        action = ort_outputs[0].squeeze(0).astype(np.float32)

        # Action smoothing
        action = (1 - self.action_beta) * self.last_action + self.action_beta * action
        self.last_action = action.copy()

        # Action clipping
        if self.action_clip is not None:
            action = np.clip(action, -self.action_clip, self.action_clip)

        # Action scaling
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

**Template (PyTorch JIT inference):**

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
        # base_policy.__init__ auto-loads torch.jit model into self.model
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
            # Concatenate in exact order matching source project observation composition
        ])

        extras = {"timestep": self.timestep}
        return obs, extras

    # get_action uses base class default (torch.jit inference) unless custom post-processing needed

    def post_step_callback(self, commands: list[str] | None = None):
        """Handle post-step commands."""
        self.timestep += 1
```

**Key implementation notes:**

1. **`@policy_registry.register` decorator is mandatory** — without it the policy cannot be found by policy_type
2. **Observation order must exactly match training** — this is the most common source of errors
3. **`env_data.base_quat` is `[x, y, z, w]` format** (scipy default) — some source projects use `[w, x, y, z]`, conversion required
4. **`get_gravity_orientation()` is a framework utility** at `robojudo.utils.util_func`
5. **Base class `get_action()` implements standard torch.jit inference + action smoothing + clip + scale** — no need to override if logic is identical
6. ONNX inference type must override `get_action()` since base class defaults to torch.jit

---

### Step 4: Register Policy Class in `robojudo/policy/__init__.py`

Append one line to the registration list at the end of the file:

```python
policy_registry.add("{POLICY_NAME}Policy", ".{snake_case}_policy")
```

**Format:**
- First argument: policy class name (must match `policy_type` field in `policy_cfgs.py`)
- Second argument: relative module path (relative to `robojudo.policy` package, prefixed with `.`)

---

### Step 5: Register Pipeline Config in `robojudo/config/g1/g1_custom_cfg.py`

**5.1 Add import** (in the import section at top of file):

```python
from .policy.g1_{snake_case}_policy_cfg import G1{POLICY_NAME}PolicyCfg
```

**5.2 Add pipeline config class** (in the config section):

```python
@cfg_registry.register
class g1_{snake_case}(RlPipelineCfg):
    """
    G1 robot with {POLICY_NAME} policy.
    Source: {SOURCE_PROJECT}
    """
    robot: str = "g1"
    env: G1_23MujocoEnvCfg = G1_23MujocoEnvCfg()  # Use G1_23MujocoEnvCfg for 23DoF, G1MujocoEnvCfg for 29DoF

    ctrl: list[KeyboardCtrlCfg] = [
        KeyboardCtrlCfg(
            triggers_extra={
                # Add policy-specific keyboard shortcuts (optional)
            }
        )
    ]

    policy: G1{POLICY_NAME}PolicyCfg = G1{POLICY_NAME}PolicyCfg()
```

**Available environment configs:**
- `G1MujocoEnvCfg` — 29DoF MuJoCo simulation
- `G1_23MujocoEnvCfg` — 23DoF MuJoCo simulation
- `G1_12MujocoEnvCfg` — 12DoF MuJoCo simulation
- `G1RealEnvCfg` — Real robot environment

**Available controller configs:**
- `KeyboardCtrlCfg` — Keyboard control (standard)
- `JoystickCtrlCfg` — Gamepad control
- `BFMKeyboardCtrlCfg` — BFM-specific keyboard control
- `G1BeyondmimicCtrlCfg` — BeyondMimic motion source control

**To add to the locomimic multi-policy system** (optional):

Add to the `mimic_policies` list in `g1_locomimic_sim` class, updating the type annotation:

```python
mimic_policies: list[... | G1{POLICY_NAME}PolicyCfg] = [
    # Existing policies...
    G1{POLICY_NAME}PolicyCfg(
        # Override parameters
    ),
]
```

---

### Step 6: Place Model Files + Verify

**6.1 Place model files:**

```
assets/models/g1/{MODEL_DIR}/
├── {MODEL_FILENAME}.onnx  # or .pt
├── config.yaml            # Optional: training config
└── ...                    # Other required files
```

**6.2 Verification checklist:**

```bash
# 1. Lint check
ruff check robojudo/policy/{snake_case}_policy.py
ruff check robojudo/policy/policy_cfgs.py
ruff check robojudo/config/g1/policy/g1_{snake_case}_policy_cfg.py
ruff check robojudo/config/g1/g1_custom_cfg.py

# 2. Format check
ruff format --check robojudo/policy/{snake_case}_policy.py
ruff format --check robojudo/config/g1/policy/g1_{snake_case}_policy_cfg.py

# 3. Import test
python -c "import robojudo; print('Import OK')"

# 4. Config registration test
python -c "from robojudo.config import cfg_registry; print('g1_{snake_case}' in cfg_registry.types)"

# 5. Policy registration test
python -c "from robojudo.policy import policy_registry; print('{POLICY_NAME}Policy' in policy_registry.types)"

# 6. Simulation run test
python scripts/run_pipeline_sim.py -c g1_{snake_case}
```

---

## Architecture Quick Reference

### Class Hierarchy

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

### Registration Mechanisms

```
cfg_registry    (robojudo/config/__init__.py)  ← Pipeline configs, via @cfg_registry.register decorator
policy_registry (robojudo/policy/__init__.py)  ← Policy classes, via policy_registry.add() lazy registration
```

### Files to Modify (Checklist)

| # | File | Action |
|---|---|---|
| 1 | `robojudo/policy/policy_cfgs.py` | Append `{POLICY_NAME}PolicyCfg` class |
| 2 | `robojudo/config/g1/policy/g1_{snake_case}_policy_cfg.py` | **Create**: DoF + G1 config |
| 3 | `robojudo/policy/{snake_case}_policy.py` | **Create**: Policy implementation |
| 4 | `robojudo/policy/__init__.py` | Append `policy_registry.add(...)` |
| 5 | `robojudo/config/g1/g1_custom_cfg.py` | Add import + `@cfg_registry.register` |
| 6 | `assets/models/g1/{MODEL_DIR}/` | Place model files |

### env_data Available Attributes

```python
env_data.base_pos       # np.ndarray (3,)  - Base world position [x, y, z]
env_data.base_quat      # np.ndarray (4,)  - Base quaternion [x, y, z, w] (scipy convention)
env_data.base_ang_vel   # np.ndarray (3,)  - Base angular velocity, body frame [wx, wy, wz]
env_data.dof_pos        # np.ndarray (N,)  - Joint positions
env_data.dof_vel        # np.ndarray (N,)  - Joint velocities
```

### Common Utility Functions

```python
from robojudo.utils.util_func import get_gravity_orientation  # base_quat -> projected gravity
from robojudo.utils.util_func import command_remap            # Joystick value remapping
from robojudo.tools.tool_cfgs import convert_29dof_to_23dof   # 29DoF -> 23DoF conversion
```

## Common Pitfalls

1. **Wrong observation order** — Most common issue. Must exactly match training, including scaling coefficients
2. **Wrong quaternion format** — `env_data.base_quat` is `[x,y,z,w]`, some projects use `[w,x,y,z]`
3. **Wrong joint order** — Source project joint order may differ from G1 standard order
4. **Forgot to register** — Both `policy_registry.add()` and `@cfg_registry.register` are required
5. **Wrong ONNX output index** — Some models have multiple outputs, confirm which one is the action (print output_names to check)
6. **action_scale dimension mismatch** — If using `list[float]`, length must equal action DoF count
