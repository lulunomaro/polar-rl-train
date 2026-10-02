from pathlib import Path

root=Path(__file__).parent
s=(root/'validate_rescue_current.py').read_text()
s=s.replace("p.add_argument('--reset_smoke'", "p.add_argument('--speed_limit',type=float,default=2.0);p.add_argument('--ramp_suite',action='store_true')\np.add_argument('--reset_smoke'")
s=s.replace("targets=torch.tensor([0.,.3,.6,1.],device=dev)[torch.arange(n,device=dev)%4]", """levels=[0.,.3,.6,1.,-args.speed_limit,args.speed_limit]
    if args.ramp_suite: levels += [-1.5,1.5,-2.,2.]
    if n % len(levels): raise ValueError('num_envs must be divisible by number of groups')
    group_ids=torch.arange(n,device=dev)%len(levels)
    peak_targets=torch.tensor(levels,device=dev)[group_ids]
    ramp_groups=group_ids>=6 if args.ramp_suite else torch.zeros(n,dtype=torch.bool,device=dev)
    targets=peak_targets.clone()
    wheelids,_=robot.find_joints(task.WHEEL_ORDER,preserve_order=True)
    motorids=legids+wheelids
    max_tilt=torch.zeros(n,device=dev)
    sat_run=torch.zeros(n,device=dev);sat_longest=sat_run.clone()
    steady_counts=torch.zeros(n,device=dev);steady_error=steady_counts.clone()
    stop_counts=torch.zeros(n,device=dev);stop_error=stop_counts.clone()""")
s=s.replace("'delta','d2']", "'delta','d2','wheel_abs_speed','wheel_abs_torque','leg_abs_torque','wheel_effort_clip_fraction','leg_effort_clip_fraction','wheel_near_no_load']")
s=s.replace("command.command[:]=0;", """t=step*env.step_dt
        # ramp .5-2.5s, cruise to 5s, brake to 7s, stop to 9s,
        # reverse 9-11s, cruise to 13s, brake to 14s, stop to 15s.
        factor=0. if t<.5 else min(1.,(t-.5)/2.) if t<5. else max(0.,1.-(t-5.)/2.) if t<9. else -min(1.,(t-9.)/2.) if t<13. else -max(0.,1.-(t-13.))
        targets=torch.where(ramp_groups,peak_targets*factor,peak_targets)
        command.command[:]=0;""")
s=s.replace("        for k,v in values.items():sums[k]+=v*mask", """        applied=robot.data.applied_torque
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
        for k,v in values.items():sums[k]+=v*mask""")
s=s.replace("    per={k:v/counts.clamp_min(1) for k,v in sums.items()}", """    per={k:v/counts.clamp_min(1) for k,v in sums.items()}
    targets=peak_targets
    per['steady_vel_error']=steady_error/steady_counts.clamp_min(1)
    per['stop_abs_speed']=stop_error/stop_counts.clamp_min(1)
    per['max_tilt']=max_tilt
    per['longest_wheel_effort_clip_s']=sat_longest""")
s=s.replace("targets*.25", "targets.abs()*.25")
s=s.replace("    for target in [0.,.3,.6,1.]:\n        ids=(targets-target).abs()<.001;", "    for group_index,target in enumerate(levels):\n        ids=group_ids==group_index;")
s=s.replace("        d['fail_counts']", "        d['profile']='ramp_brake_reverse' if args.ramp_suite and group_index>=6 else 'constant'\n        d['fail_counts']")
s=s.replace("    result['strict_pass_window']=result['strict_pass']", """    # Safety permits learning imperfect speed tracking, but rejects falls,
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
    result['strict_pass_window']=result['strict_pass']""")
(root/'validate_speed.py').write_text(s)
compile(s,'validate_speed.py','exec')
print('speed validator built')
