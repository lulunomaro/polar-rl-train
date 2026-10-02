#!/usr/bin/env bash
# Measure the 跑 (speed ladder) skill of a later-plant checkpoint, optionally waiting for it.
#
#   bash migration/linux/run_skills_later.sh <checkpoint> [num_envs] [max_wait_s] [only]
#
# Why this exists next to run_acceptance_later.sh: the full acceptance gate takes ~16
# minutes and its speed section is the same ladder.  This runs ONLY the ladder, so a
# mid-training checkpoint can be scored in ~2 minutes and compared against the mature
# reference numbers in train/deploy/skills_v17a_field_run.json.
#
# Uses the same RM_* block as training (extracted from the launcher, never copied), so the
# command window, action scale and task config are the ones the policy was trained under.
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

CKPT="${1:?usage: run_skills_later.sh <checkpoint> [num_envs] [max_wait_s] [only]}"
ENVS="${2:-64}"
WAIT="${3:-1800}"
ONLY="${4:-run}"

waited=0
while [[ ! -f "$CKPT" ]]; do
  if (( waited >= WAIT )); then echo "TIMEOUT after ${waited}s waiting for $CKPT"; exit 3; fi
  sleep 10; waited=$((waited + 10))
done
echo "checkpoint ready after ${waited}s: $CKPT"

eval "$(grep -E '^export RM_[A-Z0-9_]+=' migration/linux/run_rm2025_later_training.sh \
        | sed 's/\${[A-Z0-9_]*:-\([^}]*\)}/\1/')"
export PYTHONPATH="$ROOT/train/rmvehicle/src:$ROOT/third_party/rc_mjlab/mjlab/src"

tag="$(basename "$CKPT" .pt)"
OUT="train/deploy/skills_v2_${tag}.json"
LOG="$ROOT/logs/linux_launch/skills_v2_${tag}.log"
echo "only=$ONLY envs=$ENVS out=$OUT"
set +e
"$ROOT/third_party/rc_mjlab/.venv/bin/python" train/verify_skills.py \
    --task RM2025-Later-CC-Skills-v0 --model later --checkpoint "$CKPT" \
    --num-envs "$ENVS" --device cuda:0 --only "$ONLY" --out "$OUT" > "$LOG" 2>&1
rc=$?
set -e
echo "skills rc=$rc"
if [[ -f "$OUT" ]]; then
  "$ROOT/third_party/rc_mjlab/.venv/bin/python" - "$OUT" <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
for row in d.get("run", []):
    print("cmd %-5s achieved %+.3f  err %.3f  alive %.2f  roll %+.1f pitch %+.1f"
          % (row["cmd"], row["achieved"], row["err"], row["alive"], row["roll"], row["pitch"]))
PY
fi
exit "$rc"
