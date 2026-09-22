---
title: PyTorch PPO 학습 자료 수정 기록
version: 1.0
status: final
owner: agent
updated: 2026-09-22
target_reader: 강화학습과 PyTorch 초심자
topic: 순수 PyTorch PPO 구현에서 TorchRL까지
---

# 수정 기록

## 1. 범위와 순서

| 변경 전 위험 | 수정 | 효과 |
|---|---|---|
| 수학 복습 뒤 바로 policy gradient로 이동 | 2장을 MDP·value·Bellman·TD 중심으로 확장 | 대학 과정의 정책 평가 기반을 확보했다. |
| 대학 자료가 참고문헌에만 존재 | 목차와 각 장의 학습 흐름에 Stanford·Berkeley·MIT 순서를 대응 | 순서 선택의 근거가 드러난다. |
| 광범위한 value-based RL까지 포함할 가능성 | Q-learning·DQN은 후속 키워드와 순서만 제공 | PPO 목표를 유지하면서 선수 경로를 안내한다. |
| ONNX 전환이 최종 단계 | 직접 PyTorch→TorchRL→재현 실험으로 교체 | 현재 사용 목표와 일치한다. |

## 2. 개념 설명

1. State와 observation을 같은 말로 단정하지 않고 CartPole에서는 observation이 충분한 경우라고 설명했다.
2. Episode, trajectory, rollout을 구분했다.
3. `terminated`와 `truncated`를 첫 환경 코드부터 별도 변수로 유지했다.
4. Reward, return, value, Q-value, advantage를 작은 수 예제로 단계별 정의했다.
5. PPO clipping은 “항상 작은 update를 보장”한다고 표현하지 않고 surrogate incentive를 제한한다고 수정했다.
6. Entropy, KL, explained variance는 단독 합격 기준이 아니라 조합 진단 지표로 설명했다.
7. 여러 seed는 bit-level 재현보다 결과 분포의 반복 가능성을 보는 것으로 명확히 했다.

## 3. 코드와 수치 안정성

1. Advantage normalization 분모에 작은 epsilon을 넣었다.
2. `Categorical` action dtype을 `torch.long`으로 고정했다.
3. New log probability 계산만 gradient graph 안에 남기고 rollout tensor는 detached 상태로 저장했다.
4. GAE에 bootstrap mask와 continuation mask를 분리했다.
5. Value, advantage, log probability shape를 `[T]`로 통일해 broadcasting을 막았다.
6. Gradient norm과 finite 상태를 관찰할 수 있게 했다.
7. PPO update 과대를 줄이기 위한 target KL early stopping을 포함했다.
8. 평가에는 `torch.inference_mode()`와 deterministic action을 사용했다.
9. TorchRL의 `NormalParamExtractor` import를 Tensordict 공개 위치로 맞췄다.

## 4. 시각화

| 시각화 | 수정 목적 |
|---|---|
| Agent–environment loop | 한 step의 정보 방향을 네 화살표로 분리 |
| CartPole MDP | 추상 기호를 실제 observation/action/reward에 연결 |
| Bellman backup | 즉시 reward와 다음 value의 합을 강조 |
| Autograd | sample된 action, log probability, loss의 gradient 경계 표시 |
| Actor–critic | 공유 observation에서 서로 다른 출력 역할 분리 |
| PPO dataflow | rollout이 여러 epoch 후 버려지는 생명주기 표시 |
| TorchRL map | 직접 객체와 library primitive를 일대일 대응 |
| Debug decision | 튜닝 전 계약·수식 검사의 우선순위 고정 |

Interactive lab은 현재 slider 값의 모든 중간 계산을 숫자로 표시하도록 했다. PPO lab은 advantage 부호를 바꾸면 clipping이 반대 방향의 과도한 확률 변화를 제한하는 것을 곡선과 상태 문장으로 함께 보여 준다.

## 5. 실습과 평가

- 각 장에 즉시 확인 가능한 연습문제와 접을 수 있는 정답을 추가했다.
- 단위 테스트는 GAE termination/truncation 경계와 PPO positive/negative clipping을 포함한다.
- Smoke test와 full training 명령을 분리했다.
- 최종 프로젝트에 사전 등록 표, 비교 설정, 최소 3 seed, 결과 schema, rubric을 추가했다.
- 성능이 낮더라도 절차와 한계를 충실히 보고하면 유효한 학습 결과가 되도록 평가 기준을 바꿨다.

## 6. 출판 전 상태

본문 수정은 완료됐고 남은 항목은 자동·실행 검증뿐이다. 검증 중 API나 링크 문제가 발견되면 최종 파일과 이 기록을 함께 갱신한다.

## 7. 2차 심층 퇴고 계획

이번 퇴고는 기존 문장을 늘리는 것이 아니라 개념 의존성을 복원한다.

