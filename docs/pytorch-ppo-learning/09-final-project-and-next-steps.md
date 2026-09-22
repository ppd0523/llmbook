# 최종 프로젝트와 다음 단계

이 장의 중심 질문은 **“독립적으로 재현 가능한 PPO 실험을 어떻게 완성하는가?”** 다. 코드를 한 번 실행해 높은 점수를 보는 데서 끝내지 않고, 기준선·여러 seed·평가 protocol·ablation을 갖춘 작은 연구 프로젝트로 마무리한다.

## 학습 목표

이 장을 마치면 다음을 할 수 있다.

1. 성공 기준과 계산 예산을 학습 전에 정한다.
2. 직접 구현 PPO의 여러 seed 결과를 동일한 protocol로 평가한다.
3. 한 가지 ablation을 수행하고 여러 지표로 해석한다.
4. 코드, 설정, checkpoint, 결과표를 다른 사람이 재현할 수 있게 남긴다.
5. 다음 학습 주제를 목표에 따라 선택한다.

## 프로젝트 질문

다음 질문에 답하는 보고서를 만든다.

> 직접 구현한 PyTorch PPO는 CartPole-v1에서 random policy보다 반복 가능하게 나은가? PPO의 한 구성요소를 바꾸면 성능과 update 지표가 어떻게 달라지는가?

결과가 기대보다 낮아도 프로젝트는 실패가 아니다. 사전에 정한 절차로 원인을 좁히고 한계를 정확히 쓰면 유효한 결과다.

## 프로젝트 용어를 먼저 고정한다

- **Benchmark(벤치마크)**: 방법을 같은 조건에서 비교하기 위한 환경·데이터·지표·절차의 묶음이다. 이 프로젝트의 작은 benchmark는 `CartPole-v1`과 정해진 평가 protocol이다.
- **사전등록(preregistration)**: 결과를 보기 전에 질문, 성공 기준, seed, 예산, 분석법을 기록하는 일이다. 나중에 판단 기준을 유리하게 바꾸는 일을 줄인다.
- **선택 편향(selection bias)**: 관찰하거나 보고할 대상을 고르는 과정 때문에 결과가 한쪽으로 치우치는 현상이다. 가장 잘된 seed만 보고하는 것이 대표적이다.
- **Ablation**: 나머지 조건은 고정하고 구성요소 하나만 제거하거나 바꾸는 실험이다.
- **Rubric(채점 기준표)**: 결과물의 여러 측면을 미리 정한 단계별 기준으로 평가하는 표다.
- **상관관계(correlation)**: 두 값이 함께 변하는 통계적 패턴이다. 한 값이 다른 값의 원인이라는 **인과관계(causation)** 를 그 자체로 증명하지 않는다.

## 산출물

```text
ppo-project/
├─ README.md                 # 질문, 환경, 실행법, 결론
├─ config-baseline.json      # 기준 설정
├─ config-ablation.json      # 한 가지만 바꾼 설정
├─ results.csv               # seed별 학습·평가 결과
├─ metrics/                  # 학습 로그 또는 곡선 데이터
├─ checkpoints/              # seed별 모델
└─ report.md                 # 표, 그림, 해석, 한계
```

이 책의 예제 파일을 복사해 시작해도 되지만, 변경 사항은 diff로 설명할 수 있어야 한다.

## 1단계: 실험을 먼저 등록한다

코드를 돌리기 전에 다음 표를 채운다.

| 항목 | 기준 예시 | 직접 결정할 값 |
|---|---|---|
| 환경 | `CartPole-v1` | |
| 구현 | `examples/ppo_cartpole.py` | |
| 학습 seed | 1, 2, 3 | |
| 총 step | seed당 100,000 | |
| 평가 | deterministic, seed당 10 episodes | |
| 기준선 | random policy 100 episodes | |
| 주 성공 지표 | 평가 return 평균 | |
| 보조 지표 | entropy, KL, clip fraction, EV | |
| ablation | clip 0.2 → 0.1 | |
| 계산 예산 | 최대 실행 수·시간 | |
| 중단 규칙 | NaN 또는 예산 소진 | |

결과를 본 뒤 성공 기준이나 평가 episode 수를 바꾸면 선택 편향이 생긴다. 바꿔야 한다면 변경 시점과 이유를 기록한다.

## 2단계: 작은 검사부터 통과한다

```powershell
cd docs\pytorch-ppo-learning
python -m unittest discover -s tests -v
python examples\ppo_cartpole.py --smoke-test
```

