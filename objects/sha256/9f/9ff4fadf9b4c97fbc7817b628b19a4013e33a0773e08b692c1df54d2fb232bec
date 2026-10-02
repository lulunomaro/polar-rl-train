#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
RUN_NAME="${RUN_NAME:-map_obstacle_refine_v2}"
RUN_DIR="$ROOT/incoming/rm2025_fixed/isaac/runs/rm2025_serial_isaac/$RUN_NAME"
TARGET_ITER="${TARGET_ITER:-26000}"
CHUNK_ITERS="${CHUNK_ITERS:-4000}"
MAX_ITER="${MAX_ITER:-50000}"
POLL_SECONDS="${POLL_SECONDS:-30}"
CONDA_PYTHON="${CONDA_PYTHON:-/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python}"

latest_iter() {
  [[ -d "$1" ]] || return 0
  find "$1" -maxdepth 1 -type f -name 'model_[0-9]*.pt' -printf '%f\n' 2>/dev/null |
    sed -n 's/^model_\([0-9][0-9]*\)\.pt$/\1/p' | sort -n | tail -n 1
}

echo "$(date --iso-8601=seconds) finalizer waiting for model_$((TARGET_ITER - 1)).pt or newer"
while true; do
  iteration="$(latest_iter "$RUN_DIR")"
  iteration="${iteration:-0}"
  if (( iteration >= TARGET_ITER - 1 )); then
    break
  fi
  if ! pgrep -f 'train_isaac.py.*map_obstacle_refine_v2' >/dev/null && \
     ! pgrep -f 'supervise_refine.sh' >/dev/null; then
    echo "$(date --iso-8601=seconds) refinement stopped early at $iteration" >&2
    exit 1
  fi
  sleep "$POLL_SECONDS"
done

while pgrep -f 'train_isaac.py.*map_obstacle_refine_v2' >/dev/null; do
  sleep 5
done

iteration="$(latest_iter "$RUN_DIR")"
iteration="${iteration:-0}"
passed=0

while true; do
  checkpoint="$RUN_DIR/model_${iteration}.pt"
  report="$ROOT/logs/linux_launch/eval_gate_model_${iteration}.json"
  echo "$(date --iso-8601=seconds) zero-assistance evaluation at $checkpoint"
  CHECKPOINT="$checkpoint" REPORT="$report" NUM_ENVS=512 EVAL_STEPS=3000 \
    "$ROOT/migration/linux/run_final_eval.sh"

  gate_output="$("$CONDA_PYTHON" - "$report" <<'PY'
import json
import sys

r = json.load(open(sys.argv[1], encoding="utf-8"))
lanes = r.get("lanes", {})
means = r.get("means", {})
minimums = {
    "gap": 0.35,
    "launch": 0.20,
    "two_level_stairs": 0.15,
    "max_slope": 0.10,
    "both_slopes": 0.05,
    "full_course": 0.02,
}
rates = {name: float(lanes.get(name, {}).get("success_rate", 0.0))
         for name in minimums}
failed = [(name, rates[name], threshold) for name, threshold in minimums.items()
          if rates[name] < threshold]

# Command tracking and attitude are part of "learned", not merely reaching an x-coordinate.
gyro_error = float(means.get("gyro_yaw_error", 1e9))
turn_error = float(means.get("turn_yaw_error", 1e9))
level_fraction = float(means.get("level_5deg", 0.0))
upright_fraction = float(means.get("upright", 0.0))
motion_error = float(means.get("moving_vx_error", 1e9))
quality_failed = (gyro_error > 2.5 or turn_error > 1.8 or level_fraction < 0.55 or
                  upright_fraction < 0.92 or motion_error > 0.75)

if not failed and not quality_failed:
    print("PASS")
else:
    jump_names = ("gap", "launch")
    traverse_names = ("two_level_stairs", "max_slope", "both_slopes", "full_course")
    jump_deficit = max((minimums[n] - rates[n]) / minimums[n] for n in jump_names)
    traverse_deficit = max((minimums[n] - rates[n]) / minimums[n] for n in traverse_names)
    gyro_deficit = max(0.0, (gyro_error - 2.5) / 2.5)
    if quality_failed and level_fraction < 0.55:
        profile = "mixed"
    elif gyro_deficit > max(jump_deficit, traverse_deficit):
        profile = "gyro"
    elif traverse_deficit >= jump_deficit:
        profile = "traverse"
    else:
        profile = "jump"
    print("FAIL " + profile)
for name, value, threshold in failed:
    print("gate failed: %s %.2f%% < %.2f%%" % (name, value * 100.0, threshold * 100.0))
for name, value, relation, threshold in (
        ("gyro_yaw_error", gyro_error, "<=", 2.5),
        ("turn_yaw_error", turn_error, "<=", 1.8),
        ("level_5deg", level_fraction, ">=", 0.55),
        ("upright", upright_fraction, ">=", 0.92),
        ("moving_vx_error", motion_error, "<=", 0.75)):
    print("quality: %s %.4f %s %.4f" % (name, value, relation, threshold))
PY
)"
  printf '%s\n' "$gate_output"
  decision="$(printf '%s\n' "$gate_output" | head -n 1)"
  if [[ "$decision" == "PASS" ]]; then
    passed=1
    echo "$(date --iso-8601=seconds) all zero-assistance capability gates passed"
    break
  fi
  if (( iteration >= MAX_ITER - 1 )); then
    echo "$(date --iso-8601=seconds) safety ceiling reached at $iteration without passing all gates" >&2
    break
  fi

  profile="${decision#FAIL }"
  [[ "$profile" =~ ^(mixed|jump|traverse|gyro)$ ]] || profile=mixed
  next_target=$((iteration + CHUNK_ITERS + 1))
  (( next_target > MAX_ITER )) && next_target="$MAX_ITER"
  train_log="$ROOT/logs/linux_launch/${RUN_NAME}.log"
  [[ ! -f "$train_log" ]] || cp -f "$train_log" \
    "$ROOT/logs/linux_launch/${RUN_NAME}_through_${iteration}.log"

  attempt=0
  while (( iteration < next_target - 1 && attempt < 3 )); do
    attempt=$((attempt + 1))
    echo "$(date --iso-8601=seconds) extending to $next_target with profile $profile"
    TARGET_ITERS="$next_target" RUN_NAME="$RUN_NAME" OBSTACLE_FOCUS=1 \
      FOCUS_PROFILE="$profile" JUMP_CURRICULUM=1 \
      ASSIST_START_ITER=20580 ASSIST_END_ITER=24000 INIT_STD=0.20 \
      RESUME_CHECKPOINT="$checkpoint" "$ROOT/migration/linux/run_allterrain_training.sh"
    train_pid="$(<"$ROOT/logs/linux_launch/${RUN_NAME}.pid")"
    echo "$(date --iso-8601=seconds) extension PID $train_pid attempt $attempt"
    while kill -0 "$train_pid" 2>/dev/null; do
      sleep "$POLL_SECONDS"
    done
    iteration="$(latest_iter "$RUN_DIR")"
    iteration="${iteration:-0}"
    checkpoint="$RUN_DIR/model_${iteration}.pt"
  done
  if (( iteration < next_target - 1 )); then
    echo "$(date --iso-8601=seconds) extension stopped early at $iteration" >&2
    exit 1
  fi
done

CHECKPOINT="$checkpoint" "$ROOT/migration/linux/run_final_play.sh"
if (( passed )); then
  echo "$(date --iso-8601=seconds) verified final model and visible play launched"
else
  echo "$(date --iso-8601=seconds) best model visible play launched, but capability gate is not complete" >&2
  exit 2
fi
