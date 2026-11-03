"""Explicit SOURCE seal only. Compile source, retain tests; never execute Torch/native."""
import ast
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

def sha(raw): return hashlib.sha256(raw).hexdigest()
def receipt(path, raw=None):
    raw = path.read_bytes() if raw is None else raw
    return dict(path=str(path), bytes=len(raw), SHA256=sha(raw))
def put(name, value):
    with (HERE/name).open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False); stream.write('\n')

def run():
    assert HERE.name == 'source_bound_only_frozen_probe_v1'
    names = ['CPU_SOURCE_TEST_HISTORY_V1.json','AUDIT_INPUTS_SHA256_V1.json',
             'SOURCE_REVIEW_VERIFICATION_V1.json','DELIVERABLES_SHA256_V1.json']
    assert all(not (HERE/name).exists() for name in names)
    index_path = ROOT/'payload_frozen_microbatch_v2/MICROBATCH_STAGE_INDEX_V2.json'
    index_raw = index_path.read_bytes(); index = json.loads(index_raw)
    assert (len(index_raw),sha(index_raw)) == (4886,'69688e86528e400f188de3f147614cde5c66f86985adaceed805af800819dc50')
    inputs = [receipt(index_path,index_raw)]
    for item in index['entries']:
        path = Path(item['path']).resolve()
        assert path.is_relative_to(ROOT) and path.suffix == '.py'
        raw = path.read_bytes()
        assert len(raw) == item['bytes'] and sha(raw) == item['SHA256'], str(path)
        inputs.append(dict(receipt(path,raw), original_stage_alias=item['relative'], pinned_unchanged=True))
    assert len(index['entries']) == 14
    for name in ('QUALIFIED_E3_W35_REFERENCE_CANDIDATE_SCREEN_V1.json',
                 'QUALIFIED_EMBEDDED_TEACHER_ORIGINAL_SKILL_BASELINE_V1.json',
                 'BOUND_ONLY_FROZEN_CPU_V1.json'):
        path=ROOT/'reports'/name; raw=path.read_bytes(); json.loads(raw)
        inputs.append(receipt(path,raw))
    original = json.loads((ROOT/'reports/BOUND_ONLY_FROZEN_CPU_V1.json').read_text(encoding='utf-8'))
    actual=original['receipt']; assert actual == json.loads(original['stdout'])
    assert original['returncode']==0 and actual['passed'] is True
    assert actual['maximum_independent_bound_formula_error']==0.
    assert actual['maximum_action_component_difference_vs_clipped_teacher'] <= .050001
    assert actual['probe_subforwards']==dict(teacher=4,residual=4)
    assert original['native_steps']==original['original_model_reads']==original['probe_training_updates']==0
    for item in original['source_pins'].values(): assert type(item['bytes']) is int
    for name,item in original['source_pins'].items():
        raw=(HERE/name).read_bytes(); assert len(raw)==item['bytes'] and sha(raw)==item['SHA']
    for key in ('full_strict_state_norm_and_teacher_values_match','constructor_zeroing_did_not_erase_loaded_weights',
                'inherited_act_history_boundary_match','caller_RNG_unchanged','teacher_STD_guard_detected',
                'sticky_failure_detected','isolated_residual_norm_guard_detected'):
        assert actual[key] is True, key
    tested=[]
    for name,count in [('CPU_TEST_RESULTS_V1.json',47),('CPU_TEST_RESULTS_WITH_ROUTE_V1.json',52)]:
        value=json.loads((HERE/name).read_text(encoding='utf-8'))
        assert value['testsRun']==count and value['passed'] is True
        assert value['failures']==value['errors']==0 and value['torch_imported'] is False
        tested.append(dict(file=name, **value))
    field=json.loads((HERE/'BOUND_ONLY_SOURCE_FIELDS_CONTRACT_V1.json').read_text(encoding='utf-8'))
    assert field['native_enabled'] is False and field['full_native_stage_index_supplied'] is False
    assert field['actual_Torch_CPU_fixture_result']['passed'] is True
    assert field['actual_native_admission_wait_close_or_probe_skill'] is None
    assert field['relative_or_causal_effect'] is field['training_benefit'] is None
    for item in field['new_source_files']:
        raw=(HERE/item['relative']).read_bytes()
        assert len(raw)==item['bytes'] and sha(raw)==item['SHA256']
    compiled=[]
    for name in ['bound_only_frozen_probe_v1.py','bound_only_frozen_route_v1.py',
                 'remote_cpu_bound_only_synthetic_v1.py','test_bound_only_probe_stdlib_v1.py',Path(__file__).name]:
        source=(HERE/name).read_text(encoding='utf-8'); ast.parse(source)
        compile(source,str(HERE/name),'exec'); compiled.append(name)
    text=(HERE/'BOUND_ONLY_ZERO_UPDATE_SOURCE_V1.md').read_text(encoding='utf-8')
    assert '实际Torch CPU probe软件验证已PASS' in text and '父已独立运行' in text
    links=[]
    for target in re.findall(r'\]\(<([^>]+)>\)',text):
        value=target.split('#',1); path=Path(value[0]).resolve()
        assert path.is_relative_to(ROOT), target
        raw=path.read_bytes()
        if len(value)==2:
            match=re.fullmatch(r'L(\d+)(?:-L(\d+))?',value[1]); assert match, target
            first=int(match[1]); last=int(match[2] or match[1])
            assert 1<=first<=last<=len(raw.decode('utf-8-sig').splitlines()), target
        links.append(target)
    put('CPU_SOURCE_TEST_HISTORY_V1.json',dict(kind='SOURCE_AND_PARENT_SOFTWARE_CPU_HISTORY_V1',
        scalar_AST_fake_runs=tested, first_failure=None,
        parent_Torch_CPU_report=receipt(ROOT/'reports/BOUND_ONLY_FROZEN_CPU_V1.json'),
        parent_Torch_CPU_passed=True, parent_Torch_CPU_is_own_synthetic_only=True,
        child_Torch_or_native_executions=0, child_tests_not_blindly_rerun=True,
        actual_skill_or_training_effect=None))
    put('AUDIT_INPUTS_SHA256_V1.json',dict(kind='BOUNDED_SOURCE_METADATA_INPUT_PINS_V1',
        entries=inputs, source_files_and_metadata_only=True, no_models_raw_C_or_runtime_scans=True))
    put('SOURCE_REVIEW_VERIFICATION_V1.json',dict(kind='SOURCE_ONLY_BOUND_PROBE_SEAL_VERIFICATION_V1',
        passed=True, input_files=len(inputs), old_fourteen_stage_source_pins_unchanged=True,
        documentation_links_checked=len(links), compiled_own_Python_only=compiled,
        scalar_AST_fake_tests=52, parent_actual_Torch_CPU_passed=True,
        source_implemented=True, native_enabled=False, full_native_stage_index_supplied=False,
        native_admission_wait_close_skill_or_training_effect=None,
        no_child_SDK_Torch_GPU_PT_raw_SSH_C_locks_Git_or_native_operations=True))
    deliverables=['bound_only_frozen_probe_v1.py','bound_only_frozen_route_v1.py',
        'remote_cpu_bound_only_synthetic_v1.py','test_bound_only_probe_stdlib_v1.py',
        'CPU_TEST_RESULTS_V1.json','CPU_TEST_RESULTS_WITH_ROUTE_V1.json',
        'BOUND_ONLY_SOURCE_FIELDS_CONTRACT_V1.json','BOUND_ONLY_ZERO_UPDATE_SOURCE_V1.md',
        Path(__file__).name]+names[:-1]
    entries=[dict(relative=name, **receipt(HERE/name)) for name in sorted(deliverables)]
    material='\n'.join(f"{i['relative']}\t{i['bytes']}\t{i['SHA256']}" for i in entries).encode('utf-8')
    put('DELIVERABLES_SHA256_V1.json',dict(kind='SOURCE_ONLY_SEALED_ZERO_UPDATE_BOUND_PROBE_V1',
        created_utc=datetime.now(timezone.utc).isoformat(), entries=entries,
        canonical_bundle_SHA256=sha(material), native_enabled=False,
        actual_native_skill_or_training_effect=None))
    print(json.dumps(dict(passed=True,manifest=receipt(HERE/'DELIVERABLES_SHA256_V1.json'),
        entries=len(entries), canonical_bundle_SHA256=sha(material),inputs=len(inputs),
        documentation_links=len(links),tests=52,parent_CPU_passed=True,native_enabled=False),indent=2))

if __name__=='__main__': run()
