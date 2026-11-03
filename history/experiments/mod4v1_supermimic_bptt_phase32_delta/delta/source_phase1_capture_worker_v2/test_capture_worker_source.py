"""stdlib fake + AST checks only; no native worker/SDK/PT/resource execution."""
from pathlib import Path
import ast
import copy
import importlib.util
import json
import sys
import types
import unittest
import tempfile
from contextlib import contextmanager
from unittest.mock import patch

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
sys.path.insert(0,str(HERE))
import phase1_capture_contract as c
import phase1_capture_runtime as r
import phase1_capture_observer as o


@contextmanager
def metadata_directory():
    """Own NEW source-only scratch; verify every absolute cleanup target first."""
    root=Path(tempfile.mkdtemp(prefix='_v2_metadata_roundtrip_',dir=HERE)).resolve()
    try:yield root
    finally:
        need=root.parent==HERE and root.name.startswith('_v2_metadata_roundtrip_')
        if not need:raise AssertionError('metadata scratch cleanup root differs')
        for child in sorted(root.glob('**/*'),key=lambda p:len(p.parts),reverse=True):
            actual=child.resolve()
            if not actual.is_relative_to(root) or actual==root:raise AssertionError('metadata scratch cleanup escapes root')
            if child.is_dir():child.rmdir()
            else:child.unlink()
        root.rmdir()


def task(controls=64):
    return dict(kind=c.KIND,purpose=c.PURPOSE,batch_purpose=c.PURPOSE,integration=c.INTEGRATION,
                policy_variant=c.POLICY_VARIANT,role='E3',requested_roles=['E3'],role_catalog=list(c.ROLES),num_envs=80,
                seed=20260928,controls=controls,model_PT_reads=0,synthetic_action=[0.,0.,0.,0.,0.,0.],
                train=False,quality_evaluation=False,full_clean35='UNKNOWN',physics=copy.deepcopy(c.PHYSICS),
                asset_SHA=c.USD,contract_SHA=c.CONTRACT,overall_eight_pass_rate=None,comparison=None,
                group_id='SOURCE_FAKE_ONLY_NOT_ADMISSION',GPU_UUID='GPU-SOURCE-FAKE',absolute_worker_deadline_epoch=1.,
                finite_validation_cost_protocol=copy.deepcopy(r.ORIGINAL_COST_PROTOCOL))


def final_value(controls=64, **changes):
    params=dict(completed=controls,physics=8*controls,feedback=2*controls,
                delay_calls=dict(legs=8*controls,wheels=8*controls),
                boundary=dict(actions=controls,original_step_transitions=controls,pending_original_step=False),
                sensor={},actuation={},coverage=dict(deficits=[],natural_terminal_env_events=0,natural_partial_reset_candidate_controls=0),
                rng_counts={},trace={},restore=dict(ok=True,order=['actuation','sensor','bridge']),setup={})
    params.update(changes)
    return c.candidate_final(task(controls),**params)


def plan_value():
    index=r.source_index();rows=[]
    for role in c.ROLES:
        rows.append(dict(role=role,worker='worker_passive_interface_v1.py' if role=='E3' else 'deferred_original.py',
                         controls=160 if role=='E3' else 1600,runtime_root='/SOURCE_FAKE/runtimes/'+role,asset_dir='/SOURCE_FAKE/assets'))
    files=[dict(relative=x['install_relative'],bytes=x['bytes'],SHA=x['SHA256'])
           for x in index['original17']+index['new_sources']+index['dependency_sources']]
    baseline=[dict(relative='runtimes/'+role+'/runtime/assets/SOURCE_BANK.fake',bytes=1,SHA256='0'*64) for role in c.ROLES]
    baseline += [dict(relative=x,bytes=1,SHA256='0'*64) for x in ['pinned_assets/SOURCE.fake','worker_sources/original.py']]
    baseline += [dict(relative='supermimic_vendor_v2/'+str(i)+'.py',bytes=1,SHA256='0'*64) for i in range(7)]
    return dict(kind=c.PLAN_KIND,batch_purpose=c.PURPOSE,requested_roles=['E3'],deferred_roles=list(c.ROLES[1:]),
                roles=rows,worker_files=files,group_id='SOURCE_FAKE_ONLY_NOT_ADMISSION',GPU_UUID='GPU-SOURCE-FAKE',
                paired_reset_protocol={'SOURCE_FAKE_ONLY':True},capture_controls=64,
                retained_static_inventory=dict(kind='COMPLETE_ORIGINAL_STATIC_TREE_REFERENCE_V1',baseline=baseline,
                    installed=copy.deepcopy(baseline),SHA256=c.canonical_digest(baseline),
                    vendor7_SHA256='ddf9d6e1744c050fd5298805d125a611673ff22ade52c5177fb02c488ff8f0c0'))


