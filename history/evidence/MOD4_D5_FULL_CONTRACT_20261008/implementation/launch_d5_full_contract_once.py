"""New bounded D5 authority at the natural D4 full-save/exit/two-lock boundary."""
from pathlib import Path
import sys,json,shlex
D=Path(__file__).resolve().parent;R=D/'reports';assert not (R/'D5_LAUNCHED.json').exists()
assert json.loads((R/'STAGED_D5_FULL_CONTRACT.json').read_text(encoding='utf8'))['controller_import_schema_pass']
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect()
try:
    code=r'''
from pathlib import Path
import sys,os,json,time,subprocess
D=Path('/home/egde/rl_candidates/MOD4_D5_FULL_CONTRACT_20261008');R=D/'reports'
sys.path.insert(0,str(D));sys.path.insert(0,str(D/'isaac/mod4'));import supervise_d5_path_review as w
assert not (R/'D5_LAUNCHED.json').exists() and not (R/'D5_DISPATCH_STARTED.json').exists()
w.verify();assert w.s.left()>120
env=dict(os.environ,PYTHONPATH=str(D)+os.pathsep+str(D/'isaac/mod4'),PYTHONUNBUFFERED='1')
with (D/'controller.log').open('x') as f:p=subprocess.Popen([sys.executable,str(D/'supervise_d5_path_review.py')],cwd=w.s.q.P,env=env,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
v=dict(epoch=time.time(),owner=w.identity(p.pid),source=w.fullsave(w.source(),require_spring=False),source_count=len(w.read(R/'SOURCE_FREEZE.json')['sha256']),newscope_native_then128x2_20kx4_PPO=True,preflight_weights_discarded=True,no_repeated45min_clock_trial=True,formal_stable_blocks_seconds=[7200,7200,7200],new_budget_seconds=0,waits_existing_natural_saved_boundary=True)
w.write('D5_LAUNCHED.json',v);print(json.dumps(v))
'''
    _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=60);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace')
    v=json.loads(raw);(R/'D5_LAUNCHED.json').write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(v))
finally:c.close()
