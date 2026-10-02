#!/usr/bin/env bash
set -euo pipefail
R=/home/egde/rl_candidates/MOD4_takeover_20260914
O=$R/repair_zero_success_20260916/grounded_run_20260925
C=$O/source/mod4
PY=/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python
CK=$(find "$O/train_d08/logs" -name model_10.pt -print -quit)
MF=$(dirname "$CK")/run_manifest.json
export OMNI_KIT_ACCEPT_EULA=YES PYTHONUNBUFFERED=1 CUDA_VISIBLE_DEVICES=0
export RM_WORKSPACE_ROOT=$R/env_scaling_20260915/source
export RM_MOD4_USD=$R/repair_1536_20260915/asset/robot_tireload12_mat3.usd
export RM_MOD4_MAP=rmuc2026 RM_MOD4_TERRAIN=field RM_ROUTE_KINDS=run RM_ROUTE_WEIGHTS=run:1
export RM_EPISODE_S=15 RM_LEG_KP=250 RM_CLAMP_LEG_TARGETS=1
flock -x /tmp/mod4_takeover_gpu0.lock bash -c '
 set -e
 for trial in d065 d05; do
  if [ "$trial" = d065 ]; then export RM_DIFF_MIN=-0.65; else export RM_DIFF_MIN=-0.5; fi
  "$1" "$2/eval_episodes_mod4.py" --headless --checkpoint "$3" --manifest "$4" --num_envs 128 --steps 600 --seed 20260917 --report "$5/${trial}.json" > "$5/${trial}.log" 2>&1
  echo "$trial done $(date -Is)"
 done
' bash "$PY" "$C" "$CK" "$MF" "$O"
