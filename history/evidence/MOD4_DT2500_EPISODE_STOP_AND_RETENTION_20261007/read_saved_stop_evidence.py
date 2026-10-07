"""Read final stop diagnostics, full-save identity and runtime; no launch or writes remotely."""
from pathlib import Path
import sys, json, shlex, hashlib
D=Path(__file__).resolve().parent; R=D/'reports'
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'))
from remote_io import connect
c=connect()
try:
 code=r'''
from pathlib import Path
import sys,json,re,hashlib
D=Path('/home/egde/rl_candidates/MOD4_E0_DT2500_ENV20K_CONTINUATION_20261007');sys.path.insert(0,str(D));import supervise_dt2500_env20k_continuation as w
s=w.s;read=s.q.w.read
saved=read(D/'reports/env20k_S2_D1D2_stable2h_SAVED_EXIT.json');run=Path(saved['run']);p=Path(saved['checkpoint']['path']);receipt=read(run/'latest_complete.json');m=read(run/'run_manifest.json');f=read(D/'reports/SOURCE_FREEZE.json')['sha256']
assert receipt['pid']==918339 and receipt['checkpoint']==str(p)
assert m['source_map']==f and read(run/'rolling_source_freeze.json')['sha256']==f
for n,h in f.items():assert s.q.base.sha(D/n)==h,n
for n,h in m['src_sha256'].items():assert s.q.base.sha(run/'src_snapshot'/n)==h,n
own=s.fullsave(p);assert own==saved['checkpoint']
log=Path(read(D/'reports/SOLVER32_TRAINING_STATE.json')['active_log']);lines=log.read_text(errors='replace').splitlines();iteration=None;nonzero=[]
for i,line in enumerate(lines):
 if 'Learning iteration ' in line:iteration=line.strip()
 if 'Episode_Termination/' in line:
  try:value=float(line.rsplit(':',1)[1].strip())
  except ValueError:continue
  if value and 'time_out' not in line:nonzero.append(dict(iteration=iteration,line_number=i+1,value=value,line=line.strip(),context=lines[max(0,i-3):i+4]))
events=list(run.glob('events.out.tfevents.*'));tb={}
if events:
 from tensorboard.backend.event_processing.event_accumulator import EventAccumulator
 a=EventAccumulator(str(run),size_guidance={'scalars':0});a.Reload()
 for tag in a.Tags()['scalars']:
  if 'Termination' in tag or 'closure_err_session' in tag:
   vals=a.Scalars(tag);hits=[dict(wall_time=x.wall_time,step=x.step,value=x.value) for x in vals if x.value!=0 and 'time_out' not in tag]
   tb[tag]=dict(count=len(vals),maximum=max((x.value for x in vals),default=None),nonzero=hits if 'Termination' in tag else hits[-3:])
source={n:(D/'isaac/mod4'/n).read_text() for n in ('clock_training_health.py','mod4_task.py')}
out=dict(saved=saved,own_full_CPU=own,receipt=receipt,own_manifest=m,all213_and_own_snapshot_exact=True,health=read(run/'CLOCK_TRAINING_HEALTH.json'),S_active_training=read(s.q.ctl.STATE_PATH).get('active_training'),actual_trainers=s.trainers(),unique_completed_segment=saved['unique_completed_segment'],nonzero_termination_log=nonzero,tensorboard=tb,run_files=[x.name for x in run.iterdir()],sources=source,stop_file=(run/'STOP_AFTER_SAVE').read_text())
print(json.dumps(out))
'''
 _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=60);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace')
 v=json.loads(raw);(R/'SAVED_STOP_SOURCE_ACTUAL.json').write_text(json.dumps(v,indent=2),encoding='utf8')
 print(json.dumps({k:v[k] for k in ('own_full_CPU','health','S_active_training','actual_trainers','nonzero_termination_log','tensorboard','run_files','stop_file')},ensure_ascii=False))
finally:c.close()
