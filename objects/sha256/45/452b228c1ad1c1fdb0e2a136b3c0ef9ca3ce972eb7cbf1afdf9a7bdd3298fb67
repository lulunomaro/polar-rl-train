#!/usr/bin/env bash
set -Eeuo pipefail

ROOT=/home/egde/rl_candidates/MOD4_takeover_20260914
PY=/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python
STATUS="$ROOT/logs/takeover_20260914/supervisor/STATUS.json"
WORK="$ROOT/env_scaling_20260915"
RUNS="$WORK/runs"
RAW="$WORK/raw"
REPORTS="$ROOT/reports"
REPORT_JSON="$REPORTS/env_scaling_20260915.json"
REPORT_MD="$REPORTS/env_scaling_20260915.md"
CHECKPOINT="$ROOT/logs/takeover_20260914/2026-09-15_08-47-15_9_full_dr_10h/model_2775.pt"
MANIFEST="$ROOT/logs/takeover_20260914/2026-09-15_08-47-15_9_full_dr_10h/run_manifest.json"
mkdir -p "$WORK" "$REPORTS"

exec 9>/tmp/mod4_takeover_gpu0.lock
flock -n 9 || { echo 'GPU0 is owned by another MOD4 job' >&2; exit 80; }
if pgrep -af 'train_mod4_ppo.py|eval_episodes_mod4.py|export_final_policy.py' | grep -v "$PPID" | grep -q .; then
  echo 'refusing to share GPU with another Isaac job' >&2
  exit 81
fi
python3 - "$STATUS" <<'PY'
import json,sys
d=json.load(open(sys.argv[1],encoding='utf8'))
assert d.get('status') == 'RESUME10H_COMPLETE', d
PY
[[ -f "$CHECKPOINT" && -f "$MANIFEST" ]]

# Isolated source/layout copy.  Formal training assets and checkpoints remain read-only.
rm -rf "$WORK/source" "$RUNS" "$RAW"
mkdir -p "$WORK/source/isaac" "$WORK/source/incoming" "$WORK/source/train/deploy" "$RUNS" "$RAW"
cp -a "$ROOT/isaac/mod4" "$WORK/source/isaac/"
cp -a "$ROOT/isaac/rmuc2026_field.py" "$WORK/source/isaac/"
cp -a "$ROOT/incoming/rmuc2026_field_20260911" "$WORK/source/incoming/"
cp -a "$ROOT/train/deploy/contract_rm2025_later.json" "$WORK/source/train/deploy/"
if [[ -d "$ROOT/cad" ]]; then ln -s "$ROOT/cad" "$WORK/source/cad"; fi
BUILDER="$WORK/source/incoming/rmuc2026_field_20260911/rmuc2026_training/tools/build_layout.py"
python3 - "$BUILDER" <<'PY'
from pathlib import Path
import sys
p=Path(sys.argv[1]); s=p.read_text()
s2=s.replace('Create 1..1024 full-arena instances','Create 1..8192 full-arena instances')
s2=s2.replace("if not 1<=num_envs<=1024:raise ValueError('Supported packaged layout range: 1..1024')",
              "if not 1<=num_envs<=8192:raise ValueError('Benchmark layout range: 1..8192')")
if s2==s or 'num_envs<=8192' not in s2:
    raise SystemExit('failed to patch isolated layout guard')
p.write_text(s2)
PY

sha256sum "$CHECKPOINT" "$MANIFEST" "$BUILDER" > "$WORK/INPUTS.sha256"
date -Is > "$WORK/started.txt"
python3 - "$WORK/status.json" <<'PY'
import json,sys,time
open(sys.argv[1],'w').write(json.dumps({'status':'RUNNING','started_epoch':int(time.time())},indent=2)+'\n')
PY

set -a
source "$ROOT/takeover/common.env"
set +a
export RM_DR_OFF=0 RM_CURR_INIT_LEVEL=2 RM_INIT_STD=0.11 TAKEOVER_NUM_ENVS=1024
export RM_ROUTE_WEIGHTS='run:3,ramp_up:5,ramp_down:2,step_up:5,step_down:2,rough_cross:6,slope_spin:6,fly_jump:6,jump_in_place:3,tunnel_cross:4'

extended_ok=1
for n in 1536 2048 3072 4096; do
  if (( n > 1024 && extended_ok == 0 )); then break; fi
  echo "[$(date -Is)] begin envs=$n" | tee -a "$WORK/timeline.log"
  MAP_ROOT="$WORK/source/incoming/rmuc2026_field_20260911/rmuc2026_training"
  set +e
  "$PY" "$BUILDER" --num-envs "$n" > "$RAW/build_${n}.log" 2>&1
  build_rc=$?
  set -e
  if (( build_rc != 0 )); then
    python3 - "$RAW/result_${n}.json" "$n" "$build_rc" <<'PY'
import json,sys
json.dump({'num_envs':int(sys.argv[2]),'status':'BUILD_FAILED','rc':int(sys.argv[3])},open(sys.argv[1],'w'),indent=2)
PY
    (( n > 1024 )) && extended_ok=0
    continue
  fi

  TRAIN_LOG="$RAW/train_${n}.log"
  GPU_LOG="$RAW/gpu_${n}.csv"
  : > "$GPU_LOG"
  set +e
  timeout --signal=INT --kill-after=90 1200s "$PY" "$WORK/source/isaac/mod4/train_mod4_ppo.py" \
    --num_envs "$n" --additional_iterations 24 --save_interval 9999 --steps_per_env 24 \
    --learning_rate 0.000075 --run_name "envbench_${n}" --seed 20260924 \
    --log_root "$RUNS" --init_checkpoint "$CHECKPOINT" > "$TRAIN_LOG" 2>&1 &
  train_pid=$!
  (
    while kill -0 "$train_pid" 2>/dev/null; do
      nvidia-smi --query-gpu=timestamp,utilization.gpu,memory.used,power.draw --format=csv,noheader,nounits >> "$GPU_LOG" 2>/dev/null || true
      sleep 1
    done
  ) & monitor_pid=$!
  wait "$train_pid"; rc=$?
  kill "$monitor_pid" 2>/dev/null || true
  wait "$monitor_pid" 2>/dev/null || true
  set -e

  python3 - "$RAW/result_${n}.json" "$n" "$rc" "$TRAIN_LOG" "$GPU_LOG" <<'PY'
