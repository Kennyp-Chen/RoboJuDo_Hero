from robojudo.policy.policy_cfgs import MultiModalWBCPolicyCfg
from robojudo.tools.tool_cfgs import DoFConfig


class G1MultiModalWBCDoF(DoFConfig):
    joint_names: list[str] = [
        *[
            "left_hip_pitch_joint",
            "right_hip_pitch_joint",
            "waist_yaw_joint",
            "left_hip_roll_joint",
            "right_hip_roll_joint",
            "waist_roll_joint",
            "left_hip_yaw_joint",
            "right_hip_yaw_joint",
            "waist_pitch_joint",
            "left_knee_joint",
            "right_knee_joint",
        ],
        *[
            "left_shoulder_pitch_joint",
            "right_shoulder_pitch_joint",
            "left_ankle_pitch_joint",
            "right_ankle_pitch_joint",
            "left_shoulder_roll_joint",
            "right_shoulder_roll_joint",
            "left_ankle_roll_joint",
            "right_ankle_roll_joint",
            "left_shoulder_yaw_joint",
            "right_shoulder_yaw_joint",
        ],
        *[
            "left_elbow_joint",
            "right_elbow_joint",
            "left_wrist_roll_joint",
            "right_wrist_roll_joint",
            "left_wrist_pitch_joint",
            "right_wrist_pitch_joint",
            "left_wrist_yaw_joint",
            "right_wrist_yaw_joint",
        ],
    ]

    default_pos: list[float] | None = [
        *[-0.312, -0.312, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.669, 0.669],
        *[0.200, 0.200, -0.363, -0.363, 0.200, -0.200, 0.000, 0.000, 0.000, 0.000],
        *[0.600, 0.600, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000],
    ]

    stiffness: list[float] | None = [
        *[40.17923847137318, 40.17923847137318, 40.17923847137318, 99.09842777666113, 99.09842777666113, 28.50124619574858, 40.17923847137318, 40.17923847137318, 28.50124619574858, 99.09842777666113, 99.09842777666113],
        *[14.25062309787429, 14.25062309787429, 28.50124619574858, 28.50124619574858, 14.25062309787429, 14.25062309787429, 28.50124619574858, 28.50124619574858, 14.25062309787429, 14.25062309787429],
        *[14.25062309787429, 14.25062309787429, 14.25062309787429, 14.25062309787429, 16.77832748089279, 16.77832748089279, 16.77832748089279, 16.77832748089279],
    ]

    damping: list[float] | None = [
        *[2.5578897650279457, 2.5578897650279457, 2.5578897650279457, 6.3088018534966395, 6.3088018534966395, 1.814445686584846, 2.5578897650279457, 2.5578897650279457, 1.814445686584846, 6.3088018534966395, 6.3088018534966395],
        *[0.907222843292423, 0.907222843292423, 1.814445686584846, 1.814445686584846, 0.907222843292423, 0.907222843292423, 1.814445686584846, 1.814445686584846, 0.907222843292423, 0.907222843292423],
        *[0.907222843292423, 0.907222843292423, 0.907222843292423, 0.907222843292423, 1.06814150219, 1.06814150219, 1.06814150219, 1.06814150219],
    ]


class G1MultiModalWBCPolicyCfg(MultiModalWBCPolicyCfg):
    robot: str = "g1"

    policy_name: str = "policy"

    obs_dof: DoFConfig = G1MultiModalWBCDoF()
    action_dof: DoFConfig = obs_dof

    action_beta: float = 1.0
    # ======= POLICY SPECIFIC CONFIGURATION =======
    without_state_estimator: bool = True

    action_scales: list[float] = [
        *[0.5475464652142303, 0.5475464652142303, 0.5475464652142303, 0.3506614663788243, 0.3506614663788243, 0.43857731392336724, 0.5475464652142303, 0.5475464652142303, 0.43857731392336724, 0.3506614663788243, 0.3506614663788243],
        *[0.43857731392336724, 0.43857731392336724, 0.43857731392336724, 0.43857731392336724, 0.43857731392336724, 0.43857731392336724, 0.43857731392336724, 0.43857731392336724, 0.43857731392336724, 0.43857731392336724],
        *[0.43857731392336724, 0.43857731392336724, 0.43857731392336724, 0.43857731392336724, 0.07450087032950714, 0.07450087032950714, 0.07450087032950714, 0.07450087032950714],
    ]
