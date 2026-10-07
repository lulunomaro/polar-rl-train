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
p.add_argument('--contact-readback',action='store_true')
p.add_argument('--manual-reference',action='store_true')
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
from actuator_clip_diagnostics import rating_clipped
from isaaclab_rl.rsl_rl import RslRlOnPolicyRunnerCfg,RslRlPpoActorCriticCfg,RslRlPpoAlgorithmCfg,RslRlVecEnvWrapper,handle_deprecated_rsl_rl_cfg
from rsl_rl.runners import OnPolicyRunner
from importlib import metadata


@torch.inference_mode()
def main():
    torch.manual_seed(args.seed)
    cfg=task.Mod4EnvCfg();cfg.seed=args.seed;cfg.scene.num_envs=args.num_envs
    cfg.scene.wheel_contact_scut.filter_prim_paths_expr=['/World/ground/geometry/mesh']
    cfg.scene.wheel_contact_scut.max_contact_data_count_per_prim=64
    env=Mod4Env(cfg=cfg);vec=RslRlVecEnvWrapper(env,clip_actions=6.)
    robot=env.scene['robot'];dev=env.device;n=env.num_envs
    from frozen_history_policy import build_frozen_policy
    vec,policy,policy_observer=build_frozen_policy(vec,args.checkpoint,dev)
    env.reset();cmd=env.command_manager.get_term('twist');initial_command_audit=audit(env);initial_parameters=parameter_audit(env)
    if hasattr(cmd,'set_manual_evaluation_mode'):cmd.set_manual_evaluation_mode()
    import math, numpy as np
    from world_cycle_metrics import measure_world_cycles
    from spin_translation_math import body_command
    groups=[dict(vx=0.,wz=0.,profile='stand'),dict(vx=.3,wz=0.,profile='straight'),dict(vx=1.,wz=0.,profile='straight')]
    groups += [dict(vx=0.,wz=w,profile='world_directional',direction=a) for w,a in [(1.,0.),(-1.,0.),(2.,0.),(-2.,0.),(2.,math.pi/2),(-2.,math.pi/2),(2.,math.pi/3),(-2.,math.pi/3)]]
    if n%len(groups):raise ValueError('Number of environments must be divisible by eleven')
    gids=torch.arange(n,device=dev)%len(groups)
    vx=torch.tensor([g['vx'] for g in groups],device=dev)[gids]
    yaw=torch.tensor([g['wz'] for g in groups],device=dev)[gids]
    ramp=torch.zeros_like(gids,dtype=torch.bool)
    moving=gids>=3
    direction=torch.tensor([g.get('direction',0.) for g in groups],device=dev)[gids]
    goal=float(os.environ['RM_SPIN_WORLD_PROGRESS_M_S'])
    cmd.manual_evaluation_mode=args.manual_reference
    cmd.is_pure_spin[:]=False;cmd.is_moving_spin[:]=moving;cmd.is_transition_spin[:]=False
    cmd.world_direction[:]=direction;cmd.signed_yaw[:]=yaw;cmd.phase_elapsed[:]=0.
    trace_xy=[robot.data.root_pos_w[:,:2].clone()];trace_heading=[robot.data.heading_w.torch.clone()]
    command_observation_error=0.;reward_readback_error=0.;reward_samples=[]
    reward_original=env.reward_manager.compute
    def reward_checked(dt):
        nonlocal reward_readback_error
        manager=env.reward_manager; selected=[]
        for index,(name,term) in enumerate(zip(manager._term_names,manager._term_cfgs)):
            if name in ('track_lin_vel','track_ang_vel'):
                expected=term.func(env,**term.params)*term.weight
                selected.append((index,name,expected.clone()))
        result=reward_original(dt)
        for index,name,expected in selected:
            actual=manager._step_reward[:,index]
            reward_readback_error=max(reward_readback_error,float((actual-expected).abs().max()))
            if len(reward_samples)<12:
                reward_samples.append(dict(term=name,command=cmd.command[:11].cpu().tolist(),expected_per_s=expected[:11].cpu().tolist(),actual_per_s=actual[:11].cpu().tolist()))
        return result
    env.reward_manager.compute=reward_checked
    alive=torch.ones(n,dtype=torch.bool,device=dev);counts=torch.zeros(n,device=dev)
    initial_q=robot.data.joint_pos.cpu().tolist();initial_root=robot.data.root_state_w.cpu().tolist()
    root0=robot.data.root_pos_w[:,:2].clone();posmax=counts.clone();peaktilt=counts.clone();gapmax=counts.clone()
    unloadmax=counts.clone();wheel_speed_peak=counts.clone();wheel_torque_peak=counts.clone();turns=counts.clone();absolute_turns=counts.clone();firstfail=torch.full((n,),args.steps,device=dev,dtype=torch.long)
    last=torch.zeros((n,6),device=dev);last2=last.clone();closed=0.;mimic=0.;nonfinite=False
    names=['yaw_rate','yaw_error','speed_error','tilt','height_error','delta','d2','left_fz','right_fz',
           'guide_force','base_force','wheel_rating_clip','leg_rating_clip','left_slip','right_slip','spin_translation_speed','left_slip_legacy_reference','right_slip_legacy_reference']
    sums={k:counts.clone() for k in names};stopcount=counts.clone();stoperr=counts.clone()
    geom=ControlGeometry(env,task.USD_PATH);capture=env._integrated_contact
    contact=None
    if args.contact_readback:
        from substep_contact_readback import SubstepContactReadback
        contact=SubstepContactReadback(env,geom)
    shadows={k:torch.zeros((n,2),device=dev) for k in ('midplane_mean_speed','midplane_mean_rolling_abs','scut_vertical_bottom_mean_speed','midplane_loaded_mean_speed','midplane_load_samples','scut_history_masked_mean_speed','scut_history_samples')}
    wheel_ids,_=robot.find_joints(task.WHEEL_ORDER,preserve_order=True)
    start=time.time()
    for step in range(args.steps):
        t=step*env.step_dt
        factor=0. if t<.5 else min(1.,(t-.5)/1.) if t<5. else max(0.,1.-(t-5.)/1.5) if t<9. else -min(1.,(t-9.)/1.) if t<13. else -max(0.,1.-(t-13.)/1.)
        desired_yaw=torch.where(ramp,yaw*factor,yaw)
        cmd.time_left[:]=1e9;cmd.is_standing_env[:]=False;cmd.is_heading_env[:]=False
        if args.manual_reference:
            vx=torch.where(moving,body_command(goal,direction,robot.data.heading_w.torch,1.5)[0],vx)
        else:
            cmd._write_dynamic(torch.arange(n,device=dev))
            vx=torch.where(moving,cmd.command[:,0],vx)
        cmd.command[:]=0;cmd.command[:,0]=vx;cmd.command[:,2]=desired_yaw
        expected=2*goal*torch.cos(robot.data.heading_w.torch-direction)
        assert float((cmd.command[moving,0]-expected[moving]).abs().max())<1e-6
        actual_obs=env.observation_manager.compute()
        for group in ('policy','critic'):
            command_observation_error=max(command_observation_error,float((actual_obs[group][:,:3]-cmd.command).abs().max()))
        audit(env);task.height_cmd(env)[:]=.25
        if contact:contact.begin_control(alive & (step>=50))
        action=policy(vec.get_observations());_,_,done,_=vec.step(action)
        trace_xy.append(robot.data.root_pos_w[:,:2].clone());trace_heading.append(robot.data.heading_w.torch.clone())
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
        rolling=env._spin_rolling_consistency
        values_shadow=rolling.last
        mid=values_shadow['point_velocity'][...,:2].norm(dim=-1)
        vertical=torch.zeros((n,2,3),device=dev);vertical[...,2]=-rolling.radius.squeeze(-1)
        scutvel=(robot.data.body_link_lin_vel_w[:,geom.ids]+torch.cross(robot.data.body_ang_vel_w[:,geom.ids],vertical,dim=-1))[...,:2].norm(dim=-1)
        history=env.scene.sensors['wheel_contact_scut'].data.net_forces_w_history.norm(dim=-1).max(dim=1).values>1.
        loaded=(fz>=10.) & mask[:,None];hist=history & mask[:,None]
        shadows['midplane_mean_speed']+=mid*mask[:,None]
        shadows['midplane_mean_rolling_abs']+=values_shadow['rolling_signed'].abs()*mask[:,None]
        shadows['scut_vertical_bottom_mean_speed']+=scutvel*mask[:,None]
        shadows['midplane_loaded_mean_speed']+=mid*loaded
        shadows['midplane_load_samples']+=loaded
        shadows['scut_history_masked_mean_speed']+=scutvel*hist
        shadows['scut_history_samples']+=hist
        values=dict(yaw_rate=rate,yaw_error=(rate-desired_yaw).abs(),speed_error=(robot.data.root_lin_vel_b[:,0]-vx).abs(),
            tilt=tilt,height_error=(task.root_height_above_ground(env)-.25).abs(),
            delta=(action-last).abs().mean(1),d2=(action-2*last+last2).abs().mean(1),left_fz=fz[:,0],right_fz=fz[:,1],
            guide_force=env.scene.sensors['guide_contact'].data.net_forces_w.norm(dim=-1).sum(1),
            base_force=env.scene.sensors['chassis_contact'].data.net_forces_w.norm(dim=-1).sum(1),
            wheel_rating_clip=rating_clipped(robot.actuators['wheels']).float().mean(1),
            leg_rating_clip=rating_clipped(robot.actuators['legs']).float().mean(1),left_slip=slip[:,0],right_slip=slip[:,1],
            spin_translation_speed=robot.data.root_lin_vel_w[:,:2].norm(dim=1),left_slip_legacy_reference=geom.legacy_reference_slip[:,0],right_slip_legacy_reference=geom.legacy_reference_slip[:,1])
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
    skill_legacy_reference=(physical & (per['yaw_error']<=torch.maximum(torch.full_like(yaw,.2),yaw.abs()*.2))
           & (per['speed_error']<=torch.maximum(torch.full_like(vx,.12),vx.abs()*.25))
           & (per['tilt']<=8) & (per['peak_tilt']<=12)
           & (per['left_slip_legacy_reference']<=.15) & (per['right_slip_legacy_reference']<=.15) & (per['delta']<=.18) & (per['d2']<=.25)
           & (per['maximum_gap_m']<=.002) & (per['longest_both_low_s']<=.01501)
           & (per['left_fz']>=10) & (per['right_fz']>=10)
           & ((yaw==0) | (per['spin_translation_speed']<=.12))
           & (~ramp | (per['stop_yaw_abs']<=.2)))
    rows=[]
    for gid,g in enumerate(groups):
        ids=gids==gid;row=dict(g,group_id=gid,environments=int(ids.sum()),survival_fraction=float(alive[ids].float().mean()),
            physical_smoke_fraction=float(physical[ids].float().mean()),spin_skill_fraction=float(skill[ids].float().mean()),spin_skill_fraction_legacy_reference=float(skill_legacy_reference[ids].float().mean()))
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
        scope='World-directed low-rate spin translation. Actual full-turn net progress is measured separately from learning admission. Original numerical skill booleans remain diagnostic. Gap/slip proxy and torque are control-step sampled; load/off duration use the actual reported physics timestep.')
    result.update(geometry_reference_version=geom.reference_version,spin_skill_pass_legacy_reference=args.steps*env.step_dt>=15 and not nonfinite and closed<=.002 and mimic<=.01 and all(r['spin_skill_fraction_legacy_reference']>=.8 for r in rows),geometry_thresholds_changed=False)
    for key in ('midplane_mean_speed','midplane_mean_rolling_abs','scut_vertical_bottom_mean_speed'):shadows[key]/=counts[:,None].clamp_min(1)
    shadows['midplane_loaded_mean_speed']/=shadows['midplane_load_samples'].clamp_min(1)
    shadows['scut_history_masked_mean_speed']/=shadows['scut_history_samples'].clamp_min(1)
    result['calibration_control_shadow']={k:v.cpu().tolist() for k,v in shadows.items()}
    result['calibration_geometry']=rolling.metadata
    result['calibration_scope']='Read-only shadows; SCUT-style uses correct link reference and input-mesh radius. No old acceptance boolean changed.'
    if contact:result['substep_contact_readback']=contact.result()
    xy=torch.stack(trace_xy).cpu().numpy();head=torch.stack(trace_heading).cpu().numpy()
    world=[]
    for i in range(n):
        if not bool(moving[i]):continue
        failed=int(firstfail[i])<args.steps
        limit=int(firstfail[i])+1 if failed else -1
        m=measure_world_cycles(np.arange(len(xy))*env.step_dt,xy[:,i],head[:,i],float(direction[i]),1 if float(yaw[i])>0 else -1,limit)
        validxy=xy[:limit,i] if failed else xy[:,i]
        cross=(validxy-validxy[0])@np.array([-math.sin(float(direction[i])),math.cos(float(direction[i]))])
        m.update(env_id=i,group_id=int(gids[i]),command_yaw_rad_s=float(yaw[i]),world_direction_rad=float(direction[i]),goal_m_s=goal,cross_peak_to_peak_m=float(np.ptp(cross)))
        world.append(m)
    tracepath=Path(args.output).with_suffix('.npz')
    np.savez_compressed(tracepath,root_xy=xy,heading=head,group_ids=gids.cpu().numpy(),first_failure=firstfail.cpu().numpy())
    assert command_observation_error<1e-6,command_observation_error
    assert reward_readback_error<1e-4,reward_readback_error
    result.update(world_cycle_metrics=world,command_observation_error=command_observation_error,reward_readback_error=reward_readback_error,reward_readback_samples=reward_samples,automatic_sdk_commands=not args.manual_reference,
        whole_trace=dict(path=str(tracepath),sha256=__import__('hashlib').sha256(tracepath.read_bytes()).hexdigest()),goal_m_s=goal,world_feedback_installed=False)
    result['frozen_architecture_audit']=policy_observer.audit()
    Path(args.output).write_text(json.dumps(result,indent=2));print('SPIN_PROBE_RESULT',json.dumps({k:v for k,v in result.items() if k not in ['per_environment','groups','initial_parameter_audit','final_parameter_audit','reset_joint_pos_before_physics','reset_root_before_physics','alive','group_ids','first_failure_step']}),flush=True)
    env.close()


try:main()
except BaseException:
    error=traceback.format_exc();Path(args.output+'.error.txt').write_text(error);print(error,flush=True);raise
finally:app.close()
