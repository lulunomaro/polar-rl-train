"""Probe-only native Route2 validation. This program contains no PPO update or optimizer step."""
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
    parser.add_argument('--mode',choices=['probe'],default='probe')
    parser.add_argument('--profile',choices=['flat_v30','flat_v1','flat_v2','flat_robust','flat_robust_full','flat_joint_friction','flat_spring_damping','flat_speed_preserve','flat_external_dr','flat_obs_noise','flat_obs_delay','flat_action_delay','flat_scut_delay','flat_physical_delay','flat_forward_square','flat_body_mass','flat_effort_scale','flat_material','flat_velocity_push','flat_remaining_dr','flat_remaining_mixed_dr','rough_r0','rough_r1','rough_r2','rough_scut_v0','rough_scut_v1','rough_v0'],default='flat_v30')
    parser.add_argument('--job',required=True)
    parser.add_argument('--num-envs',type=int,default=16)
    parser.add_argument('--seconds',type=int,default=0)
    parser.add_argument('--resume')
    parser.add_argument('--iterations',type=int,default=100000)
    parser.add_argument('--learning-rate',type=float)
    parser.add_argument('--lr-schedule',choices=['fixed','adaptive'])
    parser.add_argument('--clip-param',type=float)
    parser.add_argument('--learning-epochs',type=int)
    parser.add_argument('--expected-parent-sha')
    parser.add_argument('--rough-probe',action='store_true')
    parser.add_argument('--teacher-demo',action='store_true')
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
            from .flat_speed_repair_env import FlatSpeedRepairEnv as EnvClass
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
        elif args.profile=='rough_scut_v1':
            from .pitch_stability_env import PitchStabilityEnv as EnvClass
            from .scut_flat_env import configuration as env_configuration,tensor
            terrain_selection='rough_scut_v1'
        elif args.profile=='rough_scut_v0':
            from .scut_rough_scut_v0_env import ScutUnifiedRoughV0Env as EnvClass
            from .scut_flat_env import configuration as env_configuration,tensor
            terrain_selection='rough_scut_v0'
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
        zero_dr_contract=dict(E1_DR_scale=0.,E0_unchanged=True,method='mixture curriculum starts at seed stage0')
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
        if args.profile in ('flat_remaining_dr','flat_remaining_mixed_dr','rough_r0','rough_r1','rough_r2','rough_scut_v0','rough_scut_v1'):
            assert torch.all((damping[:,env.gas_ids]>=1.5)&(damping[:,env.gas_ids]<=4.5))
        else:
            assert torch.all(damping[:,env.gas_ids]==3)
        if abs(float(mass[0].sum())-14.294140288606286)>.0001:raise ValueError('Asset mass mismatch')
        dr_name=env.mild_dr.summary().get('profile','mild_dr_white')
        put(job/'STARTUP.json',dict(epoch=time.time(),mode=args.mode,profile=args.profile,num_envs=args.num_envs,
            backend='PhysX TGS32/4' if args.profile!='rough_v0' else 'PhysX SCUT saved config',physics_dt_s=float(env.cfg.sim.dt),control_dt_s=float(env.cfg.sim.dt*env.cfg.decimation),decimation=int(env.cfg.decimation),env_spacing=float(env.cfg.scene.env_spacing),feedback_dt_s=.01,wheel_feedback_dt_s=.0025,
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
        if args.profile in ('rough_r0','rough_r1','rough_r2','rough_scut_v0','rough_scut_v1'):put(job/'TERRAIN_STARTUP.json',env.terrain_summary())
        if args.profile in ('rough_r2','rough_scut_v1'):put(job/'R2_STARTUP.json',env.r2_summary())
        assert args.mode=='probe' and args.seconds==0 and not plan['PPO_training_authorized']
        assert plan['authorized_PPO_seconds']==0 and not plan['PPO_training_authorized'] and not plan['human_restart_authorized']
        from .route2_common import HistoryQueue,LocalRoute2Actor,action_mlp
        history=HistoryQueue()
        def pack(raw,done=None,reset=False):
            raw=dict(raw);raw['obs_history']=history.reset(raw['policy'])if reset else history.append(raw['policy'],done);return raw
        current=pack(env._get_observations(),reset=True)
        class Vec:
            def __init__(self):self.num_envs=env.num_envs;self.num_actions=6;self.device=env.device;self.max_episode_length=env.max_episode_length;self.cfg=env.cfg
            @property
            def episode_length_buf(self):return env.episode_length_buf
            def get_observations(self):return TensorDict(current,batch_size=[env.num_envs])
        cfg=runner_config();cfg['actor']['class_name']='mod4v3_ppo_v1.route2_models:Route2PolicyModel';cfg['critic']['class_name']='mod4v3_ppo_v1.route2_models:Route2CriticModel';cfg['obs_groups']['actor']=['policy'];cfg['algorithm']['learning_rate']=.0001;cfg['algorithm']['schedule']='adaptive';cfg['clip_actions']=6.
        runner=OnPolicyRunner(Vec(),cfg,log_dir=None,device=env.device);alg=runner.alg
        ck=torch.load(plan['parent'],map_location=env.device,weights_only=False);assert ck['format']=='MOD4V3_MOE_ROUTE2_V1';alg.actor.load_state_dict(ck['actor_state_dict'],strict=True);alg.critic.load_state_dict(ck['critic_state_dict'],strict=True)
        assert hashlib.sha256(Path(plan['parent']).read_bytes()).hexdigest()==plan.get('collection_source_sha256',plan['locked_v1_sha256'])
        with torch.no_grad():alg.actor.distribution.e1_log_std.copy_(torch.tensor(plan['route2']['E1_initial_std'],device=env.device).log())
        trainable=[p for m in [alg.actor.mlp.e1,alg.critic.mlp.e1]for p in m.parameters()if p.requires_grad]+[alg.actor.distribution.e1_log_std];alg.optimizer=torch.optim.Adam(trainable,lr=.0001)
        assert all(not p.requires_grad for m in [alg.actor.mlp.e0,alg.critic.mlp.e0,alg.actor.mlp.e1.approach_base,alg.actor.mlp.e1.gate]for p in m.parameters()) and not alg.actor.distribution.e0_std.requires_grad
        assert all(p.requires_grad for p in trainable)
        ref=torch.load(Path(plan['root'])/'c874_reference.pt',map_location=env.device,weights_only=False);assert hashlib.sha256((Path(plan['root'])/'c874_reference.pt').read_bytes()).hexdigest()==plan['route2']['E0_sha256'];e0=action_mlp(35).to(env.device);e0.load_state_dict({k.removeprefix('mlp.'):v for k,v in ref['actor_state_dict'].items()if k.startswith('mlp.')});e0.requires_grad_(False)
        normal={k:v.clone()for k,v in current.items()};normal['policy'][:,28:35]=normal['policy'].new_tensor([1,0,0,0,0,0,0]);normal=TensorDict(normal,batch_size=[env.num_envs])
        with torch.no_grad():
            normal_error=float((alg.actor(normal)-e0(normal['policy'])).abs().max());alg.actor(normal,stochastic_output=True);std_error=float((alg.actor.output_std-ref['actor_state_dict']['distribution.std_param'].expand(env.num_envs,-1)).abs().max())
            local=LocalRoute2Actor().load_checkpoint({k:(v.cpu()if torch.is_tensor(v)else v)for k,v in ck.items()}).eval();obs=TensorDict(current,batch_size=[env.num_envs]);forward_error=float((alg.actor(obs).cpu()-local(current['policy'].cpu(),current['obs_history'].cpu())).abs().max())
        assert normal_error==0 and std_error==0 and forward_error<2e-5,(normal_error,std_error,forward_error)
        a=np.load(Path(plan['root'])/'probe_samples.npz');batch={k:torch.as_tensor(a[k],device=env.device)for k in a.files};training_obs=TensorDict({'policy':batch['obs'],'obs_history':batch['history'].flatten(1)},batch_size=[len(batch['obs'])]);alg.optimizer.zero_grad()
        mean=alg.actor(training_obs);alg.actor(training_obs,stochastic_output=True);logloss=-alg.actor.get_output_log_prob(mean.detach()+torch.randn_like(mean)*.3).mean();z=alg.actor.mlp.e1.encoder(training_obs['obs_history']);aux=.1*(z[:,:5]-batch['targets']).square().mean();cinput=current['critic'].clone();cinput[:,32:39]=cinput.new_tensor([0,1,0,0,0,1,0]);value=alg.critic(TensorDict({'critic':cinput},batch_size=[env.num_envs]));loss=logloss+aux+.01*value.square().mean();loss.backward()
        grads={name:dict(finite=bool(torch.isfinite(param.grad).all()),norm=float(param.grad.norm()))for name,param in alg.actor.named_parameters()if param.requires_grad and param.grad is not None};missing=[name for name,param in alg.actor.named_parameters()if param.requires_grad and param.grad is None];assert not missing and all(v['finite']and v['norm']>0 for v in grads.values()),(missing,grads)
        assert all(param.grad is None for m in [alg.actor.mlp.e0,alg.critic.mlp.e0,alg.actor.mlp.e1.approach_base,alg.actor.mlp.e1.gate]for param in m.parameters()) and alg.actor.distribution.e0_std.grad is None
        assert all(p.grad is not None and bool(torch.isfinite(p.grad).all())for p in alg.critic.mlp.e1.parameters())
        # Synthetic mean-action displacement tests anchor strength, with no parameter updates.
        e1_mean=alg.actor.mlp.e1(training_obs['policy'],training_obs['obs_history'])
        target=e1_mean.detach()+.01
        scaled=((e1_mean-target)/e1_mean.new_tensor([.18,.18,.18,.18,.25,.25])).square().mean()
        e1_parameters=[p for p in alg.actor.mlp.e1.parameters()if p.requires_grad]
        old_grad=torch.autograd.grad(.06*scaled,e1_parameters,retain_graph=True)
        new_grad=torch.autograd.grad(2.*scaled,e1_parameters)
        old_norm=float(torch.stack([g.square().sum()for g in old_grad]).sum().sqrt())
        new_norm=float(torch.stack([g.square().sum()for g in new_grad]).sum().sqrt())
        assert old_norm>0 and 33.<new_norm/old_norm<34.
        anchor_response=dict(synthetic_mean_displacement=.01,old_gradient_norm=old_norm,new_gradient_norm=new_norm,gradient_multiplier=new_norm/old_norm,parameter_updates=0,does_not_prove_future_closed_loop_preservation=True)
        alg.optimizer.zero_grad();before={k:v.clone()for k,v in alg.actor.state_dict().items()if k.startswith(('mlp.e0.','mlp.e1.approach_base.','mlp.e1.gate.'))or k=='distribution.e0_std'}
        untouched_actor={k:v.clone()for k,v in alg.actor.state_dict().items()}
        untouched_critic={k:v.clone()for k,v in alg.critic.state_dict().items()}
        # Independent CPU/GPU queue assembly, including route changes and autoresets.
        queue=HistoryQueue();rng=np.random.default_rng(67);npq=None;queue_error=0.
        for k in range(30):
            f=rng.normal(size=(4,35)).astype(np.float32);done=np.array([k%7==0,k%11==0,False,k==19]);tt=torch.as_tensor(f,device=env.device)
            if npq is None:npq=np.repeat(f[:,None],12,1);got=queue.reset(tt)
            else:npq=np.concatenate((npq[:,1:],f[:,None]),1);npq[done]=np.repeat(f[done,None],12,1);got=queue.append(tt,torch.as_tensor(done,device=env.device))
            queue_error=max(queue_error,float(np.abs(got.cpu().numpy()-npq.reshape(4,-1)).max()))
        assert queue_error==0
        # No optimizer updates: measure fixed20cm stochastic feedback under full DR.
        env.course_accounting=True;alg.train_mode();max_previous_error=0.;autoresets=0
        stall_count=0;stall_reward_max=-float('inf');normal_reward_error=0.;reward_sums={};forward_samples=0
        # Measure actual cooked20cm geometry in every stair environment.
        from isaaclab.utils.warp import raycast_mesh
        ids=env.continuous_stair_mask.nonzero().flatten();terrain=env.terrain
        column=terrain.terrain_types[ids];row=terrain.terrain_levels[ids]
        centers=terrain.terrain_origins[row,column];starts=centers.repeat_interleave(2,0).clone();starts[:,2]+=2.;starts[1::2,0]+=2.
        directions=torch.zeros_like(starts);directions[:,2]=-1.
        hits=raycast_mesh(starts,directions,terrain.r1_wp_mesh,max_dist=5.)[0];cooked_heights=hits[::2,2]-hits[1::2,2]
        assert torch.allclose(cooked_heights,torch.full_like(cooked_heights,.20),atol=1e-5)
        assert len(env.speed_limits)==6 and abs(float(env.speed_limits[0])-1.2)<1e-5
        assert bool((env.stair_height[ids]-.4091).abs().max()<1e-5)

        from .start_offset_partition import OFFSETS_MM,population_by_dr_offset
        offset_population=population_by_dr_offset(ids,env.reference_nominal_env_mask,env.start_offset_index)
        assert bool((offset_population>0).all()),offset_population.tolist()
        assert int(offset_population.sum())==819 and env.num_envs==2048
        assert bool((offset_population.max(1).values-offset_population.min(1).values<=1).all())
        expected_offset=env.command.new_tensor(OFFSETS_MM)[env.start_offset_index[ids]]
        assert bool((env.start_offset_mm[ids]==0).all()),'seed starts center only; five offsets are next success-gated phase'
        assert bool((env._action_delay_ticks[ids]==0).all())and bool((env._sensor_delay_ticks[ids]==0).all())
        assert bool((env.full_dr.body_mass_scale[ids]==1).all())and bool((env.full_dr.startup_com_delta[ids]==0).all())
        assert bool((env.full_dr.leg_gain_scale[ids]==1).all())and bool((env.full_dr.wheel_gain_scale[ids]==1).all())
        assert bool((env.full_dr.effort_scale[ids]==1).all())and bool((env.full_dr.torque_noise_scale[ids]==0).all())
        assert torch.equal(env.full_dr.nominal_env_mask[~env.continuous_stair_mask],env.reference_nominal_env_mask[~env.continuous_stair_mask])
        put(job/'OFFSET_COVERAGE.json',dict(offsets_mm=list(OFFSETS_MM),rows=['reference_DR_group','reference_nominal_group'],population=offset_population.tolist(),all_10_planned_cells_populated=True,actual_seed_offsets_mm=[0],PPO_updates=0,optimizer_updates=0))
        from .startup_telemetry import StartupTelemetry
        startup=StartupTelemetry(env)
        from .success_replay import NativeSuccessRecorder
        recorder=NativeSuccessRecorder(env,job/'success_replay',plan.get('collection_source_sha256',plan['locked_v1_sha256']))
        dense_ledger={name:dict(frames=0,new_total=0.,old_total_same_states=0.,new_positive=0,old_positive=0,dense=0.)for name in ['single','double']}

        for k in range(600):
            obs=TensorDict(current,batch_size=[env.num_envs])
            with torch.inference_mode():
                action=alg.actor(obs,stochastic_output=True).clamp(-6,6)
                recorder.push(obs,action)
                raw,reward,term,timeout,extra=env.step(action)
                recorder.finish(term|timeout)
            done=term|timeout;current=pack(raw,done);b=current['obs_history'].reshape(-1,12,35);assert torch.equal(b[:,-1],current['policy']);autoresets+=int(done.sum())
            if bool(done.any()):assert torch.equal(b[done],current['policy'][done,None].expand(-1,12,-1))
            max_previous_error=max(max_previous_error,float((current['policy'][:,22:28]-env.actions).abs().max()))
            fresh_reset=done&env.continuous_stair_mask
            if bool(fresh_reset.any()):
                assert float(current['policy'][fresh_reset,4:7].abs().max())<1e-6
                assert float(current['policy'][fresh_reset,16:22].abs().max())<1e-6
                expected_g=current['policy'].new_tensor([__import__('math').sin(.02),0.,-__import__('math').cos(.02)])
                assert float((current['policy'][fresh_reset,7:10]-expected_g).abs().max())<2e-6
            assert bool(torch.isfinite(reward).all())
            parts=env.last_reward_breakdown
            if parts is not None:
                startup.observe(parts,done)
                penalties=parts['penalties']
                old_total=parts['total']-parts['top_dense']-.5*env.replay_completion_bonus-19*penalties[:,7]-24*penalties[:,8]-4*penalties[:,5]
                for name,count_top in [('single',1),('double',2)]:
                    selected=env.continuous_stair_mask&parts['top_reward_eligible']&(parts['top_support_count']==count_top)
                    row=dense_ledger[name];row['frames']+=int(selected.sum());row['new_total']+=float(parts['total'][selected].sum());row['old_total_same_states']+=float(old_total[selected].sum());row['new_positive']+=int((parts['total'][selected]>0).sum());row['old_positive']+=int((old_total[selected]>0).sum());row['dense']+=float(parts['top_dense'][selected].sum())

                pure=parts['pure_stall'];count=int(pure.sum());stall_count+=count
                if count:stall_reward_max=max(stall_reward_max,float(parts['total'][pure].max()))
                normal=~env.continuous_stair_mask
                normal_reward_error=max(normal_reward_error,float((parts['total'][normal]-parts['base'][normal]).abs().max()))
                forward_samples+=int((env.continuous_stair_mask&(parts['command_vx']>.1)).sum())
                for key in ['base','positive_base_removed','event','top_dense','total']:reward_sums[key]=reward_sums.get(key,0.)+float(parts[key][env.continuous_stair_mask].sum())
            if k%100==99:put(job/'PROBE_PROGRESS.json',dict(policy_steps=k+1,attempts=env.course_attempts.tolist(),completions=env.course_successes.tolist(),PPO_updates=0,optimizer_updates=0))
        assert stall_count>0 and stall_reward_max<0 and normal_reward_error==0,(stall_count,stall_reward_max,normal_reward_error)
        frozen_error=max(float((v-alg.actor.state_dict()[k]).abs().max())for k,v in before.items());assert frozen_error==0 and not env.enforce_closure_reset
        actor_change=max(float((v-alg.actor.state_dict()[k]).abs().max())for k,v in untouched_actor.items())
        critic_change=max(float((v-alg.critic.state_dict()[k]).abs().max())for k,v in untouched_critic.items())
        assert actor_change==0 and critic_change==0
        result=dict(passed=True,architecture_passed=True,skill_graduated=False,PPO_updates=0,optimizer_updates=0,normal_action_max_error=normal_error,normal_STD_max_error=std_error,normal_gradient_norm=0.,normal_parameter_max_change=frozen_error,Isaac_MuJoCo_forward_max_error=forward_error,history_queue_max_error=queue_error,E1_gradient_parameters=grads,E1_missing_gradients=missing,E1_STD=alg.actor.distribution.e1_log_std.exp().detach().cpu().tolist(),history_always_updated=True,shared_previous_raw_executed_action_max_error=max_previous_error,autoresets=autoresets,policy_steps=600,physics_steps=4800,physics_dt=float(env.cfg.sim.dt),policy_dt=.02,leg_feedback_dt=.01,wheel_feedback_dt=.0025,stair_envs=int(env.continuous_stair_mask.sum()),normal_envs=int((~env.continuous_stair_mask).sum()),heights=[.2],attempts_DR_then_nominal=env.course_attempts.tolist(),completions_DR_then_nominal=env.course_successes.tolist(),strict_completions=int(env.strict_success_count),height_population=torch.bincount(env.course_level[env.continuous_stair_mask],minlength=1).tolist(),environment_DR_summary=env.mild_dr.summary(),E1_DR_level=0.,E0_retains_original_full_DR=True,closure2mm_diagnostic_only=True,training_authorized=False,all_actor_parameter_max_change=actor_change,all_critic_parameter_max_change=critic_change,offsets_mm=list(OFFSETS_MM),offset_population_DR_then_nominal=offset_population.tolist(),offset_attempts_DR_then_nominal=env.offset_attempts.tolist(),offset_completion_events_DR_then_nominal=env.offset_completion_events.tolist(),stochastic_training_forward=True,actual_cooked_heights_minmax_m=[float(cooked_heights.min()),float(cooked_heights.max())],stall_without_progress_samples=stall_count,maximum_stall_net_reward=stall_reward_max,normal_reward_max_error=normal_reward_error,reward_component_sums_E1=reward_sums,forward_command_samples=forward_samples,training_speed_limits_m_s=env.speed_limits.tolist(),true_top_completion_events_DR_then_nominal=env.true_top_completion_events.tolist())
        recorder.write_manifest()
        result['success_replay']=recorder.summary()
        result['dense_reward_ledger']=dense_ledger
        result['collection_source_sha256']=plan.get('collection_source_sha256',plan['locked_v1_sha256'])
        result['zero_DR_contract']=zero_dr_contract
        result['E1_DR_curriculum']=env.dr_course.summary()
        result['reset_sensor_cache']=env.reset_sensor_cache_stats
        result['actual_physical_seed_offsets_mm']=env.start_offset_mm[ids].tolist()
        result['full_DR_graduation']=False
        result['anchor_gradient_response']=anchor_response
        result['startup_diagnostics']=startup.finish()
        put(job/'STARTUP_DIAGNOSTICS.json',result['startup_diagnostics'])
        result['source_sha256']={name:hashlib.sha256((Path(plan['support'])/name).read_bytes()).hexdigest()for name in ['single_step_geometry.py','mod4v3_ppo_v1/single_step_math.py','mod4v3_ppo_v1/continuous_stair_env.py','mod4v3_ppo_v1/fixed200_reward_math.py','mod4v3_ppo_v1/route2_common.py','mod4v3_ppo_v1/route2_models.py','mod4v3_ppo_v1/start_offset_partition.py','mod4v3_ppo_v1/route2_optimizer.py','mod4v3_ppo_v1/route2_train.py','mod4v3_ppo_v1/e1_dr_mixture.py','mod4v3_ppo_v1/dr_curriculum_env.py','mod4v3_ppo_v1/pitch_stability_env.py','mod4v3_ppo_v1/reset_sensor_refresh.py']}
        for name in ['dense_top_reward.py','success_replay.py']:result['source_sha256']['mod4v3_ppo_v1/'+name]=hashlib.sha256((Path(plan['support'])/'mod4v3_ppo_v1'/name).read_bytes()).hexdigest()
        result['startup_pose_sha256']=hashlib.sha256((Path(plan['root'])/'startup_pose.json').read_bytes()).hexdigest()
        result['source_sha256']['mod4v3_ppo_v1/startup_telemetry.py']=hashlib.sha256((Path(plan['support'])/'mod4v3_ppo_v1/startup_telemetry.py').read_bytes()).hexdigest()
        put(job/'ROUTE2_NATIVE_PREFLIGHT.json',result);print('ROUTE2_NATIVE_PREFLIGHT',json.dumps(result),flush=True)
    except BaseException:
        put(job/'ERROR.json',dict(epoch=time.time(),traceback=traceback.format_exc(),PPO_updates=0,optimizer_updates=0));raise
    finally:
        if env is not None:env.close()
        put(job/'SAFE_CLOSED.json',dict(epoch=time.time(),scene_closed=True,PPO_updates=0,optimizer_updates=0));app.close()
if __name__=='__main__':main()
