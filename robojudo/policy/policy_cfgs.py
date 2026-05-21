from pydantic import field_validator, model_validator

from robojudo.config import ASSETS_DIR, Config
from robojudo.tools.tool_cfgs import DoFConfig


class PolicyCfg(Config):
    policy_type: str  # name of the policy class
    robot: str  # robot name, e.g. "g1"

    @property
    def policy_file(self) -> str:
        """path to the policy file, to be overrided in subclass"""
        policy_file = ASSETS_DIR / f"models/{self.robot}/PLCAEHOLDER.pt"
        return policy_file.as_posix()

    disable_autoload: bool = False  # if True, disable auto loading of the policy file

    freq: int = 50  # control frequency (Hz)

    obs_dof: DoFConfig
    action_dof: DoFConfig

    # action post processing
    action_scale: float = 1.0
    action_clip: float | None = None  # clip action to [-action_clip, action_clip]
    action_beta: float = 1.0  # action smoothing factor

    # history settings
    history_length: int = 0  # number of history observations to use

    # TODO
    # # upper body override settings
    # wrist_override_idxs: list[int] = []  # indices of the wrist joints to override

    @property
    def history_obs_size(self) -> int:
        """size of the history observations, to be calc in subclass"""
        return 0

    @field_validator("action_scale", "action_clip")
    def check_action_scale(cls, v):
        if v is not None and v <= 0:
            raise ValueError("action_scale must be positive")
        return v

    @model_validator(mode="after")
    def check_history(self):
        if self.history_length < 0:
            raise ValueError("history_length cannot be negative")
        if self.history_obs_size < 0:
            raise ValueError("history_obs_size cannot be negative")
        return self

class BFMZeroPolicyCfg(PolicyCfg):
    policy_type: str = "BFMZeroPolicy"
    policy_name: str = "FBcprAuxModel"
    train_method: str = "official"
    # train_method: str = "low"
    # train_method: str = "23dof-bfmzero-isaac-low"
    # train_method: str = "23dof_low_20260407_182514"

    start_timestep: int = 0
    action_rescale: int = 5
    # ======= POLICY SPECIFIC CONFIGURATION =======
    max_timestep: int = -1
    @property
    def policy_file(self) -> str:
        policy_file = ASSETS_DIR / f"models/{self.robot}/BFM0/{self.train_method}/{self.policy_name}.onnx"
        return policy_file.as_posix()
    
    @property
    def config_file(self) -> str:
        config_file = ASSETS_DIR / f"models/{self.robot}/BFM0/{self.train_method}/config.yaml"
        return str(config_file)

class GentlePolicyCfg(PolicyCfg):
    """
    Gentle Policy based on gentleHum sim2sim project
    
    This policy implements complex observations including:
    - Motion tracking with future prediction
    - Compliance control
    - Historical joint positions and actions
    - Projected gravity and root angular velocity
    """
    class ObsScalesCfg(Config):
        pass

    policy_type: str = "GentlePolicy"
    policy_name: str = "policy_latest"
    model_path: str = "gentleHum"

    @property
    def policy_file(self) -> str:
        """Path to the ONNX policy file"""
        from robojudo.config import ASSETS_DIR
        policy_file = ASSETS_DIR / f"models/{self.robot}/{self.model_path}/{self.policy_name}.onnx"
        return policy_file.as_posix()
    motions_path: str = "assets/motions/g1/gentleHumanoid"

    # Action processing - override to support array
    action_scale: list[float] =  [
        0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5,  # legs & waist
        0.5, 0.5, 1.0, 1.0, 0.5, 0.5, 1.0, 1.0,  # knees & ankles  
        0.5, 0.5, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,  # arms
        1.0, 1.0, 1.0, 1.0  # wrists
    ],  # Override to support list # Override to support list
    action_clip: float | None = 10.0
    action_beta: float = 1.0

    # # Observation configuration
    # obs_scales: ObsScalesCfg = ObsScalesCfg()

    # Joint position history steps (from JS: [0, 1, 2, 3, 4, 8])
    joint_pos_steps: list[int] = [0, 1, 2, 3, 4, 8]

    # Future prediction steps (from JS: [0, 2, 4, 8, 16])
    future_steps: list[int] = [0, 2, 4, 8, 16]

    # Previous actions history steps
    prev_actions_steps: int = 3

    # Compliance settings
    compliance_enabled: bool = False
    compliance_threshold: float = 10.0

    # Motion tracking settings
    tracking_enabled: bool = True
    transition_steps: int = 100

    # Command mapping
    commands_map: list[list[float]] = [
        [-1.0, 0.0, 1.0],
        [1.0, 0.0, -1.0], 
        [1.0, 0.0, -1.0],
    ]
     
    @field_validator("action_clip")
    def check_action_clip(cls, v):
        if v is not None and v <= 0:
            raise ValueError("action_clip must be positive")
        return v
 
    @model_validator(mode="after")
    def check_action_scale(self):
        # Custom validation for action_scale array
        if hasattr(self, 'action_scale') and isinstance(self.action_scale, list):
            for scale in self.action_scale:
                if scale <= 0:
                    raise ValueError("All action_scale values must be positive")
        return self


