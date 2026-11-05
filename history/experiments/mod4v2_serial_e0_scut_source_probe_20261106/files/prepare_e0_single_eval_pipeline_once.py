"""Write four NEW E0_SINGLE_FROZEN_ pipeline sources plus eval worker v3, without running them.
Frontdoor paths below are actual producer JSON fields, not model inspection or
iteration arithmetic. Missing actual fields stop stage with the precise JSON path
for the parent to verify. This generator itself performs no SSH/SDK/PT/GPU/Git.
A2 was PT0/PPO0 and is not an eligible candidate. Parent must bind FRONTDOOR
closed_pointer/train_plan/expected_train_root to the actually successful v4 train.
"""
from pathlib import Path
import hashlib,json

D = Path(__file__).resolve().parent
T = D.parent / 'mod4v1_experts_fulldr_rm70_20261101'
FRONTDOOR = {
    'closed_pointer': 'E0_SINGLE_ADMISSION3_CLOSED_RESULT_PATH.json',
    'train_plan': 'SOURCE_PLAN_E0_SINGLE_ADMISSION3_ACTUAL_V1.json',
    'expected_train_root': '/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V2_E0_SINGLE_ADMISSION3_FULL_LEARNER_MIGRATION_20261106_001831_1793895511281001300',
    'GPU_UUID': 'GPU-16828f91-2b45-b646-8dc0-9481138e2842',
    'closed': ['closed'],
    'owner_exit': ['metadata', 'OWNER_EXIT_ACTUAL.json'],
    'outer_wait': ['metadata', 'OUTER_OWNER_WAIT_ACTUAL.json'],
    'cohort_final': ['metadata', 'COHORT_FINAL.json'],
    'child_wait': ['cases', 'E0', 'PARENT_WAITED_ACTUAL.json'],
    'producer_final': ['cases', 'E0', 'V2_MIGRATION_FINAL.json'],
    'latest': ['latest_complete_save'],
    'fullsave': ['fullsave'],
    'live_core': ['live_core'],
    'iteration': ['iteration'],
    'Adam17_steps': ['Adam17_steps'],
    'Adam_step': ['source_Adam_step'],
    'optimizer_LRs': ['optimizer_LRs'],
    'LR': ['source_LR'],
}

