"""STDLIB AST/MOCK ONLY. No real model/torch/SDK/GPU/canonical/SSH call.

Mock counters/tensors/queues test the source contract, never physical or skill
qualification. All artifact-like paths in the original bounded-stop mock are
virtual PurePosixPath wrappers with IN-MEMORY writes and replace recording.
"""
from pathlib import Path, PurePosixPath
import ast
import builtins
import copy
import hashlib
import json
import os
import sys
import traceback
import types

B = Path(__file__).resolve().parent
sys.path.insert(0, str(B))
original_import = builtins.__import__
BLOCKED = ('torch', 'isaaclab', 'isaacsim', 'omni', 'pxr', 'rsl_rl', 'paramiko', 'project_connector')

def no_external_import(name, *args, **kwargs):
    if any(name == n or name.startswith(n + '.') for n in BLOCKED):
        raise AssertionError('AST/MOCK test forbids real external import: ' + name)
    return original_import(name, *args, **kwargs)

builtins.__import__ = no_external_import
from posttrain_fullstate_common_v1 import (EXPERTS, POSTTRAIN_KIND, FiniteWindow, FiniteStop,
    merge_preserving_omitted, omitted_paths, get_path, validate_parent_join, assert_live_saved, LIVE_KEYS)

RESULTS = []


def check(name, fn):
    try:
        detail = fn()
        RESULTS.append(dict(name=name, passed=True, detail=detail))
    except BaseException:
        RESULTS.append(dict(name=name, passed=False, error=traceback.format_exc()))


def must_raise(exc, fn):
    try:
        fn()
    except exc:
        return
    raise AssertionError('Expected ' + exc.__name__)


def ast_check():
    names = ['posttrain_fullstate_common_v1.py', 'build_source_handoff_v1.py', 'check_ast_mock_v1.py', 'construct_source_task_go_v1.py'] + [
        'worker_posttrain_' + r.lower() + '_v1.py' for r in EXPERTS]
    trees = {}
    for name in names:
        raw = (B / name).read_bytes()
        tree = ast.parse(raw.decode('utf-8-sig'), filename=name)
        compile(tree, name, 'exec')  # compile only, no entry-point execution
        trees[name] = tree
    tree = trees['posttrain_fullstate_common_v1.py']
    top_imports = [n for n in tree.body if isinstance(n, (ast.Import, ast.ImportFrom))]
    imports = [alias.name for n in top_imports if isinstance(n, ast.Import) for alias in n.names]
    assert not any(any(s == b or s.startswith(b + '.') for b in BLOCKED) for s in imports)
    calls = [ast.unparse(n.func) for n in ast.walk(tree) if isinstance(n, ast.Call)]
    assert 'original_bounded_learn' in calls and 'runner.learn' not in calls
    assert not any(s in calls for s in ('subprocess.run', 'subprocess.Popen', 'os.system', 'torch.optim.Adam'))
    assert not any(s.endswith(('.backward', '.set_rng_state', '.manual_seed')) for s in calls)
    assert not any(isinstance(n, ast.Constant) and n.value == '100000' for n in ast.walk(tree))
    # Core fields are inspected, not back-filled by computed values at save.
    for n in ast.walk(tree):
        if isinstance(n, (ast.Assign, ast.AnnAssign)):
            targets = n.targets if isinstance(n, ast.Assign) else [n.target]
            for t in targets:
                if isinstance(t, ast.Subscript) and isinstance(t.slice, ast.Constant):
                    assert t.slice.value not in ('iter', 'optimizer_state_dict', 'actor_state_dict', 'critic_state_dict')
                if isinstance(t, ast.Attribute):
                    assert t.attr not in ('learning_rate', 'std_param', 'log_std_param')
    assert set(EXPERTS) == {'E0', 'E2', 'E3'}
    return dict(parsed_files=names, imports_are_stdlib_only=True, source_only=True,
                original_bounded_learn_called=True, no_manual_core_state_backfill=True, real_SDK_validation=False)


