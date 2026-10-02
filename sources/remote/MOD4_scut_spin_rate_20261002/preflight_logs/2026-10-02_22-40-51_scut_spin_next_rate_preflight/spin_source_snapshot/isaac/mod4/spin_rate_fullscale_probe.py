"""Frozen-policy, actual patched source, 20k plane/contact smoke; no PPO."""
import argparse
import json
import os
from pathlib import Path
import time

p=argparse.ArgumentParser()
p.add_argument('--checkpoint',required=True);p.add_argument('--output',required=True)
p.add_argument('--max-rate',type=float,default=3.);p.add_argument('--num_envs',type=int,default=20000);p.add_argument('--steps',type=int,default=120)
for k,v in json.loads(Path(__file__).with_name('env.json').read_text()).items():os.environ[k]=str(v)
assert os.environ['RM_FLAT_NATIVE_PLANE']=='1'
from isaaclab.app import AppLauncher
AppLauncher.add_app_launcher_args(p);args=p.parse_args();app=AppLauncher(args).app
import torch
import warp as wp
from mod4_env import Mod4Env
import mod4_task as task
from spin_commands import audit
from isaaclab_rl.rsl_rl import (RslRlOnPolicyRunnerCfg,RslRlPpoActorCriticCfg,RslRlPpoAlgorithmCfg,
    RslRlVecEnvWrapper,handle_deprecated_rsl_rl_cfg)
from importlib import metadata
from rsl_rl.runners import OnPolicyRunner
from isaacsim.core.simulation_manager import SimulationManager


