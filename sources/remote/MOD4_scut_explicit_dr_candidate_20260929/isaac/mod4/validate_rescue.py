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
    # Window semantics mirror the upstream reward, but our observed lazy-sensor
    # sampling cadence is 10 ms, not the configured 5 ms. Neither gate is a contest standard.
    common=alive & (counts>0) & (per['vel_error']<=torch.maximum(torch.full_like(targets,.12),targets*.25)) & (per['tilt']<=8) & (per['height_error']<=.03) & (per['delta']<=.18) & (per['d2']<=.25)
    strict=common & (per['both_wheels_scut_history']>=.9)
    strict_instant=common & (per['both_wheels']>=.9)
    # 2026-09-29 追加：逐判据失败计数（只做诊断，不改变 strict 判定）
    crit={'alive':alive,'sampled':counts>0,
          'vel':per['vel_error']<=torch.maximum(torch.full_like(targets,.12),targets*.25),
          'tilt':per['tilt']<=8,'height':per['height_error']<=.03,
          'contact_window':per['both_wheels_scut_history']>=.9,
          'delta':per['delta']<=.18,'d2':per['d2']<=.25}
    groups=[]
    for target in [0.,.3,.6,1.]:
        ids=(targets-target).abs()<.001; validrows=ids & (counts>0)
        d={'command_vx':target,'environments':int(ids.sum()),'survival_fraction':float(alive[ids].float().mean()),'strict_pass':float(strict[ids].float().mean()),'first_failure_step_mean':float(firstdone[ids].float().mean()),'sampled_envs':int(validrows.sum())}
        d['fail_counts']={k:int((~m & (ids if k in ['alive','sampled'] else validrows)).sum()) for k,m in crit.items()}
        d['strict_pass_window']=d['strict_pass']
        d['strict_pass_instant_legacy']=float(strict_instant[ids].float().mean())
        if abs(args.steps*env.step_dt-15.)<1e-6:d['survival_15s']=d['survival_fraction']
        for k,v in per.items():d[k]=float(v[validrows].mean()) if validrows.any() else None
        groups.append(d)
    result={'mode':'reset_smoke' if args.reset_smoke else 'deterministic_policy','checkpoint':args.checkpoint,
            'seed':args.seed,'steps':args.steps,'seconds':args.steps*env.step_dt,'elapsed_s':time.time()-start,
            'groups':groups,'max_closure_after_grace_m':maxclosure,'max_mimic_after_grace_rad':maxmimic,
            'first_step_closure_max_m':max(reset_closures) if reset_closures else None,'first_pose':first_pose,'nonfinite':nonfinite,'resets':resets,
            'wheel_sensor_body_order':list(env.scene.sensors['wheel_contact'].body_names),
            'gate_version':'window_contact_v2_dual_reporting_20260929',
            'scut_contact_window':{'semantics':'per-wheel peak over 3 samples >1N; not simultaneous continuous loading','configured_update_period_s':.005,'actual_update_interval_s_prior_measured':.01,'prior_evidence':'contact_substep_diagnostic.json'},
            'metric_population':'per-environment means after first 0.5 s, censored at FIRST termination; survival denominator includes all environments',
            'physics_pass':not nonfinite and maxclosure<.002 and maxmimic<.01}
    from mod4_dr_profiles import audit
    result['DR_audit']=audit(env)
    result['strict_pass']=result['physics_pass'] and all(g['strict_pass']>=.8 for g in groups)
    result['strict_pass_window']=result['strict_pass']
    result['strict_pass_instant_legacy']=result['physics_pass'] and all(g['strict_pass_instant_legacy']>=.8 for g in groups)
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
