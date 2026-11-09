"""이 외부 프로젝트가 등록하는 태스크 ID를 나열한다."""

import gymnasium as gym

import ball_on_plate_lab.tasks  # noqa: F401


for spec in sorted(gym.registry.values(), key=lambda item: item.id):
    if spec.id.startswith("BallOnPlate-"):
        print(spec.id)
