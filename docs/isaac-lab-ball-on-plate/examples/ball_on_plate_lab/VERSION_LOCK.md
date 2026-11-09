# 버전 고정

이 예제는 다음 재현 가능한 스택을 대상으로 한다.

| 구성 요소 | 버전 |
|---|---|
| Ubuntu | 24.04 LTS x86_64 |
| NVIDIA driver | 595.58.03 |
| Python | 3.12 |
| Isaac Sim | 6.0.1 (`isaacsim==6.0.1.0`) |
| Isaac Lab | `v3.0.0-beta2.patch1` (`ffff603`) |
| PyTorch | 2.11.0, CUDA 12.8 wheel |
| torchvision | 0.26.0, CUDA 12.8 wheel |
| RSL-RL | 5.0.1 또는 고정한 Isaac Lab 태그가 설치하는 버전 |

이 프로젝트를 Isaac Lab 2.x 예제나 버전을 고정하지 않은 `main`/`develop` checkout과 섞지 않는다.
