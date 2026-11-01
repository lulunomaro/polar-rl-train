"""Deterministic physical reset / policy acceptance; never runs PPO."""
import argparse
import json
import os
from pathlib import Path
import sys
import time

p=argparse.ArgumentParser();p.add_argument('--checkpoint',default='');p.add_argument('--output',required=True)
p.add_argument('--steps',type=int,default=1500);p.add_argument('--num_envs',type=int,default=64)
p.add_argument('--speed_limit',type=float,default=2.0);p.add_argument('--ramp_suite',action='store_true')
p.add_argument('--ground_size',type=float,default=200.)
p.add_argument('--trace_ids',default='4,14,24,34,44,54,64,74');p.add_argument('--trace_output',required=True)
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
    from ground_plane_candidate import spawn_local_native_plane
    cfg.scene.ground.spawn.func=spawn_local_native_plane
    cfg.scene.ground.init_state.pos=(0.,0.,0.)
    from isaaclab.sensors import ContactSensorCfg
    cfg.scene.wheel_contact_legacy_capture=ContactSensorCfg(
        prim_path='{ENV_REGEX_NS}/Robot/links/(left|right)_wheel',update_period=.005,
        history_length=3,track_air_time=False,debug_vis=False)
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
    initial_capture=getattr(env,'_integrated_contact',None)
    if initial_capture is not None:
        assert all(int(torch.count_nonzero(x))==0 for x in [initial_capture.history,initial_capture.sums,initial_capture.impulse,initial_capture.off_run,initial_capture.off_max]), 'stale contact buffers after reset'
    legids,_=robot.find_joints(task.LEG_ORDER,preserve_order=True)
    command=env.command_manager.get_term('twist')
    levels=[0.,.3,.6,1.,-args.speed_limit,args.speed_limit]
    if args.ramp_suite: levels += [-1.5,1.5,-2.,2.]
    if n % len(levels): raise ValueError('num_envs must be divisible by number of groups')
    group_ids=torch.arange(n,device=dev)%len(levels)
    peak_targets=torch.tensor(levels,device=dev)[group_ids]
    ramp_groups=group_ids>=6 if args.ramp_suite else torch.zeros(n,dtype=torch.bool,device=dev)
    targets=peak_targets.clone()
    wheelids,_=robot.find_joints(task.WHEEL_ORDER,preserve_order=True)
    motorids=legids+wheelids
    from contact_geometry import ControlGeometry
    geometry=ControlGeometry(env,task.USD_PATH)
    gap_max=torch.full((n,2),-1e9,device=dev)
    unload_max=torch.zeros(n,device=dev)
    max_tilt=torch.zeros(n,device=dev)
    sat_run=torch.zeros(n,device=dev);sat_longest=sat_run.clone()
    steady_counts=torch.zeros(n,device=dev);steady_error=steady_counts.clone()
    stop_counts=torch.zeros(n,device=dev);stop_error=stop_counts.clone()
    alive=torch.ones(n,dtype=torch.bool,device=dev)
    firstdone=torch.full((n,),args.steps,device=dev,dtype=torch.long)
    counts=torch.zeros(n,device=dev)
    sums={k:torch.zeros(n,device=dev) for k in ['speed','vel_error','tilt','height','height_error','both_wheels','both_wheels_scut_history','both_wheels_history_5ms','both_wheels_binned_mean','height_credit_active','height_credit_legacy','left_wheel_contact','right_wheel_contact','left_wheel_fz','right_wheel_fz','guide_force','base_force','delta','d2','wheel_abs_speed','wheel_abs_torque','leg_abs_torque','wheel_effort_clip_fraction','leg_effort_clip_fraction','wheel_near_no_load','left_mean_fz_substep','right_mean_fz_substep','left_loaded_fraction_substep','right_loaded_fraction_substep','left_support_slip_control','right_support_slip_control']}
    trace_ids=torch.tensor([int(x) for x in args.trace_ids.split(',')],device=dev)
    initial={'root_state':robot.data.root_state_w[trace_ids].detach().cpu().tolist(),
             'q':robot.data.joint_pos[trace_ids].detach().cpu().tolist(),
             'qd':robot.data.joint_vel[trace_ids].detach().cpu().tolist()}
    # Read-only views: do not change collision filters, materials, joints or controls.
    import warp as wp
    from isaacsim.core.simulation_manager import SimulationManager
    from pxr import UsdPhysics
    partner_patterns=['/World/ground']+[f'/World/envs/env_{eid}/Robot/links/{name}' for eid in [40,14] for name in robot.body_names]
    sv=SimulationManager.get_physics_sim_view()
    partner_views=[sv.create_rigid_contact_view('/World/envs/env_14/Robot/links/'+name,
        filter_patterns=[],max_contact_data_count=4096) for name in ['left_wheel','right_wheel']]
    partner_frames=[]; net_frames=[]; all_root_frames=[]
    stage=env.scene.stage
    collision_audit=[]
    for prim in stage.Traverse():
        if prim.IsA(UsdPhysics.CollisionGroup):
            collision_audit.append({'path':str(prim.GetPath()),
                'relationships':{rel.GetName():[str(x) for x in rel.GetTargets()] for rel in prim.GetRelationships()},
                'attributes':{a.GetName():str(a.Get()) for a in prim.GetAttributes()}})
    scene_prim=stage.GetPrimAtPath(env.scene.physics_scene_path)
    partner_meta={'ground_prim_attributes':{str(p.GetPath()):{a.GetName():str(a.Get()) for a in p.GetAttributes() if 'collision' in a.GetName().lower() or a.GetName() in ['points','extent','typeName']} for p in stage.Traverse() if str(p.GetPath()).startswith('/World/ground')},'patterns':partner_patterns,'view_counts':[v.sensor_count for v in partner_views],
        'filter_counts':[v.filter_count for v in partner_views],
        'env_spacing':env.scene.cfg.env_spacing,'filter_collisions':env.scene.cfg.filter_collisions,
        'physics_backend':env.scene.physics_backend,'collision_groups':collision_audit,
        'all_initial_root_state':robot.data.root_state_w.detach().cpu().tolist(),
        'scene_collision_attributes':{a.GetName():str(a.Get()) for a in scene_prim.GetAttributes() if 'collision' in a.GetName().lower() or 'invert' in a.GetName().lower()},
        'isolated_ground_collider':'local_native_plane_z0',
        'raw_contact_capture_note':'Earlier filtered view yielded zero even on loaded ground: invalid negative evidence. This run uses unfiltered raw contacts and actor IDs.'}
    Path(args.trace_output+'.partners.json').write_text(json.dumps(partner_meta,indent=2))
    previous_update=env.scene.update
    partner_step=[0];raw_contact_rows=[]
    def update_and_read_partners(dt):
        previous_update(dt)
        partner_step[0]+=1
        now=partner_step[0]*env.physics_dt
        if 4.9<=now<=5.3:
            for wheel,v in enumerate(partner_views):
                force,point,normal,separation,count,start,ids=v.get_raw_contact_data(dt=env.physics_dt)
                nc=int(count.numpy()[0]);st=int(start.numpy()[0])
                if nc:
                    cpu_ids=wp.array(ids.numpy()[st:st+nc],dtype=wp.uint64,device='cpu')
                    paths=v.get_other_actor_paths_from_ids(cpu_ids)
                    fs=force.numpy()[st:st+nc].reshape(-1);pts=point.numpy()[st:st+nc];ns=normal.numpy()[st:st+nc];seps=separation.numpy()[st:st+nc].reshape(-1)
                    for z in range(nc):raw_contact_rows.append({'time_s':now,'wheel':wheel,'other_actor':paths[z],'force_N':float(fs[z]),'point':pts[z].tolist(),'normal':ns[z].tolist(),'separation_m':float(seps[z])})
        net_frames.append(torch.stack([wp.to_torch(v.get_net_contact_forces(dt=env.physics_dt)).reshape(-1,3).detach().clone() for v in partner_views]))
    env.scene.update=update_and_read_partners
    trace_buffers={}
    def record(k,value): trace_buffers.setdefault(k,[]).append(value[trace_ids].detach().clone())
    def flush_trace():
        import numpy as np,hashlib
        arrays={k:torch.stack(v).cpu().numpy() for k,v in trace_buffers.items()}
        arrays['env_ids']=trace_ids.cpu().numpy()
        arrays['partner_net_substep']=torch.stack(net_frames).cpu().numpy()
        arrays['all_root_pos_control']=torch.stack(all_root_frames).cpu().numpy()
        Path(args.trace_output+'.raw_contacts.json').write_text(json.dumps(raw_contact_rows,indent=2))
        np.savez_compressed(args.trace_output,**arrays)
        meta={'checkpoint':args.checkpoint,'seed':args.seed,'num_envs':n,'control_dt_s':env.step_dt,
              'raw_contact_dt_s':env.physics_dt,'steps_recorded':len(trace_buffers.get('action',[])),
              'joint_names':robot.joint_names,'motor_names':task.ACTION_ORDER,'initial':initial,
              'wheel_kd':task.WHEEL_KD,'wheel_effort':task.WHEEL_EFFORT,'wheel_stall':task.WHEEL_STALL,
              'wheel_no_load':task.WHEEL_NO_LOAD,'leg_kp':task.LEG_KP,'leg_kd':task.LEG_KD,
              'wheel_action_scale':task.WHEEL_ACTION_SCALE,'leg_action_scale':task.LEG_ACTION_SCALE,
              'note':'Control state/torque at10ms; mean force/load/unload accumulated every.5ms. done frames auto-reset and must be excluded. Not contact manifold slip.',
              'source_hashes':{f:hashlib.sha256(Path(__file__).with_name(f).read_bytes()).hexdigest() for f in ['mod4_env.py','mod4_task.py','contact_capture.py']}}
        Path(args.trace_output+'.json').write_text(json.dumps(meta,indent=2))
        print('TRACE_SAVED '+str(meta['steps_recorded']),flush=True)
    last=torch.zeros((n,6),device=dev);last2=last.clone();maxclosure=0.;maxmimic=0.;nonfinite=False;resets=0
    reset_closures=[];first_pose={};start=time.time()
    for step in range(args.steps):
        if args.reset_smoke and step%30==0:
            env.reset();alive[:]=True
        command.time_left[:]=1e9;command.is_standing_env[:]=False
        if hasattr(command,'is_heading_env'):command.is_heading_env[:]=False
        t=step*env.step_dt
        # ramp .5-2.5s, cruise to 5s, brake to 7s, stop to 9s,
        # reverse 9-11s, cruise to 13s, brake to 14s, stop to 15s.
        factor=0. if t<.5 else min(1.,(t-.5)/2.) if t<5. else max(0.,1.-(t-5.)/2.) if t<9. else -min(1.,(t-9.)/2.) if t<13. else -max(0.,1.-(t-13.))
        targets=torch.where(ramp_groups,peak_targets*factor,peak_targets)
        command.command[:]=0;command.command[:,0]=targets if not args.reset_smoke else 0.
        task.height_cmd(env)[:]=.25
        with torch.inference_mode():
            if args.reset_smoke:
                action=torch.zeros((n,6),device=dev)
                action[:,:4]=env._rescue_reset_q[:,legids]/task.LEG_ACTION_SCALE
            else:
                obs_for_policy=vec.get_observations();action=policy(obs_for_policy)
            if isinstance(obs_for_policy,torch.Tensor):record('observation',obs_for_policy)
            elif hasattr(obs_for_policy,'items'):
                for key,value in obs_for_policy.items():
                    if isinstance(value,torch.Tensor) and value.shape[0]==n:record('observation_'+key,value)
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
        history_active=env.scene.sensors['wheel_contact_scut'].data.net_forces_w_history
        # Read the shadow only at control endpoints, retaining the old 10 ms gate.
        history=env.scene.sensors['wheel_contact_legacy_capture'].data.net_forces_w_history
        both_active=(history_active.norm(dim=-1).amax(dim=1)>1.).all(dim=1).float()
        both_legacy=(history.norm(dim=-1).amax(dim=1)>1.).all(dim=1).float()
        capture=getattr(env,'_integrated_contact',None)
        integrated_history=capture.history if capture is not None else history_active
        both_integrated=(integrated_history.norm(dim=-1).amax(dim=1)>1.).all(dim=1).float()
        height_soft=task.height_track(env,sigma=task.SCUT_H_SOFT_SIGMA)
        h=task.root_height_above_ground(env)
        values={'speed':robot.data.root_lin_vel_b[:,0],
                'vel_error':(robot.data.root_lin_vel_b[:,0]-targets).abs(),
                'tilt':torch.acos((-robot.data.projected_gravity_b[:,2]).clamp(-1,1))*180/torch.pi,
                'height':h,'height_error':(h-.25).abs(),
                'both_wheels':(forces.norm(dim=-1)>1.).all(1).float(),
                'both_wheels_scut_history':both_legacy,
                'both_wheels_history_5ms':both_active,
                'both_wheels_binned_mean':both_integrated,
                'height_credit_active':height_soft*both_integrated,
                'height_credit_legacy':height_soft*both_legacy,
                'left_wheel_contact':(forces[:,0].norm(dim=-1)>1.).float(),
                'right_wheel_contact':(forces[:,1].norm(dim=-1)>1.).float(),
                'left_wheel_fz':forces[:,0,2], 'right_wheel_fz':forces[:,1,2],
                'guide_force':guide.norm(dim=-1).sum(1),'base_force':base.norm(dim=-1).sum(1),
                'delta':(action-last).abs().mean(1),'d2':(action-2*last+last2).abs().mean(1)}
        gap,slip=geometry.read()
        gap_max=torch.maximum(gap_max,torch.where(mask[:,None],gap,torch.full_like(gap,-1e9)))
        if capture is not None:
            if step==50: capture.off_max.zero_()
            unload_max=torch.maximum(unload_max,torch.where(mask,capture.off_max.float()*env.physics_dt,0.))
            mean_fz=capture.impulse/env.step_dt
            loaded=capture.loaded.float()/int(round(env.step_dt/env.physics_dt))
        else:
            mean_fz=forces[:,:,2];loaded=(forces.norm(dim=-1)>1.).float()
        values.update(left_mean_fz_substep=mean_fz[:,0],right_mean_fz_substep=mean_fz[:,1],
            left_loaded_fraction_substep=loaded[:,0],right_loaded_fraction_substep=loaded[:,1],
            left_support_slip_control=slip[:,0],right_support_slip_control=slip[:,1])
        applied=robot.data.applied_torque
        computed=robot.data.computed_torque
        wc=(computed[:,wheelids]-applied[:,wheelids]).abs()>.1
        lc=(computed[:,legids]-applied[:,legids]).abs()>.1
        values.update(wheel_abs_speed=robot.data.joint_vel[:,wheelids].abs().amax(1),
            wheel_abs_torque=applied[:,wheelids].abs().amax(1),leg_abs_torque=applied[:,legids].abs().amax(1),
            wheel_effort_clip_fraction=wc.float().mean(1),leg_effort_clip_fraction=lc.float().mean(1),
            wheel_near_no_load=(robot.data.joint_vel[:,wheelids].abs()>.95*task.WHEEL_NO_LOAD).any(1).float())
        max_tilt=torch.maximum(max_tilt,torch.where(mask,values['tilt'],0.))
        sat_run=torch.where(mask & wc.any(1),sat_run+env.step_dt,0.)
        sat_longest=torch.maximum(sat_longest,sat_run)
        settled=(~ramp_groups) | (((t>=3.5) and (t<5.)) or ((t>=12.) and (t<13.)))
        stopped=ramp_groups & (((t>=8.) and (t<9.)) or (t>=14.5))
        steady_counts+=mask & settled;steady_error+=values['vel_error']*(mask & settled)
        stop_counts+=mask & stopped;stop_error+=values['speed'].abs()*(mask & stopped)
        for k,v in values.items():sums[k]+=v*mask
        all_root_frames.append(robot.data.root_pos_w.detach().clone())
        record('action',action)
        record('leg_target',env.action_manager.get_term('legs').processed_actions)
        record('wheel_target',env.action_manager.get_term('wheels').processed_actions)
        record('q',robot.data.joint_pos);record('qd',robot.data.joint_vel)
        record('root_pos',robot.data.root_pos_w);record('root_quat',robot.data.root_quat_w)
        record('root_vel_b',robot.data.root_lin_vel_b);record('root_ang_b',robot.data.root_ang_vel_b)
        record('gravity_b',robot.data.projected_gravity_b)
        record('computed_torque',computed[:,motorids]);record('applied_torque',applied[:,motorids])
        record('mean_fz',mean_fz);record('loaded_fraction',loaded)
        record('off_run_s',capture.off_run.float()*env.physics_dt)
        record('off_max_s',capture.off_max.float()*env.physics_dt)
        record('wheel_force',forces);record('support_gap',gap);record('support_slip',slip)
        record('guide_force',guide.norm(dim=-1).sum(1));record('base_force',base.norm(dim=-1).sum(1))
        record('closure',clo);record('mimic',mim);record('done',done.float());record('command',command.command)
        if (step+1)%500==0:flush_trace()
        if (step+1)%100==0:print('TRACE_PROGRESS '+str(step+1),flush=True)
        last2=last;last=action.clone()
    flush_trace()
    per={k:v/counts.clamp_min(1) for k,v in sums.items()}
    targets=peak_targets
    per['steady_vel_error']=steady_error/steady_counts.clamp_min(1)
    per['stop_abs_speed']=stop_error/stop_counts.clamp_min(1)
    per['longest_both_low_force_s_substep']=unload_max
    per['left_gap_max_control_m']=gap_max[:,0]
    per['right_gap_max_control_m']=gap_max[:,1]
    per['max_tilt']=max_tilt
    per['longest_wheel_effort_clip_s']=sat_longest
    # Window semantics mirror the upstream reward, but our observed lazy-sensor
    # sampling cadence is 10 ms, not the configured 5 ms. Neither gate is a contest standard.
    common=alive & (counts>0) & (per['vel_error']<=torch.maximum(torch.full_like(targets,.12),targets.abs()*.25)) & (per['tilt']<=8) & (per['height_error']<=.03) & (per['delta']<=.18) & (per['d2']<=.25)
    strict=common & (per['both_wheels_scut_history']>=.9)
    strict_integrated=common & (per['both_wheels_binned_mean']>=.9)
    strict_5ms=common & (per['both_wheels_history_5ms']>=.9)
    strict_instant=common & (per['both_wheels']>=.9)
    # 2026-09-29 追加：逐判据失败计数（只做诊断，不改变 strict 判定）
    crit={'alive':alive,'sampled':counts>0,
          'vel':per['vel_error']<=torch.maximum(torch.full_like(targets,.12),targets.abs()*.25),
          'tilt':per['tilt']<=8,'height':per['height_error']<=.03,
          'contact_window':per['both_wheels_scut_history']>=.9,
          'delta':per['delta']<=.18,'d2':per['d2']<=.25}
    groups=[]
    for group_index,target in enumerate(levels):
        ids=group_ids==group_index; validrows=ids & (counts>0)
        d={'command_vx':target,'environments':int(ids.sum()),'survival_fraction':float(alive[ids].float().mean()),'strict_pass':float(strict[ids].float().mean()),'first_failure_step_mean':float(firstdone[ids].float().mean()),'sampled_envs':int(validrows.sum())}
        d['profile']='ramp_brake_reverse' if args.ramp_suite and group_index>=6 else 'constant'
        d['fail_counts']={k:int((~m & (ids if k in ['alive','sampled'] else validrows)).sum()) for k,m in crit.items()}
        d['strict_pass_window']=d['strict_pass']
        d['strict_pass_window_legacy_capture']=d['strict_pass']
        d['strict_pass_integrated_mean']=float(strict_integrated[ids].float().mean())
        d['strict_pass_window_5ms']=float(strict_5ms[ids].float().mean())
        d['strict_pass_instant_legacy']=float(strict_instant[ids].float().mean())
        if abs(args.steps*env.step_dt-15.)<1e-6:d['survival_15s']=d['survival_fraction']
        for k,v in per.items():d[k]=float(v[validrows].mean()) if validrows.any() else None
        groups.append(d)
    result={'mode':'reset_smoke' if args.reset_smoke else 'deterministic_policy','checkpoint':args.checkpoint,
            'seed':args.seed,'steps':args.steps,'seconds':args.steps*env.step_dt,'elapsed_s':time.time()-start,
            'groups':groups,'max_closure_after_grace_m':maxclosure,'max_mimic_after_grace_rad':maxmimic,
            'first_step_closure_max_m':max(reset_closures) if reset_closures else None,'first_pose':first_pose,'nonfinite':nonfinite,'resets':resets,
            'wheel_sensor_body_order':list(env.scene.sensors['wheel_contact'].body_names),
            'gate_version':'legacy_gate_preserved_with_integrated_and_endpoint_reporting_20260930',
            'scut_contact_window':{'semantics':'per-wheel peak over 3 samples >1N; not simultaneous continuous loading','configured_update_period_s':.005,'actual_update_interval_s_prior_measured':.01,'prior_evidence':'contact_substep_diagnostic.json'},
            'metric_population':'per-environment means after first 0.5 s, censored at FIRST termination; survival denominator includes all environments',
            'physics_pass':not nonfinite and maxclosure<.002 and maxmimic<.01}
    result['per_environment']={k:v.detach().cpu().tolist() for k,v in per.items()}
    result['per_environment'].update(alive=alive.cpu().tolist(), group_ids=group_ids.cpu().tolist())
    result['strict_pass']=result['physics_pass'] and all(g['strict_pass']>=.8 for g in groups)
    # Safety permits learning imperfect speed tracking, but rejects falls,
    # major posture errors, broken closures and persistent actuator clipping.
    result['speed_safety_pass']=result['physics_pass'] and all(
        g['survival_fraction']>=.95 and g['max_tilt'] is not None and g['max_tilt']<=15
        and g['height_error']<=.03 and g['wheel_effort_clip_fraction']<=.2
        and g['leg_effort_clip_fraction']<=.2 and g['longest_wheel_effort_clip_s']<=.5
        and g['wheel_near_no_load']<=.01 and g['base_force']<=1. and g['guide_force']<=1.
        for g in groups)
    result['speed_limit']=args.speed_limit
    result['ramp_suite']=args.ramp_suite
    result['effort_sampling']='10ms control-step snapshots, not substep peak audit; computed-minus-applied >0.1Nm counts clipping'
    result['contact_physical_metrics_semantics']={
        'force_and_low_load':'captured every.5ms; longest both norm force<=1N; low force is not airborne',
        'gap_and_slip':'sampled each10ms control; input USD hull support excludes cooking/offset/compliance; lowest-vertex slip approximation, not contact manifold',
        'group_values':'means of per-environment summaries; individual arrays retained in per_environment, not worst cases',
        'integration':'mean force per5ms impulse bins is a reward adaptation; bin pass is not continuous contact or legacy graduation'}
    result['strict_pass_window']=result['strict_pass']
    result['strict_pass_window_legacy_capture']=result['strict_pass']
    result['strict_pass_integrated_mean']=result['physics_pass'] and all(g['strict_pass_integrated_mean']>=.8 for g in groups)
    result['strict_pass_window_5ms']=result['physics_pass'] and all(g['strict_pass_window_5ms']>=.8 for g in groups)
    result['contact_capture_metadata']=getattr(env,'_contact_capture_metadata',{'enabled':False})
    result['graduation_gate_contact_source']='legacy control-endpoint shadow; corrected 5ms stats do not automatically promote speed'
    result['height_credit_semantics']='unweighted exp height * recent contact; weighted per control step = credit * 0.3 * 0.01'
    result['physical_contact_evidence']='reports/contact_probe_7450_20260930/FINDINGS.md in source root; 2kHz unload/gap/slip retained there, not overwritten by window stats'
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
