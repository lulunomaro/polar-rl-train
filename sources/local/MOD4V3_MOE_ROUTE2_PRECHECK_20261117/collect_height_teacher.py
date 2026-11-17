"""New task-height demonstrations from the unchanged native LQR/VMC teacher."""
from pathlib import Path
import sys,json,time,math,hashlib
import numpy as np,torch,mujoco as mj
T=Path(__file__).resolve().parent;R=T.parents[2];E=R/'sources/local/MOD4V3_SERIAL_LQR_SKILL_TEACHER_20261116/equivalent_controller_v1';sys.path.insert(0,str(E))
from native_runtime import NativeTeacher,PPO_TO_NATIVE
PROFILE=json.loads((E/'forward_capture_repair_20261116/CANDIDATE_PROFILE.json').read_text());MODE=np.array([0,1,0,0,0,1,0],np.float32);OUT=T/'local_probes/teacher_height_pool';OUT.mkdir(exist_ok=False);rows=[];torch.set_num_threads(1)
def observation(t,prev,v):
 q=t.d.qpos[t.qa][PPO_TO_NATIVE].copy();q[:4]-=t.default[PPO_TO_NATIVE[:4]];q[4:]=0.;height=float(t.controller.target_leg_length_command)+.0625
 return np.r_[[v,0,0,height*5],t.d.qvel[3:6]*.5,t.d.xmat[t.env.base_id].reshape(3,3).T@np.array([0,0,-1]),q,t.d.qvel[t.va][PPO_TO_NATIVE]*.1,prev,MODE].astype(np.float32)
def run(name,h,heightcmd):
 dest=OUT/name;dest.mkdir();t=NativeTeacher(dest,height=h,length=heightcmd-.0625);c=t.controller;c.native_contact_history=PROFILE['native_contact_history'];c.native_encoder_rates=PROFILE['native_encoder_rates'];c.native_blocked_wheel_reference=PROFILE['blocked_wheel_reference'];c.native_capture_coherent_handoff=PROFILE['capture_coherent_handoff'];c.native_capture_stop_anchor=PROFILE['capture_stop_anchor'];c.step_climb.native_capture_loaded_hold=PROFILE['capture_loaded_hold'];c.step_climb.native_prelift_geometry_gate=PROFILE['prelift_geometry_gate'];t.surface_observer.contact_hysteresis=PROFILE['contact_geometry_hysteresis']
 prev=np.zeros(6,np.float32);history=[];xs=[];ys=[];hs=[];targets=[];phases=[];sem=[];tr=[];qpos=[];hold=best=0.;entry=None;stop=False;touch=False;landed=False;peak=0.;stand_start=float(t.d.qpos[0]);stand_end=None
 for k in range(500 if h else 200):
  v=.47 if k>=50 and not stop else 0.;x=observation(t,prev,v);history.append(x);hs.append(np.asarray([history[max(0,len(history)-12+i)]for i in range(12)],np.float32));xs.append(x);speed_before=float(np.linalg.norm(t.d.qvel[:2]));ground,top,edge,guide=t.contacts();targets.append(np.r_[t.d.xmat[t.env.base_id].reshape(3,3).T@t.d.qvel[:3],(ground|edge|top).astype(float)])
  diag=t.step((v/c.reference_governor.max_speed,0.,0.,False));a=diag['action'][PPO_TO_NATIVE].astype(np.float32);ground,top,edge,guide=t.contacts();rpy=t.euler();speed=float(np.linalg.norm(t.d.qvel[:2]));wheel=t.d.geom_xpos[t.tire];phase=c.step_climb.phase;peak=max(peak,abs(float(rpy[1])))
  if k==49:stand_end=float(t.d.qpos[0])-stand_start
  if entry is None and edge.any():entry=speed_before
  touch|=bool(edge.any()or guide>5.);crossed=bool(h and top.all()and t.d.qpos[0]>1.23 and np.all(wheel[:,0]>1.225));landed|=crossed;stable=bool(crossed and max(abs(rpy[0]),abs(rpy[1]))<math.radians(25)and speed<=.6);hold=hold+.02 if stable else 0.;best=max(best,hold)
  if crossed and phase=='idle':stop=True
  sid={'lift':4,'swing':5,'plant':6,'capture':7}.get(phase,8 if landed else 3 if touch else 0 if k<50 else 1 if h==0 else 2)
  ys.append(a);sem.append(sid);phases.append(phase);qpos.append(t.d.qpos.copy());tr.append([t.d.time,*t.d.qpos[:3],speed,math.degrees(rpy[1]),math.degrees(rpy[0]),hold,float(crossed)]);prev=a
  if abs(rpy[0])>1.2 or abs(rpy[1])>1.2 or t.d.qpos[2]<.11:break
 qualified=bool(hold>=.4-1e-7 and entry is not None and .1<=entry<=.6 and peak<math.radians(25))if h else bool(abs(stand_end or 0)<.025 and peak<math.radians(15)and len(xs)==200 and abs(float(t.d.qvel[0])-.47)<.15)
 n=len(ys);np.savez_compressed(dest/'trajectory.npz',obs=np.asarray(xs[:n],np.float32),actions=np.asarray(ys,np.float32),history=np.asarray(hs[:n],np.float32),targets=np.asarray(targets[:n],np.float32),semantic_id=np.asarray(sem,np.int64),qpos=np.asarray(qpos),trace=np.asarray(tr),phases=np.asarray(phases))
 row=dict(name=name,height_m=h,commanded_height_m=heightcmd,qualified=qualified,frames=n,entry_speed=entry,physical_crossed=landed,final_stable_s=hold,max_stable_s=best,peak_pitch_deg=math.degrees(peak),pre1s_displacement_m=stand_end,teacher_score_only=True,PPO_updates=0,teacher_source_unmodified=True);(dest/'RESULT.json').write_text(json.dumps(row,indent=2)+'\n');print('TEACHER_HEIGHT',json.dumps(row),flush=True);return row
start=time.perf_counter()
for h in [.10,.14,.17,.20]:rows.append(run(f'step{round(h*1000):03d}',h,h+.2091))
for h in [.28,.35,.4091]:rows.append(run(f'flat{round(h*1000):03d}',0.,h))
(OUT/'COLLECTION.json').write_text(json.dumps(dict(rows=rows,qualified=sum(r['qualified']for r in rows),wall_seconds=time.perf_counter()-start,PPO_updates=0),indent=2)+'\n')
