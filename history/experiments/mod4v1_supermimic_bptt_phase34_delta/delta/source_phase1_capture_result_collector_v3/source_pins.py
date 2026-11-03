"""Fixed V3 SOURCE inventory plus independent B2 references; no plant imports/calls."""
from pathlib import Path
import ast
import hashlib
import json

HERE = Path(__file__).resolve().parent
R = HERE.parent
WORKER = R/'source_phase1_capture_worker_v3'
SENSOR = R/'source_phase1_passive_sensor_capture_v2'
DIAGNOSTIC = R/'source_phase1_sensor_reset_identity_diagnosis_v1'
INDEX_SHA = 'bdeea3f057fb922bd9ae2670dcbf19188f651ca64ab2cbb0331f56a5a1124797'
INDEX_BYTES = 124202
WORKER_SEAL_SHA = '80b27d160b68cc67d38fe406b3507f2df10621a054ab237e758fd6e1af1061da'
WORKER_ROOT = 'b1b6ec96f93561d201c307cab9b17fbdc8591c6e362cef45a29ee63419f87963'
WORKER_SEAL_BYTES = 2920
SENSOR_DEPENDENCY_PINS = {
    'phase1_deps/sensor/source_api.py':(31456,'a334766d6a9ca88d02d682e73d70a15e9098f1e77d1aa7a45e6d0154a4b73b62'),
    'phase1_deps/sensor/passive_capture.py':(26599,'4e05fe172068f8ed3e1f438ec73b57e89986e7da8316d16fd764026c8f53da9b'),
    'phase1_deps/sensor/SOURCE_API_MANIFEST.json':(336133,'2801135d1ff028f09a5eb7cd571cc3ca90694b60340d17e62374a42cbe60eaca'),
}
B2_SEAL_PIN = dict(path=str(SENSOR/'SOURCE_SEAL.json'),bytes=2909,
    SHA256='be538a07c8ccfb785023422ace6985e1fde0bd5b885266124e430527c1ec558a')
EXTRA_SOURCE_REFS_READY = True
BASE_V2_COLLECTOR_SEAL_SHA = '8a0dfd808483687f3a718d327c6dddf77d6989ed140eddc4de6dc262b832c29c'
BASE_COLLECTOR_SEAL_SHA = 'c6847784e4733f53767dc20f064b584eecda02f1046d88855f25d8e8381eca6c'
SEALS = {
    'source_phase1_capture_worker_v3/SOURCE_SEAL.json':WORKER_SEAL_SHA,
    'source_phase1_state_context_partition_v1/SOURCE_SEAL.json':'e7f3d29bc0319fbd9f0d4e1d5a4981edd551b6c47f16431c8545bb86b7756630',
}
WORKER_INPUTS = {
    'phase1_capture_contract.py':(9518,'7910d7f3378923275b430b7960ed833f79b394feb3317c857d3a98c501729a0a'),
    'phase1_capture_observer.py':(10438,'8a6faa66d55d4498fd1249aaabfeb9dfd7bb9e0b01013137adce3756b3c9004c'),
    'phase1_capture_runtime.py':(19145,'490dcb8fd561b8db3af78db29db59d28b6dea33e7a8026609f3d1ddb62a93017'),
    'worker_passive_interface_v1.py':(16323,'f2b7326efb546f0a274c978aa69c126506ed0d3c3a8a1792d80893fa9f163b0b'),
    'single_gpu_passive_capture_parent_v1.py':(9336,'d5575ff2e670fd18ea0a09d9f3d5c05c46bf606a027fcb84d97c6e34a88a2b41'),
}


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
    require(index.get('kind') == 'PHASE1_CAPTURE_WORKER_SOURCE_INDEX_V1'
        and index.get('source_version') == 3, 'V3 source index/version required')
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
            'actual V3 worker SOURCE path differs: '+alias)
        require((row['bytes'],row['SHA256']) == (size,digest), 'V3 worker SOURCE identity differs: '+alias)
    validate_sensor_rows(index)
    return index


def require_final_pins():
    require(is_digest(INDEX_SHA) and type(INDEX_BYTES) is int and INDEX_BYTES > 0
        and is_digest(WORKER_SEAL_SHA) and is_digest(WORKER_ROOT)
        and type(WORKER_SEAL_BYTES) is int and WORKER_SEAL_BYTES > 0,
        'FIXED_V3_PINS_PENDING')
    require(EXTRA_SOURCE_REFS_READY is True and type(SENSOR_DEPENDENCY_PINS) is dict
        and len(SENSOR_DEPENDENCY_PINS) == 3 and type(B2_SEAL_PIN) is dict,
        'FIXED_V3_EXTRA_SOURCE_REFS_PENDING')


