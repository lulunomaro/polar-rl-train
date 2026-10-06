"""Frozen 20k collection timing only; no PPO updates or production mutation."""
import argparse,os,json,sys,time
from pathlib import Path
M=Path('/home/egde/rl_candidates/MOD4_ROUGH_INTRO_GENTLE_REVIEW_20261006')
for k,v in json.loads((M/'isaac/mod4/env.json').read_text()).items():os.environ[k]=str(v)
sys.path.insert(0,str(M/'isaac/mod4'));sys.path.insert(0,str(M))
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True)
from isaaclab.app import AppLauncher
AppLauncher.add_app_launcher_args(p);args=p.parse_args();app=AppLauncher(args).app
import torch
from importlib import metadata
import mod4_task as task, rough_intro_runtime as runtime
from isaaclab_rl.rsl_rl import RslRlOnPolicyRunnerCfg,RslRlPpoActorCriticCfg,RslRlPpoAlgorithmCfg,RslRlVecEnvWrapper,handle_deprecated_rsl_rl_cfg
from rsl_rl.runners import OnPolicyRunner
timings={};events={};reset_counts=[]
def timed(name,fn):
    def call(*a,**k):
        start=torch.cuda.Event(enable_timing=True);end=torch.cuda.Event(enable_timing=True)
        start.record();t=time.perf_counter()
        value=fn(*a,**k)
        timings.setdefault(name,[]).append(time.perf_counter()-t);end.record()
        events.setdefault(name,[]).append((start,end))
        if name=='full_reset':reset_counts.append(int(len(a[1])) if a[1] is not None else a[0].num_envs)
        return value
    return call
@torch.inference_mode()
def run():
    source=Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/logs/2026-10-06_05-04-08_auto_0282_physical_dr_stage1_learning_cap12.5664_white_v3/model_23509.pt')
    assert __import__('hashlib').sha256(source.read_bytes()).hexdigest()=='2f82374fe07a849dbbaeabbf8dd34b20d0df8da789f2ebc2be3e688a1b24498a'
    runtime.refresh_ground=timed('refresh_ground',runtime.refresh_ground)
    cfg=task.Mod4EnvCfg();cfg.scene.num_envs=20000;cfg.seed=20260928
    recipe=runtime.configure_intro(cfg);cfg.events.consistent_start.func=timed('full_reset',cfg.events.consistent_start.func)
    env=runtime.RoughIntroEnv(cfg=cfg);vec=RslRlVecEnvWrapper(env,clip_actions=6.)
    rc=RslRlOnPolicyRunnerCfg(seed=cfg.seed,device=env.device,num_steps_per_env=24,max_iterations=1,save_interval=1,experiment_name='frozen_cost',run_name='diagnostic',clip_actions=6.,check_for_nan=True,obs_groups={'actor':['policy'],'critic':['critic']},policy=RslRlPpoActorCriticCfg(init_noise_std=.3,actor_hidden_dims=[256,128,64],critic_hidden_dims=[256,128,64],activation='elu'),algorithm=RslRlPpoAlgorithmCfg(value_loss_coef=2.,use_clipped_value_loss=True,clip_param=.2,entropy_coef=.005,num_learning_epochs=5,num_mini_batches=4,learning_rate=1e-4,schedule='adaptive',gamma=.99,lam=.95,desired_kl=.01,max_grad_norm=1.))
    rc=handle_deprecated_rsl_rl_cfg(rc,metadata.version('rsl-rl-lib'))
    runner=OnPolicyRunner(vec,rc.to_dict(),log_dir=None,device=env.device);runner.load(str(source));policy=runner.get_inference_policy(device=env.device)
    env.reset();env.sim.forward();env.scene.update(env.physics_dt);torch.cuda.synchronize()
    initial={k:sum(v) for k,v in timings.items()};timings.clear();events.clear();reset_counts.clear()
    env.episode_length_buf=torch.randint_like(env.episode_length_buf,high=int(env.max_episode_length))
    env.sim.step=timed('physics_step',env.sim.step)
    # Use fresh actual observations and exact loaded policy. This is a cost probe,
    # not an uncharged PPO preflight and not a replacement skill acceptance.
    rows=[];terminations=0;nonfinite=False;started=time.perf_counter()
    for i in range(96):
        t=time.perf_counter();action=policy(vec.get_observations());_,reward,done,_=vec.step(action);torch.cuda.synchronize()
        rows.append(time.perf_counter()-t);terminations+=int(env.termination_manager.terminated.sum())
        nonfinite|=not bool(torch.isfinite(reward).all() and torch.isfinite(action).all())
        if i%24==23:print(json.dumps(dict(control=i+1,wall=sum(rows),actual_task_failures=terminations)),flush=True)
    torch.cuda.synchronize()
    result=dict(ppo_performed=False,source=str(source),num_envs=env.num_envs,steps=96,seed=cfg.seed,recipe=recipe,wall_s=time.perf_counter()-started,control_seconds=rows,cpu_wall_s={k:sum(v) for k,v in timings.items()},cuda_event_s={k:sum(a.elapsed_time(b) for a,b in pairs)/1000 for k,pairs in events.items()},calls={k:len(v) for k,v in timings.items()},reset_counts=reset_counts,initial_reset_cpu_s=initial,actual_task_failures=terminations,nonfinite=nonfinite,geometry=runtime.query(env).geometry.receipt(),exact_partition=env.scene.terrain.exact_partition_receipt,extra_outer_control_sync_for_diagnostic=True,not_a_throughput_acceptance=True)
    args.output.write_text(json.dumps(result,indent=2));env.close();print(json.dumps({k:result[k] for k in ('wall_s','cpu_wall_s','cuda_event_s','calls','actual_task_failures')}),flush=True)
try:run()
except BaseException as e:
    import traceback
    args.output.with_suffix('.error.json').write_text(json.dumps(dict(error=repr(e),traceback=traceback.format_exc(),ppo_performed=False)));raise
finally:app.close()
