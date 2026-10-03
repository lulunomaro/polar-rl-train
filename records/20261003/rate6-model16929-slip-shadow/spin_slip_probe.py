"""Frozen 6-action policy, explicit pure yaw, physical evidence and no PPO.

The old policy is NOT required to know the new yaw commands before training.
Physical safety and yaw-skill acceptance are separate reported gates. 15-second
skill evidence must include signed yaw, turns, drift, stop and real load/gap.
"""
import argparse,json,os,time,traceback
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--checkpoint',required=True);p.add_argument('--output',required=True)
p.add_argument('--steps',type=int,default=500);p.add_argument('--num_envs',type=int,default=72)
p.add_argument('--seed',type=int,default=20261002);p.add_argument('--max-rate',type=float,default=3.);p.add_argument('--dr-profile',choices=['nominal','white_v1','white_v2','white_v3'],default='white_v1')
for k,v in json.loads(Path(__file__).with_name('env.json').read_text()).items():os.environ[k]=str(v)
from isaaclab.app import AppLauncher
AppLauncher.add_app_launcher_args(p);args=p.parse_args();os.environ['RM_MILD_DR_PROFILE']=args.dr_profile
assert 2 <= args.max_rate <= float(os.environ['RM_SPIN_MAX_RAD_S']) + 1e-8
app=AppLauncher(args).app
import torch
from mod4_env import Mod4Env
import mod4_task as task
from spin_commands import audit
from nominal_parameter_audit import parameter_audit
from contact_geometry import ControlGeometry
from slip_shadow import SlipShadow
from actuator_clip_diagnostics import rating_clipped
from isaaclab_rl.rsl_rl import RslRlOnPolicyRunnerCfg,RslRlPpoActorCriticCfg,RslRlPpoAlgorithmCfg,RslRlVecEnvWrapper,handle_deprecated_rsl_rl_cfg
from rsl_rl.runners import OnPolicyRunner
from importlib import metadata


