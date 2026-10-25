"""Post-closure text-only interpretation/experiment choice, never model/skill qualification."""
from pathlib import Path
import hashlib,json,time
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports'
read=lambda p:json.loads(Path(p).read_bytes())
proof=read(R/'THREE_EXPERT_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json')
assert proof['passed'] and proof['all_owner_nodes_children_actual_out'] and proof['original_canonical_cost_settled']
assert all(v['actual_cost']['duration_bound_passed'] for v in proof['models'].values())
d=proof['models']['h1']['lifetime_goal_event_diagnostic'];v=d.get('value') or {};valid=d.get('complete_closed_window_accounting_valid') is True
first=read(R/'THREE_EXPERT_ACTUAL_GO_POSITIVE_PPO_UUID_CREATE_ARGV_VERIFIED_ACTUAL.json')['source210']['lifetime_goal_diagnostic_first_snapshot']
events=v.get('events') if valid else None
if valid:
 assert set(events)=={'takeoff_count','landing_count','recovery_count'}
 assert all(isinstance(x,int) and x>=0 for x in events.values())
 assert all(events[k]>=first['value']['events'][k] for k in events)
M=T/'H1_STEP270_FULL_PATH_CLEARANCE_CARRY_V9_MATH_PREPARATION_20261026';math=read(M/'reports/V9_SAVED_ACTUAL_SDK_SOURCE_LOCAL_CPU_AND_EXACT_NEGATIVES_ACTUAL.json')
source=read(T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V79B_20261026/reports/V9_SOURCE_SCOPE_AND_UNCHANGED_ORIGINAL_VALID_READY_CPU_ACTUAL.json')
choose_V9=bool(valid and events['takeoff_count']>0 and events['landing_count']==0 and events['recovery_count']==0 and math['passed_local_CPU_with_previously_captured_actual_SDK_source'] and source['passed_synthetic_source_CPU'])
chosen='H1_STEP270_THREE_EXPERTS_RESOURCE_V79B_20261026' if choose_V9 else 'H1_STEP270_THREE_EXPERTS_RESOURCE_V79_20261026'
result=dict(epoch=time.time(),models_qualified_independently_of_diagnostic=True,H1_event_record_coverage_valid=valid,scope='All completed stochastic training control records in this78 window only. Counts are original event deltas observed at those records with selected resets accounted. Not every physical callback replay, entire historical training, frozen policy evaluation or graduation.',complete_control_rows=v.get('complete_control_rows'),expected_control_rows=d['expected_complete_control_rows'],environment_control_transitions=v.get('environment_control_transitions'),events=events,unique_environment_ids_with_event=v.get('unique_env_ids_with_event') if valid else None,both_original_leading_edges_cross_events=v.get('both_leading_edges_cross_event_count') if valid else None,negative_counter_envframes=v.get('negative_counter_envframes'),invalid_rows=v.get('invalid_rows'),diagnostic_write_errors=v.get('diagnostic_write_errors'),selected_next_source_namespace=chosen,selected_conditional_H1_V9_reward_only=choose_V9,why='Valid completed-control record window has takeoff/edge events but no recorded landing/recovery. Test the bounded reward-shaping hypothesis that the clearance-carry potential should continue beyond leading-edge crossing to the already-existing .60 path target; original success conditions remain unchanged.' if choose_V9 else 'Keep same V8 for further learning/event accounting; invalid optional diagnostics do not invalidate qualified models or introduce a new stop gate.',V9_not_proven_rootcause_or_learning_gain=True,selection_is_experiment_choice_not_model_training_or_physics_gate=True,actual_installed_new_payload_SDK_RSL_source_resources_valid_ready_and_GO_PPO_still_required=True,no_binding_Task_GO_fee_yet=True,complete78_sources={k:dict(SHA=x['final']['SHA'],Adam=x['Adam'],updates=x['updates']) for k,x in proof['models'].items()},closed78_original_fee_sumonce=proof['actual_cost_sumonce'],closed78_remaining_snapshot=proof['remaining_actual_snapshot'],source_proof_report_SHA=hashlib.sha256((R/'THREE_EXPERT_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json').read_bytes()).hexdigest())
with (R/'ACTUAL78_EVENT_ACCOUNTING_AND_NEXT_PROTOCOL_DECISION_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(result,f,indent=2)
print(json.dumps({k:result[k] for k in ('H1_event_record_coverage_valid','complete_control_rows','events','selected_next_source_namespace','selected_conditional_H1_V9_reward_only')}))
