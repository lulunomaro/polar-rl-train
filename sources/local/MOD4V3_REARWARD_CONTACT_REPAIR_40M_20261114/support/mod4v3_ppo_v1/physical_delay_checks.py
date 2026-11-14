"""Timing probe and existing fixed-command tasks, using the training environment."""
from pathlib import Path
import math
import json
import torch
from tensordict import TensorDict
from mod4v1_scut.config import observation_component

TASKS = [
    ("forward_2.0", 2.0, 0.0, .28, .15, None),
    ("forward_2.2", 2.2, 0.0, .28, .15, None),
    ("backward_1.5", -1.5, 0.0, .28, .20, None),
    ("yaw_14.137", 0.0, 4.5*math.pi, .28, None, .02),
    ("height_0.20", 0.0, 0.0, .20, None, None),
    ("height_0.40", 0.0, 0.0, .40, None, None),
    ("combo_0.9_1.2", .9, 1.2, .28, None, None),
]


def _set_command(env,vx,wz,height):
    env.heading_env.zero_();env.standing_env.zero_();env.heading_target.zero_()
    env.command.zero_();env.command[:,0]=vx;env.command[:,2]=wz
    env.height.fill_(height);env.command_timer.fill_(10000.)
    env.reward.command.copy_(env.command);env.reward.height_cmd.copy_(env.height)


def _ground_start(env,seed):
    """Same reset bank and small initial perturbations; active DR is retained."""
    from .scut_flat_env import tensor
    from isaaclab.utils.math import quat_from_euler_xyz
    env.reset()
    n=env.num_envs;ids=torch.arange(n,device=env.device,dtype=torch.long)
    gen=torch.Generator(device=env.device).manual_seed(seed)
    pick=torch.randint(len(env._bank_h),(n,),device=env.device,generator=gen)
    q=env._bank_q[pick][:,env._bank_ids].clone()
    root=tensor(env.robot.data.default_root_state).clone()
    root[:,:3]+=env.scene.env_origins;root[:,2]=env.scene.env_origins[:,2]+env._bank_h[pick]
    def uniform(low,high):return torch.empty(n,device=env.device).uniform_(low,high,generator=gen)
    root[:,3:7]=quat_from_euler_xyz(uniform(-.01,.01),uniform(-.01,.01),uniform(-.05,.05))
    root[:,7:]=0.;root[:,7]=uniform(-.01,.01);root[:,12]=uniform(-.01,.01)
    env.robot.write_root_state_to_sim(root,env_ids=ids)
    env.robot.write_joint_state_to_sim(q,torch.zeros_like(q),env_ids=ids)
    env.actions.zero_();env.torque.zero_();env.episode_length_buf.zero_()
    env.zero_torque_remaining.zero_()
    env.reward.reset(ids);env.reward._invalidate_step_caches()
    env._execution_pending.fill_(True);env._sensor_pending.fill_(True)
    env._sensor_last_tick=-1
    env.scene.write_data_to_sim();env.scene.update(dt=0.)


