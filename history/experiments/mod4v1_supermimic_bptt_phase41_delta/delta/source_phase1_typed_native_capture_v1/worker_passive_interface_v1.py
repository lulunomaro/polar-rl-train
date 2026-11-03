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
from phase1_capture_contract import candidate_final, need, PRODUCER_ABI
from phase1_capture_runtime import (task_args, wait_start, core, dependency, load_file, put_json,
    install_paired_pose_before_original_reset, paired_protocol_receipt, record_primary_error,
    close_original_eval_resources)
from phase1_capture_observer import (WindowRetention, stored_rng_counts, stored_clock,
    verify_actuation_binding, restore_interfaces, initial_sensor_memory, typed_c2_memory,
    stored_actuation_evidence, verify_c2_source_binding, incomplete_capture, C2_CONTAINER)


def bootstrap_original_helpers(group):
    """Stdlib-only metadata bootstrap; no storage call, factory call or admission."""
    import hashlib
    import importlib
    import types
    group=Path(group).resolve();directory=group/'worker_sources'/'parent'
    pins=(('launch_storage_contract','parent_five_storage',117,'e40b51db4bca2f322cc2c9b4b0fe011eed292ae605f4f175f268a5bf90326047'),
          ('n80_gpu_capacity','capacity_ctor',653,'ab26d1b22557e6a85231795cd41c52aa53b81e69661c8a62f4c72118a62c74cc'))
    need(directory.is_dir() and directory.resolve()==directory,'exact complete staged worker_sources/parent directory required')
    def code_key(code):
        return (code.co_name,code.co_argcount,code.co_posonlyargcount,code.co_kwonlyargcount,code.co_flags,
                code.co_code,code.co_names,code.co_varnames,code.co_freevars,code.co_cellvars,
                tuple(code_key(x) if isinstance(x,types.CodeType) else x for x in code.co_consts))
    modules={};origins=[]
    for name,function_name,size,digest in pins:
        path=directory/(name+'.py');need(path.is_file() and not path.is_symlink(),'complete original bootstrap source required: '+name)
        raw=path.read_bytes();need((len(raw),hashlib.sha256(raw).hexdigest())==(size,digest),'original bootstrap source bytes/SHA differ: '+name)
        cached=sys.modules.get(name)
        if cached is not None:
            need(isinstance(cached,types.ModuleType) and type(vars(cached).get('__file__')) is str
                 and Path(vars(cached)['__file__']).resolve()==path,'cached bootstrap module origin differs: '+name)
        if str(directory) not in sys.path:sys.path.insert(0,str(directory))
        importlib.invalidate_caches()
        module=importlib.import_module(name)  # Normal import of the full original staged module, never a stub/fallback.
        source=vars(module).get('__file__');spec=vars(module).get('__spec__')
        need(type(source) is str and Path(source).resolve()==path and spec is not None
             and type(spec.origin) is str and Path(spec.origin).resolve()==path,'actual imported bootstrap module origin differs: '+name)
        function=vars(module).get(function_name)
        expected=[x for x in compile(raw,str(path),'exec').co_consts if isinstance(x,types.CodeType) and x.co_name==function_name]
        need(isinstance(function,types.FunctionType) and function.__globals__ is vars(module)
             and function.__module__==name and function.__qualname__==function_name and len(expected)==1
             and Path(function.__code__.co_filename).resolve()==path and function.__code__.co_firstlineno==expected[0].co_firstlineno
             and code_key(function.__code__)==code_key(expected[0]) and function.__defaults__ is None
             and function.__kwdefaults__ is None,'actual cached/bootstrap function code differs: '+name)
        if name=='launch_storage_contract':need(vars(module).get('Path') is Path,'original storage Path global differs')
        else:
            expected_preset=dict(gpu_max_rigid_contact_count=2**20,gpu_max_rigid_patch_count=2**16,
                gpu_found_lost_pairs_capacity=2**18,gpu_found_lost_aggregate_pairs_capacity=2**22,gpu_total_aggregate_pairs_capacity=2**20)
            need(type(vars(module).get('PRESET')) is dict and vars(module)['PRESET']==expected_preset,'original capacity PRESET global differs')
        modules[name]=module
        origins.append(dict(module=name,function=function_name,relative='worker_sources/parent/'+name+'.py',
                            actual_source_file=str(path),source_bytes=size,source_SHA256=digest,
                            actual_module_and_function_code_verified=True,cached_module_was_present=cached is not None))
    return dict(modules=modules,origin_evidence=dict(kind='PHASE1_ORIGINAL_HELPER_BOOTSTRAP_V2',source_version=2,
                group=str(group),path_inserted=str(directory),sources=origins,metadata_only=True,
                parent_five_storage_calls=0,capacity_ctor_calls=0,SDK_constructor_calls=0,resource_admission=False))


