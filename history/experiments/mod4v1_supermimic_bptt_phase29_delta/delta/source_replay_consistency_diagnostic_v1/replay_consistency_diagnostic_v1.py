"""SOURCE ONLY. CPU posthoc replay/resubstitution consistency, NOT skill evaluation.

Import is stdlib-only. CLI requires the two allowlisted own checkpoints' actual
FINAL byte pins and reviewed sources. Never constructs a learner/optimizer/env.
"""
from __future__ import annotations

import argparse
import ast
from collections.abc import Mapping
import hashlib
import importlib
import importlib.util
import inspect
import io
import json
import math
import os
from pathlib import Path
import random
import sys
from types import SimpleNamespace

sys.dont_write_bytecode = True
RUN = 'MOD4V1_A1_RAW35_V6_ADMISSION2_20261102_231937_1793632777470828000'
ROOT = '/home/lc01/Zonglin Li/zonglin2/tasks/' + RUN
ASSET = '2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3'
CONTRACT = 'bae3203a7c30f75e29c20c0b0d0e215af5edfc7dbeacb9ebc5310f7867c98755'
OWN = {
    'E3': dict(role_key='supermimic_e3_72', filename='model_BPTT002182_I002282_S0005_complete.pt',
               bytes=236664417, SHA='a4c56390b4c549ba8bfb808a63206c0816ad50e8c9659dc053f98cc66b3c8127', iteration=2282),
    'W35': dict(role_key='supermimic_w35_72', filename='model_BPTT001973_I002073_S0005_complete.pt',
                bytes=233435425, SHA='b2f2878ff9aa04ddcd283fe71f5b5924b1bff78b3f04118cfa689244b0665cff', iteration=2073),
}
SOURCE_PINS = {
    'bridge_source': '8211964c2ce3dd78fdb9fee6603ee4a4dcfbca6fa9d7df44f20d3ddb7aaead29',
    'core_source': '20fd4945a0f2345c17505316560ae6d358fcce147c6988f62a08d867e084e749',
    'raw35_source': 'bb7555ff2de598677ea6cfe5dadefe0a9cfe37d37661635d186bcb14c1df2223',
    'cache_source': '1ea4bcfa1081d63d0da2136fedf8c9fafa508d7bb2155095352da496327e4a21',
}
VENDOR_PINS = {
    'networks.py': 'c7829e6a1bb9166d724a931858b76424439f371669dfb4bb534b9e76c5c74706',
    'geometry.py': '89ac3b9470fd6f041fd418365283355a07ad96c4bf38740cf3c5d2d98acb7787',
    'contract.py': 'd756f2a102a81b2f16295dad66f46e9783b42a3f67e7416360fcf136c2ff06ce',
}
# Complete producer config, from reviewed worker override + vendor dataclass.
# seed is separately bound to the original TASK JSON, never inferred from replay.
EXPECTED_CONFIG = dict(iterations=100000, buffer_steps=128, utd=.4, horizon=16,
    goal_frames=1, hist=10, z_dim=32, wm_hidden=[512, 512, 512],
    policy_hidden=[512, 256, 128], critic_hidden=[256, 128], wm_window=8,
    wm_batches=4, wm_batch=512, pi_batch=512, lr=.0001, gamma=.99, lam=.95,
    action_noise=.08, critic_epochs=2, critic_minibatches=2, no_critic=False,
    warmup_steps=64, wm_only_iters=100, lr_decay_iters=250000, ckpt_every=500,
    log_every=10, log_backend='none', amp='none', compile=False, test_hidden_dims=None)
FLOAT_WIDTHS = dict(s=73, s1=73, a=6, a_prev=6, xi=None, xi1=None, r=0)
BOOL_FIELDS = ('done', 'xi1_valid', 'term', 'trunc', 'split_known', 'stream_cut')
INTERPRETATION = dict(
    label='POSTHOC_REPLAY_RESUBSTITUTION_CONSISTENCY',
    replay_may_have_been_used_for_training=True, heldout=False,
    generalization_claim=False, actual_skill_pass_rate=None, causal_effect=None,
    relative_improvement=None, counterfactual_action_validation=False,
    bound_only_is_deployment_constraint_not_training_gain=True)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def identity(path, expected=None):
    path = Path(path).resolve(strict=True)
    need(path.suffix == '.py', 'reviewed source must be .py')
    raw = path.read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    need(expected is None or sha == expected, 'source SHA differs: ' + str(path))
    return dict(path=str(path), bytes=len(raw), SHA256=sha), raw.decode('utf-8-sig')


def same_json_type_value(actual, expected):
    if isinstance(expected, list):
        return type(actual) in (list, tuple) and len(actual) == len(expected) and all(
            same_json_type_value(a, b) for a, b in zip(actual, expected))
    return type(actual) is type(expected) and actual == expected


def strict_config(config, task):
    need(type(config) is dict and type(task.get('seed')) is int, 'config/TASK seed required')
    expected = dict(EXPECTED_CONFIG, seed=task['seed'])
    need(set(config) == set(expected), 'complete producer config key set differs')
    for key, value in expected.items():
        need(same_json_type_value(config[key], value), 'producer config differs: ' + key)
    return hashlib.sha256(canonical(config)).hexdigest()


def role_paths(role):
    own = OWN[role]
    job = ROOT + '/roles/' + role
    return job, job + '/production/FINAL.json', job + '/production/checkpoints/' + own['filename']


