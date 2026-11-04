"""One-time textual SOURCE index/diff publisher; never invokes a materializer."""
from __future__ import annotations
import ast
import difflib
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
R = HERE.parent
OLD = R / 'source_phase1_capture_materializer_v4'
PRODUCER = R / 'source_phase1_typed_native_capture_v1'
CODES = ('static_source_helpers_v1.py', 'build_mirror_manifest_v1.py',
         'typed_source_support_v1.py', 'derive_materializer_v1.py',
         'stage_phase1_typed_capture_v1.py', 'test_typed_materializer_v1.py',
         'run_source_tests_v1.py', 'verify_source_seal_v1.py', 'build_source_index_v1.py')


def H(raw):
    return hashlib.sha256(raw).hexdigest()


def pin(path):
    raw = path.read_bytes()
    return dict(bytes=len(raw), SHA256=H(raw))


def products():
    old_raw = (OLD / 'stage_phase1_capture_v4.py').read_bytes()
    new_raw = (HERE / 'stage_phase1_typed_capture_v1.py').read_bytes()
    assert (len(old_raw), H(old_raw)) == (45850, 'f3059d24444c40873f2d55aeb22fd82e32284e761db96250ec985314080c6507')
    diff = json.loads((HERE / 'FUNCTION_DIFF.json').read_bytes())
    assert diff['new_file']['SHA256'] == H(new_raw)
    old_nodes = {n.name:n for n in ast.parse(old_raw).body if isinstance(n, ast.FunctionDef)}
    new_nodes = {n.name:n for n in ast.parse(new_raw).body if isinstance(n, ast.FunctionDef)}
    assert old_nodes.keys() == new_nodes.keys() and len(old_nodes) == 14
    assert (OLD / 'static_source_helpers_v1.py').read_bytes() == (HERE / 'static_source_helpers_v1.py').read_bytes()
    mirror = json.loads((HERE / 'SOURCE_MIRROR_INPUTS.json').read_bytes())
    old_mirror = json.loads((OLD / 'SOURCE_MIRROR_INPUTS.json').read_bytes())
    m = {(r['root'],r['relative']):(r['bytes'],r['SHA256']) for r in mirror['files']}
    assert len(m) == len(mirror['files']) == 396
    assert all(m[('R',r['relative'])] == (r['bytes'],r['SHA256']) for r in old_mirror['files'])
    assert len(old_mirror['files']) == 332
    assert sum(root == 'R' for root,relative in m) == 395
    assert sum(root == 'T' for root,relative in m) == 1
    finite = json.loads((PRODUCER / 'FINITE_SOURCE_BUNDLE.json').read_bytes())
    active = finite['full_module_files']
    assert len(active) == 34 and len({r['install_relative'] for r in active}) == 34
    receipt = json.loads((HERE / 'SOURCE_TEST_RECEIPT_attempt4.json').read_bytes())
    assert receipt['passed'] and receipt['tests_run'] == 9 and not receipt['audit_violations']
    for name,expected in receipt['tested_source_files'].items():
        assert pin(HERE / name) == expected
    signatures = {}
    old_lines,new_lines = old_raw.decode().splitlines(),new_raw.decode().splitlines()
    for name in old_nodes:
        a,b = old_nodes[name],new_nodes[name]
        same = ast.dump(a,include_attributes=False) == ast.dump(b,include_attributes=False)
        signatures[name] = dict(original_header=old_lines[a.lineno-1],
            new_header=new_lines[b.lineno-1], original_lines=[a.lineno,a.end_lineno],
            new_lines=[b.lineno,b.end_lineno], complete_AST_equal=same)
    index = dict(kind='PHASE1_TYPED_CAPTURE_MATERIALIZER_SOURCE_INDEX_V1', source_version=1,
        source_only=True, typed_producer_schema='PHASE1_TYPED_NATIVE_PRODUCER_ABI_V1',
        purpose='NEW_PASSIVE_INTERFACE_PROBE_NO_TRAIN',
        own_python_sources={name:pin(HERE/name) for name in CODES},
        frozen_V4_materializer=dict(path=str(OLD/'stage_phase1_capture_v4.py'),**pin(OLD/'stage_phase1_capture_v4.py')),
        shared_helpers=dict(**pin(HERE/'static_source_helpers_v1.py'), whole_file_equal=True, complete_functions=17),
        derivation=dict(original_top_level_functions=14, same_complete_functions=diff['same_complete_functions'],
            necessary_changed_complete_functions=diff['necessary_changed_complete_functions'],
            functions=signatures, runtime_AST_fragments_or_stubs=False,
            namespace_cleanup_watchlist_is_not_the_actual_import_list=True),
        typed_publication={name:pin(PRODUCER/name) for name in ('SOURCE_SEAL.json','CAPTURE_SOURCE_INDEX.json','PRODUCER_ABI.json','FINITE_SOURCE_BUNDLE.json')},
        finite_active_source_binding=dict(complete_aliases=34, overlay_aliases=32,
            independent_baseline_authoritative_bootstrap_aliases=2,
            Python_aliases=sum(r['install_relative'].endswith('.py') for r in active),
            final_actual_installed_checks=34, rows=active,
            active_finite_bundle_is_not_full_V8_baseline=True),
        source_mirror=dict(manifest=pin(HERE/'SOURCE_MIRROR_INPUTS.json'), deduplicated_files=396,
            R_files=395,T_files=1,original_R_files=332,original_R_rows_all_exact=True,
            explicit_roots=['--source-root','--t-source-root'], Windows_paths_are_provenance_only=True,
            original_drive_fallback=False,T_relative='NINE_N80_PARALLEL_SOURCE_V8/n80_gpu_capacity.py',
            T_pin=dict(bytes=653,SHA256='ab26d1b22557e6a85231795cd41c52aa53b81e69661c8a62f4c72118a62c74cc'),
            T_tree_scan=False,B2_whole_python=155,B2_reference_pins=435,B2_source_inputs=164,
            actuation_original_sources=182,original_B2_null_root_declaration_preserved=True,
            two_exact_external_patch_proofs_only=True,external_patch_proofs_are_runtime_dependencies=False),
        complete_baseline_protocol=dict(whole_original_V8_worker_sources=True,whole_pinned_assets=True,
            all_eight_original_runtime_trees=True,static_NPY_NPZ_not_replaced_by_python_closure=True,
            native_vendor_members=7,native_vendor_tree_SHA256='ddf9d6e1744c050fd5298805d125a611673ff22ade52c5177fb02c488ff8f0c0',
            bootstrap_helpers_independent_originals_not_overlays=True,
            original_origin_input_paths_and_sorted_logical_digest=True,
            dynamic_conflicting_old_bytes_retained_under='worker_sources/phase1_retained_original/',
            actual_stream_hash_fsync_observed_before_completion=True,
            denied_models_raw_operational_names_checked_before_stat_or_classify=True,
            changed_alias_conflict_count_not_hardcoded=True,
            original_physics_DR_H1_mothers_thresholds_resource_close_protocol_unchanged=True,
            actual_V8_inventory_and_vendor7_proof_observed_here=False),
        metadata_only_tests=dict(receipt='SOURCE_TEST_RECEIPT_attempt4.json',**pin(HERE/'SOURCE_TEST_RECEIPT_attempt4.json'),
            tests=9,all_passed=True,real_whole_AppV6_Base_core_imports=True,
            actual_plan_and_real_64_128_tasks=True,negative_task_plan_checks=12,
            Source_temp_ROOT_equals_HERE=True,actual_B_directory_or_task_args_calls=0,
            missing_dependency_missing_Base_wrong_root_and_oldbyte_negatives=True,
            own_fake_stream_and_dynamic_retention=True,actual_original_input_inventory=False,
            original_input_sources_unchanged=407,old_44_63_10_suites_run=False),
        stage_protocol=dict(root_prefix='MOD4V1_PHASE1_E3_PASSIVE_CAPTURE_V1_',
            future_optional_suffix='_TYPED_V1_',root_must_be_absent_and_unconsumed=True,
            completion='STAGE_COMPLETE_PHASE1_CAPTURE_V1.json',parent_launches=0,
            order=['prepare_full_metadata','full_stream_copy_hash_fsync','observed_preservation',
                   'GROUP_PLAN','actual_root_metadata_and_ROOT_equals_HERE','completion'],
            completion_materialized=True,completion_means_native_acceptance=False),
        future_CLI=dict(entry='stage_phase1_typed_capture_v1.py',
            required=['--original-group-root','--source-root','--t-source-root','--native-root','--new-root','--group-id','--gpu-uuid'],
            controls=[64,128],exactly_one_mode=['--preflight-only','--stage'],
            new_admission_or_resource_conditions_added=False),
        actual_prepare_calls=0,actual_preflight_calls=0,actual_stage_calls=0,parent_launches=0,
        actual_SDK_or_Torch_or_parent_entry_calls=0,materialized=False,
        native_enabled=False,exact=False,gate1='UNKNOWN',stage2_GO=False)
    text = ''.join(difflib.unified_diff(old_raw.decode().splitlines(keepends=True),
        new_raw.decode().splitlines(keepends=True),
        fromfile='frozen_V4/stage_phase1_capture_v4.py',tofile='NEW/stage_phase1_typed_capture_v1.py'))
    return index,text


def main():
    index,text = products()
    with (HERE/'SOURCE_INDEX.json').open('xb') as stream:
        stream.write((json.dumps(index,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode())
    with (HERE/'SOURCE_DIFF.txt').open('xb') as stream:
        stream.write(text.encode())
    print(json.dumps(dict(source_only=True,index=pin(HERE/'SOURCE_INDEX.json'),
        diff=pin(HERE/'SOURCE_DIFF.txt'),mirror_files=396,R_files=395,T_files=1,
        stage_calls=0,parent_launches=0,native_enabled=False,exact=False,gate1='UNKNOWN')))


if __name__ == '__main__':
    main()
