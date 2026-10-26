"""Emit ONLY local review proposal/evidence/index; no authority/controller/account IO."""
from pathlib import Path
import hashlib,json,time
import single_writer_handoff_contract_cpu_v1 as C

HERE=Path(__file__).resolve().parent;J=HERE.parent;T=J.parent


def meta(path):
    raw=path.read_bytes();return dict(path=str(path),bytes=len(raw),SHA256=hashlib.sha256(raw).hexdigest())


def put(path,value):
    with path.open("x",encoding="utf8") as f:json.dump(value,f,ensure_ascii=False,indent=2)


def main():
    r83=T/"H1_STEP270_THREE_EXPERTS_RESOURCE_V83B_20261026/reports"
    closed_path=r83/"THREE_EXPERT_CLOSED_SOURCE210_CANONICAL_COST_ACTUAL.json"
    cpu_path=r83/"THREE_EXPERT_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json"
    fresh_path=J/"reports/FRESH83B_CLOSED_DISK_BEFORE84_RETURNED_ACTUAL.json"
    stage_path=J/"reports/CURRENT_SINGLE4090_HUMAN_OFFLINE_DUAL72_STAGED_WORK_ORDER_ACTUAL.json"
    closed=json.loads(closed_path.read_text(encoding="utf8"));cpu=json.loads(cpu_path.read_text(encoding="utf8"));fresh=json.loads(fresh_path.read_text(encoding="utf8"))
    p=C.proposal();C.validate_review(p)
    segment=closed["original_segment"]
    evidence=dict(schema="mod4.single_writer72.local_evidence_boundary.v1",sources=[meta(x) for x in (closed_path,cpu_path,fresh_path,stage_path)],
      settled83B=dict(fee_seconds=str(cpu["actual_cost_sumonce"]),remaining_seconds=str(cpu["remaining_actual_snapshot"]),
        all_owner_nodes_children_actual_out=cpu["all_owner_nodes_children_actual_out"],
        original_canonical_cost_settled=cpu["original_canonical_cost_settled"],all_original_private_shared_locks_free=cpu["all_original_private_shared_locks_free"]),
      original_owner=dict(pid=segment["owner_parent_pid"],kind=segment["kind"],
        last_unique_run_id=C.LAST_SETTLED_RUN,owner_exit=closed["owner_exit"],
        terminal_rows=segment["actual_terminal_rows"],not_a_current_remote_process_query=True),
      last_fresh_before_Windows=fresh["hosts"]["210"],
      original_snapshot_SHA256=dict(value=C.ORIGINAL_SNAPSHOT_SHA,basis="root explicitly supplied fresh83B precheck receipt; full JSON bytes not recovered here"),
      local_complete_ledger_recovery=dict(latest_full_original_JSON_established=False,per_run_history_rebuilt=False,
        limited_filename_search_found_old_named_candidates=True,old_candidates_not_assumed_current=True,
        incomplete_subtree="rmuc2026_work/unpack_verify_4zomhj13 access denied during filename-only rg",further_search_stopped_on_root_instruction=True),
      saved_reader_attempts=[dict(kind="broad filename listing",result="output truncated; no completeness claim derived"),
        dict(kind="known owner source rg",result="one guessed h1 payload owner source path absent; other known text matches returned"),
        dict(kind="workspace JSON filenames via check_output",result="returncode2 from inaccessible unrelated subtree; exception preserved in tool output"),
        dict(kind="corrected filename-only subprocess.run",result="captured partial candidates and stderr; no assertion of global absence"),
        dict(kind="budget_extensions literal in three known report directories",result="no matches in those bounded directories; grant summary is not a ledger")],
      historical_Git_reference_policy="existing old Git commits/tags/evidence unchanged; no Git was run; no claim to restore missing history",
      original_canonical_not_copied_or_created=True,proposal_human_authorized=False,git_archive_state="pending_root_archive")
    assert evidence["settled83B"]["fee_seconds"]==C.SETTLED_83B and evidence["settled83B"]["remaining_seconds"]==C.OPENING_REMAINING
    evidence_path=HERE/"LOCAL_83B_CLOSING_AND_LEDGER_BOUNDARY_EVIDENCE_V1.json";put(evidence_path,evidence)
    p["evidence"]=[meta(evidence_path),meta(HERE/"SINGLE_WRITER_PROPOSAL_CPU_1793010820775469200/CPU_PROPOSAL_REJECTION_TEST_RESULT.json")]
    p["Git_history_reference_files"]=[str(J/"reports/ACTUAL_ORDINARY_V3_MIXED84_COLD_HANDOFF72_GIT_NOTE.md"),str(r83/"UNIQUE_STAGE_ARCHIVE_STARTED_ACTUAL.json")]
    proposal_path=HERE/"PROPOSED_SINGLE_WRITER72_AUTHORITY_HANDOFF_MANIFEST_V1.json";put(proposal_path,p)
    files=[]
    for path in sorted(HERE.rglob("*")):
        if path.is_file():files.append(dict(**meta(path),archive="index_only_bytecode" if path.suffix==".pyc" else "include_source_report_proposal"))
    index=HERE/("HANDOFF_PROPOSAL_COMPLETE_ARCHIVE_INDEX_"+str(time.time_ns())+".json")
    put(index,dict(schema="mod4.single_writer72.handoff_archive_index.v1",files=files,proposal=meta(proposal_path),
      human_authorized=False,actual_account_or_authority_actions=False,index_itself_must_be_archived=True,
      source_frozen=True,git_archive_state="pending_root_archive_not_claimed_recorded"))
    print(json.dumps(dict(proposal=meta(proposal_path),evidence=meta(evidence_path),archive_index=meta(index),
      review=C.validate_review(p),human_authorized=False,canonical_created_or_copied=False)))


if __name__=="__main__":main()
