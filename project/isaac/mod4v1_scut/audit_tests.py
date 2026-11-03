"""Targeted cross-boundary regressions found by the complete repair review."""
import io
import json
from pathlib import Path
from types import SimpleNamespace
import unittest

import numpy as np
import torch

from .course import FourSideStrict270
from .evaluate import first_episode_contact_summary
from .math_ops import quat_from_euler_xyz
from .parity_tests import bridge_fixture
from .upstream import load_functions
from .validate import endpoint


class Tests(unittest.TestCase):
    def test_debug_clock_matches_upstream_off_and_reward_tail_only(self):
        original=load_functions('base_env', ['_debug_print_reward_and_state_stats'])['_debug_print_reward_and_state_stats']
        for enabled in (False, True):
            b,r,_,_=bridge_fixture(1)
            r._value_debug_enabled=enabled
            reference=SimpleNamespace(_value_debug_enabled=enabled,
                _value_debug_step=0,_value_debug_print_interval=0)
            for step in range(12):
                r.cache_raw_observations({'actions':torch.tensor([[121.]])},{})
                self.assertEqual(r._value_debug_step,reference._value_debug_step)
                r.compute()
                original(reference,{},torch.zeros(1))
                self.assertEqual(r._value_debug_step,reference._value_debug_step)
            self.assertEqual(bool(b.resolve_done()[0][0]),enabled)

    def test_saved_profile_does_not_enable_debug_gate_but_keeps_physical_outlier_reset(self):
        b,r,robot,_=bridge_fixture(2,'jump270')
        self.assertFalse(r._value_debug_enabled)
        for _ in range(15):
            r.cache_raw_observations({'actions':torch.full((2,1),121.)},{})
            r._debug_print_reward_and_state_stats()
        robot.data.root_lin_vel_b[1,0]=101.
        self.assertEqual(b.resolve_done()[0].tolist(),[False,True])
        self.assertEqual(r._value_debug_step,0)

    def test_reward_action_history_is_first_and_second_difference_once(self):
        _,r,_,_=bridge_fixture(2)
        for action,expected_rate,expected_smooth in ((1.,6.,6.),(3.,24.,6.),(3.,0.,24.)):
            r._actions.fill_(action)
            r.compute()
            torch.testing.assert_close(r.raw_terms['action_rate'],torch.full((2,),expected_rate))
            torch.testing.assert_close(r.raw_terms['action_smoothness'],torch.full((2,),expected_smooth))
            r.finish_observation()
        r.reset(torch.tensor([0]))
        torch.testing.assert_close(r._actions[0],torch.zeros(6))
        torch.testing.assert_close(r._previous_actions[1],torch.full((6,),3.))

    def test_post_reset_contact_does_not_leak_into_first_episode_maximum(self):
        top=np.array([[[4.,3.],[2.,0.]],[[9000.,8000.],[0.,5.]]])
        active=np.array([[True,True],[False,True]])
        result=first_episode_contact_summary(top,active)
        self.assertEqual(result,dict(anytop_envs=2,bothtop_envs=1,
            anytop_environment_ticks=3,bothtop_environment_ticks=1,max_top_force=5.))

    def test_spawn_yaw_is_fixed_before_first_physics_sample_and_reset_is_selective(self):
        meter=FourSideStrict270(2,'cpu')
        yaw=torch.tensor([.7,-1.2])
        q=quat_from_euler_xyz(torch.zeros(2),torch.zeros(2),yaw)
        meter.set_spawn_orientation(torch.arange(2),q)
        torch.testing.assert_close(meter.initial_yaw,yaw)
        meter.reset(torch.tensor([0]))
        self.assertTrue(bool(torch.isnan(meter.initial_yaw[0])))
        self.assertAlmostEqual(float(meter.initial_yaw[1]),-1.2,places=6)
        meter.set_spawn_orientation(torch.tensor([0]),q[:1])
        torch.testing.assert_close(meter.initial_yaw,yaw)


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--report',required=True,type=Path)
    args=parser.parse_args()
    if args.report.exists():raise FileExistsError(args.report)
    torch.set_num_threads(2);torch.manual_seed(270)
    stream=io.StringIO()
    result=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
    args.report.write_text(json.dumps(dict(passed=result.wasSuccessful(),tests=result.testsRun,
        output=stream.getvalue(),production_PT_reads=0,physics=0,
        kind='CPU_SOURCE_CLOCK_HISTORY_AND_FIRST_EPISODE_REGRESSION'),indent=2),encoding='utf8')
    print(stream.getvalue());raise SystemExit(0 if result.wasSuccessful() else 1)
