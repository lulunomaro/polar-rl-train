"""Build/verify only NEW source index, exact AST whitelist and immutable seal.
No materializer, native input preflight, parent, worker or resource API is invoked.
"""
from pathlib import Path
import argparse
import ast
import hashlib
import json

HERE=Path(__file__).resolve().parent
R=HERE.parent
OLD=R/'source_frozen_embedded_teacher_native_v1/stage_embedded_teacher_native_v1.py'
UPSTREAM=R/'source_good_expert_holdout_subset_v1'
INDEX_NAME='SOURCE_STAGE_GOOD_EXPERT_INDEX_V1.json'
DIFF_NAME='WHITELIST_DIFF_STAGE_GOOD_EXPERT_V1.json'
SEAL_NAME='SOURCE_STAGE_GOOD_EXPERT_SEAL_V1.json'
FILES=('derive_stage_source_v1.py','stage_good_expert_holdout_v1.py','test_stage_good_expert_stdlib_v1.py',
       'build_stage_source_manifest_v1.py','SOURCE_STAGE_GOOD_EXPERT_GUIDE_V1.md','TEST_REPORT_STAGE_GOOD_EXPERT_V1.json',DIFF_NAME)
CHANGES={
 'source_mappings':'old16→sealed holdout20 flat basename mappings; exact index/each source pin; no provenance-path reads',
 'paired_plan':'explicit allowed independent seed20260929/20260930; original pose/physical conditions unchanged',
 'prepare':'original closure+all worker_files; only selected2 complete static runtimes; full8 deferred6/H1 absent; fullvendor7; actual0 producer guard; source-only flags',
 'metadata_validate':'full actual safe metadata closure imports, AppV6→Base, make_task+crossseed/history negatives; no native layer import or physical model/FD/resource operation',
 'preflight_summary':'new kind/seed/purpose/selected tree metadata; absent root not created; no new admission/evaluation claim',
 'stage':'future whole-material streaming copy and one-use error root; fixed complete filename; materialized flag with source_native_enabled/staged/dispatched false; no process',
 'main':'new CLI explicit seed and mutually exclusive preflight-only/stage; no auto mode, enable or dispatch',
}


def H(raw):return hashlib.sha256(raw).hexdigest()

def entry(path):
    raw=path.read_bytes()
    if path.suffix=='.py':ast.parse(raw)
    assert path.suffix in ('.py','.md','.json')
    return dict(name=path.name,bytes=len(raw),SHA256=H(raw))

