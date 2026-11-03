"""Fixed local SOURCE inputs only, never remote/native/credential collection."""
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
R = HERE.parent
SEALS = {
    'source_phase1_capture_worker_v1/SOURCE_SEAL.json':'3f713457c5d66c44ad1fe962ff954e6f65f87afedfef1d6e5bb7fa608e76bea7',
    'source_phase1_state_context_partition_v1/SOURCE_SEAL.json':'e7f3d29bc0319fbd9f0d4e1d5a4981edd551b6c47f16431c8545bb86b7756630',
}
INDEX_SHA = '234f8a3d0baf2a84338e9a0bf2170510f99d33c416654bf23b47bc3b5b5aa5ad'


def identity(path):
    raw = Path(path).read_bytes()
    return dict(bytes=len(raw),SHA256=hashlib.sha256(raw).hexdigest())


def build_pins():
    target = HERE/'SOURCE_PINS.json'
    if target.exists():
        raise ValueError('source pins already frozen')
    rows = {}; counts = {}
    def add(path):
        path = Path(path).resolve(); rows[str(path)] = identity(path)
    for relative, digest in SEALS.items():
        path = R/relative; add(path)
        if identity(path)['SHA256'] != digest:
            raise ValueError('old seal differs: '+relative)
        seal = json.loads(path.read_bytes()); files = seal['files']
        records = files if type(files) is list else [dict(relative=n,**v) for n,v in files.items()]
        counts[relative] = len(records)
        for row in records:
            member = path.parent/row['relative']; add(member)
            if identity(member) != dict(bytes=row['bytes'],SHA256=row['sha256']):
                raise ValueError('old sealed member changed: '+str(member))
    index_path = R/'source_phase1_capture_worker_v1/CAPTURE_SOURCE_INDEX.json'; add(index_path)
    if identity(index_path)['SHA256'] != INDEX_SHA:
        raise ValueError('capture index pin differs')
    index = json.loads(index_path.read_bytes())
    for row in index['original17']+index['new_sources']+index['dependency_sources']:
        add(row['path'])
        if identity(row['path']) != dict(bytes=row['bytes'],SHA256=row['SHA256']):
            raise ValueError('source mapping differs: '+row['install_relative'])
    for path in (R/'source_phase1_capture_controller_v1/phase1_capture_parent_actual_wait_controller_v1.py',
                 R/'source_phase1_capture_controller_v1/SOURCE_SEAL.json',
                 R/'dispatch_phase1_e3_capture_original_parent_v1_once.py',
                 R.parent/'mod4v1_experts_fulldr_rm70_20261101/project_connector.py'):
        add(path)
    value = dict(kind='CAPTURE_COLLECTOR_FIXED_SOURCE_PINS_V1',sources=rows,old_member_counts=counts,
        source_closure_aliases=27,original_partition_nine_unchanged=True,
        no_connector_called=True,no_actual_collection=True)
    with target.open('x',encoding='utf-8') as stream:
        json.dump(value,stream,indent=2,allow_nan=False)
    return value


def verify_sources():
    value = json.loads((HERE/'SOURCE_PINS.json').read_bytes())
    for path, expected in value['sources'].items():
        if identity(path) != expected:
            raise ValueError('fixed source pin changed: '+path)
    return dict(source_count=len(value['sources']),old_member_counts=value['old_member_counts'],
                original_partition_nine_unchanged=True)


if __name__ == '__main__':
    value = verify_sources() if (HERE/'SOURCE_PINS.json').exists() else build_pins()
    print(json.dumps(dict(source_count=len(value.get('sources',{})) or value.get('source_count'),
                         actual_collection=False)))
