"""Stage isolated adapter and execute target CPU fixture, no learning authority."""
from pathlib import Path
import json,sys,shlex
D=Path(__file__).resolve().parent;R=D/'reports'
assert not (R/'CHASSIS_COM_ADAPTER_TARGET_CPU_PASSED.json').exists()
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect();root='/home/egde/rl_candidates/MOD4_D7_COM_PD_PREPARE_20261009'
try:
 with c.open_sftp() as f:
  dependency=D.parent/'MOD4_D6_DAMPING_SOURCE_PREPARE_20261008/gas_damping_sdk_adapter.py'
  for name,raw in [('gas_damping_sdk_adapter.py',dependency.read_bytes())]+[(n,(D/n).read_bytes()) for n in ('chassis_com_sdk_adapter.py','chassis_com_training_env.py','test_chassis_com_adapter_cpu.py')]:
   compile(raw.decode('utf8'),name,'exec');dest=root+'/'+name
   try:existing=f.open(dest).read();assert existing==raw
   except FileNotFoundError:
    with f.open(dest,'wb') as o:o.write(raw)
   assert f.open(dest).read()==raw
 code='import sys;sys.path.insert(0,'+repr('/home/egde/rl_candidates/MOD4_D6_FULL_CONTRACT_20261009/isaac/mod4')+');sys.path.insert(0,'+repr(root)+');from test_chassis_com_adapter_cpu import test_contracts;import json,torch;print(json.dumps(dict(passed=test_contracts(),torch_version=torch.__version__,CUDA_initialized=torch.cuda.is_initialized(),actual_SDK=False)))'
 _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=30)
 raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace')
 v=json.loads(raw);assert len(v['passed'])==12 and v['torch_version'].startswith('2.10') and not v['CUDA_initialized']
 (R/'CHASSIS_COM_ADAPTER_TARGET_CPU_PASSED.json').write_text(json.dumps(v,indent=2),encoding='utf8')
 with c.open_sftp() as f:
  with f.open(root+'/reports/CHASSIS_COM_ADAPTER_TARGET_CPU_PASSED.json','wb') as out:out.write((R/'CHASSIS_COM_ADAPTER_TARGET_CPU_PASSED.json').read_bytes())
 print(json.dumps(v))
finally:c.close()
