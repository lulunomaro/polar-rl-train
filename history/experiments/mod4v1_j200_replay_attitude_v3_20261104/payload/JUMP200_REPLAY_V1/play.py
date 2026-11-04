"""MuJoCo recorded-pose playback of the two completed J200 runs. No mj_step/control."""
import os
for name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[name]='1'
from pathlib import Path
import argparse
import json
import queue
import sys
import time
import numpy as np
import mujoco
import mujoco.viewer

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from JUMP200_LQR_MPC_V1.bridge200 import model_factory200
CASES={
    'capture':'j200_capture_v2_nominal_200002',
    'baseline':'j200_nominal_baseline_200001_attempt002',
}


def load_case(name,nq):
    folder=ROOT/'JUMP200_LQR_MPC_V1/runs'/CASES[name]
    result=json.loads((folder/'result.json').read_bytes())
    times=[];poses=[];phases=[]
    # Explicitly requested visualization: one sequential read, no payload hash.
    with (folder/'trace.jsonl').open(encoding='utf8') as source:
        for line in source:
            row=json.loads(line)
            times.append(float(row['time']))
            poses.append(row['qpos_truth_grading'])
            phases.append(str(row['phase']))
    t=np.asarray(times,float);q=np.asarray(poses,float)
    if q.shape!=(len(t),nq) or not len(t) or not np.isfinite(q).all() or not np.isfinite(t).all() or np.any(np.diff(t)<=0):
        raise ValueError('Recorded pose/time contract')
    return dict(time=t,qpos=q,phase=phases,result=result,path=str(folder))


def pose_at(record,t):
    times=record['time'];poses=record['qpos']
    i=max(0,min(len(times)-1,int(np.searchsorted(times,t,side='right')-1)))
    j=min(i+1,len(times)-1)
    a=0. if i==j else float(np.clip((t-times[i])/(times[j]-times[i]),0.,1.))
    q=(1.-a)*poses[i]+a*poses[j]
    # Root is the model's sole quaternion: shortest-arc normalized interpolation.
    qa=poses[i,3:7];qb=poses[j,3:7]
    if np.dot(qa,qb)<0:qb=-qb
    quat=(1.-a)*qa+a*qb
    q[3:7]=quat/np.linalg.norm(quat)
    return q,i


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case',choices=CASES,default='capture')
    parser.add_argument('--rate',type=float,default=.5)
    parser.add_argument('--wall-seconds',type=float,default=0.,help='Optional finite viewer-lifecycle check only')
    args=parser.parse_args()
    if not np.isfinite(args.rate) or not .05<=args.rate<=2.:raise ValueError('Playback rate must be0.05..2')
    model=model_factory200(True)
    if (model.nbody,model.nq,model.nv,model.nu)!=(32,37,36,6):raise ValueError('Authoritative model dimensions changed')
    data=mujoco.MjData(model)
    cache={args.case:load_case(args.case,model.nq)}
    selected=args.case;record=cache[selected]
    commands=queue.SimpleQueue()
    def key(code):
        action={32:'pause',80:'pause',82:'restart',83:'speed',49:'baseline',50:'capture',81:'quit'}.get(code)
        if action:commands.put(action)
    play_t=0.;rate=args.rate;paused=False
    q,_=pose_at(record,play_t);data.qpos[:]=q;mujoco.mj_forward(model,data)
    started=previous=time.perf_counter()
    print(f'J200_REPLAY_LOADING pid={os.getpid()} case={selected} recorded_rows={len(record["time"])} mj_step_calls=0',flush=True)
    with mujoco.viewer.launch_passive(model,data,key_callback=key,show_left_ui=False,show_right_ui=False) as view:
        with view.lock():
            view.cam.lookat[:]=[.30,0.,.30]
            view.cam.distance=3.0;view.cam.azimuth=135.;view.cam.elevation=-20.
            view.opt.flags[mujoco.mjtVisFlag.mjVIS_CONTACTPOINT]=False
            view.opt.flags[mujoco.mjtVisFlag.mjVIS_CONTACTFORCE]=False
        print('J200_REPLAY_READY | recorded poses, NOT a new physical trial | 1 baseline / 2 capture / P pause / R restart / S speed / Q close',flush=True)
        stop=False
        while view.is_running() and not stop:
            now=time.perf_counter();elapsed=min(.1,max(0.,now-previous));previous=now
            while not commands.empty():
                action=commands.get()
                if action=='quit':stop=True
                elif action=='pause':paused=not paused
                elif action=='restart':play_t=0.
                elif action=='speed':rate={.25:.5,.5:1.,1.:.25}.get(rate,.25)
                elif action in CASES:
                    selected=action
                    if selected not in cache:cache[selected]=load_case(selected,model.nq)
                    record=cache[selected];play_t=0.
                    print('J200_REPLAY_CASE '+selected,flush=True)
            if args.wall_seconds>0 and now-started>=args.wall_seconds:break
            if not paused:play_t+=elapsed*rate
            if play_t>record['time'][-1]+1.:play_t=0.
            q,index=pose_at(record,play_t)
            result=record['result'];guide=result['physics_contact_audit']['guide_contact_ticks']
            phase='END HOLD' if play_t>=record['time'][-1] else record['phase'][index]
            messages=[
                'RECORDED JUMP200 / NO NEW PHYSICS / '+selected.upper(),
                f't={min(play_t,record["time"][-1]):.2f}s  {rate:.2f}x  {"PAUSED" if paused else phase}',
                f'Saved top hold {result["end_stable_s"]:.2f}s | guide {guide} ticks | clean FAIL | DR untested',
                'P/Space pause   R restart   S speed   1 baseline   2 capture   Q close',
                'EXTRA 0.200m BOX, not original RM CAD | mouse: orbit/zoom',
            ]
            with view.lock():
                data.qpos[:]=q;data.qvel[:]=0.;data.time=min(play_t,float(record['time'][-1]))
                # Forward kinematics/cache only; never integrate or run a controller.
                mujoco.mj_forward(model,data)
                view.user_scn.ngeom=len(messages)
                for k,text in enumerate(messages):
                    geom=view.user_scn.geoms[k]
                    mujoco.mjv_initGeom(geom,mujoco.mjtGeom.mjGEOM_LABEL,np.zeros(3),np.array([.25,0.,1.00+.10*(len(messages)-k)]),np.eye(3).ravel(),np.array([1.,.92,.55,1.]))
                    geom.label=text[:99]
            view.sync()
            time.sleep(1/90.)
    print('J200_REPLAY_CLOSED mj_step_calls=0; no case/result/trace overwritten',flush=True)


if __name__=='__main__':main()
