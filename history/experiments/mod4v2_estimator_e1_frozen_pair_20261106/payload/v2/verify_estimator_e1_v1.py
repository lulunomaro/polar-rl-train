"""New E1 loss/transport checks, simplified geometry not P0/physics or old QA."""
from pathlib import Path
import json,math,sys
import numpy as np
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R.parent/'mod4v1_lqr_mpc_robust_20261102'));sys.path.insert(0,str(R))
from sensor_core_jump_v1 import StateEstimator,SensorPacket
from estimator_cauchy_e1 import cauchy_innovation_weight,CauchyEstimatorE1,MatchingE1Sidecar
class GeometryStub:
 def wheel_kinematics(self,hip,crank,hipdot,crankdot,spin,omega,side):
  r=np.array([-.0342,.2188 if side=='left'else-.2188,-.2385]);return .0625*spin-float(np.cross(omega,r)[0]),r,np.zeros((3,2)),0.
def main():
 D=R/'ESTIMATOR_CAUCHY_E1_V1/check001'
 if D.exists():raise RuntimeError('E1 software check already consumed')
 D.mkdir(exist_ok=False);(D/'PREEXEC.json').write_text(json.dumps(dict(new_math_points=11,static_packets=64,accelerometer_disturbance_packets=40,
  requirements=['bounded monotone Cauchy','norm0 remains0','existing scale reused','idealstatic parity','sameE1 witness exact','nonzero input effect explicitly demonstrated'],
  models=0,physics=0,FK=0,old_QA_or_raw=0),indent=2),encoding='utf-8')
 assertions=0
 def check(v):
  nonlocal assertions
  assertions+=1
  if not v:raise AssertionError('E1 assertion '+str(assertions))
 points=[0.,.1,.25,.5,1.,2.,4.,10.,1e6,1e155,1e308]
 weights=[cauchy_innovation_weight(v,1.)for v in points]
 for i,w in enumerate(weights):
  check(math.isfinite(w)and 0.<=w<=1.)
  if i:check(w<=weights[i-1])
  for norm_gate in(0.,.01,.3,1.):check(0.<=norm_gate*w<=norm_gate)
 check(weights[0]==1.);check(abs(weights[4]-.5)<2e-16);check(abs(weights[5]-.2)<2e-16)
 check(cauchy_innovation_weight(4.,0.)==1.);check(cauchy_innovation_weight(4.,-1.)==1.)
 for bad in(float('nan'),float('inf')):
  for a,b in((bad,1.),(1.,bad)):
   try:cauchy_innovation_weight(a,b)
   except ValueError:check(True)
   else:check(False)
 baseline=StateEstimator(GeometryStub(),(.03,0.,.04),upright_prior=True,accel_reference='wheel_midpoint')
 candidate=CauchyEstimatorE1(GeometryStub(),(.03,0.,.04),upright_prior=True,accel_reference='wheel_midpoint')
 side=MatchingE1Sidecar(candidate);side.attach(candidate);static_diff=0.;changed_diff=0.
 for k in range(104):
  p=SensorPacket(k*.01,k*.01+.01,np.zeros(3),np.array([0. if k<64 else 1.2+.2*math.sin(k),0.,9.81]),
   np.array([.25,.05,.25,.05]),np.zeros(4),np.zeros(2),np.zeros(6))
  before=p.accel_proper_body.copy();a=baseline.update(p);b=candidate.update(p)
  delta=float(np.max(np.abs(a.state14-b.state14)))
  if k<64:static_diff=max(static_diff,delta);check(delta==0.)
  else:changed_diff=max(changed_diff,delta)
  check(side.last['max_output_difference']==0.);check(np.array_equal(before,p.accel_proper_body));check(np.isfinite(b.state14).all())
 check(changed_diff>0.);check(side.summary()['maximum_estimate_output_difference']==0.);check(not side.failures)
 check(not any(k.startswith('mujoco')for k in sys.modules))
 result=dict(passed=True,assertions=assertions,points=points,weights=weights,ideal_static_state14_maxdiff=static_diff,
  baseline_E1_state14_difference_on_new_synthetic_disturbance=changed_diff,same_E1_witness_maxdiff=side.max_difference,
  E1_changes_feedback_explicit=True,original_norm_gate_zero_preserved=True,not_robot_accuracy_or_performance_test=True,
  models=0,forward=0,physics=0,FK=0,old_QA_or_raw_reads=0)
 (D/'RESULT.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
