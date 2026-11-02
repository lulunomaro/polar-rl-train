"""Synthetic metadata/model tests only, no physical replay or original trace."""
import copy,math,unittest
import numpy as np
from shadow_audit import *

def row(t=0,index=0,duplicate=False):
    mean=t>0;g=Geometry();q=g.base.q_nominal;dq=[0.]*4;wheel=[0.,0.]
    p={'sampled_us':t,'arrival_us':t,'channel_epoch_us':[t]*4,'sequence':t//10000+1,'flags':1,'coherent':1,'window_begin_us':t-10000 if mean else t,'mean_weight_sum_us':10000 if mean else 0,'expected_count':20 if mean else 1,'valid_count':20 if mean else 1,'dropped_count':0,'mean_mode':1 if mean else 0,'mean_valid':1,'mean_weights_valid':1 if mean else 0,'gyro_body':[0.,0.,0.],'proper_accel_body':[0.,0.,9.81],'joint_q4':q.tolist(),'joint_dq4':dq,'wheel_spin2':wheel}
    return {'capture_index':index,'packet':p,'command':{'issued_us':t,'expires_us':t+10000,'sequence':index+1,'flags':1,'enable':1,'forward_m_s':0.,'yaw_rad_s':0.},'drive_feedback':{'sampled_us':t,'flags':1,'velocity_row6':[0.]*6},'reference':'canonicalchassisBODY/loadsideSI','provenance':'synthetic schema unit not hardware calibration','channel_epoch_semantics':'sharedqueueepoch_notinstantaneoussampling; meanwindowmetadataexplicit','wheel_phase_bound':False}

class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.v4,_=load_v4();cls.noise,_=public_noise()
    def test_public_D1_source_not_episode(self):self.assertEqual(self.noise,{'omega3':.125,'gravity3':.025,'legq4':.005,'legqd4':.25,'wheelqd2':.5})
    def test_projection_extra_truth_key_rejected(self):
        r=row();r['rootGT']=[0,0,0]
        with self.assertRaises(ValueError):validate(r)
    def test_nested_extra_truth_key_rejected(self):
        r=row();r['packet']['contact']=[1,1]
        with self.assertRaises(ValueError):validate(r)
    def test_epoch_mean_center_aperture_not_instant(self):
        w=window(validate(row(10000)));self.assertEqual(w['center_us'],4750.);self.assertEqual(w['last_us'],9500);self.assertEqual(w['aperture_span_us'],9500);self.assertAlmostEqual(w['variance_time_s2'],8.3125e-6)
        self.assertEqual(w['q_end_to_center_s'],.00525)
    def test_derivative_kernel_lag_exact(self):self.assertAlmostEqual(derivative_abs_lag_s(.01,window(row(20000)['packet'])),.005415625,places=12)
    def test_boot_instant_to_mean_reset(self):
        s=Shadow(self.noise,Assumptions(),self.v4);a=s.row(row());b=s.row(row(10000,1));self.assertEqual(a['conditional']['cue'],0);self.assertIn('INSTANT_TO_MEAN',b['conditional']['reasons'][0]);self.assertNotIn('qdd_FD4',b['conditional'])
    def test_duplicate_epoch_no_derivative_no_new_alpha(self):
        s=Shadow(self.noise,Assumptions(),self.v4);r=row();s.row(r);dup=copy.deepcopy(r);dup['capture_index']=1;dup['packet']['arrival_us']=10000;dup['command']['issued_us']=10000;dup['command']['expires_us']=20000;o=s.row(dup)
        self.assertTrue(o['clock']['duplicate_epoch_no_new_derivative']);self.assertEqual(o['frozenV4_baseline']['alpha_LP60ms_B3'],[0.,0.,0.]);self.assertNotIn('qdd_FD4',o['conditional'])
    def test_duplicate_changed_sensor_payload_rejected(self):
        s=Shadow(self.noise,Assumptions(),self.v4);r=row();s.row(r);r=copy.deepcopy(r);r['packet']['arrival_us']=10000;r['packet']['proper_accel_body'][0]=1.
        with self.assertRaises(ValueError):s.row(r)
    def test_D1_noise_not_divided_by20_and_no_confidence_bump(self):
        s=Shadow(self.noise,Assumptions(),self.v4);s.row(row());s.row(row(10000,1));o=s.row(row(20000,2));e=o['conditional']['error_assumptions']
        self.assertGreaterEqual(e['qdd_axis_rad_s2'],50.);self.assertGreaterEqual(e['alpha_axis_rad_s2'],25.);self.assertLessEqual(o['conditional']['confidence'],.5);self.assertEqual(o['conditional']['cue'],0)
        self.assertEqual(s.model.c.min_cue_confidence,.60)
    def test_position_retarget_sign_constant_acceleration(self):
        s=Shadow(self.noise,Assumptions(),self.v4);g=s.geom;q0=g.base.q_nominal;v0=np.array([.1,.1,.1,.1]);a=np.array([.5,.5,.5,.5]);s.row(row())
        for i,t in enumerate((10000,20000),1):
            r=row(t,i);c=(t-5250)/1e6;end=t/1e6;vel=v0+a*c;r['packet']['joint_q4']=(q0+v0*end+.5*a*end*end).tolist();r['packet']['joint_dq4']=vel.tolist();r['drive_feedback']['velocity_row6']=[vel[0],vel[1],0.,vel[2],vel[3],0.];o=s.row(r)
        expected=q0+v0*.01475+.5*a*.01475**2
        np.testing.assert_allclose(o['conditional']['q4_window_center_model'],expected,atol=1e-12);np.testing.assert_allclose(o['conditional']['qdd_FD4'],a,atol=1e-12)
    def test_lever_source_conversion_is_IMU_to_origin(self):
        s=Shadow(self.noise,Assumptions(),self.v4);s.row(row());s.row(row(10000,1));r=row(20000,2);r['packet']['gyro_body']=[0.,0.,.01];o=s.row(r);alpha=np.array([0.,0.,1.]);omega=np.array([0.,0.,.01]);lever=np.array([.03,0,.04]);expected=np.array([0.,0.,9.81])-np.cross(alpha,lever)-np.cross(omega,np.cross(omega,lever));np.testing.assert_allclose(o['conditional']['proper_origin_window_center_model_B3'],expected,atol=1e-12)
    def test_source_reader_rejects_original_case_before_open(self):
        with self.assertRaises(AssertionError):read_evidence(TASK/'results/ORIGINAL/trace.jsonl',{PROJ/'MANIFEST.json'})
    def test_drive_domain_not_hidden_truth_velocity(self):
        r=row();r['drive_feedback']['velocity_row6'][0]=1.
        with self.assertRaises(ValueError):validate(r)
    def test_bad_mean_counts_rejected(self):
        r=row(10000);r['packet']['valid_count']=19
        with self.assertRaises(ValueError):window(r['packet'])

if __name__=='__main__':unittest.main(verbosity=2)
