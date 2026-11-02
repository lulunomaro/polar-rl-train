"""Create NEW V4 stdlib fake/AST regression suite without editing sealed V3."""
from __future__ import annotations
import ast
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCE = ROOT/'source_pose_cache_runtime_adapter_v3'/'test_pose_cache_runtime_adapter_v3.py'
TARGET = HERE/'test_pose_cache_runtime_adapter_v4.py'

ADDITIONAL = r'''
class NativeStaleSentinelTests(unittest.TestCase):
    # Reuse only the old stdlib fake source-binding fixture, not inherited tests.
    setUp = AdapterFakeTests.setUp
    install = AdapterFakeTests.install
    stamps = AdapterFakeTests.stamps

    def tag(self):
        return dict(kind='STALE_SENTINEL', value='NEGATIVE_INFINITY',
                    python_type='builtins.float', actual_native_value_read=True)

    def test_native_float_negative_infinity_each_of_eight_buffers_is_stale_metadata_only(self):
        for name in a.ROOT_DERIVED_BUFFERS:
            with self.subTest(buffer=name):
                self.robot=FakeRobot(); self.events=[]
                getattr(self.robot._data,name).timestamp=-float('inf')
                handle=a.install_pose_cache_runtime_adapter_v4(self.robot,receipt_callback=self.events.append)
                self.assertEqual(self.events[-1]['before']['timestamps'][name],self.tag())
                self.assertEqual(self.events[-1]['before']['timestamp_python_types'][name],'builtins.float')
                self.assertEqual(getattr(self.robot._data,name).timestamp,-float('inf'))
                self.assertEqual(self.robot.write_calls,[])
                self.assertEqual(self.robot._data._sim_timestamp,0.)
                json.dumps(handle.receipt(),allow_nan=False)
                self.robot.write_root_state_to_sim(object())
                self.assertEqual(self.stamps(),{n:-1. for n in a.ROOT_DERIVED_BUFFERS})
                json.dumps(self.events,allow_nan=False)

    def test_mixed_finite_minus_one_and_native_stale_fields_preserve_actual_types(self):
        self.robot._data._sim_timestamp=.2
        values=(0, .1, -float('inf'), -1., 0., .2, -float('inf'), -1)
        for name,value in zip(a.ROOT_DERIVED_BUFFERS,values):
            getattr(self.robot._data,name).timestamp=value
        self.install(); before=self.events[-1]['before']
        self.assertEqual(before['clock'],.2)
        self.assertEqual(before['clock_python_type'],'builtins.float')
        for name,value in zip(a.ROOT_DERIVED_BUFFERS,values):
            expected=self.tag() if type(value) is float and value==-math.inf else value
            self.assertEqual(before['timestamps'][name],expected)
            self.assertEqual(before['timestamp_python_types'][name],type(value).__module__+'.'+type(value).__qualname__)
        self.assertEqual(self.stamps(),dict(zip(a.ROOT_DERIVED_BUFFERS,values)))
        json.dumps(self.events,allow_nan=False)

    def test_clock_negative_infinity_positive_infinity_nan_bool_and_negative_remain_rejected(self):
        for value in (-float('inf'),float('inf'),float('nan'),True,-1.):
            with self.subTest(value=repr(value)):
                self.robot=FakeRobot(); self.events=[]
                self.robot._data._sim_timestamp=value
                with self.assertRaises(a.PoseCacheAdapterError):self.install()
                self.assertEqual(self.robot.write_calls,[])
                self.assertNotIn('write_root_state_to_sim',vars(self.robot))
                json.dumps(self.events,allow_nan=False)

    def test_nan_positive_infinity_bool_future_and_negative_non_sentinel_each_buffer_still_rejected(self):
        for name in a.ROOT_DERIVED_BUFFERS:
            for value in (float('nan'),float('inf'),True,.02,-2.):
                with self.subTest(buffer=name,value=repr(value)):
                    self.robot=FakeRobot(); self.events=[]
                    getattr(self.robot._data,name).timestamp=value
                    with self.assertRaises(a.PoseCacheAdapterError):self.install()
                    self.assertEqual(self.robot.write_calls,[])
                    self.assertNotIn('write_root_state_to_sim',vars(self.robot))
                    json.dumps(self.events,allow_nan=False)

    def test_unknown_scalar_and_float_subclass_are_not_coerced(self):
        class Wrapped:
            conversions=0
            def __float__(self):
                self.conversions+=1
                raise AssertionError('custom conversion must not run')
        class FloatSubclass(float):pass
        wrapped=Wrapped()
        for value in (wrapped,FloatSubclass('-inf'),'-inf',None):
            self.robot=FakeRobot(); self.events=[]
            self.robot._data._root_link_vel_w.timestamp=value
            with self.assertRaises(a.PoseCacheAdapterError):self.install()
            self.assertEqual(self.robot.write_calls,[])
        self.assertEqual(wrapped.conversions,0)

    def test_sealed_v3_number_rejects_the_same_native_stale_value(self):
        source=ROOT/'source_pose_cache_runtime_adapter_v3'/'pose_cache_runtime_adapter_v3.py'
        tree=ast.parse(source.read_text(encoding='utf-8'))
        node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='_number')
        namespace={'math':math,'PoseCacheAdapterError':a.PoseCacheAdapterError}
        exec(compile(ast.Module(body=[node],type_ignores=[]),str(source),'exec'),namespace)
        with self.assertRaises(a.PoseCacheAdapterError) as error:
            namespace['_number'](-float('inf'),'_root_link_vel_w',clock=0.)
        self.assertEqual(error.exception.code,'NON_NATIVE_FINITE_TIMESTAMP')
        self.assertEqual(a._number(-float('inf'),'_root_link_vel_w',clock=0.),-float('inf'))

    def test_original_writer_can_leave_native_stale_before_adapter_invalidates_to_minus_one(self):
        data=self.robot._data
        class WriterLog(list):
            def append(self,value):
                super().append(value)
                data._root_link_vel_w.timestamp=-float('inf')
        self.robot.write_calls=WriterLog()
        self.install(); result=self.robot.write_root_state_to_sim(object())
        self.assertIs(result,self.robot.return_value)
        self.assertEqual(len(self.robot.write_calls),1)
        self.assertEqual(self.stamps(),{n:-1. for n in a.ROOT_DERIVED_BUFFERS})
        self.assertEqual(self.events[-1]['event'],'write_returned_and_invalidated')
        json.dumps(self.events,allow_nan=False)

    def test_original_writer_error_preserves_native_stale_without_fake_invalidation(self):
        self.robot._data._root_link_vel_w.timestamp=-float('inf')
        self.install(); primary=ValueError('unchanged original exception');self.robot.failure=primary
        with self.assertRaises(ValueError) as caught:self.robot.write_root_state_to_sim(object())
        self.assertIs(caught.exception,primary)
        self.assertEqual(self.robot._data._root_link_vel_w.timestamp,-float('inf'))
        self.assertEqual(self.events[-1]['event'],'original_writer_raised')
        json.dumps(self.events,allow_nan=False)

    def test_logical_v3_alias_has_v4_source_version_and_no_pin_override(self):
        self.assertIs(a.install_pose_cache_runtime_adapter_v3,a.install_pose_cache_runtime_adapter_v4)
        self.assertEqual(list(inspect.signature(a.install_pose_cache_runtime_adapter_v4).parameters),['robot','receipt_callback'])
        self.install()
        self.assertEqual(self.events[-1]['kind'],'PINNED_INSTANCE_POSE_CACHE_ADAPTER_V4')
        self.assertEqual(self.events[-1]['source_code_version'],a.SOURCE_CODE_VERSION)

    def test_source_chassis_com_emits_native_negative_infinity_but_warp_constructor_defaults_minus_one(self):
        path=ROOT/'discovery/reward_command_audit_v1/E3/runtime/isaac/mod4/chassis_com_pose_roundtrip_sdk_adapter.py'
        tree=ast.parse(path.read_text(encoding='utf-8'))
        cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ChassisCOMSDK')
        method=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='invalidate_COM_dependent_cache')
        assignment=next(n for n in ast.walk(method) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Attribute) and t.attr=='timestamp' for t in n.targets))
        self.assertEqual(ast.unparse(assignment.value),"-float('inf')")
        self.assertIn('_root_link_vel_w',ast.unparse(method))
        warp=ROOT/'discovery/sdk_warp_timestamp_actual_v4/timestamped_buffer_warp.py'
        warp_tree=ast.parse(warp.read_text(encoding='utf-8'))
        stamps=[n for n in ast.walk(warp_tree) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Attribute) and t.attr=='timestamp' for t in n.targets)]
        self.assertEqual([ast.unparse(n.value) for n in stamps],['-1.0'])

    def test_actual_v5_bounded_recorder_accepts_v4_tagged_json_without_kind_gate_change(self):
        source=ROOT/'source_app_close_semantics_v5'/'app_close_semantics_v5.py'
        tree=ast.parse(source.read_text(encoding='utf-8'))
        names={'AppCloseEvidenceError','_need','BoundedPoseCacheEventsV5'}
        nodes=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in names]
        self.assertEqual({n.name for n in nodes},names)
        namespace={'json':json,'math':math,'time':time,'BOUNDED_EVENTS_KIND':'POSE_CACHE_RUNTIME_ADAPTER_BOUNDED_EVENTS_V5'}
        exec(compile(ast.Module(body=nodes,type_ignores=[]),str(source),'exec'),namespace)
        publications=[];recorder=namespace['BoundedPoseCacheEventsV5'](publications.append,clock=lambda:0.)
        self.robot._data._root_link_vel_w.timestamp=-float('inf')
        self.install(callback=recorder)
        self.robot.write_root_state_to_sim(object())
        self.assertEqual(recorder.snapshot()['event_counts']['installed'],1)
        self.assertEqual(recorder.snapshot()['event_counts']['write_returned_and_invalidated'],1)
        self.assertEqual(publications[0]['first_three'][0]['before']['timestamps']['_root_link_vel_w'],self.tag())
        json.dumps(publications,allow_nan=False)

    def test_original_binding_and_write_mutation_logic_AST_unchanged(self):
        source=ROOT/'source_pose_cache_runtime_adapter_v3'/'pose_cache_runtime_adapter_v3.py'
        old=ast.parse(source.read_text(encoding='utf-8'))
        new=ast.parse((HERE/'pose_cache_runtime_adapter_v4.py').read_text(encoding='utf-8'))
        def named(tree,name):return next(n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name==name)
        for name in ('_Pins','_plain','_source','_bound_owner','_validate_binding'):
            self.assertEqual(ast.dump(named(old,name)),ast.dump(named(new,name)))
        for name in ('__init__','_invoke','_check_data','_emit','receipt','uninstall'):
            def method(tree):
                return next(n for n in named(tree,'PoseCacheAdapterHandle').body if isinstance(n,ast.FunctionDef) and n.name==name)
            self.assertEqual(ast.dump(method(old)),ast.dump(method(new)))
'''

