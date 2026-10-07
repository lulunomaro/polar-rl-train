"""Explicit CPU fixture-call correction; no SDK or production source change."""
from pathlib import Path
import json, sys, shlex
D=Path(__file__).resolve().parent;R=D/'reports'
ROOT='/home/egde/rl_candidates/MOD4_D3_ACTOR_DELAY_SDK_PREPARE_20261008'
(R/'FIRST_CPU_FIXTURE_ERROR.json').write_text(json.dumps(dict(error='CPU test called feedback(env,key,raw,tick), but actual adapter reads env.common_step_counter and takes3arguments.',scope='CPU fixture only, before CUDA/SDK/PPO; actual runtime adapter unchanged',correction='Remove extra fixture argument; preserve original stage once, do not repeat it.'),indent=2))
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect()
try:
 with c.open_sftp() as f:
  f.put(str(D/'test_delay_actor_boundary_cpu.py'),ROOT+'/isaac/mod4/test_delay_actor_boundary_cpu.py')
  f.put(str(R/'FIRST_CPU_FIXTURE_ERROR.json'),ROOT+'/reports/FIRST_CPU_FIXTURE_ERROR.json')
 code=r'''
from pathlib import Path
import json,hashlib,subprocess,time,sys
D=Path('/home/egde/rl_candidates/MOD4_D3_ACTOR_DELAY_SDK_PREPARE_20261008');R=D/'reports';C=D/'isaac/mod4';assert not (R/'ADAPTER_CPU_PASSED.json').exists()
old=json.loads((R/'ORIGINAL218_AND_MATH_REUSED.json').read_text());f=old['original218'].copy()
for name in ('feedback_delay_mild.py','feedback_delay_runtime.py','test_delay_actor_boundary_cpu.py'):
 p=C/name;compile(p.read_text(),str(p),'exec');f['isaac/mod4/'+name]=hashlib.sha256(p.read_bytes()).hexdigest()
assert len(f)==221
for name,digest in f.items():assert hashlib.sha256((D/name).read_bytes()).hexdigest()==digest,name
res=subprocess.run([sys.executable,str(C/'test_delay_actor_boundary_cpu.py')],cwd=C,capture_output=True,text=True)
assert res.returncode==0,res.stdout+res.stderr
v=json.loads(res.stdout);assert v['passed'] and v['no_CUDA_initialized'] and not v['actual_SDK'] and not v['PPO_deployed']
(R/'SOURCE_FREEZE.json').write_text(json.dumps(dict(sha256=f,original218_exact=True),indent=2))
result=dict(epoch=time.time(),CPU=v,old_D3_math_exact_reused=True,source_count=221,production_runtime_unchanged=True,scope='Adapter CPU fixture only; immutable3060 SDK not launched',copied_training_entries_forbidden=True)
(R/'ADAPTER_CPU_PASSED.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
'''
 _,out,err=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=45);raw,errors=out.read(),err.read();assert out.channel.recv_exit_status()==0,(raw+errors).decode()
 with c.open_sftp() as f:
  for n in ('ADAPTER_CPU_PASSED.json','SOURCE_FREEZE.json','ORIGINAL218_AND_MATH_REUSED.json'):f.get(ROOT+'/reports/'+n,str(R/n))
 print(raw.decode())
finally:c.close()
