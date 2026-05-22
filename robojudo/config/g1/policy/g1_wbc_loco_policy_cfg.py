from robojudo.policy.policy_cfgs import WbcLocoPolicyCfg
from robojudo.tools.tool_cfgs import DoFConfig


class G1WbcLocoDoF(DoFConfig):
    """G1 joint config for WBC Loco policy (policy order).

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
        -0.2, -0.2, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
        0.42, 0.42, 0.35, 0.35, -0.23, -0.23,
        0.18, -0.18, 0.0, 0.0, 0.0, 0.0,
        0.87, 0.87, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    ]
    stiffness: list[float] | None = [
        200, 200, 200, 150, 150, 200,
        150, 150, 200, 200, 200,
        100, 100, 20, 20,
        100, 100, 20, 20,
        50, 50, 50, 50,
        40, 40, 40, 40, 40, 40,
    ]
    damping: list[float] | None = [
        5, 5, 5, 5, 5, 5,
        5, 5, 5, 5, 5,
        2, 2, 2, 2,
        2, 2, 2, 2,
        2, 2, 2, 2,
        2, 2, 2, 2, 2, 2,
    ]


class G1WbcLocoPolicyCfg(WbcLocoPolicyCfg):
    """G1-specific configuration for WBC Loco policy."""
    robot: str = "g1"
    obs_dof: DoFConfig = G1WbcLocoDoF()
    action_dof: DoFConfig = G1WbcLocoDoF()
