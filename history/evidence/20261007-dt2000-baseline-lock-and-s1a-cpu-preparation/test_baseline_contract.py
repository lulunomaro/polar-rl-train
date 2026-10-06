import copy,json,unittest
from pathlib import Path
from physics_baseline_contract import validate_baseline

class BaselineContract(unittest.TestCase):
    def setUp(self):self.env=json.loads((Path(__file__).parent/'env.json').read_text())
    def test_actual_frozen_env(self):self.assertEqual(validate_baseline(self.env)['decimation'],5)
    def test_reject_other_timestep(self):
        for dt in ['.0005','.001','.0025','.005','.0020001']:
            with self.subTest(dt=dt):
                e=copy.deepcopy(self.env);e['RM_PHYSICS_DT_S']=dt
                with self.assertRaises(ValueError):validate_baseline(e)
    def test_reject_control_or_contact_clock(self):
        for kwargs in [{'control_period_s':.02},{'contact_bin_s':.006}]:
            with self.assertRaises(ValueError):validate_baseline(self.env,**kwargs)
    def test_reject_solver_or_std_or_impulse(self):
        for k,v in [('RM_SOLVER_POS','8'),('RM_SOLVER_VEL','2'),('RM_KEEP_STD','0'),('RM_CONTACT_INTEGRATED','0')]:
            e=copy.deepcopy(self.env);e[k]=v
            with self.assertRaises(ValueError):validate_baseline(e)
    def test_reject_unreviewed_ppo_change(self):
        for kw in [{'steps_per_env':48},{'learning_rate':.0003},{'save_interval':50},{'num_envs':1024}]:
            with self.assertRaises(ValueError):validate_baseline(self.env,**kw)
    def test_only_explicit128_preflight(self):
        with self.assertRaises(ValueError):validate_baseline(self.env,num_envs=128)
        self.assertTrue(validate_baseline(self.env,num_envs=128,preflight=True)['accepted'])

if __name__=='__main__':unittest.main()
