#!/usr/bin/env bash
set -euo pipefail
R=/home/egde/rl_candidates/MOD4_takeover_20260914
G=$R/repair_zero_success_20260916/grounded_run_20260925
O=$G/train_gas500_mild_v1
C=$G/source/mod4
PY=/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python
while true; do
 S=$($PY -c 'import json,sys;print(json.load(open(sys.argv[1]))["status"])' "$O/stage_status.json")
 if [ "$S" != STARTING ]; then break; fi
 sleep 30
done
CK=$($PY -c 'import json,sys;print(json.load(open(sys.argv[1])).get("latest_checkpoint", ""))' "$O/stage_status.json")
test -f "$CK"
export OMNI_KIT_ACCEPT_EULA=YES PYTHONUNBUFFERED=1 CUDA_VISIBLE_DEVICES=0
export RM_WORKSPACE_ROOT=$R/env_scaling_20260915/source
export RM_MOD4_USD=$R/repair_1536_20260915/asset/robot_tireload12_mat3.usd
export RM_MOD4_MAP=rmuc2026 RM_MOD4_TERRAIN=field RM_ROUTE_KINDS=run RM_ROUTE_WEIGHTS=run:1
export RM_GAS_FORCE_DR=1 RM_GAS_FORCE_NOMINAL_N=500 RM_GAS_FORCE_MIN_N=500 RM_GAS_FORCE_MAX_N=500
flock -x /tmp/mod4_takeover_gpu0.lock bash -c '
 set -e
 "$1" "$2/eval_episodes_mod4_gas.py" --headless --checkpoint "$3" --num_envs 256 --steps 1500 --seed 20260917 --report "$4/nominal_fixed500.json" > "$4/nominal_fixed500.log" 2>&1
 "$1" "$2/eval_episodes_mod4_gas.py" --headless --checkpoint "$3" --num_envs 256 --steps 1500 --seed 20260917 --domain_rand --report "$4/mild_fixed500.json" > "$4/mild_fixed500.log" 2>&1
 export RM_GAS_FORCE_MIN_N=300 RM_GAS_FORCE_MAX_N=700
 "$1" "$2/eval_episodes_mod4_gas.py" --headless --checkpoint "$3" --num_envs 256 --steps 1500 --seed 20260917 --domain_rand --report "$4/mild_gas300_700.json" > "$4/mild_gas300_700.log" 2>&1
' bash "$PY" "$C" "$CK" "$O"
echo "DONE $(date -Is) $CK"
