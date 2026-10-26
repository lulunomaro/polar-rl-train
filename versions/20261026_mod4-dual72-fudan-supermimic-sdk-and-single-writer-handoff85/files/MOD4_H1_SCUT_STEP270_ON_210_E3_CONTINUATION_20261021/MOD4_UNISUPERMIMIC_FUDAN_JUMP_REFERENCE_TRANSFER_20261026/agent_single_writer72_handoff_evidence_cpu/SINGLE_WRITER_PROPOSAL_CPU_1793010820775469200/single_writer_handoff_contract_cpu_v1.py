"""Pure review/rejection contract. This module NEVER creates/writes any account.
No network/process/model/Git access; no controller or authority activation code.
"""
from copy import deepcopy
from decimal import Decimal
from pathlib import PurePosixPath

TOTAL="2268000"
EXTENSIONS=9
SETTLED_83B="10943.796510219574"
OPENING_CHARGED="1672743.1759386063"
OPENING_REMAINING="595256.8240613937"
WINDOWS_PENDING="9400.860692501068"
UNKNOWN_RESERVE="512"
SAFETY_RESERVE="64800"
SCOPE_CAP="11700"
STRICT_REQUIRED="86412.86069250107"
ORIGINAL_SNAPSHOT_SHA="fa47cf989898d9c771f35dcaa1e25330456694fda044502aaf82a5887b205bb1"
LAST_SETTLED_RUN="THREE4090_EXPERT_ORIGINAL_1792994651814636100"
NEW_ROOT="/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026"
NEW_ACCOUNT=NEW_ROOT+"/TRAINING_BUDGET_10H.json"
OLD_ACCOUNT="/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json"


class HandoffRejected(ValueError):pass
def require(value,message):
    if not value:raise HandoffRejected(message)


def proposal():
    """Reviewable proposal only. The returned data is NOT an activated canonical."""
    return dict(schema="mod4.single_writer72.handoff_proposal.v1",status="PROPOSED_NOT_EXECUTED_HUMAN_CONFIRMATION_REQUIRED",
      human_authorized=False,authority_activated=False,canonical_created_or_copied=False,
      migration_kind="new_authority_carry_forward_snapshot_not_byte_for_byte_ledger_migration",
      authority_generation="PROPOSED_MOD4_SINGLE_WRITER72_20261026",
      new_authority=dict(host="72",root=NEW_ROOT,canonical_path=NEW_ACCOUNT,
        owner_locks=[NEW_ROOT+"/canonical_owner.fcntl.lock",NEW_ROOT+"/all_experts_owner.fcntl.lock"],
        exactly_one_account_writer=True,existing_private_GPU_locks_retained=True,all_writers_must_use_this_generation=True),
      old_authority=dict(host="210",operating_system_reported_by_human="Windows_replaces_previous_Linux",
        original_Linux_canonical_path=OLD_ACCOUNT,retirement_proposed=True,retirement_effective=False,
        permanently_retire_old_Linux_authority_on_approval=True,allow_any_future_old_owner_writes=False,
        restored_old_disk_or_route_does_not_reauthorize_old_owner=True,
        no_active_or_owner_recovery_by_guess=True),
      carry_forward=dict(original_authorized_total_seconds=TOTAL,original_extension_count=EXTENSIONS,
        original_charged_seconds=OPENING_CHARGED,original_remaining_seconds=OPENING_REMAINING,
        settled83B_fee_seconds=SETTLED_83B,last_settled_run_id=LAST_SETTLED_RUN,
        last_original_canonical_snapshot_SHA256=ORIGINAL_SNAPSHOT_SHA,
        snapshot_hash_basis="root_supplied_fresh83B_precheck_receipt_not_a_current_Linux_poll",
        last_observed_active=None,last_observed_all_owner_children_out=True,
        old_run_history_reconstructed=False,full_original_canonical_bytes_available=False,
        immutable_old_Git_history_refs_retained=True,old_Git_history_rewritten=False,
        carry_forward_is_aggregate_boundary_not_recovered_per_run_history=True),
      holds=dict(Windows_pending_unsettled_seconds=WINDOWS_PENDING,unknown_pending_reserve_seconds=UNKNOWN_RESERVE,
        safety_headroom_seconds=SAFETY_RESERVE,existing_scope_parent_caps_total_seconds=SCOPE_CAP,
        strict_required_runway_seconds=STRICT_REQUIRED,original_parent_cap_each_seconds=3900,
        original_learning_block_each_seconds=3600,original_save_exit_headroom_each_seconds=300,
        not_refunded_not_forgiven_not_retroactively_charged_by_handoff=True),
      accounting=dict(new_authority_opening_is_exact_old_closing=True,budget_increase=False,new_extension=False,refund=False,
        backfilled_unobserved_history=False,unreconciled_pending_turned_into_charge=False,
        future_charge_contract="each_actual_expert_GO_to_received_terminal_interval_once; original receipts retained",
        idle_CPU_preparation_and_no_GO_are_not_training_fees=True,legacy83B_must_not_be_charged_again=True),
      activation_requirements=dict(explicit_human_confirmation=False,old_authority_retirement_declaration=False,
        unique_last_settled_run_and_no_active_receipt=True,both_new_owner_fcntl_locks_exclusive=False,
        all_original_source_code_paths_rebound_and_reject_old_generation=False,
        new_account_integrity_and_atomic_failclosed_protocol_reviewed=False,
        runtime_private_GPU_locks_physics_complete_save_and_task_admission_retained=True),
      failure_policy=dict(before_activation="leave_both_proposed_generation_and_new_account_inactive; no_old_writer_restart",
        on_unknown_active_or_duplicate_writer="reject; do_not_clear_active_or_guess_terminate",
        on_save_or_accounting_failure="preserve_original_receipts_and_partial_files; owner_safe_complete_save; no_refund_or_duplicate_charge",
        after_activation_old210_restored="old_authority_stays_retired; never_fall_back_to_its_file"),
      physical_and_training_boundary="existing2.5ms_TGS32_4_float32_native160k_reuse_2mm_perenv_reset_and_complete_save_guards_unchanged",
      not_a_new_Task_GO_or_model_copy_or_budget_grant=True)


