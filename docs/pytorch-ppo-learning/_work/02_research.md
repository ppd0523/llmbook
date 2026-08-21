---
title: PyTorch PPO 입문 조사 노트
version: 1.0
status: final
owner: agent
updated: 2026-08-21
target_reader: 강화학습과 PyTorch 초심자
topic: PPO-Clip, PyTorch, Gymnasium, TorchRL
---

# 조사 노트

## 1. 핵심 출처

| 구분 | 제목/문서 | 링크 | 사용할 내용 | 신뢰도 |
|---|---|---|---|---|
| 원 논문 | Schulman et al., *Proximal Policy Optimization Algorithms* (2017) | <https://arxiv.org/abs/1707.06347> | clipped surrogate, 여러 epoch의 mini-batch 업데이트, 전체 알고리즘 | 높음 |
| 원 논문 | Schulman et al., *High-Dimensional Continuous Control Using Generalized Advantage Estimation* (2015) | <https://arxiv.org/abs/1506.02438> | TD residual과 GAE | 높음 |
| 대학 강의 | Stanford CS234 Winter 2026 | <https://web.stanford.edu/class/cs234/modules.html> | RL 소개, tabular MDP planning, policy evaluation 뒤에 policy gradient를 배치하는 선수 구조 | 높음 |
| 대학 강의 | UC Berkeley CS 185/285 Spring 2026 | <https://rail.eecs.berkeley.edu/deeprlcourse/> | PyTorch·확률 복습, RL 기초, policy gradient, actor–critic, advanced policy gradient 순서와 과제 중심 학습 | 높음 |
| 대학 강의 | MIT OCW 2.997 *Decision Making in Large Scale Systems* | <https://ocw.mit.edu/courses/2-997-decision-making-in-large-scale-systems-spring-2004/pages/syllabus/> | MDP·가치/정책 반복에서 policy gradient와 actor–critic으로 이어지는 고전적 순서 확인 | 높음 |
| 공식 교육자료 | OpenAI Spinning Up: PPO | <https://spinningup.openai.com/en/latest/algorithms/ppo.html> | PPO-Clip 직관, 수식, 의사코드 | 높음 |
| 공식 문서 | PyTorch 2.13 문서 | <https://docs.pytorch.org/docs/stable/> | tensor, autograd, optimizer, distribution, gradient clipping, checkpoint | 높음 |
| 공식 문서 | `torch.distributions` | <https://docs.pytorch.org/docs/stable/distributions.html> | `Categorical`, `Normal`, `sample`, `log_prob`, `entropy` | 높음 |
| 공식 문서 | Gymnasium 기본 사용법 | <https://gymnasium.farama.org/main/introduction/basic_usage/> | `reset`, `step`, 환경 루프 | 높음 |
| 공식 문서 | Gymnasium 시간 제한 처리 | <https://gymnasium.farama.org/main/tutorials/handling_time_limits/> | termination과 truncation의 bootstrap 차이 | 높음 |
| 공식 문서 | CartPole-v1 | <https://gymnasium.farama.org/environments/classic_control/cart_pole/> | 관측·행동·보상·종료 조건 | 높음 |
| 공식 문서 | TorchRL 0.13 | <https://docs.pytorch.org/rl/stable/> | 환경, TensorDict, collector, module, objective 구조 | 높음 |
| 공식 튜토리얼 | PyTorch PPO with TorchRL | <https://docs.pytorch.org/tutorials/intermediate/reinforcement_ppo.html> | TorchRL PPO 학습 구성요소와 연결 순서 | 높음 |
| 공식 API | `ClipPPOLoss` | <https://docs.pytorch.org/rl/stable/reference/generated/torchrl.objectives.ClipPPOLoss.html> | clipped loss, entropy, critic, clip fraction | 높음 |
| 공식 API | `GAE` | <https://docs.pytorch.org/rl/stable/reference/generated/torchrl.objectives.value.GAE.html> | 입력 키, advantage와 value target, 종료 처리 | 높음 |
| 공식 API | TorchRL collectors | <https://docs.pytorch.org/rl/stable/reference/collectors.html> | on-policy 동기 수집과 정책 가중치 동기화 | 높음 |
| 구현체 | PyTorch RL 저장소 `ppo.py` | <https://github.com/pytorch/rl/blob/main/torchrl/objectives/ppo.py> | API가 구현하는 목적함수 검산 | 높음 |
| 구현체 | CleanRL `ppo.py` | <https://github.com/vwxyzjn/cleanrl/blob/master/cleanrl/ppo.py> | 단일 파일 PPO의 shape·로그 지표 비교 검산 | 중간 |

