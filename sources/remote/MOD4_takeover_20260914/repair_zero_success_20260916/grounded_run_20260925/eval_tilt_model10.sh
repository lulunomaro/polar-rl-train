#!/usr/bin/env bash
set -euo pipefail
R=/home/egde/rl_candidates/MOD4_takeover_20260914
P=$R/repair_zero_success_20260916/grounded_run_20260925
O=$P/train_tilt_v2_retry3
CK=$(find "$O/logs" -maxdepth 2 -name model_10.pt -print -quit)
export OMNI_KIT_ACCEPT_EULA=YES PYTHONUNBUFFERED=1 CUDA_VISIBLE_DEVICES=0
export RM_WORKSPACE_ROOT=$R/env_scaling_20260915/source
export RM_MOD4_USD=$R/repair_1536_20260915/asset/robot_tireload12_mat3.usd
export RM_MOD4_MAP=rmuc2026 RM_MOD4_TERRAIN=field RM_ROUTE_KINDS=run RM_ROUTE_WEIGHTS=run:1
/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python "$P/source/mod4/eval_episodes_mod4.py" --headless --checkpoint "$CK" --num_envs 256 --steps 1500 --seed 20260917 --report "$O/model10_nominal.json" > "$O/model10_nominal.log" 2>&1
echo "DONE $(date -Is)"
