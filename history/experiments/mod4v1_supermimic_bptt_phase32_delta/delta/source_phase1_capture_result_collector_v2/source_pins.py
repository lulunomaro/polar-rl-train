"""Fixed V2 SOURCE inputs; APIv1 aliases stay unchanged. No remote/native calls."""
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
R = HERE.parent
WORKER = R/'source_phase1_capture_worker_v2'
INDEX_SHA = 'cdb2ca55c08a544cd01e462b7ce27261900f3b6ebaffb4784350717f756b7cf7'
INDEX_BYTES = 65961
WORKER_SEAL_SHA = 'caacf07e8bc46bd2cc5f4fa14138782430d86de4f6382bbb35adcdcde5d469d5'
WORKER_ROOT = '83cb35d61298fdac4d2c720d1322ada0fbfa43b866709b4e5958b99ac82b62d2'
BASE_COLLECTOR_SEAL_SHA = 'c6847784e4733f53767dc20f064b584eecda02f1046d88855f25d8e8381eca6c'
SEALS = {
    'source_phase1_capture_worker_v2/SOURCE_SEAL.json':WORKER_SEAL_SHA,
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


def validate_worker_index(index):
    """SOURCE mapping validation, not execution/readback or a new wire contract."""
    require(index.get('kind') == 'PHASE1_CAPTURE_WORKER_SOURCE_INDEX_V1'
        and index.get('source_version') == 2, 'V2 source index/version required')
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
            'actual V2 worker SOURCE path differs: '+alias)
        require((row['bytes'],row['SHA256']) == (size,digest), 'V2 worker SOURCE identity differs: '+alias)
    return index


def read_index():
    path = WORKER/'CAPTURE_SOURCE_INDEX.json'
    raw = path.read_bytes()
    require((len(raw),hashlib.sha256(raw).hexdigest()) == (INDEX_BYTES,INDEX_SHA), 'V2 capture index pin differs')
    return validate_worker_index(json.loads(raw))


def verify_base_collector():
    """Separate derivation/preservation check; not added to the 50 runtime sources."""
    path = R/'source_phase1_capture_result_collector_v1/SOURCE_SEAL.json'
    require(identity(path)['SHA256'] == BASE_COLLECTOR_SEAL_SHA, 'V1 collector seal changed')
    seal = json.loads(path.read_bytes()); rows = seal['files']
    require(len(rows) == 9, 'V1 collector nine members required')
    for row in rows:
        require(identity(path.parent/row['relative']) == dict(bytes=row['bytes'],SHA256=row['sha256']),
            'V1 collector sealed member changed: '+row['relative'])
    return dict(base_v1_collector_members_unchanged=9,base_v1_collector_seal_SHA256=BASE_COLLECTOR_SEAL_SHA)


def build_pins():
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
            require(identity(path)['bytes'] == 2815 and seal.get('source_version') == 2
                and seal.get('content_root_sha256') == WORKER_ROOT and len(records) == 13,
                'final V2 thirteen-member seal required')
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
    require(len(rows) == 50, 'exact fifty V2 source inputs required')
    value = dict(kind='CAPTURE_COLLECTOR_FIXED_SOURCE_PINS_V2',source_version=2,typed_API_version=1,
        sources=rows,old_member_counts=counts,source_closure_aliases=27,
        worker_index_SHA256=INDEX_SHA,worker_source_root_sha256=WORKER_ROOT,
        source_derivation=base,static_reference_only=[str(reference.resolve())],
        future_dispatcher_source_not_a_runtime_pin=True,original_partition_nine_unchanged=True,
        no_connector_called=True,no_actual_collection=True)
    with target.open('x',encoding='utf-8') as stream:
        json.dump(value,stream,indent=2,allow_nan=False)
    return value


def verify_sources():
    base = verify_base_collector(); read_index()
    value = json.loads((HERE/'SOURCE_PINS.json').read_bytes())
    require(value.get('kind') == 'CAPTURE_COLLECTOR_FIXED_SOURCE_PINS_V2'
        and value.get('source_version') == 2 and value.get('worker_index_SHA256') == INDEX_SHA,
        'frozen V2 collector pins required')
    require(len(value['sources']) == 50 and value['old_member_counts'] == {
        'source_phase1_capture_worker_v2/SOURCE_SEAL.json':13,
        'source_phase1_state_context_partition_v1/SOURCE_SEAL.json':9}, 'V2 fixed source inventory differs')
    for path,expected in value['sources'].items():
        require(identity(path) == expected, 'fixed source pin changed: '+path)
    return dict(source_count=len(value['sources']),old_member_counts=value['old_member_counts'],
        original_partition_nine_unchanged=True,source_version=2,worker_index_SHA256=INDEX_SHA,**base)


if __name__ == '__main__':
    value = verify_sources() if (HERE/'SOURCE_PINS.json').exists() else build_pins()
    print(json.dumps(dict(source_count=len(value.get('sources',{})) or value.get('source_count'),
                         source_version=2,actual_collection=False)))
