# 3. URDF 작성과 USD 변환

이 장에서는 원판 장치를 직접 기술한다. 목적은 예쁜 모델링이 아니라 **링크, 관절, 관성, 충돌 형상이 학습 환경에서 어떤 계약을 만드는지** 이해하는 것이다.

## 3.1 기구 구조

```text
base_link
└── roll_joint  (x축, ±12°)
    └── roll_frame
        └── pitch_joint (y축, ±12°)
            └── plate (반지름 0.5 m)
```

공은 URDF에 넣지 않는다. 원판은 관절이 있는 `Articulation`, 공은 에피소드마다 자세와 속도를 다시 쓰는 `RigidObject`이기 때문이다.

두 회전축이 한 점에서 교차하도록 `roll_joint` 원점을 `z=0.20 m`에 두고 `pitch_joint` 원점은 roll frame의 원점에 둔다. 판 두께가 0.02 m이므로 초기 공 중심 높이는 `0.20 + 0.01 + 0.04 + 0.002 = 0.252 m`다.

## 3.2 URDF를 직접 작성한다

예제의 [ball_on_plate.urdf](./examples/ball_on_plate_lab/source/ball_on_plate_lab/ball_on_plate_lab/assets/urdf/ball_on_plate.urdf)를 열어 다음 항목을 확인한다.

```xml
<joint name="roll_joint" type="revolute">
  <parent link="base_link"/>
  <child link="roll_frame"/>
  <origin xyz="0 0 0.20" rpy="0 0 0"/>
  <axis xyz="1 0 0"/>
  <limit lower="-0.20944" upper="0.20944"
         effort="12.0" velocity="2.0"/>
</joint>
```

`0.20944 rad`는 약 12도다. 너무 큰 기울기는 공이 즉시 가속해 보상 설계를 보기 어렵고, 너무 작은 기울기는 제어 권한이 부족하다.

판의 충돌 형상은 시각 형상과 같은 원기둥이다.

```xml
<collision>
  <geometry><cylinder radius="0.50" length="0.02"/></geometry>
</collision>
```

테두리를 넣지 않은 이유는 실패 조건을 명확하게 만들기 위해서다. 테두리가 있으면 “밖으로 나갔지만 벽에 걸린 공”을 어떻게 처리할지 추가 설계가 필요하다.

## 3.3 관성과 질량을 생략하지 않는다

움직이는 각 링크에는 양의 질량과 유효한 관성이 필요하다. 원판처럼 반지름 `r`, 질량 `m`, 높이 `h`인 원기둥은 중심축 기준으로 다음을 사용할 수 있다.

\[
I_{xx}=I_{yy}=\frac{m}{12}(3r^2+h^2), \qquad
I_{zz}=\frac{1}{2}mr^2
\]

`m=1`, `r=0.5`, `h=0.02`를 넣으면 약 `Ixx=Iyy=0.06253`, `Izz=0.125`다. 정확한 CAD 관성이 없어도 일관된 양수 관성을 제공하는 것이 0이나 임의의 극소값보다 낫다.

!!! warning "관성 원점과 시각 형상 원점"

    형상에 `<origin>`을 주고 관성에는 주지 않으면 질량 중심이 다른 곳에 놓일 수 있다. 이 예제는 plate와 roll frame의 중심을 링크 원점에 두어 계산을 단순하게 한다.

## 3.4 XML 정적 검사

Ubuntu 대상 PC뿐 아니라 현재 문서 작성 PC에서도 XML 문법은 검사할 수 있다.

```bash
python - <<'PY'
from pathlib import Path
from xml.etree import ElementTree as ET

p = Path("source/ball_on_plate_lab/ball_on_plate_lab/assets/urdf/ball_on_plate.urdf")
root = ET.parse(p).getroot()
print("robot:", root.attrib["name"])
print("links:", [x.attrib["name"] for x in root.findall("link")])
print("joints:", [x.attrib["name"] for x in root.findall("joint")])
PY
```

예상 관절 순서는 `roll_joint`, `pitch_joint`다. 이름은 뒤의 행동 매핑에서 그대로 사용하므로 오탈자를 허용하지 않는다.

## 3.5 Isaac Sim importer로 USD 변환

