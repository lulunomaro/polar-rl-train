"""Minimal synthetic tests. Default stdlib/AST ONLY; no checkpoint/raw access.
--torch-smoke is an OPTIONAL parent-CPU test of real reviewed APIs on synthetic
small tensors; not executed locally and not a replay/skill evaluation.
"""
import argparse
import ast
import copy
import importlib.util
import json
from pathlib import Path
import random
import sys
import unittest

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('diag_under_test', HERE / 'replay_consistency_diagnostic_v1.py')
d = importlib.util.module_from_spec(spec)
spec.loader.exec_module(d)


def metadata(T, N=1, start=0):
    out = {k: [[False] * N for _ in range(T)] for k in d.BOOL_FIELDS}
    out['xi1_valid'] = [[True] * N for _ in range(T)]
    out['split_known'] = [[True] * N for _ in range(T)]
    out['ep_step'] = [[start + i] * N for i in range(T)]
    out['f'] = copy.deepcopy(out['ep_step'])
    return out


class SyntheticStdlib(unittest.TestCase):
    def test_import_is_stdlib_only(self):
        self.assertNotIn('torch', sys.modules)
        self.assertNotIn('tensordict', sys.modules)
        self.assertNotIn('supermimic_vendor_v2.learner', sys.modules)

    def test_partial_ring_chronology(self):
        self.assertEqual([d.ring_row(8, 5, 3, i) for i in range(3)], [2, 3, 4])

    def test_wrapped_ring_chronology(self):
        self.assertEqual([d.ring_row(8, 3, 8, i) for i in range(8)], [3, 4, 5, 6, 7, 0, 1, 2])
        with self.assertRaisesRegex(ValueError, 'outside'):
            d.ring_row(8, 3, 8, 8)
        with self.assertRaisesRegex(ValueError, 'metadata'):
            d.ring_row(8, 8, 8, 0)

    def test_unknown_oldest_history_is_skipped_not_padded(self):
        m, rows = metadata(20, start=50), list(range(20))
        self.assertIsNone(d.history_ages(m, rows, 0, 0))
        self.assertIsNone(d.history_ages(m, rows, 8, 0))
        self.assertEqual(d.history_ages(m, rows, 9, 0), list(range(10)))

    def test_true_episode_zero_repeats_known_observation_only(self):
        m, rows = metadata(20), list(range(20))
        self.assertEqual(d.history_ages(m, rows, 0, 0), [0] * 10)
        self.assertEqual(d.history_ages(m, rows, 2, 0), [0] * 8 + [1, 2])

    def test_history_excludes_done_cut_invalid_and_clock_gap(self):
        for key in ('done', 'stream_cut', 'xi1_valid', 'f', 'ep_step'):
            m, rows = metadata(20), list(range(20))
            m[key][4][0] = False if key == 'xi1_valid' else True if key in ('done', 'stream_cut') else 777
            self.assertIsNone(d.history_ages(m, rows, 9, 0), key)

    def test_reset_after_done_can_start_known_history(self):
        m, rows = metadata(20), list(range(20))
        m['done'][4][0], m['xi1_valid'][4][0] = True, False
        for i in range(5, 20):
            m['ep_step'][i][0] = m['f'][i][0] = i - 5
        self.assertEqual(d.history_ages(m, rows, 5, 0), [5] * 10)
        self.assertEqual(d.history_ages(m, rows, 7, 0), [5] * 8 + [6, 7])

    def test_H16_rejects_each_boundary_and_tail(self):
        m, rows = metadata(20), list(range(20))
        self.assertTrue(d.eligible_window(m, rows, 4, 0, 16))
        self.assertFalse(d.eligible_window(m, rows, 5, 0, 16))
        for key in ('done', 'stream_cut', 'xi1_valid'):
            bad = copy.deepcopy(m)
            bad[key][10][0] = key != 'xi1_valid'
            self.assertFalse(d.eligible_window(bad, rows, 0, 0, 16), key)
        # No access to a phantom 17th obs: xi1_valid on real transition16 suffices.
        self.assertTrue(d.eligible_window(m, rows, 0, 0, 16))

    def test_terminal_in_one_step_but_not_H16_context(self):
        m, rows = metadata(20), list(range(20))
        m['done'][19][0], m['xi1_valid'][19][0] = True, False
        one, actor, multi = d.pools(m, rows, 1)
        self.assertIn((19, 0), one)
        self.assertIn((19, 0), actor)  # valid HISTORY before terminal action
        self.assertNotIn((4, 0), multi)

    def test_ring_wrap_boundary_is_chronological_not_physical_index(self):
        rows = [6, 7, 0, 1, 2, 3, 4, 5]
        m = metadata(8)
        for i, row in enumerate(rows):
            m['ep_step'][row][0] = m['f'][row][0] = i
        self.assertEqual(d.history_ages(m, rows, 7, 0, hist=4), [4, 5, 6, 7])
        m['stream_cut'][7][0] = True
        self.assertFalse(d.eligible_window(m, rows, 0, 0, 4))

    def test_legacy_mask_recovery_is_not_universally_held(self):
        layout = [('actor35_original', 35), ('command_age', 1), ('mild_factor', 2),
                  ('recovery_age', 1), ('recovery_recipe', 1), ('recovery_request', 1),
                  ('recovery_credited', 1), ('recovery_stable', 1)]
        mask = d.legacy_mask(layout, 43)
        self.assertEqual(mask[:4], [0.] * 4)
        self.assertEqual(mask[4:14], [1.] * 10)
        self.assertEqual(mask[14:16], [0., 0.])
        self.assertEqual(mask[16:22], [1.] * 6)
        self.assertEqual(mask[22:38], [0.] * 16)
        self.assertEqual(mask[38:43], [1.] * 5)
        with self.assertRaisesRegex(ValueError, 'prefix'):
            d.legacy_mask([('not_actor35', 35)], 35)

    def test_strict_full_config_rejects_missing_extra_type_changed(self):
        task = dict(seed=20260928)
        cfg = dict(copy.deepcopy(d.EXPECTED_CONFIG), seed=task['seed'])
        self.assertEqual(len(d.strict_config(cfg, task)), 64)
        for field, value in [('hist', 11), ('seed', True), ('wm_hidden', [1]), ('amp', 'float16')]:
            bad = copy.deepcopy(cfg)
            bad[field] = value
            with self.assertRaises(ValueError):
                d.strict_config(bad, task)
        bad = copy.deepcopy(cfg)
        del bad['gamma']
        with self.assertRaises(ValueError):
            d.strict_config(bad, task)

    def test_lineage_does_not_fallback_to_incomplete_or_other_role(self):
        pin = d.OWN['E3']
        checkpoint = dict(path=d.role_paths('E3')[2], bytes=pin['bytes'], SHA=pin['SHA'],
                          iteration=pin['iteration'], teacher_unchanged=True,
                          full_new_model_critic_aux_optimizers_replay_RNG_hist_saved=True)
        f = dict(kind='MOD4V1_SUPERMIMIC_FULL_EXECUTION_FINAL_V3', run_id=d.RUN,
            role='E3', role_key=pin['role_key'], actor_view='raw35_legacy_held_aux_v1',
            algorithm_family='a1_raw35_legacy_v1', algorithm_variant='A1_RAW35_FRESH',
            passed_execution=True, teacher_unchanged=True, checkpoint=checkpoint)
        d.validate_final(f, 'E3')
        for field, value in [('path', '/mother.pt'), ('SHA', '0' * 64), ('bytes', 80), ('iteration', 0)]:
            bad = copy.deepcopy(f)
            bad['checkpoint'][field] = value
            with self.assertRaises(ValueError):
                d.validate_final(bad, 'E3')
        with self.assertRaises(ValueError):
            d.validate_final(f, 'W35')

    def test_AST_compile_and_no_training_or_global_seed(self):
        text = (HERE / 'replay_consistency_diagnostic_v1.py').read_text(encoding='utf-8')
        tree = ast.parse(text)
        compile(tree, str(HERE / 'replay_consistency_diagnostic_v1.py'), 'exec')
        calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call)]
        names = [ast.unparse(node.func) for node in calls]
        for forbidden in ('torch.manual_seed', 't.manual_seed', 'random.seed', 't.cuda.get_rng_state',
                          'restore_rng', 'load_full_checkpoint', 't.optim.Adam', 'torch.optim.Adam'):
            self.assertNotIn(forbidden, names)
        self.assertEqual(names.count('t.load'), 1)
        self.assertIn('g.manual_seed', names)
        self.assertNotIn('supermimic_vendor_v2.learner', text)
        self.assertIn('CONDITIONAL_STATE_OPENLOOP', text)
        self.assertIn('FULL_STATE_AND_CONTEXT_OPENLOOP_ALONG_RECORDED_ACTIONS', text)
        self.assertIn("(s['xi1'] - s['xi'])[valid]", text)
        load = next(node for node in calls if ast.unparse(node.func) == 't.load')
        kws = {kw.arg: ast.literal_eval(kw.value) for kw in load.keywords}
        self.assertEqual(kws, dict(map_location='cpu', weights_only=True))

    def test_stdlib_selection_does_not_touch_global_rng(self):
        before = random.getstate()
        d.pools(metadata(20), list(range(20)), 1)
        self.assertEqual(before, random.getstate())


