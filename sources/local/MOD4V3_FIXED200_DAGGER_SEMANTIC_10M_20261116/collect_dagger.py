"""Bounded DAgger: unchanged native teacher takes over exact live student states.
Student prefix uses only student actions; sensors/estimator run passively.
Historical collector RESULTS used student speed-history scoring in error.
Use stored ADMISSION.json from reassess_admission.py for teacher dataset entry.
No teacher/controller/scene/PD changes, no optimizer updates.
"""
from pathlib import Path
import sys,json,math,hashlib,time,argparse,traceback
import numpy as np,torch,mujoco as mj
T=Path(__file__).resolve().parent;R=T.parents[2];F=R/'sources/local/MOD4V3_SERIAL_TEACHER_FIXED200_40M_20261116';E=R/'sources/local/MOD4V3_SERIAL_LQR_SKILL_TEACHER_20261116/equivalent_controller_v1'
sys.path.insert(0,str(E))
from native_runtime import NativeTeacher,PPO_TO_NATIVE,G
from play_ppo_flatv1 import ActorMLP
PROFILE=json.loads((E/'forward_capture_repair_20261116/CANDIDATE_PROFILE.json').read_text())
STATE=mj.mjtState.mjSTATE_INTEGRATION
MODE=np.array([0,1,0,0,0,1,0],np.float32)
torch.set_num_threads(1)
def put(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def setup(dest,mm):
 t=NativeTeacher(dest,height=.2,start_x=mm/1000,length=PROFILE['length'])
 c=t.controller;c.native_contact_history=PROFILE['native_contact_history'];c.native_encoder_rates=PROFILE['native_encoder_rates'];c.native_blocked_wheel_reference=PROFILE['blocked_wheel_reference'];c.native_capture_coherent_handoff=PROFILE['capture_coherent_handoff'];c.native_capture_stop_anchor=PROFILE['capture_stop_anchor'];c.step_climb.native_capture_loaded_hold=PROFILE['capture_loaded_hold'];c.step_climb.native_prelift_geometry_gate=PROFILE['prelift_geometry_gate'];t.surface_observer.contact_hysteresis=PROFILE['contact_geometry_hysteresis']
 return t

def observation(t,previous,v,height):
 q=t.d.qpos[t.qa][PPO_TO_NATIVE].copy();q[:4]-=t.default[PPO_TO_NATIVE[:4]];q[4:]=0.
 return np.r_[[v,0.,0.,height*5.],t.d.qvel[3:6]*.5,t.d.xmat[t.env.base_id].reshape(3,3).T@np.array([0.,0.,-1.]),q,t.d.qvel[t.va][PPO_TO_NATIVE]*.1,previous,MODE].astype(np.float32)
def fullstate(t):
 a=np.empty(mj.mj_stateSize(t.m,STATE));mj.mj_getState(t.m,t.d,a,STATE);return a

def student_step(t,actor,previous,k):
 v=.47 if k>=50 else 0.;obs=observation(t,previous,v,.4091)
 with torch.inference_mode():a=actor(torch.from_numpy(obs).reshape(1,35))[0].clamp(-6,6).numpy().copy()
 # Passive sensors/state estimator only; never call controller.step in prefix.
 G.set_context(t.m,t.d);axes=(v/t.controller.reference_governor.max_speed,0.,0.,False)
 state=t.controller._read_sensors(axes);lqr=t.controller.build_lqr_state(state)
 t.controller._update_navigation(axes,state['yaw_continuous'],float(lqr[0,0]));t.controller.last_state=state;t.controller.last_x_lqr=lqr;t.controller.last_sim_time=t.d.time
 native=torch.from_numpy(a[PPO_TO_NATIVE]).reshape(1,6)
 for j in range(8):
  tau=t.env._torque(native).numpy().reshape(-1)
  if j%4==0:t.d.ctrl[t.env.act_ids[:4]]=tau[:4]
  t.d.ctrl[t.env.act_ids[4:]]=tau[4:];mj.mj_step(t.m,t.d);t.surface_observer.observe_substep()
 t.controller.previous_motor_ctrl[:]=t.d.ctrl[t.env.act_ids]
 return obs,a

def read_features(t):
 _,top,edge,guide=t.contacts();rpy=t.euler();wheel=t.d.geom_xpos[t.tire]
 return np.r_[t.d.time,t.d.qpos[:3],rpy,t.d.qvel[:3],np.linalg.norm(t.d.qvel[:2]),edge,top,guide,wheel.reshape(-1)]

def baseline(model,mm):
 dest=T/'dagger'/model.stem/f'start_{mm:+04d}mm'/'student_capture';path=dest/'CAPTURE.json'
 if path.exists():return json.loads(path.read_text())
 dest.mkdir(parents=True,exist_ok=False);ck=torch.load(model,map_location='cpu',weights_only=False);actor=ActorMLP();actor.load_state_dict(ck['actor_state_dict'],strict=False);actor.eval();t=setup(dest,mm);previous=np.zeros(6,np.float32)
 states=[];features=[];xs=[];ys=[];qs=[];vs=[];ctrl=[];mem=[]
 for k in range(500):
  states.append(fullstate(t));features.append(read_features(t));vs.append(t.d.qvel.copy());ctrl.append(t.d.ctrl.copy());mem.append(previous.copy())
  x,a=student_step(t,actor,previous,k);xs.append(x);ys.append(a);qs.append(t.d.qpos.copy());previous=a
  if not np.isfinite(t.d.qpos).all() or not np.isfinite(t.d.qvel).all():break
 z=np.asarray(features);obs=np.asarray(xs);contact=np.flatnonzero((z[:,11]>0)|(z[:,12]>0)|(z[:,15]>5))
 assert len(contact),'No real wheel/guide stair contact in frozen student rollout'
 first=int(contact[0]);high=int(np.flatnonzero(z[:,1]>=1.)[0]);window=np.arange(max(high,first-8),min(len(z),first+13));pitched=int(window[np.argmax(np.abs(z[window,5]))])
 # Keep three distinct live states, with pitch state at/near actual contact.
 if pitched in [high,first]:
  options=[int(i)for i in window if i not in [high,first]];pitched=max(options,key=lambda i:abs(z[i,5]))
 nodes={'high_wheel_speed_approach':high,'first_wall_contact':first,'pitched_wall_state':pitched}
 old=np.load(F/'evidence/checkpoint_evals'/model.stem/f'single_step/start_{mm:+04d}mm/rollout.npz')
 same=bool(np.array_equal(np.asarray(qs),old['qpos'])and np.array_equal(obs,old['obs'])and np.array_equal(np.asarray(ys),old['actions']))
 np.savez_compressed(dest/'capture.npz',integration_state=np.asarray(states),qpos_post=np.asarray(qs),qvel_pre=np.asarray(vs),ctrl_pre=np.asarray(ctrl),previous_action=np.asarray(mem),obs=obs,actions=np.asarray(ys),features=z)
 result=dict(model=str(model),sha256=sha(model),start_offset_mm=mm,frames=len(xs),nodes=nodes,first_real_stair_contact_frame=first,identical_to_archived_student_rollout=same,student_prefix_teacher_actions=0,passive_state_estimation_only=True,full_mujoco_state_type='mjSTATE_INTEGRATION',optimizer_updates=0,node_features={n:dict(frame=i,time_s=float(z[i,0]),root_x=float(z[i,1]),root_z=float(z[i,3]),pitch_deg=math.degrees(float(z[i,5])),speed_m_s=float(z[i,10]),wheel_velocity_observation=obs[i,20:22].tolist(),edge=z[i,11:13].astype(bool).tolist())for n,i in nodes.items()})
 put(path,result);print('CAPTURE',model.stem,mm,'same_as_archive',same,'nodes',nodes,flush=True)
 assert same,'Passive observation changed student dynamics; retain and inspect'
 return result

def takeover(model,mm,name,frame,capture):
 dest=T/'dagger'/model.stem/f'start_{mm:+04d}mm'/name;path=dest/'RESULT.json'
 if path.exists():return json.loads(path.read_text())
 dest.mkdir(parents=True,exist_ok=False);started=time.perf_counter();ck=torch.load(model,map_location='cpu',weights_only=False);actor=ActorMLP();actor.load_state_dict(ck['actor_state_dict'],strict=False);actor.eval();t=setup(dest,mm);previous=np.zeros(6,np.float32)
 pre_entry=None;max_approach=0.
 for k in range(frame):
  speed=float(np.linalg.norm(t.d.qvel[:2]));x,a=student_step(t,actor,previous,k);previous=a
  _,_,edge,guide=t.contacts()
  if pre_entry is None and(edge.any()or guide>5.):pre_entry=speed
  near=bool(np.min(np.abs(t.d.geom_xpos[t.tire,0]-1.2))<.45)
  if near or pre_entry is not None:max_approach=max(max_approach,float(np.linalg.norm(t.d.qvel[:2])))
 expected=np.load(T/'dagger'/model.stem/f'start_{mm:+04d}mm/student_capture/capture.npz')
 actual_state=fullstate(t);exact=bool(np.array_equal(actual_state,expected['integration_state'][frame]));assert exact,'Live takeover prefix differs'
 handoff=dict(identical_integration_state=True,frame=frame,time_s=float(t.d.time),qpos=t.d.qpos.tolist(),qvel=t.d.qvel.tolist(),ctrl=t.d.ctrl.tolist(),previous_action=previous.tolist(),student_height_command_m=.4091,teacher_height_command_m=float(t.controller.target_leg_length_command)+.0625,odometry=t.controller.body_odom.state.tolist(),wheel_support_confirmed=t.controller._wheel_support_confirmed.tolist(),wheel_torque_scale=t.controller._wheel_torque_scale.tolist(),contact_latch=t.surface_observer.contact_latch.snapshot(),current_pitch_deg=math.degrees(float(t.euler()[1])),observer_edge_detected=t.surface_observer.edge is not None,student_prefix_teacher_actions=0,policy_boundary_handoff=True,no_physical_state_reset=True)
 put(dest/'HANDOFF.json',handoff)
 xs=[];ys=[];qs=[];vs=[];phases=[];features=[];heights=[];states=[];preqs=[];hold=best=0.;stop=False;entry=pre_entry;error=None;reason='timeout';contact_frame=None;first_lift=None;previous_phase='idle';teacher_calls=0
 try:
  for j in range(500-frame):
   v=0. if stop else .47;height=float(t.controller.target_leg_length_command)+.0625;x=observation(t,previous,v,height);preqs.append(t.d.qpos.copy());states.append(fullstate(t));pre_speed=float(np.linalg.norm(t.d.qvel[:2]))
   diag=t.step((v/t.controller.reference_governor.max_speed,0.,0.,False));teacher_calls+=1;a=diag['action'][PPO_TO_NATIVE].astype(np.float32);phase=t.controller.step_climb.phase
   ground,top,edge,guide=t.contacts();rpy=t.euler();wheel=t.d.geom_xpos[t.tire];speed=float(np.linalg.norm(t.d.qvel[:2]))
   if edge.any()or guide>5.:
    if contact_frame is None:contact_frame=j
    if entry is None:entry=pre_speed
   if phase=='lift'and first_lift is None:first_lift=j
   if np.min(np.abs(wheel[:,0]-1.2))<.45 or entry is not None:max_approach=max(max_approach,speed)
   crossed=bool(top.all()and t.d.qpos[0]>1.23 and np.all(wheel[:,0]>1.225))
   stable=bool(crossed and max(abs(rpy[0]),abs(rpy[1]))<math.radians(25)and np.linalg.norm(t.d.qvel[3:6])<1.5 and abs(t.d.qvel[2])<.25 and speed<=.6 and entry is not None and .1<=entry<=.6 and max_approach<=.6)
   hold=hold+.02 if stable else 0.;best=max(best,hold)
   # Same teacher evaluator: release after completion when Cartesian state exits.
   if crossed and phase=='idle':stop=True
   xs.append(x);ys.append(a);qs.append(t.d.qpos.copy());vs.append(t.d.qvel.copy());phases.append(phase);heights.append(height);features.append(np.r_[read_features(t),hold,best,t.closure_peak])
   previous=a
   if max(abs(rpy[0]),abs(rpy[1]))>1.2:reason='tilt_above68deg';break
   if t.d.qpos[2]<.11:reason='fell_below_ground';break
   if abs(t.d.qpos[0])>3.05 or abs(t.d.qpos[1])>1.3:reason='left_scene';break
 except Exception:error=traceback.format_exc();reason='exception'
 z=np.asarray(features);success=bool(error is None and hold>=.4-1e-7 and best>=.4-1e-7)
 if success:reason='qualified_stable_final_top_support'
 result=dict(model=model.stem,model_sha256=capture['sha256'],start_offset_mm=mm,node=name,takeover_frame=frame,takeover_pitch_deg=handoff['current_pitch_deg'],qualified=success,reason=reason,frames=len(xs),first_contact_correction_frame=contact_frame,first_lift_correction_frame=first_lift,entry_speed_m_s=entry,maximum_entry_ascent_speed_m_s=max_approach,max_continuous_top_hold_s=best,final_continuous_top_hold_s=hold,pitch_peak_deg=float(np.rad2deg(np.abs(z[:,5])).max())if len(z)else None,teacher_control_calls=teacher_calls,student_prefix_teacher_actions=0,student_score=False,optimizer_updates=0,teacher_profile_unchanged=True,error=error,wall_seconds=time.perf_counter()-started)
 np.savez_compressed(dest/'correction.npz',obs=np.asarray(xs,np.float32),actions=np.asarray(ys,np.float32),qpos=np.asarray(qs),pre_qpos=np.asarray(preqs),qvel=np.asarray(vs),phases=np.asarray(phases),root_height_cmd=np.asarray(heights),features=z,integration_state=np.asarray(states))
 put(path,result);print('DAGGER',model.stem,mm,name,'qualified',success,'hold',round(best,3),'peak',result['pitch_peak_deg'],'maxspeed',round(max_approach,3),flush=True)
 return result

def main():
 p=argparse.ArgumentParser();p.add_argument('--offsets',nargs='+',type=int,default=[-60,-30,0,30,60]);p.add_argument('--models',nargs='+',default=['model_035m','model_040m']);a=p.parse_args();rows=[];started=time.time()
 index=json.loads((F/'teacher_snapshot/SOURCE_INDEX.json').read_text())
 for row in index['files']:assert sha(Path(row['path']))==row['sha256'],'Teacher source changed'
 for model_name in a.models:
  model=F/'weights'/(model_name+'.pt')
  for mm in a.offsets:
   capture=baseline(model,mm)
   for name,frame in capture['nodes'].items():rows.append(takeover(model,mm,name,frame,capture))
 report=dict(attempts=len(rows),qualified=sum(x['qualified']for x in rows),failed=sum(not x['qualified']for x in rows),rows=rows,wall_seconds=time.time()-started,max_authorized_attempts=30,no_optimizer_updates=True,teacher_profile_sha256=sha(E/'forward_capture_repair_20261116/CANDIDATE_PROFILE.json'))
 put(T/'dagger/COLLECTION.json',report)
 print('COLLECTION_TOTAL',report['qualified'],'/',report['attempts'],flush=True)
if __name__=='__main__':main()
