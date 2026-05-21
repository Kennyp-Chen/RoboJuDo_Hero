from robojudo.policy.policy_cfgs import AmpWalkPolicyCfg
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

    # default_pos: list[float] | None = [
    #     *[-0.1, -0.1, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.3, 0.3],
    #     *[0.3, 0.3, -0.2, -0.2, 0.25, -0.25, 0.0, 0.0, 0.0, 0.0],
    #     *[0.97, 0.97, 0.15, -0.15, 0.0, 0.0, 0.0, 0.0],
    # ]

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

