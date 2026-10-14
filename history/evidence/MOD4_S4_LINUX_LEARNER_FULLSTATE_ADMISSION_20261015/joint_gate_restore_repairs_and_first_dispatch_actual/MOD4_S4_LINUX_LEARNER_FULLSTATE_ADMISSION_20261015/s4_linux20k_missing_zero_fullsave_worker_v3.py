"""Only missing zero-control fullsave and own restore; native120 is never replayed."""
from pathlib import Path
import os,sys,json,hashlib,runpy,copy,time,traceback

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    root=Path(__file__).resolve().parent
    manifest=json.loads((root/'S4_OWN_GPU_INTEGRATION_MANIFEST.json').read_bytes())
    assert manifest['approved_GPU_integration_only'] is True and manifest['approved_PPO'] is False
    assert manifest['parent_pid']==os.getppid() and manifest['source_sha256']==sha(manifest['source_path'])
    assert manifest['phase'] in ('own_first_fullsave0_healthschema','own_fullrestore0_healthschema')
    for name,h in manifest['sourcefreeze'].items():
        p=root/name;assert p.resolve().is_relative_to(root.resolve()) and sha(p)==h
    runtime=root/'isaac/mod4';sys.path[:0]=[str(root),str(runtime)]
    # Preserve engine-before-torch import order and the already reviewed public
    # crash reporter launch setting; no installed SDK edits.
    from bodyframe_deferred_original_import_v1 import install,own_launcher
    install({'isaaclab.app':own_launcher})
    original=runtime/'train_e1_retention_episode_reviewed_resume_ppo.py'
    ns=runpy.run_path(str(original),run_name='s4_original_configuration_only')
    import torch
    from isaaclab_rl.rsl_rl import RslRlVecEnvWrapper,handle_deprecated_rsl_rl_cfg
    from importlib import metadata
    from rsl_rl.runners import OnPolicyRunner
    from s4_original_fullstate_migration_v1 import (migrate_first,gate_config,verify_original_restore,
        SharedControlState,install_owned_save,same)
    from retention_checkpoint_episode_reviewed import resume_e1_new_episode,install_e1_save_contract
    from e1_terrain_training_health import E1TerrainTrainingHealth,learning_health_pass
    folder=Path(ns['args'].log_root);folder.mkdir(parents=True,exist_ok=True)
    env=None;health=None
    try:
        env=ns['build_env']()
        imported={}
        for name in ('torch','isaaclab','isaacsim','rsl_rl'):
            module=sys.modules.get(name)
            imported[name]=dict(file=getattr(module,'__file__',None),version_attribute=str(getattr(module,'__version__',None)))
        (folder/'S4_ACTUAL_IMPORTED_MODULE_PATHS.json').write_text(json.dumps(dict(epoch=time.time(),modules=imported,distribution_metadata_is_not_loaded_Kit_build=True),indent=2))
        assert env.num_envs==20000 and env.cfg.seed==20260928 and env.cfg.sim.dt==.0025 and env.cfg.decimation==4
        health=E1TerrainTrainingHealth(env,folder)
        cfg=ns['runner_config']();vec=RslRlVecEnvWrapper(env,clip_actions=6.)
        cfg=handle_deprecated_rsl_rl_cfg(cfg,metadata.version('rsl-rl-lib')).to_dict()
        source=Path(manifest['source_path']);ck=torch.load(source,map_location='cpu',weights_only=False)
        own=manifest['phase']=='own_fullrestore0_healthschema'
        if own:
            assert ck['S4_native_integration_checkpoint_not_production_learning_source'] is True
            from types import SimpleNamespace
            cfg=gate_config(SimpleNamespace(cfg=cfg),manifest['expert_refs'])
        runner=OnPolicyRunner(vec,cfg,log_dir=str(folder),device='cuda:0')
        # Explicitly disabled writer for 0PPO saves, not a learn() logger change.
        runner.logger.writer=None
        runner.load(str(source))
        if own:
            runtime_state=SharedControlState(vec.get_observations())
            runtime_state.restore(ck['S4_shared_control_state'])
            disk=folder/'S4_PRE_RESET_OWN_STATE_ACTUAL_CUDA_DISK.pt'
            before=dict(algorithm=copy.deepcopy(runner.alg.save()),shared=runtime_state.save())
            torch.save(before,disk);roundtrip=torch.load(disk,map_location='cpu',weights_only=False)
            runner.alg.load(roundtrip['algorithm']);runtime_state.restore(roundtrip['shared'])
            assert same(before['algorithm'],runner.alg.save())
            assert torch.equal(runtime_state.previous.cpu(),ck['S4_shared_control_state']['previous'])
        # ALL old DR state restored before the original single fresh episode.
        old=resume_e1_new_episode(runner,env,str(source),str(folder))
        assert torch.equal(env._e1_episode.cpu(),ck['E1_terrain_state']['episode']+1)
        if own:
            receipts=verify_original_restore(folder,source)
            runtime_state=SharedControlState(vec.get_observations())
            assert (runtime_state.previous==0).all()
            proof=dict(epoch=time.time(),pid=os.getpid(),source_SHA=sha(source),passed=True,
                old_receipts=receipts,own_S4_gate_critic_optimizer_private_routing_CUDA_disk_exact_before_reset=True,
                sourceepisode_incremented_once=True,new_physical_episode_clears_shared_actual_action_history=True,
                new_gate_critic_optimizer_initialized_again=False,expert_STD_source_exact=runner.alg.actor.verify_frozen(),
                original_fivefamily_W35_integration_scope_only=True,new_supported_learning_exposure_not_admitted=True,
                no_PPO_updates=True,PhysX_exact_resume_claimed=False)
            (folder/'S4_OWN_FULLRESTORE_ACTUAL.json').write_text(json.dumps(proof,indent=2))
        else:
            runtime_state,proof=migrate_first(runner,env,str(source),str(folder),manifest['expert_refs'])
        install_e1_save_contract(runner,env)
        install_owned_save(runner,runtime_state,manifest['original_W35_source'],proof)
        before_actor=copy.deepcopy(runner.alg.actor.state_dict());before_critic=copy.deepcopy(runner.alg.critic.state_dict())
        before_optimizer=copy.deepcopy(runner.alg.optimizer.state_dict())
        processed={}
        process=env.action_manager.process_action
        def actual_process(action):
            result=process(action);processed['action']=env.action_manager.action.clone();return result
        env.action_manager.process_action=actual_process
        obs=runtime_state.cache.clone();controls=0  # New missing save scope, never replay native120
        for i in range(controls):
            with torch.inference_mode():
                runner.alg.actor(obs,stochastic_output=False)
                x=obs['policy'];low=(x[:,0].abs()>0)&(x[:,0].abs()<=.300001)&(x[:,1:3].abs().amax(-1)<=1e-6)
                z=low.long();action=runner.alg.actor.means[torch.arange(env.num_envs,device=env.device),z]
                runtime_state.begin(obs,z)
                next_obs,reward,dones,extras=vec.step(action)
                runtime_state.finish(processed['action'],action.clamp(-6,6),dones,next_obs)
                obs=next_obs
            assert env._e1_pre_reset_frame['independent_ground_error']<=1e-6
            assert env._rough_reward_query_tick==env._rough_termination_query_tick==int(env._sim_step_counter)
            assert env._e1_height_formula_error<=2e-6
            if (root/'STOP_AFTER_SAVE.json').exists():
                runner.save(str(folder/'S4_OWN_GUARD_RETAINED_NOT_COMPLETE.pt'))
                raise RuntimeError('Own integration guardian requested natural save-stop; full retained state saved')
            if (i+1)%24==0:
                (folder/'S4_PROGRESS_ACTUAL.json').write_text(json.dumps(dict(epoch=time.time(),controls=i+1,callbacks=(i+1)*4,PPO_updates=0)))
        assert same(before_actor,runner.alg.actor.state_dict()) and same(before_critic,runner.alg.critic.state_dict())
        assert same(before_optimizer,runner.alg.optimizer.state_dict()) and not runner.alg.optimizer.state
        # Save the complete live state before post-save reader assertions.
        out=folder/'S4_OWN_INTEGRATION_FULLSAVE.pt';runner.save(str(out))
        health.write();value=json.loads((folder/'CLOCK_TRAINING_HEALTH.json').read_bytes())
        assert controls==0 and value['control_steps']==0 and value['actual_physics_callbacks']==0
        from s4_zero_control_state_integrity_v1 import verify_zero_control_restore
        def tensor(v):return v.torch if hasattr(v,'torch') else v
        robot=env.scene['robot']
        finite=all(bool(torch.isfinite(tensor(v)).all()) for v in (robot.data.root_state_w,robot.data.joint_pos,robot.data.joint_vel))
        qerror=float((tensor(robot.data.joint_pos)-env._rescue_reset_q).abs().max())
        zero=verify_zero_control_restore(value,finite,qerror)
        (folder/'S4_ZERO_CONTROL_STATE_INTEGRITY_ACTUAL.json').write_text(json.dumps(zero,indent=2))
        env.write_retention_trace(folder)
        (folder/'S4_COMPLETE_ACTUAL.json').write_text(json.dumps(dict(epoch=time.time(),pid=os.getpid(),passed=True,
            phase=manifest['phase'],source_SHA=sha(source),controls=controls,callbacks=controls*4,PPO_updates=0,
            sourcefreeze_SHA=manifest['sourcefreeze_SHA'],own_checkpoint=str(out),own_checkpoint_SHA=sha(out),
            expert_STD_unchanged=True,gate_critic_optimizer_unchanged=True,
            gate_learning_admitted=False,original_fivefamily_integration_only=True,
            source_episode_plus_one=True,PhysX_exact_resume_claimed=False),indent=2))
    except Exception:
        (folder/'S4_ORIGINAL_ERROR.json').write_text(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),no_PPO_requested=True)),encoding='utf8')
        raise
    finally:
        if health:health.write()
        if env:env.close()
        ns['app'].close()

if __name__=='__main__':main()
