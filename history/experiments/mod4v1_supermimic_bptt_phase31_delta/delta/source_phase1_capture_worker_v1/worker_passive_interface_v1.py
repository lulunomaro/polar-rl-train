"""SOURCE candidate: one original formal E3 setup, bounded passive interface capture.

Not a policy evaluation/training entry. Native imports exist only inside main,
and this SOURCE package never invokes main/stages/dispatches it.
"""
from pathlib import Path
import os
import sys
import json
import time
import runpy
import traceback
from phase1_capture_contract import candidate_final, need
from phase1_capture_runtime import (task_args, wait_start, core, dependency, load_file, put_json,
    install_paired_pose_before_original_reset, paired_protocol_receipt, record_primary_error,
    close_original_eval_resources)
from phase1_capture_observer import (make_recorder, WindowRetention, stored_rng_counts,
    materialize, verify_actuation_binding, restore_interfaces, initial_sensor_memory)


def main():
    task, out, group = task_args()  # NEW kind/purpose + original inheritedEX before any SDK; no invented approval gate.
    B = Path(task['runtime_root']); mod = B/'runtime/isaac/mod4'
    ns = env = bridge = sensor = actuation = None
    started = time.time(); result = None; restore = None
    try:
        # Narrow E3 projection of original formal worker lines14-66. No training
        # worker/command-binding route is mixed in; original compute66 is retained.
        original = json.loads((B/'original_run_manifest.json').read_bytes())['env']
        for key in list(os.environ):
            if key.startswith('RM_') or key in ('RANK','WORLD_SIZE','LOCAL_RANK','MASTER_ADDR','MASTER_PORT'):
                del os.environ[key]
        os.environ.update({k:str(v) for k,v in original.items() if k not in ('RM_RESCUE_STOP_FILE','RM_RESCUE_DEADLINE','RM_SLOPE_INITIAL_ADMISSION')})
        os.environ.update(RM_MOD4_USD=str(B/'runtime/assets/robot.usd'),RM_KEEP_STD='1',RM_PHYSICS_DT_S='0.0025',RM_SOLVER_POS='32',RM_SOLVER_VEL='4',MOD4_RESUME_QUEUE_CONTROL_US='20000')
        from launch_storage_contract import parent_five_storage
        from n80_gpu_capacity import capacity_ctor
        storage=parent_five_storage(B,out);storage.mkdir();(storage/'data').mkdir();(storage/'DerivedDataCache').mkdir();(storage/'data/user.config.json').write_text('{}')
        os.environ['WP_CACHE_DIR']=str(out/'warp_cache');os.environ['PYTHONDONTWRITEBYTECODE']='1'
        os.environ.update(MOD4V1_E3_ASSET_DIR=str(B/'runtime/assets'),MOD4V1_E3_JOB_ROOT=str(B),MOD4V1_E3_KIT_STORAGE_ROOT=str(storage),OWN_E2_H1_KIND='E3_PUBLIC_RECOVERY',RM_SPAWN_GRACE_STEPS='5',RM_JUMP_SCRIPT_PROB='0',RM_MOD4_MAP='',RM_MOD4_TERRAIN='flat')
        entry=mod/'train_mod4v1_e3.py'
        sys.path[:0]=[str(B/'lib'),str(mod),str(B/'runtime'),str(B),str(out)]
        from mod4v1_fresh_dr_guard import FreshDRNominalGuard
        sys.argv=[str(entry),'--headless','--device','cuda:0','--num_envs','80','--seed','20260928','--dry_run',str(task['controls'])]
        import torch
        def no_model_load(*args, **kwargs):
            raise RuntimeError('NEW_PASSIVE_INTERFACE_PROBE_NO_TRAIN explicit syntheticzero6: model reads0, no fallback')
        torch.load=no_model_load
        ns=runpy.run_path(str(entry),run_name='phase1_passive_E3_build_no_main')
        factory=ns['build_env'];factory.__globals__['Mod4Env']=capacity_ctor(factory.__globals__['Mod4Env']);env=factory();identity=ns['E3_IDENTITY']
        from mild_dr import tensor
        from actual_DR_memory_getter272 import RuntimeOrderBinding, ActualDRMemoryGetter
        robot=env.scene['robot']
        install_paired_pose_before_original_reset(env)
        guard=FreshDRNominalGuard(env,identity,torch_module=torch,tensor_converter=tensor);guard.assert_new_nominals_unchanged()
        env.reset()  # Exactly the one original explicit reset53; returned obs is pre-E3 placement.
        env.e3_reset_enabled=True;env.place_declared_fall(torch.arange(80,device=env.device));env.publish();assert set(env.recovery.recipe.tolist())==set(range(13))
        guard.assert_new_nominals_unchanged();audit=env._mild_dr.audit();assert audit['actual_parameters_pass']
        assert env.num_envs==80 and env.step_dt==.02 and env.physics_dt==.0025 and env.cfg.decimation==8
        assert env.cfg.terminations.closure.params['threshold']==.01 and env.cfg.terminations.mimic.params['threshold']==.01
        assert identity.usd_sha256==task['asset_SHA'] and identity.contract_sha256==task['contract_SHA']
        def names(key):
            ids=robot.actuators[key].joint_indices
            if isinstance(ids,slice):ids=list(range(len(robot.joint_names)))[ids]
            elif hasattr(ids,'tolist'):ids=ids.tolist()
            return tuple(robot.joint_names[i] for i in ids)
        binding=RuntimeOrderBinding(tuple(robot.body_names),tuple(robot.joint_names),names('legs'),names('wheels'),names('gas_springs'),int(env._mild_dr.materials.shape[1]))
        getter=ActualDRMemoryGetter(env,binding);getter.capture_initial()  # Existing original63, not a new observer getter.
        def small(value):
            value=value.detach();return dict(shape=list(value.shape),dtype=str(value.dtype),finite=bool(torch.isfinite(value).all()),min=float(value.min()),max=float(value.max()),first8=value.reshape(-1)[:8].cpu().tolist())
        memory={key:small(value) for key,value in getter.cache.items()}
        obs=env.observation_manager.compute();guard.check_observations(obs)  # Existing original66, after E3 placement55.

        bridge_module=load_file('native_supermimic_bridge','native_supermimic_bridge.py',(13125,'8211964c2ce3dd78fdb9fee6603ee4a4dcfbca6fa9d7df44f20d3ddb7aaead29'))
        bridge=bridge_module.NativeTaskBridge(env,task,out,tensor,teacher=None,initial_obs=obs)
        state=bridge.init_state()  # Once, provided original66obs prevents bridge compute fallback.
        need(vars(bridge)['real'] is env and vars(bridge)['initialized'] is True, 'same initialized original env/bridge')
        boundary=core().OriginalEpisodeBoundary(torch,env.device,n=80)
        api=dependency('source_api','phase1_deps/sensor/source_api.py')
        sensor_api=dependency('passive_capture','phase1_deps/sensor/passive_capture.py')
        actuation_api=dependency('phase1_sealed_actuation_tap','phase1_deps/actuation/actuation_tap.py')
        manifest=json.loads((group/'phase1_deps/sensor/SOURCE_API_MANIFEST.json').read_bytes())
        act_sources=json.loads((group/'phase1_deps/actuation/SOURCE_PINS.json').read_bytes())['sources']
        role_sources={p:r for p,r in act_sources.items() if p.startswith('discovery/reward_command_audit_v1/E3/')}
        act_binding=verify_actuation_binding(env,api,role_sources)
        import feedback_delay_runtime
        rows=torch.arange(8,dtype=torch.long,device=env.device)
        snapshot=sensor_api.tensor_snapshot_adapter(torch.Tensor,rows,80)
        recorder=make_recorder(sensor_api.BoundedRecorder,snapshot)
        sensor=sensor_api.install_passive_capture(env,bridge,feedback_delay_runtime,manifest['roles']['E3'],manifest['bridge'],recorder=recorder,snapshot=snapshot)
        actuation=actuation_api.install_actuation_tap(env,capacity=8192)
        static_before=actuation.snapshot_static();rng_before=stored_rng_counts(env)
        initial_sensor=initial_sensor_memory(env,snapshot)  # Existing FIFO/cur/out/sample_tick; clean0 remains UNKNOWN.
        recorder.actor(state.obs['policy'],state.obs['policy'],0)
        ready=dict(purpose=task['purpose'],num_envs=80,controls=task['controls'],D0_D7_fresh_audit=audit,
                   actual_component_memory_not_independent_backend=memory,one_explicit_original_reset=True,
                   original_reset_place_publish_compute_order=[53,55,66],teacher=None,model_PT_reads=0,
                   capture_not_skill=True,resource_only_GPU_capacity=env._n80_allocation_only_capacity)
        put_json(out/'FRESH80_FULLDR_BEFORE_CONTROL.json',ready)
        go=wait_start(task,out,group,ready)
        tick=int(env._integrated_contact.tick);fb=int(env._feedback_100hz_tick);delays=dict(env._physics_action_delay.calls)
        zero=torch.zeros((80,6),dtype=torch.float32,device=env.device)  # Explicit deterministic tape, not a policy output.
        retained=WindowRetention();completed=0;natural_ends=0;partial_candidates=0
        first_control=time.time()
        with torch.inference_mode():
            for index in range(task['controls']):
                if time.time()>=task['absolute_worker_deadline_epoch']:raise TimeoutError('Own original finite worker deadline')
                if (group/'GROUP_ABORT.json').exists():raise RuntimeError('Own group aborted')
                boundary.for_action()
                state=bridge.step(zero)  # Original bridge -> exactly one original env.step; true terminal/pre-reset preserved.
                boundary.after_original_step(state.terminated,state.truncated)
                completed+=1
                recorder.actor(state.obs['policy'],state.obs['policy'],completed)
                done_count=int((state.terminated|state.truncated).sum())  # Original returned flags, not SDK getters.
                natural_ends+=done_count;partial_candidates+=int(0<done_count<80)
                retained.add(index,actuation.drain())  # Off callback, two first/two last windows only.
        physics=int(env._integrated_contact.tick)-tick;feedback=int(env._feedback_100hz_tick)-fb
        actual_delay={key:env._physics_action_delay.calls[key]-delays[key] for key in ('legs','wheels')}
        guard.assert_new_nominals_unchanged();after=env._mild_dr.audit();assert after['actual_parameters_pass']
        coverage=recorder.coverage(completed)
        coverage.update(natural_terminal_env_events=natural_ends,natural_partial_reset_candidate_controls=partial_candidates,
                        partial_reset_correctness='UNKNOWN_NEEDS_LIVE_VERIFIER',no_extra_reset_for_coverage=True)
        status=actuation.status()
        if status['dropped_events'] or status['observer_errors'] or status['missing_hooks']:
            coverage['deficits'].append('ACTUATION_CAPTURE_DROPPED_ERROR_OR_MISSING_HOOK')
        result=dict(completed=completed,physics=physics,feedback=feedback,delay_calls=actual_delay,boundary=boundary.receipt(),
                    sensor=sensor.report(),actuation=dict(status=status,binding=act_binding,static_before=static_before,static_after=actuation.snapshot_static()),
                    coverage=coverage,rng_counts=dict(before=rng_before,after=stored_rng_counts(env)),
                    trace=dict(initial_sensor_memory=initial_sensor,
                                sensor_special={key:list(value) for key,value in recorder.special.items()},actuation=retained.report()),
                    setup=dict(D0_D7_before=audit,D0_D7_after=after,original_explicit_reset_count=1,
                               original_existing_compute_count=1,bridge_init_state_count=1,paired_pose=paired_protocol_receipt(),
                               started_epoch=started,GO_epoch=go['epoch'],first_control_epoch=first_control,last_control_epoch=time.time(),
                               SDK_wall_cost_is_not_zero_by_PT0=True,finite_validation_cost_protocol=task['finite_validation_cost_protocol']))
    except BaseException:
        record_primary_error(out,role='E3',phase='NEW_passive_capture_worker',error=traceback.format_exc())
        raise
    finally:
        restore=restore_interfaces(actuation,sensor,bridge)
        if not restore['ok']:record_primary_error(out,role='E3',phase='reverse_interface_restore',error=restore)
        try:
            if result is not None and not (out/'WORKER_ERROR.json').exists():
                if actuation is not None:result['actuation']['status_after_restore']=actuation.status()
                final=candidate_final(task,**result,restore=restore)
                put_json(out/'FINAL.json',materialize(final,torch.Tensor))  # One bounded export, after all tap callbacks/restoration.
        except BaseException:
            record_primary_error(out,role='E3',phase='capture_FINAL_export',error=traceback.format_exc())
            raise
        finally:
            close_original_eval_resources(env,None if ns is None else ns['app'],out,task)


if __name__=='__main__':main()
