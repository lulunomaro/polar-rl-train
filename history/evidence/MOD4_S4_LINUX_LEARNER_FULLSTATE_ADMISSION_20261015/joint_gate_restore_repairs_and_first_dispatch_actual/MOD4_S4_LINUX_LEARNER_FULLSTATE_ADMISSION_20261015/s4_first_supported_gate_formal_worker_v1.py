"""First approved bounded S4 gate trial; source-bound startup precedes learn()."""
from pathlib import Path
import sys,os,time,json,hashlib,copy,runpy,traceback
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    root=Path(__file__).resolve().parent
    m=json.loads((root/'S4_FIRST_FORMAL_ACTUAL_MANIFEST.json').read_bytes())
    assert m['approved_first_S4_gate_learning'] is True and m['max_learning_window_seconds']==2700
    assert m['parent_pid']==os.getppid() and sha(m['source_path'])==m['source_SHA']
    assert m['actual_native_prefix_and_zero_fullstate_closed_CPU_verified'] is True
    assert m['no_reinitialized_expert_STD_or_gate_from_source'] is True
    for name,h in m['sourcefreeze'].items():assert sha(root/name)==h
    runtime_path=root/'isaac/mod4';sys.path[:0]=[str(root),str(runtime_path)]
    from bodyframe_deferred_original_import_v1 import install,own_launcher
    install({'isaaclab.app':own_launcher})
    ns=runpy.run_path(str(runtime_path/'train_e1_retention_episode_reviewed_resume_ppo.py'),run_name='s4_original_configuration_only')
    import torch
    from types import SimpleNamespace
    from importlib import metadata
    from isaaclab_rl.rsl_rl import RslRlVecEnvWrapper,handle_deprecated_rsl_rl_cfg
    from rsl_rl.runners import OnPolicyRunner
    from s4_original_fullstate_migration_v1 import gate_config,SharedControlState,same,verify_original_restore
    from s4_supported_shared_feedback_adapter_v1 import SupportedSharedFeedback
    from s4_supported_rollout_storage_v1 import PROFILE,DOMAIN
    from retention_checkpoint_episode_reviewed import resume_e1_new_episode,install_e1_save_contract
    from e1_terrain_training_health import E1TerrainTrainingHealth,learning_health_pass
    folder=Path(ns['args'].log_root);folder.mkdir(parents=True,exist_ok=True)
    env=None;health=None;runner=None
    try:
        env=ns['build_env']();assert env.num_envs==20000 and env.cfg.seed==20260928 and env.cfg.sim.dt==.0025 and env.cfg.decimation==4
        health=E1TerrainTrainingHealth(env,folder)
        cfg=ns['runner_config']();vec=RslRlVecEnvWrapper(env,clip_actions=6.)
        adapter=SupportedSharedFeedback(vec,env)
        cfg=handle_deprecated_rsl_rl_cfg(cfg,metadata.version('rsl-rl-lib')).to_dict()
        cfg=gate_config(SimpleNamespace(cfg=cfg),m['expert_refs'])
        cfg['algorithm']['class_name']='s4_supported_rollout_storage_v1:SupportedDomainPPO'
        assert cfg['algorithm']['value_loss_coef']==2.0 and cfg['algorithm']['entropy_coef']==.005
        runner=OnPolicyRunner(vec,cfg,log_dir=str(folder),device='cuda:0')
        runner.logger.writer=None # Startup fullsave is valid before learn() creates a writer.
        source=Path(m['source_path']);ck=torch.load(source,map_location='cpu',weights_only=False)
        assert ck['S4_native_integration_checkpoint_not_production_learning_source'] is True
        assert ck['S4_shared_control_state']['completed_controls']==0
        assert not ck['optimizer_state_dict']['state']
        runner.alg.import_untrained_native_integration(ck)
        runner.current_learning_iteration=0
        old_shared=SharedControlState(vec.get_observations());old_shared.restore(ck['S4_shared_control_state'])
        before=copy.deepcopy(runner.alg.save())
        disk=folder/'S4_SOURCE_GATE_CRITIC_OPT_PRIVATE_CUDA_ROUNDTRIP.pt';torch.save(before,disk)
        runner.alg.load(torch.load(disk,map_location='cpu',weights_only=False));assert same(before,runner.alg.save())
        assert same(runner.alg.actor.state_dict(),ck['actor_state_dict']) and same(runner.alg.critic.state_dict(),ck['critic_state_dict'])
        assert same(runner.alg.optimizer.state_dict(),ck['optimizer_state_dict'])
        resume_e1_new_episode(runner,env,str(source),str(folder))
        receipts=verify_original_restore(folder,source)
        assert torch.equal(env._e1_episode.cpu(),ck['E1_terrain_state']['episode']+1)
        shared=SharedControlState(vec.get_observations());assert (shared.previous==0).all()
        shared_disk=folder/'S4_NEW_DECLARED_TRAINING_META_SHARED_CUDA_ROUNDTRIP.pt';torch.save(shared.save(),shared_disk)
        restored=torch.load(shared_disk,map_location='cpu',weights_only=False);shared.restore(restored)
        assert torch.equal(shared.cache[DOMAIN].cpu(),restored['cache'][DOMAIN])
        assert int(shared.cache[DOMAIN].sum())>=1000,'No supported-domain fallback'
        assert runner.alg.actor.verify_frozen() and not runner.alg.optimizer.state
        # Own actual CUDA private-stream next-draw disk test. Restore the stream
        # and counters afterwards; this is not a physical step or PPO update.
        actor=runner.alg.actor;owned=actor.owned_state();old_cpu=torch.get_rng_state().clone();old_cuda=[v.clone() for v in torch.cuda.get_rng_state_all()]
        private_disk=folder/'S4_PRIVATE_ROUTING_ACTUAL_CUDA_DISK.pt';torch.save(owned,private_disk)
        with torch.inference_mode():
            probe=actor(shared.cache,stochastic_output=True).clone();choice=actor.z.clone();logp=actor.get_output_log_prob(probe).clone()
            assert probe.shape==(20000,6) and torch.isfinite(probe).all() and torch.isfinite(logp).all()
            actor.restore_owned(torch.load(private_disk,map_location='cpu',weights_only=False))
            repeated=actor(shared.cache,stochastic_output=True)
            assert torch.equal(probe,repeated) and torch.equal(choice,actor.z)
            actor.restore_owned(owned)
        assert torch.equal(old_cpu,torch.get_rng_state()) and all(torch.equal(a,b) for a,b in zip(old_cuda,torch.cuda.get_rng_state_all()))
        torch.save(dict(sampled_z=choice,raw_action=probe,joint_logp=logp),folder/'S4_PRIVATE_CUDA_NEXT_DRAW_WITNESS.pt')
        adapter.bind(runner.alg,shared)
        from s4_owned_rollout_audit_v1 import install_rollout_audit
        install_rollout_audit(runner.alg,folder,m['source_SHA'])
        startup=dict(epoch=time.time(),pid=os.getpid(),passed=True,source_SHA=sha(source),profile=PROFILE,
            original_eight_restore_receipts=receipts,source_episode_plus_one=True,
            source_gate_critic_optimizer_private_CUDA_roundtrip_exact=True,
            private_CUDA_sample_z_raw_joint_logp_next_draw_disk_exact=True,private_probe_no_physics_or_PPO_and_stream_restored=True,
            first_training_metadata_identity_explicit=True,same_original_physics_commands_DR_reward_clock=True,
            domain_label_not_deployment_input_or_expert_choice=True,only_full24_and_supported_bootstrap_gradient_samples=True,
            native120_original_scope_SAVE_failed_but_actual_physical_prefix_independently_reviewed=True,
            zero_control_fullsave_and_own_restore_closed=True,actual_initial_supported_rows=int(shared.cache[DOMAIN].sum()),
            no_new_gate_critic_optimizer_or_expert_STD_initialization=True,
            new_learning_not_same_expert_optimizer_resume=True,PhysX_exact_resume_claimed=False,
            sourcefreeze_SHA=m['sourcefreeze_SHA'],sole_parent_budget_segment=m['canonical_segment_kind'])
        start_path=folder/'S4_LEARNING_STARTUP_ADMITTED_ACTUAL.json';start_path.write_text(json.dumps(startup,indent=2))
        install_e1_save_contract(runner,env)
        oldsave=runner.save
        def save(path,*a,**kw):
            oldsave(path,*a,**kw);value=torch.load(path,map_location='cpu',weights_only=False)
            value['S4_shared_control_state']=shared.save()
            value['S4_original_W35_source_SHA']=m['expert_refs'][1]['sha256']
            value['S4_GPU_learning_admitted']=True
            value['S4_native_integration_checkpoint_not_production_learning_source']=False
            value['S4_learning_actual_startup_SHA']=sha(start_path)
            value['S4_first_formal_source_SHA']=m['source_SHA']
            value['S4_first_formal_scope']=PROFILE
            index=folder/'S4_GATE_FULL_ROLLOUT_INDEX_ACTUAL.json'
            value['S4_full_rollout_audit_index_SHA']=sha(index) if index.exists() else None
            torch.save(value,path)
        runner.save=save
        # Durable own initial fullsave before possible first-update failure.
        initial=folder/'S4_OWN_STARTUP0_FULLSAVE.pt';runner.save(str(initial))
        import rescue_training
        rescue_training.install(runner,str(folder))
        log=runner.logger.log
        def current_update_stop(*a,**kw):
            result=log(*a,**kw)
            if Path(os.environ['RM_RESCUE_STOP_FILE']).exists():runner.save(str(folder/f'model_{runner.current_learning_iteration}.pt'))
            return result
        runner.logger.log=current_update_stop
        try:runner.learn(num_learning_iterations=10000,init_at_random_ep_len=True)
        except rescue_training.SavedStop as stop:print('[S4 own fullsave-stop] '+str(stop),flush=True)
        health.write();h=json.loads((folder/'CLOCK_TRAINING_HEALTH.json').read_bytes())
        assert learning_health_pass(h) and h['stop_reason'] is None
        latest=json.loads((folder/'latest_complete.json').read_bytes());final=Path(latest['checkpoint'])
        actual=torch.load(final,map_location='cpu',weights_only=False)
        assert actual['S4_shared_control_state']['completed_controls']==h['control_steps']
        assert actual['S4_owned_learning']['actor_owned']['rollout_samples']==h['control_steps']*20000
        changed=sum(not torch.equal(v,ck['actor_state_dict'][k]) for k,v in actual['actor_state_dict'].items())
        critic_changed=sum(not torch.equal(v,ck['critic_state_dict'][k]) for k,v in actual['critic_state_dict'].items())
        steps=[float(v['step']) for v in actual['optimizer_state_dict']['state'].values()]
        assert changed>0 and critic_changed>0 and len(steps)==14 and len(set(steps))==1 and steps[0]>0
        result=dict(epoch=time.time(),pid=os.getpid(),passed=True,own_checkpoint=str(final),own_checkpoint_SHA=sha(final),
            complete_controls=h['control_steps'],callbacks=h['actual_physics_callbacks'],updates=int(steps[0]/20),
            gate_changed_tensor_count=changed,critic_changed_tensor_count=critic_changed,new_optimizer_parameter_states=14,
            all_new_Adam_step=steps[0],source_SHA=m['source_SHA'],sourcefreeze_SHA=m['sourcefreeze_SHA'],
            first_bounded_gate_learning_only_not_MoE_qualification=True,frozen_comparison_and_trace_review_next=True)
        (folder/'S4_FORMAL_FINAL_ACTUAL.json').write_text(json.dumps(result,indent=2))
    except Exception:
        (folder/'S4_FORMAL_ORIGINAL_ERROR.json').write_text(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),future_gpu_pass_not_inferred=True)),encoding='utf8');raise
    finally:
        if health:health.write()
        if env:env.close()
        ns['app'].close()
if __name__=='__main__':main()
