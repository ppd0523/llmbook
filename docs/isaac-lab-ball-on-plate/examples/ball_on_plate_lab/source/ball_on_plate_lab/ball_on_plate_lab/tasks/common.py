"""태스크 공통 상수와 텐서 함수.

두 작성 워크플로가 모두 이 모듈을 import하므로 MDP 정의가 모르는 사이에
서로 달라지지 않는다.
"""

from __future__ import annotations

import math
import os
from pathlib import Path
from typing import TYPE_CHECKING

import torch
import isaaclab.sim as sim_utils
from isaaclab.actuators import ImplicitActuatorCfg
from isaaclab.assets import ArticulationCfg, RigidObjectCfg
from isaaclab.sim.schemas import CollisionBaseCfg, RigidBodyBaseCfg
from isaaclab.sim.spawners.materials import RigidBodyMaterialBaseCfg

if TYPE_CHECKING:
    from isaaclab.envs import ManagerBasedRLEnv


PLATE_RADIUS = 0.50
BALL_RADIUS = 0.04
PLATE_TOP_Z = 0.21
BALL_START_Z = PLATE_TOP_Z + BALL_RADIUS + 0.002
MAX_TILT_RAD = math.radians(12.0)
INITIAL_RADIUS = 0.5 * PLATE_RADIUS
SAFE_RADIUS = PLATE_RADIUS - BALL_RADIUS
CENTER_RADIUS = 0.25 * PLATE_RADIUS
TARGET_AMPLITUDE = 0.30 * PLATE_RADIUS
TARGET_PERIOD_S = 5.0

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_USD_PATH = PACKAGE_ROOT / "assets" / "usd" / "ball_on_plate" / "ball_on_plate.usd"
PLATE_USD_PATH = Path(os.environ.get("BALL_ON_PLATE_USD", DEFAULT_USD_PATH)).expanduser().resolve()


def make_plate_cfg(prim_path: str) -> ArticulationCfg:
    """백엔드에 독립적인 articulation 설정을 만든다."""

    return ArticulationCfg(
        prim_path=prim_path,
        spawn=sim_utils.UsdFileCfg(usd_path=str(PLATE_USD_PATH)),
        init_state=ArticulationCfg.InitialStateCfg(
            pos=(0.0, 0.0, 0.0),
            joint_pos={"roll_joint": 0.0, "pitch_joint": 0.0},
        ),
        actuators={
            "tilt": ImplicitActuatorCfg(
                joint_names_expr=["roll_joint", "pitch_joint"],
                effort_limit_sim=12.0,
                velocity_limit_sim=2.0,
                stiffness=40.0,
                damping=4.0,
            )
        },
    )


def make_ball_cfg(prim_path: str) -> RigidObjectCfg:
    """두 백엔드가 모두 지원하는 절차적 구(sphere)로 공을 만든다."""

    return RigidObjectCfg(
        prim_path=prim_path,
        spawn=sim_utils.SphereCfg(
            radius=BALL_RADIUS,
            rigid_props=RigidBodyBaseCfg(disable_gravity=False),
            mass_props=sim_utils.MassPropertiesCfg(mass=0.05),
            collision_props=CollisionBaseCfg(),
            physics_material=RigidBodyMaterialBaseCfg(
                static_friction=0.35,
                dynamic_friction=0.30,
                restitution=0.05,
            ),
            visual_material=sim_utils.PreviewSurfaceCfg(
                diffuse_color=(0.95, 0.25, 0.12),
                metallic=0.0,
            ),
        ),
        init_state=RigidObjectCfg.InitialStateCfg(pos=(0.0, 0.0, BALL_START_Z)),
    )


def ball_xy(ball, env_origins: torch.Tensor) -> torch.Tensor:
    """각 환경의 로컬 수평 좌표계에서 본 공 위치."""

    return ball.data.root_pos_w.torch[:, :2] - env_origins[:, :2]


def target_xy(episode_length_buf: torch.Tensor, step_dt: float, moving: bool) -> torch.Tensor:
    """중앙 목표점 또는 최종 프로젝트 태스크가 쓰는 매끄러운 원 궤적."""

    target = torch.zeros((episode_length_buf.shape[0], 2), device=episode_length_buf.device)
    if moving:
        t = episode_length_buf.float() * step_dt
        phase = 2.0 * math.pi * t / TARGET_PERIOD_S
        target[:, 0] = TARGET_AMPLITUDE * torch.cos(phase)
        target[:, 1] = TARGET_AMPLITUDE * torch.sin(phase)
    return target


