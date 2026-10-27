"""Native88 metadata only. No model, SDK, process, network or budget I/O."""
from pathlib import PurePosixPath
import math
KEYS=('h1','recovery')
KIND='MOD4_H1_NATIVE88_GAS400_CHANGED_PLANT_NATIVE_SOURCE_CPU_V1'
BOOTSTRAP_SHA='0c1edb9603c1cb84fbb894d242dae1b6a7c87fe3237d658dbc486ccbbad3d394'
CANONICAL='/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json'
SOURCES={
 'h1':dict(SHA='ae5ff91877bcfdda72b864a181fdbbbd0c78401cb34591ca507adda44a6632e9',updates=3317,world_updates=33170,policy_updates=3253,seed=27),
 'recovery':dict(SHA='870e63b6ef41f870109fc1c3b6d9d67fe2f472ca8436145755db5d74a7b8e404',updates=1409,world_updates=14090,policy_updates=1345,seed=29)}
PIN_FIELDS=('manifest_SHA','native88_contract_SHA','qualified_R5_pair_report_SHA','previous_R5_closure_SHA','reference_artifact_SHA','gas400_parameter_source_contract_SHA','actual_gas400_asset_composition_report_SHA','own_step_objective_qualification_SHA','objective_contract_SHA')
REFERENCE_SHA='9223a53e7bf85a0dc3505cc46c0eb33d04fc35a9bf85e7ffe0e4fbd03e1e46c3'
UUIDS=dict(h1='GPU-937bdb0b-0d8f-aa3d-a10e-1b24969a5d4e',recovery='GPU-c27eecbd-6838-7290-1cd2-37e34522213d')
METHOD=dict(num_envs=4096,episode_timeout_s=5.,control_dt_s=.01,physics_dt_s=.0025,solver='TGS',solver_position_iterations=32,solver_velocity_iterations=4,decimation=4,packed_state_dim=127,aux_dim=54,static_xi_dim=31,obs_dim=86,goal_dim=146,goal_frames=10,hist=10,wm_hidden=[2048,2048,2048],policy_hidden=[2048,1024,512,256],horizon=32,buffer_steps=1000,utd=.4,wm_batch=1024,pi_batch=1024,wm_only_iters=64,amp='none',compile=False)

def require(value,message):
 if not value:raise ValueError(message)
def active_keys(q):return KEYS if set(q['specs'])==set(KEYS) else ()
def bind_prepared_detached(q,prepared):
 # Enrich only an in-memory copy. Original actual receipts stay byteexact.
 import copy
 value=copy.deepcopy(q)
 if 'owner_script' not in value:value['owner_script']=prepared['owner_script']
 return value
