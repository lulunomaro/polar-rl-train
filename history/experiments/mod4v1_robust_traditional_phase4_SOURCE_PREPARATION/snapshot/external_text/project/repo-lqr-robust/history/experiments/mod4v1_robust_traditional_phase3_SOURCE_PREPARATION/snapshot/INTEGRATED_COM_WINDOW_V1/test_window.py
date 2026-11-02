"""Synthetic continuous-signal fixtures, never physics/true capture grading."""
import inspect,math,unittest
import numpy as np
from window_math import *

class Tests(unittest.TestCase):
    def test_rotation_integral_exact_constant_model(self):
        w=np.array([2.,-3.,4.]);h=.1;S=integrated_rotation(w,h);n=2000;t=np.linspace(0,h,n+1);mat=np.array([exp_rotation(w,x) for x in t]);numerical=h/n/3*(mat[0]+mat[-1]+4*mat[1:-1:2].sum(0)+2*mat[2:-1:2].sum(0));np.testing.assert_allclose(S,numerical,atol=1e-13,rtol=0)
    def test_midpoint_transport_is_not_claimed_exact(self):
        w=[0,0,10.];h=.1;self.assertGreater(np.linalg.norm(integrated_rotation(w,h)-h*exp_rotation(w,h/2)),1e-3)
    def test_static_and_gravity_not_added_twice(self):
        for f in ([0,0,9.81],[0,0,0],[1,2,3]):
            out=piecewise_constant_window([[0,0,0]]*5,[f]*5,[.01]*5,[0,0,0],[0,0,0]);np.testing.assert_allclose(out['average_COM_proper_start_frame3'],f,atol=1e-12);self.assertAlmostEqual(out['nominal_midpoint_age_s'],.025)
    def test_rigid_spinning_freefall_box_identity(self):
        w=np.array([0,0,4*math.pi]);r=np.array([-.0342,-.00017,-.07035]);s=np.array([.03,0,.04]);rho=r-s;f=-np.cross(w,np.cross(w,rho));u=np.cross(w,rho)
        self.assertGreater(np.linalg.norm(f),5.)
        for n in (5,10,15):
            o=piecewise_constant_window([w]*n,[f]*n,[.01]*n,u,u);np.testing.assert_allclose(o['average_COM_proper_start_frame3'],0.,atol=1e-11)
    def test_moving_COM_and_constant_netforce(self):
        w=np.array([.3,-.4,4.]);s=np.array([.03,0,.04]);base=np.array([-.0342,-.00017,-.07035]);A=np.array([.01,.005,.008]);nu=6.;F=np.array([1.,-.2,3.]);h=.0005
        for T in (.05,.1,.15):
            ts=np.arange(round(T/h)+1)*h;gyro=[];forces=[];us=[]
            for t in ts:
                r=base+A*np.sin(nu*t);rd=A*nu*np.cos(nu*t);rdd=-A*nu*nu*np.sin(nu*t);R=exp_rotation(w,t)
                full=np.cross(w,np.cross(w,r-s))+2*np.cross(w,rd)+rdd;forces.append(R.T@F-full);gyro.append(w);us.append(relative_velocity(w,r,rd,s))
            out=point_series_window(gyro,forces,h,us[0],us[-1]);np.testing.assert_allclose(out['average_COM_proper_start_frame3'],F,atol=1e-8,rtol=0)
    def test_public31body_movingleg_full_rDDot_in_boundary(self):
        from DYNAMIC_COM_MOTION_V1.com_motion import Geometry
        g=Geometry();q0=g.base.q_nominal;A=np.array([.01,-.008,.012,-.007]);nu=5.;w=np.array([0.,0.,4.]);s=np.array([.03,0,.04]);F=np.array([.5,.1,2.]);h=.0005;T=.1;gyro=[];f=[];us=[]
        for t in np.arange(round(T/h)+1)*h:
            q=q0+A*np.sin(nu*t);v=A*nu*np.cos(nu*t);a=-A*nu*nu*np.sin(nu*t);m=g.motion(q,v,a);rho=m['r_B']-s;full=np.cross(w,np.cross(w,rho))+2*np.cross(w,m['rDot_B'])+m['rDDot_B'];f.append(exp_rotation(w,t).T@F-full);gyro.append(w);us.append(relative_velocity(w,m['r_B'],m['rDot_B'],s))
        out=point_series_window(gyro,f,h,us[0],us[-1]);np.testing.assert_allclose(out['average_COM_proper_start_frame3'],F,atol=2e-6,rtol=0)
    def test_pointwise_expansion_contains_alpha_and_2coriolis(self):
        r0=np.array([.02,-.01,-.1]);s=np.array([.03,0,.04]);A=np.array([.01,.005,-.01]);nu=3.;acc=2.;t=.23;eps=1e-6
        def sample(z):
            r=r0+A*np.sin(nu*z);rd=A*nu*np.cos(nu*z);w=np.array([0,0,acc*z]);R=exp_rotation([0,0,1.],.5*acc*z*z);return R,relative_velocity(w,r,rd,s)
        Rp,up=sample(t+eps);Rm,um=sample(t-eps);num=(Rp@up-Rm@um)/(2*eps);r=r0+A*np.sin(nu*t);rd=A*nu*np.cos(nu*t);rdd=-A*nu*nu*np.sin(nu*t);w=np.array([0,0,acc*t]);alpha=np.array([0,0,acc]);R,u=sample(t);full=R@(np.cross(alpha,r-s)+np.cross(w,np.cross(w,r-s))+2*np.cross(w,rd)+rdd);np.testing.assert_allclose(num,full,atol=1e-9)
    def test_body_basis_change_vector_covariance_and_norm_invariance(self):
        Q=exp_rotation([.7,-.3,.8],.8);w=np.array([.2,.3,4.]);f=np.array([1.,2.,8.]);u0=np.array([.2,-.1,.03]);u1=np.array([.3,-.05,-.02]);a=piecewise_constant_window([w]*10,[f]*10,[.01]*10,u0,u1);b=piecewise_constant_window([Q@w]*10,[Q@f]*10,[.01]*10,Q@u0,Q@u1)
        np.testing.assert_allclose(b['average_COM_proper_start_frame3'],Q@a['average_COM_proper_start_frame3'],atol=1e-12);self.assertAlmostEqual(np.linalg.norm(a['average_COM_proper_start_frame3']),np.linalg.norm(b['average_COM_proper_start_frame3']),places=12)
    def test_unknown_world_rotation_is_only_constant_left_rotation(self):
        out=piecewise_constant_window([[0,0,1.]]*5,[[1,0,9.81]]*5,[.01]*5,[0,0,0],[0,0,0]);C=exp_rotation([.3,.7,-.2],1.);y=out['average_COM_proper_start_frame3'];self.assertAlmostEqual(np.linalg.norm(C@y),np.linalg.norm(y),places=12)
    def test_no_alpha_qdd_or_true_attitude_argument(self):
        names=set(inspect.signature(piecewise_constant_window).parameters)|set(inspect.signature(EndpointModel.evaluate).parameters)
        self.assertFalse(names & {'alpha','qdd','rootGT','R_world','yaw_truth'})
    def test_noise_not_reduced_by_N_and_boundary_error_scales_inverseT(self):
        e={'u_B3':np.zeros(3),'u_error_norm_m_s':.1,'omega_B3':np.zeros(3)};noise=[];bound=[]
        for n in (5,10,15):
            out=piecewise_constant_window([[0,0,0]]*n,[[0,0,9.81]]*n,[.01]*n,[0,0,0],[0,0,0]);b=capture_budget(out,e,e,[[0,0,9.81]]*n,[.01]*n);noise.append(b['proper_noise_not_reduced_with_N_m_s2']);bound.append(b['boundary_endpoint_error_m_s2']);self.assertEqual(b['conditional_cue'],0);self.assertLess(b['conditional_confidence'],.60)
        np.testing.assert_allclose(noise,[noise[0]]*3,atol=0);np.testing.assert_allclose(bound,[4.,2.,4/3],atol=1e-12)
    def test_fixed_body_bias_does_not_magically_cancel(self):
        w=np.array([0,0,4.]);T=.1;R=exp_rotation(w,T);b=np.array([.005,0,0]);M=(R@skew(w)-skew(w))/T;explicit=(R@np.cross(w,b)-np.cross(w,b))/T;np.testing.assert_allclose(M@b,explicit,atol=1e-14);self.assertGreater(np.linalg.norm(explicit),0.)
    def test_correlated_raw_proposal_mean_identity_not_IID_gain(self):
        rng=np.random.default_rng(1203);clean=rng.normal(size=(20,3));offset=np.array([.1,-.2,.3]);noisy=clean+offset
        np.testing.assert_allclose(noisy.mean(0),clean.mean(0)+offset,atol=1e-15);np.testing.assert_allclose(np.diff(noisy,axis=0),np.diff(clean,axis=0),atol=1e-15)
        self.assertFalse(np.array_equal(noisy-clean,np.zeros_like(noisy)))
    def test_box_temporal_distance_33375us(self):
        samples=np.arange(20)*.0005;L=.01;exact=np.mean([(x*x+(L-x)**2)/(2*L) for x in samples]);self.assertAlmostEqual(exact,.0033375,places=12)
    def test_bad_bin_schema_rejected(self):
        with self.assertRaises(ValueError):piecewise_constant_window([[0,0,0]],[[0,0,9.81]],[-1],[0,0,0],[0,0,0])

if __name__=='__main__':unittest.main(verbosity=2)
