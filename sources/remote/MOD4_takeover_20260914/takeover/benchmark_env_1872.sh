#!/usr/bin/env bash
set -Eeuo pipefail
ROOT=/home/egde/rl_candidates/MOD4_takeover_20260914
PY=/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python
WORK="$ROOT/env_scaling_20260915"
RAW="$WORK/raw"
RUNS="$WORK/runs"
BUILDER="$WORK/source/incoming/rmuc2026_field_20260911/rmuc2026_training/tools/build_layout.py"
CHECKPOINT="$ROOT/logs/takeover_20260914/2026-09-15_08-47-15_9_full_dr_10h/model_2775.pt"
MANIFEST="$ROOT/logs/takeover_20260914/2026-09-15_08-47-15_9_full_dr_10h/run_manifest.json"
REPORT_JSON="$ROOT/reports/env_scaling_20260915.json"
REPORT_MD="$ROOT/reports/env_scaling_20260915.md"
N=1872

exec 9>/tmp/mod4_takeover_gpu0.lock
flock -n 9 || exit 80
if pgrep -af 'train_mod4_ppo.py|eval_episodes_mod4.py|export_final_policy.py' | grep -v "$PPID" | grep -q .; then exit 81; fi
[[ -f "$BUILDER" && -f "$CHECKPOINT" && -f "$RAW/result_1536.json" ]]
python3 - "$WORK/status.json" <<'PY'
import json,sys,time
open(sys.argv[1],'w').write(json.dumps({'status':'RUNNING_1872','started_epoch':int(time.time())},indent=2)+'\n')
PY
"$PY" "$BUILDER" --num-envs "$N" > "$RAW/build_${N}.log" 2>&1
set -a
source "$ROOT/takeover/common.env"
set +a
export RM_DR_OFF=0 RM_CURR_INIT_LEVEL=2 RM_INIT_STD=0.11
export RM_ROUTE_WEIGHTS='run:3,ramp_up:5,ramp_down:2,step_up:5,step_down:2,rough_cross:6,slope_spin:6,fly_jump:6,jump_in_place:3,tunnel_cross:4'
TRAIN_LOG="$RAW/train_${N}.log"; GPU_LOG="$RAW/gpu_${N}.csv"; : > "$GPU_LOG"
set +e
timeout --signal=INT --kill-after=90 1200s "$PY" "$WORK/source/isaac/mod4/train_mod4_ppo.py" \
  --num_envs "$N" --additional_iterations 24 --save_interval 9999 --steps_per_env 24 \
  --learning_rate 0.000075 --run_name "envbench_${N}" --seed 20260924 \
  --log_root "$RUNS" --init_checkpoint "$CHECKPOINT" > "$TRAIN_LOG" 2>&1 &
train_pid=$!
(
  while kill -0 "$train_pid" 2>/dev/null; do
    nvidia-smi --query-gpu=timestamp,utilization.gpu,memory.used,power.draw --format=csv,noheader,nounits >> "$GPU_LOG" 2>/dev/null || true
    sleep 1
  done
) & monitor_pid=$!
wait "$train_pid"; rc=$?
kill "$monitor_pid" 2>/dev/null || true; wait "$monitor_pid" 2>/dev/null || true
set -e
python3 - "$RAW/result_${N}.json" "$N" "$rc" "$TRAIN_LOG" "$GPU_LOG" <<'PY'
import csv,json,re,statistics,sys
out,n,rc,logp,gpup=sys.argv[1],int(sys.argv[2]),int(sys.argv[3]),sys.argv[4],sys.argv[5]
text=open(logp,encoding='utf8',errors='replace').read()
speeds=[int(x) for x in re.findall(r'Steps per second:\s*(\d+)',text)]
times=[float(x) for x in re.findall(r'Iteration time:\s*([0-9.]+)s',text)]
clos=[float(x) for x in re.findall(r'Metrics/plant/closure_err_max_m:\s*([0-9.eE+-]+)',text)]
mim=[float(x) for x in re.findall(r'Metrics/plant/mimic_err_max_rad:\s*([0-9.eE+-]+)',text)]
rows=[]
for row in csv.reader(open(gpup,newline='')):
  if len(row)>=4: rows.append((float(row[1]),float(row[2]),float(row[3])))
