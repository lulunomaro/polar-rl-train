"""Publish SOURCE index V2 after history-only review; no materializer import."""
from pathlib import Path
import ast
import copy
import hashlib
import json

HERE=Path(__file__).resolve().parent
R=HERE.parent
V1=R/'source_phase1_typed_capture_materializer_v1'
H=lambda raw:hashlib.sha256(raw).hexdigest()
PYTHON_FILES=('static_source_helpers_v1.py','typed_source_support_v1.py','historical_b2_binding_v2.py',
              'derive_history_binding_v2.py','stage_phase1_typed_capture_v2.py','test_history_binding_v2.py',
              'run_history_binding_tests_v2.py','build_source_index_v2.py','verify_source_seal_v2.py')


def pin(path):
    raw=Path(path).read_bytes()
    return dict(bytes=len(raw),SHA256=H(raw))


def function_records(name):
    raw=(HERE/name).read_bytes();text=raw.decode('utf-8');result={}
    for node in ast.parse(text).body:
        if isinstance(node,ast.FunctionDef):
            complete=''.join(text.splitlines(keepends=True)[node.lineno-1:node.end_lineno])
            result[node.name]=dict(header=text.splitlines()[node.lineno-1],lines=[node.lineno,node.end_lineno],
                                   complete_source_SHA256=H(complete.encode()),
                                   complete_AST_SHA256=H(ast.dump(node,include_attributes=False).encode()))
    return result


