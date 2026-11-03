"""V3 SOURCE integration audit + selected unchanged V2 stdlib metadata regressions.

No SDK/env/parent main or actual reset verifier execution. Historical B2 28 and
V2 96 are referenced, not added to this suite's test count.
"""
from pathlib import Path
import ast
import copy
import hashlib
import inspect
import json
import sys
import unittest
import prepare_sources as p

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent


class V3SourceIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index=json.loads((HERE/'CAPTURE_SOURCE_INDEX.json').read_text(encoding='utf-8'))
        cls.v2=json.loads((p.V2/'CAPTURE_SOURCE_INDEX.json').read_text(encoding='utf-8'))

    def test_all_V2_thirteen_members_and_five_full_candidates_unchanged(self):
        sealed,index=p.verify_frozen_v2()
        self.assertEqual(sealed['content_root_sha256'],p.V2_ROOT)
        self.assertEqual(len(sealed['members']),13)
        self.assertEqual(index,self.v2)

    def test_complete_B2_thirteen_members_and_manifest_regenerate_equal(self):
        sealed,manifest=p.verify_B2()
        self.assertEqual(len(sealed['members']),13)
        self.assertTrue(manifest['full_manifest_regenerated_equal'])
        self.assertEqual(manifest,self.index['sensor_source_manifest'])

    def test_full_manifest_original_file_closure_not_only_runtime_three(self):
        closure=self.index['sensor_source_manifest']['original_source_closure']
        self.assertEqual((closure['unique_full_source_files'],closure['pin_references']),(155,435))
        self.assertEqual(len(closure['sources']),155)
        for row in closure['sources']:p.check_row(row)
        self.assertFalse(closure['plant_source_modules_executed'])

    def test_bad_original_manifest_pin_fails_closed(self):
        manifest=json.loads((p.B2/'SOURCE_API_MANIFEST.json').read_text(encoding='utf-8'))
        manifest['bridge']['source_sha256']='0'*64
        with self.assertRaises(ValueError):p.source_pin_closure(manifest)

    def test_bad_complete_member_pin_fails_closed(self):
        row=copy.deepcopy(self.index['dependency_sources'][0]);row['SHA256']='0'*64
        with self.assertRaises(ValueError):p.check_row(row)

    def test_installed_aliases_unchanged_only_sensor_origin_switched(self):
        self.assertEqual([x['install_relative'] for x in self.index['dependency_sources']],
                         [x['install_relative'] for x in self.v2['dependency_sources']])
        for old,new in zip(self.v2['dependency_sources'],self.index['dependency_sources']):
            if new['install_relative'].startswith('phase1_deps/sensor/'):
                self.assertEqual(Path(new['path']).parent,p.B2);p.check_row(new)
            else:self.assertEqual(old,new)

    def test_full_original17_C182_adapter_partition_unchanged(self):
        for key in ('original17','all_actuation_original_sources','parent_mechanical_diff','evalclose_mechanical_diff','bootstrap_original_sources'):
            self.assertEqual(self.index[key],self.v2[key])
        self.assertEqual(len(self.index['original17']),17)
        self.assertEqual(len(self.index['all_actuation_original_sources']),182)
        for name,count in (('actuation',8),('adapter',10),('partition',9)):
            self.assertEqual(self.index['dependency_seals'][name],self.v2['dependency_seals'][name])
            self.assertEqual(len(self.index['dependency_seals'][name]['members']),count)

    def test_eight_role_chain_source_only_not_live(self):
        manifest=json.loads((p.B2/'SOURCE_API_MANIFEST.json').read_text(encoding='utf-8'))
        self.assertEqual(len(manifest['roles']),8)
        for role,row in manifest['roles'].items():
            with self.subTest(role=role):
                self.assertEqual(row['reset_chain']['status'],'SOURCE_CONFIRMED_LIVE_UNKNOWN')
                self.assertEqual(len(row['reset_chain']['layers']),4)

    def test_actual_complete_B2_metadata_import_and_compatible_API(self):
        previous=sys.modules.get('source_api')
        try:
            api=p.full_source_import(p.B2/'source_api.py','source_api')
            passive=p.full_source_import(p.B2/'passive_capture.py','_phase1_v3_full_B2_passive_metadata_test')
            self.assertIs(passive.verify_existing_reset_chain,api.verify_existing_reset_chain)
            self.assertIs(passive.diagnose_preflight_bindings,api.diagnose_preflight_bindings)
            self.assertEqual(list(inspect.signature(passive.preflight).parameters),['env','bridge','module','role_api','bridge_pin'])
            self.assertEqual(list(inspect.signature(passive.install_passive_capture).parameters),
                ['env','bridge','feedback_module','role_api','bridge_pin','recorder','snapshot'])
            for name in ('preflight','install_passive_capture'):
                def args(folder):
                    tree=ast.parse((folder/'passive_capture.py').read_text(encoding='utf-8'))
                    return ast.dump(next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name).args,include_attributes=False)
                self.assertEqual(args(p.B2),args(ROOT/'source_phase1_passive_sensor_capture_v1'))
        finally:
            if previous is None:sys.modules.pop('source_api',None)
            else:sys.modules['source_api']=previous

    def test_readonly_diagnosis_references_and_upstream_scope(self):
        refs=p.verify_diagnostics()
        self.assertEqual(refs,self.index['sensor_reset_diagnostic_source_references'])
        self.assertEqual(len(refs['source_references']),4)
        receipt=self.index['sensor_source_manifest']['upstream_stdlib_receipt']
        self.assertEqual((receipt['tests_run'],receipt['composition_negative_subcases']),(28,21))
        self.assertFalse(receipt['actual_native_preflight_executed'])
        self.assertFalse(receipt['actual_Torch_CPU_executed_by_this_child'])
        self.assertTrue(self.index['sensor_source_manifest']['upstream_tests_not_reexecuted_here'])

    def test_wire_V1_and_source_version3_without_candidate_logic_diff(self):
        self.assertEqual(self.index['kind'],'PHASE1_CAPTURE_WORKER_SOURCE_INDEX_V1')
        self.assertEqual(self.index['source_version'],3)
        self.assertEqual(self.index['source_derivation']['candidate_logic_diff_count'],0)
        self.assertFalse(self.index['source_derivation']['strict_original_B2_verifier_reimplemented_here'])
        self.assertEqual(self.index['gate1'],'UNKNOWN')
        for key in ('native_executed','capture_interface_passed','exact','stage2_GO'):self.assertFalse(self.index[key])

    def test_no_native_modules_or_candidate_entrypoints_executed(self):
        self.assertFalse(any(name.split('.')[0] in ('torch','isaacsim','isaaclab','omni','pxr','warp','psutil','paramiko') for name in sys.modules))
        for name in p.INHERITED:
            self.assertEqual((HERE/name).read_bytes(),(p.V2/name).read_bytes())


