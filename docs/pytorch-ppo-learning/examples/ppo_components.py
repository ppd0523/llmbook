"""PPO의 핵심 수식을 독립적으로 시험하기 위한 작은 함수 모음."""

from __future__ import annotations

import torch
from torch import Tensor


def discounted_returns(
    rewards: Tensor,
    gamma: float,
    bootstrap_value: Tensor | float = 0.0,
) -> Tensor:
    """유한 reward 열의 discounted return을 뒤에서부터 계산한다."""
    returns = torch.empty_like(rewards, dtype=torch.float32)
    running = torch.as_tensor(
        bootstrap_value, dtype=torch.float32, device=rewards.device
    )
    for index in reversed(range(rewards.shape[0])):
        running = rewards[index] + gamma * running
        returns[index] = running
    return returns


def generalized_advantage_estimate(
    rewards: Tensor,
    values: Tensor,
    next_values: Tensor,
    terminated: Tensor,
    truncated: Tensor,
    gamma: float = 0.99,
    gae_lambda: float = 0.95,
) -> tuple[Tensor, Tensor]:
    """Gymnasium 종료 의미를 보존해 GAE와 value target을 계산한다.

    자연 종료(terminated)에서는 다음 가치로 bootstrap하지 않는다.
    시간 제한(truncated)에서는 다음 가치로 bootstrap하지만 다음 episode의
    advantage로 재귀 연결하지 않는다.
    """
    if not (
        rewards.shape
        == values.shape
        == next_values.shape
        == terminated.shape
        == truncated.shape
    ):
        raise ValueError("모든 입력은 같은 1차원 shape이어야 합니다.")

    advantages = torch.zeros_like(rewards, dtype=torch.float32)
    next_advantage = torch.zeros((), dtype=torch.float32, device=rewards.device)

    for index in reversed(range(rewards.shape[0])):
        bootstrap_mask = (~terminated[index]).float()
        continuation_mask = (~(terminated[index] | truncated[index])).float()
        delta = (
            rewards[index]
            + gamma * bootstrap_mask * next_values[index]
            - values[index]
        )
        next_advantage = (
            delta + gamma * gae_lambda * continuation_mask * next_advantage
        )
        advantages[index] = next_advantage

    value_targets = advantages + values
    return advantages, value_targets


def clipped_surrogate(
    new_log_prob: Tensor,
    old_log_prob: Tensor,
    advantages: Tensor,
    clip_epsilon: float = 0.2,
) -> tuple[Tensor, Tensor]:
    """샘플별 PPO-Clip 목적값과 probability ratio를 반환한다."""
    ratio = torch.exp(new_log_prob - old_log_prob)
    unclipped = ratio * advantages
    clipped = torch.clamp(ratio, 1.0 - clip_epsilon, 1.0 + clip_epsilon) * advantages
    objective = torch.minimum(unclipped, clipped)
    return objective, ratio


def explained_variance(targets: Tensor, predictions: Tensor) -> Tensor:
    """critic 진단에 쓰는 explained variance를 계산한다."""
    target_variance = torch.var(targets, unbiased=False)
    if target_variance == 0:
        return torch.tensor(float("nan"), device=targets.device)
    residual_variance = torch.var(targets - predictions, unbiased=False)
    return 1.0 - residual_variance / target_variance

