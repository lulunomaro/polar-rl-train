from pathlib import Path
import importlib.util,json,sys,time,traceback,threading
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports';L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027'
def put(name,v):
 with (R/name).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
PRE="\nfrom pathlib import Path,PurePosixPath\nimport fcntl,hashlib,json,psutil,shutil,subprocess,time\nowned=Path('/home/lc01/Zonglin Li/zonglin2/tasks');B=Path(v['root']);old=owned/'MOD4_H1_FUDAN270_EPISODE20_2610v107CPUv2/seed27';stage=owned/'MOD4_TWO107_FUDAN270_EPISODE20_2610v106'\nassert B.resolve().is_relative_to(owned.resolve()) and not B.exists()\nC=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');raw=C.read_bytes();c=json.loads(raw)\nassert c['active_segment'] is None and c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026' and c['budget_mode']=='finite_original_limits_restored_after_single4090_return'\nassert c['authorized_training_seconds']==2268000 and c['historical_budget_extension_count']==9 and c['new_authority_budget_extensions']==[] and c['remaining_training_seconds']>86412.86069250107\ncohort=json.loads((stage/'owner/COHORT_FINAL.json').read_bytes());ending=json.loads((stage/'owner/OWNER_EXIT_ACTUAL.json').read_bytes());assert cohort['original_cost_settled'] and ending['original_cost_settled'] and set(cohort['go'])=={'h1','h1_seed28'}\nassert all(g['original_owner_pid']==630841 and g['original_owner_creation']==1793213510.36 for g in cohort['go'].values())\nsegments=[x for x in c['completed_segments'] if x['owner_parent_pid']==630841 and set(x['experts'])=={'h1','h1_seed28'} and all(x['experts'][k]['started_epoch']==cohort['go'][k]['learning_started_epoch'] for k in ('h1','h1_seed28'))]\nassert len(segments)==1 and segments[0]['charged_expert_seconds']==7229.854897737503\nassert segments[0]['experts']['h1']['charged_seconds']==3613.4053947925568 and segments[0]['experts']['h1_seed28']['charged_seconds']==3616.4495029449463\nfor pid,created in ((630841,1793213510.36),(630857,1793213511.01),(630876,1793213511.66)):\n try:\n  q=psutil.Process(pid)\n  if q.create_time()==created:assert q.status()==psutil.STATUS_ZOMBIE,'known107 still executing'\n except psutil.NoSuchProcess:pass\ngpu=v['GPU'];assert gpu in ('GPU-c27eecbd-6838-7290-1cd2-37e34522213d','GPU-16828f91-2b45-b646-8dc0-9481138e2842')\nfor p in (C.parent/'native_floor_supervisor.lock',C.parent/'autonomy_controller.lock',C.parent.parent/('three_expert_v2_'+gpu+'.lock'),C.parent.parent/'finite_environment_validation.lock'):\n with p.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)\nassert psutil.virtual_memory().available>32*1024**3 and shutil.disk_usage(owned).free>25*1024**3\noldrows={r['relative']:r for r in json.loads((old/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes())['files']};B.mkdir(parents=True);need=[];copied=0\nfor row in v['manifest']['files']:\n rel=row['relative'];r=PurePosixPath(rel);dest=B/rel;src=old/rel;previous=oldrows.get(rel)\n assert not r.is_absolute() and '..' not in r.parts and '\\\\' not in rel and dest.resolve().is_relative_to(B.resolve())\n dest.parent.mkdir(parents=True,exist_ok=True)\n if rel==v['new_native_relative']:\n  native=Path(v['native_source_path']);assert native==old/'job0/production/native_supermimic_H1_final.pt' and not native.is_symlink() and native.stat().st_size==row['bytes'];shutil.copy2(native,dest);copied+=1\n elif previous and previous['bytes']==row['bytes'] and previous['SHA']==row['SHA'] and src.is_file() and not src.is_symlink() and src.stat().st_size==row['bytes']:shutil.copy2(src,dest);copied+=1\n else:need.append(row)\nfor name in ('home','tmp','cache','config','data'):(B/'job0'/name).mkdir(exist_ok=True)\nassert shutil.disk_usage(B).free>25*1024**3 and C.read_bytes()==raw\nprint(json.dumps(dict(root=str(B),need_upload=need,files_reused=copied,C_SHA=hashlib.sha256(raw).hexdigest(),remaining_snapshot=c['remaining_training_seconds'],resource=dict(GPU_UUID=gpu,CPU_only_not_GPU_admission=True,RAM_available=psutil.virtual_memory().available,disk_after_copy=shutil.disk_usage(B).free),original107_fees_allout_CNone_readonly=True,no_account_write=True,no_GO=True)))\n"
def main():
 prep=json.loads((R/'TWO111_SOURCE_PAYLOADS_PREPARED_NO_GO_ACTUAL.json').read_bytes());assert prep['passed']
 assert json.loads((R/'SOURCE111_PREINSTALL_TASK_GO_SOURCE_BINDING_CPU_ACTUAL.json').read_bytes())['passed']
 put('TWO111_CPU_ONLY_V3_INSTALL_ENTRY_CONSUMED_ACTUAL.json',dict(epoch=time.time(),modes=['seed27','seed28'],one_serial72_connection=True,no_GO=True))
 wait=module('two103_original_actual_CPU_wait_definitions',T/'MOD4_H1_FLAT05_NATIVE_SINGLE72_RESOURCE_V90_20261027/install_flat90_parent_directory_fixed_source_CPU_V2_once.py')
 wrapper=module('two103_compressed_install_only',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py');transport,previous=wrapper.install();sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sec=module('two103_same_authorized_memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');secret=sec.recover();client=None;stop=threading.Event()
 def progress():
  while not stop.wait(25):print(json.dumps(dict(stage='SAME_HANDLE_TWO111_FUDAN270_SOURCE_SDK_CPU',epoch=time.time())),flush=True)
 thread=threading.Thread(target=progress,daemon=True);thread.start();results={}
 try:
  client=d.connect72(secret);secret=None
  for mode in ('seed27','seed28'):
   spec=prep['payloads'][mode];B=Path(spec['payload']);task=spec['task'];manifest=json.loads((B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes());root=spec['job_root']
   resource=d.code(client,d.PY72,PRE,dict(root=root,GPU=spec['GPU_UUID'],manifest=manifest,new_native_relative='job0/source/'+task['source_filename'],native_source_path=spec['source']['path']),timeout=120);put('NATIVE111_V1_'+mode+'_ACTUAL_PRECOPY_RESOURCE_RETURNED.json',resource)
   sf=client.open_sftp();sf.get_channel().settimeout(120)
   try:
    for row in resource['need_upload']:sf.put(str(B/row['relative']),root+'/'+row['relative'])
    sf.put(str(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'),root+'/THREE_SLOT_COMPLETE_MANIFEST_V1.json')
   finally:sf.close()
   value=d.code(client,d.PY72,wait.CPU,dict(root=root,manifest_SHA=spec['manifest_SHA']),timeout=300);results[mode]=dict(**value,resource=resource,actual_finite_returned=True,actual_job_root=root)
   put('NATIVE111_V1_'+mode+'_ACTUAL_SOURCE_SDK_CPU_RETURNED_ACTUAL.json',results[mode]);assert value['passed'],dict(mode=mode,errors=value.get('errors'),stdout_tail=value.get('stdout_tail'))
   print(json.dumps(dict(mode=mode,actual_CPU_passed=True,report_SHA=value['proof']['report_SHA'],wait_proof_SHA=value['proof_SHA'],no_GO=True)),flush=True)
  put('TWO111_V3_ACTUAL_TWO_SOURCE_SDK_CPU_RETURNED_ACTUAL.json',dict(passed=True,epoch=time.time(),results=results,actual_one72_finite_returned=True,no_GO=True))
 finally:
  secret=None;stop.set();thread.join(1)
  if client:client.close()
  transport.SESSION=previous
if __name__=='__main__':
 try:main()
 except BaseException:put('TWO111_CPU_ONLY_V3_INSTALL_ORIGINAL_ERROR_ACTUAL.json',dict(epoch=time.time(),error=traceback.format_exc(),no_retry_or_GO_or_partial_promotion=True));raise
