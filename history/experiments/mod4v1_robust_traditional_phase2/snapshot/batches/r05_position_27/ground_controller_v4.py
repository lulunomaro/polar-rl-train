"""Sensor-estimate-only ground controller prototype. No simulator imports/access.
Ground14LQR + command shaping + bounded roll correction. Not airborne control.
"""
import math,time
import numpy as np
from scipy.linalg import solve_discrete_are
from sensor_core_v4 import CommandShaper

class GroundController:
 def __init__(self,gain,config=None):
  c=config or{};self.g=gain;self.dt=.01;self.eq=np.r_[gain['q'],np.zeros(7)];self.tau_eq=np.asarray(gain['tau']);Q=np.asarray(gain['Q']).copy();R=np.asarray(gain['R']).copy();f=np.ones(14)
  for ids,key in[((2,), 'pitch_weight'),((9,), 'pitchrate_weight'),((0,), 'position_weight'),((7,), 'velocity_weight'),((1,8),'yaw_weight'),((3,4,5,6),'leg_weight')]:
   for i in ids:f[i]=float(c.get(key,1.))
  Q=np.diag(np.diag(Q)*f);R*=float(c.get('effort_weight',1.));P=solve_discrete_are(gain['Ad'],gain['Bd'],Q,R);self.K=np.linalg.solve(R+gain['Bd'].T@P@gain['Bd'],gain['Bd'].T@P@gain['Ad']);self.shaper=CommandShaper(float(c.get('accel',1.5)),float(c.get('yaw_accel',6.)),float(c.get('jerk',8.)));self.ref=self.eq.copy();self.ref[0:2]=0.;self.previous=np.asarray(gain['tau']).copy();self.predict=float(c.get('model_predict_fraction',0.));self.roll_kp=float(c.get('roll_kp',0.));self.roll_kd=float(c.get('roll_kd',0.));self.effort=np.array([40.,40.,5.775909774436091]*2);self.position_leash=float(c.get('position_leash',.2));self.heading_leash=float(c.get('heading_leash',.6));self.max_solve_ms=0.;self.envelope_clips=0;self.valid_command=True;self.decouple_yaw=bool(c.get("decouple_yaw",True));self.yaw_kp=float(c.get("yaw_kp",.5));self.yaw_ki=float(c.get("yaw_ki",.1));self.yaw_ff=float(c.get("yaw_ff",.08));self.yaw_integral=0.;self.yaw_integral_limit=float(c.get("yaw_integral_limit",15.));self.yaw_rate_ff=float(c.get("yaw_rate_ff",.052));self.old_shaped_w=0.;self.fixed_legs=bool(c.get("fixed_legs",True));self.leg_kp=float(c.get("leg_kp",120.));self.leg_kd=float(c.get("leg_kd",4.));self.wheel_pitch_scale=float(c.get("wheel_pitch_scale",1.));self.wheel_velocity_scale=float(c.get("wheel_velocity_scale",1.))
 def command(self,estimate,forward,yaw_rate):
  started=time.perf_counter_ns();x=estimate.state14.copy();age=estimate.sensor_age_s
  if age>.05 or not np.isfinite(x).all():self.valid_command=False;return np.zeros(6)
  # Finitefirstordermodelprediction drivenbyownknownrequest, notDRdelayoracle.
  if self.predict and age>0:
   a=self.g['A']@(x-self.eq)+self.g['B']@(self.previous-self.tau_eq);x[7:]+=self.predict*age*a[7:]
  v,w=self.shaper.update(float(forward),float(yaw_rate),self.dt);maxwheel=.9*55.3557*.06369999796152115;request=abs(v)+.4376/2*abs(w)
  if request>maxwheel:v*=maxwheel/request;w*=maxwheel/request;self.envelope_clips+=1
  self.ref[0]=float(np.clip(self.ref[0]+v*self.dt,x[0]-self.position_leash,x[0]+self.position_leash));self.ref[1]=float(np.clip(self.ref[1]+w*self.dt,x[1]-self.heading_leash,x[1]+self.heading_leash));self.ref[7]=v;self.ref[8]=w
  error=x-self.ref
  if self.decouple_yaw:error[1]=0.;error[8]=0.
  if self.fixed_legs:
   for a,b in((3,5),(4,6),(10,12),(11,13)):error[a]=error[b]=.5*(error[a]+error[b])
  weighted_error=error.copy();weighted_error[2]*=self.wheel_pitch_scale;weighted_error[9]*=self.wheel_pitch_scale;weighted_error[7]*=self.wheel_velocity_scale
  tau=self.tau_eq-self.K@weighted_error
  if self.fixed_legs:
   actual_q=np.array([x[3],x[3]+x[4],x[5],x[5]+x[6]]);reference_q=np.array([self.ref[3],self.ref[3]+self.ref[4],self.ref[5],self.ref[5]+self.ref[6]]);actual_dq=np.array([x[10],x[10]+x[11],x[12],x[12]+x[13]]);tau[[0,1,3,4]]=self.tau_eq[[0,1,3,4]]+self.leg_kp*(reference_q-actual_q)-self.leg_kd*actual_dq
  if self.decouple_yaw:
   yawerr=w-x[8];candidate=float(np.clip(self.yaw_integral+yawerr*self.dt,-self.yaw_integral_limit,self.yaw_integral_limit));common=float(np.mean(tau[[2,5]]));available=max(0.,5.775909774436091-abs(common));desired=self.yaw_kp*yawerr+self.yaw_ki*candidate+self.yaw_rate_ff*w+self.yaw_ff*(w-self.old_shaped_w)/self.dt;diff=float(np.clip(desired,-available,available));
   if abs(desired)<=available:self.yaw_integral=candidate
   tau[2]=common-diff;tau[5]=common+diff;self.old_shaped_w=w
  roll=float(np.clip(-self.roll_kp*estimate.roll-self.roll_kd*estimate.omega_body[0],-8,8));tau[1]+=roll;tau[0]-=roll;tau[4]-=roll;tau[3]+=roll;tau=np.clip(tau,-self.effort,self.effort);self.previous=tau.copy();elapsed=(time.perf_counter_ns()-started)*1e-6;self.max_solve_ms=max(self.max_solve_ms,elapsed);return tau
