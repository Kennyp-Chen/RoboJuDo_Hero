from robojudo.policy.policy_cfgs import AmpWalkPolicyCfg,AmpRunWalkPolicyCfg,AmpRecoveryPolicyCfg
from robojudo.tools.tool_cfgs import DoFConfig

class G1AmpDoF(DoFConfig):

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

    default_pos: list[float] | None =  [-0.1000, -0.1000,  0.0000,  0.0000,  0.0000,  0.0000,  0.0000,  0.0000,
          0.0000,  0.3000,  0.3000,  0.3000,  0.3000, -0.2000, -0.2000,  0.2500,
         -0.2500,  0.0000,  0.0000,  0.0000,  0.0000,  0.9700,  0.9700,  0.1500,
         -0.1500,  0.0000,  0.0000,  0.0000,  0.0000]
    # 刚度
    stiffness: list[float] | None = [100., 100., 200., 100., 100.,  40., 100., 100.,  40., 150., 150.,
        40.,  40.,  40.,  40.,  40.,  40.,  40.,  40.,  40.,  40.,  40.,
        40.,  40.,  40.,  40.,  40.,  40.,  40.]
    # 阻尼
    damping: list[float] | None = [2., 2., 5., 2., 2., 5., 2., 2., 5., 4., 4., 1., 1., 2., 2., 1., 1.,
       2., 2., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1.]
    '''
        {'default_pos': array([-0.1 , -0.1 ,  0.  ,  0.  ,  0.  ,  0.  ,  0.  ,  0.  ,  0.  ,
        0.3 ,  0.3 ,  0.3 ,  0.3 , -0.2 , -0.2 ,  0.25, -0.25,  0.  ,
        0.  ,  0.  ,  0.  ,  0.97,  0.97,  0.15, -0.15,  0.  ,  0.  ,
        0.  ,  0.  ], dtype=float32), 
        'stiffness': array([100., 100., 200., 100., 100.,  40., 100., 100.,  40., 150., 150.,
        40.,  40.,  40.,  40.,  40.,  40.,  40.,  40.,  40.,  40.,  40.,
        40.,  40.,  40.,  40.,  40.,  40.,  40.], dtype=float32), 
        'damping': array([2., 2., 5., 2., 2., 5., 2., 2., 5., 4., 4., 1., 1., 2., 2., 1., 1.,
       2., 2., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1.], dtype=float32), 
       'effort_limit': array([ 88.,  88.,  88., 139., 139.,  25.,  88.,  88.,  25., 139., 139.,
        25.,  25.,  25.,  25.,  25.,  25.,  25.,  25.,  25.,  25.,  25.,
        25.,  25.,  25.,   5.,   5.,   5.,   5.], dtype=float32), 'velocity_limit': array([32., 32., 32., 20., 20., 37., 32., 32., 37., 20., 20., 37., 37.,
       37., 37., 37., 37., 37., 37., 37., 37., 37., 37., 37., 37., 22.,
       22., 22., 22.], dtype=float32), 'armature': array([0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01,
       0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01,
       0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01], dtype=float32)}
    '''
class G1AmpWalkPolicyCfg(AmpWalkPolicyCfg):
    """
    Old
    """

    obs_dof: DoFConfig = G1AmpDoF()
    action_dof: DoFConfig = obs_dof
    
    history_obs_dims: dict[str, int] = {
        "ang_vel": 3,
        "gravity": 3, 
        "commands": 3,
        "dof_pos": obs_dof.num_dofs,
        "dof_vel": obs_dof.num_dofs,
        "actions": action_dof.num_dofs,
    }
    # 96



