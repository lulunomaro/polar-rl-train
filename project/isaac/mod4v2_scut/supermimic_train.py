"""Finite Newton/Fudan learned-model BPTT, launched only at a saved boundary."""
from dataclasses import asdict
from pathlib import Path
import argparse,gc,hashlib,json,os,random,signal,time,traceback
import numpy as np
import torch

from .config import CONTRACT_SHA,runner_config
from .newton_env import NewtonEnv
from .newton_checkpoint import FORMAT as PPO_FORMAT,restore_environment_streams
from .newton_train import put
from .supermimic_newton import load_sources,warmstarted_learner,NewtonSuperMimicBridge

FORMAT='MOD4V2_FUDAN_NEWTON_SUPERMIMIC_FULL_V1'


def decode(path,sha):
    with Path(path).open('rb')as stream:
        if hashlib.file_digest(stream,'sha256').hexdigest()!=sha:raise ValueError('Checkpoint SHA mismatch')
    return torch.load(path,map_location='cpu',weights_only=False)


def make_config(Config,small=False):
    return Config(iterations=1000000,buffer_steps=128 if small else 64,utd=.4,horizon=32,
        hist=10,goal_frames=10,wm_hidden=(128,128)if small else(512,512,512),
        policy_hidden=(128,64)if small else(512,256,128),
        critic_hidden=(64,32)if small else(256,128),
        wm_window=8,wm_batches=4,wm_batch=32 if small else 512,
        pi_batch=32 if small else 512,critic_epochs=1,critic_minibatches=4,
        warmup_steps=64,wm_only_iters=32,compile=False,amp='none',action_noise=.05,
        log_every=1,seed=9138)


def build(env,source,binding,log,small=False,residual_scale=None):
    from rsl_rl.runners import OnPolicyRunner
    Base,Config=load_sources(binding)
    from ctx_reward_learner import capture_rng,restore_rng
    runner=OnPolicyRunner(env,runner_config(),None,env.device)
    if source['format']==PPO_FORMAT:
        if source['reward_family']!='FUDAN_JUMP' or source['num_envs']!=env.num_envs:
            raise ValueError('Same Fudan task/environment count is required')
        teacher=runner.alg.actor
        teacher.load_state_dict(source['actor_state_dict'],strict=True)
        torch.set_rng_state(source['cpu_rng'].cpu())
        torch.cuda.set_rng_state_all([x.cpu()for x in source['cuda_rng']])
        random.setstate(source['python_rng']);np.random.set_state(source['numpy_rng'])
        restore_environment_streams(env,source,source['iter'])
        after_reset_rng=capture_rng()
        config=None
    elif source['format']==FORMAT:
        if source['contract_SHA']!=CONTRACT_SHA:raise ValueError('Physical contract changed')
        teacher=runner.alg.actor
        config=source['args']
    else:raise ValueError('Expected complete Newton PPO or SuperMimic checkpoint')
    # Only the actor is used as teacher. PPO rollout storage, critic and Adam
    # remain preserved at the source checkpoint, not duplicated on this GPU.
    del runner
    gc.collect();torch.cuda.empty_cache()
    cfg=make_config(Config,small)if config is None else Config(**config)
    bridge=NewtonSuperMimicBridge(env)
    cls=warmstarted_learner(Base,teacher)
    aux_hidden=source['context_reward_extension']['contract']['aux_hidden']if config else((64,64)if small else(256,256))
    learner=cls(bridge,cfg,log,backend='Newton/MuJoCo-Warp',
        aux_hidden=aux_hidden,aux_batch=cfg.wm_batch)
    if source['format']==FORMAT:learner.restore_full(source)
    else:restore_rng(after_reset_rng)
    learner.pi.residual_scale=float(source.get('policy_residual_scale',1.)if residual_scale is None else residual_scale)
    if not 0<learner.pi.residual_scale<=1:raise ValueError('Invalid residual scale')
    gc.collect();torch.cuda.empty_cache()
    return learner,bridge


