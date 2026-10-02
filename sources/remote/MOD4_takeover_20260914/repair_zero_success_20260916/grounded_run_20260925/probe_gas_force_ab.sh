#!/usr/bin/env bash
set -euo pipefail
R=/home/egde/rl_candidates/MOD4_takeover_20260914
G=$R/repair_zero_success_20260916/grounded_run_20260925
C=$G/source/mod4
PY=/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python
CK=$(find "$G/train_d08/logs" -name model_10.pt -print -quit)
test -f "$CK"
export OMNI_KIT_ACCEPT_EULA=YES PYTHONUNBUFFERED=1 CUDA_VISIBLE_DEVICES=0
export RM_WORKSPACE_ROOT=$R/env_scaling_20260915/source
export RM_MOD4_USD=$R/repair_1536_20260915/asset/robot_tireload12_mat3.usd
export RM_MOD4_MAP=rmuc2026 RM_MOD4_TERRAIN=field RM_ROUTE_KINDS=run RM_ROUTE_WEIGHTS=run:1
export RM_RUN_HEIGHT_CMD=0.34 RM_RUN_SPEED_MAX=1.20
export RM_GAS_FORCE_DR=0
"$PY" "$C/eval_episodes_mod4_gas.py" --headless --checkpoint "$CK" --num_envs 128 --steps 600 --seed 20260917 --report "$G/gas_ab_baseline.json" > "$G/gas_ab_baseline.log" 2>&1
export RM_GAS_FORCE_DR=1 RM_GAS_FORCE_NOMINAL_N=500
"$PY" "$C/eval_episodes_mod4_gas.py" --headless --checkpoint "$CK" --num_envs 128 --steps 600 --seed 20260917 --report "$G/gas_ab_500ref.json" > "$G/gas_ab_500ref.log" 2>&1
"$PY" - "$G" <<'PY'
import json,sys
from pathlib import Path
g=Path(sys.argv[1])
for name in ('gas_ab_baseline','gas_ab_500ref'):
 d=json.loads((g/(name+'.json')).read_text())
 s=d['state_stability']; f=d['gas_elastic_force_audit']
 print(name, 'tilt',round(s['tilt_deg_rms'],3),'root',round(s['root_height_above_route_ground_m_mean'],4),'both_wheel',round(s['both_drive_wheels_contact_rate'],3),'guide',round(s['guide_contact_rate'],3),'gas',round(f['mean_n'],1),round(f['minimum_n'],1),round(f['maximum_n'],1),'outside',round(f['fraction_outside_300_700'],3))
PY