def main():
    raw=SOURCE.read_bytes()
    old=raw.decode('utf-8')
    new=old.replace('import ast\n','import ast\nimport math\n',1).replace('import pose_cache_runtime_adapter_v3 as a','import pose_cache_runtime_adapter_v4 as a',1)
    new=new.replace("HERE/'pose_cache_runtime_adapter_v3.py'", "HERE/'pose_cache_runtime_adapter_v4.py'")
    body=new.split("if __name__=='__main__':",1)[0]
    ending='''\nif __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,default=HERE/'CPU_TEST_RESULTS_V4.json')
    args=parser.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    start=time.perf_counter();suite=unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    receipt=dict(kind='STDLIB_SHADOW_SENTINEL_AND_SOURCE_AST_NOT_SDK_OR_NATIVE',tests_run=result.testsRun,
        failures=len(result.failures),errors=len(result.errors),passed=result.wasSuccessful(),
        elapsed_seconds=time.perf_counter()-start,SDK_imports=0,Torch_imports=0,GPU_steps=0,
        native_installations=0,native_steps=0,C_reads_writes=0,Git_operations=0,
        old_V3_regressions_retained=True,new_native_stale_sentinel_cases=True,
        shadow_fake_source_binding_pins_only=True,SDK_source_pins_unchanged=True,
        history_runtime_raw_timestamp_value_known=False,
        actual_new_native_type_value_tag_receipt_still_pending=True)
    with args.output.open('x',encoding='utf-8') as handle:
        json.dump(receipt,handle,ensure_ascii=False,indent=2,allow_nan=False);handle.write('\\n')
    print(json.dumps(receipt));sys.exit(0 if result.wasSuccessful() else 1)
'''
    text=body+ADDITIONAL+ending
    tree=ast.parse(text);compile(tree,str(TARGET),'exec')
    with TARGET.open('x',encoding='utf-8',newline='\n') as handle:handle.write(text)
    assert SOURCE.read_bytes()==raw
    print(json.dumps(dict(kind='SHADOW_TEST_SOURCE_ONLY_BUILD',path=str(TARGET),bytes=len(text.encode('utf-8')),SHA256=hashlib.sha256(text.encode('utf-8')).hexdigest(),test_methods=sum(isinstance(n,ast.FunctionDef) and n.name.startswith('test_') for n in ast.walk(tree)),old_test_source_SHA=hashlib.sha256(raw).hexdigest(),old_source_unchanged=True)))

if __name__=='__main__':main()
