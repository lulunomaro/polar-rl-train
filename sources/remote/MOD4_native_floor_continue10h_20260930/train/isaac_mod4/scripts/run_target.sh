#!/usr/bin/env bash
# Launch MOD4 Isaac Lab training detached on the target machine (10.24.4.210).
#
#   bash train/isaac_mod4/scripts/run_target.sh [num_envs] [iterations] [run_name]
#
# Detaches with setsid and redirects every inherited descriptor so the ssh session that
# started it can close immediately while the job keeps running.
set -euo pipefail

ENVS="${1:-4096}"
ITERS="${2:-3000}"
NAME="${3:-mod4_isaac_v1}"
PY="${PY:-/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python}"
REPO="${REPO:-/home/egde/fangzhen_linux}"
LOG="${LOG:-/tmp/${NAME}.log}"

export OMNI_KIT_ACCEPT_EULA=YES
cd "$REPO"
setsid nohup "$PY" train/isaac_mod4/scripts/train.py \
  --num_envs "$ENVS" --max_iterations "$ITERS" --headless --device cuda:0 \
  --run_name "$NAME" > "$LOG" 2>&1 < /dev/null &

echo "launched name=$NAME envs=$ENVS iterations=$ITERS log=$LOG pid=$!"
