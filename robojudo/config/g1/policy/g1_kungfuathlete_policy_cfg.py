from pydantic import model_validator

from robojudo.policy.policy_cfgs import PolicyCfg
from robojudo.tools.tool_cfgs import DoFConfig


class G1KungFuAthleteDoF(DoFConfig):
    """G1 KungFuAthlete DoF configuration"""
    joint_names: list[str] = [
        'left_hip_pitch_joint', 'left_hip_roll_joint', 'left_hip_yaw_joint',
        'left_knee_joint', 'left_ankle_pitch_joint', 'left_ankle_roll_joint',
        'right_hip_pitch_joint', 'right_hip_roll_joint', 'right_hip_yaw_joint', 
        'right_knee_joint', 'right_ankle_pitch_joint', 'right_ankle_roll_joint',
        'waist_yaw_joint', 'waist_roll_joint', 'waist_pitch_joint',
        'left_shoulder_pitch_joint', 'left_shoulder_roll_joint', 'left_shoulder_yaw_joint',
        'left_elbow_joint', 'left_wrist_roll_joint', 'left_wrist_pitch_joint', 'left_wrist_yaw_joint',
        'right_shoulder_pitch_joint', 'right_shoulder_roll_joint', 'right_shoulder_yaw_joint',
        'right_elbow_joint', 'right_wrist_roll_joint', 'right_wrist_pitch_joint', 'right_wrist_yaw_joint'
    ]
    
    # 默认位置 (HOME_KEYFRAME)
    default_pos: list[float] = [
        -0.1, 0.0, 0.0, 0.3, -0.2, 0.0,     # 左腿
        -0.1, 0.0, 0.0, 0.3, -0.2, 0.0,     # 右腿
        0.0, 0.0, 0.0,                       # 腰部
        0.35, 0.18, 0.0, 0.87, 0.0,          # 左臂
        0.0, 0.0,                            # 左手腕
        0.35, -0.18, 0.0, 0.87, 0.0,         # 右臂
        0.0, 0.0                             # 右手腕
    ]
    
    # 执行器参数 (从文档中提取)
    stiffness: list[float] = [
        40.179, 99.098, 40.179, 99.098, 28.501, 28.501,  # 左腿
        40.179, 99.098, 40.179, 99.098, 28.501, 28.501,  # 右腿
        40.179, 28.501, 28.501,                            # 腰部
        14.251, 14.251, 14.251, 14.251, 14.251,          # 左臂
        16.778, 16.778,                                    # 左手腕
        14.251, 14.251, 14.251, 14.251, 14.251,          # 右臂
        16.778, 16.778                                     # 右手腕
    ]
    
    damping: list[float] = [
        2.558, 6.309, 2.558, 6.309, 1.814, 1.814,        # 左腿
        2.558, 6.309, 2.558, 6.309, 1.814, 1.814,        # 右腿
        2.558, 1.814, 1.814,                              # 腰部
        0.907, 0.907, 0.907, 0.907, 0.907,              # 左臂
        1.068, 1.068,                                      # 左手腕
        0.907, 0.907, 0.907, 0.907, 0.907,              # 右臂
        1.068, 1.068                                       # 右手腕
    ]
    
    # 动作缩放参数
    action_scales: list[float] = [
        0.547546, 0.350661, 0.547546, 0.350661, 0.438577, 0.438577,  # 左腿
        0.547546, 0.350661, 0.547546, 0.350661, 0.438577, 0.438577,  # 右腿
        0.547546, 0.438577, 0.438577,                                  # 腰部
        0.438577, 0.438577, 0.438577, 0.438577, 0.438577,            # 左臂
        0.074501, 0.074501,                                          # 左手腕
        0.438577, 0.438577, 0.438577, 0.438577, 0.438577,            # 右臂
        0.074501, 0.074501                                             # 右手腕
    ]
    
    # 力矩限制 (从文档中提取)
    torque_limits: list[float] = [
        88.0, 139.0, 88.0, 139.0, 50.0, 50.0,        # 左腿
        88.0, 139.0, 88.0, 139.0, 50.0, 50.0,        # 右腿
        88.0, 50.0, 50.0,                            # 腰部
        25.0, 25.0, 25.0, 25.0, 25.0,              # 左臂
        5.0, 5.0,                                    # 左手腕
        25.0, 25.0, 25.0, 25.0, 25.0,              # 右臂
        5.0, 5.0                                     # 右手腕
    ]


class G1KungFuAthletePolicyCfg(PolicyCfg):
    """G1 KungFuAthlete Policy Configuration"""
    model_config = {"arbitrary_types_allowed": True}
    
    robot: str = "g1"
    policy_type: str = "KungFuAthletePolicy"
    policy_name: str = "1307"
    
    # 动作文件配置
    motion_file: str = "1307.npz"
    
    @property
    def motion_file_path(self) -> str:
        """Path to the motion file"""
        from robojudo.config import ASSETS_DIR
        motion_file = ASSETS_DIR / f"motions/{self.robot}/KungFuAthlete/{self.motion_file}"
        return motion_file.as_posix()
    
    obs_dof: G1KungFuAthleteDoF = G1KungFuAthleteDoF()
    action_dof: G1KungFuAthleteDoF = None
    
    use_onnx: bool = False
    
    @property
    def policy_file(self) -> str:
        from robojudo.config import ASSETS_DIR
        ext = "onnx" if self.use_onnx else "pt"
        policy_file = ASSETS_DIR / f"models/{self.robot}/KungFuAthlete/{self.policy_name}.{ext}"
        return policy_file.as_posix()
    
    @property
    def onnx_policy_file(self) -> str:
        from robojudo.config import ASSETS_DIR
        policy_file = ASSETS_DIR / f"models/{self.robot}/KungFuAthlete/{self.policy_name}.onnx"
        return policy_file.as_posix()
    
    # 策略特定配置参数
    disable_autoload: bool = True  # 禁用基类的自动torch.jit.load
    action_scale: list[float] = None  # 使用DoF中的action_scales
    action_clip: float | None = None
    action_beta: float = 1.0
    freq: int = 50
    
    # 观测配置 (从文档中提取)
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
    
    # 观测噪声配置 (从文档中提取)
    class ObsNoiseCfg:
        command: float = 0.0
        motion_anchor_pos_b: float = 0.25
        motion_anchor_ori_b: float = 0.05
        base_lin_vel: float = 0.5
        base_ang_vel: float = 0.2
        joint_pos: float = 0.01
        joint_vel: float = 0.5
        actions: float = 0.0
    
    obs_noise: ObsNoiseCfg = ObsNoiseCfg()
    
    @model_validator(mode='after')
    def validate_config(self) -> 'G1KungFuAthletePolicyCfg':
        if self.action_dof is None:
            self.action_dof = self.obs_dof
        
        # 使用DoF中的action_scales作为action_scale
        if self.action_scale is None:
            self.action_scale = self.obs_dof.action_scales
            
        return self


class G1KungFuAthlete23DoFPolicyCfg(G1KungFuAthletePolicyCfg):
    """G1 KungFuAthlete Policy for 23DoF (if needed)"""
    # 可以在这里添加23DoF版本的特殊配置
    pass
