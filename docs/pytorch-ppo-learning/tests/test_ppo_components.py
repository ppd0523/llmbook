from __future__ import annotations

import sys
import unittest
from pathlib import Path

import torch

EXAMPLES = Path(__file__).resolve().parents[1] / "examples"
sys.path.insert(0, str(EXAMPLES))

from ppo_components import (  # noqa: E402
    clipped_surrogate,
    discounted_returns,
    generalized_advantage_estimate,
)


class DiscountedReturnTests(unittest.TestCase):
    def test_discounted_returns(self) -> None:
        rewards = torch.tensor([1.0, 2.0, 3.0])
        actual = discounted_returns(rewards, gamma=0.5)
        expected = torch.tensor([2.75, 3.5, 3.0])
        torch.testing.assert_close(actual, expected)


class GAETests(unittest.TestCase):
    def test_termination_drops_bootstrap(self) -> None:
        rewards = torch.tensor([1.0])
        values = torch.tensor([0.4])
        next_values = torch.tensor([100.0])
        terminated = torch.tensor([True])
        truncated = torch.tensor([False])

        advantages, targets = generalized_advantage_estimate(
            rewards, values, next_values, terminated, truncated
        )

        torch.testing.assert_close(advantages, torch.tensor([0.6]))
        torch.testing.assert_close(targets, torch.tensor([1.0]))

    def test_truncation_keeps_bootstrap_but_stops_recursion(self) -> None:
        rewards = torch.tensor([1.0, 9.0])
        values = torch.tensor([0.4, 0.0])
        next_values = torch.tensor([0.5, 0.0])
        terminated = torch.tensor([False, False])
        truncated = torch.tensor([True, False])

        advantages, _ = generalized_advantage_estimate(
            rewards,
            values,
            next_values,
            terminated,
            truncated,
            gamma=0.9,
            gae_lambda=1.0,
        )

        # 첫 transition은 1 + 0.9*0.5 - 0.4이며, 다음 episode의 9를 더하지 않는다.
        torch.testing.assert_close(advantages[0], torch.tensor(1.05))


class PPOClipTests(unittest.TestCase):
    def test_positive_advantage_caps_gain(self) -> None:
        old_log_prob = torch.log(torch.tensor([0.5]))
        new_log_prob = torch.log(torch.tensor([0.8]))
        objective, ratio = clipped_surrogate(
            new_log_prob, old_log_prob, torch.tensor([2.0]), clip_epsilon=0.2
        )
        torch.testing.assert_close(ratio, torch.tensor([1.6]))
        torch.testing.assert_close(objective, torch.tensor([2.4]))

    def test_negative_advantage_caps_harmful_drop(self) -> None:
        old_log_prob = torch.log(torch.tensor([0.5]))
        new_log_prob = torch.log(torch.tensor([0.2]))
        objective, ratio = clipped_surrogate(
            new_log_prob, old_log_prob, torch.tensor([-2.0]), clip_epsilon=0.2
        )
        torch.testing.assert_close(ratio, torch.tensor([0.4]))
        torch.testing.assert_close(objective, torch.tensor([-1.6]))


if __name__ == "__main__":
    unittest.main()

