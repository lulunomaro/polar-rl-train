"""CPU-only tests. Synthetic cache outcomes are not real SDK measurements."""
import ast
import copy
import io
import json
import math
from pathlib import Path
import sys
import time
import unittest
from reset_cache_and_failclosed_candidates_v2 import (
    SyntheticLazyCache, gravity_from_xyzw, xyzw_to_wxyz, matrix_from_wxyz,
    normalize_wxyz, pitch_xyzw, yaw_xyzw, max_error,
    primary_exception_with_cleanup_exit_zero, preserve_primary_and_close,
    terminal_receipt_decision, PHYSX_ROOT_DERIVED_CACHE_NAMES,
    invalidate_validated_physx_root_derived_cache,
    install_root_state_cache_invalidation_candidate)

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
CLOSED_DIR=ROOT/'reports'/'ACTUAL_SUPERMIMIC_EIGHT_V1_20261102_184527'
CLOSED=json.loads((CLOSED_DIR/'CLOSED_RESULT.json').read_text(encoding='utf-8'))


def raise_assertion():
    raise AssertionError('original gravity guard failure')
def close_zero():
    raise SystemExit(0)
def close_none():
    raise SystemExit(None)
def close_error():
    raise RuntimeError('cleanup failed')
def success_final(role='E0'):
    return dict(role=role,passed_execution=True,actual_BPTT_policy_steps=2520,
                target_reached=False,parent_finite_saved_stop=True,
                checkpoint=dict(full_new_model_critic_aux_optimizers_replay_RNG_hist_saved=True))


class QuaternionTests(unittest.TestCase):
    def test_xyzw_wxyz_conversion(self):
        self.assertEqual(xyzw_to_wxyz((1,2,3,4)),(4,1,2,3))
    def test_identity_gravity(self):
        self.assertEqual(gravity_from_xyzw((0,0,0,1)),(0,0,-1))
    def test_yaw_preserves_gravity(self):
        for angle in (.1,.5,1.7,math.pi):
            self.assertLess(max_error(gravity_from_xyzw(yaw_xyzw(angle)),(0,0,-1)),1e-14)
    def test_last_row_not_last_column(self):
        q=pitch_xyzw(.3);R=matrix_from_wxyz(xyzw_to_wxyz(q))
        g=gravity_from_xyzw(q)
        self.assertAlmostEqual(g[0],math.sin(.3))
        wrong=tuple(-R[i][2] for i in range(3))
        self.assertGreater(max_error(g,wrong),.5)
    def test_small_terrain_tilt_can_trigger_original_guard(self):
        theta=math.asin(.05059302598237991)
        err=max_error(gravity_from_xyzw(pitch_xyzw(theta)),(0,0,-1))
        self.assertAlmostEqual(err,.05059302598237991)
        self.assertGreater(err,1e-3)
    def test_quarter_turn_recovery_hypothesis(self):
        self.assertAlmostEqual(max_error(gravity_from_xyzw(pitch_xyzw(math.pi/2)),(0,0,-1)),1.)
    def test_normalization_and_sign_preserve_gravity(self):
        q=pitch_xyzw(.37)
        self.assertLess(max_error(gravity_from_xyzw(q),gravity_from_xyzw(tuple(-3*v for v in q))),1e-14)
    def test_flat_identity_guard_alone_does_not_prove_quaternion_order(self):
        xyzw=(0,0,0,1)
        correct=matrix_from_wxyz(xyzw_to_wxyz(xyzw));wrong=matrix_from_wxyz(xyzw)
        self.assertEqual(correct[2],wrong[2])
        self.assertNotEqual(correct[0],wrong[0])
    def test_invalid_quaternion_detected(self):
        for q in ((0,0,0,0),(math.nan,0,0,1)):
            with self.assertRaises(ValueError):normalize_wxyz(q)


