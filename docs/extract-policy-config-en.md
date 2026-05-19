# Skill: Extract Policy Config from RL Training Project for RoboJuDo

Extract all deployment-relevant configuration from an external robot RL training project, producing a standardized document consumed by the `add-new-policy` skill.

## Trigger

User requests to extract / analyze / summarize policy configuration from an RL training project for RoboJuDo deployment.

## First Step: Ask the User

Before doing anything, **you must ask the user**:

```
Please provide the following:

1. **Source project path**: Local path or GitHub URL of the RL training project
   e.g.: /home/hero/Projects/Robotics/RL/KungFuAthleteBot
   or: https://github.com/xxx/yyy

2. **Target robot platform**: g1 / h1 (default: g1)

3. **Policy name** (if known): e.g. KungFuAthlete
```

Start analysis only after receiving the path. **Do not guess paths. Do not skip this step.**

---

## Analysis Workflow

### Phase 1: Project Structure Reconnaissance

After receiving `SOURCE_PATH`, search for files in the following priority order:

**Highest priority — Deployment / inference scripts (the core sim2sim reference):**
```
{SOURCE_PATH}/**/play.py              # Usually contains complete inference flow and obs construction
{SOURCE_PATH}/**/play_*.py            # play variants
{SOURCE_PATH}/**/deploy*.py           # Deployment scripts
{SOURCE_PATH}/**/inference*.py        # Inference scripts
{SOURCE_PATH}/**/sim2sim*.py          # Sim2sim transfer scripts
{SOURCE_PATH}/**/eval*.py             # Evaluation scripts
{SOURCE_PATH}/**/export*.py           # Model export scripts
```

> **Key insight: `play.py` scripts typically implement the complete sim2sim pipeline, containing observation construction order, action post-processing, model loading methods, and other critical information. They are the single most important reference.**

**High priority — Environment and configuration:**
```
{SOURCE_PATH}/**/env_cfg*.py          # Environment config (obs/action definitions)
{SOURCE_PATH}/**/*_env*.py            # Environment implementation
{SOURCE_PATH}/**/agent_cfg*.py        # Agent config
{SOURCE_PATH}/**/deploy.yaml          # Deployment config
{SOURCE_PATH}/**/config*.yaml         # Training config
```

**Medium priority — Robot definitions:**
```
{SOURCE_PATH}/**/*robot*.py           # Robot definitions
{SOURCE_PATH}/**/*_const*.py          # Robot constants (joint names, parameters)
{SOURCE_PATH}/**/*actuator*.py        # Actuator config
{SOURCE_PATH}/**/*joint*.py           # Joint definitions
```

**Auxiliary — Model files:**
```
{SOURCE_PATH}/**/*.onnx               # ONNX models
{SOURCE_PATH}/**/*.pt                 # PyTorch models
{SOURCE_PATH}/**/*.jit                # TorchScript models
```

### Phase 2: Extract Key Information

Extract the following 7 categories from discovered files. Each item must have a clear source (file path + line number).

#### 2.1 Basic Information

| Item | Extraction Source | Description |
|---|---|---|
| Project name | README / pyproject.toml / setup.py | Official project name |
| Robot model | Environment config / robot constants | G1 / H1 etc. |
| Joint count | Robot constants / DoF config | Total degrees of freedom |
| Control frequency | Environment config / deploy.yaml | Hz, typically 50 or 100 |
| Simulation timestep | Environment config | dt, typically 0.005 or 0.02 |
| Decimation | Environment config | Ratio of control steps to simulation steps |

#### 2.2 Joint Configuration

Extract the complete joint list including:

```python
# Joint name list (must follow source project's actual order)
joint_names: list[str] = [...]

# Default joint angles (HOME / INIT pose)
default_pos: list[float] = [...]

# PD control parameters
stiffness: list[float] = [...]   # Precision: 3 decimal places
damping: list[float] = [...]     # Precision: 3 decimal places

# Torque limits (if available)
torque_limits: list[float] = [...]

# Action scaling (precision: 6 decimal places)
action_scale: list[float] = [...]
```

**Common action_scale formulas:**
- `scale = 0.25 * effort_limit / stiffness` (IsaacLab family)
- `scale = constant` (scalar constant)
- `scale = per_joint_list` (independent per-joint values)

**Where to look:**
- IsaacLab projects: `actuator` config for `stiffness`, `damping`, `effort_limit`
- Legged Gym projects: `LeggedRobotCfg` → `control` field
- deploy.yaml: direct deployment parameters
- play.py: may set these parameters during initialization

#### 2.3 Observation Space (Actor)

**This is the most critical section.** Must be precise about:
- Each obs item name
- Dimension
- Concatenation order (must exactly match training)
- Scaling coefficients (obs_scales)
- Noise range (if applicable)

