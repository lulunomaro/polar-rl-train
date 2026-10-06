"""Reject cross-policy/cache reuse and verify bounded progression boundaries."""
import unittest
from cadence_contract import next_step, reuse_exact, quick_summary


class Contract(unittest.TestCase):
    def test_plan(self):
        self.assertEqual(next_step(0,100000),{'action':'learn','seconds':7200})
        self.assertEqual(next_step(21500,100000),{'action':'learn','seconds':100})
        self.assertEqual(next_step(21600,100000)['reason'],'finite_stage_closeout')
        self.assertEqual(next_step(0,120)['reason'],'budget_safety_boundary')
        self.assertEqual(next_step(0,100000,True)['reason'],'material_retention_concern')
        self.assertEqual(next_step(0,900)['seconds'],900)
        for v in (-1,float('nan'),float('inf')):
            with self.assertRaises(AssertionError): next_step(v,100000)

    def test_reuse(self):
        expected=dict(checkpoint_path='/full/model.pt',checkpoint_sha256='policy',kind='flat',
                      profile='white_v3',seed=20261002,steps=1500,num_envs=80,probe_sha256='probe',runtime_freeze_sha256='scope')
        record=dict(expected,report_path='/raw/report.json',report_sha256='raw',data_admission_pass=True,
                    initial_final_parameters_checked=True)
        self.assertEqual(reuse_exact(record,expected,'raw'),'/raw/report.json')
        for key in expected:
            changed=dict(record);changed[key]='wrong'
            with self.subTest(key=key),self.assertRaises(AssertionError):reuse_exact(changed,expected,'raw')
        for key in ('data_admission_pass','initial_final_parameters_checked'):
            changed=dict(record);changed[key]=False
            with self.subTest(key=key),self.assertRaises(AssertionError):reuse_exact(changed,expected,'raw')
        with self.assertRaises(AssertionError):reuse_exact(record,expected,'modified')

    def test_quick_concerns_do_not_change_data_verdict(self):
        import copy
        mixed=dict(rough_progress_segments=[dict(requested_body_vx=-.3,valid_segments_before_each_reset=[dict(along_m_s=-.29)])],
                   complete_world_cycles=[dict(metrics=dict(valid=True,complete_cycle_count=4,post_failure_samples_used=False,
                       complete_prefix_along_m_s=.5,complete_prefix_cross_m_s=.06))])
        flat=dict(groups=[dict(profile='constant',command_vx=1.5,vel_error=.025,speed=1.48)])
        reference=dict(groups=[dict(profile='constant',command_vx=1.5,vel_error=.018,speed=1.49)])
        self.assertFalse(quick_summary(mixed,flat,reference)['request_full_review'])
        self.assertEqual(quick_summary(mixed,flat,reference)['worst_abs_net_cross'],.06)
        wrong=copy.deepcopy(mixed);wrong['rough_progress_segments'][0]['valid_segments_before_each_reset'][0]['along_m_s']=.1
        self.assertTrue(quick_summary(wrong,flat,reference)['request_full_review'])
        wrong=copy.deepcopy(mixed);wrong['complete_world_cycles'][0]['metrics']['post_failure_samples_used']=True
        with self.assertRaises(AssertionError):quick_summary(wrong,flat,reference)
        slow=copy.deepcopy(flat);slow['groups'][0]['vel_error']=.18
        self.assertTrue(quick_summary(mixed,slow,reference)['request_full_review'])


if __name__=='__main__':unittest.main()
