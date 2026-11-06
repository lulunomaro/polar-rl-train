"""New sidecar transport test only: simplified geometry stub, not robot/old QA."""
from pathlib import Path
import sys,json,math
import numpy as np
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R.parent/'mod4v1_lqr_mpc_robust_20261102'));sys.path.insert(0,str(R))
from sensor_core_jump_v1 import StateEstimator,SensorPacket
from observer_audit_v1 import ObserverSidecar
class GeometryStub:
 def __init__(self):self.calls=0
 def wheel_kinematics(self,hip,crank,hipdot,crankdot,spin,omega,side):
  self.calls+=1;r=np.array([-.0342,.2188 if side=='left'else-.2188,-.2385])
  return .0625*spin-float(np.cross(omega,r)[0]),r,np.zeros((3,2)),0.
def main():
 out=R/'OBSERVER_AUDIT_V1/check001'
 if out.exists():raise RuntimeError('New observer test prefix consumed')
 out.mkdir(exist_ok=False)
 (out/'PREEXEC.json').write_text(json.dumps(dict(new_packets=128,held_views=1,geometry='simplified deterministic stub,not P0 FK',
  model=0,forward=0,physics=0,old_QA_or_raw=0,exact_output_difference_gate=0.,identity_and_packet_immutability_required=True),indent=2),encoding='utf-8')
 original=StateEstimator(GeometryStub(),(.03,0.,.04),upright_prior=True,accel_reference='wheel_midpoint')
 saved=[None];old=original.update
 def remember(p):saved[0]=old(p);return saved[0]
 original.update=remember;side=ObserverSidecar(original);side.attach(original);asserts=0
 def check(condition):
  nonlocal asserts
  asserts+=1
  if not condition:raise AssertionError('New observer interface assertion '+str(asserts))
 for k in range(128):
  t=k*.01;age=0. if k<64 else .01
  omega=np.array([.08*math.cos(t),.1*math.sin(2*t),.04*math.sin(t)])
  proper=np.array([4. if k==90 else .15*math.sin(t),.1*math.cos(t),9.81+.08*math.sin(t)])
  p=SensorPacket(t,t+age,omega,proper,np.array([.25,.05,.25,.05]),np.zeros(4),np.array([2.*math.sin(t),2.*math.sin(t)]),np.zeros(6))
  before=[np.asarray(getattr(p,x)).copy()for x in('gyro_body','accel_proper_body','joint_pos4','joint_vel4','wheel_vel2','motor_torque6')]
  e=original.update(p);check(e is saved[0]);check(side.last['max_output_difference']==0.)
  for field,value in zip(('gyro_body','accel_proper_body','joint_pos4','joint_vel4','wheel_vel2','motor_torque6'),before):check(np.array_equal(getattr(p,field),value))
  check(side.last['pre_fusion']['kind']=='NEW_FUSION')
  if k==63:
   held=SensorPacket(p.time_s,p.arrival_s+.01,p.gyro_body,p.accel_proper_body,p.joint_pos4,p.joint_vel4,p.wheel_vel2,p.motor_torque6)
   e=original.update(held);check(e is saved[0]);check(side.last['pre_fusion']is None);check(side.last['max_output_difference']==0.)
 s=side.summary();check(s['calls']==129);check(s['new_fusion_calls']==128);check(s['held_calls']==1)
 check(s['maximum_estimate_output_difference']==0.);check(not s['observer_failures']);check(s['gravity_weight_exact_zero_count']>=1)
 check(s['maximum_abs_first_order_roll_gap_rad']>0.);check(s['sidecar_control_connections']==0)
 check(not any(name.startswith('mujoco')for name in sys.modules))
 result=dict(passed=True,assertions=asserts,original_output_identity_verified=True,packet_arrays_unchanged=True,summary=s,
  model_compile=0,forward=0,physics=0,old_QA_or_raw_reads=0,FK_calls=0,stub_geometry_calls_original=original.geom.calls,
  stub_geometry_calls_sidecar=side.audit.geom.calls,not_physical_or_calibrated_observer_qualification=True)
 (out/'RESULT.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
