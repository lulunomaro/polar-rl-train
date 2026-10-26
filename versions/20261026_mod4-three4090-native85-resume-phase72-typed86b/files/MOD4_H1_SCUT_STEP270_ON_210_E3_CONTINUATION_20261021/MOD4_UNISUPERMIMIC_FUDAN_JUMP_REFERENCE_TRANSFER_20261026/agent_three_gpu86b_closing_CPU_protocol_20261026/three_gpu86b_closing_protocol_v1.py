"""Pure metadata closing gates. No I/O, transport, model or budget side effect."""
import math

KEYS=('h1','e2','recovery')
ROOT72='/home/lc01/Zonglin Li/zonglin2/tasks/H1step270_three_gpu_native_cont_2610v86b'
ROOT210='/mnt/mod4_linux_durable_20261013/H1step270_three_gpu_native_cont_2610v86b'
CANONICAL='/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json'
SOURCES=dict(h1='8bb9869ac683550c1e7be1c9dffae9a5eac022e0de0fc8f251cd2005cfa6d4c6',
 e2='94e7f272176b4a7c485b50c1ac61f95a3ecd4460ee6a73034f9e7a47a57045af',
 recovery='7f8f270c84b7e3d9e7efd0b1bd29d10d430a51bb976e1689222859f24e714d59')
ADAM=dict(h1=829700,recovery=862540)


def require(value,message):
 if not value:raise RuntimeError(message)


def closing_gate(go,now):
 require(set(go)==set(KEYS),'Three actual original GO records required')
 assert max(x['nominal_end_epoch'] for x in go.values())-now<=900,'Original <=900 closing boundary retained'
 for key,row in go.items():
  require(row['source_SHA']==SOURCES[key],'Wrong original GO source')
  require(row['max_parent_seconds']==3900 and row['exit_headroom_seconds']==300,'Original parent/exit bound changed')
  require(abs(row['save_deadline']-row['learning_started_epoch']-3600)<1e-6
   and abs(row['nominal_end_epoch']-row['learning_started_epoch']-3900)<1e-6,'Original save/nominal bound changed')
 native=go['e2']
 require(native['native_continuation_restore_required'] is True
  and native['source_native_iteration']==68 and native['window_start_world_updates']==680
  and native['window_start_policy_updates']==58 and native['bootstrap_SHA']==SOURCES['h1']
  and native['bootstrap_Adam']==829700,'Original native source/baseline GO differs')
 return True


def validate_detached(q):
 require(isinstance(q['run_id'],str) and q['run_id'],'Run identity absent')
 require(q['owner_root']==ROOT72+'/owner','Use detached.owner_root, never identity.root/cwd')
 require(q['roots']==dict(h1=ROOT210+'/h1',e2=ROOT72+'/e2',recovery=ROOT72+'/recovery'),'Wrong three task roots')
 require(set(q['specs'])==set(KEYS),'Wrong source roles')
 owner=q['owner_identity'];require(type(owner['pid']) is int and owner['pid']>0 and owner['creation']>0,'Actual owner pid/create absent')
 for key in KEYS:
  require(q['specs'][key]['key']==key and q['specs'][key]['source_SHA']==SOURCES[key],'Detached source identity differs')
  require(q['specs'][key]['execution_backend']==('source210' if key=='h1' else 'target72'),'Detached backend differs')
 def secrets(value):
  if isinstance(value,dict):
   require(not {'password','owner_ssh_password','token','RM_SSH_PASSWORD'}&set(value),'Credential field in saved closing metadata')
   for child in value.values():secrets(child)
  elif isinstance(value,(list,tuple)):
   for child in value:secrets(child)
 secrets(q)
 return True