def merge_test():
    source = dict(actor_state_dict=dict(weight=[1, 2], unknown_normalizer=dict(count=123, mean=[3, 4])),
                  optimizer_state_dict=dict(state={0: dict(step=10, strange_slot=[5, 6])}, param_groups=[dict(lr=.001)]),
                  sensor_DR_state=dict(cache=dict(leg=([1, 1], [[4], [5]])), noise_rng=dict(leg=[8, 9])),
                  opaque_root=dict(blob=[10, 11], nested=dict(keep='UNCHANGED')), root_tuple=(2, 3))
    live = dict(actor_state_dict=dict(weight=[2, 3]), optimizer_state_dict=dict(state={0: dict(step=30)}, param_groups=[dict(lr=.0005)]),
                sensor_DR_state=dict(cache=dict(leg=([2, 2], [[6], [7]])), noise_rng=dict(leg=[9, 10])))
    before, live_before = copy.deepcopy(source), copy.deepcopy(live)
    result = merge_preserving_omitted(source, live)
    assert source == before and live == live_before
    assert result['actor_state_dict']['weight'] == [2, 3]
    assert result['actor_state_dict']['unknown_normalizer'] == source['actor_state_dict']['unknown_normalizer']
    assert result['optimizer_state_dict']['state'][0]['step'] == 30
    assert result['optimizer_state_dict']['state'][0]['strange_slot'] == [5, 6]
    assert result['sensor_DR_state'] == live['sensor_DR_state']  # live histories win, not stale source queues
    for p, value in omitted_paths(source, live):
        assert get_path(result, p) == value
    return dict(source_unchanged=True, live_unchanged=True, live_caches_override_source=True,
                omitted_root_and_nested_fields_retained=True, list_tuple_atomic_not_sliced=True)


def counters_test():
    cases = []
    for cap in (1, 3, 20):
        w = FiniteWindow(cap, 1000, lambda: False, clock=lambda: 0)
        for _ in range(cap):
            w.controls += 24
            w.before_update()
            for _ in range(20):
                w.optimizer_step_returned()
            w.update_returned()
        assert w.reason() == 'MAX_ADDITIONAL_UPDATES'
        must_raise(FiniteStop, w.before_update)
        assert w.completed == cap and w.optimizer_steps == 20 * cap
        cases.append(w.receipt())
    for cap in (0, -1, 21, 100000, True, 20.0):
        must_raise(ValueError, lambda cap=cap: FiniteWindow(cap, 1000, lambda: False))
    bad = FiniteWindow(20, 1000, lambda: False, clock=lambda: 0)
    must_raise(ValueError, bad.optimizer_step_returned)
    bad.before_update()
    for _ in range(19):
        bad.optimizer_step_returned()
    must_raise(ValueError, bad.update_returned)
    stop = FiniteWindow(20, 1, lambda: False, clock=lambda: 2)
    assert stop.reason() == 'ORIGINAL_OWNER_SAVE_DEADLINE'
    stop = FiniteWindow(20, 1000, lambda: True, clock=lambda: 0)
    assert stop.reason() == 'ORIGINAL_OWNER_OR_HEALTH_SAVE_STOP'
    return dict(valid_caps=cases, invalid_caps_and_bad_step_count_rejected=True, cap21_never_entered=True,
                zero_optimizer_calls_in_real_world=True)


def parent_join_test():
    cases = []
    for role, cfg in EXPERTS.items():
        desc = json.loads((B / (role + '_POSTTRAIN_DESCRIPTOR_SOURCE_ONLY_V1.json')).read_bytes())
        task = dict(cfg, kind=cfg['original_kind'], posttrain_kind=POSTTRAIN_KIND,
                    source_read_purpose_label='NEW_POSTTRAIN_' + role + '_MOCK_ONLY',
                    max_additional_updates=20, num_envs=20000, seed=20260928, steps_per_env=24, exit_headroom_seconds=300)
        go = dict(posttrain_kind=POSTTRAIN_KIND, max_additional_updates=20, num_envs=20000, seed=20260928, steps_per_env=24,
                  original_owner_pid=os.getppid(), save_deadline=10, nominal_end_epoch=310)
        validate_parent_join(role, task, go, desc, 0)
        for change in ({'num_envs': 80}, {'max_additional_updates': 100000}, {'source_LR': .0001},
                       {'source_read_purpose_label': 'OLD_N80_SCOPE'}):
            mutated = dict(task, **change)
            must_raise(ValueError, lambda: validate_parent_join(role, mutated, go, desc, 0))
        must_raise(ValueError, lambda: validate_parent_join(role, task, go, desc, 11))
        bad = dict(desc, status='ACTUAL_SDK_READY')
        must_raise(ValueError, lambda: validate_parent_join(role, task, go, bad, 0))
        cases.append(role)
    must_raise(ValueError, lambda: validate_parent_join('H1', {}, {}, {}, 0))
    return dict(in_memory_mock_only=True, roles=cases, no_Task_GO_admission_or_Ready_file_created=True,
                N80_H1_unbounded_stale_source_or_ready_rejected=True)


