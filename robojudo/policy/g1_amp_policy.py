import numpy as np
import torch
import onnxruntime as ort

from robojudo.policy import Policy, policy_registry
from robojudo.utils.util_func import command_remap, get_gravity_orientation
from robojudo.config.g1.policy.g1_amp_policy_cfg import G1AmpWalkPolicyCfg, G1AmpRunWalkPolicyCfg,G1AmpRecoveryPolicyCfg
from robojudo.policy.unitree_policy import UnitreePolicy


@policy_registry.register
class G1AmpPolicy(Policy):
    """
    Old
    """
    cfg_policy: G1AmpWalkPolicyCfg

    def __init__(self, cfg_policy, device):
        super().__init__(cfg_policy=cfg_policy, device=device)

        # Initialize basic attributes without calling super().__init__
        self.cfg_policy = cfg_policy
        self.device = device
        self.policy_file = cfg_policy.policy_file
        self.commands_map = self.cfg_policy.commands_map
        self.default_dof_pos = np.array(self.cfg_policy.obs_dof.default_pos, dtype=np.float32)

        
        # Add cfg_obs_dof for compatibility
        self.cfg_obs_dof = cfg_policy.obs_dof
        self.cfg_action_dof = cfg_policy.action_dof
        self.default_pos = self.default_dof_pos  # Alias for compatibility
        
        # Velocity control parameters
        self.max_linear_vel = self.cfg_policy.max_cmd[0]
        self.max_lateral_vel = self.cfg_policy.max_cmd[1] 
        self.max_angular_vel = self.cfg_policy.max_cmd[2]
        
        self.reset()

    def reset(self):
        """Reset policy state."""
        self.timestep = 0
        self.last_action = np.zeros(self.cfg_policy.action_dof.num_dofs, dtype=np.float32)
        # unitree
        self._init_history(np.zeros(self.history_obs_size))
        # wogait
        # history_obs_dims = self.cfg_policy.history_obs_dims
        # default_history = [np.zeros(dim, dtype=np.float32) for dim in history_obs_dims.values()]
        # self._init_history(default_history)

    def _get_commands(self, ctrl_data):
        """
        Process velocity commands from keyboard/joystick.
        """
        commands = np.zeros(3)
        for key in ctrl_data.keys():
            if key in ["KeyboardCtrl"]:
                keys = ctrl_data[key]["keyboard_event"]
                for event in keys:
                    if event["type"] == "keyboard" and event["pressed"]:
                        # unitree_rl_mjlab style keyboard mapping
                        value = 1.0
                        match event["name"]:
                            case "w":
                                commands[0] = command_remap(value, self.cfg_policy.commands_map[0])
                            case "s":
                                commands[0] = command_remap(-value, self.cfg_policy.commands_map[0])
                            case "a":
                                commands[1] = command_remap(-value, self.cfg_policy.commands_map[1])
                            case "d":
                                commands[1] = command_remap(value, self.cfg_policy.commands_map[1])
                            case "q":
                                commands[2] = command_remap(-value, self.cfg_policy.commands_map[2])
                            case "e":
                                commands[2] = command_remap(value, self.cfg_policy.commands_map[2])
                break
                
            elif key in ["JoystickCtrl", "UnitreeCtrl"]:
                axes = ctrl_data[key]["axes"]
                lx, ly, rx, ry = axes["LeftX"], axes["LeftY"], axes["RightX"], axes["RightY"]
                
                commands[0] = command_remap(ly, self.cfg_policy.commands_map[0])
                commands[1] = command_remap(lx, self.cfg_policy.commands_map[1])
                commands[2] = command_remap(rx, self.cfg_policy.commands_map[2])
                break
        return commands

    # def compute_obs(self, env_data, ctrl_data):
    def get_observation(self, env_data, ctrl_data):

        """
        Compute observations for ONNX model with debug output.
        """
        # Get velocity commands
        commands = self._get_commands(ctrl_data)
        
        # Build observation (matching unitree_rl_mjlab format)
        gravity_orientation = get_gravity_orientation(env_data.base_quat)
        obs = np.concatenate([
            env_data.base_ang_vel * self.cfg_policy.obs_scales.ang_vel,
            gravity_orientation * self.cfg_policy.obs_scales.gravity,
            commands * self.cfg_policy.obs_scales.command * np.array(self.cfg_policy.max_cmd),
            (env_data.dof_pos - self.default_dof_pos) * self.cfg_policy.obs_scales.dof_pos,
            env_data.dof_vel * self.cfg_policy.obs_scales.dof_vel,
            self.last_action,
        ])

        extras = {
            "commands": commands,
            # "velocity_command": commands,
        }
        
        return obs, extras

    def post_step_callback(self, commands):
        """Required abstract method implementation - pipeline only passes commands."""
        self.timestep += 1  # 更新步数用于调试




