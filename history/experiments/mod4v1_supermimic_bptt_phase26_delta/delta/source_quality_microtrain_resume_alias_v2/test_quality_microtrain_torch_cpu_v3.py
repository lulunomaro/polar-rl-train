"""A1 LEGACY synthetic CPU Torch 3 -> full resume -> actual target 5.

SOURCE deliverable: parent runs with existing CPU dependencies. Never run native
owner/worker, SDK, CUDA, original selected PT, C, GO or locks. Only newly produced
SYNTHETIC checkpoint/FINAL/output files exist in one exclusive output directory.
The old CPU fixture's main/run/tests are never called. No bounded residual/H32.
A retained decoded-root mutation is a STRICT FAILURE, not hidden by working-copy
loading. The complete 3->5 observations and negative cases are still reported.
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
from pathlib import Path
import random
import sys
sys.dont_write_bytecode = True
import time
import traceback
import types
from collections.abc import Mapping

PINS = {
    'legacy_support': '4a4141259410702d2103952a828be31a7ddaf28057272b69bbf8a8bde3109e55',
    'fixture': '4de256764f7fec0dac6fbb624a7a4189d7a686dc9d28bd5570a9a43f8afce10d',
    'bridge_source': '8211964c2ce3dd78fdb9fee6603ee4a4dcfbca6fa9d7df44f20d3ddb7aaead29',
    'payload_core': '20fd4945a0f2345c17505316560ae6d358fcce147c6988f62a08d867e084e749',
    'resume_contracts': 'dc4bc67193457a4fb72b125d23fa482cd3d686363bd1a93eb07268f4e4e26cb7',
    'raw35_source': 'bb7555ff2de598677ea6cfe5dadefe0a9cfe37d37661635d186bcb14c1df2223',
    'microtrain_contracts': '7a6d2c1378f839b5bc827683aa8951b1844b7ffb46f56478e73ecdd92b245673',
}
VENDOR_PINS = {
    'learner.py': 'da3380bf84adb90f8cd528a05c86773baf6bcb4691dbf13e0ec1ffd9f899f816',
    'networks.py': 'c7829e6a1bb9166d724a931858b76424439f371669dfb4bb534b9e76c5c74706',
    'replay.py': '8c7ddacf5387e67e7ecdd57027401a84a2cff1c31469115837d60b90357350da',
    'geometry.py': '89ac3b9470fd6f041fd418365283355a07ad96c4bf38740cf3c5d2d98acb7787',
    'contract.py': 'd756f2a102a81b2f16295dad66f46e9783b42a3f67e7416360fcf136c2ff06ce',
}
CPU_BATCH = 512  # Actual toy tensors, not N8 with forged production metadata.
REPORT_KIND = 'SYNTHETIC_CPU_A1_LEGACY_MICROTRAIN_WHOLE_INGRESS_COPY_CORE_V3'
REPORT_PURPOSE = 'SAME_CORRECTED_FIXTURE_WITH_CORE_V3_WHOLE_INGRESS_DEEPCOPY_V3'


def identity(path):
    raw = Path(path).read_bytes()
    return dict(path=str(Path(path).resolve()), bytes=len(raw), SHA256=hashlib.sha256(raw).hexdigest())


def load_source(path, name):
    assert name not in sys.modules, 'unexpected pre-import: ' + name
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    assert Path(module.__file__).resolve() == Path(path).resolve()
    return module


def write_json_once(path, value):
    raw = (json.dumps(value, indent=2, allow_nan=False, ensure_ascii=False) + '\n').encode()
    with Path(path).open('xb') as target:
        target.write(raw)
    return raw


def run(args, output, result):
    identities = {}
    for key, expected in PINS.items():
        path = getattr(args, key).resolve(strict=True)
        assert path.suffix == '.py'
        identities[key] = identity(path)
        assert identities[key]['SHA256'] == expected, (key, identities[key])
        setattr(args, key, path)
    vendor_parent = args.vendor_parent.resolve(strict=True)
    package = vendor_parent / 'supermimic_vendor_v2'
    init = package / '__init__.py'
    init_ast = ast.parse(init.read_text(encoding='utf-8'))
    assert not init_ast.body or (len(init_ast.body) == 1 and isinstance(init_ast.body[0], ast.Expr)
        and isinstance(init_ast.body[0].value, ast.Constant) and isinstance(init_ast.body[0].value.value, str)), 'use original docstring-only vendor init, no SDK import'
    vendor_ids = {name: identity(package / name) for name in VENDOR_PINS}
    assert all(vendor_ids[name]['SHA256'] == sha for name, sha in VENDOR_PINS.items())
    dependencies = [path.resolve(strict=True) for path in args.dependency_path]
    for path in reversed([vendor_parent, *dependencies]):
        sys.path.insert(0, str(path))
    support = load_source(args.legacy_support, '_quality_cpu_old_support_not_its_main')
    # Only these top-level old functions are reused. support.run/main never run.
    equal = support.assert_nested_equal
    digest = support.digest_nested
    import torch
    torch.set_num_threads(1)
    torch.set_default_dtype(torch.float32)
    torch.manual_seed(37)
    random.seed(37)
    assert not torch.cuda.is_initialized()
    try:
        import numpy as np
    except ImportError:
        np = None
    if np is not None:
        np.random.seed(37)
    from supermimic_vendor_v2.geometry import invariant_features, unflatten_state
    from supermimic_vendor_v2.contract import SUPERMIMIC_STATE_KEY, SUPERMIMIC_TRANSITION_KEY
    from supermimic_vendor_v2.learner import SuperMimicConfig
    for name in VENDOR_PINS:
        module_name = 'supermimic_vendor_v2.' + name[:-3]
        assert Path(sys.modules[module_name].__file__).resolve() == package / name
    core = load_source(args.payload_core, '_quality_cpu_original_payload_core_8116')
    base = load_source(args.resume_contracts, 'resume_runtime_contracts_v3')
    raw35 = load_source(args.raw35_source, '_quality_cpu_original_raw35_bb75')
    q = load_source(args.microtrain_contracts, 'quality_microtrain_contracts_v1')
    assert q.COUNT_FIELDS == base.COUNT_FIELDS and q.RAW35_ACTOR_VIEW == base.RAW35_ACTOR_VIEW
    ns = types.ModuleType('_quality_cpu_selected_toy_classes')
    sys.modules[ns.__name__] = ns
    ns.__dict__.update(torch=torch, dataclass=dataclass, invariant_features=invariant_features,
        unflatten_state=unflatten_state, SUPERMIMIC_STATE_KEY=SUPERMIMIC_STATE_KEY,
        SUPERMIMIC_TRANSITION_KEY=SUPERMIMIC_TRANSITION_KEY)
    support.ast_classes(args.bridge_source, ('BridgeState', 'OriginalTaskMdp', 'TeacherResidualPolicy'), ns.__dict__)
    support.ast_classes(args.fixture, ('FakeTeacher',), ns.__dict__)
    original_tree = ast.parse(args.fixture.read_text(encoding='utf-8'))
    toy = copy.deepcopy(next(node for node in original_tree.body if isinstance(node, ast.ClassDef) and node.name == 'Synthetic'))
    class ToyBatchOnly(ast.NodeTransformer):
        count = 0
        def visit_Constant(self, node):
            if type(node.value) is int and node.value == 8:
                self.count += 1
                return ast.copy_location(ast.Constant(CPU_BATCH), node)
            return node
    batch_transform = ToyBatchOnly()
    toy = batch_transform.visit(toy)
    assert batch_transform.count == 7, 'only seven original toy batch constants may change'
    toy.name = 'SyntheticCPU512'
    exec(compile(ast.fix_missing_locations(ast.Module(body=[toy], type_ignores=[])),
        str(args.fixture) + ':ONLY_TOY_BATCH_8_TO_512', 'exec'), ns.__dict__)
    FakeTeacher = ns.FakeTeacher
    TeacherResidualPolicy = ns.TeacherResidualPolicy
    CONTEXT = 40
    layout = [('SYNTHETIC_actor_obs35', 35), ('SYNTHETIC_model_only_suffix', 5)]

    class LegacyCPUEnv(ns.SyntheticCPU512):
        def __init__(self):
            super().__init__()
            self.xi = torch.cat((self.xi, torch.arange(5).float().expand(CPU_BATCH, -1) * .01), -1)
            self.mdp = raw35.Raw35ActorMDP(ns.OriginalTaskMdp(CONTEXT, self.s), transition_projector=None)
            self.fresh_initializations = 0
        def init_state(self):
            self.fresh_initializations += 1
            assert self.fresh_initializations == 1, 'synthetic lifecycle monitor: extra reset/init'
            return super().init_state()
        def export_supermimic_resume(self):
            return dict(exact=False, context_layout=layout, kind='SYNTHETIC_CPU_ENV_NOT_PHYSX', physical_restore_claim=False)

    config = SuperMimicConfig(iterations=100, buffer_steps=16, utd=1., horizon=16,
        goal_frames=1, hist=10, z_dim=4, wm_hidden=(16,), policy_hidden=(16,), critic_hidden=(16,),
        wm_window=2, wm_batches=1, wm_batch=8, pi_batch=8, lr=.001, warmup_steps=8,
        wm_only_iters=2, critic_epochs=1, critic_minibatches=1, ckpt_every=10000,
        log_every=10000, log_backend='none', amp='none', compile=False, seed=37)
    mask = torch.ones(CONTEXT)
    mask[:4] = 0
    mask[14:16] = 0
    mask[22:] = 0
    seed_teacher = FakeTeacher()
    seed_teacher.register_buffer('synthetic_frozen_buffer', torch.tensor([.2, -.4, .6]))
    teacher_root = copy.deepcopy(seed_teacher.state_dict())
    teacher_root_values = digest(teacher_root, torch)
    teacher_root_versions = {key: value._version for key, value in teacher_root.items()}
    stream = io.BytesIO()
    torch.save(dict(SYNTHETIC_ONLY=True, actor_state_dict=teacher_root), stream)
    teacher_bytes = stream.getvalue()
    teacher_identity = dict(source_path=str(output / 'NO_TEACHER_FILE_BYTESIO_IDENTITY'),
        source_SHA=hashlib.sha256(teacher_bytes).hexdigest(), source_bytes=len(teacher_bytes),
        synthetic_BytesIO_identity_only=True, original_teacher_PT_reads=0)

    def snapshot(model):
        return {key: value.detach().clone() for key, value in model.state_dict().items()}
    def teacher_guard(model, expected):
        current = model.state_dict()
        assert current.keys() == expected.keys()
        for key, value in expected.items():
            assert torch.equal(current[key], value), 'actual synthetic teacher state changed: ' + key
        assert model.training is False
        assert all(not p.requires_grad and p.grad is None for p in model.parameters())
    def make_learner(label):
        env = LegacyCPUEnv()
        teacher = FakeTeacher()
        teacher.register_buffer('synthetic_frozen_buffer', torch.zeros(3))
        teacher.load_state_dict(teacher_root, strict=True)
        teacher.eval().requires_grad_(False)
        expected_teacher = snapshot(teacher)
        class Learner(core.ContextRewardLearner):
            def _make_policy(self):
                return TeacherResidualPolicy(super()._make_policy(), teacher, 0, scale=.05)
        learner = Learner(env, config, output / label, device='cpu', aux_hidden=(16,),
            aux_batch=8, predict_context_mask=mask)
        assert env.num_envs == CPU_BATCH and learner.obs_hist.shape == (CPU_BATCH, 10, 35)
        assert env.fresh_initializations == 1 and env.calls == 0
        assert vars(learner.counts) == q.zero_counts()
        assert all(not opt.state for opt in (learner.opt_wm, learner.opt_pi, learner.opt_v, learner.opt_aux))
        assert learner.mdp.transition_projector is None and learner.mdp.tracking_component is None
        assert learner.mdp.project_predicted_context.__self__ is learner.mdp.base_mdp
        assert learner.pi.scale == .05 and type(learner.pi) is TeacherResidualPolicy
        teacher_ids = {id(p) for p in teacher.parameters()}
        assert not teacher_ids.intersection(id(p) for group in learner.opt_pi.param_groups for p in group['params'])
        teacher_guard(teacher, expected_teacher)
        return learner, env, teacher, expected_teacher
    def states(learner):
        return dict(models={name: copy.deepcopy(getattr(learner, name).state_dict()) for name in ('wm', 'pi', 'critic', 'aux')},
            optimizers={name: copy.deepcopy(getattr(learner, name).state_dict()) for name in ('opt_wm', 'opt_pi', 'opt_v', 'opt_aux')})
    def gradient(learner):
        receipt = copy.deepcopy(learner.last_bptt_receipt)
        assert receipt['verified_bptt_optimizer_step'] is True, receipt
        for finite, norm in (('cross_time_finite', 'cross_time_grad_norm'), ('wm_path_finite', 'wm_path_grad_norm')):
            assert receipt[finite] is True and receipt[norm] > 0, receipt
        assert receipt['parameter_grad_norm'] > 0 and receipt['probe_parameter_delta_l2'] > 0
        return receipt
    def tree_tensors(value, prefix='root'):
        if torch.is_tensor(value):
            yield prefix, value
        elif isinstance(value, Mapping):
            for key, child in value.items():
                yield from tree_tensors(child, prefix + '/' + str(key))
        elif isinstance(value, (list, tuple)):
            for index, child in enumerate(value):
                yield from tree_tensors(child, prefix + '/' + str(index))
    def versions(value):
        return {path: dict(identity=id(t), version=t._version, device=str(t.device), shape=list(t.shape), dtype=str(t.dtype)) for path, t in tree_tensors(value)}
    def changes(before, after, prefix='root', out=None):
        out = [] if out is None else out
        if len(out) >= 40:
            return out
        if torch.is_tensor(before) and torch.is_tensor(after):
            if before.shape != after.shape or before.dtype != after.dtype or not torch.equal(before, after):
                out.append(prefix)
        elif isinstance(before, Mapping) and isinstance(after, Mapping) and before.keys() == after.keys():
            for key in before:
                changes(before[key], after[key], prefix + '/' + str(key), out)
        elif type(before) is type(after) and isinstance(before, (tuple, list)) and len(before) == len(after):
            for index, (a, b) in enumerate(zip(before, after)):
                changes(a, b, prefix + '/' + str(index), out)
        elif before != after:
            out.append(prefix)
        return out

    result.update(torch_version=str(torch.__version__), explicit_sources=identities,
        actual_vendor_sources=vendor_ids, vendor_init=identity(init), this_test=identity(__file__),
        CPU_batch=CPU_BATCH, minibatches=8, horizon=16, history=10,
        fixture_reuse=dict(old_module_main_called=False, old_module_run_called=False, old_test_suite_rerun=False,
            original_fixture_bottom_executed=False, selected_bridge_classes=['BridgeState', 'OriginalTaskMdp', 'TeacherResidualPolicy'],
            selected_toy_classes=['FakeTeacher', 'Synthetic'], only_toy_batch_literals_changed=7,
            old_batch=8, actual_new_batch=CPU_BATCH, production_worker_executed=False))
    source, source_env, source_teacher, source_teacher_expected = make_learner('SOURCE_LEARNER_LOGS')
    source.collect(10)
    for _ in range(20):
        source.wm_update()
    source_receipts = []
    for index in range(3):
        assert source.iteration == index
        source.policy_update()
        source_receipts.append(gradient(source))
        source.iteration += 1
        teacher_guard(source_teacher, source_teacher_expected)
    source_counts = dict(vars(source.counts))
    assert source_counts == dict(policy_attempts=3, pi_optimizer_steps=3, pi_bptt_optimizer_steps=3,
        pi_unverified_steps=0, pi_skipped_nonfinite=0, pi_skipped_zero=0,
        wm_optimizer_steps=20, aux_optimizer_steps=20, critic_optimizer_steps=3)
    assert source_env.calls == 10 and source_env.fresh_initializations == 1
    source.wall_time = .125
    source.collect_fraction = .375
    source.pending_iteration = dict(phase='collect', collect_left=1, wm_left=1)
    protocol = dict(SYNTHETIC_CPU_ONLY=True, toy_fixture_not_native=True, policy_dt_s=.02, context_layout=layout)
    task_base = dict(role='E3', role_key='SYNTHETIC_CPU_SEGMENT_E3', run_id='SYNTHETIC_CPU_SEGMENT_TO5',
        num_envs=CPU_BATCH, algorithm_variant='A1_RAW35_RESUME', actor_view=base.RAW35_ACTOR_VIEW,
        algorithm_family='a1_raw35_legacy_v1', teacher_path=teacher_identity['source_path'],
        teacher_SHA=teacher_identity['source_SHA'], teacher_bytes=teacher_identity['source_bytes'],
        asset_SHA=hashlib.sha256(b'SYNTHETIC_CPU_ASSET_NOT_NATIVE').hexdigest(),
        contract_SHA=hashlib.sha256(b'SYNTHETIC_CPU_CONTRACT_NOT_NATIVE').hexdigest(), original_protocol=protocol)
    producer_run = 'SYNTHETIC_CPU_PRODUCER_AT3'
    producer_key = 'SYNTHETIC_CPU_PRODUCER_E3'
    payload = copy.deepcopy(source._checkpoint(True))
    payload.update(bootstrap_teacher=teacher_identity, role='E3', role_key=producer_key,
        original_task_protocol=protocol, asset_SHA=task_base['asset_SHA'], contract_SHA=task_base['contract_SHA'],
        new_algorithm_not_PPO_resume=True, actor_view=base.RAW35_ACTOR_VIEW,
        algorithm_family='a1_raw35_legacy_v1', algorithm_variant='A1_RAW35_FRESH', run_id=producer_run)
    expected_states = states(source)
    assert all(state['state'] for state in expected_states['optimizers'].values())
    production = output / 'OWN_SYNTHETIC_PRODUCER' / 'production'
    (production / 'checkpoints').mkdir(parents=True)
    checkpoint_path = production / 'checkpoints' / 'source_at3_complete.pt'
    stream = io.BytesIO()
    torch.save(payload, stream)
    serialized = stream.getvalue()
    checkpoint_sha = hashlib.sha256(serialized).hexdigest()  # Producer serialization identity, not cache-load hashing.
    with checkpoint_path.open('xb') as stream:
        stream.write(serialized)
    checkpoint = dict(path=str(checkpoint_path), SHA=checkpoint_sha, bytes=len(serialized), counts=source_counts,
        full_new_model_critic_aux_optimizers_replay_RNG_hist_saved=True)
    final = dict(kind=base.FINAL_KIND, role='E3', role_key=producer_key, run_id=producer_run,
        passed_execution=True, teacher_unchanged=True, algorithm_variant='A1_RAW35_FRESH',
        actor_view=base.RAW35_ACTOR_VIEW, algorithm_family='a1_raw35_legacy_v1', counts=source_counts,
        actual_BPTT_policy_steps=3, checkpoint=checkpoint, SYNTHETIC_CPU_SOFTWARE_ONLY=True,
        native_worker_owner_or_App_execution=False, original_selected_PT_reads=0)
    final_path = production / 'FINAL.json'
    final_bytes = write_json_once(final_path, final)
    descriptor = dict(kind='OWN_NEW_BPTT_FULL_CHECKPOINT_V2', path=str(checkpoint_path), SHA=checkpoint_sha,
        bytes=len(serialized), actor_view=base.RAW35_ACTOR_VIEW, algorithm_family='a1_raw35_legacy_v1',
        allow_environment_reset=True, allow_partial_update=False, producer_run_id=producer_run, producer_role_key=producer_key)
    entry = dict(task_base, resume_bptt=descriptor, microtrain=dict(schema=q.SCHEMA, target_verified_increment=2,
        source_final=dict(path=str(final_path), bytes=len(final_bytes), SHA=hashlib.sha256(final_bytes).hexdigest())))
    plan = dict(kind=q.PLAN_KIND, H1_excluded=True, requested_roles=['E3'],
        deferred_roles=[role for role in q.ROLES if role != 'E3'], entries=[entry])
    calls = dict(source_FINAL_reads=0, source_FINAL_hashes=0, checkpoint_reads=0,
        checkpoint_hashes=0, CPU_decodes=0, actual_original_full_loader_calls=0)
    old_json_hashlib = q.hashlib
    def final_hash(raw):
        calls['source_FINAL_hashes'] += 1
        assert calls['source_FINAL_hashes'] == 1
        return hashlib.sha256(raw)
    def final_reader(path):
        assert Path(path) == final_path
        calls['source_FINAL_reads'] += 1
        assert calls['source_FINAL_reads'] == 1
        with final_path.open('rb') as stream:
            return stream.read(262145)
    try:
        q.hashlib = types.SimpleNamespace(sha256=final_hash)
        bound_plan = q.validate_microtrain_plan(plan, reader=final_reader)
    finally:
        q.hashlib = old_json_hashlib
    bound = bound_plan['entries'][0]
    task = q.bind_microtrain_task(dict(bound, original_protocol=protocol), bound)
    q.validate_worker_microtrain_task(task)
    assert task['target_bptt_steps'] == 5 and task['microtrain']['declared_source_counts'] == source_counts
    restored, fresh_env, restored_teacher, restored_teacher_expected = make_learner('RESTORED_LEARNER_LOGS')
    assert digest(states(restored), torch) != digest(expected_states, torch)
    random.seed(912)
    torch.manual_seed(913)
    if np is not None:
        np.random.seed(914)
    old_cp_hashlib = base.hashlib
    def checkpoint_hash(raw):
        calls['checkpoint_hashes'] += 1
        assert calls['checkpoint_hashes'] == 1
        return hashlib.sha256(raw)
    def checkpoint_reader(path):
        assert Path(path) == checkpoint_path and checkpoint_path.is_relative_to(output)
        calls['checkpoint_reads'] += 1
        assert calls['checkpoint_reads'] == 1
        return checkpoint_path.read_bytes()
    def decoder(stream):
        calls['CPU_decodes'] += 1
        assert calls['CPU_decodes'] == 1 and isinstance(stream, io.BytesIO)
        return torch.load(stream, map_location='cpu', weights_only=True)
    try:
        base.hashlib = types.SimpleNamespace(sha256=checkpoint_hash)
        pinned = base.PinnedOwnFullCheckpoint(task['resume_bptt'], decoder, read_bytes=checkpoint_reader)
    finally:
        base.hashlib = old_cp_hashlib
    root = pinned.payload
    root_values = copy.deepcopy(root)  # Diagnostic snapshot ONLY: original loader receives root, never this copy.
    root_digest_before = digest(root, torch)
    root_versions_before = versions(root)
    q.validate_microtrain_payload(root, task)
    real_loader = restored.load_full_checkpoint
    def tracked_loader(value, **kwargs):
        calls['actual_original_full_loader_calls'] += 1
        assert calls['actual_original_full_loader_calls'] == 1 and value is root
        assert kwargs == dict(allow_environment_reset=True, allow_partial_update=False)
        return real_loader(value, **kwargs)
    restored.load_full_checkpoint = tracked_loader
    load_receipt = base.load_decoded_full_checkpoint_once(restored, pinned, task, layout)
    equal(states(restored), expected_states, torch, 'strict_four_models_four_optimizers')
    ext = root_values['context_reward_extension']
    assert dict(vars(restored.counts)) == source_counts == load_receipt['restored_counts']
    assert restored.iteration == payload['iteration'] == 3 and restored.sim_steps == payload['sim_steps']
    assert restored.wall_time == payload['wall_time'] and restored.collect_fraction == ext['collect_fraction']
    equal(restored.last_bptt_receipt, ext['last_bptt_receipt'], torch)
    equal(restored.pending_iteration, ext['pending_iteration'], torch)
    equal(restored.context_predict_mask.cpu(), ext['context_predict_mask'], torch)
    expected_replay = copy.deepcopy(ext['replay'])
    boundary = (expected_replay['ptr'] - 1) % expected_replay['T']
    expected_replay['data']['stream_cut'][boundary].fill_(True)
    equal(restored.buffer.export_state(), expected_replay, torch, 'full_replay_only_declared_stream_cut')
    for field in ('done', 'term', 'trunc', 'xi1_valid'):
        assert torch.equal(restored.buffer.data[field], ext['replay']['data'][field])
    assert torch.count_nonzero(restored.obs_hist) == 0 and torch.count_nonzero(ext['obs_hist']) > 0
    equal(core.capture_rng(), ext['rng'], torch, 'strict_actual_RNG_states_after_original_loader')
    assert fresh_env.fresh_initializations == 1 and fresh_env.calls == 0
    teacher_guard(restored_teacher, restored_teacher_expected)
    teacher_versions_before_train = {key: t._version for key, t in restored_teacher.state_dict().items()}
    norm_keys = {name: [key for key in values if 'norm' in key and key.endswith(('.mean', '.var', '.count'))]
        for name, values in expected_states['models'].items()}
    assert all(norm_keys.values())
    segment = q.start_microtrain_segment(task, dict(vars(restored.counts)), resume_receipt=load_receipt)
    assert segment['starting_verified_counter'] == 3 and segment['target_verified_increment'] == 2
    assert segment['target_cumulative_verified_counter'] == 5
    observed_after_load = dict(decoded_root_values_unchanged=digest(root, torch) == root_digest_before,
        decoded_root_tensor_id_versions_unchanged=versions(root) == root_versions_before,
        pending_iteration_alias=restored.pending_iteration is root['context_reward_extension']['pending_iteration'])
    collect_observations = []
    actual_collect = restored.collect
    def observed_collect(n):
        value = actual_collect(n)
        if not collect_observations:
            assert torch.equal(restored.obs_hist, restored.obs_hist[:, -1:, :].expand_as(restored.obs_hist))
        collect_observations.append(dict(n=n, env_calls=fresh_env.calls, initializations=fresh_env.fresh_initializations))
        return value
    restored.collect = observed_collect  # Calls original body unchanged; not a counter/target shim.
    continued_receipts = []
    actual_policy_update = restored.policy_update
    def observed_policy_update():
        before = dict(vars(restored.counts))
        value = actual_policy_update()
        after = dict(vars(restored.counts))
        if after['pi_bptt_optimizer_steps'] > before['pi_bptt_optimizer_steps']:
            continued_receipts.append(gradient(restored))
        teacher_guard(restored_teacher, restored_teacher_expected)
        return value
    restored.policy_update = observed_policy_update
    train_result = restored.train(target_bptt_steps=segment['target_cumulative_verified_counter'])
    end_counts = dict(vars(restored.counts))
    completed = q.finish_microtrain_segment(segment, end_counts, stopped=False)
    assert end_counts['pi_bptt_optimizer_steps'] == 5 and train_result['target_bptt_reached'] is True
    assert len(continued_receipts) == 2
    assert completed['starting_verified_counter'] == 3 and completed['actual_verified_increment'] == 2
    assert completed['total_original_verified_counter'] == 5 and completed['target_reached'] is True
    assert completed['ending_counts'] == end_counts and train_result['counts'] == end_counts
    assert fresh_env.fresh_initializations == 1 and fresh_env.calls == sum(x['n'] for x in collect_observations)
    assert restored.buffer.data['stream_cut'][boundary].all()
    assert all(torch.equal(restored.buffer.data[field][boundary], ext['replay']['data'][field][boundary]) for field in ('done', 'term', 'trunc', 'xi1_valid'))
    teacher_guard(source_teacher, source_teacher_expected)
    teacher_guard(restored_teacher, restored_teacher_expected)
    assert {key: t._version for key, t in restored_teacher.state_dict().items()} == teacher_versions_before_train
    assert digest(teacher_root, torch) == teacher_root_values
    assert {key: t._version for key, t in teacher_root.items()} == teacher_root_versions
    assert pinned.payload is root and pinned.raw == serialized
    assert calls == dict(source_FINAL_reads=1, source_FINAL_hashes=1, checkpoint_reads=1,
        checkpoint_hashes=1, CPU_decodes=1, actual_original_full_loader_calls=1)
    root_digest_after = digest(root, torch)
    root_versions_after = versions(root)
    retained_guard = dict(values_unchanged=root_digest_after == root_digest_before,
        tensor_identity_versions_unchanged=root_versions_after == root_versions_before,
        before_digest=root_digest_before, after_digest=root_digest_after,
        changed_value_paths=changes(root_values, root),
        changed_tensor_version_paths=[path for path in root_versions_before if root_versions_before[path] != root_versions_after.get(path)][:40],
        raw_bytes_unchanged=pinned.raw == serialized, PT_rereads_after_single_cache_load=0,
        source_PT_external_rehash_not_performed=True, original_loader_received_retained_root_not_working_copy=True)
    result['positive'] = dict(actual_source_counts=source_counts, source_gradient_receipts=source_receipts,
        actual_restored_counts=load_receipt['restored_counts'], actual_end_counts=end_counts,
        actual_core_train_result=train_result, continued_verified_gradient_receipts=continued_receipts,
        actual_segment=completed, one_cache_and_JSON_binding=calls, original_full_loader_receipt=load_receipt,
        strict_four_models_four_optimizers=True, strict_running_norm_keys=norm_keys,
        strict_replay_except_stream_cut=True, done_term_timeout_valid_masks_preserved=True,
        saved_history_retained_live_history_zero_then_original_padding=True,
        strict_original_RNG_states_restored=True, global_RNG_draw_probe_not_used=True,
        pending_collect_fraction_iteration_wall_time_restored=True,
        no_extra_fresh_environment_initialization=True, synthetic_initializations=fresh_env.fresh_initializations,
        collect_observations=collect_observations, teacher_actual_weights_and_synthetic_buffers_unchanged=True,
        teacher_versions_frozen_during_continued_train=True, standalone_CPU_teacher_root_unchanged=True,
        observed_after_load=observed_after_load, whole_retained_CPU_source_guard=retained_guard,
        model_norms_are_trainable_not_frozen_eval=True, actor_view=base.RAW35_ACTOR_VIEW,
        algorithm_family='a1_raw35_legacy_v1', legacy_projection_held_aux=True,
        bounded_residual=False, anchor_uncertainty_reward_changes=False,
        synthetic_source_FINAL={key: task['microtrain']['source_final'][key] for key in ('path', 'bytes', 'SHA')},
        synthetic_checkpoint=dict(path=str(checkpoint_path), bytes=len(serialized), SHA=checkpoint_sha))

    negatives = []
    def reject(label, layer, function, expected=(ValueError, AssertionError, RuntimeError)):
        try:
            function()
        except expected as exc:
            negatives.append(dict(label=label, validation_layer=layer, blocked=True,
                error_type=type(exc).__name__, message=str(exc)))
            return
        raise AssertionError('negative unexpectedly passed: ' + label)
    def rebound(final_variant, descriptor_variant=None):
        variant = copy.deepcopy(entry)
        if descriptor_variant is not None:
            variant['resume_bptt'] = descriptor_variant
        raw = (json.dumps(final_variant, sort_keys=True) + '\n').encode()
        variant['microtrain']['source_final'].update(bytes=len(raw), SHA=hashlib.sha256(raw).hexdigest())
        own_bound = q.bind_plan_source_final(variant, reader=lambda _: raw)
        return q.validate_microtrain_entry(own_bound)
    reject('raw FINAL byte pin stale', 'q.bind_plan_source_final exact SHA/bytes before retained metadata',
        lambda: q.bind_plan_source_final(entry, reader=lambda _: final_bytes + b' '))
    stale = copy.deepcopy(final)
    for name in ('policy_attempts', 'pi_optimizer_steps', 'pi_bptt_optimizer_steps'):
        stale['counts'][name] += 1
    stale['actual_BPTT_policy_steps'] = stale['counts']['pi_bptt_optimizer_steps']
    stale['checkpoint']['counts'] = copy.deepcopy(stale['counts'])
    assert base.validate_count_snapshot(stale['counts']) == stale['counts']
    assert stale['checkpoint']['counts'] == stale['counts']
    # Ordering is valid: metadata4 must lose to actual decoded payload3, not to metadata ordering.
    stale_bound = rebound(stale)
    reject('self-consistent stale JSON counter versus real payload', 'q.validate_microtrain_payload BEFORE original loader',
        lambda: q.validate_microtrain_payload(root_values, stale_bound))
    assert negatives[-1]['message'] == 'actual full payload counters differ from source FINAL'
    for field, wrong in (('run_id', 'STALE_OTHER_PRODUCER'), ('role', 'W35'), ('role_key', 'STALE_OTHER_KEY')):
        wrong_final = copy.deepcopy(final)
        wrong_final[field] = wrong
        reject('source FINAL ' + field + ' differs', 'q.source_final bounded JSON lineage after byte pin',
            lambda value=wrong_final: rebound(value))
    unchanged_models = digest(states(restored), torch)
    for field, wrong in (('run_id', 'OTHER_DECODED_RUN'), ('role', 'W35'), ('role_key', 'OTHER_DECODED_KEY')):
        bad = copy.deepcopy(root_values)
        bad[field] = wrong
        reject('decoded payload ' + field + ' differs', 'q.validate_microtrain_payload BEFORE four-model loader',
            lambda value=bad: q.validate_microtrain_payload(value, task))
        assert digest(states(restored), torch) == unchanged_models
    isolated, _, _, _ = make_learner('ISOLATED_BAD_SHAPE_NOT_ADMITTED')
    bad_shape = copy.deepcopy(root_values)
    bad_key = next(key for key, value in bad_shape['pi'].items()
        if key.startswith('residual.') and value.ndim == 2 and value.shape[0] > 1)
    bad_shape['pi'][bad_key] = bad_shape['pi'][bad_key][:-1].clone()
    q.validate_microtrain_payload(bad_shape, task)  # Metadata is not a strict shape checker.
    reject('wrong residual tensor shape', 'isolated SHA-pinned payload-core full loader -> strict pi.load_state_dict; prior models may already load',
        lambda: base.load_decoded_full_checkpoint_once(isolated,
            types.SimpleNamespace(payload=bad_shape, receipt=pinned.receipt), task, layout), expected=RuntimeError)
    reset_env = LegacyCPUEnv()
    reset_env.init_state()
    reject('extra init/reset', 'NEW synthetic lifecycle monitor ONLY; metadata booleans are not native reset interception',
        reset_env.init_state, expected=AssertionError)
    fresh = dict(task_base, algorithm_variant='A1_RAW35_FRESH', resume_bptt=None,
        microtrain=dict(schema=q.SCHEMA, target_verified_increment=2, source_final=None))
    fresh = q.validate_microtrain_entry(fresh)
    reject('fresh declaration spliced with restored nonzero counters', 'q.start_microtrain_segment actual nine-counter baseline',
        lambda: q.start_microtrain_segment(fresh, source_counts))
    wrong_receipt = copy.deepcopy(load_receipt)
    wrong_receipt['byte_cache']['physical_byte_opens'] = 2
    reject('multiple checkpoint opens in resume record', 'q.start_microtrain_segment receipt-consistency layer; not a file-open interception',
        lambda: q.start_microtrain_segment(task, source_counts, resume_receipt=wrong_receipt))
    zeroed = q.zero_counts()
    reject('actual loaded counter replaced by fresh zero', 'q.start_microtrain_segment no offset/fresh-count splicing',
        lambda: q.start_microtrain_segment(task, zeroed, resume_receipt=load_receipt))
    bad_teacher_learner, _, bad_teacher, teacher_expected = make_learner('ISOLATED_BAD_TEACHER_NOT_ADMITTED')
    bad_teacher_payload = copy.deepcopy(root_values)
    bad_teacher_payload['pi']['teacher.synthetic_frozen_buffer'].add_(1.)
    q.validate_microtrain_payload(bad_teacher_payload, task)
    base.load_decoded_full_checkpoint_once(bad_teacher_learner,
        types.SimpleNamespace(payload=bad_teacher_payload, receipt=pinned.receipt), task, layout)
    reject('actual decoded teacher buffer changed despite correct metadata',
        'CPU actual teacher tensor comparison equivalent to original worker guard, NOT q metadata shape/provenance gate',
        lambda: teacher_guard(bad_teacher, teacher_expected), expected=AssertionError)
    assert not torch.cuda.is_initialized()
    forbidden = [name for name in sys.modules if name == 'isaaclab' or name.startswith(('isaaclab.', 'isaacsim', 'omni.'))]
    assert not forbidden, forbidden
    result['negative_cases'] = negatives
    result['negative_case_count'] = len(negatives)
    result['CUDA_initialized'] = False
    result['whole_CPU_source_strict_check_passed'] = retained_guard['values_unchanged'] and retained_guard['tensor_identity_versions_unchanged']
    result['counter_3_to_5_actual_path_passed'] = True
    result['passed'] = result['whole_CPU_source_strict_check_passed']
    if not result['passed']:
        result['strict_failures'] = ['retained decoded whole CPU source changed through original full-loader/training path; raw bytes staying equal is not a substitute']
        result['erratum_scope'] = 'OBSERVED_CPU_SOURCE_ALIASING_ONLY; sealed inputs unchanged; no automatic repair or acceptance downgrade'
    result['validations_not_claimed'] = ['native owner/worker execution or admission', 'SDK/CUDA/PhysX/noisy sensor or 100Hz evidence',
        'original selected/bootstrap PT byte loading', 'App.close/cost/resource wait proof', 'skill pass-rate or 50/300 quality threshold',
        'bitwise trajectory continuation', 'shape-loader transactional rollback', 'native reset interception from metadata flags']
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--vendor-parent', type=Path, required=True)
    parser.add_argument('--dependency-path', type=Path, action='append', default=[])
    for name in PINS:
        parser.add_argument('--' + name.replace('_', '-'), type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=False)
    result = dict(kind=REPORT_KIND, evidence_purpose=REPORT_PURPOSE, passed=False, only_new_synthetic_checkpoints=True,
        original_selected_PT_reads=0, native_expert_BPTT_updates_counted=0,
        owner_worker_SDK_C_GO_locks_Git_operations=0, actual_training_implemented_or_enabled=False,
        A1_LEGACY_ONLY=True, bound_H32_reward_command_changes=False)
    receipt = output / 'QUALITY_MICROTRAIN_TORCH_CPU_RECEIPT_V3.json'
    try:
        run(args, output, result)
    except BaseException:
        result.update(passed=False, unhandled_error=traceback.format_exc(), actual_inputs={k:str(v) for k,v in vars(args).items()})
        write_json_once(receipt, result)
        raise
    write_json_once(receipt, result)
    print(json.dumps(result, indent=2, allow_nan=False))
    if not result['passed']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
