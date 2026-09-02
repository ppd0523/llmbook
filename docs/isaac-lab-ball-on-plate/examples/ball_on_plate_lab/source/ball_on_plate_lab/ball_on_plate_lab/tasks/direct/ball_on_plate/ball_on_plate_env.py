"""Direct implementation of Ball-on-Plate."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING

import torch
import isaaclab.sim as sim_utils
from isaaclab.assets import Articulation, RigidObject
from isaaclab.envs import DirectRLEnv

from ...common import (
    MAX_TILT_RAD,
    PLATE_RADIUS,
    ball_failed,
    ball_xy,
    reset_plate_and_ball,
    reward_terms,
    task_observation,
    weighted_reward,
)

if TYPE_CHECKING:
    from .ball_on_plate_env_cfg import BallOnPlateEnvCfg


class BallOnPlateEnv(DirectRLEnv):
    """Keep a rolling ball near a target by tilting a circular plate."""

    cfg: BallOnPlateEnvCfg

    def __init__(self, cfg: BallOnPlateEnvCfg, render_mode: str | None = None, **kwargs):
        super().__init__(cfg, render_mode, **kwargs)
        self._tilt_joint_ids, _ = self.plate.find_joints(["roll_joint", "pitch_joint"], preserve_order=True)
        self._actions = torch.zeros((self.num_envs, 2), device=self.device)
        self._previous_actions = torch.zeros_like(self._actions)

    def _setup_scene(self) -> None:
        self.plate = Articulation(self.cfg.plate_cfg)
        self.ball = RigidObject(self.cfg.ball_cfg)
        self.scene.clone_environments(copy_from_source=False)
        if self.device == "cpu":
            self.scene.filter_collisions(global_prim_paths=[])
        self.scene.articulations["plate"] = self.plate
        self.scene.rigid_objects["ball"] = self.ball

        light_cfg = sim_utils.DomeLightCfg(intensity=1800.0, color=(0.85, 0.88, 1.0))
        light_cfg.func("/World/DomeLight", light_cfg)

    def _pre_physics_step(self, actions: torch.Tensor) -> None:
        self._previous_actions.copy_(self._actions)
        self._actions.copy_(torch.clamp(actions, -1.0, 1.0))

    def _apply_action(self) -> None:
        self.plate.set_joint_position_target_index(
            target=MAX_TILT_RAD * self._actions,
            joint_ids=self._tilt_joint_ids,
        )

    def _get_observations(self) -> dict[str, torch.Tensor]:
        policy = task_observation(
            self.ball,
            self.plate,
            self.scene.env_origins,
            self._tilt_joint_ids,
            self._actions,
            self.episode_length_buf,
            self.step_dt,
            self.cfg.moving_target,
        )
        return {"policy": policy}

    def _get_rewards(self) -> torch.Tensor:
        terms = reward_terms(
            self.ball,
            self.plate,
            self.scene.env_origins,
            self._tilt_joint_ids,
            self._actions,
            self._previous_actions,
            self.episode_length_buf,
            self.step_dt,
            self.cfg.moving_target,
        )
        return weighted_reward(terms, self.reset_terminated)

    def _get_dones(self) -> tuple[torch.Tensor, torch.Tensor]:
        terminated = ball_failed(self.ball, self.scene.env_origins)
        time_out = self.episode_length_buf >= self.max_episode_length - 1
        return terminated, time_out

    def _reset_idx(self, env_ids: Sequence[int] | None) -> None:
        if env_ids is None:
            env_ids = self.plate._ALL_INDICES

        survived = self.reset_time_outs[env_ids].float()
        local_radius = torch.linalg.vector_norm(ball_xy(self.ball, self.scene.env_origins)[env_ids], dim=1)
        self.extras.setdefault("log", {})["Metrics/survival_rate"] = survived.mean().item()
        self.extras["log"]["Metrics/mean_normalized_radius"] = (local_radius / PLATE_RADIUS).mean().item()

        super()._reset_idx(env_ids)
        reset_plate_and_ball(self, env_ids)
        self._actions[env_ids] = 0.0
        self._previous_actions[env_ids] = 0.0