class CacheCounterexamples(unittest.TestCase):
    def primed(self,pose_cache_fresh=True):
        x=SyntheticLazyCache(pose_setter_updates_pose_cache=pose_cache_fresh)
        x.read_gravity();x.write_reset_pose(pitch_xyzw(.15));return x
    def test_pose_fresh_gravity_can_be_stale(self):
        x=self.primed()
        self.assertEqual(x.read_pose(),x.pose_xyzw)
        self.assertGreater(max_error(gravity_from_xyzw(x.read_pose()),x.read_gravity()),.1)
    def test_zero_dt_update_is_not_universal_cache_fix(self):
        x=self.primed();x.update(0.)
        self.assertGreater(max_error(gravity_from_xyzw(x.read_pose()),x.read_gravity()),.1)
    def test_gravity_invalidation_suffices_only_if_dependency_fresh(self):
        x=self.primed();x.invalidate_gravity_only()
        self.assertLess(max_error(gravity_from_xyzw(x.pose_xyzw),x.read_gravity()),1e-14)
    def test_gravity_only_invalidation_can_recompute_from_stale_pose(self):
        x=self.primed(False);x.invalidate_gravity_only()
        self.assertGreater(max_error(gravity_from_xyzw(x.pose_xyzw),x.read_gravity()),.1)
    def test_dependency_closure_invalidation_in_fake(self):
        x=self.primed(False);x.invalidate_dependency_closure()
        self.assertLess(max_error(gravity_from_xyzw(x.pose_xyzw),x.read_gravity()),1e-14)
    def test_targeted_invalidation_does_not_advance_fake_physics_or_rng(self):
        x=self.primed(False)
        before=(x.sim_stamp,x.physics_steps,x.resets,x.noise_rng_draws,x.command_rng_draws)
        x.invalidate_dependency_closure();x.read_gravity()
        self.assertEqual(before,(x.sim_stamp,x.physics_steps,x.resets,x.noise_rng_draws,x.command_rng_draws))
    def test_invalidate_after_original_obs_leaves_stale_actor_input(self):
        x=self.primed();obs=x.compute_original_observation_once();x.invalidate_dependency_closure()
        self.assertGreater(max_error(obs['gravity'],x.read_gravity()),.1)
        self.assertEqual(x.observation_calls,1)
    def test_hook_before_original_single_observation_preserves_draw_count(self):
        x=self.primed();x.invalidate_dependency_closure();obs=x.compute_original_observation_once()
        self.assertLess(max_error(obs['gravity'],gravity_from_xyzw(obs['pose'])),1e-14)
        self.assertEqual((x.observation_calls,x.noise_rng_draws,x.resets),(1,1,1))


class FakeBuffer:
    def __init__(self):self.timestamp=0.;self.data=object()

class FakePhysxData:
    # Synthetic marker only; this class is NOT an imported/constructed SDK class.
    __module__='isaaclab_physx.assets.articulation.articulation_data'
    __backend_name__='physx'
    def __init__(self):
        self._sim_timestamp=0.
        for name in PHYSX_ROOT_DERIVED_CACHE_NAMES:setattr(self,name,FakeBuffer())

class FakeRobot:
    def __init__(self):self.data=FakePhysxData();self.writes=0
    def write_root_state_to_sim(self,*args,**kwargs):
        self.writes+=1;return 'original-return'

