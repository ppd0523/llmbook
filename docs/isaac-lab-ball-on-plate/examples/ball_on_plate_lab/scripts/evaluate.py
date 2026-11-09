"""고정 시드 에피소드 100개 또는 무작위 행동 기준선을 평가한다.

Isaac Lab 3.0 RSL-RL play 경로를 따르되, 끝없는 viewer 루프를 여는 대신
지표 중심의 유한한 평가를 마친 뒤 종료한다.
"""

from __future__ import annotations

import argparse
import importlib.metadata as metadata
import json
import sys
from pathlib import Path

import gymnasium as gym
import torch
from rsl_rl.runners import OnPolicyRunner

from isaaclab.envs import DirectRLEnvCfg, ManagerBasedRLEnvCfg
from isaaclab_rl.rsl_rl import RslRlBaseRunnerCfg, RslRlVecEnvWrapper, handle_deprecated_rsl_rl_cfg
from isaaclab_tasks.utils import add_launcher_args, launch_simulation, setup_preset_cli
from isaaclab_tasks.utils.hydra import hydra_task_config

import ball_on_plate_lab.tasks  # noqa: F401  외부 태스크를 등록한다.


parser = argparse.ArgumentParser(description="고정 시드로 Ball-on-Plate를 평가한다.")
parser.add_argument("--task", default="BallOnPlate-Direct-v0")
parser.add_argument("--checkpoint", type=Path)
parser.add_argument("--episodes", type=int, default=100)
parser.add_argument("--seed", type=int, default=20260902)
parser.add_argument("--random_policy", action="store_true")
add_launcher_args(parser)
args_cli, remaining_args = setup_preset_cli(parser)
sys.argv = [sys.argv[0]] + remaining_args

if not args_cli.random_policy and args_cli.checkpoint is None:
    parser.error("--random_policy를 쓰지 않으면 --checkpoint가 필요하다")


@hydra_task_config(args_cli.task, "rsl_rl_cfg_entry_point")
def main(env_cfg: ManagerBasedRLEnvCfg | DirectRLEnvCfg, agent_cfg: RslRlBaseRunnerCfg) -> None:
    with launch_simulation(env_cfg, args_cli):
        env_cfg.scene.num_envs = args_cli.episodes
        env_cfg.seed = args_cli.seed
        if args_cli.device is not None:
            env_cfg.sim.device = args_cli.device

        env = gym.make(args_cli.task, cfg=env_cfg)
        installed_version = metadata.version("rsl-rl-lib")
        agent_cfg = handle_deprecated_rsl_rl_cfg(agent_cfg, installed_version)
        wrapped = RslRlVecEnvWrapper(env, clip_actions=agent_cfg.clip_actions)

        policy = None
        if not args_cli.random_policy:
            runner = OnPolicyRunner(wrapped, agent_cfg.to_dict(), log_dir=None, device=agent_cfg.device)
            runner.load(str(args_cli.checkpoint.expanduser().resolve()))
            policy = runner.get_inference_policy(device=env.unwrapped.device)

        torch.manual_seed(args_cli.seed)
        obs = wrapped.get_observations()
        completed = torch.zeros(args_cli.episodes, dtype=torch.bool, device=wrapped.device)
        steps = torch.zeros(args_cli.episodes, device=wrapped.device)
        centered_steps = torch.zeros_like(steps)
        radius_sum = torch.zeros_like(steps)
        survived = torch.zeros_like(completed)

        with torch.inference_mode():
            while not torch.all(completed):
                # 관측 필드 0:2는 공-목표, 2:4는 목표이며 각각 원판 반경으로
                # 정규화되어 있다. 둘을 더하면 정규화된 공 위치가 된다.
                normalized_ball_xy = obs[:, 0:2] + obs[:, 2:4]
                normalized_radius = torch.linalg.vector_norm(normalized_ball_xy, dim=1)
                active = ~completed
                steps[active] += 1
                centered_steps[active] += (normalized_radius[active] <= 0.25).float()
                radius_sum[active] += normalized_radius[active]

                if args_cli.random_policy:
                    actions = 2.0 * torch.rand(
                        (wrapped.num_envs, wrapped.num_actions), device=wrapped.device
                    ) - 1.0
                else:
                    actions = policy(obs)

                obs, _, dones, _ = wrapped.step(actions)
                newly_done = dones.bool() & active
                survived[newly_done] = env.unwrapped.reset_time_outs[newly_done]
                completed |= newly_done
                if policy is not None:
                    policy.reset(dones)

        total_steps = steps.sum().clamp_min(1.0)
        report = {
            "task": args_cli.task,
            "episodes": args_cli.episodes,
            "seed": args_cli.seed,
            "policy": "random" if args_cli.random_policy else str(args_cli.checkpoint),
            "survival_rate": survived.float().mean().item(),
            "center_residence_rate": (centered_steps.sum() / total_steps).item(),
            "mean_normalized_radius": (radius_sum.sum() / total_steps).item(),
            "pass_survival_90pct": survived.float().mean().item() >= 0.90,
            "pass_center_80pct": (centered_steps.sum() / total_steps).item() >= 0.80,
        }
        print(json.dumps(report, indent=2, ensure_ascii=False))
        wrapped.close()


if __name__ == "__main__":
    main()