def validate_detached(q,prepared=None):
 require(set(q['specs'])==set(q['roots'])==set(q['nodes'])==set(KEYS) and q['deferred_experts']==['e2'],'two H1 native88 slots; unknown e2 untouched')
 require(isinstance(q['run_id'],str) and q['run_id'],'actual run identity')
 owner=PurePosixPath(q['owner_root']);require(owner.name=='owner' and owner.is_relative_to('/home/lc01/Zonglin Li/zonglin2/tasks'),'independent owner root, never cwd')
 o=q['owner_identity'];require(type(o['pid']) is int and o['pid']>0 and o['creation']>0 and o.get('exe') and isinstance(o.get('argv'),list) and o['argv'] and o.get('root'),'complete actual owner identity required')
 require(o['argv'][-1]==str(owner/q['owner_script']),'owner script path exact')
 if 'own_children' in q:
  require(isinstance(q['own_children'],list),'optional hostscoped receipt list')
  for r in q['own_children']:require(r['execution_backend'] in ('source210','target72') and type(r['pid']) is int and r['pid']>0 and r['creation']>0,'typed hostscoped own PID/create')
 for key in KEYS:
  s=q['specs'][key];source=SOURCES[key];root=PurePosixPath(q['roots'][key])
  base='/mnt/mod4_linux_durable_20261013' if key=='h1' else '/home/lc01/Zonglin Li/zonglin2/tasks'
  require(root.is_relative_to(base) and '..' not in root.parts and root.name==key and str(root)!=s['previous_runtime_root'],'new per-role own namespace')
  require(s['key']==key and s['source_SHA']==source['SHA'] and s['source_progress']=={k:source[k] for k in ('updates','world_updates','policy_updates')},'own R5 source and global baseline')
  require(s['bootstrap_source_SHA']==BOOTSTRAP_SHA and s['source_Adamstep']==832460 and s['seed']==s['native_seed']==source['seed'],'separate normal86 frozen witness/seed')
  require(s['native88_changed_plant'] is True and s['changed_plant700_to_nominal400'] is True and s['native_continuation_restore_required'] is True,'new changed plant native scope')
  require(s['native87_policy_only'] is False and s['new_native_architecture_fresh'] is False and s['closed_production_continuation'] is False,'never normalPPO/fresh87/oldE2')
  require(s['execution_backend']==('source210' if key=='h1' else 'target72') and s['max_parent_seconds']==3900 and s['exit_headroom_seconds']==300,'original backend/finite cap')
  require(s['GPU_UUID']==UUIDS[key] and s['method_config']==METHOD and s['finite_method_test'] is True and s['native_continuation'] is True,'exact selected GPU and same repaired method')
  require(s['reference_artifact_SHA']==REFERENCE_SHA and s['independent_own_step_objective_admission_passed'] is True,'effective objective / original9223 reference')
  require(q['nodes'][key]['root']==str(root) and type(q['nodes'][key]['detached_pid']) is int,'actual node launch receipt bound')
 if prepared is not None:
  require(prepared['roots']==q['roots'] and prepared['owner_root']==q['owner_root'] and prepared['owner_script']==q['owner_script'],'prepared vs actual deployment roots')
  for key in KEYS:
   actual={k:v for k,v in q['specs'][key].items() if k!='preinstalled_CPU_proof_SHA'}
   expected={k:v for k,v in prepared['specs'][key].items() if k!='preinstalled_CPU_proof_SHA'}
   require(actual==expected,'actual source spec differs from prepared '+key)
 def no_secret(x):
  if isinstance(x,dict):
   require(not {'password','owner_ssh_password','token','RM_SSH_PASSWORD'}&set(x),'secret in metadata')
   for v in x.values():no_secret(v)
  elif isinstance(x,(list,tuple)):
   for v in x:no_secret(v)
 no_secret(q);return True

def validate_actual_GO_binding(go,q):
 require(set(go)==set(KEYS),'actual signed two-GO required')
 for key,g in go.items():
  s=q['specs'][key];source=SOURCES[key]
  require(g['run_id']==q['run_id'] and g['original_owner_pid']==q['owner_identity']['pid'] and g['original_owner_creation']==q['owner_identity']['creation'],'actual sole owner signed GO')
  require(g['source_SHA']==source['SHA'] and g['source_progress']==s['source_progress'] and g['bootstrap_SHA']==BOOTSTRAP_SHA and g['bootstrap_Adam']==832460,'native source vs frozen normal witness')
  require(g['source_qualification_kind']==KIND and g['native88_changed_plant'] is True and g['changed_plant700_to_nominal400'] is True and g['native_continuation_restore_required'] is True and g['new_native_architecture_fresh'] is False,'typed native88 grant')
  require(g['seed']==source['seed'] and g['num_envs']==4096 and g['independent_own_step_objective_admission_passed'] is True,'seed4096/effective objective')
  for pin in ('manifest_SHA','native88_contract_SHA','gas400_parameter_source_contract_SHA','actual_gas400_asset_composition_report_SHA','own_step_objective_qualification_SHA','objective_contract_SHA'):require(g[pin]==s[pin],'actual GO source pin '+pin)
  require(g['max_parent_seconds']==3900 and g['exit_headroom_seconds']==300 and abs(g['save_deadline']-g['learning_started_epoch']-3600)<1e-6 and abs(g['nominal_end_epoch']-g['learning_started_epoch']-3900)<1e-6,'original3900/3600/300 clock')
 return True

