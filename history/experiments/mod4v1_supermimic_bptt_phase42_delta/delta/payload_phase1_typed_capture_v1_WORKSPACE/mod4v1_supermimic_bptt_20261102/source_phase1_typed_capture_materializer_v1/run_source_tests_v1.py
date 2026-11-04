"""Run exactly nine NEW SOURCE/own-temp tests, with append-only attempt receipts."""
from __future__ import annotations
import ast
from datetime import datetime, timezone
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import time
import unittest

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
R = HERE.parent
T = R.parent / 'mod4v1_experts_fulldr_rm70_20261101'


def H(raw):
    return hashlib.sha256(raw).hexdigest()


def source_snapshot():
    mirror = json.loads((HERE / 'SOURCE_MIRROR_INPUTS.json').read_bytes())
    inputs = {str((R if row['root'] == 'R' else T) / row['relative']):
              (row['bytes'], row['SHA256']) for row in mirror['files']}
    old = R / 'source_phase1_capture_materializer_v4'
    seal_raw = (old / 'SOURCE_SEAL.json').read_bytes()
    seal = json.loads(seal_raw)
    rows = seal['files']
    if type(rows) is dict:
        rows = [dict(relative=name, **row) for name, row in rows.items()]
    inputs[str(old / 'SOURCE_SEAL.json')] = (len(seal_raw), H(seal_raw))
    for row in rows:
        inputs[str(old / row['relative'])] = (row['bytes'], row.get('sha256', row.get('SHA256')))
    result = []
    for value, expected in sorted(inputs.items()):
        path = Path(value)
        # All paths come from the frozen textual manifest or the old source seal.
        raw = path.read_bytes()
        if (len(raw), H(raw)) != expected:
            raise ValueError('immutable old source differs: ' + value)
        result.append(dict(path=value.replace('\\', '/'), bytes=len(raw), SHA256=H(raw)))
    return dict(kind='READONLY_TYPED_MATERIALIZER_INPUT_SOURCE_BYTE_MAP_V1', files=result,
                count=len(result), SHA256=H(json.dumps(result, sort_keys=True, separators=(',', ':')).encode()))


def write_once(path, value):
    raw = (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode()
    with path.open('xb') as stream:
        stream.write(raw)


def main():
    attempt = 1
    while (HERE / ('SOURCE_TEST_RECEIPT_attempt' + str(attempt) + '.json')).exists():
        attempt += 1
    before = source_snapshot()
    before_path = HERE / 'SOURCE_BEFORE.json'
    if before_path.exists():
        if json.loads(before_path.read_bytes()) != before:
            raise ValueError('original pretest source map changed')
    else:
        write_once(before_path, before)
    violations = []
    def audit(event, args):
        if event == 'import' and args and str(args[0]).split('.')[0] in {
                'torch', 'numpy', 'isaaclab', 'isaacsim', 'omni', 'pxr', 'warp', 'psutil', 'fcntl', 'paramiko'}:
            violations.append(dict(event=event, name=str(args[0])))
            raise AssertionError('SOURCE test native/resource import')
        if event in {'subprocess.Popen', 'os.system', 'os.kill', 'socket.connect', 'socket.bind'}:
            violations.append(dict(event=event))
            raise AssertionError('SOURCE test operational action')
        if event == 'open' and args and isinstance(args[0], (str, bytes)):
            text = str(args[0]).replace('\\', '/').lower()
            parts = text.split('/')
            if (text.endswith(('.pt', '.pth', '.ckpt', '.safetensors', '.jsonl', '.lock'))
                    or 'reports' in parts or 'canonical' in parts or 'budget' in parts):
                violations.append(dict(event=event, path=text))
                raise AssertionError('SOURCE test model/raw/actual/C/lock open')
    sys.addaudithook(audit)
    start = time.perf_counter()
    path = HERE / 'test_typed_materializer_v1.py'
    spec = importlib.util.spec_from_file_location('_own_typed_materializer_tests', path)
    module = importlib.util.module_from_spec(spec); sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    suite = unittest.defaultTestLoader.loadTestsFromModule(module)
    if suite.countTestCases() != 9:
        raise ValueError('only exactly nine new own tests may run')
    output = io.StringIO()
    result = unittest.TextTestRunner(stream=output, verbosity=2).run(suite)
    elapsed = time.perf_counter() - start
    after = source_snapshot()
    write_once(HERE / ('SOURCE_AFTER_attempt' + str(attempt) + '.json'), after)
    unchanged = before == after
    receipt = dict(kind='NINE_NEW_TYPED_MATERIALIZER_STDLIB_SOURCE_TESTS_V1', source_only=True,
        attempt=attempt, timestamp_UTC=datetime.now(timezone.utc).isoformat(), python=sys.version,
        tests_run=result.testsRun, failures=len(result.failures), errors=len(result.errors),
        passed=result.wasSuccessful() and unchanged and not violations, elapsed_seconds=elapsed,
        details=module.RESULTS,
        tested_source_files={name: dict(bytes=len((HERE/name).read_bytes()), SHA256=H((HERE/name).read_bytes()))
            for name in ('stage_phase1_typed_capture_v1.py', 'typed_source_support_v1.py',
                         'static_source_helpers_v1.py', 'test_typed_materializer_v1.py',
                         'derive_materializer_v1.py', 'run_source_tests_v1.py')},
        immutable_old_source_inputs=before['count'],
        immutable_old_source_before_after_equal=unchanged, immutable_old_source_map_SHA256=before['SHA256'],
        audit_violations=violations, old_44_63_10_suites_run=False,
        actual_prepare_calls=0, actual_preflight_calls=0, actual_stage_calls=0,
        actual_original_runtime_directories_read=0, real_SDK_or_Torch_imports=0,
        parent_launches=0, resource_or_canonical_operations=0,
        fake_inventory_is_not_actual_V8_baseline_or_vendor7_proof=True,
        native_enabled=False, exact=False, gate1='UNKNOWN', stage2_GO=False)
    log = HERE / ('SOURCE_TEST_LOG_attempt' + str(attempt) + '.txt')
    with log.open('x', encoding='utf-8') as stream:
        stream.write(output.getvalue())
    write_once(HERE / ('SOURCE_TEST_RECEIPT_attempt' + str(attempt) + '.json'), receipt)
    print(output.getvalue())
    print(json.dumps({k:v for k,v in receipt.items() if k != 'details'}, ensure_ascii=False))
    return 0 if receipt['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
