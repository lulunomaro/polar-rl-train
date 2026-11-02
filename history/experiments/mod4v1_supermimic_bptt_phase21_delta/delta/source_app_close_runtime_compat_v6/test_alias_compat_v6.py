"""Own CPU fake export aliases. NO SDK import; fake source pin is PRIVATE."""
import ast
from contextlib import contextmanager
from dataclasses import replace
import hashlib
import importlib.util
import json
from pathlib import Path
import sys,time,types,unittest
from unittest import mock

B=Path(__file__).resolve().parent;ROOT=B.parent
sys.path.insert(0,str(ROOT/'source_resume_runtime_v2'))
import app_close_semantics_v6 as compat

CANONICAL='isaacsim.simulation_app.simulation_app';ALTERNATE='simulation_app.simulation_app'
FIXTURE=B/'GATE_SCRATCH_V6/_synthetic_app_fixture_v5.py'

@contextmanager
def synthetic_alias(module_name):
    raw=FIXTURE.read_bytes();module=types.ModuleType(module_name);module.__file__=str(FIXTURE)
    previous=sys.modules.get(module_name);sys.modules[module_name]=module
    exec(compile(raw,str(FIXTURE),'exec'),module.__dict__)
    pin=compat._AppPin(CANONICAL,'FakeApp',len(raw),hashlib.sha256(raw).hexdigest(),
                       module.FakeApp.close.__code__.co_firstlineno,module_aliases=(ALTERNATE,))
    try:
        with mock.patch.object(compat,'_APP_PIN',pin):yield module
    finally:
        if previous is None:sys.modules.pop(module_name,None)
        else:sys.modules[module_name]=previous

class AliasTests(unittest.TestCase):
    def test_production_policy_only_two_explicit_export_modules(self):
        self.assertEqual(compat._allowed_app_modules(compat._APP_PIN),(CANONICAL,ALTERNATE))
        self.assertEqual(compat._APP_PIN.class_name,'SimulationApp')
        self.assertEqual((compat._APP_PIN.source_bytes,compat._APP_PIN.close_firstlineno),(48933,848))
        self.assertEqual(compat._APP_PIN.source_SHA256,'6af5372bb0cdda6e665a30cd285ff724b3e5bd012dbdd4df458e0726173fc903')

    def test_both_synthetic_export_modules_producer_and_owner_match_actual_alias(self):
        for name in (CANONICAL,ALTERNATE):
            with self.subTest(name=name),synthetic_alias(name) as module:
                app=module.FakeApp();before=dict(app.config)
                value=compat._pin_original_app_close(app);compat._validate_binding_receipt(value)
                self.assertEqual(value['actual_module'],name)
                self.assertEqual(value['actual_type_name'],'FakeApp')
                self.assertEqual(value['actual_class'],name+'.FakeApp')
                self.assertEqual(value['actual_MRO'],[name+'.FakeApp','builtins.object'])
                self.assertEqual(value['close_module'],name)
                self.assertEqual(value['close_owner'],name+'.FakeApp')
                self.assertEqual(value['source_code_version'],compat.SOURCE_CODE_VERSION)
                self.assertEqual(value['helper_source_SHA256'],hashlib.sha256((B/'app_close_semantics_v6.py').read_bytes()).hexdigest())
                self.assertEqual(app.calls,0);self.assertEqual(app.config,before)

    def test_unknown_export_module_fail_closed_with_plain_names(self):
        with synthetic_alias('unpublished_headless.simulation_app') as module:
            with self.assertRaises(compat.AppCloseEvidenceError) as caught:compat._pin_original_app_close(module.FakeApp())
            error=str(caught.exception)
            self.assertIn('V6_ACTUAL_APP_PYTHON_NAMES=',error)
            actual=json.loads(error.split('V6_ACTUAL_APP_PYTHON_NAMES=',1)[1])
            self.assertEqual(actual['actual_module'],'unpublished_headless.simulation_app')
            self.assertEqual(actual['actual_type_name'],'FakeApp')
            self.assertEqual(actual['actual_MRO'][-1],'builtins.object')

    def test_receipt_actual_module_may_not_be_unknown(self):
        with synthetic_alias(ALTERNATE) as module:
            value=compat._pin_original_app_close(module.FakeApp());value['actual_module']='unpublished.simulation_app'
            with self.assertRaises(compat.AppCloseEvidenceError):compat._validate_binding_receipt(value)

    def test_receiver_does_not_rewrite_alias_class_to_canonical(self):
        with synthetic_alias(ALTERNATE) as module:
            value=compat._pin_original_app_close(module.FakeApp());value['actual_class']=CANONICAL+'.FakeApp'
            with self.assertRaises(compat.AppCloseEvidenceError):compat._validate_binding_receipt(value)

    def test_receiver_does_not_rewrite_alias_close_module_to_canonical(self):
        with synthetic_alias(ALTERNATE) as module:
            value=compat._pin_original_app_close(module.FakeApp());value['close_module']=CANONICAL
            with self.assertRaises(compat.AppCloseEvidenceError):compat._validate_binding_receipt(value)

    def test_receiver_requires_actual_module_type_name_and_V6_version(self):
        with synthetic_alias(ALTERNATE) as module:
            initial=compat._pin_original_app_close(module.FakeApp())
            for key in ('actual_module','actual_type_name','source_code_version','helper_source_SHA256'):
                with self.subTest(key=key):
                    value=dict(initial);value.pop(key)
                    with self.assertRaises(compat.AppCloseEvidenceError):compat._validate_binding_receipt(value)

    def test_receiver_rejects_wrong_exact_MRO_or_helper_SHA(self):
        with synthetic_alias(ALTERNATE) as module:
            initial=compat._pin_original_app_close(module.FakeApp())
            for key,bad in [('actual_MRO',[ALTERNATE+'.FakeApp','fake.Headless','builtins.object']),('helper_source_SHA256','0'*64),('helper_source_file','relative.py')]:
                with self.subTest(key=key):
                    value=dict(initial);value[key]=bad
                    with self.assertRaises(compat.AppCloseEvidenceError):compat._validate_binding_receipt(value)

    def test_subclass_even_with_same_spelling_is_not_exact_class(self):
        with synthetic_alias(ALTERNATE) as module:
            subclass=type('FakeApp',(module.FakeApp,),{'__module__':ALTERNATE})
            with self.assertRaises(compat.AppCloseEvidenceError):compat._pin_original_app_close(subclass())

    def test_method_definition_module_must_equal_actual_alias(self):
        with synthetic_alias(ALTERNATE) as module:
            module.FakeApp.close.__module__=CANONICAL
            with self.assertRaises(compat.AppCloseEvidenceError):compat._pin_original_app_close(module.FakeApp())

    def test_wrong_source_same_alias_not_accepted(self):
        with synthetic_alias(ALTERNATE) as module:
            with mock.patch.object(compat,'_APP_PIN',replace(compat._APP_PIN,source_SHA256='0'*64)):
                with self.assertRaises(compat.AppCloseEvidenceError):compat._pin_original_app_close(module.FakeApp())

    def test_false_mode_remains_known_nonfast_and_no_fast_receipt(self):
        with synthetic_alias(ALTERNATE) as module:
            value=compat._pin_original_app_close(module.FakeApp(fast_shutdown=False))
            self.assertIs(value['fast_shutdown'],False)
            with self.assertRaises(compat.AppCloseEvidenceError):compat._validate_binding_receipt(value)

    def test_unpatched_production_pin_rejects_all_synthetic_alias_fixtures(self):
        module=types.ModuleType('own_fake_module');module.__file__=str(FIXTURE)
        exec(compile(FIXTURE.read_bytes(),str(FIXTURE),'exec'),module.__dict__)
        with self.assertRaises(compat.AppCloseEvidenceError):compat._pin_original_app_close(module.FakeApp())

