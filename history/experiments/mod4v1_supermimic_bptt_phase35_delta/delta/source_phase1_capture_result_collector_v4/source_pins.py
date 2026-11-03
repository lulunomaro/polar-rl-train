"""Fixed V4 SOURCE inventory plus independent B2 references; no plant imports/calls."""
from pathlib import Path
import ast
import hashlib
import json

HERE = Path(__file__).resolve().parent
R = HERE.parent
WORKER = R/'source_phase1_capture_worker_v4'
SENSOR = R/'source_phase1_passive_sensor_capture_v2'
DIAGNOSTIC = R/'source_phase1_sensor_reset_identity_diagnosis_v1'
INDEX_SHA = '75e36c0255a3b354dd0efeec33600f9b38d51ca28484de2dbed55db865fc7b2d'
INDEX_BYTES = 134423
WORKER_SEAL_SHA = 'ba3409a5450e378ea97eac64f0fec4c3409ac974a4c3378d0c6e6a6cfc405180'
WORKER_ROOT = '758dc867cc4040a6f1eb9f587cc88f69a3866e03a9553290128a1681cda039e8'
WORKER_SEAL_BYTES = 2919
BOUNDARY = R/'source_phase1_boundary_device_contract_v1'
BOUNDARY_SEAL_PIN = dict(path=str(BOUNDARY/'SOURCE_SEAL.json'),bytes=1570,
    SHA256='c9fae49e96b7042863372e7fb681c7c93fd8ce733646908222c9af6f7d306bdc')
BOUNDARY_ROOT = '5b4d0134e8ec0d828adef1fae8156d195ede032eacea2476457a403162e9e106'
BOUNDARY_MEMBERS = {'README.md','boundary_device_contract.py','torch_cpu_fixture.py',
    'test_boundary_device_source.py','seal_source.py','FAKE_TEST_LOG.txt','SOURCE_PINS.json','SOURCE_RECEIPT.json'}
SENSOR_DEPENDENCY_PINS = {
    'phase1_deps/sensor/source_api.py':(31456,'a334766d6a9ca88d02d682e73d70a15e9098f1e77d1aa7a45e6d0154a4b73b62'),
    'phase1_deps/sensor/passive_capture.py':(26599,'4e05fe172068f8ed3e1f438ec73b57e89986e7da8316d16fd764026c8f53da9b'),
    'phase1_deps/sensor/SOURCE_API_MANIFEST.json':(336133,'2801135d1ff028f09a5eb7cd571cc3ca90694b60340d17e62374a42cbe60eaca'),
}
B2_SEAL_PIN = dict(path=str(SENSOR/'SOURCE_SEAL.json'),bytes=2909,
    SHA256='be538a07c8ccfb785023422ace6985e1fde0bd5b885266124e430527c1ec558a')
EXTRA_SOURCE_REFS_READY = True  # final pinned V4 index binds the inherited B2 closure; verified below
BASE_V3_COLLECTOR_SEAL_SHA = '2f6188fe03958bfd237efab6c22ea6f63ffa61c54608144607db5d8bc9ff577f'
BASE_V2_COLLECTOR_SEAL_SHA = '8a0dfd808483687f3a718d327c6dddf77d6989ed140eddc4de6dc262b832c29c'
BASE_COLLECTOR_SEAL_SHA = 'c6847784e4733f53767dc20f064b584eecda02f1046d88855f25d8e8381eca6c'
SEALS = {
    'source_phase1_capture_worker_v4/SOURCE_SEAL.json':WORKER_SEAL_SHA,
    'source_phase1_state_context_partition_v1/SOURCE_SEAL.json':'e7f3d29bc0319fbd9f0d4e1d5a4981edd551b6c47f16431c8545bb86b7756630',
}
WORKER_INPUTS = {
    'phase1_capture_contract.py':(9518,'7910d7f3378923275b430b7960ed833f79b394feb3317c857d3a98c501729a0a'),
    'phase1_capture_observer.py':(10438,'8a6faa66d55d4498fd1249aaabfeb9dfd7bb9e0b01013137adce3756b3c9004c'),
    'phase1_capture_runtime.py':(19145,'490dcb8fd561b8db3af78db29db59d28b6dea33e7a8026609f3d1ddb62a93017'),
    'worker_passive_interface_v1.py':(16326,'25fa00939694f9558c8aa1a9af73a40bf9b6b1cae666e1e636c70e6e8ab2f7e9'),
    'single_gpu_passive_capture_parent_v1.py':(9336,'d5575ff2e670fd18ea0a09d9f3d5c05c46bf606a027fcb84d97c6e34a88a2b41'),
}
WORKER_ALIASES = {'phase1_capture_contract.py','phase1_capture_observer.py','phase1_capture_runtime.py',
    'worker_passive_interface_v1.py','single_gpu_passive_capture_parent_v1.py'}


