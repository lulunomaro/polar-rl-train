"""Synthetic sensor vectors only; no contact identity or episode grading."""
import dataclasses,json,math,unittest
import numpy as np
from com_motion import *

EXACT=Config(model_confidence_cap=1.,min_cue_confidence=.5,nominal_COM_position_error_m=0.,nominal_COM_velocity_error_m_s=0.,nominal_COM_acceleration_error_m_s2=0.)
def packet(g,t=0.,**kw):
    q=tuple(g.base.q_nominal)
    s=Sample(t,CORE|Valid.ALPHA|Valid.QDD4,q,(0.,)*4,(0.,0.,9.81),(0.,)*3,'chassis_origin',(0.,)*3,(0.,)*4,(0.,)*4,(0.,)*4,(0.,)*4,(0.,)*3,(0.,)*3,(0.,)*3,1.,1.,1.,(0.,)*2,(0.,)*2,(0.,)*2,(0.,)*2,(0.,)*2,(0.,)*2,None,None,'synthetic_relative_joint_wheel_binding')
    return dataclasses.replace(s,**kw)

class GeometryTests(unittest.TestCase):
    def setUp(self):self.g=Geometry(EXACT)
    def test_COM_mass_weighted_public31body(self):
        q=self.g.base.q_nominal;p=self.g.base.fk(q)
        np.testing.assert_allclose(self.g.com(q,[0,0]),np.sum(self.g.weights[:,None]*p['com_B'],axis=0),atol=1e-14,rtol=0)
    def test_wheel_not_assumed_balanced(self):
        self.assertTrue(all(w['radial_radius_m']>0 for w in self.g.wheels))
        q=self.g.base.q_nominal;a=self.g.com(q,[0,0]);b=self.g.com(q,[math.pi,math.pi]);limit=sum(2*w['weight']*w['radial_radius_m'] for w in self.g.wheels)
        self.assertGreater(float(np.linalg.norm(a-b)),0.);self.assertLessEqual(float(np.linalg.norm(a-b)),limit+1e-16)
    def test_static_motion_is_zero(self):
        m=self.g.motion(self.g.base.q_nominal,np.zeros(4),np.zeros(4));np.testing.assert_allclose(m['rDot_B'],0,atol=1e-12);np.testing.assert_allclose(m['rDDot_B'],0,atol=1e-10)
    def test_linear_acceleration_and_convective_both_present(self):
        m=self.g.motion(self.g.base.q_nominal,[.4,-.3,.35,-.2],[.1,.2,-.15,.25],[.2,-.3],[10.,-20.],[30.,-40.])
        self.assertGreater(np.linalg.norm(m['acceleration_linear_part_B']),1e-5);self.assertGreater(np.linalg.norm(m['convective_part_B']),1e-5)
        np.testing.assert_allclose(m['rDDot_B'],m['acceleration_linear_part_B']+m['convective_part_B'],atol=1e-12)
    def test_public_joint_domain_not_silently_clipped(self):
        with self.assertRaises(ModelDomainError):self.g.com([2,0,0,0],[0,0])

