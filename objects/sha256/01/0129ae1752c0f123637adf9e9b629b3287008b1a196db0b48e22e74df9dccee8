#!/usr/bin/env bash
set -euo pipefail
root=/home/egde/rl_candidates/MOD4_takeover_20260914
stage="$root/scut_v14_strong_posture_20260928"
base="$root/scut_v14_spring_mod4_20260928/run/scut_v14_linear_spring_continue_20260928/segment_000/logs/2026-09-28_02-27-38_scut_flat_mod4/model_2610.pt"
out="$stage/run/posture_pair_eval"
py=/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python
mkdir -p "$out"
test -s "$base"
test -f "$stage/run/scut_v14_strong_posture_20260928/status.json"
final="$($py - "$stage" <<'PY'
import glob,os,sys
paths=glob.glob(sys.argv[1]+'/run/scut_v14_strong_posture_20260928/segment_*/logs/*/model_*.pt')
assert paths
print(max(paths,key=os.path.getmtime))
PY
)"
echo "$final" > "$out/final_checkpoint.txt"
for pair in baseline final; do
  if [[ "$pair" == baseline ]]; then ck="$base"; else ck="$final"; fi
  for mode in nominal spring300_700; do
    if [[ "$mode" == nominal ]]; then
      low=500.58095715; high=500.58095715; dr=()
    else
      low=300; high=700; dr=(--domain_rand)
    fi
    report="$out/${pair}_${mode}.json"
    if [[ -s "$report" ]]; then continue; fi
    OMNI_KIT_ACCEPT_EULA=YES CUDA_VISIBLE_DEVICES=0 PYTHONUNBUFFERED=1 \
    RM_MOD4_MAP=fudan_plane RM_MOD4_TERRAIN=flat \
    RM_MOD4_USD="$stage/asset/robot_wheel_convex24.usd" \
    RM_GAS_SCUT_V14=1 RM_GAS_FORCE_DR=1 RM_GAS_FORCE_DR_ONLY=1 \
    RM_GAS_FORCE_FRAME=reference RM_GAS_FORCE_NOMINAL_N=500.58095715 \
    RM_GAS_FORCE_MIN_N="$low" RM_GAS_FORCE_MAX_N="$high" RM_GAS_FORCE_EDGE_PROB=0 \
    "$py" -u "$stage/source/mod4/eval_flat_diagnostics.py" --headless \
      --checkpoint "$ck" --num_envs 64 --steps 1500 --seed 20260926 \
      --report "$report" "${dr[@]}" > "$out/${pair}_${mode}.log" 2>&1
    test -s "$report"
  done
done
"$py" - "$out" <<'PY'
import json,sys
from pathlib import Path
root=Path(sys.argv[1]); rows={}
keys=('episode_15s_survived','episode_15s_pass','tilt_deg_rms',
      'velocity_error_xy_m_s_rms','both_wheels_contact_rate','root_z_mean_m',
      'action_delta_rms','action_second_diff_rms','max_closure_error_m',
      'max_mimic_error_rad','gas_elastic_force_min_n','gas_elastic_force_max_n')
for stem in ('baseline_nominal','final_nominal','baseline_spring300_700','final_spring300_700'):
    p=root/(stem+'.json'); x=json.loads(p.read_text())
    rows[stem]={'checkpoint':x['checkpoint'],'sha256':x['checkpoint_sha256'],
                'num_envs':x['num_envs'],'steps':x['steps'],
                **{k:x.get(k) for k in keys}}
(root/'comparison.json').write_text(json.dumps(rows,indent=2)+'\n')
print(json.dumps(rows,indent=2))
PY
