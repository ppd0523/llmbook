# 2. Isaac Lab의 정신 모델

Isaac Lab을 처음 볼 때 파일과 클래스 이름부터 외우면 길을 잃기 쉽다. 먼저 “정책의 행동이 공의 다음 관측으로 돌아오기까지 어느 층을 통과하는가”를 고정한다.

```text
RSL-RL policy
    ↓ action tensor [N, 2]
Isaac Lab environment
    ↓ joint target
InteractiveScene → Articulation(plate) + RigidObject(ball)
    ↓ 백엔드 독립 자산 API
Newton MJWarp 또는 Isaac Sim PhysX
    ↓ simulated state
observation / reward / termination / reset
```

## 2.1 다섯 층

### 물리 백엔드

Newton MJWarp와 PhysX가 실제 시간 적분과 충돌 계산을 한다. Isaac Lab 3.0에서는 `physics=newton_mjwarp` 또는 `physics=physx`라는 프리셋으로 선택한다. 사용자가 `plate.data.joint_pos.torch`를 읽는 코드는 유지되고, 팩토리가 백엔드별 articulation 구현을 만든다. 이것이 [다중 백엔드 구조](https://isaac-sim.github.io/IsaacLab/v3.0.0-beta2/source/overview/core-concepts/multi_backend_architecture.html)의 핵심이다.

### 자산

`Articulation`은 관절이 연결된 원판 장치를, `RigidObject`는 자유롭게 움직이는 공을 나타낸다. 설정 객체인 `ArticulationCfg`와 `RigidObjectCfg`는 무엇을 어디에 spawn할지 기술하고, 런타임 객체는 상태를 읽고 명령을 쓴다.

### 장면

`InteractiveScene`은 자산을 이름으로 묶고 `num_envs`개의 환경을 복제한다. `env_0`, `env_1`마다 Python 객체를 따로 만드는 것이 아니라, 한 자산 객체가 `[N, ...]` 텐서로 모든 인스턴스를 다룬다.

### 환경

환경은 MDP 계약을 구현한다.

- 관측: 정책이 받을 텐서
- 행동: 정책 출력이 actuator 명령으로 변환되는 규칙
- 보상: 한 스텝의 목적 신호
- 종료: 실패와 시간 제한
- 리셋: 다음 에피소드의 초기 분포

### RL 래퍼와 러너

`RslRlVecEnvWrapper`는 Isaac Lab의 관측·보상·종료 값을 RSL-RL이 기대하는 벡터 환경 규약으로 바꾼다. 러너는 롤아웃 수집, GAE, PPO 갱신, 체크포인트 저장을 맡는다. 환경은 PPO 내부를 알 필요가 없고, PPO는 USD 관절을 알 필요가 없다.

## 2.2 설정과 런타임을 구분한다

다음 두 줄은 역할이 다르다.

```python
plate_cfg = ArticulationCfg(...)
plate = Articulation(plate_cfg)
```

`plate_cfg`는 복사·직렬화 가능한 설계도다. `plate`는 시뮬레이터가 초기화된 뒤 백엔드 텐서 뷰를 가진 런타임 객체다. Manager-based 방식에서는 장면 관리자가 설계도에서 런타임 객체를 만들고, Direct 방식에서는 `_setup_scene()`에서 직접 만든다.

이 구분은 import 순서에도 중요하다. Isaac Sim 기반 코드에서는 앱을 시작하기 전에 무거운 런타임 모듈을 import하면 확장 기능 초기화 오류가 날 수 있다. Isaac Lab 3.0의 실행기와 설정 전용 import 구조는 이 문제를 줄이도록 설계되었다.

## 2.3 병렬 환경의 좌표계

세계 좌표에서 각 공의 위치는 서로 다르다. 환경이 1.5 m 간격으로 배치되기 때문이다.

```python
ball_xy_world = ball.data.root_pos_w.torch[:, :2]
ball_xy_local = ball_xy_world - scene.env_origins[:, :2]
```

보상과 종료에는 `ball_xy_local`을 사용해야 한다. 세계 원점으로부터의 거리를 쓰면 `env_0`만 정상이고 나머지는 시작 즉시 실패한다.

shape를 먼저 적으면 실수가 줄어든다.

| 값 | shape | 의미 |
|---|---:|---|
| `env_origins` | `[N, 3]` | 각 복제 환경의 세계 원점 |
| `root_pos_w` | `[N, 3]` | 공의 세계 위치 |
| `joint_pos` | `[N, 2]` | roll, pitch 관절 각도 |
| `actions` | `[N, 2]` | 정규화된 목표 기울기 |
| 정책 관측 | `[N, 12]` | 정책 입력 |

## 2.4 ProxyArray와 `.torch`

Isaac Lab 3.0의 자산 데이터는 여러 백엔드를 포괄하는 `ProxyArray`다. PyTorch 연산에 넣기 전에 `.torch` 뷰를 사용한다.

```python
joint_pos = plate.data.joint_pos.torch
ball_vel = ball.data.root_lin_vel_w.torch
```

2.x 예제의 텐서 접근을 그대로 복사하거나 내부 백엔드 뷰에 직접 접근하지 않는다. 쿼터니언 순서도 3.0에서는 XYZW이므로 과거 WXYZ 예제를 섞으면 자세가 틀어진다. 변경 사항은 [Isaac Lab 3.0 마이그레이션 안내](https://isaac-sim.github.io/IsaacLab/v3.0.0-beta2/source/migration/migrating_to_isaaclab_3-0.html)를 기준으로 한다.

## 2.5 Direct와 Manager-based

두 방식은 알고리즘이 아니라 코드 조직 방식이다.

| 질문 | Direct | Manager-based |
|---|---|---|
| 행동 적용 위치 | `_apply_action()` | Action term |
| 관측 정의 | `_get_observations()` | Observation terms |
| 보상 정의 | `_get_rewards()` | Reward terms + weights |
| 종료 정의 | `_get_dones()` | Termination terms |
| 리셋 정의 | `_reset_idx()` | Event terms |
| 장점 | 호출 흐름이 한눈에 보임, 실험적 로직이 쉬움 | 조합·교체·검사·재사용이 쉬움 |
| 단점 | 커지면 한 클래스가 비대해짐 | 처음에는 간접 호출이 많아 보임 |

이 책은 Direct를 먼저 사용한다. 공의 좌표를 읽고 행동을 쓰는 시점을 이해한 뒤 Manager-based로 옮기면 manager가 “마법”이 아니라 같은 함수를 구조화한 것임을 알 수 있다. 공식 [환경 작성 튜토리얼](https://isaac-sim.github.io/IsaacLab/v3.0.0-beta2/source/tutorials/03_envs/create_manager_rl_env.html)도 manager term을 MDP 구성 요소별로 나눈다.

## 2.6 한 정책 스텝의 시간 순서

Direct 환경에서 한 정책 스텝은 대략 다음 순서다.

1. RSL-RL이 `[N, 2]` 행동을 출력한다.
2. `_pre_physics_step()`이 행동을 제한 범위로 자르고 이전 행동을 보관한다.
3. `_apply_action()`이 관절 위치 목표를 쓴다.
4. 물리 스텝이 `decimation`번 진행된다.
5. 종료, 보상, 관측을 계산한다.
6. 끝난 환경만 `_reset_idx(env_ids)`로 다시 시작한다.

`dt=1/120 s`, `decimation=4`이므로 정책 주기는 30 Hz다. 10초 에피소드는 300 정책 스텝이다. 물리 스텝과 정책 스텝을 혼동하면 행동 변화량 페널티, 시간 제한, 목표 궤적 주기가 모두 틀어진다.

## 2.7 확인 질문

다음에 답할 수 있으면 이 장을 마친다.

1. Isaac Sim 없이 Newton 학습이 가능한 이유는 무엇인가?
2. `ArticulationCfg`와 `Articulation`은 어떻게 다른가?
3. 병렬 환경에서 `env_origins`를 빼야 하는 이유는 무엇인가?
4. Direct와 Manager-based가 서로 다른 MDP를 뜻하지 않는 이유는 무엇인가?
5. `dt`와 `decimation`으로 정책 주기를 어떻게 계산하는가?

[← 1장](./01-system-requirements-and-installation.md) · [3장: URDF 작성과 USD 변환 →](./03-build-urdf-and-convert-usd.md)