class VectorTests(unittest.TestCase):
    def setUp(self):self.o=MovingCOM(EXACT);self.g=self.o.geometry
    def test_pure_translation_no_lever_changes(self):
        s=packet(self.g,proper_origin_B3=(1.,2.,9.81));r=self.o.update(s,0.)
        np.testing.assert_allclose(r.proper_COM_B3,[1,2,9.81],atol=1e-10);self.assertEqual(r.cue,Cue.COM_NONFREEFALL_LIKE)
    def test_rotating_freefall_origin_nonzero_not_a_failure(self):
        q=self.g.base.q_nominal;r=self.g.com(q,[0,0]);w=np.array([0.,0.,4*math.pi]);a=np.array([.2,-.3,.1]);origin=-np.cross(a,r)-np.cross(w,np.cross(w,r))
        self.assertGreater(np.linalg.norm(origin),2.5)
        out=self.o.update(packet(self.g,proper_origin_B3=tuple(origin),omega_B3=tuple(w),alpha_B3=tuple(a)),0.)
        np.testing.assert_allclose(out.proper_COM_B3,0.,atol=1e-9);self.assertEqual(out.cue,Cue.COM_FREEFALL_LIKE)
    def test_moving_COM_full_coriolis_and_rddot_cancellation(self):
        q=self.g.base.q_nominal;v=np.array([.4,-.3,.35,-.2]);a=np.array([.1,.2,-.15,.25]);w=np.array([.3,-.2,4.]);alpha=np.array([.1,.3,-.2]);phi=np.array([.2,-.3]);wr=np.array([20.,-25.]);wa=np.array([100.,-200.]);m=self.g.motion(q,v,a,phi,wr,wa)
        tang=np.cross(alpha,m['r_B']);cent=np.cross(w,np.cross(w,m['r_B']));cor=2*np.cross(w,m['rDot_B']);origin=-tang-cent-cor-m['rDDot_B']
        self.assertGreater(np.linalg.norm(cor),1e-6);self.assertGreater(np.linalg.norm(m['rDDot_B']),1e-6)
        s=packet(self.g,qd4=tuple(v),qdd4=tuple(a),proper_origin_B3=tuple(origin),omega_B3=tuple(w),alpha_B3=tuple(alpha),wheel_angle2=tuple(phi),wheel_rate2=tuple(wr),wheel_acc2=tuple(wa))
        out=self.o.update(s,0.);np.testing.assert_allclose(out.proper_COM_B3,0.,atol=1e-8);self.assertEqual(out.cue,Cue.COM_FREEFALL_LIKE)
    def test_guide_supported_fixture_nonfreefall_not_identity(self):
        out=self.o.update(packet(self.g),0.);self.assertEqual(out.cue,Cue.COM_NONFREEFALL_LIKE)
        self.assertFalse(hasattr(out,'contact_identity'));self.assertFalse(hasattr(out,'all_surfaces_air'))
    def test_origin_zero_not_automatically_COM_zero(self):
        out=self.o.update(packet(self.g,proper_origin_B3=(0.,0.,0.),omega_B3=(0.,0.,4*math.pi)),0.)
        self.assertGreater(np.linalg.norm(out.nominal_corrected_estimate_B3),2.5);self.assertNotEqual(out.cue,Cue.COM_FREEFALL_LIKE)
    def test_missing_wheel_state_unbounded_is_uncertain(self):
        s=packet(self.g,wheel_binding_id='',wheel_angle2=None,wheel_rate2=None,wheel_acc2=None)
        out=self.o.update(s,0.);self.assertIsNone(out.proper_COM_B3);self.assertEqual(out.cue,Cue.UNCERTAIN);self.assertFalse(out.wheel_missing_bound['finite_declared_nominal_wheel_bound'])
    def test_missing_wheel_motion_has_explicit_geometric_bound(self):
        s=packet(self.g,wheel_binding_id='',wheel_angle2=None,wheel_rate2=None,wheel_acc2=None,wheel_rate_abs_bound_rad_s2=(60.,60.),wheel_acc_abs_bound_rad_s22=(10000.,10000.))
        out=self.o.update(s,0.);self.assertTrue(out.wheel_missing_bound['finite_declared_nominal_wheel_bound']);self.assertIsNotNone(out.proposed_error_radius_m_s2)
        self.assertTrue(all(x['nominal_radial_COM_eccentricity_m']>0 for x in out.wheel_missing_bound['wheels']))
    def test_missing_value_error_zero_does_not_fake_measured_wheel(self):
        s=packet(self.g,wheel_rate2=None,wheel_acc2=None,wheel_rate_error_rad_s2=(0.,0.),wheel_acc_error_rad_s22=(0.,0.))
        out=self.o.update(s,0.);self.assertEqual(out.cue,Cue.UNCERTAIN)
    def test_unbound_error_or_calibration_not_forced_point8(self):
        out=self.o.update(packet(self.g,derivative_confidence=.2),0.);self.assertLess(out.confidence,.8);self.assertEqual(out.cue,Cue.UNCERTAIN)
        self.o=MovingCOM(EXACT);out=self.o.update(packet(self.g,qdd_error_rad_s24=None),0.);self.assertEqual(out.cue,Cue.UNCERTAIN)
    def test_reference_and_truth_kwargs_rejected(self):
        s=packet(self.g)
        with self.assertRaises(TypeError):dataclasses.replace(s,rootGT=[0,0,0])
        self.assertEqual(self.o.update(dataclasses.replace(s,proper_reference='imu_site'),0.).cue,Cue.UNCERTAIN)
    def test_nonfinite_time_and_vectors_uncertain(self):
        for kw in [dict(q4=(math.nan,0,0,0)),dict(proper_origin_B3=(math.inf,0,0))]:
            out=MovingCOM(EXACT).update(packet(self.g,**kw),0.);self.assertEqual(out.cue,Cue.UNCERTAIN)
    def test_duplicate_time_does_not_reuse_new_confidence(self):
        s=packet(self.g);self.o.update(s,0.);self.assertEqual(self.o.update(s,0.).cue,Cue.UNCERTAIN)
    def test_joint_motion_stencil_domain_becomes_uncertain(self):
        s=packet(self.g,q4=(.49999,.2,.49999,.2),qd4=(10.,0.,10.,0.))
        self.assertEqual(self.o.update(s,0.).cue,Cue.UNCERTAIN)
    def test_output_JSON_finite_and_no_actuation(self):
        out=self.o.update(packet(self.g),0.);json.dumps(dataclasses.asdict(out),allow_nan=False);self.assertFalse(hasattr(out,'torque'));self.assertFalse(hasattr(out,'CAN'))

