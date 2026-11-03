"""Write-once source seal / read-only SHA verification. Stdlib, NEW files only."""
import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
FILES = (
    'passive_capture.py', 'source_api.py', 'fake_runtime.py',
    'test_passive_capture.py', 'cpu_reference_tap_fixture.py', 'verify_seal.py',
    'SOURCE_API_MANIFEST.json', 'README.md', 'OBSERVER_HOOK_SPEC.md',
    'NATIVE_BINDING_RECEIPT_TEMPLATE.json', 'STDLIB_FAKE_TEST_RECEIPT.json',
    'STDLIB_FAKE_TEST_RECEIPT_v2.json', 'STDLIB_FAKE_TEST_RECEIPT_v3.json',
)


def digest(name):
    p = HERE / name
    if p.parent != HERE or not p.is_file():
        raise ValueError('Unexpected sealed artifact')
    raw = p.read_bytes()
    return dict(relative=name, bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())


def verify():
    seal = json.loads((HERE / 'SOURCE_SEAL.json').read_text(encoding='utf-8'))
    actual = [digest(name) for name in FILES]
    if actual != seal['files']:
        raise ValueError('Sealed source contents changed')
    receipt = json.loads((HERE / 'STDLIB_FAKE_TEST_RECEIPT_v3.json').read_text(encoding='utf-8'))
    for name, expected in receipt['source_hashes'].items():
        if digest(name)['sha256'] != expected:
            raise ValueError('Final test receipt refers to another source')
    if receipt['tests_run'] != 28 or receipt.get('source_revision') != 2 or not receipt['passed'] or receipt['native_enabled'] or receipt['exact']:
        raise ValueError('Unexpected final source-only test status')
    return dict(source_seal_verified=True, source_revision=2, files=len(actual), stdlib_fake_tests=28,
                native_enabled=False, exact=False, parent_review='PENDING',
                actual_CPU_tap_fixture='NOT_EXECUTED_BY_CHILD', native_binding='NOT_EXECUTED')


if __name__ == '__main__':
    q = argparse.ArgumentParser()
    q.add_argument('--create', action='store_true')
    a = q.parse_args()
    if a.create:
        document = dict(kind='WRITE_ONCE_SOURCE_ONLY_SEAL_V2', source_revision=2,
            immutable_parent_source_seal_sha256='3d5fd4febf9232a8113b4d93dbf8d3d6a19658690e973d6485c1aedc39e18881',
            prior_CPU_proof_scope='HISTORICAL_B1_SAME_RUNTIME_AST_ONLY_NO_B2_NATIVE_PROOF',
            immutable_content_hash_contract=True, filesystem_readonly_claim=False,
            source_only=True, native_enabled=False, exact=False,
            final_stdlib_receipt='STDLIB_FAKE_TEST_RECEIPT_v3.json',
            historical_receipts=['STDLIB_FAKE_TEST_RECEIPT.json', 'STDLIB_FAKE_TEST_RECEIPT_v2.json'],
            parent_review='PENDING', actual_CPU_tap_fixture='NOT_EXECUTED_BY_CHILD',
            native_binding='NOT_EXECUTED', files=[digest(name) for name in FILES])
        with (HERE / 'SOURCE_SEAL.json').open('x', encoding='utf-8') as stream:
            json.dump(document, stream, indent=2)
    print(json.dumps(verify(), indent=2))