@torch.inference_mode()
def main():
    torch.manual_seed(args.seed)
    cfg=task.Mod4EnvCfg();cfg.seed=args.seed;cfg.scene.num_envs=args.num_envs
    env=Mod4Env(cfg=cfg);vec=RslRlVecEnvWrapper(env,clip_actions=6.)
    robot=env.scene['robot'];dev=env.device;n=env.num_envs
    rc=RslRlOnPolicyRunnerCfg(seed=args.seed,device=dev,num_steps_per_env=24,max_iterations=1,save_interval=1,
        experiment_name='spin_probe',run_name='frozen',clip_actions=6.,check_for_nan=True,
        obs_groups={'actor':['policy'],'critic':['critic']},
        policy=RslRlPpoActorCriticCfg(init_noise_std=.3,actor_hidden_dims=[256,128,64],critic_hidden_dims=[256,128,64],activation='elu'),
        algorithm=RslRlPpoAlgorithmCfg(value_loss_coef=2.,use_clipped_value_loss=True,clip_param=.2,entropy_coef=.005,
            num_learning_epochs=5,num_mini_batches=4,learning_rate=1e-4,schedule='adaptive',gamma=.99,lam=.95,desired_kl=.01,max_grad_norm=1.))
    rc=handle_deprecated_rsl_rl_cfg(rc,metadata.version('rsl-rl-lib'))
    runner=OnPolicyRunner(vec,rc.to_dict(),log_dir=None,device=dev);runner.load(args.checkpoint)
    policy=runner.get_inference_policy(device=dev)
    env.reset();cmd=env.command_manager.get_term('twist');initial_command_audit=audit(env);initial_parameters=parameter_audit(env)
    groups=[dict(vx=0.,wz=0.,profile='stand'),dict(vx=.3,wz=0.,profile='straight'),dict(vx=1.,wz=0.,profile='straight'),
            dict(vx=0.,wz=1.,profile='spin'),dict(vx=0.,wz=-1.,profile='spin'),
            dict(vx=0.,wz=2.,profile='spin'),dict(vx=0.,wz=-2.,profile='spin'),
            dict(vx=0.,wz=args.max_rate,profile='spin'),dict(vx=0.,wz=-args.max_rate,profile='spin'),
            dict(vx=0.,wz=args.max_rate,profile='spin_ramp_stop_reverse'),dict(vx=0.,wz=-args.max_rate,profile='spin_ramp_stop_reverse')]
    if n%len(groups):raise ValueError('Number of environments must be divisible by eleven')
    gids=torch.arange(n,device=dev)%len(groups)
    vx=torch.tensor([g['vx'] for g in groups],device=dev)[gids]
    yaw=torch.tensor([g['wz'] for g in groups],device=dev)[gids]
    ramp=gids>=9
    alive=torch.ones(n,dtype=torch.bool,device=dev);counts=torch.zeros(n,device=dev)
    initial_q=robot.data.joint_pos.cpu().tolist();initial_root=robot.data.root_state_w.cpu().tolist()
    root0=robot.data.root_pos_w[:,:2].clone();posmax=counts.clone();peaktilt=counts.clone();gapmax=counts.clone()
    unloadmax=counts.clone();wheel_speed_peak=counts.clone();wheel_torque_peak=counts.clone();turns=counts.clone();absolute_turns=counts.clone();firstfail=torch.full((n,),args.steps,device=dev,dtype=torch.long)
    last=torch.zeros((n,6),device=dev);last2=last.clone();closed=0.;mimic=0.;nonfinite=False
    names=['yaw_rate','yaw_error','speed_error','tilt','height_error','delta','d2','left_fz','right_fz',
           'guide_force','base_force','wheel_rating_clip','leg_rating_clip','left_slip','right_slip','spin_translation_speed']
    sums={k:counts.clone() for k in names};stopcount=counts.clone();stoperr=counts.clone()
    geom=ControlGeometry(env,task.USD_PATH);capture=env._integrated_contact
    shadow=SlipShadow(env,geom);shadow.trace_ids=torch.where((gids==7)|(gids==8))[0]
    wheel_ids,_=robot.find_joints(task.WHEEL_ORDER,preserve_order=True)
    start=time.time()
    for step in range(args.steps):
        t=step*env.step_dt
        factor=0. if t<.5 else min(1.,(t-.5)/1.) if t<5. else max(0.,1.-(t-5.)/1.5) if t<9. else -min(1.,(t-9.)/1.) if t<13. else -max(0.,1.-(t-13.)/1.)
        desired_yaw=torch.where(ramp,yaw*factor,yaw)
        cmd.time_left[:]=1e9;cmd.is_standing_env[:]=False;cmd.is_heading_env[:]=False
        cmd.command[:]=0;cmd.command[:,0]=vx;cmd.command[:,2]=desired_yaw
        audit(env);task.height_cmd(env)[:]=.25
        action=policy(vec.get_observations());_,_,done,_=vec.step(action)
        firstfail=torch.where(alive & done.bool(),torch.full_like(firstfail,step),firstfail);alive &= ~done.bool()
        if not torch.isfinite(robot.data.joint_pos).all() or not torch.isfinite(action).all():nonfinite=True;break
        valid=env.episode_length_buf>=10
        if valid.any():
            closed=max(closed,float(torch.stack(list(task.closure_errors(env).values()))[:,valid].max()))
            mimic=max(mimic,float(torch.stack(list(task.mimic_errors(env).values()))[:,valid].max()))
        mask=alive & (step>=50);counts+=mask
        tilt=torch.acos((-robot.data.projected_gravity_b[:,2]).clamp(-1,1))*180/torch.pi
        rate=robot.data.root_ang_vel_w[:,2]
        turns+=torch.where(alive,rate*env.step_dt/(2*torch.pi),0.)
        absolute_turns+=torch.where(alive,rate.abs()*env.step_dt/(2*torch.pi),0.)
        gap,slip=geom.read()
        if step==50:capture.off_max.zero_()
        gapmax=torch.maximum(gapmax,torch.where(mask,gap.max(1).values,0.))
        unloadmax=torch.maximum(unloadmax,torch.where(mask,capture.off_max.float()*env.physics_dt,0.))
        posmax=torch.maximum(posmax,torch.where(mask,(robot.data.root_pos_w[:,:2]-root0).norm(dim=1),0.))
        peaktilt=torch.maximum(peaktilt,torch.where(mask,tilt,0.))
        wheel_speed_peak=torch.maximum(wheel_speed_peak,torch.where(mask,robot.data.joint_vel[:,wheel_ids].abs().max(1).values,0.))
        wheel_torque_peak=torch.maximum(wheel_torque_peak,torch.where(mask,robot.actuators['wheels'].applied_effort.abs().max(1).values,0.))
        fz=capture.impulse/env.step_dt
        shadow.read(slip,fz,mask,step)
        values=dict(yaw_rate=rate,yaw_error=(rate-desired_yaw).abs(),speed_error=(robot.data.root_lin_vel_b[:,0]-vx).abs(),
            tilt=tilt,height_error=(task.root_height_above_ground(env)-.25).abs(),
            delta=(action-last).abs().mean(1),d2=(action-2*last+last2).abs().mean(1),left_fz=fz[:,0],right_fz=fz[:,1],
            guide_force=env.scene.sensors['guide_contact'].data.net_forces_w.norm(dim=-1).sum(1),
            base_force=env.scene.sensors['chassis_contact'].data.net_forces_w.norm(dim=-1).sum(1),
            wheel_rating_clip=rating_clipped(robot.actuators['wheels']).float().mean(1),
            leg_rating_clip=rating_clipped(robot.actuators['legs']).float().mean(1),left_slip=slip[:,0],right_slip=slip[:,1],
            spin_translation_speed=robot.data.root_lin_vel_w[:,:2].norm(dim=1))
        for k,v in values.items():sums[k]+=v*mask
        stopped=ramp & (((t>=8.) and (t<9.)) or (t>=14.5));stopcount+=mask & stopped
        stoperr+=rate.abs()*(mask & stopped)
        last2=last;last=action.clone()
    per={k:v/counts.clamp_min(1) for k,v in sums.items()}
    per.update(peak_wheel_speed_rad_s=wheel_speed_peak,peak_wheel_applied_torque_nm=wheel_torque_peak,peak_tilt=peaktilt,maximum_gap_m=gapmax,longest_both_low_s=unloadmax,net_signed_turns=turns,absolute_turns=absolute_turns,
               root_xy_excursion_m=posmax,stop_yaw_abs=stoperr/stopcount.clamp_min(1))
    physical=(alive & (counts>0) & (peaktilt<=15) & (per['height_error']<=.03)
              & (per['base_force']<=1) & (per['guide_force']<=1)
              & (per['wheel_rating_clip']<=.2) & (per['leg_rating_clip']<=.2))
    skill=(physical & (per['yaw_error']<=torch.maximum(torch.full_like(yaw,.2),yaw.abs()*.2))
           & (per['speed_error']<=torch.maximum(torch.full_like(vx,.12),vx.abs()*.25))
           & (per['tilt']<=8) & (per['peak_tilt']<=12)
           & (per['left_slip']<=.15) & (per['right_slip']<=.15) & (per['delta']<=.18) & (per['d2']<=.25)
           & (per['maximum_gap_m']<=.002) & (per['longest_both_low_s']<=.01501)
           & (per['left_fz']>=10) & (per['right_fz']>=10)
           & ((yaw==0) | (per['spin_translation_speed']<=.12))
           & (~ramp | (per['stop_yaw_abs']<=.2)))
    rows=[]
    for gid,g in enumerate(groups):
        ids=gids==gid;row=dict(g,group_id=gid,environments=int(ids.sum()),survival_fraction=float(alive[ids].float().mean()),
            physical_smoke_fraction=float(physical[ids].float().mean()),spin_skill_fraction=float(skill[ids].float().mean()))
        row['means']={k:float(v[ids].mean()) for k,v in per.items()}
        row['worst']={k:float(per[k][ids].max()) for k in ['peak_wheel_speed_rad_s','peak_wheel_applied_torque_nm','peak_tilt','maximum_gap_m','longest_both_low_s','height_error','wheel_rating_clip','leg_rating_clip']}
        rows.append(row)
    result=dict(probe_version='spin_rate_v1_same_gates_control_rate_motor_peaks',probe_sha256=__import__('hashlib').sha256(Path(__file__).read_bytes()).hexdigest(),target_rate_rad_s=args.max_rate,mode='frozen_deterministic_spin_rate_probe',checkpoint=args.checkpoint,seed=args.seed,steps=args.steps,
        seconds=args.steps*env.step_dt,profile=args.dr_profile,groups=rows,nonfinite=nonfinite,max_closure_m=closed,max_mimic_rad=mimic,
        physical_smoke_pass=not nonfinite and closed<=.002 and mimic<=.01 and all(r['physical_smoke_fraction']>=.95 for r in rows),
        spin_skill_pass=args.steps*env.step_dt>=15 and not nonfinite and closed<=.002 and mimic<=.01 and all(r['spin_skill_fraction']>=.8 for r in rows),
        initial_command_audit=initial_command_audit,initial_parameter_audit=initial_parameters,reset_joint_pos_before_physics=initial_q,reset_root_before_physics=initial_root,final_parameter_audit=parameter_audit(env),
        observations={k:list(v.shape) for k,v in env.observation_manager.compute().items()},
        per_environment={k:v.cpu().tolist() for k,v in per.items()},alive=alive.cpu().tolist(),group_ids=gids.cpu().tolist(),first_failure_step=firstfail.cpu().tolist(),
        elapsed_s=time.time()-start,ppo_performed=False,
        scope='Physical smoke does not require an untrained policy to track yaw. Spin skill pass requires 15s. Gap/slip proxy and torque are control-step sampled; load/off duration are 0.5ms captured. Stage one has NO spin translation.')
    result['slip_shadow']=shadow.result(args.output+'.trace.npz')
    Path(args.output).write_text(json.dumps(result,indent=2));print('SPIN_PROBE_RESULT',json.dumps({k:v for k,v in result.items() if k not in ['per_environment','groups','initial_parameter_audit','final_parameter_audit','reset_joint_pos_before_physics','reset_root_before_physics','alive','group_ids','first_failure_step']}),flush=True)
    env.close()


try:main()
except BaseException:
    error=traceback.format_exc();Path(args.output+'.error.txt').write_text(error);print(error,flush=True);raise
finally:app.close()
