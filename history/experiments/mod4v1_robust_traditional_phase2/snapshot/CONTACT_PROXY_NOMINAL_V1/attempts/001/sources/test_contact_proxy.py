"""Nominal math/synthetic sensors only. No episode or contact identity oracle."""
import dataclasses,json,math,unittest
import numpy as np
from nominal_model import NominalModel,ModelDomainError
from contact_proxy import *

class AlgebraTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.m=NominalModel()
    def terms(self,proper=(0.,0.,9.81)):
        return self.m.terms(self.m.q_nominal,np.zeros(4),np.zeros(4),proper,np.zeros(3),np.zeros(3))
    def test_public31body_mass_and_immutable_parameters(self):
        self.assertEqual(len(self.m.bodies),31);self.assertAlmostEqual(self.m.mass.sum(),14.294140288606286)
        with self.assertRaises(ValueError):self.m.mass[0]=1.
        with self.assertRaises(TypeError):self.m.public['bodies'][0]['pos_m'][0]=1.
    def test_nominal_ff_emerges_near70_not_hardcoded_half_weight(self):
        t=self.terms();f=self.m.solve_terms(t,self.m.tau_nominal)['force_body_xz_N2']
        np.testing.assert_allclose(f[:,1],[70.0574160121,70.1681001878],atol=1e-5,rtol=0)
        self.assertLess(max(abs(f[:,0])),1e-5);self.assertAlmostEqual(f[:,1].sum(),self.m.mass.sum()*9.81,places=5)
    def test_zero_proper_does_not_add_static_gravity(self):
        t=self.terms((0.,)*3);np.testing.assert_allclose(t['load4'],0.,atol=1e-12)
        tau=-t['tauGas4']-t['tauOtherPassive4'];f=self.m.solve_terms(t,tau)['force_body_xz_N2'];np.testing.assert_allclose(f,0.,atol=1e-10)
    def test_unknown_force_not_estimated_by_half_weight(self):
        t=self.terms();a=self.m.solve_terms(t,self.m.tau_nominal)['force_body_xz_N2'];b=self.m.solve_terms(t,self.m.tau_nominal+np.array([1.,-1.,0.,0.]))['force_body_xz_N2']
        self.assertGreater(np.max(abs(a-b)),1.)
    def test_known_synthetic_force_sign_and_virtual_work(self):
        for Fx,Fz in [(0.,0.),(8.,50.),(-12.,90.),(0.,-5.)]:
            with self.subTest(Fx=Fx,Fz=Fz):
                t=self.terms();known=np.array([[Fx,Fz],[-Fx,Fz+3.]])
                tau=t['load4']-t['tauGas4']-t['tauOtherPassive4']
                for i,J in enumerate(t['Jwheel_xz2']):tau[2*i:2*i+2]-=J.T@known[i]
                np.testing.assert_allclose(self.m.solve_terms(t,tau)['force_body_xz_N2'],known,atol=1e-9,rtol=0)
    def test_effective_potential_gradient(self):
        q=self.m.q_nominal;p=np.array([.3,0.,9.7]);t=self.terms(p);gradient=[]
        for k in range(4):
            d=np.zeros(4);d[k]=self.m.h;gradient.append((self.m.potential(q+d,p)-self.m.potential(q-d,p))/(2*self.m.h))
        np.testing.assert_allclose(gradient,t['load_linear4'],atol=1e-7,rtol=0)
    def test_gas_virtual_work(self):
        q=self.m.q_nominal;t=self.terms();a=np.array([.1,-.2,.2,-.15]);D=t['jacobians']['Djoint'];gas=t['gas_scalar_force_N2']
        self.assertAlmostEqual(float(t['tauGas4']@a),float(gas@(D[self.m.gas_ids]@a)),places=10)
    def test_dynamic_synthetic_equation_not_full_RNE_claim(self):
        q=self.m.q_nominal;v=np.array([.1,-.2,.15,-.1]);a=np.array([.2,-.1,.3,-.2]);t=self.m.terms(q,v,a,[.3,.1,9.6],[.2,-.1,.3],[.4,.1,-.2]);known=np.array([[5.,60.],[-4.,80.]])
        tau=t['load4']-t['tauGas4']-t['tauOtherPassive4']
        for i,J in enumerate(t['Jwheel_xz2']):tau[2*i:2*i+2]-=J.T@known[i]
        np.testing.assert_allclose(self.m.solve_terms(t,tau)['force_body_xz_N2'],known,atol=1e-9,rtol=0)
    def test_solver_condition_guard(self):
        t=dict(self.terms());t['Jwheel_xz2']=[np.array([[1.,0.],[0.,1e-12]]),np.eye(2)]
        with self.assertRaises(ModelDomainError):self.m.solve_terms(t,self.m.tau_nominal)
    def test_pose_domain_rejected_not_clipped(self):
        with self.assertRaises(ModelDomainError):self.m.fk((2.,0.,0.,0.))

