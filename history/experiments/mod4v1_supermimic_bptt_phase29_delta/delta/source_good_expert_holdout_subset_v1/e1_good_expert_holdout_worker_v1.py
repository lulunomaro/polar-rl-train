"""Two good-expert holdout E1 workers for oneparentheldGPU+finiteEX group. No importsSDK atmoduleload.
SOURCE_ONLY untilparentreview/freshactualgroupadmission; never createsGO/budget.
"""
from pathlib import Path
from types import SimpleNamespace
import argparse,ast,hashlib,json,os,sys,time,traceback
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from good_expert_holdout_runtime_v1 import KIND,put_json,wait_group_start,REQUESTED_ROLES,current_seed,POLICY_VARIANT
from good_expert_holdout_runtime_v1 import validate_group_task,A1CheckpointAdapter,configure_candidate_runtime,record_primary_error,close_original_eval_resources,INTEGRATION,paired_protocol_receipt,unresolved_evidence
from e1_fresh_runtime_bridge import HOLDER,attach_fresh_guard,fresh_full_dr_audit,build_cached_frozen_policy
from e1_endpoint_predicate import EndpointPredicate


def _configure_environment(task,case,meta):
    for k in list(os.environ):
        if k.startswith('RM_') or k in ('RANK','LOCAL_RANK','WORLD_SIZE','MASTER_ADDR','MASTER_PORT'):del os.environ[k]
    os.environ.update({k:str(v) for k,v in meta['original_env'].items() if k not in ('RM_RESCUE_DEADLINE','RM_RESCUE_STOP_FILE')})
    kit=case/'kit_isolation';kit.mkdir(exist_ok=False);(kit/'data').mkdir();(kit/'DerivedDataCache').mkdir();(kit/'data/user.config.json').write_text('{}')
    warp_cache=case/'warp_cache';warp_cache.mkdir(exist_ok=False)
    os.environ.update(RM_KEEP_STD='1',RM_PHYSICS_DT_S='.0025',RM_SOLVER_POS='32',RM_SOLVER_VEL='4',RM_MOD4_TERRAIN='flat',RM_MOD4_MAP='',RM_JUMP_SCRIPT_PROB='0',MOD4_RESUME_QUEUE_CONTROL_US='20000',MOD4V1_E1_ACTUAL_JOB_ROOT=str(case),MOD4V1_E1_KIT_STORAGE_ROOT=str(kit),PYTHONDONTWRITEBYTECODE='1',WARP_CACHE_PATH=str(warp_cache),WARP_CACHE_DIR=str(warp_cache),XDG_CACHE_HOME=str(case/'xdg_cache'))
    return kit,warp_cache




def _ready(task,case,bundle,cache,observer,primary):
    e=bundle['env'];cache.assert_entire_root_unchanged();before_reserved=cache.t.cuda.memory_reserved();cache.t.cuda.empty_cache();after_reserved=cache.t.cuda.memory_reserved()
    assert int(e._sim_step_counter)==0 and int(e._integrated_contact.tick)==0 and observer.actor_calls==0
    put_json(case/'WORKER_SCENE_READY.json',dict(seed=task['seed'],batch_purpose=task['batch_purpose'],policy_variant=POLICY_VARIANT,kind=KIND,role=task['role'],group_id=task['group_id'],GPU_UUID=task['GPU_UUID'],source_cache=cache.receipt(),actual_N80_fresh_fullDR_audit=bundle['audit_before'],actor_A1_whole_pi_and_norms_strict_frozen=True,actor_forward_calls=0,physics_steps=0,explicit_reset_count=1,primaryrefs=primary,kit_storage=str(case/'kit_isolation'),warp_storage=str(case/'warp_cache'),no_private_or_finite_lock_acquire=True,inherited_group_lock_fds_validated=task['actual_group_admission']['inherited_lock_fds'],saved20k_DR_physically_applied=False,waiting_group_start=True,torch_reserved_bytes_before_empty_cache=before_reserved,torch_reserved_bytes_after_empty_cache=after_reserved,resource_only_GPU_capacity_preset={k:getattr(e.cfg.sim.physics,k)for k in ('gpu_max_rigid_contact_count','gpu_max_rigid_patch_count','gpu_found_lost_pairs_capacity','gpu_found_lost_aggregate_pairs_capacity','gpu_total_aggregate_pairs_capacity')},capacity_overflow_in_closed_logs_disqualifies=True))


