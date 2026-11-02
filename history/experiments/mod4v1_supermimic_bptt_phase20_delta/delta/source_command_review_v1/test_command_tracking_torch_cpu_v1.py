"""SELF-CONTAINED SYNTHETIC CPU software/autograd tests, NOT expert training.

Parent runs this script ONLY on an already provisioned CPU Torch installation.
Needs adjacent command_tracking_torch_candidate_v1.py; no vendor/SDK/checkpoints.
No optimizer steps, simulator, real data or expert BPTT count. No file is written
unless --output points to a NEW file in the parent's new CPU-purpose root.
"""
import os
os.environ['CUDA_VISIBLE_DEVICES'] = ''
import argparse
from pathlib import Path
import json
import math
import sys
import unittest
import torch
from torch import nn
from command_tracking_torch_candidate_v1 import (
    UnknownCommandEvolution, ProjectedTransition, Raw35ActorMDP,
    BoundedTeacherResidualPolicy, ScaledTeacherResidualPolicy35,
    sampled_state_sensor_inputs, compose_raw35, e2_command, w35_all_rough_command,
    original_tracking_terms, lower_confidence_reward)

torch.set_num_threads(1)
torch.set_default_dtype(torch.float64)
torch.manual_seed(37)
GRADIENT_RECEIPTS = {}


class BaseMDP:
    obs_dim = 179
    context_dim = 100
    goal_frame_dim = 3
    def to(self, device):
        return self
    def critic_features(self, state, frames, context):
        return torch.cat((state[0], context), -1)


class Residual(nn.Module):
    def __init__(self, hist=2):
        super().__init__()
        self.obs_norm = nn.Identity()
        self.goal_norm = nn.Identity()
        self.dec = nn.Sequential(nn.Linear(hist * 35 + 3, 6))
    def forward(self, history, goal):
        return self.dec(torch.cat((history.flatten(-2), goal), -1))


