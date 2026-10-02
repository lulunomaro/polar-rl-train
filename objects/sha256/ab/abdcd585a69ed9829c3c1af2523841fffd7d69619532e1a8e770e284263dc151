#!/usr/bin/env bash
# Resume the v2 run past its first iteration budget, without ever racing the trainer.
#
#   TARGET_ITER=1500 bash migration/linux/continue_rm2025_later_training.sh
#
# Safe to run repeatedly and safe to run from a watchdog:
#   * it refuses to do anything while a trainer process is alive (no double launch);
#   * it refuses to do anything once the newest checkpoint already reached TARGET_ITER;
#   * the launcher it calls re-runs the model identity gate and resumes from the newest
#     checkpoint, so a continued run keeps the same config and the same rollback points.
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

EXPERIMENT="${EXPERIMENT:-rm2025_later_flat_v2}"
TARGET_ITER="${TARGET_ITER:-1500}"

if pgrep -f '[m]jlab.scripts.train' >/dev/null 2>&1; then
  echo "trainer already running; nothing to do"
  exit 0
fi

newest="$(find "train/logs/rsl_rl/$EXPERIMENT" -name 'model_[0-9]*.pt' -printf '%f\n' 2>/dev/null \
          | sed 's/^model_//; s/\.pt$//' | sort -n | tail -1)"
newest="${newest:-0}"
echo "experiment=$EXPERIMENT newest=$newest target=$TARGET_ITER"
if (( newest >= TARGET_ITER )); then
  echo "target already reached ($newest >= $TARGET_ITER); nothing to do"
  exit 0
fi

OUT="logs/linux_launch/continue_${newest}.out"
nohup env EXPERIMENT="$EXPERIMENT" TARGET_ITER="$TARGET_ITER" \
  bash migration/linux/run_rm2025_later_training.sh > "$OUT" 2>&1 &
echo "continued from $newest toward $TARGET_ITER (pid $!) log=$OUT"
