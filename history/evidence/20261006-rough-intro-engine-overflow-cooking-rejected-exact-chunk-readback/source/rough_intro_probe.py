"""New trainable task readback; frozen exact policy, no PPO."""
import argparse,os,json,sys,time
from pathlib import Path
H=Path(__file__).resolve().parents[2]
F=Path('/home/egde/rl_candidates/MOD4_PHYSICAL_DR_STAGE1_20261006')
for k,v in json.loads((H/'isaac/mod4/env.json').read_text()).items():os.environ[k]=str(v)
sys.path.insert(0,str(H/'isaac/mod4'));sys.path.insert(0,str(H))
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--num_envs',type=int,default=10);p.add_argument('--steps',type=int,default=300);p.add_argument('--manual',action='store_true');p.add_argument('--checkpoint',type=Path)
from isaaclab.app import AppLauncher
AppLauncher.add_app_launcher_args(p);args=p.parse_args();app=AppLauncher(args).app
import torch
from importlib import metadata
import mod4_task as task
from rough_intro_runtime import RoughIntroEnv,configure_intro,refresh_ground,forward_readback,query
from nominal_parameter_audit import parameter_audit
from isaaclab_rl.rsl_rl import RslRlOnPolicyRunnerCfg,RslRlPpoActorCriticCfg,RslRlPpoAlgorithmCfg,RslRlVecEnvWrapper,handle_deprecated_rsl_rl_cfg
from rsl_rl.runners import OnPolicyRunner