class G1AmpRunWalkPolicyCfg(AmpRunWalkPolicyCfg):
    '''
    新版 legged_lab amp 260212
    1. base_ang_vel: 3维
    2. root_local_rot_tan_norm: 6维
    3. velocity_commands: 3维
    4. joint_pos: 29维 (G1机器人29个关节)
    5. joint_vel: 29维
    6. actions: 29维 (上一步动作)
    7. key_body_pos_b: 18维 (6个关键身体部位 × 3维坐标)
        - left_ankle_roll_link, right_ankle_roll_link
        - left_wrist_yaw_link, right_wrist_yaw_link
        - left_shoulder_roll_link, right_shoulder_roll_link
    单时间步总维度: 3 + 6 + 3 + 29 + 29 + 29 + 18 = 117维
    包含5步历史: 117 × 5 = 585维 ✓
    '''
    obs_dof: DoFConfig = G1AmpDoF()
    action_dof: DoFConfig = obs_dof
    
    history_obs_dims: dict[str, int] = {
        "ang_vel": 3,
        "root_local_rot_tan_norm": 6, 
        "commands": 3,
        "dof_pos": obs_dof.num_dofs,
        "dof_vel": obs_dof.num_dofs,
        "actions": action_dof.num_dofs,
        "key_body_pos_b": 6*3,
    }
    # 117

ARMATURE_5020 = 0.003609725
ARMATURE_7520_14 = 0.010177520
ARMATURE_7520_22 = 0.025101925
ARMATURE_4010 = 0.00425
ARMATURE_5010_16 = 0.0021812

NATURAL_FREQ = 10.0 * 2.0 * 3.1415926535
DAMPING_RATIO = 2.0

STIFFNESS_5020 = ARMATURE_5020 * NATURAL_FREQ * NATURAL_FREQ
STIFFNESS_7520_14 = ARMATURE_7520_14 * NATURAL_FREQ * NATURAL_FREQ
STIFFNESS_7520_22 = ARMATURE_7520_22 * NATURAL_FREQ * NATURAL_FREQ
STIFFNESS_4010 = ARMATURE_4010 * NATURAL_FREQ * NATURAL_FREQ
STIFFNESS_5010_16 = ARMATURE_5010_16 * NATURAL_FREQ * NATURAL_FREQ

DAMPING_5020 = 2.0 * DAMPING_RATIO * ARMATURE_5020 * NATURAL_FREQ
DAMPING_7520_14 = 2.0 * DAMPING_RATIO * ARMATURE_7520_14 * NATURAL_FREQ
DAMPING_7520_22 = 2.0 * DAMPING_RATIO * ARMATURE_7520_22 * NATURAL_FREQ
DAMPING_4010 = 2.0 * DAMPING_RATIO * ARMATURE_4010 * NATURAL_FREQ
DAMPING_5010_16 = 2.0 * DAMPING_RATIO * ARMATURE_5010_16 * NATURAL_FREQ

JOINTS_IDS = [0, 6, 12,
            1, 7, 13,
            2, 8, 14,
            3, 9, 15, 22,
            4, 10, 16, 23,
            5, 11, 17, 24,
            18, 25,
            19, 26,
            20, 27,
            21, 28]
import numpy as np
JOINTS_IDS_REVERSE = np.argsort(JOINTS_IDS).tolist()

