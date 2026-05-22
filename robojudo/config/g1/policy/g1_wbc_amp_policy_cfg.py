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


class G1WbcAmpPolicyCfg(WbcAmpPolicyCfg):
    """G1-specific configuration for WBC AMP policy."""
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
