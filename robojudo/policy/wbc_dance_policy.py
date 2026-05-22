import logging
from collections import deque

import numpy as np
import onnxruntime as ort

from robojudo.policy import Policy, policy_registry
from robojudo.policy.policy_cfgs import WbcDancePolicyCfg
from robojudo.utils.util_func import get_gravity_orientation

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Math helpers (matching C++ mathTools.h semantics)
# Quaternion format everywhere: (w, x, y, z)
# ---------------------------------------------------------------------------


def _quat_conjugate(q):
    return np.array([q[0], -q[1], -q[2], -q[3]])


def _quat_multiply(q1, q2):
    w1, x1, y1, z1 = q1
    w2, x2, y2, z2 = q2
    return np.array([
        w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2,
        w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2,
        w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2,
        w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2,
    ])


def _quat_inv(q):
    norm_sq = q[0]**2 + q[1]**2 + q[2]**2 + q[3]**2
    conj = _quat_conjugate(q)
    return conj / max(norm_sq, 1e-9)


def _quat_apply(q, v):
    w = q[0]
    xyz = q[1:4]
    t = 2.0 * np.cross(xyz, v)
    return v + w * t + np.cross(xyz, t)


def _quat_apply_inverse(q, v):
    w = q[0]
    xyz = q[1:4]
    t = 2.0 * np.cross(xyz, v)
    return v - w * t + np.cross(xyz, t)


def _yaw_quat(q):
    yaw = np.arctan2(2.0 * (q[0] * q[3] + q[1] * q[2]),
                     1.0 - 2.0 * (q[2]**2 + q[3]**2))
    qyaw = np.array([np.cos(yaw / 2.0), 0.0, 0.0, np.sin(yaw / 2.0)])
    norm = np.sqrt(qyaw[0]**2 + qyaw[3]**2)
    return qyaw / norm


def _matrix_from_quat(q):
    w, x, y, z = q
    two_s = 2.0 / (w*w + x*x + y*y + z*z)
    return np.array([
        [1.0 - two_s * (y*y + z*z), two_s * (x*y - z*w), two_s * (x*z + y*w)],
        [two_s * (x*y + z*w), 1.0 - two_s * (x*x + z*z), two_s * (y*z - x*w)],
        [two_s * (x*z - y*w), two_s * (y*z + x*w), 1.0 - two_s * (x*x + y*y)],
    ])


def _subtract_frame_transforms(t01, q01, t02=None, q02=None):
    q10 = _quat_inv(q01)
    if q02 is not None:
        q12 = _quat_multiply(q10, q02)
    else:
        q12 = q10
    if t02 is not None:
        diff = t02 - t01
        t12 = _quat_apply(q10, diff)
    else:
        t12 = _quat_apply(q10, -t01)
    return t12, q12


def _read_bin_array(filepath, dtype=np.float32):
    """Read custom NPZ binary format used by wbc_fsm."""
    with open(filepath, 'rb') as f:
        magic = f.read(4)
        assert magic == b'NPZ\0', f'Invalid magic in {filepath}: {magic}'
        ndims = np.frombuffer(f.read(4), dtype=np.uint32)[0]
        shape = tuple(np.frombuffer(f.read(4 * ndims), dtype=np.uint32))
        _dtype_size = np.frombuffer(f.read(4), dtype=np.uint32)[0]
        _dtype_code = f.read(1)
        f.seek(3, 1)
        data = np.frombuffer(f.read(), dtype=dtype)
        return data.reshape(shape)


def _qwxyz_from_xyzw(quat_xyzw):
    """Convert (x,y,z,w) to (w,x,y,z)."""
    return np.array([quat_xyzw[3], quat_xyzw[0], quat_xyzw[1], quat_xyzw[2]])