def identity(path):
    raw = Path(path).read_bytes()
    return dict(bytes=len(raw),SHA256=hashlib.sha256(raw).hexdigest())


def require(ok, message):
    if not ok:
        raise ValueError(message)


def is_digest(value):
    return type(value) is str and len(value) == 64 and all(c in '0123456789abcdef' for c in value)


def source_path(value, *, python_only=False):
    require(type(value) is str and Path(value).is_absolute(), 'absolute SOURCE reference required')
    path = Path(value).resolve()
    require(path.is_relative_to(R.resolve()) and '..' not in Path(value).parts,
        'SOURCE reference outside project')
    require(path.suffix in ('.py','.json','.md') and 'reports' not in path.relative_to(R).parts,
        'SOURCE reference type/scope differs')
    require(not python_only or path.suffix == '.py', 'full original Python SOURCE required')
    return path


def checked_blob(row, *, python_only=False):
    """Hash full owned SOURCE bytes; optionally AST-parse, never import/execute them."""
    path = source_path(row['path'],python_only=python_only)
    require(type(row.get('bytes')) is int and row['bytes'] >= 0 and is_digest(row.get('SHA256')),
        'complete SOURCE reference pin required')
    raw = path.read_bytes()
    require((len(raw),hashlib.sha256(raw).hexdigest()) == (row['bytes'],row['SHA256']),
        'extra SOURCE reference identity differs: '+str(path))
    if python_only:
        ast.parse(raw.decode('utf-8-sig'),filename=str(path))
    return raw


def validate_sensor_rows(index):
    rows = [row for row in index.get('dependency_sources',[])
        if str(row.get('install_relative','')).startswith('phase1_deps/sensor/')]
    require(len(rows) == 3 and {r['install_relative'] for r in rows} == set(SENSOR_DEPENDENCY_PINS),
        'exact three B2 sensor aliases required')
    for row in rows:
        alias = row['install_relative']
        require(Path(row['path']).resolve() == (SENSOR/Path(alias).name).resolve()
            and (row['bytes'],row['SHA256']) == SENSOR_DEPENDENCY_PINS[alias],
            'actual B2 sensor dependency differs: '+alias)
    sensor = index.get('dependency_seals',{}).get('sensor',{})
    require(all(sensor.get(k) == v for k,v in B2_SEAL_PIN.items()), 'final B2 thirteen-member seal pin differs')
    return sensor


def validate_worker_index(index):
    """SOURCE mapping validation, not execution/readback or a new wire contract."""
    require_final_pins()
    require(index.get('kind') == 'PHASE1_CAPTURE_WORKER_SOURCE_INDEX_V1'
        and index.get('source_version') == 4, 'V4 source index/version required')
    require(index.get('source_derivation',{}).get('preserved_V1_typed_protocol') is True,
        'V1 typed protocol preservation required')
    require(len(index.get('original17',[])) == 17 and len(index.get('dependency_sources',[])) == 5,
        'whole original17+dependency5 required')
    rows = index.get('new_sources',[])
    require(len(rows) == 5 and {row.get('install_relative') for row in rows} == set(WORKER_INPUTS),
        'exact five APIv1 aliases required')
    for row in rows:
        alias = row['install_relative']; size,digest = WORKER_INPUTS[alias]
        require(Path(row['path']).resolve() == (WORKER/alias).resolve(),
            'actual V4 worker SOURCE path differs: '+alias)
        require((row['bytes'],row['SHA256']) == (size,digest), 'V4 worker SOURCE identity differs: '+alias)
    validate_sensor_rows(index)
    return index