class UnitreePolicyCfg(PolicyCfg):
    class ObsScalesCfg(Config):
        dof_pos: float = 1.0
        dof_vel: float = 0.05
        ang_vel: float = 0.25
        command: list[float] = [2.0, 2.0, 0.25]

    policy_type: str = "UnitreePolicy"
    policy_name: str = "policy"

    @property
    def policy_file(self) -> str:
        policy_file = ASSETS_DIR / f"models/{self.robot}/unitree/{self.policy_name}.pt"
        return policy_file.as_posix()

    action_scale: float = 0.25
    action_clip: float | None = None
    action_beta: float = 0.8

    # ======= POLICY SPECIFIC CONFIGURATION =======
    obs_scales: ObsScalesCfg = ObsScalesCfg()
    max_cmd: list[float] = [0.8, 0.5, 1.57]
    commands_map: list[list[float]] = [
        [-1.0, 0.0, 1.0],
        [1.0, 0.0, -1.0],
        [1.0, 0.0, -1.0],
    ]


class UnitreeWoGaitPolicyCfg(PolicyCfg):
    class ObsScalesCfg(Config):
        ang_vel: float = 0.2
        gravity: float = 1.0
        dof_pos: float = 1.0
        dof_vel: float = 0.05
        command: list[float] = [1.0, 1.0, 1.0]

    policy_type: str = "UnitreeWoGaitPolicy"
    policy_name: str = "policy_wo_gait"

    @property
    def policy_file(self) -> str:
        policy_file = ASSETS_DIR / f"models/{self.robot}/unitree/{self.policy_name}.pt"
        return policy_file.as_posix()

    action_scale: float = 0.25
    action_clip: float | None = None
    action_beta: float = 1.0

    history_length: int = 5  # number of history observations to use
    history_obs_dims: dict[str, int] = {}

    # ======= POLICY SPECIFIC CONFIGURATION =======
    obs_scales: ObsScalesCfg = ObsScalesCfg()
    max_cmd: list[float] = [0.8, 0.5, 1.57]
    commands_map: list[list[float]] = [
        [-1.0, 0.0, 1.0],
        [1.0, 0.0, -1.0],
        [1.0, 0.0, -1.0],
    ]


