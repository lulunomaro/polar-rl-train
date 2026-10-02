#!/usr/bin/env bash
# Stage-3a: true 小陀螺 (pure in-place yaw) + wheel torque-speed envelope.
# Both features are opt-in flags in train_isaac.py, so this script is the only thing that
# changes behaviour; the running map_obstacle_refine_v2 pipeline is untouched.
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ENV_NAME="${FANGZHEN_CONDA_ENV:-fangzhen-isaaclab}"
CONDA_EXE="${CONDA_EXE:-/home/egde/anaconda3/bin/conda}"
RUN_NAME="${RUN_NAME:-spin_pure_v2}"
TARGET_ITERS="${TARGET_ITERS:-36000}"
NUM_ENVS="${NUM_ENVS:-2048}"
STEPS_PER_ENV="${STEPS_PER_ENV:-12}"
# DM3519 + 15.8 wheel envelope now lives in import_contract.json, so by default we pass
# no wheel numbers on the command line at all.  Export WHEEL_STALL / WHEEL_NOLOAD /
# WHEEL_KNEE only to override the contract (e.g. after a bench measurement).
WHEEL_STALL="${WHEEL_STALL:-}"
WHEEL_NOLOAD="${WHEEL_NOLOAD:-}"
WHEEL_KNEE="${WHEEL_KNEE:-}"
YAW_CMD="${YAW_CMD:-12.6}"
# 12.6 rad/s = 2.0 rev/s, which is what a RoboMaster 小陀螺 needs.  The DM3519 + 15.8 drivetrain
# tops out at ~14.7 rad/s (2.34 rev/s), so the command is reachable but has little margin above it.
YAW_RAMP="${YAW_RAMP:-1500}"
SPIN_BAND="${SPIN_BAND:-3.0}"
GYRO_STANCE_W="${GYRO_STANCE_W:-1.0}"
# spin_pure_v1/v2 both stalled at spin_rate_ratio ~0.03 because the reward let PPO farm the
# zero-translation term by standing still: spin_hold(3.0) plus upright/level/height outweighed
# every yaw term combined.  These three knobs fix that trap; set SPIN_PRODUCT=0 and
# GYRO_RELAX=0 to go back to the v2 reward shape.
SPIN_HOLD_W="${SPIN_HOLD_W:-0.5}"
SPIN_PRODUCT="${SPIN_PRODUCT:-4.0}"
GYRO_RELAX="${GYRO_RELAX:-0.5}"
EXP_NAME="rm2025_serial_isaac"
BASE_RUN="${BASE_RUN:-$ROOT/incoming/rm2025_fixed/isaac/runs/$EXP_NAME/map_obstacle_refine_v2}"
SKILLS_RUN="$ROOT/incoming/rm2025_fixed/isaac/runs/$EXP_NAME/$RUN_NAME"
TRAIN="$ROOT/incoming/rm2025_fixed/isaac/train_isaac.py"
DISPLAY_NUMBER="${DISPLAY_NUMBER:-:0}"
XAUTH_FILE="${XAUTH_FILE:-/run/user/$(id -u)/gdm/Xauthority}"

latest() {
  local d="$1" n
  n="$(find "$d" -maxdepth 1 -type f -name 'model_[0-9]*.pt' -printf '%f\n' 2>/dev/null | sort -V | tail -n 1)"
  [[ -n "$n" ]] && printf '%s/%s\n' "$d" "$n"
}

if [[ -z "${RESUME_CHECKPOINT:-}" ]]; then
  RESUME_CHECKPOINT="$(latest "$SKILLS_RUN" || true)"
  if [[ -z "$RESUME_CHECKPOINT" ]]; then
    RESUME_CHECKPOINT="$(latest "$BASE_RUN" || true)"
  fi
fi
[[ -n "${RESUME_CHECKPOINT:-}" && -f "$RESUME_CHECKPOINT" ]] || { echo "no checkpoint" >&2; exit 2; }
iter="$(basename "$RESUME_CHECKPOINT" | sed -E 's/model_([0-9]+)\.pt/\1/')"
remaining=$((TARGET_ITERS - iter)); (( remaining > 0 )) || { echo "already at $iter"; exit 0; }

eval "$("$CONDA_EXE" shell.bash hook)"; conda activate "$ENV_NAME"
mkdir -p "$ROOT/logs/linux_launch"
log="$ROOT/logs/linux_launch/$RUN_NAME.log"; pidf="$ROOT/logs/linux_launch/$RUN_NAME.pid"
echo "resume $RESUME_CHECKPOINT (iter $iter) -> $remaining iters toward $TARGET_ITERS"
wc_flags=(--wheel-curve)
if [[ -n "$WHEEL_STALL" ]];   then wc_flags+=(--wheel-stall "$WHEEL_STALL");     fi
if [[ -n "$WHEEL_NOLOAD" ]]; then wc_flags+=(--wheel-noload "$WHEEL_NOLOAD");   fi
if [[ -n "$WHEEL_KNEE" ]];   then wc_flags+=(--wheel-knee "$WHEEL_KNEE");       fi
echo "wheel curve: ${wc_flags[*]} (empty = take DM3519+15.8 numbers from the contract) ; yaw-cmd ${YAW_CMD} rad/s ; spin band ${SPIN_BAND} rad/s ; gyro_stance weight ${GYRO_STANCE_W} ; spin_hold w=${SPIN_HOLD_W} spin_product w=${SPIN_PRODUCT} gyro_posture_relax=${GYRO_RELAX}"
nohup env DISPLAY="$DISPLAY_NUMBER" XAUTHORITY="$XAUTH_FILE" OMNI_KIT_ACCEPT_EULA=YES PYTHONUNBUFFERED=1 \
  "$CONDA_PREFIX/bin/python" "$TRAIN" \
    --ack-serial-teacher-not-deployable \
    --device cuda:0 --num_envs "$NUM_ENVS" --steps-per-env "$STEPS_PER_ENV" \
    --iters "$remaining" --save_interval 10 --viz kit --field --skills --terrain-all \
    --cmd 1.8 --yaw-cmd "$YAW_CMD" --yaw-ramp-iters "$YAW_RAMP" --init-std 0.35 --lr 7e-5 \
    "${wc_flags[@]}" \
    --spin-pure --spin-band "$SPIN_BAND" --spin-weight "$SPIN_HOLD_W" --spin-rate-weight 1.5 \
    --spin-product-weight "$SPIN_PRODUCT" --gyro-posture-relax "$GYRO_RELAX" \
    --gyro-stance-weight "$GYRO_STANCE_W" \
    --obstacle-focus --focus-profile gyro --jump-curriculum --curriculum-base-iter "$iter" \
    --run "$RUN_NAME" --resume "$RESUME_CHECKPOINT" \
    >"$log" 2>&1 </dev/null &
pid=$!; printf '%s\n' "$pid" >"$pidf"
printf '%s\n' "$pidf" > "$ROOT/logs/linux_launch/latest_pid_file"
printf '%s\n' "$log"  > "$ROOT/logs/linux_launch/latest_log_file"
echo "started PID $pid ; log $log"