class SourceTests(unittest.TestCase):
    def test_all_original_close_FINAL_error_wait_and_bounded_recorder_bodies_unchanged(self):
        old=ast.parse((ROOT/'source_app_close_semantics_v5/app_close_semantics_v5.py').read_bytes())
        new=ast.parse((B/'app_close_semantics_v6.py').read_bytes())
        changed={'_AppPin','_pin_original_app_close','_validate_binding_receipt'}
        for node in old.body:
            if isinstance(node,(ast.FunctionDef,ast.ClassDef)) and node.name not in changed:
                other=next(n for n in new.body if isinstance(n,type(node)) and n.name==node.name)
                self.assertEqual(ast.dump(node,include_attributes=False),ast.dump(other,include_attributes=False),node.name)

    def test_published_source_shows_two_export_branches_not_runtime_module_proof(self):
        text=(ROOT/'discovery/sdk_reset_cache_backend_v2/isaacsim/package_init.py').read_text(encoding='utf-8')
        tree=ast.parse(text);function=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='expose_api')
        exports=[n.module for n in ast.walk(function) if isinstance(n,ast.ImportFrom) and any(a.name=='SimulationApp' for a in n.names)]
        self.assertEqual(set(exports),{'isaacsim.simulation_app','simulation_app'})
        self.assertIn('sys.modules["isaacsim.simulation_app"]',text)

    def test_no_SDK_Torch_import_and_staged_ABI_bytes_identical(self):
        self.assertNotIn('torch',sys.modules)
        self.assertFalse(any(n.startswith(('isaacsim','isaaclab','warp','omni.')) for n in sys.modules))
        self.assertEqual((B/'app_close_semantics_v6.py').read_bytes(),(B/'GATE_SCRATCH_V6/app_close_semantics_v5.py').read_bytes())
        tree=ast.parse((B/'app_close_semantics_v6.py').read_bytes())
        imports=[n.module for n in ast.walk(tree) if isinstance(n,ast.ImportFrom)]
        imports.extend(a.name for n in ast.walk(tree) if isinstance(n,ast.Import) for a in n.names)
        self.assertFalse(set(imports)&{'torch','isaacsim','isaaclab','warp','subprocess'})

if __name__=='__main__':
    start=time.perf_counter();result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__]))
    value=dict(kind='OWN_SYNTHETIC_ALIAS_SOURCE_CPU_NOT_NATIVE_V6',tests=result.testsRun,passed=result.wasSuccessful(),failures=len(result.failures),errors=len(result.errors),duration_seconds=time.perf_counter()-start,SDK_Torch_native_GPU_original_PT_or_account_operations=0,past_or_new_native_actual_module=None)
    with (B/'CPU_ALIAS_TEST_RESULTS_V6.json').open('x',encoding='utf-8') as f:json.dump(value,f,indent=2);f.write('\n')
    raise SystemExit(0 if result.wasSuccessful() else 1)
