from robojudo.config import cfg_registry
from robojudo.controller.ctrl_cfgs import (
    JoystickCtrlCfg,  # noqa: F401
    KeyboardCtrlCfg,  # noqa: F401
    UnitreeCtrlCfg,  # noqa: F401
    BFMKeyboardCtrlCfg, BFMJoystickCtrlCfg
)
from robojudo.pipeline.pipeline_cfgs import (
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
    Source: /home/hero/Projects/Robotics/Sim2Real/wbc_fsm
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
    policy: G1WbcAmpPolicyCfg = G1WbcAmpPolicyCfg()


@cfg_registry.register
class g1_wbc_loco(RlPipelineCfg):
    """
    G1 robot with WBC_FSM Loco policy (LSTM-based).
    Source: /home/hero/Projects/Robotics/Sim2Real/wbc_fsm
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
    Source: /home/hero/Projects/Robotics/Sim2Real/wbc_fsm
    Note: Requires reference motion binary data for full functionality.
    """
    robot: str = "g1"
    env: G1MujocoEnvCfg = G1MujocoEnvCfg()
    ctrl: list[KeyboardCtrlCfg | JoystickCtrlCfg] = [
        KeyboardCtrlCfg(),
        JoystickCtrlCfg(),
    ]
    policy: G1WbcDancePolicyCfg = G1WbcDancePolicyCfg()