## 2. 버전 기준

2026-08-21에 확인한 안정 릴리스 기준은 다음과 같다.

| 구성요소 | 기준 | 자료의 정책 |
|---|---:|---|
| Python | 3.12 | 3.10 이상에서 동작하도록 표준 문법만 사용한다. |
| PyTorch | 2.13.0 | 설치 명령은 하드웨어마다 다르므로 공식 selector를 우선한다. |
| Gymnasium | 1.3.0 | `terminated`, `truncated` 분리 API를 사용한다. |
| TorchRL | 0.13.3 | 0.13 stable API를 기준으로 하고 experimental 고수준 trainer는 핵심 경로에서 제외한다. |
| MkDocs Material | 9.7.6 | 저장소의 기존 설정을 유지한다. |

## 3. 핵심 정의와 용어 도입

| 용어 | 독자 수준의 한 문장 정의 | 원어/약어 | 혼동할 개념 |
|---|---|---|---|
| 정책 | 관측을 받아 행동의 확률분포를 내놓는 규칙 | policy, $\pi_\theta$ | 가치 함수는 행동을 직접 고르지 않는다. |
| return | 한 시점 이후 보상을 할인해 더한 값 | discounted return, $G_t$ | reward는 한 스텝, return은 미래 누적이다. |
| 가치 함수 | 현재 관측에서 앞으로 얻을 return의 평균을 예측하는 함수 | value function, $V_\phi$ | 실제 return이 아니라 추정치다. |
| advantage | 선택한 행동이 그 상태의 평균 행동보다 얼마나 나았는지 나타내는 값 | advantage, $A_t$ | 양수는 확률 증가, 음수는 감소 방향이다. |
| policy gradient | 기대 return을 높이는 쪽으로 정책 파라미터를 바꾸는 기울기 | policy gradient | 환경을 미분하는 것이 아니라 로그확률을 미분한다. |
| actor–critic | 정책과 가치 예측기를 함께 학습하는 구조 | actor–critic | PPO는 actor 손실만 뜻하지 않는다. |
| GAE | 여러 길이의 TD 정보를 지수 가중해 advantage를 만드는 방법 | generalized advantage estimation, GAE | $\lambda$는 환경 discount가 아니다. |
| on-policy | 현재 정책으로 모은 경험을 현재 정책 업데이트에 사용하는 방식 | on-policy | 경험을 무제한 재사용하지 않는다. |
| importance ratio | 같은 행동의 새 정책 확률을 old 정책 확률로 나눈 값 | probability ratio, $r_t$ | 구현에서는 로그확률 차이를 지수화한다. |
| clipping | ratio가 허용 구간을 벗어날 때 추가 이득을 제한하는 연산 | clipping | 파라미터나 gradient를 직접 자르는 것과 다르다. |
| rollout | 고정된 현재 정책으로 일정 길이의 경험을 수집한 묶음 | rollout | 완전한 에피소드와 길이가 같을 필요는 없다. |
| TensorDict | 이름 있는 텐서를 batch 차원과 함께 보관하는 TorchRL 자료구조 | TensorDict | 일반 `dict[str, Tensor]`보다 shape 계약을 함께 가진다. |

## 4. 수식과 알고리즘