def require_final_pins():
    require(is_digest(INDEX_SHA) and type(INDEX_BYTES) is int and INDEX_BYTES > 0
        and is_digest(WORKER_SEAL_SHA) and is_digest(WORKER_ROOT)
        and type(WORKER_SEAL_BYTES) is int and WORKER_SEAL_BYTES > 0,
        'FIXED_V4_PINS_PENDING')
    require(type(WORKER_INPUTS) is dict and set(WORKER_INPUTS) == WORKER_ALIASES
        and all(type(v) is tuple and len(v) == 2 and type(v[0]) is int and v[0] > 0
            and is_digest(v[1]) for v in WORKER_INPUTS.values()), 'FIXED_V4_WORKER_INPUTS_PENDING')
    require(EXTRA_SOURCE_REFS_READY is True and type(SENSOR_DEPENDENCY_PINS) is dict
        and len(SENSOR_DEPENDENCY_PINS) == 3 and type(B2_SEAL_PIN) is dict,
        'FIXED_V4_EXTRA_SOURCE_REFS_PENDING')


def read_index():
    require_final_pins()
    path = WORKER/'CAPTURE_SOURCE_INDEX.json'
    raw = path.read_bytes()
    require((len(raw),hashlib.sha256(raw).hexdigest()) == (INDEX_BYTES,INDEX_SHA), 'V4 capture index pin differs')
    return validate_worker_index(json.loads(raw))


def manifest_reference_rows(manifest):
    """Collect declarations only; this is not a reset/binding verifier."""
    references = []; unique = {}
    def visit(value):
        if type(value) is dict:
            if 'source_path' in value or 'source_sha256' in value:
                require('source_path' in value and 'source_sha256' in value,
                    'incomplete manifest SOURCE reference')
                path = str(source_path(value['source_path'],python_only=True)); digest = value['source_sha256']
                require(is_digest(digest), 'manifest SOURCE hash required')
                require(path not in unique or unique[path] == digest, 'conflicting manifest SOURCE reference')
                unique[path] = digest; references.append((path,digest))
            for item in value.values():
                visit(item)
        elif type(value) is list:
            for item in value:
                visit(item)
    visit(manifest)
    return references,unique


def validate_manifest_closure(manifest,closure):
    references,unique = manifest_reference_rows(manifest)
    require(len(references) == closure.get('pin_references') == 435
        and len(unique) == closure.get('unique_full_source_files') == 155,
        'B2 manifest 435 references / 155 unique SOURCE files required')
    rows = closure.get('sources',[])
    expected = {str(source_path(row['path'],python_only=True)):row['SHA256'] for row in rows}
    require(len(rows) == len(expected) == 155 and expected == unique,
        'B2 manifest reference set differs from fixed V4 index')
    return rows


def validate_b2_members(sensor,seal):
    rows = seal.get('files',[])
    require(seal.get('source_only') is True and seal.get('native_enabled') is False
        and seal.get('source_revision') == 2 and len(rows) == 13,
        'B2 SOURCE-only thirteen-member package required')
    members = [dict(relative=row['relative'],bytes=row['bytes'],SHA256=row['sha256']) for row in rows]
    require(members == sensor.get('members'), 'B2 complete member list differs from fixed index')
    for row in members:
        relative = Path(row['relative'])
        require(not relative.is_absolute() and '..' not in relative.parts
            and (SENSOR/relative).resolve().is_relative_to(SENSOR.resolve()), 'B2 member path differs')
    require(sensor.get('content_root_sha256') is None and seal.get('content_root_sha256') is None,
        'upstream B2 root was null; no root inference')
    return [dict(path=str(SENSOR/row['relative']),bytes=row['bytes'],SHA256=row['SHA256']) for row in members]


def diagnostic_rows(index):
    value = index.get('sensor_reset_diagnostic_source_references',{})
    require(value.get('read_only_references_not_runtime_modules') is True
        and value.get('actual_native_binding') == 'NOT_EXECUTED', 'diagnostic SOURCE-only scope required')
    rows = value.get('source_references',[])
    names = {'README.md','SOURCE_DIAGNOSIS.json','SOURCE_EVIDENCE_AUDIT.json','source_evidence_audit.py'}
    require(len(rows) == 4 and {Path(row['path']).name for row in rows} == names,
        'four reset diagnostic SOURCE references required')
    handoff = value.get('final_handoff',{})
    require(Path(handoff.get('path','')).name == 'FINAL_SOURCE_HANDOFF_RECEIPT.json', 'final SOURCE handoff required')
    for row in rows+[handoff]:
        require(source_path(row['path']).parent == DIAGNOSTIC.resolve(), 'diagnostic SOURCE reference path differs')
    return rows,handoff