def validate_final(final, role):
    pin = OWN[role]
    _, _, path = role_paths(role)
    expected = dict(kind='MOD4V1_SUPERMIMIC_FULL_EXECUTION_FINAL_V3', run_id=RUN,
        role=role, role_key=pin['role_key'], actor_view='raw35_legacy_held_aux_v1',
        algorithm_family='a1_raw35_legacy_v1', algorithm_variant='A1_RAW35_FRESH',
        passed_execution=True, teacher_unchanged=True)
    for key, value in expected.items():
        need(same_json_type_value(final.get(key), value), 'actual FINAL differs: ' + key)
    checkpoint = final['checkpoint']
    for key, value in dict(path=path, bytes=pin['bytes'], SHA=pin['SHA'], iteration=pin['iteration']).items():
        need(same_json_type_value(checkpoint.get(key), value), 'allowlisted checkpoint differs: ' + key)
    need(checkpoint.get('full_new_model_critic_aux_optimizers_replay_RNG_hist_saved') is True
         and checkpoint.get('teacher_unchanged') is True, 'complete immutable own producer required')


def read_json_pin(path, size, sha):
    need(type(size) is int and 0 < size <= 16 * 1024 * 1024, 'bounded JSON bytes required')
    need(len(sha) == 64 and all(c in '0123456789abcdef' for c in sha), 'exact JSON SHA256 required')
    p = Path(path).resolve(strict=True)
    need(p.stat().st_size == size, 'JSON stat bytes differ: ' + str(p))
    raw = p.read_bytes()
    need(len(raw) == size and hashlib.sha256(raw).hexdigest() == sha, 'JSON bytes/SHA differ: ' + str(p))
    return json.loads(raw), dict(path=str(p), bytes=size, SHA256=sha)


def ring_row(T, ptr, size, age):
    need(type(T) is int and T > 0 and type(ptr) is int and 0 <= ptr < T
         and type(size) is int and 0 <= size <= T, 'invalid original ring metadata')
    need(type(age) is int and 0 <= age < size, 'chronological age outside original replay')
    return (ptr - size + age) % T


def edge_ok(meta, rows, left, env):
    """Whether physical/context/history continuity is known across this edge."""
    a, b = rows[left], rows[left + 1]
    return (not meta['done'][a][env] and not meta['stream_cut'][a][env]
        and meta['xi1_valid'][a][env]
        and meta['ep_step'][b][env] == meta['ep_step'][a][env] + 1
        and meta['f'][b][env] == meta['f'][a][env] + 1)


def history_ages(meta, rows, age, env, hist=10):
    step = meta['ep_step'][rows[age]][env]
    if type(step) is not int or step < 0:
        return None
    depth = min(step, hist - 1)
    start = age - depth
    if start < 0:  # oldest ring row is NOT an episode start unless ep_step==0
        return None
    if step < hist - 1 and meta['ep_step'][rows[start]][env] != 0:
        return None
    if not all(edge_ok(meta, rows, i, env) for i in range(start, age)):
        return None
    return [start] * (hist - 1 - depth) + list(range(start, age + 1))


def eligible_window(meta, rows, age, env, horizon):
    if horizon < 1 or age + horizon > len(rows):
        return False
    for i in range(age, age + horizon):
        row = rows[i]
        if meta['done'][row][env] or meta['stream_cut'][row][env] or not meta['xi1_valid'][row][env]:
            return False
        if i > age and not edge_ok(meta, rows, i - 1, env):
            return False
    return True


def pools(meta, rows, N, hist=10, horizon=16):
    one, actor, multi = [], [], []
    for age in range(len(rows)):
        for env in range(N):
            key = (age, env)
            one.append(key)  # terminal PRE-RESET s1/r/done are valid one-step labels
            if history_ages(meta, rows, age, env, hist) is not None:
                actor.append(key)
            if eligible_window(meta, rows, age, env, horizon):
                multi.append(key)
    return one, actor, multi


def legacy_mask(layout, C):
    need(type(layout) in (list, tuple) and layout, 'named original context layout missing')
    mask, offset, seen = [1.] * C, 0, set()
    for name, width in layout:
        need(type(name) is str and name not in seen and type(width) is int and width > 0,
             'context layout names/widths differ')
        seen.add(name)
        need(offset + width <= C, 'context layout overflows xi')
        if name.startswith(('mild_', 'PD_')) or name.endswith(('factor', 'delta_m', 'lag_steps')) or name.startswith(('feedback_delay', 'command_')):
            mask[offset:offset + width] = [0.] * width
        offset += width
    need(offset == C and list(layout[0]) == ['actor35_original', 35], 'context layout does not exactly bind xi prefix')
    mask[:4] = [0.] * 4
    mask[14:16] = [0.] * 2
    mask[22:35] = [0.] * 13
    return mask


def selected_classes(text, names, namespace, filename):
    tree = ast.parse(text, filename)
    nodes = [node for node in tree.body if isinstance(node, ast.ClassDef) and node.name in names]
    need([node.name for node in nodes] == list(names), 'selected real source classes missing/order differs')
    # No imports, module main, learner constructors, bridge/PinnedTeacher or fixture bottom.
    exec(compile(ast.Module(body=nodes, type_ignores=[]), filename + ':SELECTED_CLASSES_ONLY', 'exec'), namespace)


def import_source(text, name, filename):
    need(name not in sys.modules, 'unexpected diagnostic source module pre-import')
    module = importlib.util.module_from_spec(importlib.util.spec_from_loader(name, loader=None))
    module.__file__ = filename
    sys.modules[name] = module
    exec(compile(text, filename, 'exec'), module.__dict__)
    return module


