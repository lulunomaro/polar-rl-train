"""One finite, serial72/210: exact alias source/SDK and initial nativeCPU.

No owner/Task GO/account mutation. The former base-only installer remains UNUSED.
"""
from pathlib import Path
import importlib.util,json,sys,hashlib,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
PRE210=r'''from pathlib import Path,PurePosixPath
import json,hashlib,fcntl,psutil,subprocess,shutil
B=Path(v['root']);owned=Path('/mnt/mod4_linux_durable_20261013');old=owned/'H1step270_own_step_gas400_native_2610v88c/h1'
assert owned.is_mount() and not B.exists() and B.resolve().is_relative_to(owned.resolve())
mount=json.loads(subprocess.check_output(['findmnt','--json','--target',str(owned),'-o','TARGET,SOURCE,FSTYPE,OPTIONS,UUID'],text=True))['filesystems'][0]
assert str(mount['uuid']).upper()=='EF3105C85DD986BD' and 'rw' in mount['options'].split(',')
node=json.loads((old.parent/'node_h1/NODE_TERMINAL_ACTUAL.json').read_bytes())['row']
assert node['terminal_all_own_children_waited'] and node['final']['passed'] and not node['original_error']
gpu=v['spec']['GPU_UUID'];assert gpu=='GPU-937bdb0b-0d8f-aa3d-a10e-1b24969a5d4e'
line=subprocess.check_output(['nvidia-smi','-i',gpu,'--query-gpu=uuid,name,memory.free','--format=csv,noheader,nounits'],text=True).strip().split(',')
apps=subprocess.check_output(['nvidia-smi','-i',gpu,'--query-compute-apps=gpu_uuid','--format=csv,noheader,nounits'],text=True)
assert line[0].strip()==gpu and line[1].strip()=='NVIDIA GeForce RTX 4090' and int(line[2])>15669 and gpu not in apps
with Path(v['spec']['private_lock']).open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
assert psutil.virtual_memory().available>32*1024**3 and shutil.disk_usage(owned).free>25*1024**3
oldrows={r['relative']:r for r in json.loads((old/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes())['files']}
B.mkdir(parents=True);need=[];copied=0
for row in v['manifest']['files']:
 rel=row['relative'];r=PurePosixPath(rel);dest=B/rel;src=old/rel;prior=oldrows.get(rel)
 assert not r.is_absolute() and '..' not in r.parts and '\\' not in rel and dest.resolve().is_relative_to(B.resolve())
 dest.parent.mkdir(parents=True,exist_ok=True)
 if prior and prior['bytes']==row['bytes'] and prior['SHA']==row['SHA'] and src.is_file() and not src.is_symlink() and src.stat().st_size==row['bytes']:shutil.copy2(src,dest);copied+=1
 else:need.append(row)
for name in ('home','tmp','cache','config','data'):(B/'job0'/name).mkdir(exist_ok=True)
assert shutil.disk_usage(B).free>25*1024**3
print(json.dumps(dict(root=str(B),need_upload=need,files_reused=copied,resource=dict(GPU_UUID=gpu,free_MiB=int(line[2]),RAM_available=psutil.virtual_memory().available,disk_after_copy=shutil.disk_usage(B).free,mount=mount),old210_canonical_not_read_or_used=True,no_account_write=True,no_GO=True)))'''
ACCOUNT=r'''from pathlib import Path
import json,fcntl,hashlib
C=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');raw=C.read_bytes();c=json.loads(raw)
assert c['active_segment'] is None and c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026' and c['budget_mode']=='finite_original_limits_restored_after_single4090_return'
assert c['remaining_training_seconds']==v['remaining'] and c['remaining_training_seconds']>86412.86069250107
for p in (C.parent/'native_floor_supervisor.lock',C.parent/'autonomy_controller.lock'):
 with p.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
print(json.dumps(dict(SHA=hashlib.sha256(raw).hexdigest(),remaining=c['remaining_training_seconds'],canonical_None=True,no_account_write=True)))'''
def main():
 q=json.loads((R/'NATIVE93_TWO_DISTINCT_TARGET_ALIAS_SOURCE_PREPARED_ACTUAL.json').read_bytes())
 wc=json.loads((T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027/W35_fixed92_correct_normal900_collector_v1_source/reports/W35_FIXED92_COMPLETE_FINAL_OR_PARTIAL_ORIGINAL_COST_RETURNED_ACTUAL.json').read_bytes())
 assert wc['actual_finite_returned'] and wc['canonical_None'] and wc['original_owner_private_shared_locks_free']
 put('NATIVE93_TWO_TARGET_ACTUAL_INSTALL_CONSUMED.json',dict(epoch=time.time(),new_source_initial_CPU_each_target=True,no_GO=True))
 prior=load('prepared93_base_installer_definitions_only',N/'install_native93_actual_source_SDK_CPU_UNUSED_once.py')
 cpu=load('prior90_CPU_wait_identity_definitions_only',T/'MOD4_H1_FLAT05_NATIVE_SINGLE72_RESOURCE_V90_20261027/install_flat90_parent_directory_fixed_source_CPU_V2_once.py').CPU
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sys.path.insert(0,str(T/'MOD4_MOE_T2Z_SINGLE4090_QUANTIZED_PREPARATION_20261025'));import strict_user_forwarded_original210_transport_v1 as route
 memory=load('native93_same_authorized_memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');secret=memory.recover();c=None
 results={};resources={}
 try:
  c=d.connect72(secret);before=d.code(c,d.PY72,ACCOUNT,dict(remaining=wc['closing_remaining_snapshot']),timeout=45);c.close();c=None
  put('NATIVE93_SOLE72_BEFORE_CPU_ACTUAL.json',before)
  for alias in ('h1','h1_210'):
   row=q['targets'][alias];sp=row['spec'];B=Path(row['payload']);mf=json.loads((B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes());root=sp['job_root'];assert hashlib.sha256((B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes()).hexdigest()==sp['payload_manifest_SHA']
   c=d.connect72(secret) if alias=='h1' else route.connect();python=d.PY72 if alias=='h1' else route.PY
   payload=dict(root=root,manifest=mf,native_SHA=sp['source_SHA'],closed_W35_remaining=wc['closing_remaining_snapshot'],closed_W35_original_fee=wc['original_fee_seconds'],spec=sp)
   copied=d.code(c,python,prior.PRE if alias=='h1' else PRE210,payload,timeout=150);put(alias+'_NATIVE93_ACTUAL_PRECOPY_RESOURCE.json',copied)
   sf=c.open_sftp();sf.get_channel().settimeout(180)
   try:
    for r in copied['need_upload']:sf.put(str(B/r['relative']),root+'/'+r['relative'])
    sf.put(str(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'),root+'/THREE_SLOT_COMPLETE_MANIFEST_V1.json')
   finally:sf.close()
   result=d.code(c,python,cpu,dict(root=root,manifest_SHA=sp['payload_manifest_SHA']),timeout=330)
   put(alias+'_NATIVE93_ACTUAL_SOURCE_SDK_CPU_RETURNED.json',dict(**result,resource=copied,actual_finite_returned=True));assert result['passed'],dict(errors=result.get('errors'),stdout_tail=result.get('stdout_tail'))
   results[alias]=result;resources[alias]=copied;c.close();c=None
  c=d.connect72(secret);after=d.code(c,d.PY72,ACCOUNT,dict(remaining=wc['closing_remaining_snapshot']),timeout=45);assert after==before;c.close();c=None
  put('NATIVE93_TWO_DISTINCT_TARGET_SOURCE_SDK_CPU_RETURNED_ACTUAL.json',dict(passed=True,actual_finite_returned=True,results=results,resources=resources,canonical_before_after=before,no_account_write_or_GO=True,actual_own_source_initial_load_count_per_target=1,normal86_frozen_witness_initial_load_count_per_target=1))
  print(json.dumps(dict(two_actual_target_CPU_passed=True,no_GO=True)))
 finally:
  secret=None
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:put('NATIVE93_TWO_TARGET_INSTALL_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_same_root_retry_or_GO=True));raise
