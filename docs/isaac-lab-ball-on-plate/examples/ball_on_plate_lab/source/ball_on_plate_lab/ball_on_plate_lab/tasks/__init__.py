"""Register every Ball-on-Plate task."""

import sys

from . import direct, manager_based


def register() -> list[str]:
    """External-project callback used by Isaac Lab's RSL-RL launcher.

    Importing this module performs Gymnasium registration. Returning the original
    arguments lets the launcher's Hydra preset parser keep unconsumed overrides.
    """

    return sys.argv[1:]


__all__ = ["direct", "manager_based", "register"]
