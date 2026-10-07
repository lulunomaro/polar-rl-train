"""Frozen native S1A history/teacher interface check, with no optimizer updates."""
from pathlib import Path
import argparse,json,os,time,hashlib,sys
D=Path(__file__).resolve().parent;CODE=D/'isaac/mod4'
for k,v in json.loads((CODE/'env.json').read_text()).items():os.environ[k]=str(v)
os.environ.update(ISAACSIM_ACCEPT_EULA='Y',OMNI_KIT_ACCEPT_EULA='YES')
p=argparse.ArgumentParser();p.add_argument('--checkpoint',required=True);p.add_argument('--output',required=True)
p.add_argument('--num_envs',type=int,default=10);p.add_argument('--steps',type=int,default=300)
from isaaclab.app import AppLauncher
AppLauncher.add_app_launcher_args(p);args=p.parse_args();app=AppLauncher(args).app
sys.path.insert(0,str(CODE))
import torch
from mod4_env import Mod4Env
import mod4_task as task
from nominal_parameter_audit import parameter_audit
from history_label_adapter import LabelHistoryAdapter
from history_observation_adapter import tensor
from history_latent_component import VelocityEncoder,expand_actor_state,actor_input
from isaaclab_rl.rsl_rl import RslRlOnPolicyRunnerCfg,RslRlPpoActorCriticCfg,RslRlPpoAlgorithmCfg,RslRlVecEnvWrapper,handle_deprecated_rsl_rl_cfg
from rsl_rl.runners import OnPolicyRunner
from importlib import metadata

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def inverse_quaternion(q,v):
    # Independent Torch frame oracle; SDK implements the same rotation in a Warp kernel.
    xyz=q[:,:3];s=q[:,3:] # Native Warp wp.quat torch view is xyzw, not compatibility root_state_w wxyz.
    return v*(2*s*s-1)-2*s*torch.cross(xyz,v,dim=-1)+2*xyz*(xyz*v).sum(-1,keepdim=True)

