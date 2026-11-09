---
title: PyTorch PPO 학습 자료 퇴고 기록
status: final
owner: agent
target_reader: 강화학습과 PyTorch 초심자
topic: 순수 PyTorch PPO 구현에서 TorchRL까지
---

# 퇴고 기록

## 1. 범위와 순서

| 결정 | 이유 |
|---|---|
| 2장은 MDP·value·Bellman·TD 중심이다. | 수학 복습 뒤 바로 policy gradient로 이동하면 대학 과정의 정책 평가 기반이 빠진다. |
| 목차와 각 장의 학습 흐름을 Stanford·Berkeley·MIT 순서에 대응한다. | 대학 자료가 참고문헌에만 있으면 순서 선택의 근거가 드러나지 않는다. |
| Q-learning·DQN은 후속 키워드와 순서만 제공한다. | PPO 목표를 유지하면서 선수 경로를 안내한다. |
| 최종 단계는 직접 PyTorch→TorchRL→재현 실험이며 ONNX 변환은 다루지 않는다. | 사용 목표와 일치한다. |

## 2. 개념 설명

1. State와 observation을 같은 말로 단정하지 않고 CartPole에서는 observation이 충분한 경우라고 설명한다.
2. Episode, trajectory, rollout을 구분한다.
3. `terminated`와 `truncated`를 첫 환경 코드부터 별도 변수로 유지한다.
4. Reward, return, value, Q-value, advantage를 작은 수 예제로 단계별 정의한다.
5. PPO clipping은 “항상 작은 update를 보장”한다고 표현하지 않고 surrogate incentive를 제한한다고 설명한다.
6. Entropy, KL, explained variance는 단독 합격 기준이 아니라 조합 진단 지표로 설명한다.
7. 여러 seed는 bit-level 재현보다 결과 분포의 반복 가능성을 보는 것으로 설명한다.

## 3. 코드와 수치 안정성

1. Advantage normalization 분모에 작은 epsilon을 둔다.
2. `Categorical` action dtype은 `torch.long`으로 고정한다.
3. New log probability 계산만 gradient graph 안에 남기고 rollout tensor는 detached 상태로 저장한다.
4. GAE에서 bootstrap mask와 continuation mask를 분리한다.
5. Value, advantage, log probability shape를 `[T]`로 통일해 broadcasting을 막는다.
6. Gradient norm과 finite 상태를 관찰할 수 있다.
7. PPO update 과대를 줄이기 위한 target KL early stopping을 포함한다.
8. 평가에는 `torch.inference_mode()`와 deterministic action을 사용한다.
9. TorchRL의 `NormalParamExtractor`는 Tensordict 공개 위치에서 import한다.

## 4. 시각화

| 시각화 | 목적 |
|---|---|
| Agent–environment loop | 한 step의 정보 방향을 네 화살표로 분리 |
| CartPole MDP | 추상 기호를 실제 observation/action/reward에 연결 |
| Bellman backup | 즉시 reward와 다음 value의 합을 강조 |
| Autograd | sample된 action, log probability, loss의 gradient 경계 표시 |
| Actor–critic | 공유 observation에서 서로 다른 출력 역할 분리 |
| PPO dataflow | rollout이 여러 epoch 후 버려지는 생명주기 표시 |
| TorchRL map | 직접 객체와 library primitive를 일대일 대응 |
| Debug decision | 튜닝 전 계약·수식 검사의 우선순위 고정 |

Interactive lab은 현재 slider 값의 모든 중간 계산을 숫자로 표시한다. PPO lab은 advantage 부호를 바꾸면 clipping이 반대 방향의 과도한 확률 변화를 제한하는 것을 곡선과 상태 문장으로 함께 보여 준다.

## 5. 실습과 평가

- 각 장에 즉시 확인 가능한 연습문제와 접을 수 있는 정답이 있다.
- 단위 테스트는 GAE termination/truncation 경계와 PPO positive/negative clipping을 포함한다.
- Smoke test와 full training 명령을 분리한다.
- 최종 프로젝트에는 사전 등록 표, 비교 설정, 최소 3 seed, 결과 schema, rubric이 있다.
- 성능이 낮더라도 절차와 한계를 충실히 보고하면 유효한 학습 결과가 되도록 평가 기준을 둔다.

## 6. 장별 개념 의존성

각 장은 문장을 늘리기보다 개념 의존성을 따라 설명한다.