@torch.inference_mode()
def main():
    torch.manual_seed(20260927)
    cfg=task.Mod4EnvCfg();cfg.seed=20260927;cfg.scene.num_envs=args.num_envs
    # Do NOT override ground here: this tests the deployed task patch itself.
    env=Mod4Env(cfg=cfg);vec=RslRlVecEnvWrapper(env,clip_actions=6.)
    robot=env.scene['robot'];n=env.num_envs;dev=env.device
    ground=env.scene.stage.GetPrimAtPath('/World/ground/geometry/mesh')
    assert ground.GetTypeName()=='Plane', 'floor patch was not active'
    assert tuple(cfg.scene.ground.init_state.pos)==(0.,0.,0.)
    rc=RslRlOnPolicyRunnerCfg(seed=20260927,device=dev,num_steps_per_env=24,max_iterations=1,
       save_interval=1,experiment_name='floor_probe',run_name='frozen',clip_actions=6.,check_for_nan=True,
       obs_groups={'actor':['policy'],'critic':['critic']},
       policy=RslRlPpoActorCriticCfg(init_noise_std=.3,actor_hidden_dims=[256,128,64],critic_hidden_dims=[256,128,64],activation='elu'),
       algorithm=RslRlPpoAlgorithmCfg(value_loss_coef=2.,use_clipped_value_loss=True,clip_param=.2,entropy_coef=.005,
       num_learning_epochs=5,num_mini_batches=4,learning_rate=1e-4,schedule='adaptive',gamma=.99,lam=.95,desired_kl=.01,max_grad_norm=1.))
    rc=handle_deprecated_rsl_rl_cfg(rc,metadata.version('rsl-rl-lib'))
    runner=OnPolicyRunner(vec,rc.to_dict(),log_dir=None,device=dev);runner.load(args.checkpoint)
    policy=runner.get_inference_policy(device=dev)
    env.reset()
    assert hasattr(env, "_mild_dr"), "Whitelist profile missing at full scale"
    initial_parameters=env._mild_dr.audit()
    initial_command_audit=audit(env)
    sv=SimulationManager.get_physics_sim_view()
    ids=[0,14,n//2,n-1]
    views=[sv.create_rigid_contact_view(f'/World/envs/env_{eid}/Robot/links/{wheel}',
        filter_patterns=[],max_contact_data_count=2048) for eid in ids for wheel in ['left_wheel','right_wheel']]
    evidence={'ground_contacts':0,'loaded_ground_contacts':0,'loaded_downward_ground_contacts':0,
              'minimum_loaded_ground_normal_z':1.,'max_abs_ground_separation_m':0.,'sampled_environment_ids':ids}
    original=env.scene.update
    def read(dt):
        original(dt)
        for view in views:
            force,point,normal,separation,count,start,other=view.get_raw_contact_data(dt=env.physics_dt)
            nc=int(count.numpy()[0]);st=int(start.numpy()[0])
            if not nc:continue
            paths=view.get_other_actor_paths_from_ids(wp.array(other.numpy()[st:st+nc],dtype=wp.uint64,device='cpu'))
            fs=force.numpy()[st:st+nc].reshape(-1);nz=normal.numpy()[st:st+nc,2]
            ss=separation.numpy()[st:st+nc].reshape(-1)
            for j,path in enumerate(paths):
                if not str(path).startswith('/World/ground'):continue
                evidence['ground_contacts']+=1
                if float(fs[j])<=1:continue
                evidence['loaded_ground_contacts']+=1
                evidence['minimum_loaded_ground_normal_z']=min(evidence['minimum_loaded_ground_normal_z'],float(nz[j]))
                evidence['max_abs_ground_separation_m']=max(evidence['max_abs_ground_separation_m'],abs(float(ss[j])))
                if float(nz[j])<-.1:evidence['loaded_downward_ground_contacts']+=1
    env.scene.update=read
    cmd=env.command_manager.get_term('twist')
    gids=torch.arange(n,device=dev)%10
    targets=torch.tensor([0.,.3,.6,1.,-1.5,1.5,0.,0.,0.,0.],device=dev)[gids]
    yaw_targets=torch.tensor([0.,0.,0.,0.,0.,0.,-2.,2.,-args.max_rate,args.max_rate],device=dev)[gids]
    done_total=0;maxclo=0.;maxmim=0.;nonfinite=False;maxheight=0.;maxtilt=0.
    torch.cuda.reset_peak_memory_stats();began=time.time()
    for step in range(args.steps):
        cmd.time_left[:]=1e9;cmd.is_standing_env[:]=False
        if hasattr(cmd,'is_heading_env'):cmd.is_heading_env[:]=False
        cmd.command[:]=0;cmd.command[:,0]=targets;cmd.command[:,2]=yaw_targets;task.height_cmd(env)[:]=.25
        audit(env)
        action=policy(vec.get_observations());_,_,done,_=vec.step(action);done_total+=int(done.sum())
        if not torch.isfinite(robot.data.joint_pos).all() or not torch.isfinite(action).all():nonfinite=True;break
        if step>=10:
            clo=torch.stack(list(task.closure_errors(env).values())).max()
            mim=torch.stack(list(task.mimic_errors(env).values())).max()
            maxclo=max(maxclo,float(clo));maxmim=max(maxmim,float(mim))
            tilt=torch.acos((-robot.data.projected_gravity_b[:,2]).clamp(-1,1))*180/torch.pi
            maxtilt=max(maxtilt,float(tilt.max()))
            maxheight=max(maxheight,float((task.root_height_above_ground(env)-.25).abs().max()))
    env.scene.update=original
    final_parameters=env._mild_dr.audit()
    result={'initial_command_audit':initial_command_audit,'explicit_yaw_groups_rad_s':[0,0,0,0,0,0,-2,2,-args.max_rate,args.max_rate],'mild_initial_parameters':initial_parameters,'mild_final_parameters':final_parameters,'pass':not nonfinite and done_total==0 and maxclo<.002 and maxmim<.01
        and evidence['loaded_ground_contacts']>0 and evidence['loaded_downward_ground_contacts']==0
        and evidence['max_abs_ground_separation_m']<.01 and maxtilt<15 and maxheight<.06,
        'checkpoint':args.checkpoint,'num_envs':n,'steps':args.steps,'seconds':args.steps*env.step_dt,
        'policy_frozen':True,'ppo_performed':False,'plane_type':ground.GetTypeName(),
        'ground_z_m':0.,'friction_static':cfg.scene.ground.spawn.physics_material.static_friction,
        'friction_dynamic':cfg.scene.ground.spawn.physics_material.dynamic_friction,
        'nonfinite':nonfinite,'terminations':done_total,'max_closure_m':maxclo,'max_mimic_rad':maxmim,
        'max_tilt_deg':maxtilt,'max_height_error_m':maxheight,
        'torch_peak_allocated_MiB':torch.cuda.max_memory_allocated()/2**20,
        'elapsed_after_setup_s':time.time()-began,'raw_contact_evidence':evidence,
        'scope':'1.2s physical smoke, not fifteen-second graduation. Raw normals at four sampled environments only.'}
    Path(args.output).write_text(json.dumps(result,indent=2));print('SPIN_FULLSCALE_SMOKE '+json.dumps(result),flush=True)
    env.close()


try:main()
except BaseException:
    import traceback
    failure=traceback.format_exc()
    Path(args.output+'.error.txt').write_text(failure)
    print(failure,flush=True)
    raise
finally:app.close()
