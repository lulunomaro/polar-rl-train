"""Create local source/CPU handoff pins and complete helper index. No Git/network."""
import hashlib
import json
from pathlib import Path
import time

A = Path(__file__).resolve().parent
J = A.parent
T = J.parent
N = T / "H1_STEP270_DUAL72_FUDAN_SUPERMIMIC_E3_MIGRATED_V85M2_20261026"
V1 = A / "SYNTHETIC_READER_CPU_V1_1793015564838"
V2 = A / "SYNTHETIC_READER_CPU_V2_1793015618782"


def pin(path):
    path = Path(path)
    raw = path.read_bytes()  # Only explicitly selected source/text, or this helper's own files.
    return dict(path=str(path), bytes=len(raw), SHA=hashlib.sha256(raw).hexdigest())


def write(name, value):
    path = A / name
    with path.open("x", encoding="utf8") as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
    return pin(path)


def main():
    source_paths = [
        N / "payloads/e2/source/h1_supermimic_bridge_v1.py",
        N / "payloads/e2/source/supermimic_vendor_v2/learner.py",
        N / "payloads/e2/source/native_finalization_v1.py",
        N / "payloads/e2/h1_lifetime_goal_counter_v1.py",
        N / "payloads/e2/h1_production_control_prefix_trace_v1.py",
        N / "payloads/e2/h1_unisupermimic_step270_worker_v1.py",
        N / "collect_V85M2_single72_finals_actual_cost_V2_UNUSED.py",
        N / "review_V85M2_single72_native_E3_CPU_V3_one_load_partial_receipt_UNUSED.py",
        N / "reports/CURRENT_ACTUAL_V85M2_FUDAN_NATIVE_FIRST_POLICY_FINITE72_AUTHORITY_AND_STORAGE_WORK_ORDER.json",
        N / "reports/V85M2_SINGLE72_GO_NATIVE_E3_UUID_ACTUAL.json",
        N / "reports/OLD210_AUTHORITY_FENCE_ACTUAL_RETURNED.json",
        N / "reports/SINGLE_RETURN72_FINITE_LIMITS_RESTORED_RETURNED_ACTUAL.json",
    ]
    lineage = [pin(p) if p.is_file() else dict(path=str(p), status="missing_not_fabricated") for p in source_paths]
    plan = dict(
        schema="next_three_GPU_typed_source_plan_v1", epoch=time.time(),
        status="SOURCE_ONLY_PENDING_ORIGINAL_CURRENT_PAIR_CLOSURE_AND_FUTURE_ADMISSION",
        implemented=False, deployed=False, next_GO_authorized_by_this_plan=False,
        current_run_id="DUAL72_MIGRATED_FUDAN_H1_E3_V85M2_1793012806095856700",
        current_logical_slots=dict(e2="native_Fudan_H1_not_normal_E2", recovery="normal_E3_PPO"),
        required_prior_state=["actual_current_pair_complete_save_and_terminal", "original_current_pair_cost_settled_once",
                              "current_owner_and_all_own_children_actual_out", "original_two_authority_locks_and_selected_private_GPU_locks_released",
                              "actual_next_source_fullstate_qualification", "actual_future_target_source_SDK_scope_and_named_order_as_applicable",
                              "fresh_single72_finite_admission_with_exact_source_GPU_manifest_pins"],
        authority=dict(generation="MOD4_SINGLE_WRITER72_20261026",
                       canonical="/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json",
                       mode="finite_restored", strict_minimum_remaining_seconds=86412.86069250107,
                       current_balance=None, current_balance_status="must_read_after_actual_pair_settlement_by_originalwriter",
                       old210_canonical="permanently_retired_tombstone_do_not_recreate",
                       owner_locks_and_private_GPU_locks_retained=True,
                       original_total_authorized_seconds=2268000, historical_extensions=9,
                       cap_each_seconds=3900, save_block_seconds=3600, exit_headroom_seconds=300,
                       three_slot_cap_sum_seconds=11700,
                       actual_GO_terminal_charge="sum_distinct_actual_duration_once_in_full_even_if_overcap_duration_bound_false",
                       no_refund_truncation_new_budget_or_history_reconstruction=True),
        resources=dict(single210=dict(original_mount_UUID="EF3105C85DD986BD", last_saved_rw=True,
                                      last_saved_free_bytes=716942045184, current_probe_not_performed=True)),
        slots=[dict(logical_role="normal_H1_PPO", host="original_single210", GPU_UUID=None,
                    GPU_identity_status="pending_future_actual_readback", source_kind="qualified_complete83B_production_H1",
                    source_update=130, source_Adam=829700,
                    source_SHA="8bb9869ac683550c1e7be1c9dffae9a5eac022e0de0fc8f251cd2005cfa6d4c6",
                    controller="forwarded_originalwriter_control72_required_no_new210_ledger",
                    policy_hz=100, physics_dt=.0025, decimation=4,
                    future_target_scope_status="pending_actual_source210_source_SDK_qualification",
                    native_WM_Pi_checkpoint_allowed_as_this_PPO_source=False),
               dict(logical_role="native_realFudan_H1", historical_logical_key="e2", host="dual72",
                    GPU_UUID="GPU-16828f91-2b45-b646-8dc0-9481138e2842",
                    source_kind="future_qualified_complete85M2_native_WM_Pi_Critic_optimizers",
                    source_SHA=None, source_status="pending_actual_close_complete_native_review_and_lineage_pins",
                    production_PPO_source=False, policy_hz=100, physics_dt=.0025, decimation=4,
                    reference_artifact_SHA="0b9d642f3530ad55bd353c19918a0778378746ecc250e1f22c10c58b8c095c94",
                    reference_change_implemented=False, foreign_transition_as_own_WM_data=False,
                    runtime_joint_order_before_learning_and_Pi_required=True),
               dict(logical_role="normal_E3_recovery_PPO", historical_logical_key="recovery", host="dual72",
                    GPU_UUID="GPU-c27eecbd-6838-7290-1cd2-37e34522213d",
                    source_kind="future_latest_qualified_completed_E3_production", source_SHA=None,
                    source_status="pending_actual85M2_closure_and_production_fullstate_qualification",
                    qualified_fallback=dict(kind="complete83B_production_E3", updates=83, Adam=860800,
                                            SHA="68d95156fc5dd294e43b21ad39691da8f1df1c5b85667db3001335796521ea49"),
                    policy_hz=50, physics_dt=.0025, decimation=8)],
        unchanged=dict(physics="2.5ms_TGS32_4", closed_chain="2mm_per_environment_reset",
                       native160k_query_evidence="reuse_same_source_qualified_evidence_no_extra_global_gate",
                       E0_W35="frozen_retained", physical_actionclip_PD_delay_DR_commands_success=True),
        not_admitted=["frozen_E2_source_CPU_candidate", "any_new_reference_or_reward_task", "PPO_source_from_native_checkpoint",
                      "new_ledger_or_old210_authority", "next_three_slot_GO_from_this_source_plan"],
        evidence_lineage=lineage)
    plan_pin = write("NEXT_THREE_GPU_SOURCE_ONLY_PLAN_V1.json", plan)
    report = json.loads((V2 / "result/CPU_PARSER_FIXTURE_RESULT.json").read_text("utf8"))
    assert report["passed"] and report["pass_count"] == report["test_count"] == 11
    manifest = dict(schema="closed85_native_curve_reader_source_CPU_handoff_v1", epoch=time.time(),
                    status="FROZEN_LOCAL_SOURCE_CPU_READY_ACTUAL_CLOSING_ANALYSIS_PENDING", actual_closed85_curve_read=False,
                    adapter_source=pin(A / "native_curve_text_reader_v1.py"),
                    test_source=pin(A / "test_native_curve_text_reader_v1.py"),
                    corrected_CPU_report=pin(V2 / "result/CPU_PARSER_FIXTURE_RESULT.json"),
                    prior_failed_CPU_report=pin(V1 / "result/CPU_PARSER_FIXTURE_RESULT.json"),
                    pending_actual_analysis=pin(V2 / "actual85_pending/NATIVE_CURVE_TEXT_ANALYSIS.json"),
                    synthetic_CLI_analysis=pin(V2 / "CLI_SYNTHETIC_NOT_ACTUAL85/NATIVE_CURVE_TEXT_ANALYSIS.json"),
                    planning=plan_pin, evidence_lineage=lineage,
                    corrected_test_count=11, corrected_pass_count=11, prior_attempt_pass_count=10,
                    local_errors_preserved=[
                        dict(kind="draft_schema_mismatch", result="10_of_11", cause="draft_ACTUAL_GO_basename_not_actual_job0_GO_PRODUCTION",
                             resolution="exact_actual_job0_GO_PRODUCTION_suffix_and_fixture_test", training_failure=False),
                        dict(kind="PowerShell_New_Item_LiteralPath_not_supported", attempt="SYNTHETIC_READER_CPU_V1_1793015564838",
                             source_snapshot_copy_initially_failed=True,
                             resolution="test_created_parent_then_original_unchanged_V1_sources_copied_before_edit",
                             full_original_error="New-Item: A parameter cannot be found that matches parameter name LiteralPath. Two Copy-Item destinations absent as a consequence.",
                             training_failure=False),
                        dict(kind="source_read_lookup_missing_file", requested="payloads/e2/source/native_training_finalization_v1.py",
                             resolution="rg located and read actual native_finalization_v1.py", training_failure=False)],
                    actual_validation_pending=["root_original_closing_collector_return", "actual_collected_text_analysis",
                                               "independent_native_and_E3_fullstate_qualification", "future_next_three_slot_admission"],
                    forbidden_operations_performed=False, frozen_previous_directories_edited=False,
                    Git_status="PENDING_ROOT_ORDINARY85_SUPPLEMENT_NO_HELPER_GIT_ACTION")
    manifest_pin = write("CLOSED85_NATIVE_CURVE_SOURCE_CPU_HANDOFF_MANIFEST_V1.json", manifest)
    index = dict(schema="complete_helper_archive_index_v1", epoch=time.time(),
                 root=str(A), status="PENDING_ROOT_ORDINARY85_SUPPLEMENT", manifest=manifest_pin,
                 includes_failed_source_snapshots_fixtures_errors_and_corrected_reports=True,
                 files=[pin(p) for p in sorted(A.rglob("*")) if p.is_file()],
                 index_excludes_itself=True, no_model_raw_GPU_remote_Git_or_budget_action=True)
    index_pin = write("CLOSED85_COMPLETE_ARCHIVE_INDEX_V1.json", index)
    print(json.dumps(dict(manifest=manifest_pin, index=index_pin, planning=plan_pin, tests="11/11")))


if __name__ == "__main__":
    main()
