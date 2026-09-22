---
title: PyTorch PPO 학습 자료 검토 기록
version: 0.9
status: final
owner: agent
updated: 2026-09-22
target_reader: 강화학습과 PyTorch 초심자
topic: 순수 PyTorch PPO 구현에서 TorchRL까지
---

# 검토 기록

## 1. 범위 검토

| 질문 | 판정 | 근거와 조치 |
|---|---|---|
| 독자가 초심자로 유지되는가? | 통과 | 1장에서 환경 언어를 정의하고, 2장에서 수학을 작은 수로 재구성했다. |
| 최종 목표가 PyTorch PPO인가? | 통과 | 6장에서 직접 구현, 8장에서 TorchRL 활용, 9장에서 독립 실험을 요구한다. |
| ONNX가 중심에 남아 있는가? | 통과 | ONNX 내용은 제거했다. |
| 방대한 선수지식을 억지로 압축했는가? | 통과 | Q-learning·DQN, 연속 확률변수 변환, 고급 PPO를 후속 키워드로 분리했다. |
| 대학 과정 순서가 반영됐는가? | 통과 | Stanford·Berkeley·MIT의 MDP→평가/TD→정책경사/actor–critic 흐름과 대응표가 있다. |

## 2. 개념 정확성 검토

| 항목 | 발견 가능 오류 | 판정·조치 |
|---|---|---|
| Gymnasium 종료 | `done` 하나로 합침 | 수집 시 `terminated`, `truncated`를 따로 저장한다. |
| Truncation GAE | bootstrap과 재귀를 같은 mask로 처리 | bootstrap에는 `~terminated`, GAE 재귀에는 `~(terminated | truncated)`를 썼다. |
| Policy gradient 부호 | maximize objective를 optimizer에 그대로 전달 | 구현에서 최소화 loss로 음수를 취한다. |
| PPO ratio | 새 정책으로 old log probability 재계산 | 수집 순간 값을 buffer에 저장한다. |
| Negative advantage clipping | 양수와 같은 직관을 적용 | 부호별 표와 interactive graph로 별도 설명한다. |
| Mini-batch broadcasting | action `[B,1]`, log prob `[B]` 혼합 | 직접 구현은 action `[B]`로 통일하고 assertion을 제공한다. |
| Evaluation | stochastic 학습 점수를 그대로 보고 | deterministic evaluation 함수를 분리한다. |
| Replay buffer | 오래된 PPO 데이터를 계속 재사용 | TorchRL 예제는 한 rollout을 여러 epoch 섞은 뒤 다음 수집 전에 buffer를 비운다. |

## 3. 수식 검토

- Discounted return의 지수와 역방향 재귀가 일치한다.
- Bellman expectation 관계는 policy evaluation으로 제한해 설명한다.
- TD residual은 $r_t+\gamma V(s_{t+1})-V(s_t)$이며 terminal bootstrap mask가 코드에 반영됐다.
- GAE는 $\sum_l(\gamma\lambda)^l\delta_{t+l}$와 역방향 재귀를 함께 제시한다.
- PPO surrogate는 $\min(r_tA_t,\operatorname{clip}(r_t,1-\epsilon,1+\epsilon)A_t)$다.
- Critic loss, entropy bonus, total minimization loss의 부호를 구분했다.
- Approximate KL과 clip fraction은 진단 추정치이지 hard constraint가 아님을 명시했다.

## 4. 코드 검토

### 직접 구현

- 환경 interaction과 update 단계가 분리돼 있다.
- Actor·critic 출력 shape가 각각 logits `[B,2]`, value `[B]`다.
- 수집 action은 `Categorical.sample()`의 정수 tensor이고 Gym에는 Python 정수로 전달한다.
- Rollout buffer에 observation, action, reward, old log probability, value, next value, 종료 두 종류를 저장한다.
- Advantage를 update 전에 한 번 계산하고 정규화한다.
- 각 PPO epoch에서 shuffled mini-batch를 사용한다.
- Gradient clipping, target KL early stop, explained variance를 포함한다.
- Checkpoint load 시 state dictionary와 config를 검증한다.

### TorchRL 예제