class MockTensor:
    def __init__(self, value): self.value = value
    def cpu(self): return self
    def __eq__(self, other): return isinstance(other, MockTensor) and self.value == other.value


class MockState:
    def __init__(self, value): self.value = value
    def state_dict(self): return copy.deepcopy(self.value)


class MockRNG:
    def __init__(self, value): self.value = MockTensor(value)
    def get_state(self): return self.value


def live_saved_contract_test():
    # Explicit in-memory stubs, not SDK class imports or simulation.
    mocks = {
        'feedback_delay_runtime': types.SimpleNamespace(delay_state=lambda env: env.mock_delay),
        'chassis_pd_checkpoint': types.SimpleNamespace(current_state=lambda env: env.mock_chassis),
        'e2_command_checkpoint_v1': types.SimpleNamespace(current=lambda term: term.mock_state),
        'e3_fullstate_checkpoint_v1': types.SimpleNamespace(state=lambda env: env.mock_e3),
    }
    previous = {key: sys.modules.get(key) for key in mocks}
    sys.modules.update(mocks)
    try:
        cases = []
        for role, cfg in EXPERTS.items():
            completed = 3
            alg = types.SimpleNamespace(actor=MockState(dict(weight=MockTensor('ACTOR_MOCK'))),
                critic=MockState(dict(weight=MockTensor('CRITIC_MOCK'))),
                optimizer=MockState(dict(state={i: dict(step=cfg['source_Adam_step'] + 20 * completed) for i in range(17)},
                    param_groups=[dict(lr=cfg['source_LR'])])), learning_rate=cfg['source_LR'])
            runner = types.SimpleNamespace(alg=alg)
            term = types.SimpleNamespace(mode=MockRNG('CMD_MOCK'), mock_state=dict(nine_fields='MOCK', rng='MOCK'))
            env = types.SimpleNamespace(_sensor_mild=MockState(dict(cache=dict(leg=MockTensor('LIVE20KSHAPE_MOCK')), bias_rng='MOCK')),
                mock_delay=MockState(dict(delay=MockTensor('0_OR_1_MOCK'), cache=dict(history=MockTensor('LIVE_FEEDBACK')))),
                _physics_action_delay=MockState(dict(groups=dict(legs='LIVE4COL_MOCK', wheels='LIVE2COL_MOCK'))),
                _spring_pressure=MockState(dict(rng='SPRING_LIVE')), _gas_damping=MockState(dict(rng='GAS_LIVE')),
                mock_chassis=dict(COM='LIVE_COM_MOCK', PD='LIVE_PD_MOCK'),
                _mild_dr=types.SimpleNamespace(physical=MockRNG('PHYS_MOCK')),
                command_manager=types.SimpleNamespace(get_term=lambda name: term),
                mock_e3=dict(phase='LIVE7FIELD_MOCK', command='LIVE_RNG'), e3_reset_receipt=dict(pick=34))
            torch = types.SimpleNamespace(equal=lambda a, b: a == b,
                random=types.SimpleNamespace(get_rng_state=lambda: MockTensor('GLOBAL_CPU')),
                cuda=types.SimpleNamespace(get_rng_state_all=lambda: [MockTensor('GLOBAL_CUDA')]))
            value = dict.fromkeys(LIVE_KEYS)
            value.update(actor_state_dict=alg.actor.state_dict(), critic_state_dict=alg.critic.state_dict(),
                optimizer_state_dict=alg.optimizer.state_dict(), iter=cfg['source_iteration'] + completed,
                sensor_DR_state=env._sensor_mild.state_dict(), feedback_delay_state=env.mock_delay.state_dict(),
                physical_action_delay_state=env._physics_action_delay.state_dict(),
                spring_pressure_state=env._spring_pressure.state_dict(), gas_damping_state=env._gas_damping.state_dict(),
                chassis_PD_state=env.mock_chassis, sensor_command_DR_rng_state=dict(mode=term.mode.get_state()),
                sensor_physical_DR_rng_state=dict(physical=env._mild_dr.physical.get_state()),
                sensor_global_rng_state=dict(cpu=MockTensor('GLOBAL_CPU'), cuda=[MockTensor('GLOBAL_CUDA')]))
            if role == 'E2': value['E2_moving4_command_state'] = term.mock_state
            if role == 'E3': value.update(E3_public_recovery_state=env.mock_e3, E3_reset_contract=env.e3_reset_receipt)
            exact = lambda a, b: a == b
            assert_live_saved(torch, exact, value, runner, env, role, cfg, completed)
            for key in ('sensor_DR_state', 'feedback_delay_state', 'physical_action_delay_state', 'chassis_PD_state'):
                bad = copy.deepcopy(value)
                bad[key] = {'STALE_SOURCE_NOT_LIVE': True}
                must_raise(ValueError, lambda bad=bad: assert_live_saved(torch, exact, bad, runner, env, role, cfg, completed))
            bad = copy.deepcopy(value)
            del bad['optimizer_state_dict']
            must_raise(ValueError, lambda: assert_live_saved(torch, exact, bad, runner, env, role, cfg, completed))
            bad = copy.deepcopy(value)
            bad['iter'] -= 1
            must_raise(ValueError, lambda: assert_live_saved(torch, exact, bad, runner, env, role, cfg, completed))
            bad = copy.deepcopy(value)
            bad['optimizer_state_dict']['state'][0]['step'] += 1
            must_raise(ValueError, lambda: assert_live_saved(torch, exact, bad, runner, env, role, cfg, completed))
            cases.append(role)
        return dict(mock_roles=cases, stale_or_missing_live_core_caches_and_wrong_counters_rejected=True,
                    no_real_tensor_model_SDK_or_optimizer=True)
    finally:
        for key, old in previous.items():
            if old is None: sys.modules.pop(key, None)
            else: sys.modules[key] = old


