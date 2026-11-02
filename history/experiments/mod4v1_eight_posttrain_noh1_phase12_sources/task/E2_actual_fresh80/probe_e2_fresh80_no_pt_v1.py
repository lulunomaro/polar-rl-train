"""E2 original flat133/filter74 fresh80 D0-D7, one explicit fresh reset, no PT.
Does NOT call trainer.main, source cache, runner, policy, optimizer or saved restore.
"""
from pathlib import Path
import argparse,json,os,runpy,sys,time,traceback


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--task',type=Path,required=True);a=parser.parse_args()
    task=json.loads(a.task.read_bytes());out=a.task.parent;job=Path(task['runtime_job'])
    def put(name,value):
        with (out/name).open('x',encoding='utf-8') as f:json.dump(value,f,indent=2,allow_nan=False)
    assert task['kind']=='MOD4V1_E2_FRESH80_D0_D7_NO_PT'
    assert task['num_envs']==80 and task['controls']==24 and task['parent_limit_s']==720
    assert os.environ['CUDA_VISIBLE_DEVICES']==task['GPU_UUID']
    original=json.loads((job/'original_run_manifest.json').read_bytes())
    assert original['terrain']=='flat' and original['skill_tasks']=='all'
    assert original['env']['RM_JUMP_SCRIPT_PROB']=='0' and original['env']['RM_MOD4_TERRAIN']=='flat'
    for k in list(os.environ):
        if k.startswith('RM_') or k in ('RANK','WORLD_SIZE','LOCAL_RANK','MASTER_ADDR','MASTER_PORT'):del os.environ[k]
    os.environ.update({k:str(v) for k,v in original['env'].items() if k not in ('RM_RESCUE_STOP_FILE','RM_RESCUE_DEADLINE')})
    os.environ.update(RM_MOD4_USD=str(job/'runtime/assets/robot.usd'),MOD4V1_E2_ASSET_DIR=str(job/'runtime/assets'),MOD4V1_E2_JOB_ROOT=str(job),MOD4_RESUME_QUEUE_CONTROL_US='20000')
    os.environ.update(OWN_E2_H1_KIND='E2_WORLD_MOVING_SIGNED4',RM_SPAWN_GRACE_STEPS='5',RM_JUMP_SCRIPT_PROB='0',RM_MOD4_MAP='',RM_MOD4_TERRAIN='flat')
    storage=job/'kit_isolation';storage.mkdir(exist_ok=False);(storage/'data').mkdir();(storage/'DerivedDataCache').mkdir();(storage/'data/user.config.json').write_text('{}');os.environ['MOD4V1_E2_KIT_STORAGE_ROOT']=str(storage)
    mod=job/'runtime/isaac/mod4';sys.path[:0]=[str(mod),str(job/'runtime'),str(job/'lib')]
    entry=mod/'train_mod4v1_e2.py';sys.argv=[str(entry),'--headless','--device','cuda:0','--num_envs','80','--seed','20260928','--dry_run','24']
    ns=env=None;load_calls=0
    try:
        import torch
        def no_checkpoint_load(*args,**kwargs):
            nonlocal load_calls
            load_calls+=1
            raise RuntimeError('E2 fresh80 explicitly forbids every torch.load call')
        torch.load=no_checkpoint_load
        ns=runpy.run_path(str(entry),run_name='e2_fresh80_no_model_no_main')
        from mild_dr import tensor
        from mod4v1_fresh_dr_guard import FreshDRNominalGuard
        from actual_DR_memory_getter272 import RuntimeOrderBinding,ActualDRMemoryGetter
        env=ns['build_env']();robot=env.scene['robot'];identity=ns['E2_IDENTITY']
        term=env.command_manager.get_term('twist');assert type(term).__module__=='e2_directional_spin_runtime_v1' and term._dt==.02
        assert os.environ['OWN_E2_H1_KIND']=='E2_WORLD_MOVING_SIGNED4'
        guard=FreshDRNominalGuard(env,identity,torch_module=torch,tensor_converter=tensor)
        guard.assert_new_nominals_unchanged()
        env.reset()  # exactly ONE explicit NEW fresh reset, not a checkpoint resume
        guard.assert_new_nominals_unchanged()
        audit=env._mild_dr.audit();assert audit['actual_parameters_pass']
        bank=env._mod4v1_e2_bank_compatibility
        assert bank['pose_ranges']['all_poses']==133 and bank['pose_ranges']['original_height_filter_selected_poses']==74
        assert bank['new_contract_SHA']==identity.contract_sha256
        def names(key):
            ids=robot.actuators[key].joint_indices
            if isinstance(ids,slice):ids=list(range(len(robot.joint_names)))[ids]
            elif hasattr(ids,'tolist'):ids=ids.tolist()
            return tuple(robot.joint_names[i] for i in ids)
        binding=RuntimeOrderBinding(tuple(robot.body_names),tuple(robot.joint_names),names('legs'),names('wheels'),names('gas_springs'),int(env._mild_dr.materials.shape[1]))
        getter=ActualDRMemoryGetter(env,binding);getter.capture_initial()
        obs=env.observation_manager.compute();guard.check_observations(obs)
        assert env.num_envs==80 and env.physics_dt==.0025 and env.step_dt==.02 and env.cfg.decimation==8
        assert env.cfg.sim.physics is not None
        assert env.cfg.terminations.closure.params['threshold']==.01 and env.cfg.terminations.mimic.params['threshold']==.01
        tick=int(env._integrated_contact.tick);feedback=int(env._feedback_100hz_tick);calls=dict(env._physics_action_delay.calls)
        def small(value):
            value=value.detach()
            return dict(shape=list(value.shape),dtype=str(value.dtype),finite=bool(torch.isfinite(value).all()),min=float(value.min()),max=float(value.max()),first8=value.reshape(-1)[:8].cpu().tolist())
        put('E2_FRESH80_D0_D7_BEFORE_CONTROL.json',dict(scope='E2 fresh80 actual components; NOT20k saved-state restore/expert acceptance',asset_SHA=identity.usd_sha256,contract_SHA=identity.contract_sha256,audit=audit,bank_geometry_witness=bank,observations={k:list(v.shape) for k,v in obs.items()},actual_component_memory_not_independent_PhysX_qualification={k:small(v) for k,v in getter.cache.items()},actual_reset_counts={k:small(v) for k,v in getter.counts.items()},interface=[35,38,6],closure_m=.01,mimic_rad=.01,explicit_fresh_resets_after_build=1,source_checkpoint_restore=False,torch_load_calls=load_calls,model_opens=0,actor_calls=0,optimizer_updates=0))
        zeros=torch.zeros((80,6),device=env.device);finite=True;reasons={k:0 for k in env.termination_manager.active_terms}
        for _ in range(24):
            obs,reward,terminated,truncated,extra=env.step(zeros)
            finite=finite and all(bool(torch.isfinite(v).all()) for v in (obs['policy'],obs['critic'],reward))
            for key in reasons:reasons[key]+=int(env.termination_manager.get_term(key).sum())
        physics=int(env._integrated_contact.tick)-tick;fb=int(env._feedback_100hz_tick)-feedback
        delay={k:env._physics_action_delay.calls[k]-calls[k] for k in ('legs','wheels')}
        assert finite and physics==192 and fb==48 and delay=={'legs':192,'wheels':192}
        assert load_calls==0
        guard.assert_new_nominals_unchanged()
        audit_after=env._mild_dr.audit();assert audit_after['actual_parameters_pass']
        put('E2_FRESH80_NATIVE24_COMPLETE.json',dict(passed=True,scope='Original E2 WORLD_MOVING_SIGNED4 fresh80 noPT integration only',asset_SHA=identity.usd_sha256,contract_SHA=identity.contract_sha256,num_envs=80,controls=24,physics_callbacks=physics,feedback_samples=fb,action_delay_calls=delay,finite_policy_critic_reward=finite,actual_mild_DR_audit_after=audit_after,termination_events_by_reason=reasons,observed_max_closure_m=(float(env._mod4_max_closure) if hasattr(env,'_mod4_max_closure') else None),observed_max_mimic_rad=(float(env._mod4_max_mimic) if hasattr(env,'_mod4_max_mimic') else None),closure_is_single_env_episode_reset_not_global_peak_gate=True,D6_scope='original gas damping, not all joint friction',torch_load_calls=load_calls,model_opens=0,actor_calls=0,optimizer_updates=0,canonical_writes=0,full20k_saved_state_restore=False,expert_adaptation_or_skill_pass=False))
    except BaseException:
        put('E2_FRESH80_ORIGINAL_ERROR.json',dict(error=traceback.format_exc(),model_opens=0,torch_load_calls=load_calls,optimizer_updates=0));raise
    finally:
        try:
            if env is not None:env.close();put('ENV_CLOSE_RETURNED.json',dict(closed=True))
        finally:
            if ns is not None:put('APP_CLOSING.json',dict(calling_original_App_close=True));ns['app'].close()


if __name__=='__main__':main()