- `NormalParamExtractor`는 `tensordict.nn.distributions`에서 import한다.
- `check_env_specs`를 collector 전에 호출한다.
- `ProbabilisticActor`가 log probability를 반환한다.
- Lazy module은 optimizer 전에 materialize한다.
- `GAE`와 `ClipPPOLoss`를 stable primitive로 사용한다.
- `ReplayBuffer`는 mini-batch shuffle에만 사용하고 오래된 rollout을 남기지 않는다.
- Smoke configuration은 collector, loss, backward를 짧게 통과하도록 분리했다.

실행 검증 결과는 `08_publish.md`에 기록한다. 실제 설치 버전에서 API 오류가 발견되면 수정 후 이 검토 문서의 판정을 유지한다.

## 5. 초심자 관점 검토

| 예상 질문 | 본문 위치 | 판정 |
|---|---|---|
| State와 observation이 왜 다른가? | 1장 | 설명 있음 |
| Reward와 return은 같은가? | 2장 | 예제로 구분 |
| Critic은 정답을 어디서 얻는가? | 4장 | TD/return target 설명 |
| 왜 log probability를 쓰는가? | 2~4장 | log trick과 autograd 연결 |
| PPO가 왜 두 policy를 쓰는가? | 5장 | 수집 snapshot과 현재 policy 구분 |
| Replay buffer면 off-policy 아닌가? | 8장 | 수명과 목적을 분리 |
| 점수 하나가 높으면 성공인가? | 7·9장 | 여러 seed와 분리 평가 요구 |

## 6. 시각화 검토

- SVG마다 `<title>`과 `<desc>`가 있다.
- 정보 흐름 그림은 화살표 방향과 라벨이 일치한다.
- 색만으로 positive/negative 또는 단계 차이를 구분하지 않고 텍스트 라벨을 함께 쓴다.
- Interactive lab은 slider 입력과 숫자 출력, 설명을 함께 제공한다.
- JavaScript가 실패해도 장의 수식과 표만으로 핵심 내용을 이해할 수 있다.
- 상대 경로로 MkDocs와 로컬 파일 양쪽에서 접근할 수 있다.

## 7. 문서 구조 검토

- 모든 최종 Markdown 파일은 H1이 하나다.
- 코드 fence에 언어가 지정돼 있다.
- 수식은 MathJax 표기를 사용한다.
- `_work` 내부 문서는 MkDocs build에서 제외된다.
- 장 사이 이전·목차·다음 링크가 이어진다.
- `docs/index.md`에 책 진입 링크가 추가됐다.

## 8. 남은 출판 게이트

1. Python syntax와 단위 테스트
2. 직접 구현 smoke training과 checkpoint reload
3. TorchRL smoke training
4. SVG XML과 HTML script 문법
5. 로컬 Markdown 링크와 asset 경로
6. MkDocs strict build
7. `TODO`, placeholder, 내부 절대 경로 유출 확인

## 9. 2차 초심자 감사 결과

초판은 알고리즘과 코드가 정확하고 실행 가능했지만, “강화학습과 신경망을 모두 처음 배운다”는 독자 정의에 비해 설명이 압축된 곳이 있었다.