def main():
    task, out, group = task_args()  # NEW kind/purpose + original inheritedEX before any SDK; no invented approval gate.
    B = Path(task['runtime_root']); mod = B/'runtime/isaac/mod4'
    ns = env = bridge = sensor = actuation = None
    started = time.time(); result = None; restore = None
    codec = snapshot = retained = None; completed = 0
    try:
        # Narrow E3 projection of original formal worker lines14-66. No training
        # worker/command-binding route is mixed in; original compute66 is retained.
        original = json.loads((B/'original_run_manifest.json').read_bytes())['env']
        for key in list(os.environ):
            if key.startswith('RM_') or key in ('RANK','WORLD_SIZE','LOCAL_RANK','MASTER_ADDR','MASTER_PORT'):
                del os.environ[key]
        os.environ.update({k:str(v) for k,v in original.items() if k not in ('RM_RESCUE_STOP_FILE','RM_RESCUE_DEADLINE','RM_SLOPE_INITIAL_ADMISSION')})
        os.environ.update(RM_MOD4_USD=str(B/'runtime/assets/robot.usd'),RM_KEEP_STD='1',RM_PHYSICS_DT_S='0.0025',RM_SOLVER_POS='32',RM_SOLVER_VEL='4',MOD4_RESUME_QUEUE_CONTROL_US='20000')
        bootstrap=bootstrap_original_helpers(group)
        parent_five_storage=bootstrap['modules']['launch_storage_contract'].parent_five_storage
        capacity_ctor=bootstrap['modules']['n80_gpu_capacity'].capacity_ctor
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
        boundary=core().OriginalEpisodeBoundary(torch,bridge.device,n=80)
        codec_api=dependency('typed_capture_codec','phase1_deps/codec/typed_capture_codec.py')
        api=dependency('source_api','phase1_deps/sensor/source_api.py')
        field_api=dependency('field_snapshot','phase1_deps/sensor/field_snapshot.py')
        dependency('dependency_contract','phase1_deps/sensor/dependency_contract.py')
        sensor_api=dependency('passive_capture','phase1_deps/sensor/passive_capture.py')
        actuation_api=dependency('phase1_sealed_actuation_tap_v2','phase1_deps/actuation_c2/actuation_tap_v2.py')
        manifest=json.loads((group/'phase1_deps/sensor/SOURCE_API_MANIFEST.json').read_bytes())
        act_sources=json.loads((group/'phase1_deps/actuation/SOURCE_PINS.json').read_bytes())['sources']
        role_sources={p:r for p,r in act_sources.items() if p.startswith('discovery/reward_command_audit_v1/E3/')}
        act_binding=verify_actuation_binding(env,api,role_sources)
        c2_binding=verify_c2_source_binding(api,actuation_api)
        c2_ref='phase1_deps/actuation_c2/actuation_tap_v2.py@sha256:ec10b09b77548c560611e641d685e2cee029c9778ff8c8852a8bf070243bd95d'
        adapter_ref=next(p+'@sha256:'+r['sha256'] for p,r in role_sources.items() if p.endswith('/action_delay_sdk_adapter.py'))
        import feedback_delay_runtime
        rows=torch.arange(8,dtype=torch.long,device=env.device)
        snapshot=sensor_api.tensor_snapshot_adapter(torch.Tensor,rows,80,witness_env_ids=list(range(8)))
        codec=snapshot.codec
        ledger=codec_api.ControlLedger(codec,controls=task['controls'],run_id=task['group_id']+':E3')
        recorder=sensor_api.BoundedRecorder(first=2,last=2,max_events=256)
        sensor=sensor_api.install_passive_capture(env,bridge,feedback_delay_runtime,manifest['roles']['E3'],manifest['bridge'],
            recorder=recorder,snapshot=snapshot,ledger=ledger)  # Unchanged DEFAULT22+3, then actual native MRO/preflight, then attach.
        actuation=actuation_api.install_actuation_tap(env,capacity=8192)
        static_before=typed_c2_memory(actuation.snapshot_static(),codec,snapshot,source_ref=c2_ref,
            field='actuation.static_before',clock=stored_clock(env),role='ENV_ROWS_WITNESS')
        stored_binding_before=stored_actuation_evidence(env,codec,source_ref=adapter_ref)
        rng_before=stored_rng_counts(env)
        initial_sensor=initial_sensor_memory(env,snapshot,sensor.source_refs)
        initial_actor=snapshot.rows(state.obs['policy'],source_ref=sensor.source_refs['bridge'],
            source_field='original_initial_policy_buffer_not_fresh_clean0',clock=stored_clock(env))
        ready=dict(purpose=task['purpose'],num_envs=80,controls=task['controls'],D0_D7_fresh_audit=audit,
                   actual_component_memory_not_independent_backend=memory,one_explicit_original_reset=True,
                   original_reset_place_publish_compute_order=[53,55,66],teacher=None,model_PT_reads=0,
                   capture_not_skill=True,resource_only_GPU_capacity=env._n80_allocation_only_capacity)
        put_json(out/'FRESH80_FULLDR_BEFORE_CONTROL.json',ready)
        go=wait_start(task,out,group,ready)
        tick=int(env._integrated_contact.tick);fb=int(env._feedback_100hz_tick);delays=dict(env._physics_action_delay.calls)
        zero=torch.zeros((80,6),dtype=torch.float32,device=env.device)  # Explicit deterministic tape, not a policy output.
        retained=WindowRetention(codec,snapshot,c2_ref);natural_ends=0;partial_candidates=0
        first_control=time.time()
        with torch.inference_mode():
            for index in range(task['controls']):
                if time.time()>=task['absolute_worker_deadline_epoch']:raise TimeoutError('Own original finite worker deadline')
                if (group/'GROUP_ABORT.json').exists():raise RuntimeError('Own group aborted')
                need(sensor.begin_control(index) is True,'typed control metadata begin failed before original step')
                boundary.for_action()
                state=bridge.step(zero)  # Original bridge -> exactly one original env.step; true terminal/pre-reset preserved.
                boundary.after_original_step(state.terminated,state.truncated)
                completed+=1
                pack=sensor.end_control(post_term=state.terminated,post_trunc=state.truncated,
                    source_ref=sensor.source_refs['bridge'],actor35=state.obs['policy'])
                need(type(pack) is dict,'typed control end metadata failed; original pending callback evidence retained')
                done_count=int((state.terminated|state.truncated).sum())  # Original returned flags, not SDK getters.
                natural_ends+=done_count;partial_candidates+=int(0<done_count<80)
                retained.add(index,actuation.drain(),clock=stored_clock(env))  # C2 own clones; event tick is not adoption clock.
        physics=int(env._integrated_contact.tick)-tick;feedback=int(env._feedback_100hz_tick)-fb
        actual_delay={key:env._physics_action_delay.calls[key]-delays[key] for key in ('legs','wheels')}
        guard.assert_new_nominals_unchanged();after=env._mild_dr.audit();assert after['actual_parameters_pass']
        sensor_report=sensor.finish()  # Outside-step only; a failed control never receives a synthetic end/finish.
        ledger_report=sensor_report.get('control_ledger')
        need(type(ledger_report) is dict and ledger_report.get('all_controls_observed') is True,
             'complete original bounded ledger result required for a successful FINAL')
        coverage=dict(expected_normal_channel_records=completed*10,
            retained_normal_channel_records=ledger_report['normal_channel_records'],
            all_controls_observed=ledger_report['all_controls_observed'],
            metadata_retention_complete=sensor_report['metadata_retention_complete'],
            per_row_episode_freshness='UNKNOWN_PENDING_TYPED_CONSUMER',
            scope='ORIGINAL_BOUNDED_METADATA_NOT_SDK_OR_RNG_OR_SKILL_QUALIFICATION',deficits=[])
        if not sensor_report['metadata_retention_complete']:coverage['deficits'].append('TYPED_METADATA_INCOMPLETE')
        coverage.update(natural_terminal_env_events=natural_ends,natural_partial_reset_candidate_controls=partial_candidates,
                        partial_reset_correctness='UNKNOWN_NEEDS_LIVE_VERIFIER',no_extra_reset_for_coverage=True)
        status=actuation.status()
        if status['dropped_events'] or status['observer_errors'] or status['missing_hooks']:
            coverage['deficits'].append('ACTUATION_CAPTURE_DROPPED_ERROR_OR_MISSING_HOOK')
        result=dict(completed=completed,physics=physics,feedback=feedback,delay_calls=actual_delay,boundary=boundary.receipt(),
                    sensor=sensor_report,actuation=dict(capture_schema=C2_CONTAINER,status=status,binding=act_binding,
                         C2_source_binding=c2_binding,stored_binding_before=stored_binding_before,
                         stored_binding_after=stored_actuation_evidence(env,codec,source_ref=adapter_ref),
                         static_before=static_before,static_after=typed_c2_memory(actuation.snapshot_static(),codec,snapshot,
                             source_ref=c2_ref,field='actuation.static_after',clock=stored_clock(env),role='ENV_ROWS_WITNESS'),
                         windows=retained.report(),middle_C2_windows='UNKNOWN_UNRETAINED',
                         source_scope='ORIGINAL_C2_LABEL_PRESERVED_NOT_PHYSICAL_DOF_OR_PIPELINE_PROOF'),
                    coverage=coverage,rng_counts=dict(before=rng_before,after=stored_rng_counts(env)),
                    trace=dict(initial_sensor_memory=initial_sensor,initial_actor_original_buffer=initial_actor),
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
                put_json(out/'FINAL.json',codec.materialize(final))  # Only published materializer, after reverse restoration.
            elif sensor is not None and codec is not None:
                if actuation is not None and retained is not None:
                    events=actuation.drain()
                    if events:
                        pending_index=vars(sensor).get('_control_index')
                        retained.add(pending_index if type(pending_index) is int else max(0,completed-1),events,
                                     clock=stored_clock(env,phase='ERROR_OUTSIDE_CONTROL'))
                partial=incomplete_capture(task,sensor,actuation,retained,source_error='WORKER_ERROR_OR_NO_SUCCESS_RESULT')
                partial['restore']=restore
                put_json(out/'TYPED_CAPTURE_INCOMPLETE_V1.json',codec.materialize(partial))
        except BaseException:
            record_primary_error(out,role='E3',phase='capture_FINAL_export',error=traceback.format_exc())
            raise
        finally:
            close_original_eval_resources(env,None if ns is None else ns['app'],out,task)


if __name__=='__main__':main()
