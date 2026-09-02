# 9. 최종 프로젝트와 문제 해결

최종 프로젝트는 중심 안정화 환경의 네트워크 크기를 유지한 채 목표점만 움직인다. 목적은 코드를 크게 늘리는 것이 아니라, 이미 만든 환경 계약이 확장 가능한지 확인하는 것이다.

## 9.1 움직이는 목표점

목표는 반지름 `0.15 m`의 원을 5초에 한 바퀴 돈다.

\[
x^*(t)=0.15\cos(2\pi t/5),\qquad
y^*(t)=0.15\sin(2\pi t/5)
\]

[common.py의 `target_xy()`](./examples/ball_on_plate_lab/source/ball_on_plate_lab/ball_on_plate_lab/tasks/common.py)는 `episode_length_buf × step_dt`로 시간을 계산한다. 실제 경과 시간을 쓰지 않으므로 화면 없는 학습 속도와 관계없이 궤적이 같다.

```python
t = episode_length_buf.float() * step_dt
phase = 2.0 * math.pi * t / TARGET_PERIOD_S
target[:, 0] = TARGET_AMPLITUDE * torch.cos(phase)
target[:, 1] = TARGET_AMPLITUDE * torch.sin(phase)
```

기본 태스크와 다른 설정은 `moving_target=True`뿐이다.

```text
BallOnPlate-Tracking-Direct-v0
BallOnPlate-Tracking-Manager-v0
```

## 9.2 학습

먼저 Direct + Newton으로 학습한다.

```bash
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py \
  --task BallOnPlate-Tracking-Direct-v0 \
  --external_callback ball_on_plate_lab.tasks.register \
  --headless --num_envs 2048 --max_iterations 500 \
  physics=newton_mjwarp
```

중심 안정화보다 어려우므로 500회 반복에서 기준을 못 채울 수 있다. 먼저 목표 속도를 줄이기 위해 `TARGET_PERIOD_S=8.0`으로 커리큘럼을 시작하고, 성공한 뒤 5.0으로 되돌리는 실험이 가능하다. 두 실험의 태스크 설정과 체크포인트를 섞지 않는다.

## 9.3 추종 평가

기본 평가 스크립트의 `center_residence_rate`는 여전히 물리적 원판 중심 체류율이다. 움직이는 목표에서는 다음 지표를 추가하는 것이 자연스럽다.

```python
tracking_error = torch.linalg.vector_norm(obs[:, 0:2], dim=1)
tracking_residence = (tracking_error <= 0.25).float()
```

`obs[:,0:2]`는 `(ball-target)/R`이므로 `0.25` 이하는 목표로부터 `0.25R` 이내다. 최종 보고서는 다음을 모두 포함한다.

- 생존율
- 원판 중심 체류율
- 목표 추종 체류율
- 평균 정규화 추종 오차
- 무작위 추종 정책과의 비교

목표가 원판 중심에서 움직이므로 중심 체류율과 추종 체류율을 동시에 최대화할 수 없는 구간이 있다. 최종 과제에서는 추종 지표가 주 지표이고 생존율은 안전 지표다.

## 9.4 코드 확장 과제

다음 순서대로 한 가지씩 추가한다.

1. `evaluate.py`에 추종 체류율과 평균 추종 오차를 추가한다.
2. 목표 주기를 8초에서 5초로 줄이는 커리큘럼을 설정으로 만든다.
3. 목표 관측을 제거한 절제 실험을 학습해 성능을 비교한다.
4. 원판 마찰 무작위화 범위를 두 배로 넓혀 강건성을 비교한다.
5. Direct 체크포인트를 Manager-based 추종 태스크에서 평가한다.

각 과제는 한 번에 한 변수만 바꾸고, 시드와 평가 에피소드 수를 유지한다.

## 9.5 문제 해결표

