"""Independent branch wrapper. Original environment, RL worker and solver are unchanged."""
import os, sys, runpy, json, time
from pathlib import Path
R=Path(__file__).resolve().parent
worker=R/'isaac/mod4/train_wave50_lifetime_resume_ppo.py'
sys.path.insert(0,str(worker.parent))
import wave50_lifetime_full_checkpoint
from left_exploration_resume_contract_v1 import patch, same
patch(wave50_lifetime_full_checkpoint,R)
import rescue_training
original_install=rescue_training.install

def install(runner,log_dir):
    original_install(runner,log_dir)
    original_log=runner.logger.log
    def log(*a,**kw):
        original_log(*a,**kw)
        if Path(os.environ['RM_RESCUE_STOP_FILE']).exists():runner.save(str(Path(log_dir)/f'model_{runner.current_learning_iteration}.pt'))
    runner.logger.log=log
rescue_training.install=install

if os.environ.get('MOD4_LEFT_ADMISSION_MODE') in ('native0PPO','fresh0PPO'):
    def native(runner,n,log_dir):
        import torch
        from e1_terrain_training_health import learning_health_pass
        source_actor={k:x.detach().clone() for k,x in runner.alg.actor.state_dict().items()}
        source_optimizer=runner.alg.optimizer.state_dict()
        runner.logger.init_logging_writer()
        obs=runner.env.get_observations()
        # Explicit stochastic policy inference exercises the repaired exploration head.
        controls=0 if os.environ['MOD4_LEFT_ADMISSION_MODE']=='fresh0PPO' else 144
        for i in range(controls):
            with torch.inference_mode():
                action=runner.alg.actor(obs,stochastic_output=True)
                obs,_,_,_=runner.env.step(action)
            env=runner.env.unwrapped
            assert env._rough_termination_query_tick==env._rough_reward_query_tick==int(env._sim_step_counter)
            assert env._e1_pre_reset_frame['independent_ground_error']<=1e-6
            assert env._e1_height_formula_error<=2e-6
            if (i+1)%24==0:
                Path(log_dir,'NATIVE_PROGRESS.json').write_text(json.dumps(dict(epoch=time.time(),controls=i+1,callbacks=(i+1)*4,PPO_updates=0)))
                assert not Path(os.environ['RM_RESCUE_STOP_FILE']).exists(),'Own admission guardian requested natural stop'
        assert same(source_actor,runner.alg.actor.state_dict()) and same(source_optimizer,runner.alg.optimizer.state_dict())
        q=Path(log_dir)/'model_own_repaired0PPO.pt'
        runner.save(str(q))
        env.write_retention_trace(log_dir)
        Path(log_dir,'NATIVE_REPAIRED0PPO_COMPLETE.json').write_text(json.dumps(dict(epoch=time.time(),pid=os.getpid(),controls=controls,callbacks=controls*4,PPO_updates=0,actor_optimizer_unchanged_during_physics_probe=True,own_checkpoint=str(q),actual_ground_query_and_reward_tick_exact=True,original_source_oldfullrestore_then_explicit_left_initialization=True,health_must_be_reviewed_from_original_worker_finally=True,qualified50=False),indent=2))
        runner.logger.writer.flush()
        runner.logger.writer.close()
    rescue_training.learn=native
sys.argv[0]=str(worker)
runpy.run_path(str(worker),run_name='__main__')
