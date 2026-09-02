# 6. 학습·평가·디버깅

이 장에서 PPO는 환경을 시험하는 도구다. 알고리즘 수식은 [PPO 선수 자료](../pytorch-ppo-learning/index.md)에서 다루며, 여기서는 RSL-RL 연결과 실험 계약에 집중한다.

## 6.1 PPO 연결에서 알아야 할 최소 내용

RSL-RL 러너는 `num_steps_per_env`만큼 병렬 전이를 모으고, critic으로 advantage를 계산한 뒤 clipped PPO 갱신을 여러 epoch 수행한다. 환경 쪽에서 지켜야 할 계약은 다음뿐이다.

- 관측과 행동 크기가 매 스텝 일정하다.
- 보상은 `[N]`이고 NaN/Inf가 없다.
- 실패 종료와 시간 제한이 정확하다.
- 리셋 뒤 관측이 다음 에피소드의 정상 상태다.

[RSL-RL 설정](./examples/ball_on_plate_lab/source/ball_on_plate_lab/ball_on_plate_lab/tasks/agents/rsl_rl_ppo_cfg.py)은 작은 MLP `[128, 128]`, 24스텝 롤아웃, 최대 500회 반복을 사용한다. 이 값은 출발점이며 성공을 보장하는 마법의 조합이 아니다.

## 6.2 세 단계로 규모를 늘린다

### 단계 A: 파이프라인 확인

```bash
cd /absolute/path/to/IsaacLab
PROJECT=/absolute/path/to/ball_on_plate_lab

./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py \
  --task BallOnPlate-Direct-v0 \
  --external_callback ball_on_plate_lab.tasks.register \
  --headless --num_envs 16 --max_iterations 5 \
  physics=newton_mjwarp
```

이 단계의 통과 조건은 체크포인트·로그 디렉터리가 생기고 손실값이 유한한 것이다. 성능은 판단하지 않는다.

### 단계 B: 학습 가능성 확인

```bash
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py \
  --task BallOnPlate-Direct-v0 \
  --external_callback ball_on_plate_lab.tasks.register \
  --headless --num_envs 512 --max_iterations 100 \
  physics=newton_mjwarp
```

평균 에피소드 길이와 목표 보상이 전혀 변하지 않으면 2048개로 늘리기 전에 환경을 고친다.

### 단계 C: 기준 학습

```bash
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py \
  --task BallOnPlate-Direct-v0 \
  --external_callback ball_on_plate_lab.tasks.register \
  --headless --num_envs 2048 --max_iterations 500 \
  physics=newton_mjwarp
```

로그는 기본적으로 `logs/rsl_rl/ball_on_plate/<timestamp>/`에 생긴다. `model_*.pt`, `params/env.yaml`, `params/agent.yaml`을 함께 보관한다.

!!! note "왜 외부 callback이 필요한가"

    이 명령은 폐기 예정 표시가 있는 라이브러리별 스크립트를 의도적으로 사용한다. 3.0 beta2의 외부 프로젝트는 이 경로에서 콜백으로 등록하는 것이 작동 방식이다. 내부 Isaac Lab 태스크에 쓰는 통합 `train` 명령과 혼동하지 않는다.

## 6.3 첫 학습에서 볼 것

PPO loss 하나만 보지 않는다.

| 신호 | 좋아지는 방향 | 이상 징후 |
|---|---|---|
| 에피소드 길이 | 300스텝에 접근 | 계속 한 자릿수 |
| 목표 보상 | 증가 | 시작부터 최대값 고정 |
| action std | 서서히 감소 가능 | 즉시 0 또는 계속 폭증 |
| 가치 손실 | 유한, 완만 | NaN 또는 지속 폭증 |
| 평균 정규화 반경 | 감소 | 보상은 증가하지만 반경은 증가 |
| 생존율 | 증가 | 시간 제한과 실패가 뒤바뀜 |

보상이 좋아지는데 물리 지표가 나빠지면 보상 허점 악용이다. 예를 들어 생존 보상이 너무 크면 중심과 상관없이 최대한 늦게 떨어지는 전략이 높은 누적 보상을 받을 수 있다.

## 6.4 무작위 정책 기준선

학습 정책을 평가하기 전에 같은 시드의 무작위 행동을 측정한다.

```bash
./isaaclab.sh -p "$PROJECT/scripts/evaluate.py" \
  --task BallOnPlate-Direct-v0 \
  --random_policy --episodes 100 --seed 20260902 --headless \
  physics=newton_mjwarp
```

