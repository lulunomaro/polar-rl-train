from pathlib import Path
import sys,json,time,hashlib,shlex,importlib.util,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'
P=N/'controllers'
JOB='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_H1_FLAT05_NATIVE_2610v90b/h1'
OWNER=str(Path(JOB).parent/'owner').replace('\\','/');NODE=str(Path(JOB).parent/'node_h1').replace('\\','/')
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(name,v):
 with (R/name).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)

PRE=r'''from pathlib import Path
import json,hashlib,fcntl,socket,psutil,subprocess,shutil
job=Path(v['job']);owner=Path(v['owner']);node=Path(v['node']);assert job.is_dir() and not owner.exists() and not node.exists() and not (job/'job0/GO_PRODUCTION.json').exists() and not (job/'job0/production').exists()
C=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');raw=C.read_bytes();c=json.loads(raw)
assert c['active_segment'] is None and c['remaining_training_seconds']==558110.3183145523 and c['remaining_training_seconds']>86412.86069250107 and c['budget_mode']=='finite_original_limits_restored_after_single4090_return'
for p in (C.parent/'native_floor_supervisor.lock',C.parent/'autonomy_controller.lock',C.parent.parent/'three_expert_v2_GPU-c27eecbd-6838-7290-1cd2-37e34522213d.lock',C.parent.parent/'finite_environment_validation.lock'):
 with p.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
with socket.socket() as s:s.bind(('127.0.0.1',29754))
gpu='GPU-c27eecbd-6838-7290-1cd2-37e34522213d';line=subprocess.check_output(['nvidia-smi','-i',gpu,'--query-gpu=uuid,name,memory.free','--format=csv,noheader,nounits'],text=True).strip().split(',');apps=subprocess.check_output(['nvidia-smi','-i',gpu,'--query-compute-apps=gpu_uuid','--format=csv,noheader,nounits'],text=True)
assert line[0].strip()==gpu and line[1].strip()=='NVIDIA GeForce RTX 4090' and int(line[2])>15669 and gpu not in apps and psutil.virtual_memory().available>32*1024**3 and shutil.disk_usage(job).free>25*1024**3
proof_path=job/'job0/FLAT90_SOURCE_CPU_WAITED_ACTUAL.json'
assert not proof_path.exists()
with proof_path.open('x') as f:json.dump(v['actual_extension_wait_proof'],f,indent=2)
for path,SHA in v['sealed'].items():assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==SHA,path
owner.mkdir();node.mkdir();assert C.read_bytes()==raw
print(json.dumps(dict(canonical_None=True,remaining_snapshot=c['remaining_training_seconds'],original_owner_private_shared_locks_free=True,port_free=True,GPU_UUID=gpu,free_MiB=int(line[2]),RAM_available=psutil.virtual_memory().available,postcopy_disk_free=shutil.disk_usage(job).free,no_unknown_PID_inspected=True,no_account_write_before_original_owner=True)))'''

ADMIT=r'''from pathlib import Path
import hashlib,json,sys
for root in (v['owner'],v['node']):
 B=Path(root);assert hashlib.sha256((B/'FLAT90_SINGLE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes()).hexdigest()==v['request']['manifest_SHA']
 for r in v['manifest']['files']:
  p=B/r['relative'];assert p.stat().st_size==r['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==r['SHA']
job=Path(v['job']);static=job/'job0/TASK.json';before=static.read_bytes();binding=job/'job0/FLAT90_RUNTIME_GRANT_BINDING.json'
with binding.open('x',encoding='utf8') as f:json.dump(v['runtime_binding'],f,indent=2)
sys.path.insert(0,v['owner']);from flat90_bound_cfg_v1 import bound_cfgs
from flat90_protocol_v1 import validate_payload,load_actual_flat_preinstalled_CPU,nativeflat_valid_ready
cfg,s=bound_cfgs(v['request'],'nonsecret_source_admission_fixture_token_0000');validate_payload(s,v['node']);cpu=load_actual_flat_preinstalled_CPU(s,v['node'])
assert static.read_bytes()==before
print(json.dumps(dict(actual_installed_controller_source_and_typed_CPU_admitted=True,CPU_SHA=cpu['SHA'],original_static_Task_bytes_unchanged=True,no_model_reload=True,no_GO_or_account_write=True)))'''