class ContractTests(unittest.TestCase):
    def test_default_e3_64(self):
        value=task();self.assertIs(c.validate_task(value),value);self.assertEqual(value['controls'],64)
    def test_optional_128(self):self.assertEqual(c.validate_task(task(128))['controls'],128)
    def test_bool_not_control(self):
        with self.assertRaises(ValueError):c.validate_task(task(True))
    def test_no_old_quality_denominator(self):
        with self.assertRaises(ValueError):c.validate_task(task(160))
    def test_no_old_kind(self):
        t=task();t['kind']='FROZEN_ZERO_UPDATE_BOUND_ONLY_N80_TASK_V1'
        with self.assertRaises(ValueError):c.validate_task(t)
    def test_no_second_member(self):
        t=task();t['requested_roles']=['E3','W35']
        with self.assertRaises(ValueError):c.validate_task(t)
    def test_no_pt_fallback(self):
        t=task();t['source_path']='SOURCE_FAKE.pt'
        with self.assertRaises(ValueError):c.validate_task(t)
    def test_no_physics_change(self):
        t=task();t['physics']['decimation']=4
        with self.assertRaises(ValueError):c.validate_task(t)
    def test_no_cost_approval_gate(self):
        t=task();t.pop('finite_validation_cost_protocol');self.assertEqual(c.validate_task(t)['controls'],64)
    def test_whole_plan_members(self):self.assertEqual([x['role'] for x in c.validate_plan(plan_value(),r.source_index())],['E3'])
    def test_no_static_subset(self):
        p=plan_value();p['retained_static_inventory']['installed'].pop()
        with self.assertRaises(ValueError):c.validate_plan(p,r.source_index())
    def test_no_static_missing_runtime(self):
        p=plan_value();v=p['retained_static_inventory'];v['baseline']=[x for x in v['baseline'] if not x['relative'].startswith('runtimes/E2/')];v['installed']=copy.deepcopy(v['baseline']);v['SHA256']=c.canonical_digest(v['baseline'])
        with self.assertRaises(ValueError):c.validate_plan(p,r.source_index())
    def test_full17_not_selected_ast(self):
        p=plan_value();p['worker_files'].pop(0)
        with self.assertRaises(ValueError):c.validate_plan(p,r.source_index())
    def test_new_make_task_no_teacher(self):
        p=plan_value();t=r.make_task(p['roles'][0],p,123.,[50,51]);self.assertEqual(t['controls'],64);self.assertNotIn('source_path',t)
    def test_execution_not_coverage(self):
        f=final_value();self.assertTrue(f['passed_execution']);self.assertFalse(f['capture_interface_passed']);self.assertEqual(f['gate1'],'UNKNOWN')
        self.assertIn('NO_NATURAL_PARTIAL_RESET_CANDIDATE',f['inconclusive_reasons']);self.assertTrue(c.validate_preclose(f,task()))
    def test_initial_snapshot_survives_final_contract(self):
        value=final_value(trace=dict(initial_sensor_memory=dict(clean0='UNKNOWN',cache={'gyro':{'fifo':[1]}})))
        self.assertEqual(value['bounded_trace']['initial_sensor_memory']['cache']['gyro']['fifo'],[1])
    def test_short_or_wrong_physics_is_not_execution(self):self.assertFalse(final_value(physics=511)['passed_execution'])
    def test_boundary_pending_is_not_execution(self):self.assertFalse(final_value(boundary=dict(actions=64,original_step_transitions=63,pending_original_step=True))['passed_execution'])
    def test_restore_error_is_not_execution(self):self.assertFalse(final_value(restore=dict(ok=False,order=['actuation','sensor','bridge']))['passed_execution'])
    def test_no_gate1_promotion(self):
        f=final_value();f['capture_interface_passed']=True
        with self.assertRaises(ValueError):c.validate_preclose(f,task())
    def test_no_old_quality_final(self):
        f=final_value();f['kind']='OLD_QUALITY_FINAL'
        with self.assertRaises(ValueError):c.validate_preclose(f,task())


class ResourceValidationTests(unittest.TestCase):
    def values(self):
        t=task();t.update(inherited_lock_fds=[50,51],absolute_worker_deadline_epoch=200.)
        admission=dict(group_id=t['group_id'],resource=dict(GPU_UUID=t['GPU_UUID']),original_private_GPU_EX_held=True,
                       original_global_finite_EX_held=True,canonical_writes=0)
        return t,admission
    def test_original_gpu_deadline_and_fstat_positive(self):
        t,a=self.values();seen=[]
        self.assertIs(r.validate_inherited_admission(t,a,environment={'CUDA_VISIBLE_DEVICES':t['GPU_UUID']},fd_check=seen.append,now=lambda:100.),a)
        self.assertEqual(seen,[50,51])
    def test_original_cuda_mismatch_rejected_before_sdk(self):
        t,a=self.values();seen=[]
        with self.assertRaises(ValueError):r.validate_inherited_admission(t,a,environment={'CUDA_VISIBLE_DEVICES':'GPU-OTHER'},fd_check=seen.append,now=lambda:100.)
        self.assertEqual(seen,[])
    def test_original_admission_gpu_mismatch(self):
        t,a=self.values();a['resource']['GPU_UUID']='GPU-OTHER'
        with self.assertRaises(ValueError):r.validate_inherited_admission(t,a,environment={'CUDA_VISIBLE_DEVICES':t['GPU_UUID']},fd_check=lambda fd:None,now=lambda:100.)
    def test_original_deadline_elapsed_rejected_before_sdk(self):
        t,a=self.values()
        for now in (200.,201.):
            with self.assertRaises(ValueError):r.validate_inherited_admission(t,a,environment={'CUDA_VISIBLE_DEVICES':t['GPU_UUID']},fd_check=lambda fd:None,now=lambda:now)
    def test_original_unique_nonnegative_fds(self):
        for values in ([50,50],[-1,50],[True,50],[50]):
            t,a=self.values();t['inherited_lock_fds']=values
            with self.assertRaises(ValueError):r.validate_inherited_admission(t,a,environment={'CUDA_VISIBLE_DEVICES':t['GPU_UUID']},fd_check=lambda fd:None,now=lambda:100.)
    def test_actual_installed_runtime_parent_equals_group(self):
        group=Path('/home/lc01/Zonglin Li/zonglin2/tasks/NEW_SOURCE_FAKE_ROOT_NOT_CREATED').resolve()
        self.assertEqual(r.validate_installed_root(group,group),group)
    def test_local_source_root_is_not_remote_admission(self):
        with self.assertRaises(ValueError):r.validate_installed_root(HERE,HERE)
    def test_foreign_remote_root(self):
        group=Path('/home/lc01/Zonglin Li/zonglin2/FOREIGN_SOURCE_FAKE_ROOT_NOT_CREATED').resolve()
        with self.assertRaises(ValueError):r.validate_installed_root(group,group)
    def test_other_installed_root(self):
        group=Path('/home/lc01/Zonglin Li/zonglin2/tasks/NEW_SOURCE_FAKE_ROOT_NOT_CREATED').resolve()
        with self.assertRaises(ValueError):r.validate_installed_root(group,group.parent/'OTHER_SOURCE_FAKE_NOT_CREATED')
    def test_remote_tasks_root_itself_is_not_group(self):
        group=Path('/home/lc01/Zonglin Li/zonglin2/tasks').resolve()
        with self.assertRaises(ValueError):r.validate_installed_root(group,group)
    def test_pre_sdk_validation_order(self):
        tree=ast.parse((HERE/'phase1_capture_runtime.py').read_text(encoding='utf-8'))
        fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='task_args')
        calls=[n for n in ast.walk(fn) if isinstance(n,ast.Call)]
        at=lambda name:next(n.lineno for n in calls if ast.unparse(n.func)==name)
        self.assertLess(at('validate_installed_root'),at('validate_group_task'));self.assertLess(at('validate_group_task'),at('core().configure_candidate_runtime'))


class RecorderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        folder=ROOT/'source_phase1_passive_sensor_capture_v1'
        for name in ('source_api','passive_capture'):
            spec=importlib.util.spec_from_file_location(name,folder/(name+'.py'));module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
        cls.base=sys.modules['passive_capture'].BoundedRecorder
    def recorder(self):return o.make_recorder(self.base,lambda v:['SOURCE_WITNESS'])
    def test_all_mid_end_channels(self):
        rec=self.recorder()
        for tick,slot in ((4,'mid'),(8,'end')):
            for key in o.CHANNELS:
                rec.commit(rec.begin('feedback'),dict(key=key,clock=dict(is_original_100hz_slot=True,physics_tick=tick,feedback_tick=tick//4,control_slot=slot)))
        self.assertFalse(rec.coverage(1)['deficits']);self.assertEqual(len(rec.global_slot_identities),10)
    def test_global_slot_counts_are_not_episode_fresh_proof(self):
        value=self.recorder().coverage(0)
        self.assertEqual(value['per_row_episode_fresh_samples'],'UNKNOWN_NEEDS_LIVE_VERIFIER')
        self.assertEqual(value['counter_scope'],'GLOBAL_ORIGINAL100HZ_CALL_SLOTS_NOT_PER_ROW_EPISODE_FRESHNESS')
        self.assertNotIn('duplicate_fresh_calls',value)
    def test_duplicate_global_slot_is_not_new_global_slot(self):
        rec=self.recorder();payload=dict(key=o.CHANNELS[0],clock=dict(is_original_100hz_slot=True,physics_tick=4,feedback_tick=1,control_slot='mid'))
        for _ in range(2):rec.commit(rec.begin('feedback'),payload)
        self.assertEqual(len(rec.global_slot_identities),1);self.assertEqual(rec.duplicate_slot_calls,1)
    def test_reset_or_outside_calls_not_global100hz_slots(self):
        rec=self.recorder();rec.commit(rec.begin('feedback'),dict(key=o.CHANNELS[0],clock=dict(is_original_100hz_slot=False)))
        self.assertEqual(len(rec.global_slot_identities),0)
    def test_original_actor_identity(self):
        rec=self.recorder();value=types.SimpleNamespace(shape=(80,35));self.assertIs(rec.actor(value,value,0),value)
        self.assertEqual(rec.report()['count_by_kind']['actor35_original_buffer'],1)
    def test_actor_copy_not_source(self):
        rec=self.recorder()
        with self.assertRaises(ValueError):rec.actor(types.SimpleNamespace(shape=(80,35)),types.SimpleNamespace(shape=(80,35)),0)
    def test_terminal_special_ring(self):
        rec=self.recorder()
        for i in range(9):rec.commit(rec.begin('terminal_pre_reset'),{'index':i})
        self.assertEqual([x['payload']['index'] for x in rec.special['terminal_pre_reset']],[5,6,7,8])
    def test_window_retention_bounds(self):
        ret=o.WindowRetention()
        for i in range(128):ret.add(i,[dict(index=i)])
        report=ret.report();self.assertEqual(len(report['first'])+len(report['last']),4);self.assertEqual(report['last'][-1]['control_index'],127)
    def test_reverse_restore_all_attempted_on_conflict(self):
        calls=[]
        class Fake:
            def __init__(self,name,broken=False):self.name,self.broken=name,broken
            def close(self):
                calls.append(self.name)
                if self.broken:raise RuntimeError('SOURCE_FAKE_CONFLICT')
                return dict(restored=True)
        value=o.restore_interfaces(Fake('actuation',True),Fake('sensor'),Fake('bridge'))
        self.assertEqual(calls,['actuation','sensor','bridge']);self.assertFalse(value['ok'])
    def test_initial_same_tick_cache_is_not_fresh_clean0(self):
        sensor=types.SimpleNamespace(cache={'gyro':{'out':[4.],'sample_tick':[0]}},episode=[0],draw_counts={'gyro':1})
        delay=types.SimpleNamespace(cache={'gyro':{'fifo':[[3.]],'cur':[0],'out':[3.],'last':[0],'sample_tick':[0]}},episode=[0])
        env=types.SimpleNamespace(_sensor_mild=sensor,_feedback_delay_mild=delay,_sim_step_counter=0,_feedback_100hz_tick=0)
        before=copy.deepcopy(vars(env._feedback_delay_mild));value=o.initial_sensor_memory(env,copy.deepcopy)
        self.assertEqual(value['clean0'],'UNKNOWN');self.assertIn('SAME_TICK',value['initial_sensor_freshness'])
        self.assertEqual(vars(delay),before);delay.cache['gyro']['out'][0]=999
        self.assertEqual(value['components']['_feedback_delay_mild']['cache']['gyro']['out'],[3.])
        self.assertEqual(env._feedback_100hz_tick,0);self.assertEqual(sensor.draw_counts['gyro'],1)
    def test_initial_missing_component_remains_unknown(self):
        value=o.initial_sensor_memory(types.SimpleNamespace(),copy.deepcopy)
        self.assertEqual(value['components']['_sensor_mild']['cache'],'UNKNOWN');self.assertEqual(value['clean0'],'UNKNOWN')
    def test_stored_rng_counts_only(self):
        env=types.SimpleNamespace(_sensor_mild=types.SimpleNamespace(draw_counts={'gyro':10}))
        result=o.stored_rng_counts(env);env._sensor_mild.draw_counts['gyro']=20
        self.assertEqual(result['sensor_draw_counts']['gyro'],10);self.assertEqual(result['observer_rng_draws'],0)


class FakeCloseTests(unittest.TestCase):
    def setup_fake(self,*,fast=False,env_error=False,valid_final=True):
        case=HERE/'_IN_MEMORY_SOURCE_FAKE_CASE';files={};calls=[]
        def put(path,value,**options):files[str(path)]=copy.deepcopy(value)
        def meta(path,*args):
            value=files[str(path)];return copy.deepcopy(value),json.dumps(value,sort_keys=True).encode()
        binding=dict(fast_shutdown=fast,SOURCE_FAKE_NOT_SDK=True)
        helper=types.SimpleNamespace(_pin_original_app_close=lambda app:copy.deepcopy(binding),_validate_binding_receipt=lambda value:None)
        class Env:
            def close(self):
                calls.append('env')
                if env_error:raise RuntimeError('SOURCE_FAKE_ENV_CLOSE_ERROR')
        class App:
            def close(self):calls.append('app')
        t=task();files[str(case/'task.json')]=t
        f=final_value()
        if not valid_final:f['kind']='OLD_QUALITY_FINAL'
        files[str(case/'FINAL.json')]=f
        ctx=[patch.object(r,'put_json',side_effect=put),patch.object(r,'_metadata',side_effect=meta),
             patch.object(r,'_pinned_module',return_value=helper),
             patch.object(Path,'exists',lambda p:str(p) in files),
             patch.object(r,'core',return_value=types.SimpleNamespace(_validate_returned_app_binding=lambda value,helper:None))]
        for x in ctx:x.start();self.addCleanup(x.stop)
        return case,t,files,calls,Env(),App()
    def test_original_env_and_app_exactly_once(self):
        case,t,files,calls,env,app=self.setup_fake();self.assertFalse(r.close_original_eval_resources(env,app,case,t));self.assertEqual(calls,['env','app'])
        self.assertIn(str(case/'APP_CLOSE_CALLED_PHASE1_CAPTURE_V1.json'),files)
    def test_env_failure_still_closes_app(self):
        case,t,files,calls,env,app=self.setup_fake(env_error=True);errors=r.close_original_eval_resources(env,app,case,t)
        self.assertTrue(errors);self.assertEqual(calls,['env','app']);self.assertNotIn(str(case/'APP_FAST_CLOSE_INTENT_PHASE1_CAPTURE_V1.json'),files)
    def test_bad_final_still_closes_app_without_good_intent(self):
        case,t,files,calls,env,app=self.setup_fake(fast=True,valid_final=False);self.assertTrue(r.close_original_eval_resources(env,app,case,t));self.assertEqual(calls,['env','app'])
        self.assertNotIn(str(case/'APP_FAST_CLOSE_INTENT_PHASE1_CAPTURE_V1.json'),files)
    def test_fast_intent_is_not_wait_receipt(self):
        case,t,files,calls,env,app=self.setup_fake(fast=True);r.close_original_eval_resources(env,app,case,t)
        intent=files[str(case/'APP_FAST_CLOSE_INTENT_PHASE1_CAPTURE_V1.json')];self.assertIsNone(intent['actual_parent_wait']);self.assertEqual(calls,['env','app'])
    def test_rc_zero_without_final_fails(self):
        case,t,files,calls,env,app=self.setup_fake();files.pop(str(case/'FINAL.json'))
        self.assertFalse(r.evaluate_waited_eval_case(case,0,{'role':'E3','capture_controls':64},t['group_id'])['passed_execution'])
    def test_waited_execution_stays_inconclusive(self):
        case,t,files,calls,env,app=self.setup_fake(fast=True);r.close_original_eval_resources(env,app,case,t)
        value=r.evaluate_waited_eval_case(case,0,{'role':'E3','capture_controls':64},t['group_id'])
        self.assertTrue(value['passed_execution']);self.assertFalse(value['capture_interface_passed']);self.assertEqual(value['gate1'],'UNKNOWN')
    def test_missing_ex_release_fails_closed_grade(self):
        case,t,files,calls,env,app=self.setup_fake();group=case.parent
        files[str(group/'FINAL.json')]=dict(kind='PHASE1_PASSIVE_CAPTURE_GROUP_FINAL_V1',purpose=c.PURPOSE,passed_execution=True)
        files[str(group/'PARENT_EXIT_SCOPE.json')]=dict(all_own_children_waited=True,original_single_GPU_private_EX_released=False,original_global_finite_EX_released=True)
        self.assertFalse(r.grade_closed_capture_group(group)['passed_closed_capture_execution'])


class ASTSourceTests(unittest.TestCase):
    def worker(self):return ast.parse((HERE/'worker_passive_interface_v1.py').read_text(encoding='utf-8'))
    def test_complete_original_parent_blocks_unchanged(self):
        old=(ROOT/'source_bound_only_native_integration_v1/single_gpu_e3_w35_bound_only_parent_v1.py').read_text(encoding='utf-8').splitlines()
        new=(HERE/'single_gpu_passive_capture_parent_v1.py').read_text(encoding='utf-8').splitlines()
        for first,last in ((17,44),(46,78)):self.assertEqual(old[first-1:last],new[first-1:last])
    def test_parent_explicit_e3_only(self):
        text=(HERE/'single_gpu_passive_capture_parent_v1.py').read_text(encoding='utf-8');self.assertIn("requested==('E3',) and len(children)==len(requested)==1",text)
        self.assertNotIn('grade_closed_bound_probe_group',text)
    def test_one_original_reset_and_existing_compute(self):
        calls=[n for n in ast.walk(self.worker()) if isinstance(n,ast.Call)]
        resets=[n for n in calls if isinstance(n.func,ast.Attribute) and ast.unparse(n.func)=='env.reset']
        computes=[n for n in calls if isinstance(n.func,ast.Attribute) and ast.unparse(n.func)=='env.observation_manager.compute']
        self.assertEqual(len(resets),1);self.assertEqual(len(computes),1)
        placement=next(n for n in calls if isinstance(n.func,ast.Attribute) and ast.unparse(n.func)=='env.place_declared_fall')
        bridge=next(n for n in calls if isinstance(n.func,ast.Attribute) and n.func.attr=='NativeTaskBridge')
        self.assertLess(resets[0].lineno,placement.lineno);self.assertLess(placement.lineno,computes[0].lineno);self.assertLess(computes[0].lineno,bridge.lineno)
        self.assertEqual({k.arg:ast.unparse(k.value) for k in bridge.keywords},dict(teacher='None',initial_obs='obs'))
    def test_worker_initial_sensor_memory_is_in_result_trace(self):
        calls=[n for n in ast.walk(self.worker()) if isinstance(n,ast.Call)]
        traces=[n.value for call in calls for n in call.keywords if n.arg=='trace']
        self.assertEqual(len(traces),1)
        fields={n.arg:ast.unparse(n.value) for n in traces[0].keywords}
        self.assertEqual(fields['initial_sensor_memory'],'initial_sensor')
    def test_one_bridge_init_then_sensor_then_actuation(self):
        lines={}
        for node in ast.walk(self.worker()):
            if isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute) and node.func.attr in ('init_state','install_passive_capture','install_actuation_tap'):
                self.assertNotIn(node.func.attr,lines);lines[node.func.attr]=node.lineno
        self.assertLess(lines['init_state'],lines['install_passive_capture']);self.assertLess(lines['install_passive_capture'],lines['install_actuation_tap'])
    def test_no_native_import_at_worker_module_scope(self):
        for node in self.worker().body:
            if isinstance(node,(ast.Import,ast.ImportFrom)):
                names=[a.name for a in node.names]+([node.module] if isinstance(node,ast.ImportFrom) else [])
                self.assertFalse(any(x and x.split('.')[0] in ('torch','isaacsim','isaaclab','psutil') for x in names))
    def test_no_training_or_rng_or_compute_in_observer(self):
        tree=ast.parse((HERE/'phase1_capture_observer.py').read_text(encoding='utf-8'))
        names=[ast.unparse(n.func) for n in ast.walk(tree) if isinstance(n,ast.Call)]
        self.assertFalse(any(any(x in n for x in ('clean_policy','compute_obs','observation_manager','randn','manual_seed','env.step','env.reset')) for n in names))
        worker_names=[ast.unparse(n.func) for n in ast.walk(self.worker()) if isinstance(n,ast.Call)]
        self.assertFalse(any(any(x in n for x in ('A1CheckpointAdapter','torch.load','state_dict','export_supermimic','Learner','optimizer','Replay','clean_policy')) for n in worker_names))
    def test_full_app_base_bridge_and_formal_sources_fixed(self):
        index=r.source_index();aliases={x['install_relative']:x for x in index['original17']}
        for name,prefix in [('a1_frozen_eval_runtime_v2.py','7a092'),('frozen_a1_raw35_v1.py','1ea4'),('app_close_semantics_v5.py','3d2d'),('resume_runtime_contracts_v3.py','dc4'),('native_supermimic_bridge.py','8211')]:
            self.assertTrue(aliases[name]['SHA256'].startswith(prefix));self.assertGreater(aliases[name]['bytes'],10000)
    def test_sealed_dependency_hashes(self):
        index=r.source_index()
        for value in index['dependency_seals'].values():
            path=Path(value['path']);self.assertEqual(c.sha(path.read_bytes()),value['SHA256'])
            for row in value['members']:
                raw=(path.parent/row['relative']).read_bytes();self.assertEqual((len(raw),c.sha(raw)),(row['bytes'],row['SHA256']))
    def test_all_source_rows_actual_bytes(self):
        index=r.source_index()
        for row in index['original17']+index['new_sources']+index['dependency_sources']:
            raw=Path(row['path']).read_bytes();self.assertEqual((len(raw),c.sha(raw)),(row['bytes'],row['SHA256']))
    def test_evalclose_not_training_predicate(self):
        tree=ast.parse((HERE/'phase1_capture_runtime.py').read_text(encoding='utf-8'))
        close=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='close_original_eval_resources')
        names=[ast.unparse(n.func) for n in ast.walk(close) if isinstance(n,ast.Call)]
        self.assertEqual(names.count('env.close'),1);self.assertEqual(names.count('app.close'),1)
        self.assertIn('validate_preclose',names);self.assertNotIn('_validate_final_for_intent',names)
    def test_no_new_lock_writer_scheduler_or_approval_flag(self):
        text='\n'.join((HERE/name).read_text(encoding='utf-8') for name in ('phase1_capture_runtime.py','phase1_capture_contract.py','worker_passive_interface_v1.py'))
        self.assertNotIn('CONFIRMED_BY_PARENT',text);self.assertNotIn('fcntl.flock',text)
        self.assertNotIn('subprocess.Popen',text);self.assertNotIn('TRAINING_BUDGET_10H.json',text)


class FullOriginalStdlibCloseTests(unittest.TestCase):
    """Full unchanged core/AppV6/Base imports; SDK binding is metadata fixture only."""
    @classmethod
    def setUpClass(cls):
        aliases={x['install_relative']:x for x in r.source_index()['original17']}
        cls.loaded={};cls.previous={}
        for alias,name in [('resume_runtime_contracts_v3.py','resume_runtime_contracts_v3'),
                           ('app_close_semantics_v5.py','app_close_semantics_v5'),
                           ('a1_frozen_eval_runtime_v2.py','_phase1_v2_full_original_core_test')]:
            row=aliases[alias];path=Path(row['path']);raw=path.read_bytes()
            if (len(raw),c.sha(raw))!=(row['bytes'],row['SHA256']):raise AssertionError('full original stdlib source differs')
            cls.previous[name]=sys.modules.get(name)
            spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec)
            sys.modules[name]=module;spec.loader.exec_module(module);cls.loaded[alias]=module
        cls.actual_core=cls.loaded['a1_frozen_eval_runtime_v2.py'];cls.helper=cls.loaded['app_close_semantics_v5.py']
        def restore():
            for name,previous in cls.previous.items():
                if previous is None:sys.modules.pop(name,None)
                else:sys.modules[name]=previous
        cls.addClassCleanup(restore)

    def binding(self,fast=False,module='isaacsim.simulation_app.simulation_app'):
        name=module+'.SimulationApp';source=str((HERE/'_IN_MEMORY_NOT_SDK_SimulationApp.py').resolve())
        value=dict(kind='PINNED_SIMULATIONAPP_CLOSE_BINDING_V5',actual_class=name,
            actual_MRO=[name,'builtins.object'],close_owner=name,actual_module=module,actual_type_name='SimulationApp',
            close_module=module,close_qualname='SimulationApp.close',source_file=source,module_file=source,code_filename=source,
            source_SHA256='6af5372bb0cdda6e665a30cd285ff724b3e5bd012dbdd4df458e0726173fc903',source_bytes=48933,
            close_firstlineno=848,exact_class_verified=True,method_self_is_application=True,method_function_is_MRO_definition=True,
            fast_shutdown=fast,no_extra_SDK_getters=True,SOURCE_FIXTURE_NOT_NATIVE_BINDING=True)
        value.update(self.helper._helper_source_receipt());return value

    def setup_case(self,fast=False):
        case=HERE/'_IN_MEMORY_FULL_METADATA_CASE';files={};calls=[];binding=self.binding(fast)
        def put(path,value,**options):files[str(path)]=copy.deepcopy(value)
        def meta(path,*args):
            value=files[str(path)];return copy.deepcopy(value),json.dumps(value,sort_keys=True).encode()
        class Env:
            def close(self):calls.append('env')
        class App:
            def close(self):calls.append('app')
        t=task();files[str(case/'task.json')]=t;files[str(case/'FINAL.json')]=final_value()
        ctx=[patch.object(r,'put_json',side_effect=put),patch.object(r,'_metadata',side_effect=meta),
             patch.object(r,'_pinned_module',return_value=self.helper),patch.object(r,'core',return_value=self.actual_core),
             patch.object(self.helper,'_pin_original_app_close',return_value=copy.deepcopy(binding)),
             patch.object(Path,'exists',lambda p:str(p) in files)]
        for value in ctx:value.start();self.addCleanup(value.stop)
        self.assertFalse(r.close_original_eval_resources(Env(),App(),case,t));self.assertEqual(calls,['env','app'])
        return case,t,files,binding

    def evaluate(self,case,t):return r.evaluate_waited_eval_case(case,0,{'role':'E3','capture_controls':64},t['group_id'])
    def test_full_stdlib_modules_have_actual_source(self):
        aliases={x['install_relative']:x for x in r.source_index()['original17']}
        for alias,module in self.loaded.items():
            row=aliases[alias];self.assertEqual(Path(module.__file__).resolve(),Path(row['path']).resolve())
            raw=Path(module.__file__).read_bytes();self.assertEqual((len(raw),c.sha(raw)),(row['bytes'],row['SHA256']))
        self.assertIs(self.helper._base,self.loaded['resume_runtime_contracts_v3.py'])
    def test_actual_core_requires_helper_parameter(self):
        import inspect
        self.assertEqual(list(inspect.signature(self.actual_core._validate_returned_app_binding).parameters),['binding','helper'])
        with self.assertRaises(TypeError):self.actual_core._validate_returned_app_binding(self.binding())
    def test_runtime_passes_actual_loaded_helper(self):
        tree=ast.parse((HERE/'phase1_capture_runtime.py').read_text(encoding='utf-8'))
        calls=[n for n in ast.walk(tree) if isinstance(n,ast.Call) and ast.unparse(n.func)=='core()._validate_returned_app_binding']
        self.assertEqual(len(calls),1);self.assertEqual([ast.unparse(x) for x in calls[0].args],['binding','helper'])
    def test_nonfast_full_actual_validator(self):self.assertTrue(self.actual_core._validate_returned_app_binding(self.binding(),self.helper))
    def test_both_published_export_aliases_unchanged(self):
        for module in ('isaacsim.simulation_app.simulation_app','simulation_app.simulation_app'):
            self.assertTrue(self.actual_core._validate_returned_app_binding(self.binding(module=module),self.helper))
            self.helper._validate_binding_receipt(self.binding(True,module))
    def test_nonfast_wrong_helper_path_fails(self):
        value=self.binding();value['helper_source_file']=str(HERE/'_NOT_THE_HELPER.py')
        with self.assertRaises(ValueError):self.actual_core._validate_returned_app_binding(value,self.helper)
    def test_nonfast_missing_exact_evidence_fails(self):
        for key in ('actual_MRO','source_SHA256','source_bytes','close_firstlineno','helper_source_SHA256','helper_source_file'):
            with self.subTest(key=key):
                value=self.binding();value.pop(key)
                with self.assertRaises(ValueError):self.actual_core._validate_returned_app_binding(value,self.helper)
    def test_fast_complete_actual_helper_validator(self):self.helper._validate_binding_receipt(self.binding(True))
    def test_fast_mode_not_changed_or_relaxed(self):
        for mode in (False,1,'true',None):
            with self.assertRaises(ValueError):self.helper._validate_binding_receipt(self.binding(mode))
    def test_waited_nonfast_full_metadata_passes(self):
        case,t,files,binding=self.setup_case(False);value=self.evaluate(case,t)
        self.assertTrue(value['passed_execution'],value['errors']);self.assertFalse(value['capture_interface_passed']);self.assertEqual(value['gate1'],'UNKNOWN')
        self.assertNotIn(str(case/'APP_FAST_CLOSE_INTENT_PHASE1_CAPTURE_V1.json'),files)
    def test_waited_fast_full_metadata_passes(self):
        case,t,files,binding=self.setup_case(True);value=self.evaluate(case,t)
        self.assertTrue(value['passed_execution'],value['errors']);self.assertIsNone(files[str(case/'APP_FAST_CLOSE_INTENT_PHASE1_CAPTURE_V1.json')]['actual_parent_wait'])
        self.assertFalse(value['exact']);self.assertFalse(value['capture_interface_passed'])
    def test_nonfast_missing_returned_still_fails(self):
        case,t,files,binding=self.setup_case(False);files.pop(str(case/'APP_CLOSE_RETURNED_PHASE1_CAPTURE_V1.json'))
        self.assertFalse(self.evaluate(case,t)['passed_execution'])
    def test_fast_bad_final_digest_still_fails(self):
        case,t,files,binding=self.setup_case(True);files[str(case/'APP_FAST_CLOSE_INTENT_PHASE1_CAPTURE_V1.json')]['final_SHA']='0'*64
        self.assertFalse(self.evaluate(case,t)['passed_execution'])
    def test_nonfast_wrong_source_digest_still_fails(self):
        case,t,files,binding=self.setup_case(False);files[str(case/'APP_CLOSE_BINDING_PHASE1_CAPTURE_V1.json')]['source_SHA256']='0'*64
        self.assertFalse(self.evaluate(case,t)['passed_execution'])


    def real_filesystem_roundtrip(self,fast,*,tamper=False):
        with metadata_directory() as case:
            files=[];binding=self.binding(fast);t=task()
            class Env:
                def close(self):files.append('env')
            class App:
                def close(self):files.append('app')
            # These are actual put_json/fsync/replace/_metadata calls, not a fake FS.
            r.put_json(case/'task.json',t);r.put_json(case/'FINAL.json',final_value())
            with patch.object(r,'_pinned_module',return_value=self.helper),patch.object(r,'core',return_value=self.actual_core),patch.object(self.helper,'_pin_original_app_close',return_value=copy.deepcopy(binding)):
                self.assertEqual(r.close_original_eval_resources(Env(),App(),case,t),[])
                self.assertEqual(files,['env','app'])
                saved,raw=r._metadata(case/'APP_CLOSE_BINDING_PHASE1_CAPTURE_V1.json')
                self.assertEqual(saved,binding);self.assertNotIn('capture_metadata_epoch',saved)
                self.assertEqual(raw,json.dumps(binding,indent=2,allow_nan=False).encode())
                returned,_=r._metadata(case/'APP_CLOSE_RETURNED_PHASE1_CAPTURE_V1.json')
                self.assertEqual(returned['binding'],saved);self.assertIn('capture_metadata_epoch',returned)
                if fast:
                    intent,_=r._metadata(case/'APP_FAST_CLOSE_INTENT_PHASE1_CAPTURE_V1.json')
                    self.assertEqual(intent['binding'],saved);self.assertIsNone(intent['actual_parent_wait'])
                if tamper:
                    # Reproduces the independent SOURCE-only V1 epoch mismatch.
                    r.put_json(case/'APP_CLOSE_BINDING_PHASE1_CAPTURE_V1.json',saved)
                value=self.evaluate(case,t)
                self.assertEqual(value['passed_execution'],not tamper,value['errors'])
                self.assertFalse(value['capture_interface_passed']);self.assertFalse(value['exact']);self.assertEqual(value['gate1'],'UNKNOWN')
                self.assertFalse((case/'WORKER_ERROR.json').exists())
                return value
    def test_real_filesystem_nonfast_roundtrip(self):self.real_filesystem_roundtrip(False)
    def test_real_filesystem_fast_roundtrip(self):self.real_filesystem_roundtrip(True)
    def test_real_filesystem_nonfast_V1_epoch_mismatch_fails(self):self.real_filesystem_roundtrip(False,tamper=True)
    def test_real_filesystem_fast_V1_epoch_mismatch_fails(self):self.real_filesystem_roundtrip(True,tamper=True)
    def test_real_put_json_default_epoch_preserved_and_explicit_only_binding_optout(self):
        with metadata_directory() as case:
            value={'synthetic_metadata':True};r.put_json(case/'default.json',value);r.put_json(case/'binding.json',value,add_capture_epoch=False)
            default,_=r._metadata(case/'default.json');original,_=r._metadata(case/'binding.json')
            self.assertIn('capture_metadata_epoch',default);self.assertEqual(original,value);self.assertNotIn('capture_metadata_epoch',value)


