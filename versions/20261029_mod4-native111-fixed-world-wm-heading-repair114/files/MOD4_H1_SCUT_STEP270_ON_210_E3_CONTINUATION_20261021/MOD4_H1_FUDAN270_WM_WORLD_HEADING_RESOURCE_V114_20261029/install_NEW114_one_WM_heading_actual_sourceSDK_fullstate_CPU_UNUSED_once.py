"""One NEW114 CPU-only target admission; no actual learning/GPU/GO/account write."""
from pathlib import Path
import hashlib,importlib.util,json,sys,threading,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def module(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
PRE=r'''
from pathlib import Path,PurePosixPath
import fcntl,hashlib,json,psutil,shutil
owned=Path('/home/lc01/Zonglin Li/zonglin2/tasks');B=Path(v['root']);old=owned/'MOD4_H1_FUDAN270_REWARD_COHERENCE_2610v111/seed27';owner=owned/'MOD4_TWO111_FUDAN270_COHERENT_REWARD_2610v111/owner'
assert B.resolve().is_relative_to(owned.resolve()) and not B.exists()
C=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');raw=C.read_bytes();c=json.loads(raw)
assert c['active_segment'] is None and c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026' and c['budget_mode']=='finite_original_limits_restored_after_single4090_return'
assert c['authorized_training_seconds']==2268000 and c['historical_budget_extension_count']==9 and c['new_authority_budget_extensions']==[] and c['remaining_training_seconds']>86412.86069250107
cohort=json.loads((owner/'COHORT_FINAL.json').read_bytes());ending=json.loads((owner/'OWNER_EXIT_ACTUAL.json').read_bytes());assert cohort['original_cost_settled'] and ending['original_cost_settled'] and set(cohort['go'])=={'h1','h1_seed28'}
assert all(g['original_owner_pid']==647089 and g['original_owner_creation']==1793244602.05 for g in cohort['go'].values())
segments=[x for x in c['completed_segments'] if x['owner_parent_pid']==647089 and set(x['experts'])=={'h1','h1_seed28'} and all(x['experts'][k]['started_epoch']==cohort['go'][k]['learning_started_epoch'] for k in ('h1','h1_seed28'))]
assert len(segments)==1 and segments[0]['charged_expert_seconds']==7227.6322910785675
assert segments[0]['experts']['h1']['charged_seconds']==3612.3156723976135 and segments[0]['experts']['h1_seed28']['charged_seconds']==3615.316618680954
try:
 q=psutil.Process(647089)
 if q.create_time()==1793244602.05:assert q.status()==psutil.STATUS_ZOMBIE,'known111 still executing'
except psutil.NoSuchProcess:pass
gpu=v['GPU'];assert gpu=='GPU-c27eecbd-6838-7290-1cd2-37e34522213d'
for p in (C.parent/'native_floor_supervisor.lock',C.parent/'autonomy_controller.lock',C.parent.parent/('three_expert_v2_'+gpu+'.lock'),C.parent.parent/'finite_environment_validation.lock'):
 with p.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
assert psutil.virtual_memory().available>32*1024**3 and shutil.disk_usage(owned).free>25*1024**3
oldrows={r['relative']:r for r in json.loads((old/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes())['files']};B.mkdir(parents=True);need=[];copied=0
for row in v['manifest']['files']:
 rel=row['relative'];r=PurePosixPath(rel);dest=B/rel;src=old/rel;previous=oldrows.get(rel)
 assert not r.is_absolute() and '..' not in r.parts and '\\' not in rel and dest.resolve().is_relative_to(B.resolve())
 dest.parent.mkdir(parents=True,exist_ok=True)
 if rel==v['new_native_relative']:
  src=Path(v['native_source_path']);assert src==old/'job0/production/native_supermimic_H1_final.pt' and not src.is_symlink() and src.stat().st_size==row['bytes'];shutil.copy2(src,dest);copied+=1
 elif previous and previous['bytes']==row['bytes'] and previous['SHA']==row['SHA'] and src.is_file() and not src.is_symlink() and src.stat().st_size==row['bytes']:shutil.copy2(src,dest);copied+=1
 else:need.append(row)
for name in ('home','tmp','cache','config','data'):(B/'job0'/name).mkdir(exist_ok=True)
assert shutil.disk_usage(B).free>25*1024**3 and C.read_bytes()==raw
print(json.dumps(dict(root=str(B),need_upload=need,files_reused=copied,C_SHA=hashlib.sha256(raw).hexdigest(),remaining_snapshot=c['remaining_training_seconds'],resource=dict(GPU_UUID=gpu,CPU_only_not_GPU_admission=True,RAM_available=psutil.virtual_memory().available,disk_after_copy=shutil.disk_usage(B).free),original111_fees_closed_CNone_readonly=True,no_account_write=True,no_GO=True)))
'''
def main():
 prep=json.loads((R/'NEW114_V2_ONE_SOURCE111_TYPED_PAYLOAD_PREPARED_NOT_ADMITTED_ACTUAL.json').read_bytes())
 proof=R/'SOURCE114_V2_PREINSTALL_TASK_GO_HELPER_PRODUCER_CPU_ACTUAL.json'
 assert prep['passed_preparation'] and json.loads(proof.read_bytes())['passed']
 seal=json.loads((R/'FROZEN_NEW114_ONE_ACTUAL_TARGET_CPU_ENTRY_SOURCE_INDEX_V1.json').read_bytes())
 assert H(Path(__file__))==seal['entry_SHA'] and prep['manifest_SHA']==seal['manifest_SHA'] and H(proof)==seal['source_Task_GO_proof_SHA']
 marker=R/'NEW114_ONE_ACTUAL_TARGET_CPU_ENTRY_CONSUMED.json';assert not marker.exists()
 put(marker.name,dict(epoch=time.time(),no_GPU_GO=True,newpurpose='One source111 fullnative + normal86 witness for new114 source/inputnorm admission'))
 wait=module('new114_actual_CPU_wait_definitions_only',T/'MOD4_H1_FLAT05_NATIVE_SINGLE72_RESOURCE_V90_20261027/install_flat90_parent_directory_fixed_source_CPU_V2_once.py')
 wrapper=module('new114_compressed_memory_install_only',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py');transport,previous=wrapper.install()
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sec=module('new114_original72_memory_only',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');secret=sec.recover();client=None;stop=threading.Event()
 def progress():
  while not stop.wait(25):print(json.dumps(dict(stage='SAME_HANDLE_NEW114_ONE_SOURCE_SDK_FULLSTATE_CPU',epoch=time.time())),flush=True)
 th=threading.Thread(target=progress,daemon=True);th.start()
 try:
  client=d.connect72(secret);secret=None;B=Path(prep['payload']);task=prep['task'];manifest=json.loads((B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes());root=prep['job_root']
  resource=d.code(client,d.PY72,PRE,dict(root=root,GPU=prep['GPU_UUID'],manifest=manifest,new_native_relative='job0/source/'+task['source_filename'],native_source_path=prep['source']['path']),timeout=120)
  put('NEW114_ACTUAL_PRECOPY_CURRENT_AUTHORITY_AND_CPU_RESOURCE.json',resource)
  sf=client.open_sftp();sf.get_channel().settimeout(120)
  try:
   for row in resource['need_upload']:sf.put(str(B/row['relative']),root+'/'+row['relative'])
   sf.put(str(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'),root+'/THREE_SLOT_COMPLETE_MANIFEST_V1.json')
  finally:sf.close()
  value=d.code(client,d.PY72,wait.CPU,dict(root=root,manifest_SHA=prep['manifest_SHA']),timeout=300)
  put('NEW114_ACTUAL_SOURCE_SDK_FULLSTATE_CPU_RETURNED_ACTUAL.json',dict(epoch=time.time(),actual_finite_returned=True,actual_job_root=root,resource=resource,**value))
  assert value['passed'],dict(errors=value.get('errors'),stdout_tail=value.get('stdout_tail'))
  print(json.dumps(dict(passed_actual_target_CPU=True,report_SHA=value['proof']['report_SHA'],wait_proof_SHA=value['proof_SHA'],no_GPU_GO=True)),flush=True)
 finally:
  secret=None;stop.set();th.join(1)
  if client:client.close()
  transport.SESSION=previous
if __name__=='__main__':
 try:main()
 except BaseException:put('NEW114_TARGET_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),traceback=traceback.format_exc(),no_retry_or_GO_or_partial_promotion=True));raise