def source_runtime(args):
    ids, texts = {}, {}
    for key, pin in SOURCE_PINS.items():
        ids[key], texts[key] = identity(getattr(args, key), pin)
    package = Path(args.vendor_parent).resolve(strict=True) / 'supermimic_vendor_v2'
    init_id, init_text = identity(package / '__init__.py')
    tree = ast.parse(init_text)
    need(not tree.body or (len(tree.body) == 1 and isinstance(tree.body[0], ast.Expr)
         and isinstance(tree.body[0].value, ast.Constant) and isinstance(tree.body[0].value.value, str)),
         'vendor init must remain docstring-only')
    ids['vendor_init'] = init_id
    for filename, pin in VENDOR_PINS.items():
        ids['vendor/' + filename], _ = identity(package / filename, pin)
    for path in reversed([package.parent, *[Path(p).resolve(strict=True) for p in args.dependency_path]]):
        sys.path.insert(0, str(path))
    t = importlib.import_module('torch')
    net = importlib.import_module('supermimic_vendor_v2.networks')
    geo = importlib.import_module('supermimic_vendor_v2.geometry')
    for name in ('contract', 'geometry', 'networks'):
        mod = importlib.import_module('supermimic_vendor_v2.' + name)
        need(Path(mod.__file__).resolve() == package / (name + '.py'), 'shadowed vendor source: ' + name)
    need(net.AMP_DTYPE is None, 'CPU diagnostic expects original AMP=None')
    TD = importlib.import_module('tensordict').TensorDict
    MLP = importlib.import_module('rsl_rl.models').MLPModel
    # Same real constructor/API as bridge:43-47 and frozen helper:200-207.
    mlp_id, _ = identity(inspect.getfile(MLP))
    mlp_id.update(module=MLP.__module__, qualname=MLP.__qualname__, hardcoded_source_pin=False)
    ids['actual_rsl_MLPModel'] = mlp_id
    helper = import_source(texts['cache_source'], '_replay_diagnostic_frozen_helper', ids['cache_source']['path'])
    ns = dict(__name__='_replay_diagnostic_selected_real_classes', torch=t, nn=t.nn,
        math=math, invariant_features=geo.invariant_features, unflatten_state=geo.unflatten_state,
        RunningNorm=net.RunningNorm, mlp=net.mlp, run_mlp=net.run_mlp)
    selected_classes(texts['bridge_source'], ('OriginalTaskMdp', 'TeacherResidualPolicy'), ns, ids['bridge_source']['path'])
    selected_classes(texts['core_source'], ('TaskAuxiliaryModel',), ns, ids['core_source']['path'])
    selected_classes(texts['raw35_source'], ('Raw35ActorMDP',), ns, ids['raw35_source']['path'])
    return SimpleNamespace(t=t, net=net, geo=geo, TD=TD, MLP=MLP, helper=helper,
        classes=ns, sources=ids, texts=texts)


def nested_digest(value, t):
    """Full values, including unused models/4 optimizers/RNG/replay, no root copy."""
    h = hashlib.sha256()
    def walk(v):
        if t.is_tensor(v):
            need(v.device.type == 'cpu' and v.layout == t.strided, 'whole root must remain dense CPU')
            h.update(str((tuple(v.shape), v.dtype)).encode())
            raw = v.detach().contiguous().reshape(-1).view(t.uint8)
            for start in range(0, raw.numel(), 262144):
                chunk = raw[start:start + 262144]
                try:
                    h.update(memoryview(chunk.numpy()))
                except (ImportError, RuntimeError):
                    h.update(bytes(chunk.tolist()))
        elif isinstance(v, Mapping):
            h.update(b'M' + str(len(v)).encode())
            for key, child in v.items():
                walk(key)
                walk(child)
        elif type(v) in (tuple, list):
            h.update(type(v).__name__.encode() + str(len(v)).encode())
            for child in v:
                walk(child)
        else:
            need(type(v) in (type(None), bool, int, float, str, bytes), 'unreviewed root scalar')
            b = v if type(v) is bytes else repr(v).encode()
            h.update(type(v).__name__.encode() + str(len(b)).encode() + b)
    walk(value)
    return h.hexdigest()


def strict_load(model, saved, t, label):
    current = model.state_dict()
    need(set(current) == set(saved), 'strict state keys differ: ' + label)
    for key, target in current.items():
        value = saved[key]
        need(t.is_tensor(value) and value.device.type == 'cpu' and value.shape == target.shape
             and value.dtype == target.dtype and bool(t.isfinite(value).all()), 'state shape/dtype/finite differs: ' + label + '/' + key)
        if key.endswith('.var') or key.endswith('.count'):
            need(bool((value >= 0).all()), 'negative saved norm variance/count: ' + key)
    model.load_state_dict(saved, strict=True, assign=False)
    for key, value in model.state_dict().items():
        need(t.equal(value, saved[key]), 'strict-loaded state value differs: ' + label + '/' + key)
    model.eval().requires_grad_(False)
    need(not any(p.grad is not None or p.requires_grad for p in model.parameters()), 'live diagnostic model trainable')
    return model


