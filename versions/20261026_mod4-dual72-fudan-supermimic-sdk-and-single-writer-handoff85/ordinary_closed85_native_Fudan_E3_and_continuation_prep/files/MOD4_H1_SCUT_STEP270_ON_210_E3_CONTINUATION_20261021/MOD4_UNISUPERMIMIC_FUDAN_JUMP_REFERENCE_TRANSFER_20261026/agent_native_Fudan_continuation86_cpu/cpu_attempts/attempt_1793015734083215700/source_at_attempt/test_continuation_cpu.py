"""Tiny tensor/metadata fixtures only: no PT, actor, optimizer step or env."""
from pathlib import Path
from copy import deepcopy
import ast
import hashlib
import importlib.util
import json
import math
import sys
import time
import traceback
import types
from dataclasses import dataclass
from types import SimpleNamespace

import torch
import native_continuation_v1 as c

HERE = Path(__file__).resolve().parent


def load_source(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


finalizer = load_source('frozen_native_finalization_fixture_only', HERE / 'source_snapshots/installed85_finalization.py')
replay_source = load_source('frozen_replay_fixture_only', HERE / 'source_snapshots/installed85_replay.py')
learner_ast = ast.parse((HERE / 'source_snapshots/installed85_learner.py').read_text('utf8'))
config_ast = next(x for x in learner_ast.body if isinstance(x, ast.ClassDef) and x.name == 'SuperMimicConfig')
scope = dict(dataclass=dataclass)
exec(compile(ast.Module(body=[config_ast], type_ignores=[]), '<real_config_AST>', 'exec'), scope)
Config = scope['SuperMimicConfig']


class Slot:
    def __init__(self, value):
        self.value = deepcopy(value)
        self.loads = 0
        self.fail = False

    @property
    def param_groups(self):
        return self.value['param_groups']

    def state_dict(self):
        return deepcopy(self.value)

    def load_state_dict(self, value, strict=None):
        self.loads += 1
        if self.fail:
            raise RuntimeError('SYNTHETIC_LOADER_FAILURE_NO_RETRY')
        self.value = deepcopy(value)


def fixture():
    cfg = Config(iterations=14, buffer_steps=8, hist=3, wm_window=2,
                 warmup_steps=5, wm_only_iters=10, wm_batches=2, compile=False,
                 utd=1 / 24, log_every=1, ckpt_every=1000000, log_backend='none')
    import dataclasses
    opt = dict(state={0: dict(step=torch.tensor(23.), exp_avg=torch.tensor([.7]), exp_avg_sq=torch.tensor([.9]))},
               param_groups=[dict(params=[0], lr=cfg.lr)])
    native = dict(wm={'weight': torch.tensor([1.25])}, pi={'weight': torch.tensor([2.5])},
                  critic={'weight': torch.tensor([3.75])}, opt_wm=deepcopy(opt),
                  opt_pi=deepcopy(opt), opt_v=deepcopy(opt), iteration=12,
                  wall_time=18., sim_steps=50, args=dataclasses.asdict(cfg), saved_at='SYNTHETIC')
    learner = SimpleNamespace(cfg=cfg, device=torch.device('cpu'), iteration=0, wall_time=0., sim_steps=0,
                              obs_hist=torch.zeros(2, 3, 4),
                              buffer=SimpleNamespace(ptr=0, size=0))
    for name in c.MODULES:
        setattr(learner, name, Slot({'weight': torch.tensor([0.])}))
    for name in c.OPTIMIZERS:
        setattr(learner, name, Slot(dict(state={}, param_groups=[dict(params=[0], lr=cfg.lr)])))
    bridge = SimpleNamespace(ep_step=torch.zeros(2, dtype=torch.int32), state='fresh_lazy_state',
                             wm_updates=0, pi_updates=0)
    objective = dict(schema=c.OBJECTIVE_SCHEMA, provider_execution_scope='runtime_actual_SDK_named_mapping_required', reference_metadata=dict(sdk_joint_order_verified=True), synthetic_fixture_only=True)
    objective_sha = hashlib.sha256((c.canonical(objective) + '\n').encode()).hexdigest()
    producer = {key: str(i) * 64 for i, key in enumerate(c.PRODUCER_KEYS, 1)}
    producer.update(bootstrap_task_source_SHA=c.BOOTSTRAP_SHA, reference_artifact_SHA=c.REFERENCE_SHA, runtime_objective_contract_SHA=objective_sha)
    publication = dict(path='SYNTHETIC_NOT_A_REAL_PT', SHA='a' * 64,
        verified_new_publication=True, original_full_save_chain_returned=True,
        updates=12, world_updates=120, policy_updates=2,
        run_token='SYNTHETIC_RUN_TOKEN', save_token='SYNTHETIC_SAVE_TOKEN', producer=producer)
    final = dict(passed=True, trace_persisted=True, primary_error=None, secondary_errors=[], final=publication)
    order = dict(actual_runtime_order_readback=True, complete_named_permutation=True,
                 before_first_physical_step_and_Pi=True,
                 actual_robot_joint_names=['fixture_joint_%02d' % i for i in range(30)],
                 reference_artifact_SHA=c.REFERENCE_SHA,
                 runtime_objective_contract_SHA=objective_sha, original_run_id='SYNTHETIC_85M2')
    cpu = dict(passed=True, all_owner_nodes_children_actual_out=True,
               native_method=dict(present=True, native_fullstate_CPU_verified=True,
                                  bootstrap_frozen_Adam829700=True, final=dict(SHA='a' * 64), producer=producer))
    terminal = dict(returncode=0, original_error=False, errors=[], final=final)
    collector = dict(actual_finite_transport_returned=True, original_canonical_cost_settled=True,
        authority72=dict(all_authority72_owner_children_actual_out=True,
            cohort=dict(original_cost_settled=True, rows=dict(e2=terminal)),
            owner_exit=dict(original_cost_settled=True),
            original_locks=[dict(actual_fcntl_free=True), dict(actual_fcntl_free=True)],
            original_segment=dict(experts=dict(e2=dict(duration_bound_passed=True, charged_seconds=123.)))))
    binding = dict(schema='mod4.native.continuation_source_binding.v1', status='ACTUAL_CLOSED_CPU_QUALIFIED',
        source_namespace='H1_STEP270_DUAL72_FUDAN_SUPERMIMIC_E3_MIGRATED_V85M2_20261026',
        checkpoint_SHA='a' * 64, FINAL_metadata_SHA='b' * 64,
        full_CPU_report_SHA='c' * 64, collector_report_SHA='d' * 64,
        producer=producer, source_run_id='SYNTHETIC_85M2')
    expected = dict(version=1, run_token=publication['run_token'], save_token=publication['save_token'],
                    producer=producer, native_iteration=12, history_shape=[2, 3, 4], episode_step_shape=[2],
                    world_updates=120, policy_updates=2)
    ck = {key: dict(synthetic_original_chain=True) for key in finalizer.REQUIRED_ORIGINAL_GROUPS}
    ck.update(UniSuperMimic_H1_test=native,
              UniSuperMimic_obs_history=torch.full((2, 3, 4), 77.),
              UniSuperMimic_bridge_ep_step=torch.tensor([31, 54], dtype=torch.int32),
              UniSuperMimic_test_contract=deepcopy(finalizer.NATIVE_CONTRACT),
              UniSuperMimic_publication=expected)
    proof = dict(source_SHA='a' * 64, new_physical_episode_zeroes_goal_credit=True,
                 not_PhysX_exact_resume=True, complete_D0_D7_original_proof=dict(new_physical_episode=True))
    return SimpleNamespace(**locals())


def admit(f):
    return c.admit_closed_source(f.binding, f.final, f.cpu, f.collector, f.order, deepcopy(f.order), f.objective)


def restored(f):
    return c.restore_legacy85_new_episode(f.ck, f.learner, f.bridge, admit(f), f.proof, finalizer.verify_native)


def expect_error(fn, kind=c.ContinuationError):
    try:
        fn()
    except kind:
        return
    raise AssertionError('Required rejection did not occur')


def test_full_native_state_and_new_episode():
    f = fixture()
    old = deepcopy(f.ck)
    receipt = restored(f)
    assert all(c.exact(getattr(f.learner, n).state_dict(), f.native[n]) for n in c.MODULES + c.OPTIMIZERS)
    assert f.learner.iteration == 12 and f.learner.sim_steps == 50 and f.learner.wall_time == 18.
    assert (f.bridge.wm_updates, f.bridge.pi_updates) == (120, 2)
    assert not f.learner.obs_hist.any() and not f.bridge.ep_step.any() and f.bridge.state is None
    assert c.exact(f.ck, old) and receipt['replay_restored'] is False


def test_pending_false_prefix_and_unsettled_reject():
    mutations = [lambda f: f.binding.update(status='PENDING_ACTUAL_FINAL'),
                 lambda f: f.final.update(passed=False),
                 lambda f: f.final['final'].update(verified_new_publication=False),
                 lambda f: f.cpu['native_method'].update(present=False),
                 lambda f: f.collector.update(original_canonical_cost_settled=False),
                 lambda f: f.collector['authority72'].update(all_authority72_owner_children_actual_out=False),
                 lambda f: f.final.update(primary_error=dict(error='SYNTHETIC_ORIGINAL_ERROR'))]
    for mutate in mutations:
        f = fixture(); mutate(f)
        expect_error(lambda: admit(f))


def test_runtime_actual_order_and_objective():
    f = fixture(); changed = deepcopy(f.order)
    changed['actual_robot_joint_names'][0:2] = reversed(changed['actual_robot_joint_names'][0:2])
    expect_error(lambda: c.admit_closed_source(f.binding, f.final, f.cpu, f.collector, f.order, changed, f.objective))
    f = fixture(); f.objective['reference_metadata']['sdk_joint_order_verified'] = False
    expect_error(lambda: admit(f))
    f = fixture(); f.objective['synthetic_extra_change'] = True
    expect_error(lambda: admit(f))


def test_schema_config_and_finite_reject_before_mutation():
    for mutate in (lambda f: f.native['wm'].update(weight=torch.ones(2)),
                   lambda f: f.native['args'].update(wm_only_iters=0),
                   lambda f: f.native['opt_pi'].update(state={}),
                   lambda f: f.native['wm'].update(weight=torch.tensor([float('nan')]))):
        f = fixture(); mutate(f)
        expect_error(lambda: restored(f), (c.ContinuationError, finalizer.PublicationError))
        assert sum(getattr(f.learner, n).loads for n in c.MODULES + c.OPTIMIZERS) == 0


def test_original_new_episode_and_loader_errors_fatal():
    f = fixture(); f.proof['new_physical_episode_zeroes_goal_credit'] = False
    expect_error(lambda: restored(f))
    f = fixture(); f.learner.opt_pi.fail = True
    expect_error(lambda: restored(f), RuntimeError)
    assert f.learner.iteration == 0  # no pretend complete restore or training fallback


def test_constructor_preserves_physical_global_rng_on_success_and_error():
    saved = torch.random.get_rng_state().clone()
    try:
        torch.manual_seed(123); post_reset = torch.random.get_rng_state().clone()
        expected = torch.rand(3); torch.random.set_rng_state(post_reset)
        def factory():
            torch.manual_seed(987); torch.rand(4)
            return 'SYNTHETIC_CONSTRUCTOR_NO_MODEL'
        assert c.construct_preserving_post_reset_global_rng(factory, torch.random.get_rng_state, torch.random.set_rng_state) == 'SYNTHETIC_CONSTRUCTOR_NO_MODEL'
        assert torch.equal(torch.rand(3), expected)
        torch.random.set_rng_state(post_reset)
        def failed():
            torch.manual_seed(987)
            raise RuntimeError('SYNTHETIC_CONSTRUCTOR_ERROR')
        expect_error(lambda: c.construct_preserving_post_reset_global_rng(failed, torch.random.get_rng_state, torch.random.set_rng_state), RuntimeError)
        assert torch.equal(torch.random.get_rng_state(), post_reset)
    finally:
        torch.random.set_rng_state(saved)


def test_cumulative_phase_and_fresh_replay_real_train_AST():
    f = fixture(); restored(f)
    class Logger:
        def __init__(self, *args, **kwargs): pass
        def __getattr__(self, name): return lambda *args, **kwargs: None
    globals_ = dict(torch=torch, Path=Path, time=time, math=math, SuperMimicLogger=Logger,
                    _empty_stats=lambda: {'r': [], 'ep_len': [], 'ep_ret': [], 'term': [], 'done': []})
    globals_['_LOG_FIELDS'] = ast.literal_eval(next(
        x.value for x in learner_ast.body if isinstance(x, ast.Assign)
        and any(isinstance(y, ast.Name) and y.id == '_LOG_FIELDS' for y in x.targets)))
    cls = next(x for x in learner_ast.body if isinstance(x, ast.ClassDef) and x.name == 'SuperMimicLearner')
    methods = [x for x in cls.body if isinstance(x, ast.FunctionDef) and x.name in ('train', 'lr_at', '_mean')]
    exec(compile(ast.Module(body=methods, type_ignores=[]), '<real_train_phase_AST>', 'exec'), globals_)
    learner = f.learner
    learner.train = types.MethodType(globals_['train'], learner)
    learner.lr_at = types.MethodType(globals_['lr_at'], learner)
    learner._mean = globals_['_mean']
    learner.backend = 'SYNTHETIC_CPU_CONTROL_FLOW_ONLY'; learner.env = SimpleNamespace(num_envs=2)
    learner.log_dir = ATTEMPT / 'synthetic_train_csv'; learner.log_dir.mkdir()
    learner.collect_calls = []; learner.saved_calls = []
    def collect(steps):
        learner.collect_calls.append(steps)
        learner.buffer.size = min(learner.cfg.buffer_steps, learner.buffer.size + steps)
        learner.sim_steps += 2 * steps
    def wm():
        f.bridge.wm_updates += 1
        return torch.tensor(0.), torch.tensor(0.)
    def pi():
        f.bridge.pi_updates += 1
        return tuple(torch.tensor(0.) for _ in range(5))
    learner.collect = collect; learner.wm_update = wm; learner.policy_update = pi
    learner.save = lambda *a, **k: learner.saved_calls.append((a, k)) or Path('SYNTHETIC_NO_PT_WRITTEN')
    result = learner.train()
    assert learner.collect_calls == [5, 24, 24]
    assert learner.iteration == 14 and (f.bridge.wm_updates, f.bridge.pi_updates) == (124, 4)
    assert learner.sim_steps == 156 and result['completed'] is True
    assert all(getattr(learner, name).loads == 1 for name in c.OPTIMIZERS)


def test_no_old_positive_Pi_as_new_window_success():
    f = fixture(); receipt = restored(f); saved = []
    write = c.continuation_manifest_writer(lambda p, value: saved.append(deepcopy(value)), f.bridge, receipt)
    old_positive = dict(passed=True)
    write('SYNTHETIC_FINAL', old_positive)
    assert old_positive['passed'] is False
    f.bridge.wm_updates += 10; f.bridge.pi_updates += 1
    new_positive = dict(passed=True)
    write('SYNTHETIC_FINAL', new_positive)
    assert new_positive['passed'] is True and new_positive['native_continuation']['window_progress']['policy_updates'] == 1


def test_future_replay_snapshot_ring_and_boundary_mask():
    f = fixture()
    f.learner.buffer = replay_source.ReplayBuffer(4, 2, 'cpu', num_joints=1, context_dim=1, action_dim=1)
    b = f.learner.buffer
    for age in range(6):
        transition = {k: torch.full_like(v[0], age) for k, v in b.data.items()}
        transition['done'].zero_(); b.add(transition)
    extension = c.snapshot_replay_extension_candidate(f.learner, f.bridge, dict(cpu=torch.random.get_rng_state()))
    assert extension['replay']['ptr'] == 2 and extension['replay']['size'] == 4
    assert c.exact(extension['replay']['data'], b.data)
    before = extension['replay']['data']['s'].clone(); b.data['s'].zero_()
    assert torch.equal(extension['replay']['data']['s'], before)  # no live alias
    ep = torch.tensor([[4, 5, 0, 1], [0, 1, 2, 3]])
    original = torch.ones(2, 4)
    assert torch.equal(c.mask_episode_restart_windows(original, ep), torch.tensor([[1., 1., 0., 0.], [1., 1., 1., 1.]]))
    assert original.eq(1).all()  # no fabricated environment done or data rewrite
    assert extension['integration_status'].startswith('UNWIRED_')


def main():
    global ATTEMPT
    attempt_id = 'attempt_' + str(time.time_ns())
    ATTEMPT = HERE / 'cpu_attempts' / attempt_id
    ATTEMPT.mkdir(parents=True, exist_ok=False)
    snapshots = ATTEMPT / 'source_at_attempt'; snapshots.mkdir()
    for path in (HERE / 'native_continuation_v1.py', Path(__file__), HERE / 'h1_supermimic_bridge_continuation86_candidate.py'):
        (snapshots / path.name).write_bytes(path.read_bytes())
    tests = [value for key, value in globals().items() if key.startswith('test_') and callable(value)]
    rows = []
    for test in tests:
        try:
            test(); rows.append(dict(test=test.__name__, passed=True))
        except BaseException as error:
            rows.append(dict(test=test.__name__, passed=False, error=str(error), traceback=traceback.format_exc()))
    report = dict(epoch=time.time(), attempt_id=attempt_id, passed=all(r['passed'] for r in rows),
                  passed_count=sum(r['passed'] for r in rows), count=len(rows), tests=rows,
                  synthetic_tensors_and_metadata_only=True, real_upstream_train_AST_control_flow=True,
                  no_PT_NPZ_model_environment_optimizer_training_GPU_remote_Git_or_budget_action=True,
                  actual_native_source_admitted=False, actual_closure_pending=True,
                  source_pins=[dict(path=str(p), bytes=p.stat().st_size, SHA256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in snapshots.iterdir()],
                  Git_status='LOCAL_PENDING_ROOT_PHASE_ARCHIVE')
    path = ATTEMPT / 'TINY_NATIVE_CONTINUATION_CPU_TESTS_ACTUAL.json'
    path.write_text(json.dumps(report, indent=2) + '\n', 'utf8')
    print(json.dumps(dict(report=str(path), passed=report['passed'], passed_count=report['passed_count'], count=len(rows))))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    sys.exit(main())
