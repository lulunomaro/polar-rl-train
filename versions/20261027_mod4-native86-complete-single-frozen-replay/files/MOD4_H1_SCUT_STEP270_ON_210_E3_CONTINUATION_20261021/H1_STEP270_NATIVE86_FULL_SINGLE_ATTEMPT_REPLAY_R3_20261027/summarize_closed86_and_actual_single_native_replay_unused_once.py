from pathlib import Path
import hashlib,json,time
S=Path(__file__).resolve().parent;T=S.parent;N=T/'H1_STEP270_THREE_GPU_NATIVE_CONTINUATION_RESOURCE_V86B_20261026';R=S/'reports'
def read(p):return json.loads(Path(p).read_bytes())
def main():
 cpu=read(N/'reports/THREE_GPU86B_TYPED_FINALS_AND_ORIGINAL_COST_CPU_ACTUAL.json');assert cpu['passed']
 collected=read(N/'reports/THREE_GPU86B_FINALS_AND_ORIGINAL_COST_RETURNED_ACTUAL.json');assert collected['all_three_node_collection_passed'] and collected['original_canonical_cost_settled']
 replay=read(R/'FROZEN_NATIVE86_SINGLE_COMPLETE_ATTEMPT_RETURNED_ACTUAL.json');video=read(R/'FULL_NATIVE86_SINGLE_ATTEMPT_VIDEO_CPU_ACTUAL.json')
 assert replay['actual_finite_returned'] and replay['all_own_children_actual_out'] and replay['actual_original_SDK_admission']['passed'] and replay['actual_result']['passed'] and not replay['original_error']
 status=replay['actual_result']['result'];assert status['controls']==54 and status['physics_frames']==216 and status['termination']=='actual_original_done'
 assert status['Pi_parameters_and_normalizers_literal_unchanged'] and not status['original_success'] and status['final_original_event_counts']==dict(takeoff_count=0,landing_count=0,recovery_count=0)
 models={k:dict(final=v['final'],updates=v['updates'],Adam=v['Adam']) for k,v in cpu['models'].items()}
 result=dict(schema='mod4.closed86_and_native_full_single_replay.actual.v1',epoch=time.time(),closed86_original_CPU_all_roles_passed=True,
  latest_qualified_normal_sources=models,latest_qualified_native_source=dict(final=cpu['native_method']['final'],progress=cpu['native_method']['native_progress'],separate_method_not_PPO_or_E2=True),
  normal_E2_latest83B_retained=cpu['normal_E2_83B_preserved_paused'],original_training_fees=cpu['original_fees'],all_original_normal_duration_flags_retained=True,
  full_completed86_native_events=cpu['native_method']['physical_original_H1_events'],full86_optional_phase_sampling=cpu['native_method']['optional_policy_phase_sampling'],
  root_conclusion='Initial firstPi scheduling defect is actually repaired and request-phase starts are present, but no original task events appeared in this complete stochastic training scope. Do not blame all failure on absent phase exposure or claim a convergence gain.',
  human_requested_full_replay=True,user_latest_policy_test_status=status,actual_native_policy_attempts=1,policy_action_mode='deterministic_native_mean',environment_seed=20260928,
  fresh_single_env_not_exact_training_trajectory=True,not_best_case_selection_or_frozen_success_rate=True,
  interpretation='One fresh latest-qualified native policy episode terminated at0.54s/54controls before the original request age100..179, with no takeoff/landing/recovery; visible chassis tilt is present, exact original termination term was not saved and is not invented.',
  video_geometry='Actual400Hz31body SDK poses with original authored collider geometry; complete recorded episode, not foreign Fudan footage, PPO actions or interpolated missing training trace.',
  artifacts=video['artifacts'],frozen_replay_evaluation_wall_seconds=replay['evaluation_wall_seconds'],canonical_bytes_unchanged=replay['actual_result']['canonical_bytes_unchanged'],no_optimizer_WM_normalizer_training_or_budget_write=True,
  startup_failures_preserved=[dict(namespace='R1',policy_forwards=0,error='Original common.environment SDK settings were omitted, causing an EULA startup EOF before AppLauncher/actor; same SDK, not a different backend'),dict(namespace='R2',policy_forwards=0,original_returncode=0,primary_error='Missing closed worker source root on sys.path; ModuleNotFound h1_step270_sdk_runtime_candidate; primary saved before app.close, rc0 not success')],
  source_helpers_all_frozen=True,at_most_one_future_agent=True,no_new_training87_or_blind_identical_window=True,
  remaining_repair='Assess learned balance before public request and the already confirmed missing-distance/frozen-imagination-context/objective gaps. Any new native continuation must admit complete86 continuation-extension lineage, not reuse the legacy85-only source guard. Retention candidate is source-only/unselected and cannot invent skill.',
  not_a_new_success_or_physical_gate=True,no_new_FP64_query_or_tolerance=True,
  sole72_finite_authority_unchanged=True,old210_authority_retired=True,
  Git_pending_unique_replay_stage='mod4-native86-complete-single-frozen-replay',protect_old_tag_objects_and_peels=1457,
  no_PT_or_raw_read_for_this_summary=True)
 with (R/'CURRENT_CLOSED86_AND_FULL_SINGLE_NATIVE_REPLAY_WORK_ORDER_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(result,f,ensure_ascii=False,indent=2)
 print(json.dumps(dict(closed86_CPU_passed=True,one_policy_attempt_complete=True,seconds=.54,events=status['final_original_event_counts'],native_policy_updates=127,success=False,artifacts=len(video['artifacts']))))
if __name__=='__main__':main()
