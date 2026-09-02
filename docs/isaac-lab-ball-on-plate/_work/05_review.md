# 05. 검토 기록

## 사실과 버전

- 최신 release tag `v3.0.0-beta2.patch1`, commit `ffff603`, Isaac Sim 6.0.1 지원을 릴리스 페이지와 branch README에서 교차 확인했다.
- Isaac Sim 6.0.1 Ubuntu/driver/GPU/RAM 요구 사항을 공식 requirements 페이지에서 확인했다.
- Python 3.12, uv, Newton kit-less, `physics=` preset, 외부 프로젝트 실행 경로를 해당 version 문서와 tag source에서 확인했다.
- Direct Cartpole, Manager Cartpole, RSL-RL config, URDF converter를 patch1 tag API 표본으로 사용했다.

## 교육 구조

- PPO 상세가 환경 framework 학습을 가리지 않도록 기존 PPO 책으로 연결했다.
- Direct를 먼저 두고 Manager-based를 같은 MDP의 refactor로 설명했다.
- reward와 독립적인 생존율·중심 체류율·평균 반경을 성공 지표로 사용했다.
- 단순 성공 명령뿐 아니라 단계별 중단 기준과 오류 원인 순서를 제공했다.

## 코드 검토

- 공통 상수, 관측, 보상, 종료, reset을 `tasks/common.py`에 모아 두 workflow의 drift를 줄였다.
- 3.0의 `ProxyArray.torch`, keyword-only `_index` API, XYZW 주의 사항을 반영했다.
- 공의 schema는 deprecated 2.x alias 대신 3.0의 `RigidBodyBaseCfg`, `CollisionBaseCfg`, `RigidBodyMaterialBaseCfg`를 사용했다.
- Gym registration과 external callback 경로를 분리했다.
- Direct config의 asset field에 명시적 type을 추가했다.
- 사용하지 않는 `SceneEntityCfg` 선언을 제거했다.
- evaluation seed, episode 수, random baseline을 고정했다.

## 검증 결과

- Python 파일 18개의 구문 검사가 통과했다.
- URDF XML이 파싱되며 링크 3개와 관절 2개를 확인했다.
- MkDocs Material 9.7.6으로 `mkdocs build --strict`가 성공했다.
- 최종 퇴고 뒤 영문 기술어 표기를 정리하고 같은 엄격 빌드를 다시 통과했다.
- 미완료 작업이나 출처 보강 표시는 최종 문서에서 발견되지 않았다.

## 남은 실행 위험

- Isaac Lab 런타임 import와 시뮬레이션은 대상 Ubuntu/NVIDIA PC에서 확인해야 한다.
- URDF importer가 생성한 layered USD의 실제 경로는 대상 PC 출력으로 확정해야 한다.
- Newton과 PhysX의 접촉 차이 때문에 성능 기준은 실제 학습으로만 판정할 수 있다.
- Isaac Lab 3.0은 beta이므로 version lock을 풀면 API 호환을 보장하지 않는다.

이 위험은 누락이 아니라 사용 환경 제약이며, 각 항목의 실행 gate를 본문에 명시했다.
