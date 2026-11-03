"""Exactly one content pass per allowed raw file. Stdlib, no project imports."""
from pathlib import Path
import bisect,hashlib,json,math,traceback
D=Path(__file__).resolve().parent;R=D.parent
load=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
method=load(D/'METHOD.json');lock=load(D/'SOURCE_LOCK.json')
assert sha(D/'METHOD.json')==lock['method_SHA']
opened=[];progress={};completed=[]
def finite(x,path='row'):
    if isinstance(x,float):assert math.isfinite(x),('NONFINITE',path)
    elif isinstance(x,list):
        for i,v in enumerate(x):finite(v,path+f'[{i}]')
    elif isinstance(x,dict):
        for k,v in x.items():finite(v,path+'.'+k)
def vec(v,n):
    assert isinstance(v,list)and len(v)==n
    assert all(isinstance(x,(int,float))and not isinstance(x,bool)and math.isfinite(x)for x in v)
    return v
def rows(path):
    rel=path.relative_to(R).as_posix();assert rel in method['raw_paths'] and rel not in opened
    opened.append(rel)
    with path.open(encoding='utf-8') as f:
        for i,line in enumerate(f):
            x=json.loads(line,parse_constant=lambda s:(_ for _ in()).throw(ValueError(s)))
            finite(x);yield i,x

def control(r,i):
    p=r['phase'];e=vec(r['estimated14'],14);before=r['grade_before'];after=r['grade_after']
    assert abs(r['command_time_s']-.01*i)<1e-7 and abs(r['time_s']-(i+1)*.01)<1e-7
    assert abs(before['time']-r['command_time_s'])<1e-7 and abs(after['time']-r['time_s'])<1e-7
    keys=('phase','target_q4','target_qd4','landing_position_ref4','landing_velocity_ref_used4',
          'landing_transition_weight','landing_capture_started_s','wheel_measurement_disabled_predicted',
          'observer_quarantine_until_s','observer_quarantine_is_timer_not_contact','phase_source','contact_or_flight_trusted')
    assert all(k in p for k in keys),('missing phase fields',set(keys)-p.keys())
    assert 0<=p['landing_transition_weight']<=1
    return dict(index=i,command_time_s=r['command_time_s'],control_post_time_s=r['time_s'],
        sensor_end_label_s=r['sensor_time_s'],sensor_age_s=r['sensor_age_s'],phase={k:p[k]for k in keys},
        estimated14=e,estimated_roll=r['estimated_roll'],observed_encoder_q4=vec(r['encoder_q4'],4),
        requested_tau6=vec(r['requested_tau6'],6),
        true_before=dict(time_s=before['time'],xyz=vec(before['xyz'],3),pitch=before['pitch_true'],roll=before['roll_true'],body_velocity=vec(before['body_velocity'],3)),
        true_after=dict(time_s=after['time'],xyz=vec(after['xyz'],3),pitch=after['pitch_true'],roll=after['roll_true'],body_velocity=vec(after['body_velocity'],3)),
        last_substep_stage_time_s=None,last_substep_bounded_ctrl6=None)

def contact(c):
    return {k:c[k]for k in ('robot_geom','robot_body','environment_geom','kind','normal_N','position_world_m',
                            'normal_geom1_to_geom2_world','force_on_robot_world_N3')}

def event(r,tag,controls):
    idx=r['sample_index'];j=idx//20;t=r['stage_time_s'];c=controls[j];diag=r['private_contact_diagnostic'];dp=r['drivepoint']
    rot=diag['root_rotation_world_from_body33_pre']
    angles=None
    if rot is not None:
        assert len(rot)==3
        for a in rot:vec(a,3)
        angles=dict(pitch=math.atan2(-rot[2][0],math.hypot(rot[0][0],rot[1][0])),
            roll=math.atan2(rot[2][1],rot[2][2]),yaw=math.atan2(rot[1][0],rot[0][0]))
    return dict(tag=tag,sample_index=idx,stage_time_s=t,root_post_time_s=r['root_post_time_s'],
        root_PRE_xyz_m=dp['root_xyz_pre_m'],root_PRE_world_from_body33=rot,root_PRE_rpy=angles,
        root_POST_xyz_m=r['root_xyz_post_m'],control_index=j,request_to_drive_stage_age_s=t-c['command_time_s'],
        phase=c['phase']['phase'],landing_K_ff_eq_weight=c['phase']['landing_transition_weight'],
        guide_normal_N=r['guide_normal_N'],main_normal_N2=r['main_normal_N2'],hard_normal_N=r['hard_normal_N'],
        total_environment_normal_N=r['all_world_normal_N'],air_run_s=r['air_run_s'],air_qualified=r['air_qualified'],
        bounded_ctrl6_Nm=dp['actual_tau6_Nm'],actual_dq6_rad_s=dp['velocity6_rad_s'],actual_active_q4_2k=None,
        positive_contacts=[contact(c)for c in r['contacts']],
        private_bounds=r['private_full_collision_bounds'])

