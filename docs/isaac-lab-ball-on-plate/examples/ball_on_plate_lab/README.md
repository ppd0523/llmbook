# ball_on_plate_lab

Isaac Lab Ball-on-Plate 학습자료의 참고용 외부 프로젝트다. 실행하기 전에 상위 학습자료를 읽는다.

## 자산 준비

버전을 고정한 Isaac Lab 저장소에서 전체 Isaac Sim 환경을 활성화한 상태로 실행한다.

```bash
./isaaclab.sh -p scripts/tools/convert_urdf.py \
  /absolute/path/to/ball_on_plate.urdf \
  /absolute/path/to/ball_on_plate_lab/source/ball_on_plate_lab/ball_on_plate_lab/assets/usd \
  --fix-base --joint-target-type position \
  --joint-stiffness 40 --joint-damping 4 --headless
```

Isaac Sim 6 importer는 URDF의 로봇 이름으로 USD 파일 이름을 정한다. 기본 코드가 기대하는 경로는 다음과 같다.

```text
source/ball_on_plate_lab/ball_on_plate_lab/assets/usd/ball_on_plate/ball_on_plate.usd
```

importer가 다른 경로를 출력하면 `BALL_ON_PLATE_USD`를 그 파일의 절대 경로로 설정한다.

## 설치와 등록

```bash
uv pip install -e source/ball_on_plate_lab
python scripts/list_envs.py
```

## 학습

버전을 고정한 Isaac Lab 저장소 루트에서 실행한다. external callback이 태스크를 찾기 전에 이 패키지를 import한다.

```bash
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py \
  --task BallOnPlate-Direct-v0 \
  --external_callback ball_on_plate_lab.tasks.register \
  --headless --num_envs 2048 \
  physics=newton_mjwarp
```

Manager-based 버전에는 `BallOnPlate-Manager-v0`을 사용한다. 움직이는 목표점을 다루는 최종 프로젝트에는 `Tracking` 태스크 ID를 사용한다.

검증한 항목: Python 문법, URDF XML. 검증하지 않은 항목: Ubuntu + NVIDIA GPU 환경에서의 시뮬레이션·학습 실행. 이 두 가지는 대상 시스템에서 직접 확인한다.
