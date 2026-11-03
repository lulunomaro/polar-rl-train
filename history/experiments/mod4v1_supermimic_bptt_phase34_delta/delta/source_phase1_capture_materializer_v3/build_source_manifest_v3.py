"""Build/verify NEW V3 SOURCE only; never call prepare/preflight/stage/worker/parent."""
from pathlib import Path
import argparse
import ast
import hashlib
import json
import sys
sys.dont_write_bytecode=True
import stage_phase1_capture_v3 as m

HERE=Path(__file__).resolve().parent;R=HERE.parent
FILES=('README.md','derive_materializer_v3.py','derive_regressions_v3.py','static_source_helpers_v1.py',
       'stage_phase1_capture_v3.py','test_materializer_stdlib_v3.py','TEST_REPORT.json','build_source_manifest_v3.py',
       'SOURCE_INDEX.json','SOURCE_MIRROR_INPUTS.json','WHITELIST_DIFF.json')
ORIGINAL='source_bound_only_native_integration_v1/stage_bound_only_native_v1.py'
ORIGINAL_PIN=(34960,'74f52b47c54e742f2a60a8459b7fa013dd52793b2adc970d02149474eb21eb40')
V2_PIN=(34834,'e39fc8936136f89e708df6a9a26911135d0c1616c641564cf155235ff0d06f6d')


