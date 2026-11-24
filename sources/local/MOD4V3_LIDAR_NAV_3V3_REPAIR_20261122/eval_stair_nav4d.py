"""Independent 400 Hz CPU MuJoCo stair and arena evaluation of raw nav4d policies."""
from nav_common import HERE,put,sha256
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import argparse
import json
import math
import time
import numpy as np
import mujoco as mj
from nav4d_runtime import Nav4DPolicy,Nav4DSimulation
from nav_maps import stage_scene

def cases(profile='screen'):
    result=[]
    def add(course,x,y,yaw,height,speed,offset=0.,name=None,wasd=False,seconds=7.):
        r=math.radians(yaw);result.append(dict(course=course,x=x+offset*math.cos(r),y=y+offset*math.sin(r),yaw=yaw,
            height=height,speed=speed,lift=.11 if course=='curb_11' else .20,wasd=wasd,
            name=name or f'{course}_v{speed}_o{offset:+.2f}_yaw{yaw}',seconds=seconds))
    speeds=(.6,1.,1.5,2.) if profile=='full' else (1.,)
    offsets=(-.06,-.03,0.,.03,.06)
    for speed in speeds:
        for offset in offsets:add('step_20',-.35,0.,0.,.28,speed,offset)
    if profile=='full':
        for height in (.35,.42):
            for offset in offsets:
                add('step_20',-.35,0.,0.,height,1.,offset,name=f'step20_h{height}_o{offset:+.2f}')
        for speed in speeds:
            for yaw in (-25.,25.):add('step_20',-.35,0.,yaw,.28,speed,name=f'step20_v{speed}_yaw{yaw}')
    for course,sign in [('oblique_20',1),('oblique_20_negative',-1)]:
        # The oblique_20 fixture lane runs along yaw=0 deg with its stair edge angled at +-22 deg.
        for speed in speeds:add(course,-.35,0.,0.,.28,speed)
    for speed in speeds:add('curb_11',-.35,0.,0.,.28,speed)
    entries=[(-3.5,.8,0.,'west_outer_592'),(-2.5,-1.,90.,'west_south_594'),
             (2.5,1.,-90.,'east_north_642'),(3.5,-.8,180.,'east_outer_643')]
    for ex,ey,yaw,label in entries:
        for speed in speeds:
            angles=(-15.,0.,15.) if profile=='full' else (0.,)
            for angle in angles:
                r=math.radians(yaw)
                add('suite_rmul2027',ex-1.30*math.cos(r),ey-1.30*math.sin(r),yaw+angle,.28,speed,name=f'rmul_{label}_v{speed}_a{angle}')
    if profile=='full':
        for speed in (.6,1.):
            add('suite_rmul2027',-2.5,3.52,-90.,.28,speed,name=f'rmul_side250_v{speed}')
            result[-1]['lift']=.20
    for speed in speeds:
        for label,x,y,yaw in [('west',-16.8,-4.85,0.),('east',-5.6,-5.9,180.)]:
            add('suite_rmuc2027',x,y,yaw,.28,speed,name=f'rmuc_{label}_v{speed}')
            result[-1]['lift']=.30;result[-1]['seconds']=9.
    if profile=='full':
        for course in ('rm27_west_400','rm27_east_400'):
            for speed in speeds:
                add(course,-.20,0.,0.,.28,speed)
                # In fsm_isaac_env.py line 90, rm27_*_400 has 0.40 m lip crest and 0.36 m upper deck.
                result[-1]['lift']=.36;result[-1]['seconds']=9.
        for speed in (.6,1.,1.5,2.):
            add('suite_proving',0.,-2.8,0.,.28,speed,name=f'proving_single_v{speed}')
        # High-speed (2.4 ~ 3.0 m/s) long-runup WASD & raw-step sprints (on step_20/oblique_20 stair edge is at x=+1.0m, so x=-2.0m is 3.0m runup!)
        for speed in (2.4,2.7,3.0):
            for h_fast in (.28,.38):
                add('step_20',-2.00,0.,0.,h_fast,speed,name=f'step20_fast_wasd_v{speed}_h{h_fast}',wasd=True,seconds=8.)
            add('step_20',-1.80,0.,0.,.28,speed,name=f'step20_fast_raw_v{speed}',wasd=False,seconds=8.)
        for course in ('oblique_20','oblique_20_negative'):
            for speed in (2.4,3.0):
                add(course,-2.00,0.,0.,.28,speed,name=f'{course}_fast_wasd_v{speed}',wasd=True,seconds=8.)
        for label,rx,ry,ryaw in [
            ('west_south_594',-2.35,-3.75,90.),
            ('east_north_642',2.35,3.75,-90.),
            ('west_outer_592',-5.70,.80,0.),
            ('east_outer_643',5.70,-.80,180.),
        ]:
            for speed in ((2.4,2.7,3.0) if '594' in label or '642' in label else (2.4,3.0)):
                add('suite_rmul2027',rx,ry,ryaw,.28,speed,name=f'rmul_fast_{label}_v{speed}',wasd=True,seconds=8.)
    return result

