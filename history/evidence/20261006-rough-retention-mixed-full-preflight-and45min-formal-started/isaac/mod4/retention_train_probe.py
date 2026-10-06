"""Frozen new mixed-task SDK readback, no PPO and no claimed repair effect."""
import argparse
import hashlib
import json
import math
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for key, value in json.loads((ROOT/'isaac/mod4/env.json').read_text()).items():
    os.environ[key] = str(value)
sys.path.insert(0, str(ROOT/'isaac/mod4'))
parser = argparse.ArgumentParser()
parser.add_argument('--output', type=Path, required=True)
parser.add_argument('--checkpoint', type=Path, required=True)
parser.add_argument('--num_envs', type=int, default=32)
parser.add_argument('--steps', type=int, default=1500)
parser.add_argument('--automatic', action='store_true')
from isaaclab.app import AppLauncher
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
app = AppLauncher(args).app
import numpy as np
import torch
from importlib import metadata
import mod4_task as task
from retention_mix_math import rough_mask, spawn_xy
from retention_mix_runtime import RetentionMixEnv, configure_retention
from rough_intro_runtime import query, refresh_ground, forward_readback
from nominal_parameter_audit import parameter_audit
from isaaclab_rl.rsl_rl import (
    RslRlOnPolicyRunnerCfg, RslRlPpoActorCriticCfg, RslRlPpoAlgorithmCfg,
    RslRlVecEnvWrapper, handle_deprecated_rsl_rl_cfg,
)
from rsl_rl.runners import OnPolicyRunner



def authored_material_readback(env):
    from pxr import UsdGeom,UsdShade,UsdPhysics,PhysxSchema
    stage=env.scene.terrain._sim.stage if hasattr(env.scene.terrain,'_sim') else env.sim.stage
    rows=[]
    for prim in stage.Traverse():
        path=str(prim.GetPath())
        if not prim.IsA(UsdGeom.Mesh) or not ('retained_flat' in path or '_part' in path):continue
        if not prim.HasAPI(UsdPhysics.CollisionAPI):continue
        material,_=UsdShade.MaterialBindingAPI(prim).ComputeBoundMaterial(materialPurpose='physics')
        assert material and material.GetPrim().IsValid(),path
        api=UsdPhysics.MaterialAPI(material.GetPrim())
        physical=PhysxSchema.PhysxMaterialAPI(material.GetPrim())
        row=dict(collider=path,material=str(material.GetPath()),static_friction=api.GetStaticFrictionAttr().Get(),dynamic_friction=api.GetDynamicFrictionAttr().Get(),restitution=api.GetRestitutionAttr().Get(),friction_combine_mode=physical.GetFrictionCombineModeAttr().Get(),restitution_combine_mode=physical.GetRestitutionCombineModeAttr().Get())
        expected=.9 if 'retained_flat' in path else 1.
        assert abs(row['static_friction']-expected)<1e-6 and abs(row['dynamic_friction']-expected)<1e-6 and row['restitution']==0.,row
        if 'retained_flat' not in path:assert row['friction_combine_mode']=='multiply',row
        rows.append(row)
    assert len(rows)==env.scene.terrain.retention_geometry_receipt['rough_partition']['collider_count']+1,len(rows)
    assert sum('retained_flat' in r['collider'] for r in rows)==1
    return dict(pass_=True,collider_count=len(rows),rows=rows,scope='Actual USD physics binding and material attributes; not a material-point contact measure')

