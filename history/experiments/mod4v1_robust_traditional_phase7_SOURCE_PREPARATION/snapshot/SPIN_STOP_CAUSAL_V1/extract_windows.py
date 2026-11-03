"""One-pass, four-file, bounded descriptive extraction. No project imports/replay/physics."""
from pathlib import Path
from collections import deque
import hashlib,json,math
D=Path(__file__).resolve().parent; R=D.parent
load=lambda p:json.loads(p.read_text(encoding='utf-8'))
method=load(D/'METHOD.json'); lock=load(D/'SOURCE_LOCK.json')
assert hashlib.sha256((D/'METHOD.json').read_bytes()).hexdigest()==lock['method']['sha256']
assert [c['trace'] for c in lock['cases']]==method['trace_allowlist']
EPS=1e-7; PEAK=5.775909774436091

def num(x):
    if isinstance(x,bool) or not isinstance(x,(int,float)) or not math.isfinite(x): raise ValueError(('nonfinite/non-numeric',x))
    return float(x)
def vec(x,n):
    if not isinstance(x,list) or len(x)!=n: raise ValueError(('shape',n))
    return [num(a) for a in x]
def truth(g):
    gyro=vec(g['gyro_true'],3); p=num(g['pitch_true']); r=num(g['roll_true'])
    return [num(g['body_velocity'][0]),p,(gyro[1]*math.sin(r)+gyro[2]*math.cos(r))/max(math.cos(p),.15)]
def avg(v): return math.fsum(v)/len(v) if v else None
def rms(v): return math.sqrt(math.fsum(x*x for x in v)/len(v)) if v else None
def summary(v): return [avg(v),rms(v),min(v),max(v)] if v else None

def stats(rows):
    if not rows: return dict(n=0,unknown=True)
    out=dict(n=len(rows))
    for field in ('true','estimated','residual_now','residual_source'):
        out[field]=[summary([r[field][j] for r in rows if r[field] is not None and r[field][j] is not None]) for j in range(3)]
    for field in ('request_wheels','last_ctrl_wheels','feedback_wheel_rates'):
        out[field]=[summary([r[field][j] for r in rows]) for j in range(2)]
    out['request_minus_last_ctrl_RMS']=[rms([r['request_wheels'][j]-r['last_ctrl_wheels'][j] for r in rows]) for j in range(2)]
    out['request_absolute_peak_coincidences']=[sum(abs(abs(r['request_wheels'][j])-PEAK)<=1e-8 for r in rows) for j in range(2)]
    out['last_ctrl_absolute_peak_coincidences']=[sum(abs(abs(r['last_ctrl_wheels'][j])-PEAK)<=1e-8 for r in rows) for j in range(2)]
    out['centering_active_samples']=sum(r['center_active'] for r in rows)
    out['centering_torque']=summary([r['center_tau'] for r in rows])
    out['gain_1p5_samples']=sum(r['gain']==1.5 for r in rows) if rows[0]['gain'] is not None else None
    out['source_pairs']=sum(r['residual_source'] is not None for r in rows)
    out['sensor_age_s']=summary([r['age'] for r in rows])
    return out

def inrange(t,a,b): return t>=a-EPS and t<b-EPS