class VirtualPath:
    writes = {}
    existing = set()
    def __init__(self, path): self.path = PurePosixPath(str(path))
    def __str__(self): return str(self.path)
    def __truediv__(self, other): return VirtualPath(self.path / str(other))
    @property
    def suffix(self): return self.path.suffix
    def with_suffix(self, suffix): return VirtualPath(self.path.with_suffix(suffix))
    def write_text(self, value, **kwargs): self.writes[str(self.path)] = value
    def exists(self): return str(self.path) in self.existing


def original_bounded_mock_test():
    api = json.loads((B / 'SOURCE_API_AND_ACTUAL_PROOF_INDEX_V1.json').read_bytes())
    outcomes = []
    for role in EXPERTS:
        source_path = Path(api['roles'][role]['helper_API']['rescue_training.py']['path'])
        raw = source_path.read_text(encoding='utf-8-sig')
        module = types.ModuleType('MOCK_ONLY_original_rescue_' + role)
        exec(compile(ast.parse(raw), str(source_path), 'exec'), module.__dict__)
        assert callable(module.install) and callable(module.learn)
        for cap, deadline_after in ((20, None), (20, 3), (1, None)):
            clock = [0.]
            replaces = []
            module.Path = VirtualPath
            module.os = types.SimpleNamespace(environ={'RM_RESCUE_DEADLINE': '10', 'RM_RESCUE_STOP_FILE': '/MOCK_ONLY/STOP.json'},
                replace=lambda a, b: replaces.append((str(a), str(b))), getpid=lambda: 123)
            module.time = types.SimpleNamespace(time=lambda: clock[0])
            window = FiniteWindow(cap, 10, lambda: False, clock=lambda: clock[0])
            flags = dict(init_at_random_ep_len=None, install_seen=False, saves=[], logger_calls=0)
            class FakeRunner:
                current_learning_iteration = 100
                def __init__(self): self.logger = types.SimpleNamespace(log=self.log)
                def log(self, *a, **k): flags['logger_calls'] += 1
                def save(self, path, *a, **k): flags['saves'].append(path)
                def learn(self, *, num_learning_iterations, init_at_random_ep_len):
                    flags['init_at_random_ep_len'] = init_at_random_ep_len
                    flags['install_seen'] = self.save.__func__ is not FakeRunner.save if hasattr(self.save, '__func__') else True
                    for i in range(num_learning_iterations):
                        window.before_update()
                        window.controls += 24
                        for _ in range(20): window.optimizer_step_returned()
                        window.update_returned()
                        self.current_learning_iteration = 101 + i
                        if deadline_after is not None and window.completed == deadline_after:
                            clock[0] = 11.
                        self.logger.log()
                        # Original install save-stop path: save is a VIRTUAL
                        # capture only, never writes/reads/stats any PT artifact.
                        self.save('/MOCK_ONLY/OUTPUT_NOT_A_MODEL.bin')
                        if window.completed == cap: raise FiniteStop('MAX_ADDITIONAL_UPDATES')
            runner = FakeRunner()
            try:
                module.learn(runner, cap, '/MOCK_ONLY_LOGS')
            except FiniteStop:
                pass
            expected = cap if deadline_after is None else deadline_after
            assert flags['init_at_random_ep_len'] is True and flags['install_seen']
            assert window.completed == expected and window.optimizer_steps == 20 * expected
            assert replaces and VirtualPath.writes
            outcomes.append(dict(role=role, max_cap=cap, mock_completed=window.completed,
                                 original_init_at_random_ep_len=True, original_install_called=True,
                                 original_deadline_SaveStop_observed=deadline_after is not None))
    return dict(cases=outcomes, original_source_code_executed_only_against_virtual_mock=True,
                all_mock_files_in_RAM=True, actual_PPO_SDK_GPU_model_calls=0)