@torch.inference_mode()
def run():
    assert args.checkpoint.is_file()
    cfg = task.Mod4EnvCfg()
    cfg.scene.num_envs = args.num_envs
    cfg.seed = 20261006
    recipe = configure_retention(cfg)
    env = RetentionMixEnv(cfg=cfg)
    vec = RslRlVecEnvWrapper(env, clip_actions=6.)
    rc = RslRlOnPolicyRunnerCfg(
        seed=cfg.seed, device=env.device, num_steps_per_env=24, max_iterations=1,
        save_interval=1, experiment_name='retention_component', run_name='frozen',
        clip_actions=6., check_for_nan=True, obs_groups={'actor':['policy'],'critic':['critic']},
        policy=RslRlPpoActorCriticCfg(init_noise_std=.3, actor_hidden_dims=[256,128,64],
                                   critic_hidden_dims=[256,128,64], activation='elu'),
        algorithm=RslRlPpoAlgorithmCfg(value_loss_coef=2., use_clipped_value_loss=True,
            clip_param=.2, entropy_coef=.005, num_learning_epochs=5, num_mini_batches=4,
            learning_rate=1e-4, schedule='adaptive', gamma=.99, lam=.95,
            desired_kl=.01, max_grad_norm=1.),
    )
    rc = handle_deprecated_rsl_rl_cfg(rc, metadata.version('rsl-rl-lib'))
    runner = OnPolicyRunner(vec, rc.to_dict(), log_dir=None, device=env.device)
    runner.load(str(args.checkpoint))
    policy = runner.get_inference_policy(device=env.device)
    env.reset(); env.sim.forward(); env.scene.update(env.physics_dt)
    robot = env.scene['robot']
    ids = torch.arange(env.num_envs, device=env.device)
    terrain = rough_mask(ids); flat_ids = ids[~terrain]
    assert torch.unique(robot.data.root_pos_w[:, :2], dim=0).shape[0] == env.num_envs
    requested_xy = spawn_xy(env.scene.env_origins, ids)
    xy_error = float((robot.data.root_pos_w[:, :2]-requested_xy).abs().max())
    q_error = float((robot.data.joint_pos-env._rough_probe_expected_q).abs().max())
    assert xy_error < 1e-5 and q_error < 1e-5
    material_readback = authored_material_readback(env)
    initial_parameters = parameter_audit(env)
    initial_root = robot.data.root_state_w.cpu().tolist()
    initial_q = robot.data.joint_pos.cpu().tolist()
    term = env.command_manager.get_term('twist')
    # Inspect the actual automatic sampler before the frozen manual protocol.
    term._resample_command(ids)
    automatic = dict(commands=term.command.cpu().tolist(),
        standing=term.is_standing_env.cpu().tolist(), pure=term.is_pure_spin.cpu().tolist(),
        moving=term.is_moving_spin.cpu().tolist(), transition=term.is_transition_spin.cpu().tolist())
    assert not term.is_pure_spin[terrain].any() and not term.is_moving_spin[terrain].any()
    assert term.command[terrain, 1:].abs().max() == 0.
    resample_events=[]
    original_resample=term._resample_command
    def capture_resample(env_ids):
        original_resample(env_ids)
        resample_events.append(dict(tick=int(env._sim_step_counter),ids=torch.as_tensor(env_ids).cpu().tolist()))
    term._resample_command=capture_resample
    if not args.automatic:term.set_manual_evaluation_mode()
    slots = torch.arange(len(flat_ids), device=env.device).remainder(8)
    # Old flat stand, low/high forward/reverse, both4pi, both moving2rad.
    pure_ids = flat_ids[(slots == 4) | (slots == 5)]
    moving_ids = flat_ids[(slots == 6) | (slots == 7)]
    alive = torch.ones(env.num_envs, dtype=torch.bool, device=env.device)
    first_failure = torch.full((env.num_envs,), -1, device=env.device, dtype=torch.long)
    closure = mimic = ground_error = reward_error = observation_error = 0.
    resets = truncations = 0; nonfinite = False; records = []
    all_times=[];all_xy=[];all_heading=[];all_failure=[];all_truncation=[]
    wheel_load_sum = torch.zeros((env.num_envs, 2), device=env.device)
    began = time.time()
    for step in range(args.steps):
        if not args.automatic:
            term.time_left[:] = 1e9
            term.is_standing_env[:] = False
            term.is_pure_spin[:] = False; term.is_moving_spin[:] = False; term.is_transition_spin[:] = False
            term.command[:] = 0.
            term.is_standing_env[flat_ids[slots == 0]] = True
            for slot, vx in ((1,.3),(2,1.5),(3,-1.5)):
                term.command[flat_ids[slots == slot], 0] = vx
            term.is_pure_spin[pure_ids] = True
            term.command[flat_ids[slots == 4], 2] = 4*math.pi
            term.command[flat_ids[slots == 5], 2] = -4*math.pi
            term.is_moving_spin[moving_ids] = True
            term.world_direction[moving_ids] = math.pi/4
            term.signed_yaw[flat_ids[slots == 6]] = 2.
            term.signed_yaw[flat_ids[slots == 7]] = -2.
            heading = robot.data.heading_w.torch[moving_ids]
            term.command[moving_ids, 0] = torch.cos(heading-term.world_direction[moving_ids])
            term.command[moving_ids, 2] = term.signed_yaw[moving_ids]
            terrain_ids = ids[terrain]
            term.command[terrain_ids, 0] = torch.where(terrain_ids.div(4, rounding_mode='floor').remainder(2)==0, .3, -.3)
        assert term.command[terrain, 1:].abs().max() == 0.
        observations = vec.get_observations()
        for group in ('policy', 'critic'):
            observation_error = max(observation_error, float((observations[group][:,:3]-term.command).abs().max()))
        assert observation_error < 1e-6, 'Real actor/critic commands differ from requests'
        action = policy(observations)
        _, reward, done, _ = vec.step(action)
        actual_done = env.termination_manager.terminated
        first_failure = torch.where(alive & actual_done, torch.full_like(first_failure, step), first_failure)
        alive &= ~actual_done
        resets += int(actual_done.sum()); truncations += int(env.termination_manager.time_outs.sum())
        nonfinite |= not bool(torch.isfinite(action).all() and torch.isfinite(reward).all() and torch.isfinite(robot.data.root_state_w).all() and torch.isfinite(robot.data.joint_pos).all())
        assert env._rough_reward_query_tick == env._rough_termination_query_tick == env._sim_step_counter
        fresh = query(env).cast((robot.data.root_pos_w[:,None,:]+robot.data.root_pos_w.new_tensor([0.,0.,1.])).contiguous(), 4.)
        assert fresh['hit'].all() and (fresh['normal'][...,2] > 0).all()
        if not done.any():
            ground_error = max(ground_error, float((fresh['height'][:,0]-env._mod4_ground_z).abs().max()))
            expected_height = torch.exp(-(robot.data.root_pos_w[:,2]-fresh['height'][:,0]-.25).square()/task.SCUT_H_SIGMA)
            reward_error = max(reward_error, float((expected_height-task.height_track(env,sigma=task.SCUT_H_SIGMA)).abs().max()))
        wheel_load_sum += env._integrated_contact.impulse/env.step_dt
        if step >= 10:
            closure = max(closure, float(torch.stack(list(task.closure_errors(env).values())).max()))
            mimic = max(mimic, float(torch.stack(list(task.mimic_errors(env).values())).max()))
        if env.num_envs<=128:
            all_times.append((step+1)*env.step_dt);all_xy.append(robot.data.root_pos_w[:,:2].cpu().numpy().copy());all_heading.append(robot.data.heading_w.torch.cpu().numpy().copy());all_failure.append(actual_done.cpu().numpy().copy());all_truncation.append(env.termination_manager.time_outs.cpu().numpy().copy())
        if step % 20 == 0:
            scan = forward_readback(env)
            records.append(dict(step=step, commands=term.command.cpu().tolist(),
                root_xy=robot.data.root_pos_w[:,:2].cpu().tolist(), heading=robot.data.heading_w.torch.cpu().tolist(),
                body_velocity=robot.data.root_lin_vel_b.cpu().tolist(), ground_z=fresh['height'][:,0].cpu().tolist(),
                scan_all_hit=bool(scan['hit'].all()), actual_task_failure=actual_done.cpu().tolist(),
                truncation=env.termination_manager.time_outs.cpu().tolist()))
        if nonfinite or not alive.all():
            break
    lifecycle=dict(automatic=args.automatic,resampling_time_range=list(term.cfg.resampling_time_range),resample_events=resample_events)
    if args.automatic and args.steps>=1700:
        assert resample_events and any(any(i in flat_ids.cpu().tolist() for i in e['ids']) for e in resample_events),'No actual timed flat resampling observed'
    cycles=[];rough_segments=[]
    if all_times and not args.automatic:
        from world_cycle_metrics import measure_world_cycles
        times=np.asarray(all_times);xy=np.asarray(all_xy);head=np.asarray(all_heading);fail=np.asarray(all_failure);trunc=np.asarray(all_truncation)
        for env_id in moving_ids.cpu().tolist():
            end=np.flatnonzero(fail[:,env_id] | trunc[:,env_id]);first=int(end[0]) if len(end) else -1
            sign=1 if int(slots[(flat_ids==env_id).nonzero(as_tuple=True)[0][0]])==6 else -1
            result=measure_world_cycles(times,xy[:,env_id],head[:,env_id],math.pi/4,sign,first)
            cycles.append(dict(env_id=env_id,metrics=result,requested_world_progress=.5,requested_signed_yaw=2*sign))
        for env_id in ids[terrain].cpu().tolist():
            boundaries=np.flatnonzero(fail[:,env_id] | trunc[:,env_id]).tolist()+[len(times)]
            first=0;segments=[]
            for end in boundaries:
                if end-first>=2:
                    theta=float(head[first,env_id]);axis=np.array([math.cos(theta),math.sin(theta)]);cross=np.array([-axis[1],axis[0]])
                    delta=xy[end-1,env_id]-xy[first,env_id];duration=times[end-1]-times[first]
                    segments.append(dict(start_sample=first,end_sample=end-1,duration_s=float(duration),along_m_s=float(delta@axis/duration),cross_m_s=float(delta@cross/duration)))
                first=end+1
            rough_segments.append(dict(env_id=env_id,requested_body_vx=.3 if (env_id//4)%2==0 else -.3,valid_segments_before_each_reset=segments))
        trace_path=args.output.with_suffix('.npz');np.savez_compressed(trace_path,times=times,root_xy=xy,heading=head,task_failure=fail,truncation=trunc)
        trace_index=dict(path=str(trace_path),sha256=hashlib.sha256(trace_path.read_bytes()).hexdigest())
    else:trace_index=None
    final_parameters = parameter_audit(env)
    geometry = query(env).geometry
    streamed = hashlib.sha256()
    for first in range(0, len(geometry.faces), 100000):
        streamed.update(np.asarray(geometry.vertices,dtype='<f4')[geometry.faces[first:first+100000]].tobytes())
    actual_geometry = env.scene.terrain.retention_geometry_receipt
    assert streamed.hexdigest() == actual_geometry['combined_authored_triangle_f32_sha256']
    assert len(geometry.faces) == actual_geometry['expected_total_faces']
    result = dict(pass_=bool(alive.all()) and not nonfinite and closure <= .002 and mimic <= .01,
        actual_material_bindings=material_readback,command_lifecycle=lifecycle,complete_world_cycles=cycles,rough_progress_segments=rough_segments,trace_sha_index=trace_index,
        checkpoint=str(args.checkpoint), checkpoint_sha256=hashlib.sha256(args.checkpoint.read_bytes()).hexdigest(),
        recipe=recipe, num_envs=env.num_envs, steps_completed=step+1, seconds=(step+1)*env.step_dt,
        wall_seconds=time.time()-began, alive_count=int(alive.sum()), actual_task_resets=resets,
        boundary_or_episode_truncations=truncations, nonfinite=nonfinite,
        first_actual_failure=first_failure.cpu().tolist(), max_closure_m=closure, max_mimic_rad=mimic,
        ground_fresh_readback_error=ground_error, height_reward_readback_error=reward_error,
        actor_critic_command_readback_error=observation_error,
        full30q_writeback_error=q_error, requested_reset_xy_error=xy_error,
        initial_root_state=initial_root, initial_joint_pos=initial_q,
        initial_parameters=initial_parameters, final_parameters=final_parameters,
        automatic_command_readback=automatic, actual_geometry=actual_geometry,
        actual_authored_triangle_f32_sha256=streamed.hexdigest(), actual_mesh=geometry.receipt(),
        rough_ids=ids[terrain].cpu().tolist(), flat_ids=flat_ids.cpu().tolist(),
        physics_callback_ticks=env._integrated_contact.tick,
        mean_world_z_wheel_load_n=(wheel_load_sum/(step+1)).cpu().tolist(),
        actor_obs_dim=int(sum(env.observation_manager.group_obs_dim['policy'])),
        critic_obs_dim=int(sum(env.observation_manager.group_obs_dim['critic'])), action_dim=env.action_manager.total_action_dim,
        phase_readback=records, ppo_performed=False, repair_effect_confirmed=False,
        ground_query_is_authored_geometry_not_material_point=True,
        complete_world_circles_measured=bool(cycles),rough_tracking_maturity_not_certified=True,
        manual_frozen_protocol=not args.automatic)
    args.output.write_text(json.dumps(result, indent=2)+'\n')
    env.close()
    print(json.dumps({k:result[k] for k in ('pass_','alive_count','steps_completed','max_closure_m','max_mimic_rad')}), flush=True)


try:
    run()
except BaseException as error:
    import traceback
    args.output.with_suffix('.error.json').write_text(json.dumps(dict(error=repr(error), traceback=traceback.format_exc(), ppo_performed=False)))
    raise
finally:
    app.close()
