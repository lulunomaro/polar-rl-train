"""Final review-only V2 proposal; preserve V1 overcap semantic rejection. No account IO."""
from pathlib import Path
import hashlib,json,time
import single_writer_handoff_contract_cpu_v2 as C

HERE=Path(__file__).resolve().parent

def meta(path):
    raw=path.read_bytes();return dict(path=str(path),bytes=len(raw),SHA256=hashlib.sha256(raw).hexdigest())

def put(path,value):
    with path.open("x",encoding="utf8") as f:json.dump(value,f,ensure_ascii=False,indent=2)

def main():
    proposal=C.proposal();C.validate_review(proposal)
    evidence=HERE/"LOCAL_83B_CLOSING_AND_LEDGER_BOUNDARY_EVIDENCE_V1.json"
    cpu=HERE/"SINGLE_WRITER_PROPOSAL_CPU_V2_1793011039546929600/CPU_PROPOSAL_REJECTION_TEST_RESULT_V2.json"
    proposal["evidence"]=[meta(evidence),meta(cpu)]
    proposal["root_latest_target_status"]=dict(two_source_SDK_native_CPU_and_valid_ready_reported_passed=True,
        finite_returned=True,owner_or_GO_started=False,basis="root explicit task message; helper did not query remote")
    proposal["historical_V1_semantic_rejection"]=dict(
        prior_CPU_report=str(HERE/"SINGLE_WRITER_PROPOSAL_CPU_1793010820775469200/CPU_PROPOSAL_REJECTION_TEST_RESULT.json"),
        original_status_preserved=True,rejection="overcap_actual_fee_refusal_wrong;actual_fee_must_sumonce_in_full_and_duration_flag_false",
        correction_CPU_tests=11,no_test_scope_expansion=True)
    proposal_path=HERE/"PROPOSED_SINGLE_WRITER72_AUTHORITY_HANDOFF_MANIFEST_V2.json";put(proposal_path,proposal)
    files=[]
    for p in sorted(HERE.rglob("*")):
        if p.is_file():files.append(dict(**meta(p),archive="index_only_regenerable_bytecode" if p.suffix==".pyc" else "include_source_report_proposal"))
    index=HERE/("HANDOFF_PROPOSAL_COMPLETE_ARCHIVE_INDEX_V2_"+str(time.time_ns())+".json")
    put(index,dict(schema="mod4.single_writer72.handoff_archive_index.v2",files=files,final_proposal=meta(proposal_path),
        final_CPU_report=meta(cpu),human_authorized=False,actual_account_or_authority_actions=False,
        all_V1_original_reports_rejections_and_corrections_preserved=True,index_itself_must_be_archived=True,
        frozen=True,git_archive_state="pending_root_archive"))
    print(json.dumps(dict(proposal=meta(proposal_path),CPU_report=meta(cpu),archive_index=meta(index),review=C.validate_review(proposal),
        human_authorized=False,canonical_created_or_copied=False)))

if __name__=="__main__":main()
