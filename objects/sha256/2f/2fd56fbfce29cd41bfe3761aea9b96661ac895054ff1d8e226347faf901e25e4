from pathlib import Path

r=Path(__file__).parent
s=(r/'validate_rescue.py').read_text(encoding='utf8')
s=s.replace("    env=Mod4Env(cfg=cfg);vec=", "    from isaaclab.sensors import ContactSensorCfg\n    cfg.scene.contact_probe=ContactSensorCfg(prim_path='{ENV_REGEX_NS}/Robot/links/(left|right)_wheel',update_period=0.0,history_length=1,track_air_time=False)\n    env=Mod4Env(cfg=cfg);vec=")
needle="    env.reset()\n    legids,_=robot.find_joints"
replacement='''    env.reset()
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
    legids,_=robot.find_joints'''
assert needle in s;s=s.replace(needle,replacement)
s=s.replace("        history=env.scene.sensors['wheel_contact_scut'].data.net_forces_w_history", "        history=env.scene.sensors['wheel_contact_scut'].data.net_forces_w_history\n        import warp as wp\n        history_stamp.append(wp.to_torch(env.scene.sensors['wheel_contact_scut']._timestamp_last_update).clone())")
needle="    Path(args.output).write_text(json.dumps(result,indent=2));"
extra='''    env.scene.update=original_update
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
'''
assert needle in s;s=s.replace(needle,extra+needle)
(r/'contact_diagnostic.py').write_text(s,encoding='utf8')
