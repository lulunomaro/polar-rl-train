"""Measure the SELECTED_E0 command curve with the shared 400 Hz motor loop."""
from concurrent.futures import ProcessPoolExecutor
from argparse import ArgumentParser
import json
import numpy as np
import torch
from fsm_paths import HERE,E0_SHA
from fsm_io import put
from fsm_maps import metadata
from manual_fsm_runtime import ManualPolicy,ManualSimulation
from fsm_evaluation import reset_case

SPEEDS=(0.,.6,.8,1.,1.2,1.6,2.,2.2,2.4,2.8,3.)
HEIGHTS=(.20,.24,.28,.32,.35,.38,.38833333,.395)

def fit_height(height):
    policy=ManualPolicy(load_jumps=False)
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
            sim.step({'w'} if moving else set(),command=(requested if moving else 0.,0.))
            if k>=235:
                velocity.append(float(sim.d.qvel[0]))
        value=float(np.mean(velocity))
        samples.append(dict(raw=raw,target=requested,actual=value))
        return value
    raw_demands=[0.]
    for speed in SPEEDS[1:]:
        guess=speed
        last=None
        for iteration in range(5):
            actual=measure(guess,speed)
            if abs(actual-speed)<.025:break
            if last is not None and abs(actual-last[1])>.02:
                gradient=np.clip((actual-last[1])/(guess-last[0]),.45,2.5)
            else:gradient=1.
            next_guess=float(np.clip(guess+(speed-actual)/gradient, .05,5.5))
            last=(guess,actual)
            guess=next_guess
        raw_demands.append(guess)
        print('height',height,'speed',speed,'actual',round(actual,3),'raw',round(guess,3),flush=True)
    return dict(height=height,raw_demands=raw_demands,samples=samples)

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
    put(HERE/'E0_CALIBRATION.json',dict(e0_sha256=E0_SHA,physics_hz=400,policy_hz=50,
        speeds=SPEEDS,heights=[float(__import__('manual_fsm_model').effective_height(torch.tensor(r['height']))) for r in rows],
        raw_demands=[r['raw_demands'] for r in rows],
        method='Measured SELECTED_E0 inverse curve; R10 bilinear calibration retained as fallback',
        rows=rows))

if __name__=='__main__':main()
