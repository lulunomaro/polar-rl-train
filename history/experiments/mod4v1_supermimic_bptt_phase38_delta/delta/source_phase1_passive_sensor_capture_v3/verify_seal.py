"""Own stdlib source-only seal verification. --create writes one NEW seal once.

No target imports, Torch, SDK, processes, signals or native execution.
"""
import argparse
import ast
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
MEMBERS = (
    'CODEC_SOURCE_PINS.json', 'README.md', 'SCHEMA.md', 'SOURCE_API_CONTRACT.json',
    'SOURCE_DIFF.md', 'SOURCE_DIFF.patch', 'STDLIB_FAKE_TEST_LOG.txt', 'STDLIB_FAKE_TEST_RECEIPT.json',
    'dependency_contract.py', 'fake_runtime.py', 'fake_tensor.py', 'fake_typed_runtime.py',
    'field_snapshot.py', 'passive_capture.py', 'run_stdlib_tests.py', 'source_api.py',
    'test_passive_capture_v3.py', 'verify_seal.py',
)
BASE_SEAL_SHA = 'be538a07c8ccfb785023422ace6985e1fde0bd5b885266124e430527c1ec558a'
CODEC_SEAL_SHA = '2cc26eaee058d30c9ac5b17ca8fb37541beb7c1e5ddbb738963ddef08c199219'
CODEC_SHA = '77c007fb0b17088b54bb0c115913159c7a9bf99f50f29a0b203dea483f0d1ee4'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def need(condition, message):
    if not condition:
        raise ValueError(message)


def external_source_guards():
    base = HERE.parent / 'source_phase1_passive_sensor_capture_v2'
    publisher = HERE.parent / 'source_phase1_typed_capture_codec_v1'
    need(sha(base / 'SOURCE_SEAL.json') == BASE_SEAL_SHA, 'Immutable B2 seal changed')
    need(sha(publisher / 'SOURCE_SEAL.json') == CODEC_SEAL_SHA, 'Immutable typed publisher seal changed')
    base_items = json.loads((base / 'SOURCE_SEAL.json').read_text(encoding='utf-8'))['files']
    publisher_items = json.loads((publisher / 'SOURCE_SEAL.json').read_text(encoding='utf-8'))['files']
    need(len(base_items) == 13 and len(publisher_items) == 7, 'Original seal membership changed')
    for item in base_items:
        path = base / item['relative']
        need(path.stat().st_size == item['bytes'] and sha(path) == item['sha256'], 'B2 source member changed')
    for name, item in publisher_items.items():
        path = publisher / name
        need(path.stat().st_size == item['bytes'] and sha(path) == item['sha256'], 'Typed publisher source member changed')
    for name in ('source_api.py', 'fake_runtime.py'):
        need((HERE / name).read_bytes() == (base / name).read_bytes(), 'Inherited B2 bytes changed')
    need(sha(publisher / 'typed_capture_codec.py') == CODEC_SHA, 'Final typed module SHA mismatch')
    return dict(B2_members=13, publisher_members=7)


def current_files():
    allowed = set(MEMBERS) | {'SOURCE_SEAL.json'}
    regular = {path.name for path in HERE.iterdir() if path.is_file()}
    need(regular <= allowed and set(MEMBERS) <= regular, 'Unexpected or missing B3 source member')
    result = {}
    for name in sorted(MEMBERS):
        path = HERE / name
        raw = path.read_bytes()
        if path.suffix == '.py':
            ast.parse(raw, filename=str(path))
        elif path.suffix == '.json':
            json.loads(raw)
        result[name] = dict(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())
    return result


