#!/usr/bin/env bash
set -euo pipefail
cd '/home/egde/rl_candidates/MOD4_scut_continue10h_20260929'
python3 - <<'PY'
import json,pathlib,time
r=pathlib.Path.cwd();s=json.loads((r/'status.json').read_text())
print('Read at',time.strftime('%Y-%m-%d %H:%M:%S %z'))
keys=['stage','iteration','training_pid','attempt','speed_limit_m_s','latest_checkpoint','log_dir','deadline_epoch','evaluation_pid','evaluation_path','error','evaluation_error']
print(json.dumps({k:s.get(k) for k in keys},ensure_ascii=False,indent=2))
print('Remaining wall seconds:',max(0,s['deadline_epoch']-time.time()))
e=s.get('final_evaluation') or s.get('latest_evaluation') or {}
print('Evaluation',e.get('checkpoint'),e.get('seed'),e.get('seconds'))
for g in e.get('groups',[]):
 print({k:g.get(k) for k in ['command_vx','profile','survival_fraction','strict_pass_window','strict_pass_instant_legacy','speed','vel_error','tilt','height_error','both_wheels_scut_history','delta','d2','stop_abs_speed']})
print('physics',e.get('physics_pass'),'closure',e.get('max_closure_after_grace_m'),'mimic',e.get('max_mimic_after_grace_rad'))
PY
nvidia-smi --query-gpu=utilization.gpu,memory.used,temperature.gpu --format=csv,noheader
ps -eo pid,etime,args | grep -E 'supervise_speed.py|train_mod4_ppo.py|validate_speed.py|validate_rescue.py' | grep -v grep || true
