# wbc_fsm - RoboJuDo Deployment Config

> Source: https://github.com/ccrpRepo/wbc_fsm
> Extracted: 2026-05-21
> Target platform: Unitree G1
> Sub-policies: AMP, Loco (LSTM), Dance (WBC motion tracking)

---

## 1. Basic Information

| Item | AMP | Loco | Dance |
|------|-----|------|-------|
| Project name | wbc_fsm | wbc_fsm | wbc_fsm |
| Robot model | Unitree G1 | Unitree G1 | Unitree G1 |
| Joint count | 29 | 29 | 29 |
| Control frequency | 50 Hz | 50 Hz | 50 Hz |
| Action scale | 0.25 | 0.25 | 0.25 |
| Action clip | [-100, 100] | [-100, 100] | [-100, 100] |
| Obs clip | [-100, 100] | [-100, 100] | [-100, 100] |
| History length | 4 frames (stacked) | 1 frame (LSTM states) | 4 frames (robot state) |
| Model file | `model/loco/amp_0309_1.onnx` | `model/loco/loco_0731.onnx` | `model/wbc/dance12_0207_1.onnx` |
| File size | ~1.4 MB | ~2.1 MB | ~1.6 MB |
| Input name | `obs` | `obs`, `h_in`, `c_in` | `obs` |
| Output names | `actions` | `actions`, `h_out`, `c_out` | `actions` |

---

## 2. Joint Configuration

### Motor Order (MuJoCo XML order)

Motor order is the order of actuators in the MuJoCo XML file `assets/robots/g1/g1_29dof_rev_1_0.xml`.
This is the order of `motorState[]` in wbc_fsm C++ code and `env_data.dof_pos` in RoboJuDo.

```
Index: Joint Name
    0: left_hip_pitch_joint
    1: left_hip_roll_joint
    2: left_hip_yaw_joint
    3: left_knee_joint
    4: left_ankle_pitch_joint
    5: left_ankle_roll_joint
    6: right_hip_pitch_joint
    7: right_hip_roll_joint
    8: right_hip_yaw_joint
    9: right_knee_joint
   10: right_ankle_pitch_joint
   11: right_ankle_roll_joint
   12: waist_yaw_joint
   13: waist_roll_joint
   14: waist_pitch_joint
   15: left_shoulder_pitch_joint
   16: left_shoulder_roll_joint
   17: left_shoulder_yaw_joint
   18: left_elbow_joint
   19: left_wrist_roll_joint
   20: left_wrist_pitch_joint
   21: left_wrist_yaw_joint
   22: right_shoulder_pitch_joint
   23: right_shoulder_roll_joint
   24: right_shoulder_yaw_joint
   25: right_elbow_joint
   26: right_wrist_roll_joint
   27: right_wrist_pitch_joint
   28: right_wrist_yaw_joint
```

### Policy Order (left-right grouped — used by all 3 wbc_fsm ONNX models)

The policy order is defined by the `dof_mapping` array in the C++ FSM states:

```cpp
const int dof_mapping[NUM_DOF] = {0, 6, 12,    // left_hip_pitch, right_hip_pitch, waist_yaw
                                   1, 7, 13,    // left_hip_roll, right_hip_roll, waist_roll
                                   2, 8, 14,    // left_hip_yaw, right_hip_yaw, waist_pitch
                                   3, 9, 15, 22, // left_knee, right_knee, l_shoulder_pitch, r_shoulder_pitch
                                   4, 10, 16, 23, // left_ankle_pitch, right_ankle_pitch, l_shoulder_roll, r_shoulder_roll
                                   5, 11, 17, 24, // left_ankle_roll, right_ankle_roll, l_shoulder_yaw, r_shoulder_yaw
                                   18, 25,        // left_elbow, right_elbow
                                   19, 26,        // left_wrist_roll, right_wrist_roll
                                   20, 27,        // left_wrist_pitch, right_wrist_pitch
                                   21, 28};       // left_wrist_yaw, right_wrist_yaw
```

### Default DOF Positions

**Source:** `State_Amp.h` and `State_Loco.h` (`_default_dof_pos[NUM_DOF]`), in motor order.