def cache_clone_alias_test():
    api = json.loads((B / 'SOURCE_API_AND_ACTUAL_PROOF_INDEX_V1.json').read_bytes())
    records = []
    class FakeMutable:
        def __init__(self, value): self.value = value
        def __eq__(self, other): return isinstance(other, FakeMutable) and self.value == other.value
    for role in EXPERTS:
        source = Path(api['roles'][role]['derived_trainer']['path']).parent / 'source_cache208_v3.py'
        raw = source.read_bytes()
        tree = ast.parse(raw.decode('utf-8-sig'))
        module = types.ModuleType('MOCK_ONLY_source_cache_' + role)
        exec(compile(tree, str(source), 'exec'), module.__dict__)
        # Bypass constructor ENTIRELY: no Path/PT open/stat/hash/decode, including
        # no synthetic-file PT. Execute only actual selected-cache clone routing.
        cache = module.PinnedSource208.__new__(module.PinnedSource208)
        cache.state = dict(optimizer_state_dict=dict(state={i: dict(step=FakeMutable(100)) for i in range(17)}),
            actor_state_dict=dict(norm=FakeMutable([1, 2])), critic_state_dict=dict(norm=FakeMutable([3, 4])),
            unknown_root=dict(history=FakeMutable(['all_whole_rows_not_sliced'])),
            sensor_DR_state=dict(cache=FakeMutable(['sensor_history'])))
        truth = copy.deepcopy(cache.state)
        fallback = []
        original_load = lambda value, *a, **k: fallback.append(value) or {'MOCK_OTHER': True}
        torch = types.SimpleNamespace(load=original_load)
        cache.torch, cache.original_load = torch, original_load
        cache.owns = lambda value: value == 'IN_RAM_SOURCE_SENTINEL'
        cache.logical_cache_loads = 0
        cache.own_or_other_artifact_loads = []
        with module.selected_source(cache):
            with module.runner_source_load_scope():
                working = torch.load('IN_RAM_SOURCE_SENTINEL')
            assert torch.load is original_load
            for i in range(17):
                working['optimizer_state_dict']['state'][i]['step'].value += 1
            working['unknown_root']['history'].value.append('runner_changed_only_its_copy')
            helper = module.cached_load('IN_RAM_SOURCE_SENTINEL')
            helper['sensor_DR_state']['cache'].value.append('helper_changed_only_its_copy')
        assert cache.state == truth and not fallback and cache.logical_cache_loads == 2
        assert set(working) == set(truth) == set(helper)
        classes = [n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'PinnedSource208']
        load = next(n for n in classes[0].body if isinstance(n, ast.FunctionDef) and n.name == 'load')
        scope = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'runner_source_load_scope')
        clone = next(n for n in ast.walk(load) if isinstance(n, ast.Call) and ast.unparse(n.func) == 'copy.deepcopy')
        records.append(dict(role=role, source=str(source), source_bytes=len(raw), source_SHA=hashlib.sha256(raw).hexdigest(),
            load_lines=[load.lineno, load.end_lineno], full_root_deepcopy_line=clone.lineno,
            runner_scope_lines=[scope.lineno, scope.end_lineno],
            mutable_17step_and_unknown_root_alias_isolated=True, physical_source_constructor_calls=0,
            actual_Torch_step_alias_semantics_tested=False, mock_only=True))
    return dict(source_evidence=records, full_root_working_copy_not_truth_passed_to_runner=True,
                DR_helpers_use_same_truth_independent_copies=True, actual_PPO_Torch_SDK=False)