PARENT_ADDITIONS = r'''
def require(value, message):
 if not value:raise RuntimeError(message)

def own_json(path):
 p=Path(path);require(p.suffix.lower()=='.json' and p.resolve().is_relative_to(B.resolve()),'Own eval JSON only');return json.loads(p.read_bytes())

def make_task(r,plan,deadline,fds):
 require(r['role']=='E0' and len(fds)==2,'Single E0 and original two EX descriptors')
 ad=own_json(B/'ACTUAL_GROUP_ADMISSION.json');receipt=dict(plan['migration_close'])
 require(receipt['roles']==['E0'] and all(receipt[k] is True for k in ('all_closed','actual_wait_complete','resources_released','original_cost_settled','semantic_qualified')),'Actual training close gate')
 require(ad['epoch']>=receipt['closed_epoch'] and ad['selected_card_compute_processes']==[] and ad['resource']['free_MiB']>=23500 and ad['resource']['utilization_percent']==0,'Actual post-close empty-card observation')
 # GPU_settled is derived only NOW, under the two successfully acquired EXs.
 receipt.update(GPU_settled=True,GPU_settle_evidence=dict(epoch=ad['epoch'],GPU_UUID=plan['GPU_UUID'],resource=ad['resource'],compute_processes=[],private_GPU_EX_held=True,global_finite_EX_held=True))
 out=B/'cases/E0';task=dict(plan['task_template'])
 task.update(kind='MOD4V2_N80_FRESH_FULLDR_FROZEN_FINITE_NOT_GRADUATION',role='E0',num_envs=80,controls=1000,seed=20260928,eval_members=['E0'],run_id=plan['group_id'],group_id=plan['group_id'],group_root=str(B),output_dir=str(out),job_root=str(out),owner_pid=os.getpid(),GPU_UUID=plan['GPU_UUID'],absolute_worker_deadline_epoch=deadline,max_additional_updates=1,steps_per_env=24,helper_root=str(B/'helpers'),v8_helper_root=str(B/'worker_sources/parent'),e1_helper_root=str(B/'worker_sources/e1'),migration_cohort_close_receipt=receipt,eval_admission=dict(group_id=plan['group_id'],GPU_UUID=plan['GPU_UUID'],private_GPU_EX_held=True,global_finite_EX_held=True,inherited_lock_fds=list(fds),admitted_epoch=ad['epoch']),source_read_purpose='NEW_E0_SINGLE_FROZEN_N80_'+plan['group_id'])
 return task

def qualify_waited_e0(out,pid,rc,plan):
 # Called only AFTER the actual child p.wait() has returned.
 checks={};detail={};f={};intent={};ready={};started={};pre={};envclose={}
 try:
  fp=out/'V2_FROZEN_EVAL_FINAL.json';raw=fp.read_bytes();f=json.loads(raw)
  intent=own_json(out/'V2_FROZEN_EVAL_APP_CLOSE_INTENT.json');ready=own_json(out/'WORKER_SCENE_READY.json');started=own_json(out/'WORKER_EVAL_STARTED.json');pre=own_json(out/'PRE_CLOSE.json');envclose=own_json(out/'ENV_CLOSE_RETURNED.json');task_raw=(out/'task.json').read_bytes();task=json.loads(task_raw);expect=plan['task_template']
  checks['actual_child_wait_RC0']=rc==0
  checks['actual_worker_parent_identity']=f.get('worker_pid')==pid and f.get('parent_pid')==os.getpid() and intent.get('worker_pid')==pid and intent.get('parent_pid')==os.getpid()
  checks['single_E0_new_purpose']=f.get('role')==intent.get('role')=='E0' and f.get('run_id')==intent.get('run_id')==f.get('group_id')==plan['group_id'] and f.get('GPU_UUID')==plan['GPU_UUID']
  checks['task_binding']=f.get('task_sha256')==intent.get('task_sha256')==hashlib.sha256(task_raw).hexdigest()
  checks['finite_execution']=f.get('execution') is True and f.get('passed_execution') is True and f.get('error') is None
  checks['original_finite_scope']=f.get('num_envs')==80 and f.get('seed')==20260928 and f.get('controls')==1000 and f.get('seconds')==20. and f.get('physics_callbacks')==8000 and f.get('feedback_samples')==2000 and f.get('delay_calls')==dict(legs=8000,wheels=8000)
  checks['ready_zero_precontrols']=ready.get('worker_pid')==pid and ready.get('role')=='E0' and ready.get('group_id')==plan['group_id'] and ready.get('GPU_UUID')==plan['GPU_UUID'] and ready.get('zero_controls_before_barrier') is True and ready.get('precontrols')==ready.get('actor_calls')==0 and ready.get('explicit_fresh_resets')==1 and started.get('zero_precontrols') is True and started.get('group_id')==plan['group_id']
  cache=f.get('source_cache') or {};checks['whole_candidate_once_CPU']=all(cache.get(k)==1 for k in ('physical_byte_opens','SHA_calculations','decodes')) and cache.get('all_original_root_and_nested_cached') is True and cache.get('wholecachedidentity_passed') is True and cache.get('live_actor_STD_strict') is True
  checks['actual_new_candidate_metadata']=cache.get('source_path')==expect['checkpoint_path'] and cache.get('source_SHA')==expect['checkpoint_SHA'] and cache.get('source_iteration')==expect['checkpoint_iteration'] and cache.get('source_Adam17')==expect['checkpoint_Adam_step'] and cache.get('source_LR')==expect['checkpoint_LR']
  checks['no_optimizer_or_saved20k_application']=f.get('optimizer_updates')==0 and f.get('live_critic_optimizer_created') is False and f.get('source_saved20k_DR_history_applied') is False and f.get('source20k_DR_sliced') is False and f.get('whole_saved20k_resume') is False and cache.get('live_critic_optimizer_created') is False and cache.get('source20k_DR_history_applied') is False and cache.get('source20k_state_sliced') is False
  checks['fresh_N80_D0_D7_before_after']=all(isinstance(f.get(k),dict) and f[k].get('fresh_N80_D0_D7_enabled') is True and f[k].get('one_explicit_fresh_reset')==1 and f[k].get('saved20k_history_physically_applied') is False and f[k].get('new_constructor_nominals_preserved') is True and (f[k].get('actual_parameters') or {}).get('actual_parameters_pass') is True for k in ('fresh_fullDR_before','fresh_fullDR_after'))
  actor=f.get('actor') or {};checks['strict_frozen_original_actor']=actor.get('strict_actor_and_embedded_learned_normalizer') is True and actor.get('no_live_critic_or_optimizer') is True and actor.get('normalization_updated') is False and actor.get('mean_only') is True and f.get('original_RSL_clip_actions')==6.
  binding=f.get('actual_V2_binding') or {};checks['actual_V2_asset_binding']=binding.get('asset_sha256')==expect['asset_SHA'] and binding.get('contract_sha256')==expect['contract_SHA'] and ready.get('actual_V2_binding')==binding
  native=f.get('actual_native_static') or {};rows=native.get('actual_native_mechanical_limits');checks['actual_fresh_N80_native_readback']=isinstance(rows,list) and bool(rows) and all(x.get('actual_all_N80_verified') is True for x in rows) and native.get('no_precontrol') is True and native.get('not_N20000_native_admission_replay') is True and ready.get('actual_native_static')==native
  checks['original_env_close_returned']=pre.get('calling_original_env_close') is True and pre.get('completed_controls')==1000 and envclose.get('original_env_close_returned') is True and intent.get('env_close_returned') is True
  checks['durable_V6_intent_final_binding']=intent.get('final_sha256')==hashlib.sha256(raw).hexdigest() and intent.get('final_bytes')==len(raw) and intent.get('error_before_close') is False and intent.get('original_app_close_arguments')==[] and intent.get('original_fast_shutdown_unchanged') is True and (intent.get('original_bound_close') or {}).get('fast_shutdown') is True and intent.get('expected_process_nonreturn') is True and intent.get('app_close_returned') is None and intent.get('publication')=='TEMP_FLUSH_FSYNC_ATOMIC_RENAME_DIRECTORY_FSYNC_BEFORE_ORIGINAL_APP_CLOSE' and intent.get('epoch',0)>=f.get('last_eval_epoch',float('inf'))
  skill=f.get('skill') or {};checks['missing_E0_grader_remains_null']=skill.get('full_grader','ABSENT') is None and bool(skill.get('predicate_gap')) and f.get('full_skill_graduation','ABSENT') is None and skill.get('full_skill_graduation','ABSENT') is None
  checks['no_registry_or_mother_mutation']=f.get('registry_writes')==0 and f.get('mother_replaced') is False
 except BaseException:detail['original_qualification_error']=traceback.format_exc();checks['all_required_json_and_fields_present']=False
 errors=sorted(p.name for p in out.glob('*ERROR*.json'));checks['own_worker_ERROR_absent']=not errors;detail['own_error_files']=errors
 return dict(kind='E0_SINGLE_FROZEN_ACTUAL_WAIT_EXECUTION_QUALIFICATION_V1',role='E0',qualified=bool(checks) and all(checks.values()),checks=checks,actual_child_wait_returned=True,actual_child_pid=pid,actual_parent_pid=os.getpid(),actual_returncode=rc,qualification_scope='FINITE_EXECUTION_ONLY_NOT_SKILL_GRADUATION',skill_grader=None,full_skill_graduation=None,detail=detail)

def settle_own_card(uuid,waited,admitted):
 rows=[]
 if not waited or not admitted:return False,rows
 until=time.monotonic()+120
 while True:
  try:
   resource=nvidia(uuid);apps=subprocess.check_output(['/usr/bin/nvidia-smi','--query-compute-apps=gpu_uuid,pid','--format=csv,noheader,nounits'],text=True);empty=uuid not in apps;ok=empty and resource['free_MiB']>=23500 and resource['utilization_percent']==0;rows.append(dict(epoch=time.time(),resource=resource,selected_card_compute_empty=empty,settled=ok))
   if ok:return True,rows
  except BaseException:rows.append(dict(epoch=time.time(),original_error=traceback.format_exc(),settled=False))
  if time.monotonic()>=until:return False,rows
  time.sleep(2)
'''

