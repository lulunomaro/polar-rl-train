"""Run exactly six new AST/memory tests; never import a materializer entry."""
from pathlib import Path
import ast
import hashlib
import importlib.util
import json
import sys
import time
import unittest

HERE=Path(__file__).resolve().parent
R=HERE.parent
V1=R/'source_phase1_typed_capture_materializer_v1'
H=lambda raw:hashlib.sha256(raw).hexdigest()
violations=[]


def audit(event,args):
    if event=='import' and str(args[0]).split('.')[0] in {'torch','numpy','omni','isaaclab','isaacsim','psutil','fcntl','paramiko','subprocess'}:
        violations.append([event,str(args[0])]);raise AssertionError('SOURCE V2 test native/resource/process import')
    if event in {'subprocess.Popen','os.system','os.kill','socket.__new__'}:
        violations.append([event]);raise AssertionError('SOURCE V2 test process/network/signal call')
    if event=='open' and isinstance(args[0],(str,bytes)):
        value=str(args[0]).replace('\\','/').lower();parts=value.split('/')
        forbidden_parts={'reports','canonical','locks','.git','models','checkpoints','raw'}
        if any(p in forbidden_parts for p in parts) or value.endswith(('.pt','.pth','.ckpt','.safetensors','.onnx','.jsonl','.lock')):
            violations.append([event,str(args[0])]);raise AssertionError('SOURCE V2 test non-source file open')


def old_source_snapshot():
    raw=(V1/'SOURCE_SEAL.json').read_bytes()
    assert (len(raw),H(raw))==(5312,'e9edbf414c5c386236a1eccb0b35d2e525a9339a4dd93d6365e6d645b5c9ebda')
    seal=json.loads(raw);rows=json.loads((V1/'SOURCE_BEFORE.json').read_bytes())['files']
    expected={row['path']:(row['bytes'],row['SHA256']) for row in rows}
    assert len(expected)==407
    for row in seal['files']:
        path=str(V1/row['relative']);assert path not in expected
        expected[path]=(row['bytes'],row['SHA256'])
    expected[str(V1/'SOURCE_SEAL.json')]=(len(raw),H(raw));assert len(expected)==436
    actual=[]
    for path,pin in sorted(expected.items()):
        data=Path(path).read_bytes();assert (len(data),H(data))==pin,'old pinned text bytes differ: '+path
        actual.append(dict(path=path,bytes=len(data),SHA256=H(data)))
    return dict(count=436,all_published_pins_equal_actual=True,
                logical_SHA256=H(json.dumps(actual,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()))


def source_references():
    records=[]
    index=json.loads((R/'source_phase1_typed_native_capture_v1/CAPTURE_SOURCE_INDEX.json').read_bytes())
    handoff_raw=(R/'source_phase1_sensor_reset_identity_diagnosis_v1/FINAL_SOURCE_HANDOFF_RECEIPT.json').read_bytes()
    assert (len(handoff_raw),H(handoff_raw))==(3991,'238ef8f8ecd99383f91d3d474cbae3a409a16f9ec56e8e49f2c56e5b9b523c99')
    for folder,size,digest,count,selector in [
        ('source_phase1_passive_sensor_capture_v2',2909,'be538a07c8ccfb785023422ace6985e1fde0bd5b885266124e430527c1ec558a',13,'original_B2_reference_seal'),
        ('source_phase1_passive_sensor_capture_v4',3824,'81fe69c8c2f2ffde98b2a5e4b03d6921207d60156dcb180ab0097aa7397813b3',21,'dependency_seals.sensor')]:
        raw=(R/folder/'SOURCE_SEAL.json').read_bytes();assert (len(raw),H(raw))==(size,digest)
        declared=json.loads(raw)['files']
        if type(declared) is dict:declared=[dict(relative=name,**row) for name,row in declared.items()]
        assert len(declared)==count;members=[]
        for row in declared:
            data=(R/folder/row['relative']).read_bytes();pin=(row['bytes'],row.get('sha256',row.get('SHA256')))
            assert (len(data),H(data))==pin
            members.append(dict(relative=row['relative'],bytes=len(data),SHA256=H(data)))
        record=index['original_B2_reference_seal'] if count==13 else index['dependency_seals']['sensor']
        assert (record['bytes'],record['SHA256'])==(size,digest)
        records.append(dict(selector=selector,relative_source=folder+'/SOURCE_SEAL.json',bytes=size,SHA256=digest,
                            complete_actual_members=count,member_source_identities=members,
                            complete_member_identity_SHA256=H(json.dumps(members,sort_keys=True,separators=(',',':')).encode())))
    return dict(kind='TWO_INDEPENDENT_PUBLISHED_HISTORY_ACTIVE_REFERENCE_PROOFS_V2',source_only=True,
                expected_history_source='FIXED_PUBLISHED_B2_RAW_BYTES_SHA_AND_COMPLETE13_NOT_ACTIVE_B4',
                references=records,historical_diagnostic_handoff=dict(bytes=len(handoff_raw),SHA256=H(handoff_raw)),
                old_B2_declared_content_root_sha256=None,active_B4_strict_package_verification_unchanged=True,
                actual_materializer_calls=0,native_enabled=False,exact=False,gate1='UNKNOWN',stage2_GO=False)


def create(name,value):
    with (HERE/name).open('xb') as out:
        out.write((json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode())


def main():
    sys.addaudithook(audit)
    before=old_source_snapshot();started=time.perf_counter()
    spec=importlib.util.spec_from_file_location('_own_history_binding_tests_v2',HERE/'test_history_binding_v2.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    suite=unittest.defaultTestLoader.loadTestsFromModule(module);assert suite.countTestCases()==6
    with (HERE/'SOURCE_TEST_LOG_attempt1.txt').open('x',encoding='utf-8') as stream:
        result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
    after=old_source_snapshot();assert before==after
    refs=source_references();create('SOURCE_REFERENCES.json',refs)
    tested={}
    for name in ('stage_phase1_typed_capture_v2.py','historical_b2_binding_v2.py','static_source_helpers_v1.py',
                 'typed_source_support_v1.py','derive_history_binding_v2.py','test_history_binding_v2.py','run_history_binding_tests_v2.py'):
        raw=(HERE/name).read_bytes();ast.parse(raw);tested[name]=dict(bytes=len(raw),SHA256=H(raw))
    receipt=dict(kind='SIX_NEW_HISTORY_BINDING_AST_MEMORY_TEST_RECEIPT_V2',passed=result.wasSuccessful(),
                 tests_run=result.testsRun,failures=len(result.failures),errors=len(result.errors),
                 elapsed_seconds=time.perf_counter()-started,tested_source_files=tested,
                 old_pinned_text_sources_before=before,old_pinned_text_sources_after=after,
                 old_pinned_source_bytes_unchanged=True,audit_violations=violations,
                 old_nine_case_suite_runs=0,materializer_imports=0,actual_load_sources_calls=0,actual_B2_builder_calls=0,
                 actual_prepare_calls=0,actual_metadata_calls=0,actual_preflight_calls=0,actual_stage_calls=0,parent_launches=0,
                 actual_report_reads=0,SDK_Torch_C_lock_Git_operations=0,native_enabled=False,exact=False,gate1='UNKNOWN',stage2_GO=False)
    create('SOURCE_TEST_RECEIPT_attempt1.json',receipt)
    print(json.dumps(receipt))
    raise SystemExit(0 if result.wasSuccessful() and not violations else 1)


if __name__=='__main__':
    main()
