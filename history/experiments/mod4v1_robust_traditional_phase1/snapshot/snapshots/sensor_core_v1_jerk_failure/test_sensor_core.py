"""Pure numerical/kinematic tests; no mj_step, no hardware IO, no true-statecontrol."""
from pathlib import Path
import unittest,json,math
import numpy as np
from sensor_core import *
ROOT=Path(__file__).resolve().parent;PINS=json.loads((ROOT.parent/'traditional_control_20261101/reports/model_manifest.json').read_bytes())['neutral_skeleton_xz_m']
class Sensors(unittest.TestCase):
 def setUp(self):self.geom=LinkageGeometry(PINS)
 def packet(self,t,omega=(0.,0.,0.),wheel=(0.,0.),offset=(0.,0.,0.),age=0.):
  w=np.asarray(omega);r=np.asarray(offset);a=np.array([0.,0.,G])+np.cross(w,np.cross(w,r));return SensorPacket(t,t+age,w,a,np.array([0.,-.2,0.,-.2]),np.zeros(4),np.asarray(wheel))
 def test_quaternion_roundtrip(self):
  for a in((0.,0.,0.),(.2,-.3,2.),(-.5,.6,-2.8)):np.testing.assert_allclose(rpy(quat_from_rpy(*a)),a,atol=2e-14)
 def test_leverarm_spin_and_alpha(self):
  w=np.array([.4,-.2,4*math.pi]);alpha=np.array([1.,2.,-3.]);r=np.array([.03,-.02,.04]);origin=np.array([1.,2.,9.81]);raw=origin+np.cross(alpha,r)+np.cross(w,np.cross(w,r));np.testing.assert_allclose(compensate_lever_arm(raw,w,alpha,r),origin,atol=1e-13)
 def test_spin_wheel_odometry_not_translation(self):
  w=np.array([0.,0.,4*math.pi]);speeds=[-w[2]*self.geom.track/(2*self.geom.radius),w[2]*self.geom.track/(2*self.geom.radius)]
  for j,s in enumerate(('left','right')):self.assertAlmostEqual(self.geom.wheel_kinematics(0.,-.2,0.,0.,speeds[j],w,s)[0],0.,places=12)
 def test_pitch_rate_and_leg_motion_odometry(self):
  omega=np.array([0.,.7,0.]);h,c=.1,-.3;hd,cd=.4,-.2
  for s in('left','right'):
   r,k=self.geom.pose(h,c,s);eps=1e-6;ra,ka=self.geom.pose(h+eps*hd,c+eps*cd,s);rb,kb=self.geom.pose(h-eps*hd,c-eps*cd,s);relative=(ra-rb)/(2*eps);kdot=wrap(ka-kb)/(2*eps);wanted=1.2;spin=(wanted+relative[0]+np.cross(omega,r)[0])/self.geom.radius-omega[1]-hd-kdot;v,*_=self.geom.wheel_kinematics(h,c,hd,cd,spin,omega,s);self.assertAlmostEqual(v,wanted,places=7)
 def test_yaw_unwrap_4pi_for_ten_seconds(self):
  offset=(.03,-.02,.04);est=StateEstimator(self.geom,offset);rate=4*math.pi;wheels=(-rate*self.geom.track/(2*self.geom.radius),rate*self.geom.track/(2*self.geom.radius))
  for i in range(1000):e=est.update(self.packet(i*.01,(0.,0.,rate),wheels,offset))
  self.assertAlmostEqual(e.state14[1],rate*9.99,places=7);self.assertLess(abs(e.state14[7]),1e-10);self.assertLess(abs(e.state14[2]),1e-10)
 def test_timestamp_prediction_no_extra_initial_tick(self):
  est=StateEstimator(self.geom);rate=1.;wheels=(-rate*self.geom.track/(2*self.geom.radius),rate*self.geom.track/(2*self.geom.radius));a=est.update(self.packet(0.,(0.,0.,rate),wheels,age=.01));self.assertAlmostEqual(a.state14[1],.01,places=10);self.assertAlmostEqual(a.sensor_age_s,.01,places=10)
 def test_bias_noise_not_required_for_nominal_zero(self):
  est=StateEstimator(self.geom)
  for i in range(20):e=est.update(self.packet(i*.01))
  self.assertLess(np.max(np.abs(e.state14[[0,1,2,7,8,9]])),1e-12);self.assertGreater(e.contact_confidence,.99)
 def test_packet_invalid_and_timeout(self):
  with self.assertRaises(ValueError):self.packet(1.,age=-.1).validate()
  est=StateEstimator(self.geom);est.update(self.packet(0.))
  with self.assertRaises(ValueError):est.update(self.packet(.2))
 def test_cmd_shaper_rates(self):
  s=CommandShaper();prev=(0.,0.);a=0.
  for _ in range(300):
   v,w=s.update(2.,4*math.pi,.01);self.assertLessEqual(abs(w-prev[1]),.0800000001);self.assertLessEqual(v,2.+1e-12);self.assertLessEqual(abs(s.a),2.+1e-12);self.assertLessEqual(abs(s.a-a),.1000000001);prev=(v,w);a=s.a
  self.assertAlmostEqual(v,2.);self.assertAlmostEqual(w,4*math.pi)
 def test_combined_envelope_distinction(self):
  no_load=55.3557*.0625;single_spin=4*math.pi*.4376/2;self.assertLess(single_spin,no_load);self.assertLess(2.,no_load);self.assertGreater(2.+single_spin,no_load)
if __name__=='__main__':unittest.main(verbosity=2)