def run_timing_probe(env):
    env._trace_enabled=True;env._delay_trace=[]
    _ground_start(env,6601);_set_command(env,0.,0.,.25)
    # Force a known 5-ms lag for instrumentation, independent of reset sampling.
    delay=round(.005/env._delay_dt)
    assert delay in env._action_options.tolist() and delay in env._sensor_options.tolist()
    env._action_delay_ticks.fill_(delay);env._sensor_delay_ticks.fill_(delay)
    before_a=env._action_sample_count;before_s=env._sensor_sample_count
    action_a=torch.zeros((env.num_envs,6),device=env.device)
    action_b=action_a.clone();action_b[:,4:]=.2
    records=[]
    with torch.inference_mode():
        for step,action in enumerate([action_a,action_b,action_a,action_b]):
            obs,_,term,timeout,_=env.step(action)
            expected=observation_component(env.reward.cfg,"actions",action,"policy")
            records.append(dict(step=step,action_slot_error=float((obs["policy"][:,22:28]-expected).abs().max()),
                                finite=all(bool(torch.isfinite(v).all()) for v in obs.values()),
                                terminated=int(term.sum()),timeout=int(timeout.sum())))
    assert all(r["action_slot_error"]<1e-6 and r["finite"] for r in records)
    assert env._action_sample_count-before_a==4*env.cfg.decimation
    assert env._sensor_sample_count-before_s in (4*env.cfg.decimation,4*env.cfg.decimation+1)
    trace=env._delay_trace
    changed=[i for i,row in enumerate(trace) if i and abs(row["issued"][4]-trace[i-1]["issued"][4])>.1]
    timings=[]
    for i in changed:
        value=trace[i]["issued"][4]
        buffer=next(row for row in trace[i:] if abs(row["executed"][4]-value)<1e-6)
        pd=next(row for row in trace[i:] if row["pd_refresh"] and abs(row["executed"][4]-value)<1e-6)
        timings.append(dict(issued_ms=trace[i]["time_ms"],buffer_latency_ms=buffer["time_ms"]-trace[i]["time_ms"],
                            pd_latency_ms=pd["time_ms"]-trace[i]["time_ms"]))
    assert timings and all(abs(t["buffer_latency_ms"]-5)<1e-6 and abs(t["pd_latency_ms"]-10)<1e-6 for t in timings)
    return dict(passed=True,num_envs=env.num_envs,delay=env.physical_delay_summary(),
                action_samples=env._action_sample_count-before_a,sensor_samples=env._sensor_sample_count-before_s,
                observations=records,timings=timings,trace=trace)


@torch.inference_mode()
def run_fixed_suite(env,algorithm,job):
    """10 envs/initial states by default; all active training DR remains on."""
    results=[];policy=algorithm.get_policy()
    for index,(name,vx,wz,height,vx_limit,wz_relative_limit) in enumerate(TASKS):
        _ground_start(env,6600+index);_set_command(env,vx,wz,height)
        reset_counts=torch.zeros(env.num_envs,device=env.device,dtype=torch.long)
        records=[];start_totals=dict(env.done_totals)
        with torch.inference_mode():
            obs=TensorDict(env._get_observations(),batch_size=[env.num_envs])
            for step in range(300):
                action=policy(obs,stochastic_output=False).clamp(-6,6)
                raw,_,term,timeout,_=env.step(action)
                reset_counts+=term.long()
                _set_command(env,vx,wz,height)
                obs=TensorDict(raw,batch_size=[env.num_envs])
                if step>=180:
                    records.append(torch.stack((env.view.data.root_lin_vel_b[:,0],
                        env.view.data.root_ang_vel_b[:,2],env._height_observation()),dim=-1).clone())
        values=torch.stack(records).mean(0)
        errors=(values-values.new_tensor([vx,wz,height])).abs()
        passed=reset_counts==0
        if vx_limit is not None:passed &= errors[:,0]<=vx_limit
        if wz_relative_limit is not None:passed &= errors[:,1]<=abs(wz)*wz_relative_limit
        if name.startswith("height"):passed &= errors[:,2]<=.02
        measured={"task":name,"command":[vx,0.,wz],"height_command":height,
                  "passed":int(passed.sum()),"requested":env.num_envs,
                  "capability_gate":name!="combo_0.9_1.2",
                  "mean":values.mean(0).tolist(),"mean_abs_error":errors.mean(0).tolist(),
                  "max_abs_error":errors.max(0).values.tolist(),
                  "per_env":[dict(env=i,mean=values[i].tolist(),abs_error=errors[i].tolist(),
                                  resets=int(reset_counts[i]),passed=bool(passed[i])) for i in range(env.num_envs)],
                  "done_delta":{k:env.done_totals[k]-v for k,v in start_totals.items()}}
        results.append(measured)
        target=Path(job)/"FIXED_SUITE_PROGRESS.json"
        target.write_text(json.dumps(dict(results=results),ensure_ascii=False,indent=2),encoding="utf-8")
    gates=[row for row in results if row["capability_gate"]]
    return dict(passed=all(row["passed"]==row["requested"] for row in gates),num_envs=env.num_envs,
                physics="PhysX",active_dr=env.mild_dr.summary(),results=results,
                meaning="Capability retention under active sampled DR, not a full statistical coverage claim")


