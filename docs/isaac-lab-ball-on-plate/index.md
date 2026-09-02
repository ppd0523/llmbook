# 원반 위 공으로 배우는 Isaac Lab 강화학습

이 책은 복잡한 로봇 대신 **두 축으로 기울어지는 원형 판과 공 하나**로 Isaac Lab의 환경 작성법을 배운다. 먼저 모든 제어 흐름이 보이는 Direct 환경을 만들고, 같은 MDP를 Manager-based 환경으로 다시 구성한다. 학습은 Newton MJWarp로 빠르게 반복하고, 마지막에 Isaac Sim PhysX로 같은 정책을 비교한다.

최종 결과는 다음 네 가지다.

1. 직접 작성한 URDF에서 변환한 2-DOF 원판 USD
2. `BallOnPlate-Direct-v0`와 `BallOnPlate-Manager-v0`
3. 고정 시드 100회 평가와 무작위 정책 기준선
4. 움직이는 목표점을 따라가는 확장 과제

## Isaac Sim과 Isaac Lab은 무엇이 다른가

둘은 경쟁 제품이 아니라 층이 다르다.

| 구분 | Isaac Sim | Isaac Lab |
|---|---|---|
| 한 문장 | 로봇 시뮬레이터 | 로봇 학습 프레임워크 |
| 주 역할 | USD 장면, PhysX, RTX 렌더링, 센서, 자산 임포터 | 병렬 환경, 자산 API, MDP, 무작위화, RL 라이브러리 연결 |
| 이 책에서 | URDF→USD 변환과 PhysX 비교 | 환경 작성, Newton 학습, RSL-RL 연결 |
| 반드시 함께 실행하는가 | 아니다 | Isaac Lab 3.0은 Newton kit-less 모드를 지원한다 |

Isaac Lab 3.0은 백엔드 팩토리를 통해 같은 자산·환경 인터페이스를 Newton과 PhysX 구현에 연결한다. 따라서 “Isaac Sim을 배우고 나서 Isaac Lab을 배운다”기보다, 학습 루프는 Isaac Lab에서 만들고 시뮬레이터 고유 기능이 필요할 때 Isaac Sim을 사용한다고 이해하면 된다. 자세한 패키지 관계는 [공식 생태계 문서](https://isaac-sim.github.io/IsaacLab/v3.0.0-beta2/source/setup/ecosystem.html)에서 확인할 수 있다.

## 고정 버전

이 책은 2026-09-02 현재 최신 태그를 다음과 같이 고정한다.

| 구성 요소 | 버전 |
|---|---|
| Ubuntu | 24.04 LTS x86_64 |
| NVIDIA 드라이버 | 595.58.03 |
| Python | 3.12 |
| Isaac Sim | 6.0.1, pip `6.0.1.0` |
| Isaac Lab | `v3.0.0-beta2.patch1`, commit `ffff603` |
| PyTorch / torchvision | 2.11.0 / 0.26.0, CUDA 12.8 wheel |
| RL 라이브러리 | RSL-RL 5.0.1 계열 |

Isaac Lab patch1은 Isaac Sim 6.0.1 지원을 추가한 최신 태그다. `main`이나 `develop`은 더 새 코드일 수 있지만 재현 가능한 릴리스가 아니다. [Isaac Lab 릴리스](https://github.com/isaac-sim/IsaacLab/releases/)와 [release 브랜치 README](https://github.com/isaac-sim/IsaacLab/blob/release/3.0.0-beta2/README.md)가 이 조합을 명시한다.

!!! warning "현재 PC가 아니라 실행 대상 PC 기준"

    이 자료는 Windows 랩탑에서 작성·정적 검사되었지만, 실제 실행 대상은 Ubuntu 24.04와 NVIDIA RTX GPU를 갖춘 별도 PC다. 현재 PC에 Isaac Sim이나 CUDA를 억지로 설치하지 않는다.

## 선수 지식

- Python 함수, 클래스, import를 읽을 수 있어야 한다.
- PyTorch 텐서의 shape와 기본 연산을 이해해야 한다.
- PPO는 [처음부터 구현하며 배우는 PyTorch PPO](../pytorch-ppo-learning/index.md)를 선수 자료로 사용한다.

PPO는 이 책에서 “병렬 롤아웃을 모으고 제한된 목적 함수로 actor와 critic을 갱신하는 on-policy 알고리즘” 정도만 복습한다. 수식 유도보다 관측·행동·보상·종료·리셋을 올바르게 정의하는 데 집중한다.

## 학습 경로

| 단계 | 장 | 완료 기준 |
|---:|---|---|
| 1 | [시스템 요구 사항과 설치](./01-system-requirements-and-installation.md) | 버전을 확인하고 Cartpole을 Newton과 PhysX로 각각 실행한다. |
| 2 | [Isaac Lab의 정신 모델](./02-isaac-lab-mental-model.md) | 백엔드, 장면, 자산, 환경, RL 래퍼의 관계를 설명한다. |
| 3 | [URDF 작성과 USD 변환](./03-build-urdf-and-convert-usd.md) | 두 회전 관절을 확인하고 USD 루트 레이어를 만든다. |
| 4 | [Ball-on-Plate MDP 설계](./04-design-ball-on-plate-task.md) | 12차원 관측, 2차원 행동, 보상, 종료를 표로 검토한다. |
| 5 | [Direct 환경 구현](./05-direct-environment.md) | 무작위 행동으로 병렬 환경이 리셋되는 것을 확인한다. |
| 6 | [학습·평가·디버깅](./06-train-evaluate-and-debug.md) | 100회 평가 기준과 무작위 기준선을 비교한다. |
| 7 | [Manager-based 환경](./07-manager-based-environment.md) | 같은 MDP가 관리자 항으로 어떻게 분해되는지 설명한다. |
| 8 | [Newton과 PhysX 비교](./08-newton-and-physx.md) | 동일 체크포인트의 백엔드 차이를 측정한다. |
| 9 | [최종 프로젝트와 문제 해결](./09-final-project-and-troubleshooting.md) | 움직이는 목표점 과제와 완료 보고서를 만든다. |

## 제공 예제

- [예제 프로젝트 README](./examples/ball_on_plate_lab/README.md)
- [버전 잠금표](./examples/ball_on_plate_lab/VERSION_LOCK.md)
- [원판 URDF](./examples/ball_on_plate_lab/source/ball_on_plate_lab/ball_on_plate_lab/assets/urdf/ball_on_plate.urdf)
- [공유 MDP 함수](./examples/ball_on_plate_lab/source/ball_on_plate_lab/ball_on_plate_lab/tasks/common.py)
- [Direct 환경](./examples/ball_on_plate_lab/source/ball_on_plate_lab/ball_on_plate_lab/tasks/direct/ball_on_plate/ball_on_plate_env.py)
- [Manager-based 설정](./examples/ball_on_plate_lab/source/ball_on_plate_lab/ball_on_plate_lab/tasks/manager_based/ball_on_plate/ball_on_plate_env_cfg.py)
- [고정 시드 평가 스크립트](./examples/ball_on_plate_lab/scripts/evaluate.py)

제공 코드는 답안이면서 비교 기준이다. 각 장에서 먼저 작은 부분을 직접 작성하고, 막혔을 때 해당 파일과 비교하는 순서가 가장 좋다.

[1장: 시스템 요구 사항과 설치 →](./01-system-requirements-and-installation.md)
