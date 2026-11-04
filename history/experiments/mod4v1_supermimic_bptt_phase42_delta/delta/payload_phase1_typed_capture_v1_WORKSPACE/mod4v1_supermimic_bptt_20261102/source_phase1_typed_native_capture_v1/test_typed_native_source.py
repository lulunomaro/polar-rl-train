"""Ten NEW stdlib fake/AST checks. No old tests, Torch, SDK or worker main."""
from pathlib import Path
import ast
from contextlib import contextmanager
import importlib.util
import json
import sys
import unittest

import phase1_capture_contract as contract
import phase1_capture_observer as observer
import prepare_sources as preparation

HERE = Path(__file__).resolve().parent


class FakeTensor:
    """Own builtin metadata fixture; never a Torch tensor or a physical result."""
    def __init__(self, shape, dtype='torch.float32', data=None):
        self.shape, self.dtype, self.device = tuple(shape), dtype, 'cpu'
        self.data, self.operations = data, []

    def detach(self):
        self.operations.append('detach')
        return self

    def clone(self):
        raise AssertionError('NEW producer adoption must not clone an owned C2 payload')

    def index_select(self, *args):
        raise AssertionError('NEW C2 queue adoption / joint-ID metadata must not select rows')

    def cpu(self):
        self.operations.append('cpu')
        return self

    def tolist(self):
        self.operations.append('tolist')
        return self.data