def task_constructor_test():
    from construct_source_task_go_v1 import build_task_go, mock_examples
    required = json.loads((B / 'PARENT_REQUIRED_FIELDS_SOURCE_ONLY_V1.json').read_bytes())
    examples = mock_examples()
    assert not examples['actual_original_owner_admission'] and not examples['published_Task_GO_or_Ready_files']
    rows = []
    for role, ex in examples['roles'].items():
        task, go = ex['task_dictionary'], ex['go_dictionary']
        assert set(required['Task_required']).issubset(task)
        assert set(required['GO_required']).issubset(go)
        assert task['seed'] == go['seed'] == 20260928
        assert task['steps_per_env'] == go['steps_per_env'] == 24
        assert go['original_owner_pid'] == -1 and go['save_deadline'] == 3600
        desc = json.loads((B / (role + '_POSTTRAIN_DESCRIPTOR_SOURCE_ONLY_V1.json')).read_bytes())
        must_raise(ValueError, lambda: validate_parent_join(role, task, go, desc, 1793580000.))
        rows.append(dict(role=role, all_required_fields_present=True, expired_invalid_PID_mock_not_executable=True))
    return dict(rows=rows, pure_stdlib_function=True, no_Task_GO_admission_file_written=True,
                no_budget_admission_or_GPU_check=True)


def main():
    for name, fn in [('AST_source_invariants', ast_check), ('unknown_and_cache_preservation', merge_test),
                     ('finite_update_counter', counters_test), ('parent_source_join_negatives', parent_join_test),
                     ('live_saved_contract_mock', live_saved_contract_test), ('original_bounded_learn_virtual_mock', original_bounded_mock_test),
                     ('source_cache_full_root_mutable_alias_isolation', cache_clone_alias_test), ('complete_source_task_go_constructor', task_constructor_test)]:
        check(name, fn)
    result = dict(kind='STDLIB_AST_MOCK_ONLY_NOT_SDK_NOT_TRAINING', tests=RESULTS,
        all_passed=all(r['passed'] for r in RESULTS), real_model_PT_opens=0, real_model_PT_stats=0,
        real_model_decodes=0, real_torch_imports=0, real_SDK_GPU_calls=0, real_optimizer_steps=0,
        canonical_reads_or_writes=0, SSH_calls=0, new_Task_GO_Ready_files=0, agents_started=0,
        original_sources_edited=False, no_actual_training_or_skill_pass_claim=True)
    with (B / 'AST_MOCK_REVIEW_V2_WITH_CACHE_ALIAS_AND_CONSTRUCTOR.json').open('x', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if not result['all_passed']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