def build_models(rt, root):
    t, net, ns = rt.t, rt.net, rt.classes
    ext, cfg = root['context_reward_extension'], root['args']
    contract = ext['contract']
    C = contract['context_dim']
    with t.inference_mode(False), t.no_grad(), t.random.fork_rng(devices=[]):
        oldest = (ext['replay']['ptr'] - ext['replay']['size']) % ext['replay']['T']
        mdp = ns['Raw35ActorMDP'](ns['OriginalTaskMdp'](C, ext['replay']['data']['s'][oldest, :1]), transition_projector=None)
        wm = net.WorldModel(hidden=cfg['wm_hidden'], num_joints=30, context_dim=C, action_dim=6)
        aux = ns['TaskAuxiliaryModel'](30, 6, C, contract['aux_hidden'], .02)
        obs = rt.TD(dict(policy=t.zeros(2, 35), critic=t.zeros(2, 38)), batch_size=[2])
        distribution = dict(class_name='rsl_rl.modules.distribution:GaussianDistribution', init_std=1., std_type='scalar')
        teacher = rt.MLP(obs, dict(actor=['policy'], critic=['critic']), 'actor', 6, [256, 128, 64], 'elu', distribution_cfg=distribution)
        residual = net.Policy(35, 3, hist=10, z_dim=32, num_joints=6, hidden=cfg['policy_hidden'])
        pi = ns['TeacherResidualPolicy'](residual, teacher, 0, scale=.05)
        # Wrapper constructor zeros final residual: ALWAYS strict-load AFTER it.
        strict_load(wm, root['wm'], t, 'wm')
        strict_load(aux, ext['aux'], t, 'aux')
        strict_load(pi, root['pi'], t, 'pi_with_embedded_teacher')
    for module in (wm, aux, pi):
        need(all(p.device.type == 'cpu' for p in module.parameters()), 'live model left CPU')
        for norm in module.modules():
            if isinstance(norm, net.RunningNorm):
                need(norm.eps in (.01, .0001) and norm.max_count == 2e8, 'RunningNorm hyperparameters differ')
    return SimpleNamespace(wm=wm, aux=aux, pi=pi, mdp=mdp)


def validate_replay(root, t):
    ext = root['context_reward_extension']
    contract, replay = ext['contract'], ext['replay']
    T, N, ptr, size = (replay[k] for k in ('T', 'N', 'ptr', 'size'))
    need(type(N) is int and N == 1024 and T == 128 and size > 0, 'whole original N1024/T128 ring required')
    rows = [ring_row(T, ptr, size, age) for age in range(size)]
    C = contract['context_dim']
    data = replay['data']
    required = set(FLOAT_WIDTHS) | set(BOOL_FIELDS) | {'f', 'ep_step'}
    need(set(data) == required, 'exact extended original replay schema differs')
    for key, value in data.items():
        width = C if key in ('xi', 'xi1') else FLOAT_WIDTHS.get(key, 0)
        shape = (T, N, width) if width else (T, N)
        dtype = t.bool if key in BOOL_FIELDS else t.long if key == 'f' else t.int32 if key == 'ep_step' else t.float32
        need(t.is_tensor(value) and tuple(value.shape) == shape and value.dtype == dtype
             and value.device.type == 'cpu', 'original replay schema differs: ' + key)
    need(bool((data['ep_step'][rows] >= 0).all()) and t.equal(data['f'][rows], data['ep_step'][rows].long()), 'bridge frame/episode clock differs')
    known = data['split_known'][rows]
    need(bool(known.all()), 'original producer term/trunc split receipt missing')
    need(t.equal(data['done'][rows], data['term'][rows] | data['trunc'][rows]), 'original done != term|trunc')
    need(not bool((data['done'][rows] & data['xi1_valid'][rows]).any()), 'terminal xi1 must not be a valid observation')
    layout = ext['environment']['context_layout']
    expected_mask = legacy_mask(layout, C)
    need(same_json_type_value(contract.get('aux_hidden'), [256, 256]) and contract.get('aux_batch') == 512
         and contract.get('reward_source') == 'original_real_transition_r'
         and contract.get('termination_label') == 'original_done_term_OR_trunc', 'real auxiliary contract differs')
    need(same_json_type_value(contract['predict_context_mask'], expected_mask), 'contract legacy context mask differs')
    mask = ext['context_predict_mask']
    need(t.is_tensor(mask) and mask.dtype == t.float32 and tuple(mask.shape) == (C,)
         and t.equal(mask, t.tensor(expected_mask)), 'saved legacy context mask differs')
    meta = {key: data[key].tolist() for key in (*BOOL_FIELDS, 'ep_step', 'f')}
    return replay, rows, meta, layout, mask


def take(data, rows, keys, t, horizon=1):
    rr = t.tensor([[rows[age + k] for k in range(horizon)] for age, _ in keys], dtype=t.long)
    ee = t.tensor([env for _, env in keys], dtype=t.long)[:, None].expand_as(rr)
    return {key: value[rr, ee] for key, value in data.items()}


def check_selected_links(sample, t):
    if sample['s'].shape[1] < 2:
        return
    for left, right in (('s1', 's'), ('xi1', 'xi'), ('a', 'a_prev')):
        need(t.equal(sample[left][:, :-1], sample[right][:, 1:]), 'recorded window adjacency differs: ' + left + '->' + right)


def error_metrics(pred, target, t):
    need(pred.shape == target.shape and pred.numel() > 0, 'metric shape/empty differs')
    err = (pred - target).double().reshape(-1, pred.shape[-1])
    need(bool(t.isfinite(err).all()), 'nonfinite prediction/label: no silent sample filtering')
    return dict(samples=err.shape[0], components=err.shape[-1],
        MAE=float(err.abs().mean()), RMSE=float(err.square().mean().sqrt()),
        max_abs=float(err.abs().max()), per_component_MAE=err.abs().mean(0).tolist(),
        per_component_RMSE=err.square().mean(0).sqrt().tolist())


def state_metrics(pred, truth, rt, wm):
    t = rt.t
    err = wm.state_error(pred, truth)
    zero = t.zeros_like(err)
    slices = dict(root_position_m=(0, 3), rotation_vector_rad=(3, 6),
        linear_velocity_target_body_frame_m_s=(6, 9), angular_velocity_target_body_frame_rad_s=(9, 12),
        joint_position_rad=(12, 42), joint_velocity_rad_s=(42, 72))
    result = {name: error_metrics(err[..., a:b], zero[..., a:b], t) for name, (a, b) in slices.items()}
    result['gravity_body_unit_vector'] = error_metrics(-pred[1][..., 2, :], -truth[1][..., 2, :], t)
    result['saved_WM_output_std_scaled_mixed_units'] = error_metrics(err / wm.out_norm.std(), zero, t)
    result['state_error_layout'] = 'vendor WorldModel.state_error: 3pos+3so3log+3dv+3domega+30q+30dq; not quaternion RMSE'
    return result


