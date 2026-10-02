#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
CONDA_EXE="${CONDA_EXE:-/home/egde/anaconda3/bin/conda}"
ENV_NAME="${FANGZHEN_CONDA_ENV:-fangzhen-isaaclab}"
RUNS_ROOT="$ROOT/incoming/rm2025_fixed/isaac/runs/rm2025_serial_isaac"
BASE_RUN="$RUNS_ROOT/map_allterrain_overnight_v1"
REFINE_RUN="$RUNS_ROOT/map_obstacle_refine_v2"
TARGET=26000

latest_iter() {
  [[ -d "$1" ]] || return 0
  find "$1" -maxdepth 1 -type f -name 'model_[0-9]*.pt' -printf '%f\n' 2>/dev/null |
    sed -n 's/^model_\([0-9][0-9]*\)\.pt$/\1/p' | sort -n | tail -n 1
}

base_iter="$(latest_iter "$BASE_RUN")"
base_checkpoint="$BASE_RUN/model_${base_iter}.pt"
refine_iter="$(latest_iter "$REFINE_RUN")"
refine_iter="${refine_iter:-0}"
if (( refine_iter > base_iter )); then
  base_checkpoint="$REFINE_RUN/model_${refine_iter}.pt"
fi
printf '%s obstacle refinement base %s\n' "$(date --iso-8601=seconds)" "$base_checkpoint"

eval "$("$CONDA_EXE" shell.bash hook)"
conda activate "$ENV_NAME"
smoke_log="$ROOT/logs/linux_launch/smoke_obstacle_refine.log"
env OMNI_KIT_ACCEPT_EULA=YES PYTHONUNBUFFERED=1 \
  "$CONDA_PREFIX/bin/python" "$ROOT/incoming/rm2025_fixed/isaac/train_isaac.py" \
    --ack-serial-teacher-not-deployable \
    --device cuda:0 --num_envs 32 --steps-per-env 12 --iters 2 --save_interval 1 \
    --field --skills --terrain-all --obstacle-focus --jump-curriculum \
    --curriculum-base-iter "$refine_iter" --assist-start-iter "${ASSIST_START_ITER:-20580}" \
    --assist-end-iter 24000 --cmd 1.8 --yaw-cmd 14.0 \
    --init-std 0.27 --lr 7e-5 --run smoke_obstacle_refine \
    --resume "$base_checkpoint" >"$smoke_log" 2>&1
if grep -aqE 'Traceback|(^|[^A-Za-z])(Error|Exception):' "$smoke_log"; then
  tail -n 120 "$smoke_log" >&2
  exit 1
fi
grep -aq '\[train\] finished 2 iters' "$smoke_log"
printf '%s obstacle refinement smoke passed\n' "$(date --iso-8601=seconds)"

attempt=0
while (( attempt < 10 )); do
  attempt=$((attempt + 1))
  TARGET_ITERS="$TARGET" RUN_NAME=map_obstacle_refine_v2 OBSTACLE_FOCUS=1 \
    JUMP_CURRICULUM=1 ASSIST_START_ITER="${ASSIST_START_ITER:-20580}" ASSIST_END_ITER=24000 \
    INIT_STD=0.27 RESUME_CHECKPOINT="$base_checkpoint" \
    "$ROOT/migration/linux/run_allterrain_training.sh"
  pid="$(<"$ROOT/logs/linux_launch/map_obstacle_refine_v2.pid")"
  printf '%s launched obstacle refinement PID %s attempt %d\n' \
    "$(date --iso-8601=seconds)" "$pid" "$attempt"
  while kill -0 "$pid" 2>/dev/null; do sleep 60; done
  done_iter="$(latest_iter "$REFINE_RUN")"
  done_iter="${done_iter:-0}"
  if (( done_iter >= TARGET - 1 )); then
    printf '%s obstacle refinement complete at model_%s.pt\n' \
      "$(date --iso-8601=seconds)" "$done_iter"
    exit 0
  fi
  if (( done_iter <= 0 )); then
    printf '%s obstacle refinement exited without a numeric checkpoint\n' \
      "$(date --iso-8601=seconds)" >&2
    exit 1
  fi
  base_checkpoint="$REFINE_RUN/model_${done_iter}.pt"
  printf '%s refinement early exit at %s; retrying from %s\n' \
    "$(date --iso-8601=seconds)" "$done_iter" "$base_checkpoint"
  sleep 60
done
printf '%s refinement supervisor exhausted restart attempts\n' "$(date --iso-8601=seconds)" >&2
exit 1