def verify_extra_source_refs(index):
    """Independent SOURCE hash/AST evidence, kept separate from the fixed fifty."""
    require_final_pins(); validate_worker_index(index)
    inventory = {}
    def add(row, *, python_only=False):
        raw = checked_blob(row,python_only=python_only)
        key = str(Path(row['path']).resolve()); expected = dict(bytes=row['bytes'],SHA256=row['SHA256'])
        require(key not in inventory or inventory[key] == expected, 'conflicting extra SOURCE inventory')
        inventory[key] = expected
        return raw
    sensor = validate_sensor_rows(index)
    seal = json.loads(add(B2_SEAL_PIN))
    for row in validate_b2_members(sensor,seal):
        add(row)
    manifest_row = index.get('sensor_source_manifest',{})
    require(source_path(manifest_row['path']) == (SENSOR/'SOURCE_API_MANIFEST.json').resolve()
        and (manifest_row['bytes'],manifest_row['SHA256']) == SENSOR_DEPENDENCY_PINS['phase1_deps/sensor/SOURCE_API_MANIFEST.json'],
        'B2 source manifest pin differs')
    manifest = json.loads(add(manifest_row))
    require(manifest.get('kind') == 'PASSIVE_SENSOR_SOURCE_API_V1' and manifest.get('source_revision') == 2
        and manifest.get('source_only') is True and manifest.get('native_enabled') is False
        and len(manifest.get('roles',{})) == 8, 'whole eight-role B2 SOURCE manifest required')
    closure_rows = validate_manifest_closure(manifest,manifest_row.get('original_source_closure',{}))
    for row in closure_rows:
        add(row,python_only=True)
    diagnostics,handoff = diagnostic_rows(index)
    for row in diagnostics+[handoff]:
        add(row,python_only=Path(row['path']).suffix == '.py')
    summary = dict(kind='COLLECTOR_V4_INDEPENDENT_B2_SOURCE_REFS_V1',
        B2_seal_SHA256=B2_SEAL_PIN['SHA256'],B2_seal_members_verified=13,
        B2_upstream_content_root_sha256=None,manifest_pin_references_verified=435,
        unique_manifest_Python_sources_full_SHA_AST_verified=155,diagnostic_source_references_verified=4,
        final_SOURCE_handoff_verified=True,extra_unique_file_identities=len(inventory),
        fixed_fifty_is_a_separate_inventory=True,oldSource105_not_used_as_new155_proof=True,
        plant_source_modules_executed=False,B2_wrapper_or_reset_verifier_executed=False,
        reset_verifier_implemented_here=False,upstream_28_or_44_tests_rerun_here=False,
        actual_SSH=False,actual_SDK=False,gate1='UNKNOWN',exact=False,stage2_GO=False)
    return dict(summary=summary,sources=inventory)


def validate_boundary_source_rows(index,seal):
    """Only fixed SOURCE proof references, never a runtime boundary predicate."""
    value = index.get('boundary_device_source_contract',{})
    require(value.get('read_only_fixture_source_not_runtime_dependency') is True
        and value.get('parent_CPU_result') == 'NOT_REPRESENTED_BY_THIS_SOURCE_SEAL'
        and value.get('actual_Torch_CPU_executed_here') is False, 'boundary proof SOURCE-only scope required')
    descriptor = value.get('seal',{})
    require(all(descriptor.get(k) == v for k,v in BOUNDARY_SEAL_PIN.items())
        and descriptor.get('content_root_sha256') == BOUNDARY_ROOT, 'fixed boundary SOURCE seal pin required')
    require(type(seal) is dict and seal.get('kind') == 'PHASE1_BOUNDARY_DEVICE_SOURCE_SEAL_V1'
        and seal.get('source_only') is True and seal.get('frozen') is True
        and seal.get('actual_Torch_CPU_or_SDK') is False
        and seal.get('actual_V3_root_cause_confirmed') is False
        and seal.get('content_root_sha256') == BOUNDARY_ROOT, 'boundary eight-member SOURCE seal required')
    records = seal.get('files',[])
    require(type(records) is list and len(records) == 8
        and all(type(row) is dict and type(row.get('relative')) is str
            and type(row.get('bytes')) is int and row['bytes'] >= 0 and is_digest(row.get('sha256'))
            for row in records)
        and {row['relative'] for row in records} == BOUNDARY_MEMBERS,
        'exact eight boundary SOURCE members required')
    normalized = [dict(relative=row['relative'],bytes=row['bytes'],SHA256=row['sha256']) for row in records]
    require(normalized == descriptor.get('members'), 'boundary SOURCE member identities differ')
    contract = value.get('source_contract',{})
    require(contract.get('kind') == 'PHASE1_BOUNDARY_DEVICE_SOURCE_CONTRACT_V1'
        and contract.get('source_only') is True
        and contract.get('cause_status') == 'SOURCE_CANDIDATE_NOT_ACTUAL_V3_ROOT_CAUSE_CONFIRMED'
        and contract.get('actual_V3_flags_shape_dtype_device') is None
        and contract.get('actual_env_device_type') is None
        and contract.get('Torch_CPU_fixture_executed_here') is False
        and contract.get('SDK_or_native_executed_here') is False,
        'boundary source candidate is not actual flag or root-cause evidence')
    aliases = index.get('original17',[])+index.get('new_sources',[])+index.get('dependency_sources',[])
    require(not any(Path(row['path']).resolve().is_relative_to(BOUNDARY.resolve()) for row in aliases),
        'boundary proof SOURCE references are not runtime aliases')
    return [dict(BOUNDARY_SEAL_PIN)]+[dict(path=str(BOUNDARY/row['relative']),
        bytes=row['bytes'],SHA256=row['SHA256']) for row in normalized]