class ExactCandidateAndBackendSourceTests(unittest.TestCase):
    backend=ROOT/'discovery'/'sdk_reset_cache_backend_v2'/'backend'
    def method(self,file,class_name,method_name):
        tree=ast.parse((self.backend/file).read_text(encoding='utf-8'))
        cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name==class_name)
        return next(n for n in cls.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name==method_name)
    def test_source_pose_writer_omits_eight_derived_timestamp_invalidations(self):
        method=self.method('articulation.py','Articulation','write_root_link_pose_to_sim_index')
        touched=[]
        for node in ast.walk(method):
            if isinstance(node,ast.Assign):
                for target in node.targets:
                    if isinstance(target,ast.Attribute) and target.attr=='timestamp' and isinstance(target.value,ast.Attribute):
                        touched.append(target.value.attr)
        self.assertIn('_root_state_w',touched)
        self.assertFalse(set(PHYSX_ROOT_DERIVED_CACHE_NAMES)&set(touched))
    def test_source_gravity_exact_timestamp_comparison(self):
        m=self.method('articulation_data.py','ArticulationData','projected_gravity_b')
        compare=ast.unparse(next(n for n in ast.walk(m) if isinstance(n,ast.If)).test)
        self.assertEqual(compare,'self._projected_gravity_b.timestamp < self._sim_timestamp')
        text=ast.unparse(m);self.assertIn('self.root_link_quat_w',text)
    def test_source_update_zero_dt_does_not_advance_timestamp(self):
        m=self.method('articulation_data.py','ArticulationData','update')
        self.assertIn('self._sim_timestamp += dt',ast.unparse(m))
    def test_source_full_state_writer_calls_pose_then_com_velocity(self):
        m=self.method('articulation.py','Articulation','write_root_state_to_sim')
        calls=[n.func.attr for n in ast.walk(m) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute)]
        self.assertLess(calls.index('write_root_link_pose_to_sim_index'),calls.index('write_root_com_velocity_to_sim_index'))
    def test_source_expected_backend_not_live_binding_claim(self):
        text=(self.backend/'articulation_data.py').read_text(encoding='utf-8')
        self.assertIn('__backend_name__: str = "physx"',text)
        self.assertIn('TimestampedBufferWarp as TimestampedBuffer',text)
    def test_missing_live_binding_is_fail_closed_and_no_mutation(self):
        d=FakePhysxData()
        with self.assertRaises(RuntimeError):invalidate_validated_physx_root_derived_cache(d)
        self.assertTrue(all(getattr(d,n).timestamp==0 for n in PHYSX_ROOT_DERIVED_CACHE_NAMES))
    def test_wrong_backend_is_fail_closed(self):
        d=FakePhysxData();d.__backend_name__='newton'
        with self.assertRaises(RuntimeError):invalidate_validated_physx_root_derived_cache(d,live_binding_verified=True)
    def test_missing_field_validates_all_before_any_mutation(self):
        d=FakePhysxData();delattr(d,PHYSX_ROOT_DERIVED_CACHE_NAMES[-1])
        with self.assertRaises(RuntimeError):invalidate_validated_physx_root_derived_cache(d,live_binding_verified=True)
        self.assertEqual(d._projected_gravity_b.timestamp,0.)
    def test_exact_candidate_only_mutates_stamp_not_data_proxy_or_clock(self):
        d=FakePhysxData();before={n:(id(getattr(d,n)),id(getattr(d,n).data)) for n in PHYSX_ROOT_DERIVED_CACHE_NAMES}
        r=invalidate_validated_physx_root_derived_cache(d,live_binding_verified=True)
        self.assertEqual(d._sim_timestamp,0.)
        self.assertEqual(before,{n:(id(getattr(d,n)),id(getattr(d,n).data)) for n in PHYSX_ROOT_DERIVED_CACHE_NAMES})
        self.assertTrue(all(getattr(d,n).timestamp==-1. for n in PHYSX_ROOT_DERIVED_CACHE_NAMES))
        self.assertEqual(r['extra_observation_computes'],0)
    def test_adapter_calls_original_once_and_returns_original_value(self):
        robot=FakeRobot();install_root_state_cache_invalidation_candidate(robot,live_binding_verified=True)
        self.assertEqual(robot.write_root_state_to_sim('synthetic state',env_ids=[0]),'original-return')
        self.assertEqual(robot.writes,1)
        self.assertEqual(robot.data._sim_timestamp,0.)
        self.assertEqual(robot.data._projected_gravity_b.timestamp,-1.)
    def test_invalid_clock_blocks_install_before_original_writer(self):
        robot=FakeRobot();robot.data._sim_timestamp=float('nan')
        with self.assertRaises(RuntimeError):install_root_state_cache_invalidation_candidate(robot,live_binding_verified=True)
        self.assertEqual(robot.writes,0)
        self.assertFalse(getattr(robot,'_source_review_root_state_hook_installed',False))
    def test_duplicate_adapter_install_is_blocked(self):
        robot=FakeRobot();install_root_state_cache_invalidation_candidate(robot,live_binding_verified=True)
        with self.assertRaises(RuntimeError):install_root_state_cache_invalidation_candidate(robot,live_binding_verified=True)
    def test_manager_reset_has_original_forward_no_step_or_scene_update(self):
        path=ROOT/'discovery'/'sdk_reset_cache_backend_v2'/'base'/'manager_based_env.py'
        tree=ast.parse(path.read_text(encoding='utf-8'))
        cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ManagerBasedEnv')
        m=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='reset')
        names=[ast.unparse(n.func) for n in ast.walk(m) if isinstance(n,ast.Call)]
        self.assertIn('self.sim.forward',names)
        self.assertNotIn('self.sim.step',names);self.assertNotIn('self.scene.update',names)