class Teacher(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Linear(35, 6, bias=False)
        with torch.no_grad():
            self.net.weight.fill_(.01)
    def forward(self, raw):
        return self.net(raw)


def make_policy(bounded=True, **kw):
    cls = BoundedTeacherResidualPolicy if bounded else ScaledTeacherResidualPolicy35
    return cls(Residual(), Teacher(), lambda t, raw: t(raw), **kw)


def samples(batch=2):
    return {'base_ang_vel': torch.ones(batch, 3),
            'projected_gravity': torch.tensor([[0., 0., -1.]]).repeat(batch, 1),
            'leg_pos': torch.ones(batch, 4) * .1,
            'leg_vel': torch.ones(batch, 4) * 2.,
            'wheel_vel': torch.ones(batch, 2) * 3.}


def identity_state(batch=2, joints=8):
    return (torch.zeros(batch, 3), torch.eye(3).repeat(batch, 1, 1),
            torch.zeros(batch, 3), torch.zeros(batch, 3),
            torch.zeros(batch, joints), torch.zeros(batch, joints))


class CandidateTests(unittest.TestCase):
    def test_01_raw35_actor_identity_and_privileged_invariance(self):
        mdp = Raw35ActorMDP(BaseMDP())
        xi = torch.randn(2, 100)
        a = mdp.obs(None, None, xi, None)
        xi2 = xi.clone()
        xi2[:, 35:] = 1000.
        torch.testing.assert_close(a, xi[:, :35])
        torch.testing.assert_close(a, mdp.obs(None, None, xi2, None))
        self.assertEqual(mdp.obs_dim, 35)
        self.assertEqual(mdp.goal_with_context(None, 2, xi).shape, (2, 6))

    def test_02_teacher_frozen_and_raw_input_grad_preserved(self):
        p = make_policy()
        h = torch.ones(2, 2, 35, requires_grad=True)
        y = p(h, torch.zeros(2, 3))
        g, = torch.autograd.grad(y.sum(), h)
        self.assertGreater(float(g[:, -1].abs().sum()), 0.)
        self.assertTrue(all(not t.requires_grad for t in p.teacher.parameters()))
        self.assertTrue(all(t.grad is None for t in p.teacher.parameters()))
        self.assertFalse(p.teacher.training)
        p.train(True)
        self.assertFalse(p.teacher.training)

    def test_03_rejects_sim_privileged_policy_history(self):
        with self.assertRaisesRegex(ValueError, 'raw35 history only'):
            make_policy()(torch.zeros(2, 2, 179), torch.zeros(2, 3))

    def test_04_bounded_large_logits_and_teacher_action_clamp(self):
        p = make_policy()
        with torch.no_grad():
            p.residual.dec[-1].bias.fill_(1e6)
        h = torch.ones(2, 2, 35)
        baseline = p.teacher_baseline(h)
        out = p(h, torch.zeros(2, 3))
        self.assertLessEqual(float((out - baseline).abs().max()), .05 + 1e-12)
        self.assertLessEqual(float(out.abs().max()), 6.)

    def test_05_original_scaled_residual_is_not_bound(self):
        p = make_policy(bounded=False)
        with torch.no_grad():
            p.residual.dec[-1].bias.fill_(1000.)
        out = p(torch.zeros(2, 2, 35), torch.zeros(2, 3))
        self.assertEqual(float(out.max()), 6.)
        self.assertGreater(float(out.max()), .05)

    def test_06_anchor_default_zero_is_separate_ablation(self):
        p = make_policy()
        h = torch.zeros(2, 2, 35)
        out = p(h, torch.zeros(2, 3))
        self.assertEqual(float(p.policy_regularizer(h, None, out).sum()), 0.)

    def test_07_anchor_has_student_gradient(self):
        p = make_policy(anchor_coefficient=.3)
        with torch.no_grad():
            p.residual.dec[-1].bias.fill_(.2)
        h = torch.zeros(2, 2, 35)
        out = p(h, torch.zeros(2, 3))
        reg = p.policy_regularizer(h, None, out).mean()
        reg.backward()
        self.assertGreater(float(reg), 0.)
        self.assertGreater(float(p.residual.dec[-1].bias.grad.abs().sum()), 0.)
        self.assertTrue(all(v.grad is None for v in p.teacher.parameters()))

    def test_08_e2_world_to_body_two_V_cos_and_heading_gradient(self):
        heading = torch.tensor([0., math.pi / 2, math.pi], requires_grad=True)
        c = e2_command(torch.zeros(3, 3), heading, world_direction=torch.zeros(3),
                       signed_yaw=torch.ones(3) * 4., moving=torch.ones(3, dtype=torch.bool),
                       transition=torch.zeros(3, dtype=torch.bool), standing=torch.zeros(3, dtype=torch.bool),
                       next_write_elapsed=torch.zeros(3), progress_goal=.5, body_limit=1.5)
        torch.testing.assert_close(c[:, 0], torch.tensor([1., 0., -1.]), atol=1e-12, rtol=0.)
        g, = torch.autograd.grad(c[:, 0].sum(), heading)
        self.assertAlmostEqual(float(g[1]), -1.)
        self.assertEqual(float(c[:, 1].abs().sum()), 0.)

    def test_09_e2_transition_phase_clock_and_boolean_stand(self):
        c = e2_command(torch.zeros(2, 3), torch.zeros(2), world_direction=torch.zeros(2),
                       signed_yaw=torch.ones(2) * 4., moving=torch.zeros(2, dtype=torch.bool),
                       transition=torch.ones(2, dtype=torch.bool), standing=torch.tensor([False, True]),
                       next_write_elapsed=torch.ones(2) * 4.02, progress_goal=.5, body_limit=1.5)
        self.assertAlmostEqual(float(c[0, 2]), 3.92)
        self.assertEqual(float(c[1].abs().sum()), 0.)

    def test_10_w35_actual_allrough_held_negative_and_boolean_stand(self):
        c = w35_all_rough_command(torch.tensor([[-.2, 0., 0.], [.1, 0., 0.]]), torch.tensor([False, True]))
        torch.testing.assert_close(c, torch.tensor([[-.2, 0., 0.], [0., 0., 0.]]))

    def test_11_sample_projection_actual_indices_and_nonzero_defaults(self):
        s = list(identity_state())
        s[4] = torch.arange(8.).repeat(2, 1)
        s[5] = torch.arange(8.).repeat(2, 1) * 2.
        dq, dv = torch.ones(2, 8) * .1, torch.ones(2, 8) * .2
        x = sampled_state_sensor_inputs(tuple(s), (5, 1, 4, 2), (6, 3), dq, dv)
        torch.testing.assert_close(x['leg_pos'][0], torch.tensor([4.9, .9, 3.9, 1.9]))
        torch.testing.assert_close(x['wheel_vel'][0], torch.tensor([11.8, 5.8]))
        torch.testing.assert_close(x['projected_gravity'][0], torch.tensor([0., 0., -1.]))

    def test_12_compose_shared_sensor_projection_scales(self):
        x = compose_raw35(torch.zeros(2, 3), torch.ones(2) * .25, samples(),
                          torch.ones(2, 6), torch.zeros(2, 7))
        self.assertEqual(x.shape, (2, 35))
        self.assertAlmostEqual(float(x[0, 3]), 1.25)
        self.assertAlmostEqual(float(x[0, 4]), .5)
        self.assertEqual(float(x[:, 14:16].abs().sum()), 0.)
        self.assertAlmostEqual(float(x[0, 20]), .3)
        self.assertEqual(float(x[:, 22:28].min()), 1.)

    def test_13_strict_unknown_without_provider(self):
        m = Raw35ActorMDP(BaseMDP())
        with self.assertRaises(UnknownCommandEvolution):
            m.project_transition_context(torch.zeros(2, 100), None, None, torch.zeros(2, 6),
                                         None, None, torch.zeros(2, 100), torch.ones(100))

    def test_14_unknown_resample_not_silently_masked_or_filtered(self):
        f = lambda *args: ProjectedTransition(torch.zeros(2, 3), no_resample_or_reset=False)
        m = Raw35ActorMDP(BaseMDP(), f)
        with self.assertRaisesRegex(UnknownCommandEvolution, 'unknown command boundary'):
            m.project_transition_context(torch.zeros(2, 100), None, None, torch.zeros(2, 6),
                                         None, None, torch.zeros(2, 100), torch.ones(100))

    def test_15_missing_100Hz_samples_is_unknown_by_default(self):
        f = lambda *args: ProjectedTransition(torch.zeros(2, 3), command_clock_verified=True,
                                             no_resample_or_reset=True)
        m = Raw35ActorMDP(BaseMDP(), f)
        with self.assertRaisesRegex(UnknownCommandEvolution, 'SAMPLE-time'):
            m.project_transition_context(torch.zeros(2, 100), None, None, torch.zeros(2, 6),
                                         None, None, torch.zeros(2, 100), torch.ones(100))

    def test_16_explicit_sensor_aux_approximation_is_labelled(self):
        f = lambda *args: ProjectedTransition(torch.ones(2, 3), command_clock_verified=True,
                                             no_resample_or_reset=True)
        m = Raw35ActorMDP(BaseMDP(), f, require_sampled_sensor_projection=False)
        xi = torch.zeros(2, 100)
        delta = torch.ones(2, 100)
        y = m.project_transition_context(xi, None, None, torch.ones(2, 6) * 2.,
                                         None, None, delta, torch.ones(100))
        self.assertEqual(m.last_projection_status, 'command_exact_sensor_aux_approximation')
        self.assertEqual(float(y[0, 4]), 1.)
        self.assertEqual(float(y[0, 22]), 2.)
        self.assertEqual(float(y[0, 35]), 1.)
        self.assertEqual(m.obs(None, None, y, None).shape[-1], 35)

    def test_17_exact_projection_preserves_noisy_samples_and_gradient(self):
        action = torch.zeros(2, 6, requires_grad=True)
        sample_omega = action[:, :3] * .02 + 9.  # synthetic sampled/noisy channel
        def f(*args):
            x = samples()
            x['base_ang_vel'] = sample_omega
            return ProjectedTransition(torch.zeros(2, 3), x, True, True, True,
                                       'SYNTHETIC_sample_receipts_only')
        m = Raw35ActorMDP(BaseMDP(), f)
        xi = torch.zeros(2, 100)
        xi[:, 3] = 1.25
        y = m.project_transition_context(xi, None, None, action, None, None,
                                         torch.zeros_like(xi), torch.ones(100))
        self.assertEqual(float(y[0, 4]), 4.5)
        g, = torch.autograd.grad(y[:, 4:7].sum(), action)
        torch.testing.assert_close(g[:, :3], torch.ones(2, 3) * .01)

    def test_18_reward_decomposition_uses_old_command_and_precontrol_frame(self):
        seen = []
        def component(s1, xi, f):
            seen.append((xi[:, 0].clone(), f.clone()))
            return xi[:, 0] + f * .001
        m = Raw35ActorMDP(BaseMDP(), tracking_component=component)
        xi = torch.zeros(2, 100)
        xi[:, 0] = .3
        f = torch.tensor([11., 12.])
        sample = {'r': torch.tensor([-.7, 1.3]), 'xi': xi, 'f': f}
        target = m.aux_reward_target(sample, None, None)
        reconstructed = m.project_imagined_reward(target, None, None, None, None, xi, f)
        torch.testing.assert_close(reconstructed, sample['r'])
        torch.testing.assert_close(seen[0][0], torch.ones(2) * .3)
        torch.testing.assert_close(seen[0][1], f)

    def test_19_source_tracking_exp_sigma_and_original_gate(self):
        cmd = torch.tensor([[.5, 0., .5]])
        x = original_tracking_terms(cmd, torch.zeros(1, 3), torch.zeros(1, 3),
                                    torch.tensor([[0., 0., -1.]]), height_gate=.2)
        self.assertAlmostEqual(float(x['track_lin_vel'][0]), math.exp(-1.))
        self.assertAlmostEqual(float(x['track_ang_vel_square'][0]), (.25 * .5) ** 2 * .2)

    def test_20_uncertainty_is_separate_ensemble_lower_bound(self):
        pred = torch.tensor([[1., 3.], [3., 5.]])
        torch.testing.assert_close(lower_confidence_reward(pred, .5), torch.tensor([1.5, 3.5]))
        with self.assertRaises(ValueError):
            lower_confidence_reward(pred[:1], .5)

    def test_21_H16_delayed_s1_to_a0_autograd_not_aprev_shortcut(self):
        a0 = torch.tensor(.2, requires_grad=True)
        s1 = torch.tensor(.1) + .02 * a0
        heading = s1
        future = []
        for t in range(1, 16):
            c = e2_command(torch.zeros(1, 3), heading.reshape(1), world_direction=torch.zeros(1),
                           signed_yaw=torch.ones(1) * 4., moving=torch.ones(1, dtype=torch.bool),
                           transition=torch.zeros(1, dtype=torch.bool), standing=torch.zeros(1, dtype=torch.bool),
                           next_write_elapsed=torch.zeros(1), progress_goal=.5, body_limit=1.5)
            a = .2 + .1 * c[0, 0]
            heading = heading + .02 * a
            future.append((.99 ** t) * -(c[0, 0] - .5).square())
        delayed = torch.stack(future).sum()
        direct, = torch.autograd.grad(delayed, a0, retain_graph=True)
        cot, = torch.autograd.grad(delayed, s1, retain_graph=True)
        vjp, = torch.autograd.grad(s1, a0, grad_outputs=cot.detach(), retain_graph=True)
        self.assertTrue(bool(torch.isfinite(direct) & torch.isfinite(vjp)))
        self.assertGreater(float(direct.abs()), 0.)
        self.assertGreater(float(vjp.abs()), 0.)
        torch.testing.assert_close(direct, vjp)
        GRADIENT_RECEIPTS.update(kind='SYNTHETIC_autograd_only_no_optimizer_step',
                                 horizon=16, delayed_to_a0=float(direct),
                                 delayed_to_s1=float(cot), s1_to_a0_VJP=float(vjp),
                                 aprev_shortcut_used=False)

    def test_22_no_CUDA_or_SDK_import(self):
        self.assertFalse(torch.cuda.is_initialized())
        self.assertTrue(all(not k.startswith(('isaaclab', 'omni.', 'isaacsim')) for k in sys.modules))


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--output')
    args, remaining = ap.parse_known_args()
    # TextTestRunner writes normal stdout; no subprocess capture, no vendor package.
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__]))
    payload = dict(kind='SYNTHETIC_CPU_TORCH_SOFTWARE_AUTOGRAD_ONLY_NOT_EXPERT_TRAINING',
                   passed=result.wasSuccessful(), tests=result.testsRun,
                   failures=len(result.failures), errors=len(result.errors),
                   torch_version=torch.__version__, CUDA_initialized=torch.cuda.is_initialized(),
                   SDK_imported=False, optimizer_steps=0, native_expert_BPTT_updates_counted=0,
                   gradient_receipts=GRADIENT_RECEIPTS,
                   failure_details=[str(x) for x in result.failures + result.errors])
    if args.output:
        target = Path(args.output).resolve()
        if target.exists():
            raise FileExistsError(str(target))
        target.write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(payload, indent=2))
    raise SystemExit(0 if result.wasSuccessful() else 1)
