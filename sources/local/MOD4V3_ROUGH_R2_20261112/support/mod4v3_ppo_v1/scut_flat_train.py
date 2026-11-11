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
    parser.add_argument('--profile',choices=['flat_v30','flat_v1','flat_v2','flat_robust','flat_robust_full','flat_joint_friction','flat_spring_damping','flat_speed_preserve','flat_external_dr','flat_obs_noise','flat_obs_delay','flat_action_delay','flat_scut_delay','flat_physical_delay','flat_forward_square','flat_body_mass','flat_effort_scale','flat_material','flat_velocity_push','flat_remaining_dr','flat_remaining_mixed_dr','rough_r0','rough_r1','rough_r2','rough_v0'],default='flat_v30')
    parser.add_argument('--job',required=True)
    parser.add_argument('--num-envs',type=int,default=16)
    parser.add_argument('--seconds',type=int,default=3600)
    parser.add_argument('--resume')
    parser.add_argument('--iterations',type=int,default=100000)
    parser.add_argument('--learning-rate',type=float)
    parser.add_argument('--lr-schedule',choices=['fixed','adaptive'])
    parser.add_argument('--clip-param',type=float)
    parser.add_argument('--learning-epochs',type=int)
    parser.add_argument('--expected-parent-sha')
    parser.add_argument('--rough-probe',action='store_true')
    parser.add_argument('--r2-probe',action='store_true')
    parser.add_argument('--timing-probe',action='store_true')
    parser.add_argument('--fixed-suite',action='store_true')
    parser.add_argument('--parallel-suite',action='store_true')
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
        terrain_selection='flat'
        if args.profile=='flat_v1':
            from .scut_flat_v1_env import ScutFlatV1Env as EnvClass
            from .scut_flat_env import configuration as env_configuration,tensor
        elif args.profile=='flat_v2':
            from .scut_flat_v2_env import ScutFlatV2Env as EnvClass
            from .scut_flat_env import configuration as env_configuration,tensor
        elif args.profile=='flat_robust':
            from .scut_flat_robust_env import ScutFlatRobustEnv as EnvClass
            from .scut_flat_env import configuration as env_configuration,tensor
        elif args.profile=='flat_robust_full':
            from .scut_flat_full_dr_env import ScutFlatFullDREnv as EnvClass
            from .scut_flat_env import configuration as env_configuration,tensor
        elif args.profile=='flat_joint_friction':
            from .scut_flat_joint_friction_env import ScutFlatJointFrictionEnv as EnvClass
            from .scut_flat_env import configuration as env_configuration,tensor
        elif args.profile=='flat_spring_damping':
            from .scut_flat_spring_damping_env import ScutFlatSpringDampingEnv as EnvClass
            from .scut_flat_env import configuration as env_configuration,tensor
        elif args.profile=='flat_speed_preserve':
            from .scut_flat_speed_preserve_env import ScutFlatSpeedPreserveEnv as EnvClass
            from .scut_flat_env import configuration as env_configuration,tensor
        elif args.profile=='flat_external_dr':
            from .scut_flat_external_dr_env import ScutFlatExternalDREnv as EnvClass
            from .scut_flat_env import configuration as env_configuration,tensor
        elif args.profile=='flat_obs_noise':
            from .scut_flat_obs_noise_env import ScutFlatObsNoiseEnv as EnvClass
            from .scut_flat_env import configuration as env_configuration,tensor
        elif args.profile=='flat_obs_delay':
            from .scut_flat_obs_delay_env import ScutFlatObsDelayEnv as EnvClass
            from .scut_flat_env import configuration as env_configuration,tensor
        elif args.profile=='flat_action_delay':
            from .scut_flat_action_delay_env import ScutFlatActionDelayEnv as EnvClass
            from .scut_flat_env import configuration as env_configuration,tensor
        elif args.profile=='flat_scut_delay':
            from .scut_flat_scut_delay_env import ScutFlatScutDelayEnv as EnvClass
            from .scut_flat_env import configuration as env_configuration,tensor
        elif args.profile=='flat_physical_delay':
            from .scut_flat_physical_delay_env import ScutFlatPhysicalDelayEnv as EnvClass
            from .scut_flat_env import configuration as env_configuration,tensor
        elif args.profile=='flat_remaining_mixed_dr':
            from .scut_flat_mixed_dr_env import ScutFlatMixedRemainingDREnv as EnvClass
            from .scut_flat_env import configuration as env_configuration,tensor
        elif args.profile=='flat_remaining_dr':
            from .scut_flat_remaining_dr_env import ScutFlatRemainingDREnv as EnvClass
            from .scut_flat_env import configuration as env_configuration,tensor
        elif args.profile=='flat_velocity_push':
            from .scut_flat_velocity_push_env import ScutFlatVelocityPushEnv as EnvClass
            from .scut_flat_env import configuration as env_configuration,tensor
        elif args.profile=='flat_material':
            from .scut_flat_material_env import ScutFlatMaterialEnv as EnvClass
            from .scut_flat_env import configuration as env_configuration,tensor
        elif args.profile=='flat_effort_scale':
            from .scut_flat_effort_scale_env import ScutFlatEffortScaleEnv as EnvClass
            from .scut_flat_env import configuration as env_configuration,tensor
        elif args.profile=='flat_body_mass':
            from .scut_flat_body_mass_env import ScutFlatBodyMassEnv as EnvClass
            from .scut_flat_env import configuration as env_configuration,tensor
        elif args.profile=='flat_forward_square':
            from .scut_flat_forward_square_env import ScutFlatForwardSquareEnv as EnvClass
            from .scut_flat_env import configuration as env_configuration,tensor
        elif args.profile=='rough_r2':
            from .scut_rough_r2_env import ScutRoughR2Env as EnvClass
            from .scut_flat_env import configuration as env_configuration,tensor
            terrain_selection='rough_r1'
        elif args.profile=='rough_r1':
            from .scut_rough_r1_env import ScutRoughR1Env as EnvClass
            from .scut_flat_env import configuration as env_configuration,tensor
            terrain_selection='rough_r1'
        elif args.profile=='rough_r0':
            from .scut_rough_r0_env import ScutRoughR0Env as EnvClass
            from .scut_flat_env import configuration as env_configuration,tensor
            terrain_selection='rough_r0'
        elif args.profile=='rough_v0':
            from .scut_rough_v0_env import ScutRoughV0Env as EnvClass
            from .scut_flat_env import configuration as env_configuration,tensor
            terrain_selection='rough'
        else:
            from .scut_flat_env import ScutFlatEnv as EnvClass,configuration as env_configuration,tensor
        from .sampling import Sampling
        from mod4v1_scut.config import runner_config
        from rsl_rl.runners import OnPolicyRunner
        seed=plan['seed'];random.seed(seed);np.random.seed(seed);torch.manual_seed(seed);torch.cuda.manual_seed_all(seed)
        meta=metadata(plan['package']);bank=reset_bank(plan['package'],plan['reset_bank'])
        env=EnvClass(env_configuration(meta,bank,args.num_envs,seed,terrain_selection=terrain_selection),meta,bank)
        env.render_enabled=False
        env.reset();env.sample=Sampling(env)
        parity=env.sample.parity()
        # Confirm native mechanical limits, gas and zero implicit motor drives.
        root=env.robot.root_view
        limits=tensor(root.get_dof_limits());stiff=tensor(root.get_dof_stiffnesses())
        damping=tensor(root.get_dof_dampings());mass=tensor(env.mild_dr.mass)
        native=[]
        contract=json.loads((Path(plan['package'])/'assets/import_contract.json').read_bytes())
        for name,row in contract['joints'].items():
            actual=limits[0,env.robot.joint_names.index(name)]
            for wanted,value in zip(row['limits_si'],actual):
                if wanted is not None and abs(float(value)-wanted)>2e-6:
                    raise ValueError('Native mechanical limit differs: '+name)
            native.append(dict(name=name,limits=[str(float(v)) for v in actual]))
        assert torch.all(stiff[:,env.active_ids]==0) and torch.all(damping[:,env.active_ids]==0)
        assert torch.all(stiff[:,env.gas_ids]==2000)
        if args.profile in ('flat_remaining_dr','flat_remaining_mixed_dr','rough_r0','rough_r1','rough_r2'):
            assert torch.all((damping[:,env.gas_ids]>=1.5)&(damping[:,env.gas_ids]<=4.5))
        else:
            assert torch.all(damping[:,env.gas_ids]==3)
        if abs(float(mass[0].sum())-14.294140288606286)>.0001:raise ValueError('Asset mass mismatch')
        dr_name=env.mild_dr.summary().get('profile','mild_dr_white')
        put(job/'STARTUP.json',dict(epoch=time.time(),mode=args.mode,profile=args.profile,num_envs=args.num_envs,
            backend='PhysX TGS32/4' if args.profile!='rough_v0' else 'PhysX SCUT saved config',physics_dt_s=float(env.cfg.sim.dt),control_dt_s=float(env.cfg.sim.dt*env.cfg.decimation),decimation=int(env.cfg.decimation),env_spacing=float(env.cfg.scene.env_spacing),feedback_dt_s=.01,
            nominal=False,DR=dr_name,dr_profile=dr_name,supermimic=False,newton=False,warp=parity,
            policy_action_order=env.order,root_quaternion_native=env.qorder,native_limits=native,
            total_mass_kg=float(mass[0].sum()),reward_weights=env.reward.cfg.rewards,
            command_vx=env.command_vx,command_vy=getattr(env,'command_vy',None),command_wz=env.command_wz,heading_range=env.heading_range,heading_fraction=env.heading_fraction,standing_fraction=env.standing_fraction,command_resample=env.command_resample,height_range=env.height_range,height_cmd_mean=float(env.height.mean()),height_semantics='root_relative_to_ground',use_absolute_height=False,use_leg_length_as_height=False,mild_dr=env.mild_dr.summary(),ppo_value_loss_coef=2.0 if args.profile=='rough_v0' else 4.0,
            lin_vel_err_constraint=float(getattr(env.reward.cfg,'lin_vel_err_constraint',0.0)),lin_vel_xy_square_sigma=env.reward.cfg.lin_vel_xy_square_sigma,velocity_square_effective_coefficient=env.reward.cfg.rewards['track_lin_vel_xy_square']*env.reward.cfg.lin_vel_xy_square_sigma**2,velocity_absolute_cubic_reference_speed_m_s=getattr(env.reward.cfg,'lin_vel_abs_cubic_reference_speed',None),velocity_penalty_formula='-1.5*e**2',
            height_tight_sigma=float(getattr(env.reward.cfg,'height_tight_sigma',0.0)),
            wrong_direction_command_threshold=float(getattr(env.reward.cfg,'wrong_direction_command_threshold',0.0)),
            theta_coefficient=0.,raw_actions=True,
            airborne_state_machine=bool(getattr(env.reward.cfg,'enable_state_machines',False)),
            air_reset_fraction=float(getattr(env,'air_reset_fraction',0.0)),
            ground_reset_fraction=float(getattr(env,'ground_reset_fraction',0.0)),
            zero_torque_control_steps=int(getattr(env,'zero_torque_control_steps',0)),
            ctrl_mode_obs_enabled=bool(getattr(env.reward.cfg,'ctrl_mode_obs_enabled',False))))
        if args.profile in ('rough_r0','rough_r1','rough_r2'):put(job/'TERRAIN_STARTUP.json',env.terrain_summary())
        if args.profile=='rough_r2':put(job/'R2_STARTUP.json',env.r2_summary())
        current=env._get_observations()
        class Vec:
            def __init__(self):
                self.num_envs=env.num_envs;self.num_actions=6;self.device=env.device
                self.max_episode_length=env.max_episode_length;self.cfg=env.cfg
            @property
            def episode_length_buf(self):return env.episode_length_buf
            def get_observations(self):return TensorDict(current,batch_size=[env.num_envs])
        cfg=runner_config();cfg['clip_actions']=6.0 if args.profile in ('flat_robust_full','flat_joint_friction','flat_spring_damping','flat_speed_preserve','flat_external_dr','flat_obs_noise','flat_obs_delay','flat_action_delay','flat_scut_delay','flat_physical_delay','flat_forward_square','flat_body_mass','flat_effort_scale','flat_material','flat_velocity_push','flat_remaining_dr','flat_remaining_mixed_dr','rough_r0','rough_r1','rough_r2') else None;cfg['algorithm']['value_loss_coef']=2.0 if args.profile=='rough_v0' else 4.0
        if args.profile=='rough_v0': cfg['algorithm']['learning_rate']=1.0e-4
        for key,value in [('learning_rate',args.learning_rate),('schedule',args.lr_schedule),('clip_param',args.clip_param),('num_learning_epochs',args.learning_epochs)]:
            if value is not None:cfg['algorithm'][key]=value
        runner=OnPolicyRunner(Vec(),cfg,log_dir=None,device=env.device)
        algorithm=runner.alg;iteration=0;physics_ticks=0
        restored=None
        if args.resume:
            parent_sha=hashlib.sha256(Path(args.resume).read_bytes()).hexdigest()
            if args.expected_parent_sha and parent_sha!=args.expected_parent_sha:
                raise ValueError('Parent SHA mismatch')
            data=torch.load(args.resume,map_location=env.device,weights_only=False)
            if data['format'] not in ('MOD4V3_PHYSX_WARP_STANDING_PPO_V1','MOD4V3_SCUT_FLAT_HEIGHT_PPO_V1','MOD4V3_SCUT_FLAT_V1_AIRBORNE_PPO_V1','MOD4V3_SCUT_FLAT_V2_PPO_V1','MOD4V3_SCUT_FLAT_ROBUST_PPO_V1','MOD4V3_SCUT_FLAT_ROBUST_FULL_PPO_V1','MOD4V3_SCUT_ROUGH_V0_PPO_V1') or data['action_order']!=env.order:
                raise ValueError('Unsupported checkpoint interface')
            if args.profile=='rough_v0':
                # SCUT's Rough-v0 finetune loads policy weights only.
                # Critic, optimizer, iteration and RNG are intentionally fresh.
                if 'actor_state_dict' not in data:
                    raise ValueError('Rough-v0 policy-only resume requires actor_state_dict')
                algorithm.actor.load_state_dict(data['actor_state_dict'],strict=True)
                iteration=0;physics_ticks=0
                env.reset();current=env._get_observations()
                restored=dict(source=args.resume,iteration=iteration,
                    actor_critic_STD_Adam_restored=False,policy_only=True,
                    optimizer_entries=0,reset_rng_restored=False,
                    physics_resume='fresh critic/optimizer; policy-only actor load',
                    saved_envs=data['num_envs'],new_envs=env.num_envs)
            else:
                algorithm.load(data,load_cfg=None,strict=True);iteration=data['iter']
                algorithm.learning_rate=data['learning_rate']
                for group in algorithm.optimizer.param_groups:group['lr']=data['learning_rate']
                random.setstate(data['python_rng']);np.random.set_state(data['numpy_rng'])
                torch.set_rng_state(data['cpu_rng'].cpu());torch.cuda.set_rng_state_all([v.cpu() for v in data['cuda_rng']])
                reset_rng_restored=False
                if data.get('reset_rng') is not None:
                    env.reset_generator.set_state(data['reset_rng'].cpu())
                    reset_rng_restored=True
                physics_ticks=data['physics_ticks']
                env.reset();current=env._get_observations()
                restored=dict(source=args.resume,iteration=iteration,
                    actor_critic_STD_Adam_restored=True,optimizer_entries=len(algorithm.optimizer.state),
                    reset_rng_restored=reset_rng_restored,physics_resume='one fresh episode',
                    saved_envs=data['num_envs'],new_envs=env.num_envs)
            if args.profile in ('rough_r1','rough_r2') and data.get('terrain_curriculum_state') is not None and int(data['num_envs'])==env.num_envs:
                if int(data['num_envs'])!=env.num_envs:raise ValueError('R1 curriculum resume requires same env count')
                restored['terrain_curriculum']=env.restore_terrain_curriculum(data['terrain_curriculum_state'])
                current=env._get_observations()
                put(job/'TERRAIN_RESTORED.json',env.terrain_summary())
            if args.profile=='rough_r2' and data.get('r2_curriculum_state') is not None and int(data['num_envs'])==env.num_envs:
                env.restore_r2_counters(data['r2_curriculum_state'])
            if args.profile=='rough_r2':put(job/'R2_RESTORED_START.json',env.r2_summary())
            restored['source_sha256']=parent_sha
            put(job/'RESTORE.json',restored)
        if args.learning_rate is not None:
            algorithm.learning_rate=args.learning_rate
            for group in algorithm.optimizer.param_groups:group['lr']=args.learning_rate
        put(job/'PPO_EFFECTIVE.json',dict(config=cfg,learning_rate=algorithm.learning_rate,
            schedule=algorithm.schedule,clip_param=algorithm.clip_param,num_learning_epochs=algorithm.num_learning_epochs,
            optimizer_lrs=[g['lr'] for g in algorithm.optimizer.param_groups],
            parent_lr=data['learning_rate'] if args.resume else None))
        checkpoint_format=('MOD4V3_SCUT_FLAT_V1_AIRBORNE_PPO_V1' if args.profile=='flat_v1' else ('MOD4V3_SCUT_FLAT_V2_PPO_V1' if args.profile=='flat_v2' else ('MOD4V3_SCUT_FLAT_ROBUST_PPO_V1' if args.profile=='flat_robust' else ('MOD4V3_SCUT_FLAT_ROBUST_FULL_PPO_V1' if args.profile in ('flat_robust_full','flat_joint_friction','flat_spring_damping','flat_speed_preserve','flat_external_dr','flat_obs_noise','flat_obs_delay','flat_action_delay','flat_scut_delay','flat_physical_delay','flat_forward_square','flat_body_mass','flat_effort_scale','flat_material','flat_velocity_push','flat_remaining_dr','flat_remaining_mixed_dr','rough_r0','rough_r1','rough_r2') else ('MOD4V3_SCUT_ROUGH_V0_PPO_V1' if args.profile=='rough_v0' else 'MOD4V3_SCUT_FLAT_HEIGHT_PPO_V1')))))
        def save(name):
            data=algorithm.save()
            data.update(format=checkpoint_format,iter=iteration,
                action_order=env.order,num_envs=env.num_envs,learning_rate=algorithm.learning_rate,
                reward_recipe=dict(profile=args.profile,velocity_penalty_formula='-1.5*e**2',weights=dict(env.reward.cfg.rewards),lin_vel_xy_square_sigma=env.reward.cfg.lin_vel_xy_square_sigma,lin_vel_err_constraint=env.reward.cfg.lin_vel_err_constraint),
                domain_randomization_state=env.full_dr.checkpoint_state() if hasattr(env.full_dr,'checkpoint_state') else None,
                physics_ticks=physics_ticks,cpu_rng=torch.get_rng_state(),cuda_rng=torch.cuda.get_rng_state_all(),
                python_rng=random.getstate(),numpy_rng=np.random.get_state(),reset_rng=env.reset_generator.get_state(),
                reward_tensors={k:v for k,v in vars(env.reward).items() if torch.is_tensor(v)},
                reward_sums=env.reward._episode_sums,done_totals=env.done_totals,
                source_asset=plan['asset_identity'],full_DR=env.mild_dr.summary().get('profile','mild_dr_white'),
                 body_mass_scale=getattr(env.full_dr,'body_mass_scale',None),
                 effort_output_scale=getattr(env.full_dr,'effort_scale',None),
                 effort_last_sample_step=getattr(env.full_dr,'effort_last_sample_step',None),
                 effort_sample_count=getattr(env.full_dr,'effort_sample_count',None),
                 effort_generator_rng=env.full_dr.effort_generator.get_state() if hasattr(env.full_dr,'effort_generator') else None,
                resume_scope=('policy-only actor; fresh critic/optimizer/RNG' if args.profile=='rough_v0' else 'complete PPO actor/critic/STD/Adam/LR/RNG; one fresh physical episode'))
            if args.profile in ('rough_r0','rough_r1','rough_r2'):data['terrain_curriculum_state']=env.terrain_checkpoint_state()
            if args.profile=='rough_r2':data['r2_curriculum_state']=env.r2_checkpoint_state()
            output=job/name;tmp=output.with_name(output.name+'.partial')
            with tmp.open('wb') as f:torch.save(data,f);f.flush();os.fsync(f.fileno())
            os.replace(tmp,output)
            digest=hashlib.sha256(output.read_bytes()).hexdigest()
            return dict(path=str(output),bytes=output.stat().st_size,SHA=digest,iteration=iteration,
                        optimizer_entries=len(algorithm.optimizer.state))

        if args.r2_probe:
            from .r2_landing_checks import run_probe
            algorithm.eval_mode()
            result=run_probe(env,algorithm)
            put(job/'R2_PROBE.json',result)
            put(job/'PROBE_COMPLETE.json',dict(epoch=time.time(),no_optimizer_update=True))
            return
        if args.rough_probe:
            if args.profile=='rough_r1':from .rough_r1_checks import run_probe
            else:from .rough_r0_checks import run_probe
            algorithm.eval_mode()
            put(job/'ROUGH_PROBE.json',run_probe(env,algorithm))
            put(job/'PROBE_COMPLETE.json',dict(epoch=time.time(),no_optimizer_update=True))
            return
        if args.timing_probe:
            from .physical_delay_checks import run_timing_probe
            put(job/'TIMING_PROBE.json',run_timing_probe(env))
            put(job/'PROBE_COMPLETE.json',dict(epoch=time.time(),timing_only=True))
            return
        if args.parallel_suite:
            from .physical_delay_checks import run_parallel_fixed_suite
            algorithm.eval_mode()
            put(job/'FIXED_SUITE.json',run_parallel_fixed_suite(env,algorithm,job))
            return
        if args.fixed_suite:
            from .physical_delay_checks import run_fixed_suite
            algorithm.eval_mode()
            put(job/'FIXED_SUITE.json',run_fixed_suite(env,algorithm,job))
            return
        obs=TensorDict(current,batch_size=[env.num_envs])
        if args.profile=='rough_v0' and args.mode=='train':
            # Match SCUT's runner.learn(init_at_random_ep_len=True).
            env.episode_length_buf[:] = torch.randint(
                0, env.max_episode_length, (env.num_envs,), device=env.device
            )
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
                    stable=((s['height_obs']-s['height']).abs()<.035)&(theta.abs().amax(-1)<.15)&\
                        ((speed-s['command'][:,0]).abs()<.15)&(roll.abs()<.15)&(pitch.abs()<.15)
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
        algorithm.train_mode();start=time.time();last_save=start;last=None;next_checkpoint=300.0
        before={k:v.detach().clone() for k,v in algorithm.actor.state_dict().items()}
        start_iteration=iteration
        while iteration<args.iterations and time.time()-start<args.seconds:
            tick=time.time();reward_mean=0.;max_closure=0.;reward_min=float('inf');reward_max=float('-inf');reward_absmax=0.;top_reward_term=None;reward_debug=None
            forward_tracking=torch.zeros(4,device=env.device)
            with torch.inference_mode():
                for _ in range(cfg['num_steps_per_env']):
                    action=algorithm.act(obs)
                    if args.profile=='rough_v0':
                        # Deployment contract clip: prevent rare flat-policy
                        # outliers from exploding the MOD4 loop joints on rough
                        # terrain. SCUT itself leaves clip_actions=None.
                        action=action.clamp(-6.0,6.0)
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
                    measured=env.snapshots
                    straight=(measured['command'][:,0]>=1.5)&(measured['command'][:,2].abs()<=1.0)&(~(term|timeout))
                    speed=measured['velocity'][:,0];target=measured['command'][:,0];error=speed-target
                    forward_tracking+=torch.stack((straight.sum(),speed[straight].sum(),target[straight].sum(),error[straight].abs().sum()))
                    max_closure=max(max_closure,float(env.closure_error.max()))
                    rmin=float(reward.min());rmax=float(reward.max());reward_min=min(reward_min,rmin);reward_max=max(reward_max,rmax)
                    if abs(rmin)>reward_absmax or abs(rmax)>reward_absmax:
                        reward_absmax=max(abs(rmin),abs(rmax))
                        raw_terms=getattr(env.reward,'raw_terms',{})
                        candidates=[]
                        for name,val in raw_terms.items():
                            w=float(env.reward.cfg.rewards.get(name,0.0))
                            if w!=0.0 and torch.is_tensor(val) and val.numel() and val.dtype.is_floating_point:
                                candidates.append((abs(float((val*w).abs().max())),name,float(val.abs().max()),w))
                        if candidates:
                            top_reward_term=max(candidates)[1:]
                        else:
                            top_reward_term=None
                        worst_env=int(reward.abs().argmax())
                        reward_debug=dict(env=worst_env,
                            root_z=float(env.view.data.root_pos_w[worst_env,2]),
                            ground_z=float(env.reward.ground_z_est[worst_env]),
                            height_obs=float(env._height_observation()[worst_env]),
                            height_cmd=float(env.reward.height_cmd[worst_env]),
                            wheel_ground=[float(x) for x in env.reward.ground_wheels[worst_env]])
                algorithm.compute_returns(obs)
            losses=algorithm.update();iteration+=1;runner.current_learning_iteration=iteration
            last=dict(epoch=time.time(),iteration=iteration,iteration_seconds=time.time()-tick,
                env_steps_s=env.num_envs*cfg['num_steps_per_env']/(time.time()-tick),
                window_env_steps_s=(iteration-(restored['iteration'] if restored else 0))*env.num_envs*cfg['num_steps_per_env']/(time.time()-start),
                losses=losses,mean_reward=reward_mean/cfg['num_steps_per_env'],max_closure_m=max_closure,reward_min=reward_min,reward_max=reward_max,reward_absmax=reward_absmax,top_reward_term=top_reward_term,reward_debug=reward_debug,
                done_totals=env.done_totals,optimizer_entries=len(algorithm.optimizer.state),
                L0_mean=float(env.reward.length.mean()),theta_abs_mean=float(env.reward.theta.abs().mean()),
                vx_mean=float(env.view.data.root_lin_vel_b[:,0].mean()),learning_rate=algorithm.learning_rate,
                actor_drift_l2=float(torch.sqrt(sum((v-before[k]).square().sum() for k,v in algorithm.actor.state_dict().items()))))
            if args.profile in ('rough_r0','rough_r1','rough_r2'):last['terrain']=env.terrain_summary()
            if args.profile=='rough_r2':last['r2_landing']=env.r2_summary()
            last['training_elapsed_seconds']=time.time()-start
            samples,actual,command,abs_error=forward_tracking.tolist()
            last['forward_tracking']=dict(env_step_samples=int(samples),mean_actual_vx=actual/samples if samples else None,mean_command_vx=command/samples if samples else None,mean_abs_error=abs_error/samples if samples else None,selection='cmd_vx>=1.5 and abs(cmd_wz)<=1; varying heights and transients; rollout24steps; not fixed-task pass')
            last['numeric_peaks']=dict(
                joint_vel_max=float(getattr(env,'numeric_joint_vel_peak',torch.tensor(0.0)).max()),
                root_ang_max=float(getattr(env,'numeric_root_ang_peak',torch.tensor(0.0)).max()),
                root_lin_max=float(getattr(env,'numeric_root_lin_peak',torch.tensor(0.0)).max()))
            if hasattr(env,'velocity_push_count'):
                last['velocity_push']=dict(total_events=int(env.velocity_push_count.sum()),envs_pushed=int((env.velocity_push_count>0).sum()),last_delta_xy_abs_max=float(env.velocity_push_last_delta[:,:2].abs().max()),time_left_range_s=[float(env.velocity_push_time_left.min()),float(env.velocity_push_time_left.max())])
            if hasattr(env.full_dr,'gain_count'):
                last['remaining_dr']=dict(gain_sample_count_range=[int(env.full_dr.gain_count.min()),int(env.full_dr.gain_count.max())],reset_count_by_mode=env.reset_count_by_mode.tolist(),com_abs_max=env.full_dr.startup_com_delta.abs().amax(0).tolist())
            put(job/'LATEST_PROGRESS.json',last)
            if iteration==start_iteration+1:
                changed=any(not torch.equal(v,algorithm.actor.state_dict()[k]) for k,v in before.items())
                if not changed:raise ValueError('Actor did not update')
                last['actor_changed']=changed;last['checkpoint']=save('model_first_complete.pt')
                put(job/'FIRST_UPDATE.json',last)
            if time.time()-start>=next_checkpoint:
                elapsed_minutes=int(next_checkpoint//60)
                next_checkpoint+=300.0
                periodic_name=f'model_{elapsed_minutes:03d}m.pt'
                suffix=1
                while (job/periodic_name).exists():
                    periodic_name=f'model_{elapsed_minutes:03d}m_{suffix:02d}.pt'
                    suffix+=1
                receipt=save(periodic_name)
                receipt['training_elapsed_seconds']=time.time()-start
                put(job/f'PERIODIC_{elapsed_minutes:03d}M.json',receipt)
                put(job/'PERIODIC_FULL.json',receipt)
                last_save=time.time()
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




