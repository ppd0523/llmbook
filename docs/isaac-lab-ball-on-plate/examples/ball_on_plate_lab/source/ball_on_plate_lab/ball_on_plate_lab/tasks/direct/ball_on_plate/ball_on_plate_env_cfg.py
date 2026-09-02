"""Configuration for the Direct Ball-on-Plate environment."""

from isaaclab.assets import ArticulationCfg, RigidObjectCfg
from isaaclab.envs import DirectRLEnvCfg
from isaaclab.scene import InteractiveSceneCfg
from isaaclab.sim import SimulationCfg
from isaaclab.utils.configclass import configclass

from ...common import make_ball_cfg, make_plate_cfg
from ...events import MaterialRandomizationCfg
from ...physics import BallOnPlatePhysicsCfg


@configclass
class BallOnPlateEnvCfg(DirectRLEnvCfg):
    # Environment: 30 Hz policy rate, 10 s episodes.
    decimation = 4
    episode_length_s = 10.0
    action_space = 2
    observation_space = 12
    state_space = 0

    sim: SimulationCfg = SimulationCfg(
        dt=1.0 / 120.0,
        render_interval=decimation,
        physics=BallOnPlatePhysicsCfg(),
    )
    scene: InteractiveSceneCfg = InteractiveSceneCfg(
        num_envs=2048,
        env_spacing=1.5,
        replicate_physics=True,
        clone_in_fabric=True,
    )

    plate_cfg: ArticulationCfg = make_plate_cfg("/World/envs/env_.*/Plate")
    ball_cfg: RigidObjectCfg = make_ball_cfg("/World/envs/env_.*/Ball")
    events: MaterialRandomizationCfg = MaterialRandomizationCfg()
    moving_target = False


@configclass
class BallOnPlateTrackingEnvCfg(BallOnPlateEnvCfg):
    moving_target = True
