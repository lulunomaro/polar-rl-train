"""One permitted pass per five raw streams. Stdlib math only, no controller replay."""
from pathlib import Path
import json,math,struct,traceback,hashlib
from collections import Counter,deque
ROOT=Path(__file__).resolve().parents[1];OUT=Path(__file__).resolve().parent
LOCK=json.loads((OUT/'SOURCE_LOCK.json').read_bytes())
LEG=[0,1,3,4];W=[2,5];PEAK=[40.,40.,5.775909774436091]*2;Q0=LOCK['public_crouch_absolute_q4']
TOL=1e-9;HTOL=1e-12
OPENED=[];COUNTS={};COMPLETE={};CURRENT=None
COLS=['k','command_s','post_s','sensor_s','age_s','phase','pitch_est','pitchrate_est','goal_h','h','anchor','flight_target_q4','landing_ref_q4','request_leg4','request_wheel2','flight_unclip_leg4','samepacket_noh_clipped_leg4','goal_raw','h_rate_active','request_leg40_mask4','request_wheelpeak_mask2','landing_weight','observer_disabled','observer_until_s','true_pitch_before','true_pitch_after','true_vx_before','encoder_q4','encoder_qd4']
TOP=['command_time_s','forward_command_m_s','sensor_time_s','sensor_age_s','estimated14','estimated_roll','raw_gyro','raw_proper','encoder_q4','encoder_qd4','wheel_rate_mean2','requested_tau6']
PHASE=['phase','target_q4','target_qd4','since_operator_trigger_s','wheel_measurement_disabled_predicted','observer_quarantine_until_s','landing_transition_weight','landing_position_ref4','position_latched_push_time_s','position_relative_estimate_m']
def dump(name,v):
    with(OUT/name).open('x',encoding='utf-8',newline='\n')as f:json.dump(v,f,ensure_ascii=False,allow_nan=False,separators=(',',':'));f.write('\n')
def num(x):
    assert type(x)in(int,float)and math.isfinite(x),('nonfinite/nonnumeric',repr(x));return float(x)
def vec(x,n):assert isinstance(x,list)and len(x)==n;return[num(v)for v in x]
def clip(x,lo,hi):return min(hi,max(lo,x))
def pack(x):
    if x is None:return b'N'
    if type(x)is bool:return b'B'+bytes([x])
    if isinstance(x,str):return b'S'+x.encode('utf-8')+b'\0'
    if isinstance(x,list):return b'L'+struct.pack('<I',len(x))+b''.join(pack(v)for v in x)
    return b'F'+struct.pack('<d',num(x))
def reject(x):raise ValueError('Nonfinite JSON token '+x)
def rows(z):
    p=Path(z['path']);assert str(p)not in OPENED
    st=p.stat();assert(st.st_size,st.st_mtime_ns)==(z['bytes'],z['mtime_ns'])
    OPENED.append(str(p));COUNTS[str(p)]=0
    with p.open('r',encoding='utf-8')as f:
        for i,line in enumerate(f):
            assert i<z['maximum_rows'],('row cap',p,i)
            r=json.loads(line,parse_constant=reject);COUNTS[str(p)]=i+1;yield i,r
    assert COUNTS[str(p)]==z['maximum_rows'],('unexpected row count',p,COUNTS[str(p)])
    st=p.stat();assert(st.st_size,st.st_mtime_ns)==(z['bytes'],z['mtime_ns'])
def addphase(s,phase,tau):
    d=s.setdefault(phase,dict(rows=0,leg_at40=[0]*4,wheel_at_peak=[0]*2))
    d['rows']+=1
    for i,j in enumerate(LEG):d['leg_at40'][i]+=int(abs(abs(tau[j])-PEAK[j])<=TOL)
    for i,j in enumerate(W):d['wheel_at_peak'][i]+=int(abs(abs(tau[j])-PEAK[j])<=TOL)
