#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
CONDA_EXE="${CONDA_EXE:-/home/egde/anaconda3/bin/conda}"
ENV_NAME="${FANGZHEN_CONDA_ENV:-fangzhen-isaaclab}"
RUN_NAME="${RUN_NAME:-map_obstacle_refine_v2}"
RUN_DIR="$ROOT/incoming/rm2025_fixed/isaac/runs/rm2025_serial_isaac/$RUN_NAME"
TRAIN_SCRIPT="$ROOT/incoming/rm2025_fixed/isaac/train_isaac.py"
# Forty-eight preserves the 16-slot skill mix across all three gyro surfaces (25-degree ramp,
# 12-degree ramp and raised gap platform) while keeping the visible viewer light-weight.
NUM_ENVS="${NUM_ENVS:-48}"
DISPLAY_NUMBER="${DISPLAY_NUMBER:-:0}"
XAUTH_FILE="${XAUTH_FILE:-/run/user/$(id -u)/gdm/Xauthority}"

latest_numeric_checkpoint() {
  local directory="$1"
  local latest_name
  latest_name="$(find "$directory" -maxdepth 1 -type f -name 'model_[0-9]*.pt' \
    -printf '%f\n' 2>/dev/null | sort -V | tail -n 1)"
  [[ -n "$latest_name" ]] && printf '%s/%s\n' "$directory" "$latest_name"
}

CHECKPOINT="${CHECKPOINT:-$(latest_numeric_checkpoint "$RUN_DIR")}"
if [[ ! -f "$CHECKPOINT" ]]; then
  echo "Final play checkpoint not found: $CHECKPOINT" >&2
  exit 2
fi

eval "$("$CONDA_EXE" shell.bash hook)"
conda activate "$ENV_NAME"
launcher_dir="$ROOT/logs/linux_launch"
mkdir -p "$launcher_dir"
log_file="$launcher_dir/final_visible_play.log"
pid_file="$launcher_dir/final_visible_play.pid"
report_file="$launcher_dir/final_visible_play.json"

if [[ -f "$pid_file" ]]; then
  old_pid="$(<"$pid_file")"
  if [[ "$old_pid" =~ ^[0-9]+$ ]] && kill -0 "$old_pid" 2>/dev/null; then
    echo "Final visible play is already running as PID $old_pid."
    exit 0
  fi
fi

nohup env DISPLAY="$DISPLAY_NUMBER" XAUTHORITY="$XAUTH_FILE" \
  OMNI_KIT_ACCEPT_EULA=YES PYTHONUNBUFFERED=1 \
  "$CONDA_PREFIX/bin/python" "$TRAIN_SCRIPT" \
    --ack-serial-teacher-not-deployable \
    --device cuda:0 --num_envs "$NUM_ENVS" --steps-per-env 12 --viz kit \
    --field --skills --terrain-all --obstacle-focus --jump-curriculum \
    --cmd 1.8 --yaw-cmd 14.0 --init-std 0.27 \
    --resume "$CHECKPOINT" --eval-only --eval-steps 1 --eval-hold \
    --eval-report "$report_file" >"$log_file" 2>&1 </dev/null &

pid=$!
printf '%s\n' "$pid" >"$pid_file"
echo "Started final visible deterministic play PID $pid"
echo "Checkpoint: $CHECKPOINT"
echo "Display: $DISPLAY_NUMBER"
echo "Log: $log_file"
