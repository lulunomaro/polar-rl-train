"""Stage only new isolated adapter files and run target CPU contracts, no GPU authority."""
from pathlib import Path
import json,sys,shlex,hashlib
D=Path(__file__).resolve().parent;R=D/'reports';receipt=R/'EXPLICIT_PD_ADAPTER_TARGET_CPU_PASSED.json';assert not receipt.exists()
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect();root='/home/egde/rl_candidates/MOD4_D7_COM_PD_PREPARE_20261009'
try:
 with c.open_sftp() as f:
  hashes={}
  for name in ('explicit_pd_sdk_adapter.py','explicit_pd_training_env.py','test_explicit_pd_adapter_cpu.py','chassis_pd_nominal_readback.py'):
   raw=(D/name).read_bytes();compile(raw.decode('utf8'),name,'exec');dest=root+'/'+name
   try:old=f.open(dest).read()
   except FileNotFoundError:
    with f.open(dest,'wb') as o:o.write(raw)
   else:assert old==raw,'Never overwrite existing staged source'
   assert f.open(dest).read()==raw;hashes[name]=hashlib.sha256(raw).hexdigest()
 code='import sys;sys.path.insert(0,'+repr('/home/egde/rl_candidates/MOD4_D6_FULL_CONTRACT_20261009/isaac/mod4')+');sys.path.insert(0,'+repr(root)+');from test_explicit_pd_adapter_cpu import test_contracts;import json,torch;print(json.dumps(dict(passed=test_contracts(),torch_version=torch.__version__,CUDA_initialized=torch.cuda.is_initialized(),actual_SDK=False)))'
 _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=30);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace')
 v=json.loads(raw);assert len(v['passed'])==15 and not v['CUDA_initialized'];v['source_SHA']=hashes;receipt.write_text(json.dumps(v,indent=2),encoding='utf8')
 with c.open_sftp() as f:
  with f.open(root+'/reports/'+receipt.name,'wb') as o:o.write(receipt.read_bytes())
 print(json.dumps(v))
finally:c.close()
