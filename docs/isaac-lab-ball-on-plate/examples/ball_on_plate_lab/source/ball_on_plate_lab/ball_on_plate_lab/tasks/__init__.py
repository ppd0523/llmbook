"""모든 Ball-on-Plate 태스크를 등록한다."""

import sys

from . import direct, manager_based


def register() -> list[str]:
    """Isaac Lab RSL-RL 런처가 쓰는 외부 프로젝트 콜백.

    이 모듈을 import하면 Gymnasium 등록이 수행된다. 원래 인자를 그대로 반환하므로
    런처의 Hydra 프리셋 파서가 처리하지 않은 override를 유지한다.
    """

    return sys.argv[1:]


__all__ = ["direct", "manager_based", "register"]