def scan(case):
    name=case['case'];base=R/'results'/name;res=load(base/'result.json');cfg=load(base/'config.json')
    progress.clear();progress.update(case=name,trace_rows=0,physics_rows=0,events={})
    controls=[];transitions=[];important=set();last_phase=None;last_observer=None
    for i,r in rows(base/'trace.jsonl'):
        assert i<800
        c=control(r,i);controls.append(c);progress['trace_rows']=i+1
        phase=c['phase']['phase'];obs=c['phase']['wheel_measurement_disabled_predicted']
        if phase!=last_phase or obs!=last_observer:
            transitions.append(dict(control_index=i,time_s=c['command_time_s'],phase=phase,wheel_observer_disabled=obs,
                landing_weight=c['phase']['landing_transition_weight']))
            important.add(i)
        last_phase=phase;last_observer=obs
        if c['phase']['landing_transition_weight']>0 and not any(t.get('first_positive_landing_weight')for t in transitions):
            transitions.append(dict(control_index=i,time_s=c['command_time_s'],first_positive_landing_weight=True));important.add(i)
        if c['phase']['landing_transition_weight']==1 and not any(t.get('first_full_landing_weight')for t in transitions):
            transitions.append(dict(control_index=i,time_s=c['command_time_s'],first_full_landing_weight=True));important.add(i)
    assert len(controls)==800
    ev=progress['events'];guide_count=0;bar_count=0;peak_guide=-1.;last_guide=None;episodes=[];current=None
    air_start=None;air_count=0;qualified_seen=False;first_air_start=None;air_confirmed_post=None;pending_air_event=None
    prev_stage=None
    for i,r in rows(base/'physics.jsonl'):
        assert i<16000 and r['sample_index']==i and r['schema']=='MINIHOP_PRIVATE_GRADE_V2'
        progress['physics_rows']=i+1;t=r['stage_time_s'];post=r['root_post_time_s'];dp=r['drivepoint'];j=i//20
        assert dp['physics_tick']==i and dp['time_s']==t and abs(post-t-.0005)<1e-8
        assert abs(t-i*.0005)<1e-7 and abs(t-controls[j]['command_time_s']-(i%20)*.0005)<1e-7
        assert r['cache_stages']==dict(force_s=t,contact_geometry_s=t,mesh_s=t,drive_s=t,root_post_s=post)
        assert r['private_contact_diagnostic']['stage_time_s']==t
        vec(dp['actual_tau6_Nm'],6);vec(dp['velocity6_rad_s'],6);vec(dp['root_xyz_pre_m'],3)
        assert r['contacts']==[c for c in r['environment_contacts']if c['normal_N']>0]
        total=math.fsum(c['normal_N']for c in r['environment_contacts'])
        assert total==r['all_world_normal_N']
        assert math.fsum(c['normal_N']for c in r['environment_contacts']if c['kind']=='guide_roller')==r['guide_normal_N']
        if total<=1:
            if not air_count:
                air_start=t;pending_air_event=event(r,'first_qualified_air_run_start',controls)
            air_count+=1
        else:air_count=0;air_start=None
        assert r['air_run_s']==air_count*.0005 and r['air_qualified']==(air_count>=40)
        if r['air_qualified'] and not qualified_seen:
            qualified_seen=True;first_air_start=air_start;air_confirmed_post=post
            ev['first_qualified_air_run_start']=pending_air_event
            ev['first_qualified_air_confirmation']=event(r,'first_qualified_air_confirmation',controls)
            ev['first_qualified_air_confirmation']['run_start_stage_s']=air_start
        if qualified_seen and total>1 and 'first_landing'not in ev:
            ev['first_landing']=event(r,'first_landing',controls)
            assert abs(t-res['first_landing']['stage_time_s'])<1e-8
            assert total==res['first_landing']['all_world_normal_N'] and r['contacts']==res['first_landing']['contacts']
        hits=[c for c in r['contacts']if c['environment_geom']==res['first_transverse_bar']['name']and c['normal_N']>1.]
        if hits:
            bar_count+=1
            if 'first_bar_individual_gt1N'not in ev:
                ev['first_bar_individual_gt1N']=event(r,'first_bar_individual_gt1N',controls)
                ev['first_bar_individual_gt1N']['qualifying_bar_contacts']=[contact(c)for c in hits]
        if r['guide_normal_N']>1.:
            guide_count+=1;now_event=None
            if 'guide_first'not in ev:ev['guide_first']=event(r,'guide_first',controls)
            if r['guide_normal_N']>peak_guide:
                peak_guide=r['guide_normal_N'];ev['guide_peak']=event(r,'guide_peak',controls)
            last_guide=event(r,'guide_last',controls)
            if current is None:
                current=dict(first_sample=i,start_stage_s=t,last_stage_s=t,ticks=0,peak_normal_N=0.,surfaces=set(),robots=set())
                episodes.append(current)
            current['last_stage_s']=t;current['ticks']+=1;current['peak_normal_N']=max(current['peak_normal_N'],r['guide_normal_N'])
            for c in r['contacts']:
                if c['kind']=='guide_roller':current['surfaces'].add(c['environment_geom']);current['robots'].add(c['robot_geom'])
        else:current=None
        if i%20==19:
            controls[j]['last_substep_stage_time_s']=t;controls[j]['last_substep_bounded_ctrl6']=dp['actual_tau6_Nm']
        prev_stage=t
    assert progress['physics_rows']==16000 and guide_count==res['guide_contact_physics_ticks']==case['original_guide_ticks']
    assert abs(first_air_start-res['first_all_world_air_s'])<1e-8
    ev['guide_last']=last_guide
    ev.setdefault('first_bar_individual_gt1N',None)
    for e in ev.values():
        if e is not None:important.add(e['control_index'])
    selected=sorted({k+d for k in important for d in (-1,0,1)if 0<=k+d<800})
    for e in episodes:e['surfaces']=sorted(e['surfaces']);e['robots']=sorted(e['robots'])
    return dict(case=name,trace_rows=800,physics_rows=16000,guide_ticks=guide_count,original_pass=res['proposed_manual_first_bar_clear_stop_v1'],
        first_bar=res['first_transverse_bar'],first_bar_individual_gt1N_ticks=bar_count,
        first_air_run_start_stage_s=first_air_start,first_air_confirmation_post_s=air_confirmed_post,
        original_first_flight_main_rear_crossing_s=res['first_flight_main_rear_crossing_bar_back_s'],
        first_air_confirmation_lag_s=air_confirmed_post-first_air_start,events=ev,guide_episodes=episodes,
        control_transitions=transitions,control_neighbours=[controls[k]for k in selected],
        DR_metadata_context_only=dict(D0_only_nominal=res['DR']['D0']['D0_only_nominal_episode'],D1_enabled=res['DR']['D1']['enabled'],
            D2_bias_present=True,D3_feedback_delay_ticks=res['DR']['D3']['shared_feedback_delay_ticks100Hz'],
            D4_target_delay_us6=res['DR']['D4']['action_delay_us6']),
        unknown=method['unknowns'])

