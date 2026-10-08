"""Isolated PD component only, no installed setter/SDK/PPO/controller authority."""
from pathlib import Path
import json,sys,shlex,hashlib
D=Path(__file__).resolve().parent;R=D/'reports'
assert not (R/'D7_EXPLICIT_PD_TARGET_CPU_PASSED.json').exists()
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect();root='/home/egde/rl_candidates/MOD4_D7_COM_PD_PREPARE_20261009'
try:
 with c.open_sftp() as f:
  hashes={}
  for name in ('explicit_pd_component.py','test_explicit_pd_component.py'):
   raw=(D/name).read_bytes();compile(raw.decode('utf8'),name,'exec');dest=root+'/'+name
   try:f.stat(dest)
   except FileNotFoundError:pass
   else:raise AssertionError('Already staged; do not repeat')
   with f.open(dest,'wb') as out:out.write(raw)
   assert f.open(dest).read()==raw;hashes[name]=hashlib.sha256(raw).hexdigest()
 _,o,e=c.exec_command('cd '+shlex.quote(root)+' && /home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python test_explicit_pd_component.py',timeout=30)
 raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace')
 v=json.loads(raw);assert len(v['passed'])==12 and v['torch_version'].startswith('2.10') and not v['CUDA_initialized'];v['source_SHA']=hashes
 (R/'D7_EXPLICIT_PD_TARGET_CPU_PASSED.json').write_text(json.dumps(v,indent=2),encoding='utf8')
 with c.open_sftp() as f:
  with f.open(root+'/reports/D7_EXPLICIT_PD_TARGET_CPU_PASSED.json','wb') as out:out.write((R/'D7_EXPLICIT_PD_TARGET_CPU_PASSED.json').read_bytes())
 print(json.dumps(v))
finally:c.close()
