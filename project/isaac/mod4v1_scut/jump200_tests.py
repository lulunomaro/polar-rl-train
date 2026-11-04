"""Single200mm jump checks; synthetic tensors, no policy weights or physics."""
import io
import json
from pathlib import Path
import unittest
import torch

from .config import reward_config, command_recipe
from .jump200 import Jump200Acceptance, metadata, top_mask
from .validate import fixture, ASSETS
from .config import model_contract


class JumpTests(unittest.TestCase):
    def test_source_special_mode_flags_follow_new_task_constructor(self):
        from types import SimpleNamespace
        from .checkpoint import restore_command_fields
        source = dict(_mode_enabled=torch.tensor([True, True, False]),
                      special_mode_id=torch.tensor([0, 2]), command=torch.ones(2, 3))
        command = SimpleNamespace(_mode_enabled=torch.zeros(1, dtype=torch.bool),
            special_mode_id=torch.full((2,), -1), command=torch.zeros(2, 3))
        receipt = restore_command_fields(command, source, 'scut_stairs', 'jump200')
        self.assertEqual(command._mode_enabled.tolist(), [False])
        torch.testing.assert_close(command.special_mode_id, source['special_mode_id'])
        torch.testing.assert_close(command.command, source['command'])
        self.assertEqual(receipt[0]['field'], '_mode_enabled')
        with self.assertRaisesRegex(ValueError, '_mode_enabled'):
            restore_command_fields(command, source, 'scut_stairs', 'scut_stairs')
        source['command'] = torch.zeros(3, 3)
        with self.assertRaisesRegex(ValueError, 'command'):
            restore_command_fields(command, source, 'scut_stairs', 'jump200')

    def setUp(self):
        self.contract = model_contract(ASSETS)
        self.meter = Jump200Acceptance(1, 'cpu')
        self.q = torch.tensor([[1., 0., 0., 0.]])

    def tick(self, x=.35, z=.0625, ground=40., top=0., vz=0., vx=0., nonwheel=0.):
        pos = torch.tensor([[[x, -.2, z], [x, .2, z]]])
        net = torch.zeros(1, 2, 3)
        net[:, :, 2] = ground+top
        return self.meter.update_world(pos, self.q[:, None].expand(-1, 2, -1),
            self.contract, torch.zeros(1, 3), torch.full((1, 2), top),
            torch.full((1, 2), ground), net, torch.tensor([nonwheel]),
            torch.tensor([[vx, 0., vz]]), self.q, torch.ones(1, dtype=torch.bool))

    def jump(self):
        self.tick()
        self.tick(x=.55, z=.23, ground=0., vz=1.)
        self.tick(x=1., z=.31, ground=0., vz=.1)
        self.assertTrue(self.meter.wholeclear[0])

    def test_single_vertical_step_and_top_mask(self):
        value = metadata()
        self.assertEqual(value['step_height_m'], .2)
        self.assertEqual(len(value['raised_boxes_xy']), 1)
        p = torch.tensor([[1., 0., .2], [1., 0., .27], [.7, 0., .2], [1., 0., 0.]])
        self.assertEqual(top_mask(p).tolist(), [True, False, False, False])

    def test_climbing_with_wheel_contact_never_qualifies(self):
        self.tick()
        for _ in range(220):self.tick(x=1., z=.2625, ground=0., top=40.)
        self.assertFalse(self.meter.wholeclear[0])
        self.assertFalse(self.meter.success[0])

    def test_spawn_drop_never_qualifies(self):
        self.tick(x=1., z=.35, ground=0., vz=-.3)
        for _ in range(220):self.tick(x=1., z=.2625, ground=0., top=40.)
        self.assertFalse(self.meter.success[0])

    def test_actual_jump_requires_half_second_stable_landing(self):
        self.jump()
        for _ in range(199):self.tick(x=1., z=.2625, ground=0., top=40.)
        self.assertFalse(self.meter.success[0])
        self.tick(x=1., z=.2625, ground=0., top=40.)
        self.assertTrue(self.meter.success[0])

    def test_unstable_or_nonwheel_landing_does_not_qualify(self):
        self.jump()
        for _ in range(220):self.tick(x=1., z=.2625, ground=0., top=40., vx=.6)
        self.assertFalse(self.meter.success[0])
        for _ in range(220):self.tick(x=1., z=.2625, ground=0., top=40., nonwheel=10.)
        self.assertFalse(self.meter.success[0])

    def test_second_attempt_can_succeed_after_failed_return(self):
        self.jump()
        self.tick()
        self.assertTrue(self.meter.failed_return[0])
        self.jump()
        for _ in range(200):self.tick(x=1., z=.2625, ground=0., top=40.)
        self.assertEqual(int(self.meter.flight_id[0]), 2)
        self.assertTrue(self.meter.success[0])

    def test_profile_has_takeoff_rewards_and_no_physical_assist(self):
        cfg = reward_config('jump200')
        self.assertTrue(cfg.jump_takeoff_state_machine_cfg['enabled'])
        self.assertTrue(cfg.jump_takeoff_state_machine_cfg['trajectory']['enabled'])
        self.assertFalse(cfg.jump_takeoff_state_machine_cfg['assist']['enabled'])
        self.assertEqual(cfg.wheel_forward_scan_cfg['detect']['step_height_min'], .18)
        self.assertEqual(cfg.wheel_forward_scan_cfg['detect']['step_height_max'], .22)
        self.assertEqual(command_recipe('jump200')['ranges']['lin_vel_x'], (.6, .6))
        self.assertTrue(all(cfg.rewards[k] > 0 for k in
            ('jump200_push_height', 'jump200_push_velocity', 'jump200_peak', 'jump200_upward_velocity')))

    def test_approach_idle_bonus_cannot_outscore_forward_progress(self):
        r, robot, _ = fixture(2, profile='jump200')
        r.jump200_landed_top = torch.zeros(2, dtype=torch.bool)
        robot.data.root_pos_w[:, 2] = .25
        robot.data.root_lin_vel_b[:, 0] = torch.tensor([0., .3])
        reward = r.compute()
        self.assertGreater(float(reward[1]), float(reward[0]))
        for name in ('flat_orientation_x_exp', 'flat_orientation_y_exp',
                     'track_lin_vel_xy', 'track_ang_vel_z', 'track_height_exp_tight'):
            self.assertEqual(float(r.state_terms[name][0]), 0.)
            self.assertAlmostEqual(float(r.state_terms[name][1]), float(r.raw_terms[name][1])*.5, places=6)

    def test_progress_gate_does_not_suppress_takeoff_or_landing(self):
        r, _, _ = fixture(3, profile='jump200')
        r.jump_takeoff_phase[:] = torch.tensor([0, 1, 0])
        r.jump200_landed_top = torch.tensor([False, False, True])
        terms={name:torch.ones(3) for name in ('flat_orientation_x_exp', 'flat_orientation_y_exp',
            'track_lin_vel_xy', 'track_ang_vel_z', 'track_height_exp_tight')}
        shaped=r._postprocess_reward_terms(terms)
        torch.testing.assert_close(shaped['track_lin_vel_xy'], torch.tensor([0., 1., 1.]))

    def test_source_upward_push_reward_distinguishes_real_velocity(self):
        r, robot, _ = fixture(2, profile='jump200')
        r.jump_takeoff_phase.fill_(1)
        robot.data.root_lin_vel_w[:, 2] = torch.tensor([0., 1.])
        r.compute()
        torch.testing.assert_close(r._last_reward_terms['jump200_upward_velocity'], torch.tensor([0., .04]))

    def test_source_step_event_requests_takeoff_and_actual_landing_stops_command(self):
        r, _, _ = fixture(2, profile='jump200')
        r.jump200_requested = torch.zeros(2, dtype=torch.bool)
        r.jump200_landed_top = torch.tensor([False, True])
        r.forward_hits[0, :, 2] = .2
        r.wheel_forward_prev_ground_z.zero_()
        r.wheel_forward_prev_ground_z_valid[:] = True
        r.wheel_forward_prev_direction_sign[:] = 1.
        r._invalidate_step_caches()
        r._on_command_updated()
        self.assertTrue(r.jump_takeoff_request[0])
        self.assertTrue(r.jump200_requested[0])
        self.assertTrue(bool((r.command[1] == 0).all()))
        r._on_command_updated()
        self.assertEqual(int(r.jump_takeoff_phase[0]), 1)
        reward = r.compute()
        self.assertTrue(bool(torch.isfinite(reward).all()))
        self.assertGreater(float(r._last_reward_terms['jump200_push_height'][0]), 0.)
        r.reset(torch.tensor([0]))
        self.assertFalse(r.jump200_requested[0])


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser();p.add_argument('--report', type=Path, required=True);a = p.parse_args()
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(JumpTests))
    with a.report.open('x', encoding='utf8') as f:
        json.dump(dict(passed=result.wasSuccessful(), tests=result.testsRun,
            output=stream.getvalue(), production_model_reads=0, physics=0), f, indent=2)
    print(stream.getvalue())
    raise SystemExit(0 if result.wasSuccessful() else 1)