다음 게이트를 모두 통과한 뒤 여러 seed를 실행한다.

- GAE와 clipping 단위 테스트가 통과한다.
- environment step이 유효한 action과 종료 신호를 반환한다.
- 첫 update 전 ratio가 1에 가깝다.
- loss와 gradient가 finite다.
- checkpoint 저장 후 다시 읽어 평가할 수 있다.

## 3단계: 기준 PPO를 여러 seed로 학습한다

```powershell
1, 2, 3 | ForEach-Object {
    python examples\ppo_cartpole.py `
        --seed $_ `
        --total-steps 100000 `
        --eval-interval 10 `
        --checkpoint "checkpoints\baseline-seed$_.pt" `
        --metrics-csv "metrics\baseline-seed$_.csv"
}
```

세 seed는 학습용 최소선이다. 최종 결론의 신뢰도를 높이려면 계산 예산 안에서 5~10개로 늘린다. 가장 잘 나온 seed 하나만 선택하지 않는다.

평가는 학습과 분리한다.

```powershell
python examples\ppo_cartpole.py `
    --eval-only `
    --checkpoint checkpoints\baseline-seed1.pt `
    --eval-episodes 10
```

학습 중 stochastic action과 평가지표의 deterministic action을 구분해 보고서에 쓴다. 세 방식이 각각 어떤 질문에 답하는지는 [7장의 평가 방식 표](./07-debug-and-experiment.md)를 따른다.

저장한 곡선을 한 그림에 겹친다.

```powershell
python examples\plot_metrics.py `
    metrics\baseline-seed1.csv `
    metrics\baseline-seed2.csv `
    metrics\baseline-seed3.csv `
    --output metrics\baseline.svg
```

예제 plotter는 각 seed의 원자료 선을 보존한다. Seed 평균과 신뢰구간 띠를 추가하려면 CSV의 같은 `steps` 행들을 설정별로 묶어 평균·표준오차를 계산한다.

## 4단계: 한 가지 ablation

후보와 각 변경에서 관찰할 지표는 [7장의 비교 실험 표](./07-debug-and-experiment.md)에 정리되어 있다. 첫 프로젝트에서는 그중 **하나만** 고른다. 두 개 이상을 동시에 바꾸면 결과의 원인을 분리할 수 없다.

기준과 변경 설정은 같은 학습 seed, 같은 총 환경 step, 같은 평가 protocol을 사용한다. 실행 시간이 아니라 환경 상호작용 수를 주 예산으로 삼으면 비교가 더 공정하다.

예를 들어 clip 폭만 0.1로 바꾸는 실행은 다음과 같다.

```powershell
1, 2, 3 | ForEach-Object {
    python examples\ppo_cartpole.py `
        --seed $_ `
        --total-steps 100000 `
        --clip-epsilon 0.1 `
        --eval-interval 10 `
        --checkpoint "checkpoints\clip01-seed$_.pt" `
        --metrics-csv "metrics\clip01-seed$_.csv"
}
```

## 5단계: 결과표와 그림

최소 표 형식:

| 설정 | seed | 마지막 평가 평균 | 최고 평가 평균 | 최종 entropy | 최종 KL | 최종 EV |
|---|---:|---:|---:|---:|---:|---:|
| baseline | 1 |  |  |  |  |  |
| baseline | 2 |  |  |  |  |  |
| baseline | 3 |  |  |  |  |  |
| ablation | 1 |  |  |  |  |  |
| ablation | 2 |  |  |  |  |  |
| ablation | 3 |  |  |  |  |  |

그림에는 다음을 포함한다.

1. x축을 environment step으로 한 평가 return 곡선
2. seed별 얇은 선과 seed 평균의 굵은 선
3. 가능하면 표준편차 또는 신뢰구간 띠
4. KL과 clip fraction의 보조 곡선
5. entropy와 explained variance의 보조 곡선

곡선을 지나치게 매끈하게 만들지 않는다. **이동평균(moving average)** 은 각 지점과 그 직전 일정 개수의 평균으로 잡음을 줄인 선이다. 그 개수를 **window 크기**라 한다. 큰 window는 추세를 보기 쉽지만 급격한 변화를 숨기고 선을 시간상 늦춰 보일 수 있다. 사용하면 크기를 명시하고 원자료도 보존한다.

## 6단계: 해석

다음 순서로 쓴다.

