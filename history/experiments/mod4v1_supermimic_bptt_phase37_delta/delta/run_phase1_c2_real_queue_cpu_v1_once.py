"""NEW real-Torch CPU contract purpose for the disabled C2 observer.
Original queue class, original complete fixture derivation and new non-term probes;
no model, saved trajectory, SDK, GPU, canonical, locks or native parent.
"""
from pathlib import Path
import ast,hashlib,json,shlex,sys,time
R=Path(__file__).resolve().parent;out=R/'reports/PHASE1_C2_ACTUAL_REAL_QUEUE_CPU_V1.json';marker=R/'PAPER_ALIGNED_REBUILD_20261103/PHASE1_C2_REAL_QUEUE_CPU_STARTED_ONCE.json';assert not out.exists()and not marker.exists();H=lambda b:hashlib.sha256(b).hexdigest();D=R/'source_phase1_c2_real_cpu_fixture_v1';C=R/'source_phase1_actuation_clock_scope_v2'
for path,pin in [(D/'SOURCE_SEAL.json',(4983,'e2642cfb5731a83438c963202d3b07d034952795e67dfc16438fbdf4954a74b1')),(C/'SOURCE_SEAL.json',(5938,'105df1f6e47b82061aae729878a12874f731dd34b7cb0feeb75724028298469b'))]:
 b=path.read_bytes();assert(len(b),H(b))==pin;s=json.loads(b)
 for x in s['members']:
  raw=(path.parent/x['name']).read_bytes();assert(len(raw),H(raw))==(x['bytes'],x['SHA256'])
q=json.loads((R/'reports/PHASE1_C2_CLOCK_SCOPE_PARENT_SOURCE_VERIFY_V1.json').read_bytes());assert q['tests_run']==12 and q['failures']==q['errors']==0 and q['source_and_old_seals_unchanged']
files={'actuation_tap_v2.py':C/'actuation_tap_v2.py','real_cpu_fixture_c2.py':D/'real_cpu_fixture_c2.py','c2_cpu_fixture_wrapper.py':D/'c2_cpu_fixture_wrapper.py','action_delay_physics_queue.py':R/'discovery/reward_command_audit_v1/E3/runtime/isaac/mod4/action_delay_physics_queue.py'};payload={name:path.read_bytes()for name,path in files.items()}
for b in payload.values():ast.parse(b)
assert H(payload['action_delay_physics_queue.py'])=='a4238c581611ef7cdb710692291ddac48e076364b0587f631eb71fd6a7d15eb8'
old=(R/'source_phase1_actuation_real_cpu_fixture_v1/real_cpu_fixture.py').read_bytes();new=old.replace(b'"""Injection-only ORIGINAL PhysicsActionQueue + sealed tap CPU fixture.',b'"""DISABLED C2 V1 injection-only complete original CPU fixture derivation.',1).replace(b'TAP_SHA256 = "b9b9e288124a1ba8c031a030c00a231f4d02d2ba7efee9981141ae90b8e28828"',b'TAP_SHA256 = "ec10b09b77548c560611e641d685e2cee029c9778ff8c8852a8bf070243bd95d"',1);assert new==payload['real_cpu_fixture_c2.py']
pins={n:dict(bytes=len(b),SHA256=H(b))for n,b in payload.items()}
code='''from pathlib import Path
import hashlib,json,sys,random,time
HERE=Path(__file__).resolve().parent;H=lambda b:hashlib.sha256(b).hexdigest();pins=json.loads((HERE/'PINS.json').read_bytes())
for name,pin in pins.items():
 b=(HERE/name).read_bytes();assert(len(b),H(b))==(pin['bytes'],pin['SHA256'])
sys.path.insert(0,str(HERE));import torch
from action_delay_physics_queue import PhysicsActionQueue
import actuation_tap_v2 as tap
import real_cpu_fixture_c2 as fixture
import c2_cpu_fixture_wrapper as wrapper
assert not torch.cuda.is_initialized()and not any(x.split('.')[0]in{'isaacsim','isaaclab','omni','warp','pxr'}for x in sys.modules)
py_state=random.getstate();torch_state=torch.get_rng_state().clone();start=time.perf_counter();r=wrapper.run_c2_cpu_fixture(torch,PhysicsActionQueue,tap,fixture);assert random.getstate()==py_state and torch.equal(torch_state,torch.get_rng_state())and not torch.cuda.is_initialized();assert r['original_fixture_normal_apply_ticks']==864 and [x['n']for x in r['original_fixture_by_n']]==[2,3]
print(json.dumps(dict(kind='PHASE1_C2_REAL_TORCH_CPU_ORIGINAL_QUEUE_CONTRACT_V1',epoch=time.time(),status='PASS',seconds=time.perf_counter()-start,torch_version=str(torch.__version__),device='cpu',result=r,global_python_and_torch_CPU_rng_unchanged=True,CUDA_initialized=False,actual_SDK_model_raw_C_lock_or_parent_operations=0,stage2_GO=False),allow_nan=False))
''';ast.parse(code);payload['C2_DRIVER.py']=code.encode();payload['PINS.json']=(json.dumps(pins)+'\n').encode();B='/home/lc01/Zonglin Li/zonglin2';job=B+'/tasks/PHASE1_C2_REAL_QUEUE_CPU_V1_'+str(time.time_ns());config=dict(kind='NEW_PHASE1_C2_REAL_QUEUE_CPU_PURPOSE_NOT_NATIVE',epoch=time.time(),root=job,source_files={n:dict(bytes=len(b),SHA256=H(b))for n,b in payload.items()},expected_n=[2,3],new_nonterm_probes_are_separate=True,actual_model_raw_SDK_GPU_C_lock_or_parent_operations=0)
with marker.open('x',encoding='utf8')as f:json.dump(config,f,indent=2)
sys.path.insert(0,str(R.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
c=connect72();s=c.open_sftp()
try:
 try:s.lstat(job)
 except FileNotFoundError:pass
 else:raise AssertionError('CPU purpose exists')
 s.mkdir(job)
 for n,b in payload.items():
  with s.open(job+'/'+n,'wx')as stream:stream.write(b)
 script=job+'/C2_DRIVER.py';invoke="import os,sys,runpy;os.environ['CUDA_VISIBLE_DEVICES']='';sys.path.insert(0,%r);runpy.run_path(%r,run_name='__main__')"%(job,script)
 i,o,e=c.exec_command("CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 "+shlex.quote(B+'/run-python.sh')+' -B -c '+shlex.quote(invoke),timeout=240);i.close();stdout=o.read().decode('utf8','replace');stderr=e.read().decode('utf8','replace');rc=o.channel.recv_exit_status();v=dict(config,returncode=rc,stdout=stdout,stderr=stderr)
 if rc==0:v['receipt']=json.loads(stdout)
 with out.open('x',encoding='utf8')as stream:json.dump(v,stream,indent=2)
 assert rc==0,stderr
 print(json.dumps(dict(report=str(out),returncode=rc,status=v['receipt']['status'],original_ticks=v['receipt']['result']['original_fixture_normal_apply_ticks'],new_nonterm=v['receipt']['result']['non_term_setter_by_n'],stage2_GO=False),indent=2))
finally:s.close();c.close()
