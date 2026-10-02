#!/usr/bin/env bash
# Install the production closed-chain trainer.  This environment is deliberately
# separate from Isaac Sim: MuJoCo-Warp can enforce the similar-linkage equality
# constraints that the serial PhysX teacher removes.
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
MJLAB_ROOT="$ROOT/third_party/rc_mjlab"
ENV_NAME="${FANGZHEN_MJLAB_CONDA_ENV:-fangzhen-mjlab-bootstrap}"
CONDA_EXE="${CONDA_EXE:-/home/egde/anaconda3/bin/conda}"

[[ -x "$CONDA_EXE" ]] || { echo "conda not found: $CONDA_EXE" >&2; exit 2; }
[[ -f "$MJLAB_ROOT/pyproject.toml" ]] || { echo "mjlab checkout missing: $MJLAB_ROOT" >&2; exit 2; }
[[ -f "$ROOT/train/rmvehicle/pyproject.toml" ]] || { echo "rmvehicle package missing" >&2; exit 2; }

eval "$("$CONDA_EXE" shell.bash hook)"
if ! conda env list | awk '{print $1}' | grep -Fxq "$ENV_NAME"; then
  conda create -y -n "$ENV_NAME" python=3.12 pip
fi
conda activate "$ENV_NAME"
python -m pip install --upgrade pip uv
UV="$CONDA_PREFIX/bin/uv"

cd "$MJLAB_ROOT"
# The checked-in lock/config selects CUDA 12.8 torch and MuJoCo-Warp's MuJoCo
# index.  Keeping this venv under the checkout makes the runtime location stable.
if ! "$UV" sync --extra cu128 --no-install-project; then
  echo "The checked-in MuJoCo nightly may have expired; refreshing only MuJoCo pins and retrying."
  "$UV" lock --upgrade-package mujoco --upgrade-package mujoco-warp
  "$UV" sync --extra cu128 --no-install-project
fi
"$UV" pip install --python "$MJLAB_ROOT/.venv/bin/python" -e "$ROOT/train/rmvehicle"

"$MJLAB_ROOT/.venv/bin/python" - <<'PY'
import torch
import rmvehicle
from mjlab.tasks.registry import list_tasks

assert "RMVehicle-CC-Field-v0" in list_tasks()
print("torch", torch.__version__)
print("cuda_available", torch.cuda.is_available())
if not torch.cuda.is_available():
    raise SystemExit("CUDA is unavailable in the production mjlab environment")
print("gpu", torch.cuda.get_device_name(0))
print("production_task", "RMVehicle-CC-Field-v0")
PY

echo "Production closed-chain environment ready: $MJLAB_ROOT/.venv"