STAGE_SOURCE = r'''"""Once-only E0 frozen eval source/helper stage AFTER actual qualified train close.
No selected model stat/hash/read/decode; no SDK/GPU/C/lock/GO in this stager.
"""
from pathlib import Path, PurePosixPath
import argparse,hashlib,json,math,os,posixpath,sys,time
D=Path(__file__).resolve().parent
T=D.parent/'mod4v1_experts_fulldr_rm70_20261101'
OWN='/home/lc01/Zonglin Li/zonglin2'
FRONTDOOR=__FRONTDOOR_LITERAL__

def need(value,message):
 if not value:raise RuntimeError(message)

def at(value,parts):
 current=value
 for key in parts:
  if not isinstance(current,dict) or key not in current:raise KeyError('Required actual JSON path; parent must verify, never guess: '+json.dumps(parts))
  current=current[key]
 return current

def read_json(path):
 p=Path(path);need(p.suffix.lower()=='.json','JSON metadata only');return json.loads(p.read_bytes())

def put(path,value):
 path=Path(path);tmp=path.with_suffix(path.suffix+'.partial');tmp.write_text(json.dumps(value,indent=2,allow_nan=False),encoding='utf8');os.replace(tmp,path)

def sha(raw):return hashlib.sha256(raw).hexdigest()

def connect():
 sys.path.insert(0,str(T));from project_connector import connect72
 return connect72()

def closed_input(path):
 value=read_json(path)
 if 'path' in value and 'metadata' not in value:
  path=Path(value['path']);value=read_json(path)
 return path,value

def train_gate(closed):
 need(at(closed,FRONTDOOR['closed']) is True and closed['root']==FRONTDOOR['expected_train_root'],'Actual current single-E0 training root must be closed')
 need(set(closed['cases'])=={'E0'} and closed['all_selected_execution_qualified'] is True,'Only actual E0 qualified training case')
 end=at(closed,FRONTDOOR['owner_exit']);outer=at(closed,FRONTDOOR['outer_wait']);cohort=at(closed,FRONTDOOR['cohort_final']);wait=at(closed,FRONTDOOR['child_wait']);final=at(closed,FRONTDOOR['producer_final'])
 need(all(end[k] is True for k in ('all_own_children_waited','original_cost_settled','original_private_finite_authority_leases_released')) and end['errors']==[],'Actual allwait/costsettled/releases, not rc0 alone')
 need(outer['original_owner_reaped'] is True and outer['actual_wait_returncode']==0 and outer['original_owner_pid']==closed['metadata']['OWNER_STARTED.json']['pid'],'Actual outer owner p.wait and identity')
 need(cohort['all_own_children_waited'] is True and cohort['original_cost_settled'] is True and cohort['pending_unstarted_roles']==[] and cohort['errors']==[] and len(cohort['rows'])==1 and [x['role'] for x in cohort['rows'].values()]==['E0'],'Actual singleton cohort completion')
 need(wait['returncode']==0 and wait['terminal_all_own_children_waited'] is True and wait['semantic_qualification']['qualified'] is True and wait['semantic_qualification']['actual_child_wait_returned'] is True,'Actual trained worker wait plus semantic qualification')
 need(final['role']=='E0' and final['run_id']==end['run_id']==cohort['run_id'] and final['execution'] is True and final['passed_execution'] is True and final['completed_requested_update_window'] is True and final['completed_actual_updates']>0 and final['error'] is None and final['close_errors']==[],'Actual complete positive-update E0 producer')
 latest=at(final,FRONTDOOR['latest']);save=at(final,FRONTDOOR['fullsave']);core=at(save,FRONTDOOR['live_core'])
 need(latest==save['latest_complete_save'] and latest['path']==save['checkpoint'] and latest['bytes']==save['bytes'] and latest['sha256']==save['SHA'],'Latest producer complete save metadata exact agreement')
 need(all(save[k] is True for k in ('complete_original_learner','live_V2_D0_D7_task_rng_history_queues','unknown_and_historical_source_CPU_tree_exact','source_unchanged','atomic_published')),'Actual producer fullstate save, not a partial/policy export')
 need(save['actual_new_updates']==final['completed_actual_updates'] and final['learnedstate']['live_core']==core,'Actual final live core agreement')
 path=PurePosixPath(latest['path']);production=PurePosixPath(closed['root'])/'roles/E0/production'
 need(path.is_absolute() and '..' not in path.parts and path.is_relative_to(production) and path.suffix.lower()=='.pt','Own producer candidate PATH STRING only')
 need(type(latest['bytes']) is int and latest['bytes']>0 and isinstance(latest['sha256'],str) and len(latest['sha256'])==64 and all(c in '0123456789abcdef' for c in latest['sha256']),'Actual candidate size/SHA fields must be present')
 iteration=at(core,FRONTDOOR['iteration']);steps=at(core,FRONTDOOR['Adam17_steps']);step=at(core,FRONTDOOR['Adam_step']);lrs=at(core,FRONTDOOR['optimizer_LRs']);lr=at(core,FRONTDOOR['LR'])
 need(type(iteration) is int and iteration>=0 and isinstance(steps,list) and len(steps)==17 and len(set(steps))==1 and type(step) is int and steps[0]==step and step>0,'Actual live core iteration and complete Adam17, never arithmetic labels')
 need(isinstance(lrs,list) and bool(lrs) and all(isinstance(x,(int,float)) and math.isfinite(x) and x>0 for x in lrs) and len(set(lrs))==1 and lrs[0]==lr,'Actual live optimizer LR, not original source LR')
 epoch=max(float(end['epoch']),float(outer['epoch']),float(wait['owner_received_terminal_epoch']))
 receipt=dict(roles=['E0'],all_closed=True,actual_wait_complete=True,resources_released=True,original_cost_settled=True,semantic_qualified=True,closed_epoch=epoch,GPU_settled=False,GPU_settled_pending_fresh_resource_gate=True,training_run_id=final['run_id'],training_root=closed['root'],actual_owner_exit=end,actual_outer_wait=outer,actual_child_semantic_qualification=wait['semantic_qualification'])
 return final,latest,core,receipt

def py_tree(root,prefix):
 # Name/suffix exclusion precedes every per-entry type/stat/read operation.
 banned={'.pt','.pth','.ckpt','.safetensors','.onnx','.bin','.pkl','.pickle','.npz','.npy','.jsonl','.log','.raw','.pyc','.pyo','.partial'}
 skip={'__pycache__','.git','weights','models','checkpoints','raw','rawlogs','logs','production','private','cache'}
 root=Path(root);need(root.is_dir(),'Missing complete Python helper directory: '+str(root));found={};stack=[root]
 while stack:
  current=stack.pop()
  with os.scandir(current) as entries:
   for entry in entries:
    name=entry.name
    if name.lower() in skip or any(x.lower() in banned for x in Path(name).suffixes):continue
    if entry.is_symlink():raise RuntimeError('No helper symlink: '+entry.path)
    if entry.is_dir(follow_symlinks=False):stack.append(Path(entry.path));continue
    if Path(name).suffix.lower()!='.py':continue
    need(entry.is_file(follow_symlinks=False),'Regular Python helper only');p=Path(entry.path);found[prefix+'/'+p.relative_to(root).as_posix()]=p.read_bytes()
 need(bool(found),'Empty Python helper tree');return found

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--closed',type=Path,default=D/FRONTDOOR['closed_pointer']);args=parser.parse_args()
 marker=D/'E0_SINGLE_FROZEN_STAGE_ONCE.json';result=D/'E0_SINGLE_FROZEN_STAGE_RESULT.json';need(not marker.exists() and not result.exists(),'New E0 eval stage once only')
 closed_path,closed=closed_input(args.closed);final,latest,core,receipt=train_gate(closed);train_plan=read_json(D/FRONTDOOR['train_plan']);need(train_plan['root']==closed['root'] and len(train_plan['entries'])==1 and train_plan['entries'][0]['role']=='E0','Exact current singleton train plan')
 old=train_plan['entries'][0];need(latest['path']!=old['source_path'] and latest['sha256']!=old['source_SHA'],'New actual candidate, not original 6cd mother')
 run='E0_SINGLE_FROZEN_'+time.strftime('%Y%m%d_%H%M%S')+'_'+str(time.time_ns());root=OWN+'/tasks/'+run
 payload={'E0_SINGLE_FROZEN_parent.py':(D/'E0_SINGLE_FROZEN_parent.py').read_bytes(),'worker_mod4v2_frozen_eval_e0_single_v3.py':(D/'worker_mod4v2_frozen_eval_e0_single_v3.py').read_bytes()}
 payload.update(py_tree(T/'NINE_N80_PARALLEL_SOURCE_V8','worker_sources/parent'))
 payload.update(py_tree(T/'E1_N80_FRESH_FULLDR_PARALLEL_SKILL_SCREEN_SOURCE_V5_FEEDBACK_DESCRIPTOR','worker_sources/e1'))
 payload.update(py_tree(D.parent/'e3_fudan_recovery_alignment_20261104/source_fudan_frozen_native_eval_v8_resume55','helpers'))
 put(marker,dict(epoch=time.time(),root=root,run_id=run,closed_path=str(closed_path),source_checkpoint_operations=0,SDK_GPU_C_locks_GO=0,no_samepurpose_retry=True))
 client=connect();ftp=client.open_sftp()
 def get_train_json(rel):
  need(rel.endswith('.json') and not PurePosixPath(rel).is_absolute() and '..' not in PurePosixPath(rel).parts,'Own training JSON only')
  with ftp.open(closed['root']+'/'+rel,'rb') as stream:return json.loads(stream.read())
 def mkdirs(path):
  current=''
  for part in path.split('/'):
   if not part:continue
   current+='/'+part
   try:ftp.stat(current)
   except FileNotFoundError:ftp.mkdir(current)
 try:
  # Re-read only immutable own JSON after actual outer wait; never stat candidate.
  remote_final=get_train_json('roles/E0/production/V2_MIGRATION_FINAL.json');need(remote_final==final,'Closed snapshot versus own actual producer final differs')
  for rel,expected in [('OWNER_EXIT_ACTUAL.json',closed['metadata']['OWNER_EXIT_ACTUAL.json']),('OUTER_OWNER_WAIT_ACTUAL.json',closed['metadata']['OUTER_OWNER_WAIT_ACTUAL.json']),('roles/E0/PARENT_WAITED_ACTUAL.json',closed['cases']['E0']['PARENT_WAITED_ACTUAL.json'])]:need(get_train_json(rel)==expected,'Actual closed own JSON differs: '+rel)
  actual_task=get_train_json('roles/E0/TASK.json');train_role=closed['root']+'/roles/E0'
  need(actual_task['role']=='E0' and actual_task['run_id']==final['run_id'] and actual_task['original_runtime_root']==train_role and actual_task['v2_package']==closed['root']+'/v2_package' and actual_task['GPU_UUID']==FRONTDOOR['GPU_UUID'],'Actual training source runtime/package/GPU identity')
  need(actual_task['original_entry']=='runtime/isaac/mod4/train_mod4v1_e0.py','Original family E0 entry unchanged')
  template=dict(role='E0',source_family='e0',original_runtime_root=train_role,original_entry=actual_task['original_entry'],original_run_manifest=actual_task['original_run_manifest'],v2_package=actual_task['v2_package'],migration_worker=closed['root']+'/worker_mod4v2_expert_migration_v4.py',migration_run_id=final['run_id'],checkpoint_path=latest['path'],checkpoint_SHA=latest['sha256'],checkpoint_bytes=latest['bytes'],checkpoint_iteration=core['iteration'],checkpoint_Adam_step=core['source_Adam_step'],checkpoint_LR=core['source_LR'],asset_SHA=final['target_asset_SHA'],contract_SHA=final['target_contract_SHA'],source_path=latest['path'],source_SHA=latest['sha256'],source_bytes=latest['bytes'],source_iteration=core['iteration'],source_Adam17=core['source_Adam_step'],source_Adam_step=core['source_Adam_step'],source_LR=core['source_LR'])
  proof=dict(kind='E0_SINGLE_FROZEN_ACTUAL_TRAIN_CLOSED_GATE_V1',closed_snapshot_local=str(closed_path),producer_final=final,migration_close=receipt,candidate_metadata_from_actual_producer_only=True,model_stat_hash_read_decode_by_stage=0)
  payload['TRAINING_CLOSED_ADMISSION.json']=json.dumps(proof,indent=2,allow_nan=False).encode()
  files=[dict(relative=rel,bytes=len(raw),SHA=sha(raw)) for rel,raw in sorted(payload.items())]
  plan=dict(kind='E0_SINGLE_FROZEN_ORIGINAL_ONE_GPU_PARENT_PLAN_V1',group_id=run,GPU_UUID=FRONTDOOR['GPU_UUID'],roles=[dict(role='E0',worker='worker_mod4v2_frozen_eval_e0_single_v3.py')],worker_files=files,task_template=template,migration_close=receipt,original_supervisor_source='NINE_N80_PARALLEL_SOURCE_V8/single_gpu_group_supervisor.py',canonical_writes=0,new_PPO_BPTT_GO=0,model_operations_before_worker_admission=0)
  payload['GROUP_PLAN.json']=json.dumps(plan,indent=2,allow_nan=False).encode()
  try:ftp.lstat(root)
  except FileNotFoundError:pass
  else:raise FileExistsError(root)
  mkdirs(root)
  for rel,raw in sorted(payload.items()):
   need(PurePosixPath(rel).suffix.lower() in ('.py','.json') and '..' not in PurePosixPath(rel).parts,'Only new-root source/helper/own JSON payload');dest=root+'/'+rel;mkdirs(posixpath.dirname(dest))
   with ftp.open(dest,'wb') as stream:stream.write(raw)
  value=dict(epoch=time.time(),root=root,run_id=run,returncode=0,source_stage_only=True,parent_dispatched=False,closed_training_root=closed['root'],migration_close=receipt,checkpoint_metadata=latest,live_core=core,plan_SHA=sha(payload['GROUP_PLAN.json']),uploaded_nonPT_files=len(payload),selected_PT_stat_hash_read_decode=0,SDK_GPU_C_locks_GO=0)
  put(result,value);print(json.dumps(value,indent=2))
 finally:ftp.close();client.close()

if __name__=='__main__':main()
'''