def main():
 put('FLAT90_ACTIVATION_CONSUMED_ACTUAL.json',dict(epoch=time.time(),one_native_flat_slot=True))
 assert H(P/'INDEX.json')=='20316d71ccf5efdd0a73a13a459581bec5a53d5441cdda0a19ee8729f1aa2aea','controller must be frozen'
 sys.path.insert(0,str(P));from flat90_bound_cfg_v1 import controller_manifest
 prep=json.loads((R/'FLAT90B_PAYLOAD_SOURCE_PREPARED_ACTUAL.json').read_bytes());actual=json.loads((R/'FLAT90B_ACTUAL_SOURCE_CPU_ENVELOPE_WITH_REAL_SSH_EXIT0.json').read_bytes());assert actual['passed'] and actual['actual_finite_returned']
 task=prep['task'];value=actual['value']
 request=dict(owner_root=OWNER,node_root=NODE,run_id='MOD4_NATIVE_FLAT05_SINGLE72_'+str(time.time_ns()),worker_SHA=value['worker_SHA'],source_CPU_SHA=actual['proof']['report_SHA'],CPU_waited_proof_SHA=actual['proof_SHA'],payload_manifest_SHA=prep['manifest_SHA'],source_contract_SHA=prep['source_contract_SHA'],payload_manifest_path=JOB+'/THREE_SLOT_COMPLETE_MANIFEST_V1.json',source_contract_path=JOB+'/FLAT90_SOURCE_CONTRACT_ACTUAL.json',actual_gas400_asset_composition_report_SHA=task['actual_gas400_asset_composition_report_SHA'],own_step_objective_qualification_SHA=task['own_step_objective_qualification_SHA'])
 manifest=controller_manifest(request,P);mf=N/'FLAT90_SINGLE_SLOT_COMPLETE_MANIFEST_V1.json';mf.write_text(json.dumps(manifest,indent=2),encoding='utf8');request['manifest_SHA']=H(mf)
 put('FLAT90_PUBLIC_ACTUAL_LAUNCH_REQUEST.json',request)
 binding=dict(task,run_id=request['run_id'],worker_SHA=request['worker_SHA'],source_CPU_SHA=request['source_CPU_SHA']);put('FLAT90_PUBLIC_RUNTIME_GRANT_BINDING.json',binding)
 sealed={JOB+'/job0/FLAT90_SOURCE_SDK_CPU_ACTUAL.json':request['source_CPU_SHA'],JOB+'/job0/FLAT90_SOURCE_CPU_WAITED_ACTUAL.json':request['CPU_waited_proof_SHA'],request['payload_manifest_path']:request['payload_manifest_SHA'],request['source_contract_path']:request['source_contract_SHA']}
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sp=importlib.util.spec_from_file_location('flat90_activate_memory_secret',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');sec=importlib.util.module_from_spec(sp);sp.loader.exec_module(sec)
 secret=sec.recover();c=None
 try:
  c=d.connect72(secret);secret=None
  put('FLAT90_ACTUAL_PREGO_RESOURCE_AND_AUTHORITY_RETURNED.json',d.code(c,d.PY72,PRE,dict(job=JOB,owner=OWNER,node=NODE,sealed=sealed,actual_extension_wait_proof=actual['source_extension_wait_proof']),timeout=60))
  sf=c.open_sftp();sf.get_channel().settimeout(60)
  try:
   for root in (OWNER,NODE):
    for row in manifest['files']:sf.put(str(P/row['relative']),root+'/'+row['relative'])
    sf.put(str(mf),root+'/FLAT90_SINGLE_SLOT_COMPLETE_MANIFEST_V1.json')
  finally:sf.close()
  put('FLAT90_ACTUAL_INSTALLED_CONTROLLER_READY_RETURNED.json',d.code(c,d.PY72,ADMIT,dict(owner=OWNER,node=NODE,job=JOB,request=request,manifest=manifest,runtime_binding=binding),timeout=60))
  cmd=shlex.quote(d.PY72)+' -u -B '+shlex.quote(OWNER+'/flat90_detached_launcher_v1.py')
  i,o,e=c.exec_command(cmd,timeout=90);i.write(json.dumps(request)+'\n');i.flush();i.channel.shutdown_write();stdout=o.read().decode('utf8','replace');stderr=e.read().decode('utf8','replace');rc=o.channel.recv_exit_status()
  put('FLAT90_ACTUAL_LAUNCH_RETURNED_ORIGINAL_TEXT.json',dict(returncode=rc,stdout=stdout,stderr=stderr,possible_live_owner_no_retry=True))
  assert rc==0,(stdout,stderr)
  value=json.loads(stdout);put('FLAT90_ACTUAL_OWNER_NODE_DETACHED_RETURNED.json',value)
  print(json.dumps(dict(actual_owner_node_launched=True,run_id=request['run_id'],owner=value['owner'],node=value['node'],first_GPU_update_still_pending=True)))
 finally:
  secret=None
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:put('FLAT90_ACTIVATION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(traceback=traceback.format_exc(),possible_owner_do_not_retry_or_clear_active=True));raise
