# 5. Direct 환경 구현

Direct 방식에서는 물리 스텝 전후의 흐름을 한 클래스에서 볼 수 있다. 먼저 이 구현을 완성하면 Manager-based 장에서 무엇이 관리자로 옮겨가는지 명확해진다.

## 5.1 외부 프로젝트 설치

제공 프로젝트는 Isaac Lab 소스에 파일을 추가하지 않는 외부 확장 프로젝트다. [공식 프로젝트 템플릿](https://isaac-sim.github.io/IsaacLab/v3.0.0-beta2/source/overview/own-project/template.html)도 외부 프로젝트를 권장한다.

예제 디렉터리를 Ubuntu 작업 공간으로 복사한 뒤 설치한다.

```bash
cd /absolute/path/to/ball_on_plate_lab
uv pip install -e source/ball_on_plate_lab
python scripts/list_envs.py
```

예상 출력은 네 태스크 ID다.

```text
BallOnPlate-Direct-v0
BallOnPlate-Manager-v0
BallOnPlate-Tracking-Direct-v0
BallOnPlate-Tracking-Manager-v0
```

`pip install -e`는 소스를 복사하지 않고 편집 가능한 링크를 설치한다. 코드를 고친 뒤 매번 다시 설치할 필요는 없지만, 패키지 이름이나 등록 모듈을 바꾸면 Python 프로세스를 다시 시작한다.

## 5.2 자산 설정

[common.py의 `make_plate_cfg()`](./examples/ball_on_plate_lab/source/ball_on_plate_lab/ball_on_plate_lab/tasks/common.py)는 생성한 USD를 articulation으로 읽고 두 joint에 implicit actuator를 건다.

```python
ArticulationCfg(
    prim_path=prim_path,
    spawn=sim_utils.UsdFileCfg(usd_path=str(PLATE_USD_PATH)),
    actuators={
        "tilt": ImplicitActuatorCfg(
            joint_names_expr=["roll_joint", "pitch_joint"],
            effort_limit_sim=12.0,
            velocity_limit_sim=2.0,
            stiffness=40.0,
            damping=4.0,
        )
    },
)
```

공은 `SphereCfg`로 만든 `RigidObject`다. 원판은 USD를 재사용하지만 단순 공을 위해 별도 USD를 만들 필요는 없다. 둘 다 `isaaclab.assets`의 백엔드 독립 인터페이스를 사용한다.

## 5.3 물리 프리셋

[physics.py](./examples/ball_on_plate_lab/source/ball_on_plate_lab/ball_on_plate_lab/tasks/physics.py)는 같은 환경 설정에서 두 백엔드를 선택할 수 있게 한다.

```python
@configclass
class BallOnPlatePhysicsCfg(PresetCfg):
    default: PhysxCfg = PhysxCfg()
    physx: PhysxCfg = PhysxCfg()
    newton_mjwarp: NewtonCfg = NewtonCfg(...)
```

환경 코드 안에서 `if newton` 분기를 만들지 않는다. 백엔드 차이는 프리셋과 팩토리가 처리하고, 태스크 코드는 공 위치와 관절 상태만 다룬다.

## 5.4 Direct 설정

[ball_on_plate_env_cfg.py](./examples/ball_on_plate_lab/source/ball_on_plate_lab/ball_on_plate_lab/tasks/direct/ball_on_plate/ball_on_plate_env_cfg.py)의 핵심은 공간 크기와 시간이다.

```python
decimation = 4
episode_length_s = 10.0
action_space = 2
observation_space = 12
state_space = 0

sim = SimulationCfg(dt=1.0 / 120.0, ...)
scene = InteractiveSceneCfg(num_envs=2048, env_spacing=1.5, ...)
```

처음 간이 실행 시험에서는 명령줄에서 `--num_envs 4`처럼 줄인다. 설정의 2048은 학습용 기본값이지 디버깅 의무값이 아니다.

`events`에는 시작 시 재질 무작위화를 넣는다. Direct도 관측·보상 관리자는 쓰지 않지만 이벤트 관리자는 사용할 수 있다.

## 5.5 `_setup_scene()`

[Direct 환경 전체 코드](./examples/ball_on_plate_lab/source/ball_on_plate_lab/ball_on_plate_lab/tasks/direct/ball_on_plate/ball_on_plate_env.py)는 두 자산을 만든 뒤 환경을 복제하고 이름으로 등록한다.

```python
self.plate = Articulation(self.cfg.plate_cfg)
self.ball = RigidObject(self.cfg.ball_cfg)
self.scene.clone_environments(copy_from_source=False)
self.scene.articulations["plate"] = self.plate
self.scene.rigid_objects["ball"] = self.ball
```

`scene["plate"]`와 `scene["ball"]`이라는 공통 접근은 나중에 공유 리셋 함수와 Manager-based 항에서도 그대로 쓴다.

## 5.6 행동 훅

```python
def _pre_physics_step(self, actions):
    self._previous_actions.copy_(self._actions)
    self._actions.copy_(torch.clamp(actions, -1.0, 1.0))

def _apply_action(self):
    self.plate.set_joint_position_target_index(
        target=MAX_TILT_RAD * self._actions,
        joint_ids=self._tilt_joint_ids,
    )
```

`_pre_physics_step()`은 정책 스텝마다 한 번, `_apply_action()`은 decimation 동안 필요에 따라 호출된다. 행동 변화량 보상을 계산하려면 덮어쓰기 전에 이전 행동을 복사해야 한다.

3.0의 `_index` API는 키워드 전용이다. `target=`, `joint_ids=`를 생략하지 않는다. 공식 태그의 [Direct Cartpole](https://github.com/isaac-sim/IsaacLab/blob/v3.0.0-beta2.patch1/source/isaaclab_tasks/isaaclab_tasks/direct/cartpole/cartpole_env.py)도 같은 방식을 사용한다.

## 5.7 관측, 보상, 종료

Direct 훅은 공통 함수에 필요한 런타임 객체를 넘긴다.

```python
def _get_observations(self):
    policy = task_observation(
        self.ball,
        self.plate,
        self.scene.env_origins,
        self._tilt_joint_ids,
        self._actions,
        self.episode_length_buf,
        self.step_dt,
        self.cfg.moving_target,
    )
    return {"policy": policy}
```

`{"policy": tensor}`라는 그룹 이름은 RSL-RL 래퍼가 actor 입력을 찾는 계약이다.

종료는 `(terminated, time_out)` 순서로 반환한다.

```python
terminated = ball_failed(self.ball, self.scene.env_origins)
time_out = self.episode_length_buf >= self.max_episode_length - 1
return terminated, time_out
```

두 값을 하나로 합치면 평가 생존율과 시간 제한 부트스트래핑 정보를 잃는다.

## 5.8 부분 리셋

병렬 환경 2048개가 동시에 끝나는 것은 아니다. `_reset_idx(env_ids)`는 끝난 행만 고친다.

```python
super()._reset_idx(env_ids)
reset_plate_and_ball(self, env_ids)
self._actions[env_ids] = 0.0
self._previous_actions[env_ids] = 0.0
```

루트 자세에는 해당 `env_origins[env_ids]`를 더하고, 루트 속도에는 더하지 않는다. 위치와 속도를 혼동하는 흔한 오류다.

## 5.9 외부 태스크 등록

`gym.register()`는 패키지를 import할 때 실행된다. Isaac Lab 3.0의 통합 `./isaaclab.sh train`은 내부 `isaaclab_tasks`를 자동으로 import하지만 외부 프로젝트를 자동 발견하지 않는다. 따라서 공식 RSL-RL 스크립트의 콜백을 사용한다.

```bash
--external_callback ball_on_plate_lab.tasks.register
```

콜백은 패키지를 import해 Gymnasium 등록을 끝내고, Hydra가 처리할 프리셋 인자를 그대로 돌려준다. 이 차이를 모르고 통합 명령만 사용하면 `Environment BallOnPlate doesn't exist`가 나온다.

## 5.10 간이 실행 시험

USD 변환과 편집 가능 설치를 마친 뒤, Isaac Lab 저장소 루트에서 실행한다.

```bash
PROJECT=/absolute/path/to/ball_on_plate_lab

./isaaclab.sh -p "$PROJECT/scripts/evaluate.py" \
  --task BallOnPlate-Direct-v0 \
  --random_policy --episodes 4 --seed 7 --headless \
  physics=newton_mjwarp
```

무작위 정책이 통과 점수를 내는 것이 목적이 아니다. 다음을 확인한다.

- USD 경로 오류 없이 articulation이 생성된다.
- 관측 크기가 `[4, 12]`다.
- 행동 크기가 `[4, 2]`다.
- 공이 떨어지면 해당 환경만 리셋된다.
- 에피소드 4회가 끝나고 JSON 지표를 출력한다.

무작위 행동인데 100% 생존한다면 종료 조건이나 충돌 형상을 의심한다. 모든 공이 첫 스텝에 끝나면 로컬·세계 좌표, 초기 z, 충돌 형상을 의심한다.

[← 4장](./04-design-ball-on-plate-task.md) · [6장: 학습·평가·디버깅 →](./06-train-evaluate-and-debug.md)