DISPATCH_SOURCE = r'''"""Dispatch this one new staged E0 eval; outer controller really waits the parent."""
from pathlib import Path
import hashlib,json,shlex,time
from E0_SINGLE_FROZEN_stage import D,OWN,connect,need,put,read_json
CONTROLLER=r"""from pathlib import Path
import json,os,subprocess,time
B=Path(__file__).resolve().parent
assert not(B/'OUTER_OWNER_WAIT_ACTUAL.json').exists()
def put(name,value):
 p=B/name;q=p.with_suffix(p.suffix+'.partial');q.write_text(json.dumps(value,indent=2));os.replace(q,p)
with (B/'OWNER_STDOUT_STDERR.log').open('xb') as log:
 p=subprocess.Popen(['/home/lc01/Zonglin Li/zonglin2/run-python.sh','-u','-B',str(B/'E0_SINGLE_FROZEN_parent.py')],cwd=B,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
 put('OUTER_OWNER_IDENTITY.json',dict(epoch=time.time(),controller_pid=os.getpid(),original_owner_pid=p.pid))
 rc=p.wait()
 put('OUTER_OWNER_WAIT_ACTUAL.json',dict(epoch=time.time(),controller_pid=os.getpid(),original_owner_pid=p.pid,actual_wait_returncode=rc,original_owner_reaped=True))
"""

def main():
 marker=D/'E0_SINGLE_FROZEN_DISPATCH_ONCE.json';result=D/'E0_SINGLE_FROZEN_DISPATCH_RESULT.json';need(not marker.exists() and not result.exists(),'This eval purpose dispatch once only');stage=read_json(D/'E0_SINGLE_FROZEN_STAGE_RESULT.json');need(stage['returncode']==0 and stage['source_stage_only'] is True and stage['parent_dispatched'] is False and stage['selected_PT_stat_hash_read_decode']==0,'Only actual new source stage')
 root=stage['root'];need(root.startswith(OWN+'/tasks/E0_SINGLE_FROZEN_'),'New E0 eval root only');put(marker,dict(epoch=time.time(),root=root,one_parent_submission=True,no_resource_lock_budget_or_GO_in_dispatcher=True))
 launch="""from pathlib import Path
import hashlib,json,os,subprocess
B=Path(__ROOT__)
assert hashlib.sha256((B/'GROUP_PLAN.json').read_bytes()).hexdigest()==__PLAN_SHA__
assert not(B/'PARENT_STARTED.json').exists() and not(B/'OUTER_OWNER_IDENTITY.json').exists()
with (B/'OUTER_CONTROLLER_STDOUT_STDERR.log').open('xb') as log:
 p=subprocess.Popen(['/home/lc01/Zonglin Li/zonglin2/run-python.sh','-u','-B',str(B/'E0_SINGLE_FROZEN_OUTER_WAIT_CONTROLLER.py')],cwd=B,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
 print(json.dumps(dict(controller_pid=p.pid,root=str(B),actual_parent_wait_pending=True,SDK_PT_or_GO_not_observed_by_dispatcher=True)))
""".replace('__ROOT__',repr(root)).replace('__PLAN_SHA__',repr(stage['plan_SHA']))
 client=connect();ftp=client.open_sftp()
 try:
  name=root+'/E0_SINGLE_FROZEN_OUTER_WAIT_CONTROLLER.py'
  try:ftp.lstat(name)
  except FileNotFoundError:pass
  else:raise FileExistsError(name)
  with ftp.open(name,'wb') as stream:stream.write(CONTROLLER.encode())
  stdin,stdout,stderr=client.exec_command(shlex.quote(OWN+'/run-python.sh')+' -B -c '+shlex.quote(launch),timeout=30);stdin.close();out=stdout.read().decode();err=stderr.read().decode();rc=stdout.channel.recv_exit_status();value=dict(epoch=time.time(),root=root,returncode=rc,stdout=out,stderr=err,outer_actual_parent_wait_still_required=True);put(result,value);print(json.dumps(value,indent=2));need(rc==0,'Original dispatcher error retained; no automatic retry')
 finally:ftp.close();client.close()

if __name__=='__main__':main()
'''

