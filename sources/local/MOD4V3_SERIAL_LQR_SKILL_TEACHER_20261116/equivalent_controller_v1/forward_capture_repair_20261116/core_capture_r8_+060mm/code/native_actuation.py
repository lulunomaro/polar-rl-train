"""Exact native PD inverse and closest feasible pair torque, with explicit residuals.
Constraints are the existing voltage envelope, action bounds and front-rear PD-target
difference bounds. This changes no target bound or motor envelope.
"""
import numpy as np
LOW=.17265192458887935
HIGH=1.7508937980913823
PEAK=np.r_[[40.]*4,[5.775909774436091]*2]
STALL=np.r_[[53.333333333333336]*4,[28.18525375641699]*2]
NOLOAD=np.r_[[16.755160819145562]*4,[55.35573187814664]*2]
def envelope(v):return np.maximum(-PEAK,np.minimum(0.,-STALL*(1+v/NOLOAD))),np.minimum(PEAK,np.maximum(0.,STALL*(1-v/NOLOAD)))
def inverse(tau,q,v,default):return np.r_[(q[:4]-default+(tau[:4]+2*v[:4])/60.)/.5,(v[4:]+tau[4:]/.6)/10.]
def feasible(tau,q,v,default):
 lo,hi=envelope(v);lo[:4]=np.maximum(lo[:4],60*(default-3.-q[:4])-2*v[:4]);hi[:4]=np.minimum(hi[:4],60*(default+3.-q[:4])-2*v[:4]);lo[4:]=np.maximum(lo[4:],.6*(-60-v[4:]));hi[4:]=np.minimum(hi[4:],.6*(60-v[4:]));out=np.clip(tau,lo,hi);empty=False
 for f,r in [(0,2),(1,3)]:
  lower=60*(LOW-(q[f]-q[r]))-2*(v[f]-v[r]);upper=60*(HIGH-(q[f]-q[r]))-2*(v[f]-v[r]);dl=max(lower,lo[f]-hi[r]);dh=min(upper,hi[f]-lo[r])
  if dl>dh or lo[f]>hi[f] or lo[r]>hi[r]:empty=True;continue
  diff=out[f]-out[r]
  if diff<dl or diff>dh:
   delta=np.clip(diff,dl,dh);ff=np.clip((tau[f]+tau[r]+delta)/2.,max(lo[f],lo[r]+delta),min(hi[f],hi[r]+delta));out[f],out[r]=ff,ff-delta
 return out,empty
