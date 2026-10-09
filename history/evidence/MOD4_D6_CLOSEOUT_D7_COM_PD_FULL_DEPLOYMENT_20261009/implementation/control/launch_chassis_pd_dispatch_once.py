"""One D7 dispatcher; waits actual D6 natural settlement and original locks."""
from pathlib import Path
import sys,json,shlex
D=Path(__file__).resolve().parent;R=D/'reports';assert not (R/'D7_LAUNCHED.json').exists()
assert json.loads((R/'STAGED_D7_FULL_CONTRACT.json').read_text())['controller_import_schema_pass'] and (R/'D7_FROZEN_BEHAVIOR_PACKAGES.json').exists()
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect()
try:
 code=r'''
from pathlib import Path
import sys,os,json,time,subprocess
D=Path('/home/egde/rl_candidates/MOD4_D7_FULL_CONTRACT_20261009');R=D/'reports';sys.path.insert(0,str(D));sys.path.insert(0,str(D/'isaac/mod4'));import supervise_d7_chassis_pd_full_contract as w
assert not (R/'D7_LAUNCHED.json').exists() and not (R/'D7_DISPATCH_STARTED.json').exists();w.verify();assert w.s.left()>120;src=w.source()
before=w.s.q.ctl.CANONICAL.read_bytes();env=dict(os.environ,PYTHONPATH=str(D)+os.pathsep+str(D/'isaac/mod4'),PYTHONUNBUFFERED='1')
with (D/'controller.log').open('x') as f:p=subprocess.Popen([sys.executable,str(D/'supervise_d7_chassis_pd_full_contract.py')],cwd=w.s.q.P,env=env,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
v=dict(epoch=time.time(),owner=w.identity(p.pid),source=w.fullsave(src,require_d7=False),source_count=277,newscope_native_then128x2_20kx4_PPO=True,preflight_weights_discarded=True,no_repeated45min_clock_trial=True,formal_stable_blocks_seconds=[7200,7200,7200],new_budget_seconds=0,waits_existing_natural_saved_boundary=True)
w.write('D7_LAUNCHED.json',v);print(json.dumps(v))
'''
 _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=60);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace');v=json.loads(raw);(R/'D7_LAUNCHED.json').write_text(json.dumps(v,indent=2),encoding='utf8')
 print(json.dumps(dict(owner=v['owner'],source=v['source']['sha256'],waits_real_D6_boundary=True,no_extra_clock_trial=True)))
finally:c.close()
