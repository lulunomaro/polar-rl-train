"""Deterministic physical reset / policy acceptance; never runs PPO."""
import argparse
import json
import os
from pathlib import Path
import sys
import time

p=argparse.ArgumentParser();p.add_argument('--checkpoint',default='');p.add_argument('--output',required=True)
p.add_argument('--steps',type=int,default=1500);p.add_argument('--num_envs',type=int,default=64)
p.add_argument('--reset_smoke',action='store_true');p.add_argument('--seed',type=int,default=20260926)
for k,v in json.loads(Path(__file__).with_name('env.json').read_text()).items():os.environ[k]=str(v)
from isaaclab.app import AppLauncher
AppLauncher.add_app_launcher_args(p);args=p.parse_args()
app=AppLauncher(args).app
import torch
from mod4_env import Mod4Env
import mod4_task as task
from isaaclab_rl.rsl_rl import RslRlOnPolicyRunnerCfg,RslRlPpoActorCriticCfg,RslRlPpoAlgorithmCfg,RslRlVecEnvWrapper,handle_deprecated_rsl_rl_cfg
from importlib import metadata
from rsl_rl.runners import OnPolicyRunner


@torch.inference_mode()
def main():
    torch.manual_seed(args.seed)
    cfg=task.Mod4EnvCfg();cfg.seed=args.seed;cfg.scene.num_envs=args.num_envs
    from isaaclab.sensors import ContactSensorCfg
    cfg.scene.contact_probe=ContactSensorCfg(prim_path='{ENV_REGEX_NS}/Robot/links/(left|right)_wheel',update_period=0.0,history_length=1,track_air_time=False)
    env=Mod4Env(cfg=cfg);vec=RslRlVecEnvWrapper(env,clip_actions=6.)
    robot=env.scene['robot'];dev=env.device;n=env.num_envs
    if not args.reset_smoke:
        rcfg=RslRlOnPolicyRunnerCfg(seed=args.seed,device=dev,num_steps_per_env=24,max_iterations=1,save_interval=1,
            experiment_name='rescue_eval',run_name='paired',clip_actions=6.,check_for_nan=True,
            obs_groups={'actor':['policy'],'critic':['critic']},
            policy=RslRlPpoActorCriticCfg(init_noise_std=.3,actor_hidden_dims=[256,128,64],critic_hidden_dims=[256,128,64],activation='elu'),
            algorithm=RslRlPpoAlgorithmCfg(value_loss_coef=2.,use_clipped_value_loss=True,clip_param=.2,entropy_coef=.005,
                num_learning_epochs=5,num_mini_batches=4,learning_rate=1e-4,schedule='adaptive',gamma=.99,lam=.95,desired_kl=.01,max_grad_norm=1.))
        rcfg=handle_deprecated_rsl_rl_cfg(rcfg,metadata.version('rsl-rl-lib'))
        runner=OnPolicyRunner(vec,rcfg.to_dict(),log_dir=None,device=dev);runner.load(args.checkpoint)
        policy=runner.get_inference_policy(device=dev)
    env.reset()
    from isaaclab.utils.math import quat_apply
    import numpy as np
    samples=[];sample_dt=[];history_stamp=[]
    wheelids,_=robot.find_bodies(['left_wheel','right_wheel'],preserve_order=True)
    axis=torch.tensor([0.,1.,0.],device=dev).repeat(n*2,1)
    original_update=env.scene.update
    def measured_update(dt):
        original_update(dt)
        with torch.inference_mode():
            f=env.scene.sensors['contact_probe'].data.net_forces_w
            pos=robot.data.body_pos_w[:,wheelids]
            quat=robot.data.body_quat_w[:,wheelids]
            axis_z=quat_apply(quat.reshape(-1,4),axis)[:,2].reshape(n,2)
            extent=.0625*(1-axis_z.square()).clamp_min(0).sqrt()+.01*axis_z.abs()
            gap=pos[:,:,2]-extent
            vz=robot.data.body_lin_vel_w[:,wheelids,2]
            samples.append(torch.cat([f[:,:,2],f.norm(dim=-1),gap,vz,
                robot.data.root_pos_w[:,2:3],robot.data.root_lin_vel_w[:,2:3],
                robot.data.root_lin_vel_b[:,0:1]],dim=1).clone())
            sample_dt.append(float(dt))
    env.scene.update=measured_update
    legids,_=robot.find_joints(task.LEG_ORDER,preserve_order=True)
    command=env.command_manager.get_term('twist')
    targets=torch.tensor([0.,.3,.6,1.],device=dev)[torch.arange(n,device=dev)%4]
    alive=torch.ones(n,dtype=torch.bool,device=dev)
    firstdone=torch.full((n,),args.steps,device=dev,dtype=torch.long)
    counts=torch.zeros(n,device=dev)
    sums={k:torch.zeros(n,device=dev) for k in ['speed','vel_error','tilt','height','height_error','both_wheels','both_wheels_scut_history','left_wheel_contact','right_wheel_contact','left_wheel_fz','right_wheel_fz','guide_force','base_force','delta','d2']}
    last=torch.zeros((n,6),device=dev);last2=last.clone();maxclosure=0.;maxmimic=0.;nonfinite=False;resets=0
    reset_closures=[];first_pose={};start=time.time()
    for step in range(args.steps):
        if args.reset_smoke and step%30==0:
            env.reset();alive[:]=True
        command.time_left[:]=1e9;command.is_standing_env[:]=False
        if hasattr(command,'is_heading_env'):command.is_heading_env[:]=False
        command.command[:]=0;command.command[:,0]=targets if not args.reset_smoke else 0.
        task.height_cmd(env)[:]=.25
        with torch.inference_mode():
            if args.reset_smoke:
                action=torch.zeros((n,6),device=dev)
                action[:,:4]=env._rescue_reset_q[:,legids]/task.LEG_ACTION_SCALE
            else:action=policy(vec.get_observations())
            _,_,done,_=vec.step(action)
        done=done.bool();firstdone=torch.where(alive & done,torch.full_like(firstdone,step),firstdone)
        alive &= ~done;resets+=int(done.sum())
        if not torch.isfinite(robot.data.joint_pos).all() or not torch.isfinite(action).all():nonfinite=True;break
        clo=torch.stack(list(task.closure_errors(env).values())).max(0).values
        mim=torch.stack(list(task.mimic_errors(env).values())).max(0).values
        if step==0:
            reset_closures=clo.detach().cpu().tolist()
            first_pose={'root_z_m':robot.data.root_pos_w[:,2].detach().cpu().tolist(),
                        'ground_z_m':getattr(env,'_mod4_ground_z',torch.zeros(n,device=dev)).detach().cpu().tolist(),
                        'reported_height_m':task.root_height_above_ground(env).detach().cpu().tolist()}
        valid=env.episode_length_buf>=10
        if valid.any():
            maxclosure=max(maxclosure,float(clo[valid].max()));maxmimic=max(maxmimic,float(mim[valid].max()))
        mask=alive & (step>=50)
        counts+=mask
        forces=env.scene.sensors['wheel_contact'].data.net_forces_w
        guide=env.scene.sensors['guide_contact'].data.net_forces_w
        base=env.scene.sensors['chassis_contact'].data.net_forces_w
        history=env.scene.sensors['wheel_contact_scut'].data.net_forces_w_history
        import warp as wp
        history_stamp.append(wp.to_torch(env.scene.sensors['wheel_contact_scut']._timestamp_last_update).clone())
        h=task.root_height_above_ground(env)
        values={'speed':robot.data.root_lin_vel_b[:,0],
                'vel_error':(robot.data.root_lin_vel_b[:,0]-targets).abs(),
                'tilt':torch.acos((-robot.data.projected_gravity_b[:,2]).clamp(-1,1))*180/torch.pi,
                'height':h,'height_error':(h-.25).abs(),
                'both_wheels':(forces.norm(dim=-1)>1.).all(1).float(),
                'both_wheels_scut_history':(history.norm(dim=-1).amax(dim=1)>1.).all(1).float(),
                'left_wheel_contact':(forces[:,0].norm(dim=-1)>1.).float(),
                'right_wheel_contact':(forces[:,1].norm(dim=-1)>1.).float(),
                'left_wheel_fz':forces[:,0,2], 'right_wheel_fz':forces[:,1,2],
                'guide_force':guide.norm(dim=-1).sum(1),'base_force':base.norm(dim=-1).sum(1),
                'delta':(action-last).abs().mean(1),'d2':(action-2*last+last2).abs().mean(1)}
        for k,v in values.items():sums[k]+=v*mask
        last2=last;last=action.clone()
    per={k:v/counts.clamp_min(1) for k,v in sums.items()}
    strict=alive & (counts>0) & (per['vel_error']<=torch.maximum(torch.full_like(targets,.12),targets*.25)) & (per['tilt']<=8) & (per['height_error']<=.03) & (per['both_wheels']>=.9) & (per['delta']<=.18) & (per['d2']<=.25)
    groups=[]
    for target in [0.,.3,.6,1.]:
        ids=(targets-target).abs()<.001; validrows=ids & (counts>0)
        d={'command_vx':target,'environments':int(ids.sum()),'survival_fraction':float(alive[ids].float().mean()),'strict_pass':float(strict[ids].float().mean()),'first_failure_step_mean':float(firstdone[ids].float().mean()),'sampled_envs':int(validrows.sum())}
        if abs(args.steps*env.step_dt-15.)<1e-6:d['survival_15s']=d['survival_fraction']
        for k,v in per.items():d[k]=float(v[validrows].mean()) if validrows.any() else None
        groups.append(d)
    result={'mode':'reset_smoke' if args.reset_smoke else 'deterministic_policy','checkpoint':args.checkpoint,
            'seed':args.seed,'steps':args.steps,'seconds':args.steps*env.step_dt,'elapsed_s':time.time()-start,
            'groups':groups,'max_closure_after_grace_m':maxclosure,'max_mimic_after_grace_rad':maxmimic,
            'first_step_closure_max_m':max(reset_closures) if reset_closures else None,'first_pose':first_pose,'nonfinite':nonfinite,'resets':resets,
            'wheel_sensor_body_order':list(env.scene.sensors['wheel_contact'].body_names),
            'scut_contact_window':'per-wheel peak over 3 samples at 5ms; diagnostic only; strict gate unchanged',
            'metric_population':'per-environment means after first 0.5 s, censored at FIRST termination; survival denominator includes all environments',
            'physics_pass':not nonfinite and maxclosure<.002 and maxmimic<.01}
    result['strict_pass']=result['physics_pass'] and all(g['strict_pass']>=.8 for g in groups)
    env.scene.update=original_update
    traces=torch.stack(samples).cpu().numpy()
    stamps=torch.stack(history_stamp).cpu().numpy()
    trace_path=str(Path(args.output).with_suffix('.npz'))
    np.savez_compressed(trace_path,values=traces,dt=np.array(sample_dt),history_timestamp=stamps,
        columns=np.array(['left_fz','right_fz','left_force_norm','right_force_norm','left_gap','right_gap',
            'left_vz','right_vz','root_z','root_vz','speed']))
    elapsed=np.cumsum(sample_dt);steady=elapsed>1.0;data=traces[steady]
    dt=float(np.median(sample_dt));diag=[]
    def longest_run(mask):
        edges=np.diff(np.r_[False,mask,False].astype(int));start=np.flatnonzero(edges==1);end=np.flatnonzero(edges==-1)
        return float(max(end-start,default=0)*dt)
    for index in range(n):
        a=data[:,index];contacts=a[:,2:4]>1
        diag.append({'env':index,'command':float(targets[index]),
            'both_contact_physics':float(contacts.all(1).mean()),
            'neither_contact_physics':float((~contacts.any(1)).mean()),
            'longest_neither_contact_ms':1000*longest_run(~contacts.any(1)),
            'longest_left_off_ms':1000*longest_run(~contacts[:,0]),
            'longest_right_off_ms':1000*longest_run(~contacts[:,1]),
            'both_geom_gap_above_1mm':float((a[:,4:6]>.001).all(1).mean()),
            'gap_min_max_mm':(1000*np.stack([a[:,4:6].min(0),a[:,4:6].max(0)])).tolist(),
            'mean_wheel_fz_N':a[:,:2].mean(0).tolist(),
            'root_z_peak_to_peak_mm':float(1000*np.ptp(a[:,8])),
            'root_vz_rms':float(np.sqrt(np.mean(a[:,9]**2)))})
    result['contact_diagnostic']={'trace':trace_path,'sample_count':len(samples),'median_dt':dt,
        'lazy_sensor_update':bool(env.scene.cfg.lazy_sensor_update),
        'physics_handles_decimation':bool(env._physics_handles_decimation),
        'history_actual_update_intervals_s':np.unique(np.round(np.diff(stamps[:,0])[np.diff(stamps[:,0])>0],5)).tolist(),
        'geometry':'nominal cylinder r=0.0625m halfwidth=.01m transformed by wheel body pose; excludes contact/rest offsets',
        'metrics_after_warmup_seconds':1.,'environments':diag}
    Path(args.output).write_text(json.dumps(result,indent=2));print('RESCUE_RESULT '+json.dumps(result),flush=True)
    env.close()


try:main()
except BaseException:
    import traceback
    error=traceback.format_exc()
    Path(args.output+'.error.txt').write_text(error)
    print(error,flush=True)
    raise
finally:app.close()
