from robojudo.config import cfg_registry
from robojudo.controller.ctrl_cfgs import (
    JoystickCtrlCfg,  # noqa: F401
    KeyboardCtrlCfg,  # noqa: F401
    UnitreeCtrlCfg,  # noqa: F401
    BFMKeyboardCtrlCfg,  # noqa: F401
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
from .policy.g1_amp_policy_cfg import G1AmpWalkPolicyCfg
from .policy.g1_bfmzero_policy_cfg import (  # noqa: F401
    G1BFMZeroTracking23DoFPolicyCfg,
    G1BFMZeroReward23DoFPolicyCfg,
    G1BFMZeroGoal23DoFPolicyCfg,
)
from .policy.g1_gentle_policy_cfg import G1GentlePolicyCfg  # noqa: F401
from .policy.g1_kungfuathlete_policy_cfg import G1KungFuAthletePolicyCfg  # noqa: F401
from .policy.g1_wbc_amp_policy_cfg import G1WbcAmpPolicyCfg  # noqa: F401
from .policy.g1_wbc_dance_policy_cfg import G1WbcDancePolicyCfg  # noqa: F401


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
        # JoystickCtrlCfg(),
        KeyboardCtrlCfg(),
    ]

    policy: G1UnitreePolicyCfg = G1UnitreePolicyCfg()
    # policy: G1UnitreeWoGaitPolicyCfg = G1UnitreeWoGaitPolicyCfg()
    # policy: G1AmoPolicyCfg = G1AmoPolicyCfg()

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

    ctrl: list[UnitreeCtrlCfg | KeyboardCtrlCfg] = [
        KeyboardCtrlCfg(ctrl_type="KeyboardStdinCtrl"),  # SSH 键盘控制（通过 stdin）
        UnitreeCtrlCfg(),   # Unitree 手柄控制
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
        # KeyboardCtrlCfg(
        #     triggers_extra={
        #         "Key.tab": "[POLICY_TOGGLE]",
        #     }
        # ),
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


# # ======================== Configs for supported Policy ======================== #


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
        # policy_name="Jump_wose",
        # policy_name = "Dance_wose" , # 舞蹈
        policy_name = "Violin"   ,   # 拉小提琴
        # policy_name = "Waltz"    ,   # 华尔兹
        without_state_estimator=False,  # Violin is SE version
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
        policy_name="29dof/Dance_wose",
        use_motion_from_model=False,  # use motion from BeyondmimicCtrl instead of the onnx
    )


@cfg_registry.register
class g1_beyondmimic_real(RlPipelineCfg):
    """
    BeyondMimic Policy on Real G1 Robot.
    Deploy BeyondMimic motion tracking on real hardware.
    
    Usage:
        python scripts/run_pipeline.py -c g1_beyondmimic_real
    
    Controls:
        - ESC: Emergency stop (enter damping mode)
        - Shift + <: Start/resume motion playback
        - Shift + >: Pause motion playback
        - Shift + |: Reset motion progress
    
    Available motions (change policy_name):
        - "Jump_wose": Jumping motion
        - "Dance_wose": Dancing motion
        - "Violin": Violin playing motion
        - "Waltz": Waltz dancing motion
    """

    robot: str = "g1"
    
    # Real robot environment
    env: G1RealEnvCfg = G1RealEnvCfg(
        env_type="UnitreeCppEnv",  # For unitree_cpp
        unitree=G1UnitreeCfg(
            net_if="eth0",  # note: change to your network interface
        ),
    )

    # Keyboard control for motion playback (SSH stdin, works over SSH)
    ctrl: list[KeyboardCtrlCfg] = [
        KeyboardCtrlCfg(ctrl_type="KeyboardStdinCtrl"),
    ]

    # BeyondMimic policy configuration
    policy: G1BeyondMimicPolicyCfg = G1BeyondMimicPolicyCfg(
        # Choose one motion (wose = without state estimator):
        # policy_name="Jump_wose",      # Jumping (default, safer for testing)
        policy_name="Dance_wose",   # Dancing
        
        without_state_estimator=True,  # WOSE version (matches Jump_wose, Dance_wose)
        use_modelmeta_config=True,
        use_motion_from_model=True,
        max_timestep=140,  # Motion duration (adjust based on motion)
    )

    # Enable safety check for real robot
    do_safety_check: bool = True


