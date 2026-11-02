"""Firstnewasset sensor-only TIMED-profile 270mm prototype, NOT contactFSMqualified.
Control: IMU/encoders/timer/localodometry only. Truecontact/mesh isGRADINGONLY.
Openlooptiming is explicit; allfailedtrialsretained, norootassist/teleportafterreset.
"""
from pathlib import Path
import json,sys,math,time,argparse,hashlib,traceback
import numpy as np,mujoco
from physics_bridge import ROOT,MODEL_SHA,geometry,FullDR
from physics_bridge_contact_mu_v1 import ContactAuditPlant as BufferedImuPlant
from ground_controller_v4 import GroundController
from sensor_core_jump_v1 import StateEstimator,rotation,quat_step
from mesh_support import StepPatch

def arrays(g):return{k:np.asarray(v,float)if k in('q','tau','K','A','B','Ad','Bd','P','Q','R')else v for k,v in g.items()}
def dump(p,d):
 with Path(p).open('x',encoding='utf-8')as f:json.dump(d,f,indent=2,allow_nan=False)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--config',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();c=json.loads(a.config.read_bytes());out=a.out.resolve();assert out.is_relative_to(ROOT);out.mkdir(parents=True,exist_ok=False);dump(out/'config.json',c);rows=[];p=None;start=time.perf_counter()
 try:
  bank=json.loads((ROOT/'JUMP270_V1/GAIN_BANK.json').read_bytes());ref=bank['reference_parameters'];g=arrays(bank['gains']['crouch']);gl=arrays(bank['gains']['landing']);p=BufferedImuPlant(True);dr=FullDR(int(c.get('seed',0)),nominal=bool(c.get('nominal',True)));drmeta=p.attach_dr(dr);p.reset(g['symmetric'],float(c.get('start_x',-.8)));est=StateEstimator(geometry(),p.imu_offset,upright_prior=True,accel_reference='wheel_midpoint',innovation_limit=1.);ctrl=GroundController(g,dict(position_weight=25.,position_leash=1.,yaw_kp=.8,yaw_ki=.5,roll_kp=float(c.get('ground_roll_kp',20.)),roll_kd=2.));land=GroundController(gl,dict(position_weight=25.,position_leash=1.,yaw_kp=.8,yaw_ki=.5,roll_kp=float(c.get('ground_roll_kp',20.)),roll_kd=2.));gd=mujoco.MjData(p.m);step=StepPatch();leg=[0,1,3,4];launch=None;launch_pose=None;land_start=None;worldv=None;flight_distance=None;prev_source=None;phase='approach';maxclose=0.;maxmim=0.;first_clear=None;first_air=None;true_air_count=0;stable=0.;maxstable=0.;nonwheel_controls=0;stop='complete';bothGroundTop=0;last={};N=round(float(c.get('duration_s',7.))/.01);push=float(c.get('push_for',ref['push_for']));recover_at=float(c.get('recover_after_push_s',.72));speed=float(c.get('speed',ref['speed']))
  src=[Path(__file__),ROOT/'sensor_core_jump_v1.py',ROOT/'physics_bridge_contact_mu_v1.py',ROOT/'physics_bridge_guide_mu_v1.py',ROOT/'physics_bridge_v3.py',ROOT/'prepare_jump_roll_v2.py',ROOT/'prepare_jump_roll_v3.py',ROOT/'ground_controller_v4.py',ROOT/'physics_bridge_v3.py',ROOT/'physics_bridge_v4_grade.py',ROOT/'JUMP270_V1/GAIN_BANK.json'];dump(out/'SOURCE_MANIFEST.json',{'kind':'TIMED_PROFILE_SENSORONLY_NOT_FSMQUALIFIED','model_SHA':MODEL_SHA,'source':[{'path':str(f),'bytes':f.stat().st_size,'SHA':hashlib.sha256(f.read_bytes()).hexdigest()}for f in src]})
  for k in range(N):
   t=float(p.d.time);packet=p.sensor_packet();e=est.update(packet);x=e.state14.copy();actualq=packet.joint_pos4;actualqd=packet.joint_vel4
   if launch is None and t>=float(c.get('command_at_s',.6)) and x[0]>=float(c.get('launch_distance_m',.3)):
    launch=t;launch_pose=x[[3,4,5,6]].copy();worldv=rotation(quat_step(est.q,e.omega_body,e.sensor_age_s))@np.array([x[7],0.,0.]);worldv[2]=0.;flight_distance=float(x[0]);prev_source=packet.time_s
   if launch is not None and land_start is None:
    est.accel_correction=0.;dt_source=max(0.,packet.time_s-prev_source);Rs=rotation(est.q);accworld=Rs@e.proper_acc_origin+np.array([0.,0.,-9.81]);worldv+=dt_source*accworld;prev_source=max(prev_source,packet.time_s);Rnow=rotation(quat_step(est.q,e.omega_body,e.sensor_age_s));vbody=Rnow.T@worldv;flight_distance+=.01*float(vbody[0]);x[0]=flight_distance;x[7]=float(vbody[0]);e.state14[:]=x
   if launch is None:
    phase='approach';tau=ctrl.command(e,speed if t>=float(c.get('command_at_s',.6))else 0.,0.)
   elif t-launch<push:
    phase='push_off';u=float(np.clip((t-launch)/push,0.,1.));lh,ld,rh,rd=launch_pose;endh=float(g['q'][3])+float(c.get('hip_shift',ref['hip_shift']));pd=float(c.get('push_delta',ref['push_delta']));targets=np.array([(1-u)*lh+u*endh,(1-u)*(lh+ld)+u*(endh+pd),(1-u)*rh+u*endh,(1-u)*(rh+rd)+u*(endh+pd)]);vels=np.array([endh-lh,endh+pd-lh-ld,endh-rh,endh+pd-rh-rd])/push;tau=g['tau'].copy();tau[leg]+=ref['push_kp']*(targets-actualq)+ref['push_kd']*(vels-actualqd);wheel=ref['wheel_push']+ref['push_pitch']*x[2]+float(c.get('push_pitch_d',ref['push_pitch_d']))*x[9];tau[[2,5]]=wheel
    # Contact-phasehypothesis only: rootrollmoment allocatedvia measuredq footJ.
    reserve=float(c.get('push_reserve_Nm',8.));tau[leg]=np.clip(tau[leg],-40.+reserve,40.-reserve);rollmoment=float(np.clip(-float(c.get('push_roll_kp',40.))*e.roll-float(c.get('push_roll_kd',5.))*e.omega_body[0],-8.,8.));Rbody=rotation(quat_step(est.q,e.omega_body,e.sensor_age_s))
    for side,inds,qq in(('left',[0,1],actualq[:2]),('right',[3,4],actualq[2:])):
     _,_,J,_=est.geom.wheel_kinematics(float(qq[0]),float(qq[1]),0.,0.,0.,np.zeros(3),side);fz=rollmoment/.4376*(1 if side=='left'else -1);tau[inds]-=J.T@(Rbody.T@np.array([0.,0.,fz]))
    yd=float(np.clip(-1.2*x[8]-.4*x[1],-.5,.5));tau[2]-=yd;tau[5]+=yd
   elif t-launch-push<recover_at:
    est.wheel_measurement_enabled=False;est.ground_kinematic_constraint_enabled=False;tf=t-launch-push;phase='flight_tuck';h=ref['tuck_hip'];d=ref['tuck_delta'];extension=float(c.get('extend_after',ref['extend_after']))
    if tf>extension:
     phase='flight_extend';u=float(np.clip((tf-extension)/.1,0.,1.));h=(1-u)*h+u*gl['q'][3];d=(1-u)*d+u*gl['q'][4]
    targets=np.array([h,h+d,h,h+d]);tau=np.zeros(6);tau[leg]=ref['air_kp']*(targets-actualq)-ref['air_kd']*actualqd;tau[[2,5]]=ref['air_wheel']+ref['air_pitch']*x[2]+ref['air_pitch_d']*x[9];difference=20*(x[3]-x[5])+2*(x[10]-x[12]);tau[0]-=difference;tau[3]+=difference
   else:
    phase='timed_landing_recovery'
    if land_start is None:land_start=t;land.ref[0]=x[0]+.15*x[7];est.vb[0]=x[7];est.distance=x[0]
    est.wheel_measurement_enabled=True;est.ground_kinematic_constraint_enabled=True;est.accel_correction=1.5;vx=1.2 if t-land_start<.4 else 0.;tau=land.command(e,vx,0.)
   tau=np.clip(tau,[-40,-40,-5.775909774436091]*2,[40,40,5.775909774436091]*2);p.audit_armed=launch is not None;p.apply_torque_request(tau,packet);last=p.grade();maxclose=max(maxclose,last['closure']);maxmim=max(maxmim,last['mimic']);gd.qpos[:]=p.d.qpos;mujoco.mj_kinematics(p.m,gd);env=p.exact_support.step_envelope(gd,step);forces=np.zeros(2);topforces=np.zeros(2);other=0;stepid=p.m.geom('step270').id;floor=p.m.geom('ground').id
   for ci,ct in enumerate(p.d.contact):
    a1,b1=int(ct.geom1),int(ct.geom2)
    if stepid not in(a1,b1)and floor not in(a1,b1):continue
    f=np.zeros(6);mujoco.mj_contactForce(p.m,p.d,ci,f)
    if f[0]<=1:continue
    rob=b1 if a1 in(stepid,floor)else a1
    if rob in p.tires:
     ii=p.tires.index(rob);forces[ii]+=f[0]
     if stepid in(a1,b1):topforces[ii]+=f[0]
    else:other+=1
   nonwheel_controls+=bool(other)
   if launch is not None and max(forces)<1:true_air_count+=1
   else:true_air_count=0
   if first_air is None and true_air_count>=2:first_air=float(p.d.time)-.01
   clear=first_air is not None and env['both_rear_crossing_margin_m']>0 and env['both_entire_bottom_above_top_m']>0
   if clear and first_clear is None:first_clear=float(p.d.time)
   topbearing=bool(np.min(topforces)>1 and env['all_footprints_within_top_geometric']);bothGroundTop+=topbearing;good=bool(topbearing and first_clear is not None and abs(last['pitch_true'])<.15 and abs(last['roll_true'])<.15 and abs(last['body_velocity'][0])<.35 and other==0);stable=stable+.01 if good else 0.;maxstable=max(maxstable,stable)
   rows.append(dict(time=float(p.d.time),phase=phase,estimated14=x.tolist(),gyro=packet.gyro_body.tolist(),acc=packet.accel_proper_body.tolist(),requested_tau=tau.tolist(),actual_tau=p.d.ctrl.tolist(),qpos_truth_grading=p.d.qpos.tolist(),truth=last,envelope=env,contact_normal_N2=forces.tolist(),top_normal_N2=topforces.tolist(),nonwheel_ground_controls=other,first_clear=first_clear,stable_s=stable))
   if not last['finite']or last['closure']>.01 or last['mimic']>.01 or last['upright_cos']<.45:stop='health';break
  result=dict(kind='SENSORONLY_TIMED_JUMP270_ROLLVMC_V2_NOT_CONTACTFSM_RELEASE',config=c,model_SHA=MODEL_SHA,DR=drmeta,queues=dr.queue_receipt(),complete=len(rows)==N,stop=stop,physics_steps=p.tick_phys,controls=len(rows),launch_time=launch,first_air=first_air,first_full_mesh_clearance=first_clear,top_bearing_controls=bothGroundTop,max_stable_s=maxstable,end_stable_s=stable,legacy_ever_stable_halfsecond=maxstable>=.5,proposed_end_stable_2s=stable>=2. and len(rows)==N,nonwheel_contact_control_samples=int(nonwheel_controls),maxclosure=maxclose,maxmimic=maxmim,last=last,wall_s=time.perf_counter()-start,root_assist_forces=0,root_pose_overwrites_after_initialization=0,controller_truth_inputs=False,landing_trigger='explicitelapsedtimeNOTcontactqualification',observer_notes='WheelKFoffduringpredictedflight; inertialvelocitypushintegration; assumptionsnotvalidatedforarbitrarycontactfailure')
  h=hashlib.sha256();n=0
  with(out/'trace.jsonl').open('xb')as f:
   for r in rows:b=(json.dumps(r,separators=(',',':'))+'\n').encode();f.write(b);h.update(b);n+=len(b)
  ah=hashlib.sha256();an=0
  with(out/'physics_contact_audit.jsonl').open('xb')as af:
   for ar in p.audit_samples:
    ab=(json.dumps(ar,separators=(',',':'))+'\n').encode();af.write(ab);ah.update(ab);an+=len(ab)
  result['material_variant']=p.material_variant;result['physics_contact_audit']=dict(path=str(out/'physics_contact_audit.jsonl'),bytes=an,SHA=ah.hexdigest(),rate_hz=1/p.dt,stage_time_explicit=True,first_full_air_s=p.first_full_air,max_full_air_s=p.max_full_air,first_landing=p.first_landing,first_physics_mesh_clear=p.first_physics_mesh_clear,first_air_mesh_clear=p.first_air_mesh_clear,guide_contact_ticks=p.guide_contact_ticks,hard_other_contact_ticks=p.hard_contact_ticks);result['raw_trace']={'path':str(out/'trace.jsonl'),'bytes':n,'SHA':h.hexdigest(),'producer_streamed':True};dump(out/'result.json',result);print(json.dumps({k:v for k,v in result.items()if k not in('DR','queues')},indent=2))
 except BaseException:
  error=traceback.format_exc();ph=hashlib.sha256();nb=0
  with(out/'partial_trace.jsonl').open('xb')as f:
   for rr in rows:
    bb=(json.dumps(rr,separators=(',',':'),allow_nan=False)+'\n').encode('utf-8');f.write(bb);ph.update(bb);nb+=len(bb)
  dump(out/'ERROR.json',dict(error=error,controls=len(rows),physics_steps=None if p is None else p.tick_phys,partial_trace={'path':str(out/'partial_trace.jsonl'),'bytes':nb,'SHA':ph.hexdigest()}));raise
if __name__=='__main__':main()
