"""Collect actual successful upstream skills; never use source torque as a MOD4 label."""
from pathlib import Path
import sys,json,time,math,hashlib
import numpy as np,mujoco as mj
T=Path(__file__).resolve().parent
sys.path.insert(0,str(T/'source_adapter'))
from play_wasd import SerialSimulation
OUT=T/'source_demonstrations';OUT.mkdir(exist_ok=False)
cases=[('flat_jump','平地 / 跳跃',0.,0.,.2496265,'time'),('step07_auto_low','7 cm 单台阶',.07,.4,.34,'none'),('step07_auto_mid','7 cm 单台阶',.07,.8,.34,'none'),('step07_jump_low','7 cm 单台阶',.07,.4,.30,'edge')]
results=[];arrays={};start=time.time()
for name,scene,height,speed,stance,trigger in cases:
 s=SerialSimulation(scene);s.speed=speed;s.set_height(stance);m=s.m;d=s.d
 tire=[m.geom(n).id for n in ['left_wheel_contact','right_wheel_contact']]
 wheel_body=[int(m.geom_bodyid[g])for g in tire]
 upper_geom=mj.mj_name2id(m,mj.mjtObj.mjOBJ_GEOM,'local_step') if height else -1
 records=[];hold=0.;physical=False;air=False;jumped=False;peak=float(d.qpos[2]);phases={};landed=[False,False];reason='timeout';entry=None;maxspeed=0.
 try:
  while d.time<16.:
   age=float(d.time);keys={'w'}if age>=2. and speed>0 else set()
   if physical:keys=set()
   if not jumped and ((trigger=='time'and age>=2.)or(trigger=='edge'and d.qpos[0]>=.70)):
    s.jump();jumped=True
   s.step(keys)
   if round(float(d.time)*1000)%20:continue
   rotation=d.xmat[s.base_id].reshape(3,3);pitch=math.asin(float(np.clip(-rotation[2,0],-1,1)));roll=math.atan2(float(rotation[2,1]),float(rotation[2,2]))
   force=np.zeros(2);on_top=np.zeros(2,dtype=bool);ground=np.zeros(2,dtype=bool)
   for ci in range(d.ncon):
    contact=d.contact[ci];g1,g2=int(contact.geom1),int(contact.geom2)
    for side,body in enumerate(wheel_body):
     b1,b2=int(m.geom_bodyid[g1]),int(m.geom_bodyid[g2]);other=g1 if b2==body and b1==0 else g2 if b1==body and b2==0 else -1
     if other<0:continue
     f=np.zeros(6);mj.mj_contactForce(m,d,ci,f);normal=(1. if b2==body else -1.)*np.asarray(contact.frame).reshape(3,3)[0]
     if f[0]>5. and normal[2]>.7:
      ground[side]=True;force[side]+=float(f[0]*normal[2])
      if other==upper_geom and abs(float(contact.pos[2])-height)<.012:on_top[side]=True
   wheel=d.geom_xpos[tire].copy();peak=max(peak,float(d.qpos[2]));air|=bool(np.all(wheel[:,2]>.10)and not ground.any())
   actualspeed=float(np.linalg.norm(d.qvel[:2]))
   if height and entry is None and wheel[:,0].max()>=1.:entry=actualspeed
   if entry is not None:maxspeed=max(maxspeed,actualspeed)
   for side in range(2):landed[side]|=bool(on_top[side])
   on_platform=bool(on_top.all()and d.qpos[0]>1.32 and d.qpos[0]<2.85)
   physical|=on_platform if height else False
   ready=on_platform if height else (air and s.c.jump_state=='idle'and ground.all())
   stable=ready and max(abs(pitch),abs(roll))<math.radians(25)and np.linalg.norm(d.qvel[3:5])<1.5 and abs(d.qvel[2])<.25
   hold=hold+.02 if stable else 0.
   phase=s.c.jump_state+'|'+s.c.step_climb.phase
   if phase not in phases:phases[phase]=len(phases)
   records.append([d.time,*d.qpos[:7],*d.qvel[:6],s.c.left_leg.length,s.c.right_leg.length,s.c.left_leg.theta,s.c.right_leg.theta,s.c.target_leg_length_command,*d.ctrl,*wheel.reshape(-1),*on_top.astype(float),*ground.astype(float),*force,phases[phase]])
   if hold>=.4-1e-8:reason='qualified_stable_landing';break
   if not np.isfinite(d.qpos).all()or not np.isfinite(d.qvel).all():reason='nonfinite';break
  values=np.asarray(records);arrays[name]=values
  result=dict(case=name,scene=scene,height_m=height,command_speed=speed,stance_length=stance,jump_trigger=trigger,success=reason=='qualified_stable_landing',reason=reason,completed_s=float(d.time),root_peak_z=peak,both_drive_wheels_airborne=air,ever_both_wheels_on_top=physical,each_wheel_landed=landed,hold_s=hold,entry_speed=entry,max_approach_ascent_speed=maxspeed,phases=phases,frames=len(records),source_torque_is_not_student_action=True)
  results.append(result);print(json.dumps(result,ensure_ascii=False),flush=True)
  (OUT/'PROGRESS.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 finally:s.close()
np.savez_compressed(OUT/'trajectories.npz',**arrays)
columns=['t',*[f'root_qpos_{i}'for i in range(7)],*[f'root_qvel_{i}'for i in range(6)],'L_left','L_right','theta_left','theta_right','length_reference',*[f'source_torque_{i}'for i in range(6)],*[f'wheel_xyz_{i}'for i in range(6)],'left_upper','right_upper','left_ground','right_ground','left_force_z','right_force_z','phase_index']
(OUT/'RESULT.json').write_text(json.dumps(dict(rows=results,columns=columns,wall_seconds=time.time()-start,source='Frozen upstream LQR/VMC; native1kHz physics/500Hzcontrol; trajectories downsampled50Hz',admitted=[x['case']for x in results if x['success']],not_yet_MOD4v3_demonstrations=True),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
