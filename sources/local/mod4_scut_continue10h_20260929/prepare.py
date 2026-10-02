from pathlib import Path

root=Path(__file__).parent
p=root/'mod4_task.py'
s=p.read_text(encoding='utf-8')
old='''    f = env.scene.sensors[sensor_cfg.name].data.net_forces_w
    if hasattr(f, "torch"):
        f = f.torch
    both = (f.norm(dim=-1) > threshold).all(dim=1).float()
    return value * both'''
new='''    # Frozen SCUT wheelbipe25_v3: max per-wheel force over 3 x 5 ms samples.
    # Keep the original instantaneous sensor unchanged for strict acceptance.
    f = env.scene.sensors["wheel_contact_scut"].data.net_forces_w_history
    if hasattr(f, "torch"):
        f = f.torch
    both = (f.norm(dim=-1).amax(dim=1) > threshold).all(dim=1).float()
    return value * both'''
assert s.count(old)==1
s=s.replace(old,new)
needle='''    wheel_contact = ContactSensorCfg(
        prim_path="{ENV_REGEX_NS}/Robot/links/(left|right)_wheel", update_period=0.0,
        history_length=3, track_air_time=False, debug_vis=False)'''
assert s.count(needle)==1
s=s.replace(needle,needle+'''
    wheel_contact_scut = ContactSensorCfg(
        prim_path="{ENV_REGEX_NS}/Robot/links/(left|right)_wheel", update_period=0.005,
        history_length=3, track_air_time=False, debug_vis=False)
''')
p.write_text(s,encoding='utf-8')
p=root/'validate_rescue.py';s=p.read_text(encoding='utf-8')
s=s.replace("'both_wheels','guide_force'", "'both_wheels','both_wheels_scut_history','left_wheel_contact','right_wheel_contact','left_wheel_fz','right_wheel_fz','guide_force'")
s=s.replace("        h=task.root_height_above_ground(env)", "        history=env.scene.sensors['wheel_contact_scut'].data.net_forces_w_history\n        h=task.root_height_above_ground(env)")
s=s.replace("                'guide_force':guide.norm", "                'both_wheels_scut_history':(history.norm(dim=-1).amax(dim=1)>1.).all(1).float(),\n                'left_wheel_contact':(forces[:,0].norm(dim=-1)>1.).float(),\n                'right_wheel_contact':(forces[:,1].norm(dim=-1)>1.).float(),\n                'left_wheel_fz':forces[:,0,2], 'right_wheel_fz':forces[:,1,2],\n                'guide_force':guide.norm")
s=s.replace("'metric_population':", "'wheel_sensor_body_order':list(env.scene.sensors['wheel_contact'].body_names),\n            'scut_contact_window':'per-wheel peak over 3 samples at 5ms; diagnostic only; strict gate unchanged',\n            'metric_population':")
p.write_text(s,encoding='utf-8')
