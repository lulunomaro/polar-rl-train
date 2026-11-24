"""Jump regressions through the same unified player control loop."""
from argparse import ArgumentParser
from concurrent.futures import ProcessPoolExecutor
from itertools import product
import math
import numpy as np
import torch
import mujoco as mj
from pathlib import Path
from fsm_paths import HERE,JUMP_PATH
from fsm_io import put,sha256
from manual_fsm_runtime import ManualPolicy,ManualSimulation
from manual_fsm_core import Phase
from fsm_maps import metadata
from fsm_evaluation import ContactJudge,reset_case

def run_jump(case,frames=None,checkpoint=None):
    policy=ManualPolicy(checkpoint or case.get('checkpoint'))
    policy.jump_hold_override=case.get('hold_ticks',31)
    sim=ManualSimulation(policy)
    sim.load_map(metadata(case['course']))
    yaw,sign,ground=reset_case(sim,case)
    judge=ContactJudge(sim,case,yaw,sign,ground)
    peak=0.;air_samples=0;top_samples=0;face_max=0.;trigger=None;fall=False
    flight_start=flight_end=None;first_landing_top=False;air_streak=0
    key_speed=flight_speed=None
    top_streak=top_best=0
    timeline=[];substeps=[]
    force=np.zeros(6)
    def sample(s):
        nonlocal peak,air_samples,top_samples,face_max,flight_start,flight_end
        nonlocal first_landing_top,air_streak,top_streak,top_best,flight_speed
        judge.observe_fsm(s)
        if trigger is None:return
        wheels=s.d.geom_xpos[s.tire_gids]
        row=judge.trace[-1]
        loaded=np.array(row[21:23])
        top_samples+=int(bool((loaded>5.).all()))
        top_streak=top_streak+1 if (loaded>5.).all() else 0
        top_best=max(top_best,top_streak)
        wheel_loaded=np.zeros(2)
        face_now=0.
        for i in range(s.d.ncon):
            c=s.d.contact[i];g1,g2=map(int,c.geom)
            robot=g2 if g1 in judge.terrain else g1 if g2 in judge.terrain else None
            if robot not in judge._robot_gids:continue
            if robot is None:continue
            mj.mj_contactForce(s.m,s.d,i,force)
            normal=c.frame[:3]*(1. if g1 in judge.terrain else -1.)
            if robot in judge.tires:
                side=judge.robot_side[robot]
                wheel_loaded[side]+=max(0.,float(force[0]*normal[2]))
            if abs(normal[0])>.7 and case['course'].startswith('platform_'):
                top=int(case['course'].split('_')[1])*.001
                if abs(c.pos[0]-3.3)<.015 and c.pos[2]<top-.005:
                    face_now+=float(force[0])
        clearance=float(wheels[:,2].min()-.0625-ground)
        airborne=bool((wheel_loaded<1.).all())
        air_streak=air_streak+1 if airborne else 0
        if flight_start is None and air_streak>=4 and clearance>.04:
            flight_start=float(s.d.time)
            flight_speed=float(judge.trace[-1][2])
        if flight_end is None:
            face_max=max(face_max,face_now)
        if flight_start is not None and flight_end is None:
            peak=max(peak,clearance)
            air_samples+=int(airborne)
            if bool((wheel_loaded>5.).any()):
                flight_end=float(s.d.time)
                first_landing_top=bool((loaded>5.).any()) if case['course'].startswith('platform_') else True
        substeps.append([s.d.time,*wheel_loaded,*loaded,clearance,face_now])
    sim.physics_observer=sample
    for tick in range(round(case['seconds']/.02)):
        moving=tick*.02>=case.get('settle_s',.8)
        keys={'w'} if moving and case['speed'] else set()
        want=(tick*.02>=case.get('press_s',1.5)) if case['course']=='flat' else judge.front_gap()<=case['front_gap']
        if trigger is None and moving and want:
            keys.add('space');trigger=tick
            key_speed=float(judge.trace[-1][2]) if judge.trace else 0.
        sim.step(keys,command=(case['speed'] if moving else 0.,0.))
        timeline.append(np.r_[sim.d.time,policy.last_model_obs,sim.prev_a,int(policy.fsm.phase[0]),
                              sim.route['e2'],sim.d.qpos[:3]])
        if frames is not None:frames(sim,judge,tick)
        if sim.d.xmat[sim.env.base_id].reshape(3,3)[2,2]<math.cos(math.radians(65)):
            fall=True;break
        if flight_end is not None and sim.d.time>=flight_end+1.2 and policy.fsm.phase[0]==Phase.CRUISE_E0:
            break
    row=judge.summary(case,'fall' if fall else None)
    sim.physics_observer=None
    row.update(jump_sha256=sha256(JUMP_PATH),jump_kind=policy.jump_kind,trigger_tick=trigger,
        peak_bilateral_tire_clearance_m=peak,bilateral_airtime_s=air_samples*.0025,
        both_wheels_top_samples=top_samples,peak_riser_face_force_n=face_max,
        longest_top_support_substeps=top_best,main_flight_start_s=flight_start,main_flight_end_s=flight_end,
        main_flight_first_landing_on_top=first_landing_top,
        actual_key_ticks=int(sum(t[31]>.5 for t in timeline)),
        actual_speed_at_key_m_s=key_speed,actual_speed_at_main_flight_m_s=flight_speed,
        returned_to_cruise=bool(policy.fsm.phase[0]==Phase.CRUISE_E0),
        jump_exit_timeout=bool(getattr(policy,'jump_exit_timeout',False)))
    speed_ok=key_speed is not None and (abs(key_speed)<.10 if case['speed']==0 else key_speed>=case['speed']-.15)
    row['actual_approach_speed_passed']=speed_ok
    row['passed']=bool(trigger is not None and speed_ok and not fall and peak>=(.30 if case['speed']==0 else .38)
        and first_landing_top and face_max<=5.
        and (not case['course'].startswith('platform_') or top_samples>=40)
        and row['returned_to_cruise'] and not row['jump_exit_timeout'])
    return row,dict(timeline=np.asarray(timeline),physics=np.asarray(judge.physics_records),
        jump_substeps=np.asarray(substeps),reference_trace=np.asarray(judge.trace))

