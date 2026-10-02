#!/usr/bin/env bash
set -Eeuo pipefail
ROOT=/home/egde/rl_candidates/MOD4_takeover_20260914
PY=/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python
STATUS="$ROOT/logs/takeover_20260914/supervisor/STATUS.json"
OUT="$ROOT/acceptance/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$OUT"
readarray -t vals < <(python3 - "$STATUS" <<'PY'
import json,sys
d=json.load(open(sys.argv[1])); print(d['checkpoint']); print(d['manifest'])
PY
)
CKPT="${vals[0]}"; MANIFEST="${vals[1]}"
for mode in nominal dr; do
  extra=(); [[ "$mode" == dr ]] && extra+=(--domain_rand)
  reports=()
  for seed in 20260914 20260915 20260916; do
    report="$OUT/${mode}_${seed}.json"; reports+=("$report")
    "$PY" "$ROOT/isaac/mod4/eval_episodes_mod4.py" --checkpoint "$CKPT" \
      --manifest "$MANIFEST" --num_envs 64 --steps 4500 --seed "$seed" \
      --report "$report" "${extra[@]}" > "$OUT/${mode}_${seed}.log" 2>&1
  done
  "$PY" "$ROOT/isaac/mod4/aggregate_acceptance.py" "${reports[@]}" \
    --out "$OUT/${mode}_summary.json" > "$OUT/${mode}_summary.txt"
done
sha256sum "$CKPT" "$MANIFEST" "$OUT"/*.json > "$OUT/SHA256SUMS"
echo "$OUT"
