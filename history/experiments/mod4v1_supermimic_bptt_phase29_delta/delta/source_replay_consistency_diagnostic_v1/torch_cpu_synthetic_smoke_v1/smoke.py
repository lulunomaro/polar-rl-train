"""NEW parent-only CPU Torch synthetic replay smoke; never opens PT/raw/FINAL.

Exercises the SHA-sealed diagnostic's real WM/aux/pi/history/H16 implementation
on a tiny own synthetic ring. NOT production admission/restore/skill evidence.
Stdlib --ast-only is the only locally executed branch.
"""
from __future__ import annotations
import argparse
import ast
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import random
import sys

sys.dont_write_bytecode = True
DIAGNOSTIC_SHA = 'a372478e40d1eb0b569f1f6c86d45f285031ab5399e00efe61b20bdc2f462eec'


def load_diagnostic(path):
    path = path.resolve(strict=True)
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == DIAGNOSTIC_SHA, 'sealed diagnostic SHA differs'
    spec = importlib.util.spec_from_file_location('_new_synthetic_replay_diag', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def ast_only(d):
    # Own source/class API gate; no Torch import or checkpoint access.
    tree = ast.parse(Path(__file__).read_text(encoding='utf-8'))
    compile(tree, __file__, 'exec')
    calls = [ast.unparse(n.func) for n in ast.walk(tree) if isinstance(n, ast.Call)]
    assert 't.load' not in calls and 'torch.load' not in calls
    assert 't.optim.Adam' not in calls and 'torch.optim.Adam' not in calls
    assert 't.manual_seed' not in calls and 'random.seed' not in calls
    assert 'torch' not in sys.modules
    T, ptr = 48, 17
    rows = [d.ring_row(T, ptr, T, i) for i in range(T)]
    assert rows == list(range(17, 48)) + list(range(17))
    meta = {k: [[False, False] for _ in range(T)] for k in d.BOOL_FIELDS}
    meta['xi1_valid'] = [[True, True] for _ in range(T)]
    meta['f'] = [[0, 0] for _ in range(T)]
    meta['ep_step'] = [[0, 0] for _ in range(T)]
    for age, row in enumerate(rows):
        f = 50 + age if age <= 12 else age - 13 if age <= 30 else age - 31
        meta['f'][row] = [f, f]
        meta['ep_step'][row] = [f, f]
    meta['done'][rows[12]] = [True, True]
    meta['xi1_valid'][rows[12]] = [False, False]
    meta['stream_cut'][rows[30]] = [True, True]
    meta['xi1_valid'][rows[44]] = [False, False]
    meta['xi1_valid'][rows[-1]] = [False, False]
    assert d.history_ages(meta, rows, 0, 0) is None
    assert d.history_ages(meta, rows, 13, 0) == [13] * 10
    assert not d.eligible_window(meta, rows, 0, 0, 16)
    assert not d.eligible_window(meta, rows, 16, 0, 16)
    assert not d.eligible_window(meta, rows, 31, 0, 16)
    assert d.eligible_window(meta, rows, 13, 0, 16)
    assert d.eligible_window(meta, rows, 14, 0, 16)
    assert d.legacy_mask([('actor35_original', 35), ('SYNTHETIC_ONLY_EXTRA', 5)], 40)[35:] == [1.] * 5
    print(json.dumps(dict(status='STDLIB_AST_SYNTHETIC_PLAN_ONLY_PASS', torch_imported=False,
        real_Torch_PASS=False, real_checkpoint_opens=0, diagnostic_SHA256=DIAGNOSTIC_SHA)))


def smoke(d, args):
    rt = d.source_runtime(args)  # only SHA-pinned reviewed .py + actual CPU deps
    t, net, ns, helper = rt.t, rt.net, rt.classes, rt.helper
    assert not t.cuda.is_initialized()
    global_rng = t.get_rng_state().clone()
    py_rng = random.getstate()
    np = sys.modules.get('numpy')
    np_rng = repr(np.random.get_state()) if np is not None else None
    threads = t.get_num_threads()
    t.set_num_threads(1)
    T, N, C, ptr = 48, 2, 40, 17
    rows = [d.ring_row(T, ptr, T, age) for age in range(T)]
    layout = [('actor35_original', 35), ('SYNTHETIC_ONLY_EXTRA', 5)]
    mask = t.tensor(d.legacy_mask(layout, C), dtype=t.float32)
    with t.no_grad(), t.random.fork_rng(devices=[]):
        sample = t.zeros(N, 73)
        sample[:, 2], sample[:, 3] = .5, 1.
        mdp = ns['Raw35ActorMDP'](ns['OriginalTaskMdp'](C, sample), transition_projector=None)
        wm = net.WorldModel(hidden=(16, 16), num_joints=30, context_dim=C, action_dim=6)
        aux = ns['TaskAuxiliaryModel'](30, 6, C, hidden=(16,), policy_dt_s=.02)
        obs = rt.TD(dict(policy=t.zeros(2, 35), critic=t.zeros(2, 38)), batch_size=[2])
        distribution = dict(class_name='rsl_rl.modules.distribution:GaussianDistribution', init_std=1., std_type='scalar')
        teacher = rt.MLP(obs, dict(actor=['policy'], critic=['critic']), 'actor', 6, [256, 128, 64], 'elu', distribution_cfg=distribution)
        residual = net.Policy(35, 3, hist=10, z_dim=4, num_joints=6, hidden=(16,))
        pi = ns['TeacherResidualPolicy'](residual, teacher, 0, scale=.05)
        # Different modeled/recorded sensor increments force FULL vs conditional
        # input paths to differ; labels remain synthetic, not task sensor truth.
        aux.net[-1].bias[1 + 4] = .002 / aux.context_norm.std()[4]
        models = d.SimpleNamespace(wm=wm, aux=aux, pi=pi, mdp=mdp, mask=mask.clone())
        for name, model in (('wm', wm), ('aux', aux), ('pi', pi)):
            saved = {k: v.detach().clone() for k, v in model.state_dict().items()}
            d.strict_load(model, saved, t, 'OWN_SYNTHETIC_' + name)
        # Read actual kwargs/API from real norm, features, projector, MLP/wrapper.
        assert mdp.obs(rt.geo.unflatten_state(sample), t.zeros(N, 6), t.zeros(N, C), t.zeros(N)).shape == (N, 35)
        assert wm.step(rt.geo.unflatten_state(sample), t.zeros(N, 6), t.zeros(N, C))[0].shape == (N, 3)
        features = aux.features(rt.geo.unflatten_state(sample), rt.geo.unflatten_state(sample),
            t.zeros(N, 6), t.zeros(N, 6), t.zeros(N, C), t.tensor([2, 3]))
        assert t.allclose(features[:, -1], t.tensor([.04, .06]))
        projection = mdp.project_predicted_context(t.ones(N, C), rt.geo.unflatten_state(sample), t.zeros(N, 6), t.zeros(N))
        assert t.equal(projection[:, 14:16], t.zeros(N, 2)) and t.equal(projection[:, 22:28], t.zeros(N, 6))
        assert t.equal(projection[:, 35:], t.ones(N, C - 35))
        assert d.state_metrics(rt.geo.unflatten_state(sample), rt.geo.unflatten_state(sample), rt, wm)['joint_position_rad']['MAE'] == 0.
        data = {}
        for name, width in d.FLOAT_WIDTHS.items():
            width = C if name in ('xi', 'xi1') else width
            data[name] = t.zeros((T, N, width) if width else (T, N), dtype=t.float32)
        for name in d.BOOL_FIELDS:
            data[name] = t.zeros(T, N, dtype=t.bool)
        data['f'] = t.zeros(T, N, dtype=t.long)
        data['ep_step'] = t.zeros(T, N, dtype=t.int32)
        data['xi1_valid'].fill_(True)
        data['split_known'].fill_(True)
        for age, row in enumerate(rows):
            frames = 50 + age if age <= 12 else age - 13 if age <= 30 else age - 31
            data['f'][row].fill_(frames)
            data['ep_step'][row].fill_(frames)
            data['s'][row].copy_(sample)
            data['s1'][row].copy_(sample)  # true synthetic PRE-RESET terminal label
            data['xi'][row, :, 4] = .005 * age
            data['r'][row].fill_(.25 + .01 * (age % 7))
        for age, row in enumerate(rows):
            if age + 1 < T:
                data['xi1'][row].copy_(data['xi'][rows[age + 1]])
        terminal, cut, invalid, tail = (rows[i] for i in (12, 30, 44, T - 1))
        data['done'][terminal].fill_(True)
        data['term'][terminal].fill_(True)
        data['xi1_valid'][terminal].fill_(False)
        data['xi1'][terminal].zero_()  # invalid, not a next-observation target
        data['stream_cut'][cut].fill_(True)
        data['xi1_valid'][invalid].fill_(False)
        data['xi1_valid'][tail].fill_(False)
        replay = dict(T=T, N=N, ptr=ptr, size=T, data=data)
        meta = {name: data[name].tolist() for name in (*d.BOOL_FIELDS, 'f', 'ep_step')}
        raw = b'OWN_SYNTHETIC_RAW_NOT_A_PT_OR_NATIVE_ARTIFACT'
        root = dict(kind='OWN_SYNTHETIC_REPLAY_NOT_PRODUCTION_CHECKPOINT', replay=replay,
            model_states={name: {k: v.detach().clone() for k, v in model.state_dict().items()}
                          for name, model in (('wm', wm), ('aux', aux), ('pi', pi))},
            unused_saved_tensor=t.arange(5), saved_history=t.zeros(N, 10, 35),
            saved_RNG=t.get_rng_state().clone(), raw=raw)
        root_guard = helper._snapshot(root, t, require_cpu=True)
        root_before = d.nested_digest(root, t)
        raw_before = hashlib.sha256(raw).hexdigest()
        live = {name: model.state_dict(keep_vars=True) for name, model in (('wm', wm), ('aux', aux), ('pi', pi))}
        live_guard = helper._snapshot(live, t, require_cpu=True)
        live_before = d.nested_digest(live, t)
        opts = d.SimpleNamespace(sample_seed=20261103, batch=16, windows=4, full_context_openloop=True)
        with t.no_grad():
            report = d.run_diagnostics(models, rt, replay, rows, meta, layout, opts)
        helper._same(root, root_guard, t, require_cpu=True)
        helper._same(live, live_guard, t, require_cpu=True)
        assert root_before == d.nested_digest(root, t)
        assert live_before == d.nested_digest(live, t)
        assert raw is root['raw'] and raw_before == hashlib.sha256(raw).hexdigest()
        assert all(not m.training and all(not p.requires_grad and p.grad is None for p in m.parameters())
                   for m in (wm, aux, pi))
        conditional = report['H16']['CONDITIONAL_STATE_OPENLOOP']
        full = report['H16']['FULL_STATE_AND_CONTEXT_OPENLOOP_ALONG_RECORDED_ACTIONS']
        assert conditional['n'] == full['n'] == 4 and len(conditional['steps']) == len(full['steps']) == 16
        assert conditional['oracle_context_used_after_start'] is True
        assert full['oracle_context_used_after_start'] is False
        assert full['actual_policy_imagination_full_chain'] is False
        assert report['actor']['n'] > 0
        assert report['sampling']['original_ring']['chronological_rows'] == rows
        assert report['sampling']['exclusions']['actor_unknown_or_discontinuous_history'] > 0
        assert report['sampled_clock_and_present_recovery_fields_ONLY']['source_context_values'] == {}
        assert set(report['one_step_observed_groups']) == {'raw35_mode28_35_exact_vector'}
        # Distinguish conditioned versus aux-carried context drift on same windows.
        key = 'effective_legacy_projected_next_context'
        c_err = conditional['steps'][-1]['aux'][key]['raw35_sensor_slots4_14_and16_22']['MAE']
        f_err = full['steps'][-1]['aux'][key]['raw35_sensor_slots4_14_and16_22']['MAE']
        assert abs(c_err - f_err) > 1e-6, 'FULL unexpectedly oracle-reanchored or synthetic stimulus absent'
        # Negative guard check on OWN copies only: .data bypasses version but
        # full-value digest must still detect it; version-aware guard detects add_.
        copied = {'v': t.zeros(2)}
        snap, h = helper._snapshot(copied, t, require_cpu=True), d.nested_digest(copied, t)
        copied['v'].data.add_(1.)
        assert d.nested_digest(copied, t) != h
        helper._same(copied, snap, t, require_cpu=True)
        copied['v'].add_(1.)
        detected = False
        try:
            helper._same(copied, snap, t, require_cpu=True)
        except ValueError:
            detected = True
        assert detected, 'version guard negative control missed own mutation'
    assert t.equal(t.get_rng_state(), global_rng) and random.getstate() == py_rng
    assert np is None or repr(np.random.get_state()) == np_rng
    assert not t.cuda.is_initialized()
    t.set_num_threads(threads)
    result = dict(kind='NEW_OWN_SYNTHETIC_TORCH_CPU_REPLAY_SMOKE_V1', status='PASS',
        interpretation='API/SHAPE/NORM/READONLY synthetic only; not production admission or skill',
        diagnostic_SHA256=DIAGNOSTIC_SHA, smoke_source_SHA256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        torch_version=str(t.__version__), sources=rt.sources,
        T=T, N=N, ptr=ptr, size=T, synthetic_batch=16, H16_windows=4,
        tested=['wrapped ring', 'done/cut/xi1_invalid/tail', 'known-only history10',
                'real WM.step/aux.features/legacy project/real MLP teacher', 'two labeled matched H16 modes',
                'whole root/live values+identity+versions', 'immutable own raw',
                'global Torch/Python/NumPy RNG unchanged', 'value/version negative controls'],
        unknown_original_UID_phase_recovery_fields='EXPECTED_MISSING_NOT_FABRICATED',
        production_checkpoint_raw_FINAL_TASK_opens=0, optimizer_instances_updates=0,
        native_BPTT_updates=0, SDK_env_created=False, CUDA_initialized=False,
        synthetic_report=report)
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--diagnostic', type=Path, default=Path(__file__).resolve().parents[1] / 'replay_consistency_diagnostic_v1.py')
    p.add_argument('--ast-only', action='store_true')
    for key in ('bridge_source', 'core_source', 'raw35_source', 'cache_source'):
        p.add_argument('--' + key.replace('_', '-'), type=Path)
    p.add_argument('--vendor-parent', type=Path)
    p.add_argument('--dependency-path', type=Path, action='append', default=[])
    p.add_argument('--output', type=Path, help='optional new own synthetic JSON; outside original producer root')
    args = p.parse_args()
    d = load_diagnostic(args.diagnostic)
    if args.ast_only:
        ast_only(d)
        return
    for key in (*d.SOURCE_PINS, 'vendor_parent'):
        d.need(getattr(args, key) is not None, 'reviewed source path required: ' + key)
    os.environ['CUDA_VISIBLE_DEVICES'] = ''
    result = smoke(d, args)
    if args.output is not None:
        path = args.output.resolve()
        d.need(not path.exists() and path.parent.is_dir() and not path.is_relative_to(Path(d.ROOT).resolve()),
               'new own synthetic output outside original producer root required')
        with path.open('x', encoding='utf-8', newline='\n') as stream:
            json.dump(result, stream, indent=2, allow_nan=False)
            stream.write('\n')
    print(json.dumps({key: value for key, value in result.items() if key != 'synthetic_report'}, allow_nan=False))


if __name__ == '__main__':
    main()
