"""Stdlib CPU FAKE tests and AST-only real-source comparisons; no SDK import."""
import ast
from dataclasses import replace
import hashlib
import inspect
import json
from pathlib import Path
import sys
import time
from types import FunctionType, MethodType
import unittest
from unittest.mock import patch

import pose_cache_runtime_adapter_v3 as a

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
BACKEND=ROOT/'discovery'/'sdk_reset_cache_backend_v2'/'backend'
PRODUCTION_PINS=a._PINNED

class FakeBuffer:
    def __init__(self):self.timestamp=0.;self.data=object()

class SlotBuffer:
    __slots__=('timestamp','data')
    def __init__(self):self.timestamp=0.;self.data=object()

class PropertyBuffer:
    def __init__(self):self.data=object();self.reads=0
    @property
    def timestamp(self):
        self.reads+=1;raise AssertionError('timestamp getter must not run')

class FakeData:
    __backend_name__='physx'
    def __init__(self):
        self._sim_timestamp=0.
        for name in a.ROOT_DERIVED_BUFFERS:setattr(self,name,FakeBuffer())
    @property
    def projected_gravity_b(self):raise AssertionError('extra SDK gravity getter')
    @property
    def heading_w(self):raise AssertionError('extra SDK heading getter')
    def update(self,dt):raise AssertionError('extra SDK update')

class DifferentData(FakeData):pass

class FakeRobot:
    def __init__(self):
        self._data=FakeData();self.write_calls=[];self.pose_calls=0;self.vel_calls=0
        self.return_value=object();self.failure=None;self.advance_clock=False;self.replace_buffer=False
    @property
    def data(self):raise AssertionError('even robot.data property is not sampled')
    def write_root_state_to_sim(self,root_state,env_ids=None):
        self.write_calls.append((root_state,env_ids))
        if self.failure is not None:raise self.failure
        self.write_root_link_pose_to_sim_index(root_pose=root_state,env_ids=env_ids)
        self.write_root_com_velocity_to_sim_index(root_velocity=root_state,env_ids=env_ids)
        if self.advance_clock:self._data._sim_timestamp+=.02
        if self.replace_buffer:self._data._heading_w=FakeBuffer()
        return self.return_value
    def write_root_link_pose_to_sim_index(self,*,root_pose,env_ids=None,full_data=False):self.pose_calls+=1
    def write_root_com_velocity_to_sim_index(self,*,root_velocity,env_ids=None,full_data=False):self.vel_calls+=1

class FakeSubclass(FakeRobot):pass
class OverrideDelegate(FakeRobot):
    def write_root_link_pose_to_sim_index(self,*,root_pose,env_ids=None,full_data=False):pass

