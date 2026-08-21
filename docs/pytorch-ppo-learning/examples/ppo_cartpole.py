"""초심자용 단일 환경 PPO-Clip 구현.

의도적으로 vector environment와 프레임워크 추상화를 사용하지 않는다.
각 텐서가 한 줄의 Gymnasium 경험과 어떻게 연결되는지 보여주는 것이 목적이다.
"""

from __future__ import annotations

import argparse
import csv
import dataclasses
import math
import random
from collections import deque
from dataclasses import dataclass
from pathlib import Path

import gymnasium as gym
import numpy as np
import torch
from torch import Tensor, nn
from torch.distributions import Categorical

from ppo_components import explained_variance, generalized_advantage_estimate


@dataclass
class Config:
    env_id: str = "CartPole-v1"
    seed: int = 42
    total_steps: int = 100_000
    rollout_steps: int = 1024
    update_epochs: int = 10
    minibatch_size: int = 64
    learning_rate: float = 3e-4
    gamma: float = 0.99
    gae_lambda: float = 0.95
    clip_epsilon: float = 0.2
    value_coef: float = 0.5
    entropy_coef: float = 0.01
    max_grad_norm: float = 0.5
    target_kl: float = 0.03
    hidden_size: int = 64
    eval_episodes: int = 10
    eval_interval: int = 0
    checkpoint: str = "ppo_cartpole.pt"
    metrics_csv: str | None = None
    device: str = "auto"


METRIC_FIELDS = (
    "update",
    "steps",
    "learning_rate",
    "return20",
    "policy_loss",
    "value_loss",
    "entropy",
    "approx_kl",
    "clip_fraction",
    "grad_norm",
    "explained_variance",
    "eval_mean",
    "eval_std",
)


def initialize_metrics_csv(path: str | Path) -> Path:
    metrics_path = Path(path)
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    with metrics_path.open("w", newline="", encoding="utf-8") as file:
        csv.DictWriter(file, fieldnames=METRIC_FIELDS).writeheader()
    return metrics_path


