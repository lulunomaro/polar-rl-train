#!/usr/bin/env bash
set -euo pipefail
stage=/home/egde/rl_candidates/MOD4_takeover_20260914/scut_v14_strong_posture_20260928
status="$stage/run/scut_v14_strong_posture_20260928/status.json"
log="$stage/run/posture_finalizer.log"
exec >> "$log" 2>&1
echo "watching $(date -Is)"
for ((i=0; i<180; i++)); do
  state=$(jq -r '.state // "missing"' "$status" 2>/dev/null || true)
  case "$state" in
    time_budget_complete) break ;;
    failed_needs_review) echo "trainer failed $(date -Is)"; exit 2 ;;
  esac
  sleep 30
done
if [[ "$state" != time_budget_complete ]]; then
  echo "no normal budget completion by $(date -Is): $state"
  exit 3
fi
echo "training complete, evaluating $(date -Is)"
flock -n "$stage/run/posture_pair_eval.lock" bash "$stage/eval_posture_pair.sh"
echo "evaluation complete $(date -Is)"
