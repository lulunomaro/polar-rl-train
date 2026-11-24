"""Full independent acceptance; failures remain visible and never promote silently."""
from nav_common import HERE,put,sha256
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from itertools import product
import argparse
import json
import math
import numpy as np
from nav4d_runtime import Nav4DPolicy,Nav4DSimulation,reference
from nav_maps import stage_scene,build_elevation
from terrain_sensor_4d import TerrainSensor4D,S_GRID_NP,extract_profile
from eval_stair_nav4d import evaluate as eval_stairs
from eval_jump_all_regimes import evaluate as eval_jumps

def cruise_case(task):
    case,stair,jump=task;policy=Nav4DPolicy(stair,jump);sim=Nav4DSimulation(policy)
    sim.load_scene('flat',height=case['height'])
    sim.scene_meta['spawns']=[dict(x=case['offset'][0],y=case['offset'][1],yaw_deg=case['yaw_deg'],name=case['id'])]
    sim.reset_at_spawn(0);trace=[];false_triggers=0;failure=None
    for i in range(round(case['seconds']/.02)):
        sim.step(set(),command=(case['speed'],case['wz']))
        false_triggers+=int(sim.route['e1']>0)
        r=sim.d.xmat[sim.env.base_id].reshape(3,3)
        vx=float(np.dot(sim.d.qvel[:2],r[:2,0])/max(.01,np.linalg.norm(r[:2,0])))
        trace.append([vx,sim.d.qvel[5],sim.d.qpos[2]-sim.ground_z(*sim.pose()[:2])])
        if r[2,2]<.4:failure='fall';break
    tail=np.asarray(trace)[-200:];actual=tail.mean(0)
    taskname=case['task']
    if taskname.startswith('height'):passed=abs(actual[2]-case['height'])<=.02
    elif case['wz']:passed=abs(actual[1]-case['wz'])<=abs(case['wz'])*.02
    else:passed=abs(actual[0]-case['speed'])<=(.20 if case['speed']<0 else .15)
    return dict(case,passed=bool(passed and failure is None and false_triggers==0),failure=failure,
        tail_vx=float(actual[0]),tail_yaw_rate=float(actual[1]),tail_height=float(actual[2]),false_stair_ticks=false_triggers)

def cruise(stair=None,jump=None,workers=6):
    cases=reference.cases()[:60];stage_scene('flat')
    with ProcessPoolExecutor(max_workers=workers) as pool:rows=list(pool.map(cruise_case,[(c,stair,jump) for c in cases]))
    result=dict(passed=sum(r['passed'] for r in rows),total=len(rows),false_stair_ticks=sum(r['false_stair_ticks'] for r in rows),cases=rows)
    put(HERE/'evidence/FLAT60_NAV4D.json',result);return result

def ramps(stair=None,jump=None):
    if not (HERE/'maps/elevation/serial_17.npz').exists():build_elevation('serial_17')
    policy=Nav4DPolicy(stair,jump);sim=Nav4DSimulation(policy);sim.load_scene('serial_17')
    false=0;maxpitch=0.;samples=[]
    for i in range(280):
        sim.step(set(),command=(.8,0.));false+=int(sim.route['e1']>0)
        maxpitch=max(maxpitch,abs(math.degrees(sim.measure()['pitch'])))
        samples.append(sim.last_g.tolist())
    analytical=extract_profile(S_GRID_NP,np.tan(math.radians(17.))*S_GRID_NP)
    result=dict(passed=false==0 and analytical[1]==0.,false_stair_ticks=false,analytical_g_step=analytical.tolist(),
        physical_course='Serial_Leg donor 17 degree ramp fixture',max_pitch_deg=maxpitch,final_pose=list(sim.pose()),samples=samples)
    put(HERE/'evidence/RAMP17_NAV4D.json',result);return result

def highspeed(stair=None,jump=None):
    rows=[]
    for speed in (.8,1.2,1.6,2.,2.4,2.8,3.):
        policy=Nav4DPolicy(stair,jump);sim=Nav4DSimulation(policy);sim.load_scene('flat',height=.35)
        count=0;tail=[]
        for k in range(180):
            sim.step(set(),command=(speed,0.));count+=int(sim.route['e1']>0)
            if k>=130:tail.append(sim.measure()['vx'])
        rows.append(dict(speed=speed,mean_vx=float(np.mean(tail)),false_stair_ticks=count))
    result=dict(passed=all(r['false_stair_ticks']==0 for r in rows),cases=rows)
    put(HERE/'evidence/HIGH_SPEED_NAV4D.json',result);return result

def mission(course,stair=None,jump=None,record=None):
    policy=Nav4DPolicy(stair,jump);sim=Nav4DSimulation(policy);sim.load_scene(course)
    goals=[(-2.5,.8),(-2.5,2.1),(-4.7,2.1),(-4.9,-2.3)] if course=='suite_rmul2027' else [(-14.0,-4.80),(-13.6,-4.45),(-16.8,-4.85)]
    completed=0;failure=None;trace=[];peaktilt=0.
    for goal in goals:
        try:sim.navigate_to(*goal,speed=1.)
        except ValueError as e:failure=str(e);break
        for k in range(1100):
            sim.step(set());m=sim.measure();tilt=max(abs(math.degrees(m['pitch'])),abs(math.degrees(m['roll'])))
            peaktilt=max(peaktilt,tilt);trace.append([sim.d.time,*sim.pose(),m['vx'],*sim.last_g,sim.route['e1']])
            if record is not None:record(sim,m)
            if tilt>65.:failure='flip';break
            if sim.follower.done:completed+=1;break
        else:failure='waypoint_timeout'
        if failure:break
    result=dict(course=course,passed=completed==len(goals) and failure is None,completed_waypoints=completed,total_waypoints=len(goals),
        failure=failure,peak_tilt_deg=peaktilt,goals=goals,final_pose=list(sim.pose()))
    np.savez_compressed(HERE/'evidence'/f'MISSION_{course}.npz',control=np.asarray(trace))
    put(HERE/'evidence'/f'MISSION_{course}.json',result);return result

def main():
    p=argparse.ArgumentParser();p.add_argument('--stair',type=Path);p.add_argument('--jump',type=Path);p.add_argument('--workers',type=int,default=6)
    p.add_argument('--part',choices=('all','cruise','ramps','missions','stairs','jumps'),default='all');args=p.parse_args()
    results={};s=str(args.stair) if args.stair else None;j=str(args.jump) if args.jump else None
    if args.part in ('all','cruise'):results.update(flat60=cruise(s,j,args.workers),high_speed=highspeed(s,j))
    if args.part in ('all','ramps'):results['ramp17']=ramps(s,j)
    if args.part in ('all','stairs'):results['stairs']=eval_stairs(args.stair,'full',args.workers,HERE/'evidence/final_stairs')
    if args.part in ('all','jumps'):results['jumps']=eval_jumps(args.jump,args.workers)
    if args.part in ('all','missions'):results['missions']=[mission(c,s,j) for c in ('suite_rmul2027','suite_rmuc2027')]
    put(HERE/'evidence'/f'ACCEPTANCE_{args.part}.json',results)

if __name__=='__main__':main()