def _run_loop(task,case,bundle,cache,vec,policy,observer,torch,np,wp,tensor):
    from e1_terrain_training_health import declared_truncation_terms,ORDINARY_TERMS,INTEGRITY_TERMS,TRUNCATION_TERMS
    import mod4_task as plant
    e=bundle['env'];r=bundle['robot'];cmd=bundle['command'];cap=e._integrated_contact;steps=task['controls']
    decl=declared_truncation_terms(e.termination_manager);names=tuple(e.termination_manager.active_terms);phase={};forces=[]
    rows={k:[] for k in ('before_root','root','q','command','action','ground','normal','closure','mimic','episode','terminated','truncated','reasons','impulse','COM_link_pos','joint_vel','applied_torque')};HOLDER.update(loop_rows=rows,rawforces=forces)
    original_capture=cap.capture
    def capture(dt):
        original_capture(dt);raw=cap.sensor.contact_view.get_net_contact_forces(dt=cap.dt).view(wp.vec3);forces.append(wp.to_torch(raw).reshape(80,2,3).detach().cpu().numpy().copy())
    cap.capture=capture;oldterm=e.termination_manager.compute
    cpu=lambda x:tensor(x).detach().cpu().numpy().copy()
    def terminal(*a,**k):
        value=oldterm(*a,**k);tm=e.termination_manager
        phase.update(terminated=cpu(tm.terminated),truncated=cpu(tm.time_outs),reasons=np.stack([cpu(tm.get_term(n)) for n in names],axis=-1),impulse=cpu(cap.impulse),COM_link_pos=cpu(r.data.body_link_pos_w),joint_vel=cpu(r.data.joint_vel),applied_torque=cpu(r.data.applied_torque));return value
    e.termination_manager.compute=terminal
    episode=np.zeros(80,dtype=np.int64);starttick=int(e._sim_step_counter);startfb=int(e._feedback_100hz_tick);calls0=dict(e._physics_action_delay.calls);start=time.time();predicate=None
    if bundle['manual']:predicate=EndpointPredicate(.275 if task['role'].startswith('CURB') else 1.2)
    try:
        with torch.inference_mode():
            for i in range(steps):
                if time.time()>=task['absolute_worker_deadline_epoch']:raise TimeoutError('Groupfiniteownerdeadline, no independent retry')
                if bundle['manual']:
                    cmd.time_left[:]=1.e9;cmd.is_standing_env[:]=bundle['groups']==2
                    if hasattr(cmd,'is_heading_env'):cmd.is_heading_env[:]=False
                    cmd.is_pure_spin[:]=False;cmd.is_moving_spin[:]=False;cmd.is_transition_spin[:]=False;cmd.command[:]=0.;cmd.command[:,0]=bundle['targets'];plant.height_cmd(e)[:]=.25
                before=cpu(r.data.root_state_w);requested=cpu(cmd.command);obs=vec.get_observations();action=policy(obs);_,reward,done,extra=vec.step(action)
                frame=e._e1_pre_reset_frame
                ordinary=phase['reasons'][:,[names.index(n) for n in names if n in ORDINARY_TERMS]].any(-1)
                integrity=phase['reasons'][:,[names.index(n) for n in names if n in INTEGRITY_TERMS]].any(-1)
                unknown_names=[n for n in names if n not in ORDINARY_TERMS|INTEGRITY_TERMS|TRUNCATION_TERMS]
                unknown=phase['reasons'][:,[names.index(n) for n in unknown_names]].any(-1) if unknown_names else np.zeros(80,dtype=bool)
                trunc=phase['reasons'][:,[names.index(n) for n in TRUNCATION_TERMS]].any(-1)
                assert np.array_equal(phase['terminated'],ordinary|integrity|unknown) and np.array_equal(phase['truncated'],trunc)
                assert not integrity.any() and not unknown.any()
                assert e._rough_reward_query_tick==e._rough_termination_query_tick==int(e._sim_step_counter)
                assert len(forces)==(i+1)*8
                fz=np.maximum(np.stack(forces[-8:])[...,2],0);independent=fz.sum(0)*.0025
                assert float(np.max(abs(independent-phase['impulse'])))/.02<=.1  # Originalcontrolmean-load datacontract, notnewskillgate.
                v=dict(before_root=before,root=cpu(frame['root']),q=cpu(frame['q']),command=requested,action=cpu(action),ground=cpu(frame['ground']),normal=cpu(frame['normal']),closure=cpu(frame['closure']),mimic=cpu(frame['mimic']),episode=episode.copy(),**phase)
                assert all(np.isfinite(x).all() for x in v.values()) and torch.isfinite(reward).all()
                assert float(np.max(v['mimic']))<=.01
                if predicate is not None:
                    wi=[r.body_names.index(n) for n in ('left_wheel','right_wheel')];centers=np.asarray(bundle['route_scope']['tile_centers']);orientation=np.asarray(bundle['route_scope']['orientation'])
                    u=(phase['COM_link_pos'][:,wi,0]-centers[:,None,0])*orientation[:,None]
                    predicate.observe(i,episode.tolist(),u.tolist(),(independent/.02>1.).tolist(),phase['terminated'].tolist())
                for k,x in v.items():rows[k].append(x)
                episode+=phase['terminated']|phase['truncated']
        assert int(e._sim_step_counter)-starttick==steps*8 and int(e._feedback_100hz_tick)-startfb==steps*2
        assert {k:e._physics_action_delay.calls[k]-calls0[k] for k in ('legs','wheels')}==dict(legs=steps*8,wheels=steps*8)
        cache.assert_entire_root_unchanged()
        cache.check_actor(HOLDER['actor'])
        data={k:np.stack(v) for k,v in rows.items()};data['physical_wheel_force_N']=np.stack(forces);raw=case/'OWN_NEW_SKILL_RAW.npz';np.savez_compressed(raw,**data);rawbytes=raw.read_bytes()
        if predicate is not None:metrics=predicate.finish()
        else:
            roots=data['root'][:,:,:2];metrics=dict(kind='SLOPE50_DEFAULT_TRAINING_AXIS_DESCRIPTIVE_ONLY',accepted_original_cohort_rule_saved=False,all_environment_local_root_xy_min=roots.min(0).tolist(),all_environment_local_root_xy_max=roots.max(0).tolist(),per_environment_reason_counts=data['reasons'].sum(0).tolist(),original_fullramp_skill_graduation='UNKNOWN_NOT_CLAIMED',no_SLOPE135_predicate_or27_27_scope_borrowed=True)
        return dict(kind=KIND,num_envs=80,role=task['role'],group_id=task['group_id'],GPU_UUID=task['GPU_UUID'],passed_execution=True,controls=steps,physics=steps*8,feedback=steps*2,seconds=steps*.02,actor_calls=observer.actor_calls,source_cache=cache.receipt(),fresh_fullDR_before=bundle['audit_before'],fresh_fullDR_after=fresh_full_dr_audit(e,bundle['guard'],tensor),route_scope=bundle['route_scope'],metrics=metrics,reason_names=names,declared_timeouts=decl,termination_counts={n:int(data['reasons'][...,j].sum()) for j,n in enumerate(names)},raw=dict(path=str(raw),bytes=len(rawbytes),SHA=hashlib.sha256(rawbytes).hexdigest(),shape={k:list(v.shape) for k,v in data.items()}),wall_start_epoch=start,wall_end_epoch=time.time(),optimizer_updates=0,saved20k_DR_physically_applied=False,state_projection_or_slicing=False,whole20k_savedrestore_claim=False,cached_whole_A1_CPU_root_not_live_WM_critic_optimizer_restore=True,backend_independent_qualification=False,current_thresholds=dict(closure=.01,mimic=.01),no_new_aggregate_graduation_rate=True,integration=INTEGRATION,paired_reset_protocol=paired_protocol_receipt(),unresolved_evidence=unresolved_evidence(),Appclose_and_parent_wait_required=True)
    finally:
        e.termination_manager.compute=oldterm;cap.capture=original_capture