```python
# AMP / Dance default_pos (motor order)
# Source: State_Amp.h
default_pos_amp_motor = [
    -0.312, 0.0, 0.0, 0.669, -0.363, 0.0,     # left leg
    -0.312, 0.0, 0.0, 0.669, -0.363, 0.0,     # right leg
    0.0, 0.0, 0.0,                              # waist
    0.2, 0.2, 0.0, 0.6, 0.0, 0.0, 0.0,         # left arm
    0.2, -0.2, 0.0, 0.6, 0.0, 0.0, 0.0,        # right arm
]

# Loco default_pos (motor order)
# Source: State_Loco.h
default_pos_loco_motor = [
    -0.2, 0.0, 0.0, 0.42, -0.23, 0.0,          # left leg
    -0.2, 0.0, 0.0, 0.42, -0.23, 0.0,          # right leg
    0.0, 0.0, 0.0,                              # waist
    0.35, 0.18, 0.0, 0.87, 0.0, 0.0, 0.0,      # left arm
    0.35, -0.18, 0.0, 0.87, 0.0, 0.0, 0.0,     # right arm
]
```

### PD Gains

**Source:** `State_Amp.h` (`dof_Kps`, `dof_Kds`), in motor order.
Note: AMP uses symbolic constants `STIFFNESS_7520_22`, `STIFFNESS_5020`, etc. from `common/ArmatureConstants.h`.

```python
# AMP / Dance stiffness (motor order)
stiffness_amp = [
    99.098, 99.098, 40.179, 99.098, 28.501, 28.501,
    99.098, 99.098, 40.179, 99.098, 28.501, 28.501,
    40.179, 28.501, 28.501,
    14.251, 14.251, 14.251, 14.251, 14.251, 8.611, 8.611,
    14.251, 14.251, 14.251, 14.251, 14.251, 8.611, 8.611,
]

# AMP / Dance damping (motor order)
damping_amp = [
    6.309, 6.309, 2.558, 6.309, 1.814, 1.814,
    6.309, 6.309, 2.558, 6.309, 1.814, 1.814,
    2.558, 1.814, 1.814,
    0.907, 0.907, 0.907, 0.907, 0.907, 0.548, 0.548,
    0.907, 0.907, 0.907, 0.907, 0.907, 0.548, 0.548,
]

# Loco stiffness (motor order)
stiffness_loco = [
    200, 150, 150, 200, 20, 20,
    200, 150, 150, 200, 20, 20,
    200, 200, 200,
    100, 100, 50, 50, 40, 40, 40,
    100, 100, 50, 50, 40, 40, 40,
]

# Loco damping (motor order)
damping_loco = [
    5, 5, 5, 5, 2, 2,
    5, 5, 5, 5, 2, 2,
    5, 5, 5,
    2, 2, 2, 2, 2, 2, 2,
    2, 2, 2, 2, 2, 2, 2,
]
```

---

## 3. Observation Space

### 3.1 AMP Observation

**Model input:** 384-dim (4-frame history stacked)
**Single frame:** 96-dim

| # | Observation Item | Dim | Scale (obs_scales) | Description |
|---|------------------|-----|-------------------|-------------|
| 1 | base_ang_vel | 3 | 1.0 | Body angular velocity (gyroscope, body frame) |
| 2 | projected_gravity | 3 | 1.0 | Gravity vector rotated to body frame |
| 3 | commands | 3 | 1.0 | Velocity commands [vx, vy, yaw_rate] |
| 4 | dof_pos - default_pos | 29 | 1.0 | Relative joint positions (policy order) |
| 5 | dof_vel | 29 | 1.0 | Joint velocities (policy order) |
| 6 | last_action | 29 | — | Previous step action |
| **Single frame** | | **96** | | |
| **4-frame history** | | **384** | | Stacked along feature dim: `[f0, f1, f2, f3]` |

**Source:** `State_Amp.cpp` → `_observations_compute()`, lines 106-167.

**Obs construction order (C++):**
```cpp
current_robot_state.insert(end, body_ang_vel);       // 3
current_robot_state.insert(end, obs_projected_gravity); // 3
current_robot_state.insert(end, _vCmdBody);           // 3  [vx, vy, yaw]
current_robot_state.insert(end, dof_pos_vec);         // 29 (motor[].q - default_dof_pos, in policy order)
current_robot_state.insert(end, dof_vel_vec);         // 29 (motor[].dq, in policy order)
current_robot_state.insert(end, _action);             // 29
```

### 3.2 Loco Observation

**Model input:** 96-dim (single frame, LSTM handles temporal info via h/c states)