| 항목 | 내용 요약 | 가정과 주의 | 출처 | 상태 |
|---|---|---|---|---|
| return | $G_t=\sum_{k=0}^{T-t-1}\gamma^k r_{t+k}$ | $0\le\gamma\le1$; 유한 rollout 끝의 bootstrap을 별도 처리 | 표준 RL 정의, Spinning Up | 검증 |
| policy gradient 추정 | $\hat g=\frac1N\sum_t\nabla_\theta\log\pi_\theta(a_t\mid s_t)\hat A_t$ | 데이터는 정책 분포에서 수집 | PPO 논문 | 검증 |
| TD residual | $\delta_t=r_t+\gamma V(s_{t+1})-V(s_t)$ | 자연 종료에서는 다음 가치를 0으로 둔다. | GAE 논문 | 검증 |
| GAE | $\hat A_t=\delta_t+\gamma\lambda m_t\hat A_{t+1}$ | episode 경계에서는 재귀를 끊는다. truncation은 다음 가치로 bootstrap한다. | GAE 논문, Gymnasium | 검증 |
| ratio | $r_t(\theta)=\exp(\log\pi_\theta-\log\pi_{old})$ | old log probability는 rollout 때 저장하고 gradient에서 분리 | PPO 논문 | 검증 |
| clipped objective | $L=\mathbb E[\min(r_tA_t,\operatorname{clip}(r_t,1-\epsilon,1+\epsilon)A_t)]$ | loss로 최소화할 때 음수를 붙인다. | PPO 논문, TorchRL | 검증 |
| total loss | $-L^{clip}+c_vL_V-c_eH$ | 계수와 value loss 형태는 구현 선택 | PPO 논문, TorchRL | 검증 |

## 5. 예제와 시각화 계획

| 자료 | 보여줄 개념 | 형식 | 위험과 대응 |
|---|---|---|---|
| CartPole 대응도 | 관측·행동·보상·종료 | 정적 SVG | 상태와 관측을 동일시하지 않도록 일반 정의를 먼저 둔다. |
| discounted return 실험실 | $\gamma$가 미래 보상 가중치에 미치는 영향 | 인터랙티브 HTML | 최대값을 목표처럼 보이지 않게 실제 항별 기여를 표시한다. |
| PyTorch 계산 그래프 | log probability에서 gradient까지 | 정적 SVG | 환경 경로에는 gradient가 없음을 분리한다. |
| 정책분포 실험실 | logits, 확률, entropy | 인터랙티브 HTML | 샘플 빈도는 난수 오차가 있음을 표시한다. |
| GAE 실험실 | reward, value, $\gamma$, $\lambda$와 역방향 재귀 | 인터랙티브 HTML | 종료 마스크를 눈에 보이게 표시한다. |
| PPO clipping 실험실 | ratio와 advantage 부호별 min 선택 | 인터랙티브 HTML | clip이 항상 ratio를 잘라 쓰는 것으로 오해하지 않게 두 항을 함께 표시한다. |
| PPO dataflow | 수집→고정→GAE→여러 epoch→폐기 | 정적 SVG | on-policy 경계를 굵게 표시한다. |
| 디버깅 의사결정도 | 로그 증상에서 점검 순서 | 정적 SVG와 HTML | 단일 지표로 결론 내리지 않도록 조합을 사용한다. |
| TorchRL 대응도 | 직접 구현의 객체와 TorchRL 클래스 | 정적 SVG | high-level trainer는 experimental임을 구분한다. |

## 6. 논쟁점과 채택한 설명

