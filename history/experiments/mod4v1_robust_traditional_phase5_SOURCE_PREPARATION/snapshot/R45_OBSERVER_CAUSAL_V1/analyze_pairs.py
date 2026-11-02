"""Offline R44->R45 four TRAIN pairs. Only4222 physics streams, no new physics.
Control-sample bit/discrete equality is NOT2k physics bit equality. No rawhash.
"""
from pathlib import Path
import hashlib,json,math,struct
import numpy as np
R=Path(__file__).resolve().parent;TASK=R.parent;SEEDS=range(4221,4225)
EXCLUDE_TOP={'phase','wall_s','wall_ms','wall_elapsed_ns','solve_ms','controller_ms','log_wall_s'}

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def leaves(x,path=''):
    if isinstance(x,dict):
        for k,v in x.items():
            if not path and k in EXCLUDE_TOP:continue
            if any(t in k.lower() for t in ('wall','elapsed_ns','performance','perf_counter')):continue
            yield from leaves(v,path+'/'+k)
    elif isinstance(x,list):
        for i,v in enumerate(x):yield from leaves(v,path+'/'+str(i))
    else:yield path,x

def equal(a,b):
    if isinstance(a,float) and isinstance(b,float):return struct.pack('>d',a)==struct.pack('>d',b)
    return type(a) is type(b) and a==b

def compare(a,b):
    x=dict(leaves(a));y=dict(leaves(b));common=x.keys()&y.keys();diff=[{'path':k,'old':x[k],'new':y[k]} for k in sorted(common) if not equal(x[k],y[k])]
    return {'common_leaves':len(common),'diff_count':len(diff),'first_differences':diff[:12],'only_old':sorted(x.keys()-y.keys()),'only_new':sorted(y.keys()-x.keys())}

def support_runs(rows,key,threshold,begin):
    runs=[];start=None;last=None;n=0;peak=0.
    for x in rows:
        if x['stage_time_s']<begin:continue
        yes=key(x)>threshold
        if yes:
            if start is None:start=x['stage_time_s'];n=0;peak=0.
            n+=1;peak=max(peak,float(key(x)));last=x['root_post_time_s']
        elif start is not None:runs.append({'stage_start_s':start,'last_post_s':last,'physics_samples':n,'duration_s':n*.0005,'peak_N':peak});start=None
    if start is not None:runs.append({'stage_start_s':start,'last_post_s':last,'physics_samples':n,'duration_s':n*.0005,'peak_N':peak})
    return runs

def pose(x,control):
    private=x.get('private_contact_diagnostic',{});rot=private.get('root_rotation_world_from_body33_pre');pitch=roll=yaw=None
    if rot is not None:
        a=np.asarray(rot,float);pitch=math.atan2(-a[2,0],math.hypot(a[0,0],a[1,0]));roll=math.atan2(a[2,1],a[2,2]);yaw=math.atan2(a[1,0],a[0,0])
    stage=x['stage_time_s'];near=next((z for z in control if z['command_time_s']<=stage<z['time_s']),None)
    return {'stage_time_s':stage,'root_post_time_s':x['root_post_time_s'],'cache_stages':x['cache_stages'],'actual_root_xyz_pre_m':x['drivepoint']['root_xyz_pre_m'],'actual_root_xyz_post_m':x['root_xyz_post_m'],'actual_stage_pitch_roll_yaw_rad':[pitch,roll,yaw],'actual_stage_pitch_roll_deg':None if pitch is None else [math.degrees(pitch),math.degrees(roll)],'actual_drive_velocity6_rad_s':x['drivepoint']['velocity6_rad_s'],'actual_drive_tau6_Nm':x['drivepoint']['actual_tau6_Nm'],'main_normal_N2':x['main_normal_N2'],'guide_normal_N':x['guide_normal_N'],'hard_normal_N':x['hard_normal_N'],'all_world_normal_N':x['all_world_normal_N'],'positive_guide_contacts':[c for c in x['contacts'] if c['kind']=='guide_roller'],'bracketing_control':None if near is None else {'pre_s':near['command_time_s'],'post_s':near['time_s'],'sensor_s':near['sensor_time_s'],'encoder_q4':near['encoder_q4'],'target_q4':near['phase']['target_q4'],'truth_symmetric_hip_delta_before':near['grade_before']['state'][2:4],'truth_symmetric_hip_delta_after':near['grade_after']['state'][2:4],'estimated14':near['estimated14']},'actual_perleg_q4_at2k_not_persisted':'unknown; no reconstruction from commandedposture','not_same_time_controlq_or_target_as2ktruth':True}

