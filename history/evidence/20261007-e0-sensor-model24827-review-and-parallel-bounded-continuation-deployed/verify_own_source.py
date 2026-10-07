from pathlib import Path
import json,sys,shlex
D=Path(__file__).resolve().parent;R=D/'reports';sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect()
try:
 code=r'''
from pathlib import Path
import sys,json,time,re
D=Path('/home/egde/rl_candidates/MOD4_E0_SENSOR_CONTINUOUS_EXECUTION_20261007');sys.path.insert(0,str(D));import supervise_sensor_parallel_continuation as n
state=n.s.q.w.read(D/'reports/SENSOR_STABLE_STATE.json');child=n.s.identity(state['child']['pid']);assert child and child['state']!='Z'
name=child['argv'][child['argv'].index('--run_name')+1];runs=list((D/'learning_logs').glob('*_'+name));assert len(runs)==1;run=runs[0]
m=n.s.q.w.read(run/'run_manifest.json');f=n.s.q.w.read(D/'reports/SOURCE_FREEZE.json')['sha256'];assert len(f)==208 and m['source_map']==f
for name,h in f.items():assert n.s.q.base.sha(D/name)==h,name
for name,h in m['src_sha256'].items():assert n.s.q.base.sha(run/'src_snapshot'/name)==h,name
startup=n.s.q.w.read(run/'SENSOR_RESUME_STARTUP_VERIFIED.json');source=n.s.q.w.read(n.PRIOR/'reports/SENSOR_STABLE_COMPLETE.json')['checkpoint'];assert startup['source_sha256']==source['sha256'] and startup['actor_critic_std_exact'] and startup['sensor_streams_restored'] and startup['global_CPU_CUDA_streams_restored'] and startup['new_physical_episode']
assert n.s.q.base.budget_state()['active_segment']['pid']==child['pid']
log=Path(state['active_log']).read_text(errors='replace');iterations=[int(x) for x in re.findall(r'Learning iteration\s+(\d+)',log)];assert iterations,'No completed PPO log iteration yet'
assert 'Traceback (most recent call last)' not in log
receipt=n.s.q.w.read(run/'latest_complete.json') if (run/'latest_complete.json').exists() else None
own=None
if receipt:
 assert receipt['pid']==child['pid'];own=n.s.q.base.checkpoint(Path(receipt['checkpoint']))
freeze=(run/'rolling_source_freeze.json').exists()
if freeze:assert n.s.q.w.read(run/'rolling_source_freeze.json')['sha256']==f
v=dict(epoch=time.time(),child=child,own_run=str(run),manifest_source208_exact=True,actual_src_snapshot_count=len(m['src_sha256']),all_src_snapshots_exact=True,source_init=source,startup=startup,logged_completed_updates=len(iterations),logged_new_environment_steps=len(iterations)*24*20000,first_logged_iteration=iterations[0],last_logged_iteration=iterations[-1],own_latest=receipt,own_periodic_checkpoint=own,own_runfreeze_exists=freeze,new_behavior_not_evaluated=True,new_budget_seconds=0,no_terminal_task_health_inferred_from_activity=True)
n.s.write('PARALLEL_OWN_SOURCE_VERIFIED.json',v);print(json.dumps(v))
'''
 _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=30);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode();v=json.loads(raw)
 (R/'PARALLEL_OWN_SOURCE_VERIFIED.json').write_text(json.dumps(v,indent=2));print(json.dumps({k:v[k] for k in ('epoch','own_run','manifest_source208_exact','actual_src_snapshot_count','logged_completed_updates','logged_new_environment_steps','own_periodic_checkpoint','own_runfreeze_exists')}))
finally:c.close()