class ExceptionAndOwnerTests(unittest.TestCase):
    def test_finally_zero_exit_masks_original_exception_in_python(self):
        with self.assertRaises(SystemExit) as caught:primary_exception_with_cleanup_exit_zero()
        self.assertEqual(caught.exception.code,0)
        self.assertIsInstance(caught.exception.__context__,AssertionError)
    def test_candidate_preserves_primary_error_after_zero_exit(self):
        out=preserve_primary_and_close(raise_assertion,[('app',close_zero)])
        self.assertEqual(out.error_rc,1)
        self.assertIn('AssertionError',out.primary_error)
    def test_candidate_success_zero_cleanup_exit_stays_zero(self):
        out=preserve_primary_and_close(lambda:None,[('app',close_none)])
        self.assertEqual(out.error_rc,0)
    def test_candidate_runs_remaining_cleanups_after_first_cleanup_error(self):
        called=[]
        out=preserve_primary_and_close(raise_assertion,[('env',close_error),('app',lambda:called.append('app'))])
        self.assertEqual(called,['app']);self.assertEqual(out.error_rc,1)
        self.assertIn('AssertionError',out.primary_error)
    def test_candidate_cleanup_error_is_failure_on_otherwise_success(self):
        self.assertEqual(preserve_primary_and_close(lambda:None,[('app',close_error)]).error_rc,1)
    def test_rc_zero_with_worker_error_and_missing_final_blocks(self):
        out=terminal_receipt_decision(0,None,{'error':'guard failed'},'E3')
        self.assertTrue(out['block_pending']);self.assertEqual(out['returncode'],0)
        self.assertEqual(out['skill_success'],None)
    def test_finite_saved_partial_execution_not_forced_to_target3000(self):
        out=terminal_receipt_decision(0,success_final(),None,'E0')
        self.assertFalse(out['effective_error']);self.assertIsNone(out['skill_success'])
    def test_even_final_true_does_not_erase_worker_error(self):
        self.assertTrue(terminal_receipt_decision(0,success_final(),{},'E0')['block_pending'])
    def test_wrong_role_or_incomplete_save_blocks(self):
        final=success_final();final['checkpoint']={}
        self.assertTrue(terminal_receipt_decision(0,final,None,'E2')['block_pending'])
    def test_nonzero_rc_blocks_with_valid_final(self):
        self.assertTrue(terminal_receipt_decision(9,success_final(),None,'E0')['block_pending'])
    def test_invalid_count_blocks(self):
        for value in (None,True,-1,'2520'):
            final=success_final();final['actual_BPTT_policy_steps']=value
            self.assertTrue(terminal_receipt_decision(0,final,None,'E0')['block_pending'])