1. **사실:** “세 seed 중 두 seed에서 100k step 전에 return이 상승했다.”
2. **지표 연결:** “동시에 KL과 clip fraction은 … 범위였고 entropy는 … 했다.”
3. **가능한 설명:** “변경 설정이 update 크기를 줄였을 가능성이 있다.”
4. **대안 설명:** “하지만 seed 수가 작고 CartPole 하나만 사용했다.”
5. **다음 검증:** “같은 설정으로 seed를 늘리거나 다른 환경에서 반복한다.”

상관관계를 원인으로 단정하지 않는다. 예를 들어 entropy 감소와 return 상승이 함께 보였다는 사실만으로 entropy 감소가 상승의 원인이라고 결론 내릴 수 없다. Policy가 유용한 행동을 배우면서 두 값이 함께 변했거나, 제3의 요인이 둘 모두를 바꿨을 수 있다.

## 완료 기준 Rubric

| 영역 | 0점 | 1점 | 2점 |
|---|---|---|---|
| 정확성 | 실행 불가·수식 오류 | smoke 실행 | 단위 테스트와 여러 seed 실행 |
| 평가 | 학습 return 한 번 | 분리 평가 한 seed | 동일 protocol의 여러 seed |
| 비교 | 비교 없음 | 여러 값 동시 변경 | 한 변수 ablation |
| 관찰 | return만 기록 | 손실 일부 기록 | KL·clipfrac·entropy·EV 함께 기록 |
| 재현성 | 설정 미기록 | 명령 일부 기록 | 버전·seed·명령·checkpoint 기록 |
| 해석 | 성공/실패 단정 | 경향 기술 | 대안 설명과 한계 포함 |

총 12점 중 10점 이상이며 각 영역이 1점 이상이면 이 입문 과정의 최종 목표를 달성한 것으로 본다.

## 정리

- 성공 기준과 계산 예산은 학습을 시작하기 전에 적는다. 나중에 정하면 결과에 맞춰 기준이 움직인다.
- 기준과 변경 설정은 같은 seed 집합, 같은 총 환경 step, 같은 평가 protocol을 쓴다.
- 가장 잘 나온 seed만 보고하지 않는다. seed별 원자료를 함께 남긴다.
- 재현 패키지는 코드, 설정, checkpoint, 결과표, 곡선을 함께 담는다.
- 다음 학습 주제는 목표에 따라 고른다. 남은 주제는 각각 별도 과정 규모임을 전제한다.

## 최종 개념 점검

아래 질문에 코드를 보지 않고 답해 본다.

1. 강화학습 데이터가 서로 독립이며 같은 분포에서 나왔다고 보기 어려운 이유는 무엇인가?
2. Critic이 policy를 직접 선택하지 않는데 actor 학습을 어떻게 돕는가?
3. 시간 제한에서 value bootstrap과 GAE 재귀를 서로 다른 mask로 처리하는 이유는 무엇인가?
4. PPO가 old policy의 log probability를 저장해야 하는 이유는 무엇인가?
5. Positive advantage와 negative advantage에서 clipping의 의미가 왜 다른가?
6. 같은 rollout을 여러 epoch 쓰고도 PPO를 on-policy라고 부르는 이유는 무엇인가?
7. 학습 return과 평가 return을 분리해야 하는 이유는 무엇인가?
8. TorchRL의 replay buffer가 이 예제에서 off-policy replay가 아닌 이유는 무엇인가?

??? note "핵심 답"
    1번: 연속 transition이 같은 trajectory에 의존하며 policy update가 데이터 분포 자체를 바꾸기 때문이다. 2번: return을 예측해 baseline을 제공하고 advantage 분산을 줄인다. 3번: truncation은 MDP의 terminal이 아니므로 bootstrap은 유지하지만 episode 경계를 넘어 GAE를 전파하지는 않는다. 4번: 현재 정책과 수집 정책 확률의 ratio를 계산하기 위해서다. 5번: 좋은 행동 확률의 과도한 증가와 나쁜 행동 확률의 과도한 감소를 각각 제한해야 한다. 6번: 한 수집 batch 안에서 제한적으로 재사용하고 다음 update에는 새 현재 정책으로 다시 수집하기 때문이다. 7번: 학습 중 탐색과 update noise를 고정된 평가 protocol과 구분하기 위해서다. 8번: 한 rollout의 mini-batch 섞기에만 쓰고 다음 rollout 전에 비우기 때문이다.

## 다음 학습 경로

### RL 기반을 넓히고 싶다