def control(z):
    global CURRENT
    c=z['case'];new=c.startswith('r62_');data=[];prefix=[];phasecounts={}
    stat=dict(case=c,rows=0,new_air_ref=new,first_flight_s=None,first_capture_s=None,last_flight_s=None,observer_resume_s=None,
        flight_rows=0,flight_request_reconstruction_max_error_Nm=0.,flight_leg_reconstruction_max_error_Nm=0.,flight_request_validation_failures=0,
        flight_goal_h_target_validation_max_error_rad=0.,first_anchor_continuity_error_rad=None,
        raw_goal_clipped_low=0,raw_goal_clipped_high=0,h_rate_active_rows=0,h_at_low_rows=0,h_at_high_rows=0,
        effect_nonzero_per_axis=[0]*4,fully_masked_per_axis=[0]*4,partially_masked_per_axis=[0]*4,transmitted_per_axis=[0]*4,
        flight_unclip_over40_per_axis=[0]*4,phase_requests=phasecounts)
    CURRENT=stat;previous_h=0.;last_flight=None
    for k,r in rows(z):
        p=r['phase'];ph=p['phase'];t=num(r['command_time_s']);post=num(r['time_s']);ss=num(r['sensor_time_s']);age=num(r['sensor_age_s'])
        assert abs(t-k*.01)<1e-8 and abs(post-t-.01)<1e-7 and r['physical_sample_rows']==20*(k+1)
        assert abs((t-ss)-age)<1e-7 and -.0000001<=age<=.0500001
        x=vec(r['estimated14'],14);q=vec(r['encoder_q4'],4);dq=vec(r['encoder_qd4'],4);tau=vec(r['requested_tau6'],6)
        target=vec(p['target_q4'],4);ref=vec(p['landing_position_ref4'],4)
        assert all(abs(v)<=PEAK[j]+TOL for j,v in enumerate(tau))
        f=ph=='predicted_flight_retract';cap=ph=='timed_capture';un=None;noh=None;goalraw=None;rateactive=None
        h=num(p['air_pitch_ref_h_rad'])if new else None;goal=num(p['air_pitch_ref_goal_rad'])if new else None;anchor=p.get('air_pitch_ref_capture_anchor_rad')if new else None
        if anchor is not None:anchor=num(anchor)
        if f:
            if stat['first_flight_s']is None:stat['first_flight_s']=t
            stat['last_flight_s']=t;stat['flight_rows']+=1
            assert stat['flight_rows']<=80
            assert all(v==0 for v in vec(p['target_qd4'],4))
            un=[140.*(target[i]-q[i])-3.*dq[i]for i in range(4)]
            pred=[0.]*6
            for i,j in enumerate(LEG):pred[j]=clip(un[i],-40.,40.)
            common=25.*x[2]+4.*x[9];diff=clip(-1.2*x[8]-.4*x[1],-.5,.5)
            pred[2]=clip(common-diff,-PEAK[2],PEAK[2]);pred[5]=clip(common+diff,-PEAK[5],PEAK[5])
            err=max(abs(pred[j]-tau[j])for j in range(6));legerr=max(abs(pred[j]-tau[j])for j in LEG)
            stat['flight_request_reconstruction_max_error_Nm']=max(stat['flight_request_reconstruction_max_error_Nm'],err)
            stat['flight_leg_reconstruction_max_error_Nm']=max(stat['flight_leg_reconstruction_max_error_Nm'],legerr)
            stat['flight_request_validation_failures']+=int(err>TOL)
            nohraw=[140.*(Q0[i]-q[i])-3.*dq[i]for i in range(4)];noh=[clip(v,-40.,40.)for v in nohraw]
            for i in range(4):stat['flight_unclip_over40_per_axis'][i]+=int(abs(un[i])>40.+TOL)
            if new:
                goalraw=.25*x[2]+.04*x[9];g=clip(goalraw,-.1,.03);expect=clip(previous_h+clip(g-previous_h,-.01,.01),-.1,.03)
                he=max(abs(g-goal),abs(expect-h),max(abs(target[i]-(Q0[i]+h))for i in range(4)))
                stat['flight_goal_h_target_validation_max_error_rad']=max(stat['flight_goal_h_target_validation_max_error_rad'],he)
                stat['raw_goal_clipped_low']+=int(goalraw<-.1);stat['raw_goal_clipped_high']+=int(goalraw>.03)
                rateactive=abs(g-previous_h)>.01+HTOL;stat['h_rate_active_rows']+=int(rateactive)
                stat['h_at_low_rows']+=int(abs(h+.1)<=HTOL);stat['h_at_high_rows']+=int(abs(h-.03)<=HTOL)
                for i,j in enumerate(LEG):
                    effect=abs(un[i]-nohraw[i]);trans=abs(pred[j]-noh[i])
                    if effect>TOL:
                        stat['effect_nonzero_per_axis'][i]+=1
                        key='fully_masked_per_axis'if trans<=TOL else('partially_masked_per_axis'if trans<effect-TOL else'transmitted_per_axis')
                        stat[key][i]+=1
            else:stat['flight_goal_h_target_validation_max_error_rad']=max(stat['flight_goal_h_target_validation_max_error_rad'],max(abs(target[i]-Q0[i])for i in range(4)))
        if cap and stat['first_capture_s']is None:
            stat['first_capture_s']=t
            if new:
                assert last_flight is not None
                stat['first_anchor_continuity_error_rad']=max(abs(anchor-last_flight[9]),max(abs(ref[i]-last_flight[11][i])for i in range(4)))
        if stat['first_flight_s']is not None and not p['wheel_measurement_disabled_predicted']and stat['observer_resume_s']is None:stat['observer_resume_s']=t
        gb=r['grade_before'];ga=r['grade_after']
        assert abs(num(gb['root_pose_velocity_time_s'])-t)<1e-7 and abs(num(ga['root_pose_velocity_time_s'])-post)<1e-7
        d=[k,t,post,ss,age,ph,x[2],x[9],goal,h,anchor,target,ref,[tau[j]for j in LEG],[tau[j]for j in W],un,noh,goalraw,rateactive,
           [abs(abs(tau[j])-40.)<=TOL for j in LEG],[abs(abs(tau[j])-PEAK[j])<=TOL for j in W],num(p['landing_transition_weight']),bool(p['wheel_measurement_disabled_predicted']),num(p['observer_quarantine_until_s']),num(gb['pitch_true']),num(ga['pitch_true']),num(gb['body_velocity'][0]),q,dq]
        if f:last_flight=d
        if stat['first_flight_s']is None:
            pref={n:pack(r[n])for n in TOP};pref.update({'phase.'+n:pack(p[n])for n in PHASE});prefix.append((t,pref))
        addphase(phasecounts,ph,tau);data.append(d);previous_h=h if new else 0.;stat['rows']+=1
    assert stat['first_flight_s']is not None and stat['first_capture_s']is not None
    stat['flight_reconstruction_usable']=stat['flight_request_validation_failures']==0 and stat['flight_goal_h_target_validation_max_error_rad']<=HTOL
    if not stat['flight_reconstruction_usable']:stat['masking_interpretation']='UNKNOWN_RECONSTRUCTION_VALIDATION_FAILED'
    else:stat['masking_interpretation']='VALIDATED_SAME_PACKET_REQUEST_ALGEBRA_ONLY'if new else'BASELINE_NO_H_FUNCTION'
    captime=stat['first_capture_s'];keep=[d for d in data if d[5]=='predicted_flight_retract']
    selected={d[0]for d in keep}
    for off in [0.,.01,.05,.10,.20,.50,1.]:
        nearest=min(data,key=lambda d:abs(d[1]-(captime+off)))
        if abs(nearest[1]-captime-off)<1e-7:selected.add(nearest[0])
    selected.add(len(data)-1)
    keep=[d for d in data if d[0]in selected]
    stat['capture_windows']={}
    for name,start,end in [('first_0p2',0.,.2),('next_0p3',.2,.5),('last_1s',data[-1][1]-captime-.99,data[-1][1]-captime+.001)]:
        ds=[d for d in data if captime+start-1e-8<=d[1]<captime+end-1e-8]
        stat['capture_windows'][name]=dict(rows=len(ds),request_wheel_mean2=[math.fsum(d[14][j]for d in ds)/len(ds)for j in range(2)]if ds else None,
            request_wheel_min2=[min(d[14][j]for d in ds)for j in range(2)]if ds else None,request_wheel_max2=[max(d[14][j]for d in ds)for j in range(2)]if ds else None,
            mean_estimated_pitch=math.fsum(d[6]for d in ds)/len(ds)if ds else None,mean_true_vx_before=math.fsum(d[26]for d in ds)/len(ds)if ds else None)
    stat['first_flight']=next(d for d in data if d[5]=='predicted_flight_retract');stat['last_flight']=last_flight;stat['first_capture']=next(d for d in data if d[5]=='timed_capture')
    COMPLETE[c]=stat
    return dict(summary=stat,retained_rows=keep),data,prefix

