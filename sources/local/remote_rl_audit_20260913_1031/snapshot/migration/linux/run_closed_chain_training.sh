#!/usr/bin/env bash
# Resume the deployable similar-linkage policy on the RM2026 field.
# Actions are [left crank, left thigh, right crank, right thigh, left wheel,
# right wheel] in actuator OUTPUT coordinates; passive knees are never actions.
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PY="$ROOT/third_party/rc_mjlab/.venv/bin/python"
TRAIN_ROOT="$ROOT/train"
SOURCE_EXP="${SOURCE_EXP:-rm_cc_v17a}"
EXPERIMENT="${EXPERIMENT:-rm_cc_dm3519_closedchain_v1}"
RUN_NAME="${RUN_NAME:-production_$(date +%Y%m%d_%H%M%S)}"
NUM_ENVS="${NUM_ENVS:-8192}"
TARGET_ITER="${TARGET_ITER:-24000}"

[[ -x "$PY" ]] || { echo "run migration/linux/setup_mjlab.sh first" >&2; exit 2; }

latest_numeric_checkpoint() {
  local root="$1" path base n best_n=-1 best_path=""
  [[ -d "$root" ]] || return 0
  while IFS= read -r path; do
    base="$(basename "$path")"
    n="${base#model_}"; n="${n%.pt}"
    if [[ "$n" =~ ^[0-9]+$ ]] && (( n > best_n )); then
      best_n="$n"; best_path="$path"
    fi
  done < <(find "$root" -type f -name 'model_[0-9]*.pt' -print 2>/dev/null)
  printf '%s\n' "$best_path"
}

if [[ -z "${RESUME_CHECKPOINT:-}" ]]; then
  # Resume our own newest production checkpoint first.  Falling back to the old
  # source experiment on every invocation silently discarded hours of fine-tuning.
  RESUME_CHECKPOINT="$(latest_numeric_checkpoint "$TRAIN_ROOT/logs/rsl_rl/$EXPERIMENT")"
  if [[ -z "$RESUME_CHECKPOINT" ]]; then
    RESUME_CHECKPOINT="$(latest_numeric_checkpoint "$TRAIN_ROOT/logs/rsl_rl/$SOURCE_EXP")"
  fi
fi
[[ -f "${RESUME_CHECKPOINT:-}" ]] || {
  echo "no closed-chain checkpoint found under $TRAIN_ROOT/logs/rsl_rl/$SOURCE_EXP" >&2
  exit 2
}

# mjlab resolves resume checkpoints inside the destination experiment.  Seed a
# dedicated immutable copy so the old experiment and all rollback points remain.
seed_dir="$TRAIN_ROOT/logs/rsl_rl/$EXPERIMENT/seed"
mkdir -p "$seed_dir" "$ROOT/logs/linux_launch"
checkpoint_name="$(basename "$RESUME_CHECKPOINT")"
checkpoint_iter="${checkpoint_name#model_}"; checkpoint_iter="${checkpoint_iter%.pt}"
[[ "$checkpoint_iter" =~ ^[0-9]+$ ]] || { echo "non-numeric checkpoint: $checkpoint_name" >&2; exit 2; }
remaining=$((TARGET_ITER - checkpoint_iter))
(( remaining > 0 )) || { echo "production target already reached: $checkpoint_iter >= $TARGET_ITER"; exit 0; }
seed_checkpoint="$seed_dir/$checkpoint_name"
if [[ ! -f "$seed_checkpoint" ]]; then
  cp "$RESUME_CHECKPOINT" "$seed_checkpoint"
fi

log="$ROOT/logs/linux_launch/$RUN_NAME.log"
pidf="$ROOT/logs/linux_launch/$RUN_NAME.pid"
cd "$TRAIN_ROOT"

echo "production plant: RMVehicle-CC-Field-v0 (similar-linkage closed chain)"
echo "motor envelope: DM-J8009-2EC legs + DM3519/15.8 wheels"
echo "resume: $seed_checkpoint"
echo "batch: $NUM_ENVS envs; checkpoint $checkpoint_iter -> target $TARGET_ITER ($remaining updates)"
echo "log: $log"

nohup env \
  CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0}" \
  PYTHONUNBUFFERED=1 \
  RM_MOTOR=dm8009 \
  RM_WHEEL_SCALE="${RM_WHEEL_SCALE:-55.0}" \
  RM_WZ_MAX="${RM_WZ_MAX:-14.0}" \
  RM_WZ0="${RM_WZ0:-6.0}" \
  RM_LV_STD="${RM_LV_STD:-1.0}" \
  RM_AV_STD="${RM_AV_STD:-2.5}" \
  RM_FLAT_PROP="${RM_FLAT_PROP:-0.25}" \
  RM_SKILL_SPLIT="${RM_SKILL_SPLIT:-1}" \
  RM_SKILL_GYRO_FRAC="${RM_SKILL_GYRO_FRAC:-0.25}" \
  RM_SKILL_WZ_LOCO="${RM_SKILL_WZ_LOCO:-2.0}" \
  RM_OBS_DELAY_MIN_LAG="${RM_OBS_DELAY_MIN_LAG:-0}" \
  RM_OBS_DELAY_MAX_LAG="${RM_OBS_DELAY_MAX_LAG:-2}" \
  "$PY" -m mjlab.scripts.train RMVehicle-CC-Field-v0 \
    --env.scene.num-envs "$NUM_ENVS" \
    --agent.max-iterations "$remaining" \
    --agent.logger tensorboard \
    --agent.experiment-name "$EXPERIMENT" \
    --agent.run-name "$RUN_NAME" \
    --agent.resume True \
    --agent.load-run seed \
    --agent.load-checkpoint "$checkpoint_name" \
    >"$log" 2>&1 </dev/null &

pid=$!
printf '%s\n' "$pid" >"$pidf"
printf '%s\n' "$pidf" >"$ROOT/logs/linux_launch/latest_closed_chain_pid_file"
printf '%s\n' "$log" >"$ROOT/logs/linux_launch/latest_closed_chain_log_file"
echo "started production closed-chain PID $pid"
