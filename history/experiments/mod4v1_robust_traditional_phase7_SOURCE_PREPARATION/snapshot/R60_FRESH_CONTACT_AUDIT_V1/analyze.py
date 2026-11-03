"""Two authorised R60 TRAIN cases: one pass per raw, events only;0newphysics."""
from pathlib import Path
import collections,hashlib,json,math,traceback
R=Path(__file__).resolve().parent;TASK=R.parent;CASES=['r60_tall0_fresh_RM_DR_4605','r60_tall0_fresh_RM_DR_4606'];DT=.0005
SMALL=['run_manual_position_v4.py','MINIHOP_POSITION_TRIGGER_V1/controller.py','MINIHOP_LANDING_V3/controller.py','MINIHOP_OBSERVER_V2/controller.py','MINIHOP_V1/controller.py','MINIHOP_AUDIT_V2/contact_grade_v2.py','MANUAL_FIRST_BAR_V1/grade_rows.py','MANUAL_FIRST_BAR_V1/grade_rows_v2.py']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def new(p,v):assert not p.exists(),str(p);p.write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def meta(p):return {'path':str(p),'bytes':p.stat().st_size,'SHA':sha(p)}
def contacts(x):
    out=[]
    for c in x['contacts']:
        if c['normal_N']<=0:continue
        n=[float(v)*(1 if c['robot_is_geom2']else -1) for v in c['normal_geom1_to_geom2_world']];z=n[2]
        surface='top_up' if z>.9 else 'bottom_down' if z<-.9 else 'front_upper_edge_or_inclined' if abs(n[0])>.8 and .05<z<.9 else 'side_or_edge_not_top'
        out.append({k:c[k] for k in ('robot_geom','robot_body','environment_geom','kind','main_index','normal_N','position_world_m','normal_geom1_to_geom2_world','force_on_robot_world_N3')}|{'normal_toward_robot_world3':n,'normal_surface_description':surface})
    return out

def pose(x,trace):
    a=x['private_contact_diagnostic']['root_rotation_world_from_body33_pre'];dp=x['drivepoint'];k=x['sample_index']//20;z=trace[k];p=z['phase']
    assert z['command_time_s']-1e-8<=x['stage_time_s']<=z['time_s']+1e-8
    return {'sample_index':x['sample_index'],'stage_time_s':x['stage_time_s'],'root_post_time_s':x['root_post_time_s'],'root_PRE_xyz_m':dp['root_xyz_pre_m'],'pitch_roll_yaw_deg':[math.degrees(math.atan2(-a[2][0],math.hypot(a[0][0],a[1][0]))),math.degrees(math.atan2(a[2][1],a[2][2])),math.degrees(math.atan2(a[1][0],a[0][0]))],'root_POST_xyz_m_separate_time':x['root_xyz_post_m'],'cache_stages':x['cache_stages'],'main_normal_N2':x['main_normal_N2'],'guide_normal_N':x['guide_normal_N'],'hard_normal_N':x['hard_normal_N'],'all_world_normal_N':x['all_world_normal_N'],'positive_environment_contacts':contacts(x),'stage_drive_velocity6_rad_s':dp['velocity6_rad_s'],'stage_actual_tau6_Nm':dp['actual_tau6_Nm'],'bracket100Hz':{'command_time_s':z['command_time_s'],'sensor_time_s':z['sensor_time_s'],'sensor_age_s':z['sensor_age_s'],'post_time_s':z['time_s'],'phase':p.get('phase'),'legacy_target_q4_NOT_active_capture_ref':p.get('target_q4'),'actual_landing_position_ref4':p.get('landing_position_ref4'),'landing_transition_weight':p.get('landing_transition_weight'),'landing_capture_started_s':p.get('landing_capture_started_s'),'observer_disabled_logged':p.get('wheel_measurement_disabled_predicted'),'position_decision_time_s':p.get('position_decision_time_s'),'latched_push_time_s':p.get('position_latched_push_time_s'),'encoder_q4_NOT_actual2k_q':z.get('encoder_q4'),'estimated_pitch_rad':z['estimated14'][2],'estimated_vx':z['estimated14'][7],'forward_command_m_s':z.get('forward_command_m_s')},'actual2k_active_or_passive_q':'UNKNOWN_NO_D1_D2_INTEGRATION_OR_TARGET_SUBSTITUTION'}

