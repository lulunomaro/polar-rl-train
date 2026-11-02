"""SYNTHETIC CPU Torch software validation; never native MOD4/physics training.

Inputs are explicit SHA-pinned source bytes and existing dependency directories.
Only FakeTeacher/Synthetic fixture classes are AST-executed; fixture bottom,
PinnedTeacher, NativeTaskBridge, worker, SDK and original model PTs are excluded.
Own newly generated synthetic full-checkpoint files are permitted output only.
The parent executes this script on existing CPU Torch; local authoring is AST-only.
"""
import os
os.environ['CUDA_VISIBLE_DEVICES'] = ''
import argparse
import ast
import copy
from dataclasses import dataclass
import hashlib
import importlib.util
import io
import json
from collections.abc import Mapping
from pathlib import Path
import random
import sys
import time
import traceback
import types

PINS = {
    'fixture': '4de256764f7fec0dac6fbb624a7a4189d7a686dc9d28bd5570a9a43f8afce10d',
    'bridge_source': '8211964c2ce3dd78fdb9fee6603ee4a4dcfbca6fa9d7df44f20d3ddb7aaead29',
    'payload_core': '8116ea358dfe32e0efd568d00661ab1e13b602d267ea4b580ced04ec39e898ac',
    'resume_contracts': 'dc4bc67193457a4fb72b125d23fa482cd3d686363bd1a93eb07268f4e4e26cb7',
    'raw35_source': 'bb7555ff2de598677ea6cfe5dadefe0a9cfe37d37661635d186bcb14c1df2223',
}


def source_identity(path):
    raw = Path(path).read_bytes()
    return dict(path=str(Path(path).resolve()), bytes=len(raw), SHA256=hashlib.sha256(raw).hexdigest())


def import_exact(path, name):
    if name in sys.modules:
        raise AssertionError('explicit source module was already imported: ' + name)
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    assert Path(module.__file__).resolve() == Path(path).resolve()
    return module


def ast_classes(path, names, namespace):
    source = ast.parse(Path(path).read_text(encoding='utf-8'))
    selected = [n for n in source.body if isinstance(n, ast.ClassDef) and n.name in names]
    assert {n.name for n in selected} == set(names), (path, names)
    module = ast.Module(body=selected, type_ignores=[])
    exec(compile(ast.fix_missing_locations(module), str(path) + ':ONLY_NAMED_CLASSES', 'exec'), namespace)
    return {name: namespace[name] for name in names}


def assert_nested_equal(a, b, torch, label='state'):
    if torch.is_tensor(a) or torch.is_tensor(b):
        assert torch.is_tensor(a) and torch.is_tensor(b), label
        assert a.shape == b.shape and a.dtype == b.dtype and torch.equal(a.cpu(), b.cpu()), label
    elif isinstance(a, Mapping) or isinstance(b, Mapping):
        assert isinstance(a, Mapping) and isinstance(b, Mapping) and a.keys() == b.keys(), label
        for key in a: assert_nested_equal(a[key], b[key], torch, label + '/' + str(key))
    elif isinstance(a, (tuple, list)) or isinstance(b, (tuple, list)):
        assert type(a) is type(b) and len(a) == len(b), label
        for index, (left, right) in enumerate(zip(a, b)):
            assert_nested_equal(left, right, torch, label + '/' + str(index))
    else:
        assert a == b, (label, a, b)


def digest_nested(value, torch):
    """Deterministic value digest, not a nondeterministic pickle-byte comparison."""
    digest = hashlib.sha256()
    def visit(item):
        if torch.is_tensor(item):
            tensor = item.detach().cpu().contiguous()
            digest.update(str((str(tensor.dtype), tuple(tensor.shape))).encode())
            digest.update(bytes(tensor.reshape(-1).view(torch.uint8).tolist()))
        elif isinstance(item, Mapping):
            for key in sorted(item, key=repr):
                digest.update(repr(key).encode());visit(item[key])
        elif isinstance(item, (tuple, list)):
            digest.update(type(item).__name__.encode())
            for child in item: visit(child)
        else:
            digest.update(repr(item).encode())
    visit(value)
    return digest.hexdigest()