1. **목차:** 공개 과정 범위 대응표와 “포함/개요/별도 과정” 표시를 둔다.
2. **1장:** bandit 예로 탐색–활용을 소개한 뒤 sequential decision과 credit assignment로 이동한다. PPO의 알고리즘 좌표를 MDP 뒤에 둔다.
3. **2장:** 기호 시간선→return→확률·기댓값→가치→Bellman→MC/TD→bias/variance→최적화 수학 순으로 설명한다.
4. **3장:** tensor 전에 신경망 입력·파라미터·층·활성화·forward·loss·optimizer의 닫힌 학습 루프를 만든다.
5. **4장:** trajectory probability에서 REINFORCE까지 단계별로 유도하고 baseline의 zero-expectation 근거와 GAE의 n-step 연결을 보인다.
6. **5장:** importance sampling 수치 예→surrogate→clip 해석→KL/trust region 순서로 설명한다.
7. **6장:** test 용어, 하이퍼파라미터 전수 표, 초기화, CSV 로깅과 SVG plotting을 다룬다.
8. **7장:** 실험 용어, 평가 protocol, 통계적 불확실성, EV 예외를 다룬다.
9. **8장:** 연속 확률밀도와 Normal/TanhNormal, TorchRL 객체의 데이터 수명과 key 계약을 다룬다.
10. **9장:** 실행 가능한 CSV·plot 명령, 연구 용어 정의, 전체 용어·기호 색인을 둔다.

## 7. 퇴고 완료 조건

- [x] 각 전문용어는 첫 사용 문장 또는 바로 앞에서 정의된다.
- [x] 각 핵심 개념은 필요성, 정의, 직관, 숫자 예, 한계 중 최소 네 요소를 가진다.
- [x] 공개 커리큘럼의 핵심 주제가 포함·개요·의도적 생략 중 하나로 분류된다.
- [x] 신경망을 처음 보는 독자가 3장 코드의 모든 layer와 optimizer 단계를 설명할 수 있다.
- [x] 독자가 4장의 policy gradient 유도에서 생략된 등호를 추적할 수 있다.
- [x] 최종 프로젝트의 CSV와 학습 곡선을 제공된 코드만으로 생성할 수 있다.
- [x] 단위·smoke·plot·링크·MkDocs 검사를 통과한다. 실행일과 결과는 `08_publish.md`에 있다.

2026-08-21 검증에서 4-row smoke CSV와 여섯 지표 panel SVG를 실제 생성하고, 주기 평가 값이 각 update 행에 기록되는지 확인했다. 현재 예제 코드에는 이 실행을 다시 하지 않았다.

## 8. 잔차 용어

잔차는 다음 네 문맥으로 분리해 쓴다.

1. Target에서 예측을 뺀 일반 회귀 잔차 $e=y-\hat y$
2. 한 transition의 TD 오차 또는 TD 잔차 $\delta_t$
3. 입력에 신경망 보정을 더하는 residual connection $h+F(h)$
4. 기존 제어 행동에 학습한 residual action을 더하는 residual reinforcement learning

TD 잔차와 기대 Bellman 잔차의 표본·기댓값 차이를 명시하고, actor는 잔차 부호를 advantage 신호로 사용하지만 critic은 value target과 예측의 회귀 잔차를 줄인다는 역할 차이를 설명한다. 예제 코드와 GAE 시각화의 용어도 같은 표기를 쓴다. 이 용어 체계는 1차 출처와 충돌하는 지점이 없다.

네 문맥 구분 표는 4장의 TD 잔차 절(`TD 오차 또는 TD 잔차를 advantage 신호로 쓰기`) 직후에 둔다. TD 잔차라는 이름은 2장의 TD 오차 정의에서 먼저 소개하고 표는 4장을 가리킨다. 혼동이 생기는 자리에서 답해야 하기 때문이다. 8장에는 연속 행동과 직접 이어지는 잔차 강화학습만 두고, 잔차 정책의 결합식, torque 수치 예, residual scale과 action bound의 실패 조건을 다룬다.

## 9. 중복 단일화

같은 표·수식·명령어가 두 곳 이상이면 canonical 위치 하나로 모으고, 말로 된 직관 설명과
연습문제의 중복은 남긴다. 1장의 직관은 중복이 아니라 선행 진입로이고, 같은 개념을 여러 장의
연습문제에서 확인하는 것은 반복 학습이다. 반면 동일한 표가 두 장에 복제되어 있으면 한쪽만
고치는 순간 어긋나는 유지 비용만 생긴다.

| 항목 | canonical | 나머지 위치 |
|---|---|---|
| ablation 후보 표 | 7장 | 9장은 참조 + 프로젝트 제약만 |
| 평가 방식 sampling/argmax | 7장 표 | 9장이 7장을 가리킨다 |
| entropy 정의와 수치 예 | 3장 (`Categorical.entropy()`) | 4장은 loss 안의 역할만, 1장 직관은 유지 |
| 후속 학습 키워드 목록 | 9장 | 2장은 용어 뜻과 참조만 |

`terminated`/`truncated` bootstrap 설명은 직관(1장), 정의(2장), 마스크 표(4장), 코드(6장),
연습문제(7·9장)로 층이 다르므로 여러 곳에 둔다.

## 10. 장 끝 정리 절

`.guide/PROCESS.md`는 초고에 요약을 요구하므로 각 장 끝에 "이 장에서 확정된 것"을 담은
`## 정리`를 3~5개 불릿으로 둔다. 중복을 걷어낸 자리에 다음 장으로 넘어갈 근거를 남기는
역할이다.
