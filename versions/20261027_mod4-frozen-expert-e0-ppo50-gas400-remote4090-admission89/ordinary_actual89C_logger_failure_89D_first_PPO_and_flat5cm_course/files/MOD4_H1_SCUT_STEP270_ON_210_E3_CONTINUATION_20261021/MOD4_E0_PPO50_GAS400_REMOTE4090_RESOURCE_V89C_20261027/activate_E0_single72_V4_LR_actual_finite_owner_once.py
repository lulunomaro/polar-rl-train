"""Install reviewed single-slot controller and launch the sole finite72 writer."""
from pathlib import Path
import hashlib,importlib.util,json,shlex,sys,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'
P=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027/E0_PPO50_gas400_single72_controller_source_preparation_v1/V2_LR'
JOB='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_E0_PPO50_GAS400_2610v89c/e0'
OWNER=str(Path(JOB).parent/'owner').replace('\\','/');NODE=str(Path(JOB).parent/'node_e0').replace('\\','/')
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,x):
 with (R/n).open('x',encoding='utf8') as f:json.dump(x,f,ensure_ascii=False,indent=2)
PRE='''from pathlib import Path
import json,hashlib,fcntl,psutil,shutil,socket,subprocess
job=Path(v['job']);owner=Path(v['owner']);node=Path(v['node']);assert not owner.exists() and not node.exists() and not (job/'TASK.json').exists() and not (job/'GO_PRODUCTION.json').exists() and not (job/'adaptation').exists()
C=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');raw=C.read_bytes();c=json.loads(raw);assert c['active_segment'] is None and c['remaining_training_seconds']>86412.86069250107
for name in ('native_floor_supervisor.lock','autonomy_controller.lock'):
 with (C.parent/name).open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
for name in ('three_expert_v2_GPU-c27eecbd-6838-7290-1cd2-37e34522213d.lock','finite_environment_validation.lock'):
 with (C.parent.parent/name).open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
with socket.socket() as sock:sock.bind(('127.0.0.1',29754))
gpu='GPU-c27eecbd-6838-7290-1cd2-37e34522213d';line=subprocess.check_output(['nvidia-smi','-i',gpu,'--query-gpu=uuid,name,memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip().split(',');apps=subprocess.check_output(['nvidia-smi','-i',gpu,'--query-compute-apps=gpu_uuid','--format=csv,noheader,nounits'],text=True)
assert line[0].strip()==gpu and line[1].strip()=='NVIDIA GeForce RTX 4090' and int(line[2])>15669 and gpu not in apps
assert psutil.virtual_memory().available>8*1024**3 and shutil.disk_usage(job).free>25*1024**3
extension=job/'E0_V4_WORKER_ONLY_LR_SOURCE_MIGRATION_ACTUAL.json';assert hashlib.sha256(extension.read_bytes()).hexdigest()=='5509f4a793be9d9e5e858bc75bfa326440267f1caeff040979935b2bed6f3c8e'
worker=job/'E0_PPO50_gas400_finite_worker_v4_preserved_LR_scalar.py';assert hashlib.sha256(worker.read_bytes()).hexdigest()=='87748712b51a0b36c2ec609cd56773471ac8b41ba60d35b21884403423462d19'
owner.mkdir();node.mkdir();assert C.read_bytes()==raw
print(json.dumps(dict(epoch=__import__('time').time(),canonical_None=True,C_SHA=hashlib.sha256(raw).hexdigest(),remaining_snapshot=c['remaining_training_seconds'],owner_private_shared_locks_free=True,loopback_port_free=True,resource=dict(GPU_UUID=gpu,GPU_name=line[1].strip(),free_MiB=int(line[2]),utilization_percent=int(line[3]),compute_UUID_only_rows=0,no_unknown_PID_inspected=True),RAM_available=psutil.virtual_memory().available,disk_free=shutil.disk_usage(job).free,no_ledger_write_before_original_owner=True)))
'''
ADMIT='''from pathlib import Path
import json,hashlib,sys
for dirname in (v['owner'],v['node']):
 B=Path(dirname);m=B/'E0_SINGLE_SLOT_COMPLETE_MANIFEST_V1.json';assert hashlib.sha256(m.read_bytes()).hexdigest()==v['request']['manifest_SHA']
 for r in v['rows']:
  p=B/r['relative'];assert p.is_file() and p.stat().st_size==r['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==r['SHA']
task=Path(v['job'])/'TASK.json'
with task.open('x',encoding='utf8') as f:json.dump(v['task'],f,ensure_ascii=False,indent=2)
sys.path.insert(0,v['owner']);from E0_single72_bound_cfg_v1 import bound_cfgs
from E0_single72_protocol_v1 import validate_payload,load_E0_preinstalled_CPU
cfg,spec=bound_cfgs(v['request'],'nonsecret_source_only_fixture_token_0000')
validate_payload(spec,v['node']);proof=load_E0_preinstalled_CPU(spec,v['node'])
print(json.dumps(dict(actual_installed_controller_payload_and_ready_CPU_passed=True,source_CPU_SHA=proof['SHA'],no_model_reload=True,no_GO_or_account_write=True,Task_SHA=hashlib.sha256(task.read_bytes()).hexdigest())))
'''
def main():
 put('E0_SINGLE72_ACTIVATION_CONSUMED_ACTUAL.json',dict(epoch=time.time(),one_E0_finite_slot_only=True,no_second_writer_or_fake_slot=True))
 assert H(P/'E0_SINGLE72_V2_LR_FROZEN_INDEX_ACTUAL.json')=='eb6365b1f5be3500256d9c84e2b609ffbfc3a27b11045ef0a90406975e33cf74'
 mf=P/'E0_SINGLE_SLOT_COMPLETE_MANIFEST_V1.json';assert H(mf)=='cfee5558e2a4311c1caf159f47c1213fe146a67c718e82f8220f1a0b0a7cceb0'
 manifest=json.loads(mf.read_bytes());rows=manifest['files'];assert len(rows)==10
 for row in rows:assert (P/row['relative']).stat().st_size==row['bytes'] and H(P/row['relative'])==row['SHA']
 request=dict(owner_root=OWNER,node_root=NODE,manifest_SHA=H(mf),CPU_returned_proof_SHA='671b912670d4630c6d16d5b1ce653e1c2ae37f7f23760f6647518e12fde8db6d',run_id='E0_PPO50_GAS400_SINGLE72_'+str(time.time_ns()))
 put('E0_SINGLE72_PUBLIC_BOUND_LAUNCH_REQUEST_ACTUAL.json',request)
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sp=importlib.util.spec_from_file_location('E0_activate_secret_memory_only',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
 secret=m.recover();c=None
 try:
  c=d.connect72(secret);secret=None
  resource=d.code(c,d.PY72,PRE,dict(job=JOB,owner=OWNER,node=NODE),timeout=60);put('E0_SINGLE72_ACTUAL_PREGO_AUTHORITY_AND_4090_RESOURCE.json',resource)
  sf=c.open_sftp();sf.get_channel().settimeout(60)
  try:
   for root in (OWNER,NODE):
    for row in rows:sf.put(str(P/row['relative']),root+'/'+row['relative'])
    sf.put(str(mf),root+'/E0_SINGLE_SLOT_COMPLETE_MANIFEST_V1.json')
  finally:sf.close()
  task=dict(role='E0',run_id=request['run_id'],source_SHA='54f53453a3f793cea990f0608c0a2c3bd3e5d37aecf41bb8817691af5fea0371',original_source_SHA='b10958d2a8631b12c0f9502bf7fa9230d9a7a1ae9863443bb68388604bed61f8',original_run_manifest_SHA='1dbde5972c65baf8842bc82024fe7ddfd6393d73a51137cc9880ed6310ff1af1',num_envs=20000,source_qualification_kind='MOD4_E0_PPO50_GAS400_FULLSTATE_SOURCE_CPU_V1',source_CPU_SHA='5509f4a793be9d9e5e858bc75bfa326440267f1caeff040979935b2bed6f3c8e',worker_SHA='87748712b51a0b36c2ec609cd56773471ac8b41ba60d35b21884403423462d19',GPU_UUID='GPU-c27eecbd-6838-7290-1cd2-37e34522213d',authority_generation='MOD4_SINGLE_WRITER72_20261026',canonical_authority_path='/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json',actual_resource_admission=resource['resource'],actual_USD_gas400_composition_passed=True)
  put('E0_SINGLE72_PUBLIC_TASK_BEFORE_GO_ACTUAL.json',task)
  put('E0_SINGLE72_ACTUAL_CONTROLLER_SOURCE_AND_TYPED_READY_ADMISSION.json',d.code(c,d.PY72,ADMIT,dict(owner=OWNER,node=NODE,job=JOB,rows=rows,request=request,task=task),timeout=60))
  cmd=shlex.quote(d.PY72)+' -u -B '+shlex.quote(OWNER+'/E0_single72_detached_launcher_v1.py')
  i,o,e=c.exec_command(cmd,timeout=90);i.write(json.dumps(request)+'\n');i.flush();i.channel.shutdown_write();stdout=o.read().decode('utf8','replace');stderr=e.read().decode('utf8','replace');rc=o.channel.recv_exit_status()
  put('E0_SINGLE72_ACTUAL_LAUNCH_PROCESS_RETURNED.json',dict(epoch=time.time(),returncode=rc,stdout=stdout,stderr=stderr,may_have_live_owner_do_not_retry_or_clear_account=True))
  assert rc==0,(stdout,stderr)
  actual=json.loads(stdout);put('E0_SINGLE72_ACTUAL_OWNER_NODE_DETACHED_RETURNED.json',actual)
  print(json.dumps(dict(actual_finite_transport_returned=True,owner=actual['owner'],node=actual['node'],run_id=request['run_id'],actual_worker_GO_PPO_still_requires_first_metadata=True)))
 finally:
  secret=None
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:put('E0_SINGLE72_ACTIVATION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(traceback=traceback.format_exc(),do_not_repeat_possible_owner_or_clear_active=True));raise