def append_metrics_csv(path: str | Path, row: dict[str, float | int]) -> None:
    with Path(path).open("a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=METRIC_FIELDS)
        writer.writerow({field: row[field] for field in METRIC_FIELDS})


def layer_init(layer: nn.Linear, std: float = math.sqrt(2.0)) -> nn.Linear:
    nn.init.orthogonal_(layer.weight, std)
    nn.init.constant_(layer.bias, 0.0)
    return layer


class ActorCritic(nn.Module):
    def __init__(self, observation_size: int, action_size: int, hidden_size: int):
        super().__init__()
        self.actor = nn.Sequential(
            layer_init(nn.Linear(observation_size, hidden_size)),
            nn.Tanh(),
            layer_init(nn.Linear(hidden_size, hidden_size)),
            nn.Tanh(),
            layer_init(nn.Linear(hidden_size, action_size), std=0.01),
        )
        self.critic = nn.Sequential(
            layer_init(nn.Linear(observation_size, hidden_size)),
            nn.Tanh(),
            layer_init(nn.Linear(hidden_size, hidden_size)),
            nn.Tanh(),
            layer_init(nn.Linear(hidden_size, 1), std=1.0),
        )

    def distribution(self, observations: Tensor) -> Categorical:
        return Categorical(logits=self.actor(observations))

    def value(self, observations: Tensor) -> Tensor:
        return self.critic(observations).squeeze(-1)

    def action_and_value(
        self, observations: Tensor, actions: Tensor | None = None
    ) -> tuple[Tensor, Tensor, Tensor, Tensor]:
        distribution = self.distribution(observations)
        if actions is None:
            actions = distribution.sample()
        return (
            actions,
            distribution.log_prob(actions),
            distribution.entropy(),
            self.value(observations),
        )


def select_device(name: str) -> torch.device:
    if name == "auto":
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")
    return torch.device(name)


def seed_everything(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def allocate_rollout(
    steps: int, observation_size: int, device: torch.device
) -> dict[str, Tensor]:
    return {
        "observations": torch.zeros((steps, observation_size), device=device),
        "actions": torch.zeros(steps, dtype=torch.long, device=device),
        "old_log_probs": torch.zeros(steps, device=device),
        "rewards": torch.zeros(steps, device=device),
        "terminated": torch.zeros(steps, dtype=torch.bool, device=device),
        "truncated": torch.zeros(steps, dtype=torch.bool, device=device),
        "values": torch.zeros(steps, device=device),
        "next_values": torch.zeros(steps, device=device),
    }


def collect_rollout(
    env: gym.Env,
    model: ActorCritic,
    current_observation: np.ndarray,
    config: Config,
    device: torch.device,
    recent_returns: deque[float],
    episode_return: float,
    episode_length: int,
    steps: int | None = None,
) -> tuple[dict[str, Tensor], np.ndarray, float, int]:
    observation_size = int(np.prod(env.observation_space.shape))
    rollout_steps = steps or config.rollout_steps
    rollout = allocate_rollout(rollout_steps, observation_size, device)

    for step in range(rollout_steps):
        observation_tensor = torch.as_tensor(
            current_observation, dtype=torch.float32, device=device
        )

        with torch.inference_mode():
            action, log_prob, _, value = model.action_and_value(observation_tensor)

        next_observation, reward, terminated, truncated, _ = env.step(action.item())

        # truncation은 MDP terminal이 아니므로 final observation의 가치를 쓴다.
        with torch.inference_mode():
            if terminated:
                next_value = torch.zeros((), device=device)
            else:
                next_observation_tensor = torch.as_tensor(
                    next_observation, dtype=torch.float32, device=device
                )
                next_value = model.value(next_observation_tensor)

        rollout["observations"][step] = observation_tensor
        rollout["actions"][step] = action
        rollout["old_log_probs"][step] = log_prob
        rollout["rewards"][step] = float(reward)
        rollout["terminated"][step] = terminated
        rollout["truncated"][step] = truncated
        rollout["values"][step] = value
        rollout["next_values"][step] = next_value

        episode_return += float(reward)
        episode_length += 1
        episode_finished = terminated or truncated

        if episode_finished:
            recent_returns.append(episode_return)
            current_observation, _ = env.reset()
            episode_return = 0.0
            episode_length = 0
        else:
            current_observation = next_observation

    advantages, value_targets = generalized_advantage_estimate(
        rewards=rollout["rewards"],
        values=rollout["values"],
        next_values=rollout["next_values"],
        terminated=rollout["terminated"],
        truncated=rollout["truncated"],
        gamma=config.gamma,
        gae_lambda=config.gae_lambda,
    )
    rollout["advantages"] = advantages
    rollout["value_targets"] = value_targets
    return rollout, current_observation, episode_return, episode_length


def update_model(
    model: ActorCritic,
    optimizer: torch.optim.Optimizer,
    rollout: dict[str, Tensor],
    config: Config,
) -> dict[str, float]:
    advantages = rollout["advantages"]
    rollout["advantages"] = (advantages - advantages.mean()) / (
        advantages.std(unbiased=False) + 1e-8
    )

    batch_size = rollout["observations"].shape[0]
    indices = torch.arange(batch_size, device=rollout["observations"].device)
    metric_sums = {
        "policy_loss": 0.0,
        "value_loss": 0.0,
        "entropy": 0.0,
        "approx_kl": 0.0,
        "clip_fraction": 0.0,
        "grad_norm": 0.0,
    }
    minibatches = 0

    for _ in range(config.update_epochs):
        permutation = indices[
            torch.randperm(batch_size, device=indices.device)
        ]
        epoch_kl_values: list[float] = []

        for start in range(0, batch_size, config.minibatch_size):
            minibatch = permutation[start : start + config.minibatch_size]
            _, new_log_prob, entropy, new_value = model.action_and_value(
                rollout["observations"][minibatch], rollout["actions"][minibatch]
            )

            log_ratio = new_log_prob - rollout["old_log_probs"][minibatch]
            ratio = torch.exp(log_ratio)
            minibatch_advantage = rollout["advantages"][minibatch]
            unclipped = ratio * minibatch_advantage
            clipped = (
                torch.clamp(
                    ratio, 1.0 - config.clip_epsilon, 1.0 + config.clip_epsilon
                )
                * minibatch_advantage
            )
            policy_loss = -torch.minimum(unclipped, clipped).mean()
            value_loss = 0.5 * (
                new_value - rollout["value_targets"][minibatch]
            ).pow(2).mean()
            entropy_mean = entropy.mean()
            loss = (
                policy_loss
                + config.value_coef * value_loss
                - config.entropy_coef * entropy_mean
            )

            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            grad_norm = nn.utils.clip_grad_norm_(
                model.parameters(), config.max_grad_norm
            )
            optimizer.step()

            with torch.no_grad():
                approx_kl = ((ratio - 1.0) - log_ratio).mean()
                clip_fraction = (
                    (torch.abs(ratio - 1.0) > config.clip_epsilon).float().mean()
                )

            metric_sums["policy_loss"] += policy_loss.item()
            metric_sums["value_loss"] += value_loss.item()
            metric_sums["entropy"] += entropy_mean.item()
            metric_sums["approx_kl"] += approx_kl.item()
            metric_sums["clip_fraction"] += clip_fraction.item()
            metric_sums["grad_norm"] += float(grad_norm)
            epoch_kl_values.append(approx_kl.item())
            minibatches += 1

        if epoch_kl_values and np.mean(epoch_kl_values) > config.target_kl:
            break

    metrics = {name: total / max(minibatches, 1) for name, total in metric_sums.items()}
    with torch.inference_mode():
        predictions = model.value(rollout["observations"])
        metrics["explained_variance"] = explained_variance(
            rollout["value_targets"], predictions
        ).item()
    return metrics


def evaluate(
    model: ActorCritic,
    config: Config,
    device: torch.device,
    episodes: int | None = None,
) -> tuple[float, float]:
    env = gym.make(config.env_id)
    returns: list[float] = []
    episode_count = episodes or config.eval_episodes
    model.eval()

    for episode in range(episode_count):
        observation, _ = env.reset(seed=config.seed + 10_000 + episode)
        episode_return = 0.0
        finished = False
        while not finished:
            observation_tensor = torch.as_tensor(
                observation, dtype=torch.float32, device=device
            )
            with torch.inference_mode():
                logits = model.actor(observation_tensor)
                action = torch.argmax(logits).item()
            observation, reward, terminated, truncated, _ = env.step(action)
            episode_return += float(reward)
            finished = terminated or truncated
        returns.append(episode_return)

    env.close()
    return float(np.mean(returns)), float(np.std(returns))


def save_checkpoint(
    path: str | Path,
    model: ActorCritic,
    optimizer: torch.optim.Optimizer,
    config: Config,
) -> None:
    checkpoint_path = Path(path)
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "model_state_dict": model.state_dict(),
            "optimizer_state_dict": optimizer.state_dict(),
            "config": dataclasses.asdict(config),
        },
        checkpoint_path,
    )


