"""12 V4 SOURCE audits + selected32 frozen full-stdlib metadata regressions.
No Torch/SDK/native fixture or actual report read. CPU fixture is parent-run.
"""
from pathlib import Path
import ast
import copy
import json
import sys
import unittest
import prepare_sources as p

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent


class V4SourceIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index=json.loads((HERE/'CAPTURE_SOURCE_INDEX.json').read_text(encoding='utf-8'))
        cls.old=json.loads((p.V3/'CAPTURE_SOURCE_INDEX.json').read_text(encoding='utf-8'))

    def test_all13_frozen_V3_and_retained_full_closure(self):
        sealed,index=p.verify_v3()
        self.assertEqual(sealed['content_root_sha256'],p.V3_ROOT)
        self.assertEqual(len(sealed['members']),13);self.assertEqual(index,self.old)

    def test_four_candidates_exactly_unchanged(self):
        for name in p.INHERITED:
            if name!='worker_passive_interface_v1.py':self.assertEqual((HERE/name).read_bytes(),(p.V3/name).read_bytes())

    def test_worker_reverse_projection_is_one_literal_line(self):
        old=(p.V3/'worker_passive_interface_v1.py').read_bytes();new=(HERE/'worker_passive_interface_v1.py').read_bytes()
        self.assertEqual(old.count(p.OLD.encode()),1);self.assertEqual(new.count(p.NEW.encode()),1)
        self.assertEqual(old.replace(p.OLD.encode(),p.NEW.encode()),new)
        self.assertEqual(new.replace(p.NEW.encode(),p.OLD.encode()),old)
        self.assertEqual(len(new)-len(old),3)

    def test_existing_bridge_device_no_flag_or_boundary_change(self):
        tree=ast.parse((HERE/'worker_passive_interface_v1.py').read_text(encoding='utf-8'))
        calls=[n for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='OriginalEpisodeBoundary']
        self.assertEqual(len(calls),1);self.assertEqual(ast.unparse(calls[0].args[1]),'bridge.device')
        self.assertEqual(self.index['source_derivation']['new_SDK_getters'],0)
        self.assertTrue(self.index['source_derivation']['canonical_boundary_unchanged'])
        self.assertTrue(self.index['source_derivation']['original_bridge_bool_unchanged'])

    def test_entire_B2_13_and_original155_435_retained(self):
        sensor,manifest=p.upstream().verify_B2()
        self.assertEqual(sensor,self.index['dependency_seals']['sensor'])
        self.assertEqual(manifest,self.index['sensor_source_manifest'])
        self.assertEqual(len(sensor['members']),13)
        closure=manifest['original_source_closure']
        self.assertEqual((closure['unique_full_source_files'],closure['pin_references']),(155,435))

    def test_original17_C182_adapter10_partition9_unchanged(self):
        for key in ('original17','all_actuation_original_sources','dependency_sources','dependency_seals','bootstrap_original_sources',
                    'parent_mechanical_diff','evalclose_mechanical_diff','sensor_reset_diagnostic_source_references'):
            self.assertEqual(self.index[key],self.old[key])
        self.assertEqual(len(self.index['original17']),17)
        self.assertEqual(len(self.index['all_actuation_original_sources']),182)

    def test_index_reverse_projection_exact_V3(self):
        actual=copy.deepcopy(self.index);actual['source_version']=3;actual['source_derivation']=self.old['source_derivation']
        actual['new_sources']=self.old['new_sources'];actual.pop('boundary_device_source_contract')
        self.assertEqual(actual,self.old)
        self.assertEqual([r['install_relative'] for r in self.index['new_sources']],[r['install_relative'] for r in self.old['new_sources']])

    def test_wire_V1_version4_unknown_actual_flags(self):
        self.assertEqual(self.index['kind'],'PHASE1_CAPTURE_WORKER_SOURCE_INDEX_V1')
        self.assertEqual(self.index['source_version'],4)
        self.assertEqual(self.index['source_derivation']['candidate_logic_diff_count'],1)
        self.assertEqual(self.index['source_derivation']['cause_status'],'SOURCE_CANDIDATE_NOT_ACTUAL_V3_ROOT_CAUSE_CONFIRMED')
        self.assertIsNone(self.index['source_derivation']['actual_V3_flags_shape_dtype_device'])
        self.assertFalse(self.index['source_derivation']['actual_reports_read_here'])
        for key in ('native_executed','capture_interface_passed','exact','stage2_GO'):self.assertFalse(self.index[key])
        self.assertEqual(self.index['gate1'],'UNKNOWN')

    def test_original_parent_and_full_resource_lifecycle_unchanged(self):
        self.assertEqual((HERE/'single_gpu_passive_capture_parent_v1.py').read_bytes(),(p.V3/'single_gpu_passive_capture_parent_v1.py').read_bytes())
        self.assertEqual(self.index['parent_mechanical_diff'],self.old['parent_mechanical_diff'])

    def test_fixed_complete_boundary_contract8_source_not_CPU_claim(self):
        value=p.verify_boundary_contract()
        self.assertEqual(value,self.index['boundary_device_source_contract'])
        self.assertEqual(len(value['seal']['members']),8)
        self.assertFalse(value['actual_Torch_CPU_executed_here'])
        self.assertTrue(value['read_only_fixture_source_not_runtime_dependency'])
        self.assertIsNone(value['source_contract']['actual_V3_flags_shape_dtype_device'])

    def test_bad_new_source_pin_rejected(self):
        row=copy.deepcopy(self.index['new_sources'][0]);row['SHA256']='0'*64
        with self.assertRaises(ValueError):p.check_row(row)

    def test_no_native_or_Torch_fixture_or_main_invoked(self):
        self.assertFalse(any(name.split('.')[0] in ('torch','numpy','isaacsim','isaaclab','omni','pxr','warp','psutil','paramiko') for name in sys.modules))
        old=ast.parse((p.V3/'worker_passive_interface_v1.py').read_text(encoding='utf-8'))
        new=ast.parse((HERE/'worker_passive_interface_v1.py').read_text(encoding='utf-8'))
        def calls(tree):return [n.func.attr for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute)]
        self.assertEqual(calls(old),calls(new))


def load_tests(loader,tests,pattern):
    old_path=list(sys.path)
    for leaf,name in (('phase1_capture_contract.py','phase1_capture_contract'),('phase1_capture_observer.py','phase1_capture_observer'),
                      ('phase1_capture_runtime.py','phase1_capture_runtime'),('worker_passive_interface_v1.py','worker_passive_interface_v1')):
        p.full_source_import(HERE/leaf,name)
    legacy=p.full_source_import(p.V2/'test_capture_worker_source.py','_v4_selected_full_frozen_V2_metadata_regressions')
    legacy.HERE=HERE;legacy.ROOT=ROOT;sys.path[:]=old_path
    suite=unittest.TestSuite([loader.loadTestsFromTestCase(V4SourceIntegrationTests)])
    suite.addTests(loader.loadTestsFromTestCase(legacy.FullOriginalStdlibCloseTests))
    for name in loader.getTestCaseNames(legacy.ActualOriginalBootstrapTests):
        if name!='test_wire_kinds_and_original_parent_unchanged':suite.addTest(legacy.ActualOriginalBootstrapTests(name))
    return suite


if __name__=='__main__':unittest.main(verbosity=2)