- PPO를 “trust region을 보장하는 알고리즘”이라고 표현하지 않는다. clipping은 큰 업데이트의 유인을 제한하지만 엄밀한 KL 제약 보장은 아니다.
- advantage 정규화, gradient clipping, value clipping, 학습률 감소는 원 논문의 단일 필수 정의가 아니라 자주 쓰이는 구현 선택으로 표시한다.
- 시간 제한에서 episode는 끝나지만 MDP terminal이 아니므로 value bootstrap은 유지한다. 단, GAE의 다음 episode로 재귀 연결은 끊는다.
- TorchRL 0.13의 새로운 `PPOTrainer`는 experimental/prototype이므로 초심자 핵심 경로는 명시적 구성요소 조립으로 설명한다.
- discrete CartPole 직접 구현을 중심에 두고, continuous action은 `Normal`/`TanhNormal`이 필요하다는 설계 차이까지만 다룬다.
- Stanford CS234는 policy gradient 전에 tabular planning, policy evaluation, Q-learning을 가르친다. 이 책은 PPO가 목표이므로 MDP와 value evaluation은 2장에 포함하지만, Q-learning 구현은 중심 흐름에서 제외하고 학습 키워드와 비교표로 안내한다.
- Berkeley CS 185/285가 PyTorch tutorial과 probability review를 RL 기초·policy gradient에 인접하게 배치하는 방식을 따라 2~3장을 수학과 PyTorch의 집중 선수 블록으로 둔다.

## 7. 조사 요약

- 가장 신뢰할 기준: PPO·GAE 원 논문, PyTorch/TorchRL/Gymnasium 공식 문서와 소스
- 초고에 반드시 반영: old log probability 보존, on-policy batch 폐기, 종료 두 마스크, loss 부호, shape 표
- 버전 의존 위험: Gymnasium vector autoreset, TorchRL collector와 trainer API
- 설명 위험: PPO clipping을 파라미터 clipping이나 hard constraint로 오해하는 문제

## 8. 품질 점검

- [x] 정의, 수식, 알고리즘의 출처가 있다.
- [x] 공식 문서와 원 논문을 우선했다.
- [x] 새 용어의 한 문장 정의와 혼동 개념을 정리했다.
- [x] 버전 의존 정보에 확인 날짜와 버전을 기록했다.
- [x] 초고로 넘길 미검증 핵심 주장이 없다.

## 9. 2차 조사: 공개 지식체계와 초심자 경로 대조

2026-08-21에 “정의 없이 처음 등장하는 용어가 없는가, PPO까지 필요한 다리가 빠지지 않았는가”를 기준으로 다시 조사했다.

| 대조 자료 | 공개 학습 흐름·핵심 범위 | 이 책에 요구되는 보강 |
|---|---|---|
| Sutton & Barto, *Reinforcement Learning: An Introduction* | bandit → finite MDP → dynamic programming → Monte Carlo → TD → n-step/trace → function approximation → policy gradient | Bandit을 통해 탐색–활용을 소개하고, MDP·MC·TD·함수근사의 위치를 알고리즘 지도에서 연결한다. 상세 Q-learning은 범위 밖임을 명시한다. |
| Wikipedia: Reinforcement learning | MDP 요소, policy, expected cumulative reward, full/partial observability, value/direct policy search, MC, TD, function approximation, algorithm 비교 | `상태/관측`, `결정론/확률 정책`, `표 기반/함수근사`, `가치 기반/정책 최적화`를 첫 등장에 정의한다. 위키는 범위 점검용이고 수식 근거는 교과서·논문을 사용한다. |
| OpenAI Spinning Up | state/observation, action space, policy, trajectory, return, objective, value/Q/advantage; model-based/model-free, policy optimization/Q-learning, on/off-policy | 1~2장의 기본 용어와 PPO의 알고리즘 좌표를 보강한다. |
| Stanford CS234 Winter 2026 | RL 정의 → MDP planning → policy evaluation → Q-learning/function approximation → policy search; exploration과 algorithm evaluation | Q-learning 상세는 건너뛰되 무엇을 건너뛰는지와 PPO에 직접 필요하지 않은 이유를 설명한다. 탐색–활용과 평가 기준은 개념 수준으로 포함한다. |
| Berkeley CS 185/285 Spring 2026 | PyTorch·확률 복습 → RL basics → policy gradients → actor–critic → value-based RL → advanced policy gradients | 신경망, loss, optimizer, softmax, autograd를 독립적인 초심자 설명으로 확장하고 정책경사 유도를 단계별로 보인다. |
| MIT OCW 2.997 | MDP/DP → simulation-based Q-learning → value approximation/TD → policy gradient/actor–critic | 모델을 아는 planning과 샘플로 배우는 learning을 구분하고, function approximation이 필요한 이유를 설명한다. |
| Hugging Face Deep RL Course | DRL 소개 → Q-learning/DQN → PyTorch policy gradient → actor–critic → PPO | 실습 중심 자료처럼 각 추상 개념 뒤에 실행·계산·퀴즈를 둔다. Q-learning을 생략한 이유와 후속 경로를 눈에 띄게 표시한다. |
| PyTorch Learn the Basics | tensor → model → autograd → optimization → save/load | 3장에 layer, parameter, activation, forward pass, loss, learning rate, optimizer를 정의한다. Dataset/DataLoader는 on-policy rollout에 직접 쓰지 않으므로 차이를 설명한다. |