def torch_smoke(args):
    """Parent-only optional API test. Small real networks, synthetic labels only."""
    rt = d.source_runtime(args)  # reads only pinned PY sources, no PT/FINAL/raw
    t, net, ns = rt.t, rt.net, rt.classes
    before = t.get_rng_state().clone()
    py_before = random.getstate()
    C, B, H = 40, 2, 16
    with t.no_grad(), t.random.fork_rng(devices=[]):
        svec = t.zeros(B, 73)
        svec[:, 2], svec[:, 3] = .5, 1.
        mdp = ns['Raw35ActorMDP'](ns['OriginalTaskMdp'](C, svec), transition_projector=None)
        wm = net.WorldModel(hidden=(16, 16), num_joints=30, context_dim=C, action_dim=6)
        aux = ns['TaskAuxiliaryModel'](30, 6, C, hidden=(16,), policy_dt_s=.02)
        residual = net.Policy(35, 3, hist=10, z_dim=4, num_joints=6, hidden=(16,))
        class SyntheticTeacher(t.nn.Module):
            def forward(self, td, stochastic_output=False):
                return td['policy'][..., :6] * .1
        pi = ns['TeacherResidualPolicy'](residual, SyntheticTeacher(), 0, scale=.05)
        for name, model in (('wm', wm), ('aux', aux), ('pi', pi)):
            d.strict_load(model, {k: v.clone() for k, v in model.state_dict().items()}, t, 'SYNTHETIC_' + name)
        models = d.SimpleNamespace(wm=wm, aux=aux, pi=pi, mdp=mdp, mask=t.ones(C))
        a, xi = t.zeros(B, 6), t.zeros(B, C)
        hist = t.zeros(B, 10, 35)
        state = rt.geo.unflatten_state(svec)
        zero = d.state_metrics(state, state, rt, wm)
        assert zero['joint_position_rad']['MAE'] == 0.
        actor = d.actor_metrics(hist, models, rt)
        assert actor['actor_minus_clipped_teacher']['max_abs'] == [0.] * 6
        state0 = {name: model.state_dict(keep_vars=True) for name, model in (('wm', wm), ('aux', aux), ('pi', pi))}
        guard = d.nested_digest(state0, t)
        s = dict(s=svec, s1=svec, a=a, a_prev=a, xi=xi, xi1=xi,
                 r=t.zeros(B), f=t.zeros(B, dtype=t.long), done=t.zeros(B, dtype=t.bool),
                 stream_cut=t.zeros(B, dtype=t.bool), xi1_valid=t.ones(B, dtype=t.bool))
        context, frames = xi, s['f']
        for k in range(H):
            new = wm.step(state, a, mdp.normalize_context(context))
            panel, context, reward = d.auxiliary_metrics(s, state, new, context, a, frames, models, rt)
            assert panel['reward']['samples'] == B and t.isfinite(reward).all()
            assert panel['done']['positive_labels'] == 0
            state, frames = new, frames + 1
        assert t.equal(frames, s['f'] + H)
        assert d.nested_digest(state0, t) == guard
        # Deliberately mutate a copied model state, never source/cache, to prove value guard discriminates.
        copied = {k: v.clone() for k, v in wm.state_dict().items()}
        old = d.nested_digest(copied, t)
        first = next(v for v in copied.values() if v.is_floating_point() and v.numel())
        first.reshape(-1)[0] += 1
        assert d.nested_digest(copied, t) != old
    assert t.equal(t.get_rng_state(), before) and random.getstate() == py_before
    assert not t.cuda.is_initialized()
    print(json.dumps(dict(status='SYNTHETIC_REAL_TORCH_CPU_API_ONLY', torch_version=str(t.__version__),
        no_checkpoint_reads=True, no_optimizer=True, no_skill_claim=True, sources=rt.sources), allow_nan=False))


def main():
    if '--torch-smoke' in sys.argv:
        p = argparse.ArgumentParser(description=__doc__)
        p.add_argument('--torch-smoke', action='store_true')
        for key in d.SOURCE_PINS:
            p.add_argument('--' + key.replace('_', '-'), type=Path, required=True)
        p.add_argument('--vendor-parent', type=Path, required=True)
        p.add_argument('--dependency-path', type=Path, action='append', default=[])
        torch_smoke(p.parse_args())
    else:
        unittest.main(verbosity=2)


if __name__ == '__main__':
    main()
