"""Build/verify NEW V2 SOURCE metadata; never invoke prepare/stage/worker/parent."""
from pathlib import Path
import argparse
import ast
import hashlib
import json
import sys
sys.dont_write_bytecode=True
import stage_phase1_capture_v2 as m

HERE=Path(__file__).resolve().parent
R=HERE.parent
FILES=('README.md','derive_materializer_v2.py','static_source_helpers_v1.py','stage_phase1_capture_v2.py',
       'test_materializer_stdlib_v2.py','TEST_REPORT.json','build_source_manifest_v2.py','SOURCE_INDEX.json',
       'SOURCE_MIRROR_INPUTS.json','WHITELIST_DIFF.json')
ORIGINAL='source_bound_only_native_integration_v1/stage_bound_only_native_v1.py'
ORIGINAL_PIN=(34960,'74f52b47c54e742f2a60a8459b7fa013dd52793b2adc970d02149474eb21eb40')


def H(raw):return hashlib.sha256(raw).hexdigest()


def raw_json(value):return (json.dumps(value,sort_keys=True,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode()


def put_new_or_equal(name,raw):
    path=HERE/name
    if path.exists():
        old=path.read_bytes();m.need(old==raw,'existing NEW source artifact differs; do not overwrite: '+name)
    else:
        with path.open('xb') as stream:stream.write(raw)


def record(path):
    raw=path.read_bytes()
    if path.suffix=='.py':ast.parse(raw)
    return dict(relative=path.relative_to(HERE).as_posix(),bytes=len(raw),SHA256=H(raw))


def metadata_products():
    bundle=m.load_sources(R)  # final text PINs, not original/native input preflight
    original_raw=(R/ORIGINAL).read_bytes();m.need((len(original_raw),H(original_raw))==ORIGINAL_PIN,'original stager source changed')
    old={n.name:ast.dump(n,include_attributes=False) for n in ast.parse(original_raw).body if isinstance(n,ast.FunctionDef)}
    helper_raw=(HERE/'static_source_helpers_v1.py').read_bytes()
    helper={n.name:ast.dump(n,include_attributes=False) for n in ast.parse(helper_raw).body if isinstance(n,ast.FunctionDef)}
    m.need(len(helper)==17 and all(old[k]==v for k,v in helper.items()),'complete17 helper AST proof differs')
    report=json.loads((HERE/'TEST_REPORT.json').read_bytes())
    m.need(report['passed'] is True and report['tests_run']==33 and report['errors']==report['failures']==0
           and all(v==0 for v in report['audit'].values()),'33 SOURCE tests/audit0 required')
    m.need(all(report[k]==0 for k in ('actual_prepare_calls','actual_preflight_calls','stage_calls','native_worker_or_parent_calls')),'actual execution is not SOURCE')
    files={}
    def add(path):
        path=Path(path);m.need(path.is_relative_to(R),'source mirror path outside pinned R')
        info=m.identity(path);rel=path.relative_to(R).as_posix()
        row=dict(relative=rel,bytes=info['bytes'],SHA256=info['SHA'])
        m.need(rel not in files or files[rel]==row,'conflicting source-mirror reference');files[rel]=row
    for path,_ in bundle['sources'].values():add(path)
    add(m.reference_path(R,bundle['index']['original_index']['path']));add(R/ORIGINAL)
    for relative in bundle['index']['all_actuation_original_sources']:add(m.reference_path(R,relative))
    for row in m.BOOTSTRAP_ORIGINAL_SOURCES.values():add(m.reference_path(R,row['source_relative']))
    # These two sealed V1 texts are actual new derivation/review inputs, not an
    # inferred active tree or a fresh worker overlay. Preserve their real paths.
    add(R/'source_phase1_capture_materializer_v1/stage_phase1_capture_v1.py')
    previous_helper=R/'source_phase1_capture_materializer_v1/static_source_helpers_v1.py'
    m.need(previous_helper.read_bytes()==helper_raw,'entire V1 helper bytes differ')
    add(previous_helper)
    mirror=dict(kind='COMPLETE_PINNED_TEXT_SOURCE_MIRROR_INPUTS_PHASE1_V2',purpose=m.PURPOSE,
        root_semantics='R_source_only_mirror_preserve_relative_paths_not_flat27',files=[files[r] for r in sorted(files)],
        file_count=len(files),all_actual_source_bytes_verified=True,original_C_source_pin_count=182,
        bootstrap_original_source_evidence=m.BOOTSTRAP_ORIGINAL_SOURCES,
        excludes_actual_original_runtime_banks_assets_native_root_and_all_models=True,
        actual_prepare_calls=0,actual_preflight_calls=0,stage_calls=0,native_executed=False)
    helper_nodes={n.name:n for n in ast.parse(helper_raw).body if isinstance(n,ast.FunctionDef)}
    def portable(value):
        if isinstance(value,list):return [portable(v) for v in value]
        if isinstance(value,dict):return {k:(Path(v).relative_to(R).as_posix() if k=='path' and isinstance(v,str) and Path(v).is_relative_to(R) else portable(v)) for k,v in value.items()}
        return value
    v1=R/'source_phase1_capture_materializer_v1/stage_phase1_capture_v1.py'
    v1_raw=v1.read_bytes();m.need((len(v1_raw),H(v1_raw))==(31219,m.V1_ENTRY_SHA256),'sealed V1 source derivation differs')
    v1_functions={n.name:ast.dump(n,include_attributes=False) for n in ast.parse(v1_raw).body if isinstance(n,ast.FunctionDef)}
    v2_raw=(HERE/'stage_phase1_capture_v2.py').read_bytes()
    v2_functions={n.name:ast.dump(n,include_attributes=False) for n in ast.parse(v2_raw).body if isinstance(n,ast.FunctionDef)}
    m.need(set(v1_functions)==set(v2_functions),'unrelated V2 function addition/removal')
    changed=sorted(n for n in v1_functions if v1_functions[n]!=v2_functions[n])
    m.need(set(changed)=={'load_sources','metadata_validate','preflight_summary','stage'},'V1 to V2 whitelist differs')
    diff=dict(kind='PHASE1_CAPTURE_MINIMAL_SOURCE_WHITELIST_DIFF_V2',source_derivation_version=2,
        original_relative=ORIGINAL,original_bytes=ORIGINAL_PIN[0],original_SHA256=ORIGINAL_PIN[1],
        unchanged_complete_helper_AST_names=sorted(helper),complete_AST_equality_verified=True,
        helper_complete_function_source_SHA256={k:H(ast.get_source_segment(helper_raw.decode('utf-8'),helper_nodes[k]).encode()) for k in sorted(helper)},
        sealed_V1_materializer_entry=dict(relative=v1.relative_to(R).as_posix(),bytes=len(v1_raw),SHA256=H(v1_raw)),
        changed_V1_function_whitelist=changed,unchanged_entire_V1_functions=sorted(set(v1_functions)-set(changed)),
        native_boundary_changed=False,independent_origin_retention_changed=False,
        complete_original_static_tree_prepare_changed=False,
        stage_delta='only SOURCE receipt kind V2; entire original streaming and observed installed logic otherwise unchanged',
        source_loader_delta='final worker V2 folder/seal/index; verify exact original helper text evidence; no helper overlay fallback',
        metadata_delta='same actual worker bootstrap; exact original baseline files; whole import/file/spec/function-code/PIN/cache proof; constructors0',
        bootstrap_entry='worker_passive_interface_v1.bootstrap_original_helpers(group)',
        preserved_wire=dict(root_prefix=m.ROOT_PREFIX,completion_receipt=m.COMPLETE_NAME,task_plan_purpose_inventory_aliases_unchanged=True),
        parent_resource_blocks_changed=False,old_worker_V1_seal_changed=False,new_worker_V2_final13_verified=True,old_seals_changed=False)
    mirror_raw=raw_json(mirror)
    index=dict(kind='SOURCE_PHASE1_CAPTURE_MATERIALIZER_INDEX_V2',source_derivation_version=2,purpose=m.PURPOSE,
        entry=record(HERE/'stage_phase1_capture_v2.py'),requested_roles=['E3'],complete_role_catalog=list(m.ROLES),
        deferred_roles=list(m.ROLES[1:]),H1_constructed=False,controls=[64,128],num_envs=80,seed=20260928,
        policy='EXPLICIT_SYNTHETIC_ZERO6_NOT_POLICY_QUALITY',PT_reads=0,training=False,quality_evaluation=False,
        CLI_required=['--original-group-root','--source-root','--native-root','--new-root','--group-id','--gpu-uuid'],
        CLI_modes_exactone=['--preflight-only','--stage'],root_prefix=m.ROOT_PREFIX,completion_receipt=m.COMPLETE_NAME,
        controller_receipt_interface=dict(purpose=m.PURPOSE,materialized=True,parent_launches=0,receipt_bytes_SHA256_pinned_by_external_controller=True),
        source_closure=portable(bundle['receipt']),source_mirror=dict(relative='SOURCE_MIRROR_INPUTS.json',bytes=len(mirror_raw),SHA256=H(mirror_raw),files=len(files)),
        unchanged_helpers=dict(count=17,relative='static_source_helpers_v1.py',bytes=len(helper_raw),SHA256=H(helper_raw),proof='WHITELIST_DIFF.json'),
        safe_bootstrap=dict(entry='worker_passive_interface_v1.bootstrap_original_helpers(group)',whole_original_modules=list(m.BOOTSTRAP_ORIGINAL_SOURCES),constructors_called=0),
        inventory_proof='independent complete actual input byte inventory plus original planSHA/logical treeSHA/input_path/readbytes; conflicts retained; stage uses observed stream hashes',
        source_only=True,source_native_enabled=False,materialized=False,staged=False,dispatched=False,actual_SDK_executed=False,
        tests_run=33,actual_prepare_calls=0,actual_preflight_calls=0,stage_calls=0,parent_launches=0,
        real_static_inputs_or_vendor7_integrity_tested=False,gate1='UNKNOWN',capture_interface_passed=False,exact=False,stage2_GO=False)
    return {'SOURCE_MIRROR_INPUTS.json':mirror_raw,'WHITELIST_DIFF.json':raw_json(diff),'SOURCE_INDEX.json':raw_json(index)}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--verify',action='store_true');args=parser.parse_args()
    products=metadata_products()
    if args.verify:
        for name,raw in products.items():m.need((HERE/name).read_bytes()==raw,'generated source metadata differs: '+name)
        seal=json.loads((HERE/'SOURCE_SEAL.json').read_bytes())
        rows=[record(HERE/name) for name in FILES]
        m.need(rows==seal['files'] and m.canonical(rows)==seal['content_root_sha256'],'NEW materializer SOURCE seal differs')
        print(json.dumps(dict(kind='SOURCE_PHASE1_MATERIALIZER_V2_SEAL_VERIFIED_NO_WRITES',files=len(rows),content_root_sha256=seal['content_root_sha256'])))
    else:
        for name,raw in products.items():put_new_or_equal(name,raw)
        rows=[record(HERE/name) for name in FILES]
        seal=dict(kind='SOURCE_PHASE1_CAPTURE_MATERIALIZER_SEAL_V2',files=rows,content_root_sha256=m.canonical(rows),
            frozen=True,source_only=True,purpose=m.PURPOSE,source_derivation_version=2,
            source_native_enabled=False,materialized=False,staged=False,dispatched=False,
            actual_prepare_calls=0,actual_preflight_calls=0,stage_calls=0,parent_launches=0,actual_SDK_executed=False,
            gate1='UNKNOWN',capture_interface_passed=False,exact=False,stage2_GO=False)
        put_new_or_equal('SOURCE_SEAL.json',raw_json(seal))
        print(json.dumps(dict(kind='SOURCE_PHASE1_MATERIALIZER_V2_SEALED_NOT_PREPARED',files=len(rows),source_mirror_files=json.loads(products['SOURCE_MIRROR_INPUTS.json'])['file_count'],content_root_sha256=seal['content_root_sha256'])))


if __name__=='__main__':main()