## 10. 2차 조사에서 확정한 필수 용어 묶음

### 10.1 외부 학습으로 분리하는 선수지식

- Python 변수, 함수 호출, `while`/`for`, list와 dictionary
- 터미널에서 현재 폴더 이동과 Python 명령 실행

이 둘은 언어·운영체제 과정 전체가 필요한 큰 선수지식이므로 별도 키워드로 안내한다. 확률·미분·신경망은 PPO의 직접 선수이므로 본문에서 다시 설명한다.

### 10.2 본문에서 첫 사용 전에 설명할 용어

| 장 | 용어 묶음 |
|---:|---|
| 1 | 강화학습, deep RL, step, transition, action/observation space, delayed consequence, credit assignment, exploration/exploitation, deterministic/stochastic policy, episodic/continuing task, horizon, terminal, MDP, Markov property, partial observability, model, model-free, value-based, policy optimization, on/off-policy |
| 2 | random variable, probability distribution, sample, conditional probability, expectation, sample mean, variance, standard deviation, return, value/Q/advantage, Bellman equation/backup, prediction/control, tabular/function approximation, Monte Carlo, TD, bootstrap, bias/variance, parameter, objective/loss, derivative/partial derivative/gradient, learning rate, gradient descent/ascent, chain rule |
| 3 | tensor, axis/dimension, shape, dtype, device, broadcasting, neural network, layer, weight, bias, activation, MLP, forward pass, logits, softmax, categorical distribution, sampling, log probability, entropy, module, loss, optimizer, Adam, computation graph, backward, detach, train/eval mode, state dictionary |
| 4 | policy gradient, estimator, REINFORCE, reward-to-go, baseline, actor, critic, TD residual, n-step return, GAE, bootstrap/continuation mask, entropy bonus |
| 5 | proximal, importance sampling/ratio, surrogate objective, clip, mini-batch, epoch, KL divergence, trust region, clip fraction |
| 6 | configuration, hyperparameter, unit test, smoke test, end-to-end, buffer, orthogonal initialization, checkpoint |
| 7 | baseline experiment, metric, invariant, assertion, finite/NaN/Inf, seed, determinism/reproducibility, evaluation protocol, ablation, confidence interval, smoothing |
| 8 | API, primitive, TensorDict, nested key, spec, transform, collector, storage, sampler, continuous action, probability density, Normal distribution, location/scale, bounded distribution |
| 9 | preregistration, selection bias, benchmark, protocol, rubric, correlation/causation |

## 11. 기술 근거 사용 원칙

- Wikipedia는 누락 범위와 통용 용어를 찾는 비교표로만 사용한다.
- 정의와 수식은 Sutton & Barto, PPO·GAE 원 논문, PyTorch·Gymnasium·TorchRL 공식 문서로 검증한다.
- 공개 강의는 설명 순서와 과제 구조의 근거로 사용한다.
- 서로 다른 표기 관례인 $R_{t+1}$과 이 책의 $r_t$를 처음에 명시해 시간 index 혼동을 막는다.
