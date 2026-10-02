#!/usr/bin/env bash
# Production training for the DELIVERED later no-gimbal closed-chain plant
# (plant selected by train/rmvehicle/src/rmvehicle/names.py - currently the MOD4 delivery at
# incoming/rm2025_mod4/robot_hifi.xml), on the target 4090.
#
# This is the only launcher allowed to produce deployable weights:
#   * it refuses to start unless scripts/check_model_identity.py passes, which reads the
#     <option> block, joint/body/actuator sets and closed-chain equalities back out of the
#     compiled training model and compares them with the source MJCF;
#   * it never resumes the PhysX serial [hip, knee] teacher or the earlier CC plant;
#   * it resumes its own newest checkpoint after a crash and leaves every rollback point.
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PY="$ROOT/third_party/rc_mjlab/.venv/bin/python"
TRAIN_ROOT="$ROOT/train"
# 2026-09-10: v2 = the 0910 plant plus the fixes in docs/DIAG_FLAT_V1_20260910.md.
# A NEW experiment name is deliberate: the old experiment still holds the crashed run's
# checkpoints, and the launcher would resume from the newest one of those.
EXPERIMENT="${EXPERIMENT:-rm2025_later_flat_v2}"
RUN_NAME="${RUN_NAME:-prod_$(date +%Y%m%d_%H%M%S)}"
NUM_ENVS="${NUM_ENVS:-8192}"
# 10 h budget at the measured 15 s/iteration (8192 envs, 13.2k env-steps/s).
TARGET_ITER="${TARGET_ITER:-500}"
TASK="${TASK:-RM2025-Later-CC-Flat-v0}"
LOGDIR="$ROOT/logs/linux_launch"

[[ -x "$PY" ]] || { echo "run migration/linux/setup_mjlab.sh first" >&2; exit 2; }
mkdir -p "$LOGDIR"

latest_checkpoint() {
  local root="$1" best=-1 best_path="" path base n
  [[ -d "$root" ]] || return 0
  while IFS= read -r path; do
    base="$(basename "$path")"; n="${base#model_}"; n="${n%.pt}"
    [[ "$n" =~ ^[0-9]+$ ]] || continue
    if (( n > best )); then best="$n"; best_path="$path"; fi
  done < <(find "$root" -type f -name 'model_[0-9]*.pt' -print 2>/dev/null)
  printf '%s\n' "$best_path"
}

export RM_MOTOR="${RM_MOTOR:-dm8009}"
export RM_WHEEL_SCALE="${RM_WHEEL_SCALE:-10.0}"
export RM_WZ_MAX="${RM_WZ_MAX:-13.0}"
export RM_WZ0="${RM_WZ0:-2.0}"
export RM_LV_STD="${RM_LV_STD:-1.0}"
export RM_AV_STD="${RM_AV_STD:-2.5}"
export RM_SKILL_SPLIT="${RM_SKILL_SPLIT:-1}"
export RM_SKILL_GYRO_FRAC="${RM_SKILL_GYRO_FRAC:-0.30}"
export RM_SKILL_WZ_LOCO="${RM_SKILL_WZ_LOCO:-2.0}"
export RM_GYRO_WIDE_W="${RM_GYRO_WIDE_W:-2.0}"
export RM_GYRO_BAND="${RM_GYRO_BAND:-8.0}"
export RM_WZ_STEP="${RM_WZ_STEP:-0.5}"
export RM_WZ_EVERY="${RM_WZ_EVERY:-40}"
export RM_JUMP_P="${RM_JUMP_P:-0.2}"
export RM_TERRAIN_ROWS="${RM_TERRAIN_ROWS:-8}"
export RM_FLAT_PROP="${RM_FLAT_PROP:-0.35}"
# 2026-09-10 SCUT-aligned PPO + CC v17a warm start:
export RM_STD_TYPE="${RM_STD_TYPE:-scalar}"
export RM_INIT_STD="${RM_INIT_STD:-0.3}"
export RM_STD_MIN="${RM_STD_MIN:-0.05}"
export RM_STD_MAX="${RM_STD_MAX:-0.2}"
export RM_ENTROPY_COEF="${RM_ENTROPY_COEF:-0.0005}"
export RM_LR="${RM_LR:-1e-4}"
# 2026-09-10: rsl_rl's adaptive schedule updates the lr INSIDE the mini-batch loop, so one
# iteration can divide it by 1.5^20 and pin it to the 1e-5 floor (docs/DIAG_FLAT_V1_20260910.md).
# Fixed lr is the only schedule that honours RM_LR.
export RM_LR_SCHEDULE="${RM_LR_SCHEDULE:-fixed}"
export RM_VALUE_LOSS_COEF="${RM_VALUE_LOSS_COEF:-2.0}"
export RM_CLIP_ACTIONS="${RM_CLIP_ACTIONS:-3.0}"
# -0.5 made the leg action cost -0.2638/step, larger than every positive reward combined, so
# the net reward per step was negative and "fall over early" was the optimal policy.
export RM_ACTION_L2_W="${RM_ACTION_L2_W:--0.1}"
export RM_ACTION_L2_WHEEL="${RM_ACTION_L2_WHEEL:--0.02}"
# One-shot penalty on a non-timeout termination (bad_orientation / base_contact /
# nan_detection).  A 20 s episode at a healthy ~+0.13/step is worth ~+260, so a terminal
# state has to cost something or "fall early" stays free.
export RM_TERM_PENALTY="${RM_TERM_PENALTY:--20.0}"
export RM_NCONMAX="${RM_NCONMAX:-64}"
export RM_NJMAX="${RM_NJMAX:-900}"
# The delivered later plant carries ~66x the CC plant's qacc even in a zero-control drop
# (stiff gas spring + 10 closed-chain equalities; see docs/REWARD_SCALE_RM2025_LATER.md).
# The CC-tuned -2.5e-6 made joint_acc 99% of the episode reward and the value loss ~1e8 in
# rm2025_later_cc_v1.  -1e-8 keeps it as a mild smoothness regulariser instead.
export RM_JOINT_ACC_W="${RM_JOINT_ACC_W:--1e-8}"
# SCUT-style exploration range: their leg/wheel action units are 0.25 rad and 10 rad/s per
# unit; ours are 0.5 rad and 55 rad/s, so the initial std is halved twice over.
export RM_INIT_STD="${RM_INIT_STD:-0.3}"
# SCUT trains 5..25 ms of motor/IMU feedback delay and 0..20 ms of command latency.
# At 0.5 ms physics / 100 Hz policy: 1..2 policy steps of obs delay and 0..20 physics
# steps (= 0..10 ms) of actuator delay is the equivalent one-control-step worst case.
export RM_OBS_DELAY_MIN_LAG="${RM_OBS_DELAY_MIN_LAG:-1}"
export RM_OBS_DELAY_MAX_LAG="${RM_OBS_DELAY_MAX_LAG:-2}"
export RM_DELAY_MAX_LAG="${RM_DELAY_MAX_LAG:-20}"
export PYTHONPATH="$ROOT/train/rmvehicle/src:$ROOT/third_party/rc_mjlab/mjlab/src"

