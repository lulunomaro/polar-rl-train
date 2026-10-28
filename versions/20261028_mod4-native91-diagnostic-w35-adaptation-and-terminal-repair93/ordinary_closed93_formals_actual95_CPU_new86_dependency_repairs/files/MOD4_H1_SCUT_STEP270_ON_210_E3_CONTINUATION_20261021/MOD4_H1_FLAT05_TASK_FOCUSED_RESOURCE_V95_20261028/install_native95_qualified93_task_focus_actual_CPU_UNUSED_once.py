"""New95 source/SDK CPU admission, one original72 SSH, no learning GO."""
from pathlib import Path
import importlib.util,json,sys,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports';B=N/'payload'
REMOTE='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_H1_FLAT05_TASK_FOCUSED_2610v95/h1'

def put(name,v):
 with (R/name).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

PRE=r'''from pathlib import Path,PurePosixPath
import json,hashlib,fcntl,psutil,subprocess,shutil
B=Path(v['root']);owned=Path('/home/lc01/Zonglin Li/zonglin2/tasks');old=owned/'MOD4_H1_FLAT05_TERMINAL_2610v93/h1';stage=owned/'MOD4_THREE93_NATIVE_TERMINAL_E2_20261028'
assert B.resolve().is_relative_to(owned.resolve()) and not B.exists()
C=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');raw=C.read_bytes();c=json.loads(raw)
assert c['active_segment'] is None and c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026' and c['budget_mode']=='finite_original_limits_restored_after_single4090_return'
assert c['remaining_training_seconds']==539470.7667970657 and c['remaining_training_seconds']>86412.86069250107
for path in (C.parent/'native_floor_supervisor.lock',C.parent/'autonomy_controller.lock',C.parent.parent/'three_expert_v2_GPU-c27eecbd-6838-7290-1cd2-37e34522213d.lock',C.parent.parent/'finite_environment_validation.lock'):
 with path.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
cohort=json.loads((stage/'owner/COHORT_FINAL.json').read_bytes());ending=json.loads((stage/'owner/OWNER_EXIT_ACTUAL.json').read_bytes());node=json.loads((stage/'node_h1/NODE_TERMINAL_ACTUAL.json').read_bytes())['row']
assert cohort['original_cost_settled'] and ending['original_cost_settled'] and node['terminal_all_own_children_waited'] and not node['original_error'] and node['returncode']==0 and node['final']['passed']
go=cohort['go']['h1'];assert go['original_owner_pid']==562239 and go['original_owner_creation']==1793124879.47 and go['learning_started_epoch']==1793124888.9690776
segments=[x for x in c['completed_segments'] if x['owner_parent_pid']==562239 and x['experts']['h1']['started_epoch']==go['learning_started_epoch']]
assert len(segments)==1 and segments[0]['charged_expert_seconds']==7291.4024312496185
assert set(segments[0]['experts'])=={'h1','h1_210','e2'} and segments[0]['experts']['h1_210']['charged_seconds']==51.172107219696045
formal=node['final']['final'];assert formal['SHA']==v['native_SHA'] and formal['bytes']==256230153
native=Path(formal['path']);assert native.resolve().is_relative_to(old.resolve()) and native.is_file() and not native.is_symlink() and native.stat().st_size==formal['bytes']
gpu='GPU-c27eecbd-6838-7290-1cd2-37e34522213d';line=subprocess.check_output(['nvidia-smi','-i',gpu,'--query-gpu=uuid,name,memory.free','--format=csv,noheader,nounits'],text=True).strip().split(',');apps=subprocess.check_output(['nvidia-smi','-i',gpu,'--query-compute-apps=gpu_uuid','--format=csv,noheader,nounits'],text=True)
assert line[0].strip()==gpu and line[1].strip()=='NVIDIA GeForce RTX 4090' and int(line[2])>15669 and gpu not in apps
assert psutil.virtual_memory().available>32*1024**3 and shutil.disk_usage(owned).free>25*1024**3
oldrows={r['relative']:r for r in json.loads((old/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes())['files']}
B.mkdir(parents=True);need=[];copied=0
for row in v['manifest']['files']:
 rel=row['relative'];r=PurePosixPath(rel);dest=B/rel;src=old/rel;prior=oldrows.get(rel)
 assert not r.is_absolute() and '..' not in r.parts and '\\' not in rel and dest.resolve().is_relative_to(B.resolve())
 dest.parent.mkdir(parents=True,exist_ok=True)
 if rel=='job0/source/H1_native93_qualified_h1.pt':shutil.copy2(native,dest);copied+=1
 elif prior and prior['bytes']==row['bytes'] and prior['SHA']==row['SHA'] and src.is_file() and not src.is_symlink() and src.stat().st_size==row['bytes']:shutil.copy2(src,dest);copied+=1
 else:need.append(row)
for name in ('home','tmp','cache','config','data'):(B/'job0'/name).mkdir(exist_ok=True)
assert shutil.disk_usage(B).free>25*1024**3 and C.read_bytes()==raw
print(json.dumps(dict(root=str(B),need_upload=need,files_reused=copied,resource=dict(GPU_UUID=gpu,free_MiB=int(line[2]),RAM_available=psutil.virtual_memory().available,disk_after_copy=shutil.disk_usage(B).free),C_SHA=hashlib.sha256(raw).hexdigest(),remaining=c['remaining_training_seconds'],actual93_original_fee_and_closed_formal_passed=True,no_account_write=True,no_GO=True)))'''

