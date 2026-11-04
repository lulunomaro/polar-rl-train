"""Tests for the selected published stair task; no production model or SDK."""
from pathlib import Path
import io
import json
import unittest
import torch
from .config import reward_config, command_recipe
from .stairs import metadata, recipe, StairTraversal


class Tests(unittest.TestCase):
    def test_saved_branch_keeps_original_reward_and_commands(self):
        old, new = reward_config('trained_stair'), reward_config('scut_stairs')
        self.assertEqual(old.rewards, new.rewards)
        # This specific saved branch has no override; V13 falls back to the
        # global range. Do not borrow the inverse-low branch's.24-.38 range.
        self.assertEqual(new.height_range, tuple(old.height_range))
        self.assertFalse(new.enable_state_machines)
        self.assertEqual(command_recipe('trained_stair'), command_recipe('scut_stairs'))
        _, stair = recipe()
        self.assertEqual(tuple(stair['step_height_range']), (.025, .04))
        self.assertEqual(stair['step_width'], .1)
        self.assertTrue(stair['inverted'])
        self.assertFalse(metadata()['requires_270mm'])

    def test_support_after_spawn_drop_is_not_ascent(self):
        meter = StairTraversal(2, 'cpu')
        wheels = torch.zeros(2, 2, 3)
        wheels[:, :, 2] = -.65
        ground = torch.full((2,), -.7)
        height = torch.full((2, 2), -.7)
        force = torch.full((2, 2), 20.)
        root = torch.tensor([[0., 0., -.32], [8., 0., -.32]])
        wheels[1, :, 0] = 8.
        quat = torch.tensor([[1., 0., 0., 0.]]).repeat(2, 1)
        velocity = torch.zeros(2, 3)
        meter.update(wheels, height, force, torch.zeros(2), velocity, quat, root, ground)
        for _ in range(220):
            meter.update(wheels, height, force, torch.zeros(2), velocity, quat, root, ground)
        self.assertFalse(bool(meter.success.any()))
        wheels[:, :, 0] += .7
        height += .025
        velocity[:, 0] = .6  # locomotion recovery allows commanded travel
        for _ in range(200):
            meter.update(wheels, height, force, torch.zeros(2), velocity, quat, root, ground)
        self.assertTrue(bool(meter.success.all()))
        self.assertTrue(bool(meter.wholeclear.all()))
        meter.reset(torch.tensor([1]))
        self.assertFalse(bool(meter.success[1]))
        self.assertTrue(bool(torch.isnan(meter.birth_support[1]).all()))

    def test_nonwheel_support_and_single_wheel_do_not_graduate(self):
        meter = StairTraversal(1, 'cpu')
        wheel = torch.zeros(1, 2, 3)
        root = torch.zeros(1, 3)
        q = torch.tensor([[1., 0., 0., 0.]])
        zero = torch.zeros(1)
        velocity = torch.zeros(1, 3)
        meter.update(wheel, torch.zeros(1, 2), torch.zeros(1, 2), zero, velocity, q, root, zero)
        wheel[:, :, 0] = .8
        height = torch.full((1, 2), .03)
        force = torch.tensor([[20., 0.]])
        for _ in range(210):
            meter.update(wheel, height, force, zero, velocity, q, root, zero)
        self.assertTrue(bool(meter.leading[0]))
        self.assertFalse(bool(meter.success[0]))
        force[:] = 20.
        for _ in range(210):
            meter.update(wheel, height, force, torch.ones(1)*30, velocity, q, root, zero)
        self.assertFalse(bool(meter.success[0]))


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser(); p.add_argument('--report', type=Path, required=True); a = p.parse_args()
    if a.report.exists(): raise FileExistsError(a.report)
    stream = io.StringIO()
    r = unittest.TextTestRunner(stream=stream, verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
    a.report.write_text(json.dumps(dict(passed=r.wasSuccessful(), tests=r.testsRun, output=stream.getvalue(),
        production_model_reads=0, physics=0, current_native_skill_not_proven=True), indent=2), encoding='utf8')
    print(stream.getvalue()); raise SystemExit(0 if r.wasSuccessful() else 1)