@torch.inference_mode()
def main():
    started=time.time();torch.manual_seed(20261002)
    cfg=task.Mod4EnvCfg();cfg.seed=20261002;cfg.scene.num_envs=args.num_envs
    assert cfg.sim.dt==.001 and cfg.decimation==10
    env=Mod4Env(cfg=cfg);inner=RslRlVecEnvWrapper(env,clip_actions=6.)
    vec=LabelHistoryAdapter(inner)
    rc=RslRlOnPolicyRunnerCfg(seed=20261002,device=env.device,num_steps_per_env=24,max_iterations=1,save_interval=1,
      experiment_name='s1a_history_sdk',run_name='frozen',clip_actions=6.,check_for_nan=True,
      obs_groups={'actor':['policy'],'critic':['critic']},
      policy=RslRlPpoActorCriticCfg(init_noise_std=.3,actor_hidden_dims=[256,128,64],critic_hidden_dims=[256,128,64],activation='elu'),
      algorithm=RslRlPpoAlgorithmCfg(value_loss_coef=2.,use_clipped_value_loss=True,clip_param=.2,entropy_coef=.005,
        num_learning_epochs=5,num_mini_batches=4,learning_rate=1e-4,schedule='adaptive',gamma=.99,lam=.95,desired_kl=.01,max_grad_norm=1.))
    rc=handle_deprecated_rsl_rl_cfg(rc,metadata.version('rsl-rl-lib'))
    runner=OnPolicyRunner(vec,rc.to_dict(),log_dir=None,device=env.device);runner.load(args.checkpoint)
    policy=runner.get_inference_policy(device=env.device)
    original=runner.alg.actor
    from rsl_rl.modules import MLP
    expanded=MLP(38,6,[256,128,64],'elu').to(env.device)
    state=expand_actor_state(original.state_dict())
    expanded.load_state_dict({k[4:]:v for k,v in state.items() if k.startswith('mlp.')})
    encoder=VelocityEncoder().to(env.device)
    raw_errors=[]
    original_augment=vec.augment
    def compare_inner_return(clean):
        before={key:clean[key].clone() for key in ('policy','critic')}
        out=original_augment(clean)
        raw_errors.extend(float((out[key]-before[key]).abs().max()) for key in ('policy','critic'))
        return out
    vec.augment=compare_inner_return
    obs,_=vec.reset();robot=env.scene['robot'];initial_params=parameter_audit(env)
    def ranges(group):
        result={};offset=0
        for name,dim in zip(env.observation_manager.active_terms[group],env.observation_manager.group_obs_term_dim[group]):
            width=1
            for n in dim:width*=n
            result[name]=[offset,offset+width];offset+=width
        return result
    layouts={name:ranges(name) for name in ('policy','critic')}
    assert layouts['critic']['base_lin_vel']==[7,10]
    lc=env.cfg.observations.critic.base_lin_vel;assert lc.scale==.5
    oracle=obs['policy'][:,None,:].repeat(1,5,1).clone()
    stats=dict(history_error=0.,cache_error=0.,body_velocity_frame_error=0.,critic_velocity_scale_error=0.,
      initial_actor_action_error=0.,last_actual_action_error=0.,raw_observation_error=0.,reset_other_rows_error=0.)
    callbacks0=env._integrated_contact.tick;advances0=vec.history.advances
    failed=torch.zeros(env.num_envs,dtype=torch.bool,device=env.device)
    reset_log=[];samples=[]
    def check(current):
        tick=int(env.common_step_counter)
        cached=vec.get_observations();assert vec.history.last_tick==tick
        stats['cache_error']=max(stats['cache_error'],float((cached['feedback_history']-current['feedback_history']).abs().max()))
        stats['history_error']=max(stats['history_error'],float((current['feedback_history'].reshape(env.num_envs,5,35)-oracle).abs().max()))
        label=current['body_velocity_label']
        independent=inverse_quaternion(tensor(robot.data.root_link_quat_w),tensor(robot.data.root_com_lin_vel_w))
        valid=current['body_velocity_valid'][:,0].bool()
        if valid.any():
            stats['body_velocity_frame_error']=max(stats['body_velocity_frame_error'],float((label[valid]-independent[valid]).abs().max()))
            stats['critic_velocity_scale_error']=max(stats['critic_velocity_scale_error'],float((current['critic'][valid,7:10]-.5*label[valid]).abs().max()))
        assert torch.equal(valid,torch.tensor([True]*env.num_envs,device=env.device)) or bool((label[~valid]==0).all())
        a,b=layouts['policy']['last_action']
        stats['last_actual_action_error']=max(stats['last_actual_action_error'],float((current['policy'][:,a:b]-env.action_manager.action).abs().max()))
        for variant in ('A1','A2'):
            x=actor_input(current['policy'],current['feedback_history'],encoder,variant)
            stats['initial_actor_action_error']=max(stats['initial_actor_action_error'],float((expanded(x)-policy(current)).abs().max()))
        # env.obs_buf retains the prior step after an explicit same-tick _reset_idx.
        # Compare to the actual inner wrapper return at augmentation, not that stale buffer.
        stats['raw_observation_error']=max(raw_errors,default=0.)
        assert all(torch.isfinite(x).all() for x in current.values())
        return current
    check(obs)
    for i in range(args.steps):
        action=policy(obs);before_resets=len(vec.selected_resets)
        obs,reward,done,extra=vec.step(action)
        failed.logical_or_(env.termination_manager.terminated)
        oracle=torch.cat((oracle[:,1:].clone(),obs['policy'][:,None,:]),dim=1)
        for _,ids in vec.selected_resets[before_resets:]:oracle[ids]=obs['policy'][ids,None,:]
        assert obs['body_velocity_valid'].all(), 'Normal following physical frame must be valid'
        check(obs)
        if i in (75,150,225):
            ids=torch.tensor([1,4,8],device=env.device);keep=torch.ones(env.num_envs,dtype=torch.bool,device=env.device);keep[ids]=False
            old=vec.history.frames.clone();oldtick=int(env.common_step_counter);oldadv=vec.history.advances
            env._reset_idx(ids);obs=vec.get_observations();oracle[ids]=obs['policy'][ids,None,:]
            assert not obs['body_velocity_valid'][ids].any() and obs['body_velocity_valid'][keep].all()
            stats['reset_other_rows_error']=max(stats['reset_other_rows_error'],float((vec.history.frames[keep]-old[keep]).abs().max()))
            assert int(env.common_step_counter)==oldtick and vec.history.advances==oldadv
            check(obs);reset_log.append(dict(tick=oldtick,ids=ids.cpu().tolist(),same_global_tick=True))
        if i in (0,75,150,225,299):samples.append(dict(tick=int(env.common_step_counter),teacher_valid=obs['body_velocity_valid'].cpu().tolist(),label=obs['body_velocity_label'].cpu().tolist(),
          critic_velocity=obs['critic'][:,7:10].cpu().tolist(),native_root_link_quat_xyzw=tensor(robot.data.root_link_quat_w).cpu().tolist()))
    saved=vec.history_state_dict();frames=saved['frames'].clone();vec.history.frames.zero_();vec.load_history_state_dict(saved)
    assert torch.equal(vec.history.frames,frames)
    callbacks=env._integrated_contact.tick-callbacks0
    result=dict(phase='complete',frozen_only=True,PPO_update_count=0,checkpoint=str(args.checkpoint),checkpoint_sha256=sha(args.checkpoint),
      physics_dt_s=float(env.physics_dt),policy_period_s=float(env.step_dt),num_envs=env.num_envs,control_steps=args.steps,
      actual_physical_callbacks=callbacks,expected_physical_callbacks=args.steps*10,
      actual_task_failed_environments=int(failed.sum()),max_closure_error_m=float(env._mod4_max_closure),max_mimic_error_rad=float(env._mod4_max_mimic),
      statistics=stats,history_shape=[5,35],history_span_ms=40,history_advances=vec.history.advances-advances0,
      explicit_selected_resets=reset_log,history_state_roundtrip_exact=True,
      manager_term_ranges=layouts,teacher_point='root center of mass',teacher_frame='root link/body frame',teacher_units='m/s',
      critic_velocity_range=[7,10],critic_velocity_scale=.5,actor_groups=['policy','feedback_history'],teacher_not_actor_input=True,
      reset_frames_teacher_invalid=True,first_next_physics_frame_teacher_valid=True,old_critic38_unchanged=True,
      initial_parameters=initial_params,final_parameters=parameter_audit(env),sampled_labels=samples,
      robot_usd_sha256=sha(task.USD_PATH),import_contract_sha256=sha(Path(task.USD_PATH).with_name('import_contract.json')),
      elapsed_wall_seconds=time.time()-started,encoder_or_gate_training_deployed=False)
    result['native_quaternion_order']='xyzw (Warp wp.quat torch view)'
    Path(args.output).write_text(json.dumps(result,indent=2))
    print('HISTORY_SDK_RAW '+json.dumps(stats),flush=True)
    assert callbacks==args.steps*10 and result['history_advances']==args.steps
    assert int(failed.sum())==0 and result['max_closure_error_m']<=.002 and result['max_mimic_error_rad']<=.01
    for name in ('history_error','cache_error','critic_velocity_scale_error','last_actual_action_error','raw_observation_error','reset_other_rows_error'):assert stats[name]==0,(name,stats[name])
    assert stats['body_velocity_frame_error']<1e-5,stats
    assert stats['initial_actor_action_error']<5e-6,stats
    Path(args.output).write_text(json.dumps(result,indent=2));print('HISTORY_SDK_RESULT '+json.dumps({k:result[k] for k in ('phase','statistics','actual_task_failed_environments','max_closure_error_m','history_advances')}),flush=True)
    env.close()

if __name__=='__main__':
    try:main()
    except BaseException:
        import traceback
        Path(args.output+'.error').write_text(traceback.format_exc());print(traceback.format_exc(),flush=True);raise
    finally:app.close()