def calibration(logit, label, t):
    need(bool(t.isfinite(logit).all()), 'nonfinite done logits')
    p, y = t.sigmoid(logit).double(), label.double()
    bins = []
    for index in range(10):
        mask = (p >= index / 10) & ((p < (index + 1) / 10) if index < 9 else (p <= 1))
        n = int(mask.sum())
        bins.append(dict(lo=index / 10, hi=(index + 1) / 10, n=n,
            mean_probability=float(p[mask].mean()) if n else None,
            observed_done_rate=float(y[mask].mean()) if n else None))
    ece = sum(b['n'] * abs(b['mean_probability'] - b['observed_done_rate']) for b in bins if b['n']) / p.numel()
    return dict(n=p.numel(), positive_labels=int(label.sum()), observed_rate=float(y.mean()),
        mean_probability=float(p.mean()), Brier=float((p - y).square().mean()),
        BCE=float(t.nn.functional.binary_cross_entropy_with_logits(logit.double(), y)), ECE10=ece, bins=bins,
        label='original done = term OR trunc; not physical-term-only; natural unweighted calibration')


def context_metrics(pred, label, t):
    return dict(full_context=error_metrics(pred, label, t), raw35=error_metrics(pred[..., :35], label[..., :35], t),
        raw35_sensor_slots4_14_and16_22=error_metrics(t.cat((pred[..., 4:14], pred[..., 16:22]), -1),
            t.cat((label[..., 4:14], label[..., 16:22]), -1), t),
        original_sensor_units='0.5*omega3, gravity3, legpos4, 0.1*legvel4, 0.1*wheelvel2; observed noisy/delayed units',
        clean_state_sensor_reconstruction_used=False)


def auxiliary_metrics(s, state, state1, context, previous_action, frames, models, rt):
    t, aux, mdp = rt.t, models.aux, models.mdp
    features = aux.features(state, state1, s['a'], previous_action, mdp.normalize_context(context), frames)
    reward, delta, logit = aux(features)
    reward_error = error_metrics(reward[..., None], s['r'][..., None], t)
    std = float(s['r'].double().std(unbiased=False))
    saved_std = float(aux.reward_norm.std()[0])
    reward_error.update(actual_reward_mean=float(s['r'].double().mean()), actual_reward_std=std,
        actual_reward_mean_abs=float(s['r'].double().abs().mean()), saved_reward_norm_std=saved_std,
        MAE_over_sample_reward_std=reward_error['MAE'] / std if std > 1e-12 else None,
        MAE_over_saved_reward_norm_std=reward_error['MAE'] / saved_std)
    out = dict(reward=reward_error, done=calibration(logit, s['done'], t))
    next_context = mdp.project_predicted_context(context + models.mask * delta, state1, s['a'], frames + 1)
    valid = ~s['done'] & ~s['stream_cut'] & s['xi1_valid']
    out['context_labels'] = dict(valid=int(valid.sum()), excluded=int((~valid).sum()),
        rule='~done & ~stream_cut & xi1_valid; actual xi1 only; never postreset/zero terminal targets')
    if bool(valid.any()):
        out['raw_aux_delta_unmasked'] = error_metrics(delta[valid], (s['xi1'] - s['xi'])[valid], t)
        out['raw_aux_delta_target'] = 'recorded xi1 - recorded xi, including FULL-mode diagnostics; not xi1 minus predicted context'
        out['effective_legacy_projected_next_context'] = context_metrics(next_context[valid], s['xi1'][valid], t)
    else:
        out['raw_aux_delta_unmasked'] = None
        out['effective_legacy_projected_next_context'] = None
    return out, next_context, reward


def component_stats(value, t):
    value = value.double()
    need(bool(t.isfinite(value).all()), 'nonfinite actor result')
    return dict(mean=value.mean(0).tolist(), mean_abs=value.abs().mean(0).tolist(),
        RMS=value.square().mean(0).sqrt().tolist(), max_abs=value.abs().amax(0).tolist(),
        p95_abs=t.quantile(value.abs(), .95, dim=0).tolist())


def actor_metrics(history, models, rt):
    t, pi = rt.t, models.pi
    need(tuple(history.shape[1:]) == (10, 35), 'raw35 history10 only')
    goal = history[:, -1, :3]
    base = pi.teacher(rt.TD(dict(policy=history[:, -1]), batch_size=[len(history)]), stochastic_output=False)
    delta = .05 * pi.residual(history, goal)
    preclip = base + delta
    action = pi(history, goal)
    need(t.equal(action, preclip.clamp(-6., 6.)), 'actual wrapper/formula differs')
    teacher = base.clamp(-6., 6.)
    return dict(n=len(history), residual_preclip_scaled=component_stats(delta, t),
        actor_minus_clipped_teacher=component_stats(action - teacher, t),
        teacher_unclipped=component_stats(base, t),
        clip_saturation_per_component=(action.abs() >= 6.).double().mean(0).tolist(),
        preclip_outside_per_component=(preclip.abs() > 6.).double().mean(0).tolist(),
        teacher_clip_saturation_per_component=(teacher.abs() >= 6.).double().mean(0).tolist(),
        note='current saved deterministic mean on recorded histories; recorded behavior may have exploration/older weights; not a counterfactual future test',
        actor_inputs='ONLY original noisy/delayed xi[:35] history10 and its known command[:3]',
        teacher_source='embedded pi.teacher.*; mother checkpoint opens=0', residual_scale=.05, hard_action_clip=6.)


