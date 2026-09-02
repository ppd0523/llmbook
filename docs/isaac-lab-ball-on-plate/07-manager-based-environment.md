# 7. Manager-based 환경

Manager-based 방식은 Direct 환경을 다른 알고리즘으로 바꾸지 않는다. 같은 MDP를 행동, 관측, 보상, 이벤트, 종료라는 독립된 항으로 분해한다. 이 장의 목표는 두 태스크가 정말 같은 의미인지 검증하는 것이다.

## 7.1 장면은 선언한다

[Manager-based 설정](./examples/ball_on_plate_lab/source/ball_on_plate_lab/ball_on_plate_lab/tasks/manager_based/ball_on_plate/ball_on_plate_env_cfg.py)은 `_setup_scene()` 대신 `InteractiveSceneCfg` 하위 클래스에 자산을 배치한다.

```python
@configclass
class BallOnPlateSceneCfg(InteractiveSceneCfg):
    plate = make_plate_cfg("{ENV_REGEX_NS}/Plate")
    ball = make_ball_cfg("{ENV_REGEX_NS}/Ball")
    dome_light = AssetBaseCfg(...)
```

`{ENV_REGEX_NS}`는 장면 관리자가 각 환경 이름 공간으로 확장하는 표기다. Direct의 `/World/envs/env_.*/Plate`와 목적은 같다.

## 7.2 행동 항

Direct의 `_apply_action()`은 다음 설정으로 바뀐다.

```python
@configclass
class ActionsCfg:
    plate_tilt = base_mdp.JointPositionActionCfg(
        asset_name="plate",
        joint_names=["roll_joint", "pitch_joint"],
        scale=MAX_TILT_RAD,
        use_default_offset=False,
        preserve_order=True,
    )
```

`preserve_order=True`가 중요하다. 정책의 첫 행동을 roll, 둘째 행동을 pitch로 고정한다. regex 검색 결과의 내부 순서에 의존하지 않는다.

`use_default_offset=False`이므로 0 행동은 절대 목표 0 rad다. 기본 관절 자세도 0이지만, 이 설정을 명시하면 행동의 의미가 자산 기본값 변경에 따라 달라지지 않는다.

## 7.3 관측 항

관측은 작은 함수 여섯 개로 나뉜다.

```python
@configclass
class PolicyCfg(ObsGroup):
    ball_to_target = ObsTerm(func=mdp.ball_to_target)
    target_position = ObsTerm(func=mdp.target_position)
    ball_velocity = ObsTerm(func=mdp.ball_velocity)
    plate_position = ObsTerm(func=mdp.plate_position)
    plate_velocity = ObsTerm(func=mdp.plate_velocity)
    last_action = ObsTerm(func=base_mdp.last_action)
```

항의 선언 순서가 이어 붙이는 순서다. Direct의 12개 값과 순서까지 같아야 같은 체크포인트를 사용할 수 있다. `concatenate_terms=True`, `enable_corruption=False`도 명시한다.

[mdp.py](./examples/ball_on_plate_lab/source/ball_on_plate_lab/ball_on_plate_lab/tasks/manager_based/ball_on_plate/mdp.py)의 함수는 관리자 자체 상태를 만들지 않고 `env.scene`과 공통 상수를 읽는다.

## 7.4 보상 항

Direct의 한 식을 이름과 가중치로 분해한다.

```python
@configclass
class RewardsCfg:
    alive = RewTerm(func=base_mdp.is_alive, weight=0.2)
    target = RewTerm(func=mdp.target_reward, weight=1.0)
    speed = RewTerm(func=mdp.ball_speed_l2, weight=-0.05)
    tilt = RewTerm(func=mdp.plate_tilt_l2, weight=-0.02)
    action_rate = RewTerm(func=mdp.action_rate_l2, weight=-0.01)
    terminating = RewTerm(func=base_mdp.is_terminated, weight=-2.0)
```

관리자는 항별 에피소드 합을 자동으로 기록하기 쉬워 보상 디버깅에 유리하다. 반면 항 함수가 여러 파일에 퍼질 수 있으므로 이름과 단위를 분명히 해야 한다.

## 7.5 이벤트와 종료

리셋은 사용자 정의 이벤트로 공통 함수를 호출한다.

