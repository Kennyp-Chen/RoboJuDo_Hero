from robojudo.config import cfg_registry
from robojudo.controller.ctrl_cfgs import (
    JoystickCtrlCfg,  # noqa: F401
    KeyboardCtrlCfg,  # noqa: F401
    UnitreeCtrlCfg,  # noqa: F401
    BFMKeyboardCtrlCfg, BFMJoystickCtrlCfg
)
from robojudo.pipeline.pipeline_cfgs import (
    RlLocoMimicPipelineCfg,  # noqa: F401
    RlLocoMimicSimPipelineCfg,  # noqa: F401
    RlMultiPolicyPipelineCfg,  # noqa: F401
    RlPipelineCfg,  # noqa: F401
)

from .ctrl.g1_beyondmimic_ctrl_cfg import G1BeyondmimicCtrlCfg  # noqa: F401
from .ctrl.g1_motion_ctrl_cfg import (  # noqa: F401
    G1MotionCtrlCfg,
    G1MotionH2HCtrlCfg,
    G1MotionKungfuBotCtrlCfg,
    G1MotionTwistCtrlCfg,

)

from .ctrl.g1_twist_redis_ctrl_cfg import G1TwistRedisCtrlCfg  # noqa: F401
from .env.g1_dummy_env_cfg import G1DummyEnvCfg  # noqa: F401
from .env.g1_mujuco_env_cfg import G1_12MujocoEnvCfg, G1_23MujocoEnvCfg, G1MujocoEnvCfg  # noqa: F401
from .env.g1_real_env_cfg import G1RealEnvCfg, G1UnitreeCfg  # noqa: F401
from .policy.g1_amo_policy_cfg import G1AmoPolicyCfg  # noqa: F401
from .policy.g1_amp_policy_cfg import G1AmpWalkPolicyCfg  # noqa: F401
from .policy.g1_asap_policy_cfg import G1AsapLocoPolicyCfg, G1AsapPolicyCfg  # noqa: F401
from .policy.g1_beyondmimic_policy_cfg import G1BeyondMimicPolicyCfg  # noqa: F401
from .policy.g1_h2h_policy_cfg import G1H2HPolicyCfg  # noqa: F401
from .policy.g1_kungfubot_policy_cfg import G1KungfuBotGeneralPolicyCfg, G1KungfuBotPolicyCfg  # noqa: F401
from .policy.g1_smooth_policy_cfg import G1SmoothPolicyCfg  # noqa: F401
from .policy.g1_twist_policy_cfg import G1TwistPolicyCfg  # noqa: F401
from .policy.g1_unitree_policy_cfg import G1UnitreePolicyCfg, G1UnitreeWoGaitPolicyCfg  # noqa: F401
from .policy.g1_unitree_velocity_policy_cfg import G1UnitreeMjlabVelocityPolicyCfg# G1UnitreeWoGaitVelocityPolicyCfg  # noqa: F401
from .policy.g1_bfmzero_policy_cfg import (
    G1BFMZeroPolicyCfg,
    G1BFMZeroTrackingPolicyCfg,
    G1BFMZeroTracking23DoFPolicyCfg,
    G1BFMZeroGoal23DoFPolicyCfg,
    G1BFMZeroReward23DoFPolicyCfg,
    G1BFMZeroRewardPolicyCfg,
    G1BFMZeroGoalPolicyCfg,
)
from .policy.g1_gentle_policy_cfg import G1GentlePolicyCfg
from .policy.g1_kungfuathlete_policy_cfg import G1KungFuAthletePolicyCfg
from .policy.g1_wbc_amp_policy_cfg import G1WbcAmpPolicyCfg
from .policy.g1_wbc_loco_policy_cfg import G1WbcLocoPolicyCfg
from .policy.g1_wbc_dance_policy_cfg import G1WbcDancePolicyCfg


# ======================== Custom Configs ======================== #
"""
Add your custom config here.
"""

