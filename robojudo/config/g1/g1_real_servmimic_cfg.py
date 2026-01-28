from robojudo.config import cfg_registry
from robojudo.controller.ctrl_cfgs import UnitreeCtrlCfg
from robojudo.pipeline.pipeline_cfgs import RlLocoMimicPipelineCfg

from .env.g1_real_env_cfg import G1RealServEnvCfg, G1UnitreeCfg
from .policy.g1_beyondmimic_policy_cfg import G1BeyondMimicPolicyCfg
from .policy.g1_unitree_policy_cfg import G1UnitreePolicyCfg

@cfg_registry.register
class g1_real_servmimic(RlLocoMimicPipelineCfg):
    """
    Real G1 Robot with Serving-Mimic switching.
    Service robot with multiple modes: standing, sitting, serving, walking, damping.
    
    Usage:
        python scripts/run_pipeline.py -c g1_real_servmimic
    
    Controls (Unitree Controller):
        - L2+Up: Stand (no balance)
        - L2+Left: Sit down (only from standing, can only switch to standing/damping)
        - A: Damping (exit program and enter main control)
        - Y: Standing + Walking (AMO)
        - X: Step Walking (Unitree)
        - B: Hand serving mode
    
    Skills (only in walking or damping mode):
        - Up+X: Skill 0
        - Down+X: Skill 1
        - Left+X: Skill 2
        - Right+X: Skill 3
    
    Skills use beyondmimic policies:
        - Standing: default_pos
        - Sitting: sitting_pos
        - Serving: serving_pos (hand changes, lower body default)
        - Prepare: sitting_pos (instead of standing)
    
    Prepare mode: Enter sitting position with half interpolation time (1.0s) instead of 2.0s.
    """

    robot: str = "g1"
    
    # Real robot environment with pose configuration
    env: G1RealServEnvCfg = G1RealServEnvCfg(
        env_type="UnitreeCppEnv",
        unitree=G1UnitreeCfg(
            net_if="eth0",
        ),
        # Pose configuration
        standing_pos=[
            *[-0.1, 0.0, 0.0, 0.3, -0.2, 0.0],  # Left leg
            *[-0.1, 0.0, 0.0, 0.3, -0.2, 0.0],  # Right leg
            *[0, 0, 0],  # Waist
            *[0, 0, 0, 0, 0, 0, 0],  # Left arm
            *[0, 0, 0, 0, 0, 0, 0],  # Right arm
        ],
        sitting_pos=[
            *[-1.2, 0.0, 0.0, 1.5, -0.2, 0.0],  # Left leg
            *[-1.2, 0.0, 0.0, 1.5, -0.2, 0.0],  # Right leg
            *[0, 0, 0],  # Waist
            *[-0.4, 0, 0, 0, -1.5, 0, 0],  # Left arm
            *[-0.4, 0, 0, 0, 1.5, 0, 0],  # Right arm
        ],
        # Prepare pose: sitting instead of standing
        prepare_pos=[
            *[-1.2, 0.0, 0.0, 1.5, -0.2, 0.0],  # Left leg
            *[-1.2, 0.0, 0.0, 1.5, -0.2, 0.0],  # Right leg
            *[0, 0, 0],  # Waist
            *[-0.4, 0, 0, 0, -1.5, 0, 0],  # Left arm
            *[-0.4, 0, 0, 0, 1.5, 0, 0],  # Right arm
        ],
        serving_pos=[
            *[-0.1, 0.0, 0.0, 0.3, -0.2, 0.0],  # Left leg (default)
            *[-0.1, 0.0, 0.0, 0.3, -0.2, 0.0],  # Right leg (default)
            *[0, 0, 0],  # Waist
            *[-0.4, 0, 0, 0, -1.5, 0, 0],  # Left arm (hand changes)
            *[-0.4, 0, 0, 0, 1.5, 0, 0],  # Right arm (hand changes)
        ],
        # Interpolation configuration
        interpolation_time=2.0,  # Default interpolation time
        prepare_interpolation_time=1.0,  # Half of default for prepare mode
        enable_smooth_transition=True,
        transition_speed=1.0,
    )

    # Unitree controller with mode switching
    ctrl: list[UnitreeCtrlCfg] = [
        UnitreeCtrlCfg(
            triggers_extra={
                # Mode switching
                "L2+Up": "[MODE_STAND]",       # Stand (no balance)
                "L2+Left": "[MODE_SIT]",        # Sit down (only from standing)
                "A": "[MODE_DAMPING]",       # Damping (exit and main control)
                "Y": "[MODE_STAND_WALK]",    # Standing + Walking (AMO)
                "X": "[MODE_STEP_WALK]",     # Step Walking (Unitree)
                "B": "[MODE_SERVING]",      # Hand serving mode
                
                # Skills (only in walking or damping mode)
                "Up+X": "[SKILL_SWITCH],0",   # Skill 0
                "Down+X": "[SKILL_SWITCH],1",  # Skill 1
                "Left+X": "[SKILL_SWITCH],2",  # Skill 2
                "Right+X": "[SKILL_SWITCH],3", # Skill 3
            }
        ),
    ]

    # Locomotion policy (Unitree walking)
    loco_policy: G1UnitreePolicyCfg = G1UnitreePolicyCfg()
    
    # Mimic policies: BeyondMimic for skills
    mimic_policies: list[G1BeyondMimicPolicyCfg] = [
        # Skill 0: Standing (default_pos)
        G1BeyondMimicPolicyCfg(
            policy_name="Jump_wose",
            without_state_estimator=True,
            use_modelmeta_config=True,
            use_motion_from_model=True,
            max_timestep=2000,
        ),
        # Skill 1: Sitting (sitting_pos)
        G1BeyondMimicPolicyCfg(
            policy_name="Dance_wose",
            without_state_estimator=True,
            use_modelmeta_config=True,
            use_motion_from_model=True,
            max_timestep=2000,
        ),
        # Skill 2: Serving (serving_pos, hand changes, lower body default)
        G1BeyondMimicPolicyCfg(
            policy_name="Gangnanstyle_wose",
            without_state_estimator=True,
            use_modelmeta_config=True,
            use_motion_from_model=True,
            max_timestep=2000,
        ),
        # Skill 3: Additional skill
        G1BeyondMimicPolicyCfg(
            policy_name="Violin",
            without_state_estimator=True,
            use_modelmeta_config=True,
            use_motion_from_model=True,
            max_timestep=2000,
        ),
    ]

    # Enable safety check for real robot
    do_safety_check: bool = True