def build_model(env: gym.Env, config: Config, device: torch.device) -> ActorCritic:
    if not isinstance(env.action_space, gym.spaces.Discrete):
        raise TypeError("이 교육용 구현은 Discrete action space만 지원합니다.")
    if not isinstance(env.observation_space, gym.spaces.Box):
        raise TypeError("이 교육용 구현은 Box observation space만 지원합니다.")
    observation_size = int(np.prod(env.observation_space.shape))
    return ActorCritic(
        observation_size, env.action_space.n, config.hidden_size
    ).to(device)


def train(config: Config) -> tuple[ActorCritic, dict[str, float]]:
    seed_everything(config.seed)
    device = select_device(config.device)
    env = gym.make(config.env_id)
    observation, _ = env.reset(seed=config.seed)
    env.action_space.seed(config.seed)

    model = build_model(env, config, device)
    optimizer = torch.optim.Adam(model.parameters(), lr=config.learning_rate, eps=1e-5)
    recent_returns: deque[float] = deque(maxlen=20)
    episode_return = 0.0
    episode_length = 0
    number_of_updates = math.ceil(config.total_steps / config.rollout_steps)
    metrics: dict[str, float] = {}
    last_periodic_eval_mean = float("nan")
    last_periodic_eval_std = float("nan")
    if config.metrics_csv is not None:
        initialize_metrics_csv(config.metrics_csv)

    for update in range(number_of_updates):
        # 선형 learning-rate 감소는 PPO 정의가 아니라 흔히 쓰는 안정화 선택이다.
        progress = 1.0 - update / max(number_of_updates, 1)
        optimizer.param_groups[0]["lr"] = config.learning_rate * progress

        model.eval()  # dropout/BatchNorm이 없지만 수집 모드를 명시한다.
        steps_this_rollout = min(
            config.rollout_steps,
            config.total_steps - update * config.rollout_steps,
        )
        rollout, observation, episode_return, episode_length = collect_rollout(
            env,
            model,
            observation,
            config,
            device,
            recent_returns,
            episode_return,
            episode_length,
            steps=steps_this_rollout,
        )
        model.train()
        metrics = update_model(model, optimizer, rollout, config)

        mean_return = float(np.mean(recent_returns)) if recent_returns else float("nan")
        completed_steps = min((update + 1) * config.rollout_steps, config.total_steps)
        periodic_eval_mean = float("nan")
        periodic_eval_std = float("nan")
        if config.eval_interval > 0 and (
            (update + 1) % config.eval_interval == 0
            or update + 1 == number_of_updates
        ):
            periodic_eval_mean, periodic_eval_std = evaluate(
                model, config, device, episodes=config.eval_episodes
            )
            last_periodic_eval_mean = periodic_eval_mean
            last_periodic_eval_std = periodic_eval_std
        if config.metrics_csv is not None:
            append_metrics_csv(
                config.metrics_csv,
                {
                    "update": update + 1,
                    "steps": completed_steps,
                    "learning_rate": optimizer.param_groups[0]["lr"],
                    "return20": mean_return,
                    "eval_mean": periodic_eval_mean,
                    "eval_std": periodic_eval_std,
                    **metrics,
                },
            )

        if update == 0 or (update + 1) % 5 == 0 or update + 1 == number_of_updates:
            print(
                f"update={update + 1:03d}/{number_of_updates:03d} "
                f"steps={completed_steps:07d} "
                f"return20={mean_return:7.2f} "
                f"entropy={metrics['entropy']:.3f} "
                f"kl={metrics['approx_kl']:.5f} "
                f"clipfrac={metrics['clip_fraction']:.3f} "
                f"ev={metrics['explained_variance']:.3f}"
            )

    env.close()
    save_checkpoint(config.checkpoint, model, optimizer, config)
    if config.eval_interval > 0 and math.isfinite(last_periodic_eval_mean):
        mean, std = last_periodic_eval_mean, last_periodic_eval_std
    else:
        mean, std = evaluate(model, config, device)
    print(f"evaluation: mean={mean:.1f}, std={std:.1f}, episodes={config.eval_episodes}")
    print(f"checkpoint: {Path(config.checkpoint).resolve()}")
    metrics.update({"eval_mean": mean, "eval_std": std})
    return model, metrics


