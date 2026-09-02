"""Gymnasium registrations for Manager-based Ball-on-Plate."""

import gymnasium as gym

from ... import agents


gym.register(
    id="BallOnPlate-Manager-v0",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": f"{__name__}.ball_on_plate_env_cfg:BallOnPlateEnvCfg",
        "rsl_rl_cfg_entry_point": f"{agents.__name__}.rsl_rl_ppo_cfg:BallOnPlatePPORunnerCfg",
    },
)

gym.register(
    id="BallOnPlate-Tracking-Manager-v0",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": f"{__name__}.ball_on_plate_env_cfg:BallOnPlateTrackingEnvCfg",
        "rsl_rl_cfg_entry_point": f"{agents.__name__}.rsl_rl_ppo_cfg:BallOnPlatePPORunnerCfg",
    },
)
