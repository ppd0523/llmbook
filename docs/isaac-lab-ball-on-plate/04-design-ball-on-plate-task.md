# 4. Ball-on-Plate MDP 설계

강화학습 환경의 품질은 PPO 설정 전에 결정된다. 이 장에서는 구현보다 먼저 관측, 행동, 보상, 종료, 리셋을 수치로 고정한다. Direct와 Manager-based는 이 명세를 공동으로 사용한다.

## 4.1 과제 문장

정책은 30 Hz로 원판의 roll·pitch 목표 각도를 정한다. 공 중심이 사용 가능한 원판 영역 안에 머물면서 목표점에 가까워지도록 제어한다. 기본 목표점은 원판 중심이고, 최종 과제에서는 반지름 `0.15 m`의 원을 5초 주기로 움직인다.

기하 상수는 다음과 같다.

| 기호 | 값 | 의미 |
|---|---:|---|
| `R` | 0.50 m | 원판 반지름 |
| `r_b` | 0.04 m | 공 반지름 |
| `R_safe` | 0.46 m | 공 중심이 머물 수 있는 최대 반지름 `R-r_b` |
| `R_center` | 0.125 m | 중심 체류 판정 반지름 `0.25R` |
| `theta_max` | 0.20944 rad | 각 축 최대 목표 각도, 약 12도 |

## 4.2 상태와 관측은 다르다

시뮬레이터의 완전한 상태에는 공의 3D pose와 속도, 원판 link pose, joint state, 접촉 정보, 물리 파라미터가 포함된다. 정책에 모두 줄 필요는 없다. 이 과제는 수평 이동과 원판 기울기만으로 관측 가능한 12차원 벡터를 쓴다.

| 순서 | 항목 | 차원 | 정규화 |
|---:|---|---:|---|
| 1 | 공 위치 − 목표 위치 | 2 | `R`로 나눔 |
| 2 | 목표 위치 | 2 | `R`로 나눔 |
| 3 | 공의 세계 x/y 선속도 | 2 | 그대로, m/s |
| 4 | roll/pitch 관절 위치 | 2 | `theta_max`로 나눔 |
| 5 | roll/pitch 관절 속도 | 2 | 그대로, rad/s |
| 6 | 직전 정규화 행동 | 2 | 이미 `[-1, 1]` |

기본 중심 과제에서도 목표 위치 두 칸은 0으로 남긴다. 그러면 움직이는 목표점 과제로 갈 때 네트워크 입력 크기와 체크포인트 형식을 바꾸지 않아도 된다.

관측은 [공유 `task_observation()`](./examples/ball_on_plate_lab/source/ball_on_plate_lab/ball_on_plate_lab/tasks/common.py)에서 한 번만 정의된다.

```python
torch.cat(
    (
        (local_ball_xy - target) / PLATE_RADIUS,
        target / PLATE_RADIUS,
        ball_velocity_xy,
        joint_pos / MAX_TILT_RAD,
        joint_vel,
        last_action,
    ),
    dim=-1,
)
```

### 포함하지 않은 것

- 공의 z 위치: 정상 상태에서는 plate geometry가 정하고, 실패 판정에만 쓴다.
- 공의 quaternion과 angular velocity: 완전한 물리 상태지만 중심 안정화에 필수는 아니다.
- 접촉 센서: 단순 과제에서 프레임워크 학습을 방해하는 복잡도를 추가한다.
- 마찰 계수: 무작위화한 숨은 물리 파라미터다. 정책은 운동 결과를 통해 적응한다.

## 4.3 행동

정책 출력 `a ∈ [-1, 1]^2`를 목표 각도로 선형 변환한다.

\[
q_{target} = \theta_{max}\,\mathrm{clip}(a,-1,1)
\]

행동 0은 수평, `a=[1,-1]`은 roll +12도와 pitch -12도다. joint effort를 직접 출력하지 않고 position target을 쓰는 이유는 이 책의 관심이 저수준 모터 제어가 아니라 환경 구조이기 때문이다. URDF importer와 `ImplicitActuatorCfg`의 PD drive가 목표 각도를 추종한다.

## 4.4 보상

각 스텝의 보상은 다음 항의 합이다.

\[
r_t = 0.2
+ \exp(-4 d_t^2)
- 0.05\lVert v_{xy}\rVert^2
- 0.02\lVert q/\theta_{max}\rVert^2
- 0.01\lVert a_t-a_{t-1}\rVert^2
- 2.0\,\mathbb{1}_{failure}
\]

