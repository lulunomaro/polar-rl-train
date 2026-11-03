"""Build/readonly-verify final NEW V4 SOURCE only, after exact worker4 binding.
No prepare/preflight/stage/worker/parent or boundary CPU execution.
"""
from pathlib import Path
import argparse
import ast
import hashlib
import json
import sys
sys.dont_write_bytecode=True
import stage_phase1_capture_v4 as m

HERE=Path(__file__).resolve().parent;R=HERE.parent
FILES=('README.md','derive_materializer_v4.py','derive_regressions_v4.py','static_source_helpers_v1.py',
       'stage_phase1_capture_v4.py','test_materializer_stdlib_v4.py','TEST_REPORT.json','build_source_manifest_v4.py',
       'SOURCE_INDEX.json','SOURCE_MIRROR_INPUTS.json','WHITELIST_DIFF.json')
ORIGINAL='source_bound_only_native_integration_v1/stage_bound_only_native_v1.py'
ORIGINAL_PIN=(34960,'74f52b47c54e742f2a60a8459b7fa013dd52793b2adc970d02149474eb21eb40')
V3_PIN=(42437,'2a4213d95939216f3a91db6c1739a443907aadf33c4f615aa897eace5a915425')


def H(raw):return hashlib.sha256(raw).hexdigest()
def encode(value):return (json.dumps(value,sort_keys=True,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode()
def put(name,raw):
    path=HERE/name
    if path.exists():m.need(path.read_bytes()==raw,'existing NEW artifact differs: '+name)
    else:
        with path.open('xb')as stream:stream.write(raw)
def record(path):
    raw=path.read_bytes()
    if path.suffix=='.py':ast.parse(raw)
    return dict(relative=path.relative_to(HERE).as_posix(),bytes=len(raw),SHA256=H(raw))
def function_nodes(raw):return {n.name:n for n in ast.parse(raw).body if isinstance(n,ast.FunctionDef)}
def dump(node):return ast.dump(node,include_attributes=False)


def metadata_products():
    bundle=m.load_sources(R)  # final source text closure only, not actual input preflight
    v3_index_path=R/'source_phase1_capture_worker_v3/CAPTURE_SOURCE_INDEX.json'
    v3_index,v3_index_raw=m.metadata(v3_index_path,2*1024*1024)
    m.need((len(v3_index_raw),H(v3_index_raw))==(124202,'bdeea3f057fb922bd9ae2670dcbf19188f651ca64ab2cbb0331f56a5a1124797'),'sealed complete V3 index baseline differs')
    unchanged_index_fields=('original_index','original17','dependency_sources','dependency_seals','all_actuation_original_sources',
        'actuation_original_source_count','sensor_source_manifest','sensor_reset_diagnostic_source_references','bootstrap_original_sources')
    m.need(all(bundle['index'][k]==v3_index[k]for k in unchanged_index_fields),'original17/B2/C182/adapter/partition/bootstrap index changed')
    original_raw=(R/ORIGINAL).read_bytes();m.need((len(original_raw),H(original_raw))==ORIGINAL_PIN,'original stager source changed')
    helper_raw=(HERE/'static_source_helpers_v1.py').read_bytes();helper=function_nodes(helper_raw);original=function_nodes(original_raw)
    m.need(len(helper)==17 and all(dump(original[k])==dump(v)for k,v in helper.items()),'complete17 helper AST proof differs')
    v3_path=R/'source_phase1_capture_materializer_v3/stage_phase1_capture_v3.py';v3_raw=v3_path.read_bytes()
    m.need((len(v3_raw),H(v3_raw))==V3_PIN and (R/'source_phase1_capture_materializer_v3/static_source_helpers_v1.py').read_bytes()==helper_raw,'immutable whole V3 inputs differ')
    current_raw=(HERE/'stage_phase1_capture_v4.py').read_bytes();old_nodes=function_nodes(v3_raw);new_nodes=function_nodes(current_raw)
    changed=sorted(k for k in old_nodes if dump(old_nodes[k])!=dump(new_nodes[k]));added=sorted(set(new_nodes)-set(old_nodes))
    m.need(set(changed)=={'load_sources','metadata_validate','preflight_summary','stage'} and not added and set(new_nodes)==set(old_nodes),'V4 narrow function whitelist differs')
    old_stage=ast.get_source_segment(v3_raw.decode(),old_nodes['stage']);new_stage=ast.get_source_segment(current_raw.decode(),new_nodes['stage'])
    m.need(old_stage.replace("kind='SOURCE_PHASE1_CAPTURE_MATERIALIZED_NOT_ADMISSION_V3'","kind='SOURCE_PHASE1_CAPTURE_MATERIALIZED_NOT_ADMISSION_V4'")==new_stage,'streaming stage changed beyond SOURCE kind')
    # Final V4 one-line projection is verified against the complete sealed V3 bytes.
    for name in ('phase1_capture_contract.py','phase1_capture_observer.py','phase1_capture_runtime.py','worker_passive_interface_v1.py','single_gpu_passive_capture_parent_v1.py'):
        old=(R/'source_phase1_capture_worker_v3'/name).read_bytes();actual=(R/m.WORKER_FOLDER/name).read_bytes()
        if name=='worker_passive_interface_v1.py':
            before=b'boundary=core().OriginalEpisodeBoundary(torch,env.device,n=80)';after=b'boundary=core().OriginalEpisodeBoundary(torch,bridge.device,n=80)'
            m.need(old.count(before)==1 and actual==old.replace(before,after,1),'final V4 worker differs beyond one existing bridge.device expression')
        else:m.need(actual==old,'final V4 unchanged candidate bytes differ: '+name)
    report=json.loads((HERE/'TEST_REPORT.json').read_bytes())
    m.need(report['passed']is True and report['tests_run']==44 and report['errors']==report['failures']==0 and all(v==0 for v in report['audit'].values()),'original42 plus2 boundary SOURCE fixture regressions/audit0 required')
    m.need(all(report[k]==0 for k in ('actual_prepare_calls','actual_preflight_calls','stage_calls','native_worker_or_parent_calls')),'actual execution is not SOURCE')
    paths={}
    def add(path):
        path=Path(path);m.need(path.is_relative_to(R) and path.suffix.lower()in('.py','.json','.md','.txt'),'non-text/non-R mirror reference')
        info=m.identity(path);rel=path.relative_to(R).as_posix();row=dict(relative=rel,bytes=info['bytes'],SHA256=info['SHA'])
        m.need(rel not in paths or paths[rel]==row,'conflicting source mirror reference');paths[rel]=row
    for path,_ in bundle['sources'].values():add(path)
    add(m.reference_path(R,bundle['index']['original_index']['path']));add(R/ORIGINAL)
    for relative in bundle['index']['all_actuation_original_sources']:add(m.reference_path(R,relative))
    for row in m.BOOTSTRAP_ORIGINAL_SOURCES.values():add(m.reference_path(R,row['source_relative']))
    for path,_ in bundle['B2_source_inputs'].values():add(path)
    # Keep all real derivation inputs and unchanged whole-source regression bases.
    for relative in ('source_phase1_capture_materializer_v1/stage_phase1_capture_v1.py',
                     'source_phase1_capture_materializer_v1/static_source_helpers_v1.py',
                     'source_phase1_capture_materializer_v2/stage_phase1_capture_v2.py',
                     'source_phase1_capture_materializer_v2/static_source_helpers_v1.py',
                     'source_phase1_capture_materializer_v2/test_materializer_stdlib_v2.py',
                     'source_phase1_capture_materializer_v2/SOURCE_SEAL.json',
                     'source_phase1_capture_materializer_v3/stage_phase1_capture_v3.py',
                     'source_phase1_capture_materializer_v3/static_source_helpers_v1.py',
                     'source_phase1_capture_materializer_v3/test_materializer_stdlib_v3.py',
                     'source_phase1_capture_materializer_v3/SOURCE_SEAL.json'):add(R/relative)
    for name in ('phase1_capture_contract.py','phase1_capture_observer.py','phase1_capture_runtime.py','worker_passive_interface_v1.py','single_gpu_passive_capture_parent_v1.py','CAPTURE_SOURCE_INDEX.json'):
        add(R/'source_phase1_capture_worker_v3'/name)
    rows=[paths[r]for r in sorted(paths)]
    mirror=dict(kind='COMPLETE_PINNED_TEXT_SOURCE_MIRROR_INPUTS_PHASE1_V4',purpose=m.PURPOSE,
        root_semantics='preserve_actual_R_relative_paths_plus_separate_complete_NEW_materializer_bundle',files=rows,file_count=len(rows),
        all_actual_source_bytes_verified=True,original_C_source_pin_count=182,B2_original_pin_references=435,B2_original_Python_sources=155,
        additional_B2_builder_routing_JSON_files=4,diagnostic_final_handoff=1,diagnostic_source_references=4,
        boundary_fixture_SOURCE_members=8,boundary_fixture_seal=1,boundary_fixture_original_source_references=3,
        boundary_fixture_or_CPU_module_imports=0,parent_CPU_report_dependency=False,
        B2_original_manifest_raw_SHA256=bundle['receipt']['B2_source_closure']['manifest_SHA256'],
        actual_B2_builder_called_unmodified=True,only_source_path_explicit_R_prefix_normalized_for_derived_comparison=True,
        excludes_actual_original_runtime_banks_assets_native_root_and_all_models=True,
        isolated_copy_load_and_rebuild_regression_passed=True,original_R_fallback_forbidden_in_that_regression=True,
        actual_prepare_calls=0,actual_preflight_calls=0,stage_calls=0,native_executed=False)
    diff=dict(kind='PHASE1_CAPTURE_MINIMAL_SOURCE_WHITELIST_DIFF_V4',source_derivation_version=4,
        sealed_V3_entry=dict(relative=v3_path.relative_to(R).as_posix(),bytes=len(v3_raw),SHA256=H(v3_raw)),
        changed_V3_function_whitelist=changed,added_source_only_helpers=added,
        unchanged_entire_V3_functions=sorted(set(old_nodes)-set(changed)),
        unchanged_complete_helper_AST_names=sorted(helper),complete_AST_equality_verified=True,
        unchanged_V3_original_dependency_index_fields=list(unchanged_index_fields),complete_V3_index_bytes=len(v3_index_raw),complete_V3_index_SHA256=H(v3_index_raw),
        helper_complete_function_source_SHA256={k:H(ast.get_source_segment(helper_raw.decode(),helper[k]).encode())for k in sorted(helper)},
        original_helper_source=dict(relative=ORIGINAL,bytes=ORIGINAL_PIN[0],SHA256=ORIGINAL_PIN[1]),
        source_loader_delta='final V4 folder/seal/index/root/source version; declared readonly boundary Source8 plus seal and3 original references; same complete B2 164 source closure',
        metadata_delta='SOURCE kind/version only; same whole-module bootstrap unchanged',
        stage_delta='SOURCE kind only; entire observed streaming, retention, independent origin and installed validation unchanged',
        preserved_wire=dict(root_prefix=m.ROOT_PREFIX,completion_receipt=m.COMPLETE_NAME,typed_plan_task_purpose_inventory_aliases_unchanged=True),
        native_boundary_changed=False,complete8_runtime_prepare_changed=False,independent_origin_retention_changed=False,
        original_parent_resource_blocks_changed=False,five_worker_candidate_logic_changes=1,
        worker_delta='only OriginalEpisodeBoundary device argument: existing env.device -> existing bridge.device',
        original_flags_dtype_shape_or_semantics_changed=False,original_boundary_code_changed=False,old_seals_changed=False,
        strict_original_B2_reset_verifier_reimplemented=False,actual_native_binding='UNKNOWN',actual_runtime_flags_type_shape='UNKNOWN')
    def portable(value):
        if type(value)is list:return [portable(v)for v in value]
        if type(value)is dict:
            return {k:(Path(v).relative_to(R).as_posix()if k=='path'and type(v)is str and Path(v).is_relative_to(R)else portable(v))for k,v in value.items()}
        return value
    mirror_raw=encode(mirror)
    index=dict(kind='SOURCE_PHASE1_CAPTURE_MATERIALIZER_INDEX_V4',source_derivation_version=4,purpose=m.PURPOSE,
        entry=record(HERE/'stage_phase1_capture_v4.py'),requested_roles=['E3'],complete_role_catalog=list(m.ROLES),deferred_roles=list(m.ROLES[1:]),
        H1_constructed=False,controls=[64,128],num_envs=80,seed=20260928,policy='EXPLICIT_SYNTHETIC_ZERO6_NOT_POLICY_QUALITY',PT_reads=0,training=False,quality_evaluation=False,
        CLI_required=['--original-group-root','--source-root','--native-root','--new-root','--group-id','--gpu-uuid'],CLI_modes_exactone=['--preflight-only','--stage'],
        root_prefix=m.ROOT_PREFIX,completion_receipt=m.COMPLETE_NAME,
        controller_receipt_interface=dict(purpose=m.PURPOSE,materialized=True,parent_launches=0,wire_API_version=1),
        source_closure=portable(bundle['receipt']),source_mirror=dict(relative='SOURCE_MIRROR_INPUTS.json',bytes=len(mirror_raw),SHA256=H(mirror_raw),files=len(rows)),
        unchanged_helpers=dict(count=17,relative='static_source_helpers_v1.py',bytes=len(helper_raw),SHA256=H(helper_raw)),
        B2_manifest_rebuild='same original source_api.build_manifest(root=actual_source_mirror_root); source_path-only explicit root normalization',
        runtime_original_dependencies=27,original_full_static_tree_proof='actual preoverlay bytes+input paths+readbytes; conflict retention; actual stream hash observations',
        safe_bootstrap='same unchanged actual worker.bootstrap_original_helpers(group); whole storage/capacity modules; constructors0',
        source_only=True,source_native_enabled=False,materialized=False,staged=False,dispatched=False,actual_SDK_executed=False,
        tests_run=44,actual_prepare_calls=0,actual_preflight_calls=0,stage_calls=0,parent_launches=0,
        real_static_inputs_or_vendor7_integrity_tested=False,actual_runtime_flags_type_shape='UNKNOWN',gate1='UNKNOWN',capture_interface_passed=False,exact=False,stage2_GO=False)
    return {'SOURCE_MIRROR_INPUTS.json':mirror_raw,'WHITELIST_DIFF.json':encode(diff),'SOURCE_INDEX.json':encode(index)}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--verify',action='store_true');args=parser.parse_args();products=metadata_products()
    if args.verify:
        for name,raw in products.items():m.need((HERE/name).read_bytes()==raw,'generated SOURCE metadata differs: '+name)
        seal=json.loads((HERE/'SOURCE_SEAL.json').read_bytes());rows=[record(HERE/name)for name in FILES]
        m.need(rows==seal['files']and m.canonical(rows)==seal['content_root_sha256'],'NEW V4 materializer seal differs')
        print(json.dumps(dict(kind='SOURCE_PHASE1_MATERIALIZER_V4_SEAL_VERIFIED_NO_WRITES',files=len(rows),content_root_sha256=seal['content_root_sha256'])))
    else:
        for name,raw in products.items():put(name,raw)
        rows=[record(HERE/name)for name in FILES]
        seal=dict(kind='SOURCE_PHASE1_CAPTURE_MATERIALIZER_SEAL_V4',files=rows,content_root_sha256=m.canonical(rows),frozen=True,source_only=True,
            purpose=m.PURPOSE,source_derivation_version=4,source_native_enabled=False,materialized=False,staged=False,dispatched=False,
            actual_prepare_calls=0,actual_preflight_calls=0,stage_calls=0,parent_launches=0,actual_SDK_executed=False,
            gate1='UNKNOWN',capture_interface_passed=False,exact=False,stage2_GO=False)
        put('SOURCE_SEAL.json',encode(seal))
        print(json.dumps(dict(kind='SOURCE_PHASE1_MATERIALIZER_V4_SEALED_NOT_PREPARED',files=len(rows),source_mirror_files=json.loads(products['SOURCE_MIRROR_INPUTS.json'])['file_count'],content_root_sha256=seal['content_root_sha256'])))


if __name__=='__main__':main()