def closing_gate(go,now):
 require(set(go)==set(KEYS),'no actual GO: closing forbidden')
 assert max(x['nominal_end_epoch'] for x in go.values())-now<=900,'Original <=900 closing boundary retained'
 for key,g in go.items():
  source=SOURCES[key]
  require(g['source_SHA']==source['SHA'] and g['source_qualification_kind']==KIND and g['bootstrap_SHA']==BOOTSTRAP_SHA,'typed native88 actual GO')
  require(g['max_parent_seconds']==3900 and g['exit_headroom_seconds']==300 and abs(g['nominal_end_epoch']-g['learning_started_epoch']-3900)<1e-6 and abs(g['save_deadline']-g['learning_started_epoch']-3600)<1e-6,'original finite clock retained')
 return True

def verify_window(w,spec,require_new_pi=False):
 require(w['schema']=='mod4.native88.gas400.changed_plant_window.v1' and w['not_same_physics'] is True,'typed changed-plant window')
 source=SOURCES[spec['key']];require(w['role']==spec['key'] and w['source']==source,'source role/seed/global baseline literal exact')
 require(w['parameter_source_contract_SHA']==spec['gas400_parameter_source_contract_SHA'] and w['actual_asset_composition_report_SHA']==spec['actual_gas400_asset_composition_report_SHA'],'gas source/asset proof pin')
 require(w['adaptation']==dict(fresh_warmup_controls=64,new_window_world_only_iterations=64,minimum_new_world_steps_before_newPi=640),'new-window adaptation declared')
 c=w['counters']
 fields=('native_iteration','window_iteration','world_updates','policy_updates','new_world_updates','new_policy_updates','completed_fresh_controls','window_start_sim_steps')
 require(all(type(c[k]) is int and c[k]>=0 for k in fields),'integer cumulative/new counters')
 require(c['native_iteration']-source['updates']==c['window_iteration'] and c['world_updates']-source['world_updates']==c['new_world_updates'] and c['policy_updates']-source['policy_updates']==c['new_policy_updates'],'restored positive counters are not new progress')
 if require_new_pi or c['new_policy_updates']>0:
  require(c['new_policy_updates']>0 and c['new_world_updates']>=640 and c['completed_fresh_controls']>=64,'fresh physical+WM+newPi progress')
  first=w['first_new_policy_update'];require(first['new_policy_updates']==1 and first['window_iteration']>=64 and first['completed_fresh_controls']>=64 and first['new_world_updates']>=640,'first Pi adaptation boundary')
  require(w['prewrite_preload_validation']['actual_original_preload_active'] is True and w['prewrite_preload_validation']['actual_new_gas_parameters_passed'] is True,'original actual preload prewrite on400N')
 return c

