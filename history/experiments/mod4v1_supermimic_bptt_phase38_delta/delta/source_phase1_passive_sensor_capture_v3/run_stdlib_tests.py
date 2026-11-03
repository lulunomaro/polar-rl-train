"""Reproduce only this package's stdlib/FakeTensor/API/AST suite; never SDK/Torch.

Default: stdout only. --write-receipt creates the two named NEW receipts once,
only after PASS. It never rewrites an existing receipt or source seal.
"""
import argparse
from collections import Counter
from datetime import datetime
import hashlib
import io
import json
from pathlib import Path
import platform
import sys
import time
import unittest

HERE = Path(__file__).resolve().parent
TARGET_PREFIXES = ('torch', 'isaaclab', 'isaacsim', 'omni', 'pxr', 'numpy', 'rsl_rl', 'gymnasium')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-receipt', action='store_true')
    args = parser.parse_args()
    audit = Counter()

    def audit_only(event, values):
        if event == 'import' and type(values[0]) is str and values[0].split('.')[0] in TARGET_PREFIXES:
            audit['forbidden_import_attempts'] += 1
            raise RuntimeError('Own stdlib suite attempted a target import')
        if (event.startswith(('socket.', 'subprocess.', 'ctypes.')) or
                event in ('os.system', 'os.kill', 'os.killpg', 'os.fork', 'os.posix_spawn', 'os.exec')):
            audit['network_process_native_signal_attempts'] += 1
            raise RuntimeError('Own stdlib suite attempted an external action')
        if event == 'open' and type(values[0]) is str and values[0].lower().endswith(('.pt', '.pth', '.jsonl')):
            audit['PT_or_raw_JSONL_open_attempts'] += 1
            raise RuntimeError('Own stdlib suite attempted a forbidden artifact open')

    sys.addaudithook(audit_only)
    log = io.StringIO()
    started = time.perf_counter()
    suite = unittest.defaultTestLoader.discover(str(HERE), pattern='test_passive_capture_v3.py')
    result = unittest.TextTestRunner(stream=log, verbosity=2).run(suite)
    elapsed = time.perf_counter() - started
    loaded = sorted(name for name in sys.modules if name.split('.')[0] in TARGET_PREFIXES)
    passed = result.wasSuccessful() and not loaded and not any(audit.values())
    receipt = dict(kind='B3_STDLIB_FAKE_API_AST_TEST_RECEIPT_V1', status='PASS' if passed else 'FAIL',
        timestamp=datetime.now().astimezone().isoformat(), python=platform.python_version(), bytecode_write=False,
        command='Python314/python.exe -B run_stdlib_tests.py --write-receipt',
        test_count=result.testsRun, failures=len(result.failures), errors=len(result.errors),
        skipped=len(result.skipped), elapsed_seconds=elapsed, target_modules_loaded=loaded,
        audit=dict(forbidden_import_attempts=audit['forbidden_import_attempts'],
                   network_process_native_signal_attempts=audit['network_process_native_signal_attempts'],
                   PT_or_raw_JSONL_open_attempts=audit['PT_or_raw_JSONL_open_attempts']),
        scope='OWN_STDLIB_FAKE_TENSOR_AND_FROZEN_CODEC_API_AST_ONLY',
        actual_torch_CPU=False, SDK=False, GPU=False, actual_worker=False, native_enabled=False, exact=False,
        gate1='UNKNOWN', stage2_go=False, original_source_or_B2_edits=False,
        evidence_boundary='Fake values/counts/identity and SOURCE checks do not establish native actor35/RNG parity')
    print(log.getvalue(), end='')
    if args.write_receipt and passed:
        receipt_path, log_path = HERE / 'STDLIB_FAKE_TEST_RECEIPT.json', HERE / 'STDLIB_FAKE_TEST_LOG.txt'
        if receipt_path.exists() or log_path.exists():
            raise FileExistsError('Receipt files already exist; rerun without --write-receipt')
        log_bytes = log.getvalue().encode('utf-8')
        receipt['test_log_sha256'] = hashlib.sha256(log_bytes).hexdigest()
        with log_path.open('xb') as output:
            output.write(log_bytes)
        with receipt_path.open('x', encoding='utf-8', newline='\n') as output:
            json.dump(receipt, output, indent=2)
            output.write('\n')
    print(json.dumps(receipt, indent=2))
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