class UnitreeMjlabVelocityPolicyCfg(PolicyCfg):
    """
    参考 UnitreeWoGaitPolicyCfg

    """
    class ObsScalesCfg(Config):
        gravity: float = 1.0     # deploy.yaml: projected_gravity scale
        dof_pos: float = 1.0     # deploy.yaml: joint_pos_rel scale
        dof_vel: float = 1.0     # deploy.yaml: joint_vel_rel scale
        ang_vel: float = 1.0     # deploy.yaml: base_ang_vel scale
        command: float = 1.0     # deploy.yaml: velocity_commands scale
        
    
    robot: str = "g1"
    policy_type: str = "G1UnitreeMjlabVelocityPolicy"
    model_dir: str = "4900_23dof"  
    # model_dir: str = "demo_29dof"
    # model_dir:str="policy_20000_29dof"  

    @property
    def policy_file(self) -> str:
        """Override to point to ONNX model in unitree_mjlab_velocity directory."""
        from robojudo.config.global_path import ASSETS_DIR
        policy_file = ASSETS_DIR / f"models/{self.robot}/unitree_mjlab_velocity/{self.model_dir}/policy.onnx"
        return policy_file.as_posix()
    
    # action_scale: list[float] = [0.55, 0.35, 0.55, 0.35, 0.44, 0.44, 0.55, 0.35, 0.55, 0.35, 0.44, 0.44, 0.35, 0.44, 0.44,
    #                  0.44, 0.44, 0.44, 0.44, 0.44, 0.07, 0.07, 0.44, 0.44, 0.44, 0.44, 0.44, 0.07, 0.07]
    # action_offset: list[float] = [-0.1,0,0,0.3,-0.2,0, -0.1,0,0,0.3,-0.2,0,  0,0,0,  0.35,0.18,0,0.87,0,0,0, 0.35,-0.18,0,0.87,0,0,0]
    
    history_length: int = 1  # number of history observations to use
    history_obs_dims: dict[str, int] = {}
    
    obs_scales: ObsScalesCfg = ObsScalesCfg()
    # From deploy.yaml: step_dt
    dt: float = 0.02
    
    max_cmd: list[float] = [1.0, 0.5, 1.5]
    commands_map: list[list[float]] = [
        [-0.6, 0.0, 0.9],
        [1.0, 0.0, -1.0],
        [1.0, 0.0, -1.0],
    ]

class AmpWalkPolicyCfg(PolicyCfg):
    """
    Gmr Amp Legged Lab Policy
    """
    class ObsScalesCfg(Config):
        gravity: float = 1.0     # deploy.yaml: projected_gravity scale
        dof_pos: float = 1.0     # deploy.yaml: joint_pos_rel scale
        dof_vel: float = 1.0     # deploy.yaml: joint_vel_rel scale
        ang_vel: float = 1.0     # deploy.yaml: base_ang_vel scale
        command: float = 1.0     # deploy.yaml: velocity_commands scale
    
    robot: str = "g1"
    policy_type: str = "G1AmpPolicy"
    model_dir: str = "gmramp/run_20000" 
    # model_dir: str = "gmramp/run_18400" 
    # model_dir: str = "gmramp/walk_20000" 
    # model_dir: str = "gmramp/walk_18000" 


    @property
    def policy_file(self) -> str:
        """Override to point to ONNX model in unitree_mjlab_velocity directory."""
        from robojudo.config.global_path import ASSETS_DIR
        # policy_file = ASSETS_DIR / f"models/{self.robot}/{self.model_dir}/policy.onnx"
        policy_file = ASSETS_DIR / f"models/{self.robot}/{self.model_dir}/policy.pt"

        return policy_file.as_posix()
    action_scale: float = 0.25

    history_length: int = 1
    history_obs_dims: dict[str, int] = {}
    
    obs_scales: ObsScalesCfg = ObsScalesCfg()
    # self.decimation = 4

    dt: float = 0.02
    max_cmd: list[float] = [1., 1., 1.]
    '''
    self.commands.base_velocity.ranges.lin_vel_x = (0.0, 1.0)    # 前向速度: 0~1 m/s
    self.commands.base_velocity.ranges.lin_vel_y = (-0.5, 0.5)   # 横向速度: ±0.5 m/s
    self.commands.base_velocity.ranges.ang_vel_z = (-0.5, 0.5)   # 旋转速度: ±0.5 rad/s
    self.commands.base_velocity.ranges.heading = (-math.pi, math.pi)  # 朝向: ±π rad
    '''

    ## run 
    if "run" in model_dir:
        commands_map: list[list[float]] = [
            [-1., 0.0, 1.],
            [-0., 0.0, 0.],
            [0., 0.0, 0.],
        ]
    ## walk
    elif "walk" in model_dir:
        commands_map: list[list[float]] = [
            [-1., 0.0, 1.],
            [0., 0.0, 0.],
            [0., 0.0, 0.],
        ]


