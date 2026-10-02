#!/usr/bin/env bash
set -euo pipefail
root=/home/egde/rl_candidates/MOD4_takeover_20260914
stage="$root/height32_probe_20260928"
source_ck="$root/scut_v14_strong_posture_20260928/run/scut_v14_strong_posture_20260928/segment_000/logs/2026-09-28_08-24-52_scut_flat_mod4/model_2650.pt"
out="$stage/run/height32_eval"
py=/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python
mkdir -p "$out"
while kill -0 3121204 2>/dev/null; do sleep 30; done
if [[ ! -s "$stage/run/height32_40/report.json" ]]; then
  echo "Training did not produce a complete report; preserve run and inspect logs." > "$out/INCOMPLETE.txt"
  exit 1
fi
final_ck="$($py - "$stage" <<'PY'
import glob,os,sys
files=glob.glob(sys.argv[1]+'/run/height32_40/logs/*/model_*.pt')
assert files, 'no saved checkpoint'
print(max(files,key=os.path.getmtime))
PY
)"
printf '%s\n' "$final_ck" > "$out/final_checkpoint.txt"
for pair in baseline final; do
  if [[ "$pair" == baseline ]]; then ck="$source_ck"; else ck="$final_ck"; fi
  test -s "$ck"
  report="$out/${pair}_height32_nominal.json"
  OMNI_KIT_ACCEPT_EULA=YES CUDA_VISIBLE_DEVICES=0 PYTHONUNBUFFERED=1 \
  RM_MOD4_MAP=fudan_plane RM_MOD4_TERRAIN=flat RM_HEIGHT_MIN=0.32 RM_HEIGHT_MAX=0.32 \
  RM_MOD4_USD="$stage/asset/robot_wheel_convex24.usd" \
  RM_GAS_SCUT_V14=1 RM_GAS_FORCE_DR=1 RM_GAS_FORCE_DR_ONLY=1 \
  RM_GAS_FORCE_FRAME=reference RM_GAS_FORCE_NOMINAL_N=500.58095715 \
  RM_GAS_FORCE_MIN_N=500.58095715 RM_GAS_FORCE_MAX_N=500.58095715 RM_GAS_FORCE_EDGE_PROB=0 \
  "$py" -u "$stage/source/mod4/eval_flat_diagnostics.py" --headless \
    --checkpoint "$ck" --num_envs 64 --steps 1500 --seed 20260926 \
    --report "$report" > "$out/${pair}.log" 2>&1
  test -s "$report"
done
"$py" - "$out" <<'PY'
import json,sys
from pathlib import Path
p=Path(sys.argv[1]); keys=('episode_15s_survived','episode_15s_pass','tilt_deg_rms',
'velocity_error_xy_m_s_rms','both_wheels_contact_rate','root_z_mean_m',
'action_delta_rms','action_second_diff_rms','max_closure_error_m','max_mimic_error_rad')
d={name:{k:json.loads((p/(name+'_height32_nominal.json')).read_text()).get(k) for k in keys}
   for name in ('baseline','final')}
(p/'comparison.json').write_text(json.dumps(d,indent=2)+'\n')
print(json.dumps(d,indent=2))
PY