def physics_detail(base,result,control):
    # ONLY authorized bad-seed4222 original raw; use producerSHA reference, no hash.
    assert base.name in ('r44_miniDR_4222','r45_quarantineDR_4222');rows=[]
    with (base/'physics.jsonl').open('r',encoding='utf-8') as f:
        for line in f:rows.append(json.loads(line))
    assert len(rows)==result['physics_steps'];begin=1.5;land=result['first_landing']['stage_time_s'];after=[x for x in rows if x['stage_time_s']>=begin]
    guides=[x for x in after if x['guide_normal_N']>1.];positives=[x for x in after if x['guide_normal_N']>0.];hard=[x for x in after if x['hard_normal_N']>1.]
    assert len(guides)==result['after_trigger_guide_contact_physics_ticks'] and len(hard)==result['after_trigger_hard_contact_physics_ticks']
    maxguide=max(guides,key=lambda x:x['guide_normal_N']) if guides else None;landing=min(rows,key=lambda x:abs(x['stage_time_s']-land));support=support_runs(rows,lambda x:x['all_world_normal_N'],1.,land);air=support_runs(rows,lambda x:-x['all_world_normal_N'],-1.,land);both=support_runs(rows,lambda x:min(x['main_normal_N2']),1.,land);guideruns=support_runs(rows,lambda x:x['guide_normal_N'],1.,begin)
    # Air uses <=1 exactly, not strict<1; compute explicitly to preserve gate.
    gap=[];start=None;n=0;end=None
    for x in rows:
        if x['stage_time_s']<land:continue
        if x['all_world_normal_N']<=1.:
            if start is None:start=x['stage_time_s'];n=0
            n+=1;end=x['root_post_time_s']
        elif start is not None:gap.append({'stage_start_s':start,'last_post_s':end,'physics_samples':n,'duration_s':n*.0005});start=None
    if start is not None:gap.append({'stage_start_s':start,'last_post_s':end,'physics_samples':n,'duration_s':n*.0005})
    names={}
    for x in guides:
        for c in x['contacts']:
            if c['kind']=='guide_roller':names.setdefault(c['robot_geom'],{'positive_contact_points_in_gate_ticks':0,'max_normal_N':0.});names[c['robot_geom']]['positive_contact_points_in_gate_ticks']+=1;names[c['robot_geom']]['max_normal_N']=max(names[c['robot_geom']]['max_normal_N'],c['normal_N'])
    return {'case':base.name,'physics_source_producer':result['physical_artifact'],'producer_SHA_reused_not_recomputed':True,'physics_rows_read':len(rows),'first_landing':pose(landing,control),'first_any_positive_guide_after_trigger':None if not positives else pose(positives[0],control),'first_guide_over_gate_1N':None if not guides else pose(guides[0],control),'peak_guide_tick':None if maxguide is None else pose(maxguide,control),'after_trigger_guide_ticks_gt1N':len(guides),'after_trigger_guide_positive_ticks_gt0N':len(positives),'guide_tick_duration_s':len(guides)*.0005,'guide_runs':guideruns,'guide_names_actual_positive_points':names,'hard_ticks_gt1N':len(hard),'post_landing_world_support_runs':support,'post_landing_le1N_gaps':gap,'post_landing_bothmain_gt1N_runs':both,'end_of_stream_lastphysics':pose(rows[-1],control),'support_identity_and_forces_offline_only':True}