| 위치 | 발견한 학습성 결함 | 심각도 | 처리 방향 |
|---|---|---:|---|
| 목차 | 공개 과정에서 무엇을 포함·개요·생략했는지 한눈에 보이지 않음 | 높음 | 공개 과정과의 범위 대응표 추가 |
| 1장 | deep RL, 탐색–활용, 신용 할당, episodic/continuing, horizon이 없음 | 높음 | bandit→sequential decision 예와 함께 정의 |
| 1장 | PPO가 전체 RL 알고리즘 지도에서 어디에 있는지 늦게 드러남 | 높음 | model-free/on-policy/policy optimization actor–critic으로 위치 표시 |
| 1장 | `Discrete(2)`, action space, step, terminal이 설명보다 먼저 쓰임 | 높음 | Gym 코드 전에 API·공간·시간 용어 설명 |
| 2장 | 기댓값·분산·gradient가 한 문단 설명에 그침 | 높음 | 확률변수·표본평균·편미분·학습률·목적/손실까지 숫자 예제로 확장 |
| 2장 | $V$, $Q$, $A$의 관계와 prediction/control 차이가 약함 | 높음 | 동일 상태의 행동 표와 $V=\sum\pi Q$, $A=Q-V$ 예제 추가 |
| 2장 | tabular/function approximation, model/experience 차이가 후속 키워드로만 등장 | 중간 | PPO 신경망으로 넘어가기 위한 개념 다리 추가 |
| 3장 | 신경망을 모른다고 가정했지만 `Linear`, `Tanh`, MLP, parameter를 바로 사용 | 매우 높음 | 선형변환→활성화→층→forward→loss→optimizer 전체 루프 설명 |
| 3장 | softmax, probability distribution, sampling, log probability 설명이 짧음 | 높음 | logits 수치 예와 범주분포 계산 추가 |
| 4장 | 로그미분 트릭에서 policy gradient 식으로 큰 도약 | 매우 높음 | trajectory 확률부터 환경 dynamics 항이 사라지는 과정까지 단계별 유도 |
| 4장 | baseline이 평균 gradient를 바꾸지 않는 이유를 주장만 함 | 높음 | 행동 확률 합이 1이라는 짧은 증명 추가 |
| 4장 | GAE가 TD residual의 지수합이라는 결과만 제시 | 높음 | 1-step, 2-step advantage와 $\lambda$ 혼합의 연결 설명 |
| 5장 | importance ratio와 surrogate objective가 정의 없이 전문용어로 등장 | 매우 높음 | 분포 보정 수치 예, surrogate의 역할, clip 함수 정의 추가 |
| 5장 | KL·trust region이 진단 절에서 갑자기 등장 | 높음 | discrete KL 식, 비대칭성, PPO-Clip과 TRPO의 차이 추가 |
| 6장 | unit/smoke/end-to-end test와 hyperparameter의 의미가 암묵적 | 중간 | 테스트 층과 기본 설정 전수 표 추가 |
| 6·9장 | 최종 프로젝트는 CSV·곡선을 요구하지만 예제는 콘솔만 출력 | 높음 | `--metrics-csv`와 표준 라이브러리 SVG plot 예제 추가 |
| 7장 | explained variance가 target 분산이 작을 때 불안정할 수 있다는 경고 없음 | 높음 | 완벽한 return과 음수 EV가 공존할 수 있는 조건 설명 |
| 7·9장 | seed, 재현성, protocol, ablation, confidence interval이 무정의 또는 늦음 | 높음 | 실험 용어 절과 동일 평가 protocol 설명 추가 |
| 8장 | 연속 확률에서 확률과 밀도의 차이, Normal·loc·scale이 생략됨 | 매우 높음 | bounded continuous action 분포를 숫자·단위와 함께 설명 |
| 8장 | storage/sampler/collector/transform이 클래스 이름 위주 | 높음 | 각 객체가 읽고 쓰는 데이터와 수명을 단계별 표로 설명 |
| 9장 | IID, selection bias, correlation이 앞 설명 없이 사용 | 중간 | 일상어 풀이와 용어 사전 추가 |

## 10. 건너뛰기 판정

| 주제 | 판정 | 이유와 독자 안내 |
|---|---|---|
| Multi-armed bandit | 개념 포함, 구현 생략 | 탐색–활용의 가장 작은 예로 다루되 PPO 구현의 직접 선수는 아니다. |
| Dynamic programming, value/policy iteration | 지도와 정의만 포함 | 정확한 transition model을 아는 tabular planning 과정은 별도 여러 장 분량이다. |
| SARSA, Q-learning, DQN | 비교 개요와 후속 키워드 | PPO의 위치를 이해하는 데 비교는 필요하지만 구현은 별도 value-based 경로다. |
| n-step TD, eligibility trace | GAE에 필요한 연결만 포함 | 일반 TD($\lambda$) 이론 전체는 범위를 넘는다. |
| 신경망·최적화 | 본문에 상세 포함 | PPO 코드를 읽는 직접 선수이며 한 장 안에서 다룰 수 있다. |
| 연속분포 change of variables | 직관·결과 포함, 유도 생략 | Jacobian determinant 유도는 별도 확률론·미적분 과정이다. |
| TRPO monotonic improvement 이론 | 목적·차이만 포함 | 제약 최적화와 natural gradient 전체 유도는 범위를 넘는다. |
| 병렬·분산·recurrent·multi-agent PPO | 후속 키워드 | 각각 별도 시스템·모델 과정이 필요하다. |

누락과 의도적 생략을 구분했다. 의도적 생략은 본문에서 주제명, 필요한 이유, 권장 선행 키워드, 돌아올 시점을 함께 안내한다.


## 11. 3차 개정: 기술 재검증과 코드 대조 (2026-09-22)

### 수치 재검산

