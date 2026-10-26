"""Index all helper-owned source/attempts/errors/reports for root's Git stage.
No Git commands or external/original model/raw hashes are performed.
"""
from pathlib import Path
import hashlib,json,time

HERE=Path(__file__).resolve().parent


def main():
    files=[]
    for path in sorted(HERE.rglob("*")):
        if not path.is_file():continue
        relative=str(path.relative_to(HERE)).replace("\\","/")
        data=path.read_bytes()
        kind="report_or_schema" if path.suffix in (".json",".jsonl",".md") else "source" if path.suffix==".py" else "figure" if path.suffix==".png" else "regenerable_bytecode" if path.suffix==".pyc" else "other_helper_artifact"
        files.append(dict(path=str(path),relative_path=relative,bytes=len(data),SHA256=hashlib.sha256(data).hexdigest(),kind=kind,
            archive_recommendation="source_report_or_small_artifact_must_be_in_root_stage" if kind!="regenerable_bytecode" else "index_only_regenerable_bytecode_not_a_saved_report"))
    report_paths=[str(p) for p in HERE.rglob("*.json") if "source_snapshot" not in str(p.relative_to(HERE))]
    adapter=HERE/"supermimic_reference_adapter_v1.py"
    final_adapter_sha=hashlib.sha256(adapter.read_bytes()).hexdigest()
    assert final_adapter_sha=="0994762dbf8a78a0f44db03ac91796963e6be9fcd177e8ceecd5159748c8f476","frozen integration source changed"
    value=dict(schema="mod4.helper.complete_attempt_report_index.v1",epoch=time.time(),root=str(HERE),
        scope="source_CPU_static_reference_helper_only",files=files,
        final_adapter_SHA256=final_adapter_sha,
        final_native_reference_relative="ACTUAL_PARTIAL_STEP270_PHASE_V3_1793006590678125700/H1_PARTIAL_JUMP_NATIVE_REFERENCE_PACKED73_PHASE_V3.json",
        final_actual_CPU_proof_relative="ACTUAL_PARTIAL_H1_OBJECTIVE_CPU_PROOF_V3_1793006856598755100/ACTUAL_REFERENCE_H1_MDP_CPU_PROOF_RESULT.json",
        final_handoff_relative="FINAL_H1_REFERENCE_RETARGET_CPU_HANDOFF_V3.md",
        all_saved_json_report_paths=report_paths,
        original_rejected_direct_retarget="111_of201_fit_90_rejected_preserved_no_native_export",
        constrained_reference="261_of261_static_fits_no_dynamic_or_skill_success_claim",
        original_actual_CPU_clock_reader_error="preserved_then_uniform_control_indexing_repair_verified",
        source_preservation_reader_errors="original_exact_SHA_rejection_and_shell_quote_SyntaxError_preserved; exact_source_recovery_receipt_present",
        original_source_NPZs=[dict(case="upstream_actual_default_dt_standing_jump",bytes=1991407,
             SHA256_from_root_verified_receipt="9461c534056357da479de2b9d63ea7def8299f1b59d954133ad27af92e92750f"),
            dict(case="declared_5ms_dt_standing_jump",bytes=833106,SHA256_from_root_verified_receipt="53120107dd0a4f7b2a459a7097fd6275e6fecc12a5ef7c70ce1016dc5ce19994"),
            dict(case="declared_5ms_dt_jump_forward_command",bytes=819726,SHA256_from_root_verified_receipt="ec66c3c44bdbee6a914d44877e6a83d31528770789f9ca4d8c1aeed3d997f64d")],
        original_models_weights_old_raw_USD_NPZ_hashes_not_computed_by_this_helper=True,
        root_Git_recording_required=True,git_archive_state="pending_root_stage_archive_not_claimed_recorded",
        index_self_hash_policy="root must include this new index itself in stage; self SHA printed to root to avoid recursive index mutation",
        no_model_actor_optimizer_RNG_plant_GPU_network_Git_budget_or_lock_writes=True)
    path=HERE/("HELPER_COMPLETE_ARCHIVE_INDEX_"+str(time.time_ns())+".json")
    with path.open("x",encoding="utf8") as stream:json.dump(value,stream,ensure_ascii=False,indent=2)
    print(json.dumps(dict(index=str(path),bytes=path.stat().st_size,SHA256=hashlib.sha256(path.read_bytes()).hexdigest(),
        files=len(files),reports=len(report_paths),total_helper_bytes=sum(x["bytes"] for x in files),
        adapter_SHA256=final_adapter_sha,git_archive_state=value["git_archive_state"])))


if __name__=="__main__":main()
