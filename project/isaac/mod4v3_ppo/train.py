"""Finite PPO owner: complete checkpoints, safe exit, independent eval and replay."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import random
import sys
import time
import traceback


def put(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_name(path.name+'.partial')
    tmp.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
    os.replace(tmp,path)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--plan',required=True)
    parser.add_argument('--mode',choices=['probe','train','evaluate'],default='probe')
    parser.add_argument('--job',required=True)
    parser.add_argument('--num-envs',type=int,default=16)
    parser.add_argument('--seconds',type=int,default=3600)
    parser.add_argument('--resume')
    parser.add_argument('--iterations',type=int,default=100000)
    args=parser.parse_args();plan=json.loads(Path(args.plan).read_bytes())
    job=Path(args.job);job.mkdir(parents=True,exist_ok=False)
    storage=job/'kit_isolation';(storage/'data').mkdir(parents=True)
    (storage/'DerivedDataCache').mkdir();(storage/'data/user.config.json').write_text('{}')
    os.environ.update(MOD4V1_E0_JOB_ROOT=str(job),MOD4V1_E0_KIT_STORAGE_ROOT=str(storage),
        MOD4_SCUT_SOURCE_PATHS=plan['source_paths'],OMNI_KIT_ACCEPT_EULA='YES',ISAACSIM_ACCEPT_EULA='Y')
    sys.path[:0]=[plan['runtime'],plan['shared_package'],plan['package'],plan['support']]
    # AppLauncher installs and selects the configured PhysX extension before imports.
    from launcher_mod4v1_e0 import IsolatedAppLauncher208
    launcher=IsolatedAppLauncher208(dict(headless=True,device='cuda:0',enable_cameras=False))
    app=launcher.app;env=None
    try:
        import numpy as np
        import torch
        from tensordict import TensorDict
        from .model import metadata,reset_bank
        from .env import StandingEnv,configuration,tensor
        from .sampling import Sampling
        from mod4v1_scut.config import runner_config
        from rsl_rl.runners import OnPolicyRunner
        seed=plan['seed'];random.seed(seed);np.random.seed(seed);torch.manual_seed(seed);torch.cuda.manual_seed_all(seed)
        meta=metadata(plan['package']);bank=reset_bank(plan['package'],plan['reset_bank'])
        terrain_selection=plan.get('terrain','easy_mixed')
        env=StandingEnv(configuration(meta,bank,args.num_envs,seed,terrain_selection),meta,bank)
        env.render_enabled=False
        env.reset();env.sample=Sampling(env)
        parity=env.sample.parity()
        # Confirm native mechanical limits, gas and zero implicit motor drives.
        root=env.robot.root_view
        limits=tensor(root.get_dof_limits());stiff=tensor(root.get_dof_stiffnesses())
        damping=tensor(root.get_dof_dampings());mass=tensor(root.get_masses())
        native=[]
        contract=json.loads((Path(plan['package'])/'assets/import_contract.json').read_bytes())
        for name,row in contract['joints'].items():
            actual=limits[0,env.robot.joint_names.index(name)]
            for wanted,value in zip(row['limits_si'],actual):
                if wanted is not None and abs(float(value)-wanted)>2e-6:
                    raise ValueError('Native mechanical limit differs: '+name)
            native.append(dict(name=name,limits=[str(float(v)) for v in actual]))
        assert torch.all(stiff[:,env.active_ids]==0) and torch.all(damping[:,env.active_ids]==0)
        assert torch.all(stiff[:,env.gas_ids]==2000) and torch.all(damping[:,env.gas_ids]==3)
        if abs(float(mass[0].sum())-14.294140288606286)>.0001:raise ValueError('Asset mass mismatch')
        terrain_cfg=env.cfg.scene.terrain.terrain_generator
        terrain_config=dict(selection=terrain_selection,size=list(terrain_cfg.size),
            num_rows=terrain_cfg.num_rows,num_cols=terrain_cfg.num_cols,
            difficulty_range=list(terrain_cfg.difficulty_range),curriculum=terrain_cfg.curriculum,
            sub_terrains={key:{k:v for k,v in vars(value).items()
                if isinstance(v,(int,float,bool,str,tuple,list)) or v is None}
                for key,value in terrain_cfg.sub_terrains.items()})
        put(job/'STARTUP.json',dict(epoch=time.time(),mode=args.mode,num_envs=args.num_envs,
            terrain=terrain_config,
            backend='PhysX TGS32/4',physics_dt_s=.0025,control_dt_s=.02,feedback_dt_s=.01,
            gpu_max_rigid_patch_count=env.cfg.sim.physics.gpu_max_rigid_patch_count,
            nominal=True,DR=False,supermimic=False,newton=False,warp=parity,
            native_body_names=list(env.robot.body_names),
            policy_action_order=env.order,root_quaternion_native=env.qorder,native_limits=native,
            total_mass_kg=float(mass[0].sum()),reward_weights=env.reward.cfg.rewards,
            command=[.35,0.,0.],L0_target_m=.334,theta_coefficient=-2.,raw_actions=True))
        if args.mode=='evaluate':
            terrain=env.scene['terrain']
            mesh=getattr(terrain,'_standing_terrain_mesh',None)
            mesh_path=None
            if mesh is not None:
                mesh_path=job/'actual_terrain.npz'
                np.savez_compressed(mesh_path,vertices=mesh.vertices,faces=mesh.faces)
            put(job/'REPLAY_METADATA.json',dict(body_names=list(env.robot.body_names),
                origins=env.scene.env_origins.cpu().tolist(),quaternion_order='wxyz',
                control_dt_s=.02,source_checkpoint=args.resume,
                terrain_mesh=str(mesh_path) if mesh_path else None,
                source_USD=plan['package']+'/assets/robot.usd'))
        current=env._get_observations()
        class Vec:
            def __init__(self):
                self.num_envs=env.num_envs;self.num_actions=6;self.device=env.device
                self.max_episode_length=env.max_episode_length;self.cfg=env.cfg
            @property
            def episode_length_buf(self):return env.episode_length_buf
            def get_observations(self):return TensorDict(current,batch_size=[env.num_envs])
        cfg=runner_config();cfg['clip_actions']=None
        runner=OnPolicyRunner(Vec(),cfg,log_dir=None,device=env.device)
        algorithm=runner.alg;iteration=0;physics_ticks=0
        restored=None
        if args.resume:
            data=torch.load(args.resume,map_location=env.device,weights_only=False)
            if data['format']!='MOD4V3_PHYSX_WARP_STANDING_PPO_V1' or data['action_order']!=env.order:
                raise ValueError('Unsupported checkpoint interface')
            algorithm.load(data,load_cfg=None,strict=True);iteration=data['iter']
            algorithm.learning_rate=data['learning_rate']
            for group in algorithm.optimizer.param_groups:group['lr']=data['learning_rate']
            saved=algorithm.save()
            def equal_tree(a,b):
                if torch.is_tensor(a):return torch.is_tensor(b) and torch.equal(a.cpu(),b.cpu())
                if isinstance(a,dict):return a.keys()==b.keys() and all(equal_tree(v,b[k]) for k,v in a.items())
                if isinstance(a,(list,tuple)):return len(a)==len(b) and all(equal_tree(x,y) for x,y in zip(a,b))
                return a==b
            if not all(equal_tree(data[key],value) for key,value in saved.items()):
                raise ValueError('Full PPO restore differs from saved learner state')
            random.setstate(data['python_rng']);np.random.set_state(data['numpy_rng'])
            torch.set_rng_state(data['cpu_rng'].cpu());torch.cuda.set_rng_state_all([v.cpu() for v in data['cuda_rng']])
            env.reset_generator.set_state(data['reset_rng'].cpu())
            physics_ticks=data['physics_ticks']
            # Complete learner/RNG restoration then one fresh physical episode.
            env.reset();current=env._get_observations()
            restored=dict(source=args.resume,iteration=iteration,
                actor_critic_STD_Adam_restored=True,optimizer_entries=len(algorithm.optimizer.state),
                all_saved_learning_tensors_equal=True,
                reset_rng_restored=True,physics_resume='one fresh episode',
                saved_envs=data['num_envs'],new_envs=env.num_envs,
                population_resized=data['num_envs']!=env.num_envs,
                per_environment_state='fresh physical episodes; DR disabled')
            put(job/'RESTORE.json',restored)
        def save(name):
            data=algorithm.save()
            data.update(format='MOD4V3_PHYSX_WARP_STANDING_PPO_V1',iter=iteration,
                action_order=env.order,num_envs=env.num_envs,learning_rate=algorithm.learning_rate,
                physics_ticks=physics_ticks,cpu_rng=torch.get_rng_state(),cuda_rng=torch.cuda.get_rng_state_all(),
                python_rng=random.getstate(),numpy_rng=np.random.get_state(),reset_rng=env.reset_generator.get_state(),
                reward_tensors={k:v for k,v in vars(env.reward).items() if torch.is_tensor(v)},
                reward_sums=env.reward._episode_sums,done_totals=env.done_totals,
                source_asset=plan['asset_identity'],full_DR=False,
                resume_scope='complete PPO actor/critic/STD/Adam/LR/RNG; one fresh physical episode')
            output=job/name;tmp=output.with_name(output.name+'.partial')
            with tmp.open('wb') as f:torch.save(data,f);f.flush();os.fsync(f.fileno())
            os.replace(tmp,output)
            digest=hashlib.sha256(output.read_bytes()).hexdigest()
            return dict(path=str(output),bytes=output.stat().st_size,SHA=digest,iteration=iteration,
                        optimizer_entries=len(algorithm.optimizer.state))

        obs=TensorDict(current,batch_size=[env.num_envs])
        if args.mode=='evaluate':
            algorithm.eval_mode();trajectory=[];episodes=[];counts=torch.zeros(env.num_envs,dtype=torch.bool,device=env.device)
            policy=algorithm.get_policy();steps=0
            while not bool(counts.all()) and steps<501:
                with torch.inference_mode():
                    action=policy(obs,stochastic_output=False)
                    raw,reward,term,timeout,extra=env.step(action)
                    s=env.snapshots;done=term|timeout
                    length=s['length'];theta=s['theta'];speed=s['velocity'][:,0]
                    roll,pitch,_=euler_angles(s['root_quat'])
                    stable=((length-.334).abs().amax(-1)<.035)&(theta.abs().amax(-1)<.15)&\
                        ((speed-.35).abs()<.15)&(roll.abs()<.15)&(pitch.abs()<.15)
                    trajectory.append({k:v.detach().cpu().numpy() for k,v in s.items()})
                    for i in (done&~counts).nonzero().flatten().tolist():
                        episodes.append(dict(env=i,steps=steps+1,terminated=bool(term[i]),timeout=bool(timeout[i]),
                            last_speed=float(speed[i]),last_L0=length[i].tolist(),last_theta=theta[i].tolist()))
                    counts|=done;obs=TensorDict(raw,batch_size=[env.num_envs]);steps+=1
            np.savez_compressed(job/'actual_replay.npz',**{k:np.stack([x[k] for x in trajectory]) for k in trajectory[0]})
            put(job/'RESULT.json',dict(epoch=time.time(),independent=True,episodes=len(episodes),
                requested=env.num_envs,steps=steps,episode_results=episodes,done_totals=env.done_totals,
                final_stable_count=int(stable.sum()),replay=str(job/'actual_replay.npz'),restore=restored))
            return
        algorithm.train_mode();start=time.time();last_save=start;last=None
        before={k:v.detach().clone() for k,v in algorithm.actor.state_dict().items()}
        first_iteration=iteration
        while iteration<args.iterations and time.time()-start<args.seconds:
            tick=time.time();reward_mean=0.;max_closure=0.
            with torch.inference_mode():
                for _ in range(cfg['num_steps_per_env']):
                    action=algorithm.act(obs)
                    raw,reward,term,timeout,extra=env.step(action)
                    terminal=TensorDict(env.terminal_observations,batch_size=[env.num_envs])
                    # RSL5 defaults to V(s_t) on timeout. Use the actual terminal
                    # state once, and omit its built-in timeout correction.
                    reward=reward+algorithm.gamma*algorithm.critic(terminal).squeeze(-1)*timeout
                    obs=TensorDict(raw,batch_size=[env.num_envs])
                    if not all(bool(torch.isfinite(v).all()) for v in obs.values()):
                        raise ValueError('Nonfinite policy/critic observation')
                    if not bool(torch.isfinite(reward).all()):raise ValueError('Nonfinite reward')
                    algorithm.process_env_step(obs,reward,term|timeout,{})
                    physics_ticks+=8;reward_mean+=float(reward.mean())
                    max_closure=max(max_closure,float(env.closure_error.max()))
                algorithm.compute_returns(obs)
            losses=algorithm.update();iteration+=1;runner.current_learning_iteration=iteration
            last=dict(epoch=time.time(),iteration=iteration,iteration_seconds=time.time()-tick,
                env_steps_s=env.num_envs*cfg['num_steps_per_env']/(time.time()-tick),
                window_env_steps_s=(iteration-(restored['iteration'] if restored else 0))*env.num_envs*cfg['num_steps_per_env']/(time.time()-start),
                losses=losses,mean_reward=reward_mean/cfg['num_steps_per_env'],max_closure_m=max_closure,
                done_totals=env.done_totals,optimizer_entries=len(algorithm.optimizer.state),
                L0_mean=float(env.reward.length.mean()),theta_abs_mean=float(env.reward.theta.abs().mean()),
                vx_mean=float(env.view.data.root_lin_vel_b[:,0].mean()))
            put(job/'LATEST_PROGRESS.json',last)
            if iteration==first_iteration+1:
                changed=any(not torch.equal(v,algorithm.actor.state_dict()[k]) for k,v in before.items())
                if not changed:raise ValueError('Actor did not update')
                last['actor_changed']=changed;last['checkpoint']=save('model_first_complete.pt')
                put(job/'FIRST_UPDATE.json',last)
            if time.time()-last_save>=300:
                put(job/'PERIODIC_FULL.json',save('model_periodic.pt'));last_save=time.time()
            if args.mode=='probe':break
        receipt=save('model_final.pt')
        put(job/'FINAL.json',dict(epoch=time.time(),checkpoint=receipt,last_progress=last,
            elapsed_seconds=time.time()-start,safe_close_requested=True))
    except BaseException:
        put(job/'ERROR.json',dict(epoch=time.time(),traceback=traceback.format_exc()))
        raise
    finally:
        if env is not None:env.close()
        put(job/'SAFE_CLOSED.json',dict(epoch=time.time(),scene_closed=True))
        app.close()


def euler_angles(q):
    from mod4v1_scut.math_ops import euler_xyz_from_quat
    return euler_xyz_from_quat(q)


if __name__=='__main__':main()