본문의 모든 손계산을 다시 검산했다. **수치 오류는 없었다.** 2장 return 예제, 두 상태 가치,
4장 GAE 역방향 계산과 연습문제 답, 5장 clipping 예제와 policy loss, 6장 로그 예시가 모두
정확했다.

### 기호 정합성에서 찾은 실제 결함

| 결함 | 위치 | 처리 |
|---|---|---|
| $r_t$가 보상과 probability ratio를 동시에 지칭 | 2장 기호표 ↔ 5장 ratio 절 | ratio는 항상 $r_t(\theta)$로 표기. 2·5장에 충돌 경고 추가 |
| $A_t$와 $\hat A_t$ 혼용 | 4장 정의·불릿·연습문제, 6장 buffer 표 | 참값/추정 구분을 4장에 명문화하고 오용 지점 교정 |
| bootstrap mask 극성 충돌 | 2장 $(1-d_t)$ ↔ 4장 $b_t$ | 예제 코드의 `bootstrap_mask`와 같은 $b_t$로 통일 |
| 마스크 표의 $c_t$ 열에 산문 | 4장 "rollout 끝이지만 episode 계속" 행 | 예제 코드 확인 결과 두 마스크 모두 1이고 재귀는 $\hat A_{t+1}=0$에서 시작해 batch 경계에서 끝난다. 표를 그대로 수정 |

### 본문과 예제 코드의 어긋남

`examples/ppo_components.py`, `examples/ppo_cartpole.py`, `examples/torchrl_ppo.py`,
`tests/test_ppo_components.py`를 읽고 본문 발췌와 한 줄씩 대조했다.

- **테스트 커버리지 과장**: 6장은 단위 테스트가 네 계약을 확인한다고 썼다. 실제로는
  `ppo_cartpole.py`가 `generalized_advantage_estimate()`와 `explained_variance()`만
  가져다 쓰고, clipping은 `update_model()` 안에 다시 작성했으며 `discounted_returns()`는
  호출하지 않는다. 6·7·9장 서술을 실제 범위로 축소했다.
- `train()` 발췌가 실제 첫 두 줄(`seed_everything`, `select_device`)을 생략 표시 없이 빼고 있었다.
- `build_model()` 발췌가 observation space 검사를 빼고 있었다.
- mini-batch index의 `device` 인자가 실제 코드와 달랐다.
- KL 조기 중단 발췌에 빈 목록 가드 `epoch_kl_values and`가 빠져 있었다.
- advantage 표준화 위치를 "update 전"이라 썼으나 실제로는 `update_model()` 첫 부분이다.
- `explained_variance()`가 target 분산 0에서 `nan`을 반환하는데 7장이 이를 적지 않았다.
- TorchRL 예제가 `empty()`를 두 번 호출하는데 8장 발췌는 뒤쪽만 보여 주었다.
- 가상환경 이름이 3·6장은 `.venv-ppo`, 8장은 `.venv`였다. 8장을 따랐다면 다른 환경이 생긴다.

### 실행하지 못한 검증 (중요)

이번 개정에서는 **예제를 한 번도 실행하지 않았다.** 이유:

- 저장소의 `.venv`는 NixOS에서 만든 Linux venv여서 현재 Windows 셸에서 사용할 수 없다.
- `torch==2.13.0`, `gymnasium==1.3.0`, `torchrl==0.13.3`은 설치되어 있지 않다.
- 본문 산문 퇴고가 목적이고 예제 코드는 읽기 전용으로 합의했으므로, 실행이 확인하는 것은
  "이전 사이클에서 통과한 게이트가 여전히 통과한다"뿐이다.

따라서 `_work/08_publish.md`의 2026-08-21·2026-09-08 실행 게이트 결과는 **이번 개정에서
재확인되지 않았다.** 예제 코드 자체는 한 줄도 바꾸지 않았으므로 그 결과가 무효가 되지는
않지만, 이번 개정의 증거로 인용할 수는 없다.

### 후속 작업으로 분리한 항목

`ppo_cartpole.py`의 `update_model()`이 clipping을 인라인하는 대신
`ppo_components.clipped_surrogate()`를 호출하도록 바꾸면 단위 테스트가 학습 경로를 직접
검증한다. 더 나은 최종 상태이지만, 학습 코드를 고치고 한 번도 실행하지 못하는 것이 최악의
결과이므로 실행 가능한 환경에서 별건으로 수행한다.
