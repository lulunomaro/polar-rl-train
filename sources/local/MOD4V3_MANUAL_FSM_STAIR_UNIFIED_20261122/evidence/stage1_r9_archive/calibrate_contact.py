"""Fit deterministic contact thresholds to frozen-E0 acceleration/impact traces."""
from argparse import ArgumentParser
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace
from itertools import product
import json
import numpy as np
from fsm_paths import HERE
from fsm_io import put
from manual_fsm_core import DetectorConfig
from fsm_evaluation import run_case

def cases(quick=False):
    result = []
    def add(course, speed, height=.39, yaw=0., offset=None, seconds=4.5):
        result.append(dict(id=f'cal_{len(result):03d}_{course}', course=course, speed=speed,
            height=height, yaw_deg=yaw, offset=offset or ([0.,0.] if course in ('flat','rough_L9') else [-1.8,0.]),
            seconds=seconds, settle_s=.8, wz=0., task='', edge_sign=1, armed=True))
    for course, speed in product(('flat', 'rough_L9'), (.8,1.2,1.6,2.,2.4,2.8,3.)):
        add(course, speed, offset=[-1.5,0.] if course == 'rough_L9' else [0.,0.], seconds=3.5)
    for course, speed in product(('curb_11', 'step_20'), (.6,.8,1.2,1.6,2.,2.6)):
        add(course, speed, seconds=9. if speed < 1. else 6.5)
    if not quick:
        for course, speed, yaw in product(('step_20',), (.6,1.2,2.),(-25.,25.)):
            add(course,speed,yaw=yaw)
        for h,speed in product((.28,.35,.42),(1.2,2.8,3.)):
            add('flat',speed,height=h,seconds=3.5)
    return result

def worker(case):
    row, trace = run_case(case, calibration=True)
    folder = HERE/'evidence/contact_calibration/raw'
    folder.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(folder/(case['id']+'.npz'), **trace)
    put(folder/(case['id']+'.json'), row)
    return row

def main():
    p = ArgumentParser(description=__doc__)
    p.add_argument('--workers',type=int,default=4)
    p.add_argument('--quick',action='store_true')
    p.add_argument('--fit-only',action='store_true')
    args=p.parse_args()
    jobs = cases(args.quick)
    if not args.fit_only:
        with ProcessPoolExecutor(args.workers) as pool:
            for row in pool.map(worker,jobs):
                print(row['id'], 'face',row['first_face_contact_s'],'fall',row['failure'],flush=True)
    datasets=[]
    folder=HERE/'evidence/contact_calibration/raw'
    for case in jobs:
        with np.load(folder/(case['id']+'.npz')) as f:
            control=f['control']
        with (folder/(case['id']+'.json')).open(encoding='utf-8') as f:
            row=json.load(f)
        datasets.append((case,row,control))
    # Features were measured at the start of each control tick. The wall label
    # is the contact in the preceding completed 20 ms interval.
    negative=[]
    positive=[]
    for case,row,x in datasets:
        time=x[:,0]-.02
        gap=x[:,48]
        face=row['first_face_contact_s']
        safe=(gap>.10) | (case['course'] in ('flat','rough_L9'))
        negative.append(x[safe,42:48])
        if face is not None:
            ids=np.flatnonzero((time>=face-.003)&(time<=face+.041))
            if len(ids): positive.append((case['id'],x[ids,42:48]))
    neg=np.concatenate(negative)
    configurations=[]
    for dp, rate, decel, leg in product((.025,.04,.06,.08,.10,.14),(.10,.18,.25,.32,.5),(.10,.2,.35,.5,.8),(.15,.3,.5,.8)):
        def hit(x):
            return ((x[:,0]>dp)&(x[:,1]>rate)) | ((x[:,2]>decel)&((x[:,1]>rate)|(x[:,3]>leg)))
        fp=int(hit(neg).sum())
        if fp: continue
        detected=sum(bool(hit(x).any()) for _,x in positive)
        configurations.append((detected,dp,rate,decel,leg))
    if not configurations:
        raise RuntimeError('No zero-false-positive deterministic threshold found')
    best=max(configurations,key=lambda x:(x[0],-x[1],-x[2],-x[3],-x[4]))
    config=DetectorConfig(pitch_impulse=best[1],pitch_rate_impulse=best[2],wheel_deceleration=best[3],leg_impulse=best[4])
    put(HERE/'DETECTOR.json',dict(config=config.to_dict(),calibration_cases=len(jobs),
        negative_control_frames=len(neg),false_positive_frames=0,impact_cases=len(positive),
        impact_cases_detected_within_40ms=best[0],calibration_only=True,
        no_claim_of_unseen_zero_false_positives=True,feature_columns=['delta_gravity_x','delta_half_pitch_rate',
        'wheel_speed_drop_m_s','delta_scaled_leg_rate','wheel_speed_m_s','abs_gravity_x']))
    put(HERE/'evidence/contact_calibration/SUMMARY.json',dict(cases=[r for _,r,_ in datasets],chosen=config.to_dict(),
        threshold_candidates_with_zero_fp=len(configurations),impact_detected=best[0],impact_cases=len(positive)))
    print('CONFIG',config.to_dict(),'detected',best[0],'/',len(positive),flush=True)

if __name__=='__main__':
    main()