| # | Observation Item | Dim | Scale | Description |
|---|------------------|-----|-------|-------------|
| 1 | base_ang_vel | 3 | 1.0 | Body angular velocity (gyroscope, body frame) |
| 2 | projected_gravity | 3 | 1.0 | Gravity vector rotated to body frame |
| 3 | commands | 3 | 1.0 | Velocity commands [vx, vy, yaw_rate] |
| 4 | dof_pos - default_pos | 29 | 1.0 | Relative joint positions (policy order) |
| 5 | dof_vel | 29 | 1.0 | Joint velocities (policy order) |
| 6 | last_action | 29 | — | Previous step action |
| **Total** | | **96** | | |

**Source:** `State_Loco.cpp` → `_observations_compute()`, lines 69-131.

**Obs construction order (C++):**
```cpp
_observation.insert(end, body_ang_vel);       // 3
_observation.insert(end, obs_projected_gravity); // 3
_observation.insert(end, obs_commands);         // 3
_observation.insert(end, dof_pos_vec);          // 29
_observation.insert(end, dof_vel_vec);          // 29
_observation.insert(end, _action);              // 29
```

**LSTM state dimensions:** h_in/h_out and c_in/c_out are both `[1, 1, 256]`.

### 3.3 Dance (WBC) Observation

**Model input:** 439-dim = 372 (robot state history: 93×4) + 67 (reference motion)
- robot_state_per_frame: 93 = 3(ang_vel) + 3(gravity) + 29(dof_pos-rel) + 29(dof_vel) + 29(action)
  *(Note: no commands in WBC obs)*
- history frames: 4 (stacked)
- reference motion: 67 = 29(dof_pos) + 29(dof_vel) + 3(anchor_pos) + 6(anchor_ori)

**Source:** `State_WBC.cpp` → `_observations_compute()`

**Key caveat:** The Dance policy requires reference motion binary data files (not present in the shipped model directory). Without reference data, `mimic_obs` is zero-padded, and the policy will not produce meaningful walking/output.

---

## 4. Action Space

| Item | Value |
|------|-------|
| Dimension | 29 |
| Physical meaning | Target joint position delta (added to default_pos) |
| Action scale | 0.25 |
| Action clip | [-100, 100] |
| Smoothing (beta) | 1.0 (no EMA smoothing in C++ — but RoboJuDo applies it) |

### AMP Action Post-processing

**Source:** `State_Amp.cpp` → `_action_compute()`, lines 192-235.

```cpp
// Raw model output
_action[i] = output_tensors[0][i];

// Clip
_action[i] = max(-100.0, min(_action[i], 100.0));

// Scale + add default_pos (both in motor order via dof_mapping)
actions_scaled[i] = _action[i] * 0.25 + _default_dof_pos[dof_mapping[i]];

// Apply to joint command in motor order
_joint_q[dof_mapping[i]] = actions_scaled[i];
```

### Loco Action Post-processing

**Source:** `State_Loco.cpp` → `_action_compute()`, lines 158-195.

```cpp
// Raw model output → _action (policy order)
// Clip
_action[i] = max(-100.0, min(_action[i], 100.0));

// Scale only (no default_pos in scale step)
actions_scaled[i] = _action[i] * 0.25;

// Add default_pos and map to motor order
_joint_q[dof_mapping[i]] = actions_scaled[i] + _default_dof_pos[dof_mapping[i]];
```

### Equivalent Python Logic (used in RoboJuDo pipeline)

```python
# In WbcPolicy.get_action():
#   Returns action WITHOUT default_pos, in policy order
#   Action is already clipped and scaled

# In PolicyWrapper.get_pd_target():
pd_target = action + self.policy.default_pos   # policy-order PD target
return actions_adapter.fit(pd_target, template=env_default_pos)  # → motor order
```

---

## 5. Model Files

| Policy | Source Path | Format | Size | Inputs | Outputs |
|--------|-----------|--------|------|--------|---------|
| AMP | `model/loco/amp_0309_1.onnx` | ONNX | ~1.4 MB | `obs: [1, 384]` | `actions: [1, 29]` |
| Loco | `model/loco/loco_0731.onnx` | ONNX | ~2.1 MB | `obs: [1, 96]`, `h_in: [1,1,256]`, `c_in: [1,1,256]` | `actions: [1,29]`, `h_out: [1,1,256]`, `c_out: [1,1,256]` |
| Dance | `model/wbc/dance12_0207_1.onnx` | ONNX | ~1.6 MB | `obs: [1, 439]` | `actions: [1, 29]` |

