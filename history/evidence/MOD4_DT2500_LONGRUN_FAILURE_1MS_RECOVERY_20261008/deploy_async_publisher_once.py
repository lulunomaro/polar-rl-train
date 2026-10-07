from pathlib import Path
import sys,json,shlex,ast
D=Path(__file__).resolve().parent;R=D/'reports';ROOT='/home/egde/rl_candidates/MOD4_1MS_RECOVERY_ASYNC_PUBLICATION_20261008'
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
ast.parse((D/'supervise_recovery_async_publication.py').read_text());c=connect()
try:
 code=r'''
from pathlib import Path
import json,time
D=Path('/home/egde/rl_candidates/MOD4_1MS_RECOVERY_ASYNC_PUBLICATION_20261008');assert not D.exists();D.mkdir();(D/'reports').mkdir()
print(json.dumps(dict(created=str(D),no_GPU_or_budget_change=True)))
'''
 _,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=20);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode()
 with c.open_sftp() as sf:sf.put(str(D/'supervise_recovery_async_publication.py'),ROOT+'/supervise_recovery_async_publication.py')
 code=r'''
from pathlib import Path
import sys,time,json,hashlib,subprocess
D=Path('/home/egde/rl_candidates/MOD4_1MS_RECOVERY_ASYNC_PUBLICATION_20261008');T=Path('/home/egde/rl_candidates/MOD4_VALIDATED_1MS_EPISODE_RECOVERY_20261008');sys.path.insert(0,str(T));import supervise_validated_1ms_runtime_review as w
w.verify();assert w.s.q.w.read(T/'reports/HEALTH_1MS_SDK_PASSED.json')['passed']
sha=hashlib.sha256((D/'supervise_recovery_async_publication.py').read_bytes()).hexdigest();w.s.q.base.atomic_json(D/'reports/SOURCE_FREEZE.json',dict(sha256={'supervise_recovery_async_publication.py':sha},CPU_only=True,no_canonical_write_or_learning_authority=True))
with (D/'publisher.log').open('x') as out:p=subprocess.Popen([w.s.q.base.PY,str(D/'supervise_recovery_async_publication.py')],cwd=w.s.q.P,stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
row=dict(epoch=time.time(),owner=w.s.identity(p.pid),training_root=str(T),read_complete_source_only=True,no_GPU_or_canonical_write_authority=True);w.s.q.base.atomic_json(D/'reports/LAUNCHED.json',row);print(json.dumps(row))
'''
 _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=30);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode();v=json.loads(raw);(R/'ASYNC_PUBLISHER_LAUNCHED.json').write_text(json.dumps(v,indent=2),encoding='utf8');print(raw.decode())
finally:c.close()
