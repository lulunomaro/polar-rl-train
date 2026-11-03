"""One actual synthetic TorchCPU boundary test, using whole fixed canonical source."""
from pathlib import Path
import ast,hashlib,json,sys,time,shlex
R=Path(__file__).resolve().parent;D=R/'source_phase1_boundary_device_contract_v1';out=R/'reports/PHASE1_BOUNDARY_DEVICE_ACTUAL_CPU_V1.json';marker=R/'PAPER_ALIGNED_REBUILD_20261103/PHASE1_BOUNDARY_DEVICE_CPU_V1_STARTED_ONCE.json';assert not out.exists()and not marker.exists()
H=lambda b:hashlib.sha256(b).hexdigest();raw=(D/'SOURCE_SEAL.json').read_bytes();assert(len(raw),H(raw))==(1570,'c9fae49e96b7042863372e7fb681c7c93fd8ce733646908222c9af6f7d306bdc');seal=json.loads(raw);assert len(seal['files'])==8 and seal['content_root_sha256']=='5b4d0134e8ec0d828adef1fae8156d195ede032eacea2476457a403162e9e106';payload={}
for row in seal['files']:
 b=(D/row['relative']).read_bytes();assert(len(b),H(b))==(row['bytes'],row['sha256'])
 if row['relative']in('torch_cpu_fixture.py','boundary_device_contract.py'):ast.parse(b);payload[row['relative']]=b
assert len(payload)==2
failure=json.loads((R/'reports/PHASE1_CAPTURE_V3_CLOSED_BOUNDARY_FAILURE_FACTS_V1.json').read_bytes());scope=failure['actual_parent_exit_scope'];assert failure['status']=='FAIL_CLOSED_CAPTURE_EXECUTION'and scope['all_own_children_waited']and scope['original_single_GPU_private_EX_released']and scope['original_global_finite_EX_released']
stage=json.loads((R/'reports/PHASE1_E3_CAPTURE_RESET_BINDING_V3_ACTUAL_STAGE.json').read_bytes());B='/home/lc01/Zonglin Li/zonglin2';old=stage['group_root'];assert old==failure['root']and old.startswith(B+'/tasks/MOD4V1_PHASE1_E3_PASSIVE_CAPTURE_V1_RESET_BINDING_V3_');core=old+'/a1_frozen_eval_runtime_v2.py';job=B+'/tasks/PHASE1_BOUNDARY_DEVICE_CONTRACT_CPU_V1_'+str(time.time_ns());script=job+'/torch_cpu_fixture.py';args=[script,'--canonical-source',core]
config=dict(kind='NEW_SYNTHETIC_BOUNDARY_DEVICE_TORCH_CPU_PURPOSE_V1',epoch=time.time(),root=job,canonical_source=core,fixture_SHA256=H(payload['torch_cpu_fixture.py']),source_seal_SHA256=H(raw),PT_raw_SDK_GPU_canonical_resource_operations=0,actual_V3_flags_read=False)
with marker.open('x',encoding='utf-8')as f:json.dump(config,f,indent=2)
sys.path.insert(0,str(R.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
c=connect72();s=c.open_sftp()
try:
 try:s.lstat(job)
 except FileNotFoundError:pass
 else:raise AssertionError('NEW CPU root exists')
 s.mkdir(job)
 for name,b in payload.items():
  with s.open(job+'/'+name,'wx')as f:f.write(b)
 code="import os,sys,runpy;os.environ['CUDA_VISIBLE_DEVICES']='';sys.path.insert(0,%r);sys.argv=%r;runpy.run_path(%r,run_name='__main__')"%(job,args,script)
 i,o,e=c.exec_command("CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 "+shlex.quote(B+'/run-python.sh')+' -B -c '+shlex.quote(code),timeout=240);i.close();stdout=o.read().decode('utf-8','replace');stderr=e.read().decode('utf-8','replace');rc=o.channel.recv_exit_status();v=dict(config,returncode=rc,stdout=stdout,stderr=stderr)
 if rc==0:v['receipt']=json.loads(stdout)
 with out.open('x',encoding='utf-8')as f:json.dump(v,f,indent=2)
 assert rc==0,stderr
 q=v['receipt'];assert q['old_string_device_reproduced']and q['existing_normalized_device_passed']and q['positive_original_step_calls']==2 and q['negative_cases']==11 and q['input_values_unchanged']and q['global_Torch_CPU_RNG_unchanged']and q['global_Python_RNG_unchanged']and not q['actual_V3_root_cause_confirmed']and not q['SDK_or_native']
 print(json.dumps(dict(report=str(out),returncode=rc,receipt=q),indent=2))
finally:s.close();c.close()