def source_contract_checks():
    receipt = json.loads((HERE / 'STDLIB_FAKE_TEST_RECEIPT.json').read_text(encoding='utf-8'))
    need(receipt['status'] == 'PASS' and receipt['test_count'] == 30, 'Final 30-test receipt absent')
    need(receipt['failures'] == receipt['errors'] == receipt['skipped'] == 0, 'Final receipt not clean')
    need(not receipt['target_modules_loaded'] and not any(receipt['audit'].values()), 'Target/action audit not zero')
    need(all(receipt[key] is False for key in ('actual_torch_CPU', 'SDK', 'GPU', 'actual_worker', 'native_enabled', 'exact', 'stage2_go')), 'SOURCE receipt gained actual admission')
    need(receipt['test_log_sha256'] == sha(HERE / 'STDLIB_FAKE_TEST_LOG.txt'), 'Final test log mismatch')
    pins = json.loads((HERE / 'CODEC_SOURCE_PINS.json').read_text(encoding='utf-8'))
    need(pins['publisher_final'] is True and pins['codec_source_sha256'] == CODEC_SHA, 'Nonfinal dependency')
    need(pins['publisher_source_seal_sha256'] == CODEC_SEAL_SHA, 'Wrong dependency seal')
    need(len(pins['codec_functions']) == 17 and len(pins['field_functions']) == 5, 'Dependency API changed')
    contract = json.loads((HERE / 'SOURCE_API_CONTRACT.json').read_text(encoding='utf-8'))
    need(contract['capture_schema'] == 'PASSIVE_SENSOR_CAPTURE_V3' and contract['source_revision'] == 3, 'B3 schema missing')
    need(contract['native_enabled'] is False and contract['exact'] is False and contract['gate1'] == 'UNKNOWN' and contract['stage2_go'] is False, 'Contract gained native admission')
    need(len(contract['immutable_AST']) == 10 and len(contract['components']) == 22, 'SOURCE proof inventory changed')
    for item in contract['components'].values():
        path = HERE / Path(item['source_path']).name
        need(sha(path) == item['source_sha256'], 'Component source SHA changed after SOURCE contract')
    for item in pins['field_functions'].values():
        need(sha(HERE / 'field_snapshot.py') == item['source_sha256'], 'Field adapter changed after typed binding')
    count = sum(isinstance(node, ast.FunctionDef) and node.name.startswith('test_')
                for node in ast.walk(ast.parse((HERE / 'test_passive_capture_v3.py').read_text(encoding='utf-8'))))
    need(count == 30, 'Own test source inventory mismatch')
    links = 0
    for name in ('README.md', 'SCHEMA.md', 'SOURCE_DIFF.md'):
        for target in re.findall(r'\]\(<([^>]+)>\)', (HERE / name).read_text(encoding='utf-8')):
            file_name, _, anchor = target.partition('#')
            path = Path(file_name)
            need(path.is_file(), 'SOURCE document link target absent: ' + file_name)
            if anchor:
                match = re.fullmatch(r'L(\d+)(?:-L(\d+))?', anchor)
                need(match is not None, 'Unexpected source line anchor')
                need(1 <= int(match.group(1)) <= len(path.read_text(encoding='utf-8').splitlines()), 'Source line anchor out of range')
            links += 1
    return links


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--create', action='store_true')
    args = parser.parse_args()
    need(sys.dont_write_bytecode, 'Use the explicitly approved Python -B')
    guards = external_source_guards()
    files = current_files()
    links = source_contract_checks()
    root = hashlib.sha256(json.dumps(files, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()).hexdigest()
    path = HERE / 'SOURCE_SEAL.json'
    if args.create:
        need(not path.exists(), 'B3 source seal is write-once')
        seal = dict(kind='B3_WRITE_ONCE_SOURCE_ONLY_SEAL_V1', status='FROZEN_SOURCE_ONLY',
            timestamp=datetime.now().astimezone().isoformat(), capture_schema='PASSIVE_SENSOR_CAPTURE_V3', source_revision=3,
            source_only=True, immutable_content_hash_contract=True, filesystem_readonly_claim=False,
            native_enabled=False, exact=False, gate1='UNKNOWN', stage2_go=False, parent_review='PENDING',
            actual_B3_Torch_CPU='NOT_EXECUTED', actual_SDK_or_worker='NOT_EXECUTED',
            base_B2_source_seal_sha256=BASE_SEAL_SHA, typed_source_seal_sha256=CODEC_SEAL_SHA,
            final_test_count=30, content_root_sha256=root, files=files)
        with path.open('x', encoding='utf-8', newline='\n') as output:
            json.dump(seal, output, indent=2)
            output.write('\n')
    seal = json.loads(path.read_text(encoding='utf-8'))
    need(seal['files'] == files and seal['content_root_sha256'] == root, 'B3 immutable source content mismatch')
    need(seal['native_enabled'] is False and seal['exact'] is False and seal['gate1'] == 'UNKNOWN' and seal['stage2_go'] is False, 'B3 seal gained native admission')
    print(json.dumps(dict(status='PASS', B3_members=len(files), content_root_sha256=root,
        seal_bytes=path.stat().st_size, seal_sha256=sha(path), source_guards=guards,
        source_doc_links=links, final_test_count=30, native_enabled=False, exact=False,
        actual_B3_Torch_CPU='NOT_EXECUTED', actual_SDK_or_worker='NOT_EXECUTED'), indent=2))


if __name__ == '__main__':
    main()
