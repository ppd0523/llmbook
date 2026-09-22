# 처음부터 구현하며 배우는 PyTorch PPO

이 책은 강화학습을 처음 접하는 학습자가 **PPO(Proximal Policy Optimization)** 를 수식·tensor·실행 코드의 세 관점에서 연결하도록 만든 입문 과정이다. 먼저 순수 PyTorch로 PPO-Clip을 구현해 내부를 확인하고, 마지막에는 같은 구조를 PyTorch 공식 강화학습 라이브러리인 TorchRL로 옮긴다.

최종 목표는 예제 코드를 한 번 실행하는 것이 아니다. 학습이 실패했을 때 환경 계약, GAE, old log probability, clipping, critic 중 어디가 문제인지 근거를 들어 찾을 수 있어야 한다.

## 대학 강의 흐름을 반영한 구성

학습 순서는 다음 공개 대학 강의를 PPO 중심으로 재구성했다.

- [Stanford CS234 Winter 2026](https://web.stanford.edu/class/cs234/modules.html): 강화학습 소개 → MDP planning → policy evaluation → policy gradient
- [UC Berkeley CS 185/285 Spring 2026](https://rail.eecs.berkeley.edu/deeprlcourse/): PyTorch·확률 복습 → RL 기초 → policy gradient → actor–critic → advanced policy gradient
- [MIT OCW 2.997](https://ocw.mit.edu/courses/2-997-decision-making-in-large-scale-systems-spring-2004/pages/syllabus/): MDP, 가치·정책 반복, policy gradient와 actor–critic의 고전적 연결

Stanford 과정은 policy gradient 전에 tabular planning과 Q-learning도 깊게 다룬다. 이 책의 목표는 PPO이므로 MDP와 policy evaluation은 충분히 포함하되 Q-learning 상세 구현은 후속 학습 키워드로 분리한다. Berkeley 과정처럼 PyTorch와 확률 복습을 policy gradient 직전에 배치한다.

## 공개 커리큘럼과 비교한 범위

“PPO만 빨리 실행하기”와 “강화학습 전체 학부 과정을 모두 이수하기”는 같은 목표가 아니다. 이 책은 PPO에 직접 연결되는 다리를 생략하지 않되, 별도 과목 규모의 주제는 이름만 던지지 않고 **왜 별도 학습인지와 돌아올 순서**를 표시한다.

| 공개 자료의 주제 | 이 책의 처리 | 위치·이유 |
|---|---|---|
| Bandit과 탐색–활용 | 개념과 수치 예 포함 | 1장. 순차 의사결정 전의 가장 작은 문제로 사용한다. |
| Agent–environment, MDP | 상세 포함 | 1~2장. 모든 PPO 기호의 출발점이다. |
| Dynamic programming, value/policy iteration | 위치와 작동 조건만 설명 | 1~2장. 정확한 환경 모델과 표 기반 반복 알고리즘은 별도 과정이다. |
| Monte Carlo, TD, bootstrapping | PPO에 필요한 깊이로 포함 | 2·4장. Critic과 GAE를 이해하는 직접 선수다. |
| 잔차 용어와 residual learning | 구분·확장 개요 포함 | 2·4·7·8장. 회귀 잔차, TD 잔차, 신경망 잔차 연결, 잔차 강화학습을 분리한다. |
| SARSA, Q-learning, DQN | 비교 개요와 후속 키워드 | PPO는 정책을 직접 최적화하므로 Q-learning 구현은 직접 선수가 아니다. |
| 함수근사와 신경망 | 상세 포함 | 2~3장. 연속 상태를 표 대신 신경망으로 다루는 이유부터 설명한다. |
| Policy gradient와 REINFORCE | 유도·예제 포함 | 4장. 궤적 확률에서 샘플 gradient까지 등식을 따라간다. |
| Actor–critic과 GAE | 상세 포함 | 4장. PPO가 사용하는 advantage를 만든다. |
| TRPO·trust region | 비교 개요 | 5장. PPO의 동기를 설명하되 제약 최적화 전체 유도는 생략한다. |
| PPO-Clip | 수식·직접 구현·디버깅 포함 | 5~7장. 이 책의 중심이다. |
| 연속 행동 PPO와 라이브러리 | 실습 포함 | 8장. 확률밀도와 `TanhNormal`, 잔차 정책 개요부터 TorchRL 객체까지 연결한다. |
| 재현 가능한 실험 | 상세 포함 | 7장이 방법론(여러 seed, 평가 protocol, 비교 실험 설계)을 정의하고 9장이 그것을 프로젝트로 수행한다. |
| Model-based, offline, multi-agent, safe RL | 지도와 후속 키워드 | 9장. 각각 별도 과정 규모이며 PPO 입문 뒤 선택한다. |

이 범위표는 [Sutton과 Barto의 공개 교재](http://incompleteideas.net/book/the-book-2nd.html), [강화학습 Wikipedia 문서](https://en.wikipedia.org/wiki/Reinforcement_learning), [OpenAI Spinning Up의 알고리즘 분류](https://spinningup.openai.com/en/latest/spinningup/rl_intro2.html), [Hugging Face 공개 과정](https://huggingface.co/learn/deep-rl-course/en/unit0/introduction)과 대학 강의 순서를 대조해 작성했다. Wikipedia는 범위 확인에 사용하고 정의·수식의 근거는 교재, 논문과 공식 문서를 우선한다.

## 이 책의 설명 계약

전문용어는 처음 나올 때 다음 네 질문에 답하도록 퇴고했다.

1. 왜 이 개념이 필요한가?
2. 초심자 말로 무엇인가?
3. 작은 숫자나 CartPole에서 어떻게 보이는가?
4. 무엇과 혼동하면 안 되는가?

후속 학습으로 넘기는 용어는 상세 내용을 아는 것처럼 가정하지 않는다. 본문에서 사용하는 수학·신경망 개념은 2~3장에서 다시 설명하며, 처음 읽을 때 모든 수식을 암기할 필요는 없다. 각 수식에서 입력, 출력, 부호와 코드 shape를 말로 설명하는 것을 목표로 한다.

## 학습 경로

| 단계 | 장 | 완료 기준 | 권장 시간 |
|---:|---|---|---:|
| 1 | [강화학습의 언어와 환경 루프](./01-reinforcement-learning-mental-model.md) | CartPole 한 transition을 관측·행동·보상·종료로 설명한다. | 3–4시간 |
| 2 | [MDP, 가치와 PPO를 위한 최소 수학](./02-mdp-value-and-math.md) | return과 Bellman 관계를 계산하고 TD 오차·잔차와 최적화 수학을 설명한다. | 5–7시간 |
| 3 | [정책을 위한 PyTorch 기초](./03-pytorch-for-policies.md) | actor·critic 출력 shape와 `Categorical` 로그확률의 gradient를 추적한다. | 5–7시간 |
| 4 | [Policy gradient, actor–critic과 GAE](./04-policy-gradient-and-gae.md) | TD 잔차와 GAE를 계산해 행동 확률의 업데이트 방향을 판단하고 “잔차”의 네 문맥을 구분한다. | 6–8시간 |
| 5 | [PPO-Clip 목적함수](./05-ppo-clipped-objective.md) | advantage 부호에 따른 clipping 결과와 on-policy batch 생명주기를 설명한다. | 5–7시간 |
| 6 | [순수 PyTorch로 PPO 만들기](./06-build-ppo-with-pytorch.md) | CartPole 학습을 실행하고 코드의 각 tensor를 수식에 대응시킨다. | 8–12시간 |
| 7 | [PPO 실험과 디버깅](./07-debug-and-experiment.md) | KL, clip fraction, entropy, value loss로 실패 원인을 분류한다. | 5–8시간 |
| 8 | [TorchRL로 PPO 사용하기](./08-use-ppo-with-torchrl.md) | 직접 구현을 TorchRL 환경·collector·GAE·loss module에 대응시키고 잔차 강화학습의 결합 방식을 설명한다. | 6–9시간 |
| 9 | [최종 프로젝트와 다음 학습](./09-final-project-and-next-steps.md) | 여러 seed의 기준 실험과 변경 실험을 비교해 재현 보고서를 만든다. | 8–12시간 |

## 실습 자료

- [할인 return 실험실](./assets/mdp-value-and-math/discounted-return-lab.html)
- [Categorical 정책분포 실험실](./assets/pytorch-for-policies/policy-distribution-lab.html)
- [GAE 역방향 계산 실험실](./assets/policy-gradient-and-gae/gae-lab.html)
- [PPO clipping 실험실](./assets/ppo-clipped-objective/ppo-clipping-lab.html)
- [순수 PyTorch CartPole PPO](./examples/ppo_cartpole.py)
- [PPO 핵심 수식 함수](./examples/ppo_components.py)
- [학습 지표 SVG 생성기](./examples/plot_metrics.py)
- [TorchRL PPO 예제](./examples/torchrl_ppo.py)
- [핵심 수식 단위 테스트](./tests/test_ppo_components.py)

## 필요한 선행지식

간단한 Python 함수를 읽고 터미널에서 명령을 실행할 수 있어야 한다. 강화학습, 확률, 미분, 신경망은 처음이라고 가정하며 PPO에 직접 필요한 부분은 1~3장에서 다시 배운다. Python 언어 자체와 운영체제 명령은 한 책 안에 넣기에는 너무 크므로 다음 진단 중 1번이나 터미널 실행이 어렵다면 먼저 Python 기초를 보충한다. 2~4번이 어렵다는 이유만으로 이 책을 중단할 필요는 없다.

1. Python list를 순회하며 합계를 구할 수 있는가?
2. `f(x) = x**2`의 `x=3`에서 기울기가 6이라는 설명을 따라갈 수 있는가?
3. 평균과 표준편차가 각각 중심과 흩어진 정도를 나타낸다는 것을 아는가?
4. 길이 4 배열 32개를 `[32, 4]` 모양의 표로 이해할 수 있는가?

외부에서 먼저 배울 필수 키워드: `Python variables`, `functions`, `for/while`, `list and dictionary`, `PowerShell cd and python command`. 이 책과 병행할 보충 키워드: `NumPy array shape`, `conditional probability`, `derivative and chain rule`, `matrix multiplication`.

## 실행 환경

본문과 예제의 확인 기준은 2026-08-21 현재 Python 3.12, PyTorch 2.13.0, Gymnasium 1.3.0, TorchRL 0.13.3이다. CartPole 직접 구현은 CPU로 충분하다. PyTorch 설치 명령은 운영체제와 GPU에 따라 달라지므로 [공식 설치 선택기](https://pytorch.org/get-started/locally/)를 우선 사용한다.

[1장: 강화학습의 언어와 환경 루프 →](./01-reinforcement-learning-mental-model.md)
