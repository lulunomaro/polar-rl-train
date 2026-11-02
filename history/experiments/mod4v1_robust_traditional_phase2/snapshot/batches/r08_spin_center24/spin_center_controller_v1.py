"""Sensor-derived planarodom centering for continuousselfspin; no roottruth.
No-side-slip lateral proxy is explicitassumption, not true lateralmeasurement.
Usesphaselead to accountfor rotatingdirection+innerloopdelay; testonlycandidate.
"""
import math
import numpy as np
from spin_base_v1 import GroundController as Base
from sensor_core_v4 import LinkageGeometry
from robot_geometry_constants_v1 import PINS,TRACK
class GroundController(Base):
 def __init__(self,gain,config=None):
  super().__init__(gain,config);c=config or{};self.geo=LinkageGeometry(PINS,TRACK,.06369999796152115);self.pxy=np.zeros(2);self.target=None;self.tprev=None;self.active_prev=False;self.center_kp=float(c.get('center_kp',1.));self.lead=float(c.get('center_lead_s',.08));self.cap=float(c.get('center_v_cap',.25));self.center_log={}
 def command(self,estimate,forward,yaw_rate):
  x=estimate.state14;psi=float(x[1]);cs,sn=math.cos(psi),math.sin(psi);R=np.array([[cs,-sn],[sn,cs]]);w=estimate.omega_body;pL,_=self.geo.pose(x[3],x[3]+x[4],'left');pR,_=self.geo.pose(x[5],x[5]+x[6],'right');pivot=.5*(pL+pR);vy=-float(np.cross(w,pivot)[1]);t=float(estimate.estimated_time_s);dt=0. if self.tprev is None else t-self.tprev
  if not 0<=dt<=.05:return np.zeros(6)
  self.pxy+=dt*(R@np.array([x[7],vy]));pivot_xy=self.pxy+R@pivot[:2];active=abs(yaw_rate)>4 and abs(forward)<.1
  if active and not self.active_prev:self.target=pivot_xy.copy()
  correction=0.;error=np.zeros(2)
  if active and self.target is not None:
   error=pivot_xy-self.target;future=psi+x[8]*self.lead;projection=float(error@np.array([math.cos(future),math.sin(future)]));correction=float(np.clip(-self.center_kp*projection,-self.cap,self.cap))
  self.center_log=dict(time=t,estimated_root_xy=self.pxy.tolist(),estimated_pivot_xy=pivot_xy.tolist(),target_pivot_xy=None if self.target is None else self.target.tolist(),error_xy=error.tolist(),no_side_slip_vy=vy,operator_v=float(forward),centering_v=correction,applied_v=float(forward+correction),active=active,lead_s=self.lead,assumption='lateralnoslipproxy_notmeasurement')
  self.tprev=t;self.active_prev=active;self.internal_v_offset=correction;return super().command(estimate,forward,yaw_rate)