@cfg_registry.register
class g1_real_locomimic(RlLocoMimicPipelineCfg):
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
        *[0.35,0.18,0.,0.87,0.,0.,0.],
        *[0.35,-0.18,0.,0.87,0.,0.,0.]
    ]

    # Standing pose configuration
    standing_pos: list[float] = [
        *[-0.1, 0.0, 0.0, 0.3, -0.2, 0.0],  # 左腿
        *[-0.1, 0.0, 0.0, 0.3, -0.2, 0.0],  # 右腿
        *[0, 0, 0],  # 腰部
        *[0.35,0.18,0.,0.87,0.,0.,0.],
        *[0.35,-0.18,0.,0.87,0.,0.,0.]
    ]

    # Keyboard and controller with policy switching
    ctrl: list[UnitreeCtrlCfg] = [
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

    loco_policy: G1UnitreeMjlabVelocityPolicyCfg = G1UnitreeMjlabVelocityPolicyCfg()


    '''
        policies: list[G1UnitreePolicyCfg | G1AmoPolicyCfg] = [
        G1UnitreePolicyCfg(),
        G1AmoPolicyCfg(),
    ]

    '''
    mimic_policies: list[G1BeyondMimicPolicyCfg | G1AmoPolicyCfg|G1AmpWalkPolicyCfg] = [
        # v260625 
        G1WbcDancePolicyCfg(),#1 
        G1BeyondMimicPolicyCfg(policy_name="23dof_50fps/go_woman",), # 2
        G1BeyondMimicPolicyCfg(policy_name="23dof_50fps/fightAndSports1_subject4", # 3踢腿两次后转身踢腿一次
            # start_timestep = 100, # 可以
            start_timestep = 2500,
            max_timestep=2850,       
                               ),
        G1BeyondMimicPolicyCfg(# 旋转踢腿 前方预留5米以上 4
            policy_name="23dof_50fps/fightAndSports1_subject1",
            start_timestep = 5200,
            max_timestep=6300,        
        ),
    ]

    # Enable safety check for real robot
    do_safety_check: bool = False


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


@cfg_registry.register
class g1_gentle(RlPipelineCfg):
    robot: str = "g1"
    env: G1_23MujocoEnvCfg = G1_23MujocoEnvCfg()

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
class g1_bfmzero_tracking(RlPipelineCfg):
    robot: str = "g1"
    env: G1_23MujocoEnvCfg = G1_23MujocoEnvCfg()

    ctrl: list[BFMKeyboardCtrlCfg] = [
        BFMKeyboardCtrlCfg(),
    ]
    policy: G1BFMZeroTracking23DoFPolicyCfg = G1BFMZeroTracking23DoFPolicyCfg(
        train_method="23dof_260411",
        ctx_path="tracking_inference/zs_18.pkl"
    )


@cfg_registry.register
class g1_bfmzero_reward(RlPipelineCfg):
    robot: str = "g1"
    env: G1_23MujocoEnvCfg = G1_23MujocoEnvCfg()

    ctrl: list[BFMKeyboardCtrlCfg] = [
        BFMKeyboardCtrlCfg(),
    ]
    policy: G1BFMZeroReward23DoFPolicyCfg = G1BFMZeroReward23DoFPolicyCfg(
        train_method="23dof_260411"
    )


@cfg_registry.register
class g1_bfmzero_goal(RlPipelineCfg):
    robot: str = "g1"
    env: G1_23MujocoEnvCfg = G1_23MujocoEnvCfg()

    ctrl: list[BFMKeyboardCtrlCfg] = [
        BFMKeyboardCtrlCfg(),
    ]
    policy: G1BFMZeroGoal23DoFPolicyCfg = G1BFMZeroGoal23DoFPolicyCfg(
        train_method="23dof_260411"
    )


@cfg_registry.register
class g1_kungfuathlete(RlPipelineCfg):
    robot: str = "g1"
    env: G1MujocoEnvCfg = G1MujocoEnvCfg()

    ctrl: list[KeyboardCtrlCfg | G1BeyondmimicCtrlCfg] = [
        KeyboardCtrlCfg(
            triggers_extra={
                "]": "[MOTION_FADE_OUT]",
                "[": "[MOTION_FADE_IN]",
                ";": "[MOTION_LOAD_NEXT]",
                "'": "[MOTION_LOAD_PREV]",
            }
        ),
        G1BeyondmimicCtrlCfg(
            motion_subdir="KungFuAthlete",
            motion_name="1307",
        ),
    ]

    policy: G1KungFuAthletePolicyCfg = G1KungFuAthletePolicyCfg(
        policy_name="1307Taichi",
        use_onnx=True,
    )


# ======================== Custom Multi-Policy Examples ======================== #


@cfg_registry.register
class g1_unitree_mjlab_velocity(RlPipelineCfg):
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
    mimic_policies: list[G1BeyondMimicPolicyCfg|G1AmoPolicyCfg] = [
        # G1AsapPolicyCfg(),
        G1AmoPolicyCfg(),
        G1BeyondMimicPolicyCfg(
        policy_name="Gangnan_wose_stable",
        without_state_estimator=True,
        use_modelmeta_config=True,  # use robot dof config from modelmeta
        use_motion_from_model=True,  # use motion from onnx model
        max_timestep=1500,
        ),
        G1BeyondMimicPolicyCfg(
        policy_name="Gangnan_wose_robust",
        without_state_estimator=True,
        use_modelmeta_config=True,  # use robot dof config from modelmeta
        use_motion_from_model=True,  # use motion from onnx model
        max_timestep=1500,
        ),
        G1BeyondMimicPolicyCfg(
        policy_name="Gangnan_wose_bias",
        without_state_estimator=True,
        use_modelmeta_config=True,  # use robot dof config from modelmeta
        use_motion_from_model=True,  # use motion from onnx model
        max_timestep=1500,
        ),
        G1BeyondMimicPolicyCfg(
        policy_name="Gangnan_wose",
        without_state_estimator=True,
        use_modelmeta_config=True,  # use robot dof config from modelmeta
        use_motion_from_model=True,  # use motion from onnx model
        max_timestep=1500,
        ),

    ]


@cfg_registry.register
class g1_amp(RlPipelineCfg):
    """
    Unitree G1 robot configuration, AMP Walk Policy, Sim2Sim.
    
    Uses GmrAmp policy for AMP-based walking with velocity control.
    
    Features:
    - AMP-based walking policy
    - Keyboard-based velocity commands (WASD+QE)
    - Training configuration compatibility
    
    Controls:
    - Keyboard: WASD for movement, QE for rotation
    """

    robot: str = "g1"
    env: G1MujocoEnvCfg = G1MujocoEnvCfg()

    ctrl: list[KeyboardCtrlCfg | JoystickCtrlCfg] = [
        KeyboardCtrlCfg(
            triggers_extra={
                "w": "[VELOCITY_FORWARD]",
                "s": "[VELOCITY_BACKWARD]", 
                "a": "[VELOCITY_LEFT]",
                "d": "[VELOCITY_RIGHT]",
                "q": "[VELOCITY_TURN_LEFT]",
                "e": "[VELOCITY_TURN_RIGHT]",
            }
        ),
        JoystickCtrlCfg(),
    ]

    policy: G1AmpWalkPolicyCfg = G1AmpWalkPolicyCfg()


# ======================== Real Robot Configs for New Policies ======================== #


@cfg_registry.register
class g1_bfmzero_tracking_real(RlPipelineCfg):
    """
    BFMZero Tracking Policy on Real G1 Robot.

    ⚠️ Warning: BFMZero has NOT been validated on real hardware.
    Use at your own risk. Ensure safety measures are in place.

    Usage:
        python scripts/run_pipeline.py -c g1_bfmzero_tracking_real

    BFMZero tracking mode: follows reference motions using diffusion-based policy.

    Controls (Unitree Controller):
        - L1+R1+L2 (hold): Enter command mode
        - A: Emergency stop (SHUTDOWN)
        - B: Zero actions (safety stop, BFM_ACTIONS_ZERO)
        - X: Start motion (BFM_MOTION_START)
        - Y: Reset policy state (MOTION_RESET)
        - Right: Next motion (BFM_NEXT)
        - Left: Previous motion (BFM_LAST)

    Controls (SSH Keyboard):
        - `-`: Start motion (BFM_MOTION_START)
        - `n`: Next motion (BFM_NEXT)
        - `m`: Last motion (BFM_LAST)
        - `p`: Reset stop state (BFM_RESET_STOP_STATE)
        - `o`: Zero actions (BFM_ACTIONS_ZERO)
        - `|`: Reset policy state (MOTION_RESET)
        - Esc: Emergency stop (SHUTDOWN)
    """

    robot: str = "g1"

    env: G1RealEnvCfg = G1RealEnvCfg(
        env_type="UnitreeCppEnv",
        unitree=G1UnitreeCfg(net_if="eth0"),
    )

    ctrl: list[KeyboardCtrlCfg | UnitreeCtrlCfg] = [
        KeyboardCtrlCfg(
            ctrl_type="KeyboardStdinCtrl",
            triggers_extra={
                "-": "[BFM_MOTION_START]",
                "n": "[BFM_NEXT]",
                "m": "[BFM_LAST]",
                "p": "[BFM_RESET_STOP_STATE]",
                "o": "[BFM_ACTIONS_ZERO]",
                "|": "[MOTION_RESET]",
            }
        ),
        UnitreeCtrlCfg(
            combination_init_buttons=["L1", "R1", "L2"],
            triggers_extra={
                "A": "[SHUTDOWN]",
                "B": "[BFM_ACTIONS_ZERO]",
                "X": "[BFM_MOTION_START]",
                "Y": "[MOTION_RESET]",
                "Right": "[BFM_NEXT]",
                "Left": "[BFM_LAST]",
            }
        ),
    ]

    policy: G1BFMZeroTracking23DoFPolicyCfg = G1BFMZeroTracking23DoFPolicyCfg(
        train_method="23dof_260411",
        ctx_path="tracking_inference/zs_18.pkl"
    )

    do_safety_check: bool = True


@cfg_registry.register
class g1_bfmzero_reward_real(RlPipelineCfg):
    """
    BFMZero Reward Policy on Real G1 Robot.

    ⚠️ Warning: BFMZero has NOT been validated on real hardware.
    Use at your own risk. Ensure safety measures are in place.

    Usage:
        python scripts/run_pipeline.py -c g1_bfmzero_reward_real

    BFMZero reward mode: learns reward-conditioned motions.

    Controls (Unitree Controller):
        - L1+R1+L2 (hold): Enter command mode
        - A: Emergency stop (SHUTDOWN)
        - B: Zero actions (safety stop, BFM_ACTIONS_ZERO)
        - X: Start motion (BFM_MOTION_START)
        - Y: Reset policy state (MOTION_RESET)
        - Right: Next reward (BFM_NEXT)
        - Left: Previous reward (BFM_LAST)

    Controls (SSH Keyboard):
        - `-`: Start motion (BFM_MOTION_START)
        - `n`: Next reward (BFM_NEXT)
        - `m`: Last reward (BFM_LAST)
        - `p`: Reset stop state (BFM_RESET_STOP_STATE)
        - `o`: Zero actions (BFM_ACTIONS_ZERO)
        - `|`: Reset policy state (MOTION_RESET)
        - Esc: Emergency stop (SHUTDOWN)
    """

    robot: str = "g1"

    env: G1RealEnvCfg = G1RealEnvCfg(
        env_type="UnitreeCppEnv",
        unitree=G1UnitreeCfg(net_if="eth0"),
    )

    ctrl: list[KeyboardCtrlCfg | UnitreeCtrlCfg] = [
        KeyboardCtrlCfg(
            ctrl_type="KeyboardStdinCtrl",
            triggers_extra={
                "-": "[BFM_MOTION_START]",
                "n": "[BFM_NEXT]",
                "m": "[BFM_LAST]",
                "p": "[BFM_RESET_STOP_STATE]",
                "o": "[BFM_ACTIONS_ZERO]",
                "|": "[MOTION_RESET]",
            }
        ),
        UnitreeCtrlCfg(
            combination_init_buttons=["L1", "R1", "L2"],
            triggers_extra={
                "A": "[SHUTDOWN]",
                "B": "[BFM_ACTIONS_ZERO]",
                "X": "[BFM_MOTION_START]",
                "Y": "[MOTION_RESET]",
                "Right": "[BFM_NEXT]",
                "Left": "[BFM_LAST]",
            }
        ),
    ]

    policy: G1BFMZeroReward23DoFPolicyCfg = G1BFMZeroReward23DoFPolicyCfg(
        train_method="23dof_260411"
    )

    do_safety_check: bool = True


@cfg_registry.register
class g1_bfmzero_goal_real(RlPipelineCfg):
    """
    BFMZero Goal Policy on Real G1 Robot.

    ⚠️ Warning: BFMZero has NOT been validated on real hardware.
    Use at your own risk. Ensure safety measures are in place.

    Usage:
        python scripts/run_pipeline.py -c g1_bfmzero_goal_real

    BFMZero goal mode: follows goal-conditioned motions (e.g. walking, squat).

    Controls (Unitree Controller):
        - L1+R1+L2 (hold): Enter command mode
        - A: Emergency stop (SHUTDOWN)
        - B: Zero actions (safety stop, BFM_ACTIONS_ZERO)
        - X: Start motion (BFM_MOTION_START)
        - Y: Reset policy state (MOTION_RESET)
        - Right: Next goal (BFM_NEXT)
        - Left: Previous goal (BFM_LAST)

    Controls (SSH Keyboard):
        - `-`: Start motion (BFM_MOTION_START)
        - `n`: Next goal (BFM_NEXT)
        - `m`: Last goal (BFM_LAST)
        - `p`: Reset stop state (BFM_RESET_STOP_STATE)
        - `o`: Zero actions (BFM_ACTIONS_ZERO)
        - `|`: Reset policy state (MOTION_RESET)
        - Esc: Emergency stop (SHUTDOWN)
    """

    robot: str = "g1"

    env: G1RealEnvCfg = G1RealEnvCfg(
        env_type="UnitreeCppEnv",
        unitree=G1UnitreeCfg(net_if="eth0"),
    )

    ctrl: list[KeyboardCtrlCfg | UnitreeCtrlCfg] = [
        KeyboardCtrlCfg(
            ctrl_type="KeyboardStdinCtrl",
            triggers_extra={
                "-": "[BFM_MOTION_START]",
                "n": "[BFM_NEXT]",
                "m": "[BFM_LAST]",
                "p": "[BFM_RESET_STOP_STATE]",
                "o": "[BFM_ACTIONS_ZERO]",
                "|": "[MOTION_RESET]",
            }
        ),
        UnitreeCtrlCfg(
            combination_init_buttons=["L1", "R1", "L2"],
            triggers_extra={
                "A": "[SHUTDOWN]",
                "B": "[BFM_ACTIONS_ZERO]",
                "X": "[BFM_MOTION_START]",
                "Y": "[MOTION_RESET]",
                "Right": "[BFM_NEXT]",
                "Left": "[BFM_LAST]",
            }
        ),
    ]

    policy: G1BFMZeroGoal23DoFPolicyCfg = G1BFMZeroGoal23DoFPolicyCfg(
        train_method="23dof_260411"
    )

    do_safety_check: bool = True


@cfg_registry.register
class g1_kungfuathlete_real(RlPipelineCfg):
    """
    KungFuAthlete Policy on Real G1 Robot.

    ⚠️ Warning: KungFuAthlete has NOT been validated on real hardware.
    Use at your own risk. Ensure safety measures are in place.

    Usage:
        python scripts/run_pipeline.py -c g1_kungfuathlete_real

    Motion tracking for martial arts motions (Tai Chi, fist, saber, acrobatics)
    with fall recovery.

    Controls (Unitree Controller):
        - L1+R1 (hold): Enter command mode
        - A: Emergency stop (SHUTDOWN)
        - X: Start/resume motion (MOTION_FADE_IN)
        - B: Pause motion (MOTION_FADE_OUT)
        - Y: Reset motion progress (MOTION_RESET)
        - Up: Load next motion (MOTION_LOAD_NEXT)
        - Down: Load previous motion (MOTION_LOAD_PREV)

    Controls (SSH Keyboard):
        - Shift + `<`: Fade in motion
        - Shift + `>`: Fade out motion
        - Shift + `|`: Reset motion
        - Shift + `{`: Previous motion
        - Shift + `}`: Next motion
        - Esc: Emergency stop
    """

    robot: str = "g1"

    env: G1RealEnvCfg = G1RealEnvCfg(
        env_type="UnitreeCppEnv",
        unitree=G1UnitreeCfg(net_if="eth0"),
    )

    ctrl: list[KeyboardCtrlCfg | UnitreeCtrlCfg | G1BeyondmimicCtrlCfg] = [
        KeyboardCtrlCfg(
            ctrl_type="KeyboardStdinCtrl",
            triggers_extra={
                ">": "[MOTION_FADE_OUT]",
                "<": "[MOTION_FADE_IN]",
                "|": "[MOTION_RESET]",
                "}": "[MOTION_LOAD_NEXT]",
                "{": "[MOTION_LOAD_PREV]",
            }
        ),
        UnitreeCtrlCfg(
            combination_init_buttons=["L1", "R1", "L2"],
            triggers_extra={
                "A": "[SHUTDOWN]",
                "X": "[MOTION_FADE_IN]",
                "B": "[MOTION_FADE_OUT]",
                "Y": "[MOTION_RESET]",
                "Up": "[MOTION_LOAD_NEXT]",
                "Down": "[MOTION_LOAD_PREV]",
            }
        ),
        G1BeyondmimicCtrlCfg(
            motion_subdir="KungFuAthlete",
            motion_name="1307",
        ),
    ]

    policy: G1KungFuAthletePolicyCfg = G1KungFuAthletePolicyCfg(
        policy_name="1307Taichi",
        use_onnx=True,
    )

    do_safety_check: bool = True


@cfg_registry.register
class g1_amp_real(RlPipelineCfg):
    """
    GMR-AMP Walk Policy on Real G1 Robot.

    ⚠️ Warning: AMP has NOT been validated on real hardware.
    Currently has poor performance in both sim and real (experimental).
    Use at your own risk. Ensure safety measures are in place.

    Usage:
        python scripts/run_pipeline.py -c g1_amp_real

    AMP-based walking policy with velocity control.
    Walk and run variants available.

    Controls (Unitree Controller):
        - Left Stick: Forward/Backward/Strafe velocity
        - Right Stick: Turn velocity (left/right)
        - A: Emergency stop (SHUTDOWN)

    Controls (SSH Keyboard):
        - w/s: Forward/Backward
        - a/d: Left/Right strafe
        - q/e: Turn left/right
        - Esc: Emergency stop
    """

    robot: str = "g1"

    env: G1RealEnvCfg = G1RealEnvCfg(
        env_type="UnitreeCppEnv",
        unitree=G1UnitreeCfg(net_if="eth0"),
    )

    ctrl: list[KeyboardCtrlCfg | UnitreeCtrlCfg] = [
        KeyboardCtrlCfg(
            ctrl_type="KeyboardStdinCtrl",
            triggers_extra={
                "w": "[VELOCITY_FORWARD]",
                "s": "[VELOCITY_BACKWARD]",
                "a": "[VELOCITY_LEFT]",
                "d": "[VELOCITY_RIGHT]",
                "q": "[VELOCITY_TURN_LEFT]",
                "e": "[VELOCITY_TURN_RIGHT]",
            }
        ),
        UnitreeCtrlCfg(
            combination_init_buttons=["L1", "R1", "L2"],
            triggers_extra={
                "A": "[SHUTDOWN]",
            }
        ),
    ]

    policy: G1AmpWalkPolicyCfg = G1AmpWalkPolicyCfg()

    do_safety_check: bool = True


@cfg_registry.register
class g1_wbc_amp_real(RlPipelineCfg):
    """
    WBC FSM AMP Locomotion Policy on Real G1 Robot.

    ⚠️ Warning: WBC FSM AMP has NOT been validated on real hardware.
    Use at your own risk. Ensure safety measures are in place.

    Usage:
        python scripts/run_pipeline.py -c g1_wbc_amp_real

    AMP locomotion policy with 4-frame history and fall recovery.

    Controls (Unitree Controller):
        - Left Stick: Forward/Backward/Strafe velocity
        - Right Stick: Turn velocity
        - A: Emergency stop (SHUTDOWN)

    Controls (SSH Keyboard):
        - w: Loco mode forward
        - s: Loco mode backward
        - Esc: Emergency stop
    """

    robot: str = "g1"

    env: G1RealEnvCfg = G1RealEnvCfg(
        env_type="UnitreeCppEnv",
        unitree=G1UnitreeCfg(net_if="eth0"),
    )

    ctrl: list[KeyboardCtrlCfg | UnitreeCtrlCfg] = [
        KeyboardCtrlCfg(
            ctrl_type="KeyboardStdinCtrl",
            triggers_extra={
                "w": "[POLICY_LOCO]",
                "s": "[POLICY_LOCO]",
            }
        ),
        UnitreeCtrlCfg(
            combination_init_buttons=["L1", "R1", "L2"],
            triggers_extra={
                "A": "[SHUTDOWN]",
            }
        ),
    ]

    policy: G1WbcAmpPolicyCfg = G1WbcAmpPolicyCfg()

    do_safety_check: bool = True


@cfg_registry.register
class g1_wbc_dance_real(RlPipelineCfg):
    """
    WBC FSM Dance Motion Tracking Policy on Real G1 Robot.

    ⚠️ Warning: WBC FSM Dance has NOT been validated on real hardware.
    Requires LAFAN1 reference motion data for full functionality.
    Use at your own risk. Ensure safety measures are in place.

    Usage:
        python scripts/run_pipeline.py -c g1_wbc_dance_real

    Dance motion tracking policy with LAFAN1 reference motion data and fall recovery.

    Controls (Unitree Controller):
        - L1+R1 (hold): Enter command mode
        - A: Emergency stop (SHUTDOWN)
        - X: Start motion (MOTION_FADE_IN)
        - B: Stop motion (MOTION_FADE_OUT)
        - Y: Reset motion (MOTION_RESET)

    Controls (SSH Keyboard):
        - Shift + `<`: Fade in motion
        - Shift + `>`: Fade out motion
        - Shift + `|`: Reset motion
        - Esc: Emergency stop
    """

    robot: str = "g1"

    env: G1RealEnvCfg = G1RealEnvCfg(
        env_type="UnitreeCppEnv",
        unitree=G1UnitreeCfg(net_if="eth0"),
    )

    ctrl: list[KeyboardCtrlCfg | UnitreeCtrlCfg] = [
        KeyboardCtrlCfg(
            ctrl_type="KeyboardStdinCtrl",
            triggers_extra={
                ">": "[MOTION_FADE_OUT]",
                "<": "[MOTION_FADE_IN]",
                "|": "[MOTION_RESET]",
            }
        ),
        UnitreeCtrlCfg(
            combination_init_buttons=["L1", "R1", "L2"],
            triggers_extra={
                "A": "[SHUTDOWN]",
                "X": "[MOTION_FADE_IN]",
                "B": "[MOTION_FADE_OUT]",
                "Y": "[MOTION_RESET]",
            }
        ),
    ]

    policy: G1WbcDancePolicyCfg = G1WbcDancePolicyCfg()

    do_safety_check: bool = True


