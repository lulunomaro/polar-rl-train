from pathlib import Path
r=Path(__file__).resolve().parent;t=(r/'validate_speed.py').read_text(encoding='utf-8')
t=t.replace("    max_tilt=torch.zeros(n,device=dev)", '''    from contact_geometry import ControlGeometry
    geometry=ControlGeometry(env,task.USD_PATH)
    gap_max=torch.full((n,2),-1e9,device=dev)
    unload_max=torch.zeros(n,device=dev)
    max_tilt=torch.zeros(n,device=dev)''')
t=t.replace("'wheel_near_no_load']}","'wheel_near_no_load','left_mean_fz_substep','right_mean_fz_substep','left_loaded_fraction_substep','right_loaded_fraction_substep','left_support_slip_control','right_support_slip_control']}")
needle="        applied=robot.data.applied_torque"
t=t.replace(needle,'''        gap,slip=geometry.read()
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
        applied=robot.data.applied_torque''')
t=t.replace("    per['max_tilt']=max_tilt",'''    per['longest_both_low_force_s_substep']=unload_max
    per['left_gap_max_control_m']=gap_max[:,0]
    per['right_gap_max_control_m']=gap_max[:,1]
    per['max_tilt']=max_tilt''')
t=t.replace("    result['strict_pass_window']=result['strict_pass']",'''    result['contact_physical_metrics_semantics']={
        'force_and_low_load':'captured every.5ms; longest both norm force<=1N; low force is not airborne',
        'gap_and_slip':'sampled each10ms control; input USD hull support excludes cooking/offset/compliance; lowest-vertex slip approximation, not contact manifold',
        'group_values':'means of per-environment summaries; individual arrays retained in per_env, not worst cases',
        'integration':'mean force per5ms impulse bins is a reward adaptation; bin pass is not continuous contact or legacy graduation'}
    result['strict_pass_window']=result['strict_pass']''')
compile(t,'validate_speed.py','exec');(r/'validate_speed.py').write_text(t,encoding='utf-8')
print('Physical unload/impulse and explicit control-rate geometry reporting added')
