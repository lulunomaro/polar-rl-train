#!/usr/bin/env bash
set -euo pipefail
ROOT=/home/egde/rl_candidates/MOD4_takeover_20260914
OUT=$ROOT/repair_zero_success_20260916/grounded_run_20260925/train_d08
CODE=$ROOT/env_scaling_20260915/source/isaac/mod4
PY=/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python
while true; do
  STATE=$($PY -c 'import json,sys;print(json.load(open(sys.argv[1]))["status"])' "$OUT/stage_status.json")
  if [ "$STATE" = FINISHED_UNEVALUATED ]; then break; fi
  if [ "$STATE" = STOPPED_OR_FAILED ]; then echo "training failed, no evaluation"; exit 3; fi
  sleep 30
done
CKPT=$($PY -c 'import json,sys;print(json.load(open(sys.argv[1]))["latest_checkpoint"])' "$OUT/stage_status.json")
export OMNI_KIT_ACCEPT_EULA=YES PYTHONUNBUFFERED=1 CUDA_VISIBLE_DEVICES=0
export RM_MOD4_USD=$ROOT/repair_1536_20260915/asset/robot_tireload12_mat3.usd
export RM_MOD4_MAP=rmuc2026 RM_MOD4_TERRAIN=field RM_ROUTE_KINDS=run RM_ROUTE_WEIGHTS=run:1
flock -x /tmp/mod4_takeover_gpu0.lock bash -c '
  set -e
  "$1" "$2/eval_episodes_mod4.py" --headless --checkpoint "$3" --num_envs 256 --steps 1500 --seed 20260917 --report "$4/nominal.json" > "$4/nominal.log" 2>&1
  "$1" "$2/eval_episodes_mod4.py" --headless --checkpoint "$3" --num_envs 256 --steps 1500 --seed 20260917 --domain_rand --report "$4/dr.json" > "$4/dr.log" 2>&1
' bash "$PY" "$CODE" "$CKPT" "$OUT"
echo "nominal and DR reports complete at $(date -Is)"