**Loading:** ONNX Runtime (`CPUExecutionProvider` by default, `CUDAExecutionProvider` if GPU available)

---

## 6. Velocity Commands

### AMP

```cpp
// vx: max forward 3.0, max backward -3.0
_vxLim = {-3.0, 3.0};
// vy: max lateral ±0.01 (effectively disabled for AMP)
_vyLim = {-0.01, 0.01};
// yaw: max ±1.57 rad/s
_wyawLim = {-1.57, 1.57};
```

### Loco

```cpp
// vx: max forward 0.85, max backward -0.6 (from commands_map)
_vxLim = {-0.6, 0.85};
// vy: max lateral ±0.4
_vyLim = {-0.4, 0.4};
// yaw: max ±1.0 (dYawCmd)
_wyawLim = {-1.0, 1.0};
```

---

## 7. Quaternion Format

- **wbc_fsm C++ code:** `{w, x, y, z}` (Eigen convention)
  - `_lowState->imu.quaternion[0]` = w
  - `_lowState->imu.quaternion[1]` = x
  - `_lowState->imu.quaternion[2]` = y
  - `_lowState->imu.quaternion[3]` = z
- **RoboJuDo:** `{x, y, z, w}` (scipy convention)
  - **Conversion needed when reading raw quaternions** (though `get_gravity_orientation()` in RoboJuDo handles this internally)

---

## 8. Key Source Files

| File | Relevance |
|------|-----------|
| `wbc_fsm/include/FSM/State_Amp.h` | AMP constants: `dof_mapping`, `_default_dof_pos`, `dof_Kps`, `dof_Kds`, obs/action dims |
| `wbc_fsm/src/FSM/State_Amp.cpp` | AMP obs construction (`_observations_compute`), action compute (`_action_compute`) |
| `wbc_fsm/include/FSM/State_Loco.h` | Loco constants: `dof_mapping`, `_default_dof_pos`, `dof_Kps`, `dof_Kds`, LSTM inputs |
| `wbc_fsm/src/FSM/State_Loco.cpp` | Loco obs construction, action compute with LSTM state management |
| `wbc_fsm/include/FSM/State_WBC.h` | WBC/Dance constants: `_mimic_obs_predictive_horizon`, reference motion params |
| `wbc_fsm/src/FSM/State_WBC.cpp` | WBC obs construction with reference motion blending |
| `wbc_fsm/common/ArmatureConstants.h` | Symbolic constants for actuator stiffness/damping values |

---

## 9. RoboJuDo Integration Notes

### Joint Order Mapping

The critical integration detail is the `dof_mapping` array that converts between motor order and policy order:

```
Policy order (i) → Motor order (dof_mapping[i]):
   0→0,   1→6,   2→12,
   3→1,   4→7,   5→13,
   6→2,   7→8,   8→14,
   9→3,  10→9,  11→15, 12→22,
  13→4,  14→10, 15→16, 16→23,
  17→5,  18→11, 19→17, 20→24,
  21→18, 22→25,
  23→19, 24→26,
  25→20, 26→27,
  27→21, 28→28
```

**In RoboJuDo:** `DoFAdapter` in `PolicyWrapper` handles this automatically via joint name matching:
- `obs_adapter` maps env motor order → policy order
- `actions_adapter` maps policy order → env motor order

### DoFConfig Design

The G1-specific DoFConfig should use **policy order** (left-right grouped) for `joint_names` and `default_pos`. The `DoFAdapter` remaps to/from motor order at the env boundary.

### Observation Scaling vs C++

The C++ code uses `scale_lin_vel = 1.0`, `scale_ang_vel = 1.0`, `scale_dof_pos = 1.0`, `scale_dof_vel = 1.0` for all three policies. The RoboJuDo `obs_scales` can all be set to `1.0`.

### Action Compute vs RoboJuDo Pipeline

- C++ adds `default_pos` inside action_compute: `actions_scaled[i] = _action[i] * 0.25 + default_pos[dof_mapping[i]]`
- RoboJuDo pipeline adds `default_pos` in `get_pd_target()`: `pd_target = action + self.policy.default_pos`
- Both approaches produce the same target position because the default_pos is consistently mapped

### Dance Policy Requirements

The Dance policy requires reference motion binary files (`.bin`) for motion tracking. Without these, the `mimic_obs` input is all zeros, and the policy output may be unstable or meaningless. The motion files were not included in the copied model directory.
