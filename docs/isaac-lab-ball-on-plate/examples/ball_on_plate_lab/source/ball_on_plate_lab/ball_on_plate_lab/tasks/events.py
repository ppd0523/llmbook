"""백엔드에 독립적인 시작 시 도메인 무작위화."""

from isaaclab.envs import mdp
from isaaclab.managers import EventTermCfg as EventTerm
from isaaclab.managers import SceneEntityCfg
from isaaclab.utils.configclass import configclass


@configclass
class MaterialRandomizationCfg:
    """모든 병렬 환경의 접촉 파라미터를 한 번 무작위화한다."""

    ball_material = EventTerm(
        func=mdp.randomize_rigid_body_material,
        mode="startup",
        params={
            "asset_cfg": SceneEntityCfg("ball"),
            "static_friction_range": (0.25, 0.45),
            "dynamic_friction_range": (0.20, 0.40),
            "restitution_range": (0.0, 0.10),
            "num_buckets": 64,
        },
    )
    plate_material = EventTerm(
        func=mdp.randomize_rigid_body_material,
        mode="startup",
        params={
            "asset_cfg": SceneEntityCfg("plate", body_names=["plate"]),
            "static_friction_range": (0.25, 0.45),
            "dynamic_friction_range": (0.20, 0.40),
            "restitution_range": (0.0, 0.05),
            "num_buckets": 64,
        },
    )