Stanford·MIT의 전통적인 순서를 따라 다음 키워드를 공부한다.

```text
iterative policy evaluation
→ policy iteration / value iteration
→ Monte Carlo prediction
→ TD(0)
→ SARSA / Q-learning
→ function approximation
→ DQN
```

이 내용은 한 장에 책임 있게 압축하기에는 양이 많아 이 책에서는 상세 구현을 생략했다. PPO만 아는 것보다 value-based 방법을 함께 알면 on-policy와 off-policy, policy search와 value control의 차이가 선명해진다.

### 연속 제어로 가고 싶다

8장의 `Pendulum-v1`에서 시작해 다음을 공부한다.

- multivariate normal과 여러 action 차원의 상관관계
- `tanh` transformation의 log probability correction
- action rescaling과 environment spec
- observation·reward normalization
- vectorized environment와 병렬 collector
- 기존 제어 행동에 PPO 보정 행동을 더하는 residual reinforcement learning
- MuJoCo 또는 로봇 시뮬레이터의 termination 설계

여러 변수의 함께 움직이는 정도를 나타내는 covariance, 확률변수 변환, 물리 시뮬레이션은 양이 큰 선수지식이다. 부족하다면 `multivariate Gaussian`, `change of variables`, `Jacobian determinant`, `control timestep`을 별도 학습 키워드로 잡는다. 기존 PID·모델 기반 제어기가 있다면 8장의 잔차 강화학습 구분을 읽은 뒤 `base controller`, `residual action scale`, `action saturation`을 추가 키워드로 학습한다.

### 직접 환경을 만들고 싶다

다음을 먼저 명세한다.

- observation이 의사결정에 충분한가?
- action의 단위와 안전 범위는 무엇인가?
- reward는 목표를 대리하면서 악용되기 쉬운 구멍이 없는가?
- `terminated`와 `truncated` 조건은 무엇인가?
- random policy와 손으로 만든 간단한 policy의 기준선은 무엇인가?

Gymnasium contract를 구현한 뒤 `check_env_specs`, random rollout, deterministic test 순으로 검증한다.

### 대규모·고급 PPO로 가고 싶다

다음 주제는 각각 별도 과정이 필요한 규모다.

- **Recurrent policy**: 이전 관측을 hidden state라는 기억에 보존해 부분 관측 문제를 다룬다.
- **Convolutional policy**: 이미지의 가까운 픽셀 패턴을 처리하는 convolution 층을 사용한다.
- **Distributed rollout**: 여러 환경·프로세스가 병렬로 데이터를 수집해 처리량을 높인다.
- **Multi-agent PPO**: 여러 agent가 협력하거나 경쟁하는 환경으로 확장한다.
- **Constrained/safe RL**: reward 외에 위반하면 안 되는 비용·안전 제약을 함께 다룬다.
- **Offline RL과 imitation learning**: 환경을 새로 실행하지 않고 고정 데이터로 학습하거나 전문가 행동을 모방한다.
- **인간 피드백 강화학습(Reinforcement Learning from Human Feedback, RLHF)**: 사람의 선호 데이터로 만든 reward model을 사용해 정책을 조정한다.

특히 RLHF에서 말하는 PPO는 이 책의 policy ratio 개념을 공유하지만 language model token sequence, reference model, reward model, 대규모 분산 학습이 추가된다. CartPole PPO 다음 단계로 바로 같은 난이도라고 보지 않는다.

## 과정 마무리 체크리스트

- [ ] Gymnasium transition 다섯 반환값을 설명할 수 있다.
- [ ] Return, value, advantage, TD 오차·잔차, GAE를 구분한다.
- [ ] 회귀 잔차, TD 잔차, 신경망 잔차 연결, 잔차 강화학습을 구분한다.
- [ ] `Categorical` policy의 sample과 log probability를 계산한다.
- [ ] PPO ratio와 clipping을 advantage 부호별로 설명한다.
- [ ] 직접 구현의 rollout과 update 경계를 찾는다.
- [ ] 단위 테스트와 smoke test를 실행한다.
- [ ] 여러 seed와 분리 평가로 결과를 보고한다.
- [ ] TorchRL primitive를 직접 구현 요소에 대응한다.
- [ ] 실패 로그에서 환경·수식·최적화 문제를 순서대로 좁힌다.

모든 항목이 체크되면 목표는 “PPO 코드를 실행했다”가 아니라 **“PyTorch PPO를 읽고, 실행하고, 검증하고, 한 가지 가설을 실험할 수 있다”** 로 바뀐다.