class ClosedSourceEvidenceTests(unittest.TestCase):
    def test_closed_metadata_eight_roles_six_errors(self):
        self.assertEqual(len(CLOSED['rows']),8)
        self.assertEqual(sum(x['status']=='ERROR' for x in CLOSED['rows']),6)
    def test_six_error_producer_counts_are_null_not_recorded_zero(self):
        for row in CLOSED['rows']:
            if row['status']=='ERROR':
                self.assertIsNone(row['counts']);self.assertIsNone(row['actual_BPTT_policy_steps'])
                self.assertIsNone(row['final']);self.assertIsNone(row['error']['counts'])
                self.assertIn("AssertionError: ('SDK quaternion convention'",row['error']['error'])
    def test_e0_e2_actual_counts_retained(self):
        rows={x['role']:x for x in CLOSED['rows']}
        self.assertEqual(rows['E0']['actual_BPTT_policy_steps'],2520)
        self.assertEqual(rows['E2']['actual_BPTT_policy_steps'],2392)
    def test_eight_waited_rc_zero_six_would_block_candidate(self):
        decisions=[]
        for row in CLOSED['rows']:
            waited=json.loads((CLOSED_DIR/'roles'/row['role']/'PARENT_WAITED_ACTUAL.json').read_text(encoding='utf-8'))
            self.assertEqual(waited['returncode'],0)
            decisions.append(terminal_receipt_decision(waited['returncode'],row['final'],row['error'],row['role']))
        self.assertEqual(sum(x['effective_error'] for x in decisions),6)
        self.assertTrue(all(not x['accounting_rewrite'] for x in decisions))
    def test_original_settlement_and_leases_are_not_rewritten(self):
        e=CLOSED['parent_exit']
        self.assertTrue(e['all_own_children_waited'] and e['original_cost_settled'] and e['original_leases_released'])
    def test_worker_source_rethrows_original_exception(self):
        text=(ROOT/'source_runtime'/'worker_supermimic_bptt.py').read_text(encoding='utf-8')
        tree=ast.parse(text)
        handlers=[n for n in ast.walk(tree) if isinstance(n,ast.ExceptHandler) and isinstance(n.type,ast.Name) and n.type.id=='BaseException']
        self.assertTrue(any(any(isinstance(x,ast.Raise) for x in h.body) for h in handlers))
    def test_bridge_threshold_and_xyzw_reorder_unchanged(self):
        text=(ROOT/'source_runtime'/'native_supermimic_bridge.py').read_text(encoding='utf-8')
        self.assertIn('root[:,[6,3,4,5]]',text)
        self.assertIn('assert err<1e-3',text)
        self.assertIn('state[1][:,2,:]',text)
    def test_no_audited_task_sdk_or_torch_imported(self):
        self.assertFalse(any(k=='torch' or k=='isaaclab' or k.startswith('isaaclab.') or k=='mod4_task' for k in sys.modules))


if __name__=='__main__':
    suite=unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    output=io.StringIO();start=time.perf_counter()
    result=unittest.TextTestRunner(stream=output,verbosity=2).run(suite)
    receipt=dict(kind='STDLIB_CPU_SYNTHETIC_COUNTEREXAMPLES_AND_CLOSED_METADATA_SOURCE_TESTS_NOT_SDK_RUNTIME',
                 tests_run=result.testsRun,failures=len(result.failures),errors=len(result.errors),
                 passed=result.wasSuccessful(),elapsed_seconds=time.perf_counter()-start,
                 SDK_imports=0,torch_imports=0,GPU_or_physics_steps=0,
                 audited_sources_imported_or_modified=False,accounting_modified=False,
                 output=output.getvalue())
    (HERE/'CPU_TEST_RESULTS_V2.json').write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(output.getvalue());print(json.dumps({k:v for k,v in receipt.items() if k!='output'},ensure_ascii=False))
    raise SystemExit(0 if result.wasSuccessful() else 1)