class SensorHarness:
    def __init__(self,c=None):
        self.ob=ContactProxy(c or Config(execution_context='synthetic_fixture',allow_nominal_design_fixture=True));self.t=-.01
    def packet(self,**kw):
        self.t=round(self.t+.01,9);m=self.ob.model
        p=SensorInput(self.t,self.t,self.t,ALL_VALID,tuple(m.q_nominal),(0.,)*4,tuple(m.tau_nominal),(0.,0.,9.81),(0.,)*3,(0.,)*3,TorqueDomain.NOMINAL_DESIGN_OUTPUT_FIXTURE,'nominal_sim_design_not_calibration',True,False,'chassis_origin',(1.,)*4,(.02,)*4,1.,1.,1.,1.,(.002,)*4)
        return dataclasses.replace(p,**kw)
    def step(self,**kw):p=self.packet(**kw);return self.ob.step(p,self.t)
    def warm(self,**kw):
        for _ in range(4):r=self.step(**kw)
        return r

class ObserverTests(unittest.TestCase):
    def test_warmup_unknown_never_fake_zero(self):
        h=SensorHarness();r=h.step();self.assertEqual(r.normal_proxy_N2,(None,None));self.assertEqual(r.confidence2,(0.,0.))
    def test_nominal_sensor_fixture_low_confidence_model_not_sensor(self):
        h=SensorHarness();r=h.warm();np.testing.assert_allclose(r.normal_proxy_N2,[70.057416,70.168100],atol=1e-5)
        self.assertTrue(all(.2<=x<=.55 for x in r.confidence2));self.assertIn('DESIGN_TORQUE_FIXTURE_NOT_MEASURED_CALIBRATION',r.common_reasons)
    def test_default_design_torque_not_measured(self):
        h=SensorHarness(Config());r=h.warm();self.assertEqual(r.normal_proxy_N2,(None,None));self.assertIn('DESIGN_EFFORT_NOT_MEASURED_CALIBRATION',r.common_reasons)
    def test_measurement_domain_requires_declared_calibration(self):
        h=SensorHarness();r=h.warm(torque_domain=TorqueDomain.MEASURED_JOINT_OUTPUT_NM);self.assertEqual(r.normal_proxy_N2,(None,None));self.assertIn('MEASURED_OUTPUT_TORQUE_CALIBRATION_UNBOUND',r.common_reasons)
    def test_unknown_sign_and_rotor_domain_not_converted_silently(self):
        for kw in [dict(torque_sign_verified=False),dict(torque_domain=TorqueDomain.UNKNOWN),dict(torque_binding_id='')]:
            with self.subTest(kw=kw):self.assertEqual(SensorHarness().warm(**kw).normal_proxy_N2,(None,None))
    def test_proper_reference_must_be_root_not_imu_or_COM(self):
        for ref in ['imu_site','whole_robot_COM','unbound']:
            with self.subTest(ref=ref):self.assertEqual(SensorHarness().warm(proper_reference=ref).normal_proxy_N2,(None,None))
    def test_low_alpha_confidence_returns_unknown(self):
        h=SensorHarness();r=h.warm(alpha_confidence=.1);self.assertEqual(r.normal_proxy_N2,(None,None));self.assertIn('ENCODER_OR_IMU_CALIBRATION_ALPHA_UNTRUSTED',r.common_reasons)
    def test_large_alpha_and_omega_untrusted(self):
        for kw in [dict(alpha_B_rad_s2=(0.,0.,200.)),dict(omega_B_rad_s=(30.,0.,0.))]:
            with self.subTest(kw=kw):
                r=SensorHarness().warm(**kw);self.assertEqual(r.normal_proxy_N2,(None,None))
    def test_legdd_noise_unknown(self):
        r=SensorHarness().warm(encoder_qd_sigma4=(1.,)*4);self.assertEqual(r.normal_proxy_N2,(None,None));self.assertIn('LEG_DD_NOISE_UNTRUSTED',r.common_reasons)
    def test_qd_noise_unbound_reduces_confidence(self):
        a=SensorHarness().warm();b=SensorHarness().warm(encoder_qd_sigma4=(None,)*4)
        self.assertLess(b.confidence2[0],a.confidence2[0]);self.assertIn('QD_NOISE_UNBOUND_CONFIDENCE_REDUCED',b.common_reasons)
    def test_torque_sigma_unbound_is_unknown(self):
        r=SensorHarness().warm(torque_sigma_Nm4=(None,)*4);self.assertEqual(r.normal_proxy_N2,(None,None))
    def test_one_leg_unknown_is_not_zero_and_other_independent(self):
        h=SensorHarness();tau=list(h.ob.model.tau_nominal);tau[0]=None;r=h.warm(output_motor_tau4=tuple(tau));self.assertIsNone(r.normal_proxy_N2[0]);self.assertAlmostEqual(r.normal_proxy_N2[1],70.1681,places=4)
    def test_stale_or_skew_channels_unknown(self):
        h=SensorHarness();h.warm();p=h.packet();r=h.ob.step(dataclasses.replace(p,torque_timestamp_s=p.timestamp_s-.01),h.t);self.assertEqual(r.normal_proxy_N2,(None,None))
    def test_duplicate_does_not_refresh_derivative_history(self):
        h=SensorHarness();h.warm();p=h.packet();h.ob.step(p,h.t);r=h.ob.step(p,h.t);self.assertEqual(r.normal_proxy_N2,(None,None));self.assertIn('SAMPLE_TIME_REPLAY_OR_ROLLBACK',r.common_reasons)
    def test_valid_stream_recovers_after_gap_with_new_warmup(self):
        h=SensorHarness();h.warm();h.t+=.1;r=h.step();self.assertIsNone(r.normal_proxy_N2[0])
        r=h.warm();self.assertIsNotNone(r.normal_proxy_N2[0])
    def test_validity_and_nonfinite_unknown(self):
        for kw in [dict(valid_bits=Valid.Q4),dict(proper_root_B_m_s2=(float('nan'),0.,0.))]:
            with self.subTest(kw=kw):self.assertEqual(SensorHarness().warm(**kw).normal_proxy_N2,(None,None))
    def test_negative_compression_not_converted_to_zero_support(self):
        h=SensorHarness();m=h.ob.model;t=m.terms(m.q_nominal,np.zeros(4),np.zeros(4),[0,0,9.81],[0,0,0],[0,0,0]);tau=t['load4']-t['tauGas4']-t['tauOtherPassive4']
        for i,J in enumerate(t['Jwheel_xz2']):tau[2*i:2*i+2]-=J.T@np.array([0.,-5.])
        r=h.warm(output_motor_tau4=tuple(tau));self.assertEqual(r.normal_proxy_N2,(None,None));self.assertIn('NEGATIVE_COMPRESSION_NOT_SUPPORT',r.reasons2[0])
    def test_consistent_zero_proper_zero_force_algebra_not_flight_claim(self):
        h=SensorHarness();m=h.ob.model;t=m.terms(m.q_nominal,np.zeros(4),np.zeros(4),[0,0,0],[0,0,0],[0,0,0]);tau=-t['tauGas4']-t['tauOtherPassive4'];r=h.warm(output_motor_tau4=tuple(tau),proper_root_B_m_s2=(0.,)*3)
        np.testing.assert_allclose(r.model_force_body_xz_N2,0.,atol=1e-8);self.assertTrue(all(x<=.55 for x in r.confidence2));self.assertFalse(hasattr(r,'airborne_truth'))
    def test_no_whole_robot_air_or_contact_identity_claim(self):
        r=SensorHarness().warm();self.assertIn('ONLY_WHEEL_CENTER_LOAD_PATH_ASSUMED_GUIDE_NONWHEEL_SUPPORT_UNOBSERVED',r.common_reasons)
    def test_truth_or_DR_kwargs_rejected(self):
        h=SensorHarness();p=h.packet()
        for key in ['contacts','root_world_xyz','actual_mass_DR','step_top_truth']:
            with self.subTest(key=key):
                with self.assertRaises(TypeError):dataclasses.replace(p,**{key:0})
    def test_results_strict_JSON_and_no_actuation(self):
        r=SensorHarness().warm();json.dumps(dataclasses.asdict(r),allow_nan=False);self.assertFalse(hasattr(r,'motor_command'));self.assertFalse(hasattr(r,'CAN'))
    def test_proposed_configs_reject_inconsistent_context(self):
        for kw in [dict(allow_nominal_design_fixture=True),dict(nominal_model_confidence_cap=math.nan),dict(min_dt_s=.2),dict(condition_soft=1000.)]:
            with self.subTest(kw=kw):
                with self.assertRaises(ValueError):Config(**kw)

if __name__=='__main__':unittest.main(verbosity=2)