def load_for_evaluation(config: Config) -> tuple[ActorCritic, torch.device]:
    device = select_device(config.device)
    env = gym.make(config.env_id)
    model = build_model(env, config, device)
    env.close()
    checkpoint = torch.load(config.checkpoint, map_location=device, weights_only=True)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()
    return model, device


def parse_args() -> tuple[Config, bool]:
    parser = argparse.ArgumentParser(description="순수 PyTorch PPO로 CartPole 학습")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--total-steps", type=int, default=100_000)
    parser.add_argument("--device", default="auto")
    parser.add_argument("--checkpoint", default="ppo_cartpole.pt")
    parser.add_argument("--metrics-csv")
    parser.add_argument("--eval-episodes", type=int, default=10)
    parser.add_argument(
        "--eval-interval",
        type=int,
        default=0,
        help="0이면 마지막에만 평가하고, 양수면 해당 update 간격으로 평가합니다.",
    )
    parser.add_argument("--learning-rate", type=float, default=3e-4)
    parser.add_argument("--gae-lambda", type=float, default=0.95)
    parser.add_argument("--clip-epsilon", type=float, default=0.2)
    parser.add_argument("--entropy-coef", type=float, default=0.01)
    parser.add_argument("--update-epochs", type=int, default=10)
    parser.add_argument("--eval-only", action="store_true")
    parser.add_argument("--smoke-test", action="store_true")
    args = parser.parse_args()
    config = Config(
        seed=args.seed,
        total_steps=args.total_steps,
        device=args.device,
        checkpoint=args.checkpoint,
        metrics_csv=args.metrics_csv,
        eval_episodes=args.eval_episodes,
        eval_interval=args.eval_interval,
        learning_rate=args.learning_rate,
        gae_lambda=args.gae_lambda,
        clip_epsilon=args.clip_epsilon,
        entropy_coef=args.entropy_coef,
        update_epochs=args.update_epochs,
    )
    if args.smoke_test:
        config.total_steps = 512
        config.rollout_steps = 128
        config.update_epochs = 2
        config.eval_episodes = 2
    return config, args.eval_only


def main() -> None:
    config, eval_only = parse_args()
    if eval_only:
        model, device = load_for_evaluation(config)
        mean, std = evaluate(model, config, device)
        print(f"evaluation: mean={mean:.1f}, std={std:.1f}")
    else:
        train(config)


if __name__ == "__main__":
    main()
