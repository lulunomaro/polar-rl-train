"""Reusable read-only current identity/source/own-save inspection."""
from pathlib import Path
import json,sys,shlex
D=Path(__file__).resolve().parent;R=D/'reports';sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect()
try:
 code=r'''
from pathlib import Path
import sys,json,time
D=Path('/home/egde/rl_candidates/MOD4_E0_SENSOR_CONTINUOUS_EXECUTION_20261007');sys.path.insert(0,str(D));import supervise_sensor_parallel_continuation as n
rows={p.name:n.s.q.w.read(p) for p in (D/'reports').glob('*.json')};state=rows.get('SENSOR_STABLE_STATE.json',{});owner=rows.get('PARALLEL_STARTED.json',{}).get('owner');guard=rows.get('PARALLEL_GUARDIAN_STARTED.json');child=state.get('child')
runs=[]
for run in (D/'learning_logs').glob('*'):
 row=dict(path=str(run))
 for name in ('run_manifest.json','latest_complete.json','SENSOR_RESUME_STARTUP_VERIFIED.json','rolling_source_freeze.json','CLOCK_TRAINING_HEALTH.json'):
  if (run/name).exists():row[name]=n.s.q.w.read(run/name)
 runs.append(row)
logs={p.name:p.read_text(errors='replace').splitlines()[-35:] for p in D.glob('*.log')}
v=dict(epoch=time.time(),phase=state.get('phase'),owner=n.s.identity(owner['pid']) if owner else None,guardian=n.s.identity(guard['pid']) if guard else None,child=n.s.identity(child['pid']) if child else None,rows=rows,runs=runs,logs=logs,budget=n.s.q.base.budget_state(),Sactive=n.s.q.w.read(n.s.q.ctl.STATE_PATH).get('active_training'),window_spent_seconds=n.spent())
print(json.dumps(v))
'''
 _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=30);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode();v=json.loads(raw)
 (R/'CURRENT_ACTUAL.json').write_text(json.dumps(v,indent=2));print(json.dumps(dict(epoch=v['epoch'],phase=v['phase'],owner=v['owner'],guardian=v['guardian'],child=v['child'],attention=v['rows'].get('PARALLEL_ATTENTION.json'),reader_attention=v['rows'].get('ASYNC_READER_ATTENTION.json'),run_paths=[dict(path=x['path'],own_latest=x.get('latest_complete.json'),startup=x.get('SENSOR_RESUME_STARTUP_VERIFIED.json',{}).get('actor_critic_std_exact'),freeze='rolling_source_freeze.json' in x) for x in v['runs']],logs=v['logs'],active=v['budget']['active_segment'])))
finally:c.close()
