#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ISAACLAB="$ROOT/third_party/IsaacLab-3.0.0-beta2.patch1"
ENV_NAME="${FANGZHEN_CONDA_ENV:-fangzhen-isaaclab}"
USD_ENV_NAME="${FANGZHEN_USD_CONDA_ENV:-fangzhen-usd}"
CONDA_EXE="${CONDA_EXE:-/home/egde/anaconda3/bin/conda}"

if [[ ! -x "$CONDA_EXE" ]]; then
  echo "conda not found: $CONDA_EXE" >&2
  exit 2
fi
if [[ ! -d "$ISAACLAB/source/isaaclab" ]]; then
  echo "Isaac Lab source is missing: $ISAACLAB" >&2
  exit 2
fi

eval "$("$CONDA_EXE" shell.bash hook)"
if ! conda env list | awk '{print $1}' | grep -Fxq "$ENV_NAME"; then
  conda create -y -n "$ENV_NAME" python=3.12 pip
fi
conda activate "$ENV_NAME"

python -m pip install --upgrade pip uv
uv pip install \
  "isaacsim[all,extscache]==6.0.1.0" \
  --extra-index-url https://pypi.nvidia.com \
  --index-strategy unsafe-best-match \
  --prerelease=allow
uv pip install --upgrade \
  torch==2.10.0 torchvision==0.25.0 \
  --index-url https://download.pytorch.org/whl/cu128

# Install only the Isaac Lab packages needed by the current PhysX+rsl_rl task.
uv pip install -e "$ISAACLAB/source/isaaclab"
uv pip install -e "$ISAACLAB/source/isaaclab_assets"
uv pip install -e "$ISAACLAB/source/isaaclab_tasks"
uv pip install -e "$ISAACLAB/source/isaaclab_rl[rsl-rl]"
uv pip install -e "$ISAACLAB/source/isaaclab_visualizers[kit]"

# Keep the remaining project runners usable on Linux too.
uv pip install -r "$ROOT/incoming/rm2025_fixed/requirements-training.txt"

python - <<'PY'
import sys
import torch
print("python", sys.version.split()[0])
print("torch", torch.__version__)
print("cuda_available", torch.cuda.is_available())
if torch.cuda.is_available():
    print("gpu", torch.cuda.get_device_name(0))
else:
    raise SystemExit("CUDA is unavailable. The NVIDIA driver may need an upgrade before training.")
PY

echo "Environment ready: $ENV_NAME"

# usd-core 26.8 conflicts with the version selected by Isaac Sim. Keep static USD
# auditing in a small, separate environment instead of mutating the trainer.
conda deactivate
if ! conda env list | awk '{print $1}' | grep -Fxq "$USD_ENV_NAME"; then
  conda create -y -n "$USD_ENV_NAME" python=3.12 pip
fi
conda run -n "$USD_ENV_NAME" python -m pip install \
  -r "$ROOT/incoming/rm2025_fixed/requirements-usd.txt"
echo "Static USD environment ready: $USD_ENV_NAME"
