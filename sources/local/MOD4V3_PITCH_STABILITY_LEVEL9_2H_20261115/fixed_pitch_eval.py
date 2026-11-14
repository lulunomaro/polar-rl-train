"""Fixed nominal IMU pitch comparison on existing official level9 rough and plane."""
from pathlib import Path
import argparse,json,hashlib,sys,importlib.util,types,time,gc
import numpy as np
import torch,mujoco
p=argparse.ArgumentParser();p.add_argument('--model',required=True);p.add_argument('--out',required=True);a=p.parse_args();torch.set_num_threads(1)
T=Path(__file__).resolve().parent;R=T.parents[2];D=R/'deliveries/MOD4V3_BEST_MANUAL_STAIRS_20261112';E=Path(a.out).resolve();E.mkdir(parents=True,exist_ok=False);B=E/'scene_assets';(B/'tiles').mkdir(parents=True)
spec=importlib.util.spec_from_file_location('pitch_fixed_show',D/'viewer/showcase.py');show=importlib.util.module_from_spec(spec);spec.loader.exec_module(show)
for level,family in [(9,'random_uniform_for_rm'),(0,'plane_for_rm')]:
 col=show.COLS[family];name=f'r{level:02d}_c{col:02d}.npz';(B/'tiles'/name).write_bytes((D/'viewer/tiles'/name).read_bytes())
show.B=B;show.CKPT=Path(a.model).resolve();show.EXPECTED=hashlib.sha256(show.CKPT.read_bytes()).hexdigest()
sys.path.insert(0,str(T/'manual_replay'));from replay_supported_guards import replay_step
show.Replay.step=replay_step(show.Simulation,show.SafetyStop,duration_steps=10,event_dir=E/'reset_events')
rows=[];arrays={};wall=time.time()
for family,level in [('random_uniform_for_rm',9),('plane_for_rm',0)]:
 for height in [.28,.40]:
  for speed in [1.2,2.2]:
   s=show.Replay(level=level,family=family,direction='up');e=s.env;m=e.m;d=e.d
   x0=-.8;y0=-.1 if speed<2. else .1
   d.qpos[:3]=[x0,y0,s.ground(x0,y0)+e.bank_z];d.qpos[3:7]=[1.,0.,0.,0.];d.qvel[:]=0.;mujoco.mj_forward(m,d);e.state();s.reset_count=1;s.reason='';maxclosure=0.
   def physics(env,act):
    global maxclosure
    act=act.clamp(-env.action_clip,env.action_clip)
    for j in range(env.decim):
     tau=env._torque(act).detach().numpy().reshape(-1)
     if j%4==0:d.ctrl[env.act_ids[:4]]=tau[:4]
     d.ctrl[env.act_ids[4:]]=tau[4:];mujoco.mj_step(m,d)
     if not np.isfinite(d.qpos).all() or not np.isfinite(d.qvel).all():raise show.SafetyStop('nonfinite')
     cl=max(float(np.linalg.norm(d.site_xpos[u]-d.site_xpos[v]))for u,v in s.pairs);s.closure=cl;maxclosure=max(maxclosure,cl)
     if cl>.002:raise show.SafetyStop('closure>2mm')
    env.a_prev=act.detach().to(env.device);return env.state()
   e.step=types.MethodType(physics,e);trace=[]
   try:
    for k in range(700):
     age=k*.02;elapsed=max(0.,age-2.);leg=int(elapsed//3.);phase=elapsed%3.;moving=age>=2. and phase<1.
     vx=speed*(1. if leg%2==0 else -1.)if moving else 0.
     s.args.vx=speed;s.cmd_vx=vx;s.cmd_vy=0.;s.cmd_wz=0.;s.set_height(height)
     pressed={'w'}if vx>0 else {'s'}if vx<0 else set();s.step(pressed)
     rotation=np.asarray(d.xmat[e.base_id]).reshape(3,3);gravity=rotation.T@np.array([0.,0.,-1.]);pitch=float(np.arctan2(gravity[0],np.linalg.norm(gravity[1:])))
     velocity=np.zeros(6);mujoco.mj_objectVelocity(m,d,mujoco.mjtObj.mjOBJ_BODY,e.base_id,velocity,1)
     trace.append([age,pitch,float(velocity[1]),vx,float(e.vx),float(d.qpos[0]),float(d.qpos[2]),s.closure,float(s.reset_count-1),float(moving),phase])
     if s.reset_count>1:break
    arr=np.asarray(trace);window=arr[:,0]>=2.;startup=window&(arr[:,9]>.5)&(arr[:,10]<.8);braking=window&(arr[:,9]<.5)&(arr[:,10]>=1.)&(arr[:,10]<1.8)
    def peak(mask):return float(np.degrees(np.abs(arr[mask,1])).max())if mask.any()else None
    row=dict(family=family,level=level,height=height,speed=speed,resets=s.reset_count-1,reason=s.reason,completed_s=float(arr[-1,0]),pitch_RMS_deg=float(np.degrees(np.sqrt(np.mean(arr[window,1]**2))))if window.any()else None,pitch_rate_RMS_rad_s=float(np.sqrt(np.mean(arr[window,2]**2)))if window.any()else None,startup_peak_deg=peak(startup),braking_peak_deg=peak(braking),moving_vx_MAE=float(np.mean(np.abs(arr[startup,4]-arr[startup,3])))if startup.any()else None,max_closure_m=maxclosure)
    rows.append(row);arrays[family+f'_h{height}_v{speed}']=arr;(E/'PROGRESS.json').write_text(json.dumps(dict(completed=len(rows),last=row)))
   finally:s.close();del s,e,m,d;gc.collect()
summary={}
for fam in ['random_uniform_for_rm','plane_for_rm']:
 group=[r for r in rows if r['family']==fam];valid=[r for r in group if r['pitch_RMS_deg']is not None]
 summary[fam]=dict(cases=len(group),completed_without_reset=sum(r['resets']==0 and r['completed_s']>=13.9 for r in group),pitch_RMS_deg_mean=float(np.mean([r['pitch_RMS_deg']for r in valid]))if valid else None,startup_peak_deg_max=max((r['startup_peak_deg']for r in valid if r['startup_peak_deg']is not None),default=None),braking_peak_deg_max=max((r['braking_peak_deg']for r in valid if r['braking_peak_deg']is not None),default=None),moving_vx_MAE_mean=float(np.mean([r['moving_vx_MAE']for r in valid if r['moving_vx_MAE']is not None]))if valid else None)
np.savez_compressed(E/'trajectory.npz',**arrays)
result=dict(model=str(show.CKPT),sha256=show.EXPECTED,rows=rows,summary=summary,wall_seconds=time.time()-wall,no_optimizer=True,protocol='Existing official random_uniform level9 and plane0;2heights0.28/0.40 x2speeds1.2/2.2;14s;stand2s then1s hard run/2s hard stop,alternating direction;actual gravity body pitch and local body omega_y;first episode only;nominal0ms;matched2.5ms/100Hz legs/400Hz wheels/50Hz policy;2mm guards;not fullDR graduation')
(E/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(summary=summary,wall_seconds=result['wall_seconds'])),flush=True)
