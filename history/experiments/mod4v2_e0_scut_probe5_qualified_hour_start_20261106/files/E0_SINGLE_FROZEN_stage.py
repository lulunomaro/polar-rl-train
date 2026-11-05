"""Once-only E0 frozen eval source/helper stage AFTER actual qualified train close.
No selected model stat/hash/read/decode; no SDK/GPU/C/lock/GO in this stager.
"""
from pathlib import Path, PurePosixPath
import argparse,hashlib,json,math,os,posixpath,sys,time
D=Path(__file__).resolve().parent
T=D.parent/'mod4v1_experts_fulldr_rm70_20261101'
OWN='/home/lc01/Zonglin Li/zonglin2'
FRONTDOOR={'closed_pointer': 'E0_SINGLE_ADMISSION3_CLOSED_RESULT_PATH.json', 'train_plan': 'SOURCE_PLAN_E0_SINGLE_ADMISSION3_ACTUAL_V1.json', 'expected_train_root': '/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V2_E0_SINGLE_ADMISSION3_FULL_LEARNER_MIGRATION_20261106_001831_1793895511281001300', 'GPU_UUID': 'GPU-16828f91-2b45-b646-8dc0-9481138e2842', 'closed': ['closed'], 'owner_exit': ['metadata', 'OWNER_EXIT_ACTUAL.json'], 'outer_wait': ['metadata', 'OUTER_OWNER_WAIT_ACTUAL.json'], 'cohort_final': ['metadata', 'COHORT_FINAL.json'], 'child_wait': ['cases', 'E0', 'PARENT_WAITED_ACTUAL.json'], 'producer_final': ['cases', 'E0', 'V2_MIGRATION_FINAL.json'], 'latest': ['latest_complete_save'], 'fullsave': ['fullsave'], 'live_core': ['live_core'], 'iteration': ['iteration'], 'Adam17_steps': ['Adam17_steps'], 'Adam_step': ['source_Adam_step'], 'optimizer_LRs': ['optimizer_LRs'], 'LR': ['source_LR']}

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