@cfg_registry.register
class g1_locomimic_sim(RlLocoMimicSimPipelineCfg):
    """
    Example of loco mimic pipeline configuration.
    You can switch between loco and mimic policies during runtime, with interpolation.
    === Check more fancy locomimic examples in g1_loco_mimic_cfg.py ===
    """

    robot: str = "g1"
    env: G1MujocoEnvCfg = G1MujocoEnvCfg()

    # env: G1_23MujocoEnvCfg = G1_23MujocoEnvCfg()

    ctrl: list[KeyboardCtrlCfg | JoystickCtrlCfg ] = [
        KeyboardCtrlCfg(
            triggers_extra={
                "]": "[POLICY_LOCO]",
                "[": "[POLICY_MIMIC]",
                ";": "[POLICY_SWITCH],NEXT",
                "'": "[POLICY_SWITCH],LAST",
                # "Key.tab": "[POLICY_TOGGLE]",

            }
        ),
        JoystickCtrlCfg(
            triggers_extra={
                "RB+Down": "[POLICY_LOCO]",
                "RB+Up": "[POLICY_MIMIC]",
            }
        ),
        BFMKeyboardCtrlCfg(),

    ]

    loco_policy: G1UnitreeMjlabVelocityPolicyCfg = G1UnitreeMjlabVelocityPolicyCfg(
        max_cmd=[1.5, 1., 2.],# sim比real会更保守，所以加大
        commands_map=[
            [-0.6, 0.0, 0.9],
            [1.0, 0.0, -1.0],
            [1.5, 0.0, -1.],
        ]
    )

    # loco_policy: G1UnitreeWoGaitPolicyCfg = G1UnitreeWoGaitPolicyCfg()
    # loco_policy: G1UnitreePolicyCfg = G1UnitreePolicyCfg()
        
    # loco_policy: G1AmpRunWalkPolicyCfg=G1AmpRunWalkPolicyCfg()
    # loco_policy:G1AmpRecoveryPolicyCfg=G1AmpRecoveryPolicyCfg()
    # loco_policy: G1AsapLocoPolicyCfg = G1AsapLocoPolicyCfg()

    # loco_policy: list[G1UnitreePolicyCfg|G1UnitreeWoGaitPolicyCfg|G1AsapLocoPolicyCfg] = [
    #     G1UnitreePolicyCfg(),
    #     G1UnitreeWoGaitPolicyCfg(),
    #     G1AsapLocoPolicyCfg(),
    # ]


    mimic_policies: list[G1BeyondMimicPolicyCfg | G1BFMZeroTracking23DoFPolicyCfg | G1BFMZeroGoal23DoFPolicyCfg | G1BFMZeroReward23DoFPolicyCfg] = [
        ###############GentleHumanoid Policies###############
        
        ###############BFM Zero Policies###############
        # G1BFMZeroTracking23DoFPolicyCfg(),
        # G1BFMZeroTrackingPolicyCfg(),
        # G1BFMZeroGoal23DoFPolicyCfg(),
        # G1BFMZeroGoalPolicyCfg(),  
        # G1BFMZeroReward23DoFPolicyCfg(),
        # G1BFMZeroRewardPolicyCfg(),
        ##################BeyondMimic Policies######################
        # G1BeyondMimicPolicyCfg(policy_name="29dof_50fps/OldTownRoad_v1",),
        G1BeyondMimicPolicyCfg(policy_name="23dof_50fps/eva_angel_dance",),
        G1BeyondMimicPolicyCfg(policy_name="23dof_50fps/goodness_dance",),
        G1BeyondMimicPolicyCfg(policy_name="23dof_50fps/gangster_dance",),
        G1BeyondMimicPolicyCfg(policy_name="23dof_50fps/baicai",),
        G1BeyondMimicPolicyCfg(policy_name="23dof_50fps/slide",),
        G1BeyondMimicPolicyCfg(policy_name="23dof_50fps/go_james",),
        G1BeyondMimicPolicyCfg(policy_name="23dof_50fps/go_woman",),
        G1BeyondMimicPolicyCfg(policy_name="23dof_50fps/OldTownRoad_v1",),

        # 23dof_50fps start####################################
        # # # fightAndSports1_subject1
        # G1BeyondMimicPolicyCfg(# KUNGFU HighKICK 蹲下后结束
        #     policy_name="23dof_50fps/fight1_subject2",
        #     start_timestep = 850,
        #     max_timestep=1250,        
        # ),
        # G1BeyondMimicPolicyCfg(# KUNGFU HighKICK 上钩拳后结束
        #     policy_name="23dof_50fps/fight1_subject2",
        #     start_timestep = 850,
        #     max_timestep=1350,        
        # ),

        # G1BeyondMimicPolicyCfg(# BOX
        #     policy_name="23dof_50fps/fightAndSports1_subject1",
        #     start_timestep = 3800,
        #     max_timestep=4900,        
        # ),
        G1BeyondMimicPolicyCfg(# 旋转踢腿
            policy_name="23dof_50fps/fightAndSports1_subject1",
            start_timestep = 5200,
            max_timestep=6300,        
        ),
        # G1BeyondMimicPolicyCfg(# 
        #     policy_name="23dof_50fps/fightAndSports1_subject1",
        #     start_timestep = 6200,
        #     max_timestep=8390,        
        # ),

        # fight1_subject2 上钩拳 长序列 双踢腿 ；保龄球；篮球接球传球
        # G1BeyondMimicPolicyCfg( # 1800-2000上钩拳
        #     policy_name="23dof_50fps//WoHandTrack/fight1_subject2",
        #     start_timestep = 1590,
        #     max_timestep=2000,        
        # ),
        G1BeyondMimicPolicyCfg( # 5000-5100 双踢腿 
            policy_name="23dof_50fps//WoHandTrack/fight1_subject2",
            start_timestep = 4800,
            max_timestep=5250,        
        ),
        G1BeyondMimicPolicyCfg( # 三连双踢腿 
            policy_name="23dof_50fps/WoHandTrack/fight1_subject2",
            start_timestep = 14300,
            max_timestep=14900,        
        ),
        ]
