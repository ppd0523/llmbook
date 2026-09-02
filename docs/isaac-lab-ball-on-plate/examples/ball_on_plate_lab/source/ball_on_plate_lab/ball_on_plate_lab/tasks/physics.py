"""Selectable physics presets for the Ball-on-Plate tasks."""

from isaaclab_newton.physics import MJWarpSolverCfg, NewtonCfg
from isaaclab_physx.physics import PhysxCfg
from isaaclab.utils.configclass import configclass
from isaaclab_tasks.utils import PresetCfg


@configclass
class BallOnPlatePhysicsCfg(PresetCfg):
    """Expose the two backends used in the tutorial."""

    default: PhysxCfg = PhysxCfg()
    physx: PhysxCfg = PhysxCfg()
    newton_mjwarp: NewtonCfg = NewtonCfg(
        solver_cfg=MJWarpSolverCfg(
            njmax=8,
            nconmax=16,
            cone="pyramidal",
            impratio=1,
            integrator="implicitfast",
        ),
        num_substeps=2,
        debug_mode=False,
        use_cuda_graph=True,
    )
