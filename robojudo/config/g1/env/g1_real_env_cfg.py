from typing import Literal

from robojudo.environment.env_cfgs import UnitreeEnvCfg

from .g1_env_cfg import G1EnvCfg


class G1UnitreeCfg(UnitreeEnvCfg.UnitreeCfg):
    robot: Literal["h1", "g1"] = "g1"

    msg_type: Literal["hg", "go"] = "hg"
    hand_type: Literal["Dex-3", "Inspire", "NONE"] = "NONE"

    enable_odometry: bool = True


class G1RealEnvCfg(G1EnvCfg, UnitreeEnvCfg):
    # env_type: str = UnitreeEnvCfg.model_fields["env_type"].default
    env_type: str = "UnitreeCppEnv"
    # ====== ENV CONFIGURATION ======
    unitree: UnitreeEnvCfg.UnitreeCfg = G1UnitreeCfg(
        net_if="eth0",
    )

    odometry_type: Literal["NONE", "DUMMY", "UNITREE", "ZED"] = "UNITREE"

    joint2motor_idx: list[int] | None = None  # list(range(0, 29))


class G1WithHandRealEnvCfg(G1EnvCfg, UnitreeEnvCfg):
    # env_type: str = UnitreeEnvCfg.model_fields["env_type"].default
    env_type: str = "UnitreeCppEnv"
    # ====== ENV CONFIGURATION ======
    unitree: UnitreeEnvCfg.UnitreeCfg = G1UnitreeCfg(
        net_if="eth0",
        hand_type="Dex-3",
    )

    odometry_type: Literal["NONE", "DUMMY", "UNITREE", "ZED"] = "DUMMY"
    # zed_cfg: ZedOdometryCfg | None = ZedOdometryCfg(
    #     server_ip="192.168.123.167",
    #     pos_offset=[0.0, 0.0, 0.9],
    #     zero_align=True,
    # )

    joint2motor_idx: list[int] | None = None  # list(range(0, 29))


# class G1RealServEnvCfg(G1EnvCfg, UnitreeEnvCfg):
#     """
#     Real G1 Robot Environment for Serving-Mimic pipeline.
#     Supports multiple poses and interpolation between states.
#     """
    
#     env_type: str = "UnitreeCppEnv"
    
#     # ====== ENV CONFIGURATION ======
#     unitree: UnitreeEnvCfg.UnitreeCfg = G1UnitreeCfg(
#         net_if="eth0",
#     )

#     odometry_type: Literal["NONE", "DUMMY", "UNITREE", "ZED"] = "UNITREE"

#     joint2motor_idx: list[int] | None = None  # list(range(0, 29))
    
#     # ====== POSE CONFIGURATION ======
#     # Standing pose (default)
#     standing_pos: list[float] = [
#         *[-0.1, 0.0, 0.0, 0.3, -0.2, 0.0],  # Left leg
#         *[-0.1, 0.0, 0.0, 0.3, -0.2, 0.0],  # Right leg
#         *[0, 0, 0],  # Waist
#         *[0, 0, 0, 0, 0, 0, 0],  # Left arm
#         *[0, 0, 0, 0, 0, 0, 0],  # Right arm
#     ]
    
#     # Sitting pose 端盘子
#     sitting_pos: list[float] = [
#         *[-1.2, 0.0, 0.0, 1.5, -0.2, 0.0],  # Left leg
#         *[-1.2, 0.0, 0.0, 1.5, -0.2, 0.0],  # Right leg
#         *[0, 0, 0],  # Waist
#         # *[-0.4, 0, 0, 0, -1.5, 0, 0],  # Left arm
#         # *[-0.4, 0, 0, 0, 1.5, 0, 0],  # Right arm
#         *[0., 0, 0, 0, 0, 0, 0],  # Left arm
#         *[0., 0, 0, 0, 0, 0, 0],  # Right arm
#     ]
    
#     # Prepare pose (sitting instead of standing)
#     prepare_pos: list[float] = [
#         *[-1.2, 0.0, 0.0, 1.5, -0.2, 0.0],  # Left leg
#         *[-1.2, 0.0, 0.0, 1.5, -0.2, 0.0],  # Right leg
#         *[0, 0, 0],  # Waist
#         # *[-0.4, 0, 0, 0, -1.5, 0, 0],  # Left arm
#         # *[-0.4, 0, 0, 0, 1.5, 0, 0],  # Right arm
#         *[0., 0, 0, 0, 0, 0, 0],  # Left arm
#         *[0., 0, 0, 0, 0, 0, 0],  # Right arm

#     ]
    
#     # Serving pose (hand changes, lower body default)
#     # serving_pos: list[float] = [
#     #     *[-0.1, 0.0, 0.0, 0.3, -0.2, 0.0],  # Left leg (default)
#     #     *[-0.1, 0.0, 0.0, 0.3, -0.2, 0.0],  # Right leg (default)
#     #     *[0, 0, 0],  # Waist
#     #     *[-0.4, 0, 0, 0, -1.5, 0, 0],  # Left arm (hand changes)
#     #     *[-0.4, 0, 0, 0, 1.5, 0, 0],  # Right arm (hand changes)
#     # ]
    
#     # ====== INTERPOLATION CONFIGURATION ======
#     # Default interpolation time (seconds)
#     interpolation_time: float = 2.0
    
#     # Prepare mode interpolation time (half of default)
#     prepare_interpolation_time: float = 1.0
    
#     # Enable smooth transitions between states
#     enable_smooth_transition: bool = True
    
#     # Transition speed factor (lower = slower, higher = faster)
#     transition_speed: float = 1.0