def read_index():
    require_final_pins()
    path = WORKER/'CAPTURE_SOURCE_INDEX.json'
    raw = path.read_bytes()
    require((len(raw),hashlib.sha256(raw).hexdigest()) == (INDEX_BYTES,INDEX_SHA), 'V3 capture index pin differs')
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
        'B2 manifest reference set differs from fixed V3 index')
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
    summary = dict(kind='COLLECTOR_V3_INDEPENDENT_B2_SOURCE_REFS_V1',
        B2_seal_SHA256=B2_SEAL_PIN['SHA256'],B2_seal_members_verified=13,
        B2_upstream_content_root_sha256=None,manifest_pin_references_verified=435,
        unique_manifest_Python_sources_full_SHA_AST_verified=155,diagnostic_source_references_verified=4,
        final_SOURCE_handoff_verified=True,extra_unique_file_identities=len(inventory),
        fixed_fifty_is_a_separate_inventory=True,oldSource105_not_used_as_new155_proof=True,
        plant_source_modules_executed=False,B2_wrapper_or_reset_verifier_executed=False,
        reset_verifier_implemented_here=False,upstream_28_or_44_tests_rerun_here=False,
        actual_SSH=False,actual_SDK=False,gate1='UNKNOWN',exact=False,stage2_GO=False)
    return dict(summary=summary,sources=inventory)


def verify_base_collector():
    """Old V1 and immediate V2 derivations; neither added to the fifty runtime inputs."""
    result = {}
    for version,digest in ((1,BASE_COLLECTOR_SEAL_SHA),(2,BASE_V2_COLLECTOR_SEAL_SHA)):
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
            require(identity(path)['bytes'] == WORKER_SEAL_BYTES and seal.get('source_version') == 3
                and seal.get('content_root_sha256') == WORKER_ROOT and len(records) == 13,
                'final V3 thirteen-member seal required')
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
    require(len(rows) == 50, 'exact fifty V3 source inputs required')
    extra = verify_extra_source_refs(index)
    value = dict(kind='CAPTURE_COLLECTOR_FIXED_SOURCE_PINS_V3',source_version=3,typed_API_version=1,
        sources=rows,old_member_counts=counts,source_closure_aliases=27,
        worker_index_SHA256=INDEX_SHA,worker_source_root_sha256=WORKER_ROOT,
        source_derivation=base,static_reference_only=[str(reference.resolve())],
        extra_source_refs=extra,future_dispatcher_source_not_a_runtime_pin=True,
        original_partition_nine_unchanged=True,no_connector_called=True,no_actual_collection=True)
    with target.open('x',encoding='utf-8') as stream:
        json.dump(value,stream,indent=2,allow_nan=False)
    return value


def verify_sources():
    require_final_pins()
    base = verify_base_collector(); index = read_index()
    value = json.loads((HERE/'SOURCE_PINS.json').read_bytes())
    require(value.get('kind') == 'CAPTURE_COLLECTOR_FIXED_SOURCE_PINS_V3'
        and value.get('source_version') == 3 and value.get('worker_index_SHA256') == INDEX_SHA,
        'frozen V3 collector pins required')
    require(len(value['sources']) == 50 and value['old_member_counts'] == {
        'source_phase1_capture_worker_v3/SOURCE_SEAL.json':13,
        'source_phase1_state_context_partition_v1/SOURCE_SEAL.json':9}, 'V3 fixed source inventory differs')
    for path,expected in value['sources'].items():
        require(identity(path) == expected, 'fixed source pin changed: '+path)
    extra = verify_extra_source_refs(index)
    require(extra == value.get('extra_source_refs'), 'independent new B2 SOURCE references differ')
    return dict(source_count=len(value['sources']),old_member_counts=value['old_member_counts'],
        original_partition_nine_unchanged=True,source_version=3,worker_index_SHA256=INDEX_SHA,
        extra_source_refs=extra['summary'],**base)


if __name__ == '__main__':
    value = verify_sources() if (HERE/'SOURCE_PINS.json').exists() else build_pins()
    print(json.dumps(dict(source_count=len(value.get('sources',{})) or value.get('source_count'),
        extra_source_refs=value['extra_source_refs'].get('summary',value['extra_source_refs']),
        source_version=3,actual_collection=False)))