class SmoothPolicyCfg(PolicyCfg):
    class ObsScalesCfg(Config):
        ang_vel: float = 0.25
        dof_vel: float = 0.05
        lin_vel: float = 0.5

    policy_type: str = "SmoothPolicy"
    policy_name: str

    @property
    def policy_file(self) -> str:
        policy_file = ASSETS_DIR / f"models/{self.robot}/smooth/{self.policy_name}.pt"
        return policy_file.as_posix()

    action_scale: float = 0.5
    action_clip: float | None = 10.0
    action_beta: float = 0.8

    # ======= POLICY SPECIFIC CONFIGURATION =======
    obs_scales: ObsScalesCfg = ObsScalesCfg()

    history_length: int = 10

    @property
    def history_obs_size(self) -> int:
        history_obs_size = 2 + 3 + 3 + 2 + 2 * self.obs_dof.num_dofs + self.action_dof.num_dofs
        return history_obs_size

    cycle_time: float = 0.8

    commands_map: list[list[float]] = [
        [-1.0, 0.0, 1.0],
        [1.0, 0.0, -1.0],
        [1.0, 0.0, -1.0],
    ]


class H2HPolicyCfg(PolicyCfg):
    class ObsScalesCfg(Config):
        ang_vel: float = 1.0
        dof_vel: float = 1.0

    # obs_type as "v-teleop-extend-vr-max-nolinvel"
    policy_type: str = "H2HStudentPolicy"
    policy_name: str

    @property
    def policy_file(self) -> str:
        policy_file = ASSETS_DIR / f"models/{self.robot}/h2h/{self.policy_name}.pt"
        return policy_file.as_posix()

    action_scale: float = 0.25
    action_clip: float | None = 10.0
    action_beta: float = 0.8

    # ======= POLICY SPECIFIC CONFIGURATION =======
    use_imu_torso: bool = False
    use_dof_pos_offset: bool = False

    obs_scales: ObsScalesCfg = ObsScalesCfg()

    history_length: int = 25

    @property
    def history_obs_size(self) -> int:
        history_obs_size = 2 * self.obs_dof.num_dofs + 3 + 3 + self.action_dof.num_dofs
        return history_obs_size


class AMOPolicyCfg(PolicyCfg):
    class ObsScalesCfg(Config):
        ang_vel: float = 0.25
        dof_vel: float = 0.05

    policy_type: str = "AMOPolicy"

    @property
    def policy_file(self) -> str:
        policy_file = ASSETS_DIR / f"models/{self.robot}/amo/amo_jit.pt"
        return policy_file.as_posix()

    @property
    def policy_adapter_file(self) -> str:
        policy_adapter_file = ASSETS_DIR / f"models/{self.robot}/amo/adapter_jit.pt"
        return policy_adapter_file.as_posix()

    @property
    def policy_adapter_norm_file(self) -> str:
        policy_adapter_norm_file = ASSETS_DIR / f"models/{self.robot}/amo/adapter_norm_stats.pt"
        return policy_adapter_norm_file.as_posix()

    # ======= POLICY SPECIFIC CONFIGURATION =======
    obs_scales: ObsScalesCfg = ObsScalesCfg()

    action_scale: float = 0.25

    commands_map: list[list[float]]


