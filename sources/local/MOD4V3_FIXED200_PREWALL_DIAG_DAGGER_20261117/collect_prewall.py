"""Live same-simulation pre-wall DAgger; unchanged native teacher, no PPO.
No contact prerequisite. Student prefix matches archived closed-loop rollout.
No time/qpos/qvel/ctrl reset occurs at handoff. Failed attempts are retained.
"""
from common import *
import math,time,traceback,argparse
NODES={'command_onset':50,'command_plus60ms':53,'before_crouch':60}

def main_entry(t):
 hit=False
 for j in range(t.d.ncon):
  c=t.d.contact[j];g1,g2=int(c.geom1),int(c.geom2)
  if t.platform not in(g1,g2):continue
  other=g2 if g1==t.platform else g1
  if t.m.geom_bodyid[other]not in t.wheels:continue
  f=np.zeros(6);mj.mj_contactForce(t.m,t.d,j,f)
  hit|=f[0]>5.
 return hit

def capture(actor,tag,mm):
 dest=T/f'dagger/{tag}/start_{mm:+04d}mm/student_capture';dest.mkdir(parents=True,exist_ok=False)
 t=setup(dest,mm);prev=np.zeros(6,np.float32);states=[];xs=[];ys=[];preqs=[];postqs=[];vels=[];ft=[]
 for k in range(max(NODES.values())+1):
  states.append(fullstate(t));preqs.append(t.d.qpos.copy());vels.append(t.d.qvel.copy());ft.append(read_features(t))
  o,a=student_step(t,actor,prev,k);xs.append(o);ys.append(a);postqs.append(t.d.qpos.copy());prev=a
 old=np.load(P/f'evidence/checkpoint_evals/{tag}/single_step/start_{mm:+04d}mm/rollout.npz')
 same=dict(qpos=bool(np.array_equal(postqs,old['qpos'][:len(xs)])),obs=bool(np.array_equal(xs,old['obs'][:len(xs)])),actions=bool(np.array_equal(ys,old['actions'][:len(xs)])))
 np.savez_compressed(dest/'capture.npz',integration_state=np.asarray(states),pre_qpos=np.asarray(preqs),qvel_pre=np.asarray(vels),qpos_post=np.asarray(postqs),obs=np.asarray(xs),actions=np.asarray(ys),features=np.asarray(ft))
 put(dest/'CAPTURE.json',dict(model=tag,start_offset_mm=mm,frames=len(xs),identical_to_archive=same,teacher_actions_in_prefix=0,no_physical_state_reset=True,optimizer_updates=0,nodes=NODES))
 assert all(same.values()),'Prefix differs from archived rollout: '+repr(same)
 return dest

