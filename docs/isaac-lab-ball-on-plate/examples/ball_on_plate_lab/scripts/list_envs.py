"""List the task IDs registered by this external project."""

import gymnasium as gym

import ball_on_plate_lab.tasks  # noqa: F401


for spec in sorted(gym.registry.values(), key=lambda item: item.id):
    if spec.id.startswith("BallOnPlate-"):
        print(spec.id)
