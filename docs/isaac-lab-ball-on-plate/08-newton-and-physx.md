# 8. Newton과 PhysX 비교

같은 환경 코드가 두 백엔드에서 실행된다는 말은 결과가 동일하다는 뜻이 아니다. 접촉 모델, 마찰 결합, 솔버, 하위 스텝, 수치 정밀도가 다르므로 정책 성능 차이를 측정해야 한다.

## 8.1 이 책의 역할 분담

| 작업 | Newton MJWarp | Isaac Sim PhysX |
|---|---:|---:|
| 대규모 반복 학습 | 주 경로 | 선택 |
| kit-less 실행 | 가능 | 불가 |
| Newton visualizer | 가능 | 불가 |
| URDF importer | 불가 | 필요 |
| Isaac Sim GUI/RTX | 불가 | 가능 |
| 최종 교차 백엔드 평가 | 기준 | 비교 |

Isaac Lab 3.0 kit-less 기능표는 [공식 설치 문서](https://isaac-sim.github.io/IsaacLab/v3.0.0-beta2/source/setup/installation/kitless_installation.html)에 있다.

## 8.2 바뀌어야 하는 것은 프리셋뿐이다

Newton 평가:

```bash
./isaaclab.sh -p "$PROJECT/scripts/evaluate.py" \
  --task BallOnPlate-Direct-v0 \
  --checkpoint "$CHECKPOINT" \
  --episodes 100 --seed 20260902 --headless \
  physics=newton_mjwarp | tee policy_newton.json
```

PhysX 평가:

```bash
./isaaclab.sh -p "$PROJECT/scripts/evaluate.py" \
  --task BallOnPlate-Direct-v0 \
  --checkpoint "$CHECKPOINT" \
  --episodes 100 --seed 20260902 --headless \
  physics=physx | tee policy_physx.json
```

다음은 바꾸지 않는다.

- 태스크 ID
- 체크포인트
- 평가 시드
- 에피소드 수
- 관측·행동·보상·종료 코드
- USD 루트 레이어

한 번에 백엔드 외의 변수를 바꾸면 차이를 해석할 수 없다.

## 8.3 비교표

실행 뒤 다음 표를 채운다.

| 지표 | Newton | PhysX | 차이 |
|---|---:|---:|---:|
| 생존율 |  |  | PhysX − Newton |
| 중심 체류율 |  |  | PhysX − Newton |
| 평균 정규화 반경 |  |  | PhysX − Newton |
| 에피소드 100회 실행 시간 |  |  |  |
| 최대 VRAM 사용량 |  |  |  |

성능 차이가 곧 한 백엔드의 버그라는 뜻은 아니다. 정책은 Newton 롤아웃 분포에 최적화되었으므로 PhysX에서는 도메인 차이가 나타난다.

## 8.4 차이가 생기는 지점

### 접촉과 마찰

공-원판 접촉의 침투 보정과 마찰 원뿔 근사가 다르면 공 감속이 달라진다. 이 과제는 구름 동역학에 민감하므로 작은 차이도 10초 동안 누적된다.

### actuator 응답

같은 강성과 감쇠라도 솔버가 관절 제약과 접촉을 함께 푸는 방식 때문에 실제 원판 각도 추종이 달라질 수 있다. 목표값만 비교하지 말고 `joint_pos` 응답을 비교한다.

### 시간 적분

둘 다 `dt=1/120`, 정책 주기 30 Hz여도 내부 하위 스텝과 솔버 반복 횟수는 다를 수 있다. 백엔드를 비교할 때 시간 설정부터 기록한다.

### 재질 무작위화

PhysX는 유한한 재질 버킷을 만들고, Newton은 마찰과 반발을 백엔드 방식에 맞춰 적용한다. 같은 범위는 같은 분포 의도를 뜻하지만 표본별 물리 동일성을 보장하지 않는다.

## 8.5 원인 분리 실험

PhysX 성능이 크게 낮으면 다음 순서로 한 변수씩 검사한다.

1. 재질 무작위화를 고정값으로 바꾸고 비교한다.
2. 단일 환경에서 0 행동으로 공 감속 곡선을 기록한다.
3. 동일한 사인파 행동으로 관절 위치 응답을 기록한다.
4. 물리 하위 스텝과 솔버 설정을 기록한다.
5. 마지막으로 PhysX에서 짧게 미세 조정한다.

처음부터 PhysX 하이퍼파라미터를 여러 개 바꾸면 어느 물리 차이가 원인이었는지 알 수 없다.

## 8.6 환경 작성 방식까지 교차 비교한다

최종 비교는 2×2가 된다.

| | Newton | PhysX |
|---|---|---|
| Direct | 기준 학습·평가 | 같은 체크포인트 평가 |
| Manager-based | 같은 MDP 재구현 | 작성 방식과 백엔드 동시 확인 |

네 칸을 모두 한 번에 최적화할 필요는 없다. 권장 순서는 다음과 같다.

1. Direct + Newton에서 학습 성공
2. Manager + Newton에서 계약 동등성 확인
3. Direct + PhysX에서 백엔드 차이 측정
4. Manager-based + PhysX에서 최종 통합 간이 실행 시험

## 8.7 교차 백엔드 통과 기준

기본 과제의 절대 통과 기준 90%/80%는 Newton 학습 기준이다. PhysX 비교에서는 다음을 함께 보고한다.

- PhysX가 절대 기준을 통과하는가?
- 통과하지 않더라도 무작위 PhysX 정책보다 우수한가?
- Newton 대비 각 지표 감소폭은 얼마인가?
- 재질 고정 실험에서 차이가 줄어드는가?

이 네 질문이 있어야 “PhysX에서 안 됨”을 재현 가능한 기술 보고서로 바꿀 수 있다.

[← 7장](./07-manager-based-environment.md) · [9장: 최종 프로젝트와 문제 해결 →](./09-final-project-and-troubleshooting.md)
