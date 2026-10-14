"""Owned zeroPPO worker: preserve original Kit-before-RL import order."""
from pathlib import Path
import hashlib,json,os,runpy,sys,time

def main():
    root=Path(__file__).resolve().parent;sys.path.insert(0,str(root));runtime=root/'isaac/mod4';sys.path.insert(0,str(runtime))
    manifest=json.loads((root/'BODYFRAME_TARGET_ACTUAL_MANIFEST.json').read_bytes())
    assert manifest['mode'] in ('native144_0PPO','fullrestore120_0PPO') and manifest['PPO_updates_authorized']==0
    assert manifest['actual_parent_pid']==os.getppid() and manifest['actual_target_root']==str(root)
    freeze=root/manifest['sourcefreeze_relative_path'];assert hashlib.sha256(freeze.read_bytes()).hexdigest()==manifest['sourcefreeze_SHA']
    for name,h in json.loads(freeze.read_bytes())['sha256'].items():
        q=root/name;assert q.is_file() and q.resolve().is_relative_to(root.resolve()) and hashlib.sha256(q.read_bytes()).hexdigest()==h
    from bodyframe_deferred_original_import_v1 import install,own_launcher
    same=None
    def checkpoint(module):
        nonlocal same
        from birth_bodyframe_full_checkpoint_v5 import guard_manifest,patch,same as actual_same
        import left_sameidentity_typed13_receipts as typed
        guard_manifest(manifest,False);same=actual_same
        def query(env):
            from wave50_entry_full_pose_reset_v2 import query as actual_query
            return actual_query(env)
        patch(module,manifest,typed,query,fixture=False)
    def native(runner, n, log_dir):
        import torch
        actor = {k: v.detach().clone() for k, v in runner.alg.actor.state_dict().items()}
        critic = {k: v.detach().clone() for k, v in runner.alg.critic.state_dict().items()}
        import copy
        optimizer = copy.deepcopy(runner.alg.optimizer.state_dict())
        runner.logger.init_logging_writer()
        obs = runner.env.get_observations()
        env = runner.env.unwrapped
        controls = 144 if manifest['mode'] == 'native144_0PPO' else 120
        for i in range(controls):
            with torch.inference_mode():
                action = runner.alg.actor(obs, stochastic_output=True)
                obs, _, _, _ = runner.env.step(action)
            assert env._rough_termination_query_tick == env._rough_reward_query_tick == int(env._sim_step_counter)
            assert env._e1_pre_reset_frame['independent_ground_error'] <= 1e-6
            assert env._e1_height_formula_error <= 2e-6
            env.command_manager.get_term('twist').audit_direction()
            if (i + 1) % 24 == 0:
                Path(log_dir, 'BODYFRAME_NATIVE_PROGRESS.json').write_text(json.dumps(dict(
                    epoch=time.time(), controls=i + 1, callbacks=(i + 1) * 4, PPO_updates=0,
                    bodyframe_audit=env.command_manager.get_term('twist').audit_direction())), encoding='utf8')
                assert not Path(os.environ['RM_RESCUE_STOP_FILE']).exists(), 'Own guardian requested natural stop'
        assert same(actor, runner.alg.actor.state_dict()) and same(critic, runner.alg.critic.state_dict())
        assert same(optimizer, runner.alg.optimizer.state_dict())
        target = Path(log_dir) / 'model_bodyframe_own0PPO.pt'
        runner.save(target)
        env.write_retention_trace(log_dir)
        Path(log_dir, 'BODYFRAME_OWN0PPO_COMPLETE.json').write_text(json.dumps(dict(
            epoch=time.time(), pid=os.getpid(), source_sha256=manifest['actual_source_SHA'],
            own_checkpoint=str(target), own_checkpoint_SHA=hashlib.sha256(target.read_bytes()).hexdigest(),
            controls=controls, callbacks=controls * 4, PPO_updates=0,
            actor_critic_std_optimizer_unchanged_during_own_probe=True,
            all_health_and_original_physical_contracts_require_independent_postexit_review=True,
            native_completion_NOT_qualification=True,
            qualified50=False, formal_learning_admitted=False), indent=2), encoding='utf8')
        runner.logger.writer.flush(); runner.logger.writer.close()

    def rescue(module):module.learn=native
    install({'isaaclab.app':own_launcher,'wave50_lifetime_full_checkpoint':checkpoint,'rescue_training':rescue})
    worker=runtime/'train_wave50_lifetime_resume_ppo.py';sys.argv[0]=str(worker);runpy.run_path(str(worker),run_name='__main__')

if __name__=='__main__':main()
