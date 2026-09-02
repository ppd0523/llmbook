# 03. 구성안

## 학습 흐름

1. `index.md` — 목표, 결과물, 선수 지식, 전체 지도
2. `01-system-requirements-and-installation.md` — 호환성 표, Ubuntu/드라이버/uv/Isaac Sim/Isaac Lab 설치와 검증
3. `02-isaac-lab-mental-model.md` — Isaac Sim과 Isaac Lab 차이, backend/scene/asset/env/RL wrapper의 관계
4. `03-build-urdf-and-convert-usd.md` — 2-DOF 원판 URDF 작성, 검증, USD 변환
5. `04-design-ball-on-plate-task.md` — MDP 명세, 좌표계, 관측/행동/보상/종료/리셋/평가 기준
6. `05-direct-environment.md` — 외부 프로젝트와 Direct 환경 구현
7. `06-train-evaluate-and-debug.md` — PPO 연결, smoke test, 학습, 재현 가능한 평가, 보상 디버깅
8. `07-manager-based-environment.md` — 같은 MDP를 manager term으로 분해하고 Direct와 비교
9. `08-newton-and-physx.md` — Newton 주 경로와 PhysX 비교, backend gap 해석
10. `09-final-project-and-troubleshooting.md` — 움직이는 목표점 과제, 완료 기준, 고장 진단표

## 장별 반복 구조

- 이 장에서 답할 질문
- 핵심 개념
- 실행 또는 구현
- 확인 체크포인트
- 흔한 실패와 원인
- 다음 장 연결

## 예제 프로젝트 구조

```text
examples/ball_on_plate_lab/
├── VERSION_LOCK.md
├── README.md
├── scripts/
│   ├── list_envs.py
│   └── evaluate.py
└── source/ball_on_plate_lab/
    ├── config/extension.toml
    ├── setup.py
    └── ball_on_plate_lab/
        ├── assets/
        │   ├── urdf/ball_on_plate.urdf
        │   └── usd/README.md
        └── tasks/
            ├── common.py
            ├── direct/ball_on_plate/
            └── manager_based/ball_on_plate/
```

## 교육 설계

- 먼저 Direct에서 프레임마다 실제로 무엇이 호출되는지 보이게 한다.
- 다음으로 같은 함수와 상수를 Manager-based term으로 옮겨 구조화의 이점을 확인한다.
- PPO 하이퍼파라미터는 최소 설명만 하고 환경 설계와 평가에 시간을 쓴다.
- 모든 실행 절차는 예상 결과와 중단 기준을 함께 제공한다.
- GPU가 없는 작성 환경에서 검증하지 않은 결과 수치는 예시로 단정하지 않는다.
