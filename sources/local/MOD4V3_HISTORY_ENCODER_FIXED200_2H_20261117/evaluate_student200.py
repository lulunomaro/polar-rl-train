"""Pure35->6 student on the fixed native200mm scene; no LQR instances or teacher calls."""
from pathlib import Path
import sys,json,argparse,math,time,hashlib
import numpy as np,torch,mujoco as mj
T=Path(__file__).resolve().parent;R=T.parents[2];E=R/'sources/local/MOD4V3_SERIAL_LQR_SKILL_TEACHER_20261116/equivalent_controller_v1'
sys.path.insert(0,str(E));from native_runtime import model_xml,PLANT,D,RobotSpec,_q_from_runtime,_q_from_bank,Mod4v3Mujoco,Mod4Retarget,NAMES,PPO_TO_NATIVE
from play_ppo_flatv1 import ActorMLP
torch.set_num_threads(1)
def run(model,out,video=False):
 out=Path(out);out.mkdir(parents=True,exist_ok=False);started=time.time();ck=torch.load(model,map_location='cpu',weights_only=False);actor=ActorMLP();actor.load_state_dict(ck['actor_state_dict'],strict=False);actor.eval();rows=[]
 for offset in [-60,-30,0,30,60]:
  dest=out/f'start_{offset:+04d}mm';dest.mkdir();xml,root,_=model_xml(dest,.2)
  spec=RobotSpec(**json.loads((D/'runtime/core/template_spec.json').read_text())['spec']);runtime=json.loads((PLANT/'runtime_config.json').read_text());default=_q_from_runtime(runtime,spec.joint_names);bank=json.loads((D/'plant/reset_bank.json').read_text());sem=json.loads((PLANT/'semantics.json').read_text());bq,bz=_q_from_bank(bank,sem,spec.joint_names);env=Mod4v3Mujoco(str(xml),spec,default,bq,bz,action_clip=6.);m,d=env.m,env.d;m.opt.timestep=.0025
  ik=Mod4Retarget();fit=ik.fit(np.sqrt(.3466**2+ik.lateral_offset**2),0.);d.qpos[:]=fit['qpos'];d.qpos[:3]=[offset/1000,0,.3466+.0625+.001];d.qpos[3:7]=[1,0,0,0];d.qvel[:]=0;mj.mj_forward(m,d)
  qa=np.array([m.jnt_qposadr[m.joint(n).id]for n in NAMES])[PPO_TO_NATIVE];va=np.array([m.jnt_dofadr[m.joint(n).id]for n in NAMES])[PPO_TO_NATIVE];baseline=np.r_[env.default_q[env.leg_ids].numpy(),[0,0]][PPO_TO_NATIVE]
  tire=np.array([m.geom(s+'_tire').id for s in ['left','right']]);bodies=m.geom_bodyid[tire];platform=m.geom('native_teacher_platform').id;pairs=[(m.site(x.get('site1')).id,m.site(x.get('site2')).id)for x in root.findall('equality/connect')]
  prev=np.zeros(6,np.float32);landed=False;stop=False;hold=best=0.;peak=0.;entry=None;approach_speed=0.;maxclosure=0.;reason='timeout';states=[];observations=[];actions=[];trace=[];tiltdwell=0;top=np.zeros(2,bool)
  with torch.inference_mode():
   for k in range(500):
    age=k*.02;v=.47 if age>=1. and not stop else 0.;height=.2 if landed else .4091;rot=d.xmat[env.base_id].reshape(3,3);q=d.qpos[qa]-baseline;q[4:]=0.
    obs=np.r_[[v,0,0,height*5],d.qvel[3:6]*.5,rot.T@np.array([0,0,-1]),q,d.qvel[va]*.1,prev,[0,1,0,0,0,1,0]].astype(np.float32)
    a=actor(torch.from_numpy(obs).reshape(1,35))[0].clamp(-6,6).numpy().copy();native=a[PPO_TO_NATIVE];a_t=torch.from_numpy(native).reshape(1,6);pre_v=float(np.linalg.norm(d.qvel[:2]))
    for j in range(8):
     tau=env._torque(a_t).numpy().reshape(-1)
     if j%4==0:d.ctrl[env.act_ids[:4]]=tau[:4]
     d.ctrl[env.act_ids[4:]]=tau[4:];mj.mj_step(m,d)
    if not np.isfinite(d.qpos).all()or not np.isfinite(d.qvel).all():reason='nonfinite';break
    closure=max(float(np.linalg.norm(d.site_xpos[l]-d.site_xpos[r]))for l,r in pairs);maxclosure=max(maxclosure,closure)
    if closure>1.:reason='catastrophic_closure_above1m';break
    top[:]=False;contact=False
    for i in range(d.ncon):
     c=d.contact[i];g1,g2=int(c.geom1),int(c.geom2);f=np.zeros(6);mj.mj_contactForce(m,d,i,f)
     if platform not in (g1,g2):continue
     other=g2 if g1==platform else g1;body=m.geom_bodyid[other]
     for side,b in enumerate(bodies):
      if body!=b:continue
      contact|=f[0]>5.;normal=(1 if body==m.geom_bodyid[g2]else -1)*np.asarray(c.frame).reshape(3,3)[0]
      if f[0]>5. and normal[2]>.7 and abs(float(c.pos[2])-.2)<.012:top[side]=True
    if contact and entry is None:entry=pre_v
    vx=float(d.qvel[0]);speed=float(np.linalg.norm(d.qvel[:2]));rot=d.xmat[env.base_id].reshape(3,3);pitch=math.asin(float(np.clip(-rot[2,0],-1,1)));roll=math.atan2(float(rot[2,1]),float(rot[2,2]));yaw=math.atan2(float(rot[1,0]),float(rot[0,0]));peak=max(peak,abs(pitch));wheel=d.geom_xpos[tire]
    near=bool(np.min(np.abs(wheel[:,0]-1.2))<.45)
    if near or entry is not None:approach_speed=max(approach_speed,speed)
    crossed=bool(top.all()and d.qpos[0]>1.23 and np.all(wheel[:,0]>1.225));landed|=crossed
    stable=bool(crossed and max(abs(pitch),abs(roll))<math.radians(25)and np.linalg.norm(d.qvel[3:6])<1.5 and abs(d.qvel[2])<.25 and speed<=.6 and entry is not None and .1<=entry<=.6 and approach_speed<=.6)
    hold=hold+.02 if stable else 0.;best=max(best,hold)
    if hold>=.4-1e-7:stop=True
    tilt=abs(pitch)>math.radians(40)or abs(roll)>math.radians(40);tiltdwell=tiltdwell+1 if tilt else 0
    states.append(d.qpos.copy());observations.append(obs);actions.append(a);trace.append([d.time,*d.qpos[:3],vx,speed,pitch,roll,yaw,*top,hold,height,closure]);prev=a
    if tiltdwell>=10:reason='tilt_above40deg_for0.2s';break
    if d.qpos[2]<.11:reason='fell_below_ground';break
    if abs(d.qpos[0])>3.05 or abs(d.qpos[1])>1.3:reason='left_platform_scene';break
  success=bool(best>=.4-1e-7 and hold>=.4-1e-7 and top.all())
  if success:reason='qualified_stable_final_top_support'
  tr=np.asarray(trace);retreat=0.
  if len(tr):retreat=float(np.max(np.maximum.accumulate(tr[:,1])-tr[:,1]))
  row=dict(start_offset_mm=offset,success=success,reason=reason,max_continuous_top_hold_s=best,final_continuous_hold_s=hold,entry_speed_m_s=entry,maximum_entry_ascent_speed_m_s=approach_speed,pitch_peak_deg=math.degrees(peak),minimum_forward_vx=float(tr[:,4].min())if len(tr)else None,maximum_retreat_m=retreat,maximum_closure_m=maxclosure,frames=len(states),teacher_calls=0,pure_student=True,mode=[0,1,0,0,0,1,0]);rows.append(row)
  np.savez_compressed(dest/'rollout.npz',qpos=np.asarray(states),obs=np.asarray(observations),actions=np.asarray(actions),trace=tr)
  (dest/'RESULT.json').write_text(json.dumps(row,indent=2)+'\n');print('INDEPENDENT_STUDENT',offset,success,reason,flush=True)
  if video and offset==0 and states:
   import imageio.v2 as imageio
   renderer=mj.Renderer(m,height=480,width=720);camera=mj.MjvCamera();camera.azimuth=90;camera.elevation=-15;camera.distance=2.;camera.lookat[:]=[1.1,0,.3]
   with imageio.get_writer(str(out/'STUDENT_CENTER_1X.mp4'),fps=25,codec='libx264',quality=7)as writer:
    for i in range(0,len(states),2):d.qpos[:]=states[i];mj.mj_forward(m,d);renderer.update_scene(d,camera=camera);writer.append_data(renderer.render())
   renderer.close()
 result=dict(model=str(model),sha256=hashlib.sha256(Path(model).read_bytes()).hexdigest(),iteration=ck['iter'],requested=5,passed=sum(r['success']for r in rows),rows=rows,mode=[0,1,0,0,0,1,0],pure_student35_to6=True,teacher_controller_instances=0,teacher_actions=0,optimizer_updates=0,native_full_DR_graduation=False,wall_seconds=time.time()-started)
 (out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--model',required=True);p.add_argument('--out',required=True);p.add_argument('--video',action='store_true');a=p.parse_args();run(a.model,a.out,a.video)
