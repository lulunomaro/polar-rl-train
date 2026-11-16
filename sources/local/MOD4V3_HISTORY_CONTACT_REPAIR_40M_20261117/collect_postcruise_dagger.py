"""Frozen native teacher takes live contact states from the new history policy; no resets."""
from pathlib import Path
import sys,importlib.util,json,time,math,hashlib,traceback,collections
import numpy as np,torch,mujoco as mj
T=Path(__file__).resolve().parent;R=T.parents[2];old=R/'sources/local/MOD4V3_FIXED200_DAGGER_SEMANTIC_10M_20261116'
s=importlib.util.spec_from_file_location('frozen_native_contact_collector',old/'collect_dagger.py');f=importlib.util.module_from_spec(s);s.loader.exec_module(f)
sys.path.insert(0,str(T));from history_eval_hooks import ReplayHistoryActor
MODE=f.MODE;MODEL=T/'local_probes/gated_v1/model_fit_02000.pt';OUT=T/'contact_dagger_postcruise_v2';OUT.mkdir(exist_ok=False);torch.set_num_threads(1)
def put(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def actor():
 a=ReplayHistoryActor();a.load_state_dict(torch.load(MODEL,map_location='cpu',weights_only=False)['actor_state_dict']);a.eval();return a

def attach_force(t):
 q=collections.deque(maxlen=3);original=t.surface_observer.observe_substep
 def norm():
  force=np.zeros((2,3))
  for j in range(t.d.ncon):
   c=t.d.contact[j];v=np.zeros(6);mj.mj_contactForce(t.m,t.d,j,v);world=np.asarray(c.frame).reshape(3,3).T@v[:3]
   for i,b in enumerate(t.wheels):
    if t.m.geom_bodyid[c.geom1]==b:force[i]-=world
    if t.m.geom_bodyid[c.geom2]==b:force[i]+=world
  return np.linalg.norm(force,axis=1)
 def watch():
  original()
  if round(t.d.time/.0025)%2==0:q.append(norm())
 t.surface_observer.observe_substep=watch;q.append(norm())
 return lambda:np.max(np.asarray(q),axis=0)>5.
def capture(mm):
 dest=OUT/f'start_{mm:+04d}mm';dest.mkdir();cap=dest/'student_capture';cap.mkdir();t=f.setup(cap,mm);a=actor();prev=np.zeros(6,np.float32);states=[];obs=[];actions=[];post=[];features=[]
 for k in range(300):
  states.append(f.fullstate(t));features.append(f.read_features(t));x,y=f.student_step(t,a,prev,k);obs.append(x);actions.append(y);post.append(t.d.qpos.copy());prev=y
 z=np.asarray(features);contact=np.where((z[:,11]>0)|(z[:,12]>0)|(z[:,15]>5))[0];assert len(contact)>0;first=int(contact[0]);near=int(np.where(z[:,1]>=1.)[0][0]);nodes=dict(approach=near,first_contact=first,contact_plus100ms=min(first+5,len(z)-1));np.savez_compressed(cap/'capture.npz',integration_state=np.asarray(states),obs=np.asarray(obs),actions=np.asarray(actions),qpos_post=np.asarray(post),features=z)
 archived=np.load(T/f'local_probes/gated_v1/eval_02000/start_{mm:+04d}mm/rollout.npz');n=min(nodes.values());same=bool(np.array_equal(post[:n],archived['qpos'][:n])and np.array_equal(obs[:n],archived['obs'][:n])and np.array_equal(actions[:n],archived['actions'][:n]));assert same
 put(cap/'CAPTURE.json',dict(nodes=nodes,identical_prefix=True,teacher_control_calls=0,frames=300));return dest,nodes,np.asarray(states),np.asarray(obs)
def attempt(mm,dest,name,frame,states,prefix):
 dest=dest/name;dest.mkdir();t=f.setup(dest,mm);get_contact=attach_force(t);a=actor();prev=np.zeros(6,np.float32);entry=None
 for k in range(frame):
  speed=float(np.linalg.norm(t.d.qvel[:2]));x,y=f.student_step(t,a,prev,k);prev=y
  if entry is None and t.contacts()[2].any():entry=speed
 assert np.array_equal(f.fullstate(t),states[frame]),'Handoff physics state not identical'
 put(dest/'HANDOFF.json',dict(frame=frame,time_s=t.d.time,no_reset=True,same_integration_state=True,source=str(MODEL),student_teacher_calls=0,previous_action=prev.tolist()))
 xs=[];ys=[];hs=[];qs=[];vs=[];targets=[];ph=[];sem=[];top_before=False;top_ticks=0;touch=False;hold=best=0.;stop=False;error=None;history=list(prefix[:frame]);prestates=[];tr=[]
 try:
  for j in range(500-frame):
   v=0. if stop else .47;height=float(t.controller.target_leg_length_command)+.0625;x=f.observation(t,prev,v,height);history.append(x);hs.append(np.asarray([history[max(0,len(history)-12+i)]if len(history)>=12 else history[max(0,len(history)-12+i)]for i in range(12)],np.float32));targets.append(np.r_[t.d.xmat[t.env.base_id].reshape(3,3).T@t.d.qvel[:3],get_contact().astype(float)]);prestates.append(f.fullstate(t));speed_before=float(np.linalg.norm(t.d.qvel[:2]));xs.append(x);diag=t.step((v/t.controller.reference_governor.max_speed,0.,0.,False));y=diag['action'][f.PPO_TO_NATIVE].astype(np.float32);phase=t.controller.step_climb.phase;ground,top,edge,guide=t.contacts();rpy=t.euler();speed=float(np.linalg.norm(t.d.qvel[:2]));wheel=t.d.geom_xpos[t.tire]
   if entry is None and edge.any():entry=speed_before
   touch|=bool(edge.any()or guide>5.);crossed=bool(top.all()and t.d.qpos[0]>1.23 and np.all(wheel[:,0]>1.225));stable=bool(crossed and abs(rpy[0])<.35 and abs(rpy[1])<.35 and speed<.6);hold=hold+.02 if stable else 0.;best=max(best,hold)
   if crossed and phase=='idle':top_before=True
   if top_before:top_ticks+=1
   if top_ticks>=40:stop=True
   sid={'lift':4,'swing':5,'plant':6,'capture':7}.get(phase,8 if top_before else 3 if touch else 9);ys.append(y);qs.append(t.d.qpos.copy());vs.append(t.d.qvel.copy());ph.append(phase);sem.append(sid);tr.append(np.r_[f.read_features(t),hold,best]);prev=y
   if max(abs(rpy[0]),abs(rpy[1]))>1.2 or t.d.qpos[2]<.11 or abs(t.d.qpos[0])>3.05 or abs(t.d.qpos[1])>1.3:break
 except Exception:error=traceback.format_exc()
 n=len(ys);qualified=bool(error is None and hold>=.4-1e-7 and entry is not None and .1<=entry<=.6);row=dict(offset_mm=mm,node=name,frame=frame,qualified=qualified,frames=n,entry_speed_m_s=entry,final_stable_s=hold,max_stable_s=best,error=error,student_score=False,no_reset=True,teacher_source_unchanged=True,optimizer_updates=0,PPO_updates=0)
 np.savez_compressed(dest/'correction.npz',obs=np.asarray(xs[:n],np.float32),actions=np.asarray(ys,np.float32),history=np.asarray(hs[:n],np.float32),targets=np.asarray(targets[:n],np.float32),semantic_id=np.asarray(sem),qpos=np.asarray(qs),qvel=np.asarray(vs),integration_state=np.asarray(prestates[:n]),phases=np.asarray(ph),trace=np.asarray(tr));put(dest/'RESULT.json',row);print('CONTACT_DAGGER',json.dumps(row),flush=True);return row
rows=[];start=time.time()
for mm in [-60,-30,0,30,60]:
 dest,nodes,states,prefix=capture(mm)
 for name,frame in [('approach',nodes['approach'])]:rows.append(attempt(mm,dest,name,frame,states,prefix));put(OUT/'PROGRESS.json',dict(attempts=len(rows),qualified=sum(v['qualified']for v in rows),rows=rows))
put(OUT/'COLLECTION.json',dict(attempts=len(rows),qualified=sum(v['qualified']for v in rows),qualified_frames=sum(v['frames']for v in rows if v['qualified']),rows=rows,wall_seconds=time.time()-start,PPO_updates=0,optimizer_updates=0));print('COLLECTION_COMPLETE',flush=True)
