"""Spinrelativeodomcentering throughbounded common WHEEL torque, notrootforce.
Internalstabilization isnot ajoystickvelocitytarget. Originaltorque/DC/envelope
remaininforce. Position/lateralnoslip uncertainty remains explicit.
"""
import math
import numpy as np
from spin_center_controller_v1 import GroundController as VelocityCenter
class GroundController(VelocityCenter):
 def __init__(self,gain,config=None):
  c=config or{};super().__init__(gain,c);self.kt=float(c.get('center_torque_kp',4.));self.tcap=float(c.get('center_torque_cap',.6));self.cap=0.
 def command(self,estimate,forward,yaw_rate):
  tau=super().command(estimate,forward,yaw_rate);corr=0.;x=estimate.state14
  if self.center_log.get('active',False):
   err=np.asarray(self.center_log['error_xy']);psi=x[1]+x[8]*self.lead;corr=float(np.clip(-self.kt*(err@np.array([math.cos(psi),math.sin(psi)])),-self.tcap,self.tcap));diff=.5*(tau[5]-tau[2]);bound=max(0.,5.775909774436091-abs(diff));common=float(np.clip(.5*(tau[2]+tau[5])+corr,-bound,bound));tau[2]=common-diff;tau[5]=common+diff
  self.center_log['centering_torque_Nm']=corr;self.center_log['internal_action']='commonwheeltorque_notvelocityreference';self.previous=tau.copy();return tau
