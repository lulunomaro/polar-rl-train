from pathlib import Path
import sys,shlex,json
D=Path(__file__).resolve().parent;R=D/'reports';assert not (R/'FROZEN_PROTOCOL_REVIEW_LAUNCHED.json').exists()
assert json.loads((R/'WORLD_GATE_SCHEMA_ACTUAL_REVIEW.json').read_text())['gate']['pass_']
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect();ROOT='/home/egde/rl_candidates/MOD4_S1A_FROZEN_WORLD_PROTOCOL_REVIEW_20261007'
try:
 code=r'''
from pathlib import Path
import json,hashlib,shutil
D=Path('ROOT');B=Path('/home/egde/rl_candidates/MOD4_S1A_FROZEN_EVAL_CONTROLLER_20261007');assert not D.exists();D.mkdir();(D/'reports').mkdir()
f=json.loads((B/'reports/SOURCE_FREEZE.json').read_text())['sha256'];assert len(f)==219
for n,h in f.items():
 p=B/n;assert hashlib.sha256(p.read_bytes()).hexdigest()==h;out=D/n;out.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,out)
'''.replace("Path('ROOT')","Path("+repr(ROOT)+")")
 _,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code));assert o.channel.recv_exit_status()==0,e.read().decode()
 with c.open_sftp() as s:s.put(str(D/'continue_frozen_world_protocol_review_once.py'),ROOT+'/continue_frozen_world_protocol_review_once.py')
 code=r'''
from pathlib import Path
import json,hashlib,sys,time,subprocess
D=Path('ROOT');B=Path('/home/egde/rl_candidates/MOD4_S1A_FROZEN_EVAL_CONTROLLER_20261007');f=json.loads((B/'reports/SOURCE_FREEZE.json').read_text())['sha256'];n='continue_frozen_world_protocol_review_once.py';f[n]=hashlib.sha256((D/n).read_bytes()).hexdigest();(D/'reports/SOURCE_FREEZE.json').write_text(json.dumps(dict(sha256=f,source_count=220,old219_exact=True),indent=2))
sys.path.insert(0,str(D));import continue_frozen_world_protocol_review_once as q;q.verify()
with (D/'controller.log').open('x') as log:p=subprocess.Popen([q.q.q.base.PY,str(D/n)],cwd=q.q.q.P,env=q.q.q.w.runtime(),stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
time.sleep(.4);assert p.poll() is None
v=dict(epoch=time.time(),root=str(D),owner=q.q.q.helpers.identity(p.pid),source_count=220,old219_exact=True,new_learning=False,new_budget_seconds=0);(D/'reports/FROZEN_PROTOCOL_REVIEW_LAUNCHED.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
'''.replace("Path('ROOT')","Path("+repr(ROOT)+")")
 _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=30)
 raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode()
 v=json.loads(raw);(R/'FROZEN_PROTOCOL_REVIEW_LAUNCHED.json').write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(v))
finally:c.close()