def load_tests(loader,tests,pattern):
    # Import complete frozen V2 test source; retarget only metadata globals to
    # the byte-identical V3 candidate. No function cropping or physical reruns.
    old_path=list(sys.path)
    for leaf,name in (('phase1_capture_contract.py','phase1_capture_contract'),
                      ('phase1_capture_observer.py','phase1_capture_observer'),
                      ('phase1_capture_runtime.py','phase1_capture_runtime'),
                      ('worker_passive_interface_v1.py','worker_passive_interface_v1')):
        p.full_source_import(HERE/leaf,name)
    legacy=p.full_source_import(p.V2/'test_capture_worker_source.py','_v3_selected_full_frozen_V2_metadata_regressions')
    legacy.HERE=HERE;legacy.ROOT=ROOT;sys.path[:]=old_path
    suite=unittest.TestSuite([loader.loadTestsFromTestCase(V3SourceIntegrationTests)])
    suite.addTests(loader.loadTestsFromTestCase(legacy.FullOriginalStdlibCloseTests))
    # The one V2 source_version==2 assertion is replaced above by the explicit
    # V3 wire test; all other bootstrap regression method source is unchanged.
    for name in loader.getTestCaseNames(legacy.ActualOriginalBootstrapTests):
        if name!='test_wire_kinds_and_original_parent_unchanged':suite.addTest(legacy.ActualOriginalBootstrapTests(name))
    return suite


if __name__=='__main__':unittest.main(verbosity=2)
