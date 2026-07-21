from robojudo.policy.policy_cfgs import WbcAmpPolicyCfg
from robojudo.tools.tool_cfgs import DoFConfig


class G1WbcAmpDoF(DoFConfig):
    """G1 joint config for WBC AMP policy (policy order).

    Policy order = left-right grouped (both legs, both arms, waist).
    DoFAdapter in PolicyWrapper handles remapping from env motor order to this order.
    """

    joint_names: list[str] = [
        'left_hip_pitch_joint',
        'right_hip_pitch_joint',
        'waist_yaw_joint',
        'left_hip_roll_joint',
        'right_hip_roll_joint',
        'waist_roll_joint',
        'left_hip_yaw_joint',
        'right_hip_yaw_joint',
        'waist_pitch_joint',
        'left_knee_joint',
        'right_knee_joint',
        'left_shoulder_pitch_joint',
        'right_shoulder_pitch_joint',
        'left_ankle_pitch_joint',
        'right_ankle_pitch_joint',
        'left_shoulder_roll_joint',
        'right_shoulder_roll_joint',
        'left_ankle_roll_joint',
        'right_ankle_roll_joint',
        'left_shoulder_yaw_joint',
        'right_shoulder_yaw_joint',
        'left_elbow_joint',
        'right_elbow_joint',
        'left_wrist_roll_joint',
        'right_wrist_roll_joint',
        'left_wrist_pitch_joint',
        'right_wrist_pitch_joint',
        'left_wrist_yaw_joint',
        'right_wrist_yaw_joint',
    ]

    default_pos: list[float] | None = [
        -0.312, -0.312, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
        0.669, 0.669, 0.2, 0.2, -0.363, -0.363,
        0.2, -0.2, 0.0, 0.0, 0.0, 0.0,
        0.6, 0.6, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    ]
    stiffness: list[float] | None = [
        99.098, 99.098, 40.179, 99.098, 99.098, 28.501,
        40.179, 40.179, 28.501, 99.098, 99.098,
        14.251, 14.251, 28.501, 28.501,
        14.251, 14.251, 28.501, 28.501,
        14.251, 14.251, 14.251, 14.251,
        14.251, 14.251, 8.611, 8.611, 8.611, 8.611,
    ]
    damping: list[float] | None = [
        6.309, 6.309, 2.558, 6.309, 6.309, 1.814,
        2.558, 2.558, 1.814, 6.309, 6.309,
        0.907, 0.907, 1.814, 1.814,
        0.907, 0.907, 1.814, 1.814,
        0.907, 0.907, 0.907, 0.907,
        0.907, 0.907, 0.548, 0.548, 0.548, 0.548,
    ]


class G1WbcAmp23DoF(DoFConfig):
    """G1 23-DoF joint config for WBC AMP policy.

    Joint order matches env hardware order (G1_23DoF), so DoFAdapter is identity.
    This is essential: the 23-DoF ONNX model was trained with MuJoCo hardware order
    (left leg → right leg → waist → left arm → right arm), NOT left-right grouped.

    Stiffness/damping from g1_23dof_constants motor groups:
      7520_14 (hip_pitch/hip_yaw/waist_yaw): stiffness=40.179, damping=2.558
      7520_22 (hip_roll/knee):              stiffness=99.098, damping=6.309
      5020x2 (ankle_pitch/ankle_roll):      stiffness=28.501, damping=1.814
      5020 (shoulder/elbow/wrist):          stiffness=14.251, damping=0.907
    """

    joint_names: list[str] = [
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
        'left_shoulder_pitch_joint',
        'left_shoulder_roll_joint',
        'left_shoulder_yaw_joint',
        'left_elbow_joint',
        'left_wrist_roll_joint',
        'right_shoulder_pitch_joint',
        'right_shoulder_roll_joint',
        'right_shoulder_yaw_joint',
        'right_elbow_joint',
        'right_wrist_roll_joint',
    ]

    default_pos: list[float] | None = [0.0] * 23
    stiffness: list[float] | None = [
        40.179, 99.098, 40.179, 99.098, 28.501, 28.501,
        40.179, 99.098, 40.179, 99.098, 28.501, 28.501,
        40.179,
        14.251, 14.251, 14.251, 14.251, 14.251,
        14.251, 14.251, 14.251, 14.251, 14.251,
    ]
    damping: list[float] | None = [
        2.558, 6.309, 2.558, 6.309, 1.814, 1.814,
        2.558, 6.309, 2.558, 6.309, 1.814, 1.814,
        2.558,
        0.907, 0.907, 0.907, 0.907, 0.907,
        0.907, 0.907, 0.907, 0.907, 0.907,
    ]


class G1WbcAmpPolicyCfg(WbcAmpPolicyCfg):
    """G1-specific configuration for WBC AMP policy (29-DoF)."""
    robot: str = "g1"
    obs_dof: DoFConfig = G1WbcAmpDoF()
    action_dof: DoFConfig = G1WbcAmpDoF()

    history_obs_dims: dict[str, int] = {
        "ang_vel": 3,
        "gravity": 3,
        "commands": 3,
        "dof_pos": G1WbcAmpDoF().num_dofs,
        "dof_vel": G1WbcAmpDoF().num_dofs,
        "actions": G1WbcAmpDoF().num_dofs,
    }


class G1WbcAmp23PolicyCfg(G1WbcAmpPolicyCfg):
    """G1-specific configuration for WBC AMP policy (23-DoF).

    Uses 23-DoF ONNX model: Unitree-G1-23DOF-AMP-Flat-HeightReward2x_model_9700.onnx
    Observation per frame: 3(ang_vel) + 3(gravity) + 3(commands) + 23(dof_pos) + 23(dof_vel) + 23(action) = 78
    4-frame history: 78 * 4 = 312
    """

    model_dir: str = "wbc_amp/G1_23dof"

    @property
    def policy_file(self) -> str:
        from robojudo.config import ASSETS_DIR
        policy_file = ASSETS_DIR / f"models/{self.robot}/{self.model_dir}/Unitree-G1-23DOF-AMP-Flat-HeightReward2x_model_9700.onnx"
        return policy_file.as_posix()

    obs_dof: DoFConfig = G1WbcAmp23DoF()
    action_dof: DoFConfig = G1WbcAmp23DoF()

    # Per-joint action_scale in hardware order (matching training env.yaml)
    # Groups: hip_pitch/yaw/waist_yaw=0.5475, hip_roll/knee=0.3507, rest=0.4386
    action_scale: list[float] = [
        0.547546, 0.350661, 0.547546, 0.350661, 0.438577, 0.438577,
        0.547546, 0.350661, 0.547546, 0.350661, 0.438577, 0.438577,
        0.547546,
        0.438577, 0.438577, 0.438577, 0.438577, 0.438577,
        0.438577, 0.438577, 0.438577, 0.438577, 0.438577,
    ]

    robot_state_dim: int = 78  # 3+3+3+23+23+23
    history_obs_dims: dict[str, int] = {
        "ang_vel": 3,
        "gravity": 3,
        "commands": 3,
        "dof_pos": 23,
        "dof_vel": 23,
        "actions": 23,
    }