def observed_groups(xi, layout):
    # Group only actual observed values; never assign standing/recovery phase/UID labels.
    candidates = [('raw35_mode28_35_exact_vector', 28, 35)]
    offset = 0
    for name, width in layout:
        if name in ('command_mode', 'command_key', 'recovery_recipe', 'recovery_request') and width == 1:
            candidates.append((name, offset, offset + width))
        offset += width
    out = {}
    for name, start, end in candidates:
        values = [tuple(row) for row in xi[:, start:end].tolist()]
        unique = sorted(set(values))
        if len(unique) <= 8:
            out[name] = [(list(v), [i for i, got in enumerate(values) if got == v]) for v in unique]
    return out


def run_diagnostics(models, rt, replay, rows, meta, layout, args):
    t, data = rt.t, replay['data']
    one_pool, actor_pool, h16_pool = pools(meta, rows, replay['N'])
    g = t.Generator(device='cpu')
    g.manual_seed(args.sample_seed)  # private generator; NEVER global manual_seed
    def select(pool, maximum):
        if not pool:
            return []
        return [pool[i] for i in t.randperm(len(pool), generator=g)[:maximum].tolist()]
    keys1, keys_actor, keys16 = select(one_pool, args.batch), select(actor_pool, args.batch), select(h16_pool, args.windows)
    out = dict(interpretation=INTERPRETATION,
        sampling=dict(seed=args.sample_seed, generator='private torch.Generator(cpu)', replacement=False,
            populations=dict(one_step=len(one_pool), legal_actor_history=len(actor_pool), legal_H16=len(h16_pool)),
            selected=dict(one_step=keys1, actor=keys_actor, H16=keys16),
            exclusions=dict(actor_unknown_or_discontinuous_history=len(one_pool)-len(actor_pool), H16_unavailable_or_boundary=len(one_pool)-len(h16_pool)),
            original_ring=dict(T=replay['T'], N=replay['N'], ptr=replay['ptr'], size=replay['size'], chronological_rows=rows),
            H16_condition='all16 ~done & ~stream_cut & xi1_valid; complete within saved ring; survivor-window bias, not all-transition calibration'),
        source_semantics=dict(history_padding='repeat visible true ep_step0 observation ONLY; unknown oldest history skipped, never zeros',
            f='bridge ep_step precontrol; f_next=f+1; aux seconds=f*.02; not held',
            legacy_project='OriginalTaskMdp.project_predicted_context clones input, zeros14:16, writes22:28=recorded action; all other slots untouched by projector',
            context_mask='raw35[:4],14:16,22:35 held before projector; mild_/PD_, *factor/*delta_m/*lag_steps, feedback_delay*, command_* held; others use saved mask*aux delta',
            recovery='bridge recovery age/stable stored*.01; recipe/request/credited unscaled; none universally held by legacy mask. Actual named layout and saved mask emitted below',
            raw35='Raw35ActorMDP.obs returns xi[:35] identity; add_noise identity; goal xi[:3]. No clean-state substitution, UID or phase injection'),
        context_layout=layout, context_predict_mask=models.mask.tolist())
    sample = {k: v[:, 0] for k, v in take(data, rows, keys1, t).items()}
    for key in FLOAT_WIDTHS:
        need(bool(t.isfinite(sample[key]).all()), 'nonfinite real one-step label: ' + key)
    clock_audit = dict(f_precontrol=sample['f'].tolist(), ep_step_precontrol=sample['ep_step'].tolist(),
                       source_context_values={})
    offset = 0
    for name, width in layout:
        if name.startswith('recovery_') or name in ('command_age', 'command_time_left', 'command_mode', 'command_key'):
            clock_audit['source_context_values'][name] = dict(offset=offset, width=width,
                saved_predict_mask=models.mask[offset:offset + width].tolist(),
                observed_values=sample['xi'][:, offset:offset + width].tolist())
        offset += width
    out['sampled_clock_and_present_recovery_fields_ONLY'] = clock_audit
    s, s1 = rt.geo.unflatten_state(sample['s']), rt.geo.unflatten_state(sample['s1'])
    pred = models.wm.step(s, sample['a'], models.mdp.normalize_context(sample['xi']))
    aux_true, _, _ = auxiliary_metrics(sample, s, s1, sample['xi'], sample['a_prev'], sample['f'], models, rt)
    aux_pred, _, _ = auxiliary_metrics(sample, s, pred, sample['xi'], sample['a_prev'], sample['f'], models, rt)
    out['one_step'] = dict(n=len(keys1), state=state_metrics(pred, s1, rt, models.wm),
        aux_on_true_s_and_true_s1=aux_true, aux_on_true_s_and_WM_s1=aux_pred,
        real_terminal_count=int(sample['done'].sum()), real_term_count=int(sample['term'].sum()), real_trunc_count=int(sample['trunc'].sum()),
        terminal_state_rule='pre-reset physical s1 and original r/done INCLUDED; terminal/context-invalid xi1 EXCLUDED')
    out['one_step_observed_groups'] = {}
    for name, parts in observed_groups(sample['xi'], layout).items():
        out['one_step_observed_groups'][name] = []
        for value, indices in parts:
            ix = t.tensor(indices)
            sub = {k: v[ix] for k, v in sample.items()}
            ss, tt = tuple(x[ix] for x in s), tuple(x[ix] for x in s1)
            pp = tuple(x[ix] for x in pred)
            aa, _, _ = auxiliary_metrics(sub, ss, pp, sub['xi'], sub['a_prev'], sub['f'], models, rt)
            out['one_step_observed_groups'][name].append(dict(observed_value=value, n=len(indices),
                state=state_metrics(pp, tt, rt, models.wm), aux_on_WM_s1=aa))
    if keys_actor:
        hh = t.tensor([[rows[i] for i in history_ages(meta, rows, age, env)] for age, env in keys_actor])
        ee = t.tensor([env for _, env in keys_actor])[:, None].expand_as(hh)
        hist = data['xi'][hh, ee, :35]
        # Check actual array adjacency for nonpadding edges, not counters alone.
        for age, env in keys_actor:
            ages = list(dict.fromkeys(history_ages(meta, rows, age, env)))
            if len(ages) > 1:
                check_selected_links(take(data, rows, [(ages[0], env)], t, len(ages)), t)
        out['actor'] = actor_metrics(hist, models, rt)
        ax = hist[:, -1]
        out['actor_observed_raw35_mode_groups'] = [dict(observed_value=v, **actor_metrics(hist[t.tensor(ix)], models, rt))
            for v, ix in observed_groups(ax, [('actor35_original', 35)]).get('raw35_mode28_35_exact_vector', [])]
    else:
        out['actor'] = dict(status='MISSING_LEGAL_KNOWN_HISTORY', n=0)
    out['H16'] = {}
    if not keys16:
        out['H16']['status'] = 'NO_LEGAL_COMPLETE_16_STEP_WINDOWS; NOT_A_PASS'
        return out
    multi = take(data, rows, keys16, t, 16)
    check_selected_links(multi, t)
    modes = ['CONDITIONAL_STATE_OPENLOOP']
    if args.full_context_openloop:
        modes.append('FULL_STATE_AND_CONTEXT_OPENLOOP_ALONG_RECORDED_ACTIONS')
    for mode in modes:
        state = rt.geo.unflatten_state(multi['s'][:, 0])
        context = multi['xi'][:, 0].clone()
        previous = multi['a_prev'][:, 0]
        frames = multi['f'][:, 0].clone()
        steps, predicted_rewards = [], []
        for k in range(16):
            step = {name: v[:, k] for name, v in multi.items()}
            for name in FLOAT_WIDTHS:
                need(bool(t.isfinite(step[name]).all()), 'nonfinite H16 real label: ' + name)
            if mode == 'CONDITIONAL_STATE_OPENLOOP':
                context, previous, frames = step['xi'], step['a_prev'], step['f']
            next_state = models.wm.step(state, step['a'], models.mdp.normalize_context(context))
            am, next_context, reward = auxiliary_metrics(step, state, next_state, context, previous, frames, models, rt)
            steps.append(dict(h=k + 1, state=state_metrics(next_state, rt.geo.unflatten_state(step['s1']), rt, models.wm), aux=am))
            predicted_rewards.append(reward)
            state, context, previous, frames = next_state, next_context, step['a'], frames + 1
        out['H16'][mode] = dict(n=len(keys16), horizon=16, steps=steps,
            cumulative_original_reward=error_metrics(t.stack(predicted_rewards, 1).sum(1, keepdim=True), multi['r'].sum(1, keepdim=True), t),
            state_reanchored_after_start=False, actions='only recorded applied actions; no actor counterfactuals',
            context_reanchored_after_start=mode == 'CONDITIONAL_STATE_OPENLOOP',
            oracle_context_used_after_start=mode == 'CONDITIONAL_STATE_OPENLOOP',
            ground_truth_use='real future s1/xi1/r/done used ONLY as labels in FULL mode',
            actual_policy_imagination_full_chain=False, learned_done_gating_used=False,
            diagnostic_execution_only_NOT_quality_pass=True)
    return out