class BeyondMimicPolicyCfg(PolicyCfg):
    policy_type: str = "BeyondMimicPolicy"
    disable_autoload: bool = True

    policy_name: str
    max_timestep: int = -1
    start_timestep: int = 0

    @property
    def policy_file(self) -> str:
        policy_file = ASSETS_DIR / f"models/{self.robot}/beyondmimic/{self.policy_name}.onnx"
        return policy_file.as_posix()

    # ======= POLICY SPECIFIC CONFIGURATION =======
    action_scales: list[float]

    without_state_estimator: bool
    override_robot_anchor_pos: bool = True  # if True, drop pos fdb

    use_modelmeta_config: bool = True  # if True, use the config from modelmeta
    use_motion_from_model: bool = True  # if True, use the motion data of onnx model

    @model_validator(mode="after")
    def check_modelmeta(self):
        if self.use_motion_from_model:
            if not self.use_modelmeta_config:
                raise ValueError("use_modelmeta_config must be True when use_motion_from_model")

        return self


class AsapPolicyCfg(PolicyCfg):
    policy_type: str = "AsapPolicy"
    disable_autoload: bool = True

    # ======= MOTION POLICY CONFIGURATION =======
    policy_name: str
    relative_path: str

    motion_length_s: float
    start_upper_body_dof_pos: list[float] | None = None  # reserved for interpolation loco to mimic

    @property
    def policy_file(self) -> str:
        policy_file = ASSETS_DIR / f"models/{self.robot}/asap/mimic/{self.policy_name}/{self.relative_path}"
        return policy_file.as_posix()

    # ======= POLICY SPECIFIC CONFIGURATION =======
    class ObsScalesCfg(Config):
        # base_lin_vel: float
        base_ang_vel: float
        projected_gravity: float
        # command_lin_vel: float
        # command_ang_vel: float
        # command_stand: float
        # command_base_height: float
        # ref_upper_dof_pos: float
        dof_pos: float
        dof_vel: float
        history: float
        actions: float
        # phase_time: float
        ref_motion_phase: float
        # sin_phase: float
        # cos_phase: float

    action_scale: float = 0.25
    action_clip: float | None = 100.0
    obs_scales: ObsScalesCfg

    history_length: int = 4  # number of history observations to use
    history_obs_dims: dict[str, int] = {}
    """
    Note: the history obs item should be aligned with code of policy
    IMPORTANT: the key order should be SORTED when concat history obs!!!
    """

    USE_HISTORY: bool


class AsapLocoPolicyCfg(PolicyCfg):
    policy_type: str = "AsapLocoPolicy"
    disable_autoload: bool = True

    # ======= MOTION POLICY CONFIGURATION =======
    policy_name: str
    relative_path: str

    @property
    def policy_file(self) -> str:
        policy_file = ASSETS_DIR / f"models/{self.robot}/asap/dec_loco/{self.policy_name}/{self.relative_path}"
        return policy_file.as_posix()

    # ======= POLICY SPECIFIC CONFIGURATION =======
    class ObsScalesCfg(Config):
        # base_lin_vel: float
        base_ang_vel: float
        projected_gravity: float
        command_lin_vel: float
        command_ang_vel: float
        command_stand: float
        command_base_height: float
        ref_upper_dof_pos: float
        dof_pos: float
        dof_vel: float
        history: float
        actions: float
        # phase_time: float
        ref_motion_phase: float
        sin_phase: float
        cos_phase: float

    action_scale: float = 0.25
    action_clip: float | None = 100.0
    obs_scales: ObsScalesCfg

    history_length: int = 4  # number of history observations to use
    history_obs_dims: dict[str, int] = {}
    """Note: the history obs item should be aligned with code of policy"""

    USE_HISTORY: bool
    GAIT_PERIOD: float
    NUM_UPPER_BODY_JOINTS: int

    # ======= Default Command CONFIGURATION =======
    command_base_height_default: float


