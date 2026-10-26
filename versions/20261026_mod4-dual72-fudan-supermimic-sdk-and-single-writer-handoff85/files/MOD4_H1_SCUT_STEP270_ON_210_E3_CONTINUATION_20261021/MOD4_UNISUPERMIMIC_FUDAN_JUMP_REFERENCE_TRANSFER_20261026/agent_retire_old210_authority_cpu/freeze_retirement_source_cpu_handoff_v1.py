"""Freeze local source/CPU evidence and invocation schema. No production execution."""
from pathlib import Path
import ast,hashlib,json,time
import retire_old210_authority_core_v1 as C

HERE=Path(__file__).resolve().parent;T=HERE.parent.parent
SOURCE=T/"H1_STEP270_THREE_EXPERTS_RESOURCE_V83B_20261026/payloads/h1"
AUTH=T/"H1_STEP270_DUAL72_FUDAN_SUPERMIMIC_E3_MIGRATED_V85M_20261026/reports/HUMAN_SINGLE_WRITER72_TEMPORARY_UNLIMITED_AUTHORIZATION_ACTUAL.json"

def meta(path):
    raw=path.read_bytes();return dict(path=str(path),bytes=len(raw),SHA256=C.sha(raw))
def put(path,value):
    with path.open("x",encoding="utf8") as f:json.dump(value,f,ensure_ascii=False,indent=2)

def main():
    C.validate_authorization(AUTH.read_bytes())
    proof=[];tomb=C.tombstone(Path(C.OLD_C),C.history_path(C.OLD_C),epoch=0)
    owner_path=SOURCE/"three_slot_finite_owner_v1.py";tree=ast.parse(owner_path.read_text(encoding="utf8"))
    # Exact pre-GO admission If, not the later account() field access.
    node=next(n for n in ast.walk(tree) if isinstance(n,ast.If) and isinstance(n.test,ast.Compare)
        and isinstance(n.test.left,ast.Subscript) and isinstance(n.test.left.value,ast.Name) and n.test.left.value.id=="c"
        and isinstance(n.test.left.slice,ast.Constant) and n.test.left.slice.value=="active_segment")
    try:eval(compile(ast.fix_missing_locations(ast.Expression(node.test)),str(owner_path),"eval"),{"c":tomb})
    except KeyError as error:proof.append(dict(source=meta(owner_path),exact_admission_expression=ast.unparse(node.test),line=node.lineno,
                                             tombstone_rejection=type(error).__name__,no_owner_or_network_execution=True))
    else:raise AssertionError("old exact admission expression unexpectedly accepted tombstone")
    cpu=HERE/"OLD210_RETIREMENT_CPU_1793013841964394900/OLD210_RETIREMENT_CPU_RESULT.json"
    core=HERE/"retire_old210_authority_core_v1.py";executor=HERE/"retire_old210_authority_local_executor_v1.py"
    manifest=dict(schema="mod4.old210_authority_retirement.source_CPU_handoff.v1",status="SOURCE_CPU_READY_NOT_EXECUTED_ROOT_SERIAL_ONLY",
      source_files=[meta(core),meta(executor)],CPU_report=meta(cpu),human_authorization=meta(AUTH),old_C=C.OLD_C,
      expected_old_C_SHA256=C.SOURCE_SHA,expected_remaining=C.REMAINING,expected_total=C.TOTAL,expected_extensions=9,
      expected_active_segment=None,old_original_fcntl_paths=list(C.OLD_LOCKS),
      history_path=str(C.history_path(C.OLD_C)),new72_canonical_data_reference_only=C.NEW_C,new72_generation=C.GENERATION,
      source_process_scope=dict(owner_pid=C.OWNER_PID,owner_creation=C.OWNER_CREATION,source_node_pid=C.OLD_SOURCE_NODE_PID,source_worker_pid=C.OLD_SOURCE_WORKER_PID,
                                other_old_cohort_children_use_existing83B_terminal_receipt_no_72_query=True),
      actual_old_owner_preGO_admission_rejection=proof,
      old_budget_validator=meta(SOURCE/"job0/runtime/isaac/mod4/budget_authority.py"),
      CODE="retire_old210_authority_local_executor_v1.py",
      args_schema=dict(authorization_file="required path;raw SHA must equal "+C.AUTH_SHA,
                       serial_clearance_file="required mod4.root.serial_source210_retirement_clearance.v1",
                       execute="explicit flag required for any rename/tombstone;absent=dry review"),
      no_path_or_SHA_override_arguments=True,no_network_no_GPU_no_new72_account_IO=True,
      actual_source_fcntl_current_process_and_renameat2_not_executed_by_helper=True,
      root_latest_first_observer_returned=True,root_latest_live72_owner_pid_reference=477414,
      live72_finite_mode_already_restored_not_read_or_changed_here=True,
      original_bytes_retained_by_no_replace_rename_no_copy_no_refund=True,
      frozen=True,git_archive_state="pending_root_archive_after_actual_serial_fence")
    path=HERE/"OLD210_AUTHORITY_RETIREMENT_SOURCE_CPU_HANDOFF_MANIFEST_V1.json";put(path,manifest)
    files=[]
    for p in sorted(HERE.rglob("*")):
        if p.is_file():files.append(dict(**meta(p),archive="index_only_regenerable_bytecode" if p.suffix==".pyc" else "include_source_report_or_synthetic_fault_fixture"))
    index=HERE/("OLD210_RETIREMENT_COMPLETE_ARCHIVE_INDEX_"+str(time.time_ns())+".json")
    put(index,dict(schema="mod4.old210_retirement.complete_CPU_archive_index.v1",files=files,manifest=meta(path),index_itself_must_be_archived=True,
                   production_old_canonical_untouched_by_helper=True,no_remote_activity=True,frozen=True,git_archive_state="pending_root_archive"))
    print(json.dumps(dict(manifest=meta(path),core=meta(core),executor=meta(executor),CPU_report=meta(cpu),archive_index=meta(index))))

if __name__=="__main__":main()
