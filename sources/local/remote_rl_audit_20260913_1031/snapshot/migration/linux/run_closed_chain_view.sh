#!/usr/bin/env bash
# Visible inference of the newest deployable closed-chain checkpoint.
# This is the real RMVehicle-CC-Field-v0 plant, not the serial Isaac teacher.
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PY="$ROOT/third_party/rc_mjlab/.venv/bin/python"
TRAIN_ROOT="$ROOT/train"
EXPERIMENT="${EXPERIMENT:-rm_cc_dm3519_closedchain_v1}"
NUM_ENVS="${NUM_ENVS:-8}"
DISPLAY_NUMBER="${DISPLAY_NUMBER:-:0}"
XAUTH_FILE="${XAUTH_FILE:-/run/user/$(id -u)/gdm/Xauthority}"

latest_numeric_checkpoint() {
  local root="$1" path base n best_n=-1 best_path=""
  while IFS= read -r path; do
    base="$(basename "$path")"
    n="${base#model_}"; n="${n%.pt}"
    if [[ "$n" =~ ^[0-9]+$ ]] && (( n > best_n )); then
      best_n="$n"; best_path="$path"
    fi
  done < <(find "$root" -type f -name 'model_[0-9]*.pt' -print 2>/dev/null)
  printf '%s\n' "$best_path"
}

CHECKPOINT="${CHECKPOINT:-$(latest_numeric_checkpoint "$TRAIN_ROOT/logs/rsl_rl/$EXPERIMENT")}" 
[[ -x "$PY" ]] || { echo "run migration/linux/setup_mjlab.sh first" >&2; exit 2; }
[[ -f "$CHECKPOINT" ]] || { echo "closed-chain checkpoint missing: $CHECKPOINT" >&2; exit 2; }

mkdir -p "$ROOT/logs/linux_launch"
log="$ROOT/logs/linux_launch/closed_chain_visible.log"
pidf="$ROOT/logs/linux_launch/closed_chain_visible.pid"
if [[ -f "$pidf" ]]; then
  old="$(<"$pidf")"
  if [[ "$old" =~ ^[0-9]+$ ]] && kill -0 "$old" 2>/dev/null; then
    echo "closed-chain viewer already running: $old"
    exit 0
  fi
fi

cd "$TRAIN_ROOT"
nohup env \
  DISPLAY="$DISPLAY_NUMBER" XAUTHORITY="$XAUTH_FILE" \
  XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}" \
  MUJOCO_GL=glfw CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0}" \
  PYTHONUNBUFFERED=1 RM_MOTOR=dm8009 \
  RM_WHEEL_SCALE="${RM_WHEEL_SCALE:-55.0}" \
  RM_WZ_MAX="${RM_WZ_MAX:-14.0}" RM_WZ0="${RM_WZ0:-6.0}" \
  RM_LV_STD="${RM_LV_STD:-1.0}" RM_AV_STD="${RM_AV_STD:-2.5}" \
  RM_FLAT_PROP="${RM_FLAT_PROP:-0.25}" RM_SKILL_SPLIT=1 \
  RM_SKILL_GYRO_FRAC="${RM_SKILL_GYRO_FRAC:-0.25}" \
  RM_SKILL_WZ_LOCO="${RM_SKILL_WZ_LOCO:-2.0}" \
  "$PY" -m mjlab.scripts.play RMVehicle-CC-Field-v0 \
    --checkpoint-file "$CHECKPOINT" --num-envs "$NUM_ENVS" \
    --device cuda:0 --viewer native --log-root "$TRAIN_ROOT/logs/rsl_rl" \
    >"$log" 2>&1 </dev/null &

pid=$!
printf '%s\n' "$pid" >"$pidf"
echo "started closed-chain MuJoCo viewer PID $pid"
echo "checkpoint: $CHECKPOINT"
echo "viewer envs: $NUM_ENVS (period/comma switch; A shows all)"