def main_role(role):
    assert role in REQUESTED_ROLES
    parser=argparse.ArgumentParser();parser.add_argument('--task',type=Path,required=True);parser.add_argument('--group-root',type=Path,required=True);cli=parser.parse_args()
    case=cli.task.resolve().parent;group=cli.group_root.resolve();stage='STARTUP';app=None;cache=None
    try:
        task=json.loads(cli.task.read_bytes());contracts=json.loads((Path(__file__).parent/'ROLE_CONTRACTS.json').read_bytes());validate_group_task(task,role,group,case,contracts);configure_candidate_runtime(task,case)
        runtime=Path(task['runtime_root']);mod=runtime/'runtime/isaac/mod4';meta=json.loads((runtime/'E1_CANONICAL_SOURCE_METADATA.json').read_bytes());assert meta['canonical']==role
        _configure_environment(task,case,meta);sys.path[:0]=[str(mod),str(runtime/'runtime')]
        from launcher_mod4v1_e1_actual import E1IsolatedAppLauncher as AppLauncher
        ap=argparse.ArgumentParser();AppLauncher.add_app_launcher_args(ap);app_args=ap.parse_args(['--headless','--device','cuda:0']);app=AppLauncher(app_args).app
        import numpy as np,torch,warp as wp
        # Oneuniqueperworker Warp cache beforeanyownterrainkernellaunch; environmentfallback kept.
        wp.config.kernel_cache_dir=str(case/'warp_cache')
        from mod4v1_fresh_dr_guard import bind_before_task_import,verify_task_module,configure_new_task
        identity=bind_before_task_import(Path(task['asset_dir']))
        import mod4_task
        verify_task_module(mod4_task,identity);assert mod4_task.POLICY_HZ==50 and mod4_task.DECIMATION==8
        from mild_dr import tensor
        cache=A1CheckpointAdapter(torch,task)
        def forbidden(*a,**k):raise RuntimeError('GroupN80skill screen forbids optimizer/PPO')
        torch.optim.Optimizer.step=forbidden;torch.optim.Adam.step=forbidden
        torch.manual_seed(current_seed())
        from e1_route80_factories import build_original_route80
        bundle=build_original_route80(role,task,case,identity,torch,np,wp,tensor)
        vec,policy,observer=build_cached_frozen_policy(bundle['env'],cache,torch,tensor)
        _ready(task,case,bundle,cache,observer,contracts[role]['primary_references']);stage='BARRIER'
        barrier=wait_group_start(task,group,maximum_seconds=900)
        assert int(bundle['env']._sim_step_counter)==0 and observer.actor_calls==0
        stage='EVAL';result=_run_loop(task,case,bundle,cache,vec,policy,observer,torch,np,wp,tensor);result.update(group_barrier=barrier,seed=task['seed'],holdout_protocol=task['holdout_protocol'],policy_variant=POLICY_VARIANT,evaluation_purpose=task['batch_purpose'],actor_semantics=task['actor_semantics'])
        bundle['env'].close();HOLDER['closed']=True;result['env_close_returned']=True;result['actual_parent_wait_RC0']='PARENT_TO_VERIFY_AFTER_APP_CLOSE'
        put_json(case/'FINAL.json',result);stage='COMPLETE'
    except BaseException:
        error=dict(kind=KIND,role=role,stage=stage,error=traceback.format_exc(),no_independent_retry=True,parent_must_cancel_entire_group_scope=True,saved20k_DR_physically_applied=False)
        record_primary_error(case,role=role,phase=stage,error=error['error'],cache=cache)
        if cache is not None:
            try:error['source_cache']=cache.receipt()
            except BaseException:error['source_cache_error']=traceback.format_exc()
        if 'np' in locals() and HOLDER.get('loop_rows'):
            data={k:np.stack(v) for k,v in HOLDER['loop_rows'].items() if v}
            if HOLDER.get('rawforces'):data['physical_wheel_force_N']=np.stack(HOLDER['rawforces'])
            if data:np.savez_compressed(case/'OWN_PARTIAL_SKILL_RAW.npz',**data)
        raise
    finally:
        close_original_eval_resources(HOLDER.get('env'),app,case,task,env_already_closed=HOLDER.get('closed',False))
