"""Physical DR readback and explicit practical closeout, without quality vetoes."""
import math
RANGES={'white_v2':{'mass':[.925,1.075],'motor':[.925,1.075],'friction':[.75,1.]},
        'white_v3':{'mass':[.9,1.1],'motor':[.9,1.1],'friction':[.7,1.]}}

def parameter_readback(r,profile,kind):
    a=r.get('initial_parameter_audit') or r.get('mild_initial_parameters')
    z=r.get('final_parameter_audit') or r.get('mild_final_parameters')
    if a is None and z is None:
        assert kind=='flat' and profile=='nominal', 'Missing actual parameter readback'
        return {'provided':False,'scope':'Original nominal flat protocol provides no separate parameter object'}
    assert a and z and a['actual_parameters_pass'] is True and z['actual_parameters_pass'] is True
    if profile!='nominal':
        for obj in (a,z):
            assert obj['profile']==profile and obj['registered_ranges']==RANGES[profile]
            assert obj['material_buckets']==33 and obj['legacy_full_dr_disabled'] is True
            for key,recipe in (('mass_inertia_factor_range','mass'),('friction_range','friction')):
                lo,hi=obj[key];low,high=RANGES[profile][recipe]
                assert math.isfinite(lo) and math.isfinite(hi) and low-1e-5<=lo<=hi<=high+1e-5
            assert set(obj['motor_strength'])=={'legs','wheels'}
            for item in obj['motor_strength'].values():
                assert RANGES[profile]['motor'][0]-1e-5<=item['min']<=item['max']<=RANGES[profile]['motor'][1]+1e-5
                assert item['per_step_noise_abs_error']==0
            assert all(math.isfinite(v) and 0<=v<(1e-5 if k=='mass_relative_error' else 1e-6) for k,v in obj['errors'].items())
    return {'provided':True,'initial_and_final_pass':True,'profile':profile}

def paired_review(pairs,read,flat_gate,spin_gate,target,checkpoint,profiles=('nominal','white_v2')):
    rows=[];worlds=[];survival={'flat':0,'spin':0,'world':0}
    assert len(pairs)==6
    assert {(p['seed'],p['kind']) for p in pairs}=={(s,k) for s in (20261002,20261003) for k in ('flat','spin','world')}
    for pair in pairs:
        seed,kind=pair['seed'],pair['kind'];assert len(pair['paths'])==len(profiles)
        reports=[read(p) for p in pair['paths']]
        for r,profile in zip(reports,profiles):
            assert r['checkpoint']==checkpoint['path'] and r['seed']==seed
            actual_profile=r.get('profile') or (r.get('mild_initial_parameters') or {}).get('profile')
            assert actual_profile==profile or (actual_profile is None and kind=='flat' and profile=='nominal' and r.get('mode')=='deterministic_policy')
            assert r['steps']==1500 and r['seconds']==15
            verdict=flat_gate(r) if kind=='flat' else spin_gate(r,'spin',15)
            assert verdict['pass_'],verdict
            alive=(r.get('per_environment') or {}).get('alive') if kind=='flat' else r['alive']
            assert all(x is True for x in alive)
            survival[kind]+=len(alive)
            pa=parameter_readback(r,profile,kind)
            item=dict(seed=seed,kind=kind,profile=profile,admission=verdict,parameter_readback=pa,
                      report_path=pair['paths'][profiles.index(profile)],survivors=len(alive))
            if kind=='world':
                t=target(r,.5);worlds.append(t);item['world_target']=t
            rows.append(item)
        for r in reports[1:]:
            assert all(r[k]==reports[0][k] for k in ('reset_joint_pos_before_physics','reset_root_before_physics')),'Full initial root/q mismatch'
    return dict(pass_=True,checkpoint=checkpoint,rows=rows,world_tracking=worlds,survival=survival,
                world_progress_05_confirmed=all(x['pass_'] for x in worlds),all_initial_root_q_exact=True,
                performance_target_is_learning_veto=False)

def compact_worlds(worlds):
    result=[]
    for t in worlds:
        rows=t['rows'];failed=[r for r in rows if not r['pass_']]
        result.append(dict(passed=sum(r['pass_'] for r in rows),total=len(rows),
            along_range=[min(r['along_m_s'] for r in rows),max(r['along_m_s'] for r in rows)],
            max_abs_net_cross=max(abs(r['cross_m_s']) for r in rows),
            failures=[{k:r[k] for k in ('env_id','group_id','along_m_s','cross_m_s','command_yaw_rad_s','observed_yaw_rad_s')} for r in failed],
            whole_cycles_retained=True,world_progress_05_confirmed=t['pass_']))
    return result
