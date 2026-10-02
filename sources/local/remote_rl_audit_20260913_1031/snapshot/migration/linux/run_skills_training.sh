#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ENV_NAME="${FANGZHEN_CONDA_ENV:-fangzhen-isaaclab}"
CONDA_EXE="${CONDA_EXE:-/home/egde/anaconda3/bin/conda}"
TARGET_ITERS="${TARGET_ITERS:-8000}"
NUM_ENVS="${NUM_ENVS:-2048}"
STEPS_PER_ENV="${STEPS_PER_ENV:-12}"
RUN_NAME="${RUN_NAME:-map_skills_level_turn_gyro_stairs_v1}"
EXP_NAME="rm2025_serial_isaac"
RUNS_ROOT="$ROOT/incoming/rm2025_fixed/isaac/runs/$EXP_NAME"
BASE_RUN="$RUNS_ROOT/map_fixed_v1_linux_balanced"
SKILLS_RUN="$RUNS_ROOT/$RUN_NAME"
TRAIN_SCRIPT="$ROOT/incoming/rm2025_fixed/isaac/train_isaac.py"
DISPLAY_NUMBER="${DISPLAY_NUMBER:-:0}"
XAUTH_FILE="${XAUTH_FILE:-/run/user/$(id -u)/gdm/Xauthority}"

latest_numeric_checkpoint() {
  local directory="$1"
  local latest_name
  latest_name="$(find "$directory" -maxdepth 1 -type f -name 'model_[0-9]*.pt' -printf '%f\n' 2>/dev/null | sort -V | tail -n 1)"
  [[ -n "$latest_name" ]] && printf '%s/%s\n' "$directory" "$latest_name"
}

if [[ -n "${RESUME_CHECKPOINT:-}" ]]; then
  CHECKPOINT="$RESUME_CHECKPOINT"
elif [[ -d "$SKILLS_RUN" ]] && CHECKPOINT="$(latest_numeric_checkpoint "$SKILLS_RUN")" && [[ -n "$CHECKPOINT" ]]; then
  :
else
  CHECKPOINT="$(latest_numeric_checkpoint "$BASE_RUN")"
fi

if [[ ! -f "$CHECKPOINT" ]]; then
  echo "No stage-1/stage-2 checkpoint found: $CHECKPOINT" >&2
  exit 2
fi

base_name="$(basename "$CHECKPOINT")"
checkpoint_iter="${base_name#model_}"
checkpoint_iter="${checkpoint_iter%.pt}"
if [[ ! "$checkpoint_iter" =~ ^[0-9]+$ ]]; then
  echo "Checkpoint must use model_<iteration>.pt naming: $CHECKPOINT" >&2
  exit 2
fi
remaining=$((TARGET_ITERS - checkpoint_iter))
if (( remaining <= 0 )); then
  echo "Checkpoint iteration $checkpoint_iter already reached target $TARGET_ITERS."
  exit 0
fi

eval "$("$CONDA_EXE" shell.bash hook)"
conda activate "$ENV_NAME"

launcher_dir="$ROOT/logs/linux_launch"
mkdir -p "$launcher_dir"
log_file="$launcher_dir/$RUN_NAME.log"
pid_file="$launcher_dir/$RUN_NAME.pid"

echo "Stage-2 warm start: $CHECKPOINT (iteration $checkpoint_iter)"
echo "Objectives: level walk/run + turning + bidirectional gyro + jump/stairs"
echo "Running $remaining iterations toward $TARGET_ITERS"
echo "Batch: $NUM_ENVS environments x $STEPS_PER_ENV rollout steps"
echo "GUI display: $DISPLAY_NUMBER"
echo "Log: $log_file"

nohup env \
  DISPLAY="$DISPLAY_NUMBER" \
  XAUTHORITY="$XAUTH_FILE" \
  OMNI_KIT_ACCEPT_EULA=YES \
  PYTHONUNBUFFERED=1 \
  "$CONDA_PREFIX/bin/python" "$TRAIN_SCRIPT" \
    --ack-serial-teacher-not-deployable \
    --device cuda:0 \
    --num_envs "$NUM_ENVS" \
    --steps-per-env "$STEPS_PER_ENV" \
    --iters "$remaining" \
    --save_interval 10 \
    --viz kit \
    --field \
    --skills \
    --cmd 1.8 \
    --yaw-cmd 14.0 \
    --init-std 0.55 \
    --lr 1e-4 \
    --run "$RUN_NAME" \
    --resume "$CHECKPOINT" \
    >"$log_file" 2>&1 </dev/null &

pid=$!
printf '%s\n' "$pid" >"$pid_file"
printf '%s\n' "$pid_file" >"$launcher_dir/latest_pid_file"
printf '%s\n' "$log_file" >"$launcher_dir/latest_log_file"
echo "Started PID $pid"
