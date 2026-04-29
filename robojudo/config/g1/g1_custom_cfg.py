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


# ======================== Custom Configs ======================== #
"""
Add your custom config here.
"""

@cfg_registry.register
class g1_gentle(RlPipelineCfg):
    robot: str = "g1"
    env: G1_23MujocoEnvCfg = G1_23MujocoEnvCfg()
    # env: G1MujocoEnvCfg = G1MujocoEnvCfg()
    # env: G1_12MujocoEnvCfg = G1_12MujocoEnvCfg()

    ctrl: list[KeyboardCtrlCfg] = [
        KeyboardCtrlCfg(
            triggers_extra={
                "]": "[MOTION_FADE_OUT]",
                "[": "[MOTION_FADE_IN]",
                ";": "[MOTION_LOAD_NEXT]",
                "'": "[MOTION_LOAD_PREV]",
                "-": "[COMPLIANCE_ON]",
                "=": "[COMPLIANCE_OFF]",
                "Key.up": "[TRESH_UP]",
                "Key.down": "[TRESH_DOWN]",

            }
        )
    ]
    policy: G1GentlePolicyCfg = G1GentlePolicyCfg()

@cfg_registry.register
class g1_locomimic_sim(RlLocoMimicSimPipelineCfg):
    """
    Example of loco mimic pipeline configuration.
    You can switch between loco and mimic policies during runtime, with interpolation.
    === Check more fancy locomimic examples in g1_loco_mimic_cfg.py ===
    """

    robot: str = "g1"
    # env: G1MujocoEnvCfg = G1MujocoEnvCfg()

    env: G1_23MujocoEnvCfg = G1_23MujocoEnvCfg()

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
        G1BeyondmimicCtrlCfg(
            # motion_name="fallAndGetUp3_subject1",  # you can put your own motion file in assets/motions/g1
        ),
        # BFMKeyboardCtrlCfg(),

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


    mimic_policies: list[G1BeyondMimicPolicyCfg] = [
        G1BeyondMimicPolicyCfg(policy_name="23dof_50fps/baicai",),
        G1BeyondMimicPolicyCfg(policy_name="23dof_50fps/slide",),
        G1BeyondMimicPolicyCfg(policy_name="23dof_50fps/go_james",),
        G1BeyondMimicPolicyCfg(policy_name="23dof_50fps/go_woman",),
        G1BeyondMimicPolicyCfg(policy_name="23dof_50fps/OldTownRoad_v1",),

        ##################BeyondMimic Policies######################
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
    # policy: G1BFMZeroTrackingPolicyCfg = G1BFMZeroTrackingPolicyCfg()
    policy: G1BFMZeroTracking23DoFPolicyCfg = G1BFMZeroTracking23DoFPolicyCfg(
        train_method="23dof_260411",
        ctx_path="tracking_inference/zs_18.pkl"
    )


@cfg_registry.register
class g1_bfmzero_reward(RlPipelineCfg):
    """
    Unitree G1 robot with BFM Zero reward policy.
    """

    robot: str = "g1"
    # env: G1MujocoEnvCfg = G1MujocoEnvCfg()
    env: G1_23MujocoEnvCfg = G1_23MujocoEnvCfg()

    ctrl: list[BFMKeyboardCtrlCfg] = [
        BFMKeyboardCtrlCfg(),
    ]
    # policy: G1BFMZeroRewardPolicyCfg = G1BFMZeroRewardPolicyCfg()
    policy: G1BFMZeroReward23DoFPolicyCfg = G1BFMZeroReward23DoFPolicyCfg(
        train_method="23dof_260411"
    )


@cfg_registry.register
class g1_bfmzero_goal(RlPipelineCfg):
    """
    Unitree G1 robot with BFM Zero goal policy.
    """

    robot: str = "g1"
    # env: G1MujocoEnvCfg = G1MujocoEnvCfg()
    env: G1_23MujocoEnvCfg = G1_23MujocoEnvCfg()

    ctrl: list[BFMKeyboardCtrlCfg] = [
        BFMKeyboardCtrlCfg(),
    ]

    # policy: G1BFMZeroGoalPolicyCfg = G1BFMZeroGoalPolicyCfg()
    policy: G1BFMZeroGoal23DoFPolicyCfg = G1BFMZeroGoal23DoFPolicyCfg(
        train_method="23dof_260411"
    )
