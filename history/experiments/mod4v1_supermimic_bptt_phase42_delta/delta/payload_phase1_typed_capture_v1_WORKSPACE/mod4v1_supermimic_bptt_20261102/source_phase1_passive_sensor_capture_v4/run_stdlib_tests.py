"""Run only NEW V4 preinstall tests with stdlib Python -B; append-only receipts."""
import argparse
from datetime import datetime
import hashlib
import io
import json
from pathlib import Path
import sys
import time
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
parser = argparse.ArgumentParser()
parser.add_argument('--attempt', required=True, type=int)
args = parser.parse_args()
if args.attempt < 1 or not sys.dont_write_bytecode:
    raise SystemExit('Positive attempt and Python -B required')
paths = {kind: HERE / (prefix + '_attempt' + str(args.attempt) + suffix)
         for kind, prefix, suffix in (('receipt', 'STDLIB_TEST_RECEIPT', '.json'),
                                     ('log', 'STDLIB_TEST_LOG', '.txt'),
                                     ('after', 'SOURCE_AFTER', '.json'))}
if any(path.exists() for path in paths.values()):
    raise SystemExit('Attempt outputs already exist; choose a new attempt')
sha = lambda data: hashlib.sha256(data).hexdigest()
before = json.loads((HERE / 'SOURCE_BEFORE.json').read_text(encoding='utf-8'))

def old_hashes():
    values = {}
    for name, wanted in before['files'].items():
        data = Path(name).read_bytes()
        item = dict(bytes=len(data), sha256=sha(data))
        if item != wanted:
            raise AssertionError('Original source/seal changed: ' + name)
        values[name] = item
    return values

old_hashes()
activity = dict(target_imports=[], blocked_calls=[], raw_or_report_opens=[])

def audit(event, values):
    if event == 'import':
        name = str(values[0])
        if name.split('.')[0] in {'torch', 'numpy', 'isaaclab', 'omni', 'pxr', 'carb'}:
            activity['target_imports'].append(name)
            raise AssertionError('Target import prohibited in SOURCE test')
    if event in {'subprocess.Popen', 'os.system', 'os.spawn', 'os.posix_spawn',
                 'os.kill', 'os.killpg', 'socket.connect', 'socket.bind', 'ctypes.dlopen'}:
        activity['blocked_calls'].append(event)
        raise AssertionError('External/native activity prohibited in SOURCE test')
    if event == 'open' and values and isinstance(values[0], (str, bytes)):
        name = str(values[0]).replace('\\', '/').lower()
        if name.endswith(('.pt', '.pth', '.jsonl')) or '/reports/' in name:
            activity['raw_or_report_opens'].append(name)
            raise AssertionError('Raw/actual-report input prohibited in SOURCE test')

sys.addaudithook(audit)
sys.path.insert(0, str(HERE))
started = time.perf_counter()
stream = io.StringIO()
suite = unittest.defaultTestLoader.loadTestsFromName('test_dependency_contract_v4.StrictDependencyTests')
result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
elapsed = time.perf_counter() - started
from fake_tensor import FakeTensor
after_files = old_hashes()
root = sha(json.dumps(after_files, sort_keys=True, separators=(',', ':')).encode())
assert root == before['manifest_sha256']
assert result.testsRun == 11
assert activity == dict(target_imports=[], blocked_calls=[], raw_or_report_opens=[])
after = dict(kind='V4_OLD_SOURCE_AFTER_HASHES_V1', source_only=True, old_source_and_seal_files=len(after_files),
             all_original_bytes_unchanged=True, before_manifest_sha256=before['manifest_sha256'],
             after_manifest_sha256=root, files=after_files)
inputs = {name: dict(bytes=len((HERE / name).read_bytes()), sha256=sha((HERE / name).read_bytes()))
          for name in ('dependency_contract.py', 'test_dependency_contract_v4.py', 'run_stdlib_tests.py',
                       'passive_capture.py', 'field_snapshot.py', 'source_api.py', 'CODEC_SOURCE_PINS.json', 'fake_tensor.py')}
receipt = dict(kind='V4_STRICT_PREINSTALL_STDLIB_SOURCE_TESTS_V1', source_revision=4,
               status='PASS' if result.wasSuccessful() else 'FAIL', timestamp=datetime.now().astimezone().isoformat(),
               python=sys.version.split()[0], executable=sys.executable, dont_write_bytecode=sys.dont_write_bytecode,
               tests_run=result.testsRun, failures=len(result.failures), errors=len(result.errors), seconds=elapsed,
               test_names=[case.id() for case in unittest.defaultTestLoader.loadTestsFromName('test_dependency_contract_v4.StrictDependencyTests')],
               scope='OWN_STDLIB_PREINSTALL_SOURCE_BINDING_ONLY', source_only=True, native_enabled=False, exact=False,
               gate1='UNKNOWN', stage2_go=False, original_B3_30_rerun=False, tensor_numerical_proof=False,
               actual_Torch_or_SDK_execution=False, full_default_checked_functions=22, full_default_checked_classes=3,
               fake_tensor_operations=dict(FakeTensor.operations), activity=activity,
               old_source_and_seal_files=len(after_files), old_before_after_equal=True,
               old_manifest_sha256=root, tested_inputs=inputs)
for kind, value in (('after', after), ('receipt', receipt)):
    with paths[kind].open('x', encoding='utf-8', newline='\n') as output:
        json.dump(value, output, indent=2)
        output.write('\n')
with paths['log'].open('x', encoding='utf-8', newline='\n') as output:
    output.write(stream.getvalue())
print(stream.getvalue())
print(json.dumps({key: receipt[key] for key in ('status', 'tests_run', 'failures', 'errors', 'seconds',
      'old_source_and_seal_files', 'old_before_after_equal', 'fake_tensor_operations', 'activity')}, indent=2))
raise SystemExit(0 if result.wasSuccessful() else 1)
