from pathlib import Path
r=Path(__file__).resolve().parent
t=(r/'validate_speed_baseline.py').read_text(encoding='utf-8')
t=t.replace('    env=Mod4Env(cfg=cfg);', '''    from isaaclab.sensors import ContactSensorCfg
    cfg.scene.wheel_contact_legacy_capture=ContactSensorCfg(
        prim_path='{ENV_REGEX_NS}/Robot/links/(left|right)_wheel',update_period=.005,
        history_length=3,track_air_time=False,debug_vis=False)
    env=Mod4Env(cfg=cfg);''')
t=t.replace("'both_wheels_scut_history','left_wheel_contact'", "'both_wheels_scut_history','both_wheels_history_5ms','height_credit_active','height_credit_legacy','left_wheel_contact'")
t=t.replace("        history=env.scene.sensors['wheel_contact_scut'].data.net_forces_w_history", """        history_active=env.scene.sensors['wheel_contact_scut'].data.net_forces_w_history
        # Read the shadow only at control endpoints, retaining the old 10 ms gate.
        history=env.scene.sensors['wheel_contact_legacy_capture'].data.net_forces_w_history
        both_active=(history_active.norm(dim=-1).amax(dim=1)>1.).all(dim=1).float()
        both_legacy=(history.norm(dim=-1).amax(dim=1)>1.).all(dim=1).float()
        height_soft=task.height_track(env,sigma=task.SCUT_H_SOFT_SIGMA)""")
t=t.replace("'both_wheels_scut_history':(history.norm(dim=-1).amax(dim=1)>1.).all(1).float(),", """'both_wheels_scut_history':both_legacy,
                'both_wheels_history_5ms':both_active,
                'height_credit_active':height_soft*both_active,
                'height_credit_legacy':height_soft*both_legacy,""")
t=t.replace("    strict_instant=common &", "    strict_5ms=common & (per['both_wheels_history_5ms']>=.9)\n    strict_instant=common &")
t=t.replace("        d['strict_pass_window']=d['strict_pass']", """        d['strict_pass_window']=d['strict_pass']
        d['strict_pass_window_legacy_capture']=d['strict_pass']
        d['strict_pass_window_5ms']=float(strict_5ms[ids].float().mean())""")
t=t.replace("'gate_version':'window_contact_v2_dual_reporting_20260929'", "'gate_version':'legacy_gate_preserved_with_corrected_5ms_reporting_20260930'")
t=t.replace("    result['strict_pass_window']=result['strict_pass']", """    result['strict_pass_window']=result['strict_pass']
    result['strict_pass_window_legacy_capture']=result['strict_pass']
    result['strict_pass_window_5ms']=result['physics_pass'] and all(g['strict_pass_window_5ms']>=.8 for g in groups)
    result['contact_capture_metadata']=getattr(env,'_contact_capture_metadata',{'enabled':False})
    result['graduation_gate_contact_source']='legacy control-endpoint shadow; corrected 5ms stats do not automatically promote speed'
    result['height_credit_semantics']='unweighted exp height * recent contact; weighted per control step = credit * 0.3 * 0.01'
    result['physical_contact_evidence']='reports/contact_probe_7450_20260930/FINDINGS.md in source root; 2kHz unload/gap/slip retained there, not overwritten by window stats'""")
assert 'strict_5ms=' in t and 'wheel_contact_legacy_capture' in t
compile(t,'validate_speed.py','exec')
(r/'validate_speed.py').write_text(t,encoding='utf-8')
print('Evaluator syntax passed: legacy graduation gate retained')