COLLECT_SOURCE = r'''"""Once <=4500s /15s own-JSON collector. No model/raw/log/C/GPU-state reads."""
from pathlib import PurePosixPath
import argparse,json,math,time
from E0_SINGLE_FROZEN_stage import D,OWN,connect,need,put,read_json
ROOT_NAMES=['PARENT_STARTED.json','BOUNDED_ORIGINAL_RESOURCE_WAIT.json','ACTUAL_GROUP_ADMISSION.json','CHILDREN.json','GROUP_BARRIER_STATUS.json','GROUP_EVAL_START.json','GROUP_ABORT.json','GROUP_STARTUP_ABORT.json','PARENT_ORIGINAL_ERROR.json','TERMINAL_ROWS.json','E0_SINGLE_FROZEN_PARENT_FINAL.json','PARENT_EXIT_SCOPE.json','OUTER_OWNER_IDENTITY.json','OUTER_OWNER_WAIT_ACTUAL.json']
CASE_NAMES=['task.json','WORKER_SCENE_READY.json','WORKER_EVAL_STARTED.json','V2_FROZEN_EVAL_FINAL.json','PRE_CLOSE.json','ENV_CLOSE_RETURNED.json','V2_FROZEN_EVAL_APP_CLOSE_INTENT.json','APP_CLOSED.json']

def normal_metrics(final):
 if not isinstance(final,dict):return None
 skill=final.get('skill') or {};integral=skill.get('body_velocity_absolute_error_time_integral_per_env');n=final.get('num_envs');seconds=final.get('seconds');mae=None
 if n==80 and isinstance(seconds,(int,float)) and seconds>0 and isinstance(integral,list) and len(integral)==80 and all(isinstance(row,list) and len(row)==3 and all(isinstance(v,(int,float)) and math.isfinite(v) for v in row) for row in integral):mae=dict(zip(('body_vx_m_s','body_vy_m_s','yaw_rate_rad_s'),[sum(row[i] for row in integral)/(n*seconds) for i in range(3)]))
 return dict(controls=final.get('controls'),seconds=seconds,physics_callbacks=final.get('physics_callbacks'),feedback_samples=final.get('feedback_samples'),termination_events_by_reason=final.get('termination_events_by_reason'),unique_envs_terminated=final.get('unique_envs_terminated'),unique_envs_truncated=final.get('unique_envs_truncated'),episode_end_events=final.get('episode_end_events'),body_velocity_MAE=mae,max_current_closure_m=final.get('max_current_closure_m'),max_current_mimic_rad=final.get('max_current_mimic_rad'),max_raw_action_abs=final.get('max_raw_action_abs'),max_applied_action_abs=final.get('max_applied_action_abs'),skill_grader=skill.get('full_grader'),predicate_gap=skill.get('predicate_gap'),full_skill_graduation=final.get('full_skill_graduation'),execution_not_skill_graduation=True)

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--seconds',type=int,default=4500);args=parser.parse_args();need(1<=args.seconds<=4500,'Own JSON observation bound at most4500s')
 marker=D/'E0_SINGLE_FROZEN_COLLECT_ONCE.json';need(not marker.exists(),'One own metadata observation only');stage=read_json(D/'E0_SINGLE_FROZEN_STAGE_RESULT.json');dispatch=read_json(D/'E0_SINGLE_FROZEN_DISPATCH_RESULT.json');need(stage['returncode']==dispatch['returncode']==0 and stage['root']==dispatch['root'],'Same actually dispatched own purpose');root=stage['root'];need(root.startswith(OWN+'/tasks/E0_SINGLE_FROZEN_'),'Only new E0 eval root')
 out=D/'reports'/stage['run_id'];out.mkdir(parents=True,exist_ok=False);put(marker,dict(epoch=time.time(),root=root,output=str(out),bound_seconds=args.seconds,interval_seconds=15,only_own_JSON=True,model_raw_log_C_GPU_reads=0));until=time.monotonic()+args.seconds;client=connect();ftp=client.open_sftp();cache={};last=None;closed=False
 def get(relative):
  rel=PurePosixPath(relative);need(not rel.is_absolute() and '..' not in rel.parts and rel.suffix=='.json','Own purpose JSON only');path=root+'/'+relative;remaining=until-time.monotonic()
  if remaining<=0:raise TimeoutError('Own JSON observation deadline reached')
  ftp.get_channel().settimeout(min(15.,remaining))
  try:
   st=ftp.stat(path);signature=(st.st_mtime,st.st_size)
   if path in cache and cache[path][0]==signature:return cache[path][1]
   with ftp.open(path,'rb') as stream:value=json.loads(stream.read())
   cache[path]=(signature,value);return value
  except FileNotFoundError:return None
 try:
  while time.monotonic()<until:
   meta={name:get(name) for name in ROOT_NAMES};case={name:get('cases/E0/'+name) for name in CASE_NAMES}
   try:names=ftp.listdir(root+'/cases/E0')
   except FileNotFoundError:names=[]
   case['ERROR_JSON']={name:get('cases/E0/'+name) for name in names if name.endswith('.json') and 'ERROR' in name}
   final=case['V2_FROZEN_EVAL_FINAL.json'];rows=meta['TERMINAL_ROWS.json'] or [];exit_scope=meta['PARENT_EXIT_SCOPE.json'] or {};outer=meta['OUTER_OWNER_WAIT_ACTUAL.json'];parent_final=meta['E0_SINGLE_FROZEN_PARENT_FINAL.json'] or {};identity=meta['PARENT_STARTED.json'] or {}
   qualified=bool(outer and outer.get('original_owner_reaped') is True and outer.get('actual_wait_returncode')==0 and outer.get('original_owner_pid')==identity.get('pid') and exit_scope.get('all_own_children_waited') is True and exit_scope.get('original_single_GPU_private_EX_released') is True and exit_scope.get('original_global_finite_EX_released') is True and exit_scope.get('GPU_settled') is True and exit_scope.get('errors')==[] and parent_final.get('all_E0_actual_execution_complete') is True and len(rows)==1 and rows[0].get('role')=='E0' and rows[0].get('returncode')==0 and rows[0].get('actual_waited') is True and rows[0].get('passed_execution') is True and (rows[0].get('semantic_qualification') or {}).get('qualified') is True and not case['ERROR_JSON'] and meta['PARENT_ORIGINAL_ERROR.json'] is None)
   value=dict(epoch=time.time(),root=root,metadata=meta,cases={'E0':case},execution_qualified=qualified,skill_grader=None,full_skill_graduation=None,normal_metrics=normal_metrics(final),only_own_JSON_read=True,models_raw_logs_C_GPU_reads=0,qualification_scope='ACTUAL_WAIT_FINAL_INTENT_ERROR_AND_RESOURCE_CLOSE_CONJUNCTION_NOT_RC0_ALONE')
   put(out/'LATEST_METADATA.json',value);token=json.dumps(dict(ready=case['WORKER_SCENE_READY.json'] is not None,started=case['WORKER_EVAL_STARTED.json'] is not None,final=final is not None,exit=bool(exit_scope),outer=outer,qualified=qualified,errors=list(case['ERROR_JSON'])),sort_keys=True)
   if token!=last:print(token,flush=True);last=token
   if outer is not None and (meta['PARENT_EXIT_SCOPE.json'] is not None or outer['actual_wait_returncode']!=0):
    value['closed']=True;value['all_selected_execution_qualified']=qualified;value['skill_graduation_not_claimed']=True;put(out/'CLOSED_RESULT.json',value);put(D/'E0_SINGLE_FROZEN_CLOSED_RESULT_PATH.json',dict(path=str(out/'CLOSED_RESULT.json'),root=root));print(json.dumps(dict(closed_result=str(out/'CLOSED_RESULT.json'),execution_qualified=qualified,skill_grader=None,full_skill_graduation=None,normal_metrics=value['normal_metrics'])),flush=True);closed=True;break
   time.sleep(min(15,max(0,until-time.monotonic())))
  if not closed:raise TimeoutError('Own E0 eval metadata observation bound; no extension, retry or foreign action')
 finally:ftp.close();client.close()

if __name__=='__main__':main()
'''


