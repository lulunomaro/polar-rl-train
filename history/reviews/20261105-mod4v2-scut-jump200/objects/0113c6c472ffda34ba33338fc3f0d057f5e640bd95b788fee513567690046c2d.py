"""Analyze saved first episodes; no policy load, optimizer, or physics."""
from pathlib import Path
import json
import argparse
import numpy as np

ROOT=Path(__file__).resolve().parent
parser=argparse.ArgumentParser()
parser.add_argument('directories',nargs='+')
args=parser.parse_args()

def longest(mask):
    best=cur=0
    for value in mask:
        cur=cur+1 if value else 0
        best=max(best,cur)
    return best

def first(mask,dt):
    ids=np.flatnonzero(mask)
    return float((ids[0]+1)*dt) if len(ids) else None

all_results={}
for name in args.directories:
    p=ROOT/name
    meta=json.loads((p/'CASES.json').read_text(encoding='utf-8'))
    rows=json.loads((p/'FLAT_ROWS.json').read_text(encoding='utf-8'))
    d=np.load(p/'PHYSICAL.npz')
    dt=meta['physics_dt']
    decimation=int(round(.02/dt))
    wheel=[meta['body_names'].index(s+'_wheel_link')for s in ('left','right')]
    cw=[meta['contact_names'].index(s+'_wheel_link')for s in ('left','right')]
    co=[i for i,n in enumerate(meta['contact_names'])if not n.endswith('_wheel_link')]
    requests=json.loads((p/'REQUESTS.json').read_text())if(p/'REQUESTS.json').exists()else[]
    results=[]
    for e,case in enumerate(meta['cases']):
        # The simulator may reset during a terminal control step. Exclude its
        # entire physical block and every later episode from first-episode data.
        done=[i for i,r in enumerate(rows)if r['terminated'][e]or r['timeout'][e]]
        end=done[0]*decimation if done else len(d['root'])
        valid=np.arange(len(d['root']))<end
        origin=np.asarray(meta['origins'][e])
        root=d['root'][:,e].astype(float).copy();root[:,:3]-=origin
        wp=d['body_pos'][:,e,wheel].astype(float)-origin
        force=d['force'][:,e,cw].astype(float)
        norm=np.linalg.norm(force,axis=-1)
        other=np.linalg.norm(d['force'][:,e,co],axis=-1).max(-1)
        h=case['step_height'];edge=case['edge'];r=.06
        bottom=wp[:,:,2]-r
        supported=(force[:,:,2]>1).all(-1)&(np.abs(bottom)<.015).all(-1)
        air=(norm<1).all(-1)&(other<1)
        crossed=(wp[:,:,0]-r>edge).all(-1)
        above=(bottom>h+.002).all(-1)
        above_and_crossed=above&crossed
        top=(case['kind']!='flat')&crossed&(np.abs(bottom-h)<.015).all(-1)&(force[:,:,2]>1).all(-1)&(other<1)
        w,x,y,z=root[:,3:7].T
        roll=np.arctan2(2*(w*x+y*z),1-2*(x*x+y*y))
        pitch=np.arcsin(np.clip(2*(w*y-z*x),-1,1))
        yaw=np.arctan2(2*(w*z+x*y),1-2*(y*y+z*z))
        quiet=top&(np.linalg.norm(root[:,7:9],axis=-1)<=.03)&(abs(root[:,9])<=.03)&(abs(roll)<=np.deg2rad(10))&(abs(pitch)<=np.deg2rad(10))&(abs(yaw)<=.2)
        near_side=(wp[:,:,0]+r>=edge-.015)&(wp[:,:,0]-r<=edge+.015)&(bottom<h-.01)
        side_contact=(near_side&(np.linalg.norm(force[:,:,:2],axis=-1)>20)).any(-1)
        flights=[];start=None;last_support=None
        for t in range(end):
            if supported[t]:last_support=t
            if air[t]and start is None:start=t
            if start is not None and((not air[t])or t==end-1):
                stop=t if not air[t]else t+1
                sequence=slice(start,stop)
                supported_before=last_support is not None and start-last_support<=int(.2/dt)
                up=bool((root[sequence,9]>.05).any())
                clear=bool(above_and_crossed[sequence].any())
                before_side=bool(side_contact[:start].any())
                if supported_before and up:
                    flights.append(dict(start_seconds=(start+1)*dt,end_seconds=stop*dt,
                        duration_seconds=(stop-start)*dt,ground_support_recent=True,
                        takeoff_wheel_front_max_x=float((wp[start,:,0]+r).max()),
                        before_step_face=(wp[start,:,0]+r<edge-.005).all().item(),
                        prior_step_side_contact=before_side,
                        full_wheel_clear_in_same_no_contact_interval=clear,
                        wheel_bottom_pair_peak=float(bottom[sequence].min(-1).max())))
                start=None
        pure=[f for f in flights if f['before_step_face']and not f['prior_step_side_contact']and f['full_wheel_clear_in_same_no_contact_interval']]
        ctl={}
        for field in ('jump_takeoff_phase','wheel_forward_stair_state','wheel_forward_wall_reset','jump_takeoff_assist_event'):
            ctl[field+'_any_firstepisode']=bool(d[field][:end,e].any())
            ctl[field+'_max_firstepisode']=float(d[field][:end,e].max())if end else None
            ctl[field+'_any_in_terminal_control_block']=bool(d[field][end:end+decimation,e].any())if done else False
        ctl['effective_height_range']=[float(d['effective_height'][:end,e].min()),float(d['effective_height'][:end,e].max())]
        ctl['jump_ctrl_mode_any']=bool((d['ctrl_mode'][:end,e,4]>0).any())
        ctl['stair_ctrl_mode_any']=bool((d['ctrl_mode'][:end,e,1]>0).any())
        ctl['control_events_available']='controller'in rows[0]
        if ctl['control_events_available']:
            last=done[0]if done else len(rows)
            for field in ('jump_takeoff_trigger_event','wheel_forward_stair_detect_event','wheel_forward_step_detect_event','wheel_forward_wall_reset','wheel_forward_stair_success_exit_event','wheel_forward_stair_failure_exit_event'):
                ctl[field+'_control_count_firstepisode']=sum(bool(row['controller'][field][e])for row in rows[:last+1])
        elif ctl['jump_takeoff_phase_any_firstepisode']:
            ctl['trigger_evidence']='Phase and jump observation seen; pre-physics pulse is absent from physical snapshots, do not infer zero triggers.'
        result=dict(case=e,**case,first_episode_valid_seconds=end*dt,
            terminal_control_excluded=bool(done),recorded_root_body_force_finite=bool(np.isfinite(root[:end]).all()and np.isfinite(wp[:end]).all()and np.isfinite(force[:end]).all()),
            requested=any(e in r['ids']for r in requests),controller=ctl,
            full_wheels_crossed=bool((crossed&valid).any()),full_wheels_above_and_crossed=bool((above_and_crossed&valid).any()),
            first_full_wheel_cross_seconds=first(crossed&valid,dt),
            first_bilateral_top_support_seconds=first(top&valid,dt),
            bilateral_top_support_seconds_max=longest(top&valid)*dt,
            strict_quiet_top_seconds_max=longest(quiet&valid)*dt,
            strict_quiet_top_pass=longest(quiet&valid)*dt>=.5,
            side_contact_before_crossing=bool((side_contact&valid&(~crossed)).any()),
            first_step_side_contact_seconds=first(side_contact&valid,dt),
            pre_side_ground_takeoff_wholeclear_sequences=pure,
            ground_recent_upward_no_contact_sequences=flights,
            ground_recent_upward_no_contact_count=len(flights),
            root_x_max=float(root[:end,0].max()),root_z_max=float(root[:end,2].max()),
            wheel_bottom_pair_peak=float(bottom[:end].min(-1).max()))
        results.append(result)
    report=dict(directory=str(p),method='Saved 200 Hz physics; terminal control block and all later episodes excluded; 60 mm radius; bilateral top Fz>1 N and no nonwheel force>1 N; strict rest .5s.',
        original_quick_RESULT_preserved='RESULT.json, if present; its nonflat top was hardcoded .2m and must not be used for13cm scores',
        assistance_scope='Jump force/velocity assist disabled; original domain-randomization interval push/force events retained.',results=results)
    (p/'CONTROLLER_RESULT.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    summary={}
    for kind in sorted({c['kind']for c in meta['cases']}):
        rr=[v for v in results if v['kind']==kind]
        summary[kind]=dict(cases=len(rr),requested=sum(v['requested']for v in rr),jump_phase=sum(v['controller']['jump_takeoff_phase_any_firstepisode']for v in rr),stair_state=sum(v['controller']['wheel_forward_stair_state_any_firstepisode']for v in rr),
            wall_reset=sum(v['controller']['wheel_forward_wall_reset_any_firstepisode']for v in rr),
            wall_reset_in_terminal_block=sum(v['controller']['wheel_forward_wall_reset_any_in_terminal_control_block']for v in rr),
            whole_cross=sum(v['full_wheels_crossed']for v in rr),above_and_cross=sum(v['full_wheels_above_and_crossed']for v in rr),
            bilateral_top_support=sum(v['bilateral_top_support_seconds_max']>0 for v in rr),
            top_support_max=max(v['bilateral_top_support_seconds_max']for v in rr),
            strict_quiet=sum(v['strict_quiet_top_pass']for v in rr),
            pre_side_ground_takeoff_clear=sum(bool(v['pre_side_ground_takeoff_wholeclear_sequences'])for v in rr),
            jump_assist_events=sum(v['controller']['jump_takeoff_assist_event_any_firstepisode']for v in rr))
    all_results[name]=summary
(ROOT/'CONTROLLER_SUMMARY.json').write_text(json.dumps(all_results,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(all_results,ensure_ascii=False,indent=2))
