"""NEW V4 stdlib source seal: one-time create, otherwise read-only verify.

Does not import the codec/observer/tests, call an SDK, or read any actual report.
"""
import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
FILES = (
    'CODEC_SOURCE_PINS.json', 'FAILURE_RECORD.json', 'README.md',
    'SOURCE_AFTER_attempt1.json', 'SOURCE_AFTER_attempt2.json', 'SOURCE_API_CONTRACT.json',
    'SOURCE_BEFORE.json', 'SOURCE_DIFF.md', 'SOURCE_DIFF.patch',
    'STDLIB_TEST_LOG_attempt1.txt', 'STDLIB_TEST_LOG_attempt2.txt',
    'STDLIB_TEST_RECEIPT_attempt1.json', 'STDLIB_TEST_RECEIPT_attempt2.json',
    'dependency_contract.py', 'fake_tensor.py', 'field_snapshot.py', 'passive_capture.py',
    'run_stdlib_tests.py', 'source_api.py', 'test_dependency_contract_v4.py', 'verify_seal.py',
)

def digest(data):
    return hashlib.sha256(data).hexdigest()


def inventory():
    return {name: dict(bytes=len((HERE / name).read_bytes()), sha256=digest((HERE / name).read_bytes()))
            for name in FILES}


def original_guard():
    before = json.loads((HERE / 'SOURCE_BEFORE.json').read_text(encoding='utf-8'))
    assert before['old_source_and_seal_files'] == 41
    for name, expected in before['files'].items():
        data = Path(name).read_bytes()
        assert dict(bytes=len(data), sha256=digest(data)) == expected, name
    root = digest(json.dumps(before['files'], sort_keys=True, separators=(',', ':')).encode())
    assert root == before['manifest_sha256'] == '34345662be0e30cfb08d2598d7e3e36c7f11c24796805ab8ae0285444ac12fbe'
    return root


def evidence_guard():
    receipt = json.loads((HERE / 'STDLIB_TEST_RECEIPT_attempt2.json').read_text(encoding='utf-8'))
    assert receipt['status'] == 'PASS' and receipt['tests_run'] == 11
    assert receipt['errors'] == receipt['failures'] == 0
    assert receipt['native_enabled'] is False and receipt['exact'] is False
    assert receipt['gate1'] == 'UNKNOWN' and receipt['stage2_go'] is False
    assert receipt['original_B3_30_rerun'] is False and receipt['tensor_numerical_proof'] is False
    assert receipt['fake_tensor_operations'] == {}
    for name, expected in receipt['tested_inputs'].items():
        data = (HERE / name).read_bytes()
        assert dict(bytes=len(data), sha256=digest(data)) == expected, name
    for name in ('passive_capture.py', 'field_snapshot.py', 'source_api.py', 'fake_tensor.py', 'CODEC_SOURCE_PINS.json'):
        assert (HERE / name).read_bytes() == (HERE.parent / 'source_phase1_passive_sensor_capture_v3' / name).read_bytes(), name
    failure = json.loads((HERE / 'STDLIB_TEST_RECEIPT_attempt1.json').read_text(encoding='utf-8'))
    assert failure['status'] == 'FAIL' and failure['errors'] == 1 and failure['failures'] == 0
    assert failure['tested_inputs']['dependency_contract.py'] == receipt['tested_inputs']['dependency_contract.py']


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--create', action='store_true')
    args = parser.parse_args()
    assert sys.dont_write_bytecode, 'Use approved stdlib Python -B'
    assert len(FILES) == len(set(FILES)) == 21
    root = original_guard()
    evidence_guard()
    items = inventory()
    content_root = digest(json.dumps(items, sort_keys=True, separators=(',', ':')).encode())
    path = HERE / 'SOURCE_SEAL.json'
    if args.create:
        assert not path.exists(), 'Source seal is write-once'
        seal = dict(kind='PASSIVE_SENSOR_SOURCE_SEAL_V4', source_revision=4, source_only=True,
                    native_enabled=False, exact=False, gate1='UNKNOWN', stage2_go=False,
                    timestamp=datetime.now().astimezone().isoformat(), capture_schema='PASSIVE_SENSOR_CAPTURE_V3',
                    binding_inspection_kind='V4_TYPED_SOURCE_BINDING_INSPECTION_V1', parent_review='PENDING',
                    actual_Torch_CPU='NOT_EXECUTED', actual_SDK_native='NOT_EXECUTED', original_B3_30_rerun=False,
                    stdlib_preinstall_tests=11, member_count=21, total_files_including_seal=22,
                    content_root_sha256=content_root, old_source_and_seal_files=41,
                    old_before_after_manifest_sha256=root, files=items)
        with path.open('x', encoding='utf-8', newline='\n') as output:
            json.dump(seal, output, indent=2)
            output.write('\n')
    seal = json.loads(path.read_text(encoding='utf-8'))
    assert seal['kind'] == 'PASSIVE_SENSOR_SOURCE_SEAL_V4' and seal['source_revision'] == 4
    assert seal['member_count'] == 21 and seal['total_files_including_seal'] == 22
    assert seal['native_enabled'] is False and seal['exact'] is False
    assert seal['gate1'] == 'UNKNOWN' and seal['stage2_go'] is False
    assert seal['files'] == items and seal['content_root_sha256'] == content_root
    assert {item.name for item in HERE.iterdir()} == set(FILES) | {'SOURCE_SEAL.json'}
    data = path.read_bytes()
    print(json.dumps(dict(status='PASS', readonly_verification=not args.create, member_count=21,
                         total_files=22, stdlib_preinstall_tests=11, old_source_and_seal_files=41,
                         source_revision=4, capture_schema=seal['capture_schema'], native_enabled=False, exact=False,
                         gate1='UNKNOWN', stage2_go=False, seal_bytes=len(data), seal_sha256=digest(data),
                         content_root_sha256=content_root), indent=2))


if __name__ == '__main__':
    main()