echo "== identity gate =="
"$PY" "$ROOT/scripts/check_model_identity.py" \
  --task RM2025-Later-CC-Flat-v0 --model later --num-envs 4 \
  --json-out "$LOGDIR/${RUN_NAME}_identity.json" \
  > "$LOGDIR/${RUN_NAME}_identity.log" 2>&1 || {
    echo "IDENTITY GATE FAILED -- refusing to train. See $LOGDIR/${RUN_NAME}_identity.log" >&2
    exit 3
  }
grep -E "IDENTITY GATE|FAIL" "$LOGDIR/${RUN_NAME}_identity.log" | tail -3

existing="$(latest_checkpoint "$TRAIN_ROOT/logs/rsl_rl/$EXPERIMENT")"
resume_args=()
start_iter=0
if [[ -n "$existing" ]]; then
  base="$(basename "$existing")"
  start_iter="${base#model_}"; start_iter="${start_iter%.pt}"
  if (( start_iter >= TARGET_ITER )); then
    echo "target already reached: $start_iter >= $TARGET_ITER"; exit 0
  fi
  seed_dir="$TRAIN_ROOT/logs/rsl_rl/$EXPERIMENT/seed"
  mkdir -p "$seed_dir"
  [[ -f "$seed_dir/$base" ]] || cp "$existing" "$seed_dir/$base"
  resume_args=(--agent.resume True --agent.load-run seed --agent.load-checkpoint "$base")
  echo "resume from $base ($start_iter) -> target $TARGET_ITER"
else
  echo "fresh run -> target $TARGET_ITER"
fi
remaining=$((TARGET_ITER - start_iter))

log="$LOGDIR/${RUN_NAME}.log"
pidf="$LOGDIR/${RUN_NAME}.pid"
cd "$TRAIN_ROOT"
nohup env CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0}" PYTHONUNBUFFERED=1 \
  "$PY" -m mjlab.scripts.train "$TASK" \
    --env.scene.num-envs "$NUM_ENVS" \
    --agent.max-iterations "$remaining" \
    --agent.logger tensorboard \
    --agent.experiment-name "$EXPERIMENT" \
    --agent.run-name "$RUN_NAME" \
    "${resume_args[@]}" \
    >"$log" 2>&1 </dev/null &
pid=$!
printf '%s\n' "$pid" > "$pidf"
printf '%s\n' "$pid" > "$LOGDIR/latest_rm2025_later_pid_file"
printf '%s\n' "$log" > "$LOGDIR/latest_rm2025_later_log_file"
echo "started $TASK pid $pid envs $NUM_ENVS"
echo "log: $log"
