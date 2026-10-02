#!/usr/bin/env bash
# Stage 2 of the 0910 ladder (2026-09-10): warm-start the all-terrain + skills Field task
# from the flat policy that rm2025_later_flat_v2 produced.
#
# Ladder context: the flat stage proves the reward net is positive and the policy can stand
# and track; the Field stage then adds ramps/stairs/barricades/bumps/gaps and the real
# 250 mm x 800 mm x 300 mm tunnel, plus the 小陀螺 window and the jump schedule.  Both use
# the same 35-D observation / 6-D action contract, so the flat weights load directly.
#
# NO SUPERVISOR: this script runs the identity gate, seeds the new experiment from the flat
# checkpoint, starts training under nohup and exits.  If the run dies it stays dead - the
# local Start-Sleep heartbeat (scripts/monitor_rm2025.ps1) only reports, it never restarts.
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SRC_EXP="${SRC_EXP:-rm2025_later_flat_v2}"
DST_EXP="${DST_EXP:-rm2025_later_field_0910_v1}"
TARGET_ITER="${TARGET_ITER:-2400}"
NUM_ENVS="${NUM_ENVS:-8192}"
RUN_NAME="${RUN_NAME:-prod_$(date +%Y%m%d_%H%M%S)}"
LOGSDIR="$ROOT/train/logs/rsl_rl"

if pgrep -f "[m]jlab.scripts.train" >/dev/null; then
  echo "refusing to start: a training process is already running" >&2
  pgrep -af "[m]jlab.scripts.train" >&2
  exit 4
fi

src=""
best=-1
while IFS= read -r path; do
  base="$(basename "$path")"; n="${base#model_}"; n="${n%.pt}"
  [[ "$n" =~ ^[0-9]+$ ]] || continue
  if (( n > best )); then best="$n"; src="$path"; fi
done < <(find "$LOGSDIR/$SRC_EXP" -type f -name 'model_[0-9]*.pt' -print 2>/dev/null)
[[ -n "$src" ]] || { echo "no checkpoint under $LOGSDIR/$SRC_EXP" >&2; exit 5; }

seed_dir="$LOGSDIR/$DST_EXP/seed"
mkdir -p "$seed_dir"
cp "$src" "$seed_dir/model_0.pt"
echo "seed warm start: $src (iter $best) -> $seed_dir/model_0.pt"

# The flat stage drove Policy/mean_std to the 0.05 floor (entropy_coef 0.0005): fine for a
# gait that only has to stand and track, but the jump/gyro skills need the policy to keep
# probing.  0.002 is still 2.5x below SCUT's 0.005 and the std_range cap of 0.2 remains in
# place, so this cannot repeat the 2026-09-09 std runaway (std 0.30 -> 12.88).
#
# NOTE: plain `export` lines.  An earlier version put a comment in the middle of a
# backslash-continued command, which ended the command early and silently ran the launcher
# with its own defaults (EXPERIMENT=rm2025_later_flat_v2, TARGET_ITER=500) - the run then
# exited with "target already reached".
export EXPERIMENT="$DST_EXP"
export RUN_NAME="$RUN_NAME"
export TASK="${TASK:-RM2025-Later-CC-Field-v0}"
export TARGET_ITER NUM_ENVS
export RM_SKILL_SPLIT="${RM_SKILL_SPLIT:-1}"
export RM_WZ0="${RM_WZ0:-2.0}" RM_WZ_STEP="${RM_WZ_STEP:-0.5}" RM_WZ_EVERY="${RM_WZ_EVERY:-40}"
export RM_WHEEL_SCALE="${RM_WHEEL_SCALE:-10.0}"
export RM_ENTROPY_COEF="${RM_ENTROPY_COEF:-0.002}"
bash "$ROOT/migration/linux/run_rm2025_later_training.sh"