def worker(case):
    import gc
    row,trace=run_jump(case)
    folder=HERE/'evidence'/case.get('output_tag','jump_integration')
    folder.mkdir(parents=True,exist_ok=True)
    put(folder/(case['id']+'.json'),row)
    np.savez_compressed(folder/(case['id']+'.npz'),**trace)
    gc.collect()
    return row

def cases(sweep=False):
    rows=[dict(id='stationary_000',course='flat',speed=0.,height=.28,yaw_deg=0.,offset=[0.,0.],
               seconds=5.,settle_s=.8,press_s=1.5,wz=0.,task='',armed=False)]
    for course,speed,lead in product(('platform_380','platform_360'),(1.6,2.8),(.15,.25,.35,.45,.55,.7) if sweep else (.7,)):
        rows.append(dict(id=f'jump_{len(rows):03d}',course=course,speed=speed,height=.28,yaw_deg=0.,
            offset=[-5.,0.],seconds=10.,settle_s=.8,front_gap=(lead if speed==2.8 else .35),wz=0.,task='',armed=False,hold_ticks=31))
    return rows

def main():
    from datetime import datetime
    p=ArgumentParser(description=__doc__);p.add_argument('--workers',type=int,default=2)
    p.add_argument('--sweep',action='store_true');p.add_argument('--checkpoint',type=Path);args=p.parse_args()
    rows=[]
    tag='jump_'+datetime.now().strftime('%Y%m%d_%H%M%S')
    jobs=[dict(c,output_tag=tag,checkpoint=str(args.checkpoint) if args.checkpoint else None) for c in cases(args.sweep)]
    with ProcessPoolExecutor(args.workers) as pool:
        for row in pool.map(worker,jobs):
            rows.append(row)
            print(row['id'],row['course'],row['speed'],row['passed'],'peak',round(row['peak_bilateral_tire_clearance_m'],3),
                  'support',row['both_wheels_top_samples'],'end',row['end_phase'],flush=True)
    put(HERE/'evidence'/tag/'RESULT.json',dict(passed=sum(r['passed'] for r in rows),total=len(rows),rows=rows))

if __name__=='__main__':main()