def replace_once(text, old, new):
    if text.count(old) != 1:
        raise RuntimeError('Original supervisor source anchor changed; parent must review: ' + old)
    return text.replace(old, new)


def parent_source():
    original = (T / 'NINE_N80_PARALLEL_SOURCE_V8/single_gpu_group_supervisor.py').read_text(encoding='utf-8-sig')
    if len(original.splitlines()) != 79:
        raise RuntimeError('Expected original complete 79-line supervisor; no silent partial rewrite')
    text = replace_once(original, 'from worker_sources.parent.task_contract import make_task', 'import math')
    text = replace_once(text, 'def main():', PARENT_ADDITIONS + '\ndef main():')
    text = replace_once(text, 'assert len(roles)==9 and len({r[\'role\']for r in roles})==9', "assert len(roles)==1 and [r['role']for r in roles]==['E0'] and plan['migration_close']['roles']==['E0']")
    text = text.replace('ONEGPU_NINE_FRESH80_SKILL_EVAL_NO_LEARNING', 'ONEGPU_SINGLE_E0_FRESH80_FINITE_EVAL_NO_LEARNING')
    text = replace_once(text, 'assert len(children)==9', 'assert len(children)==1')
    text = replace_once(text, 'if len(ready)==9:', 'if ready==[\'E0\']:')
    text = replace_once(text, 'All9SDKscenes+liveactors+N80fullDRreadybeforeanycontrolledstep', 'SingleE0SDKscene+liveactor+N80fullDRreadybeforeanycontrolledstep')
    text = replace_once(text, 'NineSDKstartupreadybarrier900s expired', 'SingleE0SDKstartupreadybarrier900s expired')
    old_row = "rc=p.wait();data=json.loads((out/'FINAL.json').read_bytes())if(out/'FINAL.json').exists()else None;err=json.loads((out/'WORKER_ERROR.json').read_bytes())if(out/'WORKER_ERROR.json').exists()else None;terminal.append(dict(role=r['role'],pid=p.pid,GPU_UUID=uuid,returncode=rc,actual_waited=True,ready=(out/'WORKER_SCENE_READY.json').exists(),started=(out/'WORKER_EVAL_STARTED.json').exists(),pre_close=(out/'PRE_CLOSE.json').exists(),passed_execution=bool(rc==0 and data and data.get('passed_execution')and err is None and(out/'PRE_CLOSE.json').exists()),data=data,error=err));put('TERMINAL_ROWS.json',terminal)"
    new_row = "rc=p.wait();data=json.loads((out/'V2_FROZEN_EVAL_FINAL.json').read_bytes())if(out/'V2_FROZEN_EVAL_FINAL.json').exists()else None;q=qualify_waited_e0(out,p.pid,rc,plan);err={ep.name:json.loads(ep.read_bytes())for ep in out.glob('*ERROR*.json')};terminal.append(dict(role=r['role'],pid=p.pid,GPU_UUID=uuid,returncode=rc,actual_waited=True,ready=(out/'WORKER_SCENE_READY.json').exists(),started=(out/'WORKER_EVAL_STARTED.json').exists(),pre_close=(out/'PRE_CLOSE.json').exists(),passed_execution=q['qualified'],semantic_qualification=q,data=data,error=err));put('TERMINAL_ROWS.json',terminal)"
    text = replace_once(text, old_row, new_row)
    text = replace_once(text, "put('FINAL.json',dict(kind='ACTUAL_SINGLE_GPU_NINE_FRESH80_PARALLEL_SKILL_SCREEN'", "put('E0_SINGLE_FROZEN_PARENT_FINAL.json',dict(kind='ACTUAL_SINGLE_GPU_E0_FRESH80_FROZEN_FINITE_EVAL'")
    text = replace_once(text, 'nine_ready_before_start=True,all_nine_actual_execution_complete=', 'single_E0_ready_before_start=True,skill_grader=None,full_skill_graduation=None,all_E0_actual_execution_complete=')
    # Preserve own-PID cleanup and actual p.wait; observe settling while EXs still held.
    text = replace_once(text, '   if waited:\n    for fd in reversed(locks):', "   settled,settle_rows=settle_own_card(uuid,waited,(B/'ACTUAL_GROUP_ADMISSION.json').exists())\n   if waited:\n    for fd in reversed(locks):")
    text = replace_once(text, 'original_global_finite_EX_released=waited,errors=errors,', 'original_global_finite_EX_released=waited,GPU_settled=settled,GPU_settle_rows=settle_rows,errors=errors,')
    text = replace_once(text, '"""OneoriginalGPUprivateEX+globalfiniteEXowner, nineisolatedSDKworkers, honestreadybarrier/result/closewait. No learner/GO/ledgerwrite."""', '"""Original complete supervisor specialized to one E0 worker; actual waits, durable intent qualification and original resource gates. No learner/GO/ledgerwrite."""')
    return text