def verify_boundary_source_refs(index):
    """Hash 9 independent proof files; AST only, no fixture/canonical import or CPU run."""
    require_final_pins(); validate_worker_index(index)
    seal = json.loads(checked_blob(BOUNDARY_SEAL_PIN))
    rows = validate_boundary_source_rows(index,seal)
    inventory = {}; python_count = 0
    for row in rows:
        path = Path(row['path']).resolve()
        require(path.parent == BOUNDARY.resolve(), 'boundary SOURCE member path differs')
        raw = path.read_bytes()
        require((len(raw),hashlib.sha256(raw).hexdigest()) == (row['bytes'],row['SHA256']),
            'boundary SOURCE member identity differs: '+str(path))
        if path.suffix == '.py':
            ast.parse(raw.decode('utf-8-sig'),filename=str(path)); python_count += 1
        inventory[str(path)] = dict(bytes=row['bytes'],SHA256=row['SHA256'])
    require(len(inventory) == 9 and python_count == 4, 'boundary 9 SOURCE refs / 4 Python ASTs required')
    summary = dict(kind='COLLECTOR_V4_INDEPENDENT_BOUNDARY_SOURCE_REFS_V1',
        SOURCE_seal_SHA256=BOUNDARY_SEAL_PIN['SHA256'],content_root_sha256=BOUNDARY_ROOT,
        sealed_members_verified=8,independent_SOURCE_file_identities=9,Python_sources_AST_parsed=4,
        not_in_runtime_27_aliases=True,not_counted_as_fixed50_or_B2_extra174=True,
        boundary_or_canonical_code_imported_here=False,Torch_CPU_fixture_executed_here=False,
        parent_CPU_result_read_or_used=False,upstream_11_tests_rerun_here=False,
        actual_reports_read=False,actual_V3_flags_shape_dtype_device=None,
        actual_V3_root_cause_confirmed=False,actual_SSH=False,actual_SDK=False,
        gate1='UNKNOWN',exact=False,stage2_GO=False)
    return dict(summary=summary,sources=inventory)


def verify_base_collector():
    """Old V1/V2 and immediate V3 derivations; neither added to the fifty runtime inputs."""
    result = {}
    for version,digest in ((1,BASE_COLLECTOR_SEAL_SHA),(2,BASE_V2_COLLECTOR_SEAL_SHA),(3,BASE_V3_COLLECTOR_SEAL_SHA)):
        path = R/('source_phase1_capture_result_collector_v'+str(version))/'SOURCE_SEAL.json'
        require(identity(path)['SHA256'] == digest, 'old collector seal changed: '+str(version))
        rows = json.loads(path.read_bytes())['files']
        require(len(rows) == 9, 'old collector nine members required: '+str(version))
        for row in rows:
            require(identity(path.parent/row['relative']) == dict(bytes=row['bytes'],SHA256=row['sha256']),
                'old collector sealed member changed: '+str(version)+':'+row['relative'])
        result['base_v'+str(version)+'_collector_members_unchanged'] = 9
        result['base_v'+str(version)+'_collector_seal_SHA256'] = digest
    return result


