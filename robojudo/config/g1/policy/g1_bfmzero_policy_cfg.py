from pathlib import Path
import yaml

from pydantic import ConfigDict, model_validator

from robojudo.policy.policy_cfgs import BFMZeroPolicyCfg
from robojudo.tools.tool_cfgs import DoFConfig


def load_yaml_config(path_config = "assets/models/g1/BFM0/config.yaml"):
    """Load YAML configuration from config.yaml"""
    yaml_path = (
        Path(__file__).parent.parent.parent.parent.parent /
        path_config
    )
    if yaml_path.exists():
        with open(yaml_path, 'r') as f:
            return yaml.safe_load(f)
    return {}


def map_joint_config(joint_names, config_dict, default_value=0.0):
    """Map configuration values to joint names using pattern matching"""
    result = []
    for joint_name in joint_names:
        matched = False
        for pattern, value in config_dict.items():
            if pattern.replace('.*', '') in joint_name:
                result.append(value)
                matched = True
                break
        if not matched:
            result.append(default_value)
    return result



# Load configuration from YAML
_yaml_config = load_yaml_config()


class G1BFMZeroDoF(DoFConfig):
    """G1 BFM Zero DoF configuration with YAML-based parameters"""
    
    joint_names: list[str] = ['left_hip_pitch_joint', 'left_hip_roll_joint', 'left_hip_yaw_joint', 'left_knee_joint', 'left_ankle_pitch_joint', 'left_ankle_roll_joint',
              'right_hip_pitch_joint', 'right_hip_roll_joint', 'right_hip_yaw_joint', 'right_knee_joint', 'right_ankle_pitch_joint', 'right_ankle_roll_joint',
              'waist_yaw_joint', 'waist_roll_joint', 'waist_pitch_joint',
              'left_shoulder_pitch_joint', 'left_shoulder_roll_joint', 'left_shoulder_yaw_joint', 'left_elbow_joint', 
              'left_wrist_roll_joint', 'left_wrist_pitch_joint', 'left_wrist_yaw_joint',
              'right_shoulder_pitch_joint', 'right_shoulder_roll_joint', 'right_shoulder_yaw_joint', 'right_elbow_joint', 
              'right_wrist_roll_joint', 'right_wrist_pitch_joint', 'right_wrist_yaw_joint']
    
    default_pos: list[float] | None = map_joint_config(joint_names, _yaml_config['default_joint_pos'], 0.0)
    stiffness: list[float] | None = map_joint_config(joint_names, _yaml_config['joint_kp'], 0.0)
    damping: list[float] | None = map_joint_config(joint_names, _yaml_config['joint_kd'], 0.0)

    torque_limits: list[float] | None = map_joint_config(joint_names, _yaml_config['joint_effort_limit'])
    action_scales: list[float]  = map_joint_config(joint_names, _yaml_config['action_scale'], 1.0)



class G1BFMZeroPolicyCfg(BFMZeroPolicyCfg):
    robot: str = "g1"

    obs_dof: DoFConfig = G1BFMZeroDoF()
    action_dof: DoFConfig = obs_dof

    action_beta: float = 1.0
    
    # YAML-based configurations
    action_rescale: int = 5
    
    # Observation configurations from YAML
    dof_pos_scale: float = 1.0
    dof_vel_scale: float = 1.0
    projected_gravity_scale: float = 1.0
    base_ang_vel_scale: float = 0.25
    prev_actions_scale: float = 1.0
    history_steps: int = 4
    
    # BFM Zero Task Configuration
    task_type: str = "single"  # Options: "single", "tracking", "reward", "goal"

    # For tracking task
    start: int = 0
    end: int = 2000
    stop: int = 0
    ctx_path: str = "assets/models/g1/BFM0/tracking_inference/zs_7.pkl"  # Path to context file relative to model directory
    gamma: float = 0.8
    window_size: int = 3

    # Override action_scales from the DoF configuration
    # action_scales: list[float] = G1BFMZeroDoF().action_scales or [1.0] * len(G1BFMZeroDoF().joint_names)

    # # For reward task
    # selected_rewards_filter_z: list = None

    # # For goal task
    # selected_goals: list = None


class G1BFMZeroTrackingPolicyCfg(G1BFMZeroPolicyCfg):
    """BFM Zero Policy for tracking tasks"""
    task_type: str = "tracking"
    ctx_path: str = "tracking_inference/zs_7.pkl"
    start: int = 0
    end: int = 2000
    stop: int = 0
    gamma: float = 0.8
    window_size: int = 3


class G1BFMZeroRewardPolicyCfg(G1BFMZeroPolicyCfg):
    """BFM Zero Policy for reward-based tasks"""
    task_type: str = "reward"
    ctx_path: str = "../reward_inference/reward_locomotion.pkl"
    selected_rewards_filter_z: list = [
        {"reward": "move-ego-low0.6-0-0.7", "z_ids": [0]},
        {"reward": "move-ego-90-0.3", "z_ids": [0]},
        {"reward": "move-ego-0-0", "z_ids": [0]},
        {"reward": "spin-arms-5-l-l", "z_ids": [0]},
    ]


class G1BFMZeroGoalPolicyCfg(G1BFMZeroPolicyCfg):
    """BFM Zero Policy for goal-based tasks"""
    task_type: str = "goal"
    ctx_path: str = "../goal_inference/goal_reaching.pkl"
    # selected_goals: list = [
    #     "fallAndGetUp1_subject4_2193",
    #     "dance1_subject3_505", 
    #     "fightAndSports1_subject1_252",
    #     "walk2_subject1_2588",
    # ]

