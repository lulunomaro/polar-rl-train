"""Independent first80 episodes from the final model; zero optimizer operations."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import random
import time
import traceback
from .train import boot,load_guard,put,ScutVecEnv,close_application


def first_episode_contact_summary(top, active):
    """Exclude subsequent reset episodes from every contact statistic."""
    import numpy as np
    both=(top>1).all(-1)&active
    anytop=(top>1).any(-1)&active
    return dict(anytop_envs=int(anytop.any(0).sum()),
        bothtop_envs=int(both.any(0).sum()),
        anytop_environment_ticks=int(anytop.sum()),
        bothtop_environment_ticks=int(both.sum()),
        max_top_force=float(np.where(active[...,None],top,0.).max()))


def main():
    p=argparse.ArgumentParser()
    for name in ('assets','runtime','runtime-manifest','guard','job-root','checkpoint','checkpoint-SHA'):
        p.add_argument('--'+name,required=True)
    p.add_argument('--support',action='append',default=[])
    p.add_argument('--profile',choices=['trained_stair','jump270'],default='jump270')
    p.add_argument('--repair-unclipped-v2',action='store_true')
    p.add_argument('--repair-target-limits',action='store_true')
    p.add_argument('--repair-first-axis',action='store_true')
    p.add_argument('--e0-source-diagnostic',action='store_true',
                   help='Explicit weights-only E0 inference, no optimizer; compare source/adapted inputs')
    a=p.parse_args();a.num_envs=80;a.seed=9137;a.device='cuda:0'
    out=Path(a.job_root);out.mkdir(parents=True,exist_ok=False)
    ns=boot(a,out);env=bridge=None;error=None
    try:
        import numpy as np
        import torch
        from tensordict import TensorDict
        from rsl_rl.models import MLPModel
        from chassis_pd_training_env import ChassisPDMod4Env
        import mod4_task as task
        from mild_dr import tensor
        from pose_cache_runtime_adapter_v4 import install_pose_cache_runtime_adapter_v4
        from .sdk import configure,ScutBridge
        from .config import model_contract,runner_config
        from .checkpoint import check_interface
        from .course import metadata
        random.seed(a.seed);np.random.seed(a.seed);torch.manual_seed(a.seed);torch.cuda.manual_seed_all(a.seed)
        guard_module=load_guard(a.guard);identity=ns['E0_IDENTITY']
        guard_module.verify_task_module(task,identity)
        cfg=task.Mod4EnvCfg();cfg.seed=a.seed;cfg.sim.device=a.device
        contract=model_contract(a.assets)
        configure(cfg,80,a.profile,contract);guard_module.configure_new_task(cfg,identity)
        env=ChassisPDMod4Env(cfg=cfg)
        guard=guard_module.FreshDRNominalGuard(env,identity,torch_module=torch,tensor_converter=tensor)
        events=[]
        def receipt(v):
            if len(events)<40:events.append(v)
            put(out/'POSE_CACHE_EVENTS.json',dict(events=events))
        install_pose_cache_runtime_adapter_v4(env.scene['robot'],receipt_callback=receipt)
        bridge=ScutBridge(env,task,contract,tensor,a.profile)
        vec=ScutVecEnv(env,bridge,env.observation_manager.compute())
        rc=runner_config();actor_cfg=rc['actor'].copy();actor_cfg.pop('class_name')
        actor=MLPModel(vec.get_observations(),rc['obs_groups'],'actor',6,**actor_cfg).to(a.device)
        raw=Path(a.checkpoint).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=a.checkpoint_SHA:raise ValueError('Final checkpoint identity mismatch')
        checkpoint_bytes=len(raw)
        saved=torch.load(io.BytesIO(raw),map_location=a.device,weights_only=False);del raw
        if a.e0_source_diagnostic:
            if (a.checkpoint_SHA != '6cdac1e4b84df407d41a38444b87eaa91309ed898af05fe95a6c80f6ac3fd693'
                    or checkpoint_bytes != 14035411):
                raise ValueError('E0 diagnostic requires the explicitly selected source')
            compatibility=dict(kind='E0_SOURCE_WEIGHTS_ONLY_DIAGNOSTIC',optimizer_operations=0)
        else:
            compatibility=check_interface(saved,a.profile,a.repair_unclipped_v2,a.repair_target_limits)
        actor.load_state_dict(saved['actor_state_dict'],strict=True);actor.eval().requires_grad_(False)
        if a.repair_first_axis:
            from .finetune import repair_saturated_first_axis
            compatibility['first_axis_repair'] = repair_saturated_first_axis(actor)
        with guard.around_original_fullstate_restore():
            obs=env.reset();vec.current=obs[0] if isinstance(obs,tuple) else obs
        guard.check_observations(vec.current)
        bridge.ready=True
        put(out/'NATIVE_STARTUP.json',dict(epoch=time.time(),native=True,D0_D7=guard.receipt(),
            source_SHA=a.checkpoint_SHA,model_reads=1,optimizer_operations=0,seed=9137,
            saved_pose_quaternion_order='wxyz',native_sdk_quaternion_order=bridge.quaternion_order,
            compatibility=compatibility,course=metadata()))
        active=torch.ones(80,dtype=torch.bool,device=a.device)
        allticks=[];poses=[];curves=[];result=[None]*80;record_ids=[0,1,40,41]
        input_comparison=[]
        # Use a bounded callback; physical stepping remains solely env.step.
        def observe(b):
            d=b.reward.robot.data
            row=dict(tick=np.int32(b.physics_ticks),active=active.cpu().numpy().copy())
            values=dict(top_force=b.top_force,ground_force=b.ground_force,
                wheel_pos=d.body_pos_w[:,b.reward._wheel_link_idx],root_pos=d.root_pos_w,
                root_quat=d.root_quat_w,root_velocity=d.root_lin_vel_w,
                wholeclear=b.acceptance.wholeclear,leading=b.acceptance.leading,strict=b.acceptance.success)
            row.update({k:v.detach().cpu().numpy().copy() for k,v in values.items()})
            allticks.append(row)
            if b.physics_ticks%8==0:
                poses.append(dict(tick=np.int32(b.physics_ticks),active=active[record_ids].cpu().numpy().copy(),
                    body_pos=d.body_pos_w[record_ids].detach().cpu().numpy().copy(),
                    body_quat=d.body_quat_w[record_ids].detach().cpu().numpy().copy()))
        bridge.physics_observer=observe
        for control in range(400):
            # Reward/state helpers cache tensors during rollout. Keep the
            # entire native environment lifecycle in the same inference scope.
            with torch.inference_mode():
                adapted=vec.get_observations()
                action=actor(adapted)
                if a.e0_source_diagnostic and control < 24:
                    original=vec.current['policy']
                    source_action=actor(TensorDict({'policy':original},batch_size=[80]))
                    input_comparison.append(dict(control=control+1,
                        original_policy=original.detach().cpu().tolist(),
                        adapted_policy=adapted['policy'].detach().cpu().tolist(),
                        original_input_action=source_action.detach().cpu().tolist(),
                        adapted_input_action=action.detach().cpu().tolist()))
                obs,rewards,dones,extras=vec.step(action)
            snap=bridge.terminal_snapshot
            done=(snap['terminated']|snap['time_out']|((control+1)==400))&active
            for i in done.nonzero(as_tuple=False).flatten().tolist():
                result[i]={k:(v[i].detach().cpu().tolist() if torch.is_tensor(v) else v) for k,v in snap.items()}
                result[i].update(env=i,controls=control+1)
            curves.append(dict(control=control+1,active=active.cpu().tolist(),reward=rewards.detach().cpu().tolist(),
                action=action.detach().cpu().tolist(),
                **{key:snap[key].detach().cpu().tolist() for key in (
                    'applied_action','joint_target','raw_policy_max_abs','raw_critic_max_abs',
                    'observation_outlier','closure_reset','mimic_reset','numerical_reset',
                    'reset_body_contact_force','roll_pitch_rad','termination_raw',
                    'command','command_height','effective_height',
                    'termination_duration_counter')}))
            active &= ~done
            if not bool(active.any()):break
        def npz(name,rows):
            path=out/name
            np.savez_compressed(path,**{k:np.stack([row[k] for row in rows]) for k in rows[0]})
            with path.open('rb') as stream:sha=hashlib.file_digest(stream,'sha256').hexdigest()
            return dict(path=str(path),bytes=path.stat().st_size,SHA=sha)
        ticks=npz('actual400hz.npz',allticks);posefile=npz('selected_actual_poses.npz',poses)
        put(out/'CONTROL_CURVES.json',dict(curves=curves))
        if a.e0_source_diagnostic:
            put(out/'E0_INPUT_COMPARISON.json',dict(source_SHA=a.checkpoint_SHA,
                same_weights_same_physical_endpoint=True,physics_action='adapted input only',
                source_input_inference_not_independent_physical_rollout=True,
                optimizer_operations=0,rows=input_comparison))
        put(out/'ALL80.json',dict(seed=9137,first_episodes=result))
        top=np.stack([r['top_force'] for r in allticks]);mask=np.stack([r['active'] for r in allticks])
        put(out/'RESULT.json',dict(epoch=time.time(),passed_execution=all(r is not None for r in result),
            independent_first_episodes=80,seed=9137,actual_physics_hz=400,controls_max=400,
            saved_pose_quaternion_order='wxyz',native_sdk_quaternion_order=bridge.quaternion_order,
            reset_contact_body_names=[bridge.robot.body_names[i] for i in bridge.reward._reset_contact_link_idx],
            source_SHA=a.checkpoint_SHA,compatibility=compatibility,optimizer_operations=0,strict=sum(r['strict270'] for r in result),
            wholeclear=sum(r['first_flight_wholeclear'] for r in result),leading=sum(r['first_flight_leading'] for r in result),
            **first_episode_contact_summary(top,mask),all80_manifold=ticks,actual_poses=posefile,
            recorded_envs=record_ids,body_names=list(bridge.robot.body_names),course=metadata(),
            native_pose_visual_review_pending=True))
    except BaseException:
        error=traceback.format_exc();put(out/'ERROR.json',dict(epoch=time.time(),error=error));raise
    finally:
        if bridge is not None:bridge.close()
        if env is not None:env.close();put(out/'ENV_CLOSED.json',dict(epoch=time.time(),returned=True))
        put(out/'APP_CLOSE_INTENT.json',dict(epoch=time.time(),error=error,env_closed=(out/'ENV_CLOSED.json').exists()))
        close_application(ns['app'], error)


if __name__=='__main__':main()
