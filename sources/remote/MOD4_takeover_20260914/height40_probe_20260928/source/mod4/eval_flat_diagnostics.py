"""Deterministic 15-second flat-ground audit for a saved MOD4 policy."""
from __future__ import annotations
import hashlib,json,math,os
from pathlib import Path
import torch
from eval_episodes_mod4 import args,app,mod4_task,Mod4Env,build_runner,RslRlVecEnvWrapper,MANIFEST_PATH

def scalar(x):
    return float(x.detach().item())
def main():
    if os.environ.get('RM_MOD4_MAP') != 'fudan_plane':
        raise ValueError('flat evaluator requires the Fudan plane contract')
    dest=Path(args.report)
    if not args.report or dest.exists():
        raise ValueError('provide a new --report path')
    cfg=mod4_task.Mod4EnvCfg()
    cfg.scene.num_envs=args.num_envs
    cfg.seed=args.seed
    env=Mod4Env(cfg=cfg)
    try:
        vec=RslRlVecEnvWrapper(env,clip_actions=6.0)
        policy=build_runner(vec,args.checkpoint,MANIFEST_PATH)
        env.reset(seed=args.seed)
        obs=vec.get_observations()
        n=env.num_envs;dev=env.device
        z=lambda:torch.zeros(n,device=dev)
        masses=torch.tensor([mod4_task.CONTRACT["bodies"][name]["mass_kg"] for name in env.scene["robot"].body_names],device=dev)
        total_mass=masses.sum()
        count=z();tilt2=z();velerr2=z();ang2=z();wheel_both=z();wheel_any=z()
        d2=z();dd2=z();d_count=z();dd_count=z()
        early_done=torch.zeros(n,dtype=torch.bool,device=dev)
        prev=None;prev_delta=None;prev_valid=torch.zeros_like(early_done)
        max_closure=0.0;max_mimic=0.0
        gas_min=float('inf');gas_max=float('-inf')
        pitch_sum=z();roll_abs_sum=z();action_sum=torch.zeros(6,device=dev);wheel_vel_sum=z();vx_sum=z()
        root_z_sum=z();root_z_min=torch.full((n,),float("inf"),device=dev);root_z_max=z()
        leg_q_sum=torch.zeros((n,4),device=dev);leg_tau_abs_sum=torch.zeros((n,4),device=dev)
        leg_tau_sat_sum=torch.zeros((n,4),device=dev);leg_vel_abs_sum=torch.zeros((n,4),device=dev)
        wheel_force_sum=z();guide_force_sum=z();guide_touch_sum=z();chassis_force_sum=z()
        com_wheel_dx_sum=z();com_wheel_dz_sum=z();com_wheel_dx_abs_sum=z()
        wheel_tau_abs_sum=z();wheel_tau_sat_sum=z()
        guide_body_force_sum=torch.zeros(8,device=dev);guide_body_touch_sum=torch.zeros(8,device=dev)
        guide_body_names=list(env.scene.sensors["guide_contact"].body_names)
        for step in range(args.steps):
            if step%100==0: print("[flat-eval] step",step,flush=True)
            with torch.inference_mode():
                actions=policy(obs)
            if os.environ.get("RM_EVAL_LEG_SWEEP") == "1":
                ids=torch.arange(n,device=dev)
                crank_grid=torch.tensor([-1.0,-0.8,-0.6,-0.4,-0.2,0.0,0.2,0.4],device=dev)
                hip_grid=torch.tensor([-0.6,-0.3,0.0,0.3,0.5,0.7,0.9,1.0],device=dev)
                actions=actions.clone()
                actions[:,0]=actions[:,2]=crank_grid[ids//8]
                actions[:,1]=actions[:,3]=hip_grid[ids%8]
            leg_override=os.environ.get("RM_EVAL_LEG_OVERRIDE")
            if leg_override is not None:
                crank,hip=[float(v) for v in leg_override.split(",")]
                actions=actions.clone()
                actions[:,0]=crank;actions[:,1]=hip;actions[:,2]=crank;actions[:,3]=hip
            wheel_override=os.environ.get('RM_EVAL_WHEEL_OVERRIDE')
            if wheel_override is not None:
                actions=actions.clone()
                actions[:,4:6]=float(wheel_override)
            if not bool(torch.isfinite(actions).all()):
                raise RuntimeError('nonfinite action')
            obs,reward,dones,extras=vec.step(actions)
            good=~dones.bool()
            if step<args.steps-1:early_done|=dones.bool()
            active=good & ~early_done
            robot=env.scene['robot']
            grav=robot.data.projected_gravity_b
            tilt=torch.rad2deg(torch.acos((-grav[:,2]).clamp(-1,1)))
            ang=torch.linalg.vector_norm(robot.data.root_ang_vel_b[:,:2],dim=1)
            cmd=env.command_manager.get_term('twist').command
            verr=torch.linalg.vector_norm(robot.data.root_lin_vel_b[:,:2]-cmd[:,:2],dim=1)
            force=env.scene.sensors['wheel_contact'].data.net_forces_w
            if hasattr(force,'torch'):force=force.torch
            touch=force.norm(dim=-1)>1.0
            m=active.float()
            count+=m;tilt2+=m*tilt.square();velerr2+=m*verr.square();ang2+=m*ang.square()
            pitch_sum+=m*torch.rad2deg(torch.asin(grav[:,0].clamp(-1,1)))
            roll_abs_sum+=m*torch.rad2deg(torch.asin(grav[:,1].clamp(-1,1))).abs()
            action_sum+=(m[:,None]*actions).sum(dim=0)
            wids=[robot.joint_names.index(x) for x in mod4_task.WHEEL_ORDER]
            wheel_vel_sum+=m*robot.data.joint_vel[:,wids].mean(dim=1)
            vx_sum+=m*robot.data.root_lin_vel_b[:,0]
            root_z=robot.data.root_pos_w[:,2]
            root_z_sum+=m*root_z
            root_z_min=torch.minimum(root_z_min,torch.where(good,root_z,root_z_min))
            root_z_max=torch.maximum(root_z_max,torch.where(good,root_z,root_z_max))
            leg_ids=[robot.joint_names.index(x) for x in mod4_task.LEG_ORDER]
            leg_q_sum+=m[:,None]*robot.data.joint_pos[:,leg_ids]
            tau=robot.data.applied_torque[:,leg_ids].abs()
            leg_tau_abs_sum+=m[:,None]*tau
            leg_tau_sat_sum+=m[:,None]*(tau>=39.5).float()
            leg_vel_abs_sum+=m[:,None]*robot.data.joint_vel[:,leg_ids].abs()
            wheel_force_sum+=m*force.norm(dim=-1).sum(dim=1)
            gf=env.scene.sensors["guide_contact"].data.net_forces_w
            guide_force_sum+=m*gf.norm(dim=-1).sum(dim=1)
            guide_touch_sum+=m*(gf.norm(dim=-1)>1.0).any(dim=1).float()
            guide_body_force_sum+=(m[:,None]*gf.norm(dim=-1)).sum(dim=0)
            guide_body_touch_sum+=(m[:,None]*(gf.norm(dim=-1)>1.0).float()).sum(dim=0)
            cf=env.scene.sensors["chassis_contact"].data.net_forces_w
            chassis_force_sum+=m*cf.norm(dim=-1).sum(dim=1)
            body_com=robot.data.body_com_pos_w
            if hasattr(body_com,"torch"):body_com=body_com.torch
            com_w=(body_com*masses[None,:,None]).sum(dim=1)/total_mass
            body_pos=robot.data.body_pos_w
            if hasattr(body_pos,"torch"):body_pos=body_pos.torch
            wheel_bid=[robot.body_names.index(x) for x in ("left_wheel","right_wheel")]
            wheel_w=body_pos[:,wheel_bid,:].mean(dim=1)
            dx=com_w[:,0]-wheel_w[:,0];dz=com_w[:,2]-wheel_w[:,2]
            com_wheel_dx_sum+=m*dx;com_wheel_dz_sum+=m*dz;com_wheel_dx_abs_sum+=m*dx.abs()
            wt=robot.data.applied_torque[:,wids].abs()
            wheel_tau_abs_sum+=m*wt.sum(dim=1)
            wheel_tau_sat_sum+=m*(wt>=mod4_task.WHEEL_EFFORT*0.99).any(dim=1).float()
            wheel_both+=m*touch.all(dim=1).float()
            wheel_any+=m*touch.any(dim=1).float()
            if prev is not None:
                da=actions-prev
                valid=prev_valid&active
                d2+=valid.float()*da.square().mean(dim=1)
                d_count+=valid.float()
                if prev_delta is not None:
                    v2=valid&prev_delta_valid
                    dd2+=v2.float()*(da-prev_delta).square().mean(dim=1)
                    dd_count+=v2.float()
                prev_delta=da
                prev_delta_valid=valid
            prev=actions.detach();prev_valid=active
            max_closure=max(max_closure,float(getattr(env,'_mod4_max_closure',0.0)))
            max_mimic=max(max_mimic,float(getattr(env,'_mod4_max_mimic',0.0)))
            gf=getattr(env,'_mod4_gas_force_ref_realized_n',None)
            if gf is not None:
                gas_min=min(gas_min,scalar(gf.min()))
                gas_max=max(gas_max,scalar(gf.max()))
        denom=count.clamp_min(1)
        tilt_rms=(tilt2/denom).sqrt()
        verr_rms=(velerr2/denom).sqrt()
        ang_rms=(ang2/denom).sqrt()
        contact=wheel_both/denom
        delta=(d2/d_count.clamp_min(1)).sqrt()
        delta2=(dd2/dd_count.clamp_min(1)).sqrt()
        survived=~early_done
        quality=(tilt_rms<=8)&(verr_rms<=0.75)&(ang_rms<=1.5)&(contact>=0.9)&(delta<=0.18)&(delta2<=0.25)
        passed=survived&quality&(count>=args.steps-1)
        report={
          'checkpoint':str(Path(args.checkpoint).resolve()),
          'checkpoint_sha256':hashlib.sha256(Path(args.checkpoint).read_bytes()).hexdigest(),
          'manifest':MANIFEST_PATH,'map':'fudan_plane',
          'domain_rand':bool(args.domain_rand),'seed':args.seed,
          'num_envs':n,'steps':args.steps,'step_dt':env.step_dt,
          'test_horizon_survived':int(survived.sum().item()),
          'test_horizon_pass':int(passed.sum().item()),
          'episode_15s_survived':int(survived.sum().item()) if args.steps>=1500 else None,
          'episode_15s_pass':int(passed.sum().item()) if args.steps>=1500 else None,
          'tilt_deg_rms':scalar((tilt2.sum()/count.sum().clamp_min(1)).sqrt()),
          'ang_xy_rad_s_rms':scalar((ang2.sum()/count.sum().clamp_min(1)).sqrt()),
          'velocity_error_xy_m_s_rms':scalar((velerr2.sum()/count.sum().clamp_min(1)).sqrt()),
          'both_wheels_contact_rate':scalar(wheel_both.sum()/count.sum().clamp_min(1)),
          'pitch_signed_mean_deg':scalar(pitch_sum.sum()/count.sum().clamp_min(1)),
          'roll_abs_mean_deg':scalar(roll_abs_sum.sum()/count.sum().clamp_min(1)),
          'action_mean':(action_sum/count.sum().clamp_min(1)).tolist(),
          'wheel_vel_mean_rad_s':scalar(wheel_vel_sum.sum()/count.sum().clamp_min(1)),
          'root_vx_mean_m_s':scalar(vx_sum.sum()/count.sum().clamp_min(1)),
          'root_z_mean_m':scalar(root_z_sum.sum()/count.sum().clamp_min(1)),
          'root_z_min_m':scalar(root_z_min.min()),'root_z_max_m':scalar(root_z_max.max()),
          'leg_q_mean_rad':(leg_q_sum.sum(dim=0)/count.sum().clamp_min(1)).tolist(),
          'leg_tau_abs_mean_nm':(leg_tau_abs_sum.sum(dim=0)/count.sum().clamp_min(1)).tolist(),
          'leg_tau_sat_fraction':(leg_tau_sat_sum.sum(dim=0)/count.sum().clamp_min(1)).tolist(),
          'leg_vel_abs_mean_rad_s':(leg_vel_abs_sum.sum(dim=0)/count.sum().clamp_min(1)).tolist(),
          'wheel_force_norm_sum_mean_n':scalar(wheel_force_sum.sum()/count.sum().clamp_min(1)),
          'guide_force_norm_sum_mean_n':scalar(guide_force_sum.sum()/count.sum().clamp_min(1)),
          'guide_touch_rate':scalar(guide_touch_sum.sum()/count.sum().clamp_min(1)),
          'guide_body_names':guide_body_names,
          'guide_body_force_mean_n':(guide_body_force_sum/count.sum().clamp_min(1)).tolist(),
          'guide_body_touch_rate':(guide_body_touch_sum/count.sum().clamp_min(1)).tolist(),
          'chassis_force_norm_sum_mean_n':scalar(chassis_force_sum.sum()/count.sum().clamp_min(1)),
          'total_mass_kg':scalar(total_mass),
          'com_minus_wheel_axle_x_mean_m':scalar(com_wheel_dx_sum.sum()/count.sum().clamp_min(1)),
          'com_minus_wheel_axle_x_abs_mean_m':scalar(com_wheel_dx_abs_sum.sum()/count.sum().clamp_min(1)),
          'com_minus_wheel_axle_z_mean_m':scalar(com_wheel_dz_sum.sum()/count.sum().clamp_min(1)),
          'single_support_gravity_pitch_moment_nm':scalar(total_mass*9.81*com_wheel_dx_abs_sum.sum()/count.sum().clamp_min(1)),
          'wheel_torque_abs_sum_mean_nm':scalar(wheel_tau_abs_sum.sum()/count.sum().clamp_min(1)),
          'wheel_torque_any_saturated_rate':scalar(wheel_tau_sat_sum.sum()/count.sum().clamp_min(1)),
          'per_env_tilt_rms_deg':(tilt2/denom).sqrt().tolist(),
          'per_env_root_z_mean_m':(root_z_sum/denom).tolist(),
          'per_env_com_minus_wheel_x_m':(com_wheel_dx_sum/denom).tolist(),
          'per_env_com_minus_wheel_z_m':(com_wheel_dz_sum/denom).tolist(),
          'per_env_wheel_both_rate':(wheel_both/denom).tolist(),
          'per_env_vx_mean_m_s':(vx_sum/denom).tolist(),
          'per_env_pitch_mean_deg':(pitch_sum/denom).tolist(),
          'per_env_survived':survived.tolist(),
          'leg_sweep':os.environ.get('RM_EVAL_LEG_SWEEP')=='1',
          'any_wheel_contact_rate':scalar(wheel_any.sum()/count.sum().clamp_min(1)),
          'action_delta_rms':scalar((d2.sum()/d_count.sum().clamp_min(1)).sqrt()),
          'action_second_diff_rms':scalar((dd2.sum()/dd_count.sum().clamp_min(1)).sqrt()),
          'max_closure_error_m':max_closure,'max_mimic_error_rad':max_mimic,
          'gas_elastic_force_min_n':None if gas_min==float('inf') else gas_min,
          'gas_elastic_force_max_n':None if gas_max==float('-inf') else gas_max,
          'acceptance':{'tilt_deg_rms':8,'velocity_error_xy_m_s_rms':0.75,
                        'ang_xy_rad_s_rms':1.5,'both_wheels_contact_rate':0.9,
                        'action_delta_rms':0.18,'action_second_diff_rms':0.25}}
        dest.write_text(json.dumps(report,indent=2)+'\n')
        print(json.dumps(report,indent=2),flush=True)
    finally:
        env.close()
if __name__=='__main__':
    import traceback
    try:main()
    except BaseException:
        crash=traceback.format_exc()
        Path(args.report+'.crash.txt').write_text(crash)
        print(crash,flush=True)
        raise
    finally:app.close()
