"""Capture actual stalled states of frozen policies with original contact guards; no learning."""
from pathlib import Path
import json,sys,importlib.util,hashlib,gc,types,math,time
import torch,numpy as np,mujoco
T=Path(__file__).resolve().parent;R=T.parents[2];L=T.parent/'MOD4V3_LOW_SPEED_RETRACTION_20261113';spec=importlib.util.spec_from_file_location('oldsetup',L/'replay_probe.py');old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
out=T/'evidence/actual_stall_capture_r1';out.mkdir(exist_ok=False);show=old.setup(out,'parent');sys.path.insert(0,str(T/'manual_replay'));from replay_supported_guards import replay_step
show.Replay.step=replay_step(show.Simulation,show.SafetyStop,duration_steps=10,event_dir=out/'reset_events')
models={'parent':T/'weights/frozen_comprehensive_parent.pt','previous40m':T.parent/'MOD4V3_REARWARD_SUPPORTED_STAIRS_40M_20261114/weights/model_040m.pt'};result=[]
for label,model in models.items():
 show.CKPT=model;show.EXPECTED=hashlib.sha256(model.read_bytes()).hexdigest();s=show.Replay(level=3);s.args.vx=.4;e=s.env;m,d=e.m,e.d;wheelids=[m.body(n).id for n in ['left_wheel_link','right_wheel_link']];support={i for i in range(m.nbody)if 'guide'in m.body(i).name}|{e.base_id};d.qpos[:3]=[-3.9,0,e.bank_z];d.qpos[3:7]=[1,0,0,0];d.qvel[:]=0;mujoco.mj_forward(m,d);s.reset_count=1;s.reason='';peak=0.;selected=[];rows=[];cf=np.zeros(6)
 def physics(env,a):
  global peak
  a=a.clamp(-env.action_clip,env.action_clip)
  for j in range(8):
   tau=env._torque(a).detach().numpy().reshape(-1)
   if j%4==0:d.ctrl[env.act_ids[:4]]=tau[:4]
   d.ctrl[env.act_ids[4:]]=tau[4:];mujoco.mj_step(m,d)
   cl=max(float(np.linalg.norm(d.site_xpos[u]-d.site_xpos[v]))for u,v in s.pairs);s.closure=cl;peak=max(peak,cl)
   if not np.isfinite(d.qpos).all()or not np.isfinite(d.qvel).all():raise show.SafetyStop('nonfinite')
   if cl>.002:raise show.SafetyStop('closure>2mm')
  env.a_prev=a.detach();return env.state()
 e.step=types.MethodType(physics,e)
 try:
  for k in range(1500):
   s.set_height(.28+(.42-.28)*min(k/100,1));s.step({'w'}if k>=150 else set());force=0.
   for ci in range(d.ncon):
    c=d.contact[ci];g1,g2=int(c.geom1),int(c.geom2);b1,b2=int(m.geom_bodyid[g1]),int(m.geom_bodyid[g2])
    if(b1==0)==(b2==0):continue
    terrain,robot,sgn=(g1,b2,1.)if b1==0 else(g2,b1,-1.);mujoco.mj_contactForce(m,d,ci,cf);frame=np.asarray(c.frame).reshape(3,3)
    if robot in support and(m.geom(terrain).name or '')=='step_1'and sgn*frame[0,2]>.7:force+=max(0.,float((sgn*frame.T@cf[:3])[2]))
   row=dict(time=float(d.time),root=d.qpos[:3].tolist(),quat=d.qpos[3:7].tolist(),velocity=d.qvel[:6].tolist(),vx=float(e.vx),depth_m=float(d.qpos[0]+2.9),support_N=force,wheel=d.xpos[wheelids].tolist(),cos_tilt=float(e.cos_tilt));rows.append(row)
   if k>=150 and force>5 and abs(e.vx)<.1 and d.qpos[0]>-2.9 and s.reset_count==1:
    selected.append(dict(row=row,qpos=d.qpos.copy(),qvel=d.qvel.copy(),ctrl=d.ctrl.copy(),a_prev=s.a_prev.numpy().copy()))
   if s.reset_count>1:break
  selected.sort(key=lambda q:q['row']['depth_m'],reverse=True);chosen=[]
  for item in selected:
   if all(abs(item['row']['time']-prior['row']['time'])>=.2 for prior in chosen):chosen.append(item)
   if len(chosen)>=3:break
  arrays={}
  for i,item in enumerate(chosen):
   for key in ['qpos','qvel','ctrl','a_prev']:arrays[f'{key}_{i}']=item[key]
  np.savez_compressed(out/(label+'_states.npz'),**arrays);item=dict(model=label,sha256=show.EXPECTED,resets=s.reset_count-1,reason=s.reason,max_closure_m=peak,max_body_depth_m=max(r['depth_m']for r in rows),actual_stuck_snapshots=[x['row']for x in chosen],trace=rows,joint_qposadr={m.joint(j).name:int(m.jnt_qposadr[j])for j in range(m.njnt)},nq=m.nq,nv=m.nv);(out/(label+'.json')).write_text(json.dumps(item,indent=2)+'\n');result.append({k:v for k,v in item.items()if k!='trace'});print(label,'actual_stuck_snapshots',len(chosen),'max_depth',item['max_body_depth_m'],flush=True)
 finally:s.close();del s,e,m,d;gc.collect()
(out/'RESULT.json').write_text(json.dumps(dict(no_optimizer=True,original_guard=True,models=result),indent=2)+'\n');print('ACTUAL_STALL_CAPTURE_COMPLETE',flush=True)
