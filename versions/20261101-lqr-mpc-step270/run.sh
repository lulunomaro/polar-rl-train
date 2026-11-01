#!/bin/bash
set -euo pipefail
TASK='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_MUJOCO_LQR_MPC_STEP270_20261101'
export CUDA_VISIBLE_DEVICES=GPU-16828f91-2b45-b646-8dc0-9481138e2842
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export MUJOCO_GL=egl
export PYTHONDONTWRITEBYTECODE=1
cd "$TASK"
exec '/home/lc01/Zonglin Li/zonglin2/run-python.sh' "$@"