def H(raw):return hashlib.sha256(raw).hexdigest()
def encode(value):return (json.dumps(value,sort_keys=True,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode()
def put(name,raw):
    path=HERE/name
    if path.exists():m.need(path.read_bytes()==raw,'existing NEW artifact differs: '+name)
    else:
        with path.open('xb') as stream:stream.write(raw)
def record(path):
    raw=path.read_bytes()
    if path.suffix=='.py':ast.parse(raw)
    return dict(relative=path.relative_to(HERE).as_posix(),bytes=len(raw),SHA256=H(raw))
def function_nodes(raw):return {n.name:n for n in ast.parse(raw).body if isinstance(n,ast.FunctionDef)}
def dump(node):return ast.dump(node,include_attributes=False)


def metadata_products():
    bundle=m.load_sources(R)  # SOURCE pins and original pure B2 source builder, not preflight
    original_raw=(R/ORIGINAL).read_bytes();m.need((len(original_raw),H(original_raw))==ORIGINAL_PIN,'original stager source changed')
    helper_raw=(HERE/'static_source_helpers_v1.py').read_bytes();helper=function_nodes(helper_raw)
    original=function_nodes(original_raw)
    m.need(len(helper)==17 and all(dump(original[k])==dump(v) for k,v in helper.items()),'complete17 helper AST proof differs')
    v2_path=R/'source_phase1_capture_materializer_v2/stage_phase1_capture_v2.py';v2_raw=v2_path.read_bytes()
    m.need((len(v2_raw),H(v2_raw))==V2_PIN and (R/'source_phase1_capture_materializer_v2/static_source_helpers_v1.py').read_bytes()==helper_raw,'immutable whole V2 inputs differ')
    current_raw=(HERE/'stage_phase1_capture_v3.py').read_bytes();old_nodes=function_nodes(v2_raw);new_nodes=function_nodes(current_raw)
    changed=sorted(k for k in old_nodes if dump(old_nodes[k])!=dump(new_nodes[k]))
    added=sorted(set(new_nodes)-set(old_nodes))
    m.need(set(changed)=={'load_sources','metadata_validate','preflight_summary','stage'} and set(added)=={'normalize_B2_source_paths','verify_B2_source_closure'},'V3 narrow function whitelist differs')
    old_stage=ast.get_source_segment(v2_raw.decode(),old_nodes['stage']);new_stage=ast.get_source_segment(current_raw.decode(),new_nodes['stage'])
    m.need(old_stage.replace("kind='SOURCE_PHASE1_CAPTURE_MATERIALIZED_NOT_ADMISSION_V2'","kind='SOURCE_PHASE1_CAPTURE_MATERIALIZED_NOT_ADMISSION_V3'")==new_stage,'streaming stage changed beyond SOURCE kind')
    report=json.loads((HERE/'TEST_REPORT.json').read_bytes())
    m.need(report['passed'] is True and report['tests_run']==42 and report['errors']==report['failures']==0 and all(v==0 for v in report['audit'].values()),'42 SOURCE tests/audit0 required')
    m.need(all(report[k]==0 for k in ('actual_prepare_calls','actual_preflight_calls','stage_calls','native_worker_or_parent_calls')),'actual execution is not SOURCE')
    paths={}
    def add(path):
        path=Path(path);m.need(path.is_relative_to(R) and path.suffix.lower() in ('.py','.json','.md','.txt'),'non-text/non-R mirror reference')
        info=m.identity(path);rel=path.relative_to(R).as_posix();row=dict(relative=rel,bytes=info['bytes'],SHA256=info['SHA'])
        m.need(rel not in paths or paths[rel]==row,'conflicting source mirror reference');paths[rel]=row
    for path,_ in bundle['sources'].values():add(path)
    add(m.reference_path(R,bundle['index']['original_index']['path']));add(R/ORIGINAL)
    for relative in bundle['index']['all_actuation_original_sources']:add(m.reference_path(R,relative))
    for row in m.BOOTSTRAP_ORIGINAL_SOURCES.values():add(m.reference_path(R,row['source_relative']))
    # The loader's actual 164 B2 dependency inputs include all 155 full .py files,
    # four source-builder routing JSONs, final diagnostic handoff plus four refs.
    for path,_ in bundle['B2_source_inputs'].values():add(path)
    # Actual immutable derivation inputs, not inferred active worker modules.
    for relative in ('source_phase1_capture_materializer_v1/stage_phase1_capture_v1.py',
                     'source_phase1_capture_materializer_v1/static_source_helpers_v1.py',
                     'source_phase1_capture_materializer_v2/stage_phase1_capture_v2.py',
                     'source_phase1_capture_materializer_v2/static_source_helpers_v1.py',
                     'source_phase1_capture_materializer_v2/test_materializer_stdlib_v2.py',
                     'source_phase1_capture_materializer_v2/SOURCE_SEAL.json'):add(R/relative)
    rows=[paths[r] for r in sorted(paths)]
    mirror=dict(kind='COMPLETE_PINNED_TEXT_SOURCE_MIRROR_INPUTS_PHASE1_V3',purpose=m.PURPOSE,
        root_semantics='preserve_actual_R_relative_paths_plus_separate_complete_NEW_materializer_bundle',files=rows,file_count=len(rows),
        all_actual_source_bytes_verified=True,original_C_source_pin_count=182,B2_original_pin_references=435,B2_original_Python_sources=155,
        additional_B2_builder_routing_JSON_files=4,diagnostic_final_handoff=1,diagnostic_source_references=4,
        B2_original_manifest_raw_SHA256=bundle['receipt']['B2_source_closure']['manifest_SHA256'],
        actual_B2_builder_called_unmodified=True,only_source_path_explicit_R_prefix_normalized_for_derived_comparison=True,
        excludes_actual_original_runtime_banks_assets_native_root_and_all_models=True,
        isolated_copy_load_and_rebuild_regression_passed=True,original_R_fallback_forbidden_in_that_regression=True,
        actual_prepare_calls=0,actual_preflight_calls=0,stage_calls=0,native_executed=False)
    diff=dict(kind='PHASE1_CAPTURE_MINIMAL_SOURCE_WHITELIST_DIFF_V3',source_derivation_version=3,
        sealed_V2_entry=dict(relative=v2_path.relative_to(R).as_posix(),bytes=len(v2_raw),SHA256=H(v2_raw)),
        changed_V2_function_whitelist=changed,added_source_only_helpers=added,
        unchanged_entire_V2_functions=sorted(set(old_nodes)-set(changed)),
        unchanged_complete_helper_AST_names=sorted(helper),complete_AST_equality_verified=True,
        helper_complete_function_source_SHA256={k:H(ast.get_source_segment(helper_raw.decode(),helper[k]).encode()) for k in sorted(helper)},
        original_helper_source=dict(relative=ORIGINAL,bytes=ORIGINAL_PIN[0],SHA256=ORIGINAL_PIN[1]),
        source_loader_delta='final V3/B2 pins; all155 full original Python files + four routing JSON + diagnostic final+4; actual original B2 builder',
        metadata_delta='SOURCE kind/version only; same whole-module bootstrap unchanged',
        stage_delta='SOURCE kind only; entire observed streaming, retention, independent origin and installed validation unchanged',
        preserved_wire=dict(root_prefix=m.ROOT_PREFIX,completion_receipt=m.COMPLETE_NAME,typed_plan_task_purpose_inventory_aliases_unchanged=True),
        native_boundary_changed=False,complete8_runtime_prepare_changed=False,independent_origin_retention_changed=False,
        original_parent_resource_blocks_changed=False,five_worker_candidate_logic_changes=0,old_seals_changed=False,
        strict_original_B2_reset_verifier_reimplemented=False,actual_native_binding='UNKNOWN')
    def portable(value):
        if type(value) is list:return [portable(v) for v in value]
        if type(value) is dict:
            return {k:(Path(v).relative_to(R).as_posix() if k=='path' and type(v) is str and Path(v).is_relative_to(R) else portable(v)) for k,v in value.items()}
        return value
    mirror_raw=encode(mirror)
    index=dict(kind='SOURCE_PHASE1_CAPTURE_MATERIALIZER_INDEX_V3',source_derivation_version=3,purpose=m.PURPOSE,
        entry=record(HERE/'stage_phase1_capture_v3.py'),requested_roles=['E3'],complete_role_catalog=list(m.ROLES),deferred_roles=list(m.ROLES[1:]),
        H1_constructed=False,controls=[64,128],num_envs=80,seed=20260928,policy='EXPLICIT_SYNTHETIC_ZERO6_NOT_POLICY_QUALITY',PT_reads=0,training=False,quality_evaluation=False,
        CLI_required=['--original-group-root','--source-root','--native-root','--new-root','--group-id','--gpu-uuid'],CLI_modes_exactone=['--preflight-only','--stage'],
        root_prefix=m.ROOT_PREFIX,completion_receipt=m.COMPLETE_NAME,
        controller_receipt_interface=dict(purpose=m.PURPOSE,materialized=True,parent_launches=0,wire_API_version=1),
        source_closure=portable(bundle['receipt']),source_mirror=dict(relative='SOURCE_MIRROR_INPUTS.json',bytes=len(mirror_raw),SHA256=H(mirror_raw),files=len(rows)),
        unchanged_helpers=dict(count=17,relative='static_source_helpers_v1.py',bytes=len(helper_raw),SHA256=H(helper_raw)),
        B2_manifest_rebuild='actual source_api.build_manifest(root=actual_source_mirror_root); source_path-only explicit root normalization',
        runtime_original_dependencies=27,original_full_static_tree_proof='actual preoverlay bytes+input paths+readbytes; conflict retention; actual stream hash observations',
        safe_bootstrap='same unchanged actual worker.bootstrap_original_helpers(group); whole storage/capacity modules; constructors0',
        source_only=True,source_native_enabled=False,materialized=False,staged=False,dispatched=False,actual_SDK_executed=False,
        tests_run=42,actual_prepare_calls=0,actual_preflight_calls=0,stage_calls=0,parent_launches=0,
        real_static_inputs_or_vendor7_integrity_tested=False,gate1='UNKNOWN',capture_interface_passed=False,exact=False,stage2_GO=False)
    return {'SOURCE_MIRROR_INPUTS.json':mirror_raw,'WHITELIST_DIFF.json':encode(diff),'SOURCE_INDEX.json':encode(index)}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--verify',action='store_true');args=parser.parse_args();products=metadata_products()
    if args.verify:
        for name,raw in products.items():m.need((HERE/name).read_bytes()==raw,'generated SOURCE metadata differs: '+name)
        seal=json.loads((HERE/'SOURCE_SEAL.json').read_bytes());rows=[record(HERE/name) for name in FILES]
        m.need(rows==seal['files'] and m.canonical(rows)==seal['content_root_sha256'],'NEW V3 materializer seal differs')
        print(json.dumps(dict(kind='SOURCE_PHASE1_MATERIALIZER_V3_SEAL_VERIFIED_NO_WRITES',files=len(rows),content_root_sha256=seal['content_root_sha256'])))
    else:
        for name,raw in products.items():put(name,raw)
        rows=[record(HERE/name) for name in FILES]
        seal=dict(kind='SOURCE_PHASE1_CAPTURE_MATERIALIZER_SEAL_V3',files=rows,content_root_sha256=m.canonical(rows),frozen=True,source_only=True,
            purpose=m.PURPOSE,source_derivation_version=3,source_native_enabled=False,materialized=False,staged=False,dispatched=False,
            actual_prepare_calls=0,actual_preflight_calls=0,stage_calls=0,parent_launches=0,actual_SDK_executed=False,
            gate1='UNKNOWN',capture_interface_passed=False,exact=False,stage2_GO=False)
        put('SOURCE_SEAL.json',encode(seal))
        print(json.dumps(dict(kind='SOURCE_PHASE1_MATERIALIZER_V3_SEALED_NOT_PREPARED',files=len(rows),source_mirror_files=json.loads(products['SOURCE_MIRROR_INPUTS.json'])['file_count'],content_root_sha256=seal['content_root_sha256'])))

if __name__=='__main__':main()