def main(out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True);assert not (out/'RESULT.json').exists();pairs=[];loaded={};source=[]
    for seed in SEEDS:
        old=TASK/'results'/f'r44_miniDR_{seed}';new=TASK/'results'/f'r45_quarantineDR_{seed}';a=load(old/'result.json');b=load(new/'result.json');ca=load(old/'config.json');cb=load(new/'config.json');assert a['model_SHA']==b['model_SHA'] and a['DR']==b['DR'],'Not same paired model/DR receipt'
        aa=[];bb=[]
        for base,rows in ((old,aa),(new,bb)):
            with (base/'trace.jsonl').open('r',encoding='utf-8') as f:
                for line in f:rows.append(json.loads(line))
            for p in (base/'result.json',base/'config.json',base/'SOURCE_MANIFEST.json'):source.append({'path':str(p),'bytes':p.stat().st_size,'SHA':sha(p)})
        assert len(aa)==a['controls']==len(bb)==b['controls']==600
        prefix=[];first_full_diff=None;schedule_diffs=[]
        for i,(x,y) in enumerate(zip(aa,bb)):
            assert equal(x['command_time_s'],y['command_time_s']);c=compare(x,y)
            if x['command_time_s']<2.0:prefix.append(c)
            if first_full_diff is None and c['diff_count']:first_full_diff={'control_index':i,'command_time_s':x['command_time_s'],'post_time_s':x['time_s'],'diff':c}
            for k in ('phase','target_q4','target_qd4','phase_source','since_operator_trigger_s'):
                if k in x['phase'] and k in y['phase'] and not all(z['diff_count']==0 and not z['only_old'] and not z['only_new'] for z in [compare({'schedule':x['phase'][k]},{'schedule':y['phase'][k]})]):schedule_diffs.append({'i':i,'time':x['command_time_s'],'key':k})
        assert len(prefix)==200;bitsame=all(z['diff_count']==0 and not z['only_old'] and not z['only_new'] for z in prefix)
        def gates(x):return {'flat_scene':x['config']['scene']=='flat','complete':x['complete'],'peak_fullair_mesh_clearance_ge0p08':x['maximum_main_mesh_clearance_during_full_air_m'] is not None and x['maximum_main_mesh_clearance_during_full_air_m']>=.08,'after_trigger_hard_eq0':x['after_trigger_hard_contact_physics_ticks']==0,'after_trigger_guide_eq0':x['after_trigger_guide_contact_physics_ticks']==0,'endstable_ge2p0':x['end_stable_s']>=2.,'original_combined_pass':x['proposed_flat_clear80mm_recover2s_v2']}
        def vals(x):return {k:x[k] for k in ('complete','stop','controls','physics_steps','max_all_world_air_s','maximum_main_mesh_clearance_during_full_air_m','after_trigger_guide_contact_physics_ticks','after_trigger_hard_contact_physics_ticks','end_stable_s','max_stable_s','max_pitch_rad','max_roll_rad','max_closure_m','max_mimic_rad','proposed_flat_clear80mm_recover2s_v2')}
        pairs.append({'seed':seed,'model_and_DR_receipt_exact_equal':True,'old':vals(a),'new':vals(b),'old_gates':gates(a),'new_gates':gates(b),'exact_pre2p00_control_comparison':{'count':len(prefix),'time_start_s':aa[0]['command_time_s'],'last_command_time_s':aa[199]['command_time_s'],'shared_leaf_comparisons':sum(x['common_leaves'] for x in prefix),'all_shared_floats_binary64_bits_and_discrete_values_equal':bitsame,'nonwall_nonphase_shape_same':all(not x['only_old'] and not x['only_new'] for x in prefix),'mismatching_samples':[{'index':i,'detail':x} for i,x in enumerate(prefix) if x['diff_count'] or x['only_old'] or x['only_new']][:5],'exclusions':sorted(EXCLUDE_TOP),'scope':'200 controlrecords, NOT4000 physics-step bit comparisons','public_packet_fields':'logged rawgyro/rawproper/encoderq/qd/wheelmean/sensor time+age; missingpacketflags not invented'},'all600_torque_phase_target_schedule_differences':schedule_diffs,'first_shared_signal_difference':first_full_diff,'trace_sources':{'old':a['trace_artifact'],'new':b['trace_artifact']},'original_raw_SHA_not_recomputed':True})
        loaded[seed]=(old,new,a,b,aa,bb)
    old,new,a,b,aa,bb=loaded[4222];detail=[physics_detail(old,a,aa),physics_detail(new,b,bb)];bd=TASK/'MINIHOP_OBSERVER_V2/BOUNDARY_DIAGNOSTIC.json';contract=TASK/'MINIHOP_AUDIT_V2/GRADING_CONTRACT.json';source+=[{'path':str(p),'bytes':p.stat().st_size,'SHA':sha(p)} for p in (bd,contract,TASK/'MINIHOP_AUDIT_V2/run_minihop_case_v2.py',TASK/'MINIHOP_AUDIT_V2/contact_grade_v2.py')]
    result={'status':'R44_R45_PAIRED_TRAIN_OBSERVER_TIMER_DIAGNOSTIC_NOT_CONTACT_QUALIFICATION','pairs':pairs,'bad_seed4222_physics_only':detail,'boundary_diagnostic':load(bd),'source_small_SHA':source,'new_physics_Git_GPU_agents_realIO_or_parameterfit':False,'GT_private_raw_offline_only_never_onlineinput':True,'otherphysics_trajectories_read':False,'comparison_float_semantics':'struct.pack binary64 after original JSON numeric decode; bool/int/str/None exact types+values; not byte-identical serialized JSON claim','causal_limit':'Same-seed controlled timer observation path intervention, not detectedcontact oractive landingposture change; no independentseedstudy or parameterfit.','PH5pending':True}
    (out/'RESULT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    compact={'pairs':[{'seed':x['seed'],'old':x['old'],'new':x['new'],'gates_old':x['old_gates'],'gates_new':x['new_gates'],'pre2':x['exact_pre2p00_control_comparison'],'firstDiff':x['first_shared_signal_difference']} for x in pairs],'4222':[{'case':x['case'],'guide_count':x['after_trigger_guide_ticks_gt1N'],'firstguide':x['first_guide_over_gate_1N'],'guideruns':x['guide_runs'],'post_landing_support_runs':x['post_landing_world_support_runs'],'post_landing_airgaps':x['post_landing_le1N_gaps']} for x in detail]}
    print(json.dumps(compact,ensure_ascii=False,indent=2))
if __name__=='__main__':main(R/'analysis')