## 핵심 용어·기호 빠른 찾기

이 표는 첫 설명을 대신하는 사전이 아니라 복습용 색인이다. 뜻이 모호하면 표시된 장의 본문과 worked example로 돌아간다.

| 용어·기호 | 한 줄 뜻 | 처음 자세히 다룬 장 |
|---|---|---:|
| agent / environment | 행동하는 주체 / 그 행동에 반응하는 바깥 시스템 | 1 |
| state $s_t$ / observation $o_t$ | 의사결정에 충분한 상태 / agent가 실제로 보는 정보 | 1 |
| action $a_t$ / reward $r_t$ | 선택 / 한 transition 뒤의 즉시 평가 신호 | 1 |
| policy $\pi_\theta(a\mid s)$ | 상태에서 행동분포를 만드는 파라미터 함수 | 1 |
| trajectory $\tau$ / episode | transition의 시간 열 / 자연·시간 제한 경계까지의 한 실행 | 1, 4 |
| MDP / POMDP | Markov 상태를 가정한 문제 / 관측만으로 상태가 불완전한 문제 | 1 |
| on-policy / off-policy | 현재 정책 데이터 사용 / 다른 정책 데이터도 사용 | 1 |
| return $G_t$ / discount $\gamma$ | 미래 reward의 할인합 / 먼 미래의 가중치 | 2 |
| expectation / variance | 확률 가중 평균 / 평균 주위의 흔들림 | 2 |
| $V^\pi$, $Q^\pi$, $A^\pi$ | 상태 가치, 행동 가치, 평균 대비 행동 이점 | 2 |
| residual $e=y-\hat y$ | target에서 예측을 뺀 아직 설명하지 못한 차이 | 2 |
| TD error / TD residual $\delta_t$ | 한 스텝 TD target과 현재 가치 예측의 차이 | 2, 4 |
| residual connection | 입력에 신경망 보정값을 더하는 $h+F(h)$ 구조 | 8 |
| residual reinforcement learning | 기존 제어 행동에 학습한 보정 행동을 더하는 설계 | 8 |
| actor / critic | 행동분포 모델 / 상태 가치 모델 | 3, 4 |
| logits / softmax / entropy | 정규화 전 점수 / 확률 변환 / 분포 불확실성 | 3 |
| gradient / optimizer / loss | 변화 방향 / 파라미터 갱신법 / 줄일 목적값 | 2, 3 |
| GAE / $\lambda$ | 여러 길이 TD 잔차의 가중합 / 길이 혼합 계수 | 4 |
| old/new log probability | 수집 정책 / 갱신 중 현재 정책의 선택 행동 로그확률 | 5 |
| ratio $r_t(\theta)$ | 새 선택 행동 확률을 old 확률로 나눈 값 | 5 |
| clip $\epsilon$ / KL | ratio 목적의 제한 폭 / 두 정책분포 차이 척도 | 5 |
| rollout / mini-batch / epoch | 수집 묶음 / 갱신 조각 / 묶음 전체 1회 학습 | 5 |
| terminated / truncated | MDP 자연 종료 / 외부 시간 제한 종료 | 1, 4 |
| seed / protocol / ablation | 난수 시작값 / 고정 절차 / 한 요소 변경 실험 | 7, 9 |

## 참고문헌

- Schulman et al. (2017), [*Proximal Policy Optimization Algorithms*](https://arxiv.org/abs/1707.06347)
- Schulman et al. (2015), [*High-Dimensional Continuous Control Using Generalized Advantage Estimation*](https://arxiv.org/abs/1506.02438)
- Johannink et al. (2019), [*Residual Reinforcement Learning for Robot Control*](https://arxiv.org/abs/1812.03201)
- [PyTorch 공식 TorchRL PPO 튜토리얼](https://docs.pytorch.org/tutorials/intermediate/reinforcement_ppo.html)
- [OpenAI Spinning Up: PPO](https://spinningup.openai.com/en/latest/algorithms/ppo.html)
- [Stanford CS234](https://web.stanford.edu/class/cs234/)
- [UC Berkeley CS 185/285](https://rail.eecs.berkeley.edu/deeprlcourse/)
- [MIT OCW 2.997 syllabus](https://ocw.mit.edu/courses/2-997-decision-making-in-large-scale-systems-spring-2004/pages/syllabus/)

[← 8장](./08-use-ppo-with-torchrl.md) · [목차](./index.md)
