"""Once-only E0 frozen eval source/helper stage AFTER actual qualified train close.
No selected model stat/hash/read/decode; no SDK/GPU/C/lock/GO in this stager.
"""
from pathlib import Path, PurePosixPath
import argparse,ast,hashlib,json,math,os,posixpath,sys,time
D=Path(__file__).resolve().parent
T=D.parent/'mod4v1_experts_fulldr_rm70_20261101'
OWN='/home/lc01/Zonglin Li/zonglin2'
SCUT_MODE='SCUT_V14_ORIGINAL_FINITE_WALL_CLOCK_HOUR'
SCUT_TASK='Robotics-Wheelbipe-V14-Flat-v0'
FORMAL_SOURCE_SHA='6cdac1e4b84df407d41a38444b87eaa91309ed898af05fe95a6c80f6ac3fd693'
EXPECTED_ASSET_SHA='7361b6930a7270e65f3b290cfa71c50f8e1f0beccaa9cab1fa8a994f03cb35b8'
EXPECTED_CONTRACT_SHA='f01ffcf0f967e1c1f8dc153c9e06d73a70ab3f78e17e8b479159c14a6cf63047'
SCUT_ADAPTER_SHA={'scut_v14_flat_reward_adapter_v4': 'ddb3f77f19a29c0bc047082aef774aa62b585801d539b670f69c434041828570', 'scut_v14_flat_command_termination_adapter_v1': '3f4c93437a7128677701d58c7012ab13a91d78bec727e1f0b1182f12316a1cd8'}
EXPECTED_HOUR_WORKER_SHA='4b200f1276ecec7bda4112e131212f1c8061f21a6f7c0123ecd4fec588d0a8e8'
FRONTDOOR={'closed_pointer': 'E0_SCUT_HOUR_CLOSED_RESULT_PATH.json', 'train_plan': 'SOURCE_PLAN_E0_SCUT_HOUR_ACTUAL_V1.json', 'expected_train_root': '/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V2_E0_SCUT_HOUR_FULL_LEARNER_MIGRATION_20261106_062902_1793917742719982000', 'GPU_UUID': 'GPU-16828f91-2b45-b646-8dc0-9481138e2842', 'closed': ['closed'], 'owner_exit': ['metadata', 'OWNER_EXIT_ACTUAL.json'], 'outer_wait': ['metadata', 'OUTER_OWNER_WAIT_ACTUAL.json'], 'cohort_final': ['metadata', 'COHORT_FINAL.json'], 'child_wait': ['cases', 'E0', 'PARENT_WAITED_ACTUAL.json'], 'producer_final': ['cases', 'E0', 'V2_MIGRATION_FINAL.json'], 'latest': ['latest_complete_save'], 'fullsave': ['fullsave'], 'live_core': ['live_core'], 'iteration': ['iteration'], 'Adam17_steps': ['Adam17_steps'], 'Adam_step': ['source_Adam_step'], 'optimizer_LRs': ['optimizer_LRs'], 'LR': ['source_LR']}

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
 need(closed['cases']['E0']['ERROR_JSON']=={} and closed['metadata']['OWNER_ORIGINAL_ERROR.json'] is None,'Unknown: own training ERROR must be absent')
 need(wait['semantic_qualification']['errors']==[] and bool(wait['semantic_qualification']['checks']) and all(v is True for v in wait['semantic_qualification']['checks'].values()),'Every actual waited semantic check must pass')
 need(final['worker_pid']==wait['semantic_qualification']['actual_child_pid'] and final['parent_pid']==wait['semantic_qualification']['actual_parent_pid']==closed['metadata']['OWNER_STARTED.json']['pid'],'Actual SCUT training child/parent identity')
 need(final['window_mode']==save['window_mode']==SCUT_MODE and final['requested_update_quota'] is None and final['hour_not_started'] is False and final['stop_reason'] in ('STOP_SAVE','save_deadline'),'Actual SCUT finite wall-clock hour FINAL, not prior probe/non-SCUT/U000')
 need(final['source_env_state_applied'] is False and final['source_once1'] is True and final['actual_original_runner_learn_calls']==1 and final['learnedstate']['complete_original_actor_critic_STD6_Adam17_LR_normalizer'] is True,'Complete actual SCUT learner/source-once/fresh physical boundary')
 need(final['target_asset_SHA']==EXPECTED_ASSET_SHA and final['target_contract_SHA']==EXPECTED_CONTRACT_SHA,'Exact D6 producer asset/contract')
 need(all(final['source_IO'][k]==1 for k in ('physical_byte_opens','SHA_calculations','CPU_decodes')),'Actual once-only source byte/hash/CPU decode')
 need(save['actual_optimizer_steps']==final['actual_optimizer_steps'] and save['actual_rollout_controls']==final['actual_rollout_controls'],'Same FINAL/save actual counters only; no arithmetic labels')
 need(all(save[k] is True for k in ('own_roundtrip_full_tree_exact','command_done_and_reward_history_saved','actual_cfg_and_source_SHA_saved')),'Complete original SCUT state/config/source full-save evidence')
 initial=closed['cases']['E0']['SCUT_INITIAL_CHECKPOINT_ACCEPTANCE.json']
 exact7=('actor_exact','critic_exact','normalization_exact','learned_STD_exact','Adam17_exact','LR_exact','iteration_exact')
 need(initial==final['initial_checkpoint_acceptance'] and initial['schema']=='mod4v2.e0.scut_initial_checkpoint_acceptance.v1' and initial['role']=='E0' and initial['run_id']==final['run_id'] and initial['worker_pid']==final['worker_pid'] and initial['task_sha256']==final['task_sha256'],'Standalone and FINAL U000 receipt exact identity')
 need(initial['mode']==SCUT_MODE and initial['accepted'] is True and initial['passed'] is True and all(initial[k] is True for k in exact7) and initial['source_SHA']==FORMAL_SOURCE_SHA,'Actual formal6cd U000 exact7 acceptance')
 need(initial['source_core']==initial['saved_core']==save['source_core']==final['learnedstate']['source_core'],'U000 complete source/saved core exact, separate from current live_core')
 need(initial['source_once1'] is True and initial['source_immutable_CPU_tree_exact'] is True and initial['own_full_save_roundtrip_exact'] is True and initial['statistics_invented'] is False and initial['source_environment_state_applied'] is False,'Actual complete immutable initial checkpoint, no invented state')
 need(initial['actual_PPO_updates']==initial['actual_Adam_steps']==initial['actual_PPO_rollout_controls']==0 and initial['native_zero_controls_not_PPO']==1,'U000 accepted before all PPO, separate native admission only')
 need(initial['actual_save']==initial['latest_complete_save'] and initial['checkpoint']==initial['actual_save']['path'] and initial['bytes']==initial['actual_save']['bytes'] and initial['SHA']==initial['actual_save']['sha256'],'Exact U000 complete save metadata')
 need(latest['path']!=initial['checkpoint'] and latest['sha256']!=initial['SHA'],'FINAL latest candidate must not be first V2_COMPLETE_SAVE/U000')
 need(final['recipe_binding']['mode']==SCUT_MODE and final['recipe_binding']['task']==SCUT_TASK,'Actual SCUT recipe, not renamed old E0 evaluation')
 epoch=max(float(end['epoch']),float(outer['epoch']),float(wait['owner_received_terminal_epoch']))
 receipt=dict(roles=['E0'],all_closed=True,actual_wait_complete=True,resources_released=True,original_cost_settled=True,semantic_qualified=True,closed_epoch=epoch,GPU_settled=False,GPU_settled_pending_fresh_resource_gate=True,training_run_id=final['run_id'],training_root=closed['root'],actual_owner_exit=end,actual_outer_wait=outer,actual_child_semantic_qualification=wait['semantic_qualification'],training_window_mode=SCUT_MODE,U000_exact7=True,formal_source_SHA=FORMAL_SOURCE_SHA)
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
 marker=D/'SCUT_E0_HOUR_FROZEN_STAGE_ONCE.json';result=D/'SCUT_E0_HOUR_FROZEN_STAGE_RESULT.json';need(not marker.exists() and not result.exists(),'New E0 eval stage once only')
 need(args.closed.resolve()==(D/FRONTDOOR['closed_pointer']).resolve(),'Unknown: exact E0_SCUT_HOUR_CLOSED_RESULT_PATH.json frontdoor required')
 closed_path,closed=closed_input(args.closed);final,latest,core,receipt=train_gate(closed);train_plan=read_json(D/FRONTDOOR['train_plan']);need(train_plan['root']==closed['root'] and len(train_plan['entries'])==1 and train_plan['entries'][0]['role']=='E0','Exact current singleton train plan')
 old=train_plan['entries'][0];need(latest['path']!=old['source_path'] and latest['sha256']!=old['source_SHA'],'New actual candidate, not original 6cd mother')
 need(old['worker_argv'][0]==closed['root']+'/worker_e0_scut_v14_hour_v3.py' and old['source_SHA']==FORMAL_SOURCE_SHA,'Exact current SCUT hour plan worker/formal source')
 need(sha((D/'worker_e0_scut_v14_hour_v3.py').read_bytes())==EXPECTED_HOUR_WORKER_SHA,'Unknown: current local hour worker source changed since preparation')
 run='SCUT_E0_HOUR_FROZEN_'+time.strftime('%Y%m%d_%H%M%S')+'_'+str(time.time_ns());root=OWN+'/tasks/'+run
 payload={
  'SCUT_E0_HOUR_FROZEN_factory.py':(D/'SCUT_E0_HOUR_FROZEN_factory.py').read_bytes(),
  'SCUT_E0_HOUR_FROZEN_parent.py':(D/'SCUT_E0_HOUR_FROZEN_parent.py').read_bytes(),'SCUT_E0_HOUR_FROZEN_worker.py':(D/'SCUT_E0_HOUR_FROZEN_worker.py').read_bytes()}
 payload.update(py_tree(T/'NINE_N80_PARALLEL_SOURCE_V8','worker_sources/parent'))
 payload.update(py_tree(T/'E1_N80_FRESH_FULLDR_PARALLEL_SKILL_SCREEN_SOURCE_V5_FEEDBACK_DESCRIPTOR','worker_sources/e1'))
 payload.update(py_tree(D.parent/'e3_fudan_recovery_alignment_20261104/source_fudan_frozen_native_eval_v8_resume55','helpers'))
 for rel in ('SCUT_E0_HOUR_FROZEN_parent.py', 'SCUT_E0_HOUR_FROZEN_worker.py', 'SCUT_E0_HOUR_FROZEN_factory.py'):
  raw_source=payload[rel];ast.parse(raw_source,filename=rel);compile(raw_source,rel,'exec')
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
  need(actual_task['window_mode']==SCUT_MODE and actual_task['source_SHA']==FORMAL_SOURCE_SHA and actual_task['num_envs']==20000 and actual_task['seed']==20260928,'Actual SCUT training TASK, not frozen eval or a probe')
  need(get_train_json('roles/E0/production/SCUT_INITIAL_CHECKPOINT_ACCEPTANCE.json')==final['initial_checkpoint_acceptance'],'Own remote U000 receipt differs from actual CLOSED snapshot')
  template=dict(role='E0',source_family='e0',original_runtime_root=train_role,original_entry=actual_task['original_entry'],original_run_manifest=actual_task['original_run_manifest'],v2_package=actual_task['v2_package'],migration_worker=closed['root']+'/worker_e0_scut_v14_hour_v3.py',migration_worker_SHA=EXPECTED_HOUR_WORKER_SHA,training_window_mode=SCUT_MODE,formal_source_SHA=FORMAL_SOURCE_SHA,SCUT_adapter_SHA=SCUT_ADAPTER_SHA,candidate_live_core=core,candidate_actual_updates=final['completed_actual_updates'],candidate_actual_optimizer_steps=final['actual_optimizer_steps'],candidate_actual_rollout_controls=final['actual_rollout_controls'],initial_checkpoint_acceptance=final['initial_checkpoint_acceptance'],migration_run_id=final['run_id'],checkpoint_path=latest['path'],checkpoint_SHA=latest['sha256'],checkpoint_bytes=latest['bytes'],checkpoint_iteration=core['iteration'],checkpoint_Adam_step=core['source_Adam_step'],checkpoint_LR=core['source_LR'],asset_SHA=final['target_asset_SHA'],contract_SHA=final['target_contract_SHA'],source_path=latest['path'],source_SHA=latest['sha256'],source_bytes=latest['bytes'],source_iteration=core['iteration'],source_Adam17=core['source_Adam_step'],source_Adam_step=core['source_Adam_step'],source_LR=core['source_LR'])
  proof=dict(kind='SCUT_E0_HOUR_FROZEN_ACTUAL_TRAIN_CLOSED_GATE_V1',closed_snapshot_local=str(closed_path),producer_final=final,migration_close=receipt,candidate_metadata_from_actual_producer_only=True,model_stat_hash_read_decode_by_stage=0)
  payload['TRAINING_CLOSED_ADMISSION.json']=json.dumps(proof,indent=2,allow_nan=False).encode()
  files=[dict(relative=rel,bytes=len(raw),SHA=sha(raw)) for rel,raw in sorted(payload.items())]
  plan=dict(kind='SCUT_E0_HOUR_FROZEN_ORIGINAL_ONE_GPU_PARENT_PLAN_V1',group_id=run,GPU_UUID=FRONTDOOR['GPU_UUID'],roles=[dict(role='E0',worker='SCUT_E0_HOUR_FROZEN_worker.py')],worker_files=files,task_template=template,migration_close=receipt,original_supervisor_source='NINE_N80_PARALLEL_SOURCE_V8/single_gpu_group_supervisor.py',canonical_writes=0,new_PPO_BPTT_GO=0,model_operations_before_worker_admission=0)
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
