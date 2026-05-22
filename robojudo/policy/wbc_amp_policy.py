import logging
from collections import deque

import numpy as np
import onnxruntime as ort

from robojudo.policy import Policy, policy_registry
from robojudo.policy.policy_cfgs import WbcAmpPolicyCfg
from robojudo.utils.util_func import command_remap, get_gravity_orientation

logger = logging.getLogger(__name__)


@policy_registry.register
class WbcAmpPolicy(Policy):
    """WBC_FSM AMP Policy implementation.
    Source: /home/hero/Projects/Robotics/Sim2Real/wbc_fsm
    Model: model/loco/amp_0309_1.onnx
    """

    cfg_policy: WbcAmpPolicyCfg

    def __init__(self, cfg_policy: WbcAmpPolicyCfg, device: str = "cpu"):
        super().__init__(cfg_policy=cfg_policy, device=device)

        self.cfg_policy = cfg_policy
        self.device = device
        self.policy_file = cfg_policy.policy_file
        self.commands_map = self.cfg_policy.commands_map
        self.default_dof_pos = np.array(self.cfg_policy.obs_dof.default_pos, dtype=np.float32)

        self._load_onnx_model()

        self.cfg_obs_dof = cfg_policy.obs_dof
        self.cfg_action_dof = cfg_policy.action_dof
        self.default_pos = self.default_dof_pos

        self.max_linear_vel = self.cfg_policy.max_cmd[0]
        self.max_lateral_vel = self.cfg_policy.max_cmd[1]
        self.max_angular_vel = self.cfg_policy.max_cmd[2]

        self.reset()

    def reset(self):
        """Reset policy state - init history buffer with zero observations."""
        self.timestep = 0
        self.last_action = np.zeros(self.cfg_policy.action_dof.num_dofs, dtype=np.float32)

        # Init frame buffer (frame-interleaved format: [frame0, frame1, frame2, frame3])
        robot_state_dim = getattr(self.cfg_policy, 'robot_state_dim', 96)
        self._history_length = self.cfg_policy.history_length
        self._frame_buf = deque(
            [np.zeros(robot_state_dim, dtype=np.float32) for _ in range(self._history_length)],
            maxlen=self._history_length,
        )

    def _load_onnx_model(self):
        """Load ONNX model using ONNX Runtime."""
        model_path = self.policy_file

        providers = ['CPUExecutionProvider']
        if hasattr(self.device, 'type') and self.device.type == 'cuda':
            providers.insert(0, 'CUDAExecutionProvider')

        self.ort_session = ort.InferenceSession(model_path, providers=providers)
        self.input_names = [input.name for input in self.ort_session.get_inputs()]
        self.output_names = [output.name for output in self.ort_session.get_outputs()]

        logger.info(f"Loaded WBC AMP ONNX model: {model_path}")
        logger.info(f"ONNX Model inputs: {self.input_names}")
        logger.info(f"ONNX Model outputs: {self.output_names}")

    def _get_commands(self, ctrl_data):
        """Process velocity commands from keyboard/joystick."""
        commands = np.zeros(3)
        for key in ctrl_data.keys():
            if key in ["JoystickCtrl", "UnitreeCtrl"]:
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
        """Compute observation vector (frame-interleaved format).

        C++ reference: State_Amp::_observations_compute()
        _robot_state_obs_buf = [frame0(96), frame1(96), frame2(96), frame3(96)]
        Each frame: 96 dim = 3(ang_vel) + 3(gravity) + 3(commands) + 29(dof_pos) + 29(dof_vel) + 29(action)
        """
        commands = self._get_commands(ctrl_data)
        gravity_orientation = get_gravity_orientation(env_data.base_quat)

        # Build current frame (96-dim)
        current_frame = np.concatenate([
            env_data.base_ang_vel * self.cfg_policy.obs_scales.ang_vel,
            gravity_orientation * self.cfg_policy.obs_scales.gravity,
            commands * self.cfg_policy.obs_scales.command,
            (env_data.dof_pos - self.default_dof_pos) * self.cfg_policy.obs_scales.dof_pos,
            env_data.dof_vel * self.cfg_policy.obs_scales.dof_vel,
            self.last_action,
        ])

        # Push to frame buffer (deque, auto-discards oldest)
        self._frame_buf.append(current_frame)

        # Concatenate frames in order [frame0, frame1, frame2, frame3]
        obs = np.concatenate(list(self._frame_buf))
        obs = np.clip(obs, -100.0, 100.0)

        extras = {
            "commands": commands,
        }
        return obs, extras

    def get_action(self, obs: np.ndarray) -> np.ndarray:
        """Run ONNX inference and post-process action.

        Processing: ONNX inference -> smoothing -> clip -> scale
        Note: default_pos is NOT added here (handled by PD target computation in pipeline)
        """
        obs_tensor = obs.astype(np.float32)
        ort_inputs = {self.input_names[0]: obs_tensor[None, :]}
        actions_tensor = self.ort_session.run(self.output_names, ort_inputs)
        action = actions_tensor[0][0]

        action = (1 - self.action_beta) * self.last_action + self.action_beta * action

        if self.action_clip is not None:
            action = np.clip(action, -self.action_clip, self.action_clip)

        self.last_action = action.copy()
        action = action * self.action_scale

        return action

    def post_step_callback(self, commands):
        """Handle post-step commands."""
        self.timestep += 1