@torch.inference_mode()
def run():
    ready=json.loads((F/'reports/PHYSICAL_DR_STAGE1_REVIEW_READY.json').read_text())
    checkpoint=args.checkpoint or Path(ready['checkpoint']['path'])
    cfg=task.Mod4EnvCfg();cfg.scene.num_envs=args.num_envs;cfg.seed=20261006
    recipe=configure_intro(cfg)
    env=RoughIntroEnv(cfg=cfg);vec=RslRlVecEnvWrapper(env,clip_actions=6.)
    rc=RslRlOnPolicyRunnerCfg(seed=cfg.seed,device=env.device,num_steps_per_env=24,max_iterations=1,save_interval=1,experiment_name='intro_readback',run_name='frozen',clip_actions=6.,check_for_nan=True,obs_groups={'actor':['policy'],'critic':['critic']},
       policy=RslRlPpoActorCriticCfg(init_noise_std=.3,actor_hidden_dims=[256,128,64],critic_hidden_dims=[256,128,64],activation='elu'),
       algorithm=RslRlPpoAlgorithmCfg(value_loss_coef=2.,use_clipped_value_loss=True,clip_param=.2,entropy_coef=.005,num_learning_epochs=5,num_mini_batches=4,learning_rate=1e-4,schedule='adaptive',gamma=.99,lam=.95,desired_kl=.01,max_grad_norm=1.))
    rc=handle_deprecated_rsl_rl_cfg(rc,metadata.version('rsl-rl-lib'))
    runner=OnPolicyRunner(vec,rc.to_dict(),log_dir=None,device=env.device);runner.load(str(checkpoint));policy=runner.get_inference_policy(device=env.device)
    env.reset();env.sim.forward();env.scene.update(env.physics_dt)
    robot=env.scene['robot'];initial=parameter_audit(env);reset=env._rough_probe_reset_receipt
    assert torch.unique(robot.data.root_pos_w[:,:2],dim=0).shape[0]==env.num_envs, 'Shared spawn XY violates independent-grid contract'
    partition=env.scene.terrain.exact_partition_receipt
    assert partition['pass_'] and partition['collider_count']>1
    qerr=float((robot.data.joint_pos-env._rough_probe_expected_q).abs().max());assert qerr<1e-5
    term=env.command_manager.get_term('twist')
    if args.manual:term.set_manual_evaluation_mode()
    alive=torch.ones(env.num_envs,dtype=torch.bool,device=env.device)
    failures=torch.full((env.num_envs,),-1,dtype=torch.long,device=env.device)
    closure=mimic=height_error=ground_error=0.;nonfinite=False;records=[];truncations=0;actual_resets=0
    failure_snapshots=[];last_action=None;wheel_force_sum=torch.zeros((env.num_envs,2),device=env.device)
    old_termination=env.termination_manager.compute
    def tensor_list(value):
        if hasattr(value,'torch'):value=value.torch
        return value.detach().cpu().tolist()
    def capture_failure():
        result=old_termination()
        ids=env.termination_manager.terminated.nonzero(as_tuple=True)[0]
        if len(ids):
            failure_snapshots.append(dict(env_ids=tensor_list(ids),physics_tick=int(env._sim_step_counter),
                terms={n:tensor_list(env.termination_manager.get_term(n)[ids]) for n in env.termination_manager.active_terms},
                root_state=tensor_list(robot.data.root_state_w[ids]),ground_z=tensor_list(env._mod4_ground_z[ids]),
                projected_gravity=tensor_list(robot.data.projected_gravity_b[ids]),commands=tensor_list(term.command[ids]),
                actions=tensor_list(last_action[ids])))
        return result
    env.termination_manager.compute=capture_failure
    xy0=robot.data.root_pos_w[:,:2].clone();started=time.time()
    for step in range(args.steps):
        if args.manual:
            term.time_left[:]=1e9;term.command[:]=0.;term.is_standing_env[:]=False
            term.command[:,0]=torch.where(torch.arange(env.num_envs,device=env.device)%2==0,.3,-.3)
        action=policy(vec.get_observations());last_action=action.clone();_,reward,done,_=vec.step(action)
        wheel_force_sum+=env._integrated_contact.impulse/env.step_dt
        actual_done=env.termination_manager.terminated
        truncations+=int(env.termination_manager.time_outs.sum());actual_resets+=int(actual_done.sum())
        failures=torch.where(alive & actual_done,torch.full_like(failures,step),failures);alive &= ~actual_done
        nonfinite |= not bool(torch.isfinite(robot.data.joint_pos).all() and torch.isfinite(action).all() and torch.isfinite(reward).all())
        assert env._rough_reward_query_tick==env._rough_termination_query_tick==env._sim_step_counter
        # Ground cache used by the actual manager terms must equal fresh mesh rays.
        independent=query(env).cast((robot.data.root_pos_w[:,None,:]+torch.tensor([0.,0.,1.],device=env.device)).contiguous(),4.)
        assert independent['hit'].all()
        if not done.any():
            ground_error=max(ground_error,float((independent['height'][:,0]-env._mod4_ground_z).abs().max()))
            expected=torch.exp(-(robot.data.root_pos_w[:,2]-independent['height'][:,0]-.25).square()/task.SCUT_H_SIGMA)
            height_error=max(height_error,float((expected-task.height_track(env,sigma=task.SCUT_H_SIGMA)).abs().max()))
        assert term.command[:,1:].abs().max()<=1e-6 and term.command[:,0].abs().max()<=.300001
        assert not term.is_moving_spin.any() and not term.is_pure_spin.any()
        if step>=10:
            closure=max(closure,float(torch.stack(list(task.closure_errors(env).values())).max()))
            mimic=max(mimic,float(torch.stack(list(task.mimic_errors(env).values())).max()))
        if step%20==0:
            forward=forward_readback(env)
            records.append(dict(step=step,ground_tick=env._rough_query_tick,physics_tick=env._sim_step_counter,forward_all_hit=bool(forward['hit'].all()),
                command_vx_range=[float(term.command[:,0].min()),float(term.command[:,0].max())],root_height_range=[float((robot.data.root_pos_w[:,2]-env._mod4_ground_z).min()),float((robot.data.root_pos_w[:,2]-env._mod4_ground_z).max())]))
        if nonfinite or not alive.all():break
    final=parameter_audit(env)
    result=dict(pass_=not nonfinite and bool(alive.all()) and closure<=.002 and mimic<=.01 and height_error<1e-6 and ground_error<1e-5,
        checkpoint=str(checkpoint),recipe=recipe,num_envs=env.num_envs,steps_completed=step+1,seconds=(step+1)*env.step_dt,
        wall_seconds=time.time()-started,alive_count=int(alive.sum()),actual_task_resets=actual_resets,boundary_or_episode_truncations=truncations,
        first_actual_task_failure=failures.cpu().tolist(),nonfinite=nonfinite,max_closure_m=closure,max_mimic_rad=mimic,
        ground_reward_readback_max_error=height_error,ground_height_fresh_query_max_error=ground_error,
        all_30_joint_writeback_error=qerr,reset=reset,initial_parameters=initial,final_parameters=final,phase_readback=records,
        actor_obs_dim=int(sum(env.observation_manager.group_obs_dim['policy'])),critic_obs_dim=int(sum(env.observation_manager.group_obs_dim['critic'])),action_dim=env.action_manager.total_action_dim,
        actual_mesh=query(env).geometry.receipt(),net_world_xy=(robot.data.root_pos_w[:,:2]-xy0).cpu().tolist(),
        command_distribution='Manual alternating +/-.3' if args.manual else 'Actual trainable 20% stand, BODYvx uniform[-.3,.3], vy/yaw0',
        forward_scan_in_observation=False,rolling_pure_mask_always_false=True,original_vertical_impulse_not_ground_normal_force=True,
        ppo_performed=False,all_terrain_skill_completed=False)
    geometry=query(env).geometry
    streamed=__import__('hashlib').sha256()
    for start in range(0,len(geometry.faces),100000):
        streamed.update(__import__('numpy').asarray(geometry.vertices,dtype='<f4')[geometry.faces[start:start+100000]].tobytes())
    assert streamed.hexdigest()==partition['triangle_world_f32_order_sha256'],'Authored ray geometry differs from physical collider partition'
    result.update(exact_collision_partition=partition,actual_authored_triangle_f32_sha256=streamed.hexdigest(),
        mean_world_z_wheel_load_n=(wheel_force_sum/(step+1)).cpu().tolist(),physical_contact_callback_ticks=env._integrated_contact.tick,
        unused_partner_matrix_disabled=True,net_force_capture_unchanged=True,failure_snapshots=failure_snapshots,allocation_rows=40,allocation_columns=40,terrain_origins_used=False)
    args.output.write_text(json.dumps(result,indent=2));env.close();print(json.dumps({k:result[k] for k in ('pass_','steps_completed','alive_count','ground_reward_readback_max_error','ground_height_fresh_query_max_error','max_closure_m','max_mimic_rad')}),flush=True)
try:run()
except BaseException as e:
    import traceback
    args.output.with_suffix('.error.json').write_text(json.dumps(dict(error=repr(e),traceback=traceback.format_exc(),ppo_performed=False)));raise
finally:app.close()
