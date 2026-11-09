"""Ball-on-Plate 태스크에서 선택할 수 있는 물리 프리셋."""

from isaaclab_newton.physics import MJWarpSolverCfg, NewtonCfg
from isaaclab_physx.physics import PhysxCfg
from isaaclab.utils.configclass import configclass
from isaaclab_tasks.utils import PresetCfg


@configclass
class BallOnPlatePhysicsCfg(PresetCfg):
    """학습자료에서 쓰는 두 백엔드를 노출한다."""

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