```python
@configclass
class EventCfg(MaterialRandomizationCfg):
    reset_task = EventTerm(func=mdp.reset_task, mode="reset")
```

시작 시 재질 무작위화는 부모 설정에서 상속한다. 물리 매개변수는 시뮬레이션 초기화 뒤 한 번, 자세와 속도는 각 에피소드 리셋 때 바뀐다.

종료는 시간 제한과 실패를 별도 항으로 둔다.

```python
time_out = DoneTerm(func=base_mdp.time_out, time_out=True)
ball_out_of_bounds = DoneTerm(func=mdp.ball_out_of_bounds)
```

## 7.6 Direct와 일대일 대응

| MDP 요소 | Direct | Manager-based |
|---|---|---|
| 장면 | `_setup_scene()` | `BallOnPlateSceneCfg` |
| 행동 | `_pre_physics_step()`, `_apply_action()` | `JointPositionActionCfg` |
| 관측 | `_get_observations()` | `ObservationsCfg` |
| 보상 | `_get_rewards()` | `RewardsCfg` |
| 실패/시간 제한 | `_get_dones()` | `TerminationsCfg` |
| 리셋 | `_reset_idx()` | `EventCfg.reset_task` |
| 도메인 무작위화 | `events` 설정 | 같은 `events` 설정 |

Manager-based가 더 빠른 것도, Direct가 더 정확한 것도 아니다. 동일 백엔드와 같은 텐서 연산이면 차이는 주로 프레임워크 부가 비용과 코드 조직에서 온다.

## 7.7 간이 실행 시험과 학습

```bash
./isaaclab.sh -p "$PROJECT/scripts/evaluate.py" \
  --task BallOnPlate-Manager-v0 \
  --random_policy --episodes 4 --seed 7 --headless \
  physics=newton_mjwarp
```

학습 명령에서는 태스크 ID만 바꾼다.

```bash
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py \
  --task BallOnPlate-Manager-v0 \
  --external_callback ball_on_plate_lab.tasks.register \
  --headless --num_envs 2048 --max_iterations 500 \
  physics=newton_mjwarp
```

## 7.8 의미 동등성 검사

같은 시드라고 두 환경 작성 방식의 매 스텝이 비트 단위로 같다고 기대하지 않는다. 초기화 순서가 달라 난수 소비 순서가 달라질 수 있다. 대신 다음 불변식을 검사한다.

1. 두 태스크의 관측 공간이 12다.
2. 0 행동이 양쪽에서 관절 목표 0 rad를 만든다.
3. 같은 명시적 상태를 썼을 때 관측 벡터가 수치 허용 오차 내에서 같다.
4. 같은 상태와 행동에 보상 식이 같다.
5. `radius=0.46 m` 경계와 시간 제한 길이가 같다.
6. 무작위 정책 지표가 같은 규모이며 한쪽만 0% 또는 100%로 포화하지 않는다.

한 작성 방식의 체크포인트를 다른 방식에서 평가하는 것이 가장 강한 통합 검사다. 두 관측·행동 계약이 같으므로 네트워크 크기는 호환되어야 한다. 성능이 크게 무너지면 항 순서, 행동 순서, 리셋 차이를 먼저 본다.

## 7.9 언제 어느 방식을 선택하는가

Direct가 적합한 경우:

- 새로운 시뮬레이션 루프나 비정형 계산을 빠르게 실험한다.
- 한 파일에서 호출 순서를 추적하는 것이 중요하다.
- Warp kernel 등 매우 특화된 계산을 붙인다.

Manager-based가 적합한 경우:

- 여러 로봇·태스크 조합에서 보상과 관측을 재사용한다.
- 설정 덮어쓰기로 실험군을 만든다.
- 항별 로깅, 커리큘럼, 무작위화를 체계화한다.
- 팀원이 MDP 요소를 독립적으로 검토한다.

이 작은 과제에서는 Direct가 더 짧다. 규모가 커질 때 Manager-based의 구조적 이득이 커진다는 점을 체감하는 것이 목표다.

[← 6장](./06-train-evaluate-and-debug.md) · [8장: Newton과 PhysX 비교 →](./08-newton-and-physx.md)