@cfg_registry.register
class g1_wbc_amp(RlPipelineCfg):
    """
    G1 robot with WBC_FSM AMP locomotion policy.
    Source: https://github.com/ccrpRepo/wbc_fsm
    """
    robot: str = "g1"
    # env: G1MujocoEnvCfg = G1MujocoEnvCfg()
    env: G1_23MujocoEnvCfg = G1_23MujocoEnvCfg()

    ctrl: list[KeyboardCtrlCfg | JoystickCtrlCfg] = [
        KeyboardCtrlCfg(
            triggers_extra={
                "w": "[POLICY_LOCO]",
                "s": "[POLICY_LOCO]",
            }
        ),
        JoystickCtrlCfg(),
    ]
    policy: G1WbcAmpPolicyCfg = G1WbcAmpPolicyCfg()


@cfg_registry.register
class g1_wbc_loco(RlPipelineCfg):
    """
    G1 robot with WBC_FSM Loco policy (LSTM-based).
    Source: https://github.com/ccrpRepo/wbc_fsm
    """
    robot: str = "g1"
    env: G1MujocoEnvCfg = G1MujocoEnvCfg()
    ctrl: list[KeyboardCtrlCfg | JoystickCtrlCfg] = [
        KeyboardCtrlCfg(
            triggers_extra={
                "w": "[POLICY_LOCO]",
                "s": "[POLICY_LOCO]",
            }
        ),
        JoystickCtrlCfg(),
    ]
    policy: G1WbcLocoPolicyCfg = G1WbcLocoPolicyCfg()


@cfg_registry.register
class g1_wbc_dance(RlPipelineCfg):
    """
    G1 robot with WBC_FSM Dance policy (motion tracking WBC).
    Source: https://github.com/ccrpRepo/wbc_fsm
    Note: Requires reference motion binary data for full functionality.
    """
    robot: str = "g1"
    env: G1MujocoEnvCfg = G1MujocoEnvCfg()
    # env: G1_23MujocoEnvCfg = G1_23MujocoEnvCfg()

    ctrl: list[KeyboardCtrlCfg | JoystickCtrlCfg] = [
        KeyboardCtrlCfg(),
        JoystickCtrlCfg(),
    ]
    policy: G1WbcDancePolicyCfg = G1WbcDancePolicyCfg()


