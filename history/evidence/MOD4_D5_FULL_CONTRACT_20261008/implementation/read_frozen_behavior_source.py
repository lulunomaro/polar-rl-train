"""Inspect exact prior immutable evaluator modules; no physics/publication."""
from pathlib import Path
import sys,json,shlex
D=Path(__file__).resolve().parent;R=D/'reports'
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect()
try:
 code=r'''
from pathlib import Path
import json,zipfile,hashlib
E=Path('/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007');job=json.loads((E/'eval_queue/clk2500-closure-episode-d3-45-d4world-anchor-world.json').read_text());p=Path(job['artifacts']['runtime']['path']);assert hashlib.sha256(p.read_bytes()).hexdigest()==job['artifacts']['runtime']['sha256']
with zipfile.ZipFile(p) as z:
 names=[n for n in z.namelist() if n.endswith(('frozen_history_flat.py','frozen_history_spin.py','frozen_history_world.py'))]
 v=dict(package=job['artifacts']['runtime'],modules={n:z.read(n).decode() for n in names})
print(json.dumps(v))
'''
 _,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=40);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace')
 v=json.loads(raw)
 for name,source in v['modules'].items():
  p=D/'frozen_source'/Path(name).name;p.parent.mkdir(exist_ok=True);p.write_text(source,encoding='utf8')
 (R/'FROZEN_BASE_D4_SOURCE.json').write_text(json.dumps(dict(package=v['package'],module_names=list(v['modules'])),indent=2),encoding='utf8')
 print(json.dumps(dict(package=v['package'],modules=list(v['modules']))))
finally:c.close()
