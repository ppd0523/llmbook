# 1. 시스템 요구 사항과 설치

이 장의 목표는 “설치 명령이 끝났다”가 아니다. **드라이버, Python, Isaac Sim, Isaac Lab, PyTorch가 의도한 한 묶음인지 증명**하는 것이다. 이후 오류의 절반은 이 표를 지키면 예방된다.

## 1.1 실행 PC 점검

Isaac Sim 6.0.1의 x86_64 최소 사양은 Ubuntu 22.04/24.04, RAM 32 GB, RTX 4080, VRAM 16 GB다. 권장 RAM은 64 GB다. Linux 검증 드라이버는 595.58.03이다. 정확한 표는 [Isaac Sim 6.0.1 요구 사항](https://docs.isaacsim.omniverse.nvidia.com/6.0.1/installation/requirements.html)을 기준으로 한다.

```bash
uname -m
lsb_release -ds
free -h
lspci | grep -i nvidia
df -h "$HOME"
```

통과 조건은 다음과 같다.

- `x86_64`
- `Ubuntu 24.04 LTS`
- NVIDIA RTX GPU가 보임
- RAM 32 GB 이상
- 최소 100 GB의 작업 여유 공간. 공식 최소 저장 공간은 50 GB지만 wheel cache, USD, 로그를 고려해 더 잡는다.

## 1.2 NVIDIA 드라이버

Ubuntu 기본 nouveau 드라이버나 임의의 오래된 프로덕션 드라이버로 시작하지 않는다. Isaac Sim 요구 사항의 검증 버전인 **595.58.03** 또는 해당 페이지가 명시한 더 새로운 지원 프로덕션 계열을 사용한다.

드라이버 설치는 NVIDIA의 [Ubuntu 드라이버 설치 가이드](https://docs.nvidia.com/datacenter/tesla/driver-installation-guide/ubuntu.html)에 따라 NVIDIA 네트워크 저장소를 등록한 뒤 open kernel module 패키지를 설치한다. 저장소의 패키지 이름은 시점에 따라 달라질 수 있으므로, 아래처럼 595 계열 후보를 먼저 확인한다.

```bash
sudo apt update
sudo apt install -y linux-headers-"$(uname -r)" build-essential
apt-cache search '^nvidia.*595' | sort
```

목록에 표시된 595 open 패키지를 설치하고 재부팅한다. 패키지 이름을 추측해 다른 계열을 설치하지 않는다. NVIDIA 저장소가 제공하는 메타패키지가 `nvidia-open`뿐이라면 설치 후 버전을 반드시 확인한다.

```bash
sudo apt install -y nvidia-open
sudo reboot
```

재부팅 뒤 다음 세 줄이 모두 성공해야 한다.

```bash
nvidia-smi
cat /proc/driver/nvidia/version
lsmod | grep '^nvidia'
```

`nvidia-smi`의 Driver Version이 `595.58.03`인지 기록한다. 더 새 버전을 선택했다면 Isaac Sim 요구 사항 페이지가 그 계열을 지원한다고 명시하는지도 기록한다.

!!! danger "드라이버와 CUDA Toolkit을 혼동하지 않는다"

    PyTorch wheel은 필요한 CUDA 런타임을 포함한다. 이 실습을 위해 시스템 전체 CUDA Toolkit을 먼저 설치할 필요가 없다. `nvidia-smi`가 보여 주는 “CUDA Version”은 드라이버가 지원하는 최대 API 수준이지, 현재 가상 환경의 PyTorch CUDA 런타임 버전이 아니다.

## 1.3 기본 도구와 uv

```bash
sudo apt update
sudo apt install -y git git-lfs curl build-essential
git lfs install
curl -LsSf https://astral.sh/uv/install.sh | sh
source "$HOME/.local/bin/env"
uv --version
```

uv 설치 명령은 [uv 공식 설치 문서](https://docs.astral.sh/uv/getting-started/installation/)에서 갱신 여부를 확인한다.

## 1.4 Isaac Lab 태그와 Python 환경

작업 디렉터리 예시는 `$HOME/work/isaac`이다.

```bash
mkdir -p "$HOME/work/isaac"
cd "$HOME/work/isaac"
git clone https://github.com/isaac-sim/IsaacLab.git \
  --branch v3.0.0-beta2.patch1
cd IsaacLab
git rev-parse --short HEAD
```

출력은 `ffff603`이어야 한다.

```bash
uv venv --python 3.12 --seed env_isaaclab
source env_isaaclab/bin/activate
python --version
uv pip install --upgrade pip
```

Isaac Sim 6.x와 Python 3.12의 결합은 [kit-less 설치 문서](https://isaac-sim.github.io/IsaacLab/v3.0.0-beta2/source/setup/installation/kitless_installation.html)에 명시되어 있다.

## 1.5 Isaac Sim 6.0.1과 Isaac Lab 설치

URDF importer와 PhysX 비교를 위해 같은 환경에 Isaac Sim을 설치한다.

```bash
uv pip install "isaacsim[all,extscache]==6.0.1.0" \
  --extra-index-url https://pypi.nvidia.com \
  --index-strategy unsafe-best-match \
  --prerelease=allow
```

이 책의 PyTorch 조합을 먼저 고정한다. 이 순서는 해당 버전 빠른 시작 안내의 전체 설치 순서와 같다.

```bash
uv pip install --upgrade \
  torch==2.11.0 torchvision==0.26.0 \
  --index-url https://download.pytorch.org/whl/cu128
```

이제 Newton, RSL-RL, Newton visualizer를 포함한 Isaac Lab 소스 패키지를 설치한다.

```bash
./isaaclab.sh -i 'newton,rl[rsl-rl],visualizer[newton]'
```

Isaac Lab의 [로컬 설치 개요](https://isaac-sim.github.io/IsaacLab/v3.0.0-beta2/source/setup/installation/index.html)는 Newton 전용 설치와 Isaac Sim 포함 설치의 기능 차이를 설명한다. 여기서는 한 번의 URDF 변환과 백엔드 비교가 필요하므로 전체 환경을 만들되, 반복 학습은 Newton으로 실행한다.

## 1.6 버전 감사

```bash
python - <<'PY'
import importlib.metadata as m
import torch

names = ["isaacsim", "isaaclab", "torch", "torchvision", "rsl-rl-lib"]
for name in names:
    try:
        print(f"{name:12s} {m.version(name)}")
    except m.PackageNotFoundError:
        print(f"{name:12s} NOT INSTALLED")
print("torch CUDA runtime:", torch.version.cuda)
print("CUDA available:", torch.cuda.is_available())
if torch.cuda.is_available():
    print("GPU:", torch.cuda.get_device_name(0))
PY
```

예상 핵심 값은 Python 3.12, Isaac Sim 6.0.1 계열, PyTorch 2.11.0, CUDA 런타임 12.8, `CUDA available: True`다. `isaaclab` 배포판의 표시 버전이 태그 이름과 다를 수 있으므로 Git 커밋 `ffff603`도 함께 기록한다.

## 1.7 두 백엔드 간이 실행 시험

먼저 Isaac Sim이 필요 없는 Newton 경로다.

```bash
./isaaclab.sh train --rl_library rsl_rl \
  --task Isaac-Cartpole-Direct-v0 \
  --num_envs 16 --max_iterations 10 \
  physics=newton_mjwarp --visualizer newton
```

다음은 Isaac Sim이 필요한 PhysX 경로다.

```bash
./isaaclab.sh train --rl_library rsl_rl \
  --task Isaac-Cartpole-Direct-v0 \
  --num_envs 16 --max_iterations 10 \
  physics=physx
```

첫 Isaac Sim 실행에서는 NVIDIA Omniverse EULA 동의와 확장 기능 캐시 준비 때문에 시간이 걸릴 수 있다. 공식 [빠른 시작 상세 안내](https://isaac-sim.github.io/IsaacLab/v3.0.0-beta2/source/setup/quickstart_details.html)의 `physics=` 선택 방식과 같은 명령이다.

## 1.8 중단 기준

다음 중 하나라도 발생하면 다음 장으로 가지 않는다.

| 증상 | 먼저 확인할 것 |
|---|---|
| `nvidia-smi` 실패 | 드라이버 설치와 재부팅 |
| `torch.cuda.is_available()`가 False | 가상 환경, cu128 wheel, 드라이버 |
| Python 3.11 또는 3.13 | 환경 삭제 대신 올바른 3.12 환경을 새로 생성 |
| `ModuleNotFoundError: isaaclab_newton` | 선택 설치 문자열과 활성화된 환경 |
| PhysX만 실패 | Isaac Sim `6.0.1.0`, EULA, 확장 기능 캐시 |
| Newton만 실패 | `newton` extra와 GPU 지원 여부 |

설치 로그와 버전 감사 출력을 파일로 보관하면 이후 질문할 때 훨씬 빠르게 원인을 좁힐 수 있다.

[← 책 소개](./index.md) · [2장: Isaac Lab의 정신 모델 →](./02-isaac-lab-mental-model.md)
