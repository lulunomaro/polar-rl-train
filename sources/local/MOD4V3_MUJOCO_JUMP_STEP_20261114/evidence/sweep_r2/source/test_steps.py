"""Measure actual MuJoCo jumps onto the existing single official stair tile."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import shutil
import sys
import time
import traceback

import mujoco
import numpy as np
import torch

T=Path(__file__).resolve().parent
R=T.parents[2]
PLAYER=R/'sources/local/MOD4V3_FORWARD_JUMP_MANUAL_20261114'
PRIOR=R/'sources/local/MOD4V3_FORWARD_JUMP_REPAIR_2H_20261114'
HEIGHT=R/'sources/local/MOD4V3_FORWARD_JUMP_HEIGHT_2H_20261114'
sys.path.insert(0,str(PLAYER))
import manual_jump as player


def put(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n',encoding='utf8')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def checkpoints():
    rows=[dict(name='parent085',path=PRIOR/'weights/train7200__model_085m.pt',
               sha256='c4d0328472e8642c497f113e37fb8940d92435cd8d96f547b8f1f4aa15cc1dfe')]
    for minute in (40,55):
        result=json.loads((HEIGHT/f'evidence/eval_model_{minute:03d}m/RESULT.json').read_bytes())
        rows.append(dict(name=f'height{minute:03d}',path=HEIGHT/f'weights/train7200__model_{minute:03d}m.pt',
                         sha256=result['checkpoint_sha256']))
    return rows


def contact_state(sim,top_id,top_height):
    model,data=sim.env.m,sim.env.d
    top=np.zeros(2,dtype=bool)
    wall_force=0.
    force=np.zeros(6)
    for index in range(data.ncon):
        c=data.contact[index]
        ids=(int(c.geom1),int(c.geom2))
        if top_id not in ids:continue
        other=ids[1] if ids[0]==top_id else ids[0]
        body=int(model.geom_bodyid[other])
        if body not in sim.wheel_bodies:continue
        mujoco.mj_contactForce(model,data,index,force)
        normal_force=abs(float(force[0]))
        if abs(float(c.frame[2]))>.7 and float(c.pos[2])>top_height-.025:
            top[sim.wheel_bodies.index(body)]|=normal_force>5.
        else:wall_force=max(wall_force,normal_force)
    return top,wall_force


def run_case(sim,out,ident,gap,vx,flat=False,no_jump=False):
    case=out/ident
    case.mkdir()
    sim.reset_standing()
    sim.paused=False
    sim.args.vx=vx
    sim.last_jump=None
    reset_before=sim.resets
    request_before=sim.requests
    event_before=len(sim.events)
    model,data=sim.env.m,sim.env.d
    step_id=-1 if flat else model.geom('map_step_r03_c00_1').id
    step_edge=-2.9000000953674316
    next_edge=-1.4000000953674316
    height=0.2199999988079071
    if not flat:
        step_edge=float(model.geom_pos[step_id,0]-model.geom_size[step_id,0])
        height=float(model.geom_pos[step_id,2]+model.geom_size[step_id,2])
        upper=model.geom('map_step_r03_c00_2').id
        next_edge=float(model.geom_pos[upper,0]-model.geom_size[upper,0])
    requested=False
    request_time=None
    request_x=None
    request_vx=None
    physical_takeoff=False
    airborne_run=max_air_run=0.
    top_history=np.zeros((25,2),dtype=bool)
    stable_hold=max_stable=0.
    first_top=None
    first_both_top=None
    success_time=None
    wall_peak=0.
    peak_ground_clearance=0.
    furthest_wheel_x=-100.
    samples=[]
    reason='not_reached'
    started=time.perf_counter()
    for frame in range(450):
        now=float(data.time)
        wheels=data.xpos[sim.wheel_bodies].copy()
        lead=float(wheels[:,0].max()+.0625)
        pressed=set() if now<1. else {'w'}
        trigger=(now>=2.5) if flat else (now>=1. and step_edge-lead<=gap)
        if not requested and not no_jump and trigger:
            requested=bool(sim.request_jump())
            request_time=float(data.time)
            request_x=float(data.qpos[0])
            request_vx=float(sim.env.vx)
        sim.step(pressed)
        now=float(data.time)
        roll,pitch=sim._angles()
        wheels=data.xpos[sim.wheel_bodies].copy()
        rims=wheels[:,2]-.0625
        top,wall=contact_state(sim,step_id,height) if not flat else (np.zeros(2,dtype=bool),0.)
        wall_peak=max(wall_peak,wall)
        top_history[frame%25]=top
        if requested:
            airborne_run=airborne_run+.02 if sim.no_support else 0.
            max_air_run=max(max_air_run,airborne_run)
            physical_takeoff|=airborne_run>=.04 and float(data.qvel[2])>.1
            if sim.no_support:peak_ground_clearance=max(peak_ground_clearance,float(rims.min()))
        if physical_takeoff and top.any() and first_top is None:first_top=now
        if physical_takeoff and top.all() and first_both_top is None:first_both_top=now
        on_tread=bool(np.all(wheels[:,0]>step_edge+.02) and np.all(wheels[:,0]<next_edge-.02)
                      and np.all(np.abs(wheels[:,1])<2.8) and np.all(np.abs(rims-height)<.04))
        stable=bool(not flat and physical_takeoff and first_top is not None and on_tread
                    and top_history.mean(0).min()>=.8 and roll<math.radians(15) and pitch<math.radians(15)
                    and abs(float(data.qvel[2]))<.3 and abs(float(sim.env.vx))<1.2 and not sim.forbidden)
        stable_hold=stable_hold+.02 if stable else 0.
        max_stable=max(max_stable,stable_hold)
        if stable_hold>=.5 and success_time is None:success_time=now
        furthest_wheel_x=max(furthest_wheel_x,float(wheels[:,0].min()))
        samples.append(dict(t=now,qpos=data.qpos.copy(),qvel=data.qvel.copy(),phase=sim.phase,
                            root=data.qpos[:3].copy(),wheels=wheels,support=sim.support.copy(),top=top.copy(),
                            vx=float(sim.env.vx),command_vx=float(sim.cmd_vx),roll=roll,pitch=pitch,
                            stable_hold=stable_hold,no_support=sim.no_support,wall_force=wall,
                            requested=requested))
        if sim.resets!=reset_before:
            reason=sim.reason or 'automatic_reset'
            break
        if flat and requested and sim.last_jump:
            reason=sim.last_jump['reason']
            break
        if not flat and success_time is not None and now-success_time>=.6:
            reason='jumped_onto_step_and_stable'
            break
        if requested and request_time is not None and now-request_time>=5.:
            reason='landed_on_step_but_not_stable' if first_top is not None else ('hit_riser' if wall_peak>5. else 'did_not_land_on_step')
            break
        if no_jump and now>=7.:
            reason='drive_only_control'
            break
    resets=sim.resets-reset_before
    accepted=bool((sim.last_jump and sim.last_jump['accepted']) if flat else
                  (requested and physical_takeoff and max_air_run>=.08 and success_time is not None and resets==0))
    if flat:accepted=accepted and resets==0
    result=dict(id=ident,epoch=time.time(),flat=flat,no_jump=no_jump,trigger_gap_m=gap,command_vx_m_s=vx,
                terrain='r03_c50' if flat else 'r03_c00',step_height_m=0. if flat else height,
                step_edge_x_m=step_edge,request_time_s=request_time,request_root_x_m=request_x,
                actual_vx_at_request_m_s=request_vx,requests=sim.requests-request_before,
                physical_takeoff=physical_takeoff,max_continuous_air_s=max_air_run,
                airborne_lower_rim_peak_above_approach_m=peak_ground_clearance,
                first_top_contact_s=first_top,first_both_wheels_top_contact_s=first_both_top,
                max_stable_on_step_s=max_stable,success_time_s=success_time,
                max_riser_contact_force_N=wall_peak,furthest_both_wheel_center_x_m=furthest_wheel_x,
                accepted=accepted,reason=reason,resets=resets,player_last_jump=sim.last_jump,
                closure_m=sim.closure,mimic_rad=sim.mimic,simulation_seconds=float(data.time),
                wall_seconds=time.perf_counter()-started,final_root_xyz=data.qpos[:3].tolist(),
                events=sim.events[event_before:])
    np.savez_compressed(case/'trajectory.npz',**{key:np.stack([s[key] for s in samples]) for key in samples[0]})
    put(case/'RESULT.json',result)
    print(json.dumps({k:result[k] for k in ['id','accepted','reason','airborne_lower_rim_peak_above_approach_m','max_stable_on_step_s','resets']}),flush=True)
    return result


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--run',required=True)
    parser.add_argument('--models',nargs='+',default=['parent085','height040','height055'])
    parser.add_argument('--gaps',nargs='+',type=float,default=[.2,.3,.4,.5,.6])
    args=parser.parse_args()
    out=T/'evidence'/args.run
    out.mkdir(parents=True,exist_ok=False)
    torch.set_num_threads(1)
    torch.manual_seed(66);np.random.seed(66)
    rows=checkpoints()
    for row in rows:assert digest(row['path'])==row['sha256'],row['name']
    source=[]
    for p in [PLAYER/'manual_jump.py',PLAYER/'map_terrain.py',Path(__file__)]:
        destination=out/'source'/p.name
        destination.parent.mkdir(exist_ok=True)
        shutil.copy2(p,destination)
        source.append(dict(path=str(p),sha256=digest(p)))
    manifest=dict(epoch=time.time(),run=args.run,mujoco_version=mujoco.__version__,seed=66,
                  models=[{**row,'path':str(row['path'])} for row in rows],source=source,
                  gaps_m=args.gaps,terrain='Original saved Isaac Lab tile r03_c00, one tile, first22cm riser',
                  controller='Existing MuJoCo WASD drive actor and one-shot learned Space jump',
                  physics_dt_s=.0025,leg_feedback_hz=100,wheel_feedback_hz=400,policy_hz=50,
                  closure_reset_m=.01,mimic_reset_rad=.01,plant_motors_unchanged=True,
                  optimizer_created=False,external_jump_assist=False,
                  success='Measured flight before top landing, both wheels on first tread, stable>=0.5s, no reset',
                  limitations='Deterministic nominal MuJoCo and selected trigger distances; no statistical DR pass-rate claim')
    put(out/'INPUTS.json',manifest)
    results=[]
    try:
        for row in rows:
            if row['name'] not in args.models:continue
            player.JUMP=row['path'];player.JUMP_SHA=row['sha256']
            sim=player.JumpSimulation(terrain=True,terrain_family=8)
            try:results.append(run_case(sim,out,row['name']+'_flat',.0,.6,flat=True))
            finally:sim.close()
            sim=player.JumpSimulation(terrain=True)
            try:
                assert abs(sim.env.m.opt.timestep-.0025)<1e-12
                assert sum((sim.env.m.geom(i).name or '').startswith('map_visual_') for i in range(sim.env.m.ngeom))==1
                if row['name']=='parent085':
                    results.append(run_case(sim,out,'drive_only',0.,.6,no_jump=True))
                for gap in args.gaps:
                    ident=f"{row['name']}_gap{int(round(gap*100)):02d}"
                    results.append(run_case(sim,out,ident,gap,.6))
            finally:sim.close()
        summary=dict(epoch=time.time(),run=args.run,attempts=len(results),
                     step_attempts=sum(not x['flat'] and not x['no_jump'] for x in results),
                     step_passes=sum(x['accepted'] for x in results if not x['flat'] and not x['no_jump']),
                     cases=results)
        put(out/'RESULT.json',summary)
    except BaseException:
        put(out/'ERROR.json',dict(epoch=time.time(),traceback=traceback.format_exc(),completed_cases=len(results)))
        raise


if __name__=='__main__':main()
