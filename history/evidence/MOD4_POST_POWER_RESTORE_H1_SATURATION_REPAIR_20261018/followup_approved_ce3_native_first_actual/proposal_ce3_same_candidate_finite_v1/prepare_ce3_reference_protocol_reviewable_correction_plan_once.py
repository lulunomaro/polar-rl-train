"""Concrete protocol choice for the same approved but never-started paid segment."""
from pathlib import Path
import json,time,hashlib
B=Path(__file__).resolve().parent;R=B/'reports';TOP=B.parent;H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
 grant=json.loads((R/'HUMAN_EXPLICIT_CE3_SINGLE_FINITE_APPROVAL_ACTUAL.json').read_bytes());close=json.loads((R/'CE3_NATIVE_REJECTED_ZERO_GO_COST_ACTUAL_EXIT_FCNTL_HANDBACK_ACTUAL.json').read_bytes());fp32=json.loads((R/'CE3_ORIGINAL_FP32_FORMAL_NATIVE_ALL_ROWS_CPU_SAME_BOUND_ACTUAL.json').read_bytes());fp64=json.loads((R/'CE3_EXISTING_NATIVE_STRICT_ACTOR_FALSE_ALL_ROWS_CPU_DIAGNOSTIC_ACTUAL.json').read_bytes());assert grant['explicit_human_grant_received'] and close['new_paid_cost_seconds']==0 and close['original_canonicalNone_two_real_fcntl_and_target_private_shared_free'];assert fp32['original_FP32_formal_allrow_CPU']['passed'] and not fp64['report']['strict_actor_reference_pass']
 out=dict(epoch=time.time(),review_id='ce3-native-original-fp32-reference-protocol-correction-same-unstarted-approved-segment',
  actual_human_one_finite_training_grant_already_received=True,old_grant_receipt=dict(path=str(R/'HUMAN_EXPLICIT_CE3_SINGLE_FINITE_APPROVAL_ACTUAL.json'),SHA=H(R/'HUMAN_EXPLICIT_CE3_SINGLE_FINITE_APPROVAL_ACTUAL.json')),
  source_SHA=grant['source_SHA'],source_Adam=646100,source_owned_updates=24,actual_new_native180_720_3p6Mpolicy14p4Mphysical_complete=True,
  original_prepared_dual_FP64_admission_rejected_max=fp64['report']['all_saved_actor_CPUmean_maxabs'],dual_FP64_references_cross_max=fp64['report']['dual_FP64_cross_maxabs'],
  exact_original_formal_H1_FP32_allrow_reader_passed=True,original_FP32_same_absolute1e4_max=fp32['original_FP32_formal_allrow_CPU']['all_saved_actor_CPUmean_maxabs'],
  all_original_source_phase_query_contact_COM_geometry_hardware_checks_passed=True,
  original_FP64_false_reports_retained_without_relabel=True,all_two_native_models199tensor105float_finite_source9STD8critic17Adam_exact=True,
  proposed_change_only='Restore the original formal H1 native FP32 actor reference implementation at the unchanged absolute1e-4 bound. Do not change model/GPU runtime/optimizer/STD/LR/reward/physics/DR/commands/action-CAD bounds or other guards. Do not claim FP64 passed. This protocol choice is separate from the already approved one paid finite segment.',
  reviewable_exact_reader=dict(path=str(B/'review_ce3_native_original_FP32_reference_allrows_CPU_once.py'),SHA=H(B/'review_ce3_native_original_FP32_reference_allrows_CPU_once.py')),
  actual_report=dict(path=str(R/'CE3_ORIGINAL_FP32_FORMAL_NATIVE_ALL_ROWS_CPU_SAME_BOUND_ACTUAL.json'),SHA=H(R/'CE3_ORIGINAL_FP32_FORMAL_NATIVE_ALL_ROWS_CPU_SAME_BOUND_ACTUAL.json')),
  all_prior_owner_node_CPU_children_actual_out=True,new_GO0_paid_cost0_original_remaining_unchanged=close['original_remaining_unchanged_snapshot'],original_and_target_locks_actual_free=True,
  pending_protocol_question_not_another_budget_or_training_grant=True,protocol_change_approved=False,
  after_explicit_protocol_choice_only='If restore-original-FP32 is approved: consume the completed same-source/backend/GPU native and original full-allrow CPU report with fresh bound CPU/reuse negatives, actual old native and failed node original owner out/cost0/canonicalNone/two realfcntl/private/shared free/current SDK+resources. Then only the already approved ONE1800/300/max24/free8GiB/start25GiB finite production chain in a new unused namespace; no native replay or following paid window. If original FP64 is retained: no PPO and preserve pending diagnostic state.',
  native_task_and_old_failed_node_not_retroactively_passed=True,new_safe_handoff_deployer_not_created_or_dispatched_yet=True,
  no_new_GPU_case_or_raw_PT_download_for_hash_or_budget_mutation=True)
 p=TOP/'NEXT_CE3_NATIVE_REFERENCE_MISMATCH_ORIGINAL_FP32_REVIEWABLE_ZERO_GO_V9_WORK_ORDER.json'
 with p.open('x',encoding='utf8') as f:json.dump(out,f,indent=2)
 print(json.dumps(dict(reviewable_protocol_choice_ready=True,existing_paid_grant_not_reasked=True,no_GO_cost0=True)))

if __name__=='__main__':main()