try:
    for case in lock['cases']:
        completed.append(scan(case))
    assert len(opened)==4 and set(opened)==set(method['raw_paths'])
    for case in lock['cases']:
        for x in case['raw']:
            st=(R/x['path']).stat();assert st.st_size==x['bytes'] and st.st_mtime_ns==x['mtime_ns']
    output=dict(kind='SINGLE_PASS_TWO_TRAIN_PRIVATE_EVENTS_NOT_UNIQUE_CAUSE_OR_QUALIFICATION',method_SHA=sha(D/'METHOD.json'),
        source_lock_SHA=sha(D/'SOURCE_LOCK.json'),extractor_SHA=sha(Path(__file__)),raw_content_opens=opened,raw_archival_hashes=0,
        cases=completed,PH7_pending=True)
    with (D/'EVENTS.json').open('x',encoding='utf-8')as f:json.dump(output,f,separators=(',',':'),allow_nan=False);f.write('\n')
    tiny=[]
    for c in completed:
        tiny.append(dict(case=c['case'],guide_ticks=c['guide_ticks'],first_air=c['first_air_run_start_stage_s'],
            qualified_post=c['first_air_confirmation_post_s'],events={k:None if v is None else dict(stage=v['stage_time_s'],phase=v['phase'],
                pitch=v['root_PRE_rpy']['pitch']if v['root_PRE_rpy']else None,guide_N=v['guide_normal_N'],
                surfaces=sorted({p['environment_geom']for p in v['positive_contacts']}),weight=v['landing_K_ff_eq_weight'])for k,v in c['events'].items()},
            episodes=c['guide_episodes'],control_rows_retained=len(c['control_neighbours'])))
    print(json.dumps(dict(status='SUCCESS_SINGLE_PASS',raw_content_opens=opened,event_bytes=(D/'EVENTS.json').stat().st_size,cases=tiny),indent=2))
except BaseException:
    with (D/'PARTIAL_ERROR.json').open('x',encoding='utf-8')as f:
        json.dump(dict(status='PARTIAL_NOT_SEALED_NO_RESCAN',traceback=traceback.format_exc(),raw_content_opens=opened,progress=progress,completed=completed),f,allow_nan=False)
    raise