def run_case(case,checkpoint=None,jump_checkpoint=None,record=None):
    policy=Nav4DPolicy(checkpoint,jump_checkpoint);sim=Nav4DSimulation(policy)
    sim.load_scene(case['course'],height=case['height'])
    sim.scene_meta['spawns']=[dict(x=case['x'],y=case['y'],yaw_deg=case['yaw'],name=case['name'])]
    sim.reset_at_spawn(0)
    floor=sim.ground_z(case['x'],case['y']);target=floor+case['lift']
    # Keep invalid historical targets visible as coverage failures, rather than
    # attributing an absent deck to the neural checkpoint.
    check_s=np.arange(0.,4.21,.02);check_yaw=math.radians(case['yaw'])
    check_z=sim.elevation.sample(case['x']+check_s*math.cos(check_yaw),case['y']+check_s*math.sin(check_yaw))
    if not np.any(np.isfinite(check_z)&(np.abs(check_z-target)<.025)):
        return dict(case,passed=False,failure='invalid_evaluation_geometry',support_s=0.,
            max_pitch_deg=0.,max_roll_deg=0.,rollback_m=0.,progress_m=0.,stair_active_ticks=0,
            raw_commands_unchanged=True,seen_wheel_lift=False,physics_hz=400,
            ground_z_m=floor,target_z_m=target,
            coverage_note='No supporting tread at the requested target elevation exists on the first 4.2 m of this mapped approach.'),np.empty((0,22))
    traces=[];window=[];support=peak_support=0;peak_pitch=peak_roll=0.;rollback=0.;maxprogress=0.;stair_ticks=0
    r=math.radians(case['yaw']);direction=np.array([math.cos(r),math.sin(r)]);origin=np.array([case['x'],case['y']])
    failed=None;seen_lift=False;zero_hijack=True
    def observe(s):
        nonlocal peak_pitch,peak_roll
        m=s.measure();peak_pitch=max(peak_pitch,abs(math.degrees(m['pitch'])));peak_roll=max(peak_roll,abs(math.degrees(m['roll'])))
        window.append((m['loads'].copy(),m['wheel_low'].copy(),m['pitch']))
        if record is not None:record(s,m)
    sim.physics_observer=observe
    for k in range(round(case['seconds']/.02)):
        speed=0. if k<40 else case['speed'];window.clear()
        if case.get('wasd'):
            sim.max_vx=case['speed']
            sim.step({'w'} if speed else set())
        else:
            sim.step({'w'} if speed else set(),command=(speed,0.))
        zero_hijack &= np.array_equal(sim.last_obs[:4],policy.last_model_obs[:4])
        stair_ticks+=int(sim.route['e1']>0)
        measured=sim.measure();progress=float(np.dot(np.array(sim.pose()[:2])-origin,direction))
        maxprogress=max(maxprogress,progress);rollback=max(rollback,maxprogress-progress)
        loads=np.mean([w[0] for w in window],axis=0)
        geometry=all(np.max(np.abs(w[1]-target))<.04 for w in window)
        upright=all(abs(w[2])<math.radians(25.) for w in window)
        on_top=loads.min()>5. and geometry and upright
        support=support+1 if on_top else 0;peak_support=max(peak_support,support)
        seen_lift |= measured['wheel_low'].min()>floor+.09
        traces.append([float(sim.d.time),*sim.pose(),progress,measured['vx'],measured['body_height'],
                       math.degrees(measured['pitch']),math.degrees(measured['roll']),*sim.last_g,*loads,
                       *measured['wheel_low'],sim.route['e1'],support,sim.closure_mm])
        if peak_pitch>65. or peak_roll>65.:failed='flip';break
        if sim.closure_mm>1000.:failed='catastrophic_closure';break
        if support>=20:break
    out=dict(case,passed=peak_support>=20 and failed is None,failure=failed,support_s=peak_support*.02,
        max_pitch_deg=peak_pitch,max_roll_deg=peak_roll,rollback_m=rollback,progress_m=maxprogress,
        stair_active_ticks=stair_ticks,raw_commands_unchanged=zero_hijack,seen_wheel_lift=bool(seen_lift),
        physics_hz=400,ground_z_m=floor,target_z_m=target)
    return out,np.asarray(traces)