def main():
    old_raw=(V1/'SOURCE_INDEX.json').read_bytes()
    assert (len(old_raw),H(old_raw))==(23560,'3ca53da2954e78300026eeb3d51e26a629fd7daac0e919be96e042214920c84d')
    old=json.loads(old_raw);index=copy.deepcopy(old)
    index.update(kind='PHASE1_TYPED_CAPTURE_MATERIALIZER_SOURCE_INDEX_V2',source_version=2,
                 materializer_source_publication=2,history_binding_version=2)
    index['own_python_sources']={name:pin(HERE/name) for name in PYTHON_FILES}
    for name in PYTHON_FILES:ast.parse((HERE/name).read_bytes())
    diff=json.loads((HERE/'FUNCTION_SOURCE_DIFF.json').read_bytes())
    receipt=json.loads((HERE/'SOURCE_TEST_RECEIPT_attempt1.json').read_bytes())
    references=json.loads((HERE/'SOURCE_REFERENCES.json').read_bytes())
    assert receipt['passed'] and receipt['tests_run']==6 and receipt['audit_violations']==[]
    for name,value in receipt['tested_source_files'].items():assert pin(HERE/name)==value
    assert diff['entire_source_and_AST_unchanged']==13 and diff['original_top_functions']==14
    index['frozen_typed_V1_materializer']=dict(relative='source_phase1_typed_capture_materializer_v1/stage_phase1_typed_capture_v1.py',
        **pin(V1/'stage_phase1_typed_capture_v1.py'))
    index['frozen_typed_V1_source_index']=dict(relative='source_phase1_typed_capture_materializer_v1/SOURCE_INDEX.json',**pin(V1/'SOURCE_INDEX.json'))
    index['historical_V4_to_V1_derivation']=index.pop('derivation')
    index['historical_V4_to_V1_derivation']['scope']='HISTORICAL_V1_RECORD_NOT_V2_SAME_FUNCTION_CLAIM; B2 historical comparator defect documented by new audit'
    records=function_records('stage_phase1_typed_capture_v2.py')
    index['derivation']=dict(original_top_level_functions=14,entire_source_and_AST_same_vs_typed_V1=13,
        changed_complete_functions=['verify_B2_source_closure'],function_source_diff=pin(HERE/'FUNCTION_SOURCE_DIFF.txt'),
        module_source_diff=pin(HERE/'MODULE_SOURCE_DIFF.txt'),function_comparison=pin(HERE/'FUNCTION_SOURCE_DIFF.json'),
        source_generation='UNIQUE_LOCAL_HUNKS_OF_COMPLETE_FROZEN_TYPED_V1_NOT_AST_SLICES',
        current_function_API=records,shared_helpers_complete_functions=17,
        source_protocol_V1_and_producer_ABI_V1_unchanged=True)
    index['historical_V1_metadata_test_provenance']=dict(
        relative='source_phase1_typed_capture_materializer_v1/SOURCE_TEST_RECEIPT_attempt4.json',
        **pin(V1/'SOURCE_TEST_RECEIPT_attempt4.json'),rerun_by_V2=False,V2_metadata_or_native_proof=False)
    index.pop('metadata_only_tests')
    index['history_binding_tests']=dict(receipt='SOURCE_TEST_RECEIPT_attempt1.json',**pin(HERE/'SOURCE_TEST_RECEIPT_attempt1.json'),
        unique_new_tests=6,all_passed=True,only_AST_pure_memory_and_published_source_bytes=True,
        old_nine_case_suite_runs=0,materializer_imports=0,actual_metadata_calls=0,
        old_pinned_text_sources=receipt['old_pinned_text_sources_after'],audit_violations=[])
    index['history_reference_binding']=dict(
        references_file='SOURCE_REFERENCES.json',references_pin=pin(HERE/'SOURCE_REFERENCES.json'),
        expected_root='FIXED_INDEPENDENT_PUBLISHED_B2_RAW_SEAL_2909_BE538A07_NOT_ACTIVE_SENSOR',
        reference_proof=references,
        helper_file='historical_b2_binding_v2.py',helper_source_pin=pin(HERE/'historical_b2_binding_v2.py'),
        helper_API=function_records('historical_b2_binding_v2.py'),
        actual_history_function_calls_by_child=0,arbitrary_claim_or_boolean_sourceproof_accepted=False,
        active_B4_package_verification_whole_source_unchanged=True)
    audit_root=R/'source_phase1_typed_materializer_history_binding_audit_v1'
    index['source_audit']=dict(
        report_relative='source_phase1_typed_materializer_history_binding_audit_v1/AUDIT.md',report=pin(audit_root/'AUDIT.md'),
        evidence_relative='source_phase1_typed_materializer_history_binding_audit_v1/SOURCE_AUDIT.json',evidence=pin(audit_root/'SOURCE_AUDIT.json'),
        independently_verified_real_sources=396,sourceproof_aliases=272,all_source_mapping_aliases=305,
        SourceProof_logical_SHA256='f74f7e5fa02931f155bb55930f35f835f61a28cc7941cb94058c46968a8c6324',
        all_mapping_logical_SHA256='cb8bc8d40e69ef5d8d3c5ed4cab6b24aff2cd1c945cac24fff93178c7678d21b',
        source_only_not_load_sources_execution=True)
    index['review_provenance']=dict(message_ref='m01892',scope='Parent reviewed complete function/module/helper/reference proofs; independent history-only V2 source seal, no runtime approval field or condition',
        compact_wire_change_included=False,parent_final13_modified=False)
    index['future_CLI']['entry']='stage_phase1_typed_capture_v2.py'
    index['stage_protocol']['future_optional_suffix']='_TYPED_V2_'
    index['stage_protocol']['consumed_V1_SOURCE_INPUT_replay']=False
    index['current_source_materializer_entry']=dict(relative='stage_phase1_typed_capture_v2.py',**pin(HERE/'stage_phase1_typed_capture_v2.py'))
    index['actual_B2_builder_calls']=0;index['actual_metadata_calls']=0;index['actual_load_sources_calls']=0
    # The original physical/assets/baseline/stage/CLI contracts and all34 rows
    # are copied as data, not silently regenerated or rewritten to new pins.
    for key in ('typed_publication','finite_active_source_binding','source_mirror','complete_baseline_protocol','shared_helpers'):
        assert index[key]==old[key]
    with (HERE/'SOURCE_INDEX.json').open('xb') as out:
        out.write((json.dumps(index,ensure_ascii=False,indent=2)+'\n').encode())
    print(json.dumps(dict(index=pin(HERE/'SOURCE_INDEX.json'),own_python=9,functions=14,changed_complete_functions=1,
                         SourceMirror396_whole_bytes_unchanged=True,actual_materializer_calls=0)))


if __name__=='__main__':
    main()