@cfg_registry.register
class g1_real_locomimic_custom(RlLocoMimicPipelineCfg):
    """
    Real G1 Robot with Loco-Mimic switching.
    Switch between locomotion (WASD control) and mimic (BeyondMimic/...) policies.
    
    Usage:
        python scripts/run_pipeline.py -c g1_real_locomimic
    
    Controls (Keyboard via SSH):
        - WASD/QE: Movement control (when in LOCO mode)
        - ]: Switch to LOCO mode
        - [: Switch to current MIMIC policy
        - 1: Switch to Dance motion
        - 2: Switch to xxxx motion
        - 5: Switch to sitting pose
        - 6: Switch to standing pose
        - ESC: Emergency stop
    
    Controls (Unitree Controller):
        - Left/Right Stick: Movement control (when in LOCO mode)
        - Y: Switch to LOCO mode
        - X: Switch to current MIMIC policy
        - up: Switch to Dance motion
        - down: Switch to xxxx motion
        - A: Emergency stop
        - B: Switch to sitting pose
        - L2+Up: Switch to standing pose
    """

    robot: str = "g1"
    
    # Real robot environment
    env: G1RealEnvCfg = G1RealEnvCfg(
        env_type="UnitreeCppEnv",
        unitree=G1UnitreeCfg(
            net_if="eth0",
        ),
    )

    # # Sitting pose configuration
    sitting_pos: list[float] = [
        *[-1.2, 0.0, 0.0, 1.5, -0.2, 0.0],  # 左腿
        *[-1.2, 0.0, 0.0, 1.5, -0.2, 0.0],  # 右腿
        *[0, 0, 0],  # 腰部
        # *[-0.4, 0, 0, 0, -1.5, 0, 0],# 左臂
        # *[-0.4, 0, 0, 0, 1.5, 0, 0], # 右臂
        *[0.35,0.18,0.,0.87,0.,0.,0.],
        *[0.35,-0.18,0.,0.87,0.,0.,0.]
    ]

    # Standing pose configuration
    standing_pos: list[float] = [
        *[-0.1, 0.0, 0.0, 0.3, -0.2, 0.0],  # 左腿
        *[-0.1, 0.0, 0.0, 0.3, -0.2, 0.0],  # 右腿
        *[0, 0, 0],  # 腰部
        # *[0, 0, 0, 0, 0, 0, 0],  # 左臂
        # *[0, 0, 0, 0, 0, 0, 0],  # 右臂
        *[0.35,0.18,0.,0.87,0.,0.,0.],
        *[0.35,-0.18,0.,0.87,0.,0.,0.]
    ]

    # Keyboard and controller with policy switching
    ctrl: list[UnitreeCtrlCfg] = [
    # ctrl: list[KeyboardCtrlCfg | UnitreeCtrlCfg] = [
        # KeyboardCtrlCfg(
        #     ctrl_type="KeyboardStdinCtrl",
        #     triggers_extra={
        #         "]": "[POLICY_LOCO]",       # Switch to LOCO
        #         "[": "[POLICY_MIMIC]",      # Switch to current MIMIC
        #         # "Key.tab": "[POLICY_TOGGLE]",

        #         "1": "[POLICY_SWITCH],0",   #  Index0 motion
        #         "2": "[POLICY_SWITCH],1",   #  Index1 motion
        #         "3": "[POLICY_SWITCH],2",   #  Index2 motion
        #         "4": "[POLICY_SWITCH],3",   #  Index3 motion
        #         "5": "[SITTING_POSE]",      # Switch to sitting pose
        #         "6": "[STANDING_POSE]",      # Switch to standing pose

        #     }
        # ),
        UnitreeCtrlCfg(
            combination_init_buttons=["L1", "R1", "L2"],  # Add L2 for combination keys
            triggers_extra={
                "Y": "[POLICY_LOCO]",       # Y button -> LOCO
                "X": "[POLICY_MIMIC]",      # X button -> MIMIC
                "Up": "[POLICY_SWITCH],0",     # Up -> Index0 motion
                "Down": "[POLICY_SWITCH],1",   # Down -> Index1 motion
                "Left": "[POLICY_SWITCH],2",    # Left -> Index2 motion
                "Right": "[POLICY_SWITCH],3",   # Right -> Index3 motion
                "B": "[SITTING_POSE]",         # B button -> Switch to sitting pose
                "L2+Up": "[STANDING_POSE]",    # L2+Up -> Switch to standing pose
            }
        ),
    ]

    # Locomotion policy (WASD control)
    # loco_policy: G1UnitreeWoGaitPolicyCfg = G1UnitreeWoGaitPolicyCfg()
    # loco_policy: G1UnitreePolicyCfg = G1UnitreePolicyCfg()
    # loco_policy: G1AsapLocoPolicyCfg = G1AsapLocoPolicyCfg()
    loco_policy: G1UnitreeMjlabVelocityPolicyCfg = G1UnitreeMjlabVelocityPolicyCfg()
    # loco_policy: G1AmpWalkPolicyCfg = G1AmpWalkPolicyCfg()
    # loco_policy: G1AmoPolicyCfg() = G1AmoPolicyCfg(),
    # 

    '''
        policies: list[G1UnitreePolicyCfg | G1AmoPolicyCfg] = [
        G1UnitreePolicyCfg(),
        G1AmoPolicyCfg(),
    ]

    '''
    # Mimic policies: Dance + ASAP CR7
    mimic_policies: list[G1BeyondMimicPolicyCfg | G1AmoPolicyCfg|G1AmpWalkPolicyCfg] = [
       
       
        ## 260428test
        ### gvhmr dance
        # G1BeyondMimicPolicyCfg(policy_name="23dof_50fps/baicai",),# 效果可以
        # # G1BeyondMimicPolicyCfg(policy_name="23dof_50fps/slide",), 效果不佳
        # G1BeyondMimicPolicyCfg(policy_name="23dof_50fps/go_james",), # 最后动作有点僵硬
        # G1BeyondMimicPolicyCfg(policy_name="23dof_50fps/gangster_dance",),
        # G1BeyondMimicPolicyCfg(policy_name="23dof_50fps/goodness_dance",),
        G1BeyondMimicPolicyCfg(policy_name="23dof_50fps/eva_angel_dance",),
        G1BeyondMimicPolicyCfg(policy_name="23dof_50fps/go_woman",),# 效果更好

        # G1BeyondMimicPolicyCfg(policy_name="23dof_50fps/OldTownRoad_v1",),
        ### kungfu
        # G1BeyondMimicPolicyCfg(# KUNGFU KICK 蹲下后结束
        #     policy_name="23dof_50fps/fight1_subject2",
        #     start_timestep = 850,
        #     max_timestep=1250,        
        # ),
        # G1BeyondMimicPolicyCfg(# KUNGFU KICK 上钩拳后结束
        #     policy_name="23dof_50fps/fight1_subject2",
        #     start_timestep = 850,
        #     max_timestep=1350,        
        # ),
        # G1BeyondMimicPolicyCfg(# 旋转踢腿成功
        #     policy_name="23dof_50fps/fightAndSports1_subject1",
        #     start_timestep = 5200,
        #     max_timestep=6300,        
        # ),

        ## 260428test
        
        # # Index 0: Dance motion
        G1BeyondMimicPolicyCfg(
            policy_name="23dof_65fps/Take102",           
            start_timestep = 100,
            max_timestep=1800,        
        ),

        G1BeyondMimicPolicyCfg(# 扭扭 swing
            policy_name="23dof_50fps/WoHandTrack/dance2_subject4",
            start_timestep = 6800,
            max_timestep= 8760,        
        ),
        G1BeyondMimicPolicyCfg(
            policy_name="23dof_65fps/GangnamStyle",           
            start_timestep = 300,
            max_timestep=2000,        
        ),
        G1BeyondMimicPolicyCfg(# 遮眼舞蹈
            policy_name="23dof_50fps/WoHandTrack/dance2_subject4",
            start_timestep = 4500,
            max_timestep=6900,        
        ),

        ####23dof 65fps start####
        # G1BeyondMimicPolicyCfg( # 4
        #     policy_name="23dof_65fps/dance1_subject1",
        #     start_timestep = 3000,# 3400
        #     max_timestep=4300,        
        # ),

        # G1BeyondMimicPolicyCfg( # 5
        #     policy_name="23dof_65fps/dance1_subject1",
        #     start_timestep = 3380,
        #     max_timestep=4158,        
        # ),
        # # G1BeyondMimicPolicyCfg( # 6
        # #     policy_name="23dof_65fps/dance1_subject1",
        # #     start_timestep = 5800,# 适合运动开始
        # #     max_timestep=6400,        
        # # ),
        # G1BeyondMimicPolicyCfg( # 6
        #     policy_name="23dof_65fps/dance1_subject1",
        #     start_timestep = 5950,# 适合静止开始 更好
        #     max_timestep=6400,        
        # ),
        # G1BeyondMimicPolicyCfg( # 0
        #     policy_name="23dof_65fps/dance2_subject4",
        #     start_timestep = 9000,
        #     max_timestep=10600,       
        # ),
        # G1BeyondMimicPolicyCfg( # 1 不太稳定
        #     policy_name="23dof_65fps/dance2_subject4",
        #     start_timestep = 10100,
        #     max_timestep=11300,      
        # ),
        # # G1BeyondMimicPolicyCfg(
        # #     policy_name="23dof_65fps/dance2_subject4",
        # #     start_timestep = 6000,
        # #     max_timestep=6720,        
        # # ),
        # G1BeyondMimicPolicyCfg( # 2
        #     policy_name="23dof_65fps/dance2_subject4",
        #     start_timestep = 4300, 
        #     max_timestep=5700,        
        # ),
        # G1BeyondMimicPolicyCfg( # swing 结束些许不稳
        #     policy_name="23dof_65fps/dance2_subject4",
        #     start_timestep = 8800,
        #     max_timestep=10100,       
        # ),
        # G1BeyondMimicPolicyCfg(# 3
        #     policy_name="23dof_65fps/dance2_subject4",
        #     start_timestep = 5990, # 在往前10 试试 5990
        #     max_timestep=7400,   # 6720   
        # ),

        ####23dof 65fps end####



        ####23dof 80fps start####
        # G1BeyondMimicPolicyCfg(
        #     policy_name="Take102_23dof_80fps",
        #     start_timestep = 100,
        #     max_timestep=-1,),
        # G1BeyondMimicPolicyCfg(
        #     policy_name="horse_23dof_80fps",
        #     start_timestep = 100,
        #     max_timestep=-1,),
        # G1BeyondMimicPolicyCfg(
        #     policy_name="dance12_23dof",
        #     start_timestep = 100,
        #     max_timestep=-1,) ,
        # G1BeyondMimicPolicyCfg(
        #     policy_name="dance12_wose",
        #     start_timestep = 100,
        #     max_timestep=-1,) ,
        ####23dof 80fps end####
            
        # # G1BeyondMimicPolicyCfg(
        # #     policy_name="dance24_wose",
        # #     start_timestep = 1500,
        # #     max_timestep=2900,  
        # #     # max_timestep=2300,      1800  
        # #     # max_timestep= 1800 aa

        # # ),
        # # G1BeyondMimicPolicyCfg(
        # #     policy_name="dance24_wose",
        # #     start_timestep = 3100,
        # #     # max_timestep=4500,   
        # #     # max_timestep=4100,    # 4200 4100    
        # #     max_timestep=4000,   

        # # ),
        # # # G1BeyondMimicPolicyCfg(
        # # #     policy_name="dance24_wose",
        # # #     start_timestep = 4500,
        # # #     max_timestep=6800,        
        # # # ),
        # # G1BeyondMimicPolicyCfg(# 扭扭
        # #     policy_name="dance24_wose",
        # #     start_timestep = 6800,
        # #     # max_timestep= 8700,  
        # #     max_timestep= 7600,

        # # ),
        # # # G1BeyondMimicPolicyCfg(
        # # #     policy_name="dance24_wose",
        # # #     start_timestep = 8700,
        # # #     max_timestep=10900,        
        # # # ),
        # # # G1BeyondMimicPolicyCfg(# 不美观
        # # #     policy_name="dance24_wose",
        # # #     start_timestep = 200,
        # # #     max_timestep=1500,        
        # # # ),
        # # # FS11
        # # # G1BeyondMimicPolicyCfg(# KUNGFU KICK
        # # #     policy_name="fightSport11wose",
        # # #     start_timestep = 850,
        # # #     max_timestep=1740,        
        # # # ),
        # # G1BeyondMimicPolicyCfg(# BOX
        # #     policy_name="fightSport11wose",
        # #     start_timestep = 3800,
        # #     max_timestep=4850,        
        # # ),
        # # # G1BeyondMimicPolicyCfg(# 踢腿
        # # #     policy_name="fightSport11wose",
        # # #     start_timestep = 5300,
        # # #     max_timestep=-1,        
        # # # ),
        # # ## Dance12
        # # # G1BeyondMimicPolicyCfg(
        # # #     policy_name="dance12_wose",
        # # #     start_timestep = 1800,
        # # #     max_timestep=3000,        
        # # # ),
        # # # G1BeyondMimicPolicyCfg(# 有难度
        # # #     policy_name="dance12_wose",
        # # #     start_timestep = 3000,
        # # #     max_timestep=4900,        
        # # # ),
        # # # G1BeyondMimicPolicyCfg(# 难
        # # #     policy_name="dance12_wose",
        # # #     start_timestep = 4900,
        # # #     max_timestep=6500,        
        # # # ),
        # # ### Dance 11
        # # G1BeyondMimicPolicyCfg(
        # #     policy_name="Dance11_wose",           
        # #     start_timestep = 1850,
        # #     max_timestep = 3500,
        # # ),
        # # G1BeyondMimicPolicyCfg( # 会摔
        # #     policy_name="Dance11_wose",           
        # #     start_timestep = 3750,
        # #     max_timestep=5000,        
        # # ),
        # # # 翻一个跟斗后跳舞
        # # G1BeyondMimicPolicyCfg(
        # #     policy_name="Dance11_wose",           
        # #     start_timestep = 5700,
        # #     max_timestep=6500,        
        # # ),



        # ## test
        # # G1BeyondMimicPolicyCfg(
        # #     policy_name="dance24_wose",
        # #     start_timestep = 3230, 
        # #     max_timestep=3845 ,    #可以再缩短？  会向后退，可能跌倒
        # # ),
        # # G1BeyondMimicPolicyCfg(
        # #     policy_name="dance24_wose",
        # #     start_timestep = 4500,
        # #     max_timestep=5100 ,    
        # # ),

        # # G1BeyondMimicPolicyCfg(
        # #     policy_name="dance24_wose",
        # #     start_timestep = 4500,
        # #     max_timestep=5190,      
        # # ),

        # # G1BeyondMimicPolicyCfg(# 扭扭  7600 
        # #     policy_name="dance24_wose",
        # #     start_timestep = 6800,
        # #     max_timestep= 7510, #7600 ,  # 王厚一点      
        # # ),
        # # G1BeyondMimicPolicyCfg(# BOX
        # #     policy_name="fightSport11wose",
        # #     start_timestep = 3800, 
        # #     max_timestep=4050 ,    
        # # ),
        # # G1BeyondMimicPolicyCfg(# BOX
        # #     policy_name="fightSport11wose",
        # #     start_timestep = 4330, 
        # #     max_timestep=4830,    
        # # ),

        # G1BeyondMimicPolicyCfg(
        #     policy_name="Gangnan_wose",           
        #     start_timestep = 100,
        #     max_timestep=896,        
        # ),
        # # G1BeyondMimicPolicyCfg(
        # #     policy_name="Gangnan_wose",           
        # #     start_timestep = 1000,
        # #     max_timestep=1800,        
        # # ),
        # G1BeyondMimicPolicyCfg(
        #     policy_name="Dance102_sar_wose",           
        #     start_timestep = 0,
        #     max_timestep=640,        
        # ),
        # G1BeyondMimicPolicyCfg(
        #     policy_name="Dance102_sar_wose",           
        #     start_timestep = 900,
        #     max_timestep=1700,        
        # ),
    
    ]

    # Enable safety check for real robot
    do_safety_check: bool = True