class KungfuBotGeneralPolicyCfg(PolicyCfg):
    policy_type: str = "KungfuBotGeneralPolicy"
    disable_autoload: bool = True

    # ======= MOTION POLICY CONFIGURATION =======
    policy_name: str

    @property
    def policy_file(self) -> str:
        policy_file = ASSETS_DIR / f"models/{self.robot}/kungfubot2/{self.policy_name}.onnx"
        return policy_file.as_posix()

    # ======= POLICY SPECIFIC CONFIGURATION =======
    class ObsScalesCfg(Config):
        # base_lin_vel: float
        base_ang_vel: float
        dof_pos: float
        dof_vel: float
        actions: float
        roll_pitch: float
        # anchor_ref_pos: float
        anchor_ref_rot: float
        next_step_ref_motion: float
        history: float
        future_motion_root_height: float
        future_motion_roll_pitch: float
        future_motion_base_lin_vel: float
        future_motion_base_yaw_vel: float
        future_motion_dof_pos: float

    action_scale: float = 0.0  # not used, scale for each dof
    action_clip: float | None = 100.0
    action_scales: list[float]
    obs_scales: ObsScalesCfg

    history_length: int = 10  # number of history observations to use
    history_obs_dims: dict[str, int] = {}
    """
    Note: the history obs item should be aligned with code of policy
    IMPORTANT: the key order should be SORTED when concat history obs!!!
    """

    compatibility_old_version: bool = False
    """For old version of kungfubot general policy (before 2025-11-13 bugfix #68)"""


class TwistPolicyCfg(PolicyCfg):
    class ObsScalesCfg(Config):
        ang_vel: float = 0.25
        dof_vel: float = 0.05
        dof_pos: float = 1.0

    policy_type: str = "TwistPolicy"
    policy_name: str

    @property
    def policy_file(self) -> str:
        policy_file = ASSETS_DIR / f"models/{self.robot}/twist/{self.policy_name}.pt"
        return policy_file.as_posix()

    action_scale: float = 0.5
    action_clip: float | None = 10.0
    action_beta: float = 1.0

    # ======= POLICY SPECIFIC CONFIGURATION =======
    obs_scales: ObsScalesCfg = ObsScalesCfg()

    history_length: int = 10

    @property
    def n_mimic_obs(self) -> int:
        return self.action_dof.num_dofs + 8

    @property
    def history_obs_size(self) -> int:
        history_obs_size = self.n_mimic_obs + 3 + 2 + 3 * self.action_dof.num_dofs
        return history_obs_size

    ankle_idx: list[int]
    mimic_obs_total_degrees: int
    mimic_obs_wrist_ids: list[int]

    @property
    def mimic_obs_other_ids(self) -> list[int]:
        return [f for f in range(self.mimic_obs_total_degrees) if f not in self.mimic_obs_wrist_ids]


class KungFuAthletePolicyCfg(PolicyCfg):
    """KungFuAthlete Policy Configuration for G1 Robot
    Source: https://github.com/NPCLEI/KungFuAthleteBot
    """
    model_config = {"arbitrary_types_allowed": True}
    
    policy_type: str = "KungFuAthletePolicy"
    policy_name: str = "1307Taichi"
    use_onnx: bool = False
    
    @property
    def policy_file(self) -> str:
        from robojudo.config import ASSETS_DIR
        ext = "onnx" if self.use_onnx else "pt"
        policy_file = ASSETS_DIR / f"models/{self.robot}/KungFuAthlete/{self.policy_name}/policy.{ext}"
        return policy_file.as_posix()

    # 策略特定配置
    action_scale: list[float] = None  # 将在DoF配置中设置
    action_clip: float | None = None
    action_beta: float = 1.0
    freq: int = 50
    
    # 观测配置 (从文档中提取: 160维)
    class ObsScalesCfg:
        command: float = 1.0
        motion_anchor_pos_b: float = 1.0
        motion_anchor_ori_b: float = 1.0
        base_lin_vel: float = 1.0
        base_ang_vel: float = 1.0
        joint_pos: float = 1.0
        joint_vel: float = 1.0
        actions: float = 1.0
    
    obs_scales: ObsScalesCfg = ObsScalesCfg()
    