@contextmanager
def published_metadata():
    """Normal full SOURCE module imports, metadata-only; no target construction."""
    names = ('typed_capture_codec', 'source_api', 'field_snapshot', 'dependency_contract')
    before = {name: sys.modules.get(name) for name in names}
    modules = {}
    try:
        for name in names:
            folder = preparation.CODEC if name == 'typed_capture_codec' else preparation.B4
            path = folder / (name + '.py')
            spec = importlib.util.spec_from_file_location(name, path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[name] = module
            spec.loader.exec_module(module)
            modules[name] = module
        yield modules
    finally:
        for name in reversed(names):
            if before[name] is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = before[name]


def make_codec(module):
    return module.CaptureCodec(FakeTensor, witness_index=FakeTensor((8,), 'torch.int64'),
                               witness_env_ids=list(range(8)), n=80)


def fake_task():
    return dict(kind=contract.KIND, purpose=contract.PURPOSE, batch_purpose=contract.PURPOSE,
        integration=contract.INTEGRATION, typed_producer_schema=contract.PRODUCER_ABI,
        policy_variant=contract.POLICY_VARIANT, role='E3', requested_roles=['E3'], role_catalog=list(contract.ROLES),
        num_envs=80, seed=20260928, controls=64, physics=dict(contract.PHYSICS), model_PT_reads=0,
        synthetic_action=[0., 0., 0., 0., 0., 0.], train=False, quality_evaluation=False,
        full_clean35='UNKNOWN', overall_eight_pass_rate=None, comparison=None,
        asset_SHA=contract.USD, contract_SHA=contract.CONTRACT, group_id='SOURCE_FAKE_GROUP',
        GPU_UUID='SOURCE_FAKE_GPU_NOT_RESOURCE_ADMISSION', absolute_worker_deadline_epoch=1234)


def calls(tree):
    return [node for node in ast.walk(tree) if isinstance(node, ast.Call)]


def function(path, name):
    return next(node for node in ast.parse(Path(path).read_bytes()).body
                if isinstance(node, ast.FunctionDef) and node.name == name)


class TypedNativeSourceTests(unittest.TestCase):
    def test_01_full_frozen_closure_and_finite_overlay(self):
        index, bundle = preparation.build_metadata()
        self.assertEqual(index, json.loads((HERE/'CAPTURE_SOURCE_INDEX.json').read_bytes()))
        self.assertEqual(bundle, json.loads((HERE/'FINITE_SOURCE_BUNDLE.json').read_bytes()))
        self.assertEqual([len(index[key]) for key in ('original17','new_sources','dependency_sources','bootstrap_original_sources')],
                         [17,5,9,2])
        self.assertEqual(len(bundle['full_module_files']),34)
        self.assertTrue(bundle['all_eight_runtime_trees_and_banks_REQUIRED'])
        self.assertTrue(bundle['original_static_tree_is_not_replaced_by_this_finite_source_overlay'])
        self.assertEqual(bundle['materialized_files'],0)
        aliases = {row['install_relative'] for row in index['dependency_sources']}
        self.assertIn('phase1_deps/sensor/CODEC_SOURCE_PINS.json',aliases)
        self.assertIn('phase1_deps/actuation_c2/actuation_tap_v2.py',aliases)
        self.assertNotIn('phase1_deps/actuation/actuation_tap.py',aliases)
        self.assertEqual(len(index['all_actuation_original_sources']),182)
        self.assertEqual(index['sensor_source_manifest']['original_source_closure']['unique_full_source_files'],155)

    def test_02_actual_wire_and_execution_is_not_science(self):
        abi = json.loads((HERE/'PRODUCER_ABI.json').read_bytes())
        self.assertEqual(abi['wire']['TASK.kind'],contract.KIND)
        self.assertEqual(abi['wire']['TASK.integration'],contract.INTEGRATION)
        self.assertEqual(abi['wire']['cases/E3/FINAL.kind'],contract.FINAL_KIND)
        self.assertEqual(abi['kind'],contract.PRODUCER_ABI)
        task = fake_task()
        contract.validate_task(task)
        sensor = dict(kind='PASSIVE_SENSOR_CAPTURE_V3', metadata_retention_complete=True,
            incomplete_current_control=None, control_ledger=dict(kind='BOUNDED_TYPED_CONTROL_LEDGER_V1',
                requested_controls=64,recorded_controls=64,run_id=task['group_id']+':E3',
                all_controls_observed=True,normal_channel_records=640,controls=['OWN_SOURCE_FAKE']*64))
        result = contract.candidate_final(task,completed=64,physics=512,feedback=128,
            delay_calls=dict(legs=512,wheels=512),boundary=dict(actions=64,original_step_transitions=64,pending_original_step=False),
            sensor=sensor,actuation=dict(capture_schema=observer.C2_CONTAINER),coverage={},rng_counts={},trace={},
            restore=dict(ok=True,order=['actuation','sensor','bridge']),setup={'fixture':'OWN_SOURCE_FAKE'})
        self.assertTrue(contract.validate_preclose(result,task))
        self.assertTrue(result['passed_execution'])  # Explicit synthetic metadata, not an actual waited run.
        for name in ('capture_interface_passed','exact','stage2_GO','paper_ready'):
            self.assertIs(result[name],False)
        self.assertEqual(result['science_consistency_status'],'UNKNOWN_PENDING_TYPED_CONSUMER')
        bad = dict(task,kind='PHASE1_PASSIVE_CAPTURE_E3_N80_TASK_V1')
        with self.assertRaises(ValueError):contract.validate_task(bad)
        bad_final = dict(result,actuation={'capture_schema':'OLD_C1_NOT_TYPED'})
        with self.assertRaises(ValueError):contract.validate_preclose(bad_final,task)

    def test_03_full_original_setup_and_once_calls(self):
        old = function(preparation.V4/'worker_passive_interface_v1.py','main')
        new = function(HERE/'worker_passive_interface_v1.py','main')
        def prefix(node):
            body = next(item for item in node.body if isinstance(item,ast.Try)).body
            stop = next(i for i,item in enumerate(body) if isinstance(item,ast.Assign)
                        and any(isinstance(t,ast.Name) and t.id=='boundary' for t in item.targets))
            return [ast.dump(item,include_attributes=False) for item in body[:stop+1]]
        self.assertEqual(prefix(old),prefix(new))
        names = [ast.unparse(node.func) for node in calls(new)]
        for name in ('env.reset','env.observation_manager.compute','bridge.init_state','bridge.step',
                     'boundary.for_action','boundary.after_original_step','sensor.begin_control','sensor.end_control','sensor.finish'):
            self.assertEqual(names.count(name),1,name)
        self.assertNotIn('torch.load',names)
        loop = next(node for node in ast.walk(new) if isinstance(node,ast.For)
                    and ast.unparse(node.iter)=="range(task['controls'])")
        ordered = {ast.unparse(node.func):node.lineno for node in calls(loop)}
        self.assertLess(ordered['sensor.begin_control'],ordered['bridge.step'])
        self.assertLess(ordered['bridge.step'],ordered['boundary.after_original_step'])
        self.assertLess(ordered['boundary.after_original_step'],ordered['sensor.end_control'])
        self.assertNotIn('sensor.finish',ordered)

    def test_04_default_published_22_plus_3_with_own_fake_metadata(self):
        with published_metadata() as modules:
            codec = make_codec(modules['typed_capture_codec'])
            snapshot = modules['field_snapshot'].FieldSnapshot(codec)
            ledger = modules['typed_capture_codec'].ControlLedger(codec,controls=64,run_id='OWN_SOURCE_FAKE')
            result = modules['dependency_contract'].verify_typed_dependency(snapshot,ledger)
            self.assertEqual(len(result['checked_functions']),22)
            self.assertEqual(len(result['classes']),3)
            self.assertEqual(result['expected_pins_sha256'],'5cd6c770c7f3541308201389f721b43f9e7c681199443c9a2f80d2f80347e452')
            self.assertEqual(result['actual_MDP_calls'],0)
            with self.assertRaises(ValueError):
                modules['dependency_contract'].verify_typed_dependency(snapshot,ledger,dependency_pins={})
            self.assertEqual(codec.witness_index.operations,[])

    def test_05_owned_C2_full80_no_second_copy_or_cast(self):
        with published_metadata() as modules:
            codec = make_codec(modules['typed_capture_codec'])
            clock = dict(physics_tick=888,feedback_tick=222,common_control_counter=4,phase='adoption',reset_depth=0)
            value = FakeTensor((80,),'torch.int64',[2**60+7]*80)
            typed = observer.adopt_queue_owned(value,codec,group='legs',source_ref='OWN_SOURCE_FAKE_PIN',field='episode',clock=clock)
            self.assertIs(typed['values'],value)
            self.assertEqual(value.operations,[])
            self.assertEqual(typed['retained_shape'],[80])
            self.assertEqual(typed['row_mapping']['env_ids'],list(range(80)))
            decoded = codec.materialize(typed)
            self.assertEqual(decoded['values'],[2**60+7]*80)
            self.assertEqual(value.operations,['detach','cpu','tolist'])
            self.assertEqual(decoded['original_dtype'],'torch.int64')
            boolean = FakeTensor((80,),'torch.bool',[True,False]*40)
            decoded = codec.materialize(observer.adopt_queue_owned(boolean,codec,group='wheels',
                source_ref='OWN_SOURCE_FAKE_PIN',field='pending_valid',clock=clock))
            self.assertIs(decoded['values'][0],True)
            self.assertIs(decoded['values'][1],False)

    def test_06_C2_scope_original_tick_and_joint_ID_unknown(self):
        with published_metadata() as modules:
            codec = make_codec(modules['typed_capture_codec'])
            clock = dict(physics_tick=888,feedback_tick=222,common_control_counter=4,phase='adoption',reset_depth=0)
            joint = FakeTensor((80,),'torch.int32')  # Same length N80 deliberately must NOT imply env IDs.
            command = FakeTensor((80,4))
            event = dict(capture_schema='ACTUATION_CLOCK_SCOPE_V2_SOURCE_DISABLED',seq=7,kind='target_write',
                group='legs',tick=31,write_scope='SAME_ASSET_TERM_APPLY_CONTEXT',raw_stored_counter=32,
                clock_source='original_parent_term_context',args=[command,joint],kwargs={},pre={'episode':FakeTensor((80,),'torch.int64')},
                post={},outcome='RETURNED',parent_term_apply_seq=6,active_term_context={'seq':6,'group':'legs','tick':31},
                setter={'method':'set_joint_position_target','joint_ids_source':'positional[1]_UNQUALIFIED_SDK_SIGNATURE','joint_ids':joint},
                physical_readback={'status':'UNKNOWN'},extra_original_key={'kept':True})
            result = observer.typed_c2_event(event,codec,None,source_ref='OWN_SOURCE_FAKE_PIN',clock=clock)
            self.assertTrue(set(event)<=set(result))
            self.assertEqual(result['tick'],31)
            self.assertEqual(result['adoption_clock']['physics_tick'],888)
            self.assertEqual(result['args'][0]['semantic_role'],'QUEUE_GROUP_FULL')
            self.assertEqual(result['args'][0]['source_clock']['physics_tick'],888)
            self.assertEqual(result['args'][1]['status'],'UNKNOWN')
            self.assertNotIn('envelope_kind',result['setter']['joint_ids'])
            self.assertEqual(result['typed_producer_metadata']['DOF_target_pipeline_join'],'UNKNOWN')
            self.assertEqual(result['capture_schema'],event['capture_schema'])
            self.assertEqual(joint.operations,[])
            self.assertEqual(command.operations,[])

    def test_07_only_first2_last2_C2_and_middle_UNKNOWN(self):
        with published_metadata() as modules:
            codec = make_codec(modules['typed_capture_codec'])
            clock = dict(physics_tick=8,feedback_tick=2,common_control_counter=1,phase='adoption',reset_depth=0)
            retained = observer.WindowRetention(codec,None,'OWN_SOURCE_FAKE_PIN')
            for index in range(64):
                retained.add(index,[dict(kind='queue_apply',seq=index,group='legs',tick=index,outcome='RETURNED')],clock=clock)
            result = retained.report()
            self.assertEqual(result['control_windows_seen'],64)
            self.assertEqual([row['control_index'] for row in result['first']],[0,1])
            self.assertEqual([row['control_index'] for row in result['last']],[62,63])
            self.assertEqual(result['middle_windows'],'UNKNOWN_UNRETAINED')
            with self.assertRaises(ValueError):retained.add(64,[{}]*8193,clock=clock)
            self.assertEqual(retained.count,64)

    def test_08_pending_is_original_no_synthetic_finish_and_restore_all(self):
        pending = {'kind':'B3_INCOMPLETE_OWNED_CONTROL','owned_partial_control':{'reset':{'outcome':'RAISED'}},
                   'b3_callback_provenance':{'original_pending_marker':True}}
        report = dict(incomplete_current_control=pending,control_ledger={'status':'PENDING_EXPLICIT_FINISH'})
        class Sensor:
            def report(self):return report
            def end_control(self,*args,**kwargs):raise AssertionError('No invented end')
            def finish(self):raise AssertionError('No invented finish')
        result = observer.incomplete_capture(fake_task(),Sensor(),None,None,source_error='OWN_SOURCE_FAKE_RAISED')
        self.assertIs(result['typed_pending_control'],pending)
        self.assertIs(result['sensor'],report)
        self.assertFalse(result['capture_interface_passed'])
        order = []
        class Close:
            def __init__(self,name):self.name=name
            def close(self):
                order.append(self.name)
                return {'restored':False} if self.name=='actuation' else None
        restored = observer.restore_interfaces(Close('actuation'),Close('sensor'),Close('bridge'))
        self.assertEqual(order,['actuation','sensor','bridge'])
        self.assertFalse(restored['ok'])
        self.assertEqual(len(restored['errors']),1)

    def test_09_complete_original_resource_and_App_close_functions_unchanged(self):
        result = preparation.verify_minimal_diff()
        self.assertTrue(result['parent_byte_identical'])
        self.assertEqual(preparation.identity(HERE/'single_gpu_passive_capture_parent_v1.py'),
            dict(bytes=9336,SHA256='d5575ff2e670fd18ea0a09d9f3d5c05c46bf606a027fcb84d97c6e34a88a2b41'))
        runtime = (HERE/'phase1_capture_runtime.py').read_text(encoding='utf-8')
        self.assertIn("put_json(case / 'APP_CLOSE_BINDING_PHASE1_CAPTURE_V1.json', binding, add_capture_epoch=False)",runtime)
        self.assertIn('core()._validate_returned_app_binding(binding, helper)',runtime)
        parent = (HERE/'single_gpu_passive_capture_parent_v1.py').read_text(encoding='utf-8')
        self.assertIn('p.wait',parent)
        self.assertIn('if waited:',parent)

    def test_10_no_new_MDP_RNG_getters_and_default_native_install_order(self):
        main = function(HERE/'worker_passive_interface_v1.py','main')
        nodes = calls(main)
        restore = next(node for node in nodes if ast.unparse(node.func)=='restore_interfaces')
        materializers = [node for node in nodes if ast.unparse(node.func)=='codec.materialize']
        self.assertEqual(len(materializers),2)
        self.assertTrue(all(node.lineno>restore.lineno for node in materializers))
        native_install = next(node for node in nodes if ast.unparse(node.func)=='sensor_api.install_passive_capture')
        self.assertNotIn('dependency_pins',{kw.arg for kw in native_install.keywords})
        actual = function(preparation.B4/'passive_capture.py','install_passive_capture')
        ordered = {ast.unparse(node.func):node.lineno for node in calls(actual)}
        self.assertLess(ordered['verify_typed_dependency'],ordered['preflight'])
        self.assertLess(ordered['preflight'],ordered['PassiveCapture'])
        own = ast.parse((HERE/'phase1_capture_observer.py').read_bytes())
        names = [ast.unparse(node.func) for node in calls(own)]
        for name in names:
            self.assertFalse(name.endswith(('.cpu','.tolist','.clone','.float','.to','.step','.reset','.compute','.get_state','.set_state')),
                             name)
        for name in ('torch','isaaclab','isaacsim','omni','pxr','genesis'):
            self.assertNotIn(name,sys.modules)


if __name__ == '__main__':
    unittest.main(verbosity=2)
