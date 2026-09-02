# ball_on_plate_lab

Reference external project for the Isaac Lab Ball-on-Plate tutorial. Read the parent learning material before running it.

## Prepare the asset

From the pinned Isaac Lab repository, with the full Isaac Sim environment active:

```bash
./isaaclab.sh -p scripts/tools/convert_urdf.py \
  /absolute/path/to/ball_on_plate.urdf \
  /absolute/path/to/ball_on_plate_lab/source/ball_on_plate_lab/ball_on_plate_lab/assets/usd \
  --fix-base --joint-target-type position \
  --joint-stiffness 40 --joint-damping 4 --headless
```

The Isaac Sim 6 importer chooses the USD file name from the URDF robot name. The default code expects:

```text
source/ball_on_plate_lab/ball_on_plate_lab/assets/usd/ball_on_plate/ball_on_plate.usd
```

If the importer prints a different path, set `BALL_ON_PLATE_USD` to that absolute file path.

## Install and register

```bash
uv pip install -e source/ball_on_plate_lab
python scripts/list_envs.py
```

## Train

Run this from the pinned Isaac Lab repository root. The external callback imports this package before task lookup.

```bash
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py \
  --task BallOnPlate-Direct-v0 \
  --external_callback ball_on_plate_lab.tasks.register \
  --headless --num_envs 2048 \
  physics=newton_mjwarp
```

Use `BallOnPlate-Manager-v0` for the Manager-based version. Use the `Tracking` task IDs for the moving-target capstone.

This repository was created on a Windows laptop without an NVIDIA GPU. Its Python syntax and URDF XML are checked locally; simulation and learning must be validated on the target Ubuntu/NVIDIA system.
