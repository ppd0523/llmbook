# Version lock

This example targets the following reproducible stack.

| Component | Version |
|---|---|
| Ubuntu | 24.04 LTS x86_64 |
| NVIDIA driver | 595.58.03 |
| Python | 3.12 |
| Isaac Sim | 6.0.1 (`isaacsim==6.0.1.0`) |
| Isaac Lab | `v3.0.0-beta2.patch1` (`ffff603`) |
| PyTorch | 2.11.0, CUDA 12.8 wheel |
| torchvision | 0.26.0, CUDA 12.8 wheel |
| RSL-RL | 5.0.1 or the version installed by the pinned Isaac Lab tag |

Do not combine this project with Isaac Lab 2.x examples or an unpinned `main`/`develop` checkout.
