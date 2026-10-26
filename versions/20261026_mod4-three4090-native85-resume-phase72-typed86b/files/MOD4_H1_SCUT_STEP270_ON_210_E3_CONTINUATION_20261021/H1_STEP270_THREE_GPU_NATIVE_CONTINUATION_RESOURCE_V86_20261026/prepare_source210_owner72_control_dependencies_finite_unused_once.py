"""Finite serial72->210 public dependency handoff, no training/account writes."""
from pathlib import Path
import hashlib,importlib.util,json,sys,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'
SOURCE='/home/lc01/Zonglin Li/zonglin2/state/mod4_forwarded_owner_control_deps_20261025'
DEST='/home/egde/rl_candidates/mod4_owner72_control_deps_v86_20261026'
ORIGINAL_SHA='770a17505e6c25cd70477690d48acd0ae0bb167cc7bad109e48e2ce597b3fd14'
def put(name,value):
 with (R/name).open('x',encoding='utf8') as stream:json.dump(value,stream,indent=2)
def main():
 closed=json.loads((T/'H1_STEP270_DUAL72_FUDAN_SUPERMIMIC_E3_MIGRATED_V85M2_20261026/reports/V85M2_SINGLE72_NATIVE_E3_AND_ACTUAL_COST_CPU_ACTUAL.json').read_bytes())
 assert closed['passed'] and closed['all_owner_nodes_children_actual_out'] and closed['original_canonical_cost_settled'] and closed['remaining_actual_snapshot']==587957.6840648651
 put('SOURCE210_OWNER72_DEPS_NEW_FINITE_STARTED_ACTUAL.json',dict(epoch=time.time(),serial_hosts=['72','210'],public_dependencies_only=True,no_training_or_budget_write=True))
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 spec=importlib.util.spec_from_file_location('known72_auth_memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');memory=importlib.util.module_from_spec(spec);spec.loader.exec_module(memory)
 sys.path.insert(0,str(T/'MOD4_MOE_T2Z_SINGLE4090_QUANTIZED_PREPARATION_20261025'));import strict_user_forwarded_original210_transport_v1 as route
 client=None;secret=memory.recover();files=[];deadline=time.monotonic()+300
 try:
  client=d.connect72(secret);secret=None
  account=d.code(client,d.PY72,"from pathlib import Path;import json,fcntl;P=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026');c=json.loads((P/'TRAINING_BUDGET_10H.json').read_bytes());assert c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026' and c['budget_mode']=='finite_original_limits_restored_after_single4090_return' and c['active_segment'] is None and c['remaining_training_seconds']==587957.6840648651 and c['remaining_training_seconds']>86412.86069250107\nfor name in ('native_floor_supervisor.lock','autonomy_controller.lock'):\n with (P/name).open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)\nprint(json.dumps(dict(actual_canonical_None=True,remaining=c['remaining_training_seconds'],sole72_generation=c['authority_generation'],actual_two_owner_locks_free=True,no_account_write=True)))",{},timeout=45)
  sf=client.open_sftp();sf.get_channel().settimeout(30)
  try:
   with sf.open(SOURCE+'/INSTALLED_SOURCE_CPU_RECEIPT.json','rb') as stream:raw=stream.read()
   assert hashlib.sha256(raw).hexdigest()==ORIGINAL_SHA
   receipt=json.loads(raw);assert receipt['returncode']==0 and receipt['paramiko_version']=='5.0.0'
   for row in receipt['installed_files']:
    assert time.monotonic()<deadline
    relative=Path(row['relative']);assert not relative.is_absolute() and '..' not in relative.parts
    with sf.open(SOURCE+'/'+row['relative'],'rb') as stream:body=stream.read()
    assert len(body)==row['bytes'] and hashlib.sha256(body).hexdigest()==row['SHA']
    files.append((row,body))
  finally:sf.close()
  client.close();client=None
  put('SOURCE72_PUBLIC_DEPS_PINNED_IN_MEMORY_RETURNED_ACTUAL.json',dict(epoch=time.time(),files=len(files),bytes=sum(len(x[1]) for x in files),source_receipt_SHA=ORIGINAL_SHA,actual72_account=account,no_credential_or_dependency_binary_local_disk=True))
  client=route.connect()
  pre=d.code(client,route.PY,"from pathlib import Path;import json,shutil,subprocess;D=Path(v['dest']);owned=Path('/home/egde/rl_candidates');assert D.resolve().is_relative_to(owned.resolve()) and not D.exists();assert shutil.disk_usage(owned).free>100*1024**2;mount=json.loads(subprocess.check_output(['findmnt','--json','--target','/mnt/mod4_linux_durable_20261013','--output','SOURCE,TARGET,UUID,FSTYPE,OPTIONS'],text=True))['filesystems'][0];assert mount['uuid']=='EF3105C85DD986BD' and 'rw' in mount['options'].split(',');assert shutil.disk_usage('/mnt/mod4_linux_durable_20261013').free>25*1024**3;D.mkdir();print(json.dumps(dict(new_unused_dependency_root=str(D),durable_mount=mount,durable_free=shutil.disk_usage('/mnt/mod4_linux_durable_20261013').free,no_oldcanonical_action=True,no_GPU_query_or_training=True)))",dict(dest=DEST),timeout=45)
  sf=client.open_sftp();sf.get_channel().settimeout(30)
  try:
   directories={DEST}
   def write(relative,body):
    current=Path(DEST)
    for part in Path(relative).parts[:-1]:
     current=current/part;name=current.as_posix()
     if name not in directories:sf.mkdir(name);directories.add(name)
    with sf.open(DEST+'/'+str(relative).replace('\\','/'),'x') as stream:stream.write(body)
   for row,body in files:
    assert time.monotonic()<deadline;write(row['relative'],body)
   write('INSTALLED_SOURCE_CPU_RECEIPT.json',raw)
  finally:sf.close()
  code="from pathlib import Path;import hashlib,json,sys,time;D=Path(v['dest']);raw=(D/'INSTALLED_SOURCE_CPU_RECEIPT.json').read_bytes();assert hashlib.sha256(raw).hexdigest()==v['receipt_SHA'];receipt=json.loads(raw)\nfor row in receipt['installed_files']:\n p=D/row['relative'];assert p.resolve().is_relative_to(D.resolve()) and not p.is_symlink() and p.stat().st_size==row['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==row['SHA']\nsys.path.insert(0,str(D/'site_packages'));import paramiko;assert paramiko.__version__=='5.0.0' and Path(paramiko.__file__).resolve().is_relative_to(D.resolve());value=dict(epoch=time.time(),passed=True,root=str(D),paramiko_version=paramiko.__version__,module_path=str(Path(paramiko.__file__).resolve()),python=sys.executable,source_receipt_SHA=v['receipt_SHA'],verified_file_count=len(receipt['installed_files']),no_training_environment_modified=True,no_GPU_or_model_load=True);result=json.dumps(value,indent=2).encode();p=D/'TARGET210_DEPENDENCIES_CPU_ACTUAL.json'\nwith p.open('xb') as f:f.write(result)\nprint(json.dumps(dict(value=value,path=str(p),bytes=len(result),SHA=hashlib.sha256(result).hexdigest())))"
  proof=d.code(client,route.PY,code,dict(dest=DEST,receipt_SHA=ORIGINAL_SHA),timeout=90)
  binding=dict(schema='mod4.owner72.source210.control_dependencies.v1',actual_target210_CPU_passed=True,host72_original_pin_SHA256='301a9837e8503b664fa4cedde20407769d8f1b86ae59d9a54afb236bdfa41795',DEPS_root=DEST,target_CPU_receipt_SHA=proof['SHA'],original_source_receipt_SHA=ORIGINAL_SHA)
  put('OWNER72_CONTROL_DEPENDENCIES_BINDING_ACTUAL.json',binding)
  put('SOURCE210_OWNER72_DEPS_ACTUAL_CPU_FINITE_RETURNED_ACTUAL.json',dict(epoch=time.time(),actual_finite_returned=True,actual_target210_CPU_passed=True,target_proof=proof,preflight=pre,actual72_account=account,files=len(files),bytes=sum(len(x[1]) for x in files),no_controller_payload_Task_GO_or_fee=True,no_canonical_or_mount_modification=True))
  print(json.dumps(dict(actual_finite_returned=True,target210_paramiko_CPU_passed=True,files=len(files),no_training=True)))
 finally:
  secret=None;files.clear()
  if client:client.close()
if __name__=='__main__':
 try:main()
 except BaseException:
  put('SOURCE210_OWNER72_DEPS_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_auto_retry_same_root_or_once=True,no_training_or_budget_write=True));raise