| 증상 | 가능한 원인 | 확인·해결 |
|---|---|---|
| USD 파일을 찾지 못함 | 임포터 출력은 디렉터리 아래 로봇 이름 레이어 | `Generated USD file:` 경로를 확인하고 `BALL_ON_PLATE_USD` 설정 |
| articulation 관절을 찾지 못함 | URDF 이름 또는 임포터 결과 불일치 | Stage와 URDF에서 `roll_joint`, `pitch_joint` 확인 |
| 모든 환경이 즉시 종료 | 세계 좌표 사용, 초기 z 오류, 충돌 형상 누락 | 로컬 xy, `BALL_START_Z=0.252`, 충돌 형상 표시 확인 |
| `env_0`만 정상 | `env_origins`를 빼거나 더하지 않음 | 관측에서는 빼고 리셋 루트 자세에는 더함 |
| 공이 판을 통과 | 충돌 레이어 누락, 너무 큰 dt/속도 | USD 보조 레이어, 충돌 형상, `dt=1/120`, 침투 보정 확인 |
| 원판이 통째로 떨어짐 | `--fix-base` 없이 변환 | USD를 올바른 플래그로 다시 변환 |
| 행동해도 원판이 안 움직임 | actuator 관절 정규식, 드라이브, effort 한계 | 관절 ID와 목표 텐서, 강성·effort 확인 |
| 원판이 심하게 떨림 | 강성 과대 또는 감쇠 부족 | 단일 환경에서 스텝 응답 측정 후 게인 조정 |
| 보상은 증가하지만 중심에 안 옴 | 생존 보상·페널티 균형 또는 지표 오류 | 항별 크기와 독립 반경 지표 확인 |
| Newton만 import 실패 | 선택 설치에 Newton 없음 | `./isaaclab.sh -i 'newton,rl[rsl-rl]'` 재확인 |
| PhysX만 시작 실패 | Isaac Sim·버전·EULA·캐시 | `isaacsim==6.0.1.0`, 첫 실행, 공식 요구 사항 확인 |
| 태스크를 찾지 못함 | 외부 패키지 미설치·미등록 | 편집 가능 설치와 `--external_callback` 확인 |
| RSL-RL 체크포인트 크기 오류 | 관측 순서·크기 또는 actor 설정 변경 | `observation_space=12`, 항 순서, 설정 YAML 비교 |
| NaN 보상 | 잘못된 상태, 물리 발산, 지나친 게인 | 작은 환경 수, 유한성 단언, 관절·공 상태 범위 출력 |
| PhysX 성능만 낮음 | 접촉·마찰·actuator 백엔드 차이 | 8장의 고정 재질 및 스텝 응답 실험 |

## 9.6 버전 오류를 진단하는 순서

1. `git rev-parse --short HEAD`가 `ffff603`인지 본다.
2. Python이 3.12인지 본다.
3. `isaacsim`이 6.0.1 계열인지 본다.
4. PyTorch가 2.11.0 cu128인지 본다.
5. `nvidia-smi` 드라이버를 본다.
6. 설치 로그보다 현재 활성 환경의 `python -c` 결과를 신뢰한다.

2.x 문서의 import 경로, WXYZ 쿼터니언, 폐기 예정인 비인덱스 쓰기 API를 일부만 섞어 고치지 않는다. 새 가상 환경에서 이 책의 버전 잠금을 그대로 재현하는 편이 빠르다.

## 9.7 완료 보고서

최종 산출물은 다음 구조면 충분하다.

```text
1. 환경
   - GPU, 드라이버, OS, Isaac Lab 커밋, Isaac Sim, PyTorch
2. MDP
   - 관측·행동·보상·종료·리셋 표
3. 학습
   - 태스크 ID, 백엔드, 시드, 환경 수, 반복 횟수, 체크포인트 해시
4. 평가
   - 무작위 정책과 학습 정책, Newton과 PhysX, Direct와 Manager-based 비교표
5. 추종 확장
   - 목표 궤적과 추종 지표
6. 실패와 변경
   - 한 번에 바꾼 변수, 근거, 결과
7. 결론
   - 성공 기준 통과 여부와 다음 실험
```

## 9.8 최종 체크리스트

- [ ] Ubuntu/NVIDIA 요구 사항과 버전 잠금을 기록했다.
- [ ] URDF를 직접 작성하고 임포터 결과를 Stage에서 검증했다.
- [ ] Direct 환경에서 무작위 정책 간이 실행 시험이 끝난다.
- [ ] Direct + Newton 정책이 에피소드 100회 기준을 평가받았다.
- [ ] 무작위 기준선보다 생존율이 높고 평균 반경이 낮다.
- [ ] Manager-based 환경의 관측 12개 순서와 행동 2개 의미가 같다.
- [ ] 같은 체크포인트를 Newton과 PhysX에서 비교했다.
- [ ] 움직이는 목표점에서 추종 지표를 추가했다.
- [ ] 검증하지 않은 수치를 성공 결과로 쓰지 않았다.

이 체크리스트를 마치면 단순히 Isaac Lab 예제를 실행한 것이 아니다. 자산에서 MDP, 벡터화 리셋, 환경 작성 방식, RL 러너, 백엔드 비교까지 한 환경의 전체 수명주기를 직접 다룬 것이다.

[← 8장](./08-newton-and-physx.md) · [책 소개로 돌아가기](./index.md)