URDF 임포터는 Isaac Sim 기능이므로 Newton 전용 설치에서는 실행할 수 없다. 1장의 전체 환경을 활성화하고, Isaac Lab 저장소 루트에서 실행한다.

```bash
source env_isaaclab/bin/activate

URDF=/absolute/path/to/ball_on_plate_lab/source/ball_on_plate_lab/ball_on_plate_lab/assets/urdf/ball_on_plate.urdf
USD_DIR=/absolute/path/to/ball_on_plate_lab/source/ball_on_plate_lab/ball_on_plate_lab/assets/usd

./isaaclab.sh -p scripts/tools/convert_urdf.py \
  "$URDF" "$USD_DIR" \
  --fix-base \
  --joint-target-type position \
  --joint-stiffness 40 \
  --joint-damping 4 \
  --headless
```

`--fix-base`는 베이스를 세계에 고정한다. 위치 드라이브와 PD 게인은 정책의 정규화 행동을 목표 각도로 해석하기 위한 것이다. 공식 [URDF 자산 가져오기](https://isaac-sim.github.io/IsaacLab/v3.0.0-beta2/source/how-to/import_new_asset.html)와 태그의 [convert_urdf.py](https://github.com/isaac-sim/IsaacLab/blob/v3.0.0-beta2.patch1/scripts/tools/convert_urdf.py)를 기준으로 한 명령이다.

Isaac Sim 6 임포터는 출력 인자를 단일 파일이 아니라 출력 디렉터리로 사용하고, 로봇 이름에서 루트 USD 파일명을 정한다. 터미널의 `Generated USD file:` 줄을 복사해 둔다. 이 URDF에서는 보통 다음 경로다.

```text
assets/usd/ball_on_plate/ball_on_plate.usd
```

경로가 다르면 환경 변수를 지정한다.

```bash
export BALL_ON_PLATE_USD=/actual/generated/path/ball_on_plate.usd
```

루트 USD와 같은 디렉터리의 보조 레이어를 따로 떼어 복사하지 않는다. 레이어 참조가 깨질 수 있다.

## 3.6 변환 결과 검증

먼저 파일과 레이어를 확인한다.

```bash
find "$USD_DIR" -maxdepth 3 -type f -name '*.usd*' -print
```

그다음 Isaac Sim GUI로 루트 레이어를 연다.

```bash
./isaaclab.sh -s
```

Stage에서 다음을 확인한다.

1. 베이스가 고정되어 낙하하지 않는다.
2. articulation에 정확히 두 자유도가 있다.
3. 관절 이름이 `roll_joint`, `pitch_joint`다.
4. 관절 한계가 약 ±0.20944 rad다.
5. 원판 충돌 형상이 원기둥 전체를 덮는다.
6. 한 축을 움직였을 때 다른 축의 회전 중심도 같은 위치에 남는다.

GUI에서 모양만 맞는 것은 충분하지 않다. 충돌 형상 표시를 켜고 관절 드라이브 목표를 작게 바꿔 본다. 시각 메시와 충돌 형상 또는 관절 축이 틀리면 RL은 그 잘못된 물리를 정확하게 학습한다.

## 3.7 현재 저장소의 USD에 관하여

이 자료를 만든 Windows 랩탑에는 NVIDIA GPU와 Isaac Sim이 없어 임포터 결과를 생성·검증할 수 없다. 따라서 예제 저장소는 검증되지 않은 USD를 답안처럼 넣지 않고, URDF와 정확한 변환 절차를 제공한다. 대상 Ubuntu PC에서 생성한 전체 USD 디렉터리가 이 실습의 첫 번째 실행 산출물이다.

## 3.8 체크포인트

- URDF XML 파싱이 성공한다.
- 링크 세 개와 회전 관절 두 개가 보인다.
- 임포터가 루트 USD 경로를 출력한다.
- GUI에서 베이스 고정, 관절 축, 한계, 충돌 형상을 확인했다.
- 실제 루트 USD 경로를 기록하거나 `BALL_ON_PLATE_USD`를 설정했다.

[← 2장](./02-isaac-lab-mental-model.md) · [4장: Ball-on-Plate MDP 설계 →](./04-design-ball-on-plate-task.md)