@torch.inference_mode()
def run_parallel_fixed_suite(env,algorithm,job):
    """Seven tasks in parallel, ten initial states per task, same active DR."""
    n=env.num_envs
    if n%len(TASKS):raise ValueError("Parallel suite needs a multiple of seven environments")
    per=n//len(TASKS)
    torch.manual_seed(6600);torch.cuda.manual_seed_all(6600)
    env.reset_generator.manual_seed(6779)
    env.full_dr.generator.manual_seed(8383);env.full_dr.cpu_generator.manual_seed(8484)
    _ground_start(env,6600)
    commands=env.command.new_tensor([[vx,0.,wz] for _,vx,wz,_,_,_ in TASKS]).repeat_interleave(per,0)
    heights=env.height.new_tensor([h for _,_,_,h,_,_ in TASKS]).repeat_interleave(per)
    def set_commands():
        env.heading_env.zero_();env.standing_env.zero_();env.heading_target.zero_()
        env.command.copy_(commands);env.height.copy_(heights);env.command_timer.fill_(10000.)
        env.reward.command.copy_(commands);env.reward.height_cmd.copy_(heights)
    set_commands()
    initial_dr=dict(mass_scale=env.full_dr.factor.tolist(),leg_gain=env.full_dr.leg_gain_scale.tolist(),
                    wheel_gain=env.full_dr.wheel_gain_scale.tolist(),wheel_mu=env.full_dr.mu.tolist(),
                    action_delay_ticks=env._action_delay_ticks.tolist(),sensor_delay_ticks=env._sensor_delay_ticks.tolist())
    obs=TensorDict(env._get_observations(),batch_size=[n]);policy=algorithm.get_policy()
    resets=torch.zeros(n,device=env.device,dtype=torch.long);records=[]
    for step in range(300):
        actions=policy(obs,stochastic_output=False).clamp(-6,6)
        raw,_,term,timeout,_=env.step(actions);resets+=term.long();set_commands()
        obs=TensorDict(raw,batch_size=[n])
        if step>=180:records.append(torch.stack((env.view.data.root_lin_vel_b[:,0],env.view.data.root_ang_vel_b[:,2],env._height_observation()),-1).clone())
    values=torch.stack(records).mean(0);results=[]
    for index,(name,vx,wz,height,vlimit,wlimit) in enumerate(TASKS):
        sl=slice(index*per,(index+1)*per);v=values[sl];errs=(v-v.new_tensor([vx,wz,height])).abs();reset=resets[sl]
        passed=reset==0
        if vlimit is not None:passed &= errs[:,0]<=vlimit
        if wlimit is not None:passed &= errs[:,1]<=abs(wz)*wlimit
        if name.startswith("height"):passed &= errs[:,2]<=.02
        results.append(dict(task=name,command=[vx,0.,wz],height_command=height,passed=int(passed.sum()),requested=per,
            capability_gate=name!="combo_0.9_1.2",mean=v.mean(0).tolist(),mean_abs_error=errs.mean(0).tolist(),max_abs_error=errs.max(0).values.tolist(),
            per_env=[dict(env=index*per+i,mean=v[i].tolist(),abs_error=errs[i].tolist(),resets=int(reset[i]),passed=bool(passed[i])) for i in range(per)]))
    return dict(passed=all(r["passed"]==per for r in results if r["capability_gate"]),num_envs=n,initial_states_per_task=per,
        protocol="parallel fixed commands, original 0.28m default; 300 steps/tail120; deterministic paired DR seed6600",
        physics="PhysX",active_dr=env.mild_dr.summary(),initial_dr=initial_dr,results=results)
