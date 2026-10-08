"""Deploy independent CPU publication at a new root; no GPU or budget rights."""
from pathlib import Path
import sys,json,shlex,time
D=Path(__file__).resolve().parent;R=D/'reports';assert not (R/'NOMINAL_PUBLICATION_LAUNCHED.json').exists()
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect();root='/home/egde/rl_candidates/MOD4_D5_NOMINAL_SCOPE_PUBLICATION_20261009'
try:
 code='from pathlib import Path;import json;D=Path('+repr(root)+');assert not D.exists();(D/"reports").mkdir(parents=True);print(json.dumps({"created":True}))'
 _,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code));raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace')
 with c.open_sftp() as f:
  f.put(str(D/'supervise_nominal_scope_publication.py'),root+'/supervise_nominal_scope_publication.py')
  f.put(str(R/'NOMINAL_SCOPE_PACKAGE_PUBLISHED.json'),root+'/reports/NOMINAL_SCOPE_PACKAGE_PUBLISHED.json')
 code=r'''
from pathlib import Path
import subprocess,json,time,os
D=Path(ROOT);R=D/'reports';assert not (R/'STARTED.json').exists();ast=__import__('ast');ast.parse((D/'supervise_nominal_scope_publication.py').read_text())
with (D/'publisher.log').open('x') as f:p=subprocess.Popen(['/usr/bin/python3',str(D/'supervise_nominal_scope_publication.py')],cwd=D,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
s=(Path('/proc')/str(p.pid)/'stat').read_text().rsplit(')',1)[1].split();v=dict(epoch=time.time(),pid=p.pid,start_ticks=int(s[19]),root=str(D),no_GPU_PPO_canonical_or_training_launch_authority=True)
(R/'STARTED.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
'''.replace('ROOT',repr(root))
 _,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code));raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace');v=json.loads(raw)
 (R/'NOMINAL_PUBLICATION_LAUNCHED.json').write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(v))
finally:c.close()