class ActualOriginalBootstrapTests(unittest.TestCase):
    GROUP=ROOT/'discovery/phase1_first_startup_failure_v1'
    NAMES=('launch_storage_contract','n80_gpu_capacity')
    def setUp(self):
        import worker_passive_interface_v1 as worker
        self.worker=worker;previous={name:sys.modules.pop(name,None) for name in self.NAMES};old_path=list(sys.path)
        def restore():
            sys.path[:]=old_path
            for name,module in previous.items():
                if module is None:sys.modules.pop(name,None)
                else:sys.modules[name]=module
        self.addCleanup(restore)
    @contextmanager
    def group_copy(self):
        with metadata_directory() as group:
            directory=group/'worker_sources/parent';directory.mkdir(parents=True)
            for name in self.NAMES:(directory/(name+'.py')).write_bytes((self.GROUP/'worker_sources/parent'/(name+'.py')).read_bytes())
            yield group
    def test_full_actual_alias_sources_import_without_existing_sys_path(self):
        directory=(self.GROUP/'worker_sources/parent').resolve();sys.path[:]=[p for p in sys.path if Path(p).resolve()!=directory]
        value=self.worker.bootstrap_original_helpers(self.GROUP)
        self.assertEqual(sys.path[0],str(directory));self.assertEqual(set(value['modules']),set(self.NAMES))
        for name,module in value['modules'].items():self.assertEqual(Path(module.__file__).resolve(),directory/(name+'.py'))
        self.assertEqual([row['source_bytes'] for row in value['origin_evidence']['sources']],[117,653])
    def test_actual_inventory_and_failure_source_authority(self):
        value=r.source_index();rows=value['bootstrap_original_sources']
        self.assertEqual([row['install_relative'] for row in rows],['worker_sources/parent/launch_storage_contract.py','worker_sources/parent/n80_gpu_capacity.py'])
        for row in rows:
            raw=Path(row['path']).read_bytes();self.assertEqual((len(raw),c.sha(raw)),(row['bytes'],row['SHA256']))
        self.assertEqual(value['source_derivation']['actual_bootstrap_source_evidence']['actual_static_inventory_rows'],3675)
    def test_metadata_only_never_calls_storage_capacity_or_SDK(self):
        value=self.worker.bootstrap_original_helpers(self.GROUP)['origin_evidence']
        for key in ('parent_five_storage_calls','capacity_ctor_calls','SDK_constructor_calls'):self.assertEqual(value[key],0)
        self.assertFalse(value['resource_admission']);self.assertTrue(value['metadata_only'])
        self.assertFalse(any(name in sys.modules for name in ('torch','isaacsim','isaaclab')))
    def test_cached_correct_module_identity_retained(self):
        first=self.worker.bootstrap_original_helpers(self.GROUP);second=self.worker.bootstrap_original_helpers(self.GROUP)
        for name in self.NAMES:self.assertIs(first['modules'][name],second['modules'][name])
        self.assertTrue(all(x['cached_module_was_present'] for x in second['origin_evidence']['sources']))
    def test_cached_foreign_module_origin_fails(self):
        module=types.ModuleType('launch_storage_contract');module.__file__=str(HERE/'_FOREIGN_MODULE.py');sys.modules[module.__name__]=module
        with self.assertRaises(ValueError):self.worker.bootstrap_original_helpers(self.GROUP)
    def test_cached_function_replacement_fails(self):
        value=self.worker.bootstrap_original_helpers(self.GROUP);value['modules']['launch_storage_contract'].parent_five_storage=lambda a,b:None
        with self.assertRaises(ValueError):self.worker.bootstrap_original_helpers(self.GROUP)
    def test_cached_storage_global_pollution_fails(self):
        value=self.worker.bootstrap_original_helpers(self.GROUP);value['modules']['launch_storage_contract'].Path=lambda p:p
        with self.assertRaises(ValueError):self.worker.bootstrap_original_helpers(self.GROUP)
    def test_cached_capacity_global_pollution_fails(self):
        value=self.worker.bootstrap_original_helpers(self.GROUP);value['modules']['n80_gpu_capacity'].PRESET['gpu_max_rigid_contact_count']=1
        with self.assertRaises(ValueError):self.worker.bootstrap_original_helpers(self.GROUP)
    def test_missing_actual_directory_fails_no_fallback(self):
        with self.assertRaises(ValueError):self.worker.bootstrap_original_helpers(HERE/'_ABSENT_STAGED_GROUP')
    def test_full_source_tamper_fails_no_stub_fallback(self):
        with self.group_copy() as group:
            path=group/'worker_sources/parent/launch_storage_contract.py';path.write_bytes(path.read_bytes()+b'\n# tamper\n')
            with self.assertRaises(ValueError):self.worker.bootstrap_original_helpers(group)
    def test_missing_full_source_fails(self):
        with self.group_copy() as group:
            path=group/'worker_sources/parent/n80_gpu_capacity.py';self.assertTrue(path.resolve().is_relative_to(group.resolve()));path.unlink()
            with self.assertRaises(ValueError):self.worker.bootstrap_original_helpers(group)
    def test_real_copy_of_both_full_original_modules_not_half_functions(self):
        with self.group_copy() as group:
            value=self.worker.bootstrap_original_helpers(group)
            self.assertEqual(len(value['origin_evidence']['sources']),2)
            self.assertFalse((group/'kit_isolation').exists())
    def test_bootstrap_before_storage_and_first_native_import(self):
        tree=ast.parse((HERE/'worker_passive_interface_v1.py').read_text(encoding='utf-8'));main=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main')
        calls={}
        for node in ast.walk(main):
            if isinstance(node,ast.Call):calls.setdefault(ast.unparse(node.func),[]).append(node.lineno)
        native=min(n.lineno for n in ast.walk(main) if isinstance(n,ast.Import) and any(a.name=='torch' for a in n.names))
        self.assertLess(calls['task_args'][0],calls['bootstrap_original_helpers'][0]);self.assertLess(calls['bootstrap_original_helpers'][0],calls['parent_five_storage'][0]);self.assertLess(calls['bootstrap_original_helpers'][0],native)
    def test_wire_kinds_and_original_parent_unchanged(self):
        index=r.source_index();self.assertEqual(index['kind'],'PHASE1_CAPTURE_WORKER_SOURCE_INDEX_V1');self.assertEqual(index['source_version'],2)
        old=ROOT/'source_phase1_capture_worker_v1';self.assertEqual((HERE/'single_gpu_passive_capture_parent_v1.py').read_bytes(),(old/'single_gpu_passive_capture_parent_v1.py').read_bytes())
        self.assertEqual((HERE/'phase1_capture_contract.py').read_bytes(),(old/'phase1_capture_contract.py').read_bytes())


if __name__=='__main__':unittest.main(verbosity=2)