steady=speeds[5:] if len(speeds)>5 else speeds; active=[r for r in rows if r[0]>=10]
fatal=bool(re.search(r'CUDA out of memory|Traceback \(most recent call last\)|NaN detected|nonfinite|limit of 64K materials',text,re.I))
d={'num_envs':n,'status':'PASS' if rc==0 and len(steady)>=10 and not fatal else 'FAIL','rc':rc,
   'iterations_seen':len(speeds),'steady_steps_per_s_mean':statistics.mean(steady) if steady else None,
   'steady_steps_per_s_median':statistics.median(steady) if steady else None,
   'iteration_s_mean':statistics.mean(times[5:] if len(times)>5 else times) if times else None,
   'gpu_util_active_mean_pct':statistics.mean(x[0] for x in active) if active else None,
   'gpu_util_max_pct':max((x[0] for x in rows),default=None),'vram_peak_mib':max((x[1] for x in rows),default=None),
   'power_active_mean_w':statistics.mean(x[2] for x in active) if active else None,
   'power_peak_w':max((x[2] for x in rows),default=None),'closure_err_max_m':max(clos,default=None),
   'mimic_err_max_rad':max(mim,default=None),'fatal_signature':fatal,'train_log':logp,'gpu_log':gpup}
json.dump(d,open(out,'w'),indent=2)
PY
python3 - "$RAW" "$REPORT_JSON" "$REPORT_MD" "$CHECKPOINT" "$MANIFEST" <<'PY'
from pathlib import Path
import hashlib,json,sys,time
raw=Path(sys.argv[1]); rows=[]
for n in (1536,1872):
 p=raw/f'result_{n}.json'
 if p.exists(): rows.append(json.loads(p.read_text()))
errp=raw/'train_2048.log'; errtxt=errp.read_text(errors='replace') if errp.exists() else ''
rows.append({'num_envs':2048,'status':'FAIL','failure':'PhysX 64K material limit',
             'material_limit_errors':errtxt.count('limit of 64K materials reached'),'train_log':str(errp)})
passed=[r for r in rows if r.get('status')=='PASS']
best=max(passed,key=lambda r:r.get('steady_steps_per_s_mean',0)) if passed else None
d={'status':'COMPLETE','completed_epoch':int(time.time()),'checkpoint':sys.argv[4],'manifest':sys.argv[5],
   'checkpoint_sha256':hashlib.sha256(Path(sys.argv[4]).read_bytes()).hexdigest(),
   'recommended_num_envs':best['num_envs'] if best else None,
   'maximum_stable_tested_num_envs':max((r['num_envs'] for r in passed),default=None),
   'current_hard_limit':'PhysX 64K materials; 2048 invalid','results':rows}
Path(sys.argv[2]).write_text(json.dumps(d,indent=2)+'\n')
lines=['# MOD4 environment scaling benchmark','',f"- Recommended tested envs: **{d['recommended_num_envs']}**",
f"- Maximum stable tested envs: **{d['maximum_stable_tested_num_envs']}**",'- 2048 env: **FAIL — PhysX 64K material limit**','',
'| envs | status | steady steps/s | iter s | GPU % | VRAM MiB | power W | closure m | mimic rad |','|---:|---|---:|---:|---:|---:|---:|---:|---:|']
for r in rows:
 def f(k,p=2):
  v=r.get(k); return '' if v is None else f'{v:.{p}f}'
 lines.append(f"| {r['num_envs']} | {r['status']} | {f('steady_steps_per_s_mean',0)} | {f('iteration_s_mean')} | {f('gpu_util_active_mean_pct',1)} | {f('vram_peak_mib',0)} | {f('power_active_mean_w',1)} | {f('closure_err_max_m',6)} | {f('mimic_err_max_rad',6)} |")
Path(sys.argv[3]).write_text('\n'.join(lines)+'\n')
PY
python3 - "$WORK/status.json" <<'PY'
import json,sys,time
open(sys.argv[1],'w').write(json.dumps({'status':'COMPLETE','completed_epoch':int(time.time())},indent=2)+'\n')
PY
