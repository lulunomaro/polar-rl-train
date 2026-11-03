"""One-shot NEW-directory SOURCE receipt/seal; stdlib tests only, never native."""
from __future__ import annotations
import hashlib
import io
import json
import os
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
SOURCE_FILES = ('README.md', 'capture_contract.py', 'capture_adapter.py', 'SOURCE_REQUEST.json',
                'source_preflight.py', 'test_native_probe_source.py', 'seal_source.py')
OUTPUT_FILES = ('SOURCE_PINS.json', 'SYNTHETIC_TEST_LOG.txt', 'SOURCE_RECEIPT.json', 'SOURCE_SEAL.json')
AUDIT = dict(blocked_operations=0, native_imports=0, model_reads=0, subprocess_starts=0)
MODEL_SUFFIXES = {'.pt', '.pth', '.ckpt', '.safetensors', '.onnx', '.pt2', '.pkl', '.pickle'}


def audit_hook(event, args):
    if event == 'import' and args and str(args[0]).split('.')[0] in (
            'torch', 'isaaclab', 'isaacsim', 'omni', 'pxr', 'psutil', 'paramiko', 'fabric'):
        AUDIT['native_imports'] += 1
        raise RuntimeError('SOURCE test forbids native/remote import: ' + str(args[0]))
    if event in ('subprocess.Popen', 'os.system', 'socket.connect', 'socket.bind'):
        AUDIT['subprocess_starts'] += 1
        raise RuntimeError('SOURCE test forbids subprocess/network')
    if event == 'open' and args and not isinstance(args[0], int):
        path = Path(os.fsdecode(args[0]))
        if path.suffix.lower() in MODEL_SUFFIXES:
            AUDIT['model_reads'] += 1
            raise RuntimeError('SOURCE test forbids selected/mother model path access')
        mode = args[1] or ''
        flags = args[2] if len(args) > 2 else 0
        writes = any(x in mode for x in ('w', 'a', 'x', '+')) or bool(flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT))
        if writes and not path.resolve().is_relative_to(HERE):
            AUDIT['blocked_operations'] += 1
            raise RuntimeError('SOURCE receipt write escaped NEW directory')


def write_new(name, content):
    path = HERE / name
    if path.exists():
        raise FileExistsError('Frozen outputs require a new lineage: ' + name)
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(content)


def json_text(value):
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + '\n'


def file_identity(name):
    raw = (HERE / name).read_bytes()
    return dict(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())


def main():
    for name in OUTPUT_FILES:
        if (HERE / name).exists():
            raise FileExistsError('No overwrite of completed SOURCE seal: ' + name)
    sys.addaudithook(audit_hook)
    from source_preflight import audit_source
    preflight = audit_source()
    output = io.StringIO()
    suite = unittest.defaultTestLoader.loadTestsFromName('test_native_probe_source')
    result = unittest.TextTestRunner(stream=output, verbosity=2).run(suite)
    if not result.wasSuccessful():
        print(output.getvalue())
        raise SystemExit('SOURCE tests failed; no seal emitted')
    imports = [name for name in sys.modules if name.split('.')[0] in ('torch', 'isaaclab', 'isaacsim', 'omni', 'pxr')]
    if imports or any(AUDIT.values()):
        raise RuntimeError('SOURCE execution boundary counters differ: ' + repr(AUDIT))
    receipt = dict(kind='SOURCE_FAKE_AST_INTEGRATION_RECEIPT_NOT_NATIVE',
                   source_only=True, tests_run=result.testsRun, tests_passed=result.testsRun,
                   test_failures=len(result.failures), test_errors=len(result.errors),
                   interpreter=sys.executable, python_version=sys.version.split()[0], dont_write_bytecode=sys.dont_write_bytecode,
                   fake_injection_tests=True, actual_sensor_install_tested=False,
                   source17_full_bytes_SHA_verified=True, original_sources_edited=False,
                   sensor_dependency_status='SEALED_SOURCE_VERIFIED_NATIVE_PENDING',
                   action_observer_status='DEFERRED_UNSEALED_NO_API_GUESSED',
                   actual_PT_reads=0, actual_SDK_imports=0, actual_native_runs=0,
                   actual_resource_gate_runs=0, actual_stage_dispatch=0, actual_GPU_use=0,
                   canonical_reads=0, canonical_writes=0, lock_accesses=0,
                   audit_counters=dict(AUDIT), native_enabled=False, gate1='UNKNOWN',
                   capture_interface_passed=False, exact=False, training_stage2_admitted=False,
                   native_worker_generated=False, remote_materializer_or_dispatcher_generated=False,
                   resource_close_wait_release_attested_here=False,
                   preserved_parent_resource_block='SOURCE_ONLY_FULL_17_MAPPING_VERIFIED_NOT_EXECUTED')
    write_new('SOURCE_PINS.json', json_text(preflight))
    write_new('SYNTHETIC_TEST_LOG.txt', output.getvalue())
    write_new('SOURCE_RECEIPT.json', json_text(receipt))
    files = {name: file_identity(name) for name in sorted(SOURCE_FILES + OUTPUT_FILES[:-1])}
    content_root = hashlib.sha256(json.dumps(files, sort_keys=True, separators=(',', ':')).encode('utf-8')).hexdigest()
    seal = dict(kind='SOURCE_CONTENT_ADDRESS_FREEZE_NOT_SDK_OR_NATIVE_ADMISSION', seal_version=1,
                files=files, content_root_sha256=content_root,
                external_sensor_source_pin=preflight['sensor_seal'],
                external_sensor_status='SEALED_SOURCE_VERIFIED_NATIVE_PENDING',
                external_action_source_pin='DEFERRED_UNSEALED',
                original17_index_pin=preflight['original17_index'],
                gate1='UNKNOWN', exact=False, actual_sdk_pass=False, native_enabled=False,
                scope='Only NEW SOURCE integration artifacts. Native worker/close/gates and actual resource verification deferred.')
    write_new('SOURCE_SEAL.json', json_text(seal))
    # Re-read own outputs to verify all file digests in the completed seal.
    if any(file_identity(name) != row for name, row in files.items()):
        raise RuntimeError('SOURCE seal verification differs')
    print(json_text(dict(tests_run=result.testsRun, stdlib_pass=True, actual_native_runs=0,
                         gate1='UNKNOWN', content_root_sha256=content_root)))


if __name__ == '__main__':
    main()