import csv,json,re,statistics,sys
out,n,rc,logp,gpup=sys.argv[1],int(sys.argv[2]),int(sys.argv[3]),sys.argv[4],sys.argv[5]
text=open(logp,encoding='utf8',errors='replace').read()
speeds=[int(x) for x in re.findall(r'Steps per second:\s*(\d+)',text)]
times=[float(x) for x in re.findall(r'Iteration time:\s*([0-9.]+)s',text)]
clos=[float(x) for x in re.findall(r'Metrics/plant/closure_err_max_m:\s*([0-9.eE+-]+)',text)]
mim=[float(x) for x in re.findall(r'Metrics/plant/mimic_err_max_rad:\s*([0-9.eE+-]+)',text)]
rows=[]
try:
  with open(gpup,newline='') as f:
    for row in csv.reader(f):
      if len(row)>=4:
        rows.append((float(row[1]),float(row[2]),float(row[3])))
except FileNotFoundError: pass
steady=speeds[5:] if len(speeds)>5 else speeds
active=[r for r in rows if r[0]>=10]
fatal=bool(re.search(r'CUDA out of memory|Traceback \(most recent call last\)|NaN detected|nonfinite|PxPhysics::createMaterial.*64K',text,re.I))
d={'num_envs':n,'status':'PASS' if rc==0 and len(steady)>=10 and not fatal else 'FAIL','rc':rc,
   'iterations_seen':len(speeds),'steady_steps_per_s_mean':statistics.mean(steady) if steady else None,
   'steady_steps_per_s_median':statistics.median(steady) if steady else None,
   'iteration_s_mean':statistics.mean(times[5:] if len(times)>5 else times) if times else None,
   'gpu_util_active_mean_pct':statistics.mean(x[0] for x in active) if active else None,
   'gpu_util_max_pct':max((x[0] for x in rows),default=None),
   'vram_peak_mib':max((x[1] for x in rows),default=None),
   'power_active_mean_w':statistics.mean(x[2] for x in active) if active else None,
   'power_peak_w':max((x[2] for x in rows),default=None),
   'closure_err_max_m':max(clos,default=None),'mimic_err_max_rad':max(mim,default=None),
   'fatal_signature':fatal,'train_log':logp,'gpu_log':gpup}
json.dump(d,open(out,'w'),indent=2)
print(json.dumps(d))
PY
  status=$(python3 -c "import json;print(json.load(open('$RAW/result_${n}.json'))['status'])")
  echo "[$(date -Is)] end envs=$n rc=$rc status=$status" | tee -a "$WORK/timeline.log"
  if [[ "$status" != PASS ]]; then extended_ok=0; break; fi
done

python3 - "$RAW" "$REPORT_JSON" "$REPORT_MD" "$CHECKPOINT" "$MANIFEST" <<'PY'
from pathlib import Path
import datetime,hashlib,json,sys,time
raw=Path(sys.argv[1]); jp=Path(sys.argv[2]); mp=Path(sys.argv[3])
rows=[json.loads(p.read_text()) for p in raw.glob('result_*.json')]
rows.sort(key=lambda x:x['num_envs'])
passed=[r for r in rows if r.get('status')=='PASS' and r.get('steady_steps_per_s_mean') is not None]
best=max(passed,key=lambda r:r['steady_steps_per_s_mean']) if passed else None
d={'status':'COMPLETE','completed_epoch':int(time.time()),'checkpoint':sys.argv[4],'manifest':sys.argv[5],
   'checkpoint_sha256':hashlib.sha256(Path(sys.argv[4]).read_bytes()).hexdigest(),
   'selection_rule':'maximum stable policy environment steps/s; physics correctness required',
   'recommended_num_envs':best['num_envs'] if best else None,
   'maximum_stable_num_envs':max((r['num_envs'] for r in passed),default=None),'results':rows}
jp.write_text(json.dumps(d,indent=2)+'\n')
lines=['# MOD4 environment scaling benchmark','',f"- Recommended envs: **{d['recommended_num_envs']}**",
       f"- Maximum stable envs: **{d['maximum_stable_num_envs']}**",'',
       '| envs | status | steady steps/s | iter s | GPU % | VRAM MiB | power W | closure m | mimic rad |',
       '|---:|---|---:|---:|---:|---:|---:|---:|---:|']
for r in rows:
  def f(k,p=2):
    v=r.get(k); return '' if v is None else f'{v:.{p}f}'
  lines.append(f"| {r['num_envs']} | {r['status']} | {f('steady_steps_per_s_mean',0)} | {f('iteration_s_mean')} | {f('gpu_util_active_mean_pct',1)} | {f('vram_peak_mib',0)} | {f('power_active_mean_w',1)} | {f('closure_err_max_m',6)} | {f('mimic_err_max_rad',6)} |")
mp.write_text('\n'.join(lines)+'\n')
PY
python3 - "$WORK/status.json" <<'PY'
import json,sys,time
p=sys.argv[1];d=json.load(open(p));d.update(status='COMPLETE',completed_epoch=int(time.time()));open(p,'w').write(json.dumps(d,indent=2)+'\n')
PY
date -Is > "$WORK/completed.txt"
