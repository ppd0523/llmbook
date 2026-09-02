# 02. 조사 기록

조사 기준일: 2026-09-02

## 버전과 호환성

- Isaac Lab 릴리스 페이지의 최신 태그는 `v3.0.0-beta2.patch1`이며 commit은 `ffff603`이다. 이 패치는 Isaac Sim 6.0.1 지원을 추가한다.
  - https://github.com/isaac-sim/IsaacLab/releases/
- `release/3.0.0-beta2` README는 재현 가능한 체크아웃에 patch1 태그를 사용하라고 명시한다.
  - https://github.com/isaac-sim/IsaacLab/blob/release/3.0.0-beta2/README.md
- Isaac Sim 6.0.1 x86_64 요구 사항은 Ubuntu 22.04/24.04, Linux 드라이버 595.58.03, 최소 RTX 4080/16 GB VRAM, RAM 32 GB다.
  - https://docs.isaacsim.omniverse.nvidia.com/6.0.1/installation/requirements.html
- Isaac Sim 6.x는 Python 3.12를 요구한다.
  - https://isaac-sim.github.io/IsaacLab/v3.0.0-beta2/source/setup/installation/kitless_installation.html

## 설치 경로

- Isaac Lab 3.0은 Isaac Sim 없이 Newton을 사용하는 kit-less 설치를 지원한다.
- URDF/MJCF 임포터와 Isaac Sim PhysX는 Isaac Sim 설치가 필요하다.
- `uv` 가상 환경과 모듈 선택 설치가 공식 권장 경로다.
- 본 자료는 먼저 전체 호환 환경을 한 번 구성한 뒤, 평소 학습은 Newton kit-less 명령을 사용한다. 같은 가상 환경에 Isaac Sim을 두어 URDF 변환과 PhysX 비교를 가능하게 한다.
  - https://isaac-sim.github.io/IsaacLab/v3.0.0-beta2/source/setup/installation/index.html
  - https://isaac-sim.github.io/IsaacLab/v3.0.0-beta2/source/setup/quickstart.html

## 프레임워크 구조

- Isaac Sim은 물리, USD 장면, 렌더링, 센서, 임포터를 제공하는 시뮬레이터다.
- Isaac Lab은 그 위 또는 kit-less 백엔드 위에서 벡터화 환경, 자산 인터페이스, MDP 구성, RL 라이브러리 래퍼를 제공하는 로봇 학습 프레임워크다.
- Isaac Lab 3.0의 팩토리 기반 자산 계층은 사용자 환경 코드를 유지한 채 물리 백엔드를 선택할 수 있게 한다.
  - https://isaac-sim.github.io/IsaacLab/v3.0.0-beta2/source/setup/ecosystem.html
  - https://isaac-sim.github.io/IsaacLab/v3.0.0-beta2/source/overview/core-concepts/multi_backend_architecture.html

## 환경 작성 방식

- Direct는 `DirectRLEnv`를 상속하고 장면 구성, 행동 적용, 관측, 보상, 종료, 리셋을 한 클래스에 명시한다.
- Manager-based는 `ManagerBasedRLEnvCfg`와 Observation/Action/Reward/Event/Termination term을 조합한다.
- 공식 Cartpole 코드를 API 기준 표본으로 사용했다.
  - https://github.com/isaac-sim/IsaacLab/tree/v3.0.0-beta2.patch1/source/isaaclab_tasks/isaaclab_tasks/direct/cartpole
  - https://github.com/isaac-sim/IsaacLab/tree/v3.0.0-beta2.patch1/source/isaaclab_tasks/isaaclab_tasks/manager_based/classic/cartpole

## Isaac Lab 3.0 주의점

- 자산 데이터는 `ProxyArray`이며 PyTorch 연산에는 `.torch`를 사용한다.
- quaternion 순서는 XYZW다.
- `PresetCfg`로 `physx`, `newton_mjwarp` 등의 물리 설정을 노출한다.
- 베타 API이므로 2.x 튜토리얼 코드를 섞지 않고 태그 문서와 태그 소스를 기준으로 한다.
  - https://isaac-sim.github.io/IsaacLab/v3.0.0-beta2/source/migration/migrating_to_isaaclab_3-0.html

## 자산 파이프라인

- 학습자는 `base_link → roll_frame → plate` 구조의 URDF를 직접 작성한다.
- Isaac Sim의 URDF 임포터를 한 번 사용해 USD로 변환한다.
- 이후 환경은 같은 USD를 Newton과 PhysX에서 로드한다.
- 태그의 `scripts/tools/convert_urdf.py`는 `--fix-base`, position target, stiffness/damping 옵션을 지원한다.
  - https://isaac-sim.github.io/IsaacLab/v3.0.0-beta2/source/how-to/import_new_asset.html
  - https://github.com/isaac-sim/IsaacLab/blob/v3.0.0-beta2.patch1/scripts/tools/convert_urdf.py

## PPO와 평가

- RSL-RL은 Isaac Lab 3.0의 공식 RL 래퍼가 지원하는 라이브러리다.
- PPO 설명은 정책/가치 함수, rollout, clipped objective의 역할만 연결하고 기존 `pytorch-ppo-learning`으로 위임한다.
- 평가 지표는 학습 보상과 분리해 생존율, 중심 체류율, 평균 정규화 반경으로 고정한다.

## 보류 또는 위험

- 현재 작성 PC에서 Isaac Sim URDF 변환 결과 USD와 GPU 학습을 실행 검증할 수 없다.
- Newton과 PhysX의 접촉, 마찰, 적분 차이 때문에 동일 정책 성능은 달라질 수 있다.
- Isaac Lab 3.0은 베타다. 이 자료의 버전 잠금 파일을 바꾸지 않고 새 릴리스로 올리는 것은 별도의 마이그레이션 작업이다.