class DerivativeTests(unittest.TestCase):
    def test_sensor_difference_value_but_unbound_jerk_uncertain(self):
        o=MovingCOM(EXACT);g=o.geometry
        base=packet(g,valid_bits=CORE,alpha_B3=None,qdd4=None)
        self.assertEqual(o.update(base,0.).cue,Cue.UNCERTAIN)
        s=dataclasses.replace(base,timestamp_s=.01,qd4=(.1,0.,0.,0.),omega_B3=(0.,0.,.01));out=o.update(s,.01)
        self.assertEqual(out.cue,Cue.UNCERTAIN);self.assertIsNone(out.derivative_metadata['qdd_error_bound4']);self.assertEqual(out.derivative_metadata['qdd_midpoint_lag_s'],.005)
    def test_noisy_qdot_difference_has_large_declared_error(self):
        c=dataclasses.replace(EXACT,min_cue_confidence=.6,qdd_jerk_abs_bound_rad_s34=(100.,)*4,angular_jerk_abs_bound_rad_s33=(20.,)*3);o=MovingCOM(c);g=o.geometry
        s=packet(g,valid_bits=CORE,alpha_B3=None,qdd4=None,qd_error_rad_s4=(.25,)*4,omega_error_rad_s3=(.003,)*3)
        o.update(s,0.);out=o.update(dataclasses.replace(s,timestamp_s=.01,qd4=(.25,-.25,.25,-.25)),.01)
        self.assertGreaterEqual(out.derivative_metadata['qdd_error_bound4'][0],50.);self.assertEqual(out.cue,Cue.UNCERTAIN);self.assertLess(out.confidence,.8)
    def test_stale_gap_and_invalid_mask_uncertain(self):
        o=MovingCOM(EXACT);s=packet(o.geometry)
        self.assertEqual(o.update(s,.1).cue,Cue.UNCERTAIN)
        self.assertEqual(o.update(dataclasses.replace(s,valid_bits=-1),0.).cue,Cue.UNCERTAIN)
    def test_invalid_config_no_hidden_acceptance(self):
        with self.assertRaises(ValueError):Config(model_confidence_cap=math.nan)
        with self.assertRaises(ValueError):Config(min_dt_s=.1)

if __name__=='__main__':unittest.main(verbosity=2)
