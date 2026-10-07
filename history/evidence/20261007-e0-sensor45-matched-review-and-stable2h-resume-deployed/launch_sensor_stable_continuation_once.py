"""Launch only the newly frozen same-scope authority at the saved boundary."""
from pathlib import Path
import sys,json,shlex
D=Path(__file__).resolve().parent;R=D/'reports';W=D.parent
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect()
try:
 code=r'''
from pathlib import Path
import sys,json,subprocess,time,os
D=Path('/home/egde/rl_candidates/MOD4_E0_SENSOR_STABLE_CONTINUATION_20261007');R=D/'reports';sys.path.insert(0,str(D))
import supervise_sensor_stable_continuation as s
assert not (R/'SENSOR_STABLE_LAUNCHED.json').exists();s.verify()
assert s.q.base.budget_state()['active_segment'] is None and not s.trainers() and not s.q.w.read(s.q.ctl.STATE_PATH).get('active_training')
before=s.q.ctl.CANONICAL.read_bytes()
with (D/'controller.log').open('x') as f:p=subprocess.Popen([s.q.base.PY,str(D/'supervise_sensor_stable_continuation.py')],cwd=s.q.P,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
time.sleep(.4);actual=s.identity(p.pid);assert actual and actual['state']!='Z'
receipt=dict(epoch=time.time(),owner=actual,one_new_unique_entry=True,prior_full_boundary=True,no_repeated_PPO_preflight=True,canonical_unchanged_during_CPU_launch=before==s.q.ctl.CANONICAL.read_bytes())
s.write('SENSOR_STABLE_LAUNCHED.json',receipt);print(json.dumps(receipt))
'''
 _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=30);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode();v=json.loads(raw)
 (R/'SENSOR_STABLE_LAUNCHED.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
finally:c.close()
