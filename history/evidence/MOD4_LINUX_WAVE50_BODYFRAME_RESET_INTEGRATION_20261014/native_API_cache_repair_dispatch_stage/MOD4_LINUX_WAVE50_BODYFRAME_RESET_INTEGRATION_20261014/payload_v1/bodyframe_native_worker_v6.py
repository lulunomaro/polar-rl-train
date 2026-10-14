"""Prepared independent Linux native/fullrestore worker, zero PPO only.

Only an actual source-bound target manifest plus the original parent's held
lease/resource admission can run this worker. The CPU template always rejects.
Formal learning is deliberately outside this first native worker's modes.
"""
from pathlib import Path
import hashlib
import json
import os
import runpy
import sys
import time


def main():
    root = Path(__file__).resolve().parent
    sys.path.insert(0, str(root))
    from birth_bodyframe_full_checkpoint_v4 import guard_manifest, patch, same
    manifest_path = root / 'BODYFRAME_TARGET_ACTUAL_MANIFEST.json'
    manifest = json.loads(manifest_path.read_bytes())
    guard_manifest(manifest, fixture=False)
    assert manifest['mode'] in ('native144_0PPO', 'fullrestore120_0PPO')
    assert manifest['PPO_updates_authorized'] == 0
    assert manifest['actual_parent_pid'] == os.getppid()
    assert manifest['actual_target_root'] == str(root)
    freeze_path = root / manifest['sourcefreeze_relative_path']
    assert hashlib.sha256(freeze_path.read_bytes()).hexdigest() == manifest['sourcefreeze_SHA']
    freeze = json.loads(freeze_path.read_bytes())['sha256']
    assert len(freeze) >= 522
    for name, expected in freeze.items():
        path = root / name
        assert path.resolve().is_relative_to(root.resolve()) and path.is_file()
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected
    assert freeze[Path(__file__).name] == hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    runtime = root / 'isaac/mod4'
    sys.path.insert(0, str(runtime))
    import wave50_lifetime_full_checkpoint as original
    import left_sameidentity_typed13_receipts as typed
    def query(env):
        from wave50_entry_full_pose_reset_v2 import query as actual_query
        return actual_query(env)
    patch(original, manifest, typed, query, fixture=False)
    import rescue_training

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

    rescue_training.learn = native
    worker = runtime / 'train_wave50_lifetime_resume_ppo.py'
    sys.argv[0] = str(worker)
    runpy.run_path(str(worker), run_name='__main__')


if __name__ == '__main__':
    main()