Output format:

```markdown
| # | Observation Item | Dim | Scale | Noise Range | Description |
|---|------------------|-----|-------|-------------|-------------|
| 1 | base_ang_vel | 3 | 0.25 | ±0.2 | Base angular velocity (body frame) |
| 2 | projected_gravity | 3 | 1.0 | ±0.05 | Projected gravity vector |
| 3 | commands | 3 | 1.0 | None | Velocity commands [vx, vy, yaw_rate] |
| 4 | dof_pos - default_pos | N | 1.0 | ±0.01 | Relative joint positions |
| 5 | dof_vel | N | 0.05 | ±1.5 | Joint velocities |
| 6 | last_action | N | 1.0 | None | Previous step action |
| **Total** | | **X** | | | |
```

**Where to look:**
- `play.py` obs construction code (most reliable)
- `env_cfg.py` → `observations.policy.xxx` or `ObservationsCfg`
- Environment implementation → `_get_observations()` or `compute_observations()` method
- Note: some projects include history frames in obs — mark `history_length` if so

#### 2.4 Action Space

| Item | Description |
|---|---|
| Dimension | Usually equals number of controlled joints |
| Physical meaning | Target joint position / joint torque / position delta |
| Post-processing | clip → scale → offset (record in actual order) |
| action_beta | Action smoothing factor (EMA) |

**Action post-processing pipeline must be precisely recorded:**
```python
# Typical pipeline (record source project's actual pipeline)
action = model(obs)                          # Raw output
action = clip(action, -clip_val, clip_val)   # Clip
action = action * action_scale               # Scale
target_pos = action + default_pos            # Add offset (if applicable)
```

#### 2.5 Quaternion Format

Confirm the quaternion format used by the source project:
- `[x, y, z, w]` (scipy / IsaacLab default)
- `[w, x, y, z]` (PyBullet / some projects)

**RoboJuDo uses `[x, y, z, w]`. If different, record the required conversion.**

#### 2.6 Model File Information

| Item | Description |
|---|---|
| Model format | `.onnx` / `.pt` / `.jit` |
| Model path | Relative to source project root |
| File size | Bytes or MB |
| Input names | ONNX: `session.get_inputs()` |
| Output names | ONNX: `session.get_outputs()` — note which output is the action if multiple |
| Loading method | JIT / ONNX Runtime / checkpoint |

#### 2.7 Special Configuration (if applicable)

- History observations (history_length, history_obs_size)
- Motion reference data (motion tracking / reference motion)
- Velocity command mapping (commands_map, max_cmd)
- Compliance control
- Multi-modal inputs (vision, force sensors, etc.)

---

### Phase 3: Generate Output Document

Organize extracted information into a standardized Markdown document, saved in the RoboJuDo project:

**Output path**: `docs/SummaryNewPolicy/{POLICY_NAME}_policy_config.md`

**Document structure:**

```markdown
# {POLICY_NAME} - RoboJuDo Deployment Config

> Source: {SOURCE_PROJECT}
> Extracted: {DATE}
> Target platform: Unitree {ROBOT}

## 1. Basic Information
[Basic config table]

## 2. Joint Configuration
[Joint names, default_pos, stiffness, damping, action_scale — table + Python list format]

## 3. Observation Space
[Detailed obs item table with concatenation order, dimensions, scaling, noise]

## 4. Action Space
[Dimensions, meaning, post-processing pipeline]

## 5. Model Files
[Format, path, loading method]

## 6. Key Source Files
[List all referenced file paths]

## 7. RoboJuDo Integration Notes
[Quaternion conversion, joint order mapping, special handling, etc.]
```

### Phase 4: Verification Checklist

After generating the document, self-check each item:

- [ ] Joint count matches source project code
- [ ] Observation dimension total matches model input dimension
- [ ] Action dimension matches model output dimension
- [ ] Joint order exactly matches source project (not alphabetically sorted)
- [ ] All numeric list lengths equal joint count
- [ ] stiffness/damping/action_scale precision meets requirements
- [ ] Quaternion format is documented
- [ ] Action post-processing pipeline is completely recorded
- [ ] Model files exist and are accessible

---

## Collaboration with add-new-policy

This skill's output document is the input for the `add-new-policy` skill. Typical workflow:

```
1. /extract-policy-config   → Generates docs/SummaryNewPolicy/XXX_policy_config.md
2. /add-new-policy           → Reads above document + source project code, generates RoboJuDo policy code
```

Users can also do it in one step:
```
Integrate the policy from /home/hero/Projects/RL/MyProject into RoboJuDo
```
In this case, the agent should first load `extract-policy-config` to extract information, then load `add-new-policy` to generate code.
