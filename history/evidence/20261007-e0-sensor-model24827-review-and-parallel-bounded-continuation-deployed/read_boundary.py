from pathlib import Path
import json,sys,shlex
D=Path(__file__).resolve().parent;R=D/'reports';R.mkdir(exist_ok=True)
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect()
try:
 code=r'''
from pathlib import Path
import json,sys,time,hashlib
T=Path('/home/egde/rl_candidates/MOD4_E0_SENSOR_STABLE_CONTINUATION_20261007');sys.path.insert(0,str(T));import supervise_sensor_stable_continuation as s
s.verify();row=s.q.w.read(T/'reports/SENSOR_STABLE_COMPLETE.json');p=Path(row['checkpoint']['path']);assert s.q.base.sha(p)==row['checkpoint']['sha256']
assert s.q.base.checkpoint(p)==row['checkpoint']
assert s.q.base.budget_state()['active_segment'] is None and not s.trainers() and not s.q.w.read(s.q.ctl.STATE_PATH).get('active_training')
state=s.q.w.read(T/'reports/SENSOR_STABLE_STATE.json');guard=s.q.w.read(T/'reports/SENSOR_STABLE_GUARDIAN_STARTED.json')
for old in (state['owner'],guard):
 now=s.identity(old['pid']);assert not now or now['state']=='Z' or now['start_ticks']!=old['start_ticks']
run=Path(row['run']);manifest=s.q.w.read(run/'run_manifest.json');f=s.q.w.read(T/'reports/SOURCE_FREEZE.json')['sha256']
assert manifest['source_map']==f and s.q.w.read(run/'rolling_source_freeze.json')['sha256']==f
for n,h in f.items():assert s.q.base.sha(T/n)==h,n
for n,h in manifest['src_sha256'].items():assert s.q.base.sha(run/'src_snapshot'/n)==h,n
assert [x for x in s.q.w.read(s.q.ctl.CANONICAL)['completed_segments'] if x['pid']==row['own_PID_bound_receipt']['pid']]==row['unique_completed_segment']
results=[]
for directory in ('eval_results','eval_queue'):
 p=s.ER.parent/directory
 results.append(dict(path=str(p),names=[str(x.relative_to(p)) for x in p.glob('*')][-25:]))
print(json.dumps(dict(epoch=time.time(),formal=row,source_count=len(f),old_authorities_retired=True,active=None,approval=s.q.w.read(s.ER/'PLAN_APPROVAL.json'),tracks=s.q.w.read(s.ER/'EXECUTION_TRACKS.json'),handoff=(s.ER/'LATEST_HANDOFF.md').read_text(),results=results,budget=s.q.base.budget_state(),new_training_started=False)))
'''
 _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=40);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode();v=json.loads(raw)
 (R/'BOUNDARY_VERIFIED.json').write_text(json.dumps(v,indent=2));print(json.dumps({k:v[k] for k in ('epoch','source_count','old_authorities_retired','active','results','new_training_started')}))
 with c.open_sftp() as f:
  for name in ('supervise_sensor_stable_continuation.py','isaac/mod4/test_sensor_resume_actual_cpu.py'):
   out=D/'source'/name;out.parent.mkdir(parents=True,exist_ok=True);f.get('/home/egde/rl_candidates/MOD4_E0_SENSOR_STABLE_CONTINUATION_20261007/'+name,str(out))
finally:c.close()
