from robojudo.config import cfg_registry
from robojudo.controller.ctrl_cfgs import (
    JoystickCtrlCfg,  # noqa: F401
    KeyboardCtrlCfg,  # noqa: F401
    UnitreeCtrlCfg,  # noqa: F401
)
from robojudo.pipeline.pipeline_cfgs import (
    RlLocoMimicPipelineCfg,  # noqa: F401
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

from .env.g1_mujuco_env_cfg import G1MujocoEnvCfg,G1_23MujocoEnvCfg
from .env.g1_real_env_cfg import G1RealEnvCfg, G1UnitreeCfg  # noqa: F401
from .policy.g1_amo_policy_cfg import G1AmoPolicyCfg  # noqa: F401
from .policy.g1_asap_policy_cfg import G1AsapLocoPolicyCfg, G1AsapPolicyCfg  # noqa: F401
from .policy.g1_beyondmimic_policy_cfg import G1BeyondMimicPolicyCfg  # noqa: F401
from .policy.g1_h2h_policy_cfg import G1H2HPolicyCfg  # noqa: F401
from .policy.g1_kungfubot_policy_cfg import G1KungfuBotGeneralPolicyCfg, G1KungfuBotPolicyCfg  # noqa: F401
from .policy.g1_smooth_policy_cfg import G1SmoothPolicyCfg  # noqa: F401
from .policy.g1_twist_policy_cfg import G1TwistPolicyCfg  # noqa: F401
from .policy.g1_unitree_policy_cfg import G1UnitreePolicyCfg, G1UnitreeWoGaitPolicyCfg  # noqa: F401
from .policy.g1_unitree_velocity_policy_cfg import G1UnitreeMjlabVelocityPolicyCfg# G1UnitreeWoGaitVelocityPolicyCfg  # noqa: F401
from .policy.g1_amp_policy_cfg import G1AmpWalkPolicyCfg,G1AmpRunWalkPolicyCfg,G1AmpRecoveryPolicyCfg
from .policy.g1_multimodalwbc_policy_cfg import G1MultiModalWBCPolicyCfg
from .policy.g1_bfmzero_policy_cfg import (
    G1BFMZeroPolicyCfg,
    G1BFMZeroTrackingPolicyCfg,
    G1BFMZeroRewardPolicyCfg,
    G1BFMZeroGoalPolicyCfg,
)
from ...controller.ctrl_cfgs import BFMKeyboardCtrlCfg, BFMJoystickCtrlCfg

@cfg_registry.register
class g1_bfmzero_tracking(RlPipelineCfg):
    """
    Unitree G1 robot with BFM Zero tracking policy using position control.
    """

    robot: str = "g1"
    # env: G1MujocoEnvCfg = G1MujocoEnvCfg()
    env: G1_23MujocoEnvCfg = G1_23MujocoEnvCfg()

    ctrl: list[BFMKeyboardCtrlCfg] = [
        BFMKeyboardCtrlCfg(),
    ]

    policy: G1BFMZeroTrackingPolicyCfg = G1BFMZeroTrackingPolicyCfg()


@cfg_registry.register
class g1_bfmzero_reward(RlPipelineCfg):
    """
    Unitree G1 robot with BFM Zero reward policy.
    """

    robot: str = "g1"
    env: G1MujocoEnvCfg = G1MujocoEnvCfg()
    # env: G1_23MujocoEnvCfg = G1_23MujocoEnvCfg()

    ctrl: list[BFMKeyboardCtrlCfg] = [
        BFMKeyboardCtrlCfg(),
    ]

    policy: G1BFMZeroRewardPolicyCfg = G1BFMZeroRewardPolicyCfg()


@cfg_registry.register
class g1_bfmzero_goal(RlPipelineCfg):
    """
    Unitree G1 robot with BFM Zero goal policy.
    """

    robot: str = "g1"
    env: G1MujocoEnvCfg = G1MujocoEnvCfg()
    # env: G1_23MujocoEnvCfg = G1_23MujocoEnvCfg()

    ctrl: list[BFMKeyboardCtrlCfg] = [
        BFMKeyboardCtrlCfg(),
    ]

    policy: G1BFMZeroGoalPolicyCfg = G1BFMZeroGoalPolicyCfg()


# ======================== Basic Configs ======================== #
@cfg_registry.register
class g1(RlPipelineCfg):
    """
    Unitree G1 robot configuration, Unitree Policy, Sim2Sim.
    You can modify to play with other policies and controllers.
    """

    robot: str = "g1"
    env: G1MujocoEnvCfg = G1MujocoEnvCfg()
    # env: G1_23MujocoEnvCfg = G1_23MujocoEnvCfg()
    # env: G1_12MujocoEnvCfg = G1_12MujocoEnvCfg()

    ctrl: list[JoystickCtrlCfg | KeyboardCtrlCfg] = [  # note: the ranking of controllers matters
        JoystickCtrlCfg(),
        KeyboardCtrlCfg(),
    ]

    # policy: G1UnitreePolicyCfg = G1UnitreePolicyCfg()
    # policy: G1UnitreeWoGaitPolicyCfg = G1UnitreeWoGaitPolicyCfg()
    # policy: G1AmoPolicyCfg = G1AmoPolicyCfg()
    # policy: G1AmpWalkPolicyCfg = G1AmpWalkPolicyCfg()
    # policy: G1AmpRunWalkPolicyCfg = G1AmpRunWalkPolicyCfg()
    policy: G1BFMZeroPolicyCfg = G1BFMZeroPolicyCfg()

    # run_fullspeed: bool = env.is_sim


@cfg_registry.register
class g1_real(g1):
    """
    Unitree G1 robot, Unitree Policy, Sim2Real.
    To extend the sim2sim config to sim2real, just need to change the env to real env.
    """

    # env: G1DummyEnvCfg = G1DummyEnvCfg()
    env: G1RealEnvCfg = G1RealEnvCfg(
        # env_type="UnitreeEnv",  # For unitree_sdk2py
        env_type="UnitreeCppEnv",  # For unitree_cpp, check README for more details
        unitree=G1UnitreeCfg(
            net_if="eth0",  # note: change to your network interface
        ),
    )

    ctrl: list[UnitreeCtrlCfg] = [
        UnitreeCtrlCfg(),
    ]

    do_safety_check: bool = True  # enable safety check for real robot


@cfg_registry.register
class g1_switch(RlMultiPolicyPipelineCfg):
    """
    Example of multi-policy pipeline configuration.
    """

    robot: str = "g1"
    env: G1MujocoEnvCfg = G1MujocoEnvCfg()

    ctrl: list[KeyboardCtrlCfg | JoystickCtrlCfg] = [
        KeyboardCtrlCfg(
            triggers_extra={
                "Key.tab": "[POLICY_TOGGLE]",
            }
        ),
        JoystickCtrlCfg(
            triggers_extra={
                "RB+Down": "[POLICY_SWITCH],0",
                "RB+Up": "[POLICY_SWITCH],1",
            }
        ),
    ]

    policies: list[G1UnitreePolicyCfg | G1AmoPolicyCfg] = [
        G1UnitreePolicyCfg(),
        G1AmoPolicyCfg(),
    ]



@cfg_registry.register
class g1_locomimic(RlLocoMimicPipelineCfg):
    """
    Example of loco mimic pipeline configuration.
    You can switch between loco and mimic policies during runtime, with interpolation.
    === Check more fancy locomimic examples in g1_loco_mimic_cfg.py ===
    """

    robot: str = "g1"
    env: G1MujocoEnvCfg = G1MujocoEnvCfg()

    # env: G1_23MujocoEnvCfg = G1_23MujocoEnvCfg()

    ctrl: list[KeyboardCtrlCfg | JoystickCtrlCfg | G1BeyondmimicCtrlCfg|BFMKeyboardCtrlCfg] = [
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
        G1BeyondmimicCtrlCfg(
            # motion_name="fallAndGetUp3_subject1",  # you can put your own motion file in assets/motions/g1
        ),
        BFMKeyboardCtrlCfg(),

    ]

    loco_policy: G1UnitreeMjlabVelocityPolicyCfg = G1UnitreeMjlabVelocityPolicyCfg()

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


    mimic_policies: list[G1BeyondMimicPolicyCfg|G1AmoPolicyCfg|G1AmpWalkPolicyCfg|G1MultiModalWBCPolicyCfg|G1BFMZeroTrackingPolicyCfg] = [
        # G1AsapPolicyCfg(),
        # G1AmpRunWalkPolicyCfg(),
        # G1AmoPolicyCfg(),
        # G1AmpWalkPolicyCfg(),
        # G1MultiModalWBCPolicyCfg(
        #     policy_name="policy",
        #     without_state_estimator=True,
        #     use_modelmeta_config=False,  # use robot dof config from modelmeta
        #     use_motion_from_model=False,  # use motion from onnx model
        #     max_timestep=5000,
        # ),
        G1BFMZeroTrackingPolicyCfg(),
        ##################BeyondMimic Policies######################
        # 23dof_50fps start####################################
        # # # fightAndSports1_subject1
        # G1BeyondMimicPolicyCfg(# KUNGFU KICK
        #     policy_name="23dof_50fps/fightAndSports1_subject1",
        #     start_timestep = 850,
        #     max_timestep=1300,        
        # ),
        # G1BeyondMimicPolicyCfg(# BOX
        #     policy_name="23dof_50fps/fightAndSports1_subject1",
        #     start_timestep = 3800,
        #     max_timestep=4900,        
        # ),
        # G1BeyondMimicPolicyCfg(# 踢腿
        #     policy_name="23dof_50fps/fightAndSports1_subject1",
        #     start_timestep = 5200,
        #     max_timestep=6300,        
        # ),
        # G1BeyondMimicPolicyCfg(# 
        #     policy_name="23dof_50fps/fightAndSports1_subject1",
        #     start_timestep = 6200,
        #     max_timestep=8390,        
        # ),


        # # fight1_subject2 上钩拳 长序列 双踢腿 ；保龄球；篮球接球传球
        # G1BeyondMimicPolicyCfg( # 1800-2000上钩拳
        #     policy_name="23dof_50fps/fight1_subject2",
        #     start_timestep = 1590,
        #     max_timestep=2000,        
        # ),
        # G1BeyondMimicPolicyCfg( # 5000-5100 双踢腿 
        #     policy_name="23dof_50fps/fight1_subject2",
        #     start_timestep = 4800,
        #     max_timestep=5250,        
        # ),
        # G1BeyondMimicPolicyCfg( # 三连双踢腿 
        #     policy_name="23dof_50fps/fight1_subject2",
        #     start_timestep = 14300,
        #     max_timestep=14900,        
        # ),


        

        # ## dance1_subject1
        # G1BeyondMimicPolicyCfg(
        #     policy_name="23dof_50fps/dance1_subject1",           
        #     start_timestep = 1850,
        #     max_timestep = 3500,
        # ),
        # G1BeyondMimicPolicyCfg(
        #     policy_name="23dof_50fps/dance1_subject1",           
        #     start_timestep = 3750,
        #     max_timestep=5000,        
        # ),
        # # 翻一个跟斗后跳舞
        # G1BeyondMimicPolicyCfg(
        #     policy_name="23dof_50fps/dance1_subject1",           
        #     start_timestep = 5700,
        #     max_timestep=6500,        
        # ),
        
        # # dance1_subject2
        # G1BeyondMimicPolicyCfg(
        #     policy_name="23dof_50fps/dance1_subject2",
        #     start_timestep = 200,
        #     max_timestep=1850,        
        # ),
        # G1BeyondMimicPolicyCfg(
        #     policy_name="23dof_50fps/dance1_subject2",
        #     start_timestep = 1800,
        #     max_timestep=3130,        
        # ),
        # G1BeyondMimicPolicyCfg(
        #     policy_name="23dof_50fps/dance1_subject2",
        #     start_timestep = 3000,
        #     max_timestep=4900,        
        # ),
        # G1BeyondMimicPolicyCfg(
        #     policy_name="23dof_50fps/dance1_subject2",
        #     start_timestep = 4900,
        #     max_timestep=6700,        
        # ),

        # ## dance1_subject3 
        # ##共6500 没有舞蹈感觉 需要29的手腕关节，否则前2000看不出来在跳舞
        # # 单脚跳 

        # # G1BeyondMimicPolicyCfg(
        # #     policy_name="23dof_50fps/dance1_subject3",
        # #     start_timestep = 100,
        # #     max_timestep=-1,        
        # # ),


        # # dance2_subject1 
        # # 转圈 后仰抖肩 单脚跳舞 空中转圈 第一次失败了

        # G1BeyondMimicPolicyCfg(# 甩脚舞
        #     policy_name="23dof_50fps/dance2_subject1",
        #     start_timestep = 1800,
        #     max_timestep=2800,        
        # ),
        # G1BeyondMimicPolicyCfg(# 抖肩
        #     policy_name="23dof_50fps/dance2_subject1",
        #     start_timestep = 2800,
        #     max_timestep=3335,        
        # ),
        # G1BeyondMimicPolicyCfg(# 双手渐进抬手
        #     policy_name="23dof_50fps/dance2_subject1",
        #     start_timestep = 3300,
        #     max_timestep=4260,        
        # ),
        # G1BeyondMimicPolicyCfg(# 转圈 低重心有难
        #     policy_name="23dof_50fps/dance2_subject1",
        #     start_timestep = 4260,
        #     max_timestep=6300,        
        # ),
        # G1BeyondMimicPolicyCfg(# 上下摆手转圈后倾斜搓碟
        #     policy_name="23dof_50fps/dance2_subject1",
        #     start_timestep = 6300,
        #     max_timestep=7600,        
        # ),
        # G1BeyondMimicPolicyCfg( # 单脚小跳 后仰倒退 后仰摇手
        #     policy_name="23dof_50fps/dance2_subject1",
        #     start_timestep = 7600,
        #     max_timestep=9630,        
        # ),

        # # ## dance2_subject4
        # # G1BeyondMimicPolicyCfg(
        # #     policy_name="23dof_50fps/dance2_subject4",
        # #     start_timestep = 1500,
        # #     max_timestep=2900,        
        # # ),
        
        # # G1BeyondMimicPolicyCfg(
        # #     policy_name="23dof_50fps/dance2_subject4",
        # #     start_timestep = 3100,
        # #     max_timestep=4500,        
        # # ),
        # # G1BeyondMimicPolicyCfg(
        # #     policy_name="23dof_50fps/dance2_subject4",
        # #     start_timestep = 4500,
        # #     max_timestep=5130 ,    
        # # ),
        # # G1BeyondMimicPolicyCfg(# 遮眼舞蹈
        # #     policy_name="23dof_50fps/dance2_subject4",
        # #     start_timestep = 4500,
        # #     max_timestep=6900,        
        # # ),
        # # G1BeyondMimicPolicyCfg(# 扭扭
        # #     policy_name="23dof_50fps/dance2_subject4",
        # #     start_timestep = 7500,
        # #     max_timestep= 8760,  # 7595 
        # # ),



        # # 23dof_50fps end ####################################

        # # 23dof_65fps start ####################################

        # G1BeyondMimicPolicyCfg(
        #     policy_name="23dof_65fps/Take102",           
        #     start_timestep = 100,
        #     max_timestep=1800,        
        # ),
        # G1BeyondMimicPolicyCfg( # swing
        #     policy_name="23dof_65fps/dance2_subject4",
        #     start_timestep = 8800,
        #     max_timestep=10100,       
        # ),
        # G1BeyondMimicPolicyCfg(
        #     policy_name="23dof_65fps/GangnamStyle",           
        #     start_timestep = 300,
        #     max_timestep=2000,        
        # ),
        # G1BeyondMimicPolicyCfg( 
        #     policy_name="23dof_65fps/dance2_subject4",
        #     start_timestep = 9000,
        #     max_timestep=10600,       
        # ),
        # G1BeyondMimicPolicyCfg( # 1
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
        # G1BeyondMimicPolicyCfg(# 3
        #     policy_name="23dof_65fps/dance2_subject4",
        #     start_timestep = 6000,
        #     max_timestep=7400,   # 6720     
        # ),

        # 23dof_65fps end ####################################
   
        ]



@cfg_registry.register
class g1_unitree_velocity(RlPipelineCfg):
    """
    Unitree Velocity policy from unitree_rl_mjlab.
    
    Uses WoGait policy for velocity control where the robot remains static
    when velocity commands are zero, matching the unitree_rl_mjlab behavior.
    
    Features:
    - WoGait policy for static standing
    - Original unitree_rl_mjlab velocity control
    - Keyboard-based velocity commands (WASD+QE)
    - Training configuration compatibility
    
    Controls:
    - Keyboard: WASD for movement, QE for rotation
    - Joystick: Standard dual-stick control
    """

    robot: str = "g1"
    env: G1MujocoEnvCfg = G1MujocoEnvCfg()

    ctrl: list[KeyboardCtrlCfg | JoystickCtrlCfg] = [
        KeyboardCtrlCfg(
            triggers_extra={
                # Velocity control keys (unitree_rl_mjlab style)
                "w": "[VELOCITY_FORWARD]",
                "s": "[VELOCITY_BACKWARD]", 
                "a": "[VELOCITY_LEFT]",
                "d": "[VELOCITY_RIGHT]",
                "q": "[VELOCITY_TURN_LEFT]",
                "e": "[VELOCITY_TURN_RIGHT]",
            }
        ),
        JoystickCtrlCfg(
            triggers_extra={
                "RB+Down": "[POLICY_TOGGLE]",
                "RB+Up": "[POLICY_TOGGLE]",
            }
        ),
    ]
    
    # Use the Unitree Velocity MJLab policy
    policy: G1UnitreeMjlabVelocityPolicyCfg = G1UnitreeMjlabVelocityPolicyCfg()
    # Alternative: Use standard Unitree policy for comparison
    # loco_policy: G1UnitreePolicyCfg = G1UnitreePolicyCfg()
    # loco_policy: G1AsapLocoPolicyCfg = G1AsapLocoPolicyCfg()

    # Keep the same mimic policies as the original g1_locomimic
    # mimic_policies: list[G1BeyondMimicPolicyCfg|G1AmoPolicyCfg] = [
    #     # G1AsapPolicyCfg(),
    #     G1AmoPolicyCfg(),
    #     G1BeyondMimicPolicyCfg(
    #     policy_name="Gangnan_wose_stable",
    #     without_state_estimator=True,
    #     use_modelmeta_config=True,  # use robot dof config from modelmeta
    #     use_motion_from_model=True,  # use motion from onnx model
    #     max_timestep=1500,
    #     ),
    #     G1BeyondMimicPolicyCfg(
    #     policy_name="Gangnan_wose_robust",
    #     without_state_estimator=True,
    #     use_modelmeta_config=True,  # use robot dof config from modelmeta
    #     use_motion_from_model=True,  # use motion from onnx model
    #     max_timestep=1500,
    #     ),
    #     G1BeyondMimicPolicyCfg(
    #     policy_name="Gangnan_wose_bias",
    #     without_state_estimator=True,
    #     use_modelmeta_config=True,  # use robot dof config from modelmeta
    #     use_motion_from_model=True,  # use motion from onnx model
    #     max_timestep=1500,
    #     ),
    #     G1BeyondMimicPolicyCfg(
    #     policy_name="Gangnan_wose",
    #     without_state_estimator=True,
    #     use_modelmeta_config=True,  # use robot dof config from modelmeta
    #     use_motion_from_model=True,  # use motion from onnx model
    #     max_timestep=1500,
    #     ),

    # ]


# ======================== Configs for supported Policy ======================== #


@cfg_registry.register
class g1_h2h(RlPipelineCfg):
    """
    Human2Humanoid
    """

    robot: str = "g1"
    env: G1MujocoEnvCfg = G1MujocoEnvCfg()
    ctrl: list[KeyboardCtrlCfg | G1MotionH2HCtrlCfg] = [
        KeyboardCtrlCfg(),
        G1MotionH2HCtrlCfg(),
    ]

    policy: G1H2HPolicyCfg = G1H2HPolicyCfg()


@cfg_registry.register
class g1_beyondmimic(RlPipelineCfg):
    """
    BeyondMimic Policy, support both with and without state estimator.
    """

    robot: str = "g1"
    env: G1MujocoEnvCfg = G1MujocoEnvCfg()
    ctrl: list[KeyboardCtrlCfg] = [
        KeyboardCtrlCfg(),
    ]

    policy: G1BeyondMimicPolicyCfg = G1BeyondMimicPolicyCfg(
        policy_name="Jump_wose",
        without_state_estimator=True,
        use_modelmeta_config=True,  # use robot dof config from modelmeta
        use_motion_from_model=True,  # use motion from onnx model
        max_timestep=140,
    )


@cfg_registry.register
class g1_beyondmimic_with_ctrl(RlPipelineCfg):
    """
    BeyondMimic with External BeyondMimicCtrl as motion source.
    """

    robot: str = "g1"
    env: G1MujocoEnvCfg = G1MujocoEnvCfg()
    ctrl: list[KeyboardCtrlCfg | G1BeyondmimicCtrlCfg] = [
        KeyboardCtrlCfg(),
        G1BeyondmimicCtrlCfg(
            motion_name="dance1_subject2",  # you can put your own motion file in assets/motions/g1
        ),
    ]

    policy: G1BeyondMimicPolicyCfg = G1BeyondMimicPolicyCfg(
        policy_name="Dance_wose",
        # policy_name="Jump_wose",
        use_motion_from_model=False,  # use motion from BeyondmimicCtrl instead of the onnx
    )


@cfg_registry.register
class g1_asap(RlPipelineCfg):
    """
    Unitree G1 robot configuration, ASAP Policy, Sim2Sim.
    You can modify to play with other policies and controllers.
    """

    robot: str = "g1"
    env: G1MujocoEnvCfg = G1MujocoEnvCfg(forward_kinematic=None, update_with_fk=False, born_place_align=True)

    ctrl: list[JoystickCtrlCfg | KeyboardCtrlCfg] = [  # note: the ranking of controllers matters
        # JoystickCtrlCfg(),
        KeyboardCtrlCfg(triggers={"i": "[SIM_REBORN]", "o": "[SHUTDOWN]", "r": "[MOTION_RESET]"}),
    ]

    policy: G1AsapPolicyCfg = G1AsapPolicyCfg()
    """You can also try other models, from ASAP, RoboMimic, KungfuBot(PBHC)"""
    # policy: G1KungfuBotPolicyCfg = G1KungfuBotPolicyCfg() # KungfuBot horse_squat
    # # fmt: off
    # policy: G1AsapPolicyCfg = G1AsapPolicyCfg(
    #     policy_name="robomimic",
    #     relative_path="dance_0605.onnx",
    #     motion_length_s=18.0,
    #     start_upper_body_dof_pos = [
    #         0, 0, 0,
    #         0.35, 0.18, 0, 0.87,
    #         0.35, -0.18, 0, 0.87,
    #     ],
    # )
    # # fmt: on


@cfg_registry.register
class g1_asap_loco(RlPipelineCfg):
    """
    Unitree G1 robot configuration, ASAP Locomotion Policy, Sim2Sim.
    You can modify to play with other policies and controllers.
    """

    robot: str = "g1"
    env: G1MujocoEnvCfg = G1MujocoEnvCfg(forward_kinematic=None, update_with_fk=False, born_place_align=False)

    ctrl: list[JoystickCtrlCfg | KeyboardCtrlCfg] = [  # note: the ranking of controllers matters
        # JoystickCtrlCfg(),
        KeyboardCtrlCfg(
            triggers={
                "i": "[SIM_REBORN]",
                "o": "[SHUTDOWN]",
            }
        ),
    ]

    policy: G1AsapLocoPolicyCfg = G1AsapLocoPolicyCfg()


@cfg_registry.register
class g1_kungfubot2(RlPipelineCfg):
    """
    PBHC KungfuBot2 General Policy
    """

    robot: str = "g1"
    env: G1MujocoEnvCfg = G1MujocoEnvCfg()
    ctrl: list[KeyboardCtrlCfg | G1MotionKungfuBotCtrlCfg] = [
        KeyboardCtrlCfg(),
        G1MotionKungfuBotCtrlCfg(
            motion_name="kungfubot/Horse-stance_pose",  # put motion files in assets/motions/g1/phc/kungfubot
        ),
    ]

    policy: G1KungfuBotGeneralPolicyCfg = G1KungfuBotGeneralPolicyCfg(
        policy_name="horse_test_43000",  # this is a test model trained with only one motion
        compatibility_old_version=True,  # for old version of kungfubot general policy (before 2025-11-13 bugfix #68)
    )


@cfg_registry.register
class g1_twist(RlPipelineCfg):
    """
    Unitree G1 robot configuration, TWIST Policy, Sim2Sim.
    TwistRedisCtrl for the original repo of high level motion stream over redis.
    MotionTwistCtrl for built-in motion control.
    """

    robot: str = "g1"
    env: G1MujocoEnvCfg = G1MujocoEnvCfg(forward_kinematic=None, update_with_fk=False, born_place_align=False)

    ctrl: list[G1TwistRedisCtrlCfg | G1MotionTwistCtrlCfg] = [  # note: the ranking of controllers matters
        G1TwistRedisCtrlCfg(redis_host="localhost"),  # with hign level motion lib through redis
        # G1MotionTwistCtrlCfg(), # with built-in motion ctrl
    ]

    policy: G1TwistPolicyCfg = G1TwistPolicyCfg()


# ======================== Fancy Example Configs ======================== #


@cfg_registry.register
class g1_switch_beyondmimic(RlMultiPolicyPipelineCfg):
    """
    Switch between multiple BeyondMimic policies. Withour Interpolation.
    """

    robot: str = "g1"
    env: G1MujocoEnvCfg = G1MujocoEnvCfg()
    ctrl: list[KeyboardCtrlCfg | JoystickCtrlCfg] = [
        KeyboardCtrlCfg(
            triggers_extra={
                "Key.tab": "[POLICY_TOGGLE]",
                "!": "[POLICY_SWITCH],0",  # note: with shift
                "@": "[POLICY_SWITCH],1",  # note: with shift
                "#": "[POLICY_SWITCH],2",  # note: with shift
                "$": "[POLICY_SWITCH],3",  # note: with shift
            }
        ),
        JoystickCtrlCfg(
            triggers_extra={
                "RB+Down": "[POLICY_SWITCH],0",
                "RB+Left": "[POLICY_SWITCH],1",
                "RB+Up": "[POLICY_SWITCH],2",
                "RB+Right": "[POLICY_SWITCH],3",
            }
        ),
    ]

    policies: list[G1AmoPolicyCfg | G1BeyondMimicPolicyCfg] = [
        G1AmoPolicyCfg(),
        G1BeyondMimicPolicyCfg(policy_name="Violin", without_state_estimator=False, max_timestep=500),
        G1BeyondMimicPolicyCfg(policy_name="Waltz", without_state_estimator=False, max_timestep=850),
        G1BeyondMimicPolicyCfg(policy_name="Dance_wose", without_state_estimator=True),
    ]


# TIPS: check g1_loco_mimic_cfg.py for more complex examples
