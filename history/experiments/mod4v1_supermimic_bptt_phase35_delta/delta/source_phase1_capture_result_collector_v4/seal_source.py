"""Append-only content seal; subsequent calls only verify SOURCE bytes."""
from pathlib import Path
import hashlib
import json
import source_pins

HERE = Path(__file__).resolve().parent
EXPECTED_TESTS = 51  # own final SOURCE fake/AST suite; no upstream totals
MEMBERS = ('collect_capture_result.py','remote_metadata_reader.py','source_pins.py',
           'SOURCE_PINS.json','test_collector_source.py','README.md','FAKE_TEST_LOG.txt',
           'SOURCE_RECEIPT.json','seal_source.py')


def identity(path):
    raw = Path(path).read_bytes()
    return dict(bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())


def run():
    if type(EXPECTED_TESTS) is not int:
        raise ValueError('V4_TEMPLATE_UNSEALED_FINAL_PINS_PENDING')
    sources = source_pins.verify_sources()
    receipt = json.loads((HERE/'SOURCE_RECEIPT.json').read_bytes())
    if (receipt.get('status') != 'SOURCE_STDLIB_FAKE_AST_PASS' or receipt.get('tests_run') != EXPECTED_TESTS
        or receipt.get('kind') != 'PHASE1_CAPTURE_RESULT_COLLECTOR_SOURCE_RECEIPT_V4'
        or receipt.get('source_version') != 4 or receipt.get('typed_API_version') != 1
        or receipt.get('tests_declared') != EXPECTED_TESTS or receipt.get('tests_skipped') != 0
        or receipt.get('template_mode') is not False or receipt.get('excluded_final_pin_tests') != []
        or receipt.get('failures') != 0 or receipt.get('errors') != 0):
        raise ValueError('final fake/AST receipt required')
    if any(receipt.get(k) is not False for k in ('actual_SSH','actual_collect','actual_remote_metadata_or_trace_read',
        'actual_parent_created','actual_SDK','actual_GPU','actual_PT_or_raw_reads',
        'actual_boundary_fixture_or_Torch_execution','parent_CPU_report_read_or_used',
        'capture_interface_passed','exact','stage2_GO')):
        raise ValueError('SOURCE scope flags changed')
    if identity(HERE/'FAKE_TEST_LOG.txt')['sha256'] != receipt['test_log_SHA256']:
        raise ValueError('test log differs')
    rows = [dict(relative=name,**identity(HERE/name)) for name in MEMBERS]
    root = hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    seal = HERE/'SOURCE_SEAL.json'
    if seal.exists():
        value = json.loads(seal.read_bytes())
        if value['files'] != rows or value['content_root_sha256'] != root:
            raise ValueError('collector source seal mismatch')
    else:
        value = dict(kind='PHASE1_CAPTURE_RESULT_COLLECTOR_SOURCE_SEAL_V4',files=rows,source_version=4,
            typed_API_version=1,source_derivation=receipt['source_derivation'],
            content_root_sha256=root,source_count=sources['source_count'],
            extra_source_refs=sources['extra_source_refs'],boundary_source_refs=sources['boundary_source_refs'],
            old_partition_nine_unchanged=True,worker_thirteen_unchanged=True,base_v1_collector_nine_unchanged=True,
            base_v2_collector_nine_unchanged=True,base_v3_collector_nine_unchanged=True,actual_B2_or_reset_verifier_executed=False,
            actual_boundary_fixture_or_Torch_execution=False,parent_CPU_report_read_or_used=False,
            actual_collection=False,actual_SDK=False,gate1='UNKNOWN',exact=False,stage2_GO=False)
        with seal.open('x',encoding='utf-8') as stream:
            json.dump(value,stream,indent=2,allow_nan=False)
    reread = json.loads(seal.read_bytes())
    if reread != value:
        raise ValueError('seal readback differs')
    return dict(seal=str(seal),sealed_members=len(rows),source_count=sources['source_count'],
        content_root_sha256=root,seal_sha256=identity(seal)['sha256'],readonly_verify=True,
        extra_source_refs=sources['extra_source_refs'],boundary_source_refs=sources['boundary_source_refs'],
        original_partition_nine_unchanged=True,worker_thirteen_unchanged=True,
        base_v1_collector_nine_unchanged=True,base_v2_collector_nine_unchanged=True,base_v3_collector_nine_unchanged=True,
        actual_collection=False,actual_SDK=False,gate1='UNKNOWN',exact=False,stage2_GO=False)


if __name__=='__main__':print(json.dumps(run()))