def compare_prefix(a,b):
    cutoff=min(a[0]['summary']['first_flight_s'],b[0]['summary']['first_flight_s']);aa={t:p for t,p in a[2]if t<cutoff-1e-8};bb={t:p for t,p in b[2]if t<cutoff-1e-8}
    assert set(aa)==set(bb)
    mismatch=Counter();first=[];count=0
    for t in sorted(aa):
        assert aa[t].keys()==bb[t].keys()
        for n in aa[t]:
            count+=1
            if aa[t][n]!=bb[t][n]:
                mismatch[n]+=1
                if len(first)<8:first.append(dict(command_s=t,field=n,old_hex=aa[t][n].hex(),new_hex=bb[t][n].hex()))
    return dict(snapshot_only_not_2k=True,before_command_s=cutoff,rows=len(aa),field_values_compared=count,mismatch_counts=dict(mismatch),first_mismatches=first)

def surface(c,bar):
    n=vec(c['normal_geom1_to_geom2_world'],3);n=[v*(1. if c['robot_is_geom2']else -1.)for v in n];p=vec(c['position_world_m'],3)
    label='UNKNOWN_OR_EDGE';dist=None
    if c['environment_geom']=='ground':label='GROUND_NAME_NORMAL_RECORDED'
    elif c['environment_geom']==bar['name']:
        dist=dict(front=abs(p[0]-bar['front_x_m']),back=abs(p[0]-bar['back_x_m']),top=abs(p[2]-bar['top_z_m']))
        candidates=[]
        for name,v in [('front',-n[0]),('back',n[0]),('top',n[2])]:
            if v>=.95 and dist[name]<=.005:candidates.append(name)
        if len(candidates)==1:label='FIRST_BAR_'+candidates[0].upper()
    return dict(label=label,outward_environment_to_robot_normal3=n,absolute_plane_distances_m=dist)

