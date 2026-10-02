#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
CONDA_EXE="${CONDA_EXE:-/home/egde/anaconda3/bin/conda}"
ENV_NAME="${FANGZHEN_CONDA_ENV:-fangzhen-isaaclab}"
RUN_NAME="${RUN_NAME:-map_obstacle_refine_v2}"
RUN_DIR="$ROOT/incoming/rm2025_fixed/isaac/runs/rm2025_serial_isaac/$RUN_NAME"
TRAIN_SCRIPT="$ROOT/incoming/rm2025_fixed/isaac/train_isaac.py"
NUM_ENVS="${NUM_ENVS:-512}"
EVAL_STEPS="${EVAL_STEPS:-3000}"

latest_numeric_checkpoint() {
  local directory="$1"
  local latest_name
  latest_name="$(find "$directory" -maxdepth 1 -type f -name 'model_[0-9]*.pt' \
    -printf '%f\n' 2>/dev/null | sort -V | tail -n 1)"
  [[ -n "$latest_name" ]] && printf '%s/%s\n' "$directory" "$latest_name"
}

CHECKPOINT="${CHECKPOINT:-$(latest_numeric_checkpoint "$RUN_DIR")}"
if [[ ! -f "$CHECKPOINT" ]]; then
  echo "Final evaluation checkpoint not found: $CHECKPOINT" >&2
  exit 2
fi

checkpoint_name="$(basename "$CHECKPOINT" .pt)"
launcher_dir="$ROOT/logs/linux_launch"
mkdir -p "$launcher_dir"
REPORT="${REPORT:-$launcher_dir/eval_final_${checkpoint_name}.json}"
LOG="${LOG:-$launcher_dir/eval_final_${checkpoint_name}.log}"

eval "$("$CONDA_EXE" shell.bash hook)"
conda activate "$ENV_NAME"

echo "Final deterministic evaluation: $CHECKPOINT"
echo "Zero assistance, normal obstacle starts, $NUM_ENVS envs x $EVAL_STEPS steps"
echo "Report: $REPORT"

env OMNI_KIT_ACCEPT_EULA=YES PYTHONUNBUFFERED=1 \
  "$CONDA_PREFIX/bin/python" "$TRAIN_SCRIPT" \
    --ack-serial-teacher-not-deployable \
    --device cuda:0 --num_envs "$NUM_ENVS" --steps-per-env 12 \
    --field --skills --terrain-all --obstacle-focus --jump-curriculum \
    --cmd 1.8 --yaw-cmd 14.0 --init-std 0.27 \
    --resume "$CHECKPOINT" --eval-only --eval-steps "$EVAL_STEPS" \
    --eval-report "$REPORT" 2>&1 | tee "$LOG"

python - "$REPORT" <<'PY'
import json
import sys

report = json.load(open(sys.argv[1], encoding="utf-8"))
if report.get("assist_probability") != 0.0 or report.get("assist_events") != 0:
    raise SystemExit("final evaluation was not zero-assistance")
print("Final evaluation verified zero-assistance.")
for name, lane in report.get("lanes", {}).items():
    print("%s: %d/%d (%.2f%%)" % (
        name, lane["successes"], lane["episodes"], 100.0 * lane["success_rate"]))
PY
