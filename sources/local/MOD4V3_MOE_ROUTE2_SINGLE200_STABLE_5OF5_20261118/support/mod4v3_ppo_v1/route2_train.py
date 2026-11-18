"""Train the independent Route2 stair expert within the new explicitly authorized budget; never reuse an old clock."""
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
    parser.add_argument('--mode',choices=['train'],default='train')
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
    assert plan.get('PPO_training_authorized') and plan.get('human_restart_authorized'), 'Human restart authorization required before native app or job creation'
    assert 0 < args.seconds == plan['authorized_PPO_seconds'] == plan['strict_timing']['maximum_seconds'] <= 7200
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
        assert args.mode=='train' and plan['PPO_training_authorized'] and args.seconds==plan['authorized_PPO_seconds'] and args.seconds>60
        assert hashlib.sha256(Path(plan['parent']).read_bytes()).hexdigest()==plan['locked_v1_sha256']
        from .route2_common import HistoryQueue,action_mlp
        from .route2_optimizer import route2_update
        import types,copy
        history=HistoryQueue()
        def pack(raw,done=None,reset=False):
            raw=dict(raw)
            raw['obs_history']=history.reset(raw['policy']) if reset else history.append(raw['policy'],done)
            raw['settle_anchor']=((env.episode_length_buf*env.step_dt<1.0)&(raw['policy'][:,0].abs()<.05)&(raw['policy'][:,3]>1.7)).float().unsqueeze(1)
            return raw
        current=pack(env._get_observations(),reset=True)
        class Vec:
            def __init__(self):
                self.num_envs=env.num_envs;self.num_actions=6;self.device=env.device
                self.max_episode_length=env.max_episode_length;self.cfg=env.cfg
            @property
            def episode_length_buf(self):return env.episode_length_buf
            def get_observations(self):return TensorDict(current,batch_size=[env.num_envs])
        cfg=runner_config()
        cfg['actor']['class_name']='mod4v3_ppo_v1.route2_models:Route2PolicyModel'
        cfg['critic']['class_name']='mod4v3_ppo_v1.route2_models:Route2CriticModel'
        cfg['obs_groups']['actor']=['policy'];cfg['clip_actions']=6.
        cfg['num_steps_per_env']=24
        cfg['algorithm'].update(learning_rate=1e-4,schedule='adaptive',clip_param=.05,desired_kl=.006,num_learning_epochs=3,num_mini_batches=4)
        runner=OnPolicyRunner(Vec(),cfg,log_dir=None,device=env.device);algorithm=runner.alg
        ck=torch.load(plan['parent'],map_location=env.device,weights_only=False)
        assert ck['format']=='MOD4V3_MOE_ROUTE2_V1'
        algorithm.actor.load_state_dict(ck['actor_state_dict'],strict=True)
        algorithm.critic.load_state_dict(ck['critic_state_dict'],strict=True)
        algorithm.initial_v1_e1=copy.deepcopy(algorithm.actor.mlp.e1).eval().requires_grad_(False)
        with torch.no_grad():algorithm.actor.distribution.e1_log_std.copy_(torch.tensor(plan['route2']['E1_initial_std'],device=env.device).log())
        algorithm.initial_exploration_std=algorithm.actor.distribution.e1_log_std.detach().exp().clone()
        algorithm.v1_anchor_action_scale=algorithm.initial_exploration_std.new_tensor([.18,.18,.18,.18,.25,.25])
        assert all(not p.requires_grad for p in algorithm.initial_v1_e1.parameters())
        trainable=[p for m in [algorithm.actor.mlp.e1,algorithm.critic.mlp.e1] for p in m.parameters() if p.requires_grad]+[algorithm.actor.distribution.e1_log_std]
        assert all(p.requires_grad for p in trainable)
        algorithm.optimizer=torch.optim.Adam(trainable,lr=1e-4)
        algorithm.learning_rate=1e-4
        algorithm.completed_PPO_updates=0
        from .success_replay import SuccessReplayPool,NativeSuccessRecorder
        algorithm.success_replay=SuccessReplayPool()
        for folder in plan.get('bootstrap_replay_dirs',[]):algorithm.success_replay.load_directory(folder)
        assert algorithm.success_replay.frames>0,'Qualified native success replay must be collected before PPO'
        success_recorder=NativeSuccessRecorder(env,job/'success_replay',plan['locked_v1_sha256'],algorithm.success_replay)

        algorithm.update=types.MethodType(route2_update,algorithm)
        with torch.no_grad():
            probe_mean=algorithm.actor.mlp.e1(current['policy'],current['obs_history'])
            reference_mean=algorithm.initial_v1_e1(current['policy'],current['obs_history'])
            initial_anchor_mean_error=float((probe_mean-reference_mean).abs().max())
        assert initial_anchor_mean_error==0.

        ref_path=Path(plan['root'])/'c874_reference.pt'
        assert hashlib.sha256(ref_path.read_bytes()).hexdigest()==plan['route2']['E0_sha256']
        ref=torch.load(ref_path,map_location=env.device,weights_only=False)
        for k,v in ref['actor_state_dict'].items():
            if k.startswith('mlp.'):
                assert torch.equal(v,algorithm.actor.state_dict()['mlp.e0.'+k.removeprefix('mlp.')])
        assert torch.equal(ref['actor_state_dict']['distribution.std_param'],algorithm.actor.distribution.e0_std)
        frozen_actor={k:v.clone() for k,v in algorithm.actor.state_dict().items() if k.startswith(('mlp.e0.','mlp.e1.approach_base.','mlp.e1.gate.')) or k=='distribution.e0_std'}
        frozen_critic={k:v.clone() for k,v in algorithm.critic.mlp.e0.state_dict().items()}
        initial_e1={k:v.clone() for k,v in algorithm.actor.state_dict().items() if (k.startswith('mlp.e1.') and not k.startswith(('mlp.e1.approach_base.','mlp.e1.gate.'))) or k=='distribution.e1_log_std'}
        initial_c1={k:v.clone() for k,v in algorithm.critic.mlp.e1.state_dict().items()}
        def isolation():
            change=max(float((algorithm.actor.state_dict()[k]-v).abs().max()) for k,v in frozen_actor.items())
            cchange=max(float((algorithm.critic.mlp.e0.state_dict()[k]-v).abs().max()) for k,v in frozen_critic.items())
            assert change==0. and cchange==0.
            assert all(not p.requires_grad and p.grad is None for m in [algorithm.actor.mlp.e0,algorithm.critic.mlp.e0,algorithm.actor.mlp.e1.approach_base,algorithm.actor.mlp.e1.gate] for p in m.parameters())
            return dict(E0_actor_STD_max_change=change,E0_critic_max_change=cchange,E0_gradient_norm=0.)
        from .start_offset_partition import population_by_dr_offset
        def curriculum():
            mask=env.continuous_stair_mask
            return dict(heights_m=[.20],height_population=torch.bincount(env.course_level[mask],minlength=1).tolist(),attempts_DR_then_nominal=env.course_attempts.tolist(),completions_DR_then_nominal=env.course_successes.tolist(),true_top_completion_events_DR_then_nominal=env.true_top_completion_events.tolist(),top_latch_04s_events_DR_then_nominal=env.top_latch_events.tolist(),step_regression_terminations=int(env.step_regression_terminations),offset_completion_events_DR_then_nominal=env.offset_completion_events.tolist(),offset_attempts_DR_then_nominal=env.offset_attempts.tolist(),offset_population_reference_groups=population_by_dr_offset(mask.nonzero().flatten(),env.reference_nominal_env_mask,env.actual_start_offset_index).tolist(),E1_DR_curriculum=env.dr_course.summary(),reset_sensor_cache=getattr(env,'reset_sensor_cache_stats',None),speed_limits_m_s=env.speed_limits.tolist(),speed_stage_population=torch.bincount(env.speed_stage[mask],minlength=6).tolist(),speed_completions=env.speed_completed.tolist(),strict_completions_all_heights=int(env.strict_success_count))
        iteration=0;adam_steps=0;physics_ticks=0;partial_update=False;last=None;assessment40_done=False;pending40=False;early_stop_info=None
        class TrainingBudgetReached(Exception):pass
        algorithm.train_mode();env.begin_training_counts()
        import datetime
        start_mono=time.monotonic();start_epoch=time.time()
        original_deadline=None
        effective_seconds=float(args.seconds)
        assert effective_seconds==plan['authorized_PPO_seconds'], 'Explicit new training duration required'
        deadline=start_mono+effective_seconds;stop_work=deadline-60.
        from .startup_telemetry import StartupTelemetry
        startup=StartupTelemetry(env)
        def check_budget():
            nonlocal assessment40_done,pending40,early_stop_info
            elapsed=time.monotonic()-start_mono
            if elapsed>=2400. and not assessment40_done:
                assessment40_done=True
                events=env.true_top_completion_events.tolist()
                if sum(events)==0:
                    early_stop_info=dict(reason='40m_zero_true20cm_stable_completion',elapsed_seconds=elapsed,true_top_completion_events_DR_then_nominal=events,curriculum=curriculum(),safe_save_requested=True)
                    put(job/'EARLY_STOP.json',early_stop_info)
                    raise TrainingBudgetReached()
                pending40=True
            if time.monotonic()>=stop_work or (job/'REQUEST_STOP').exists():raise TrainingBudgetReached()
        algorithm.check_budget=check_budget
        original_step=algorithm.optimizer.step
        def counted_step(*a,**kw):
            nonlocal adam_steps
            check_budget()
            result=original_step(*a,**kw);adam_steps+=1
            return result
        algorithm.optimizer.step=counted_step
        put(job/'TRAINING_CLOCK.json',dict(epoch=start_epoch,requested_seconds=args.seconds,effective_this_run_seconds=effective_seconds,planned_end_epoch=start_epoch+effective_seconds,strict_max_seconds=args.seconds,superseded_original_absolute_deadline_epoch=original_deadline,previous_attempt_seconds=plan['restart_policy']['previous_elapsed_seconds'],save_close_reserve_seconds=60,monotonic_start=start_mono,work_cutoff_monotonic=stop_work,deadline_monotonic=deadline,automatic_restart=False,automatic_extension=False,automatic_promotion=False,parent_sha256=plan['locked_v1_sha256']))
        def save(name):
            success_recorder.write_manifest()
            data=algorithm.save()
            data['success_replay_state']=algorithm.success_replay.checkpoint_state()
            data['success_replay_summary']=success_recorder.summary()
            data['top_dense_reward_sum']=float(env.top_dense_reward_sum)
            data.update(frozen_v1_E1_state_dict=algorithm.initial_v1_e1.state_dict(),initial_exploration_std=algorithm.initial_exploration_std,v1_anchor_action_scale=algorithm.v1_anchor_action_scale,early_stop=early_stop_info,format='MOD4V3_MOE_ROUTE2_V1',iter=iteration,PPO_updates_in_experiment=iteration,actual_Adam_steps=adam_steps,partial_update=partial_update,route2=plan['route2'],route2_recipe=plan['route2'],action_order=env.order,num_envs=env.num_envs,learning_rate=algorithm.learning_rate,training_elapsed_seconds=time.monotonic()-start_mono,source_asset=plan['asset_identity'],continuous_stair=plan['continuous_stair'],curriculum_summary=curriculum(),terrain_curriculum_state=env.terrain_checkpoint_state(),r2_curriculum_state=env.r2_checkpoint_state(),domain_randomization_state=env.full_dr.checkpoint_state() if hasattr(env.full_dr,'checkpoint_state') else None,cpu_rng=torch.get_rng_state(),cuda_rng=torch.cuda.get_rng_state_all(),python_rng=random.getstate(),numpy_rng=np.random.get_state(),reset_rng=env.reset_generator.get_state(),reward_tensors={k:v for k,v in vars(env.reward).items() if torch.is_tensor(v)},reward_sums=env.reward._episode_sums,done_totals=env.done_totals,physics_ticks=physics_ticks,full_DR=env.mild_dr.summary(),normal_isolation=isolation(),resume_scope='complete PPO/Adam/STD/RNG/DR/course; fresh physical episodes; no automatic restart',clock=dict(start_epoch=start_epoch,deadline_epoch=start_epoch+effective_seconds))
            output=job/name;tmp=output.with_name(output.name+'.partial')
            with tmp.open('wb') as stream:
                torch.save(data,stream);stream.flush();os.fsync(stream.fileno())
            os.replace(tmp,output)
            return dict(path=str(output),SHA=hashlib.sha256(output.read_bytes()).hexdigest(),bytes=output.stat().st_size,iteration=iteration,actual_Adam_steps=adam_steps,elapsed_seconds=time.monotonic()-start_mono)
        obs=TensorDict(current,batch_size=[env.num_envs]);next_checkpoint=300.
        put(job/'PREUPDATE_ISOLATION.json',dict(**isolation(),locked_v1_sha256=plan['locked_v1_sha256'],optimizer_trainable_parameter_tensors=len(trainable),no_keep=True,no_teacher=True,hard_route=True,initial_v1_anchor_mean_error=initial_anchor_mean_error,runtime_E1_STD=algorithm.initial_exploration_std.tolist(),learning_rate=algorithm.learning_rate,clip_param=algorithm.clip_param))
        while time.monotonic()<stop_work:
            tick=time.monotonic();rewards=0.
            try:
                with torch.inference_mode():
                    for _ in range(24):
                        check_budget()
                        action=algorithm.act(obs)
                        success_recorder.push(obs,action.clamp(-6,6),algorithm.completed_PPO_updates)
                        raw,reward,term,timeout,extra=env.step(action)
                        success_recorder.finish(term|timeout)
                        startup.observe(env.last_reward_breakdown,term|timeout)
                        raw=pack(raw,term|timeout)
                        terminal=TensorDict(env.terminal_observations,batch_size=[env.num_envs])
                        reward=reward+algorithm.gamma*algorithm.critic(terminal).squeeze(-1)*timeout
                        obs=TensorDict(raw,batch_size=[env.num_envs])
                        if not all(bool(torch.isfinite(v).all()) for v in obs.values()) or not bool(torch.isfinite(reward).all()):raise ValueError('Nonfinite observation or reward')
                        algorithm.process_env_step(obs,reward,term|timeout,{})
                        physics_ticks+=8;rewards+=float(reward.mean())
                    algorithm.compute_returns(obs)
                losses=algorithm.update()
            except TrainingBudgetReached:
                partial_update=True;break
            iteration+=1
            elapsed=time.monotonic()-start_mono
            last=dict(epoch=time.time(),iteration=iteration,actual_Adam_steps=adam_steps,training_elapsed_seconds=elapsed,iteration_seconds=time.monotonic()-tick,mean_reward=rewards/24,losses=losses,curriculum=curriculum(),E1_STD=algorithm.actor.distribution.e1_log_std.detach().exp().tolist(),success_replay=success_recorder.summary(),top_dense_reward_sum=float(env.top_dense_reward_sum),done_totals={k:int(v.sum()) if torch.is_tensor(v) else v for k,v in env.done_totals.items()},normal_isolation=isolation(),startup_diagnostics=startup.finish(include_rows=False))
            parts=env.last_reward_breakdown
            if parts is not None:
                pure=parts['pure_stall'];last['reward_gate']=dict(last_pure_stall_samples=int(pure.sum()),last_pure_stall_max_net_reward=float(parts['total'][pure].max())if bool(pure.any())else None,last_positive_base_removed_sum=float(parts['positive_base_removed'].sum()),course_quality_penalty_sums=env.course_quality_penalty_sum.tolist())
            put(job/'LATEST_PROGRESS.json',last)
            print('ROUTE2_PROGRESS',json.dumps(last),flush=True)
            if iteration==1:
                state=algorithm.actor.state_dict()
                groups={name:max(float((state[k]-v).abs().max()) for k,v in initial_e1.items() if k.startswith(prefix)) for name,prefix in [('E1_head','mlp.e1.head.'),('E1_top_head','mlp.e1.top_head.'),('E1_encoder','mlp.e1.encoder.'),('E1_STD','distribution.e1_log_std')]}
                groups['E1_critic']=max(float((algorithm.critic.mlp.e1.state_dict()[k]-v).abs().max()) for k,v in initial_c1.items())
                assert groups['E1_critic']>0 and all(groups[k]==0. for k in ['E1_head','E1_top_head','E1_encoder','E1_STD']),groups
                receipt=save('model_first_complete.pt')
                put(job/'FIRST_UPDATE.json',dict(**last,checkpoint=receipt,trainable_group_max_changes=groups,critic_warmup_active=True,actor_changed=False))
            if iteration==16:
                state=algorithm.actor.state_dict()
                groups={name:max(float((state[k]-v).abs().max()) for k,v in initial_e1.items() if k.startswith(prefix)) for name,prefix in [('E1_head','mlp.e1.head.'),('E1_top_head','mlp.e1.top_head.'),('E1_encoder','mlp.e1.encoder.'),('E1_STD','distribution.e1_log_std')]}
                groups['E1_critic']=max(float((algorithm.critic.mlp.e1.state_dict()[k]-v).abs().max()) for k,v in initial_c1.items())
                assert all(v>0 for v in groups.values()),groups
                receipt16=save('model_first_actor_complete.pt')
                put(job/'FIRST_ACTOR_UPDATE.json',dict(**last,checkpoint=receipt16,trainable_group_max_changes=groups,critic_warmup_active=False,actor_changed=True))
            if elapsed>=next_checkpoint:
                minute=int(next_checkpoint/60);receipt=save(f'model_{minute:03d}m.pt')
                put(job/f'PERIODIC_{minute:03d}M.json',receipt);put(job/'PERIODIC_FULL.json',receipt)
                next_checkpoint+=300.
            if pending40:
                pending40=False
                put(job/'WAITING_040M_ASSESSMENT.json',dict(epoch=time.time(),checkpoint='model_040m.pt',updates_paused=True,elapsed_seconds=time.monotonic()-start_mono,deadline_unchanged=True))
                verdict_path=job/'STOP_VERDICT_040M.json'
                try:
                    while not verdict_path.exists():
                        check_budget();time.sleep(1.)
                    verdict=json.loads(verdict_path.read_text())
                    put(job/'ASSESSMENT_040M_CONSUMED.json',dict(epoch=time.time(),verdict=verdict))
                    if verdict['stop']:
                        early_stop_info=dict(reason='40m_independent_E1_collapsed_no_top_progress',elapsed_seconds=time.monotonic()-start_mono,verdict=verdict,safe_save_requested=True)
                        put(job/'EARLY_STOP.json',early_stop_info)
                        break
                except TrainingBudgetReached:break
        if early_stop_info is not None and not (job/'model_040m.pt').exists():
            receipt40=save('model_040m.pt');put(job/'PERIODIC_040M.json',receipt40)
        put(job/'STARTUP_DIAGNOSTICS_FINAL.json',startup.finish())
        receipt=save('model_final.pt')
        put(job/'FINAL.json',dict(epoch=time.time(),checkpoint=receipt,last_progress=last,elapsed_seconds=time.monotonic()-start_mono,actual_Adam_steps=adam_steps,early_stop=early_stop_info,partial_update=partial_update,strict_deadline_epoch=start_epoch+effective_seconds,stopped_before_deadline=time.monotonic()<deadline,safe_close_requested=True,normal_isolation=isolation()))
    except BaseException:
        put(job/'ERROR.json',dict(epoch=time.time(),traceback=traceback.format_exc()))
        raise
    finally:
        if env is not None:env.close()
        put(job/'SAFE_CLOSED.json',dict(epoch=time.time(),scene_closed=True))
        app.close()

if __name__=='__main__':main()