def extract(c):
    path=R/c['trace']; before=path.stat(); assert before.st_size==c['raw_bytes'] and before.st_mtime_ns==c['raw_mtime_ns']
    keep=[]; hist=deque(maxlen=16); stops=[]; transitions={'gain':[],'mix_stage':[]}; counts={'gain':0,'mix_stage':0}; prev={}
    prev_req=0.; last_t=None; last_post=None; schema=None; n=0; gaps=[]; cache_gaps=[]; source_misses=0; integral_fields=set()
    with path.open('r',encoding='utf-8') as f:
        for n,line in enumerate(f,1):
            if n>method['max_rows_per_trace']: raise ValueError(('row cap',c['case']))
            raw=json.loads(line,parse_constant=lambda x:(_ for _ in ()).throw(ValueError(x)))
            if schema is None: schema=sorted(raw)
            t=num(raw['estimate_time']); post=num(raw['time']); ts=num(raw['sensor_timestamp_s']); age=num(raw['sensor_age_s'])
            gt=raw['ground_truth_before']; ga=raw['ground_truth']; cur=truth(gt); after=truth(ga)
            assert abs(num(gt['root_pose_velocity_time_s'])-t)<EPS and abs(num(ga['root_pose_velocity_time_s'])-post)<EPS
            assert abs(num(gt['time'])-t)<EPS and abs(num(ga['time'])-post)<EPS
            assert abs(post-t-.01)<EPS and abs(age-(t-ts))<EPS and age>=0
            if last_t is not None: assert abs(t-last_t-.01)<EPS
            gaps.append(post-t); cache_gaps.append(t-num(gt['collision_site_cache_time_s'])); last_t=t; last_post=post
            hist.append((t,cur)); pair=min(hist,key=lambda x:abs(x[0]-ts)); aligned=pair[1] if abs(pair[0]-ts)<EPS else None
            if aligned is None: source_misses+=1
            x=vec(raw['estimated14'],14); est=[x[7],x[2],x[8]]; req=vec(raw['request'],2); shaped=vec(raw['shaped'],2)
            tau=vec(raw['raw_requested_tau'],6); ctrl=vec(raw['actual_tau'],6); rate=vec(raw['wheel_rate2'],2); center=raw['spin_center']
            assert isinstance(center['active'],bool)
            gain=num(raw['accel_correction_gain_used']) if 'accel_correction_gain_used' in raw else None
            mix=num(center['stop_capture_mix']) if 'stop_capture_mix' in center else None
            cref=num(center['stop_capture_reference']) if 'stop_capture_reference' in center else None
            integral_fields.update(k for k in list(raw)+list(center) if 'integral' in k.lower())
            signals={'gain':gain,'mix_stage':None if mix is None else (0 if mix<=0 else 2 if mix>=1 else 1)}
            for key,value in signals.items():
                if value is not None and (key not in prev or value!=prev[key]):
                    counts[key]+=1
                    if len(transitions[key])<method['all_scan_transition_cap_per_kind']: transitions[key].append([t,value])
                prev[key]=value
            if abs(req[1])<1e-12 and abs(prev_req)>1:
                expected=10. if prev_req>0 else 22.; assert abs(t-expected)<.03
                stops.append(dict(t0=t,sign=1 if prev_req>0 else -1,next_nonzero=None))
            if abs(req[1])>1 and stops and stops[-1]['next_nonzero'] is None: stops[-1]['next_nonzero']=t
            prev_req=req[1]
            if any(a-EPS<=t<b+EPS for a,b in method['retained_control_time_ranges_s']):
                keep.append(dict(t=t,post=post,source_t=ts,age=age,true=cur,true_after=after,estimated=est,
                    residual_now=[a-b for a,b in zip(est,cur)],
                    residual_source=None if aligned is None else [est[0]-aligned[0],None,est[2]-aligned[2]],
                    request_wheels=[tau[2],tau[5]],last_ctrl_wheels=[ctrl[2],ctrl[5]],feedback_wheel_rates=rate,
                    center_active=center['active'],center_tau=num(center['centering_torque_Nm']),
                    mix=mix,capture_ref=cref,estimated_distance=x[0],gain=gain,shaped_w=shaped[1],request_w=req[1],
                    xy_before=vec(gt['xyz'],3)[:2],xy_after=vec(ga['xyz'],3)[:2],estimated_xy=vec(center['estimated_root_xy'],2)))
    assert n==c['rows_expected'] and len(stops)==2
    after_stat=path.stat(); assert (after_stat.st_size,after_stat.st_mtime_ns)==(before.st_size,before.st_mtime_ns)
    out=dict(case=c['case'],seed=c['seed'],variant=c['variant'],scanned_rows=n,retained_rows=len(keep),
        schema=schema,integral_fields=sorted(integral_fields),source_pair_misses=source_misses,
        before_to_after_s=summary(gaps),root_to_collision_cache_s=summary(cache_gaps),
        transitions=transitions,transition_counts=counts,
        original_transition_proposed_pass=c['original_transition_proposed_pass'],
        original_wholecase_xy_displacement_m=c['original_wholecase_xy_displacement_m'],stops=[])
    for event in stops:
        t0=event['t0']; end=event['next_nonzero'] if event['next_nonzero'] is not None else last_post
        sr=[r for r in keep if inrange(r['t'],t0,end) and abs(r['request_w'])<1e-12]
        assert sr and abs(sr[0]['t']-t0)<EPS
        ranges={'pre':(t0-.5,t0),'early':(t0,t0+.5),'mid':(t0+.5,t0+1.5),'tail':(end-1.,end),'whole_stop':(t0,end)}
        segments={name:stats([r for r in keep if inrange(r['t'],a,b)]) for name,(a,b) in ranges.items()}
        snaps=[]
        for at in method['snapshots_s']:
            row=sr[-1] if at=='last_control_sample' else min(sr,key=lambda r:abs(r['t']-(t0+at)))
            snaps.append({k:row[k] for k in ('true','estimated','residual_now','residual_source','request_wheels','last_ctrl_wheels','shaped_w','gain','mix','capture_ref','estimated_distance')})
            snaps[-1]['dt_s']=row['t']-t0
        first=sr[0]; last=sr[-1]
        xy_delta=[last['xy_after'][j]-first['xy_before'][j] for j in range(2)]
        est_delta=[last['estimated_xy'][j]-first['estimated_xy'][j] for j in range(2)]
        first_at=lambda pred:next((r['t']-t0 for r in sr if pred(r)),None)
        phase='first_stop' if event['sign']>0 else 'final_stop'
        original=next(p for p in c['original_phase_metrics'] if p['name']==phase)
        out['stops'].append(dict(phase=phase,prior_spin_sign=event['sign'],t0_control_s=t0,end_s=end,duration_s=end-t0,
            segments=segments,snapshots=snaps,xy_true_delta_m=xy_delta,xy_true_displacement_m=math.hypot(*xy_delta),
            xy_estimated_odom_delta_m=est_delta,
            first_shaped_abs_lt_2_s=first_at(lambda r:abs(r['shaped_w'])<2.),first_shaped_zero_s=first_at(lambda r:abs(r['shaped_w'])<1e-12),
            first_gain_1p5_s=first_at(lambda r:r['gain']==1.5),first_mix_positive_s=first_at(lambda r:r['mix'] is not None and r['mix']>0),
            first_mix_full_s=first_at(lambda r:r['mix'] is not None and r['mix']>=1),
            original_phase_metrics=original,
            tail_post_criterion_break_counts=dict(v=sum(abs(r['true_after'][0])>=.15 for r in sr if r['t']>=end-1-EPS),
                yaw=sum(abs(r['true_after'][2])>=.3 for r in sr if r['t']>=end-1-EPS),
                pitch=sum(abs(r['true_after'][1])>=math.radians(10) for r in sr if r['t']>=end-1-EPS))))
    return out

