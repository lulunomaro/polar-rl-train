"""Only deterministic stdlib fake/AST tests; no SSH, SDK, Torch or actual collect."""
from pathlib import Path
import ast
import copy
import hashlib
import io
import json
import sys
import tempfile
import unittest
from unittest.mock import patch
import collect_capture_result as collector
import remote_metadata_reader as remote
import source_pins

HERE = Path(__file__).resolve().parent


def dispatch():
    gid = remote.PREFIX+'FAKE_STDLIB_ONLY'
    return dict(root=remote.BASE+'/tasks/'+gid,group_id=gid,purpose=remote.PURPOSE,
        controller=dict(pid=101,linux_start_ticks='10001'),parent=dict(pid=102,linux_start_ticks='10002'),
        parent_source_SHA=remote.PARENT_SHA,actual_native_parent_Popen_calls=1,
        SDK_scene_or_skill_admission=False,stage_receipt_SHA256='b'*64)


def packet():
    d = dispatch(); flags = dict(gate1='UNKNOWN',capture_interface_passed=False,exact=False,stage2_GO=False)
    worker = dict(kind='PHASE1_PASSIVE_CAPTURE_E3_N80_FINAL_V1',purpose=remote.PURPOSE,
        group_id=d['group_id'],role='E3',controls=64,physics_callbacks=512,feedback_samples=128,
        delay_calls=dict(legs=512,wheels=512),passed_execution=True,model_PT_reads=0,
        training_updates=0,optimizer_updates=0,learner_created=False,replay_created=False,teacher_created=False,
        full_clean35='UNKNOWN',policy_variant='EXPLICIT_SYNTHETIC_ZERO6_NOT_POLICY_QUALITY',
        coverage=dict(deficits=['PER_ROW_LIVE_VERIFIER_PENDING']),**flags)
    terminal = [dict(role='E3',pid=103,returncode=0,actual_waited=True,passed_execution=True,
        error=None,semantic=dict(passed_execution=True),data=worker)]
    docs = {
        'GROUP_PLAN.json':dict(kind='PHASE1_PASSIVE_CAPTURE_E3_ONLY_PLAN_V1',batch_purpose=remote.PURPOSE,
            group_id=d['group_id'],requested_roles=['E3']),
        'STAGE_COMPLETE_PHASE1_CAPTURE_V1.json':dict(materialized=True,parent_launches=0,
            purpose=remote.PURPOSE,GROUP_PLAN_SHA256='a'*64),
        'PHASE1_CAPTURE_PARENT_DISPATCH_REQUEST_V1.json':dict(d,controller_source_SHA=remote.CONTROLLER_SHA),
        'PHASE1_CAPTURE_PARENT_DISPATCH_RECEIPT_V1.json':dict(d,kind='ONE_ORIGINAL_PHASE1_CAPTURE_PARENT_POPEN_NOT_RESOURCE_ADMISSION'),
        'PHASE1_CAPTURE_PARENT_CONTROLLER_STARTED_V1.json':dict(kind='OWN_PHASE1_CAPTURE_PARENT_ACTUAL_WAIT_CONTROLLER_V1',
            controller=d['controller'],parent_source_SHA=remote.PARENT_SHA,controller_resource_SDK_model_C_lock_or_signal_operations=0),
        'PARENT_STARTED.json':dict(kind='ONEGPU_PHASE1_PASSIVE_CAPTURE_E3_ONLY_PARENT_V1',pid=102,requested_roles=['E3']),
        'CHILDREN.json':[dict(role='E3',pid=103,root=d['root']+'/cases/E3',worker='worker_passive_interface_v1.py')],
        remote.OUTER:dict(d,kind='ACTUAL_EXTERNAL_PARENT_POPEN_WAIT_PHASE1_CAPTURE_V1',
            actual_parent_p_wait_returned=True,returncode=0,controller_errors=[],
            original_parent_resource_close_wait_not_replaced=True,controller_resource_SDK_model_C_lock_or_signal_operations=0),
        'PARENT_EXIT_SCOPE.json':dict(all_own_children_waited=True,original_single_GPU_private_EX_released=True,
            original_global_finite_EX_released=True,canonical_writes=0,errors=[],no_foreign_scope_touched=True,
            child_waits=[dict(role='E3',pid=103,returncode=0,actual_waited=True)]),
        'PHASE1_CAPTURE_GROUP_CLOSED_SOURCE_GRADE_V1.json':dict(kind='PHASE1_CAPTURE_CLOSED_SOURCE_GRADE_V1',
            purpose=remote.PURPOSE,passed_closed_capture_execution=True,errors=[],**flags),
        'FINAL.json':dict(kind='PHASE1_PASSIVE_CAPTURE_GROUP_FINAL_V1',purpose=remote.PURPOSE,
            group_id=d['group_id'],requested_roles=['E3'],passed_execution=True,terminal=terminal,GO_epoch=123.,**flags),
        'TERMINAL_ROWS.json':terminal,'cases/E3/FINAL.json':worker,
        'cases/E3/task.json':dict(kind='PHASE1_PASSIVE_CAPTURE_E3_N80_TASK_V1',purpose=remote.PURPOSE,
            group_id=d['group_id'],controls=64,train=False,quality_evaluation=False),
        'ACTUAL_GROUP_ADMISSION.json':dict(group_id=d['group_id'],original_private_GPU_EX_held=True,
            original_global_finite_EX_held=True,canonical_writes=0),
        'GROUP_EVAL_START.json':dict(kind='PHASE1_PASSIVE_CAPTURE_COMMON_START_V1',purpose=remote.PURPOSE,
            group_id=d['group_id'],members=['E3'],epoch=123.),
        'cases/E3/WORKER_SCENE_READY.json':dict(role='E3'),
        'cases/E3/WORKER_EVAL_STARTED.json':dict(role='E3',GO_epoch=123.),
    }
    return dict(kind='PHASE1_CAPTURE_OWN_METADATA_PACKET_V1',documents=docs,collector_errors=[],
        file_metadata={'GROUP_PLAN.json':dict(SHA256='a'*64),
            'STAGE_COMPLETE_PHASE1_CAPTURE_V1.json':dict(SHA256='b'*64),
            'cases/E3/FINAL.json':dict(SHA256='c'*64,bytes=12345,whole_JSON_read=True,
                new_capture_trace_fields_parsed=True,trace_payload_exported=False,read_count=1)},
        closure=dict(source_aliases=27,full_AppV6_Base_imported=True,native_modules_loaded=[]),
        metadata_validation=dict(original_capture_plan=True,original_capture_preclose=True,
            original_app_close_metadata=True,errors=[]),watch=dict(stop_reason='OUTER_WAIT_FILE_PUBLISHED'))


