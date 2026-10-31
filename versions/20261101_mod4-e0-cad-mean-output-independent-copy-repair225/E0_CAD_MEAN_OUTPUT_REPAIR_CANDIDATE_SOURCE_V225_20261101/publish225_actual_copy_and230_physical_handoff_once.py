from pathlib import Path
import json,time
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports'
def read(p):return json.loads(p.read_bytes())
copy=read(R/'ROOT225_ACTUAL_BOUND_COPY_AND_OWN_READBACK_CPU_RETURNED_ACTUAL.json')
P=T/'E0_CANDIDATE225_CONTROLLED_PHYSICAL_REGRESSION_V230_20261101/reports'
parent=read(P/'ROOT230_ORIGINAL_N1_PARENT_CASE_OR_ERROR_RETURNED_ACTUAL.json')
free=read(P/'ROOT230_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json')
assert copy['passed'] and parent['passed_execution'] and free['global_serial_control_client_lease']=='FREE'
case=parent['original_parent']['result'];summary=[]
for x in case['cases']:
 f=x['endpoint_flight']
 summary.append({k:x[k]for k in('name','command','controls','seconds','requested_window_complete','first_episode_original_terminal_flags','BODY_vx_MAE','BODY_vx_mean','yaw_delta_rad','raw_left_crank_range','raw_abs_gt6_count_by_channel','producer')}|dict(
  endpoint_flight_status=f['status'],bilateral_above5mm_low_force_runs=len(f['confirmed_runs']),candidate_rows=f['candidate_rows'],geometry_known_rows=f['geometry_known_rows'],
  confirmed_run_50Hz_endpoints=[r['consecutive_50Hz_endpoints']for r in f['confirmed_runs']],
  candidate_rows_with_original_penalised_nonwheel_force_gt1N=len(f['wheel_evidence_with_nonwheel_force_gt1N_rows']),
  flight_scope='50Hz endpoints:both wheel authored bottoms>5mm AND already-read force norms<=1N for>=2endpoints. Not continuous400Hz/full-body-air/stable landing/270.',
  yaw_scope='Wrapped first-to-final root heading difference, not total turns or unwrapped angular travel.'))
out=dict(epoch=time.time(),kind='ACTUAL225_BOUND_COPY_AND230_FOUR_ORIGINAL_GUARD_PHYSICAL_REGRESSIONS',
 candidate=copy['candidate'],parent_source=copy['parent_input'],actual_repair_copy=True,latest_learned_policy_promoted=False,
 original_frozen_E0_untouched=True,copy_changes='Left crank output row/bias, scalarSTD and corresponding Adam moment rows only;actual SDK CAD/action mapping and17parameter identity bound. Other5 rows/trunk/critic/all17steps/LR unchanged.',
 CPU=dict(finite_tensors=259,conditional_same_input32_original_mean_target_residual=0.,iteration=32341,Adam17=648340,STD_left=copy['candidate_left_STD'],model_physical_regression_not_inferred_from_CPU=True),
 physical230=dict(passed_execution=True,controls=case['controls'],physics_callbacks=case['physics_callbacks'],feedback=case['feedback_samples'],cases=summary,
  wait=parent['original_parent']['wait'],all_SSH_closed=free,one_candidate_GPU_byte_read_decode=True,model_uploads=1,target_postcopy_integrity_reads=1,
  original_frozen_or_unrepaired_model_writes=0,training_or_optimizer_or_account_writes=0,NPZ_default_metadata_only=True,GUI=False),
 decision='Candidate removed persistent left mean clamp in these short ground cases and showed wheel-air endpoints in controlled literalJUMP. Heading drift and jump tracking error remain;do not claim complete repair/stable jump or automatically repeat a three-hour window.',
 remaining=dict(full_original20s20k_ground_regression='NOT_RUN',same_history_unrepaired_vs_repaired_paired_cause_test='NOT_RUN',stochastic_sampling_or_training_update='NOT_RUN',stable_full_body_landing='NOT_PROVEN',true270=False,full_SuperMimic=False),
 consumed_purposes=['225 source read/save/readback CPU','228 original metadata error','228V2 actual mapping with wrapper-origin guardFalse','229 original_process closure proof','230 four first episodes and one candidate upload/GPUread'],
 next_W35='227A/B/C frozen;C has before-use owner/node cwd mismatch to actual219V3. Same authorized child preparing separate227D;ROOT must use D only after actual source gate and freshCNone/resources. No W35 new GO yet.',
 current_learning=False,old219_active_binding='HISTORICAL',all_new_remote_requires_fresh_CNone_or_actual_new_owner_run_GO=True)
p=R/'CURRENT_ACTUAL225_COPY_230_BILATERAL_WHEEL_AIR_AND_REMAINING_HEADING_WORK_ORDER.json'
assert not p.exists();p.write_text(json.dumps(out,indent=2,ensure_ascii=False,allow_nan=False),encoding='utf8')
print(json.dumps(dict(passed=True,path=str(p),bilateral_wheel_air_runs=summary[-1]['bilateral_above5mm_low_force_runs'],all_four_short_original_guard_windows=True,not_stable_jump_or270=True)))
