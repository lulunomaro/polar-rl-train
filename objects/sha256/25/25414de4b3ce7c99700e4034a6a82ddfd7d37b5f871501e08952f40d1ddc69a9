#!/usr/bin/env bash
# Deterministic acceptance gate (docs/ACCEPTANCE_RM2025_LATER.md) for a later-plant checkpoint.
#
#   bash migration/linux/run_acceptance_later.sh <checkpoint> [num_envs]
#
# The gate MUST run with the same task configuration as training, otherwise it grades a
# different task than the one the policy was trained on.  Instead of copying the RM_* block
# (which then drifts) this pulls it straight out of the launcher and substitutes each
# "${VAR:-default}" with its default.
#
# Runs alongside training: 128 envs is ~1/64th of the training scene and the script never
# mutates the checkpoint or the run.
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

PY="$ROOT/third_party/rc_mjlab/.venv/bin/python"
CKPT="${1:?usage: run_acceptance_later.sh <checkpoint> [num_envs]}"
ENVS="${2:-128}"
[[ -f "$CKPT" ]] || { echo "no such checkpoint: $CKPT" >&2; exit 2; }

# [A-Z0-9_] not [A-Z_]: RM_WZ0, RM_ACTION_L2_W and RM_ACTION_L2_WHEEL all carry digits,
# and silently grading with their code defaults instead of the trained values is exactly
# the class of bug this wrapper exists to prevent.
eval "$(grep -E '^export RM_[A-Z0-9_]+=' migration/linux/run_rm2025_later_training.sh \
        | sed 's/\${[A-Z0-9_]*:-\([^}]*\)}/\1/')"
export PYTHONPATH="$ROOT/train/rmvehicle/src:$ROOT/third_party/rc_mjlab/mjlab/src"

tag="$(basename "$CKPT" .pt)"
LOG="$ROOT/logs/linux_launch/acceptance_v2_${tag}.log"
JSON="train/deploy/acceptance_v2_${tag}.json"
MD="docs/ACCEPTANCE_REPORT_RM2025_LATER_v2_${tag}.md"

echo "checkpoint : $CKPT"
echo "num envs   : $ENVS"
echo "log        : $LOG"
set +e
"$PY" train/verify_acceptance_later.py --checkpoint "$CKPT" --num-envs "$ENVS" \
    --device cuda:0 --seed 0 --condition nominal --identity auto \
    --out-json "$JSON" --out-md "$MD" > "$LOG" 2>&1
rc=$?
set -e
echo "acceptance rc=$rc"
grep -E '^\| |RESULT|PASS|FAIL' "$LOG" | tail -25 || tail -25 "$LOG"
exit "$rc"
