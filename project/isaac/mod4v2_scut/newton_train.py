"""Finite actual Newton/MuJoCo-Warp PPO training and complete checkpoint boundary."""
from pathlib import Path
import argparse
import json
import os
import random
import signal
import time
import traceback

import numpy as np
import torch
import warp as wp

from .config import runner_config
from .newton_env import NewtonEnv
from .newton_checkpoint import restore,save


def put(path,value):
    path=Path(path);tmp=path.with_name(path.name+'.partial')
    with tmp.open('w',encoding='utf8')as f:json.dump(value,f,indent=2);f.flush();os.fsync(f.fileno())
    os.replace(tmp,path)


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--package',required=True)
    p.add_argument('--components',required=True)
    p.add_argument('--reset-bank',required=True)
    p.add_argument('--job-root',required=True,type=Path)
    p.add_argument('--resume',required=True)
    p.add_argument('--resume-SHA',required=True)
    p.add_argument('--num-envs',type=int,default=20000)
    p.add_argument('--seed',type=int,default=66)
    p.add_argument('--save-deadline',type=float,required=True)
    a=p.parse_args();job=a.job_root;job.mkdir(exist_ok=False)
    env=runner=None;error=None;started=False
    try:
        random.seed(a.seed);np.random.seed(a.seed);torch.manual_seed(a.seed);torch.cuda.manual_seed_all(a.seed)
        from rsl_rl.runners import OnPolicyRunner
        env=NewtonEnv(a.package,a.components,a.reset_bank,a.num_envs,'cuda:0',a.seed)
        runner=OnPolicyRunner(env,runner_config(),str(job),'cuda:0')
        receipt=restore(runner,env,a.resume,a.resume_SHA)
        put(job/'FULL_STATE_RESTORE.json',dict(epoch=time.time(),**receipt))
        put(job/'STARTUP.json',dict(epoch=time.time(),num_envs=a.num_envs,physics_dt=.0025,
            feedback_hz=100,policy_hz=50,model=env.plant.receipt,recipe='FUDAN_JUMP16',
            actual_Newton_MuJoCo_Warp=True,PhysX=False,physics_assists=False,
            D0_D7='Original component math, native Newton parameter writes'))
        obs=env.get_observations();runner.alg.train_mode();runner.logger.init_logging_writer()
        first_iteration=runner.current_learning_iteration;max_time=0.;stop=[False]
        signal.signal(signal.SIGTERM,lambda *args:stop.__setitem__(0,True))
        grads=dict(steps=0,actor_norm=0.,critic_norm=0.)
        def gradient(*args):
            grads['steps']+=1
            for label,model in [('actor',runner.alg.actor),('critic',runner.alg.critic)]:
                values=[p.grad.detach().norm().square()for p in model.parameters()if p.grad is not None]
                grads[label+'_norm']=float(torch.stack(values).sum().sqrt())if values else 0.
        hook=runner.alg.optimizer.register_step_pre_hook(gradient)
        started=True
        for iteration in range(first_iteration,first_iteration+1000000):
            if stop[0]or(job.parent/'STOP_AFTER_SAVE.json').exists()or time.time()+max(30.,2*max_time)>=a.save_deadline:break
            start=time.time();env.command.set_training_iteration(iteration)
            with torch.inference_mode():
                for control in range(24):
                    action=runner.alg.act(obs)
                    obs,reward,done,info=env.step(action)
                    assert all(bool(torch.isfinite(x).all())for x in obs.values())and bool(torch.isfinite(reward).all())
                    runner.alg.process_env_step(obs,reward,done,info)
                    runner.logger.process_env_step(reward,done,info,None)
                runner.alg.compute_returns(obs)
            collection=time.time()-start;learn=time.time()
            losses=runner.alg.update();runner.current_learning_iteration=iteration+1
            learning=time.time()-learn
            assert all(np.isfinite(float(x))for x in losses.values())
            runner.logger.log(it=iteration,start_it=first_iteration,total_it=first_iteration+1000000,
                collect_time=collection,learn_time=learning,loss_dict=losses,
                learning_rate=runner.alg.learning_rate,action_std=runner.alg.get_policy().output_std,rnd_weight=None)
            progress=dict(epoch=time.time(),iteration=iteration+1,physics_ticks=env.physics_ticks,
                collection_seconds=collection,learning_seconds=learning,
                samples_per_second=a.num_envs*24/(collection+learning),
                numerical_resets=int(env.numerical_reset_counts.sum()),
                solver_overflow_world_masks=env.solver_overflow_summary(),
                gradient=grads.copy(),jump200_completed=env.completed_strict,
                losses={k:float(v)for k,v in losses.items()})
            put(job/'LATEST_PROGRESS.json',progress)
            if iteration==first_iteration:
                ck=save(runner,env,job/'model_first_complete.pt')
                assert grads['actor_norm'] > 0. and grads['critic_norm'] > 0.
                put(job/'FIRST_UPDATED.json',dict(**progress,actual_native=True,PPO_updates=1,
                    rollout_controls=24,actual_onpolicy_samples=a.num_envs*24,
                    full_save=True,checkpoint=ck,backend='Newton/MuJoCo-Warp'))
            max_time=max(max_time,time.time()-start)
        final=save(runner,env,job/'model_final.pt')
        put(job/'FINAL.json',dict(epoch=time.time(),passed_execution=True,checkpoint=final,
            PPO_updates=runner.current_learning_iteration-first_iteration,
            numerical_resets=int(env.numerical_reset_counts.sum()),
            solver_overflow_world_masks=env.solver_overflow_summary(),
            jump200_completed=env.completed_strict,episodes_completed=env.completed_episodes))
        started=False
    except BaseException:
        error=traceback.format_exc();put(job/'ERROR.json',dict(epoch=time.time(),error=error));raise
    finally:
        if started and runner is not None:save(runner,env,job/'model_interrupted.pt')
        if runner is not None:runner.logger.stop_logging_writer()
        if env is not None:env.close()
        put(job/'APP_CLOSE_INTENT.json',dict(epoch=time.time(),error=error,env_closed=env is not None,
                                           final_exists=(job/'FINAL.json').exists()))


if __name__=='__main__':main()
