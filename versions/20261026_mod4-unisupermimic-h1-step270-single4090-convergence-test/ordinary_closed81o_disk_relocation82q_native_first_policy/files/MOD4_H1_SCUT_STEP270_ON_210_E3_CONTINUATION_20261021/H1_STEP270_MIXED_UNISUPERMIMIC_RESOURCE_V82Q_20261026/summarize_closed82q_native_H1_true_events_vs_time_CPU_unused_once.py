from pathlib import Path
import json,time
N=Path(__file__).resolve().parent;R=N/'reports';read=lambda p:json.loads(Path(p).read_bytes())
proof=read(R/'PRODUCTION_PAIR_AND_NATIVE_METHOD_FULLSTATE_ORIGINAL_COST_CPU_ACTUAL.json');assert proof['original_canonical_cost_settled'] and proof['all_owner_nodes_children_actual_out']
path=N/'current_three_closed_text/e2/job0/production/ACTUAL_H1_CONVERGENCE_CURVE.jsonl';rows=[]
if path.is_file():
 for i,line in enumerate(path.read_text('utf8').splitlines(),1):
  if line.strip():rows.append(dict(read_line=i,**json.loads(line)))
native=proof['native_method'];curves=[]
for row in rows:
 value=row['events'];assert value['diagnostic_valid'] and value['complete_control_rows']==row['completed_control_rows'] and value['environment_control_transitions']==row['environment_transitions']
 curves.append(dict(GO_elapsed_s=row['GO_elapsed_s'],environment_transitions=row['environment_transitions'],native_iteration=row['native_iteration'],world_updates=row['world_updates'],policy_updates=row['policy_updates'],events=value['events'],leading_edge_cross_events=value['both_leading_edges_cross_event_count'],world_model_losses=row['wm_last'],policy_losses=row['policy_last']))
for a,b in zip(curves,curves[1:]):assert a['GO_elapsed_s']<=b['GO_elapsed_s'] and a['environment_transitions']<=b['environment_transitions'] and a['policy_updates']<=b['policy_updates']
milestones={}
for name in ('takeoff_count','landing_count','recovery_count'):
 first=next((i for i,r in enumerate(curves) if r['events'][name]>0),None)
 milestones[name]=dict(first_positive_curve_row_elapsed_s=(curves[first]['GO_elapsed_s'] if first is not None else None),previous_logged_zero_elapsed_s=(curves[first-1]['GO_elapsed_s'] if first is not None and first>0 else None),event_time_is_interval_censored_by_curve_frequency=True)
result=dict(epoch=time.time(),actual_closed_window=True,native_fullfinite_passed=native.get('passed_native_fullfinite_CPU',False),native_final=native.get('final'),actual_method_original_cost=proof['original_slots_cost']['e2'],curve_rows=curves,first_logged_event_time_brackets=milestones,original_H1_final_completed_control_events=native.get('original_H1_events'),source_actor_fresh128_history10_goal73_versus_pretrained_PPO35_not_matched=True,world_model_loss_not_step_success=True,success_requires_original_270mm_dualwheel_platform_contact_and200stable_callbacks=True,counts_are_stochastic_completed_controls_not_frozen_policy_success_rate=True,elapsed_includes_original_GO_initialization_and_warmup=True,no_PPO_speed_multiplier_or_graduation_claim=True)
with (R/'ACTUAL_NATIVE_H1_CLOSED_WINDOW_CONVERGENCE_TIME_AND_EVENTS_CPU_SUMMARY.json').open('x',encoding='utf8') as f:json.dump(result,f,indent=2)
print(json.dumps(dict(native_fullfinite=result['native_fullfinite_passed'],curve_rows=len(curves),events=result['original_H1_final_completed_control_events'],original_method_fee=result['actual_method_original_cost']['charged_seconds'])))
