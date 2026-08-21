"""TorchRL 0.13의 primitive를 조립한 PPO 예제.

PyTorch 공식 TorchRL PPO 튜토리얼의 구조를 교육용으로 축소했다.
연속 행동 Pendulum-v1에서 TanhNormal 정책을 사용한다.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass

import torch
from tensordict.nn import TensorDictModule
from tensordict.nn.distributions import NormalParamExtractor
from torch import nn
from torchrl.collectors import Collector
from torchrl.data.replay_buffers import ReplayBuffer
from torchrl.data.replay_buffers.samplers import SamplerWithoutReplacement
from torchrl.data.replay_buffers.storages import LazyTensorStorage
from torchrl.envs import Compose, DoubleToFloat, GymEnv, StepCounter, TransformedEnv
from torchrl.envs.utils import ExplorationType, check_env_specs, set_exploration_type
from torchrl.modules import ProbabilisticActor, TanhNormal, ValueOperator
from torchrl.objectives import ClipPPOLoss
from torchrl.objectives.value import GAE


@dataclass
class Config:
    seed: int = 42
    frames_per_batch: int = 1024
    total_frames: int = 50_000
    sub_batch_size: int = 64
    epochs: int = 10
    learning_rate: float = 3e-4
    gamma: float = 0.99
    gae_lambda: float = 0.95
    clip_epsilon: float = 0.2
    entropy_coeff: float = 1e-4
    max_grad_norm: float = 1.0


def make_environment() -> TransformedEnv:
    return TransformedEnv(
        GymEnv("Pendulum-v1", device="cpu"),
        Compose(DoubleToFloat(), StepCounter()),
    )


def make_modules(
    env: TransformedEnv, hidden_size: int = 64
) -> tuple[ProbabilisticActor, ValueOperator]:
    action_size = env.action_spec.shape[-1]
    actor_network = nn.Sequential(
        nn.LazyLinear(hidden_size),
        nn.Tanh(),
        nn.LazyLinear(hidden_size),
        nn.Tanh(),
        nn.LazyLinear(2 * action_size),
        NormalParamExtractor(),
    )
    actor_parameters = TensorDictModule(
        actor_network,
        in_keys=["observation"],
        out_keys=["loc", "scale"],
    )
    policy = ProbabilisticActor(
        module=actor_parameters,
        spec=env.action_spec,
        in_keys=["loc", "scale"],
        distribution_class=TanhNormal,
        distribution_kwargs={
            "low": env.action_spec.space.low,
            "high": env.action_spec.space.high,
        },
        return_log_prob=True,
    )

    value_network = nn.Sequential(
        nn.LazyLinear(hidden_size),
        nn.Tanh(),
        nn.LazyLinear(hidden_size),
        nn.Tanh(),
        nn.LazyLinear(1),
    )
    value = ValueOperator(module=value_network, in_keys=["observation"])

    # LazyLinear의 shape를 실제 환경 observation으로 확정한다.
    initial = env.reset()
    policy(initial.clone())
    value(initial.clone())
    return policy, value


def train(config: Config) -> None:
    torch.manual_seed(config.seed)
    env = make_environment()
    env.set_seed(config.seed)
    check_env_specs(env)
    policy, value = make_modules(env)

    collector = Collector(
        env,
        policy,
        frames_per_batch=config.frames_per_batch,
        total_frames=config.total_frames,
        split_trajs=False,
        device="cpu",
        auto_register_policy_transforms=True,
    )
    replay_buffer = ReplayBuffer(
        storage=LazyTensorStorage(max_size=config.frames_per_batch),
        sampler=SamplerWithoutReplacement(),
    )
    advantage = GAE(
        gamma=config.gamma,
        lmbda=config.gae_lambda,
        value_network=value,
        average_gae=True,
    )
    loss_module = ClipPPOLoss(
        actor_network=policy,
        critic_network=value,
        clip_epsilon=config.clip_epsilon,
        entropy_bonus=True,
        entropy_coeff=config.entropy_coeff,
        critic_coeff=1.0,
        loss_critic_type="smooth_l1",
    )
    optimizer = torch.optim.Adam(loss_module.parameters(), lr=config.learning_rate)

    collected = 0
    for batch_index, batch in enumerate(collector, start=1):
        replay_buffer.empty()
        with torch.no_grad():
            advantage(batch)
        replay_buffer.extend(batch.reshape(-1).cpu())
        for _ in range(config.epochs):
            for _ in range(config.frames_per_batch // config.sub_batch_size):
                sample = replay_buffer.sample(config.sub_batch_size)
                losses = loss_module(sample)
                total_loss = (
                    losses["loss_objective"]
                    + losses["loss_critic"]
                    + losses["loss_entropy"]
                )
                optimizer.zero_grad(set_to_none=True)
                total_loss.backward()
                nn.utils.clip_grad_norm_(
                    loss_module.parameters(), config.max_grad_norm
                )
                optimizer.step()
        replay_buffer.empty()

        collector.update_policy_weights_()
        collected += batch.numel()
        mean_reward = batch["next", "reward"].mean().item()
        if batch_index == 1 or batch_index % 5 == 0:
            print(
                f"batch={batch_index:03d} frames={collected:07d} "
                f"mean_step_reward={mean_reward:8.3f}"
            )

    with set_exploration_type(ExplorationType.DETERMINISTIC), torch.inference_mode():
        evaluation = env.rollout(200, policy)
    print(f"evaluation_return={evaluation['next', 'reward'].sum().item():.1f}")
    collector.shutdown()
    env.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="TorchRL primitive PPO 예제")
    parser.add_argument("--smoke-test", action="store_true")
    args = parser.parse_args()
    config = Config()
    if args.smoke_test:
        config.frames_per_batch = 128
        config.total_frames = 256
        config.sub_batch_size = 32
        config.epochs = 2
    train(config)


if __name__ == "__main__":
    main()