def schedule(trace,cfg):
    def first(pred):return next((z for z in trace if pred(z)),None)
    d=first(lambda z:z['phase'].get('position_decision_time_s')is not None);push=first(lambda z:z['phase'].get('phase')=='timed_push');cap=first(lambda z:z['phase'].get('landing_capture_started_s')is not None);weight=first(lambda z:z['phase'].get('landing_transition_weight',0)>0);disabled=first(lambda z:z['phase'].get('wheel_measurement_disabled_predicted')is True);obs=first(lambda z:disabled is not None and z['command_time_s']>disabled['command_time_s'] and z['phase'].get('wheel_measurement_disabled_predicted')is False)
    def select(z):return None if z is None else {'command_time_s':z['command_time_s'],'sensor_time_s':z['sensor_time_s'],'post_time_s':z['time_s'],'phase':z['phase']}
    return {'decision_first_logged':select(d),'first_actual_push':select(push),'capture_first_logged':select(cap),'first_positive_K_ff_position_weight':select(weight),'first_observer_disabled':select(disabled),'observer_first_reenabled_after_disable':select(obs),'configured_brake_time_s':cfg['brake_at_s'],'gravity_correction_schedule_not_independently_logged':'same original prepare_estimator source; do not substitute nominal arithmetic for logged flags'}

def scan(case,cfg,v):
    base=TASK/'results'/case;opens={};trace=[]
    with Path(v['trace_artifact']['path']).open('r',encoding='utf-8')as f:
        opens[str(Path(v['trace_artifact']['path']))]=1
        for line in f:trace.append(json.loads(line))
    assert len(trace)==v['controls'];events={};parts={'guide':{'runs':[],'active':None,'ticks':0},'hard':{'runs':[],'active':None,'ticks':0}};air_ticks=0;air_start=None;first_air=None;confirmed=None;landed=None;row_count=0;max_pitch=None;bars=collections.Counter();opened=Path(v['physical_artifact']['path']);opens[str(opened)]=1
    with opened.open('r',encoding='utf-8')as f:
        for line in f:
            x=json.loads(line);k=x['sample_index'];t=x['stage_time_s'];assert k==row_count and abs(t-k*DT)<1e-8;row_count+=1
            a=x['private_contact_diagnostic']['root_rotation_world_from_body33_pre'];pd=abs(math.degrees(math.atan2(-a[2][0],math.hypot(a[0][0],a[1][0]))))
            if max_pitch is None or pd>max_pitch['abs_pitch_deg']:max_pitch={'abs_pitch_deg':pd,'pose':pose(x,trace)}
            sums=collections.defaultdict(float)
            for c in x['environment_contacts']:
                if c['environment_geom'].startswith('rm_bar_'):sums[c['environment_geom']]+=max(0.,c['normal_N'])
            hit={n:f for n,f in sums.items()if f>1.}
            for n in hit:bars[n]+=1
            if hit and 'first_any_bar_over1N'not in events:events['first_any_bar_over1N']={'bar_positive_normal_sums_N':hit,'pose':pose(x,trace),'all_robot_parts_not_just_main':True}
            if x['all_world_normal_N']<=1.:
                if not air_ticks:air_start=t;air_first_pose=pose(x,trace)
                air_ticks+=1
                if first_air is None and air_ticks*DT>=.02:first_air=air_start;confirmed=x['root_post_time_s'];events['first_operational_air']={'start_s':first_air,'confirmed_post_s':confirmed,'duration_threshold_s':.02,'normal_limit_N':1.,'start_pose':air_first_pose,'confirmation_pose':pose(x,trace),'net_world_force_operational_not_hardware_air':True}
            else:
                air_ticks=0
                if first_air is not None and landed is None:landed=t;events['first_landing']=pose(x,trace)
            for name in ('guide','hard'):
                p=parts[name];force=x[name+'_normal_N'];on=force>1.
                if on:
                    p['ticks']+=1;s=pose(x,trace)
                    if p['active']is None:p['active']={'start_stage_s':t,'first':s,'peak':s,'last':s,'ticks':0}
                    run=p['active'];run['ticks']+=1;run['last']=s
                    if force>run['peak'][name+'_normal_N']:run['peak']=s
                elif p['active']is not None:p['runs'].append(p['active']);p['active']=None
    for name,p in parts.items():
        if p['active']is not None:p['runs'].append(p['active']);p['active']=None
        for run in p['runs']:run['duration_s']=run['ticks']*DT;run['last_post_s']=run['last']['root_post_time_s']
        assert p['ticks']==v[name+'_contact_physics_ticks']
    assert row_count==v['physics_steps']==len(trace)*20 and abs(first_air-v['first_all_world_air_s'])<1e-8 and abs(landed-v['first_landing']['stage_time_s'])<1e-8
    events['max_abs_cached_stage_pitch']=max_pitch;events['guide_segments']=parts['guide']['runs'];events['hard_segments']=parts['hard']['runs']
    return {'case':case,'original_metrics':{k:v[k]for k in ('complete','stop','controls','physics_steps','guide_contact_physics_ticks','hard_contact_physics_ticks','end_stable_s','max_pitch_rad','max_roll_rad','maximum_main_mesh_clearance_during_full_air_m','proposed_manual_first_bar_clear_stop_v1','first_flight_main_rear_crossing_bar_back_s')},'schedule':schedule(trace,cfg),'events':events,'bar_rows_counts_not_contactpoint_counts':dict(bars),'raw_producer_references_not_rehashed':[v['trace_artifact'],v['physical_artifact']],'raw_open_counts':opens,'first_landing_record_matches_stream':True,'q_reconstruction_or_fit':False}

