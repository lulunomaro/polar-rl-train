#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
CONDA_EXE="${CONDA_EXE:-/home/egde/anaconda3/bin/conda}"
ENV_NAME="${FANGZHEN_CONDA_ENV:-fangzhen-isaaclab}"
RUNS_ROOT="$ROOT/incoming/rm2025_fixed/isaac/runs/rm2025_serial_isaac"
SKILLS_RUN="$RUNS_ROOT/map_skills_v1"
TERRAIN_RUN="$RUNS_ROOT/map_allterrain_overnight_v1"
SUP_LOG="$ROOT/logs/linux_launch/overnight_supervisor.log"

latest_iter() {
  local directory="$1"
  find "$directory" -maxdepth 1 -type f -name 'model_[0-9]*.pt' -printf '%f\n' 2>/dev/null |
    sed -n 's/^model_\([0-9][0-9]*\)\.pt$/\1/p' | sort -n | tail -n 1
}

skills_pid_file="$ROOT/logs/linux_launch/map_skills_v1.pid"
if [[ -f "$skills_pid_file" ]]; then
  skills_pid="$(<"$skills_pid_file")"
  while kill -0 "$skills_pid" 2>/dev/null; do
    printf '%s waiting for stage-2 PID %s\n' "$(date --iso-8601=seconds)" "$skills_pid"
    sleep 30
  done
fi

base_iter="$(latest_iter "$SKILLS_RUN")"
base_checkpoint="$SKILLS_RUN/model_${base_iter}.pt"
terrain_iter="$(latest_iter "$TERRAIN_RUN")"
terrain_iter="${terrain_iter:-0}"
if (( terrain_iter > base_iter )); then
  base_checkpoint="$TERRAIN_RUN/model_${terrain_iter}.pt"
fi
printf '%s stage-2 stopped; latest checkpoint %s\n' "$(date --iso-8601=seconds)" "$base_checkpoint"

eval "$("$CONDA_EXE" shell.bash hook)"
conda activate "$ENV_NAME"
smoke_log="$ROOT/logs/linux_launch/smoke_allterrain.log"
env OMNI_KIT_ACCEPT_EULA=YES PYTHONUNBUFFERED=1 \
  "$CONDA_PREFIX/bin/python" "$ROOT/incoming/rm2025_fixed/isaac/train_isaac.py" \
    --ack-serial-teacher-not-deployable \
    --device cuda:0 --num_envs 32 --steps-per-env 12 --iters 2 --save_interval 1 \
    --field --skills --terrain-all --cmd 1.8 --yaw-cmd 14.0 --init-std 0.27 --lr 7e-5 \
    --run smoke_allterrain --resume "$base_checkpoint" >"$smoke_log" 2>&1
printf '%s all-terrain smoke passed\n' "$(date --iso-8601=seconds)"

attempt=0
while (( attempt < 10 )); do
  attempt=$((attempt + 1))
  TARGET_ITERS=20000 RUN_NAME=map_allterrain_overnight_v1 \
    RESUME_CHECKPOINT="${base_checkpoint}" "$ROOT/migration/linux/run_allterrain_training.sh"
  terrain_pid_file="$ROOT/logs/linux_launch/map_allterrain_overnight_v1.pid"
  terrain_pid="$(<"$terrain_pid_file")"
  printf '%s launched all-terrain PID %s attempt %d\n' \
    "$(date --iso-8601=seconds)" "$terrain_pid" "$attempt"
  while kill -0 "$terrain_pid" 2>/dev/null; do sleep 60; done
  done_iter="$(latest_iter "$TERRAIN_RUN")"
  done_iter="${done_iter:-0}"
  if (( done_iter >= 19999 )); then
    printf '%s all-terrain target complete at model_%s.pt\n' \
      "$(date --iso-8601=seconds)" "$done_iter"
    exit 0
  fi
  base_checkpoint="$TERRAIN_RUN/model_${done_iter}.pt"
  printf '%s early exit at %s; retrying from %s\n' \
    "$(date --iso-8601=seconds)" "$done_iter" "$base_checkpoint"
  sleep 60
done
printf '%s supervisor exhausted restart attempts\n' "$(date --iso-8601=seconds)" >&2
exit 1