def validate_review(p):
    require(p["migration_kind"]=="new_authority_carry_forward_snapshot_not_byte_for_byte_ledger_migration","cannot claim full original ledger migration")
    c=p["carry_forward"];a=p["accounting"];h=p["holds"];n=p["new_authority"];old=p["old_authority"]
    expected={"original_authorized_total_seconds":TOTAL,"original_extension_count":EXTENSIONS,"original_charged_seconds":OPENING_CHARGED,
              "original_remaining_seconds":OPENING_REMAINING,"settled83B_fee_seconds":SETTLED_83B,
              "last_original_canonical_snapshot_SHA256":ORIGINAL_SNAPSHOT_SHA,"last_settled_run_id":LAST_SETTLED_RUN}
    require(all(c[k]==v for k,v in expected.items()),"original budget/balance/lineage changed")
    require(Decimal(c["original_charged_seconds"])+Decimal(c["original_remaining_seconds"])==Decimal(TOTAL),"carry-forward aggregate identity broken")
    require(c["last_observed_active"] is None and c["last_observed_all_owner_children_out"],"unknown active or owner not out")
    require(not c["old_run_history_reconstructed"] and not c["full_original_canonical_bytes_available"],"history gap may not be fabricated")
    require(c["immutable_old_Git_history_refs_retained"] and not c["old_Git_history_rewritten"],"old Git evidence must be retained")
    require(not any(a[k] for k in ("budget_increase","new_extension","refund","backfilled_unobserved_history","unreconciled_pending_turned_into_charge")),"unauthorized grant/refund/history/pending mutation")
    require(n["host"]=="72" and n["root"]==NEW_ROOT and n["canonical_path"]==NEW_ACCOUNT,"new authority path changed")
    locks=n["owner_locks"];require(len(locks)==2 and len(set(locks))==2 and all(str(PurePosixPath(x).parent)==NEW_ROOT for x in locks),"both exclusive owner locks must be in the one72 authority root")
    require(n["exactly_one_account_writer"] and n["existing_private_GPU_locks_retained"],"second writer or missing private GPU protection")
    require(old["permanently_retire_old_Linux_authority_on_approval"] and not old["allow_any_future_old_owner_writes"],"old Linux authority must be permanently retired")
    require(old["restored_old_disk_or_route_does_not_reauthorize_old_owner"],"old-host recovery may not revive its writer")
    hold_expected={"Windows_pending_unsettled_seconds":WINDOWS_PENDING,"unknown_pending_reserve_seconds":UNKNOWN_RESERVE,
      "safety_headroom_seconds":SAFETY_RESERVE,"existing_scope_parent_caps_total_seconds":SCOPE_CAP,"strict_required_runway_seconds":STRICT_REQUIRED}
    require(all(h[k]==v for k,v in hold_expected.items()),"pending/safety/caps changed")
    require(h["original_parent_cap_each_seconds"]==3900 and h["original_learning_block_each_seconds"]==3600 and h["original_save_exit_headroom_each_seconds"]==300,"original interval caps changed")
    # Historical float receipt is retained as its original literal. Decimal sum
    # is explanatory only; this is not a newly imposed physical/precision gate.
    require(Decimal(c["original_remaining_seconds"])>Decimal(STRICT_REQUIRED),"insufficient original strict runway")
    require(not p["canonical_created_or_copied"] and not p["authority_activated"],"this artifact is a proposal, not an executed account")
    return dict(status="PASS_READ_ONLY_PROPOSAL_REVIEW",human_authorized=p["human_authorized"],activation_permitted=False,
                original_balance_preserved=OPENING_REMAINING,strict_required_preserved=STRICT_REQUIRED)


def validate_activation_request(p):
    validate_review(p)
    require(p["human_authorized"] and p["activation_requirements"]["explicit_human_confirmation"],"explicit human authority-transfer confirmation missing")
    require(p["old_authority"]["retirement_effective"] and p["activation_requirements"]["old_authority_retirement_declaration"],"old210 Linux authority retirement declaration missing")
    require(all(p["activation_requirements"].values()),"one-writer lock/source/integrity/admission proof incomplete")
    return dict(status="PRECONDITIONS_REVIEWED_IN_MEMORY_ONLY_NO_EXECUTION",does_not_create_any_account=True)


def charge_sum_once_candidate(records,already_settled_ids=()):
    """Pure CPU candidate for future receipt review. Never writes/extends a ledger."""
    seen=set(already_settled_ids);seen.add(LAST_SETTLED_RUN);total=Decimal(0)
    for row in records:
        key=row["interval_id"]
        require(key not in seen,"duplicate or already-settled interval")
        require(row.get("authority_generation")=="PROPOSED_MOD4_SINGLE_WRITER72_20261026" and row.get("post_cutover_new_interval") is True,
                "legacy or pre-cutover intervals may not be back-charged through this handoff")
        require(row.get("actual_GO") is True and row.get("actual_terminal_received") is True,"actual GO and terminal receipts required")
        start=Decimal(str(row["GO_epoch"]));end=Decimal(str(row["terminal_epoch"]))
        require(end>=start and end-start<=Decimal(3900),"invalid or over-cap GO-terminal interval")
        require(Decimal(str(row["charged_seconds"]))==end-start,"charge must equal the observed interval exactly once")
        total+=end-start;seen.add(key)
    return total
