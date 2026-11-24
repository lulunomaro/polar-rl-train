"""Measure the SELECTED_E0 command curve with the shared 400 Hz motor loop."""
from concurrent.futures import ProcessPoolExecutor
from argparse import ArgumentParser
import json
import numpy as np
import torch
from fsm_paths import HERE,E0_SHA,E0_BASE_SHA
from fsm_io import put,sha256
from fsm_maps import metadata
from manual_fsm_runtime import ManualPolicy,ManualSimulation
from fsm_evaluation import reset_case

SPEEDS=(0.,.6,.8,1.,1.2,1.6,2.,2.2,2.4,2.8,3.)
HEIGHTS=(.20,.24,.28,.32,.35,.38,.39,.42)

def fit_height(height):
    identity=sha256(HERE/'manual_fsm_model.py')+sha256(__file__)
    cache=HERE/'evidence/stage2_calibration_rows'/f'height_{height:.3f}.json'
    if cache.is_file():
        row=json.loads(cache.read_text(encoding='utf-8'))
        if row.get('calibration_code_identity')==identity:
            print('reused completed calibration',height,flush=True)
            return row
    policy=ManualPolicy(load_jumps=False,detector={})
    policy.e0.selected_calibration=None
    sim=ManualSimulation(policy)
    sim.load_map(metadata('flat'))
    original=policy.e0.observation
    demand=[0.]
    def adapted(obs):
        x=original(obs)
        x[:,0]=torch.as_tensor(demand[0],dtype=x.dtype)
        return x
    policy.e0.observation=adapted
    samples=[]
    def measure(raw,requested):
        case=dict(course='flat',height=height,speed=requested,yaw_deg=0.,offset=[0.,0.],armed=False)
        reset_case(sim,case)
        velocity=[]
        for k in range(310):
            moving=k>=40
            goal=raw if moving else 0.
            if moving:
                demand[0]+=(goal-demand[0])/12.
            else:demand[0]=0.
            sim.step(({'w'} if requested>0 else {'s'}) if moving else set(),command=(requested if moving else 0.,0.))
            if k>=235:
                velocity.append(float(sim.d.qvel[0]))
        value=float(np.mean(velocity))
        samples.append(dict(raw=raw,target=requested,actual=value))
        return value
    tables=[]
    for direction in (1.,-1.):
        raw_demands=[0.]
        for speed in SPEEDS[1:]:
            guess=direction*speed
            target=direction*speed
            last=None
            attempts=[]
            for iteration in range(5):
                actual=measure(guess,target)
                attempts.append((abs(actual-target),guess,actual))
                if abs(actual-target)<.025:break
                if last is not None and abs(actual-last[1])>.02:
                    gradient=np.clip((actual-last[1])/(guess-last[0]),.45,2.5)
                else:gradient=1.
                next_guess=direction*float(np.clip(abs(guess+direction*(speed-direction*actual)/gradient), .05,5.5))
                last=(guess,actual)
                guess=next_guess
            _,guess,actual=min(attempts)
            raw_demands.append(abs(guess))
            print('height',height,'speed',target,'actual',round(actual,3),'raw',round(guess,3),flush=True)
        tables.append(raw_demands)
    row=dict(height=height,raw_demands=tables[0],raw_demands_reverse=tables[1],samples=samples,
        calibration_code_identity=identity)
    put(cache,row)
    return row

def main():
    p=ArgumentParser(description=__doc__)
    p.add_argument('--workers',type=int,default=2)
    p.add_argument('--heights',type=float,nargs='+')
    args=p.parse_args()
    if args.heights:
        prior=json.loads((HERE/'E0_CALIBRATION.json').read_text(encoding='utf-8'))
        rows=prior['rows']
        with ProcessPoolExecutor(args.workers) as pool:new=list(pool.map(fit_height,args.heights))
        rows=[r for r in rows if r['height'] not in args.heights]+new
    else:
        with ProcessPoolExecutor(args.workers) as pool:rows=list(pool.map(fit_height,HEIGHTS))
    rows.sort(key=lambda r:r['height'])
    put(HERE/'E0_CALIBRATION.json',dict(e0_sha256=E0_SHA,e0_base_sha256=E0_BASE_SHA,height_blend_m=[.32,.40],physics_hz=400,policy_hz=50,
        speeds=SPEEDS,heights=[float(__import__('manual_fsm_model').effective_height(torch.tensor(r['height']))) for r in rows],
        raw_demands=[r['raw_demands'] for r in rows],
        raw_demands_reverse=[r['raw_demands_reverse'] for r in rows],
        method='Measured symmetric BlendedDrive inverse curves, independently for forward and reverse',
        speed_stance_rule='At |command|>2.2 m/s low stance smoothly rises to .32 m; high-stance reverse smoothly lowers to .32 m to avoid the measured reverse-curve fold',
        rows=rows))

if __name__=='__main__':main()
