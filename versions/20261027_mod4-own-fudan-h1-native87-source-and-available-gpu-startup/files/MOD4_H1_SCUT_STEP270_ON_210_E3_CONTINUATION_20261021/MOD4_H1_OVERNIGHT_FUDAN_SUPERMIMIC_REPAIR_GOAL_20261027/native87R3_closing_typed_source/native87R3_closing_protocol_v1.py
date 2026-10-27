"""Pure native87 exact source/clock/fee metadata. No process/model/budget side effects."""
import math
from pathlib import PurePosixPath
CANONICAL='/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json'
SOURCE_SHA='0c1edb9603c1cb84fbb894d242dae1b6a7c87fe3237d658dbc486ccbbad3d394'
KIND='MOD4_H1_NATIVE87_POLICY_ONLY_SOURCE_SDK_CPU_PRECONTROL_V2'
KEYS=('h1','recovery')
SEEDS=dict(h1=27,e2=28,recovery=29)
def require(v,message):
 if not v:raise RuntimeError(message)
def active_keys(q):
 return tuple(k for k in KEYS if k in q['specs'])
def validate_detached(q):
 keys=active_keys(q);two=keys==('h1','recovery')
 require(two and set(q['specs'])==set(KEYS),'Exact R3 two-native schedule required')
 suffix='v87r3'
 base72='/home/lc01/Zonglin Li/zonglin2/tasks/H1step270_own_fudan_native_2610'+suffix
 base210='/mnt/mod4_linux_durable_20261013/H1step270_own_fudan_native_2610'+suffix
 require(q['owner_root']==base72+'/owner','Use owner_root, never identity cwd')
 expected={k:(base210 if k=='h1' else base72)+'/'+k for k in keys}
 require(q['roots']==expected and set(q['nodes'])==set(keys),'Actual active roots/nodes differ')
 require(q.get('deferred_experts',[])==(['e2'] if two else []),'Deferred schedule differs')
 o=q['owner_identity'];require(type(o['pid']) is int and o['pid']>0 and o['creation']>0,'Actual owner pid/create absent')
 for k in keys:
  s=q['specs'][k]
  require(s['key']==k and s['source_SHA']==s['bootstrap_source_SHA']==SOURCE_SHA and s['source_Adamstep']==832460,'Qualified normal H1 bootstrap differs')
  require(s['seed']==SEEDS[k] and s['native87_policy_only'] is True and s['new_native_architecture_fresh'] is True,'New native scope differs')
  require(s['native_continuation'] is False and s['closed_production_continuation'] is False,'No exact legacy native/PPO continuation')
  require(s['execution_backend']==('source210' if k=='h1' else 'target72'),'Backend differs')
 def no_secret(x):
  if isinstance(x,dict):
   require(not {'password','owner_ssh_password','token','RM_SSH_PASSWORD'}&set(x),'Secret in saved metadata')
   for c in x.values():no_secret(c)
  elif isinstance(x,(list,tuple)):
   for c in x:no_secret(c)
 no_secret(q);return True

def closing_gate(go,now):
 require(set(go)==set(KEYS),'Exact R3 two-native signed GO keyset required')
 assert max(x['nominal_end_epoch'] for x in go.values())-now<=900,'Original <=900 closing boundary retained'
 for key,g in go.items():
  require(g['source_SHA']==g['bootstrap_SHA']==SOURCE_SHA and g['bootstrap_Adam']==832460,'Qualified normal H1 bootstrap GO')
  require(g['max_parent_seconds']==3900 and g['exit_headroom_seconds']==300,'Original finite cap')
  require(abs(g['save_deadline']-g['learning_started_epoch']-3600)<1e-6 and abs(g['nominal_end_epoch']-g['learning_started_epoch']-3900)<1e-6,'Original clock deadlines')
  require(g['native87_policy_only'] is True and g['new_native_architecture_fresh'] is True and g['native_continuation_restore_required'] is False,'Fresh repaired native scope')
  require(g['source_qualification_kind']==KIND and g['seed']==SEEDS[key] and g['num_envs']==4096,'Ready/new seed/env scope')
 return True

def native_window(commit):
 require(commit['passed'] is True and commit['trace_persisted'] is True and commit['primary_error'] is None and not commit['secondary_errors'],'Complete native FINAL required')
 final=commit['final'];c=commit['counters']
 require(c=={k:final[k] for k in ('updates','world_updates','policy_updates')},'Final native counters disagree')
 require(all(type(c[k]) is int and c[k]>0 for k in c),'New native WM/Pi/iteration progress required')
 require(final['verified_new_publication'] and final['original_full_save_chain_returned'],'Actual complete save publisher required')
 return dict(passed=True,start_iteration=0,start_world_updates=0,start_policy_updates=0,**c,native_PPO20Adam_rule_applied=False)

def validate_fees(authority,go,owner):
 require(authority['owner_exit']['original_cost_settled'] is True
  and authority['cohort']['original_cost_settled'] is True
  and authority['all_authority72_owner_children_actual_out'] is True,'Original owner closure incomplete')
 require(authority['canonical_active_segment'] is None and authority['canonical_path']==CANONICAL,'Sole72 original canonical not None')
 locks=authority['original_locks'];require(len(locks)==2 and all(x['actual_fcntl_free'] is True for x in locks),'Original72 two locks not free')
 segment=authority['original_segment'];require(segment['owner_parent_pid']==owner['pid'] and segment['started_epoch']>=owner['creation'],'Wrong original owner segment')
 experts=segment['experts'];require(set(experts)==set(go)==set(KEYS),'Exact active independent original fee slots required')
 total=0.
 for key in go:
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

def optional_phase(value):
 result=dict(optional=True,model_gate=False,counts_attempted_starts_not_completed_Pi=True,
  missing=value is None,diagnostic_valid=False,not_physical_task_events=True)
 if value is None:return dict(result,limitation='Optional phase sampling receipt missing')
 try:
  require(value['schema']=='mod4.native.sampled_policy_phase_coverage.v1','Wrong optional phase schema')
  require(value['counts_attempted_starts_not_completed_optimizer_updates'] is True
   and value['not_a_training_or_model_or_skill_gate'] is True,'Optional count semantics differ')
  require(value['window_start_iteration']==0,'Fresh native sampling baseline differs')
  counts=list(value['bands'].values())
  require(len(counts)==5 and all(type(x) is int and x>=0 for x in counts)
   and sum(counts)==value['sampled_starts'],'Invalid optional band counts')
  result.update(diagnostic_valid=value['diagnostic_valid'] is True,policy_sampling_calls=value['policy_sampling_calls'],
   sampled_starts=value['sampled_starts'],bands=value['bands'],imagined_horizon_intersects_request=value['imagined_horizon_intersects_request'],
   errors=value.get('errors'),io_errors=value.get('io_errors'))
 except Exception as error:result['limitation']=type(error).__name__+': '+str(error)
 return result