def main():
 put('NATIVE95_INSTALL_CONSUMED_ACTUAL.json',dict(epoch=time.time(),new_source_initial_CPU_purpose=True,no_GO=True))
 prep=json.loads((R/'NATIVE95_SOURCE_PREPARED_ACTUAL.json').read_bytes());manifest=json.loads((B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes())
 previous=T/'MOD4_H1_FLAT05_NATIVE_SINGLE72_RESOURCE_V90_20261027/install_flat90_parent_directory_fixed_source_CPU_V2_once.py';m=module('original_actual_CPU_wait_wrapper_definitions',previous)
 wrapper=module('same_authorized_compressed_install_only',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py');transport,oldsession=wrapper.install()
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sec=module('same_authorized_memory_secret',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');secret=sec.recover();c=None
 try:
  c=d.connect72(secret);secret=None
  resource=d.code(c,d.PY72,PRE,dict(root=REMOTE,manifest=manifest,native_SHA=prep['task']['source_SHA']),timeout=120);put('NATIVE95_ACTUAL_PRECOPY_RESOURCE_RETURNED.json',resource)
  sf=c.open_sftp();sf.get_channel().settimeout(120)
  try:
   for row in resource['need_upload']:sf.put(str(B/row['relative']),REMOTE+'/'+row['relative'])
   sf.put(str(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'),REMOTE+'/THREE_SLOT_COMPLETE_MANIFEST_V1.json')
  finally:sf.close()
  result=d.code(c,d.PY72,m.CPU,dict(root=REMOTE,manifest_SHA=prep['h1_spec_pending_actual_CPU_and_controller']['payload_manifest_SHA']),timeout=300)
  put('NATIVE95_ACTUAL_SOURCE_SDK_CPU_AND_RESOURCE_RETURNED_ACTUAL.json',dict(**result,resource=resource,actual_finite_returned=True))
  assert result['passed'],dict(errors=result.get('errors'),stdout_tail=result.get('stdout_tail'))
  print(json.dumps(dict(actual_CPU_passed=True,CPU_SHA=result['proof']['report_SHA'],CPU_proof_SHA=result['proof_SHA'],no_GO=True)))
 finally:
  secret=None
  if c:c.close()
  transport.SESSION=oldsession

if __name__=='__main__':
 try:main()
 except BaseException:put('NATIVE95_INSTALL_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(traceback=traceback.format_exc(),no_retry_or_GO=True));raise