JSON을 `random_newton.json`으로 보관한다.

```bash
./isaaclab.sh -p "$PROJECT/scripts/evaluate.py" \
  --task BallOnPlate-Direct-v0 \
  --random_policy --episodes 100 --seed 20260902 --headless \
  physics=newton_mjwarp | tee random_newton.json
```

## 6.5 학습 정책 평가

평가할 체크포인트를 명시한다. “가장 최근”을 자동 선택하면 실험 재현성이 떨어진다.

```bash
CHECKPOINT=/absolute/path/to/logs/rsl_rl/ball_on_plate/RUN/model_500.pt

./isaaclab.sh -p "$PROJECT/scripts/evaluate.py" \
  --task BallOnPlate-Direct-v0 \
  --checkpoint "$CHECKPOINT" \
  --episodes 100 --seed 20260902 --headless \
  physics=newton_mjwarp | tee policy_newton.json
```

통과 조건은 세 가지다.

```text
survival_rate >= 0.90
center_residence_rate >= 0.80
policy survival_rate > random survival_rate
policy mean_normalized_radius < random mean_normalized_radius
```

점수가 기준에 못 미치면 숨기지 않는다. 체크포인트, 시드, 반복 횟수, 환경 변경 내역을 기록하고 실패 원인을 다음 순서로 좁힌다.

## 6.6 디버깅 순서

### 1. 환경 계약

```python
assert obs.shape == (num_envs, 12)
assert torch.isfinite(obs).all()
assert torch.isfinite(reward).all()
assert actions.shape == (num_envs, 2)
```

잘못된 크기, NaN, 잘못된 종료 값은 하이퍼파라미터로 고칠 수 없다.

### 2. 기하와 리셋

- 초기 반경이 항상 `≤0.25 m`인지 확인한다.
- 초기 z가 원판 윗면보다 공 반지름만큼 높은지 확인한다.
- `env_1` 이상에서도 로컬 위치가 원점 근처인지 확인한다.
- 리셋된 관절 목표와 행동 이력이 0인지 확인한다.

### 3. actuator 방향

단일 환경에서 수동 행동을 넣는다. `roll=+`일 때 공이 어느 y 방향으로 가는지, `pitch=+`일 때 어느 x 방향으로 가는지 기록한다. 기대 방향이 반대여도 학습은 가능하지만, 두 백엔드에서 방향이 같아야 한다.

### 4. 보상 항 크기

각 항의 평균과 최대값을 따로 로그한다. 목표 항이 `0~1`, 속도 페널티 원값이 `m²/s²`, 기울기가 정규화 제곱이라는 단위를 기억한다. 계수만 보고 영향력을 판단하지 않는다.

### 5. PPO

환경이 무작위·수동 정책에서 정상일 때만 학습률, 엔트로피, 롤아웃 길이를 조정한다. 다음은 한 번에 하나씩 바꿀 후보 순서다.

1. 학습률 `5e-4 → 3e-4`
2. 초기 action std `0.6 → 0.4`
3. rollout `24 → 32`
4. 네트워크 `[128,128] → [256,128]`

동시에 모두 바꾸면 무엇이 효과였는지 알 수 없다.

## 6.7 평가 스크립트의 한계

[evaluate.py](./examples/ball_on_plate_lab/scripts/evaluate.py)는 각 환경에서 첫 번째 에피소드 하나를 수집해 총 100회로 만든다. 종료 스텝 뒤 자동으로 리셋된 관측은 지표에 넣지 않고, 스텝 직전의 마지막 유효 관측까지 집계한다. 이 정의를 무작위 정책과 학습 정책에 똑같이 적용하므로 비교는 공정하다.

현재 문서 작성 PC에서는 수치를 생성하지 않았다. 따라서 이 책은 검증하지 않은 “예상 성공률”을 제시하지 않는다. 대상 GPU에서 얻은 JSON이 실제 결과다.

## 6.8 재현 보고서 최소 항목

```text
GPU / driver:
Ubuntu:
Isaac Lab commit:
Isaac Sim:
PyTorch / CUDA runtime:
task ID / backend:
num_envs / iterations:
checkpoint SHA-256:
evaluation seed:
random metrics:
policy metrics:
pass/fail and next experiment:
```

[← 5장](./05-direct-environment.md) · [7장: Manager-based 환경 →](./07-manager-based-environment.md)
