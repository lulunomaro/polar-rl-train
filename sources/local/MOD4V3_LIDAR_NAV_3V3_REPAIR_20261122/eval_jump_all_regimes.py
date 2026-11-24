"""Raw human input matrix: 56 (height,C,speed) groups x keep/release =112 runs."""
from nav_common import HERE,put,sha256
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from itertools import product
import argparse
import json
import math
import numpy as np
from nav4d_runtime import Nav4DPolicy,Nav4DSimulation

def run_jump(case,checkpoint=None,record=None):
    policy=Nav4DPolicy(jump_checkpoint=checkpoint);sim=Nav4DSimulation(policy)
    sim.load_scene(case.get('course','flat'),height=case['height'])
    sim.mode_latched=case['c'];floor=sim.ground_z(*sim.pose()[:2])
    peak_rim=peak_all=airpitch=airroll=peak_pitch=peak_roll=0.;airtime=0.;flipped=False
    trace=[];window=[];raw_ok=True;initial_vx=None
    def physics(s):
        nonlocal peak_rim,peak_all,airpitch,airroll,peak_pitch,peak_roll,airtime,flipped
        m=s.measure();p=abs(math.degrees(m['pitch']));r=abs(math.degrees(m['roll']))
        peak_pitch=max(peak_pitch,p);peak_roll=max(peak_roll,r)
        flipped |= p>65. or r>65.
        if m['airborne']:
            peak_rim=max(peak_rim,m['tire_low']-floor);peak_all=max(peak_all,m['lowest']-floor)
            airpitch=max(airpitch,p);airroll=max(airroll,r);airtime+=.0025
        if record is not None:record(s,m)
    for i in range(120):sim.step(set(),command=(0. if i<40 else case['speed'],0.))
    initial_measurement=sim.measure();initial_vx=initial_measurement['vx'];policy.assist=bool(case['c'])
    sim.physics_observer=physics
    for k in range(180):
        keys={'space'} if k<case.get('hold_ticks',5) else set()
        if not case['release'] and case['speed']>0:keys.add('w')
        command=0. if case['release'] else case['speed']
        sim.step(keys,command=(command,0.))
        raw_ok &= np.array_equal(sim.last_obs[:4],policy.last_model_obs[:4])
        m=sim.measure();trace.append([sim.d.time,*sim.pose(),m['vx'],m['tire_low']-floor,m['lowest']-floor,
            math.degrees(m['pitch']),math.degrees(m['roll']),sim.route['e2'],*sim.last_obs[:4]])
        if flipped:break
    result=dict(case,liftoff=peak_rim>=.22,passed=peak_rim>=.22 and not flipped,flip=flipped,
        rim_cm=100.*peak_rim,all_geom_clearance_cm=100.*peak_all,air_pitch_deg=airpitch,air_roll_deg=airroll,
        peak_pitch_deg=peak_pitch,peak_roll_deg=peak_roll,airtime_s=airtime,actual_takeoff_request_vx=initial_vx,
        actual_takeoff_request_height_m=initial_measurement['body_height'],
        air_pitch_within_10deg=airpitch<=10.,air_roll_within_8deg=airroll<=8.,
        raw_commands_unchanged=raw_ok,one_jump_checkpoint=True,external_pre_crouch_ticks=0,
        external_command_latch=False,jump_motor_law='R10 JumpPlant._compute_motor_torque')
    return result,np.asarray(trace)

def worker(task):
    case,checkpoint,out,index=task;result,trace=run_jump(case,checkpoint)
    folder=Path(out);folder.mkdir(parents=True,exist_ok=True)
    np.savez_compressed(folder/f'jump_{index:04d}.npz',control=trace)
    put(folder/f'jump_{index:04d}.json',result);return result

def evaluate(checkpoint=None,workers=6,out=None,full=False,nominal=False):
    if checkpoint is None and (HERE/'CANDIDATE_NAV4D.json').exists():
        selected=json.loads((HERE/'CANDIDATE_NAV4D.json').read_text(encoding='utf-8'))
        if 'jump' in selected:checkpoint=HERE/selected['jump']['checkpoint']
    folder=Path(out or HERE/'evidence/jump_matrix');folder.mkdir(parents=True,exist_ok=True)
    heights=(.28,) if nominal else (.28,.35,.39,.42)
    speeds=(1.2,1.6,2.2,2.8) if nominal else (0.,.6,.8,1.2,1.6,2.2,2.8)
    rows=[]
    for h,c,v,release,hold in product(heights,(False,True),speeds,(False,True),(5,25) if full else (5,)):
        rows.append(dict(height=h,c=c,speed=v,release=release,hold_ticks=hold))
    tasks=[(row,str(checkpoint) if checkpoint else None,str(folder/'cases'),i) for i,row in enumerate(rows)]
    with ProcessPoolExecutor(max_workers=workers) as pool:results=list(pool.map(worker,tasks))
    groups=[]
    for h,c,v in product(heights,(False,True),speeds):
        group=[r for r in results if r['height']==h and r['c']==c and r['speed']==v]
        groups.append(dict(height=h,c=c,speed=v,liftoff=all(r['liftoff'] for r in group),
                           passed=all(r['passed'] for r in group),flips=sum(r['flip'] for r in group)))
    summary=dict(checkpoint=str(checkpoint),sha256=sha256(checkpoint) if checkpoint else None,
        group_count=len(groups),groups_liftoff=sum(r['liftoff'] for r in groups),groups_passed=sum(r['passed'] for r in groups),
        actual_replays=len(results),replays_liftoff=sum(r['liftoff'] for r in results),flips=sum(r['flip'] for r in results),
        passed=all(r['passed'] for r in results),groups=groups,cases=results,
        max_air_pitch_deg=max(r['air_pitch_deg'] for r in results),
        max_air_roll_deg=max(r['air_roll_deg'] for r in results),
        level_air_pitch_replays=sum(r['air_pitch_within_10deg'] for r in results),
        level_air_roll_replays=sum(r['air_roll_within_8deg'] for r in results),
        all_commands_unchanged=all(r['raw_commands_unchanged'] for r in results),
        count_note=f'{len(heights)} heights x 2 C states x {len(speeds)} speeds = {len(groups)} groups; keep/release W x {2 if full else 1} hold duration(s) = {len(results)} actual replays.')
    put(folder/'SUMMARY.json',summary)
    if out is None:put(HERE/'evidence/JUMP_56_AUDIT.json',summary)
    print(json.dumps({k:v for k,v in summary.items() if k not in ('groups','cases')},indent=2),flush=True)
    return summary

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--checkpoint',type=Path);p.add_argument('--workers',type=int,default=6)
    p.add_argument('--out',type=Path);p.add_argument('--full',action='store_true');p.add_argument('--nominal',action='store_true');a=p.parse_args()
    evaluate(a.checkpoint,a.workers,a.out,a.full,a.nominal)