def main():
    assert not(R/'SOURCE_PREEXEC.json').exists();assert not(R/'EVENTS.json').exists();inputs={};small=[R/'METHOD_PREDECLARED.md',Path(__file__)]+[TASK/p for p in SMALL]
    for case in CASES:
        base=TASK/'results'/case;cfg=load(base/'config.json');v=load(base/'result.json');src=load(base/'SOURCE_MANIFEST.json');assert cfg['seed']in(4605,4606)and cfg['nominal']is False and cfg['case_id']==case
        source_by_path={str(Path(z['path']).resolve()).lower():z['SHA']for z in src['files']}
        for p in [TASK/x for x in SMALL]:assert sha(p)==source_by_path[str(p.resolve()).lower()],p
        for key in ('trace_artifact','physical_artifact'):
            p=Path(v[key]['path']);assert p.parent==base and p.name in ('trace.jsonl','physics.jsonl')and p.stat().st_size==v[key]['bytes']and v[key]['producer_streamed_once']is True
        inputs[case]=(cfg,v);small.extend([base/'config.json',base/'result.json',base/'SOURCE_MANIFEST.json'])
    pins={str(p):sha(p)for p in small};new(R/'SOURCE_PREEXEC.json',{'status':'METHOD_AND_SMALL_SOURCE_SHA_FIXED_BEFORE_FOUR_RAW_READS','sources':[meta(p)for p in small],'raw_paths_producer_only':[dict(case=c,artifact=k,**v[k])for c,(cfg,v)in inputs.items()for k in ('trace_artifact','physical_artifact')],'new_physics_Git_agents_compile_rawhash':False,'no_other_TRAIN_H5_heldout':True})
    data=[scan(c,*inputs[c])for c in CASES];assert all(sha(Path(p))==h for p,h in pins.items());new(R/'EVENTS.json',{'status':'R60_TWO_FRESH_TRAIN_CONTACT_FACTS_NOT_CONTROLLER_OR_GAIN_SELECTION','cases':data,'time_semantics':'2kforce/contact/cacheR/drive/rootPRE at stage;rootPOST at stage+.0005;control/sensor are bracketing only','single_raw_pass':True,'same_or_different_mechanism_not_assumed':True,'D1_D2_q_not_integrated_as_true_q':True,'old_thresholds_scores_sources_unchanged':True,'physics_compile_Git_agents_rawhash':False,'PH7pending':True})
    def fmt(x):return 'unknown'if x is None else f'{x:.9g}'
    lines=['# R60 fresh TRAIN4605/4606 contact audit（offline only）','','四raw路径与方法/小源SHA先锁；各trace/physics仅stream一遍，producerSHA沿用。没有D1/D2 q积分/控制/拟合/physics/Git/新agent/H5/heldout/mesh/rawhash。']
    compact=[]
    for c in data:
        e=c['events'];s=c['schedule'];mm=c['original_metrics'];lines+=['',f"## {c['case']}",f"原gate={mm['proposed_manual_first_bar_clear_stop_v1']}; guide/hard ticks={mm['guide_contact_physics_ticks']}/{mm['hard_contact_physics_ticks']}; endstable={mm['end_stable_s']!r}; firstflightmainrear={mm['first_flight_main_rear_crossing_bar_back_s']!r}（非整机器人净跨）。",'|event|stage/control s|rootPREz m|pitch deg|main L/R, guide, hard N|','|---|---:|---:|---:|---|']
        for name,z in [('decision',s['decision_first_logged']),('push',s['first_actual_push']),('capture',s['capture_first_logged']),('Kffref_weight>0',s['first_positive_K_ff_position_weight']),('observer_reenable',s['observer_first_reenabled_after_disable'])]:lines.append(f"|{name}|{fmt(z['command_time_s'])if z else'unknown'}|—|—|100Hz loggedphase/flags; not2kpose|")
        selected=[('anybar>1',e.get('first_any_bar_over1N',{}).get('pose')),('air_onset',e.get('first_operational_air',{}).get('start_pose')),('air_confirm',e.get('first_operational_air',{}).get('confirmation_pose')),('landing',e.get('first_landing'))]
        for kind in ('guide','hard'):
            runs=e[kind+'_segments']
            if runs:
                selected.extend([(kind+'_first',runs[0]['first']),(kind+'_peak',max((r['peak']for r in runs),key=lambda p:p[kind+'_normal_N'])),(kind+'_last',runs[-1]['last'])])
        for name,p in selected:
            if p:lines.append(f"|{name}|{fmt(p['stage_time_s'])}|{p['root_PRE_xyz_m'][2]:.9g}|{p['pitch_roll_yaw_deg'][0]:.9g}|{p['main_normal_N2']}, {p['guide_normal_N']:.9g}, {p['hard_normal_N']:.9g}|")
        lines.append('guide/hard segment first/peak/last/force/contactsurface和邻近100Hz实际landing_ref4/weight/observer详EVENTS；legacytarget不冒currentref，2k单腿q未知。')
        compact.append({'case':c['case'],'metrics':mm,'schedule_times':{k:None if z is None else z['command_time_s']for k,z in s.items()if isinstance(z,dict)or z is None},'first_bar':e.get('first_any_bar_over1N'),'landing':e.get('first_landing'),'guide_segments':e['guide_segments'],'hard_segments':e['hard_segments']})
    lines+=['','两案分别报告，不从单一时序推独一机制；bar/top/front-edge按实存normal/point区分，guide不冒main支持，positive force点数与>1N物理row不同。完整源前后SHA/原计数核对见RECEIPT；仅PH7pending诊断，原失败不改。']
    report='\n'.join(lines)+'\n';assert report.count('\n')<=90;(R/'REPORT.md').write_text(report,encoding='utf-8');new(R/'RECEIPT.json',{'status':'R60_BOUNDED_TWO_CASE_OFFLINE_FACTS_COMPLETE','source_preexec_SHA':sha(R/'SOURCE_PREEXEC.json'),'events_SHA':sha(R/'EVENTS.json'),'report_SHA':sha(R/'REPORT.md'),'report_lines':report.count('\n'),'raw_open_counts':[c['raw_open_counts']for c in data],'small_sources_before_after_SHA_equal':True,'old_source_threshold_scores_modified':False,'D1_D2_q_reconstruction':False,'new_physics_compile_Git_GPU_agents_realIO_rawhash_H5':False,'PH7pending':True})
    print(json.dumps({'report':str(R/'REPORT.md'),'report_lines':report.count('\n'),'events_bytes':(R/'EVENTS.json').stat().st_size,'summary':compact},ensure_ascii=False,indent=2))
if __name__=='__main__':
    try:main()
    except BaseException:
        n=1
        while(R/f'ERROR_{n:03d}.txt').exists():n+=1
        (R/f'ERROR_{n:03d}.txt').write_text(traceback.format_exc(),encoding='utf-8');(R/f'ERROR_SOURCE_{n:03d}.py').write_bytes(Path(__file__).read_bytes());raise