여기서 `d_t`는 공과 목표 사이 거리를 `R`로 나눈 값이다.

- `alive`: 살아 있는 매 스텝에 작은 양수. 긴 에피소드의 가치를 만든다.
- `target`: 중심에 가까울수록 최대 1.0인 부드러운 핵심 보상.
- `speed`: 중심을 빠르게 통과하기만 하는 행동을 줄인다.
- `tilt`: 계속 최대 각도로 붙는 정책을 억제한다.
- `action_rate`: 매 스텝 반대 방향으로 떨리는 명령을 줄인다.
- `failure`: 경계 이탈을 명확히 불리하게 만든다.

보상 스케일은 정답이 아니라 시작점이다. 그러나 항을 추가하기 전에 각 항의 평균 크기를 로그로 확인한다. 작은 계수라도 원래 값이 100이면 지배적일 수 있다.

## 4.5 종료와 시간 제한

실패 종료는 두 조건의 OR다.

```python
radius > PLATE_RADIUS - BALL_RADIUS
local_ball_z < 0.08
```

공의 **중심**이 원판 반지름 `R`에 닿을 때까지 기다리면 공 절반이 이미 밖으로 나간다. 따라서 `R-r_b`를 쓴다. z 조건은 수치 오차로 충돌 면을 뚫거나 잘못된 충돌 형상 때문에 공이 아래로 빠지는 경우를 잡는다.

10초가 끝난 시간 제한은 실패 종료와 구분한다. RSL-RL은 시간 제한에서 가치 부트스트래핑을 다르게 처리할 수 있고, 평가의 생존율도 `시간 제한으로 끝난 에피소드 / 전체 에피소드`로 정의하기 때문이다.

## 4.6 리셋 분포

공을 중심으로부터 `0.5R` 이내에 둔다. 반지름을 단순히 균일 분포에서 뽑으면 중심에 표본이 몰린다. 원판 면적에 균일하게 놓으려면 다음처럼 제곱근을 쓴다.

\[
\rho = 0.5R\sqrt{u},\quad \phi=2\pi v,
\qquad u,v\sim U(0,1)
\]

```python
radius = INITIAL_RADIUS * torch.sqrt(torch.rand(count, device=device))
angle = 2.0 * math.pi * torch.rand(count, device=device)
x = radius * torch.cos(angle)
y = radius * torch.sin(angle)
```

초기 x/y 속도는 각각 `[-0.15, 0.15] m/s`에서 뽑는다. 원판과 공의 마찰·반발 계수도 시작 이벤트에서 범위 내 무작위화한다. Isaac Lab 3.0의 재질 무작위화 기능은 Newton과 PhysX를 감지해 백엔드별 구현을 사용한다. [공식 이벤트 API](https://isaac-sim.github.io/IsaacLab/v3.0.0-beta2/source/api/lab/isaaclab.envs.mdp.html)가 두 백엔드의 차이를 설명한다.

## 4.7 평가 계약

학습 보상은 설계 도구이고, 성공 기준은 독립된 물리 지표다. 고정 시드 `20260902`로 100회 평가한다.

| 지표 | 정의 | 통과 |
|---|---|---:|
| 생존율 | 시간 제한으로 끝난 에피소드 / 100 | 90% 이상 |
| 중심 체류율 | `radius ≤ 0.25R`인 스텝 / 전체 스텝 | 80% 이상 |
| 평균 정규화 반경 | 모든 스텝의 `radius/R` 평균 | 무작위 정책보다 작음 |
| 기준선 비교 | 동일 시드·백엔드·환경 수의 무작위 행동 | 생존율도 학습 정책이 큼 |

평가 코드가 관측에서 공 위치를 복원하는 이유도 관측 계약을 검증하기 위해서다.

```python
normalized_ball_xy = obs[:, 0:2] + obs[:, 2:4]
```

첫 항은 `(ball-target)/R`, 둘째 항은 `target/R`이므로 합은 `ball/R`다.

## 4.8 설계 검토 질문

1. 공 위치를 세계 원점 기준으로 계산한 곳이 없는가?
2. 실패 경계가 `R`이 아니라 `R-r_b`인가?
3. 시간 제한과 물리 실패를 구분하는가?
4. 움직이는 목표점에서도 관측 크기가 12로 유지되는가?
5. Direct와 Manager-based가 같은 상수와 함수를 참조하는가?
6. 평가 지표가 보상과 독립적인가?

[← 3장](./03-build-urdf-and-convert-usd.md) · [5장: Direct 환경 구현 →](./05-direct-environment.md)
