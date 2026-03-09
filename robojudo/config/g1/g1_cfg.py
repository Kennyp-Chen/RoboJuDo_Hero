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


@cfg_registry.register
class g1_locomimic(RlLocoMimicPipelineCfg):
    """
    Example of loco mimic pipeline configuration.
    You can switch between loco and mimic policies during runtime, with interpolation.
    === Check more fancy locomimic examples in g1_loco_mimic_cfg.py ===
    """

    robot: str = "g1"
    env: G1MujocoEnvCfg = G1MujocoEnvCfg()

    ctrl: list[KeyboardCtrlCfg | JoystickCtrlCfg] = [
        KeyboardCtrlCfg(
            triggers_extra={
                "]": "[POLICY_LOCO]",
                "[": "[POLICY_MIMIC]",
            }
        ),
        JoystickCtrlCfg(
            triggers_extra={
                "RB+Down": "[POLICY_LOCO]",
                "RB+Up": "[POLICY_MIMIC]",
            }
        ),
    ]

    loco_policy: G1UnitreePolicyCfg = G1UnitreePolicyCfg()
    mimic_policies: list[G1AsapPolicyCfg] = [
        G1AsapPolicyCfg(),
    ]


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
        policy_name="Dance_wose",
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
        # *[-0.4, 0, 0, 0, -1.5, 0, 0],# 左臂
        # *[-0.4, 0, 0, 0, 1.5, 0, 0], # 右臂
        *[0.35,0.18,0.,0.87,0.,0.,0.],
        *[0.35,-0.18,0.,0.87,0.,0.,0.]
    ]

    # # Standing pose configuration
    # standing_pos: list[float] = [
    #     *[-0.1, 0.0, 0.0, 0.3, -0.2, 0.0],  # 左腿
    #     *[-0.1, 0.0, 0.0, 0.3, -0.2, 0.0],  # 右腿
    #     *[0, 0, 0],  # 腰部
    #     *[0, 0, 0, 0, 0, 0, 0],  # 左臂
    #     *[0, 0, 0, 0, 0, 0, 0],  # 右臂
    # ]

    # Keyboard and controller with policy switching
    ctrl: list[KeyboardCtrlCfg | UnitreeCtrlCfg] = [
        KeyboardCtrlCfg(
            ctrl_type="KeyboardStdinCtrl",
            triggers_extra={
                "]": "[POLICY_LOCO]",       # Switch to LOCO
                "[": "[POLICY_MIMIC]",      # Switch to current MIMIC
                # "Key.tab": "[POLICY_TOGGLE]",

                "1": "[POLICY_SWITCH],0",   #  Index0 motion
                "2": "[POLICY_SWITCH],1",   #  Index1 motion
                "3": "[POLICY_SWITCH],2",   #  Index2 motion
                "4": "[POLICY_SWITCH],3",   #  Index3 motion
                "5": "[SITTING_POSE]",      # Switch to sitting pose
                "6": "[STANDING_POSE]",      # Switch to standing pose

            }
        ),
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
        # Index 0: Dance motion
        # G1AmoPolicyCfg(),
        # G1AmpWalkPolicyCfg(),


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
        # G1BeyondMimicPolicyCfg( # 6
        #     policy_name="23dof_65fps/dance1_subject1",
        #     start_timestep = 5800,# 适合运动开始
        #     max_timestep=6400,        
        # ),
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
        G1BeyondMimicPolicyCfg(# 3
            policy_name="23dof_65fps/dance2_subject4",
            start_timestep = 5990, # 在往前10 试试 5990
            max_timestep=7400,   # 6720   
        ),
        G1BeyondMimicPolicyCfg( # 稳定
            policy_name="23dof_65fps/GangnamStyle",           
            start_timestep = 200,
            max_timestep=-1,        
        ),
        G1BeyondMimicPolicyCfg( # 稳定
            policy_name="23dof_65fps/Take102",           
            start_timestep = 100,
            max_timestep=-1,        
        ),  
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



# ======================== Custom Multi-Policy Examples ======================== #


@cfg_registry.register
class g1_real_locomimic_multi(RlLocoMimicPipelineCfg):
    """
    Real G1 Robot with multiple Mimic policies.
    Example configuration showing how to add multiple mimic policies and switch between them.
    
    Usage:
        python scripts/run_pipeline.py -c g1_real_locomimic_multi
    
    Controls (Keyboard via SSH):
        - WASD/QE: Movement control (when in LOCO mode)
        - ]: Switch to LOCO mode
        - [: Switch to current MIMIC policy
        - 1: Switch to Jump motion (index 0)
        - 2: Switch to Dance motion (index 1)
        - 3: Switch to ASAP CR7 motion (index 2)
        - ESC: Emergency stop
    
    Controls (Unitree Controller):
        - Left/Right Stick: Movement control (when in LOCO mode)
        - Y: Switch to LOCO mode
        - X: Switch to current MIMIC policy
        - up: Switch to Jump motion
        - down: Switch to Dance motion
        - left: Switch to ASAP CR7 motion
        - right: Next MIMIC policy
        - A: Emergency stop
    
    Note: You can only switch between mimic policies when in LOCO mode.
          See docs/G1_REAL_LOCOMIMIC_GUIDE.md for more details.
    """

    robot: str = "g1"
    
    env: G1RealEnvCfg = G1RealEnvCfg(
        env_type="UnitreeCppEnv",
        unitree=G1UnitreeCfg(net_if="eth0"),
    )

    ctrl: list[KeyboardCtrlCfg | UnitreeCtrlCfg] = [
        # SSH keyboard control
        KeyboardCtrlCfg(
            ctrl_type="KeyboardStdinCtrl",
            triggers_extra={
                "]": "[POLICY_LOCO]",       # Switch to LOCO
                "[": "[POLICY_MIMIC]",      # Switch to current MIMIC
                "1": "[POLICY_SWITCH],0",   # Jump
                "2": "[POLICY_SWITCH],1",   # Dance
                "3": "[POLICY_SWITCH],2",   # ASAP CR7
            }
        ),
        # Unitree controller
        UnitreeCtrlCfg(
            triggers_extra={
                "Y": "[POLICY_LOCO]",       # Y button -> LOCO
                "X": "[POLICY_MIMIC]",      # X button -> MIMIC
                "Up": "[POLICY_SWITCH],0",     # Up -> Jump
                "Down": "[POLICY_SWITCH],1",   # Down -> Dance
                "Left": "[POLICY_SWITCH],2",   # Left -> ASAP
                "Right": "[POLICY_SWITCH],NEXT",  # Right -> Next policy
            }
        ),
    ]

    loco_policy: G1UnitreePolicyCfg = G1UnitreePolicyCfg()
    
    # Multiple mimic policies
    mimic_policies: list[G1BeyondMimicPolicyCfg | G1AsapPolicyCfg] = [
        # Index 0: Jump motion
        G1BeyondMimicPolicyCfg(
            policy_name="Jump_wose",
            without_state_estimator=True,
            use_modelmeta_config=True,
            use_motion_from_model=True,
            max_timestep=140,
        ),
        # Index 1: Dance motion
        G1BeyondMimicPolicyCfg(
            policy_name="Dance_wose",
            without_state_estimator=True,
            use_modelmeta_config=True,
            use_motion_from_model=True,
            max_timestep=200,
        ),
        # Index 2: ASAP CR7 motion
        G1AsapPolicyCfg(
            policy_name="CR7_level1",
            relative_path="model_191500.onnx",
            motion_length_s=3.967,
        ),
    ]

    do_safety_check: bool = True

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


# from .g1_real_servmimic_cfg import g1_real_servmimic  # noqa: F401


