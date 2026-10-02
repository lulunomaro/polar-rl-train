#!/usr/bin/env bash
set -euo pipefail
R=/home/egde/rl_candidates/MOD4_takeover_20260914
G=$R/repair_zero_success_20260916/grounded_run_20260925
C=$G/source/mod4
CK=$(find "$G/train_d08/logs" -name model_10.pt -print -quit)
PY=/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python
export OMNI_KIT_ACCEPT_EULA=YES PYTHONUNBUFFERED=1 CUDA_VISIBLE_DEVICES=0
export RM_WORKSPACE_ROOT=$R/env_scaling_20260915/source
export RM_MOD4_USD=$R/repair_1536_20260915/asset/robot_tireload12_mat3.usd
export RM_MOD4_MAP=rmuc2026 RM_MOD4_TERRAIN=field RM_ROUTE_KINDS=run RM_ROUTE_WEIGHTS=run:1
export RM_GAS_FORCE_DR=1 RM_GAS_FORCE_NOMINAL_N=500 RM_GAS_FORCE_MIN_N=500 RM_GAS_FORCE_MAX_N=500
"$PY" "$C/eval_episodes_mod4_gas.py" --headless --checkpoint "$CK" --num_envs 256 --steps 1500 --seed 20260917 --report "$G/d08_gas500_nominal_control.json" > "$G/d08_gas500_nominal_control.log" 2>&1
echo "DONE $(date -Is) $CK"
