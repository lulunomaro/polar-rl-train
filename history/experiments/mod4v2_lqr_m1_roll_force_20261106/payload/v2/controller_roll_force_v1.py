"""T01-only candidate: SPR chassis_task.c:919,972-973 force-couple structure.
Independent IMU roll PD -> equal/opposite estimated-world-vertical toe forces,
then motor tau=-J^T F_ground. Not the old axial-D candidate or force detector.
No foreign gains/rod lengths/gas formula; no plant/contact/DR inputs or arming.
"""
import math
import numpy as np
from controller_heading_v2 import GroundController as Base
VARIANT='coord_soft_MOD4v2_VMC_roll_force_v1'
NOMINAL_MASS_KG=14.294140288606286 # published P0 design mass, not sampled DR mass

class GroundController(Base):
 def __init__(self,*args,**kwargs):
  super().__init__(*args,**kwargs);self.mode=VARIANT
  r,_=self._fk(self.q0,'left');h=abs(float(r[2]))
  if not .1<h<1.:raise ValueError('Nominal root-to-wheel design lever outside domain')
  # Approximate point mass at root, NOT identified COM/roll inertia.
  # K=2*m*g*h, omega=sqrt(g/h), zeta=.7, D=2*zeta*(m*h^2)*omega.
  # Finite design bandwidth; no terrain-specific tuning or random-parameter use.
  m=NOMINAL_MASS_KG;w=math.sqrt(9.81/h)
  self.roll_force_design=dict(nominal_mass_kg=m,root_wheel_design_height_m=h,
   approximate_roll_inertia_kg_m2=m*h*h,design_omega_rad_s=w,damping_ratio=.7,
   kp_moment_Nm_rad=2*m*9.81*h,kd_moment_Nms_rad=2*.7*m*h*h*w,
   force_couple_limit_N=.2*m*9.81,filter_s=.03,extra_joint_torque_limit_Nm=6.,
   point_mass_approximation_not_measured_inertia=True,ground_T01_only=True,
   contact_identity_confirmed=False,truth_inputs=False)
  self.roll_moment=0.;self.roll_force_diag={}
 def command(self,e,forward,yaw_rate):
  tau=super().command(e,forward,yaw_rate)
  if not self.valid_command:return tau
  x=np.asarray(e.state14,float);roll=float(e.roll);pitch=float(x[2]);om=np.asarray(e.omega_body,float)
  # Euler roll derivative from body gyro, avoiding setpoint differentiation.
  rolldot=float(om[0]+math.tan(pitch)*(math.sin(roll)*om[1]+math.cos(roll)*om[2]))
  p=self.roll_force_design
  desired=-p['kp_moment_Nm_rad']*roll-p['kd_moment_Nms_rad']*rolldot
  self.roll_moment+=self.dt/(p['filter_s']+self.dt)*(desired-self.roll_moment)
  nB=np.array([-math.sin(pitch),math.sin(roll)*math.cos(pitch),math.cos(roll)*math.cos(pitch)])
  rL,JL=self._fk([x[3],x[3]+x[4]],'left');rR,JR=self._fk([x[5],x[5]+x[6]],'right')
  lever=float(np.cross(rL-rR,nB)[0])
  if not np.isfinite(lever)or lever<.2:raise ValueError('VMC_ROLL_FORCE_LEVER_DOMAIN')
  f=float(np.clip(self.roll_moment/lever,-p['force_couple_limit_N'],p['force_couple_limit_N']))
  extra=np.zeros(6);extra[[0,1]]=-JL.T@nB*f;extra[[3,4]]=JR.T@nB*f
  scale=min(1.,p['extra_joint_torque_limit_Nm']/max(float(np.max(np.abs(extra))),1e-12))
  # Scale the whole force couple together to preserve zero net requested force.
  # Baseline control has priority, rather than clipping one side independently.
  for i in (0,1,3,4):
   if abs(extra[i])>1e-12:
    room=float(self.effort[i]-math.copysign(1.,extra[i])*tau[i])
    scale=min(scale,max(0.,room/abs(float(extra[i]))))
  out=tau+scale*extra
  if not np.isfinite(out).all()or np.any(np.abs(out)>self.effort+1e-8):raise ValueError('VMC_ROLL_FORCE_OUTPUT_BOUNDS')
  self.previous=out.copy()
  self.roll_force_diag=dict(raw_roll_moment_Nm=desired,filtered_roll_moment_Nm=self.roll_moment,
   requested_ground_force_couple_N=f,applied_scale=scale,extra_joint_tau6_Nm=(scale*extra).tolist(),
   roll_rate_rad_s=rolldot,net_requested_ground_force_N=0.,truth_inputs=False,contact_identity_confirmed=False)
  return out