def physics(z,control_data,result):
    global CURRENT
    first=None;window={};ring=deque(maxlen=21);hard=[];guide=0;first_air=None;land=None;first_resume=None
    CURRENT=dict(case=z['case'],kind='physics',processed=0)
    for i,r in rows(z):
        assert r['sample_index']==i
        t=num(r['stage_time_s']);post=num(r['root_post_time_s']);dp=r['drivepoint'];assert dp['physics_tick']==i
        assert abs(t-i*.0005)<1e-7 and abs(post-t-.0005)<1e-7 and abs(num(dp['time_s'])-t)<1e-8
        ctrl=control_data[i//20];assert ctrl[1]-1e-7<=t<ctrl[1]+.01+1e-7
        rot=r['private_contact_diagnostic']['root_rotation_world_from_body33_pre'];assert len(rot)==3
        rot=[vec(v,3)for v in rot];pitch=math.atan2(-rot[2][0],math.hypot(rot[0][0],rot[1][0]));roll=math.atan2(rot[2][1],rot[2][2])
        actual=vec(dp['actual_tau6_Nm'],6);vel=vec(dp['velocity6_rad_s'],6)
        hn=num(r['hard_normal_N']);gn=num(r['guide_normal_N']);guide+=int(gn>1.)
        if first_air is None and r['air_qualified']:first_air=dict(confirmation_post_s=post,interval_start_s=t-num(r['air_run_s'])+.0005)
        if first_air is not None and land is None and num(r['all_world_normal_N'])>1.:land=dict(stage_s=t,post_s=post)
        row=dict(sample_index=i,stage_s=t,root_post_s=post,root_xyz_pre_m=vec(dp['root_xyz_pre_m'],3),root_pitch_pre=pitch,root_roll_pre=roll,
            hard_normal_N=hn,guide_normal_N=gn,all_normal_N=num(r['all_world_normal_N']),actual_bounded_tau6_Nm=actual,actual_velocity6_rad_s=vel,
            control_k=ctrl[0],command_s=ctrl[1],stage_age_from_request_s=t-ctrl[1],control_phase=ctrl[5],estimated_pitch_at_command=ctrl[6],estimated_pitchrate_source=ctrl[7],h_at_command=ctrl[9],anchor=ctrl[10],landing_weight=ctrl[21],observer_disabled=ctrl[22],observer_until_s=ctrl[23],requested_leg4_at_command=ctrl[13],requested_wheel2_at_command=ctrl[14],actual_q4_pre=None)
        ring.append(row)
        if hn>1.:
            assert len(hard)<32
            contacts=[c for c in r['contacts']if c['kind']=='hard_other'and num(c['normal_N'])>0.]
            assert contacts
            for c in contacts:c['surface_diagnostic']=surface(c,result['first_transverse_bar'])
            hard.append(dict(**row,positive_hard_contacts=contacts))
            if first is None:
                first=i
                for q in ring:
                    if q['sample_index']-i in [-20,-10,-1,0]:window[q['sample_index']]=q
        if first is not None and i-first in [1,10,20]:window[i]=row
        CURRENT['processed']=i+1
    assert len(hard)==result['hard_contact_physics_ticks']and guide==result['guide_contact_physics_ticks']
    return dict(rows=16000,first_qualified_air=first_air,first_landing_after_qualified_air=land,hard_ticks=len(hard),guide_ticks=guide,hard_events=hard,first_hard_window=[window[i]for i in sorted(window)],actual_q2k='UNKNOWN_NOT_LOGGED_NO_DQ_INTEGRATION',actual_bounded_torque_meaning='same_PRE_stage_model_d_ctrl_command_not_independent_measured_output',driver_internal_clipping_counts=None)

def main():
    dump('RAW_PASS_STARTED.json',dict(status='STARTED_DO_NOT_RERUN_RAW',method_SHA=LOCK['method']['SHA']))
    for z in LOCK['sources']:assert hashlib.sha256(Path(z['path']).read_bytes()).hexdigest()==z['SHA']
    work={};cases={}
    for z in LOCK['raw']:
        if z['file']=='trace.jsonl':
            triple=control(z);work[z['case']]=triple;cases[z['case']]=triple[0]
    pairs={str(s):compare_prefix(work[f'r60_tall0_fresh_RM_DR_{s}'],work[f'r62_airref002_paired_RM_DR_{s}'])for s in[4606,4610]}
    pz=next(z for z in LOCK['raw']if z['file']=='physics.jsonl');result=json.loads((ROOT/'results'/pz['case']/'result.json').read_bytes())
    phy=physics(pz,work[pz['case']][1],result)
    output=dict(kind='SINGLE_PASS_R62_RESPONSE_EXTRACTION_NOT_REPLAY_OR_DYNAMIC_QUALIFICATION',control_columns=COLS,cases=cases,paired_prefix= pairs,new4606_physics=phy,raw_opened=OPENED,row_counts=COUNTS,total_rows=sum(COUNTS.values()),raw_hashes_recomputed=0,project_imports=0,new_physics_or_QA=0)
    dump('EXTRACTED.json',output)
    print(json.dumps(dict(status='EXTRACTED',rows=output['total_rows'],streams=len(OPENED),cases={c:{k:d['summary'][k]for k in['first_flight_s','first_capture_s','flight_rows','flight_request_reconstruction_max_error_Nm','flight_request_validation_failures','flight_goal_h_target_validation_max_error_rad','fully_masked_per_axis','partially_masked_per_axis','transmitted_per_axis','raw_goal_clipped_low','raw_goal_clipped_high','h_rate_active_rows']}for c,d in cases.items()},prefix=pairs,hard=[{k:r[k]for k in['stage_s','root_pitch_pre','control_phase','h_at_command','landing_weight','observer_disabled']}for r in phy['hard_events']]),indent=2))
if __name__=='__main__':
    try:main()
    except BaseException:
        dump('PARTIAL_ERROR.json',dict(error=traceback.format_exc(),raw_opened=OPENED,row_counts=COUNTS,complete_case_summaries=COMPLETE,current_prefix=CURRENT,no_rescan_allowed=True));raise