class AdapterFakeTests(unittest.TestCase):
    def setUp(self):
        raw=Path(__file__).read_bytes();digest=hashlib.sha256(raw).hexdigest()
        pins=a._Pins(__name__,'FakeRobot',digest,len(raw),__name__,'FakeData',digest,len(raw))
        self.pins=pins;self.policy=patch.object(a,'_PINNED',pins);self.policy.start();self.addCleanup(self.policy.stop)
        self.robot=FakeRobot();self.events=[]
    def install(self,callback=None):
        return a.install_pose_cache_runtime_adapter_v3(self.robot,receipt_callback=self.events.append if callback is None else callback)
    def stamps(self):return {n:getattr(self.robot._data,n).timestamp for n in a.ROOT_DERIVED_BUFFERS}
    def test_fake_install_has_actual_new_binding_metadata_not_past_claim(self):
        h=self.install();e=self.events[-1]
        self.assertEqual(e['event'],'installed');self.assertTrue(e['binding']['checked_this_new_instance'])
        self.assertIsNone(e['binding']['past_worker_binding_claim'])
        self.assertEqual(e['binding']['writer_owner']['SHA256'],self.pins.asset_sha256)
        self.assertEqual(e['binding']['data_source']['SHA256'],self.pins.data_sha256)
        self.assertIn(__name__+'.FakeRobot',e['binding']['asset_actual_MRO'])
        self.assertTrue(h.receipt()['active'])
    def test_install_does_not_write_or_invalidate_cache(self):
        self.install();self.assertEqual(self.robot.write_calls,[])
        self.assertEqual(self.stamps(),{n:0. for n in a.ROOT_DERIVED_BUFFERS})
    def test_writer_called_once_arguments_and_return_identity_preserved(self):
        self.install();state=object();env_ids=[2,7]
        r=self.robot.write_root_state_to_sim(state,env_ids=env_ids)
        self.assertIs(r,self.robot.return_value)
        self.assertEqual(len(self.robot.write_calls),1);self.assertIs(self.robot.write_calls[0][0],state)
        self.assertIs(self.robot.write_calls[0][1],env_ids)
        self.assertEqual((self.robot.pose_calls,self.robot.vel_calls),(1,1))
    def test_only_eight_stamps_changed_data_array_and_buffer_identity_preserved(self):
        d=self.robot._data;before={n:(getattr(d,n),getattr(d,n).data) for n in a.ROOT_DERIVED_BUFFERS}
        other=FakeBuffer();d.unrelated_cache=other
        self.install();self.robot.write_root_state_to_sim(object())
        self.assertEqual(self.stamps(),{n:-1. for n in a.ROOT_DERIVED_BUFFERS})
        self.assertEqual(d._sim_timestamp,0.)
        self.assertEqual(before,{n:(getattr(d,n),getattr(d,n).data) for n in a.ROOT_DERIVED_BUFFERS})
        self.assertEqual(other.timestamp,0.)
    def test_callback_small_metadata_counts_and_no_raw_state(self):
        h=self.install();self.robot.write_root_state_to_sim(object())
        e=self.events[-1];json.dumps(e)
        self.assertEqual(e['event'],'write_returned_and_invalidated')
        self.assertEqual((e['write_call_count'],e['original_return_count'],e['invalidated_write_count']),(1,1,1))
        self.assertEqual(e['before']['clock'],e['after']['clock'])
        self.assertNotIn('root_state',e);self.assertEqual(e['extra_getter_samples'],0)
        self.assertEqual(h.receipt()['counters']['extra_RNG_draws'],0)
    def test_repeated_writes_counts_without_any_extra_observation(self):
        h=self.install()
        for i in range(3):self.robot.write_root_state_to_sim(object())
        self.assertEqual(h.receipt()['counters']['invalidated_write_count'],3)
        self.assertEqual(len(self.robot.write_calls),3)
    def test_other_direct_writer_is_not_wrapped(self):
        self.install();self.robot.write_root_link_pose_to_sim_index(root_pose=object())
        self.assertEqual(self.robot.pose_calls,1);self.assertEqual(len(self.events),1)
        self.assertEqual(self.robot._data._projected_gravity_b.timestamp,0.)
    def test_class_and_second_instance_not_mutated(self):
        original=FakeRobot.write_root_state_to_sim;other=FakeRobot();self.install()
        self.assertIs(FakeRobot.write_root_state_to_sim,original)
        self.assertIs(other.write_root_state_to_sim.__func__,original)
    def test_inherited_asset_mro_with_original_delegates_is_recorded(self):
        self.robot=FakeSubclass();h=self.install()
        self.assertEqual(h.receipt()['binding']['asset_actual_MRO'][0],__name__+'.FakeSubclass')
    def test_derived_override_of_called_delegate_is_fail_closed(self):
        self.robot=OverrideDelegate()
        with self.assertRaises(a.PoseCacheAdapterError):self.install()
        self.assertEqual(self.robot.write_calls,[])
    def test_asset_source_hash_mismatch_stops_before_install(self):
        with patch.object(a,'_PINNED',replace(self.pins,asset_sha256='0'*64)):
            with self.assertRaises(a.PoseCacheAdapterError):self.install()
        self.assertNotIn('write_root_state_to_sim',vars(self.robot));self.assertEqual(self.robot.write_calls,[])
    def test_data_source_hash_mismatch_stops_before_install(self):
        with patch.object(a,'_PINNED',replace(self.pins,data_sha256='1'*64)):
            with self.assertRaises(a.PoseCacheAdapterError):self.install()
        self.assertNotIn('write_root_state_to_sim',vars(self.robot))
    def test_data_subclass_does_not_satisfy_exact_data_pin(self):
        self.robot._data=DifferentData()
        with self.assertRaises(a.PoseCacheAdapterError):self.install()
    def test_missing_actual_module_file_is_fail_closed(self):
        with patch.object(sys.modules[__name__],'__file__',None):
            with self.assertRaises(a.PoseCacheAdapterError):self.install()
    def test_wrong_bound_self_is_fail_closed(self):
        other=FakeRobot();self.robot.write_root_state_to_sim=other.write_root_state_to_sim
        with self.assertRaises(a.PoseCacheAdapterError):self.install()
        self.assertEqual(other.write_calls,[])
    def test_instance_lambda_or_untracked_wrapper_is_fail_closed(self):
        self.robot.write_root_state_to_sim=MethodType(lambda self,*x,**k:None,self.robot)
        with self.assertRaises(a.PoseCacheAdapterError):self.install()
    def test_method_code_line_not_matching_pinned_source_is_fail_closed(self):
        old=FakeRobot.write_root_state_to_sim
        func=FunctionType(old.__code__.replace(co_firstlineno=old.__code__.co_firstlineno+1),globals(),old.__name__)
        with patch.object(FakeRobot,'write_root_state_to_sim',func):
            with self.assertRaises(a.PoseCacheAdapterError):self.install()
    def test_backend_mismatch_is_fail_closed(self):
        self.robot._data.__backend_name__='newton'
        with self.assertRaises(a.PoseCacheAdapterError):self.install()
    def test_missing_buffer_validates_all_before_any_stamp_mutation(self):
        del self.robot._data._root_com_ang_vel_b
        with self.assertRaises(a.PoseCacheAdapterError):self.install()
        self.assertEqual(self.robot._data._projected_gravity_b.timestamp,0.)
    def test_none_data_rejected(self):
        self.robot._data._heading_w.data=None
        with self.assertRaises(a.PoseCacheAdapterError):self.install()
    def test_property_timestamp_not_evaluated(self):
        b=PropertyBuffer();self.robot._data._heading_w=b
        with self.assertRaises(a.PoseCacheAdapterError):self.install()
        self.assertEqual(b.reads,0)
    def test_plain_slot_buffer_supported_without_properties(self):
        for n in a.ROOT_DERIVED_BUFFERS:setattr(self.robot._data,n,SlotBuffer())
        self.install();self.robot.write_root_state_to_sim(object())
        self.assertTrue(all(v==-1. for v in self.stamps().values()))
    def test_nan_clock_rejected_before_original_write(self):
        self.robot._data._sim_timestamp=float('nan')
        with self.assertRaises(a.PoseCacheAdapterError):self.install()
        self.assertEqual(self.robot.write_calls,[])
    def test_bool_or_nonfinite_buffer_timestamp_rejected(self):
        for bad in (True,float('inf'),float('nan')):
            self.robot._data._heading_w.timestamp=bad
            with self.assertRaises(a.PoseCacheAdapterError):self.install()
    def test_future_timestamp_rejected(self):
        self.robot._data._heading_w.timestamp=.1
        with self.assertRaises(a.PoseCacheAdapterError):self.install()
    def test_negative_non_sentinel_timestamp_rejected(self):
        self.robot._data._heading_w.timestamp=-2.
        with self.assertRaises(a.PoseCacheAdapterError):self.install()
    def test_duplicate_install_is_fail_closed_without_overwriting_first(self):
        first=self.install();wrapper=self.robot.write_root_state_to_sim
        with self.assertRaises(a.PoseCacheAdapterError):self.install()
        self.assertIs(self.robot.write_root_state_to_sim,wrapper);self.assertTrue(first.receipt()['active'])
    def test_original_exception_preserved_no_invalidation(self):
        h=self.install();error=ValueError('original failure');self.robot.failure=error
        with self.assertRaises(ValueError) as caught:self.robot.write_root_state_to_sim(object())
        self.assertIs(caught.exception,error);self.assertEqual(self.events[-1]['event'],'original_writer_raised')
        self.assertEqual(h.receipt()['counters']['original_return_count'],0)
        self.assertEqual(self.stamps(),{n:0. for n in a.ROOT_DERIVED_BUFFERS})
    def test_failure_is_sticky_even_if_caller_catches_and_changes_error_condition(self):
        h=self.install();self.robot.failure=ValueError('primary')
        with self.assertRaises(ValueError):self.robot.write_root_state_to_sim(object())
        self.robot.failure=None
        with self.assertRaises(a.PoseCacheAdapterError):self.robot.write_root_state_to_sim(object())
        self.assertEqual(len(self.robot.write_calls),1);self.assertTrue(h.receipt()['failed_sticky'])
    def test_original_baseexception_not_silenced(self):
        self.install();error=SystemExit(9);self.robot.failure=error
        with self.assertRaises(SystemExit) as caught:self.robot.write_root_state_to_sim(object())
        self.assertEqual(caught.exception.code,9)
    def test_callback_failure_does_not_mask_original_exception(self):
        def callback(event):
            if event['event']=='original_writer_raised':raise RuntimeError('receipt failure')
        self.install(callback);self.robot.failure=ValueError('primary')
        with self.assertRaises(ValueError) as caught:self.robot.write_root_state_to_sim(object())
        self.assertEqual(str(caught.exception),'primary')
    def test_install_callback_failure_rolls_back_instance_binding(self):
        def callback(event):raise RuntimeError('receipt failure')
        with self.assertRaises(a.PoseCacheAdapterError):self.install(callback)
        self.assertNotIn('write_root_state_to_sim',vars(self.robot));self.assertEqual(self.robot.write_calls,[])
    def test_write_callback_failure_is_fail_closed_after_invalidation(self):
        def callback(event):
            if event['event']=='write_returned_and_invalidated':raise RuntimeError('receipt failure')
        h=self.install(callback)
        with self.assertRaises(a.PoseCacheAdapterError):self.robot.write_root_state_to_sim(object())
        self.assertEqual(self.stamps(),{n:-1. for n in a.ROOT_DERIVED_BUFFERS})
        self.assertEqual(h.receipt()['counters']['callback_failure_count'],1)
    def test_clock_advance_in_original_writer_rejected_not_faked_back(self):
        self.install();self.robot.advance_clock=True
        with self.assertRaises(a.PoseCacheAdapterError):self.robot.write_root_state_to_sim(object())
        self.assertEqual(self.robot._data._sim_timestamp,.02)
        self.assertEqual(self.events[-1]['event'],'adapter_rejected_after_write')
        self.assertEqual(self.robot._data._heading_w.timestamp,0.)
    def test_buffer_identity_change_rejected_after_original_return(self):
        self.install();self.robot.replace_buffer=True
        with self.assertRaises(a.PoseCacheAdapterError):self.robot.write_root_state_to_sim(object())
        self.assertEqual(self.events[-1]['event'],'adapter_rejected_after_write')
    def test_data_identity_change_before_write_stops_original(self):
        self.install();self.robot._data=FakeData()
        with self.assertRaises(a.PoseCacheAdapterError):self.robot.write_root_state_to_sim(object())
        self.assertEqual(self.robot.write_calls,[])
    def test_buffer_array_change_before_write_stops_original(self):
        self.install();self.robot._data._heading_w.data=object()
        with self.assertRaises(a.PoseCacheAdapterError):self.robot.write_root_state_to_sim(object())
        self.assertEqual(self.robot.write_calls,[])
    def test_callback_gets_copy_cannot_mutate_handle_receipt(self):
        def callback(event):event.clear()
        h=self.install(callback)
        self.assertEqual(h.receipt()['last_event']['event'],'installed')
    def test_uninstall_restores_class_lookup_not_old_stale_stamps(self):
        h=self.install();self.robot.write_root_state_to_sim(object());h.uninstall()
        self.assertNotIn('write_root_state_to_sim',vars(self.robot))
        self.assertIs(self.robot.write_root_state_to_sim.__func__,FakeRobot.write_root_state_to_sim)
        self.assertFalse(h.receipt()['active']);self.assertEqual(self.robot._data._heading_w.timestamp,-1.)
    def test_uninstall_preserves_existing_exact_instance_binding(self):
        previous=self.robot.write_root_state_to_sim;self.robot.write_root_state_to_sim=previous
        h=self.install();h.uninstall();self.assertIs(vars(self.robot)['write_root_state_to_sim'],previous)
    def test_uninstall_does_not_overwrite_foreign_new_binding(self):
        h=self.install();foreign=lambda *x,**k:None;self.robot.write_root_state_to_sim=foreign
        with self.assertRaises(a.PoseCacheAdapterError):h.uninstall()
        self.assertIs(self.robot.write_root_state_to_sim,foreign)
    def test_reentrant_write_during_callback_is_stopped_before_second_original(self):
        def callback(event):
            if event['event']=='write_returned_and_invalidated':
                with self.assertRaises(a.PoseCacheAdapterError):self.robot.write_root_state_to_sim(object())
        self.install(callback);self.robot.write_root_state_to_sim(object())
        self.assertEqual(len(self.robot.write_calls),1)
    def test_bound_wrapper_rejects_a_different_self(self):
        self.install();other=FakeRobot()
        with self.assertRaises(a.PoseCacheAdapterError):self.robot.write_root_state_to_sim.__func__(other,object())
        self.assertEqual(other.write_calls,[]);self.assertEqual(self.robot.write_calls,[])
    def test_required_receipt_callback(self):
        with self.assertRaises(a.PoseCacheAdapterError):self.install(callback=0)
    def test_public_API_has_no_verified_bool_or_pin_override(self):
        params=list(inspect.signature(a.install_pose_cache_runtime_adapter_v3).parameters)
        self.assertEqual(params,['robot','receipt_callback'])

class RealSourceASTTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.asset_raw=(BACKEND/'articulation.py').read_bytes()
        cls.data_raw=(BACKEND/'articulation_data.py').read_bytes()
        cls.asset_tree=ast.parse(cls.asset_raw);cls.data_tree=ast.parse(cls.data_raw)
    def method(self,tree,cls_name,name):
        cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name==cls_name)
        return next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name==name)
    def test_unpatched_production_default_rejects_fake_before_install(self):
        self.assertIs(a._PINNED,PRODUCTION_PINS);robot=FakeRobot();events=[]
        with self.assertRaises(a.PoseCacheAdapterError):a.install_pose_cache_runtime_adapter_v3(robot,receipt_callback=events.append)
        self.assertNotIn('write_root_state_to_sim',vars(robot));self.assertEqual(robot.write_calls,[])
        self.assertEqual(events[-1]['event'],'install_rejected')
    def test_production_pins_match_actual_fetched_bytes(self):
        self.assertEqual(hashlib.sha256(self.asset_raw).hexdigest(),PRODUCTION_PINS.asset_sha256)
        self.assertEqual(hashlib.sha256(self.data_raw).hexdigest(),PRODUCTION_PINS.data_sha256)
        self.assertEqual(len(self.asset_raw),PRODUCTION_PINS.asset_bytes)
        self.assertEqual(len(self.data_raw),PRODUCTION_PINS.data_bytes)
    def test_original_full_state_writer_calls_only_expected_pose_velocity_pair(self):
        m=self.method(self.asset_tree,'Articulation','write_root_state_to_sim')
        calls=[n.func.attr for n in ast.walk(m) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and isinstance(n.func.value,ast.Name) and n.func.value.id=='self']
        self.assertEqual(calls,['write_root_link_pose_to_sim_index','write_root_com_velocity_to_sim_index'])
    def test_exact_eight_timestamps_omitted_by_pose_setter(self):
        m=self.method(self.asset_tree,'Articulation','write_root_link_pose_to_sim_index')
        assigned={t.value.attr for n in ast.walk(m) if isinstance(n,ast.Assign) for t in n.targets if isinstance(t,ast.Attribute) and t.attr=='timestamp' and isinstance(t.value,ast.Attribute)}
        self.assertIn('_root_state_w',assigned);self.assertFalse(set(a.ROOT_DERIVED_BUFFERS)&assigned)
    def test_gravity_and_heading_getters_strict_timestamp_comparison(self):
        for name,field in [('projected_gravity_b','_projected_gravity_b'),('heading_w','_heading_w')]:
            m=self.method(self.data_tree,'ArticulationData',name)
            condition=next(n.test for n in ast.walk(m) if isinstance(n,ast.If))
            self.assertEqual(ast.unparse(condition),f'self.{field}.timestamp < self._sim_timestamp')
    def test_original_data_accessor_returns_private_data_only(self):
        m=self.method(self.asset_tree,'Articulation','data')
        self.assertEqual(ast.unparse(m.body[0]),'return self._data')
    def test_original_bridge_order_and_threshold_not_changed(self):
        p=ROOT/'source_runtime'/'native_supermimic_bridge.py';text=p.read_text(encoding='utf-8')
        self.assertIn('root[:,3:7]=root[:,[6,3,4,5]]',text)
        self.assertIn('err<1e-3',text);self.assertIn('state[1][:,2,:]',text)
    def test_adapter_imports_stdlib_only_and_no_auto_install(self):
        tree=ast.parse((HERE/'pose_cache_runtime_adapter_v3.py').read_text(encoding='utf-8'))
        modules={n.module.split('.')[0] for n in tree.body if isinstance(n,ast.ImportFrom)}
        modules|={name.name.split('.')[0] for n in tree.body if isinstance(n,ast.Import) for name in n.names}
        self.assertTrue(modules<=set(sys.stdlib_module_names)|{'__future__'})
        self.assertFalse(any(isinstance(n,ast.Expr) and isinstance(n.value,ast.Call) for n in tree.body))
    def test_no_sdk_torch_or_task_import_in_test_process(self):
        self.assertNotIn('torch',sys.modules)
        self.assertFalse(any(k=='isaaclab' or k.startswith(('isaaclab.','isaaclab_physx.','isaacsim.')) for k in sys.modules))

if __name__=='__main__':
    start=time.perf_counter();suite=unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    receipt=dict(kind='STDLIB_CPU_FAKE_BEHAVIOR_AND_REAL_SOURCE_AST_NOT_NATIVE',tests_run=result.testsRun,
                 failures=len(result.failures),errors=len(result.errors),passed=result.wasSuccessful(),
                 elapsed_seconds=time.perf_counter()-start,SDK_imports=0,torch_imports=0,GPU_steps=0,
                 native_install_or_runtime_binding_claim=None,
                 tested_production_default_rejects_nonpinned_types=True,
                 fake_positive_tests_patch_private_pins_to_own_test_source=True)
    (HERE/'CPU_TEST_RESULTS_V3.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(receipt));sys.exit(0 if result.wasSuccessful() else 1)
