"""One-shot NEW source-only flat input/index and SHA receipts. No real stage/dispatch."""
import ast
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import stage_a1_native_v5 as stage
import test_stage_dispatch_stdlib_v5 as tests


def main():
    # These are fourteen exact, pinned small .py files. Not static native roles or models.
    flat=HERE/'_SOURCE_INPUT'
    if flat.exists():raise RuntimeError('one-shot source input already exists')
    rows=[];sources=[]
    mapping=tests.actual_fourteen_sources()
    assert len(mapping)==14 and set(mapping)==set(stage.FIXED_PINS)
    assert all(stage.is_sha(pin)for pin in stage.FIXED_PINS.values())
    for install,path in sorted(mapping.items()):
        raw=path.read_bytes();digest=stage.sha_bytes(raw)
        assert digest==stage.FIXED_PINS[install],install
        relative='sealed_source/'+path.name
        stage.write_bytes_once(flat/relative,raw)
        rows.append(dict(source_relative=relative,install_relative=install,SHA=digest,bytes=len(raw)))
        sources.append(dict(path=str(path),SHA=digest,bytes=len(raw)))
    index=dict(kind=stage.SOURCE_INDEX_KIND,sealed=True,v5_code_seal_SHA=stage.V5_CODE_SEAL_SHA,files=rows,
        description='14 verified small sources only; parent may upload this sibling input pack; no actual native staging or PT')
    stage.put_once(flat/'SEALED_A1_SOURCE_INDEX_V5.json',index)
    # Actual complete mapping/alias/ownerAST validation, NOT prepare()/stage()/dispatch().
    resolved=stage.source_index_files(flat,index)
    assert resolved['worker_sources/ctx_reward_learner.py'][1]==resolved['worker_sources/ctx_reward_full_resume_candidate_v2.py'][1]
    old27=json.loads((HERE/'TEST_RESULTS_STDLIB_STAGE_DISPATCH_V5.json').read_bytes())
    final29=json.loads((HERE/'TEST_RESULTS_STDLIB_STAGE_DISPATCH_RECHECK_V5.json').read_bytes())
    assert old27['passed']and old27['tests_run']==27 and final29['passed']and final29['tests_run']==29
    artifacts=[]
    names=['stage_a1_native_v5.py','dispatch_a1_native_v5_once.py','test_stage_dispatch_stdlib_v5.py',
        'SOURCE_INDEX_SCHEMA_AND_CLI_V5.md','TEST_RESULTS_STDLIB_STAGE_DISPATCH_V5.json',
        'TEST_RESULTS_STDLIB_STAGE_DISPATCH_RECHECK_V5.json','seal_stage_sources_v5.py']
    for name in names:
        path=HERE/name;raw=path.read_bytes()
        if path.suffix=='.py':ast.parse(raw.decode());compile(raw,str(path),'exec')
        artifacts.append(dict(relative=name,SHA=stage.sha_bytes(raw),bytes=len(raw)))
    stage.put_once(HERE/'STAGE_SOURCE_PROVENANCE_V5.json',dict(kind='SOURCE_ONLY_A1_STAGE_DISPATCH_FINAL_SEAL_V5',
        passed=True,fixed_pin_length_all64=True,actual_fixed_source_matches=14,source_index_full_mapping_verified=True,
        source_index_installed_alias_count=len(resolved),v5_code_seal_SHA=stage.V5_CODE_SEAL_SHA,
        original_shared_owner_protected_AST_SHA=stage.OWNER_PROTECTED_AST_SHA,original_shared_owner_main_normalized_AST_SHA=stage.OWNER_NORMALIZED_MAIN_AST_SHA,
        tests_distinct=29,previous27_are_subset_not_added=True,artifacts=artifacts,read_only_original_sources=sources,
        ready_input_relative='_SOURCE_INPUT/SEALED_A1_SOURCE_INDEX_V5.json',real_stage_calls=0,real_dispatch_Popen=0,
        actual_C_locks_originalPT_SDK_GPU_Git_SSH_operations=0,Torch_imported='torch'in sys.modules,
        notes='local synthetic fixture tests only; source-index verifies actual 14 pinned small files; runtime role/static assets and admission remain parent-owned'))
    lines=['%s  %s'%(row['SHA'],row['relative'])for row in artifacts]
    lines+=['%s  _SOURCE_INPUT/%s'%(row['SHA'],row['source_relative'])for row in rows]
    info=stage.identity(flat/'SEALED_A1_SOURCE_INDEX_V5.json');lines+=['%s  _SOURCE_INPUT/SEALED_A1_SOURCE_INDEX_V5.json'%info['SHA']]
    stage.write_bytes_once(HERE/'SHA256SUMS_STAGE_V5.txt',('\n'.join(lines)+'\n').encode())
    print(json.dumps(dict(passed=True,tests=29,actual_pinned_small_sources=14,real_stage_dispatch=0,artifacts=artifacts),indent=2))


if __name__=='__main__':main()