@policy_registry.register
class WbcDancePolicy(Policy):
    """WBC_FSM Dance Policy (motion tracking with reference data)."""

    cfg_policy: WbcDancePolicyCfg

    def __init__(self, cfg_policy: WbcDancePolicyCfg, device: str = "cpu"):
        super().__init__(cfg_policy=cfg_policy, device=device)

        self.cfg_policy = cfg_policy
        self.device = device
        self.policy_file = cfg_policy.policy_file
        self.default_dof_pos = np.array(
            self.cfg_policy.obs_dof.default_pos, dtype=np.float32
        )

        # Load reference motion data
        self._load_motion_data()

        self._load_onnx_model()

        self.cfg_obs_dof = cfg_policy.obs_dof
        self.cfg_action_dof = cfg_policy.action_dof
        self.default_pos = self.default_dof_pos

        self.reset()

    # ------------------------------------------------------------------
    # Motion data loading (matching C++ BinaryArrayReader)
    # ------------------------------------------------------------------

    def _load_motion_data(self):
        folder = self.cfg_policy.motion_path
        logger.info("Loading motion data from: %s", folder)

        self._joint_pos = _read_bin_array(f"{folder}/joint_pos.bin", np.float32)
        self._joint_vel = _read_bin_array(f"{folder}/joint_vel.bin", np.float32)
        self._body_pos_w = _read_bin_array(f"{folder}/body_pos_w.bin", np.float32)
        self._body_quat_w = _read_bin_array(f"{folder}/body_quat_w.bin", np.float32)
        self._body_ang_vel_w = _read_bin_array(
            f"{folder}/body_ang_vel_w.bin", np.float32
        )
        self._body_lin_vel_w = _read_bin_array(
            f"{folder}/body_lin_vel_w.bin", np.float32
        )
        self._fps = _read_bin_array(f"{folder}/fps.bin", np.int64)

        self._motion_frame_count = self._joint_pos.shape[0]
        logger.info(
            "Motion loaded: %d frames, %d joints, fps=%d",
            self._motion_frame_count,
            self._joint_pos.shape[1],
            self._fps[0],
        )

    # ------------------------------------------------------------------
    # ONNX
    # ------------------------------------------------------------------

    def _load_onnx_model(self):
        model_path = self.policy_file
        providers = ["CPUExecutionProvider"]
        if hasattr(self.device, "type") and self.device.type == "cuda":
            providers.insert(0, "CUDAExecutionProvider")
        self.ort_session = ort.InferenceSession(model_path, providers=providers)
        self.input_names = [inp.name for inp in self.ort_session.get_inputs()]
        self.output_names = [out.name for out in self.ort_session.get_outputs()]
        logger.info("Loaded WBC Dance ONNX model: %s", model_path)

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def reset(self):
        self.timestep = 0
        self.last_action = np.zeros(
            self.cfg_policy.action_dof.num_dofs, dtype=np.float32
        )

        # Robot state history buffer (4 frames * 93 = 372)
        robot_state_dim = self.cfg_policy.robot_state_dim
        self._robot_state_obs_buf = np.zeros(
            robot_state_dim * self.cfg_policy.history_length, dtype=np.float32
        )

        # Reference frame tracking
        cfg = self.cfg_policy
        self._refer_idx = cfg.start_idx
        self._end_refer_idx = cfg.end_idx
        if self._end_refer_idx < 0:
            self._end_refer_idx = self._motion_frame_count - 1
        self._pause_flag = False
        self._pause_curr_flag = False
        self._motion_projected_gravity = None

    # ------------------------------------------------------------------
    # Observation
    # ------------------------------------------------------------------

    def get_observation(self, env_data, ctrl_data):
        cfg = self.cfg_policy

        # Advance reference frame (matching C++ State_WBC::run)
        if not self._pause_flag:
            self._refer_idx += 1
        else:
            if not self._pause_curr_flag:
                self._refer_idx = cfg.pause_idx

        # -- Current robot state --
        gravity_orientation = get_gravity_orientation(env_data.base_quat)

        current_robot_state = np.concatenate(
            [
                env_data.base_ang_vel * cfg.obs_scales.ang_vel,
                gravity_orientation,
                (env_data.dof_pos - self.default_dof_pos)
                * cfg.obs_scales.dof_pos,
                env_data.dof_vel * cfg.obs_scales.dof_vel,
                self.last_action,
            ]
        )
        current_robot_state = np.clip(current_robot_state, -100.0, 100.0)

        self._robot_state_obs_buf = np.roll(
            self._robot_state_obs_buf, -len(current_robot_state)
        )
        self._robot_state_obs_buf[-len(current_robot_state):] = current_robot_state

        # -- Build mimic_obs from reference motion --
        mimic_obs = self._build_mimic_obs(gravity_orientation, env_data.base_quat)

        # -- Assemble final observation --
        obs = np.concatenate([mimic_obs, self._robot_state_obs_buf])
        obs = np.clip(obs, -100.0, 100.0)

        extras = {}
        return obs, extras

    def _build_mimic_obs(self, projected_gravity, base_quat_xyzw):
        """Build mimic_obs from reference motion data (matching C++ State_WBC).

        Returns 67-dim array:
            tgt_dof_pos_flat(29) + tgt_dof_vel_flat(29) +
            tgt_anchor_pos_b_flat(3) + tgt_anchor_ori_b_flat(6)
        """
        cfg = self.cfg_policy
        anchor_idx = cfg.anchor_idx
        interval = cfg.frame_interval

        # Current reference frame
        idx = self._refer_idx
        last_idx = idx - interval

        # Clamp
        if idx >= self._end_refer_idx:
            idx = self._end_refer_idx
        elif idx <= 1:
            idx = 1
        if last_idx >= self._end_refer_idx:
            last_idx = self._end_refer_idx
        elif last_idx <= 1:
            last_idx = 1

        # Reference data at idx
        cur_refer_dof_pos = self._joint_pos[idx]
        if self._pause_flag:
            cur_refer_dof_vel = np.zeros(self._joint_pos.shape[1], dtype=np.float32)
        else:
            cur_refer_dof_vel = self._joint_vel[idx]

        cur_refer_anchor_pos = self._body_pos_w[idx, anchor_idx]
        cur_refer_anchor_quat = _qwxyz_from_xyzw(
            self._body_quat_w[idx, anchor_idx]
        )

        # Last-frame reference data (for relative transform)
        last_refer_anchor_pos = self._body_pos_w[last_idx, anchor_idx]
        last_refer_anchor_quat = _qwxyz_from_xyzw(
            self._body_quat_w[last_idx, anchor_idx]
        )

        # Yaw alignment
        base_quat_wxyz = _qwxyz_from_xyzw(base_quat_xyzw)
        base_yaw_quat = _yaw_quat(base_quat_wxyz)
        ref_yaw_quat = _yaw_quat(cur_refer_anchor_quat)
        ref_yaw_quat_conj = _quat_conjugate(ref_yaw_quat)
        yaw_quat_delta = _quat_multiply(base_yaw_quat, ref_yaw_quat_conj)
        aligned_cur_refer_anchor_quat = _quat_multiply(
            yaw_quat_delta, cur_refer_anchor_quat
        )

        # Store motion_projected_gravity for termination check
        gravity_vec = np.array([0.0, 0.0, -1.0], dtype=np.float32)
        motion_proj_grav = _quat_apply_inverse(
            aligned_cur_refer_anchor_quat, gravity_vec
        )
        self._motion_projected_gravity = motion_proj_grav.copy()

        # Relative transform: subtract last frame from current frame
        cur_target_pos, cur_target_quat = _subtract_frame_transforms(
            last_refer_anchor_pos,
            last_refer_anchor_quat,
            cur_refer_anchor_pos,
            cur_refer_anchor_quat,
        )

        # Convert quat to rotation matrix and extract 6 elements
        mat = _matrix_from_quat(cur_target_quat)
        tgt_anchor_ori_b = np.array([
            mat[0, 0], mat[0, 1],
            mat[1, 0], mat[1, 1],
            mat[2, 0], mat[2, 1],
        ], dtype=np.float32)

        # Concatenate all reference components
        tgt_dof_pos_flat = cur_refer_dof_pos.astype(np.float32)
        tgt_dof_vel_flat = cur_refer_dof_vel.astype(np.float32)
        tgt_anchor_pos_b_flat = cur_target_pos.astype(np.float32)

        mimic_obs = np.concatenate([
            tgt_dof_pos_flat,
            tgt_dof_vel_flat,
            tgt_anchor_pos_b_flat,
            tgt_anchor_ori_b,
        ])
        return mimic_obs

    # ------------------------------------------------------------------
    # Action
    # ------------------------------------------------------------------

    def get_action(self, obs: np.ndarray) -> np.ndarray:
        obs_tensor = obs.astype(np.float32)[None, :]
        ort_inputs = {self.input_names[0]: obs_tensor}
        actions_tensor = self.ort_session.run(self.output_names, ort_inputs)
        action = actions_tensor[0][0]

        action = (
            1 - self.action_beta
        ) * self.last_action + self.action_beta * action

        if self.action_clip is not None:
            action = np.clip(action, -self.action_clip, self.action_clip)

        self.last_action = action.copy()
        action = action * self.action_scale

        return action

    def post_step_callback(self, commands):
        self.timestep += 1
