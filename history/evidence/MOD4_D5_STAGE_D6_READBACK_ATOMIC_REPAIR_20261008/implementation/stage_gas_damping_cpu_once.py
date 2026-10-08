"""Stage only three CPU component files; no production/GPU/ledger authority."""
from pathlib import Path
import json,sys,hashlib,shlex,time
D=Path(__file__).resolve().parent;R=D/'reports';assert not (R/'GAS_DAMPING_CPU_STAGED.json').exists()
source=D/'reviewed_sources/spring_pressure_component.py';dest=D/'spring_pressure_component.py'
assert not dest.exists();dest.write_bytes(source.read_bytes())
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect();root='/home/egde/rl_candidates/MOD4_D6_DAMPING_SOURCE_PREPARE_20261008'
try:
 with c.open_sftp() as f:
  try:f.stat(root);raise AssertionError('New preparation root exists; inspect actual receipts, never repeat stage')
  except FileNotFoundError:f.mkdir(root)
  f.mkdir(root+'/reports')
  for n in ('gas_damping_factor.py','test_gas_damping_cpu.py','spring_pressure_component.py'):
   raw=(D/n).read_bytes()
   with f.open(root+'/'+n,'wb') as o:o.write(raw)
   assert f.open(root+'/'+n).read()==raw
 _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python '+shlex.quote(root+'/test_gas_damping_cpu.py'),timeout=40);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace');v=json.loads(raw)
 assert v['passed'] and v['CPU_only'] and not v['CUDA_initialized'] and v['count']==9
 with c.open_sftp() as f:f.get(root+'/reports/GAS_DAMPING_CPU_PASSED.json',str(R/'GAS_DAMPING_CPU_PASSED.json'))
 proof=dict(epoch=time.time(),CPU_component_only=True,root=root,source_math_reused_exact_SHA=hashlib.sha256(source.read_bytes()).hexdigest(),GPU_PPO_canonical_writes=0,passed=v)
 (R/'GAS_DAMPING_CPU_STAGED.json').write_text(json.dumps(proof,indent=2),encoding='utf8');print(json.dumps(proof))
finally:c.close()
