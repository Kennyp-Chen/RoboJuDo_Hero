from pydantic import field_validator, model_validator

from robojudo.config import ASSETS_DIR, Config
from robojudo.tools.tool_cfgs import DoFConfig

import math
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
    # model_dir: str = "policy_20000_29dof" 
    # model_dir: str = "4900_23dof"  
    model_dir: str = "demo_29dof"  

    @property
    def policy_file(self) -> str:
        """Override to point to ONNX model in unitree_mjlab_velocity directory."""
        from robojudo.config.global_path import ASSETS_DIR
        policy_file = ASSETS_DIR / f"models/{self.robot}/unitree_mjlab_velocity/{self.model_dir}/policy.onnx"
        return policy_file.as_posix()
    

    history_length: int = 1  # number of history observations to use
    history_obs_dims: dict[str, int] = {}
    
    obs_scales: ObsScalesCfg = ObsScalesCfg()
    # From deploy.yaml: step_dt
    dt: float = 0.02
    # Velocity command ranges from deploy.yaml
    # max_cmd: list[float] = [1.0, 0.5, 1.0]  # [lin_vel_x, lin_vel_y, ang_vel_z] from deploy.yaml
    max_cmd: list[float] = [1.0, 0.5, 1.5]

    # Command mapping from deploy.yaml（修复为3个值）
    # commands_map: list[list[float]] = [
    #     [-0.5, 0.0, 1.0],  # forward: [-0.5, 0.0, 1.0] from deploy.yaml
    #     [0.5, 0.0, -0.5],  # lateral: [-0.5, 0.0, 0.5] from deploy.yaml  
    #     [1.0, 0.0, -1.0],  # angular: [-1.0, 0.0, 1.0] from deploy.yaml
    # ]
    
    commands_map: list[list[float]] = [
        [-1.0, 0.0, 1.0],
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
    # sim_dt: float = 0.005
    dt: float = 0.02

    max_cmd: list[float] = [1., 1., 2.5]
    '''
    self.commands.base_velocity.ranges.lin_vel_x = (0.0, 1.0)    # 前向速度: 0~1 m/s
    self.commands.base_velocity.ranges.lin_vel_y = (-0.5, 0.5)   # 横向速度: ±0.5 m/s
    self.commands.base_velocity.ranges.ang_vel_z = (-0.5, 0.5)   # 旋转速度: ±0.5 rad/s
    self.commands.base_velocity.ranges.heading = (-math.pi, math.pi)  # 朝向: ±π rad
    '''

    ## run 
    if "run" in model_dir:
        commands_map: list[list[float]] = [
            [-1., 0.0, 2.5],
            [-0., 0.0, 0.],
            # [-0., 0.0, 0.],
            [-math.pi, 0.0, math.pi],

        ]
    # walk
    elif "walk" in model_dir:
        commands_map: list[list[float]] = [
            [-1., 0.0, 1.],
            [0., 0.0, 0.],
            # [0., 0.0, 0.],
            [-math.pi, 0.0, math.pi],
        ]

class AmpRunWalkPolicyCfg(PolicyCfg):
    """
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
    """
    class ObsScalesCfg(Config):
        ang_vel: float = 1.0
        root_local_rot_tan_norm: float = 1.0 # TODO: check if this is correct
        command: float = 1.0
        dof_pos: float = 1.0
        dof_vel: float = 1.0
        key_body_pos_b: float = 1.0 # TODO: check if this is correct

    robot: str = "g1"
    policy_type: str = "G1AmpRunWalkPolicy"
    model_dir: str = "gmramp/runwalk_30000" 
    # model_dir: str = "gmramp/runwalk_24000" 

    @property
    def policy_file(self) -> str:
        """Override to point to ONNX model in unitree_mjlab_velocity directory."""
        from robojudo.config.global_path import ASSETS_DIR
        policy_file = ASSETS_DIR / f"models/{self.robot}/{self.model_dir}/policy.pt"


        return policy_file.as_posix()
    action_scale: float = 0.25

    history_length: int = 5
    history_obs_dims: dict[str, int] = {}
    
    obs_scales: ObsScalesCfg = ObsScalesCfg()
    # dt: float = 0.005 # sim_dt
    dt: float = 0.02 # ctrl_dt = sim_dt * decimation(采样/抽取因子)
    # action_clip: float | None = 1.8

    max_cmd: list[float] = [3., 1., 1.]# scale
    action_beta: float = 1


    commands_map: list[list[float]] = [
        [-0.2, 0.0, 1.],
        [-0.5, 0.0, 0.5],
        [-0.5, 0.0, 0.5],
    ]
    # commands_map: list[list[float]] = [
    #     [-0.1, 0.0, 0.1],
    #     [-0.1, 0.0, 0.1],
    #     [-math.pi, 0.0, math.pi],
    # ]


class AmpRecoveryPolicyCfg(PolicyCfg):
    """

    """

    robot: str = "g1"
    policy_type: str = "G1AmpRecoveryPolicy"
    model_dir: str ="recover_policy/loco/amp_0309_1.onnx"
    @property
    def policy_file(self) -> str:
        """Override to point to ONNX model in unitree_mjlab_velocity directory."""
        from robojudo.config.global_path import ASSETS_DIR
        policy_file = ASSETS_DIR / f"models/{self.robot}/{self.model_dir}"

        return policy_file.as_posix()
    class ObsScalesCfg(Config):
        gravity: float = 1.0     # deploy.yaml: projected_gravity scale
        dof_pos: float = 1.0     # deploy.yaml: joint_pos_rel scale
        dof_vel: float = 1.0     # deploy.yaml: joint_vel_rel scale
        ang_vel: float = 1.0     # deploy.yaml: base_ang_vel scale
        command: float = 1.0     # deploy.yaml: velocity_commands scale
    
    action_scale: float = 0.25

    history_length: int = 4
    history_obs_dims: dict[str, int] = {}
    
    obs_scales: ObsScalesCfg = ObsScalesCfg()
    dt: float = 0.02
    action_clip: float = 100.0
    max_cmd: list[float] = [1., 1., 2.5]
    '''
    self.commands.base_velocity.ranges.lin_vel_x = (0.0, 1.0)    # 前向速度: 0~1 m/s
    self.commands.base_velocity.ranges.lin_vel_y = (-0.5, 0.5)   # 横向速度: ±0.5 m/s
    self.commands.base_velocity.ranges.ang_vel_z = (-0.5, 0.5)   # 旋转速度: ±0.5 rad/s
    self.commands.base_velocity.ranges.heading = (-math.pi, math.pi)  # 朝向: ±π rad
    '''

    mode: str = "run" 
    if mode == "run" :
        commands_map: list[list[float]] = [
            [-1., 0.0, 2.5],
            [-0., 0.0, 0.],
            # [-0., 0.0, 0.],
            [-math.pi, 0.0, math.pi],

        ]
    # walk
    elif mode == "walk" :
        commands_map: list[list[float]] = [
            [-1., 0.0, 1.],
            [0., 0.0, 0.],
            # [0., 0.0, 0.],
            [-math.pi, 0.0, math.pi],
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

class MultiModalWBCPolicyCfg(PolicyCfg):
    
    policy_type: str = "MultiModalWBCPolicy"
    disable_autoload: bool = True

    policy_name: str
    max_timestep: int = -1
    start_timestep: int = 0

    @property
    def policy_file(self) -> str:
        policy_file = ASSETS_DIR / f"models/{self.robot}/mulModWBC/50000/{self.policy_name}.onnx"
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


class BeyondMimicPolicyCfg(PolicyCfg):
    policy_type: str = "BeyondMimicPolicy"
    disable_autoload: bool = True

    policy_name: str
    max_timestep: int = -1
    start_timestep: int = 0 

    @property
    def policy_file(self) -> str:
        policy_file = ASSETS_DIR / f"models/{self.robot}/beyondmimic/{self.policy_name}.onnx"
        # policy_file = ASSETS_DIR / f"models/{self.robot}/beyondmimic/23dof_65fps/{self.policy_name}.onnx"

        return policy_file.as_posix()

    # ======= POLICY SPECIFIC CONFIGURATION =======
    action_scales: list[float]

    without_state_estimator: bool =True
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
