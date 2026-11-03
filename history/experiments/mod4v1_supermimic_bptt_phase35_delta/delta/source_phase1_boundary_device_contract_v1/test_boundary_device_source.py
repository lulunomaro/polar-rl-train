"""SOURCE/actual-full-stdlib-import tests; no Torch fixture invocation."""
from pathlib import Path
import ast
import inspect
import sys
import unittest
import boundary_device_contract as c
import torch_cpu_fixture as f


class BoundaryDeviceSourceTests(unittest.TestCase):
    def test_frozen_V3_all13_preserved(self):
        self.assertEqual(len(c.verify_v3()['files']),13)

    def test_complete_canonical_and_bridge_pins(self):
        rows=c.source_paths()
        self.assertEqual((rows['canonical']['bytes'],rows['canonical']['SHA256']),c.CORE_PIN)
        self.assertEqual((rows['bridge']['bytes'],rows['bridge']['SHA256']),c.BRIDGE_PIN)

    def test_actual_complete_canonical_metadata_import_API(self):
        module,row=c.load_full_canonical()
        self.assertIs(module.OriginalEpisodeBoundary.after_original_step.__globals__,module.__dict__)
        self.assertEqual(Path(module.OriginalEpisodeBoundary.__init__.__code__.co_filename).resolve(),Path(row['path']).resolve())
        self.assertEqual(list(inspect.signature(module.OriginalEpisodeBoundary.after_original_step).parameters),['self','terminated','truncated'])

    def test_source_candidate_is_not_actual_root_cause_claim(self):
        value=c.verify_source_contract()
        self.assertEqual(value['cause_status'],'SOURCE_CANDIDATE_NOT_ACTUAL_V3_ROOT_CAUSE_CONFIRMED')
        self.assertIsNone(value['actual_env_device_type'])
        self.assertIsNone(value['actual_V3_flags_shape_dtype_device'])
        self.assertFalse(value['actual_reports_read_by_this_child'])
        self.assertFalse(value['Torch_CPU_fixture_executed_here'])

    def test_canonical_predicate_and_bridge_bool_unchanged(self):
        value=c.verify_source_contract()
        self.assertTrue(value['canonical_API_unchanged'])
        self.assertFalse(value['predicate_relaxed'])
        self.assertFalse(value['bridge_bool_conversion_changed'])
        self.assertEqual(value['new_SDK_getters'],0)

    def test_bad_complete_core_pin_rejected(self):
        source=c.source_paths()['canonical']['path']
        with self.assertRaises(ValueError):c.check(source,(37927,'0'*64))

    def test_replacement_is_existing_bridge_member_only(self):
        self.assertEqual(c.OLD.replace('torch,env.device,','torch,bridge.device,'),c.NEW)
        node=ast.parse(c.NEW).body[0].value
        self.assertEqual(ast.unparse(node.args[1]),'bridge.device')
        self.assertEqual(node.keywords[0].arg,'n');self.assertEqual(node.keywords[0].value.value,80)

    def test_fixture_is_explicit_caller_injected_and_not_invoked(self):
        self.assertEqual(list(inspect.signature(f.run_torch_cpu_fixture).parameters),['torch_module','canonical_source'])
        tree=ast.parse(Path(f.__file__).read_text(encoding='utf-8'))
        self.assertFalse(any(isinstance(node,(ast.Expr,ast.Assign)) and isinstance(getattr(node,'value',None),ast.Call) for node in tree.body))
        self.assertFalse(any(isinstance(n,ast.Import) and any(a.name=='torch' for a in n.names) for n in tree.body))
        self.assertIsNotNone(next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main'))

    def test_fixture_source_asserts_rng_identity_masks_and_pairing(self):
        text=Path(f.__file__).read_text(encoding='utf-8')
        for literal in ('term.device!=\'cpu\'','old_steps==1','steps==receipt[\'actions\']==receipt[\'original_step_transitions\']==2',
                        'id(term)==term_id','t.equal(term,term_before)','random.getstate()==python_rng_before',
                        't.equal(t.get_rng_state(),torch_rng_before)','following is fixed.next_start'):
            self.assertIn(literal,text)
        self.assertNotIn('manual_seed',text);self.assertNotIn('.cuda',text)

    def test_fixture_keeps_negative_shape_dtype_and_step_predicates(self):
        text=Path(f.__file__).read_text(encoding='utf-8')
        for label in ('shape79','shape80x1','float32','int32','step_without_action','two_actions_without_step','non_N80'):
            self.assertIn(label,text)

    def test_no_Torch_SDK_or_native_module_imported(self):
        self.assertFalse(any(name.split('.')[0] in ('torch','numpy','isaacsim','isaaclab','omni','pxr','warp','paramiko','psutil') for name in sys.modules))


if __name__=='__main__':unittest.main(verbosity=2)
