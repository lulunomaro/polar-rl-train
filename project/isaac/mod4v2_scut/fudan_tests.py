"""CPU checks for the exact Fudan equations and MOD4 measurement adapter."""
import ast
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
import torch
from .config import reward_config
from .fudan_source import FudanJumpFunctions
from .rewards import ScutRewards


def fixture():
    n = 4
    obj = ScutRewards.__new__(ScutRewards)
    data = SimpleNamespace(root_pos_w=torch.zeros(n, 3),
        root_quat_w=torch.tensor([[1., 0., 0., 0.]]).repeat(n, 1),
        root_lin_vel_w=torch.tensor([[.6, 0., .3]]).repeat(n, 1),
        root_lin_vel_b=torch.tensor([[.6, 0., .3]]).repeat(n, 1),
        root_ang_vel_b=torch.zeros(n, 3), projected_gravity_b=torch.tensor([[0., 0., -1.]]).repeat(n, 1),
        applied_torque=torch.zeros(n, 6), body_pos_w=torch.zeros(n, 3, 3))
    data.root_pos_w[:, 2] = .4
    data.body_pos_w[:, 1, :] = torch.tensor([0., .15, .1])
    data.body_pos_w[:, 2, :] = torch.tensor([0., -.15, .1])
    obj.robot = SimpleNamespace(data=data)
    obj.contract = {'joints': {side+'_hip': {'local_pos0': [0., y, 0.]}
                              for side, y in [('left', .15), ('right', -.15)]}}
    obj.cfg = reward_config()
    obj.num_envs, obj.device, obj.step_dt = n, 'cpu', .02
    obj._wheel_link_idx, obj._actuate_idx, obj._reset_contact_link_idx = [1, 2], list(range(6)), [0]
    forces = torch.zeros(n, 3, 3)
    forces[[0, 2], 1:, 2] = 20.
    obj.contact_sensor = SimpleNamespace(data=SimpleNamespace(net_forces_w=forces))
    obj.fudan_last_contacts = torch.zeros(n, 2, dtype=torch.bool)
    obj.fudan_contact_filt = obj.fudan_last_contacts.clone()
    obj.fudan_was_in_flight = torch.zeros(n, dtype=torch.bool)
    obj.fudan_base_air_time = torch.zeros(n)
    obj.fudan_leg_length = torch.zeros(n, 2)
    obj.fudan_leg_theta = torch.zeros(n, 2)
    obj.fudan_reward_cfg = SimpleNamespace(rewards=SimpleNamespace(
        tracking_sigma=.25, clip_single_reward=2.5, only_positive_rewards=False))
    obj.command = torch.tensor([[.6, 0., 0.]]).repeat(n, 1)
    obj.height_cmd = torch.full((n,), .25)
    obj._actions = torch.zeros(n, 6)
    obj._previous_actions = obj._actions.clone()
    obj._episode_sums = {}
    obj.command_generator = SimpleNamespace(command=obj.command, command_counter=torch.zeros(n), compute=lambda dt: None)
    obj._resample_custom_cmd = lambda counter: None
    obj._on_command_updated = lambda: None
    return obj


class FudanTests(unittest.TestCase):
    def test_extracted_methods_match_original_pinned_AST(self):
        index = json.loads(Path(__file__).with_name('FUDAN_SOURCE.json').read_bytes())
        source = Path(index['robot']['path'])
        self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), index['robot']['SHA'])
        a = next(n for n in ast.parse(source.read_text(encoding='utf8')).body
                 if isinstance(n, ast.ClassDef) and n.name == 'LeggedRobot')
        b = next(n for n in ast.parse(Path(__file__).with_name('fudan_source.py').read_text(encoding='utf8')).body
                 if isinstance(n, ast.ClassDef))
        before = {n.name: ast.dump(n, include_attributes=False) for n in a.body if isinstance(n, ast.FunctionDef)}
        for method in b.body:
            self.assertEqual(ast.dump(method, include_attributes=False), before[method.name])

    def test_actual_hip_anchor_and_sagittal_length(self):
        obj = fixture()
        length, theta = obj.virtual_legs()
        torch.testing.assert_close(length, torch.full((4, 2), .3))
        torch.testing.assert_close(theta, torch.zeros(4, 2))
        obj.robot.data.body_pos_w[:, 1:, 0] = -.1
        length, theta = obj.virtual_legs()
        torch.testing.assert_close(length, torch.full((4, 2), (.1**2+.3**2)**.5))
        self.assertTrue(bool((theta > 0).all()))

    def test_source_contact_filter_retains_one_control(self):
        obj = fixture()
        obj.compute()
        self.assertEqual(obj.fudan_was_in_flight.tolist(), [False, True, False, True])
        obj.contact_sensor.data.net_forces_w.zero_()
        obj.compute()
        self.assertEqual(obj.fudan_was_in_flight.tolist(), [False, True, False, True])
        obj.compute()
        self.assertTrue(bool(obj.fudan_was_in_flight.all()))

    def test_original_tuck_extend_and_velocity_masks(self):
        obj = fixture()
        obj.compute()
        raw = obj.raw_terms
        self.assertGreater(float(raw['takeoff_extend'][0]), 0.)
        self.assertEqual(float(raw['leg_tuck'][0]), 0.)
        self.assertEqual(float(raw['takeoff_extend'][1]), 0.)
        expected_tuck = torch.exp(torch.tensor(-4.*2.*abs(.3-.16)))
        torch.testing.assert_close(raw['leg_tuck'][1], expected_tuck)
        self.assertAlmostEqual(float(raw['line_z'][1]), .3, places=6)
        obj.robot.data.root_lin_vel_w[:, 2] = -.1
        obj.compute()
        self.assertEqual(float(obj.raw_terms['line_z'][1]), 0.)
        self.assertEqual(float(obj.raw_terms['takeoff_extend'][0]), 0.)

    def test_all16_source_scales_clip_each_once_and_sum(self):
        obj = fixture()
        obj.robot.data.projected_gravity_b[:, 0] = 1.
        obj.robot.data.root_lin_vel_w[:, 2] = 100.
        value = obj.compute()
        self.assertEqual(len(obj._last_reward_terms), 16)
        torch.testing.assert_close(value, torch.stack(list(obj._last_reward_terms.values())).sum(0))
        torch.testing.assert_close(obj._last_reward_terms['orientation'], torch.full((4,), -.05))
        self.assertAlmostEqual(float(obj._last_reward_terms['line_z'][1]), .05, places=7)
        for name, raw in obj.raw_terms.items():
            expected = (raw*obj.cfg.rewards[name]*.02).clamp(-.05, .05)
            torch.testing.assert_close(obj._last_reward_terms[name], expected)

    def test_no_scut_reward_terms_or_assistance(self):
        cfg = reward_config()
        self.assertFalse(any(k.startswith('scut_') for k in cfg.rewards))
        self.assertEqual(cfg.jump_takeoff_state_machine_cfg['push']['reward_additions'], {})
        self.assertEqual(cfg.jump_takeoff_state_machine_cfg['tuck']['reward_additions'], {})
        self.assertFalse(cfg.jump_takeoff_state_machine_cfg['assist']['enabled'])
        self.assertEqual(cfg.rewards['leg_tuck'], 1.7)
        self.assertEqual(cfg.rewards['takeoff_extend'], .5)


if __name__ == '__main__':
    unittest.main()