def build_pins():
    require_final_pins()
    target = HERE/'SOURCE_PINS.json'
    require(not target.exists(), 'source pins already frozen')
    base = verify_base_collector(); rows = {}; counts = {}
    def add(path):
        path = Path(path).resolve(); rows[str(path)] = identity(path)
    for relative,digest in SEALS.items():
        path = R/relative; add(path)
        require(identity(path)['SHA256'] == digest, 'sealed source differs: '+relative)
        seal = json.loads(path.read_bytes()); records = seal['files']
        if type(records) is dict:
            records = [dict(relative=n,**v) for n,v in records.items()]
        counts[relative] = len(records)
        if path.parent == WORKER:
            require(identity(path)['bytes'] == WORKER_SEAL_BYTES and seal.get('source_version') == 4
                and seal.get('content_root_sha256') == WORKER_ROOT and len(records) == 13,
                'final V4 thirteen-member seal required')
        for row in records:
            member = path.parent/row['relative']; add(member)
            require(identity(member) == dict(bytes=row['bytes'],SHA256=row['sha256']),
                'sealed member changed: '+str(member))
    index = read_index(); add(WORKER/'CAPTURE_SOURCE_INDEX.json')
    for row in index['original17']+index['new_sources']+index['dependency_sources']:
        add(row['path'])
        require(identity(row['path']) == dict(bytes=row['bytes'],SHA256=row['SHA256']),
            'source mapping differs: '+row['install_relative'])
    reference = R/'dispatch_phase1_e3_capture_original_parent_v1_once.py'
    for path in (R/'source_phase1_capture_controller_v1/phase1_capture_parent_actual_wait_controller_v1.py',
                 R/'source_phase1_capture_controller_v1/SOURCE_SEAL.json',reference,
                 R.parent/'mod4v1_experts_fulldr_rm70_20261101/project_connector.py'):
        add(path)
    require(len(rows) == 50, 'exact fifty V4 source inputs required')
    extra = verify_extra_source_refs(index)
    boundary = verify_boundary_source_refs(index)
    value = dict(kind='CAPTURE_COLLECTOR_FIXED_SOURCE_PINS_V4',source_version=4,typed_API_version=1,
        sources=rows,old_member_counts=counts,source_closure_aliases=27,
        worker_index_SHA256=INDEX_SHA,worker_source_root_sha256=WORKER_ROOT,
        source_derivation=base,static_reference_only=[str(reference.resolve())],
        extra_source_refs=extra,boundary_source_refs=boundary,future_dispatcher_source_not_a_runtime_pin=True,
        original_partition_nine_unchanged=True,no_connector_called=True,no_actual_collection=True)
    with target.open('x',encoding='utf-8') as stream:
        json.dump(value,stream,indent=2,allow_nan=False)
    return value


def verify_sources():
    require_final_pins()
    base = verify_base_collector(); index = read_index()
    value = json.loads((HERE/'SOURCE_PINS.json').read_bytes())
    require(value.get('kind') == 'CAPTURE_COLLECTOR_FIXED_SOURCE_PINS_V4'
        and value.get('source_version') == 4 and value.get('worker_index_SHA256') == INDEX_SHA,
        'frozen V4 collector pins required')
    require(len(value['sources']) == 50 and value['old_member_counts'] == {
        'source_phase1_capture_worker_v4/SOURCE_SEAL.json':13,
        'source_phase1_state_context_partition_v1/SOURCE_SEAL.json':9}, 'V4 fixed source inventory differs')
    for path,expected in value['sources'].items():
        require(identity(path) == expected, 'fixed source pin changed: '+path)
    extra = verify_extra_source_refs(index)
    require(extra == value.get('extra_source_refs'), 'independent new B2 SOURCE references differ')
    boundary = verify_boundary_source_refs(index)
    require(boundary == value.get('boundary_source_refs'), 'independent boundary SOURCE references differ')
    return dict(source_count=len(value['sources']),old_member_counts=value['old_member_counts'],
        original_partition_nine_unchanged=True,source_version=4,worker_index_SHA256=INDEX_SHA,
        extra_source_refs=extra['summary'],boundary_source_refs=boundary['summary'],**base)


if __name__ == '__main__':
    value = verify_sources() if (HERE/'SOURCE_PINS.json').exists() else build_pins()
    print(json.dumps(dict(source_count=len(value.get('sources',{})) or value.get('source_count'),
        extra_source_refs=value['extra_source_refs'].get('summary',value['extra_source_refs']),
        boundary_source_refs=value['boundary_source_refs'].get('summary',value['boundary_source_refs']),
        source_version=4,actual_collection=False)))
