"""Launch new validated same-scope authority once at the audited idle boundary."""
from pathlib import Path
import json,sys,shlex
D=Path(__file__).resolve().parent;R=D/'reports';sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect()
try:
 code=r'''
from pathlib import Path
import sys,json,subprocess,time
D=Path('/home/egde/rl_candidates/MOD4_E0_SENSOR_CONTINUOUS_EXECUTION_20261007');sys.path.insert(0,str(D));import supervise_sensor_parallel_continuation as n
n.s.verify();assert not (D/'reports/PARALLEL_LAUNCHED.json').exists() and not (D/'parallel_controller.log').exists()
assert n.s.q.base.budget_state()['active_segment'] is None and not n.s.trainers() and not n.s.q.w.read(n.s.q.ctl.STATE_PATH).get('active_training')
with (D/'parallel_controller.log').open('x') as f:p=subprocess.Popen([n.s.q.base.PY,str(D/'supervise_sensor_parallel_continuation.py')],cwd=n.s.q.P,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
time.sleep(.5);ident=n.s.identity(p.pid);assert ident and ident['state']!='Z'
v=dict(epoch=time.time(),owner=ident,one_new_unique_entry=True,new_budget_seconds=0,no_old_entry_resumed=True,no_repeated_preflight=True)
n.s.write('PARALLEL_LAUNCHED.json',v);print(json.dumps(v))
'''
 _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=30);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode();v=json.loads(raw)
 (R/'PARALLEL_LAUNCHED.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
finally:c.close()
