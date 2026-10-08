"""Stage only the isolated CPU component and execute target Torch contracts."""
from pathlib import Path
import json,sys,shlex
D=Path(__file__).resolve().parent;R=D/'reports';R.mkdir(exist_ok=True)
assert not (R/'CHASSIS_COM_TARGET_CPU_PASSED.json').exists()
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect();root='/home/egde/rl_candidates/MOD4_D7_COM_PD_PREPARE_20261009'
try:
 with c.open_sftp() as f:
  for name in ('chassis_com_component.py','test_chassis_com_component.py'):
   raw=(D/name).read_bytes();dest=root+'/'+name
   try:existing=f.open(dest).read();assert existing==raw
   except FileNotFoundError:
    with f.open(dest,'wb') as o:o.write(raw)
   assert f.open(dest).read()==raw
 _,o,e=c.exec_command('cd '+shlex.quote(root)+' && /home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python test_chassis_com_component.py',timeout=30)
 raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace')
 v=json.loads(raw);assert v['torch_version'].startswith('2.10') and not v['CUDA_initialized'] and len(v['passed'])==14
 (R/'CHASSIS_COM_TARGET_CPU_PASSED.json').write_text(json.dumps(v,indent=2),encoding='utf8')
 with c.open_sftp() as f:
  with f.open(root+'/reports/CHASSIS_COM_TARGET_CPU_PASSED.json','wb') as out:out.write((R/'CHASSIS_COM_TARGET_CPU_PASSED.json').read_bytes())
 print(json.dumps(v))
finally:c.close()
