"""Custom Manager-based MDP terms backed by the shared task definition."""

from __future__ import annotations

import torch

from ...common import (
    MAX_TILT_RAD,
    PLATE_RADIUS,
    ball_failed,
    ball_xy,
    reset_plate_and_ball,
    target_xy,
)


def _assets(env):
    plate = env.scene["plate"]
    ball = env.scene["ball"]
    joint_ids, _ = plate.find_joints(["roll_joint", "pitch_joint"], preserve_order=True)
    return plate, ball, joint_ids


def ball_to_target(env) -> torch.Tensor:
    _, ball, _ = _assets(env)
    target = target_xy(env.episode_length_buf, env.step_dt, env.cfg.moving_target)
    return (ball_xy(ball, env.scene.env_origins) - target) / PLATE_RADIUS


def target_position(env) -> torch.Tensor:
    return target_xy(env.episode_length_buf, env.step_dt, env.cfg.moving_target) / PLATE_RADIUS


def ball_velocity(env) -> torch.Tensor:
    return env.scene["ball"].data.root_lin_vel_w.torch[:, :2]


def plate_position(env) -> torch.Tensor:
    plate, _, joint_ids = _assets(env)
    return plate.data.joint_pos.torch[:, joint_ids] / MAX_TILT_RAD


def plate_velocity(env) -> torch.Tensor:
    plate, _, joint_ids = _assets(env)
    return plate.data.joint_vel.torch[:, joint_ids]


def target_reward(env) -> torch.Tensor:
    return torch.exp(-4.0 * torch.sum(torch.square(ball_to_target(env)), dim=1))


def ball_speed_l2(env) -> torch.Tensor:
    return torch.sum(torch.square(ball_velocity(env)), dim=1)


def plate_tilt_l2(env) -> torch.Tensor:
    return torch.sum(torch.square(plate_position(env)), dim=1)


def action_rate_l2(env) -> torch.Tensor:
    delta = env.action_manager.action - env.action_manager.prev_action
    return torch.sum(torch.square(delta), dim=1)


def ball_out_of_bounds(env) -> torch.Tensor:
    return ball_failed(env.scene["ball"], env.scene.env_origins)


def reset_task(env, env_ids: torch.Tensor) -> None:
    reset_plate_and_ball(env, env_ids)