def eval_worker_source():
    # Bytes are retained exactly except the ONE explicit migration basename.
    # No AST rewrite, import, execution, env/clock patch or learner change here.
    raw = (D / 'worker_mod4v2_frozen_eval_e0_single_v2.py').read_bytes()
    if hashlib.sha256(raw).hexdigest() != 'a36ee03113fb535123a60919115c151a18f35d2ab0a5ff5d09134c1687ed6280':
        raise RuntimeError('Original delivered eval worker v2 differs; leave it unchanged for parent review')
    old = b'worker_mod4v2_expert_migration_v3.py'
    new = b'worker_mod4v2_expert_migration_v4.py'
    if raw.count(old) != 1 or new in raw:
        raise RuntimeError('Expected sole explicit migration_worker v3 basename')
    changed = raw.replace(old, new, 1)
    if changed.replace(new, old, 1) != raw:
        raise RuntimeError('Only the explicit migration basename may change')
    return changed.decode('utf-8')


def main():
    outputs = {
        'worker_mod4v2_frozen_eval_e0_single_v3.py': eval_worker_source(),
        'E0_SINGLE_FROZEN_parent.py': parent_source(),
        'E0_SINGLE_FROZEN_stage.py': STAGE_SOURCE.replace('__FRONTDOOR_LITERAL__', repr(FRONTDOOR)),
        'E0_SINGLE_FROZEN_dispatch_once.py': DISPATCH_SOURCE,
        'E0_SINGLE_FROZEN_collect_once.py': COLLECT_SOURCE,
    }
    for name in outputs:
        if (D / name).exists():
            raise FileExistsError('New pipeline sources only; leave existing source unchanged: ' + str(D / name))
    for name, source in outputs.items():
        with (D / name).open('x', encoding='utf-8', newline='\n') as stream:
            stream.write(source)
    print(json.dumps(dict(generated_sources=list(outputs),generated_source_executions=0,SSH_SDK_PT_GPU_Git=0,entrypoints=['python E0_SINGLE_FROZEN_stage.py --closed E0_SINGLE_ADMISSION2_CLOSED_RESULT_PATH.json','python E0_SINGLE_FROZEN_dispatch_once.py','python E0_SINGLE_FROZEN_collect_once.py --seconds 4500'],frontdoor_actual_producer_JSON_paths=FRONTDOOR),indent=2))


if __name__ == '__main__':
    main()