1. **목차:** 공개 과정 범위 대응표와 “포함/개요/별도 과정” 표시를 추가한다.
2. **1장:** bandit 예로 탐색–활용을 소개한 뒤 sequential decision과 credit assignment로 이동한다. PPO의 알고리즘 좌표를 MDP 뒤에 둔다.
3. **2장:** 기호 시간선→return→확률·기댓값→가치→Bellman→MC/TD→bias/variance→최적화 수학 순으로 확장한다.
4. **3장:** tensor 전에 신경망 입력·파라미터·층·활성화·forward·loss·optimizer의 닫힌 학습 루프를 만든다.
5. **4장:** trajectory probability에서 REINFORCE까지 단계별로 유도하고 baseline의 zero-expectation 근거와 GAE의 n-step 연결을 보강한다.
6. **5장:** importance sampling 수치 예→surrogate→clip 해석→KL/trust region 순서로 확장한다.
7. **6장:** test 용어, 하이퍼파라미터 전수 표, 초기화, CSV 로깅과 SVG plotting을 추가한다.
8. **7장:** 실험 용어, 평가 protocol, 통계적 불확실성, EV 예외를 보강한다.
9. **8장:** 연속 확률밀도와 Normal/TanhNormal, TorchRL 객체의 데이터 수명과 key 계약을 상세화한다.
10. **9장:** 실행 가능한 CSV·plot 명령, 연구 용어 정의, 전체 용어·기호 색인을 추가한다.

## 8. 2차 퇴고 완료 조건

- [x] 각 전문용어는 첫 사용 문장 또는 바로 앞에서 정의된다.
- [x] 각 핵심 개념은 필요성, 정의, 직관, 숫자 예, 한계 중 최소 네 요소를 가진다.
- [x] 공개 커리큘럼의 핵심 주제가 포함·개요·의도적 생략 중 하나로 분류된다.
- [x] 신경망을 처음 보는 독자가 3장 코드의 모든 layer와 optimizer 단계를 설명할 수 있다.
- [x] 독자가 4장의 policy gradient 유도에서 생략된 등호를 추적할 수 있다.
- [x] 최종 프로젝트의 CSV와 학습 곡선을 제공된 코드만으로 생성할 수 있다.
- [x] 개정 뒤 단위·smoke·plot·링크·MkDocs 검사를 다시 통과한다.

2차 퇴고 검증에서는 4-row smoke CSV와 여섯 지표 panel SVG를 실제 생성하고, 주기 평가 값이 각 update 행에 기록되는지 확인했다.

## 9. 잔차 용어 퇴고

2026-09-08 추가 퇴고에서는 다음 네 문맥을 분리했다.

1. Target에서 예측을 뺀 일반 회귀 잔차 $e=y-\hat y$
2. 한 transition의 TD 오차 또는 TD 잔차 $\delta_t$
3. 입력에 신경망 보정을 더하는 residual connection $h+F(h)$
4. 기존 제어 행동에 학습한 residual action을 더하는 residual reinforcement learning

TD 잔차와 기대 Bellman 잔차의 표본·기댓값 차이를 명시하고, actor는 잔차 부호를 advantage 신호로 사용하지만 critic은 value target과 예측의 회귀 잔차를 줄인다는 역할 차이를 추가했다. 8장에는 잔차 정책의 결합식, torque 수치 예, residual scale과 action bound의 실패 조건을 넣었다. 예제 코드와 GAE 시각화의 용어도 같은 표기로 맞췄다.


## 10. 3차 개정: 구조 퇴고와 중복 단일화 (2026-09-22)

### 중복 처리 원칙

같은 표·수식·명령어가 두 곳 이상이면 canonical 위치 하나로 모으고, 말로 된 직관 설명과
연습문제의 중복은 남겼다. 1장의 직관은 중복이 아니라 선행 진입로이고, 같은 개념을 여러 장의
연습문제에서 확인하는 것은 반복 학습이다. 반면 동일한 표가 두 장에 복제된 상태는 한쪽만
고치면 즉시 어긋나는 유지 비용만 만든다.

| 중복 항목 | 이전 | canonical | 나머지 처리 |
|---|---|---|---|
| ablation 후보 표 (5행 동일) | 7장, 9장 | 7장 | 9장은 참조 + 프로젝트 제약만 |
| 평가 방식 sampling/argmax | 6·7·9장 | 7장 표 | 9장이 7장을 가리킨다 |
| entropy 정의와 수치 예 | 1·3·4장 | 3장 (`Categorical.entropy()`) | 4장은 loss 안의 역할만, 1장 직관은 유지 |
| 후속 학습 키워드 목록 | 2장, 9장 | 9장 | 2장은 용어 뜻과 참조만 |

`terminated`/`truncated` bootstrap 설명은 6곳에 있었으나 각각 직관(1장), 정의(2장),
마스크 표(4장), 코드(6장), 연습문제(7·9장)로 층이 다르므로 유지했다.

### 요약 절 신설

`.guide/PROCESS.md`는 초고에 요약을 요구하는데 9개 장 어디에도 요약이 없었다. 각 장 끝에
"이 장에서 확정된 것"을 담은 `## 정리`를 3~5개 불릿으로 신설했다. 중복을 걷어낸 자리에
다음 장으로 넘어갈 근거를 남기는 역할이다.

### 잔차 용어

2026-09-08 개정으로 수렴시킨 용어 체계는 그대로 두었다. 1차 출처와 충돌하는 지점은 찾지
못했다. 바꾼 것은 위치뿐이다 — 네 문맥 구분 표가 8장(TorchRL)에 있어 TD 잔차가 처음 나오는
4장보다 네 장 뒤에서야 혼동이 해소됐으므로, 표를 4장의 TD 잔차 절 직후로 옮기고 연속 행동과
직접 이어지는 잔차 강화학습만 8장에 남겼다.