def validate_first_new_positive(first,index,pre,go,spec):
 source=SOURCES[spec['key']]
 require(go['source_SHA']==spec['source_SHA']==source['SHA'] and go['source_qualification_kind']==KIND and go['manifest_SHA']==spec['manifest_SHA'],'firstPi actual native88 Task/GO')
 require(first['native_actual_method']=='own_MOD4_native88_nominal400_changed_plant' and first['original_source_actor_frozen_not_PPO_learning'] is True and first['not_PPO_or_production_source'] is True,'native producer scope')
 w=first['native88_migration_window'];c=verify_window(w,spec,True)
 require(first['updates']==c['native_iteration'] and first['world_updates']==c['world_updates'] and first['policy_updates']==c['policy_updates'] and first['before_control']==c['completed_fresh_controls'],'same publication/global/window/control counters')
 producer=first['producer'];require(producer['initial_native_source']==source and producer['native_architecture_fresh'] is False and producer['method']=='MOD4_own_Fudan_native88_nominal400_changed_plant','original native88 publication producer')
 for a,b in [('gas400_parameter_source_contract_SHA','gas400_parameter_source_contract_SHA'),('actual_gas400_asset_composition_report_SHA','actual_gas400_asset_composition_report_SHA'),('own_step_objective_qualification_SHA','own_step_objective_qualification_SHA'),('runtime_objective_contract_SHA','objective_contract_SHA')]:require(producer[a]==spec[b],'original producer pin '+a)
 require(producer['bootstrap_task_source_SHA']==BOOTSTRAP_SHA and producer['bootstrap_Adam']==832460 and producer['reference_artifact_SHA']==REFERENCE_SHA,'producer frozen witness/reference')
 require(producer['bridge_source_SHA']==spec['candidate_pins']['source/native_own_fudan88_gas400_training_v2.py'] and producer['finalization_source_SHA']==spec['candidate_pins']['source/native_finalization_own88_gas400.py'],'exact deployed producer Python')
 require(isinstance(first['run_token'],str) and first['run_token'] and isinstance(first['save_token'],str) and first['save_token'],'original atomic publication tokens')
 require(pre['source_SHA']==source['SHA'] and pre['frozen_RSL_bootstrap_SHA']==BOOTSTRAP_SHA and pre['actual_reference_SHA']==REFERENCE_SHA,'actual plant source/witness/reference')
 require(pre['actual_GPU_runtime_readback_passed'] is True and pre['before_first_native_physical_control_and_Pi'] is True and pre['actual_environment_count']==4096,'actual fresh GPU precontrol')
 require(pre['actual_static_context_dim']==31 and pre['actual_dynamic_aux_dim']==54 and pre['packed_state_dim']==127 and pre['actor_obs_dim']==86 and pre['goal_frame_dim']==146,'actual native88 dimensions')
 require(pre['actual_physics_dt']==.0025 and pre['actual_control_dt']==.01 and pre['actual_solver']==[1,32,4] and pre['original_true_physical_success_unchanged'] is True,'original solver/clock/success')
 require(pre['new_native_model_initialization'] is False and pre['actual_new_gas_parameters']['actual_new_gas_parameters_passed'] is True,'models preserved / actual400N plant')
 require(pre['actual_source_frozen_RSL_witness']['old700N_environment_DR_not_restored'] is True,'no old plant restore')
 matches=[r for r in index.get('preupdate_full_sources',[]) if all(r.get(k)==first.get(k) for k in ('path','SHA','bytes','before_control'))]
 require(len(matches)==1 and index['controls']>=first['before_control'] and matches[0]['no_optimizer_call'] is True,'same natural critical-index publication required')
 return dict(passed=True,source=source,new_world_updates=c['new_world_updates'],new_policy_updates=c['new_policy_updates'],completed_fresh_controls=c['completed_fresh_controls'],SHA=first['SHA'],before_control=first['before_control'],not_skill_or_FINAL=True)

def publication_index_status(first,index):
 if first is None:return 'pending_first_new_policy'
 if index is None:return 'pending_natural_index_publication'
 matches=[r for r in index.get('preupdate_full_sources',[]) if all(r.get(k)==first.get(k) for k in ('path','SHA','bytes','before_control'))]
 if not matches:return 'pending_natural_index_publication'
 require(len(matches)==1,'duplicate matching critical preupdate metadata')
 return 'coherent' if index['controls']>=first['before_control'] else 'pending_natural_index_publication'

def native_window(commit,spec):
 require(commit['passed'] is True and commit['trace_persisted'] is True and commit['primary_error'] is None and not commit['secondary_errors'],'formal complete native88 FINAL, never rc0-only')
 final=commit['final'];c=verify_window(final['native88_migration_window'],spec,True)
 require(commit['counters']=={k:final[k] for k in ('updates','world_updates','policy_updates')},'formal global counters')
 require(final['updates']==c['native_iteration'] and final['world_updates']==c['world_updates'] and final['policy_updates']==c['policy_updates'],'formal/window counters')
 require(final['verified_new_publication'] is True and final['original_full_save_chain_returned'] is True,'original complete native publisher')
 return dict(passed=True,source=SOURCES[spec['key']],new_world_updates=c['new_world_updates'],new_policy_updates=c['new_policy_updates'],completed_fresh_controls=c['completed_fresh_controls'],native_PPO20Adam_rule_applied=False)


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
