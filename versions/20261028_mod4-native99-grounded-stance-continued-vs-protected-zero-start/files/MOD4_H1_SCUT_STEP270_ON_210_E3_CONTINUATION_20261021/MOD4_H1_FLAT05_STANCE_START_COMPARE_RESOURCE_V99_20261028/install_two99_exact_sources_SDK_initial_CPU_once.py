from pathlib import Path
import importlib.util,json,sys,time,traceback,threading
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports';L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027'
def put(n,x):
 with (R/n).open('x',encoding='utf8') as f:json.dump(x,f,indent=2,allow_nan=False)
def module(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
PRE=r'''from pathlib import Path,PurePosixPath
import json,hashlib,fcntl,psutil,subprocess,shutil
B=Path(v['root']);owned=Path('/home/lc01/Zonglin Li/zonglin2/tasks');old=owned/'MOD4_H1_FLAT05_TASK_FOCUSED_2610v97/h1';stage=owned/'MOD4_TWO97_H1_E3_2610v97'
assert B.resolve().is_relative_to(owned.resolve()) and not B.exists()
C=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');raw=C.read_bytes();c=json.loads(raw)
assert c['active_segment'] is None and c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026' and c['budget_mode']=='finite_original_limits_restored_after_single4090_return'
assert c['remaining_training_seconds']==531527.5335400105 and c['remaining_training_seconds']>86412.86069250107
cohort=json.loads((stage/'owner/COHORT_FINAL.json').read_bytes());ending=json.loads((stage/'owner/OWNER_EXIT_ACTUAL.json').read_bytes());assert cohort['original_cost_settled'] and ending['original_cost_settled'] and set(cohort['go'])=={'h1','e3'}
assert all(g['original_owner_pid']==595647 and g['original_owner_creation']==1793175876.15 for g in cohort['go'].values())
segments=[a for a in c['completed_segments'] if a['owner_parent_pid']==595647 and set(a['experts'])=={'h1','e3'} and all(a['experts'][k]['started_epoch']==cohort['go'][k]['learning_started_epoch'] for k in ('h1','e3'))]
assert len(segments)==1 and segments[0]['charged_expert_seconds']==7259.734082698822 and segments[0]['experts']['h1']['charged_seconds']==3615.187491416931 and segments[0]['experts']['e3']['charged_seconds']==3644.546591281891
for key in ('h1','e3'):
 node=json.loads((stage/('node_'+key)/'NODE_TERMINAL_ACTUAL.json').read_bytes())['row'];exit=json.loads((stage/('node_'+key)/'NODE_EXIT_ACTUAL.json').read_bytes())
 assert node['terminal_all_own_children_waited'] and not node['original_error'] and node['returncode']==0 and node['final']['passed'] and exit['actual_all_own_children_waited']
for row in v['known_original_nodes_owner']:
 try:
  p=psutil.Process(row['pid']);creation=p.create_time()
  if creation==row['creation']:assert p.status()==psutil.STATUS_ZOMBIE,'known original97 process is still executing'
 except psutil.NoSuchProcess:pass
gpu=v['GPU'];assert gpu in ('GPU-c27eecbd-6838-7290-1cd2-37e34522213d','GPU-16828f91-2b45-b646-8dc0-9481138e2842')
for path in (C.parent/'native_floor_supervisor.lock',C.parent/'autonomy_controller.lock',C.parent.parent/('three_expert_v2_'+gpu+'.lock'),C.parent.parent/'finite_environment_validation.lock'):
 with path.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
line=subprocess.check_output(['nvidia-smi','-i',gpu,'--query-gpu=uuid,name,memory.free','--format=csv,noheader,nounits'],text=True).strip().split(',');apps=subprocess.check_output(['nvidia-smi','-i',gpu,'--query-compute-apps=gpu_uuid','--format=csv,noheader,nounits'],text=True)
assert line[0].strip()==gpu and line[1].strip()=='NVIDIA GeForce RTX 4090' and int(line[2])>15669 and gpu not in apps
assert psutil.virtual_memory().available>32*1024**3 and shutil.disk_usage(owned).free>25*1024**3
oldrows={r['relative']:r for r in json.loads((old/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes())['files']}
B.mkdir(parents=True);need=[];copied=0
for row in v['manifest']['files']:
 rel=row['relative'];r=PurePosixPath(rel);dest=B/rel;src=old/rel;prior=oldrows.get(rel)
 assert not r.is_absolute() and '..' not in r.parts and '\\' not in rel and dest.resolve().is_relative_to(B.resolve())
 dest.parent.mkdir(parents=True,exist_ok=True)
 if rel==v['new_native_relative'] and v['mode']=='continue97':
  native=Path(v['native_source_path']);assert native.resolve().is_relative_to(old.resolve()) and not native.is_symlink() and native.stat().st_size==row['bytes'];shutil.copy2(native,dest);copied+=1
 elif prior and prior['bytes']==row['bytes'] and prior['SHA']==row['SHA'] and src.is_file() and not src.is_symlink() and src.stat().st_size==row['bytes']:shutil.copy2(src,dest);copied+=1
 else:need.append(row)
for name in ('home','tmp','cache','config','data'):(B/'job0'/name).mkdir(exist_ok=True)
assert shutil.disk_usage(B).free>25*1024**3 and C.read_bytes()==raw
print(json.dumps(dict(root=str(B),need_upload=need,files_reused=copied,resource=dict(GPU_UUID=gpu,free_MiB=int(line[2]),RAM_available=psutil.virtual_memory().available,disk_after_copy=shutil.disk_usage(B).free),C_SHA=hashlib.sha256(raw).hexdigest(),remaining=c['remaining_training_seconds'],original97_fee_allout_and_CNone_readonly=True,no_account_write=True,no_GO=True)))'''
def main():
 prep=json.loads((R/'TWO99_EXACT_START_PAYLOADS_PREPARED_ACTUAL.json').read_bytes());assert prep['passed']
 launched=json.loads((L/'TWO97_H1_E3_NEW_FULL_CPU_OWNER_SOURCE_V1/reports/TWO97_ACTUAL_OWNER_AND_TWO_NODES_DETACHED.json').read_bytes());known=[v['exact_identity'] for v in launched['identities'].values()]
 put('TWO99_INSTALL_SOURCE_CPU_CONSUMED_ACTUAL.json',dict(epoch=time.time(),modes=['continue97','restart0'],one_serial72_connection=True,no_GO=True))
 wait=module('two99_original_actual_CPU_wait_definitions',T/'MOD4_H1_FLAT05_NATIVE_SINGLE72_RESOURCE_V90_20261027/install_flat90_parent_directory_fixed_source_CPU_V2_once.py')
 wrapper=module('two99_compressed_install_only',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py');transport,previous=wrapper.install();sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sec=module('two99_same_authorized_memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');secret=sec.recover();client=None;stop=threading.Event()
 def progress():
  while not stop.wait(25):print(json.dumps(dict(stage='SAME_HANDLE_TWO99_SOURCE_SDK_CPU',epoch=time.time())),flush=True)
 thread=threading.Thread(target=progress,daemon=True);thread.start();results={}
 try:
  client=d.connect72(secret);secret=None
  for mode in ('continue97','restart0'):
   spec=prep['payloads'][mode];B=Path(spec['payload']);task=spec['task'];manifest=json.loads((B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes());root=spec['job_root']
   resource=d.code(client,d.PY72,PRE,dict(root=root,GPU=spec['GPU_UUID'],mode=mode,manifest=manifest,known_original_nodes_owner=known,new_native_relative='job0/source/'+task['source_filename'],native_source_path=spec['source']['path']),timeout=120);put('NATIVE99_'+mode+'_ACTUAL_PRECOPY_RESOURCE_RETURNED.json',resource)
   sf=client.open_sftp();sf.get_channel().settimeout(120)
   try:
    for row in resource['need_upload']:sf.put(str(B/row['relative']),root+'/'+row['relative'])
    sf.put(str(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'),root+'/THREE_SLOT_COMPLETE_MANIFEST_V1.json')
   finally:sf.close()
   value=d.code(client,d.PY72,wait.CPU,dict(root=root,manifest_SHA=spec['manifest_SHA']),timeout=300);results[mode]=dict(**value,resource=resource,actual_finite_returned=True)
   put('NATIVE99_'+mode+'_ACTUAL_SOURCE_SDK_CPU_RETURNED_ACTUAL.json',results[mode]);assert value['passed'],dict(mode=mode,errors=value.get('errors'),stdout_tail=value.get('stdout_tail'))
   print(json.dumps(dict(mode=mode,actual_CPU_passed=True,report_SHA=value['proof']['report_SHA'],wait_proof_SHA=value['proof_SHA'],no_GO=True)),flush=True)
  put('TWO99_ACTUAL_TWO_SOURCE_SDK_CPU_RETURNED_ACTUAL.json',dict(passed=True,epoch=time.time(),results=results,actual_one72_finite_returned=True,no_GO=True))
 finally:
  secret=None;stop.set();thread.join(1)
  if client:client.close()
  transport.SESSION=previous
if __name__=='__main__':
 try:main()
 except BaseException:put('TWO99_SOURCE_INSTALL_ORIGINAL_ERROR_ACTUAL.json',dict(epoch=time.time(),error=traceback.format_exc(),no_retry_or_GO_or_partial_promotion=True));raise
