# 01. 범위 정의

## 학습 자료 목표

Isaac Lab 3.0의 핵심 구조를 복잡한 로봇 없이 익힌다. 학습자는 원형 판의 두 축 기울기를 제어해 공을 중심 부근에 유지하는 강화학습 환경을 직접 만들고, 같은 MDP를 Direct 및 Manager-based 방식으로 각각 구현한다.

## 대상 독자와 선수 지식

- Python과 PyTorch 텐서 연산을 사용할 수 있다.
- 강화학습의 상태, 행동, 보상, 에피소드 개념은 복습이 필요할 수 있다.
- PPO 이론과 구현은 기존 `pytorch-ppo-learning` 자료를 선수 과정으로 둔다.
- Isaac Sim과 Isaac Lab은 처음 사용한다고 가정한다.

## 고정 기술 스택

| 항목 | 기준 버전 |
|---|---|
| Ubuntu | 24.04 LTS x86_64 |
| NVIDIA 드라이버 | 595.58.03 (Isaac Sim 6.0.1 Linux 검증 버전) |
| Python | 3.12 |
| Isaac Sim | 6.0.1 / pip 패키지 6.0.1.0 |
| Isaac Lab | v3.0.0-beta2.patch1, commit `ffff603` |
| PyTorch / torchvision | 2.11.0 / 0.26.0, CUDA 12.8 wheel |
| 환경 관리자 | uv |
| 학습 라이브러리 | RSL-RL, PPO |
| 주 학습 백엔드 | Newton MJWarp, kit-less |
| 비교 백엔드 | Isaac Sim PhysX |

이 버전 묶음은 2026-09-02 기준 최신 태그를 고정한 재현 가능한 조합이다. 베타 릴리스이므로 `main`이나 `develop`을 설치하지 않는다.

## 예제 과제

- 반지름 `R = 0.5 m`인 테두리 없는 원형 판
- 반지름 `0.04 m`인 공 하나
- `roll_joint`, `pitch_joint` 두 회전 관절의 목표 각도가 행동
- 기본 과제는 중심 안정화, 마지막 과제는 움직이는 목표점 추종
- 판 밖으로 벗어나거나 아래로 떨어지면 조기 종료
- 에피소드 최대 길이 10초
- 초기 공 위치는 중심에서 `0.5R` 이내, 초기 속도와 일부 물리 파라미터는 무작위화

## 성공 기준

고정된 100개 시드로 평가한다.

1. 에피소드 최대 시간까지 생존한 비율이 90% 이상이다.
2. 전체 평가 스텝 중 공 중심이 `0.25R` 이내인 비율이 80% 이상이다.
3. 생존율과 평균 정규화 반경 모두 무작위 정책보다 낫다.
4. Direct와 Manager-based 구현이 같은 관측, 행동, 보상, 종료 정의를 사용한다.
5. Newton에서 학습한 체크포인트를 PhysX에서 비교 평가하고 차이를 기록한다.

## 산출물

- MkDocs 다중 장 학습 자료 10개 문서
- 외부 설치형 `ball_on_plate_lab` 예제 프로젝트
- 직접 작성하는 URDF와 변환 명령
- Direct 및 Manager-based 환경, RSL-RL 설정, 평가 스크립트
- Newton/PhysX 비교 절차와 문제 해결표

## 제외 범위

- PPO 수식과 알고리즘 구현의 상세 설명
- 실제 로봇 제어와 sim-to-real 배포
- 카메라나 접촉 센서 기반 관측
- `unitree_rl_lab` 설치 및 마이그레이션
- 현재 Windows/비-NVIDIA 문서 작성 PC에서의 시뮬레이션 실행

## 제약과 검증 전략

현재 PC에서는 GPU 실행 검증을 하지 않는다. 대신 공식 태그의 API와 설치 문서를 기준으로 코드를 작성하고, Python 문법, URDF XML, 내부 링크, MkDocs strict 빌드를 정적 검증한다. 실제 GPU 실행 체크리스트는 Ubuntu/NVIDIA 대상 장비에서 순서대로 수행하도록 제공한다.