def validate_fees(authority,go,owner):
 require(authority['owner_exit']['original_cost_settled'] is True
  and authority['cohort']['original_cost_settled'] is True
  and authority['all_authority72_owner_children_actual_out'] is True,'Original owner closure incomplete')
 require(authority['canonical_active_segment'] is None and authority['canonical_path']==CANONICAL,'Sole72 original canonical not None')
 locks=authority['original_locks'];require(len(locks)==2 and all(x['actual_fcntl_free'] is True for x in locks),'Original72 two locks not free')
 segment=authority['original_segment'];require(segment['owner_parent_pid']==owner['pid'] and segment['started_epoch']>=owner['creation'],'Wrong original owner segment')
 experts=segment['experts'];require(set(experts)==set(go)==set(KEYS),'Three independent original fee slots required')
 total=0.
 for key in KEYS:
  cost=experts[key];g=go[key]
  require(cost['duration_bound_passed'] is True,'Original duration false remains false: '+key)
  require(cost['actual_returncode']==authority['cohort']['rows'][key]['returncode'],'Original fee/terminal rc differs')
  require(cost['started_epoch']==g['learning_started_epoch'] and math.isfinite(cost['charged_seconds'])
   and 0<cost['charged_seconds']<=3900,'Original fee start/duration invalid')
  require(abs(cost['charged_seconds']-(cost['ended_epoch']-cost['started_epoch']))<1e-5,'Actual independent original duration differs')
  require(cost['max_parent_seconds']==3900,'Original slot cap changed')
  total+=cost['charged_seconds']
 require(abs(total-segment['charged_expert_seconds'])<1e-5,'Original single-writer sum differs')
 require(math.isfinite(authority['original_canonical_remaining']),'Nonfinite actual remainder')
 return dict(passed=True,actual_cost_sumonce=total,remaining_actual_snapshot=authority['original_canonical_remaining'],
  no_refund_clamp_reconstruction_or_secondwriter=True)


def native_window(commit,source_native=None):
 require(commit['passed'] is True and commit['trace_persisted'] is True
  and commit['primary_error'] is None and not commit['secondary_errors'],'Native formal FINAL incomplete')
 final=commit['final'];cont=commit['native_continuation'];restore=cont['restore'];progress=cont['window_progress']
 require(restore['passed'] is True and restore['source_checkpoint_SHA']==SOURCES['e2']
  and restore['restored_iteration']==68 and restore['restored_world_updates']==680
  and restore['restored_policy_updates']==58,'Native85 restore lineage differs')
 require(restore['all_three_native_optimizers_restored'] is True and restore['new_physical_episode'] is True
  and restore['replay_restored'] is False and restore['fresh_replay_refill_steps']==48,'Native new-episode restore differs')
 require(cont['no_fresh_weight_restart'] is True and final['updates']>68
  and final['world_updates']>=680 and final['policy_updates']>58,'No new native learning progress')
 require(progress['world_updates']==final['world_updates']-680
  and progress['policy_updates']==final['policy_updates']-58 and progress['policy_updates']>0,'Native new-window delta differs')
 if source_native is not None:
  require(source_native['iteration']==68,'Native initial source iteration differs')
 return dict(passed=True,source_iteration=68,source_world_updates=680,source_policy_updates=58,
  cumulative_iteration=final['updates'],world_updates=final['world_updates'],policy_updates=final['policy_updates'],
  window_world_updates=progress['world_updates'],window_policy_updates=progress['policy_updates'],native_PPO20Adam_rule_applied=False)


def optional_phase(value):
 result=dict(optional=True,model_gate=False,counts_attempted_starts_not_completed_Pi=True,
  missing=value is None,diagnostic_valid=False,not_physical_task_events=True)
 if value is None:return dict(result,limitation='Optional phase sampling receipt missing')
 try:
  require(value['schema']=='mod4.native.sampled_policy_phase_coverage.v1','Wrong optional phase schema')
  require(value['counts_attempted_starts_not_completed_optimizer_updates'] is True
   and value['not_a_training_or_model_or_skill_gate'] is True,'Optional count semantics differ')
  require(value['window_start_iteration']==68,'Optional sampling baseline differs')
  counts=list(value['bands'].values())
  require(len(counts)==5 and all(type(x) is int and x>=0 for x in counts)
   and sum(counts)==value['sampled_starts'],'Invalid optional band counts')
  result.update(diagnostic_valid=value['diagnostic_valid'] is True,policy_sampling_calls=value['policy_sampling_calls'],
   sampled_starts=value['sampled_starts'],bands=value['bands'],imagined_horizon_intersects_request=value['imagined_horizon_intersects_request'],
   errors=value.get('errors'),io_errors=value.get('io_errors'))
 except Exception as error:result['limitation']=type(error).__name__+': '+str(error)
 return result