def expect_error(function, expected, label):
    try:
        function()
    except expected as exc:
        return dict(label=label, blocked=True, error_type=type(exc).__name__, message=str(exc))
    raise AssertionError('negative case unexpectedly passed: ' + label)


def run(args, output):
    identities = {}
    for key, expected in PINS.items():
        path = getattr(args, key).resolve(strict=True)
        setattr(args, key, path)
        identities[key] = source_identity(path)
        assert identities[key]['SHA256'] == expected, (key, identities[key])
    vendor_parent = args.vendor_parent.resolve(strict=True)
    assert (vendor_parent / 'supermimic_vendor_v2' / 'learner.py').is_file()
    dependencies = [path.resolve(strict=True) for path in args.dependency_path]
    for path in reversed([vendor_parent, *dependencies]): sys.path.insert(0, str(path))
    import torch
    torch.set_num_threads(1)
    torch.set_default_dtype(torch.float32)
    torch.manual_seed(37);random.seed(37)
    assert not torch.cuda.is_initialized()
    # Existing optional numpy is included by the real core RNG capture if loaded.
    try:
        import numpy as np
    except ImportError:
        np = None
    if np is not None: np.random.seed(37)
    from supermimic_vendor_v2.geometry import invariant_features, unflatten_state
    from supermimic_vendor_v2.contract import SUPERMIMIC_STATE_KEY, SUPERMIMIC_TRANSITION_KEY
    from supermimic_vendor_v2.learner import SuperMimicConfig
    actual_vendor = Path(sys.modules['supermimic_vendor_v2.learner'].__file__).resolve()
    assert actual_vendor == vendor_parent / 'supermimic_vendor_v2' / 'learner.py'
    core = import_exact(args.payload_core, '_resume_validation_actual_payload_core_v1')
    contracts = import_exact(args.resume_contracts, '_resume_validation_actual_contracts_v3')
    raw35 = import_exact(args.raw35_source, '_resume_validation_actual_raw35_v1')
    namespace = types.ModuleType('_resume_validation_selected_ast_classes_v1')
    sys.modules[namespace.__name__] = namespace
    namespace.__dict__.update(torch=torch, dataclass=dataclass,
        invariant_features=invariant_features, unflatten_state=unflatten_state,
        SUPERMIMIC_STATE_KEY=SUPERMIMIC_STATE_KEY, SUPERMIMIC_TRANSITION_KEY=SUPERMIMIC_TRANSITION_KEY)
    ast_classes(args.bridge_source, ('BridgeState', 'OriginalTaskMdp'), namespace.__dict__)
    # The exact original policy class is selected separately, never reimplemented.
    ast_classes(args.bridge_source, ('TeacherResidualPolicy',), namespace.__dict__)
    ast_classes(args.fixture, ('FakeTeacher', 'Synthetic'), namespace.__dict__)
    OriginalTaskMdp = namespace.OriginalTaskMdp
    TeacherResidualPolicy = namespace.TeacherResidualPolicy
    FakeTeacher, Synthetic = namespace.FakeTeacher, namespace.Synthetic
    CONTEXT_DIM = 40
    layout = [('SYNTHETIC_actor_obs35', 35), ('SYNTHETIC_model_only_suffix', 5)]
    seed_teacher = FakeTeacher()
    seed_teacher.register_buffer('synthetic_frozen_buffer', torch.tensor([.2, -.4, .6]))
    teacher_source_root = copy.deepcopy(seed_teacher.state_dict())
    teacher_stream = io.BytesIO()
    torch.save(dict(SYNTHETIC_ONLY=True, actor_state_dict=teacher_source_root), teacher_stream)
    teacher_bytes = teacher_stream.getvalue()  # No teacher file exists or is read.
    teacher_identity = dict(source_path=str(output / 'SYNTHETIC_TEACHER_IDENTITY_NO_FILE'),
        source_SHA=hashlib.sha256(teacher_bytes).hexdigest(), source_bytes=len(teacher_bytes),
        synthetic_BytesIO_identity_only=True, original_teacher_PT_reads=0)
    teacher_source_versions = {key: value._version for key, value in teacher_source_root.items()}
    source_root_digest = digest_nested(teacher_source_root, torch)

    class LegacySynthetic(Synthetic):
        """Original toy fixture, no sensor oracle, no real timing/noise proof."""
        def __init__(self, view):
            super().__init__()
            suffix = torch.arange(5, dtype=torch.float32).expand(8, -1) * .01
            self.xi = torch.cat((self.xi, suffix), -1)
            base = OriginalTaskMdp(CONTEXT_DIM, self.s)
            self.mdp = raw35.Raw35ActorMDP(base, transition_projector=None) if view == contracts.RAW35_ACTOR_VIEW else base
            self.synthetic_view = view
            self.fresh_initializations = 0
        def init_state(self):
            self.fresh_initializations += 1
            assert self.fresh_initializations == 1, 'one fresh synthetic environment initialization only'
            return super().init_state()
        def export_supermimic_resume(self):
            return dict(exact=False, context_layout=layout,
                kind='SYNTHETIC_ENVIRONMENT_EXPORT_NOT_PHYSX', physical_restore_claim=False)

    config = SuperMimicConfig(iterations=100, buffer_steps=16, utd=1., horizon=16,
        goal_frames=1, hist=10, z_dim=4, wm_hidden=(16,), policy_hidden=(16,), critic_hidden=(16,),
        wm_window=2, wm_batches=1, wm_batch=8, pi_batch=8, lr=.001, warmup_steps=8,
        wm_only_iters=2, critic_epochs=1, critic_minibatches=1, ckpt_every=10000,
        log_every=10000, log_backend='none', amp='none', compile=False, seed=37)
    mask = torch.ones(CONTEXT_DIM)
    mask[:4] = 0;mask[14:16] = 0;mask[22:] = 0
    generated_checkpoints = []

    def teacher_snapshot(model): return {key: value.detach().clone() for key, value in model.state_dict().items()}
    def assert_teacher(model, snapshot):
        current = model.state_dict()
        assert current.keys() == snapshot.keys()
        for key, value in snapshot.items():
            assert torch.equal(current[key], value), 'actual frozen teacher state changed: ' + key
        assert model.training is False
        assert all(not parameter.requires_grad and parameter.grad is None for parameter in model.parameters())
    def make_learner(view, directory):
        env = LegacySynthetic(view)
        teacher = FakeTeacher()
        teacher.register_buffer('synthetic_frozen_buffer', torch.zeros(3))
        teacher.load_state_dict(teacher_source_root, strict=True)
        teacher.eval().requires_grad_(False)
        snapshot = teacher_snapshot(teacher)
        class Learner(core.ContextRewardLearner):
            def _make_policy(self):
                offset = 0 if view == contracts.RAW35_ACTOR_VIEW else env.mdp.actor_context_offset
                return TeacherResidualPolicy(super()._make_policy(), teacher, offset, scale=.05)
        learner = Learner(env, config, directory, device='cpu', aux_hidden=(16,),
                          aux_batch=8, predict_context_mask=mask)
        assert vars(learner.counts) == dict.fromkeys(contracts.COUNT_FIELDS, 0)
        assert all(not optimizer.state for optimizer in (learner.opt_wm, learner.opt_pi, learner.opt_v, learner.opt_aux))
        assert learner.obs_hist.shape == (8, 10, 35 if view == contracts.RAW35_ACTOR_VIEW else 119)
        assert learner.pi.scale == .05 and type(learner.pi) is TeacherResidualPolicy
        assert_teacher(teacher, snapshot)
        teacher_ids = {id(p) for p in teacher.parameters()}
        assert not teacher_ids.intersection(id(p) for group in learner.opt_pi.param_groups for p in group['params'])
        if view == contracts.RAW35_ACTOR_VIEW:
            assert learner.mdp.transition_projector is None
            assert learner.mdp.tracking_component is None
            assert learner.mdp.project_predicted_context.__self__ is learner.mdp.base_mdp
            raw = learner.mdp.obs(unflatten_state(env.s), env.a, env.xi, env.f)
            altered = env.xi.clone();altered[:, 35:] += 123.
            assert torch.equal(raw, env.xi[:, :35])
            assert torch.equal(raw, learner.mdp.obs(unflatten_state(env.s + .1), env.a + 1., altered, env.f + 5))
            assert torch.equal(learner.mdp.goal_with_context(env.f, 1, altered), env.xi[:, :3])
        assert all(value.device.type == 'cpu' for model in (learner.wm, learner.pi, learner.critic, learner.aux)
                   for value in model.state_dict().values())
        assert not torch.cuda.is_initialized()
        return learner, env, teacher, snapshot

    def gradient_receipt(learner):
        receipt = copy.deepcopy(learner.last_bptt_receipt)
        assert receipt['verified_bptt_optimizer_step'] is True, receipt
        for finite, norm in [('cross_time_finite', 'cross_time_grad_norm'), ('wm_path_finite', 'wm_path_grad_norm')]:
            assert receipt[finite] and receipt[norm] > 0, receipt
        assert receipt['parameter_grad_norm'] > 0 and receipt['probe_parameter_delta_l2'] > 0, receipt
        return receipt

    def full_states(learner):
        return dict(models={name: copy.deepcopy(getattr(learner, name).state_dict()) for name in ('wm', 'pi', 'critic', 'aux')},
                    optimizers={name: copy.deepcopy(getattr(learner, name).state_dict()) for name in ('opt_wm', 'opt_pi', 'opt_v', 'opt_aux')})

    def base_task(name, view):
        task = dict(role='SYNTHETIC_ONLY_' + name, role_key='SYNTHETIC_ONLY_' + name,
            run_id='SYNTHETIC_CPU_' + name, num_envs=8, actor_view=view,
            algorithm_variant=name + '_FRESH', teacher_path=teacher_identity['source_path'],
            teacher_SHA=teacher_identity['source_SHA'], teacher_bytes=teacher_identity['source_bytes'],
            asset_SHA=hashlib.sha256(('SYNTHETIC_ASSET_' + name).encode()).hexdigest(),
            contract_SHA=hashlib.sha256(('SYNTHETIC_TASK_CONTRACT_' + name).encode()).hexdigest(),
            original_protocol=dict(SYNTHETIC_ONLY=True, policy_dt_s=.02, toy_fixture_not_native=True))
        task.update(contracts.validate_worker_variant(task))
        return task

    def write_own_synthetic(payload, directory, filename, task):
        stream = io.BytesIO();torch.save(payload, stream);raw = stream.getvalue()
        path = directory / filename
        assert path.resolve().is_relative_to(output.resolve())
        with path.open('xb') as target: target.write(raw)
        descriptor = dict(kind='OWN_NEW_BPTT_FULL_CHECKPOINT_V2', path=str(path),
            SHA=hashlib.sha256(raw).hexdigest(), bytes=len(raw), actor_view=task['actor_view'],
            algorithm_family=task['algorithm_family'], allow_environment_reset=True,
            allow_partial_update=False, producer_run_id=task['run_id'])
        read_task = dict(task, algorithm_variant=task['algorithm_variant'].replace('_FRESH', '_RESUME'), resume_bptt=descriptor)
        read_task.update(contracts.validate_worker_variant(read_task))
        generated_checkpoints.append(dict(path=str(path), bytes=len(raw), SHA=descriptor['SHA'],
            kind='OWN_NEW_SYNTHETIC_CPU_ONLY_CHECKPOINT_NOT_ORIGINAL_MODEL'))
        return read_task

    def pinned_read_and_load(learner, read_task):
        calls = dict(physical_reads=0, decodes=0, decoded_loader_calls=0)
        admitted_path = Path(read_task['resume_bptt']['path']).resolve()
        def reader(path):
            assert Path(path).resolve() == admitted_path and admitted_path.is_relative_to(output.resolve())
            calls['physical_reads'] += 1
            assert calls['physical_reads'] == 1
            return admitted_path.read_bytes()
        def decoder(stream):
            calls['decodes'] += 1
            assert calls['decodes'] == 1 and isinstance(stream, io.BytesIO)
            return torch.load(stream, map_location='cpu', weights_only=True)
        pinned = contracts.PinnedOwnFullCheckpoint(read_task['resume_bptt'], decoder, read_bytes=reader)
        actual_api = learner.load_full_checkpoint
        def counted_api(payload, **kwargs):
            calls['decoded_loader_calls'] += 1
            assert kwargs == dict(allow_environment_reset=True, allow_partial_update=False)
            return actual_api(payload, **kwargs)
        learner.load_full_checkpoint = counted_api
        receipt = contracts.load_decoded_full_checkpoint_once(learner, pinned, read_task, layout)
        assert calls == dict(physical_reads=1, decodes=1, decoded_loader_calls=1)
        assert pinned.receipt()['physical_byte_opens'] == pinned.receipt()['SHA_calculations'] == pinned.receipt()['decodes'] == 1
        return pinned, receipt, calls

    def assert_all_restored(learner, payload, expected_states):
        ext = payload['context_reward_extension']
        assert_nested_equal(full_states(learner), expected_states, torch, 'four_models_four_optimizers')
        assert vars(learner.counts) == ext['counts']
        assert learner.iteration == payload['iteration'] and learner.sim_steps == payload['sim_steps']
        assert learner.wall_time == payload['wall_time'] and learner.collect_fraction == ext['collect_fraction']
        assert learner.pending_iteration == ext['pending_iteration']
        assert_nested_equal(learner.last_bptt_receipt, ext['last_bptt_receipt'], torch)
        assert_nested_equal(learner.context_predict_mask.cpu(), ext['context_predict_mask'], torch)
        expected_replay = copy.deepcopy(ext['replay'])
        expected_replay['data']['stream_cut'][(expected_replay['ptr'] - 1) % expected_replay['T']].fill_(True)
        assert_nested_equal(learner.buffer.export_state(), expected_replay, torch, 'full_replay_plus_only_stream_cut')
        for field in ('done', 'term', 'trunc', 'xi1_valid'):
            assert torch.equal(learner.buffer.data[field], ext['replay']['data'][field]), field
        assert torch.count_nonzero(learner.obs_hist) == 0
        assert torch.count_nonzero(ext['obs_hist']) > 0
        assert_nested_equal(core.capture_rng(), ext['rng'], torch, 'global_RNG_restored_by_real_loader')

    def rng_sequence_probe(saved_rng):
        isolated_python = random.Random();isolated_python.setstate(saved_rng['python'])
        isolated_torch = torch.Generator(device='cpu');isolated_torch.set_state(saved_rng['torch_cpu'])
        assert random.random() == isolated_python.random()
        assert torch.equal(torch.rand(5), torch.rand(5, generator=isolated_torch))
        if 'numpy' in saved_rng:
            assert np is not None
            name, values, pos, gauss, cached = saved_rng['numpy']
            isolated_np = np.random.RandomState(0)
            isolated_np.set_state((name, np.asarray(values, dtype='uint32'), pos, gauss, cached))
            assert (np.random.rand(5) == isolated_np.rand(5)).all()
        return dict(global_states_equal_before_draw=True, next_python_torch_numpy_draws_equal=True,
                    test_did_not_manually_restore_global_rng=True)

    def one_variant(name, view):
        directory = output / name;directory.mkdir()
        task = base_task(name, view)
        learner, env, teacher, snapshot = make_learner(view, directory / 'SOURCE_LEARNER_LOGS')
        initial_counts = dict(vars(learner.counts))
        started = time.monotonic()
        learner.collect(8)
        assert env.fresh_initializations == 1 and learner.sim_steps == 64
        for _ in range(20): learner.wm_update()
        receipts = []
        for index in range(3):
            assert learner.iteration == index
            learner.policy_update();receipts.append(gradient_receipt(learner))
            learner.iteration += 1
            assert_teacher(teacher, snapshot)
        learner.wall_time = time.monotonic() - started
        learner.collect_fraction = .375
        learner.pending_iteration = dict(phase='collect', collect_left=1, wm_left=1)
        expected_counts = dict(policy_attempts=3, pi_optimizer_steps=3, pi_bptt_optimizer_steps=3,
            pi_unverified_steps=0, pi_skipped_nonfinite=0, pi_skipped_zero=0,
            wm_optimizer_steps=20, aux_optimizer_steps=20, critic_optimizer_steps=3)
        assert vars(learner.counts) == expected_counts
        if view == contracts.RAW35_ACTOR_VIEW: assert learner.mdp.last_projection_status == 'not_used'
        payload = copy.deepcopy(learner._checkpoint(True))
        payload.update(bootstrap_teacher=teacher_identity, role=task['role'],
            original_task_protocol=task['original_protocol'], asset_SHA=task['asset_SHA'],
            contract_SHA=task['contract_SHA'], new_algorithm_not_PPO_resume=True,
            actor_view=view, algorithm_family=task['algorithm_family'],
            algorithm_variant=task['algorithm_variant'], run_id=task['run_id'])
        expected_states = full_states(learner)
        assert all(state['state'] for state in expected_states['optimizers'].values())
        read_task = write_own_synthetic(payload, directory, 'OWN_NEW_SYNTHETIC_FULL.pt', task)
        restored, fresh_env, restored_teacher, restored_snapshot = make_learner(view, directory / 'RESTORED_LEARNER_LOGS')
        assert vars(restored.counts) == initial_counts
        assert digest_nested(full_states(restored), torch) != digest_nested(expected_states, torch)
        random.seed(912);torch.manual_seed(913)
        if np is not None: np.random.seed(914)
        pinned, load_receipt, pin_calls = pinned_read_and_load(restored, read_task)
        assert_all_restored(restored, pinned.payload, expected_states)
        assert_teacher(restored_teacher, restored_snapshot)
        assert fresh_env.calls == fresh_env.fresh_initializations == 0
        # Fresh environment state is first initialized by original collect; no old physical state import.
        rng_probe = rng_sequence_probe(pinned.payload['context_reward_extension']['rng'])
        restored_counts = dict(vars(restored.counts))
        norm_keys = {model: [key for key in state if 'norm' in key and key.endswith(('.mean', '.var', '.count'))]
                     for model, state in expected_states['models'].items()}
        assert all(norm_keys.values())
        norm_digest = digest_nested({model: {key: state[key] for key in norm_keys[model]}
            for model, state in expected_states['models'].items()}, torch)
        old_boundary = (restored.buffer.ptr - 1) % restored.buffer.T
        restored.collect(1)
        assert fresh_env.calls == fresh_env.fresh_initializations == 1
        assert torch.equal(restored.obs_hist, restored.obs_hist[:, -1:, :].expand_as(restored.obs_hist))
        assert restored.buffer.data['stream_cut'][old_boundary].all()
        windows = restored.buffer.sample_windows(4096, 2)
        assert (windows['mask'][:, 1] == 0).any(), 'reset-resume stream boundary must mask later row'
        restored.pending_iteration['collect_left'] -= 1
        restored.pending_iteration['phase'] = 'wm'
        restored.wm_update();restored.pending_iteration['wm_left'] -= 1
        restored.pending_iteration['phase'] = 'policy'
        restored.policy_update();continued = gradient_receipt(restored)
        restored.iteration += 1;restored.pending_iteration = None
        assert vars(restored.counts) == dict(expected_counts, policy_attempts=4, pi_optimizer_steps=4,
            pi_bptt_optimizer_steps=4, wm_optimizer_steps=21, aux_optimizer_steps=21, critic_optimizer_steps=4)
        assert restored.iteration == 4 and restored.sim_steps == 72
        if view == contracts.RAW35_ACTOR_VIEW: assert restored.mdp.last_projection_status == 'not_used'
        assert all(value.device.type == 'cpu' for model in (restored.wm, restored.pi, restored.critic, restored.aux)
                   for value in model.state_dict().values())
        assert_teacher(restored_teacher, restored_snapshot)
        # Correct metadata cannot substitute for comparing the actual teacher tensors.
        bad = copy.deepcopy(pinned.payload)
        damaged_key = 'teacher.net.weight' if view == contracts.BASELINE_ACTOR_VIEW else 'teacher.synthetic_frozen_buffer'
        assert damaged_key in bad['pi']
        bad['pi'][damaged_key].add_(1.)
        bad_task = write_own_synthetic(bad, directory, 'OWN_NEW_SYNTHETIC_BAD_TEACHER.pt', task)
        bad_learner, bad_env, bad_teacher, bad_snapshot = make_learner(view, directory / 'BAD_TEACHER_LEARNER_LOGS')
        _, bad_load_receipt, bad_pin_calls = pinned_read_and_load(bad_learner, bad_task)
        teacher_negative = expect_error(lambda: assert_teacher(bad_teacher, bad_snapshot), AssertionError,
            'actual teacher weights' if view == contracts.BASELINE_ACTOR_VIEW else 'actual teacher buffers')
        assert teacher_negative['message'].startswith('actual frozen teacher state changed:')
        assert {key: value._version for key, value in teacher_source_root.items()} == teacher_source_versions
        assert digest_nested(teacher_source_root, torch) == source_root_digest
        assert bad_env.calls == 0
        return dict(name=name, actor_view=view, algorithm_family=task['algorithm_family'],
            actor_obs_dim=learner.mdp.obs_dim, context_dim=CONTEXT_DIM, horizon=16, history=10,
            initial_all_nine_counts_zero=initial_counts, source_counts=expected_counts,
            all_three_gradient_receipts=receipts, restored_counts=restored_counts,
            continued_counts=dict(vars(restored.counts)), continued_gradient_receipt=continued,
            restored_iteration=payload['iteration'], continued_iteration=restored.iteration,
            restored_sim_steps=payload['sim_steps'], continued_sim_steps=restored.sim_steps,
            exact_four_model_and_four_optimizer_values=True,
            restored_state_value_digests={name: digest_nested(value, torch) for name, value in expected_states.items()},
            running_norm_keys=norm_keys, running_norm_values_digest=norm_digest,
            replay_equal_except_declared_stream_cut=True, done_term_timeout_valid_masks_unchanged=True,
            saved_history_retained_live_history_zero_then_original_fresh_padding=True,
            collect_fraction_pending_iteration_wall_time_restored=True, RNG_probe=rng_probe,
            actual_pin_and_decoded_load=load_receipt, pin_call_counts=pin_calls,
            bad_teacher_actual_loader_completed=True, bad_teacher_pin_call_counts=bad_pin_calls,
            teacher_corruption_detected=teacher_negative, corrupted_payload_teacher_key=damaged_key,
            unchanged_standalone_source_root_versions_did_not_protect_actor=True,
            actual_teacher_weights_and_buffers_unchanged_for_admitted_restore=True,
            only_one_fresh_initialization_before_continued_collection=True,
            legacy_held_command_aux_sensor_approximation=True, command_tracking_fixed=False,
            sensor_projection_exact=False, oracle_used=False, bounded_residual=False,
            anchor_reward_uncertainty_changes=0), pinned.payload, read_task

    outcomes = []
    payloads = {}
    for name, view in [('A0_FULLCTX', contracts.BASELINE_ACTOR_VIEW), ('A1_RAW35', contracts.RAW35_ACTOR_VIEW)]:
        result, payload, read_task = one_variant(name, view)
        outcomes.append(result);payloads[name] = (payload, read_task)
    cross_view = []
    for source_name, target_name, target_view in [('A0_FULLCTX', 'A1_RAW35', contracts.RAW35_ACTOR_VIEW),
                                                ('A1_RAW35', 'A0_FULLCTX', contracts.BASELINE_ACTOR_VIEW)]:
        payload, read_task = payloads[source_name]
        target_learner, _, _, _ = make_learner(target_view, output / ('CROSS_VIEW_' + target_name + '_LOGS'))
        wrong = dict(read_task, actor_view=target_view, algorithm_variant=target_name + '_RESUME')
        cross_view.append(expect_error(lambda: contracts.validate_worker_variant(wrong), ValueError,
                                       source_name + '_to_' + target_name + '_descriptor_view'))
        forged_descriptor = dict(read_task['resume_bptt'], actor_view=target_view,
            algorithm_family='a1_raw35_legacy_v1' if target_view == contracts.RAW35_ACTOR_VIEW else 'a0_fullctx_legacy_v1')
        metadata_case = dict(wrong, resume_bptt=forged_descriptor)
        # Role/protocol identity is intentionally unchanged: the real contract/shape gate still blocks.
        before = digest_nested(full_states(target_learner), torch)
        cross_view.append(expect_error(lambda: contracts.validate_full_resume_payload(payload, metadata_case,
            target_learner.extension_contract, layout), ValueError, source_name + '_to_' + target_name + '_contract_gate'))
        assert digest_nested(full_states(target_learner), torch) == before
        cross_view.append(expect_error(lambda: target_learner.pi.load_state_dict(payload['pi'], strict=True), RuntimeError,
            source_name + '_to_' + target_name + '_isolated_strict_policy_shape_gate'))
        # The direct shape counterexample is isolated, not an admitted resume and never continued.
    assert not torch.cuda.is_initialized()
    assert not any(name == 'isaaclab' or name.startswith(('isaaclab.', 'omni.')) for name in sys.modules)
    return dict(kind='SYNTHETIC_CPU_ACTUAL_LEGACY_A0_A1_AND_FULL_RESET_RESUME_NOT_NATIVE_V1', passed=True,
        torch_version=str(torch.__version__), CUDA_initialized=False, native_expert_BPTT_updates_counted=0,
        original_model_PT_reads=0, own_new_synthetic_checkpoint_files=generated_checkpoints,
        no_original_selected_PT_worker_SDK_Apps_C_GO_locks_Git=True,
        explicit_dependency_paths=[str(path) for path in dependencies], actual_vendor=source_identity(actual_vendor),
        explicit_pinned_sources=identities, this_test=source_identity(__file__),
        fixture_AST_classes=['FakeTeacher', 'Synthetic'], fixture_bottom_executed=False,
        bridge_AST_classes=['BridgeState', 'OriginalTaskMdp'], original_policy_AST_class='TeacherResidualPolicy',
        PinnedTeacher_and_NativeTaskBridge_executed=False, actual_metadata_validator='resume_runtime_contracts_v3.validate_full_resume_payload',
        actual_decoded_loader='ctx_reward_full_resume_candidate_v2.ContextRewardLearner.load_full_checkpoint',
        all_task_metadata_SYNTHETIC_NOT_PRODUCTION=True, variants=outcomes, cross_view_counterexamples=cross_view,
        RNG_draw_sequence_test_is_not_bitwise_physics_trajectory_resume=True,
        validations_not_claimed=['native owner admission', 'SDK/backend/getter binding', 'original bootstrap PT byte loading',
            'real physics/DR/noisy sensors/100Hz clock', 'real E0/E2 saved checkpoint restoration',
            'App.close semantics', 'native task robustness or success rate'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--vendor-parent', type=Path, required=True)
    parser.add_argument('--dependency-path', type=Path, action='append', default=[])
    for name in PINS: parser.add_argument('--' + name.replace('_', '-'), type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=False)
    receipt_path = output / 'SYNTHETIC_TORCH_RESUME_RECEIPT_V1.json'
    try:
        result = run(args, output)
    except BaseException:
        result = dict(kind='SYNTHETIC_CPU_LEGACY_RESUME_SOFTWARE_TEST_ERROR_V1', passed=False,
                      error=traceback.format_exc(), native_expert_BPTT_updates_counted=0,
                      output_dir=str(output), actual_inputs=vars(args))
        with receipt_path.open('x', encoding='utf-8') as stream: json.dump(result, stream, indent=2, default=str)
        raise
    with receipt_path.open('x', encoding='utf-8') as stream: json.dump(result, stream, indent=2, allow_nan=False)
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == '__main__': main()
