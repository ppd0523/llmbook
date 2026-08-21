---
title: PyTorch PPO 학습 자료 수정 기록
version: 0.9
status: final
owner: agent
updated: 2026-08-21
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
