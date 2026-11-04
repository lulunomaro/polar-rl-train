"""Processed target/real D4 queue regression with synthetic articulation data."""
import importlib.util
import io
import json
from pathlib import Path
from types import SimpleNamespace
import sys
import unittest

import torch

from .config import LEGS, TARGET_INTERFACE, ACTION_CLIP, ACTION_INTERFACE, USD_SHA, CONTRACT_SHA
from .checkpoint import check_interface, V3_FORMAT, V3_INTERFACE
from .target_limits import limited_action_type, project_leg_targets

CONTRACT = {'joints': {n: {'limits_si': [-1.2, .9] if 'crank' in n else [-.5, .5]} for n in LEGS}}


class Tests(unittest.TestCase):
    def test_recorded_outside_targets_are_bounded_without_losing_cad_difference(self):
        # Recorded source/final requests, after original scale and projection.
        value = torch.tensor([[-.2449, .8384, -.2616, .620], [3., 3., -3., -3.]])
        original = value.clone()
        actual = project_leg_targets(value, LEGS, CONTRACT, -1.0843, .85)
        torch.testing.assert_close(actual, torch.tensor([[-.2449, .5, -.2616, .5], [.9, .5, -1.2, -.5]]))
        torch.testing.assert_close(value, original, atol=0, rtol=0)

    def test_named_mapping_and_extreme_requests_keep_all_constraints(self):
        generator = torch.Generator().manual_seed(270)
        names = ('right_hip', 'left_crank', 'right_crank', 'left_hip')
        requests = torch.randn(12000, 4, generator=generator)*100
        result = project_leg_targets(requests, names, CONTRACT, -1.0843, .85)
        for i, name in enumerate(names):
            lo, hi = CONTRACT['joints'][name]['limits_si']
            self.assertTrue(bool(((result[:, i] >= lo) & (result[:, i] <= hi)).all()))
        for side in ('left', 'right'):
            difference = result[:, names.index(side+'_crank')]-result[:, names.index(side+'_hip')]
            self.assertGreaterEqual(float(difference.min()), -1.084301)
            self.assertLessEqual(float(difference.max()), .850001)

    def test_original_d4_submits_limits_before_actual_queue_application(self):
        metadata = json.loads((Path(__file__).parent/'DEPENDENCIES.json').read_bytes())
        runtime = Path(next(x['path'] for x in metadata['files'] if Path(x['path']).name == 'action_delay_sdk_adapter.py')).parent
        sys.path.insert(0, str(runtime))
        from action_delay_sdk_adapter import PhysicalActionDelayAdapter
        robot = SimpleNamespace(joint_names=list(LEGS)+['left_wheel_spin', 'right_wheel_spin'],
            data=SimpleNamespace(default_joint_pos=torch.zeros(2, 6), joint_pos_target=torch.zeros(2, 6),
                                 joint_vel_target=torch.zeros(2, 6)))
        class Original:
            def __init__(self, cfg, env):
                self._asset = robot; self._joint_ids = [0, 1, 2, 3]
                self.action_dim = 4; self._max_lag = 0
                self._processed_actions = torch.zeros(2, 4)
                self.diff_min, self.diff_max = -1.0843, .85
            @property
            def processed_actions(self):
                return self._processed_actions
            def process_actions(self, action):
                self._processed_actions = action*.5
            def apply_actions(self):
                robot.data.joint_pos_target[:, :4] = self._processed_actions
            def reset(self, env_ids=None):
                pass
        class Wheel(Original):
            def __init__(self, cfg, env):
                super().__init__(cfg, env)
                self.action_dim = 2; self._joint_ids = [4, 5]
                self._processed_actions = torch.zeros(2, 2)
            def apply_actions(self):
                robot.data.joint_vel_target[:, 4:] = self._processed_actions
        env = SimpleNamespace(num_envs=2, device='cpu', physics_dt=.0025, step_dt=.02,
            cfg=SimpleNamespace(decimation=8), sim=SimpleNamespace(), _sim_step_counter=0)
        legs = limited_action_type(Original, CONTRACT)(None, env); wheels = Wheel(None, env)
        env.action_manager = SimpleNamespace(get_term=lambda key: {'legs': legs, 'wheels': wheels}[key])
        adapter = PhysicalActionDelayAdapter(env, True, 9137)
        raw = torch.tensor([[-6., 3.8, 2., 2.], [6., -3., -6., 3.]])
        legs.process_actions(raw)
        requested = legs.processed_actions.clone()
        for tick in range(1, 5):
            env._sim_step_counter = tick
            legs.apply_actions()
            actual = robot.data.joint_pos_target[:, :4]
            self.assertTrue(bool((actual[:, [1, 3]].abs() <= .5).all()))
        torch.testing.assert_close(actual, requested)
        self.assertEqual(adapter.formula_max_error, 0.)

    def test_v3_requires_explicit_target_interface_repair(self):
        saved = dict(format=V3_FORMAT, interface=V3_INTERFACE, action_clip=ACTION_CLIP,
            action_interface=ACTION_INTERFACE, usd_SHA=USD_SHA, contract_SHA=CONTRACT_SHA,
            profile='trained_stair', actor_dim=35, critic_dim=78)
        with self.assertRaises(ValueError):
            check_interface(saved, 'trained_stair')
        receipt = check_interface(saved, 'trained_stair', repair_target_limits=True)
        self.assertTrue(receipt['target_limits_repair'])
        self.assertEqual(receipt['target_interface'], TARGET_INTERFACE)

    def test_first_axis_repair_preserves_all_other_learned_parameters(self):
        from .train import build_runner
        from .action_tests import spy_vec
        from .finetune import repair_saturated_first_axis
        vec, _, _ = spy_vec(8)
        runner = build_runner(vec, None)
        actor = runner.alg.actor
        layer = [m for m in actor.mlp.modules() if isinstance(m, torch.nn.Linear)][-1]
        with torch.no_grad():
            layer.bias[0] = -105.
            actor.distribution.std_param[0] = 23.35
        before = {key: value.clone() for key, value in actor.state_dict().items()}
        receipt = repair_saturated_first_axis(actor)
        changed = []
        for key, value in actor.state_dict().items():
            if not torch.equal(value, before[key]):
                changed.append(key)
                torch.testing.assert_close(value[1:], before[key][1:], atol=0, rtol=0)
        self.assertEqual(len(changed), 3)
        self.assertEqual(receipt['joint_name'], 'left_crank')
        self.assertEqual(float(actor.distribution.std_param[0]), 1.)
        with torch.no_grad():
            self.assertTrue(bool((actor(vec.get_observations())[:, 0] == 0).all()))
        self.assertEqual(len(runner.alg.optimizer.state), 0)

    def test_repaired_78_finetune_keeps_critic_and_source_file_with_fresh_adam(self):
        import hashlib
        import tempfile
        from .train import build_runner
        from .action_tests import spy_vec
        from .finetune import initialize
        vec, _, _ = spy_vec(8)
        source = build_runner(vec, None); target = build_runner(vec, None)
        saved = dict(source.alg.save(), format=V3_FORMAT, interface=V3_INTERFACE,
            action_clip=ACTION_CLIP, action_interface=ACTION_INTERFACE,
            usd_SHA=USD_SHA, contract_SHA=CONTRACT_SHA, profile='trained_stair',
            actor_dim=35, critic_dim=78)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/'synthetic.pt'; torch.save(saved, path)
            raw = path.read_bytes(); digest = hashlib.sha256(raw).hexdigest()
            receipt = initialize(target, path, digest, len(raw), True, 'trained_stair')
            self.assertEqual(path.read_bytes(), raw)
            self.assertEqual(len(target.alg.optimizer.state), 0)
            self.assertEqual(target.current_learning_iteration, 0)
            self.assertTrue(receipt['actor35_critic78_strict'])
            for key, value in source.alg.critic.state_dict().items():
                torch.testing.assert_close(value, target.alg.critic.state_dict()[key], atol=0, rtol=0)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(); parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    if args.report.exists():
        raise FileExistsError(args.report)
    stream = io.StringIO(); torch.set_num_threads(2)
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
    args.report.write_text(json.dumps(dict(passed=result.wasSuccessful(), tests=result.testsRun,
        output=stream.getvalue(), production_PT_reads=0, new_physics=0,
        real_D4_queue_synthetic_articulation=True), indent=2), encoding='utf8')
    print(stream.getvalue()); raise SystemExit(0 if result.wasSuccessful() else 1)
