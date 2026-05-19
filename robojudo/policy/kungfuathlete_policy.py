import logging

import numpy as np
import torch
from scipy.spatial.transform import Rotation as sRot

from robojudo.config.g1.policy.g1_kungfuathlete_policy_cfg import G1KungFuAthletePolicyCfg
from robojudo.policy import policy_registry
from robojudo.policy.base_policy import Policy
from robojudo.utils.util_func import matrix_from_quat, subtract_frame_transforms

logger = logging.getLogger(__name__)


@policy_registry.register
class KungFuAthletePolicy(Policy):
    """KungFuAthlete Policy for G1 Robot
    
    This policy implements motion tracking for KungFuAthlete project
    with 29DOF position control and 154D observations (1307 model config).
    """
    
    def __init__(self, cfg_policy: G1KungFuAthletePolicyCfg, device: str = "cpu"):
        super().__init__(cfg_policy, device)
        
        # 观测维度配置 (1307模型: 154维)
        self.observation_dim = 154

        # 加载动作文件
        self._load_motion_data()
        self.motion_anchor_body_index = -1
        self.command = None
        
        # 加载机器人初始状态
        self._load_robot_init_states()
        
        self.use_onnx = getattr(self.cfg_policy, "use_onnx", False)
        if self.use_onnx:
            self._load_onnx_model()
        else:
            self._load_model()
        
        # 初始化动作历史
        self.last_action = np.zeros(self.num_actions, dtype=np.float32)
        self.current_frame = 0
        self.motion_time = 0.0
        
        # XML body orientation correction: at motion frame 0, the robot's MJ
        # torso xquat differs from the motion data's torso quat because the
        # two G1 XMLs (training vs RoboJuDo) produce different body orientations
        # for the same joint positions. This correction rotates motion anchor
        # quats into the robot's world frame so that subtract_frame_transforms
        # yields identity at frame 0 (matching training behavior).
        self._xml_quat_correction = None  # computed lazily on first update
        
        logger.info(
            f"KungFuAthletePolicy: {self.observation_dim}D obs, {self.num_actions}D actions"
        )
    
    def _load_motion_data(self):
        """加载动作数据文件"""
        try:
            motion_path = self.cfg_policy.motion_file_path
            logger.info(f"Loading motion data from {motion_path}")
            
            self.motion_data = np.load(motion_path)
            
            # 提取关键数据
            self.motion_fps = float(self.motion_data['fps'][0])
            self.motion_joint_pos = self.motion_data['joint_pos']  # (N, 29)
            self.motion_joint_vel = self.motion_data['joint_vel']  # (N, 29)
            self.motion_body_pos = self.motion_data['body_pos_w']  # (N, 30, 3)
            self.motion_body_quat = self.motion_data['body_quat_w']  # (N, 30, 4)
            self.motion_body_lin_vel = self.motion_data['body_lin_vel_w']  # (N, 30, 3)
            self.motion_body_ang_vel = self.motion_data['body_ang_vel_w']  # (N, 30, 3)
            
            self.motion_length = self.motion_joint_pos.shape[0]
            self.motion_dt = 1.0 / self.motion_fps
            
            logger.info(f"Loaded motion data: {self.motion_length} frames, {self.motion_fps} FPS")
            
        except Exception as e:
            logger.error(f"Failed to load motion data: {e}")
            self.motion_data = None
            self.motion_length = 0
            self.motion_fps = 30.0
            self.motion_dt = 1.0 / self.motion_fps
    
    def _load_robot_init_states(self):
        """加载机器人初始状态文件"""
        # 构建机器人初始状态文件路径
        motion_dir = self.cfg_policy.motion_file_path.rsplit('/', 1)[0]
        init_states_path = f"{motion_dir}/robot_init_states_8192.pth"
        
        logger.info(f"Loading robot init states from {init_states_path}")
        
        # 直接载入，不使用try-catch
        self.robot_init_states = torch.load(init_states_path, map_location=self.device)
        
        # 根据实际文件结构提取数据
        if 'dof_pos' in self.robot_init_states:
            # dof_pos: [8192, 29] - 取第一个环境的状态
            self.init_joint_pos = self.robot_init_states['dof_pos'][0]
            logger.info(f"Loaded init joint pos: {self.init_joint_pos.shape}")
        
        if 'robot_root_states_xyzw' in self.robot_init_states:
            # robot_root_states_xyzw: [8192, 13] - [x, y, z, qx, qy, qz, qw, vx, vy, vz, wx, wy, wz]
            self.init_base_pos = self.robot_init_states['robot_root_states_xyzw'][0, :3]  # [x, y, z]
            self.init_base_quat = self.robot_init_states['robot_root_states_xyzw'][0, 3:7]  # [qx, qy, qz, qw]
            self.init_base_lin_vel = self.robot_init_states['robot_root_states_xyzw'][0, 7:10]  # [vx, vy, vz]
            self.init_base_ang_vel = self.robot_init_states['robot_root_states_xyzw'][0, 10:13]  # [wx, wy, wz]
            logger.info(f"Loaded init base pos: {self.init_base_pos.shape}")
            logger.info(f"Loaded init base quat: {self.init_base_quat.shape}")
            logger.info(f"Loaded init base lin vel: {self.init_base_lin_vel.shape}")
            logger.info(f"Loaded init base ang vel: {self.init_base_ang_vel.shape}")
        
        logger.info("Successfully loaded robot init states")
        logger.info(f"Init states keys: {list(self.robot_init_states.keys())}")
    
    def _load_onnx_model(self):
        try:
            import onnxruntime as ort
            model_path = getattr(self.cfg_policy, "onnx_policy_file", self.cfg_policy.policy_file)
            if self.cfg_policy.policy_file.endswith(".onnx"):
                model_path = self.cfg_policy.policy_file
            logger.info(f"Loading ONNX model from {model_path}")
            providers = ['CPUExecutionProvider']
            if hasattr(self.device, 'type') and self.device.type == 'cuda':
                providers.insert(0, 'CUDAExecutionProvider')
            elif isinstance(self.device, str) and "cuda" in self.device:
                providers.insert(0, 'CUDAExecutionProvider')
            self.ort_session = ort.InferenceSession(model_path, providers=providers)
            self.input_names = [i.name for i in self.ort_session.get_inputs()]
            self.output_names = [o.name for o in self.ort_session.get_outputs()]
            logger.info(f"ONNX Model inputs: {self.input_names}")
            logger.info(f"ONNX Model outputs: {self.output_names}")
            self.actor_weights = None
        except Exception as e:
            logger.error(f"Failed to load ONNX model: {e}")
            self.ort_session = None

    def _load_model(self):
        """Load PyTorch checkpoint directly"""
        try:
            logger.info(f"Loading PyTorch checkpoint from {self.cfg_policy.policy_file}")
            checkpoint = torch.load(self.cfg_policy.policy_file, map_location=self.device)
            
            if "model_state_dict" in checkpoint:
                model_state_dict = checkpoint["model_state_dict"]
                self.actor_weights = {}
                for key, value in model_state_dict.items():
                    if key.startswith("actor."):
                        new_key = key.replace("actor.", "")
                        self.actor_weights[new_key] = value.to(self.device)
                
                self.obs_normalizer_mean = model_state_dict["actor_obs_normalizer._mean"].to(self.device)
                self.obs_normalizer_std = model_state_dict["actor_obs_normalizer._std"].to(self.device)
                
                logger.info("Successfully loaded PyTorch checkpoint and extracted actor weights.")
                self.ort_session = None
            else:
                logger.error("model_state_dict not found in checkpoint.")
                self.actor_weights = None
                
        except Exception as e:
            logger.error(f"Failed to load PyTorch checkpoint: {e}")
            self.actor_weights = None

    def _forward_network(self, obs):
        """网络前向传播"""
        if not isinstance(obs, torch.Tensor):
            obs = torch.tensor(obs, dtype=torch.float32, device=self.device)
        
        if len(obs.shape) == 1:
            obs = obs.unsqueeze(0)
            
        # 观测标准化
        obs_norm = (obs - self.obs_normalizer_mean) / self.obs_normalizer_std
        
        # MLP前向传播
        x = obs_norm
        for i in range(0, 6, 2):  # 6层权重: 0,1,2,3,4,5,6
            weight = self.actor_weights[f"{i}.weight"]
            bias = self.actor_weights[f"{i}.bias"]
            x = torch.nn.functional.elu(torch.matmul(x, weight.T) + bias)
        
        # 输出层
        action = torch.matmul(x, self.actor_weights["6.weight"].T) + self.actor_weights["6.bias"]
        return action

    def get_observation(self, env_data, ctrl_data) -> tuple[np.ndarray, dict]:
        """获取154维观测值 (1307模型配置)
        
        观测项分解:
        - command: 58维 - 运动命令参数
        - motion_anchor_ori_b: 6维 - 锚点方向(身体坐标系)
        - base_ang_vel: 3维 - 基座角速度
        - joint_pos: 29维 - 关节位置
        - joint_vel: 29维 - 关节速度
        - actions: 29维 - 上一步动作
        """
        # 获取环境数据
        dof_pos = env_data.dof_pos
        dof_vel = env_data.dof_vel
        base_ang_vel = env_data.base_ang_vel
        
        # 获取命令和锚点信息
        command, robot_anchor_pos_w, robot_anchor_quat_w, anchor_pos_w, anchor_quat_w, hand_pose = self._get_command(
            env_data, ctrl_data
        )
        
        # 计算相对位置和方向
        pos, ori = subtract_frame_transforms(
            robot_anchor_pos_w, robot_anchor_quat_w, anchor_pos_w, anchor_quat_w
        )
        mat = matrix_from_quat(ori)
        
        # 构建观测项
        obs_command = command
        obs_motion_anchor_ori_b = mat[:, :2].flatten()  # 6维
        obs_base_ang_vel = base_ang_vel
        obs_joint_pos_rel = dof_pos - self.default_dof_pos
        obs_joint_vel_rel = dof_vel
        obs_last_action = self.last_action
        
        # 1307配置: 剔除motion_anchor_pos_b和base_lin_vel
        obs_prop = np.concatenate(
            [
                obs_command,              # 58维
                obs_motion_anchor_ori_b,  # 6维
                obs_base_ang_vel,         # 3维
                obs_joint_pos_rel,         # 29维
                obs_joint_vel_rel,         # 29维
                obs_last_action,           # 29维
            ]
        )
        
        # 验证维度
        assert obs_prop.shape[0] == self.observation_dim, (
            f"Expected {self.observation_dim}D obs, got {obs_prop.shape[0]}D"
        )
        
        extras = {
            "pos": pos,
            "ori": ori,
            "robot_anchor_pos_w": robot_anchor_pos_w,
            "robot_anchor_quat_w": robot_anchor_quat_w,
            "anchor_pos_w": anchor_pos_w,
            "anchor_quat_w": anchor_quat_w,
            "command": command,
            "hand_pose": hand_pose,
        }
        return obs_prop, extras
    
    def _get_command(self, env_data, ctrl_data):
        assert "BeyondMimicCtrl" in ctrl_data, "BeyondMimicCtrl not found in ctrl_data"
        command = ctrl_data.get("BeyondMimicCtrl")
        self.command = command
        
        robot_quat_w = command["robot_anchor_quat_w"]
        robot_pos_w = command["robot_anchor_pos_w"]
        
        current_timestep = command["timestep"]
        target_timestep = min(current_timestep + 1, self.motion_length - 1)
        
        anchor_idx = 0
        anchor_pos_w_raw = self.motion_body_pos[target_timestep, anchor_idx].copy()
        
        raw_quat_wxyz = self.motion_body_quat[target_timestep, anchor_idx].copy()
        anchor_quat_w_raw = raw_quat_wxyz[[1, 2, 3, 0]]
        
        if self._xml_quat_correction is None:
            if np.allclose(robot_quat_w, [0, 0, 0, 1], atol=1e-6):
                return (
                    command["command"],
                    robot_pos_w,
                    robot_quat_w,
                    anchor_pos_w_raw,
                    anchor_quat_w_raw,
                    command.get("hand_pose", None),
                )
            
            motion_q_frame0 = self.motion_body_quat[0, anchor_idx].copy()[[1, 2, 3, 0]]
            r_robot = sRot.from_quat(robot_quat_w)
            r_motion = sRot.from_quat(motion_q_frame0)
            self._xml_quat_correction = (r_robot * r_motion.inv()).as_quat()
            logger.info(
                f"Computed XML quat correction: {self._xml_quat_correction} "
                f"(robot {robot_quat_w} vs motion {motion_q_frame0} at frame 0)"
            )
        
        r_corr = sRot.from_quat(self._xml_quat_correction)
        anchor_quat_corrected = (r_corr * sRot.from_quat(anchor_quat_w_raw)).as_quat()
        
        return (
            command["command"],
            robot_pos_w,
            robot_quat_w,
            anchor_pos_w_raw,
            anchor_quat_corrected,
            command.get("hand_pose", None),
        )
    
    def get_action(self, obs: np.ndarray) -> np.ndarray:
        assert obs.shape[0] == self.observation_dim, f"Expected {self.observation_dim}D obs, got {obs.shape[0]}D"
        
        if self.use_onnx and hasattr(self, 'ort_session') and self.ort_session is not None:
            try:
                obs_tensor = obs.astype(np.float32)
                with torch.no_grad():
                    ort_inputs = {self.input_names[0]: obs_tensor[None, :]}
                    actions_tensor = self.ort_session.run(self.output_names, ort_inputs)
                raw_action = actions_tensor[0][0]
            except Exception as e:
                logger.error(f"ONNX network inference failed: {e}")
                raw_action = np.zeros(self.num_actions, dtype=np.float32)
        elif hasattr(self, 'actor_weights') and self.actor_weights is not None:
            try:
                with torch.no_grad():
                    action_tensor = self._forward_network(obs)
                    raw_action = action_tensor.cpu().numpy().flatten()
            except Exception as e:
                logger.error(f"Neural network inference failed: {e}")
                raw_action = np.zeros(self.num_actions, dtype=np.float32)

        assert raw_action.shape[0] == self.num_actions, (
            f"Expected {self.num_actions}D action, got {raw_action.shape[0]}D"
        )
        
        self.last_action = raw_action.copy()
        scaled_action = self._post_process_action(raw_action)
        return scaled_action
    
    def _post_process_action(self, action: np.ndarray) -> np.ndarray:
        """动作后处理"""
        # 应用动作缩放
        if hasattr(self.cfg_policy, 'action_scale') and self.cfg_policy.action_scale is not None:
            action = action * np.array(self.cfg_policy.action_scale)
        
        return action
    
    def get_init_dof_pos(self) -> np.ndarray:
        """Return motion frame 0 joint positions.

        In training, the robot starts at motion frame 0 position (via
        _resample_command -> write_joint_state_to_sim). Using motion frame 0
        instead of HOME_KEYFRAME ensures the initial pose matches the
        training distribution for the first observation.
        """
        if hasattr(self, 'motion_joint_pos') and self.motion_joint_pos is not None:
            return self.motion_joint_pos[0].copy()
        return self.default_pos.copy()

    def get_init_qpos(self):
        """Return full MuJoCo qpos for motion frame 0 (teleport initialization).

        Matches training's _resample_command which writes both joint and
        root state to sim simultaneously. Format: [px, py, pz, qw, qx, qy, qz, j0..j28]
        """
        if not hasattr(self, 'motion_data') or self.motion_data is None:
            return None
        try:
            # Pelvis position at frame 0: body_pos_w[0, 0] = [x, y, z]
            pelvis_pos = self.motion_body_pos[0, 0]  # (3,)
            # Pelvis quaternion at frame 0: body_quat_w[0, 0] = [w, x, y, z] (MuJoCo native)
            pelvis_quat = self.motion_body_quat[0, 0]  # (4,) in [w, x, y, z]
            # Joint positions at frame 0
            joint_pos = self.motion_joint_pos[0]  # (29,)

            # Full qpos: [pelvis_pos(3), pelvis_quat(4), joint_pos(29)] = 36 elements
            qpos = np.concatenate([pelvis_pos, pelvis_quat, joint_pos]).astype(np.float64)
            return qpos
        except Exception as e:
            logger.error(f"Failed to build init qpos: {e}")
            return None

    def get_init_qvel(self):
        """Return full MuJoCo qvel for motion frame 0.

        Training sets both base and joint velocities from motion data
        via _resample_command -> write_root_state_to_sim.
        body_lin_vel_w/body_ang_vel_w are in world frame (MuJoCo free joint convention).
        """
        if not hasattr(self, 'motion_joint_vel') or self.motion_joint_vel is None:
            return None
        try:
            # Base velocities from motion data (world frame, matches MuJoCo free joint)
            base_lin_vel = self.motion_body_lin_vel[0, 0].astype(np.float64)  # (3,)
            base_ang_vel = self.motion_body_ang_vel[0, 0].astype(np.float64)  # (3,)
            base_qvel = np.concatenate([base_lin_vel, base_ang_vel])  # (6,)
            # Joint velocities at frame 0
            joint_vel = self.motion_joint_vel[0].astype(np.float64)  # (29,)
            qvel = np.concatenate([base_qvel, joint_vel])
            return qvel
        except Exception as e:
            logger.error(f"Failed to build init qvel: {e}")
            return None

    def reset(self):
        """重置策略状态"""
        self.last_action = np.zeros(self.num_actions, dtype=np.float32)
        self.current_frame = 0
        self.motion_time = 0.0
        self._xml_quat_correction = None  # recompute after reset
        logger.info("KungFuAthletePolicy reset")
    
    def post_step_callback(self, commands: list[str] | None = None):
        """每步回调 (满足基类抽象方法)"""
        if commands:
            logger.debug(f"Received commands: {commands}")
        pass