def stat_tuple(path):
    s = Path(path).stat()
    return (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns)


def run(args):
    need(1 <= args.batch <= 64 and 1 <= args.windows <= 32, 'bounded CPU batch<=64/windows<=32 required')
    job, final_path, checkpoint_path = role_paths(args.role)
    need(str(Path(args.final).resolve()) == final_path, 'exact original actual FINAL path required; no copy/fallback')
    task_path = job + '/TASK.json'
    final, final_id = read_json_pin(args.final, args.final_bytes, args.final_sha)
    task, task_id = read_json_pin(task_path, args.task_bytes, args.task_sha)
    need(task_id['path'] == task_path, 'exact original TASK resolved path differs')
    validate_final(final, args.role)
    for k, v in dict(role=args.role, role_key=OWN[args.role]['role_key'], run_id=RUN, num_envs=1024,
                     asset_SHA=ASSET, contract_SHA=CONTRACT).items():
        need(same_json_type_value(task.get(k), v), 'original TASK differs: ' + k)
    python_rng = random.getstate()
    rt = source_runtime(args)
    t, helper = rt.t, rt.helper
    torch_rng = t.get_rng_state().clone()
    np = sys.modules.get('numpy')
    numpy_rng = repr(np.random.get_state()) if np is not None else None
    need(not t.cuda.is_initialized(), 'diagnostic expects CPU-only fresh process')
    original_threads = t.get_num_threads()
    t.set_num_threads(args.cpu_threads)
    path = Path(checkpoint_path).resolve(strict=True)
    need(str(path) == checkpoint_path, 'allowlisted checkpoint resolved path differs')
    before_stat = stat_tuple(path)
    raw = path.read_bytes()  # Exactly ONE own physical checkpoint read.
    pin = OWN[args.role]
    need(len(raw) == pin['bytes'], 'own checkpoint byte length differs')
    raw_sha = hashlib.sha256(raw).hexdigest()  # Exactly ONE checkpoint SHA.
    need(raw_sha == pin['SHA'], 'own checkpoint SHA differs')
    with t.inference_mode(False):
        root = t.load(io.BytesIO(raw), map_location='cpu', weights_only=True)  # Exactly ONE CPU decode.
    guard = helper._snapshot(root, t, require_cpu=True)
    digest_before = nested_digest(root, t)
    expected = dict(role=args.role, role_key=pin['role_key'], run_id=RUN, asset_SHA=ASSET, contract_SHA=CONTRACT)
    helper._validate_payload(root, final, expected, t)
    need(root.get('original_task_protocol') == task.get('original_protocol')
         and type(task.get('original_protocol')) is dict, 'original TASK/payload protocol differs')
    config_sha = strict_config(root['args'], task)
    replay, rows, meta, layout, mask = validate_replay(root, t)
    models = build_models(rt, root)
    models.mask = mask.detach().clone()
    live = {name: getattr(models, name).state_dict(keep_vars=True) for name in ('wm', 'aux', 'pi')}
    live_guard = helper._snapshot(live, t, require_cpu=True)
    live_before = nested_digest(live, t)
    failure = None
    try:
        with t.no_grad():
            result = run_diagnostics(models, rt, replay, rows, meta, layout, args)
    except Exception as error:
        failure = error
        result = {}
    finally:
        helper._same(root, guard, t, require_cpu=True)
        need(nested_digest(root, t) == digest_before, 'WHOLE cached root VALUES changed')
        helper._same(live, live_guard, t, require_cpu=True)
        need(nested_digest(live, t) == live_before, 'frozen live model VALUES changed')
        need(all(not m.training for model in (models.wm, models.aux, models.pi) for m in model.modules()), 'model training mode changed')
        need(all(not p.requires_grad and p.grad is None for model in (models.wm, models.aux, models.pi) for p in model.parameters()), 'frozen parameters/grad changed')
        need(stat_tuple(path) == before_stat, 'original checkpoint stat changed during diagnostic')
        need(t.equal(torch_rng, t.get_rng_state()) and random.getstate() == python_rng, 'global Torch/Python RNG changed')
        need(np is None or repr(np.random.get_state()) == numpy_rng, 'global NumPy RNG changed')
        need(not t.cuda.is_initialized(), 'CUDA unexpectedly initialized')
        t.set_num_threads(original_threads)
    if failure is not None:
        raise failure
    result.update(kind='SOURCE_REPLAY_CONSISTENCY_DIAGNOSTIC_V1', role=args.role,
        provenance=dict(actual_FINAL=final_id, original_TASK=task_id, run_id=RUN, role_key=pin['role_key'],
            checkpoint_path=checkpoint_path, checkpoint_bytes=len(raw), checkpoint_SHA256=raw_sha,
            complete_config=root['args'], config_canonical_SHA256=config_sha, contract=root['context_reward_extension']['contract']),
        execution=dict(torch_version=str(t.__version__), python_version=sys.version,
            sources=rt.sources, entrypoint=identity(__file__)[0], cpu_threads=args.cpu_threads,
            physical_checkpoint_reads=1, checkpoint_SHA_calculations=1, weights_only_CPU_decodes=1,
            mother_checkpoint_reads=0, optimizer_instances=0, optimizer_updates=0, norm_updates=0,
            environment_or_SDK_created=False, training=False, native_BPTT_updates_this_diagnostic=0,
            saved_producer_counts_ARE_NOT_skill_evidence=True, whole_root_value_SHA256_before_after=digest_before,
            whole_root_tensor_identity_version_values_unchanged=True, live_models_frozen_unchanged=True,
            retained_source_bytes='immutable Python bytes; never reserialized or written; SHA computed once',
            disk_integrity_check='read-only open plus before/after stat(device,inode,size,mtime_ns,ctime_ns); no second disk-byte hash',
            saved_optimizer_RNG_env_history_restored=False, source_N1024_never_sliced_to_N80_resume=True,
            global_Torch_Python_NumPy_RNG_unchanged=True, CUDA_initialized=False,
            Torch_runtime_validation='RUN_BY_PARENT_CPU_ONLY; local stdlib tests do not establish Torch PASS'))
    return result


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--role', required=True, choices=tuple(OWN))
    p.add_argument('--final', required=True)
    p.add_argument('--final-bytes', type=int, required=True)
    p.add_argument('--final-sha', required=True)
    p.add_argument('--task-bytes', type=int, required=True)
    p.add_argument('--task-sha', required=True)
    for name in SOURCE_PINS:
        p.add_argument('--' + name.replace('_', '-'), type=Path, required=True)
    p.add_argument('--vendor-parent', type=Path, required=True)
    p.add_argument('--dependency-path', type=Path, action='append', default=[])
    p.add_argument('--batch', type=int, default=64)
    p.add_argument('--windows', type=int, default=32)
    p.add_argument('--sample-seed', type=int, default=20261103)
    p.add_argument('--cpu-threads', type=int, choices=range(1, 5), default=1)
    p.add_argument('--full-context-openloop', action='store_true')
    p.add_argument('--output', type=Path, required=True, help='new JSON file outside original job root')
    return p


def main():
    args = parser().parse_args()
    # Set visibility before lazy Torch import; no hardware/SDK query.
    os.environ['CUDA_VISIBLE_DEVICES'] = ''
    output = args.output.resolve()
    need(not output.exists() and not output.is_relative_to(Path(ROOT).resolve()), 'new output outside original producer root required')
    need(output.parent.is_dir(), 'create a separate own diagnostic output directory first')
    result = run(args)
    with output.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(result, stream, indent=2, ensure_ascii=False, allow_nan=False)
        stream.write('\n')
    print(json.dumps(dict(output=str(output), role=args.role, kind=result['kind'],
        native_BPTT_updates_this_diagnostic=0, skill_pass_rate=None, causal_effect=None), allow_nan=False))


if __name__ == '__main__':
    main()
