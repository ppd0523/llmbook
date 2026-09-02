"""Manager-based configuration of the same Ball-on-Plate MDP."""

import isaaclab.sim as sim_utils
from isaaclab.assets import AssetBaseCfg
from isaaclab.envs import ManagerBasedRLEnvCfg, mdp as base_mdp
from isaaclab.managers import EventTermCfg as EventTerm
from isaaclab.managers import ObservationGroupCfg as ObsGroup
from isaaclab.managers import ObservationTermCfg as ObsTerm
from isaaclab.managers import RewardTermCfg as RewTerm
from isaaclab.managers import TerminationTermCfg as DoneTerm
from isaaclab.scene import InteractiveSceneCfg
from isaaclab.utils.configclass import configclass

from ...common import MAX_TILT_RAD, make_ball_cfg, make_plate_cfg
from ...events import MaterialRandomizationCfg
from ...physics import BallOnPlatePhysicsCfg
from . import mdp


@configclass
class BallOnPlateSceneCfg(InteractiveSceneCfg):
    plate = make_plate_cfg("{ENV_REGEX_NS}/Plate")
    ball = make_ball_cfg("{ENV_REGEX_NS}/Ball")
    dome_light = AssetBaseCfg(
        prim_path="/World/DomeLight",
        spawn=sim_utils.DomeLightCfg(intensity=1800.0, color=(0.85, 0.88, 1.0)),
    )


@configclass
class ActionsCfg:
    plate_tilt = base_mdp.JointPositionActionCfg(
        asset_name="plate",
        joint_names=["roll_joint", "pitch_joint"],
        scale=MAX_TILT_RAD,
        use_default_offset=False,
        preserve_order=True,
    )


@configclass
class ObservationsCfg:
    @configclass
    class PolicyCfg(ObsGroup):
        ball_to_target = ObsTerm(func=mdp.ball_to_target)
        target_position = ObsTerm(func=mdp.target_position)
        ball_velocity = ObsTerm(func=mdp.ball_velocity)
        plate_position = ObsTerm(func=mdp.plate_position)
        plate_velocity = ObsTerm(func=mdp.plate_velocity)
        last_action = ObsTerm(func=base_mdp.last_action)

        def __post_init__(self) -> None:
            self.enable_corruption = False
            self.concatenate_terms = True

    policy: PolicyCfg = PolicyCfg()


@configclass
class EventCfg(MaterialRandomizationCfg):
    reset_task = EventTerm(func=mdp.reset_task, mode="reset")


@configclass
class RewardsCfg:
    alive = RewTerm(func=base_mdp.is_alive, weight=0.2)
    target = RewTerm(func=mdp.target_reward, weight=1.0)
    speed = RewTerm(func=mdp.ball_speed_l2, weight=-0.05)
    tilt = RewTerm(func=mdp.plate_tilt_l2, weight=-0.02)
    action_rate = RewTerm(func=mdp.action_rate_l2, weight=-0.01)
    terminating = RewTerm(func=base_mdp.is_terminated, weight=-2.0)


@configclass
class TerminationsCfg:
    time_out = DoneTerm(func=base_mdp.time_out, time_out=True)
    ball_out_of_bounds = DoneTerm(func=mdp.ball_out_of_bounds)


@configclass
class BallOnPlateEnvCfg(ManagerBasedRLEnvCfg):
    scene: BallOnPlateSceneCfg = BallOnPlateSceneCfg(
        num_envs=2048,
        env_spacing=1.5,
        replicate_physics=True,
        clone_in_fabric=True,
    )
    observations: ObservationsCfg = ObservationsCfg()
    actions: ActionsCfg = ActionsCfg()
    events: EventCfg = EventCfg()
    rewards: RewardsCfg = RewardsCfg()
    terminations: TerminationsCfg = TerminationsCfg()
    moving_target = False

    def __post_init__(self) -> None:
        self.decimation = 4
        self.episode_length_s = 10.0
        self.viewer.eye = (1.8, 1.8, 1.4)
        self.viewer.lookat = (0.0, 0.0, 0.15)
        self.sim.dt = 1.0 / 120.0
        self.sim.render_interval = self.decimation
        self.sim.physics = BallOnPlatePhysicsCfg()


@configclass
class BallOnPlateTrackingEnvCfg(BallOnPlateEnvCfg):
    moving_target = True
