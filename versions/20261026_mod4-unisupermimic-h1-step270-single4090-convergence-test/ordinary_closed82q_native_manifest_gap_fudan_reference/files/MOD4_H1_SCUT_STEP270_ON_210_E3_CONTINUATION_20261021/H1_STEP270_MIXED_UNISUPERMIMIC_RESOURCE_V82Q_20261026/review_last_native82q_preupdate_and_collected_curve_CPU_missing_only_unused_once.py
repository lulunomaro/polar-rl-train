from pathlib import Path
import json,time,torch
N=Path(__file__).resolve().parent;R=N/'reports';read=lambda p:json.loads(Path(p).read_bytes());q=read(R/'THREE_EXPERTS_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json');receipt=read(R/'LAST_NATIVE_COMPLETE_PREUPDATE_EXECUTION_EVIDENCE_RETURNED_ACTUAL.json');assert receipt['actual_finite_returned']
torch.set_num_threads(2);s=torch.load(receipt['checkpoint']['local_path'],map_location='cpu',weights_only=False);counts=[0,0]
def finite(x):
 if torch.is_tensor(x):counts[0]+=1;counts[1]+=int(x.is_floating_point());assert not x.is_floating_point() or torch.isfinite(x).all()
 elif isinstance(x,dict):
  for v in x.values():finite(v)
 elif isinstance(x,(tuple,list)):
  for v in x:finite(v)
finite(s);last=receipt['checkpoint'];method=s['UniSuperMimic_H1_test'];contract=s['UniSuperMimic_test_contract'];assert contract['not_production_expert_source'] and contract['original_RSL_core_frozen_bootstrap_only'] and contract['state_joints']==30 and contract['actions']==6 and contract['obs_dim']==128
assert method['iteration']==last['updates'] and last['policy_updates']>0 and last['world_updates']>0
optimizers={}
for name in ('opt_wm','opt_pi','opt_v'):
 states=method[name]['state'];assert states;steps=[int(v['step']) for v in states.values()];optimizers[name]=dict(parameter_states=len(states),min_step=min(steps),max_step=max(steps))
assert optimizers['opt_wm']['max_step']==last['world_updates'] and optimizers['opt_pi']['max_step']==last['policy_updates'] and optimizers['opt_v']['max_step']>0
assert {int(v['step']) for v in s['optimizer_state_dict']['state'].values()}=={q['specs']['e2']['source_Adamstep']}
production=read(R/'PRODUCTION_PAIR_AND_NATIVE_METHOD_FULLSTATE_ORIGINAL_COST_CPU_ACTUAL.json');sourceSTD=production['models']['h1']['raw_actor_distribution_std_param6']['source'];assert s['actor_state_dict']['distribution.std_param'].detach().reshape(-1).tolist()==sourceSTD
snapshot={};phase=s['H1_step270_task_state']['phase'];assert phase['version']==270 and phase['num_envs']==20000
age=phase.get('tensors',{}).get('age_control')
if torch.is_tensor(age):snapshot=dict(scope='Only currently retained episode state in the last complete preupdate, not whole-window episode ages',age_min=int(age.min()),age_max=int(age.max()),age_median=float(age.float().median()),envs_in_original_request_age100_to179=int(((age>=100)&(age<180)).sum()))
base=N/'current_three_closed_text/e2/job0/production/control_prefix_raw';diag=read(base/'CONTROL_LIFETIME_GOAL_EVENTS_ACTUAL.json');idx=read(base/'CONTROL_VALID_PREFIX_INDEX_ACTUAL.json');assert diag['diagnostic_valid'] and diag['complete_control_rows']==idx['controls'] and diag['environment_control_transitions']==idx['controls']*20000
curvepath=N/'current_three_closed_text/e2/job0/production/ACTUAL_H1_CONVERGENCE_CURVE.jsonl';curve=[json.loads(line) for line in curvepath.read_text('utf8').splitlines() if line.strip()]
assert curve and all(x['events']['diagnostic_valid'] for x in curve)
stat=receipt['target72']['finalization_path_stat_only'];endfile=next(x for x in stat if x['path'].endswith('/native_supermimic_H1_final.pt'));assert endfile['present']
result=dict(epoch=time.time(),passed_complete_preupdate_fullfinite_CPU=True,not_a_FINAL_or_production_source=True,original_node_error_and_missing_FINAL_manifest_not_rewritten=True,original_unpublished_native_final_pt_exists_stat_only=endfile,native_last_complete_checkpoint=last,native_iteration=method['iteration'],world_updates=last['world_updates'],policy_updates=last['policy_updates'],finite_tensor_counts=counts,optimizer_steps=optimizers,original_PPO_17Adam_source_literal_retained=True,original_PPO_STD6_matches_existing_source_CPU_receipt=True,original_PPO_other_weights_not_reread_or_claimed_literal_recompared=True,current_episode_age_diagnostic=snapshot,complete_record_scope=dict(complete_control_rows=diag['complete_control_rows'],environment_control_transitions=diag['environment_control_transitions'],events=diag['events'],leading_edge_cross_events=diag['both_leading_edges_cross_event_count'],coverage_valid=True),curve_rows=len(curve),first_curve_elapsed=curve[0]['GO_elapsed_s'],last_curve_elapsed=curve[-1]['GO_elapsed_s'],last_curve_world_updates=curve[-1]['world_updates'],last_curve_policy_updates=curve[-1]['policy_updates'],no_recorded_task_event_not_causal_failure_diagnosis=True,not_frozen_evaluation_or_permanent_impossibility=True,finalization_cause_not_proven=True,no_inference_physics_GPU_nativequery_or_source_PT_reread=True)
assert not torch.cuda.is_initialized()
with (R/'NATIVE_LAST_COMPLETE_PREUPDATE_FINITE_AND_FULL_RECORD_EVENTS_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(result,f,indent=2)
print(json.dumps(dict(finite_complete_preupdate=True,world_updates=last['world_updates'],policy_updates=last['policy_updates'],records=result['complete_record_scope'],unpublished_final_pt_present=True,FINAL_manifest_missing_original_error=True)))
