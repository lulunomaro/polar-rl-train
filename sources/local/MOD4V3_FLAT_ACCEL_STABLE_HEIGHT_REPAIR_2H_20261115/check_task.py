"""CPU regressions for single-flight accounting and real preload decisions."""
import ast
import io
import json
from pathlib import Path
import time
import unittest
from types import SimpleNamespace
import torch
from flat_height.objective import HeightAccount, moving_takeoff
from flat_height.preload import spring_state, ready_to_push, release_fraction
from flat_height.policy_repair import initialize, bound_exploration, in_bounds, INITIAL_STD

T = Path(__file__).resolve().parent


class Checks(unittest.TestCase):
    def setUp(self):
        self.account = HeightAccount(1, 'cpu')

    def step(self, **changes):
        values = dict(launch=False, airborne=False, landed=False, stable=False,
                      failed=False, rim=0., body=0., balance=1., moving=True)
        values.update(changes)
        return self.account.update(**{k: torch.tensor([v]) for k, v in values.items()})

    def test_repeated_hops_cannot_add_height_or_completion_rewards(self):
        self.step(launch=True, airborne=True, rim=.2, body=.1)
        self.step(airborne=True, rim=.4, body=.3)
        self.step(landed=True)
        repeated = self.step(launch=True, airborne=True, rim=1., body=1.)
        self.assertEqual(float(repeated['reward']), 0.)
        self.assertAlmostEqual(float(self.account.rim_peak), .4, places=6)
        self.assertEqual(int(self.account.takeoffs), 1)
        self.assertGreater(float(self.step(stable=True)['deferred']), 0.)
        self.assertEqual(float(self.step(stable=True)['reward']), 0.)

    def test_failure_never_receives_settled_height(self):
        self.step(launch=True, airborne=True, rim=.5, body=.4)
        self.step(landed=True, failed=True)
        self.assertEqual(float(self.step(stable=True)['deferred']), 0.)

    def test_unstable_flight_does_not_settle(self):
        self.step(launch=True, airborne=True, rim=.5, body=.4, balance=.1)
        self.step(landed=True)
        self.assertEqual(float(self.step(stable=False)['deferred']), 0.)

    def jump_reward(self, rim, body, quality=1.):
        self.account = HeightAccount(1, 'cpu')
        dense = self.step(launch=True, airborne=True, rim=rim, body=body, balance=quality)['reward']
        self.step(landed=True)
        return float(dense + self.step(stable=True)['reward'])

    def test_higher_level_flight_earns_more(self):
        self.assertGreater(self.jump_reward(.5, .4), self.jump_reward(.3, .2))
        self.assertGreater(self.jump_reward(.4, .3, 1.), self.jump_reward(.4, .3, .2))

    def test_stationary_launch_cannot_earn_height(self):
        self.step(launch=True, airborne=True, rim=.5, body=.4, moving=False)
        self.step(landed=True)
        self.assertEqual(float(self.step(stable=True)['reward']), 0.)
        self.assertEqual(float(self.account.dense_paid), 0.)

    def test_command_speed_error_does_not_erase_high_stable_jump(self):
        self.assertEqual(moving_takeoff(torch.tensor([-.1, 0., .2, .6, 1.6, 2.1])).tolist(),
                         [False, False, False, True, True, False])
        moving = bool(moving_takeoff(torch.tensor([1.6])))
        self.step(launch=True, airborne=True, rim=.3, body=.25, moving=moving)
        self.step(landed=True)
        self.assertGreater(float(self.step(stable=True)['deferred']), 0.)

    def test_individual_reset_clears_entire_account(self):
        self.step(launch=True, airborne=True, rim=.4, body=.3)
        self.account.reset(torch.tensor([0]))
        self.assertTrue(all(not bool(v.any()) for v in vars(self.account).values()))
        self.assertTrue(bool(self.step(launch=True, airborne=True, rim=.2)['first_takeoff']))

    def test_preload_uses_travel_stop_not_outside_drive_reference(self):
        lower = torch.tensor([-.0393605589, -.0393605589])
        upper = lower + .060
        reference = torch.tensor([.1706394411, .1706394411])
        compression, energy = spring_state(upper[None], lower, upper, reference, 2000.)
        self.assertTrue(bool((compression == 0).all()))
        self.assertEqual(float(energy), 0.)
        self.assertFalse(bool(ready_to_push(compression, torch.tensor([.36]))))
        self.assertTrue(bool(ready_to_push(compression, torch.tensor([.26]))))
        compression, energy = spring_state((upper - .04)[None], lower, upper, reference, 2000.)
        self.assertTrue(bool(ready_to_push(compression, torch.tensor([.36]))))
        self.assertGreater(float(energy), 0.)

    def test_spring_assist_is_bounded_and_no_release_pays_zero(self):
        fraction = release_fraction(torch.tensor([20., 20., 0.]), torch.tensor([0., 200., 0.]))
        self.assertEqual(fraction.tolist(), [0., 1., 0.])

    def policy(self):
        actor = torch.nn.Module()
        actor.mlp = torch.nn.Sequential(torch.nn.Linear(3, 4), torch.nn.ELU(), torch.nn.Linear(4, 6))
        actor.distribution = torch.nn.Module()
        actor.distribution.std_param = torch.nn.Parameter(torch.full((6,), .2))
        critic = torch.nn.Module()
        critic.mlp = torch.nn.Sequential(torch.nn.Linear(3, 4), torch.nn.ELU(), torch.nn.Linear(4, 1))
        optimizer = torch.optim.Adam(list(actor.parameters()) + list(critic.parameters()), lr=3e-5)
        for parameter in list(actor.parameters()) + list(critic.parameters()):
            parameter.grad = torch.ones_like(parameter)
        optimizer.step()
        return SimpleNamespace(actor=actor, critic=critic, optimizer=optimizer)

    def test_repair_retains_actor_and_recalibrates_only_std_and_value_head(self):
        alg = self.policy()
        actor = {k: v.clone() for k, v in alg.actor.mlp.state_dict().items()}
        hidden = alg.critic.mlp[0].weight.clone()
        momentum = alg.optimizer.state[alg.actor.mlp[0].weight]['exp_avg'].clone()
        initialize(alg)
        self.assertTrue(all(torch.equal(v, alg.actor.mlp.state_dict()[k]) for k, v in actor.items()))
        self.assertTrue(torch.equal(hidden, alg.critic.mlp[0].weight))
        self.assertTrue(torch.equal(momentum, alg.optimizer.state[alg.actor.mlp[0].weight]['exp_avg']))
        self.assertTrue(torch.equal(alg.actor.distribution.std_param, torch.tensor(INITIAL_STD)))
        self.assertEqual(float(alg.critic.mlp[-1].weight.detach().abs().sum()), 0.)
        for parameter in (alg.actor.distribution.std_param, alg.critic.mlp[-1].weight, alg.critic.mlp[-1].bias):
            self.assertTrue(all(not bool(v.any()) for v in alg.optimizer.state[parameter].values()))

    def test_exploration_clamp_clears_only_outward_momentum(self):
        alg = self.policy()
        std = alg.actor.distribution.std_param
        with torch.no_grad():
            std.copy_(torch.tensor([-.1, .04, .07, .03, 1., .005]))
        before = alg.optimizer.state[std]['exp_avg'].clone()
        bound_exploration(alg)
        self.assertTrue(in_bounds(std))
        for i in (0, 2, 4, 5):
            self.assertEqual(float(alg.optimizer.state[std]['exp_avg'][i]), 0.)
        for i in (1, 3):
            self.assertEqual(float(alg.optimizer.state[std]['exp_avg'][i]), float(before[i]))


if __name__ == '__main__':
    for path in T.rglob('*.py'):
        ast.parse(path.read_text(encoding='utf-8-sig'))
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Checks))
    report = dict(attempt_id='stable-height-repair-cpu-r1', epoch=time.time(), passed=result.wasSuccessful(),
                  tests_run=result.testsRun, output=stream.getvalue(), optimizer_updates=0)
    (T / 'evidence').mkdir(exist_ok=True)
    (T / 'evidence/OBJECTIVE_CHECK.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf8')
    print(stream.getvalue())
    raise SystemExit(0 if result.wasSuccessful() else 1)
