"""Only one runtime path literal change; final source/metadata freeze, no launch."""
from pathlib import Path
from unittest import mock
import ast,copy,hashlib,importlib.util,json,shutil,sys,time,traceback
HERE=Path(__file__).resolve().parent;T=HERE.parents[2]
N=T/'MOD4_H1_FLAT05_NATIVE_SINGLE72_RESOURCE_V90_20261027'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
def emit(name,v):
 with (HERE/name).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def main():
 assert not (HERE/'INDEX.json').exists();runtime=HERE/'RUNTIME_V2';runtime.mkdir()
 names=['flat90_protocol_v1.py','flat90_finite_owner_authority72_v1.py','flat90_finite_node_v1.py','three_slot_common_v1.py','single_writer72_authority_V85M_source.py','flat90_resource_guard_v1.py','flat90_bound_cfg_v1.py','flat90_detached_launcher_v1.py']
 for name in names:shutil.copyfile(HERE/name,runtime/name)
 path=runtime/'flat90_protocol_v1.py';old=path.read_bytes();a=b"'job0/TASK.json'";b=b"'job0/FLAT90_RUNTIME_GRANT_BINDING.json'";assert old.count(a)==1
 new=old.replace(a,b,1);path.write_bytes(new);assert new.replace(b,a,1)==old
 p=load('flat90_protocol_v1',path);cfg=load('flat90_bound_cfg_v1',runtime/'flat90_bound_cfg_v1.py')
 actual_path=N/'reports/FLAT90_ACTUAL_SOURCE_SDK_CPU_AND_RESOURCE_V2_RETURNED_ACTUAL.json';actual=json.loads(actual_path.read_bytes());v=actual['value'];w=actual['proof']
 cpuSHA='ff20606386aefd53d53e81599d24e020c97e375be453d30263832a46e25734f8';waitSHA='85ba6639d3106a9e689cb96a362831bad296b6aea8ccaf1b54625569e5d97a68'
 require_spec=dict(worker_SHA=v['worker_SHA'],payload_manifest_SHA=v['payload_manifest_SHA'],source_contract_SHA=v['source_contract_SHA'],source_CPU_SHA=cpuSHA)
 assert actual['passed'] and actual['actual_CPU_waited_EXIT0'] and actual['actual_finite_returned'] and actual['proof_SHA']==waitSHA and w['report_SHA']==cpuSHA
 p.validate_cpu_value(v,require_spec);p.validate_waited_value(w,require_spec)
 # New path-only structural check, with source file I/O intercepted entirely.
 request=dict(owner_root=str(Path(p.JOB).parent/'owner'),node_root=str(Path(p.JOB).parent/'node_h1'),run_id='SYNTHETIC_NEW_BINDING_ONLY',
  worker_SHA=v['worker_SHA'],source_CPU_SHA=cpuSHA,CPU_waited_proof_SHA=waitSHA,manifest_SHA='4'*64,payload_manifest_SHA=v['payload_manifest_SHA'],
  source_contract_SHA=v['source_contract_SHA'],payload_manifest_path=p.JOB+'/THREE_SLOT_COMPLETE_MANIFEST_V1.json',source_contract_path=p.JOB+'/FLAT90_SOURCE_CONTRACT_ACTUAL.json',
  actual_gas400_asset_composition_report_SHA='5'*64,own_step_objective_qualification_SHA='6'*64)
 _,s=cfg.bound_cfgs(request,'x'*64);binding={k:x for k,x in s.items() if k!='token'}
 manifest=dict(key='h1',source_SHA=p.SOURCE,worker_SHA=s['worker_SHA'],source_CPU_SHA=cpuSHA,files=[])
 reads=[]
 def rb(file):
  name=str(file).replace('\\','/');reads.append(name)
  if name.endswith('/FLAT90_RUNTIME_GRANT_BINDING.json'):return json.dumps(binding).encode()
  if name.endswith('/FLAT90_SINGLE_SLOT_COMPLETE_MANIFEST_V1.json'):return json.dumps(manifest).encode()
  raise AssertionError('Unexpected read '+name)
 def hash_spy(file):return s['worker_SHA'] if str(file).replace('\\','/').endswith('/'+p.WORKER_NAME) else s['manifest_SHA']
 with mock.patch.object(Path,'read_bytes',rb),mock.patch.object(p,'H',hash_spy):p.validate_payload(s,Path(request['node_root']))
 assert not any(x.endswith('/TASK.json') for x in reads) and any(x.endswith('/FLAT90_RUNTIME_GRANT_BINDING.json') for x in reads)
 binding['run_id']='WRONG_SYNTHETIC_RUN'
 with mock.patch.object(Path,'read_bytes',rb),mock.patch.object(p,'H',hash_spy):
  try:p.validate_payload(s,Path(request['node_root']))
  except ValueError:pass
  else:raise AssertionError('Wrong dynamic run ID accepted')
 emit('RUNTIME_BINDING_V2_PATH_AND_ACTUAL245_CPU_SCHEMA_ACTUAL.json',dict(epoch=time.time(),passed=True,
  exact_one_path_literal_change=True,inverse_old_protocol_bytes=True,old_protocol_SHA=hashlib.sha256(old).hexdigest(),new_protocol_SHA=H(path),
  dynamic_runtime_binding_read_static_sealed_Task_not_read_or_modified=True,wrong_dynamic_run_rejected=True,
  actual245_metadata_path=str(actual_path),actual245_metadata_SHA=H(actual_path),actual_CPU_SHA=cpuSHA,actual_waited_proof_SHA=waitSHA,
  actual245_report_and_wait_schema_pass=True,actual_worker_SHA=v['worker_SHA'],actual_payload_manifest_SHA=v['payload_manifest_SHA'],actual_source_contract_SHA=v['source_contract_SHA'],
  no_CPU_model_or_oldfixture_rerun_no_PT_SDK_GPU_remote_or_ledger_IO=True,actual_owner_GO_native_update_pending=True))
 for f in HERE.rglob('*.py'):ast.parse(f.read_bytes())
 assert json.loads((HERE/'FLAT90_READY_GO_DISPATCH_ACCOUNT_STRUCT_CPU_ACTUAL_V2.json').read_bytes())['passed']
 files=[dict(relative=f.relative_to(HERE).as_posix(),bytes=f.stat().st_size,SHA=H(f)) for f in sorted(HERE.rglob('*')) if f.is_file()]
 emit('INDEX.json',dict(epoch=time.time(),schema='mod4.flat90.single72.h1.controller_source.frozen.v2',files=files,
  selected_runtime_directory=str(runtime),runtime_files=[dict(relative=n,bytes=(runtime/n).stat().st_size,SHA=H(runtime/n)) for n in names],
  original_account_charge_HMAC_locks_caps_unchanged=True,source_frozen=True,actual_CPU245_passed_metadata_reused=True,
  actual_source_install_resource_authority_GO_and_native_update_pending=True,Git_status='ordinary_supplement_pending_root'))
 print(json.dumps(dict(index_SHA=H(HERE/'INDEX.json'),runtime_dir=str(runtime),protocol_V2_SHA=H(path),runtime_files=len(names),actual245_schema_passed=True,no_launch=True)))
if __name__=='__main__':
 try:main()
 except BaseException:emit('FINALIZE_V2_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(traceback=traceback.format_exc(),no_actual_launch=True));raise