def worker(task):
    case,checkpoint,out=task
    result,trace=run_case(case,checkpoint)
    folder=Path(out);folder.mkdir(parents=True,exist_ok=True)
    name=case['name'].replace('+','p').replace('-','m').replace('.','_')
    np.savez_compressed(folder/(name+'.npz'),control=trace)
    put(folder/(name+'.json'),result)
    return result

def evaluate(checkpoint=None,profile='screen',workers=6,out=None):
    if checkpoint is None and (HERE/'CANDIDATE_NAV4D.json').exists():
        selected=json.loads((HERE/'CANDIDATE_NAV4D.json').read_text(encoding='utf-8'))
        if 'stair' in selected:checkpoint=HERE/selected['stair']['checkpoint']
    out=Path(out or HERE/'evidence/stair_screen');out.mkdir(parents=True,exist_ok=True)
    tasks=[(c,str(checkpoint) if checkpoint else None,str(out/'cases')) for c in cases(profile)]
    for course in dict.fromkeys(c['course'] for c,_,_ in tasks):stage_scene(course)
    with ProcessPoolExecutor(max_workers=workers) as pool:rows=list(pool.map(worker,tasks))
    by={}
    for course in dict.fromkeys(c['course'] for c in rows):
        group=[c for c in rows if c['course']==course]
        by[course]=dict(passed=sum(c['passed'] for c in group),total=len(group),flips=sum(c['failure']=='flip' for c in group))
    single=[c for c in rows if c['course'] in ('step_20','oblique_20','oblique_20_negative')]
    fast=[c for c in rows if c['speed']>=2.4]
    result=dict(checkpoint=str(checkpoint),sha256=sha256(checkpoint) if checkpoint else None,profile=profile,
        passed=sum(c['passed'] for c in rows),total=len(rows),by_course=by,
        single200_preserved=all(c['passed'] for c in single),
        highspeed_stair_passed=bool(fast) and all(c['passed'] for c in fast),
        highspeed_cases_passed=sum(c['passed'] for c in fast),highspeed_cases_total=len(fast),
        all_commands_unchanged=all(c['raw_commands_unchanged'] for c in rows),cases=rows)
    put(out/'SUMMARY.json',result);print(json.dumps({k:v for k,v in result.items() if k!='cases'},indent=2),flush=True)
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--checkpoint',type=Path);p.add_argument('--profile',choices=('screen','full'),default='screen')
    p.add_argument('--workers',type=int,default=6);p.add_argument('--out',type=Path);a=p.parse_args()
    evaluate(a.checkpoint,a.profile,a.workers,a.out)