def attempt(actor,model,tag,mm,name,frame,cap):
 dest=T/f'dagger/{tag}/start_{mm:+04d}mm/{name}';dest.mkdir(parents=True,exist_ok=False);t=setup(dest,mm);prev=np.zeros(6,np.float32)
 started=time.perf_counter()
 for k in range(frame):o,a=student_step(t,actor,prev,k);prev=a
 expected=np.load(cap/'capture.npz');state=fullstate(t);same=bool(np.array_equal(state,expected['integration_state'][frame]));assert same,'Live prefix integration state mismatch'
 assert t.d.qpos[0]<.8 and t.d.time<1.3,'Not a pre-wall start'
 ground,top,edge,guide=t.contacts();assert not(edge.any()or guide>5.),'Unexpected stair contact before handoff'
 handoff=dict(frame=frame,pre_action_time_s=float(t.d.time),qpos=t.d.qpos.tolist(),qvel=t.d.qvel.tolist(),ctrl=t.d.ctrl.tolist(),previous_action=prev.tolist(),obs35=observation(t,prev,.47,.4091).tolist(),root_xyz=t.d.qpos[:3].tolist(),real_step_contact=False,identical_integration_state=same,no_physical_state_reset=True,teacher_actions_in_prefix=0,student_model=str(model),model_sha256=sha(model),controller_target_leg_length_command=float(t.controller.target_leg_length_command),wheel_support_confirmed=t.controller._wheel_support_confirmed.tolist(),body_odom=t.controller.body_odom.state.tolist())
 put(dest/'HANDOFF.json',handoff)
 xs=[];ys=[];qs=[];preqs=[];vels=[];ph=[];ft=[];states=[];hcmd=[];hold=best=0.;entry=None;firstguide=None;firstmain=None;firstlift=None;stop=False;err=None;reason='timeout';maxnear=0.
 for j in range(500-frame):
  try:
   v=0. if stop else .47;height=float(t.controller.target_leg_length_command)+.0625
   o=observation(t,prev,v,height);xs.append(o);preqs.append(t.d.qpos.copy());states.append(fullstate(t));hcmd.append(height);pre_speed=float(np.linalg.norm(t.d.qvel[:2]))
   # NativeTeacher.step is the frozen original, with no wrapper gain/state patch.
   diag=t.step((v/t.controller.reference_governor.max_speed,0.,0.,False));a=diag['action'][PPO_TO_NATIVE].astype(np.float32);phase=t.controller.step_climb.phase
   ground,top,edge,guide=t.contacts();rpy=t.euler();speed=float(np.linalg.norm(t.d.qvel[:2]));wheel=t.d.geom_xpos[t.tire]
   if (edge.any()or guide>5.)and firstguide is None:firstguide=j
   if main_entry(t)and entry is None:entry=pre_speed;firstmain=j
   if phase=='lift'and firstlift is None:firstlift=j
   if np.min(np.abs(wheel[:,0]-1.2))<.45 or entry is not None:maxnear=max(maxnear,speed)
   stable=bool(top.all()and t.d.qpos[0]>1.23 and abs(rpy[0])<.35 and abs(rpy[1])<.35 and speed<.6)
   hold=hold+.02 if stable else 0.;best=max(best,hold)
   if top.all()and t.d.qpos[0]>1.23 and phase=='idle':stop=True
   ys.append(a);qs.append(t.d.qpos.copy());vels.append(t.d.qvel.copy());ph.append(phase);ft.append(np.r_[read_features(t),hold,best,t.closure_peak]);prev=a
   if not(np.isfinite(t.d.qpos).all()and np.isfinite(t.d.qvel).all()):reason='nonfinite';break
   if t.closure_peak>1.:reason='catastrophic_closure_above1m';break
   if max(abs(rpy[0]),abs(rpy[1]))>1.2:reason='tilt_above68deg';break
   if t.d.qpos[2]<.11:reason='fell_below_ground';break
   if abs(t.d.qpos[0])>3.05 or abs(t.d.qpos[1])>1.3:reason='left_scene';break
  except Exception:err=traceback.format_exc();reason='exception';break
 n=len(ys);xs=xs[:n];preqs=preqs[:n];states=states[:n];hcmd=hcmd[:n];z=np.asarray(ft)
 physical=bool(err is None and n and hold>=.4-1e-7 and z[-1,13]and z[-1,14]);entryok=bool(entry is not None and .1<=entry<=.6);qualified=physical and entryok
 if qualified:reason='native_final_stable0.4s_and_low_entry'
 elif physical:reason='physical_stable_but_entry_out_of_range'
 result=dict(model=tag,model_sha256=sha(model),start_offset_mm=mm,node=name,takeover_frame=frame,qualified=qualified,reason=reason,physical_native_stable_final=physical,low_entry_qualified=entryok,entry_speed_m_s=entry,maximum_entry_ascent_speed_m_s=maxnear,max_continuous_top_hold_s=best,final_continuous_top_hold_s=hold,first_guide_or_edge_frame=firstguide,first_main_wheel_contact_frame=firstmain,first_teacher_lift_frame=firstlift,teacher_lift_before_real_contact=bool(firstlift is not None and(firstguide is None or firstlift<firstguide)),frames=n,pitch_peak_deg=float(np.rad2deg(abs(z[:,5])).max())if n else None,prewall_min_root_z=float(z[z[:,1]<.8,3].min())if n and np.any(z[:,1]<.8)else None,teacher_calls=n,student_score=False,teacher_profile_unchanged=True,optimizer_updates=0,PPO_updates=0,error=err,wall_seconds=time.perf_counter()-started,admission_protocol='NATIVE_STABLE_TOP_0P4_PLUS_MAIN_WHEEL_ENTRY_0P1_TO_0P6',historical_student_speed_veto=False)
 np.savez_compressed(dest/'correction.npz',obs=np.asarray(xs,np.float32),actions=np.asarray(ys,np.float32),qpos=np.asarray(qs),pre_qpos=np.asarray(preqs),qvel=np.asarray(vels),phases=np.asarray(ph),root_height_cmd=np.asarray(hcmd),features=z,integration_state=np.asarray(states))
 put(dest/'RESULT.json',result)
 print('PREWALL_DAGGER',tag,mm,name,'qualified',qualified,'entry',round(entry,4)if entry is not None else None,'hold',round(best,2),'reason',reason,flush=True)
 return result

def main():
 p=argparse.ArgumentParser();p.add_argument('--offsets',nargs='+',type=int,default=[-60,-30,0,30,60]);args=p.parse_args();guard();rows=[];started=time.perf_counter()
 for tag in ['model_005m','model_010m']:
  model=P/f'weights/{tag}.pt';actor,ck=actor_load(model)
  for mm in args.offsets:
   cap=T/f'dagger/{tag}/start_{mm:+04d}mm/student_capture'
   if not(cap/'CAPTURE.json').exists():capture(actor,tag,mm)
   else:assert all(json.loads((cap/'CAPTURE.json').read_text())['identical_to_archive'].values())
   for name,frame in NODES.items():
    dest=T/f'dagger/{tag}/start_{mm:+04d}mm/{name}/RESULT.json'
    rows.append(json.loads(dest.read_text())if dest.exists()else attempt(actor,model,tag,mm,name,frame,cap))
   put(T/'dagger/COLLECTION_PROGRESS.json',dict(attempts=len(rows),qualified=sum(x['qualified']for x in rows),rows=rows,PPO_updates=0,wall_seconds=time.perf_counter()-started))
 guard();summary_name='COLLECTION.json' if args.offsets==[-60,-30,0,30,60] else 'COLLECTION_offsets_'+('_'.join(f'{x:+04d}' for x in args.offsets))+'.json';put(T/'dagger'/summary_name,dict(attempts=len(rows),qualified=sum(x['qualified']for x in rows),failed=sum(not x['qualified']for x in rows),qualified_frames=sum(x['frames']for x in rows if x['qualified']),rows=rows,PPO_updates=0,optimizer_updates=0,wall_seconds=time.perf_counter()-started))
if __name__=='__main__':main()