class Tests(unittest.TestCase):
    def test_fixed_source_pins_and_old_partition_nine(self):
        result = source_pins.verify_sources()
        self.assertEqual(result['source_count'],50)
        self.assertEqual(result['old_member_counts']['source_phase1_state_context_partition_v1/SOURCE_SEAL.json'],9)

    def test_valid_dispatch_exact_current_parent(self):
        self.assertIs(remote.validate_dispatch(dispatch())['SDK_scene_or_skill_admission'],False)

    def test_foreign_old_relative_and_traversal_roots(self):
        for root in ('/tmp/other',remote.BASE+'/tasks/OLD_BOUND',dispatch()['root']+'/../x',
                     remote.BASE+'/tasks/'+remote.PREFIX+'bad/name'):
            with self.subTest(root=root):
                value=dispatch();value['root']=root
                with self.assertRaises(ValueError):remote.validate_dispatch(value)

    def test_missing_identity_or_boolean_count_rejected(self):
        for key in ('controller','parent','parent_source_SHA','stage_receipt_SHA256'):
            value=dispatch();value.pop(key)
            with self.assertRaises(ValueError):remote.validate_dispatch(value)
        value=dispatch();value['actual_native_parent_Popen_calls']=True
        with self.assertRaises(ValueError):remote.validate_dispatch(value)

    def test_complete_fake_execution_never_promotes_gate1(self):
        result=collector.summarize(dispatch(),packet())
        self.assertTrue(result['passed_closed_capture_execution'],result['errors'])
        self.assertEqual(result['status'],'PASS_CLOSED_CAPTURE_EXECUTION_METADATA_ONLY')
        for key in ('capture_interface_passed','exact','stage2_GO','paper_ready'):
            self.assertIs(result[key],False)
        self.assertEqual(result['gate1'],'UNKNOWN');self.assertIsNone(result['skill_success_rate'])

    def test_rc0_alone_and_materialized_alone_are_not_pass(self):
        for docs in ({remote.OUTER:dict(returncode=0)}, {'STAGE_COMPLETE_PHASE1_CAPTURE_V1.json':dict(materialized=True)}):
            result=collector.summarize(dispatch(),dict(documents=docs))
            self.assertFalse(result['passed_closed_capture_execution'])

    def test_missing_observed_counts_are_null_not_zero(self):
        result=collector.summarize(dispatch(),dict(documents={}))
        for key in ('controls','physics_callbacks','feedback_samples','model_PT_reads','training_updates','optimizer_updates'):
            self.assertIsNone(result['worker_observed'][key])
        self.assertIsNone(result['actual_native_parent_Popen_calls'])
        self.assertIsNone(result['actual_parent_wait_returned']);self.assertIsNone(result['remote_FINAL_read_count'])

    def test_outer_wait_is_independent_of_parent_finally(self):
        value=packet();value['documents'].pop(remote.OUTER)
        result=collector.summarize(dispatch(),value)
        self.assertTrue(result['checks']['parent_own_child_wait_and_both_EX_release'])
        self.assertFalse(result['checks']['independent_outer_actual_parent_wait'])
        self.assertFalse(result['passed_closed_capture_execution'])

    def test_pid_reuse_start_ticks_and_rc_nonzero(self):
        value=packet();value['documents'][remote.OUTER]['parent']=dict(pid=102,linux_start_ticks='9999')
        self.assertFalse(collector.summarize(dispatch(),value)['checks']['outer_wait_identity'])
        value=packet();value['documents'][remote.OUTER]['returncode']=1
        self.assertEqual(collector.summarize(dispatch(),value)['status'],'FAIL_CLOSED_CAPTURE_EXECUTION')

    def test_missing_either_EX_release_never_passes(self):
        for key in ('original_single_GPU_private_EX_released','original_global_finite_EX_released'):
            value=packet();value['documents']['PARENT_EXIT_SCOPE.json'][key]=False
            self.assertFalse(collector.summarize(dispatch(),value)['passed_closed_capture_execution'])

    def test_old_quality_final_and_false_training_claim_rejected(self):
        value=packet();value['documents']['cases/E3/FINAL.json']['kind']='OLD_QUALITY_FINAL'
        self.assertFalse(collector.summarize(dispatch(),value)['checks']['worker_same_task_and_complete_bound'])
        value=packet();value['documents']['cases/E3/FINAL.json']['model_PT_reads']=1
        self.assertFalse(collector.summarize(dispatch(),value)['checks']['synthetic_PT0_probe_not_quality_or_training'])

    def test_fake_interface_true_is_recorded_as_contradiction(self):
        value=packet();value['documents']['cases/E3/FINAL.json']['capture_interface_passed']=True
        result=collector.summarize(dispatch(),value)
        self.assertFalse(result['passed_closed_capture_execution'])
        self.assertTrue(result['worker_observed']['producer_capture_interface_passed'])
        self.assertFalse(result['capture_interface_passed'])

    def test_resource1800_zero_GO_reason_is_preserved(self):
        value=packet();value['documents']={
            'PARENT_ORIGINAL_ERROR.json':dict(errors=['Originalresourcewait1800sexpiredwithoutSDK/model/foreignactions']),
            'BOUNDED_ORIGINAL_RESOURCE_WAIT.json':[dict(reason='Selectedcardhasexistingcomputeprocess',locks_held=0)]}
        result=collector.summarize(dispatch(),value)
        self.assertEqual(result['status'],'FAIL_CLOSED_CAPTURE_EXECUTION')
        self.assertIn('1800s',json.dumps(result['published_metadata']))
        self.assertIsNone(result['worker_observed']['controls'])

    def test_group_plan_digest_and_terminal_identity_mismatch(self):
        value=packet();value['file_metadata']['GROUP_PLAN.json']['SHA256']='z'*64
        self.assertFalse(collector.summarize(dispatch(),value)['checks']['materialization_is_not_admission'])
        value=packet();value['documents']['CHILDREN.json'][0]['pid']=999
        self.assertFalse(collector.summarize(dispatch(),value)['checks']['actual_child_terminal_receipts'])

    def test_trace_projection_never_exports_payload(self):
        value=packet()['documents']['cases/E3/FINAL.json'];value['bounded_trace']={'secret_capture_payload':[123]*100}
        value['sensor']={'events':['RAW']};value['actuation']={'trace':['RAW']}
        for result in (remote.project('cases/E3/FINAL.json',value),
            remote.project('FINAL.json',dict(terminal=[dict(data=value)]))['terminal'][0]['data']):
            self.assertNotIn('bounded_trace',result);self.assertNotIn('sensor',result);self.assertNotIn('actuation',result)

    def test_whole_final_hash_once_and_honest_trace_read_flags(self):
        with tempfile.TemporaryDirectory(prefix='fake_final_',dir=HERE) as name:
            root=Path(name);self.assertTrue(root.resolve().is_relative_to(HERE))
            raw=json.dumps(dict(kind='FAKE',bounded_trace={'read_but_not_exported':[1,2,3]})).encode()
            (root/'FINAL.json').write_bytes(raw);reader=remote.MetadataReader(root)
            with self.assertRaises(ValueError):reader.read('FINAL.json')
            first=reader.read('FINAL.json',terminal=True);second=reader.read('FINAL.json',terminal=True)
            self.assertIs(first,second);info=reader.info['FINAL.json']
            self.assertEqual(info['read_count'],1);self.assertEqual(info['SHA256'],hashlib.sha256(raw).hexdigest())
            self.assertTrue(info['whole_JSON_read']);self.assertTrue(info['new_capture_trace_fields_parsed'])
            self.assertFalse(info['trace_payload_exported'])

    def test_no_raw_model_or_other_path_alias(self):
        reader=remote.MetadataReader(HERE)
        for alias in ('../outside.json','/proc/123/stat','model.pt','capture.jsonl','capture.npz','state/C.json'):
            with self.subTest(alias=alias):
                with self.assertRaises(ValueError):reader.read(alias)

    def test_immutable_changed_metadata_is_error_not_second_read(self):
        with tempfile.TemporaryDirectory(prefix='fake_immutable_',dir=HERE) as name:
            root=Path(name);path=root/'PARENT_EXIT_SCOPE.json';path.write_text('{"ok":1}')
            reader=remote.MetadataReader(root);reader.read('PARENT_EXIT_SCOPE.json');path.write_text('{"ok":22222}')
            reader.read('PARENT_EXIT_SCOPE.json')
            self.assertEqual(reader.info['PARENT_EXIT_SCOPE.json']['read_count'],1)
            self.assertTrue(reader.errors)

    def test_stdout_tail_has_fixed_16KiB_bound(self):
        with tempfile.TemporaryDirectory(prefix='fake_log_',dir=HERE) as name:
            root=Path(name);(root/remote.LOGS[0]).write_bytes(b'x'*20000)
            result=remote.MetadataReader(root).tail(remote.LOGS[0])
            self.assertEqual(result['bytes_read'],16384);self.assertEqual(len(result['tail']),16384)

    def test_collector_cap_only_no_parent_stop(self):
        class Reader:
            def __init__(self):self.cache={};self.calls=[]
            def read(self,name,**kwargs):self.calls.append((name,kwargs))
        class Clock:
            value=0
            def now(self):return self.value
            def sleep(self,d):self.value+=d
        reader=Reader();clock=Clock()
        result=remote.watch(reader,cap_seconds=40,interval_seconds=20,monotonic=clock.now,sleep=clock.sleep)
        self.assertEqual(result['polls'],3);self.assertEqual(result['signals_sent'],0)
        self.assertIn('COLLECTOR_CAP_ONLY',result['stop_reason'])
        for name in remote.BIG:
            self.assertEqual(sum(n==name for n,_ in reader.calls),1)
        self.assertEqual(reader.calls[-1][1],dict(terminal=True))

    def test_outer_wait_stops_watch_without_pid_scan(self):
        class Reader:
            def __init__(self):self.cache={};self.calls=[]
            def read(self,name,**kwargs):
                self.calls.append(name)
                if name==remote.OUTER:self.cache[name]={}
        reader=Reader();result=remote.watch(reader,monotonic=lambda:0,sleep=lambda n:self.fail('sleep after outer receipt'))
        self.assertEqual(result['polls'],1);self.assertEqual(result['stop_reason'],'OUTER_WAIT_FILE_PUBLISHED')

    def test_terminal_validator_uses_cached_full_hash_no_reread(self):
        class Contract:
            def validate_plan(self,*args):pass
            def validate_preclose(self,*args):pass
        class App:
            def _validate_binding_receipt(self,value):pass
        class Reader:pass
        reader=Reader();binding={'fast_shutdown':True};reader.cache={
            'GROUP_PLAN.json':{},'cases/E3/task.json':{},'cases/E3/FINAL.json':{},
            'cases/E3/APP_CLOSE_BINDING_PHASE1_CAPTURE_V1.json':binding,
            'cases/E3/ENV_CLOSE_RETURNED_PHASE1_CAPTURE_V1.json':dict(closed=True),
            'cases/E3/APP_FAST_CLOSE_INTENT_PHASE1_CAPTURE_V1.json':dict(kind='PINNED_PHASE1_CAPTURE_FAST_CLOSE_INTENT_V1',
                binding=binding,final_SHA='f'*64,final_bytes=123,original_env_close_returned=True)}
        reader.info={'cases/E3/FINAL.json':dict(SHA256='f'*64,bytes=123,read_count=1)}
        result=remote.validate_terminal_cache(reader,dispatch(),dict(contract=Contract(),index={},app=App()))
        self.assertTrue(result['original_app_close_metadata']);self.assertEqual(reader.info['cases/E3/FINAL.json']['read_count'],1)
        reader.cache['cases/E3/APP_FAST_CLOSE_INTENT_PHASE1_CAPTURE_V1.json']['final_SHA']='e'*64
        self.assertFalse(remote.validate_terminal_cache(reader,dispatch(),dict(contract=Contract(),index={},app=App()))['original_app_close_metadata'])

    def test_added_binding_epoch_is_not_silently_removed(self):
        class App:
            def _validate_binding_receipt(self,value):pass
        class Reader:pass
        reader=Reader();original=dict(fast_shutdown=True);published=dict(original,capture_metadata_epoch=1.)
        reader.cache={'cases/E3/APP_CLOSE_BINDING_PHASE1_CAPTURE_V1.json':published,
            'cases/E3/ENV_CLOSE_RETURNED_PHASE1_CAPTURE_V1.json':dict(closed=True),
            'cases/E3/APP_FAST_CLOSE_INTENT_PHASE1_CAPTURE_V1.json':dict(kind='PINNED_PHASE1_CAPTURE_FAST_CLOSE_INTENT_V1',
                binding=original,final_SHA='f'*64,final_bytes=123,original_env_close_returned=True)}
        reader.info={'cases/E3/FINAL.json':dict(SHA256='f'*64,bytes=123,read_count=1)}
        result=remote.validate_terminal_cache(reader,dispatch(),dict(contract=object(),app=App()))
        self.assertFalse(result['original_app_close_metadata'])
        self.assertIn('capture_metadata_epoch',reader.cache['cases/E3/APP_CLOSE_BINDING_PHASE1_CAPTURE_V1.json'])

    def test_returned_path_uses_real_helper_parameter_shape(self):
        class App:pass
        class Core:
            calls=[]
            def _validate_returned_app_binding(self,binding,helper):self.calls.append((binding,helper))
        class Reader:pass
        reader=Reader();binding=dict(fast_shutdown=False);app=App();core=Core()
        reader.cache={'cases/E3/APP_CLOSE_BINDING_PHASE1_CAPTURE_V1.json':binding,
            'cases/E3/ENV_CLOSE_RETURNED_PHASE1_CAPTURE_V1.json':dict(closed=True),
            'cases/E3/APP_CLOSE_RETURNED_PHASE1_CAPTURE_V1.json':dict(returned=True,binding=binding)}
        reader.info={}
        result=remote.validate_terminal_cache(reader,dispatch(),dict(contract=object(),app=app,core=core))
        self.assertTrue(result['original_app_close_metadata']);self.assertIs(core.calls[0][1],app)

    def test_null_metadata_closure_stays_inconclusive(self):
        value=packet();value['closure']=None
        result=collector.summarize(dispatch(),value)
        self.assertFalse(result['passed_closed_capture_execution'])
        self.assertFalse(result['checks']['full_real_metadata_source_closure'])

    def test_atomic_output_new_root_and_no_repeat(self):
        with tempfile.TemporaryDirectory(prefix='fake_output_',dir=HERE) as name:
            root=Path(name)/'new';target=collector.atomic_closed(root,dict(fake_only=True))
            self.assertEqual(json.loads(target.read_bytes()),dict(fake_only=True))
            self.assertFalse((root/'CLOSED_RESULT.json.partial').exists())
            with self.assertRaises(ValueError):collector.atomic_closed(root,{})

    def test_fake_collect_one_connection_and_always_saves_failure(self):
        class Client:
            calls=0
            def close(self):self.calls+=1
        client=Client()
        with tempfile.TemporaryDirectory(prefix='fake_collect_',dir=HERE) as name:
            output=Path(name)/'out';calls=[]
            def connect():calls.append(1);return client
            def read(*args,**kwargs):return packet()
            target,result=collector.collect(dispatch(),output,connector=connect,packet_reader=read)
            self.assertTrue(result['passed_closed_capture_execution']);self.assertEqual(len(calls),1);self.assertEqual(client.calls,1)
            self.assertTrue(target.exists())
        with tempfile.TemporaryDirectory(prefix='fake_failure_',dir=HERE) as name:
            def broken():raise RuntimeError('FAKE transport failure')
            target,result=collector.collect(dispatch(),Path(name)/'out',connector=broken)
            self.assertTrue(target.exists());self.assertFalse(result['passed_closed_capture_execution'])
            self.assertIn('FAKE transport failure',json.dumps(result['errors']))

    def test_transport_close_exception_still_has_atomic_report(self):
        class Client:
            def close(self):raise RuntimeError('FAKE close failure')
        with tempfile.TemporaryDirectory(prefix='fake_close_',dir=HERE) as name:
            target,result=collector.collect(dispatch(),Path(name)/'out',connector=lambda:Client(),
                packet_reader=lambda *a,**kw:packet())
            self.assertTrue(target.exists());self.assertFalse(result['passed_closed_capture_execution'])
            self.assertIn('FAKE close failure',json.dumps(result['errors']))

    def test_cli_and_remote_source_no_native_lifecycle_calls(self):
        for name in ('collect_capture_result.py','remote_metadata_reader.py'):
            tree=ast.parse((HERE/name).read_text(encoding='utf-8'))
            for node in ast.walk(tree):
                if isinstance(node,(ast.Import,ast.ImportFrom)):
                    names=[n.name for n in node.names] if isinstance(node,ast.Import) else [node.module or '']
                    self.assertFalse(any(n.split('.')[0] in ('torch','paramiko','psutil','isaacsim','isaaclab') for n in names))
                if isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute):
                    self.assertNotIn(node.func.attr,('Popen','kill','killpg','terminate','send_signal','flock','nvidia'))
            compile(tree,str(HERE/name),'exec')
        text=(HERE/'remote_metadata_reader.py').read_text(encoding='utf-8')
        self.assertIn('base = app._base',text);self.assertIn('runtime.core()',text)
        self.assertNotIn('grade_closed_capture_group(',text)
        self.assertNotIn('torch.load(',text);self.assertNotIn('/proc/',text)

    def test_v1_index_is_rejected_before_any_full_closure_import(self):
        old = HERE.parent/'source_phase1_capture_worker_v1/CAPTURE_SOURCE_INDEX.json'
        raw = old.read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(),
            '234f8a3d0baf2a84338e9a0bf2170510f99d33c416654bf23b47bc3b5b5aa5ad')
        self.assertNotEqual(hashlib.sha256(raw).hexdigest(),remote.INDEX_SHA)
        with tempfile.TemporaryDirectory(prefix='fake_v1_index_',dir=HERE) as name:
            root=Path(name);(root/'CAPTURE_SOURCE_INDEX.json').write_bytes(raw)
            with patch.object(remote.importlib,'import_module',side_effect=AssertionError('closure import reached')):
                with self.assertRaisesRegex(ValueError,'current index pin differs'):
                    remote.load_metadata_closure(root)

    def test_actual_v3_source_mapping_and_fixed_final_pins(self):
        value=source_pins.read_index()
        source_pins.require_final_pins()
        self.assertEqual(remote.INDEX_SHA,source_pins.INDEX_SHA)
        self.assertEqual(len(remote.INDEX_SHA),64)
        self.assertEqual(source_pins.identity(source_pins.WORKER/'CAPTURE_SOURCE_INDEX.json'),
            dict(bytes=source_pins.INDEX_BYTES,SHA256=source_pins.INDEX_SHA))
        self.assertEqual(source_pins.identity(source_pins.WORKER/'SOURCE_SEAL.json'),
            dict(bytes=source_pins.WORKER_SEAL_BYTES,SHA256=source_pins.WORKER_SEAL_SHA))
        self.assertEqual(json.loads((source_pins.WORKER/'SOURCE_SEAL.json').read_bytes())['content_root_sha256'],
            source_pins.WORKER_ROOT)
        for alteration in ('old_version','old_v2_version','old_path_with_identical_contract_hash',
                           'old_v2_path_with_identical_contract_hash','wrong_source_hash'):
            changed=copy.deepcopy(value)
            if alteration=='old_version':changed['source_version']=1
            elif alteration=='old_v2_version':changed['source_version']=2
            elif alteration=='old_path_with_identical_contract_hash':
                changed['new_sources'][0]['path']=str(HERE.parent/'source_phase1_capture_worker_v1/phase1_capture_contract.py')
            elif alteration=='old_v2_path_with_identical_contract_hash':
                changed['new_sources'][0]['path']=str(HERE.parent/'source_phase1_capture_worker_v2/phase1_capture_contract.py')
            else:changed['new_sources'][0]['SHA256']='0'*64
            with self.subTest(alteration=alteration):
                with self.assertRaises(ValueError):source_pins.validate_worker_index(changed)

    def test_v1_logic_wire_and_all_thirty_old_tests_are_preserved(self):
        class NormalizeSourceMetadata(ast.NodeTransformer):
            def visit_Call(self,node):
                self.generic_visit(node)
                if isinstance(node.func,ast.Name) and node.func.id=='dict':
                    node.keywords=[k for k in node.keywords if k.arg not in ('source_version','source_derivation')]
                return node
            def visit_Constant(self,node):
                if node.value in ('PHASE1_E3_CAPTURE_RESULT_COLLECTION_V2_','PHASE1_E3_CAPTURE_RESULT_COLLECTION_V3_'):
                    node.value='PHASE1_E3_CAPTURE_RESULT_COLLECTION_V1_'
                return node
        oldroot=HERE.parent/'source_phase1_capture_result_collector_v1'
        for name in ('collect_capture_result.py','remote_metadata_reader.py'):
            old=ast.parse((oldroot/name).read_text(encoding='utf-8'))
            new=ast.parse((HERE/name).read_text(encoding='utf-8'))
            olddefs={n.name:n for n in old.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
            newdefs={n.name:n for n in new.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
            self.assertEqual(set(olddefs),set(newdefs))
            for key in olddefs:
                self.assertEqual(ast.dump(olddefs[key]),ast.dump(NormalizeSourceMetadata().visit(copy.deepcopy(newdefs[key]))),
                    name+':'+key+' contains a non-SOURCE logic change')
            if name=='remote_metadata_reader.py':
                oldconst={}
                def literal(node):
                    if isinstance(node,ast.Name):return oldconst[node.id]
                    if isinstance(node,ast.Tuple):return tuple(literal(x) for x in node.elts)
                    if isinstance(node,ast.Set):return {literal(x) for x in node.elts}
                    return ast.literal_eval(node)
                for node in old.body:
                    if (isinstance(node,ast.Assign) and isinstance(node.targets[0],ast.Name)
                        and node.targets[0].id in ('BASE','PREFIX','PURPOSE','PARENT_SHA','CONTROLLER_SHA',
                            'OUTER','BIG','SMALL','LOGS','MUTABLE','WORKER_KEYS')):
                        oldconst[node.targets[0].id]=literal(node.value)
                for key,expected in oldconst.items():self.assertEqual(getattr(remote,key),expected,key)
        old=ast.parse((oldroot/'test_collector_source.py').read_text(encoding='utf-8'))
        oldtests=next(n for n in old.body if isinstance(n,ast.ClassDef) and n.name=='Tests')
        oldmethods={n.name:n for n in oldtests.body if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
        new=ast.parse((HERE/'test_collector_source.py').read_text(encoding='utf-8'))
        newtests=next(n for n in new.body if isinstance(n,ast.ClassDef) and n.name=='Tests')
        newmethods={n.name:n for n in newtests.body if isinstance(n,ast.FunctionDef)}
        self.assertEqual(len(oldmethods),30)
        for key,node in oldmethods.items():self.assertEqual(ast.dump(node),ast.dump(newmethods[key]),key)
        result=collector.summarize(dispatch(),packet())
        self.assertEqual(result['kind'],'PHASE1_CAPTURE_RESULT_COLLECTION_CLOSED_V1')
        self.assertEqual(result['source_version'],3)
        self.assertTrue(result['source_derivation']['wire_V1_namespace_preserved'])
        self.assertEqual(source_pins.verify_base_collector()['base_v1_collector_members_unchanged'],9)

    def test_v2_index_is_rejected_before_any_full_closure_import(self):
        raw=(HERE.parent/'source_phase1_capture_worker_v2/CAPTURE_SOURCE_INDEX.json').read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(),
            'cdb2ca55c08a544cd01e462b7ce27261900f3b6ebaffb4784350717f756b7cf7')
        self.assertNotEqual(hashlib.sha256(raw).hexdigest(),remote.INDEX_SHA)
        with tempfile.TemporaryDirectory(prefix='fake_v2_index_',dir=HERE) as name:
            root=Path(name);(root/'CAPTURE_SOURCE_INDEX.json').write_bytes(raw)
            with patch.object(remote.importlib,'import_module',side_effect=AssertionError('closure import reached')):
                with self.assertRaisesRegex(ValueError,'current index pin differs'):
                    remote.load_metadata_closure(root)

    def test_v2_production_AST_preserved_with_report_tail_only(self):
        class NormalizeTail(ast.NodeTransformer):
            def visit_Constant(self,node):
                if node.value=='PHASE1_E3_CAPTURE_RESULT_COLLECTION_V3_':
                    node.value='PHASE1_E3_CAPTURE_RESULT_COLLECTION_V2_'
                return node
        oldroot=HERE.parent/'source_phase1_capture_result_collector_v2'
        for name in ('collect_capture_result.py','remote_metadata_reader.py'):
            before=ast.parse((oldroot/name).read_text(encoding='utf-8'))
            after=ast.parse((HERE/name).read_text(encoding='utf-8'))
            definitions=lambda tree:{n.name:n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
            olddefs=definitions(before);newdefs=definitions(after)
            self.assertEqual(set(olddefs),set(newdefs))
            for key in olddefs:
                self.assertEqual(ast.dump(olddefs[key]),ast.dump(NormalizeTail().visit(copy.deepcopy(newdefs[key]))),name+':'+key)
        base=source_pins.verify_base_collector()
        self.assertEqual(base['base_v1_collector_members_unchanged'],9)
        self.assertEqual(base['base_v2_collector_members_unchanged'],9)

    def test_pending_final_pins_stop_before_inventory_or_base_reads(self):
        with patch.object(source_pins,'INDEX_SHA',None),patch.object(source_pins,'verify_base_collector',
                side_effect=AssertionError('base read before pending pin gate')):
            for operation in (source_pins.read_index,source_pins.build_pins,source_pins.verify_sources):
                with self.subTest(operation=operation.__name__):
                    with self.assertRaisesRegex(ValueError,'FIXED_V3_PINS_PENDING'):operation()

    def test_new_B2_source_refs_are_independent_of_fixed_fifty(self):
        checked=source_pins.verify_sources()
        self.assertEqual(checked['source_count'],50)
        extra=checked['extra_source_refs']
        self.assertEqual(extra['B2_seal_members_verified'],13)
        self.assertEqual(extra['manifest_pin_references_verified'],435)
        self.assertEqual(extra['unique_manifest_Python_sources_full_SHA_AST_verified'],155)
        self.assertEqual(extra['diagnostic_source_references_verified'],4)
        self.assertTrue(extra['final_SOURCE_handoff_verified'])
        self.assertEqual(extra['extra_unique_file_identities'],174)
        self.assertIsNone(extra['B2_upstream_content_root_sha256'])
        self.assertTrue(extra['oldSource105_not_used_as_new155_proof'])
        self.assertFalse(extra['plant_source_modules_executed'])
        self.assertFalse(extra['B2_wrapper_or_reset_verifier_executed'])
        self.assertFalse(extra['reset_verifier_implemented_here'])
        self.assertFalse(extra['upstream_28_or_44_tests_rerun_here'])
        self.assertEqual(extra['gate1'],'UNKNOWN')
        self.assertFalse(extra['actual_SDK'])
        frozen=json.loads((HERE/'SOURCE_PINS.json').read_bytes())
        self.assertEqual(len(frozen['sources']),50)
        self.assertEqual(len(frozen['extra_source_refs']['sources']),174)

    def test_B2_dependency_actual_paths_aliases_and_seal_are_exact(self):
        index=source_pins.read_index()
        for mutation in ('old_path','wrong_hash','missing_alias','extra_alias','wrong_seal'):
            value=copy.deepcopy(index)
            if mutation=='old_path':
                value['dependency_sources'][0]['path']=str(HERE.parent/'source_phase1_passive_sensor_capture_v1/source_api.py')
            elif mutation=='wrong_hash':value['dependency_sources'][0]['SHA256']='0'*64
            elif mutation=='missing_alias':value['dependency_sources'].pop(0)
            elif mutation=='extra_alias':value['dependency_sources'].append(copy.deepcopy(value['dependency_sources'][0]))
            else:value['dependency_seals']['sensor']['SHA256']='0'*64
            with self.subTest(mutation=mutation):
                with self.assertRaises(ValueError):source_pins.validate_sensor_rows(value)

    def test_complete_B2_thirteen_member_source_seal_is_required(self):
        index=source_pins.read_index();sensor=index['dependency_seals']['sensor']
        seal=json.loads(Path(source_pins.B2_SEAL_PIN['path']).read_bytes())
        self.assertEqual(len(source_pins.validate_b2_members(sensor,seal)),13)
        for mutation in ('missing','hash','outside','native_flag','invented_root'):
            value=copy.deepcopy(seal);expected=copy.deepcopy(sensor)
            if mutation=='missing':value['files'].pop()
            elif mutation=='hash':value['files'][0]['sha256']='0'*64
            elif mutation=='outside':value['files'][0]['relative']='../foreign.py'
            elif mutation=='native_flag':value['native_enabled']=True
            else:expected['content_root_sha256']='0'*64
            with self.subTest(mutation=mutation):
                with self.assertRaises(ValueError):source_pins.validate_b2_members(expected,value)

    def test_manifest_reference_conflicts_incomplete_and_non_source_paths(self):
        path=str(HERE/'synthetic_reference.py')
        ref=dict(source_path=path,source_sha256='1'*64)
        refs,unique=source_pins.manifest_reference_rows(dict(a=ref,b=copy.deepcopy(ref)))
        self.assertEqual((len(refs),len(unique)),(2,1))
        for value in (dict(a=ref,b=dict(source_path=path,source_sha256='2'*64)),
                dict(source_path=path),dict(source_sha256='1'*64),
                dict(source_path=str(HERE/'fixture.pt'),source_sha256='1'*64),
                dict(source_path=str(HERE.parent.parent/'outside.py'),source_sha256='1'*64)):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):source_pins.manifest_reference_rows(value)

    def test_manifest_435_and_new155_rows_match_not_upstream_claim_only(self):
        index=source_pins.read_index();row=index['sensor_source_manifest']
        manifest=json.loads(Path(row['path']).read_bytes());closure=row['original_source_closure']
        self.assertEqual(len(source_pins.validate_manifest_closure(manifest,closure)),155)
        for mutation in ('missing_row','wrong_hash','duplicate_row','old105_count','wrong435_count'):
            changed=copy.deepcopy(closure)
            if mutation=='missing_row':changed['sources'].pop()
            elif mutation=='wrong_hash':changed['sources'][0]['SHA256']='0'*64
            elif mutation=='duplicate_row':changed['sources'][-1]=copy.deepcopy(changed['sources'][0])
            elif mutation=='old105_count':changed['unique_full_source_files']=105
            else:changed['pin_references']=434
            with self.subTest(mutation=mutation):
                with self.assertRaises(ValueError):source_pins.validate_manifest_closure(manifest,changed)

    def test_full_source_bytes_SHA_and_AST_checked_without_import(self):
        with tempfile.TemporaryDirectory(prefix='fake_source_ref_',dir=HERE) as name:
            root=Path(name).resolve();self.assertTrue(root.is_relative_to(HERE))
            path=root/'owned.py';path.write_bytes(b'VALUE = 1\n')
            row=dict(path=str(path),**source_pins.identity(path))
            self.assertEqual(source_pins.checked_blob(row,python_only=True),b'VALUE = 1\n')
            wrong=dict(row,SHA256='0'*64)
            with self.assertRaisesRegex(ValueError,'identity differs'):source_pins.checked_blob(wrong,python_only=True)
            path.write_bytes(b'def broken(:\n')
            invalid=dict(path=str(path),**source_pins.identity(path))
            with self.assertRaises(SyntaxError):source_pins.checked_blob(invalid,python_only=True)
            forbidden=dict(path=str(root/'model.pt'),bytes=1,SHA256='0'*64)
            with patch.object(Path,'read_bytes',side_effect=AssertionError('non-source read reached')):
                with self.assertRaises(ValueError):source_pins.checked_blob(forbidden,python_only=True)

    def test_diagnostic_four_plus_handoff_are_source_only_not_reset_verifier(self):
        index=source_pins.read_index()
        rows,handoff=source_pins.diagnostic_rows(index)
        self.assertEqual(len(rows),4)
        self.assertEqual(Path(handoff['path']).name,'FINAL_SOURCE_HANDOFF_RECEIPT.json')
        for mutation in ('missing_reference','missing_handoff','foreign_path','scope','native_pass'):
            changed=copy.deepcopy(index);value=changed['sensor_reset_diagnostic_source_references']
            if mutation=='missing_reference':value['source_references'].pop()
            elif mutation=='missing_handoff':value['final_handoff']={}
            elif mutation=='foreign_path':value['source_references'][0]['path']=str(HERE/'README.md')
            elif mutation=='scope':value['read_only_references_not_runtime_modules']=False
            else:value['actual_native_binding']='PASS'
            with self.subTest(mutation=mutation):
                with self.assertRaises(ValueError):source_pins.diagnostic_rows(changed)

    def test_imports_never_connect_or_load_torch(self):
        self.assertNotIn('torch',sys.modules)
        self.assertNotIn('_phase1_result_original_connector',sys.modules)
        self.assertEqual(remote.BIG,('FINAL.json','TERMINAL_ROWS.json','cases/E3/FINAL.json'))


def run(receipt=False,template=False):
    if template and receipt:raise ValueError('template never writes final receipt')
    if not template:source_pins.require_final_pins()
    names=unittest.defaultTestLoader.getTestCaseNames(Tests)
    if template:
        names=[n for n in names if n not in ('test_fixed_source_pins_and_old_partition_nine',
            'test_actual_v3_source_mapping_and_fixed_final_pins',
            'test_new_B2_source_refs_are_independent_of_fixed_fifty',
            'test_B2_dependency_actual_paths_aliases_and_seal_are_exact',
            'test_complete_B2_thirteen_member_source_seal_is_required',
            'test_manifest_435_and_new155_rows_match_not_upstream_claim_only',
            'test_diagnostic_four_plus_handoff_are_source_only_not_reset_verifier')]
    suite=unittest.TestSuite(Tests(name) for name in names)
    log=io.StringIO();result=unittest.TextTestRunner(stream=log,verbosity=2).run(suite)
    text=log.getvalue();print(text,end='')
    if template:
        print(json.dumps(dict(status='SOURCE_TEMPLATE_FAKE_AST_ONLY',tests_run=result.testsRun,
            fixed_V3_worker_pins_verified=False,extra_sourceRefs_verified=False,
            final_source_receipt_created=False,actual_collection=False,actual_SDK=False)))
    if receipt:
        pins=source_pins.verify_sources()
        for name in ('FAKE_TEST_LOG.txt','SOURCE_RECEIPT.json'):
            if (HERE/name).exists():raise ValueError('receipt already frozen: '+name)
        with (HERE/'FAKE_TEST_LOG.txt').open('x',encoding='utf-8') as stream:stream.write(text)
        value=dict(kind='PHASE1_CAPTURE_RESULT_COLLECTOR_SOURCE_RECEIPT_V3',source_version=3,
            typed_API_version=1,source_derivation=remote.SOURCE_DERIVATION,
            status='SOURCE_STDLIB_FAKE_AST_PASS' if result.wasSuccessful() else 'SOURCE_TEST_FAILED',
            tests_run=result.testsRun,failures=len(result.failures),errors=len(result.errors),source_pins=pins,
            actual_SSH=False,actual_collect=False,actual_remote_metadata_or_trace_read=False,
            actual_parent_created=False,actual_SDK=False,actual_GPU=False,actual_PT_or_raw_reads=False,
            canonical_operations=0,Git_operations=0,original_partition_nine_unchanged=True,
            base_v1_collector_nine_unchanged=True,base_v2_collector_nine_unchanged=True,
            prior_V2_development_history_preserved_in_base_receipt=True,
            pre_final_template_tests=dict(tests_run=34,failures=0,errors=0,final_pins_verified_then=False),
            final_test_suite_scope='THIS_COLLECTOR_43_SOURCE_FAKE_AST_TESTS_NOT_UPSTREAM_28_44_96',
            independently_verified_new_B2_source_refs=pins['extra_source_refs'],
            actual_B2_CPU_or_native_execution=False,reset_verifier_implemented_here=False,
            runtime_full_AppV6_Base_metadata_import='FUTURE_CALLER_ONLY_NOT_EXECUTED_HERE',
            gate1='UNKNOWN',capture_interface_passed=False,exact=False,stage2_GO=False,
            test_log_SHA256=hashlib.sha256((HERE/'FAKE_TEST_LOG.txt').read_bytes()).hexdigest(),
            test_log_hash_encoding='ACTUAL_ON_DISK_BYTES')
        with (HERE/'SOURCE_RECEIPT.json').open('x',encoding='utf-8') as stream:json.dump(value,stream,indent=2)
    return 0 if result.wasSuccessful() else 1


if __name__=='__main__':raise SystemExit(run('--receipt' in sys.argv,'--template' in sys.argv))
