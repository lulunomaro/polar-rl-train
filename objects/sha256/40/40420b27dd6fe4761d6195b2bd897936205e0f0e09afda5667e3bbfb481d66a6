#!/usr/bin/env bash
# Lightweight, visible Isaac Lab view of the latest serial teacher checkpoint.
# This is a viewer only; the deployable policy trains in RMVehicle-CC-Field-v0.
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
CONDA_EXE="${CONDA_EXE:-/home/egde/anaconda3/bin/conda}"
ENV_NAME="${FANGZHEN_CONDA_ENV:-fangzhen-isaaclab}"
RUN_NAME="${RUN_NAME:-spin_gate_v2}"
RUN_DIR="$ROOT/incoming/rm2025_fixed/isaac/runs/rm2025_serial_isaac/$RUN_NAME"
TRAIN="$ROOT/incoming/rm2025_fixed/isaac/train_isaac.py"
# One rendered environment is enough for human inspection.  Keeping dozens of
# invisible copies alive in a viewer only steals throughput from the deployable
# headless trainer sharing the 4090.
NUM_ENVS="${NUM_ENVS:-1}"
DISPLAY_NUMBER="${DISPLAY_NUMBER:-:0}"
XAUTH_FILE="${XAUTH_FILE:-/run/user/$(id -u)/gdm/Xauthority}"

latest="$(find "$RUN_DIR" -maxdepth 1 -type f -name 'model_[0-9]*.pt' -printf '%f\n' \
  2>/dev/null | sort -V | tail -n 1)"
CHECKPOINT="${CHECKPOINT:-$RUN_DIR/$latest}"
[[ -f "$CHECKPOINT" ]] || { echo "teacher checkpoint missing: $CHECKPOINT" >&2; exit 2; }

eval "$("$CONDA_EXE" shell.bash hook)"
conda activate "$ENV_NAME"
mkdir -p "$ROOT/logs/linux_launch"
log="$ROOT/logs/linux_launch/teacher_visible.log"
pidf="$ROOT/logs/linux_launch/teacher_visible.pid"

if [[ -f "$pidf" ]]; then
  old="$(<"$pidf")"
  if [[ "$old" =~ ^[0-9]+$ ]] && kill -0 "$old" 2>/dev/null; then
    echo "teacher viewer already running: $old"
    exit 0
  fi
fi

nohup env DISPLAY="$DISPLAY_NUMBER" XAUTHORITY="$XAUTH_FILE" \
  OMNI_KIT_ACCEPT_EULA=YES PYTHONUNBUFFERED=1 \
  "$CONDA_PREFIX/bin/python" "$TRAIN" \
    --ack-serial-teacher-not-deployable \
    --device cuda:0 --num_envs "$NUM_ENVS" --steps-per-env 12 --viz kit \
    --field --skills --terrain-all --obstacle-focus --focus-profile gyro \
    --jump-curriculum --cmd 1.8 --yaw-cmd 12.6 --yaw-ramp-iters 1500 \
    --wheel-curve --spin-pure --spin-pivot wheel --spin-band 3.0 \
    --spin-weight 0.5 --spin-rate-weight 1.5 --spin-product-weight 4.0 \
    --gyro-posture-relax 0.5 --gyro-stance-weight 1.0 \
    --resume "$CHECKPOINT" --eval-only --eval-steps 1 --eval-hold \
    --eval-report "$ROOT/logs/linux_launch/teacher_visible.json" \
    >"$log" 2>&1 </dev/null &

pid=$!
printf '%s\n' "$pid" >"$pidf"
echo "started Isaac Lab teacher viewer PID $pid"
echo "checkpoint: $CHECKPOINT"
echo "THIS VIEW IS NOT THE DEPLOYABLE CLOSED-CHAIN POLICY"
