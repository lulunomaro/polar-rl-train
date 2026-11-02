"""Purestdlib contract validation. No canonicalread/write,SDK ormodeloperations.
ParentROOTadmission+GO mustexistbefore even originalsource PT cache opens.
"""
from pathlib import Path
import hashlib,json,os,time
KIND='MOD4V1_E1_ORIGINAL_PPO_FULL20K_POSTTRAIN_FINITE_V1'
ADMISSION_KIND='ROOT_MOD4V1_EIGHT_POSTTRAIN_ACTUAL_ADMISSION_V1'
GENERATION='MOD4_SINGLE_WRITER72_20261026'
USD='2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3'
CONTRACT='bae3203a7c30f75e29c20c0b0d0e215af5edfc7dbeacb9ebc5310f7867c98755'
ROLES=('CURB_PROTECTED878','CURB_INDEPENDENT113','SLOPE135','SLOPE_INDEPENDENT50')
# AllworkerrequiredfieldscheckedbeforeSDK/PT; metadatacannotpassthenlateKeyErrorseed.
REQUIRED_TASK_KEYS=('kind','canonical','role_key','run_id','GPU_UUID','num_envs','steps_per_env','additional_updates','save_interval','seed','source_SHA','source_bytes','source_iteration','source_LR','original_source_SHA','selected_typed_source_path','model_path','source_saved_envs','policy_hz','feedback_hz','physics_dt','TGS','closure_episode_m','mimic_rad','gas_nominal_N','gas_stiffness_N_m','gas_damping_Ns_m','asset_USD_SHA','asset_contract_SHA','asset_dir','training_capacity_scope','apply_saved20k_history','state_slicing_or_projection','retype_checkpoint','live_full_actor_critic_optimizer_restore','original_PPO_init_at_random_ep_len','canonical_path','original_canonical_generation','owner_parent_pid','inherited_lock_fds','root_admission_file','root_admission_SHA','go_file','rescue_stop_file','source_read_purpose','max_parent_seconds','exit_headroom_seconds')

def require_source_admission(task,admission,go,*,now=None,environ=None,fd_check=None):
 now=time.time() if now is None else now;environ=os.environ if environ is None else environ
 assert not [k for k in REQUIRED_TASK_KEYS if k not in task or task[k] is None], 'MissingrequiredTaskmetadatafieldsbeforeSDK/PT'
 assert type(task['seed']) is int and task['seed']>=0 and type(task['source_bytes']) is int and task['source_bytes']>0
 assert 'source_Adam_step' in task or 'source_Adam17' in task
 assert task['kind']==KIND and task['canonical'] in ROLES and task['canonical']!='H1_normal'
 assert task['num_envs']==20000 and task['steps_per_env']==24 and 1<=task['additional_updates']<=20
 assert 1<=task['save_interval']<=task['additional_updates']
 assert task['policy_hz']==50 and task['feedback_hz']==100 and task['physics_dt']==.0025 and task['TGS']==[32,4]
 assert task['closure_episode_m']==.01 and task['mimic_rad']==.01 and task['gas_nominal_N']==400 and task['gas_stiffness_N_m']==2000 and task['gas_damping_Ns_m']==3.
 assert task['source_saved_envs']==20000 and task['apply_saved20k_history'] is True and task['state_slicing_or_projection'] is False
 assert task['retype_checkpoint'] is False and task['live_full_actor_critic_optimizer_restore'] is True and task['original_PPO_init_at_random_ep_len'] is True
 assert task['training_capacity_scope']=='ORIGINAL_N20K_NO_N80_PRESET'
 assert admission['kind']==ADMISSION_KIND
 for k in ('run_id','role_key','GPU_UUID','source_SHA','asset_USD_SHA','asset_contract_SHA'):assert admission[k]==task[k],k
 assert task['asset_USD_SHA']==USD and task['asset_contract_SHA']==CONTRACT
 for k in ('actual_original_private_GPU_EX_held_by_original_parent','actual_original_shared_finite_env_SH_held','actual_current_canonical_owner_and_budget_admission_passed'):assert admission[k] is True,k
 binding=admission['canonical_binding'];assert binding['path']==task['canonical_path'] and binding['generation']==task['original_canonical_generation']==GENERATION
 assert binding['owner_run_id']==task['run_id'] and binding['owner_parent_pid']==task['owner_parent_pid'] and binding['one_original_writer'] is True
 for k in ('run_id','role_key','GPU_UUID','asset_USD_SHA','asset_contract_SHA'):assert go[k]==task[k],k
 assert go['source_model_SHA']==task['source_SHA'] and go['one_original_writer'] is True and go['original_owner_pid']==task['owner_parent_pid']
 assert go['root_admission_SHA']==task['root_admission_SHA']
 assert go['num_envs']==20000 and go['policy_hz']==50 and go['feedback_hz']==100 and go['physics_dt']==.0025 and go['TGS']==[32,4]
 assert go['source_iteration']==task['source_iteration'] and go['input_Adam']==source_Adam(task)
 assert 0<go['max_parent_seconds']==task['max_parent_seconds']<=3900
 assert go['save_deadline']>now and go['nominal_end_epoch']>go['save_deadline'] and go['exit_headroom_seconds']==task['exit_headroom_seconds']
 assert go['nominal_end_epoch']-go['save_deadline']>=task['exit_headroom_seconds']
 assert environ['CUDA_VISIBLE_DEVICES']==task['GPU_UUID']
 for fd in task['inherited_lock_fds']:
  assert type(fd) is int and fd>=0;(fd_check or os.fstat)(fd)
 assert len(task['inherited_lock_fds'])>=2 and len(set(task['inherited_lock_fds']))==len(task['inherited_lock_fds'])
 assert task['rescue_stop_file'] and task['source_read_purpose'] and task['canonical_path']
 assert task['root_admission_file'] and task['go_file']
 return True

def source_Adam(task):
 if 'source_Adam_step' in task:
  if 'source_Adam17' in task:assert task['source_Adam_step']==task['source_Adam17']
  return task['source_Adam_step']
 return task['source_Adam17']

def read_parent_receipts(job_root,task):
 root=Path(job_root).resolve();a=Path(task['root_admission_file']);g=Path(task['go_file']);a=a if a.is_absolute() else root/a;g=g if g.is_absolute() else root/g
 # Parentauthorityroot maybesiblingofclonedruntime; absoluteTaskbindings+SHA/run/source match, neverreadcanonicalitself.
 raw=a.read_bytes();assert hashlib.sha256(raw).hexdigest()==task['root_admission_SHA']
 admission=json.loads(raw);go=json.loads(g.read_bytes());require_source_admission(task,admission,go)
 return admission,go