def save(learner,path,source):
    payload=learner._checkpoint(True)
    payload.update(format=FORMAT,reward_family='FUDAN_JUMP',contract_SHA=CONTRACT_SHA,
        actor_dim=35,critic_dim=78,physics_backend='Newton/SolverMuJoCo/MuJoCo-Warp',
        source_PPO=source,source_PPO_optimizers_preserved_at_original_checkpoint=True,
        policy_residual_scale=learner.pi.residual_scale,
        new_BPTT_optimizers_not_PPO_resume=True)
    path=Path(path);tmp=path.with_name(path.name+'.partial')
    with tmp.open('wb')as stream:torch.save(payload,stream);stream.flush();os.fsync(stream.fileno())
    with tmp.open('rb')as stream:sha=hashlib.file_digest(stream,'sha256').hexdigest()
    os.replace(tmp,path)
    return dict(path=str(path),bytes=path.stat().st_size,SHA=sha,format=FORMAT,
        iteration=learner.iteration,counts=asdict(learner.counts))


def main():
    p=argparse.ArgumentParser()
    for key in ('package','components','reset-bank','job-root','resume','resume-SHA','binding'):
        p.add_argument('--'+key,required=True)
    p.add_argument('--num-envs',type=int,default=20000)
    p.add_argument('--save-deadline',type=float,required=True)
    p.add_argument('--small-test',action='store_true')
    p.add_argument('--max-updates',type=int)
    p.add_argument('--residual-scale',type=float)
    a=p.parse_args();job=Path(a.job_root);job.mkdir(exist_ok=False)
    env=bridge=learner=None;error=None;final_saved=False
    try:
        random.seed(9138);np.random.seed(9138);torch.manual_seed(9138);torch.cuda.manual_seed_all(9138)
        source=decode(a.resume,a.resume_SHA)
        source_ref=source.get('source_PPO',dict(path=a.resume,SHA=a.resume_SHA,
            iteration=source.get('iter'),bytes=Path(a.resume).stat().st_size))
        env=NewtonEnv(a.package,a.components,a.reset_bank,a.num_envs,'cuda:0',9138)
        learner,bridge=build(env,source,a.binding,job/'learner',a.small_test,a.residual_scale)
        initial=learner.iteration;initial_counts=asdict(learner.counts)
        if source['format']==FORMAT:
            assert initial==source['iteration']
            assert initial_counts==source['context_reward_extension']['counts']
            put(job/'FULL_STATE_RESTORE.json',dict(epoch=time.time(),source_path=a.resume,
                source_SHA=a.resume_SHA,source_iteration=initial,counts=initial_counts,
                all4_optimizers_replay_RNG_7components_restored=True,
                source_replay_shape=[learner.buffer.T,learner.buffer.N],
                source_replay_size=learner.buffer.size,source_replay_ptr=learner.buffer.ptr,
                teacher_actor_and_learned_models_restored=True,
                source_policy_residual_scale=source.get('policy_residual_scale',1.),
                target_policy_residual_scale=learner.pi.residual_scale,
                fresh_physical_reset=True,exact_solver_state_restored=False))
        del source
        memory=sum(x.numel()*x.element_size()for x in learner.buffer.data.values())
        put(job/'STARTUP.json',dict(epoch=time.time(),backend='Newton/MuJoCo-Warp',
            learner='SuperMimic learned dynamics/context/reward H32 BPTT',
            reward_family='FUDAN_JUMP',source_PPO=source_ref,model=env.plant.receipt,
            config=asdict(learner.cfg),replay_bytes=memory,
            policy_residual_scale=learner.pi.residual_scale,
            replay_storage_device=str(learner.buffer.device),
            replay_sample_device=str(learner.buffer.sample_device),
            torch_allocated_bytes=torch.cuda.memory_allocated(),
            torch_reserved_bytes=torch.cuda.memory_reserved(),
            CUDA_memory_free_total=list(torch.cuda.mem_get_info()),
            original_PPO_complete_checkpoint_untouched=True,numerical_invalid_replay_excluded=True,
            physical_reset_resume=True,exact_solver_state_resume=False))
        stop=[False];signal.signal(signal.SIGTERM,lambda*args:stop.__setitem__(0,True))
        max_round=0.;first_saved=False;fraction=learner.collect_fraction
        required=max(learner.cfg.hist,learner.cfg.wm_window,learner.cfg.warmup_steps)
        while learner.buffer.size<required and time.time()+30<a.save_deadline and not stop[0]:learner.collect(1)
        while learner.buffer.size>=required:
            if stop[0]or(job.parent/'STOP_AFTER_SAVE.json').exists()or time.time()+max(30.,2*max_round)>=a.save_deadline:break
            start=time.time()
            for optimizer in (learner.opt_wm,learner.opt_pi,learner.opt_v,learner.opt_aux):
                for group in optimizer.param_groups:group['lr']=learner.lr_at(learner.iteration)
            fraction+=1/learner.cfg.utd;steps=int(fraction);fraction-=steps
            learner.collect(steps);collection=time.time()-start
            losses=[]
            for _ in range(learner.cfg.wm_batches):
                loss,error8=learner.wm_update();losses.append((float(loss),float(error8)))
            if learner.iteration>=learner.cfg.wm_only_iters:learner.policy_update()
            learner.iteration+=1;learner.collect_fraction=fraction
            seconds=time.time()-start;learner.wall_time+=seconds;max_round=max(max_round,seconds)
            progress=dict(epoch=time.time(),iteration=learner.iteration,
                controls=bridge.controls,sim_steps=learner.sim_steps,
                collection_seconds=collection,iteration_seconds=seconds,
                counts=asdict(learner.counts),wm_losses=losses,auxiliary=learner.last_aux,
                new_verified_BPTT_steps=learner.counts.pi_bptt_optimizer_steps-initial_counts['pi_bptt_optimizer_steps'],
                bptt=learner.last_bptt_receipt,numerical_resets=int(env.numerical_reset_counts.sum()),
                constraint_resets=int(env.constraint_reset_counts.sum()),
                solver_overflow_world_masks=env.solver_overflow_summary())
            put(job/'LATEST_PROGRESS.json',progress)
            if (not first_saved and learner.last_bptt_receipt.get('verified_bptt_optimizer_step')
                    and learner.counts.pi_bptt_optimizer_steps>initial_counts['pi_bptt_optimizer_steps']):
                ck=save(learner,job/'model_first_complete.pt',source_ref)
                put(job/'FIRST_UPDATED.json',dict(**progress,full_save=True,checkpoint=ck,
                    actual_native=True,horizon=32,verified_BPTT=True))
                first_saved=True
            if a.max_updates and learner.iteration-initial>=a.max_updates:break
        ck=save(learner,job/'model_final.pt',source_ref);final_saved=True
        put(job/'FINAL.json',dict(epoch=time.time(),passed_execution=True,checkpoint=ck,
            verified_BPTT_steps=learner.counts.pi_bptt_optimizer_steps,
            numerical_resets=int(env.numerical_reset_counts.sum()),
            constraint_resets=int(env.constraint_reset_counts.sum()),
            jump200_completed=env.completed_strict))
    except BaseException:
        error=traceback.format_exc();put(job/'ERROR.json',dict(epoch=time.time(),error=error));raise
    finally:
        if learner is not None and not final_saved:
            save(learner,job/'model_interrupted.pt',source_ref)
        if bridge is not None:bridge.close()
        if env is not None:env.close()
        put(job/'APP_CLOSE_INTENT.json',dict(epoch=time.time(),error=error,
            env_closed=env is not None,final_exists=final_saved))


if __name__=='__main__':main()