def task_observation(
    ball,
    plate,
    env_origins: torch.Tensor,
    joint_ids,
    last_action: torch.Tensor,
    episode_length_buf: torch.Tensor,
    step_dt: float,
    moving: bool,
) -> torch.Tensor:
    """두 워크플로가 공유하는 12차원 정책 관측을 반환한다."""

    local_ball_xy = ball_xy(ball, env_origins)
    target = target_xy(episode_length_buf, step_dt, moving)
    return torch.cat(
        (
            (local_ball_xy - target) / PLATE_RADIUS,
            target / PLATE_RADIUS,
            ball.data.root_lin_vel_w.torch[:, :2],
            plate.data.joint_pos.torch[:, joint_ids] / MAX_TILT_RAD,
            plate.data.joint_vel.torch[:, joint_ids],
            last_action,
        ),
        dim=-1,
    )


def reward_terms(
    ball,
    plate,
    env_origins: torch.Tensor,
    joint_ids,
    action: torch.Tensor,
    previous_action: torch.Tensor,
    episode_length_buf: torch.Tensor,
    step_dt: float,
    moving: bool,
) -> dict[str, torch.Tensor]:
    """두 워크플로가 공유하는 이름 붙은 보상 항을 계산한다."""

    local_ball_xy = ball_xy(ball, env_origins)
    target = target_xy(episode_length_buf, step_dt, moving)
    target_radius = torch.linalg.vector_norm(local_ball_xy - target, dim=1) / PLATE_RADIUS
    ball_speed = torch.linalg.vector_norm(ball.data.root_lin_vel_w.torch[:, :2], dim=1)
    tilt = plate.data.joint_pos.torch[:, joint_ids] / MAX_TILT_RAD
    action_rate = action - previous_action
    return {
        "alive": torch.ones_like(target_radius),
        "target": torch.exp(-4.0 * torch.square(target_radius)),
        "speed": torch.square(ball_speed),
        "tilt": torch.sum(torch.square(tilt), dim=1),
        "action_rate": torch.sum(torch.square(action_rate), dim=1),
    }


def weighted_reward(terms: dict[str, torch.Tensor], terminated: torch.Tensor) -> torch.Tensor:
    """공통 보상 가중치를 적용한다."""

    return (
        0.2 * terms["alive"]
        + 1.0 * terms["target"]
        - 0.05 * terms["speed"]
        - 0.02 * terms["tilt"]
        - 0.01 * terms["action_rate"]
        - 2.0 * terminated.float()
    )


def ball_failed(ball, env_origins: torch.Tensor) -> torch.Tensor:
    """공 중심이 사용 가능한 원판 영역을 벗어났거나 그 아래로 떨어졌는지 감지한다."""

    radius = torch.linalg.vector_norm(ball_xy(ball, env_origins), dim=1)
    local_z = ball.data.root_pos_w.torch[:, 2] - env_origins[:, 2]
    return (radius > SAFE_RADIUS) | (local_z < 0.08)


def reset_plate_and_ball(env, env_ids: torch.Tensor) -> None:
    """면적 기준으로 균일한 공 위치와 무작위 속도로 상태를 리셋한다."""

    plate = env.scene["plate"]
    ball = env.scene["ball"]
    count = len(env_ids)
    device = env.device

    plate_root_pose = plate.data.default_root_pose.torch[env_ids].clone()
    plate_root_pose[:, :3] += env.scene.env_origins[env_ids]
    plate_root_vel = plate.data.default_root_vel.torch[env_ids].clone()
    joint_pos = plate.data.default_joint_pos.torch[env_ids].clone()
    joint_vel = plate.data.default_joint_vel.torch[env_ids].clone()
    plate.write_root_pose_to_sim_index(root_pose=plate_root_pose, env_ids=env_ids)
    plate.write_root_velocity_to_sim_index(root_velocity=plate_root_vel, env_ids=env_ids)
    plate.write_joint_position_to_sim_index(position=joint_pos, env_ids=env_ids)
    plate.write_joint_velocity_to_sim_index(velocity=joint_vel, env_ids=env_ids)

    root_pose = ball.data.default_root_pose.torch[env_ids].clone()
    root_pose[:, :3] += env.scene.env_origins[env_ids]
    radius = INITIAL_RADIUS * torch.sqrt(torch.rand(count, device=device))
    angle = 2.0 * math.pi * torch.rand(count, device=device)
    root_pose[:, 0] += radius * torch.cos(angle)
    root_pose[:, 1] += radius * torch.sin(angle)
    root_vel = ball.data.default_root_vel.torch[env_ids].clone()
    root_vel[:, :2].uniform_(-0.15, 0.15)
    ball.write_root_pose_to_sim_index(root_pose=root_pose, env_ids=env_ids)
    ball.write_root_velocity_to_sim_index(root_velocity=root_vel, env_ids=env_ids)


def manager_reset(env: ManagerBasedRLEnv, env_ids: torch.Tensor) -> None:
    """공통 리셋 함수를 event manager에 연결하는 어댑터."""

    reset_plate_and_ball(env, env_ids)
