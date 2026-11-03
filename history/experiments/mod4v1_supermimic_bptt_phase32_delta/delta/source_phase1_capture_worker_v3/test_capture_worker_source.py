"""V3 UNSEALED template audit only; no B2 API, native imports or admission.

This is not the final V3 integration suite. Replace/extend only in this NEW
unsealed lineage after the parent supplies the final B2 receipt.
"""
from pathlib import Path
import ast
import hashlib
import json
import unittest

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
V2=ROOT/'source_phase1_capture_worker_v2'
V2_SEAL_SHA='caacf07e8bc46bd2cc5f4fa14138782430d86de4f6382bbb35adcdcde5d469d5'
V2_CONTENT_ROOT='83cb35d61298fdac4d2c720d1322ada0fbfa43b866709b4e5958b99ac82b62d2'
INHERITED=('phase1_capture_contract.py','phase1_capture_observer.py','phase1_capture_runtime.py',
           'worker_passive_interface_v1.py','single_gpu_passive_capture_parent_v1.py')


def source(name):
    return (HERE/name).read_text(encoding='utf-8')


def function(tree,name):
    return next(node for node in tree.body if isinstance(node,ast.FunctionDef) and node.name==name)


class V3PendingTemplateTests(unittest.TestCase):
    def test_all_frozen_V2_members_and_root_unchanged(self):
        raw=(V2/'SOURCE_SEAL.json').read_bytes()
        self.assertEqual((len(raw),hashlib.sha256(raw).hexdigest()),(2815,V2_SEAL_SHA))
        seal=json.loads(raw)
        self.assertEqual(len(seal['files']),13)
        canonical=json.dumps(seal['files'],sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
        self.assertEqual(hashlib.sha256(canonical).hexdigest(),V2_CONTENT_ROOT)
        self.assertEqual(seal['content_root_sha256'],V2_CONTENT_ROOT)
        for row in seal['files']:
            with self.subTest(relative=row['relative']):
                raw=(V2/row['relative']).read_bytes()
                self.assertEqual((len(raw),hashlib.sha256(raw).hexdigest()),(row['bytes'],row['sha256']))

    def test_five_full_sources_are_byte_identical_to_V2(self):
        for name in INHERITED:
            with self.subTest(name=name):
                self.assertEqual((HERE/name).read_bytes(),(V2/name).read_bytes())
                ast.parse(source(name),filename=str(HERE/name))

    def test_bootstrap_and_close_fixes_are_preserved(self):
        worker=ast.parse(source('worker_passive_interface_v1.py'))
        self.assertIsInstance(function(worker,'bootstrap_original_helpers'),ast.FunctionDef)
        runtime=ast.parse(source('phase1_capture_runtime.py'))
        put=function(runtime,'put_json')
        self.assertEqual([arg.arg for arg in put.args.kwonlyargs],['add_capture_epoch'])
        self.assertEqual(ast.literal_eval(put.args.kw_defaults[0]),True)
        calls=[node for node in ast.walk(runtime) if isinstance(node,ast.Call)]
        returned=[node for node in calls if ast.unparse(node.func)=='core()._validate_returned_app_binding']
        self.assertEqual(len(returned),1)
        self.assertEqual([ast.unparse(arg) for arg in returned[0].args],['binding','helper'])
        opted_out=[node for node in calls if ast.unparse(node.func)=='put_json' and any(
            keyword.arg=='add_capture_epoch' and isinstance(keyword.value,ast.Constant) and keyword.value.value is False
            for keyword in node.keywords)]
        self.assertEqual(len(opted_out),1)
        self.assertIn('APP_CLOSE_BINDING_PHASE1_CAPTURE_V1.json',ast.unparse(opted_out[0]))

    def test_original_parent_complete_lifecycle_blocks_preserved(self):
        old=ROOT/'source_bound_only_native_integration_v1'/'single_gpu_e3_w35_bound_only_parent_v1.py'
        raw=old.read_bytes()
        self.assertEqual((len(raw),hashlib.sha256(raw).hexdigest()),
            (9348,'63eaa4b04ee085a1efbbbc72a4d0756036faa7928af01e19713e6871925d0e80'))
        original=raw.decode('utf-8').splitlines(keepends=True)
        current=source('single_gpu_passive_capture_parent_v1.py').splitlines(keepends=True)
        for first,last in ((17,44),(46,78)):
            self.assertEqual(original[first-1:last],current[first-1:last])

    def test_no_plant_or_install_calls_added(self):
        main=function(ast.parse(source('worker_passive_interface_v1.py')),'main')
        calls=[ast.unparse(node.func) for node in ast.walk(main) if isinstance(node,ast.Call)]
        for name in ('env.reset','env.observation_manager.compute','bridge.init_state',
                     'bridge.step','sensor_api.install_passive_capture','actuation_api.install_actuation_tap'):
            with self.subTest(call=name):self.assertEqual(calls.count(name),1)
        self.assertEqual(calls.count('env.step'),0)
        self.assertFalse(any('clean_policy' in name for name in calls))

    def test_no_V3_packaging_or_B2_claim_while_receipt_pending(self):
        for name in ('prepare_sources.py','seal_source.py','CAPTURE_SOURCE_INDEX.json',
                     'SOURCE_PINS.json','SOURCE_RECEIPT.json','SOURCE_SEAL.json','FAKE_TEST_LOG.txt'):
            with self.subTest(name=name):self.assertFalse((HERE/name).exists())
        self.assertIn('UNSEALED_TEMPLATE_WAITING_PARENT_FINAL_B2_RECEIPT',source('README.md'))


if __name__=='__main__':
    unittest.main(verbosity=2)
