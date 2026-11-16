"""Instrument an independent copy of the existing source player; never touches live UI."""
from pathlib import Path
import sys,json,hashlib,time,argparse
import numpy as np,mujoco as mj
HERE=Path(__file__).resolve().parent
PLAYER=Path(r'D:\claude2\fangzhen\playgrounds\Serial_Leg_Simulation_local')
sys.path.insert(0,str(PLAYER))
from play_wasd import SerialSimulation

def capture(name,speed):
 out=HERE/name;out.mkdir(exist_ok=False);start=time.perf_counter();s=SerialSimulation('20 cm 单台阶');s.speed=speed;s.set_height(.34);m,d=s.m,s.d
 qa=np.array([m.jnt_qposadr[int(x[0])]for x in m.actuator_trnid]);va=np.array([m.jnt_dofadr[int(x[0])]for x in m.actuator_trnid]);tire=np.array([m.geom(x+'_wheel_contact').id for x in ['left','right']]);bodies=m.geom_bodyid[tire];guide={i for i in range(m.ngeom)if 'guide' in (m.geom(i).name or '')};step=m.geom('local_step').id
 rows=[];phases=[];qs=[];vs=[];torques=[];ctrls=[];command=[];contact_records=[];stopped=False;best=hold=0.;entry=None
 try:
  while d.time<10.:
   age=float(d.time);moving=age>=1. and not stopped;s.step({'w'}if moving else set())
   R=d.xmat[s.base_id].reshape(3,3);pitch=np.arcsin(np.clip(-R[2,0],-1,1));yaw=np.arctan2(R[1,0],R[0,0]);roll=np.arctan2(R[2,1],R[2,2]);force_up=np.zeros(2);top=np.zeros(2,bool);wheel_wall=np.zeros(2);guide_v=guide_h=0.;any_contact=False
   for ci,c in enumerate(d.contact):
    g1,g2=int(c.geom1),int(c.geom2)
    if step not in (g1,g2):continue
    other=g2 if g1==step else g1;body=int(m.geom_bodyid[other]);f=np.zeros(6);mj.mj_contactForce(m,d,ci,f);normal=(1. if g1==step else -1.)*np.asarray(c.frame).reshape(3,3)[0]
    if f[0]>5.:any_contact=True
    if other in guide:guide_v+=max(0.,float(f[0]*normal[2]));guide_h+=float(f[0]*np.linalg.norm(normal[:2]))
    for side,b in enumerate(bodies):
     if body!=b:continue
     force_up[side]+=max(0.,float(f[0]*normal[2]))
     wheel_wall[side]+=float(f[0]*np.linalg.norm(normal[:2]))
     if f[0]>5. and normal[2]>.7 and abs(c.pos[2]-.2)<.012:top[side]=True
   if any_contact and entry is None:entry=dict(t=float(d.time),speed=float(np.linalg.norm(d.qvel[:2])),previous_speed_100ms=float(np.mean([r[8]for r in rows[-100:]]))if rows else 0.)
   crossing=bool(top.all()and d.qpos[0]>1.23)
   if crossing and s.c.step_climb.phase=='idle':stopped=True
   stable=crossing and abs(pitch)<.35 and abs(roll)<.35 and np.linalg.norm(d.qvel[:2])<.60
   hold=hold+float(m.opt.timestep) if stable else 0.;best=max(best,hold)
   rows.append([d.time,*d.qpos[:3],roll,pitch,yaw,d.qvel[0],np.linalg.norm(d.qvel[:2]),s.c.left_leg.length,s.c.right_leg.length,s.c.left_leg.theta,s.c.right_leg.theta,*d.geom_xpos[tire].reshape(-1),*top,*force_up,guide_v,guide_h,*wheel_wall,s.c.target_leg_length_command])
   phases.append(s.c.step_climb.phase);qs.append(d.qpos.copy());vs.append(d.qvel.copy());torques.append(d.actuator_force.copy());ctrls.append(d.ctrl.copy());command.append([speed if moving else 0.,s.c.target_leg_length_command]);contact_records.append([*force_up,guide_v,guide_h,*wheel_wall])
   if abs(pitch)>1.2 or abs(roll)>1.2:break
 finally:s.close()
 a=np.asarray(rows);np.savez_compressed(out/'trace.npz',trace=a,qpos=np.asarray(qs),qvel=np.asarray(vs),actual=np.asarray(torques),requested=np.asarray(ctrls),commands=np.asarray(command),phases=np.asarray(phases),columns=np.array(['time','x','y','z','roll','pitch','yaw','vx','speed','L_l','L_r','theta_l','theta_r','wheel_lx','wheel_ly','wheel_lz','wheel_rx','wheel_ry','wheel_rz','top_l','top_r','load_l','load_r','guide_v','guide_h','wheel_wall_l','wheel_wall_r','height_command']))
 (out/'MODEL.json').write_text(json.dumps(dict(scene=str(s.m and PLAYER.parent/'Serial_Leg_Simulation/mjcf/bigeye_step_20cm_local.xml'),physics_dt=float(m.opt.timestep),control_dt=s.c.dt,leg_command=.34,speed_command=speed,mass_kg=float(m.body_mass.sum()),wheel_radius=.06,qa=qa.tolist(),va=va.tolist(),guide_geoms=[m.geom(i).name for i in guide],actuator_order=[m.actuator(i).name for i in range(m.nu)]),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 r=dict(case=name,kind='independent_source_reproduction_not_exact_user_replay',sim_s=float(d.time),wall_s=time.perf_counter()-start,entry=entry,top_hold_s=best,pass_stair=best>=.4,phase_transitions=[dict(t=float(a[i,0]),phase=phases[i])for i in range(len(phases))if i==0 or phases[i]!=phases[i-1]],pitch_peak_deg=float(np.rad2deg(abs(a[:,5])).max()),final_xyz=d.qpos[:3].tolist(),final_pitch_deg=float(np.rad2deg(a[-1,5])),optimizer_steps=0)
 (out/'RESULT.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(r),flush=True)
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--name',required=True);ap.add_argument('--speed',type=float,required=True);args=ap.parse_args();capture(args.name,args.speed)
