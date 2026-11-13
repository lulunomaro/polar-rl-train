"""Collect actual native successful stair teacher episodes; never run an optimizer."""
from pathlib import Path
import torch,time,hashlib
from tensordict import TensorDict

def collect_successful_stairs(env,algorithm,plan,job,put):
    spec=plan['demo_collection'];dev=env.device;ids=env.continuous_stair_mask.nonzero().flatten();n=len(ids)
    env.reset();env.stair_height[ids]=float(spec['height_cmd_m']);env.stair_speed[ids]=float(spec['speed_cmd_m_s']);env.reward._invalidate_step_caches()
    obs=TensorDict(env._get_observations(),batch_size=[env.num_envs]);finished=torch.zeros(n,dtype=torch.bool,device=dev);success=torch.zeros_like(finished)
    initial_stage=env.stair_initial_stage[ids].clone();nominal=env.full_dr.nominal_env_mask[ids].clone();up=env.stair_up[ids].clone()
    observations=[];targets=[];valids=[];success_step=torch.full((n,),-1,device=dev,dtype=torch.long);started=time.time();algorithm.eval_mode();policy=algorithm.get_policy()
    with torch.inference_mode():
        for step in range(int(spec['max_steps'])):
            action=policy(obs,stochastic_output=False).clamp(-6,6)
            valid=(~finished)&up&(env.episode_length_buf[ids]*env.step_dt>=3.)
            observations.append(obs['policy'][ids].clone());targets.append(action[ids].clone());valids.append(valid)
            raw,reward,term,timeout,extra=env.step(action)
            newly=(~finished)&up&(env.stair_goal_hold[ids]>=.3)
            success|=newly;success_step[newly]=step
            finished|=term[ids]|timeout[ids]|newly
            obs=TensorDict(raw,batch_size=[env.num_envs])
            if step%100==0 or bool(finished.all()):
                put(job/'DEMO_PROGRESS.json',dict(step=step+1,seconds=(step+1)*env.step_dt,wall_seconds=time.time()-started,successful_total=int(success.sum()),successful_full=int((success&(initial_stage==0)).sum()),successful_mid=int((success&(initial_stage==1)).sum()),first_episode_finished=int(finished.sum()),done_totals=env.done_totals))
            if bool(finished.all()):break
    obs_all=torch.stack(observations);act_all=torch.stack(targets);valid=torch.stack(valids)&success[None,:]
    x=obs_all[valid].float().cpu().clone();y=act_all[valid].float().cpu().clone();env_ids=ids[None,:].expand_as(valid)[valid].cpu();frame=torch.arange(len(valid),device=dev)[:,None].expand_as(valid)[valid].cpu()
    meta=dict(teacher_sha256=plan['parent_sha256'],native_successful_episodes=int(success.sum()),native_successful_full=int((success&(initial_stage==0)).sum()),native_successful_mid=int((success&(initial_stage==1)).sum()),success_DR=int((success&~nominal).sum()),success_nominal=int((success&nominal).sum()),observations=int(len(x)),policy_dim=35,action_dim=6,collection=spec,first_episode_success_envs=ids[success].cpu().tolist(),full_success_envs=ids[success&(initial_stage==0)].cpu().tolist(),nominal_success_envs=ids[success&nominal].cpu().tolist(),success_endpoint=success_step[success].cpu().tolist(),done_totals=env.done_totals,wall_seconds=time.time()-started,no_optimizer_update=True)
    assert x.shape[1:]==(35,) and y.shape[1:]==(6,)
    path=job/'success_demos.pt';torch.save(dict(policy=x,actions=y,env_id=env_ids,endpoint=frame,metadata=meta),path)
    meta.update(dataset_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),dataset_bytes=path.stat().st_size)
    put(job/'DEMO_RESULT.json',meta)
    return meta