@policy_registry.register
# class G1AmpRunWalkPolicy(UnitreePolicy):
class G1AmpRunWalkPolicy(Policy):

    """
    New
    history_obs_dims: dict[str, int] = {
        "ang_vel": 3,
        "root_local_rot_tan_norm": 6, 
        "commands": 3,
        "dof_pos": obs_dof.num_dofs,
        "dof_vel": obs_dof.num_dofs,
        "actions": action_dof.num_dofs,
        "key_body_pos_b": 6*3,
    }
    """
    
    cfg_policy: G1AmpRunWalkPolicyCfg

    def __init__(self, cfg_policy, device):
        super().__init__(cfg_policy=cfg_policy, device=device)

        # Initialize basic attributes without calling super().__init__
        self.cfg_policy = cfg_policy
        self.device = device
        self.policy_file = cfg_policy.policy_file
        self.commands_map = self.cfg_policy.commands_map
        self.default_dof_pos = np.array(self.cfg_policy.obs_dof.default_pos, dtype=np.float32)

        # Add cfg_obs_dof for compatibility
        self.cfg_obs_dof = cfg_policy.obs_dof
        self.cfg_action_dof = cfg_policy.action_dof
        self.default_pos = self.default_dof_pos  # Alias for compatibility
        
        # Velocity control parameters
        self.max_linear_vel = self.cfg_policy.max_cmd[0]
        self.max_lateral_vel = self.cfg_policy.max_cmd[1] 
        self.max_angular_vel = self.cfg_policy.max_cmd[2]
        
        self.reset()

    def reset(self):
        self.timestep: int = 0

        history_obs_dims = self.cfg_policy.history_obs_dims
        default_history = [np.zeros(dim, dtype=np.float32) for dim in history_obs_dims.values()]
        self._init_history(default_history)


    # def compute_obs(self, env_data, ctrl_data):
    def get_observation(self, env_data, ctrl_data):

        """
        Compute observations for model.
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
        commands = self._get_commands(ctrl_data)
        root_local_rot_tan_norm = compute_root_local_rot_tan_norm(env_data)
        key_body_pos_b = compute_key_body_pos_b(env_data)
        obs_current = [
            env_data.base_ang_vel * self.cfg_policy.obs_scales.ang_vel,
            root_local_rot_tan_norm * self.cfg_policy.obs_scales.root_local_rot_tan_norm,
            commands * self.cfg_policy.obs_scales.command * self.cfg_policy.max_cmd,
            (env_data.dof_pos - self.default_dof_pos) * self.cfg_policy.obs_scales.dof_pos,
            env_data.dof_vel * self.cfg_policy.obs_scales.dof_vel,
            self.last_action,
            key_body_pos_b * self.cfg_policy.obs_scales.key_body_pos_b,
        ]


        self.history_buf.append(obs_current)

        history_list = [np.concatenate(items, axis=0) for items in zip(*self.history_buf, strict=True)]
        obs = np.concatenate(history_list, axis=0)

        extras = {
            "commands": commands,
        }
        return obs, extras
        

    def post_step_callback(self, commands):
        """Required abstract method implementation - pipeline only passes commands."""
        self.timestep += 1  # 更新步数用于调试

    def _get_commands(self, ctrl_data):
        """
        Process velocity commands from keyboard/joystick.
        """
        commands = np.zeros(3)
        for key in ctrl_data.keys():
            if key in ["JoystickCtrl", "UnitreeCtrl", "KeyboardCtrl"]:
                axes = ctrl_data[key]["axes"]
                lx, ly, rx, ry = axes["LeftX"], axes["LeftY"], axes["RightX"], axes["RightY"]

                commands[0] = command_remap(ly, self.commands_map[0])
                commands[1] = command_remap(lx, self.commands_map[1])
                commands[2] = command_remap(rx, self.commands_map[2])
                break

            if key in ["KeyboardCtrl"]:
                keys = ctrl_data[key]["keyboard_event"]
                for event in keys:
                    if event["type"] == "keyboard":
                        value = event["pressed"] * 1.
                        match event["name"]:
                            case "w":
                                commands[0] = command_remap(value, self.commands_map[0])
                            case "s":
                                commands[0] = command_remap(-value, self.commands_map[0])
                            case "a":
                                commands[1] = command_remap(-value, self.commands_map[1])
                            case "d":
                                commands[1] = command_remap(value, self.commands_map[1])
                            case "e":
                                commands[2] = command_remap(value, self.commands_map[2])
                            case "q":
                                commands[2] = command_remap(-value, self.commands_map[2])
                break
            
        # print(commands)
        return commands
        

@policy_registry.register
class G1AmpRecoveryPolicy(Policy):
    """
    """
    cfg_policy: G1AmpRecoveryPolicyCfg

    def __init__(self, cfg_policy, device):
        super().__init__(cfg_policy=cfg_policy, device=device)
        # Initialize basic attributes without calling super().__init__
        self.cfg_policy = cfg_policy
        self.device = device
        self.policy_file = cfg_policy.policy_file
        self.commands_map = self.cfg_policy.commands_map
        self.default_dof_pos = np.array(self.cfg_policy.obs_dof.default_pos, dtype=np.float32)

        self._load_onnx_model()
        
        # Add cfg_obs_dof for compatibility
        self.cfg_obs_dof = cfg_policy.obs_dof
        self.cfg_action_dof = cfg_policy.action_dof
        self.default_pos = self.default_dof_pos  # Alias for compatibility
        
        # Velocity control parameters
        self.max_linear_vel = self.cfg_policy.max_cmd[0]
        self.max_lateral_vel = self.cfg_policy.max_cmd[1] 
        self.max_angular_vel = self.cfg_policy.max_cmd[2]
        
        self.reset()

    def reset(self):
        self.timestep: int = 0

        history_obs_dims = self.cfg_policy.history_obs_dims
        default_history = [np.zeros(dim, dtype=np.float32) for dim in history_obs_dims.values()]

        self._init_history(default_history)

    def _load_onnx_model(self):
        """Load ONNX model using ONNX Runtime."""
        model_path = self.policy_file

        # Setup ONNX Runtime session
        providers = ['CPUExecutionProvider']
        if hasattr(self.device, 'type') and self.device.type == 'cuda':
            providers.insert(0, 'CUDAExecutionProvider')
        
        self.ort_session = ort.InferenceSession(
            model_path,providers=providers)
        
        # Get input/output names
        self.input_names = [input.name for input in self.ort_session.get_inputs()]
        self.output_names = [output.name for output in self.ort_session.get_outputs()]
        
        print(f"ONNX Model inputs: {self.input_names}")
        print(f"ONNX Model outputs: {self.output_names}")
    def _get_commands(self, ctrl_data):
        """
        Process velocity commands from keyboard/joystick.
        """
        commands = np.zeros(3)
        for key in ctrl_data.keys():
            if key in ["JoystickCtrl", "UnitreeCtrl", "KeyboardCtrl"]:
                axes = ctrl_data[key]["axes"]
                lx, ly, rx, ry = axes["LeftX"], axes["LeftY"], axes["RightX"], axes["RightY"]

                commands[0] = command_remap(ly, self.commands_map[0])
                commands[1] = command_remap(lx, self.commands_map[1])
                commands[2] = command_remap(rx, self.commands_map[2])
                break

            if key in ["KeyboardCtrl"]:
                keys = ctrl_data[key]["keyboard_event"]
                for event in keys:
                    if event["type"] == "keyboard":
                        value = event["pressed"] * 1.
                        match event["name"]:
                            case "w":
                                commands[0] = command_remap(value, self.commands_map[0])
                            case "s":
                                commands[0] = command_remap(-value, self.commands_map[0])
                            case "a":
                                commands[1] = command_remap(-value, self.commands_map[1])
                            case "d":
                                commands[1] = command_remap(value, self.commands_map[1])
                            case "e":
                                commands[2] = command_remap(value, self.commands_map[2])
                            case "q":
                                commands[2] = command_remap(-value, self.commands_map[2])
                break
            
        return commands
    def get_observation(self, env_data, ctrl_data):

        """
        总维度：_robot_state_dim * _actor_state_history_length = 96 * 4 = 384 维

        单帧机器人状态维度：96 维，包含：

        机体角速度（body_ang_vel）：3 维
        投影重力（projected_gravity）：3 维
        速度命令（_vCmdBody）：3 维
        关节位置偏差（dof_pos_vec）：29 维
        关节速度（dof_vel_vec）：29 维
        上一步动作（_action）：29 维
        总计：3 + 3 + 3 + 29 + 29 + 29 = 96 维
        使用 4 帧历史状态堆叠，所以最终观测是 384 维
        """
        
        commands = self._get_commands(ctrl_data)
        gravity_orientation = get_gravity_orientation(env_data.base_quat)
        obs_current = [
            env_data.base_ang_vel * self.cfg_policy.obs_scales.ang_vel,
            gravity_orientation * self.cfg_policy.obs_scales.gravity,
            commands * self.cfg_policy.obs_scales.command * np.array(self.cfg_policy.max_cmd),
            (env_data.dof_pos - self.default_dof_pos) * self.cfg_policy.obs_scales.dof_pos,
            env_data.dof_vel * self.cfg_policy.obs_scales.dof_vel,
            self.last_action,
        ]
        self.history_buf.append(obs_current)
        history_list = [np.concatenate(items, axis=0) for items in zip(*self.history_buf, strict=True)]
        obs = np.concatenate(history_list, axis=0)
        
        
        extras = {
            "commands": commands,
        }
        return obs, extras
        
    def get_action(self, obs: np.ndarray) -> np.ndarray:

        # Prepare input for ONNX model
        obs_tensor = obs.astype(np.float32)
        
        # Run ONNX inference
        with torch.no_grad():
            ort_inputs = {self.input_names[0]: obs_tensor[None, :]}  # Add batch dimension
            actions_tensor = self.ort_session.run(self.output_names, ort_inputs)
        
        # Get action from output
        action = actions_tensor[0][0]#numpy().squeeze()  # Remove batch dimension
        # action_beta: float = 1.0  # action smoothing factor 1的时候不变
        action = (1 - self.action_beta) * self.last_action + self.action_beta * action
        self.last_action = action.copy()
        if self.action_clip is not None:
            action = np.clip(action, -self.action_clip, self.action_clip)

        # Apply action scale from deploy.yaml (exact values)
        if hasattr(self.cfg_policy, 'action_scale'):
            action_scale = np.array(self.cfg_policy.action_scale)
            # action_offset = np.array(self.cfg_policy.action_offset)
            # action = action * action_scale + action_offset
            action = action * action_scale

        return action
    def post_step_callback(self, commands):
        """Required abstract method implementation - pipeline only passes commands."""
        self.timestep += 1  # 更新步数用于调试

################## function ##############################################

def compute_key_body_pos_b(env_data):
    """
    Compute key body positions relative to root in body frame.
    Based on Isaac Lab implementation with proper coordinate transformation.
    验证无误
    
    """
    # Define key body names (6 bodies × 3 coordinates = 18)
    key_body_names = [
        'left_ankle_roll_link', 'right_ankle_roll_link',
        'left_wrist_yaw_link', 'right_wrist_yaw_link', 
        'left_shoulder_roll_link', 'right_shoulder_roll_link'
    ]
    # Get root position and quaternion
    if hasattr(env_data, 'base_pos'):
        root_pos = env_data.base_pos
    else:
        root_pos = env_data.torso_pos  # fallback
        
    if hasattr(env_data, 'base_quat'):
        root_quat = env_data.base_quat  # x, y, z, w
    else:
        root_quat = env_data.torso_quat  # fallback
    
    def quat_apply_inverse(quat, vec):
        """Apply inverse quaternion rotation to vector (x,y,z,w format)."""
        # Convert to w,x,y,z for computation
        w, x, y, z = quat[3], quat[0], quat[1], quat[2]
        xyz = np.array([x, y, z])
        t = np.cross(xyz, vec) * 2
        return vec - w * t + np.cross(xyz, t)
    
    # Get key body positions from fk_info
    key_body_positions = []
    
    for body_name in key_body_names:
        body_data = getattr(env_data.fk_info, body_name)
        body_pos = body_data.pos
        key_body_positions.append(body_pos)
    
    # Convert to numpy array
    key_body_pos_array = np.array(key_body_positions)  # (6, 3)
    
    # Compute relative positions to root in world frame
    key_body_pos_relative = key_body_pos_array - root_pos  # (6, 3)
    
    # Transform to body frame using inverse quaternion
    key_body_pos_body = np.array([
        quat_apply_inverse(root_quat, pos) for pos in key_body_pos_relative
    ])  # (6, 3)
    
    # Flatten to 18D vector (6 bodies × 3 coordinates)
    key_body_pos_b = key_body_pos_body.reshape(-1)
    
    return key_body_pos_b



def compute_root_local_rot_tan_norm(env_data):
    """
    Compute root local rotation tangent and normal vectors.
    Based on correct reference implementation with yaw extraction.
    验证无误
    """
    # Get base quaternion from env_data
    if hasattr(env_data, 'base_quat'):
        base_quat = env_data.base_quat
    # else:
    #     base_quat = env_data.torso_quat  # fallback
    
    # Extract yaw component from quaternion
    def extract_yaw_quat(quat):
        """Extract yaw component from quaternion (x, y, z, w)."""
        x, y, z, w = quat
        yaw = np.arctan2(2 * (w * z + x * y), 1 - 2 * (y * y + z * z))
        # Convert to w,x,y,z format for yaw quaternion, then back to x,y,z,w
        yaw_quat_wxyz = np.array([np.cos(yaw / 2), 0, 0, np.sin(yaw / 2)])
        yaw_quat = np.array([yaw_quat_wxyz[1], yaw_quat_wxyz[2], yaw_quat_wxyz[3], yaw_quat_wxyz[0]])  # x,y,z,w
        # Normalize
        yaw_quat = yaw_quat / np.linalg.norm(yaw_quat)
        return yaw_quat
    
    def quat_conjugate(quat):
        """Compute quaternion conjugate."""
        x, y, z, w = quat
        return np.array([-x, -y, -z, w])
    
    def quat_mul(q1, q2):
        """Multiply two quaternions (x, y, z, w format)."""
        x1, y1, z1, w1 = q1
        x2, y2, z2, w2 = q2
        # Convert to w,x,y,z for multiplication, then back to x,y,z,w
        q1_wxyz = np.array([w1, x1, y1, z1])
        q2_wxyz = np.array([w2, x2, y2, z2])
        
        w1, x1, y1, z1 = q1_wxyz
        w2, x2, y2, z2 = q2_wxyz
        
        # Isaac Lab multiplication formula
        ww = (z1 + x1) * (x2 + y2)
        yy = (w1 - y1) * (w2 + z2)
        zz = (w1 + y1) * (w2 - z2)
        xx = ww + yy + zz
        qq = 0.5 * (xx + (z1 - x1) * (x2 - y2))
        w = qq - ww + (z1 - y1) * (y2 - z2)
        x = qq - xx + (x1 + w1) * (x2 + w2)
        y = qq - yy + (w1 - x1) * (y2 + z2)
        z = qq - zz + (z1 + y1) * (w2 - x2)
        
        result_wxyz = np.array([w, x, y, z])
        # Convert back to x,y,z,w
        return np.array([result_wxyz[1], result_wxyz[2], result_wxyz[3], result_wxyz[0]])
    
    def matrix_from_quat(quat):
        """Convert quaternion to rotation matrix (x, y, z, w format)."""
        x, y, z, w = quat
        # Convert to w,x,y,z for Isaac Lab formula
        quat_wxyz = np.array([w, x, y, z])
        r, i, j, k = quat_wxyz  # r=w, i=x, j=y, k=z
        
        two_s = 2.0 / (r*r + i*i + j*j + k*k)
        return np.array([
            [1 - two_s * (j * j + k * k), two_s * (i * j - k * r), two_s * (i * k + j * r)],
            [two_s * (i * j + k * r), 1 - two_s * (i * i + k * k), two_s * (j * k - i * r)],
            [two_s * (i * k - j * r), two_s * (j * k + i * r), 1 - two_s * (i * i + j * j)]
        ])
    
    # Extract yaw quaternion
    yaw_quat = extract_yaw_quat(base_quat)
    
    # Compute local quaternion (remove yaw component)
    root_quat_local = quat_mul(quat_conjugate(yaw_quat), base_quat)
    
    # Convert to rotation matrix
    root_rotm_local = matrix_from_quat(root_quat_local)
    
    # Extract tangent and normal vectors (first and third columns)
    tan_vec = root_rotm_local[:, 0]  # First column: tangent vector (3,)
    norm_vec = root_rotm_local[:, 2]  # Third column: normal vector (3,)
    
    # Concatenate to get 6D vector
    root_local_rot_tan_norm = np.concatenate([tan_vec, norm_vec])
    
    return root_local_rot_tan_norm