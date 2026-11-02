import copy,math,unittest
import numpy as np
from raw_functional import *
from INTEGRATED_COM_WINDOW_V1.window_math import piecewise_constant_window

def frame(epoch=10000,sequence=2,boot=False):
    q=[.250328109554,.050328109554,.250328109554,.050328109554];times=[0] if boot else list(range(epoch-10000,epoch,500));samples=[]
    for t in times:samples.append({'gyro_body':[0.,0.,.2],'accel_proper_body':[.1,0.,9.81],'joint_pos4':q[:],'joint_vel4':[0.]*4,'wheel_vel2':[0.,0.],'sampled_us':t,'encoder_pos_sampled_us':t,'encoder_rate_sampled_us':t,'weight_us':0 if boot else 500,'valid':True})
    return {'kind':'RAW2K_CORRELATED_SHADOW_NOT_OLD_BENCHMARK','sequence':1 if boot else sequence,'source_epoch_us':0 if boot else epoch,'window_begin_us':0 if boot else epoch-10000,'window_end_us':0 if boot else epoch,'aperture_us':0 if boot else 10000,'mean_mode':0 if boot else 1,'count':1 if boot else 20,'sample_weight_us':0 if boot else 500,'dropped_count':0,'correlated_postmean_noise':True,'extra_information_branch':True,'hardware_binding':False,'actuation_used':False,'mean':{k:samples[0][k] for k in MEAN},'endpoint_joint_pos4':q[:],'samples':samples,'payload_SHA':'a'*64,'arrival_us':0 if boot else epoch,'duplicate_source':False}

class Tests(unittest.TestCase):
    def test_strict_extra_truth_rejected(self):
        f=frame();f['truth']={}
        with self.assertRaises(ValueError):validate(f)
    def test_nested_clean_offset_rejected(self):
        f=frame();f['samples'][0]['clean']=[0,0,0]
        with self.assertRaises(ValueError):validate(f)
    def test_same_time_raw_endpoint_enforced(self):
        f=frame();f['samples'][-1]['encoder_rate_sampled_us']-=500
        with self.assertRaises(ValueError):validate(f)
    def test_boot_discard_and_duplicate_not_reintegrated(self):
        s=Stitch();f=frame(boot=True);s.add(f);dup=copy.deepcopy(f);dup['arrival_us']=10000;dup['duplicate_source']=True;s.add(dup);s.add(frame());self.assertEqual(s.boots,1);self.assertEqual(s.duplicates,1);self.assertEqual(len(s.points),20);self.assertEqual(s.points[-1]['sampled_us'],9500)
    def test_duplicate_payload_change_rejected(self):
        s=Stitch();f=frame(boot=True);s.add(f);f=copy.deepcopy(f);f['arrival_us']=10000;f['samples'][0]['gyro_body'][0]=1.
        with self.assertRaises(ValueError):s.add(f)
    def test_epoch_endpoint_not_used_as_rawposition(self):
        s=Stitch();f=frame();f['endpoint_joint_pos4']=[1000.]*4;s.add(f);self.assertLess(max(s.points[-1]['joint_pos4']),1.);self.assertGreater(s.endpoint_q_time_difference[0],999.)
    def test_prefix_matches_direct_analytic_bins(self):
        rng=np.random.default_rng(41);p=[]
        for i in range(250):
            w=rng.normal(size=3);f=rng.normal(size=3)+[0,0,9.81];p.append({'sampled_us':i*500,'gyro_body':w,'accel_proper_body':f,'mean':{'gyro_body':w,'accel_proper_body':f}})
        a=Prefix(p);u0=np.array([.1,.2,.3]);u1=np.array([-.1,.3,-.2]);got=a.evaluate(7,207,u0,u1);ref=piecewise_constant_window([x['gyro_body'] for x in p[7:207]],[x['accel_proper_body'] for x in p[7:207]],[.0005]*200,u0,u1);np.testing.assert_allclose(got['raw_discrete_average3'],ref['average_COM_proper_start_frame3'],atol=1e-10)
    def test_constant_raw_and_mean_paths_equal(self):
        s=Stitch()
        for i in range(1,9):s.add(frame(i*10000,i+1))
        a=Prefix(s.points);out=a.evaluate(19,119,np.zeros(3),np.zeros(3));self.assertAlmostEqual(out['paired_vector_difference_norm_m_s2'],0.,places=12)
    def test_raw_transport_difference_is_observable_not_truth_error(self):
        s=Stitch()
        for i in range(1,9):
            f=frame(i*10000,i+1)
            for j,x in enumerate(f['samples']):x['gyro_body']=[1.5*math.sin(j*.5),.5,2.];x['accel_proper_body']=[2*math.cos(j*.4),0.,9.81]
            for k in MEAN:f['mean'][k]=np.mean([x[k] for x in f['samples']],axis=0).tolist()
            s.add(f)
        a=Prefix(s.points);o=a.evaluate(19,119,np.zeros(3),np.zeros(3));self.assertGreater(o['paired_vector_difference_norm_m_s2'],1e-5);self.assertTrue(o['not_continuous_true_COM_error'])
    def test_discrete_budget_no_IID_gain_or_continuous_hardware_claim(self):
        s=Stitch()
        for i in range(1,18):s.add(frame(i*10000,i+1))
        a=Prefix(s.points);e={'u_B3':np.zeros(3),'u_error_norm_m_s':.1};vals=[]
        for n in (100,200,300):
            o=a.evaluate(19,19+n,np.zeros(3),np.zeros(3));b=a.discrete_budget(19,19+n,o,e,e);vals.append(b['noise_term_not_divided_by20_or_windowN']);self.assertIsNone(b['continuous_physical_quadrature_error_radius']);self.assertEqual(b['trusted_cue'],0);self.assertEqual(b['confidence_cap'],.5)
        np.testing.assert_allclose(vals,[vals[0]]*3,atol=0.)
    def test_age_is_half_window_plus_last_sample_transport_age(self):
        epoch=100000;last=epoch-500;arrival=epoch+10000;T=50000;age=arrival-(last-T/2);self.assertEqual(age,35500)
    def test_gap_breaks_contiguous_functional(self):
        s=Stitch();s.add(frame());s.add(frame(30000,4));a=Prefix(s.points)
        with self.assertRaises(ValueError):a.evaluate(19,39,np.zeros(3),np.zeros(3))
    def test_endpoint_alignment_removes_only_time_skew_not_model_noise(self):
        e=endpoint_model();self.assertEqual(e.a.mean_endpoint_age_s,0.);self.assertEqual(e.a.qd_axis_noise_rad_s,.25);self.assertEqual(e.a.nominal_COM_position_error_norm_m,.005)

if __name__=='__main__':unittest.main(verbosity=2)
