#!/usr/bin/env bash
set -euo pipefail
ROOT=/home/egde/rl_candidates/MOD4_takeover_20260914
CODE=$ROOT/env_scaling_20260915/source/isaac/mod4
OUT=$ROOT/repair_zero_success_20260916/grounded_run_20260925
V10=$ROOT/repair_zero_success_20260916/flat_dr/flat_run_reference_v10_continue/logs/2026-09-16_15-42-04_flat_run_reference_v10_continue
PY=/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python
export OMNI_KIT_ACCEPT_EULA=YES PYTHONUNBUFFERED=1 CUDA_VISIBLE_DEVICES=0
export RM_MOD4_USD=$ROOT/repair_1536_20260915/asset/robot_tireload12_mat3.usd
export RM_MOD4_MAP=rmuc2026 RM_MOD4_TERRAIN=field RM_ROUTE_KINDS=run RM_ROUTE_WEIGHTS=run:1
export RM_EPISODE_S=15 RM_LEG_KP=250 RM_CLAMP_LEG_TARGETS=1
for trial in baseline restricted; do
  if [ "$trial" = baseline ]; then export RM_DIFF_MIN=-1.0843; else export RM_DIFF_MIN=-0.2; fi
  "$PY" "$CODE/eval_episodes_mod4.py" --headless --checkpoint "$V10/model_25.pt" --manifest "$V10/run_manifest.json" --num_envs 128 --steps 600 --seed 20260917 --report "$OUT/${trial}.json" > "$OUT/${trial}.log" 2>&1
  echo "$trial completed at $(date -Is)"
done
