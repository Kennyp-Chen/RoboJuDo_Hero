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


class G1WbcAmp23DoF(G1WbcAmpDoF):
    """G1 23-DoF joint config for WBC AMP policy (policy order).

    23 DoF removes 6 joints from 29 DoF:
    - waist_roll_joint, waist_pitch_joint
    - left_wrist_pitch_joint, left_wrist_yaw_joint
    - right_wrist_pitch_joint, right_wrist_yaw_joint

    Keeps: 12 leg + 1 waist_yaw + 10 arms (5 each side) = 23
    """

    _subset: bool = True
    _subset_joint_names: list[str] = [
        'left_hip_pitch_joint',
        'right_hip_pitch_joint',
        'waist_yaw_joint',
        'left_hip_roll_joint',
        'right_hip_roll_joint',
        'left_hip_yaw_joint',
        'right_hip_yaw_joint',
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
    robot_state_dim: int = 78  # 3+3+3+23+23+23
    history_obs_dims: dict[str, int] = {
        "ang_vel": 3,
        "gravity": 3,
        "commands": 3,
        "dof_pos": 23,
        "dof_vel": 23,
        "actions": 23,
    }