def encoded(value):return (json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode()

def put_once(path,value):
    raw=encoded(value)
    if path.exists():assert path.read_bytes()==raw, 'existing source metadata differs: '+path.name
    else:
        with path.open('xb') as stream:stream.write(raw)


def whitelist():
    before_raw=OLD.read_bytes();after_path=HERE/'stage_good_expert_holdout_v1.py';after_raw=after_path.read_bytes()
    def functions(raw):return {n.name:n for n in ast.parse(raw).body if isinstance(n,ast.FunctionDef)}
    before,after=functions(before_raw),functions(after_raw)
    assert set(before)==set(after), 'unlisted helper additions/removals'
    rows=[];changed=set()
    for name in sorted(before):
        left,right=ast.dump(before[name],include_attributes=False),ast.dump(after[name],include_attributes=False)
        same=left==right
        if not same:changed.add(name)
        rows.append(dict(function=name,unchanged_full_AST=same,old_AST_SHA256=H(left.encode()),new_AST_SHA256=H(right.encode()),
            old_lines=[before[name].lineno,before[name].end_lineno],new_lines=[after[name].lineno,after[name].end_lineno],
            reason=CHANGES.get(name,'exact entire original helper AST preserved')))
    assert changed==set(CHANGES), 'AST change whitelist differs'
    return dict(kind='EXACT_WHOLE_FUNCTION_AST_WHITELIST_GOOD_EXPERT_STAGE_V1',
        original_source=dict(path=str(OLD),bytes=len(before_raw),SHA256=H(before_raw)),
        new_source=dict(path=str(after_path),bytes=len(after_raw),SHA256=H(after_raw)),
        changed_functions=sorted(changed),unchanged_helper_count=len(before)-len(changed),functions=rows,
        top_level_changes=['docstring/import runpy→tempfile','requested2/allowed seeds/new index20/aliases/false flags/receipt filename'],
        original_source_modified=False,production_import_AST_cropping=False,native_execution=False)


def make_index():
    upstream_seal=json.loads((UPSTREAM/'GOOD_EXPERT_HOLDOUT_SOURCE_SEAL_V1.json').read_bytes())
    assert upstream_seal['root_SHA256']=='032c431b844aedc02bffad76549b9516f92e5cfd06cce6194e47d5f4451c7534'
    for row in upstream_seal['files']:
        assert row==entry(UPSTREAM/row['name']), 'upstream sealed V1 changed'
    report=json.loads((HERE/'TEST_REPORT_STAGE_GOOD_EXPERT_V1.json').read_bytes())
    assert report['passed'] is True and report['tests_run']==18 and report['errors']==report['failures']==0
    assert report['audit']['model_stat_lstat_open']==report['audit']['native_imports']==report['audit']['process_network_lock']==0
    assert report['stage_function_calls']==report['CLI_stage_calls']==0 and report['actual_inputs_preflighted'] is False
    return dict(kind='SOURCE_ONLY_MINIMAL_GOOD_EXPERT_HOLDOUT_MATERIALIZER_INDEX_V1',enabled=False,
        source_native_enabled=False,staged=False,dispatched=False,actual_inputs_preflighted=False,
        upstream_seal=dict(path=str(UPSTREAM/'GOOD_EXPERT_HOLDOUT_SOURCE_SEAL_V1.json'),root_SHA256=upstream_seal['root_SHA256']),
        upstream_source_index=dict(path=str(UPSTREAM/'GOOD_EXPERT_HOLDOUT_SOURCE_INDEX_V1.json'),bytes=21075,SHA256='6f2fb9a4c3ad145620e1bb1b9748ae3848ef1287129aa5970dacee22502a128e'),
        files=[entry(HERE/name) for name in FILES],
        CLI=dict(entry='stage_good_expert_holdout_v1.py',required=['--original-group-root','--source-dir','--source-index','--native-root','--new-root','--group-id','--gpu-uuid','--seed'],
            modes_exactly_one=['--preflight-only','--stage'],seeds=[20260929,20260930],requested_roles=['CURB_PROTECTED878','SLOPE135'],
            seed_tagged_absent_independent_root=True,success_filename='STAGE_COMPLETE_GOOD_EXPERT_HOLDOUT_V1.json',process_launches=0),
        completeness=dict(original_worker_files='complete original source/asset set verified against sealed index',
            selected_runtime_static_trees='complete permitted original selected2 runtime/static NPZ/NPY/assets/deps; no import slicing',
            vendor='full original7 strict tree SHA ddf9d6e1744c050fd5298805d125a611673ff22ade52c5177fb02c488ff8f0c0',
            real_native_metadata='actual owner/wait/producer source checks; no model filesystem observation',
            safe_module_import='whole actual metadata modules + AppV6→Base + make_task seed negatives',
            native_module_layer='retained/PIN/AST only; no Torch/SDK/parent imports'),
        tests=report,pending_parent_phase=['real original asset/vendor7/runtime tree preflight','review paper/BPTT audit before choosing next native version','no SOURCE-tool admission/enable/dispatch'])


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    modes=parser.add_mutually_exclusive_group();modes.add_argument('--seal',action='store_true');modes.add_argument('--verify',action='store_true')
    args=parser.parse_args();diff=whitelist()
    if args.verify:assert (HERE/DIFF_NAME).read_bytes()==encoded(diff)
    else:put_once(HERE/DIFF_NAME,diff)
    index=make_index()
    if args.verify:assert (HERE/INDEX_NAME).read_bytes()==encoded(index)
    else:put_once(HERE/INDEX_NAME,index)
    if args.seal or args.verify:
        rows=[entry(HERE/name) for name in sorted(FILES+(INDEX_NAME,))]
        root=H(''.join(row['name']+'\t'+str(row['bytes'])+'\t'+row['SHA256']+'\n' for row in rows).encode())
        seal=dict(kind='SOURCE_ONLY_GOOD_EXPERT_MATERIALIZER_IMMUTABLE_SEAL_V1',enabled=False,source_native_enabled=False,staged=False,dispatched=False,
            root_algorithm='SHA256(sorted name TAB bytes TAB SHA256 LF records UTF8)',root_SHA256=root,files=rows)
        if args.verify:assert (HERE/SEAL_NAME).read_bytes()==encoded(seal)
        else:put_once(HERE/SEAL_NAME,seal)
    print(json.dumps(dict(kind='SOURCE_STAGE_SEAL_VERIFIED_NO_WRITES' if args.verify else 'SOURCE_STAGE_METADATA_BUILT_NOT_MATERIALIZED',
        root_SHA256=root if args.seal or args.verify else None,unchanged_helpers=diff['unchanged_helper_count'],changed_functions=len(CHANGES),
        source_native_enabled=False,staged=False,dispatched=False)))


if __name__=='__main__':main()
