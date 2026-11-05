"""Exercise the pinned SCUT velocity reward; no model load or simulation."""
from types import SimpleNamespace
import unittest
import torch
from .config import reward_config
from .shared import load


class TakeoffVelocityTests(unittest.TestCase):
    def source_reward(self, phase, vz):
        cfg = reward_config()
        selected = cfg.jump_takeoff_state_machine_cfg['push']['reward_additions']['scut_jump_takeoff_velocity']
        isolated = dict(reward_scales={}, reward_additions={},
                        push=dict(reward_additions={'scut_jump_takeoff_velocity': selected}),
                        tuck=dict(reward_additions={}))
        machine = load('upstream').state_classes()['jump_takeoff']()
        phase = torch.tensor(phase, dtype=torch.long)
        velocity = torch.tensor(vz, dtype=torch.float32)
        robot = SimpleNamespace(data=SimpleNamespace(root_lin_vel_w=torch.stack(
            (torch.zeros_like(velocity), torch.zeros_like(velocity), velocity), dim=-1)))
        env = SimpleNamespace(cfg=SimpleNamespace(jump_takeoff_state_machine_cfg=isolated),
                              jump_takeoff_phase=phase, robot=robot,
                              num_envs=len(vz), device='cpu', step_dt=.02)
        return machine.apply_reward_term_scales(env, {})['scut_jump_takeoff_velocity']

    def test_push_rewards_upward_speed_and_caps_outliers(self):
        values = self.source_reward([1]*6, [-1., 0., .05, .5, 2., 9.])
        torch.testing.assert_close(values, torch.tensor([0., 0., .05, .5, 2., 3.]))

    def test_idle_spawn_and_tuck_receive_no_new_reward(self):
        values = self.source_reward([0, 0, 2, 2], [-1., 1., 1., -1.])
        torch.testing.assert_close(values, torch.zeros(4))

    def test_existing_recipe_and_physical_assist_stay_fixed(self):
        cfg = reward_config()
        self.assertEqual(cfg.rewards['scut_jump_takeoff_velocity'], 4.)
        self.assertEqual([cfg.rewards[k] for k in
                          ['scut_jump_push_height', 'scut_jump_push_velocity', 'scut_jump_peak']],
                         [2., 1., 2.])
        self.assertFalse(cfg.jump_takeoff_state_machine_cfg['assist']['enabled'])
        self.assertFalse(any(k.startswith('jump200_') for k in cfg.rewards))


if __name__ == '__main__':
    unittest.main()
