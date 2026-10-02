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
        count=z();tilt2=z();velerr2=z();ang2=z();wheel_both=z();wheel_any=z()
        d2=z();dd2=z();d_count=z();dd_count=z()
        early_done=torch.zeros(n,dtype=torch.bool,device=dev)
        prev=None;prev_delta=None;prev_valid=torch.zeros_like(early_done)
        max_closure=0.0;max_mimic=0.0
        gas_min=float('inf');gas_max=float('-inf')
        pitch_sum=z();roll_abs_sum=z();action_sum=torch.zeros(6,device=dev);wheel_vel_sum=z();vx_sum=z()
        for step in range(args.steps):
            if step%100==0: print("[flat-eval] step",step,flush=True)
            with torch.inference_mode():
                actions=policy(obs)
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
