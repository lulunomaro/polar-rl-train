"""Read real identities and own run artifacts; never launches/restarts a worker."""
from pathlib import Path
import sys,json,shlex
D=Path(__file__).resolve().parent;R=D/'reports';W=D.parent
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect()
try:
 code=r'''
from pathlib import Path
import sys,json,time
D=Path('/home/egde/rl_candidates/MOD4_E0_SENSOR_STABLE_CONTINUATION_20261007');sys.path.insert(0,str(D));import supervise_sensor_stable_continuation as s
rows={p.name:s.q.w.read(p) for p in (D/'reports').glob('*.json') if p.stat().st_size<3000000};state=rows.get('SENSOR_STABLE_STATE.json',{})
own=state.get('owner');child=state.get('child');runs=[]
for run in (D/'learning_logs').glob('*'):
 r=dict(path=str(run))
 for name in ('run_manifest.json','latest_complete.json','CLOCK_TRAINING_HEALTH.json','SENSOR_RESUME_STARTUP_VERIFIED.json','rolling_source_freeze.json'):
  if (run/name).exists():r[name]=s.q.w.read(run/name)
 runs.append(r)
budget=s.q.base.budget_state();a=budget['active_segment'];remaining=budget['remaining_training_seconds']-(max(0,time.time()-a['accounted_through_epoch']) if a else 0)
logs={p.name:[x[:500] for x in p.read_text(errors='replace').splitlines()[-12:]] for p in D.glob('*.log')}
actual=dict(epoch=time.time(),phase=state.get('phase'),owner=s.identity(own['pid']) if own else None,child=s.identity(child['pid']) if child else None,guardian=s.identity(rows['SENSOR_STABLE_GUARDIAN_STARTED.json']['pid']) if 'SENSOR_STABLE_GUARDIAN_STARTED.json' in rows else None,trainers=s.trainers(),rows=rows,runs=runs,logs=logs,budget=budget,actual_remaining_seconds=remaining,Sactive=s.q.w.read(s.q.ctl.STATE_PATH).get('active_training'))
print(json.dumps(actual))
'''
 _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=30);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode();v=json.loads(raw)
 (R/'SENSOR_STABLE_CURRENT_ACTUAL.json').write_text(json.dumps(v,indent=2));print(json.dumps(dict(epoch=v['epoch'],phase=v['phase'],owner=v['owner'],child=v['child'],guardian=v['guardian'],attention=v['rows'].get('SENSOR_STABLE_ATTENTION.json'),ownruns=[dict(path=x['path'],startup_verified='SENSOR_RESUME_STARTUP_VERIFIED.json' in x,complete=x.get('latest_complete.json'),freeze_exists='rolling_source_freeze.json' in x) for x in v['runs']],active=v['budget']['active_segment'],remaining=v['actual_remaining_seconds'],logs=v['logs'])))
finally:c.close()