class G1AmpRecoveryDoF(DoFConfig):
    # list
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
        'waist_roll_joint', 
        'waist_pitch_joint', 
        'left_shoulder_pitch_joint',
        'left_shoulder_roll_joint',
        'left_shoulder_yaw_joint', 
        'left_elbow_joint', 
        'left_wrist_roll_joint', 
        'left_wrist_pitch_joint', 
        'left_wrist_yaw_joint', 
        'right_shoulder_pitch_joint', 
        'right_shoulder_roll_joint', 
        'right_shoulder_yaw_joint', 
        'right_elbow_joint', 
        'right_wrist_roll_joint', 
        'right_wrist_pitch_joint', 
        'right_wrist_yaw_joint'
        ]
    # joint_names: list[str] = [
    #     *[
    #         "left_hip_pitch_joint",
    #         "right_hip_pitch_joint",
    #         "waist_yaw_joint",
    #         "left_hip_roll_joint",
    #         "right_hip_roll_joint",
    #         "waist_roll_joint",
    #         "left_hip_yaw_joint",
    #         "right_hip_yaw_joint",
    #         "waist_pitch_joint",
    #         "left_knee_joint",
    #         "right_knee_joint",
    #     ],
    #     *[
    #         "left_shoulder_pitch_joint",
    #         "right_shoulder_pitch_joint",
    #         "left_ankle_pitch_joint",
    #         "right_ankle_pitch_joint",
    #         "left_shoulder_roll_joint",
    #         "right_shoulder_roll_joint",
    #         "left_ankle_roll_joint",
    #         "right_ankle_roll_joint",
    #         "left_shoulder_yaw_joint",
    #         "right_shoulder_yaw_joint",
    #     ],
    #     *[
    #         "left_elbow_joint",
    #         "right_elbow_joint",
    #         "left_wrist_roll_joint",
    #         "right_wrist_roll_joint",
    #         "left_wrist_pitch_joint",
    #         "right_wrist_pitch_joint",
    #         "left_wrist_yaw_joint",
    #         "right_wrist_yaw_joint",
    #     ],
    # ]


    default_pos: list[float] | None =  [-0.312, 0.0, 0.0, 0.669, -0.363, 0.0,
                                        -0.312, 0.0, 0.0, 0.669, -0.363, 0.0,
                                        0.0, 0.0, 0.0, 
                                        0.2, 0.2, 0.0, 0.6, 0.0, 0.0, 0.0,
                                        0.2, -0.2, 0.0, 0.6, 0.0, 0.0, 0.0,]
    # 刚度
    stiffness: list[float] | None = [STIFFNESS_7520_22, STIFFNESS_7520_22, STIFFNESS_7520_14, STIFFNESS_7520_22, 2.0 * STIFFNESS_5020, 2.0 * STIFFNESS_5020,
                                STIFFNESS_7520_22, STIFFNESS_7520_22, STIFFNESS_7520_14, STIFFNESS_7520_22, 2.0 * STIFFNESS_5020, 2.0 * STIFFNESS_5020,
                                STIFFNESS_7520_14, 2.0 * STIFFNESS_5020, 2.0 * STIFFNESS_5020,
                                STIFFNESS_5020, STIFFNESS_5020, STIFFNESS_5020, STIFFNESS_5020, STIFFNESS_5020, STIFFNESS_5010_16, STIFFNESS_5010_16,
                                STIFFNESS_5020, STIFFNESS_5020, STIFFNESS_5020, STIFFNESS_5020, STIFFNESS_5020, STIFFNESS_5010_16, STIFFNESS_5010_16,]
    # 阻尼
    damping: list[float] | None = [DAMPING_7520_22, DAMPING_7520_22, DAMPING_7520_14, DAMPING_7520_22, 2.0 * DAMPING_5020, 2.0 * DAMPING_5020,
                                DAMPING_7520_22, DAMPING_7520_22, DAMPING_7520_14, DAMPING_7520_22, 2.0 * DAMPING_5020, 2.0 * DAMPING_5020,
                                DAMPING_7520_14, 2.0 * DAMPING_5020, 2.0 * DAMPING_5020,
                                DAMPING_5020, DAMPING_5020, DAMPING_5020, DAMPING_5020, DAMPING_5020, DAMPING_5010_16, DAMPING_5010_16,
                                DAMPING_5020, DAMPING_5020, DAMPING_5020, DAMPING_5020, DAMPING_5020, DAMPING_5010_16, DAMPING_5010_16,]
    joint_names = np.array(joint_names)[JOINTS_IDS].tolist()
    default_pos = np.array(default_pos)[JOINTS_IDS].tolist()
    stiffness = np.array(stiffness)[JOINTS_IDS].tolist()
    damping = np.array(damping)[JOINTS_IDS].tolist()
    

class G1AmpRecoveryPolicyCfg(AmpRecoveryPolicyCfg):
    obs_dof: DoFConfig = G1AmpRecoveryDoF()
    action_dof: DoFConfig = obs_dof
    
    history_obs_dims: dict[str, int] = {
        "ang_vel": 3,
        "gravity": 3, 
        "commands": 3,
        "dof_pos": obs_dof.num_dofs,
        "dof_vel": obs_dof.num_dofs,
        "actions": action_dof.num_dofs,
    }
    # action_clip:float=0.