# Source-aligned pitch remains null: it is already an age-view; no placeholder numeric observations.
cases=[extract(c) for c in lock['cases']]
# Representation-only revision: deduplicate repeated dictionary keys, retain every value.
stat_fields=list(cases[0]['stops'][0]['segments']['pre'])
snapshot_fields=list(cases[0]['stops'][0]['snapshots'][0])
packed_cases=[]
for case in cases:
    packed=dict(case); packed['stops']=[]
    for stop in case['stops']:
        item=dict(stop); item['segments']={}; item['snapshots']=[]
        for name,value in stop['segments'].items():
            assert list(value)==stat_fields
            encoded=[value[k] for k in stat_fields]
            assert dict(zip(stat_fields,encoded))==value
            item['segments'][name]=encoded
        for value in stop['snapshots']:
            assert list(value)==snapshot_fields
            encoded=[value[k] for k in snapshot_fields]
            assert dict(zip(snapshot_fields,encoded))==value
            item['snapshots'].append(encoded)
        packed['stops'].append(item)
    packed_cases.append(packed)
result=dict(kind='FOUR_TRAIN_DESCRIPTIVE_WINDOWS_NOT_NEW_SCORE_OR_CAUSAL_IDENTIFICATION',
    extractor_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),method_sha256=lock['method']['sha256'],
    source_lock_sha256=hashlib.sha256((D/'SOURCE_LOCK.json').read_bytes()).hexdigest(),
    numeric_vector_order=['vx_m_s','pitch_rad','Euler_heading_rate_rad_s'],stat_vector_order=['mean','RMS','min','max'],
    source_pitch_slot=None,source_pitch_reason='pitch already age-view; compare with current before truth, not old source truth',
    raw_hashes_computed=0,trace_paths_opened=method['trace_allowlist'],cases=packed_cases,
    encoding='segments and snapshots are lossless ordered arrays using these global field schemas',
    segment_stat_fields=stat_fields,snapshot_fields=snapshot_fields,
    unknown=['actual yaw I and antiwindup decisions','spin ref0 in baseline','2k preclip/target/clip masks and instantaneous motor speed',
             'independent measured wheel torque/current','instantaneous electrical power','unique contribution of accel vs capture vs history'])
raw=(json.dumps(result,separators=(',',':'),allow_nan=False)+'\n').encode('utf-8')
assert len(raw)<=method['output_limits']['window_summary_bytes'], ('summary cap',len(raw))
with (D/'WINDOWS.json').open('xb') as f:f.write(raw)
print('WINDOWS bytes',len(raw),'SHA',hashlib.sha256(raw).hexdigest(),'rows',sum(c['scanned_rows'] for c in cases))
for c in cases:
    print(c['case'],'startup transitions',c['transitions'])
    for s in c['stops']:
        tail=s['segments']['tail']; at=s['segments']['whole_stop']
        print(json.dumps(dict(case=c['case'],phase=s['phase'],n=at['n'],tail_n=tail['n'],xy=s['xy_true_displacement_m'],
            tail_true=[x[0] for x in tail['true']],tail_est=[x[0] for x in tail['estimated']],
            tail_source_residual=[x[0] if x is not None else None for x in tail['residual_source']],
            tail_pitch_residual=tail['residual_now'][1][0],shaped_zero=s['first_shaped_zero_s'],gain=s['first_gain_1p5_s'],
            mix=s['first_mix_positive_s'],full=s['first_mix_full_s'],requested_peak=at['request_absolute_peak_coincidences'],
            actual_peak=at['last_ctrl_absolute_peak_coincidences'],gap=at['request_minus_last_ctrl_RMS'],
            tail_breaks=s['tail_post_criterion_break_counts']),separators=(',',':')))
