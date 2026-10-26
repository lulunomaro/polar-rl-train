"""Synthetic/source/small JSON only. Never opens a PT/NPZ or starts an SDK."""
from pathlib import Path
import ast
from copy import deepcopy
from dataclasses import dataclass, asdict
import importlib.util
import json
import os
import sys
import time
import traceback
from types import SimpleNamespace

os.environ['CUDA_VISIBLE_DEVICES'] = ''
D = Path(__file__).resolve().parent
B = D / 'candidate_overlay'
T = D.parent.parent
OLD = T / 'H1_STEP270_DUAL72_FUDAN_SUPERMIMIC_E3_MIGRATED_V85M2_20261026/payloads/e2'
sys.path[:0] = [str(B), str(B / 'source'), str(OLD), str(OLD / 'source')]
import torch
torch.set_num_threads(1)
from native86_source_guard_v1 import *
from native_continuation_v1 import read_pinned_metadata_bundle, admit_closed_source, restore_legacy85_new_episode, exact
from native_finalization_v1 import NATIVE_CONTRACT, verify_native, REQUIRED_ORIGINAL_GROUPS
from h1_step270_fullstate_checkpoint_candidate_uninstalled import validate_new_phase


def main():
    # Fail closed if this harness accidentally starts reading a real binary.
    original_load = torch.load
    def forbidden_load(*a, **k):
        raise AssertionError('Synthetic harness forbids every torch.load')
    torch.load = forbidden_load
    cases = []
    def case(name, fn, rejects=False):
        try:
            fn()
            if rejects:
                raise AssertionError('Negative fixture unexpectedly admitted')
            cases.append(dict(name=name, passed=True, expected_rejection=False))
        except Exception as e:
            if rejects and not (isinstance(e, AssertionError) and str(e) == 'Negative fixture unexpectedly admitted'):
                cases.append(dict(name=name, passed=True, expected_rejection=True,
                                  original_exception_type=type(e).__name__, original_error=str(e)))
            else:
                cases.append(dict(name=name, passed=False, expected_rejection=rejects,
                                  original_exception_type=type(e).__name__, original_error=str(e), traceback=traceback.format_exc()))
    contract = read(B / 'NATIVE86_SOURCE_CONTRACT_ACTUAL.json')
    original = read(B / 'NATIVE85_ORIGINAL_COMPLETE_MANIFEST.json')
    binding, metadata = read_pinned_metadata_bundle(B / 'NATIVE_CONTINUATION_BINDING_ACTUAL.json')
    runtime = read(B / 'native_source_metadata/NATIVE85M2_RUNTIME_OBJECTIVE_CONTRACT_ACTUAL.json')
    def admit(meta=None, bind=None, order=None):
        return admit_closed_source(bind or binding, current_runtime_order=order or metadata['runtime_order'],
            current_runtime_objective=runtime, **(meta or metadata))
    case('actual85_pinned_metadata_as_explicit_same_source_CPU_fixture', admit)
    changed = deepcopy(metadata['runtime_order']); changed['actual_robot_joint_names'].reverse()
    case('fresh30_order_permutation_rejected', lambda: admit(order=changed), True)
    changed_binding = deepcopy(binding); changed_binding['status'] = 'PENDING'
    case('pending_native_closure_rejected', lambda: admit(bind=changed_binding), True)
    changed_meta = deepcopy(metadata); changed_meta['collector']['original_canonical_cost_settled'] = False
    case('unsettled_original85_cost_rejected', lambda: admit(meta=changed_meta), True)
    spec = dict(key='e2', native_continuation=True, source_SHA=NATIVE_SHA,
        source_Adamstep=BOOTSTRAP_ADAM, bootstrap_source_SHA=BOOTSTRAP_SHA, bootstrap_Adam=BOOTSTRAP_ADAM,
        GPU_UUID=GPU, execution_backend=BACKEND, native_continuation_restore_required=True)
    case('typed_native_identity_positive', lambda: validate_identity(spec))
    def dispatcher_AST_prefix():
        before = (OLD / 'closed_production_continuation_CPU_v2.py').read_bytes()
        after = (B / 'closed_production_continuation_CPU_v2.py').read_bytes()
        assert after.startswith(before)
        a, b = ast.parse(before), ast.parse(after)
        assert [ast.dump(n) for n in b.body[:len(a.body)]] == [ast.dump(n) for n in a.body]
        node = ast.parse((OLD / 'three_slot_finite_node_v1.py').read_text('utf8'))
        imports = [n for n in ast.walk(node) if isinstance(n, ast.ImportFrom)
                   and n.module == 'closed_production_continuation_CPU_v2']
        assert len(imports) == 1 and imports[0].names[0].name == 'load'
    case('unchanged_node_import_and_original_loader_byte_AST_prefix', dispatcher_AST_prefix)
    def dispatcher_CPU():
        path = B / 'closed_production_continuation_CPU_v2.py'
        modspec = importlib.util.spec_from_file_location('native86_synthetic_dispatch_only', path)
        module = importlib.util.module_from_spec(modspec); modspec.loader.exec_module(module)
        import native86_closed_source_CPU_v1 as native_loader
        original_native = native_loader.load
        original_preceding = module._native86_preceding_load
        try:
            native_loader.load = lambda s, b: ('typed_native', s, b)
            module._native86_preceding_load = lambda s, b: ('original_non_native', s, b)
            assert module.load(dict(native_continuation=True), 'synthetic_only')[0] == 'typed_native'
            assert module.load(dict(native_continuation=False), 'synthetic_only')[0] == 'original_non_native'
        finally:
            native_loader.load = original_native
            module._native86_preceding_load = original_preceding
    case('native_first_dispatch_and_original_nonnative_delegation_CPU', dispatcher_CPU)
    for field, value in (('source_SHA', BOOTSTRAP_SHA), ('bootstrap_source_SHA', NATIVE_SHA),
        ('source_Adamstep', 829720), ('GPU_UUID', 'other_GPU'), ('execution_backend', 'source210'),
        ('native_continuation_restore_required', False)):
        wrong = dict(spec); wrong[field] = value
        case('typed_identity_reject_' + field, lambda wrong=wrong: validate_identity(wrong), True)
    synthetic_manifest = deepcopy(original)
    rows = {r['relative']: r for r in synthetic_manifest['files']}
    rows.update({r['relative']: r for r in contract['overlay_files']})
    native_row = dict(relative='job0/source/native85_final.pt', bytes=140492265, SHA=NATIVE_SHA)
    rows[native_row['relative']] = native_row
    rows['NATIVE86_SOURCE_CONTRACT_ACTUAL.json'] = dict(relative='NATIVE86_SOURCE_CONTRACT_ACTUAL.json',
        bytes=(B / 'NATIVE86_SOURCE_CONTRACT_ACTUAL.json').stat().st_size, SHA=H(B / 'NATIVE86_SOURCE_CONTRACT_ACTUAL.json'))
    synthetic_manifest.update(source_SHA=NATIVE_SHA, source_filename='native85_final.pt',
        bootstrap_filename=original['source_filename'], source_Adamstep=BOOTSTRAP_ADAM,
        bootstrap_SHA=BOOTSTRAP_SHA, bootstrap_Adam=BOOTSTRAP_ADAM, files=list(rows.values()))
    case('protected_inventory_exact_overlay_positive', lambda: validate_inventory(synthetic_manifest, original, contract))
    wrong = deepcopy(synthetic_manifest); wrong['files'].append(dict(relative='source/unapproved.py', bytes=0, SHA='0' * 64))
    case('unapproved_added_python_rejected', lambda: validate_inventory(wrong, original, contract), True)
    wrong = deepcopy(synthetic_manifest); next(r for r in wrong['files'] if r['relative'] == 'h1_step270_path_reward_v1.py')['SHA'] = '0' * 64
    case('physical_V8_reward_pin_change_rejected', lambda: validate_inventory(wrong, original, contract), True)
    wrong = deepcopy(contract); wrong['controller_replacements'] = [dict(relative='h1_step270_path_reward_v1.py', original_SHA='0' * 64, SHA='0' * 64, bytes=0)]
    case('controller_inventory_blanket_exception_rejected', lambda: validate_inventory(synthetic_manifest, original, wrong), True)
    replacement_manifest = deepcopy(synthetic_manifest); replacement_contract = deepcopy(contract)
    task_row = next(r for r in replacement_manifest['files'] if r['relative'] == 'job0/TASK.json')
    task_old_sha = task_row['SHA']; task_row.update(bytes=123, SHA='1' * 64)
    replacement_contract['metadata_replacements'] = [dict(relative='job0/TASK.json',
        original_SHA=task_old_sha, bytes=123, SHA='1' * 64)]
    case('exact_TASK_metadata_replacement_positive', lambda: validate_inventory(replacement_manifest, original, replacement_contract))
    task_bad_contract = deepcopy(replacement_contract); task_bad_contract['metadata_replacements'][0]['original_SHA'] = '0' * 64
    case('TASK_wrong_original_SHA_rejected', lambda: validate_inventory(replacement_manifest, original, task_bad_contract), True)
    overlay_bad_contract = deepcopy(contract); overlay_bad_contract['overlay_files'].append(dict(relative='source/loose.py', bytes=0, SHA='0' * 64))
    case('overlay_path_blanket_exception_rejected', lambda: validate_inventory(synthetic_manifest, original, overlay_bad_contract), True)
    go = dict(source_qualification_kind=KIND, source_SHA=NATIVE_SHA, bootstrap_SHA=BOOTSTRAP_SHA,
        bootstrap_Adam=BOOTSTRAP_ADAM, native_continuation_restore_required=True,
        source_native_iteration=68, window_start_world_updates=680, window_start_policy_updates=58,
        manifest_SHA='f' * 64, max_parent_seconds=3900, exit_headroom_seconds=300,
        save_deadline=3600, nominal_end_epoch=3900)
    case('TASK_without_circular_manifest_SHA_signed_GO_positive', lambda: validate_task_go(spec, go, 'f' * 64))
    bad_go = dict(go); bad_go['manifest_SHA'] = 'e' * 64
    case('signed_GO_manifest_mismatch_rejected', lambda: validate_task_go(spec, bad_go, 'f' * 64), True)
    reference_bundle = read(OLD / 'MIXED84_REFERENCE_BINDING_ACTUAL.json')
    ready_spec = dict(spec, manifest_SHA='f' * 64, candidate_pins=contract['candidate_pins'],
        native_source_contract_SHA='e' * 64,
        reference_artifact_SHA=binding['producer']['reference_artifact_SHA'],
        adapter_CPU_report_SHA=binding['producer']['adapter_CPU_report_SHA'],
        objective_contract_SHA=binding['producer']['objective_contract_SHA'])
    sdk_fixture = dict(passed_CPU_only=True, actual_H1_source_SDK_CPU_passed=True,
        source_SHA=NATIVE_SHA, bootstrap_SHA=BOOTSTRAP_SHA, bootstrap_Adam=BOOTSTRAP_ADAM,
        native85_fullstate_source_CPU_passed=True, source_original85_cost_allout_passed=True,
        native_continuation_restore_required=True, manifest_SHA='f' * 64,
        actual_RSL_sources=[{}, {}], sampling_acceleration_CPU=dict(passed=True),
        new_reward_integration_CPU=dict(actual_installed_sampled_excess_SDK_compute_tested=True),
        boundary_repair_integration_CPU=dict(passed=True), rsl_load_roundtrip_CPU=True,
        whole_native=dict(passed=True))
    unit_fixture = dict(passed=True, actual_installed_CPU_passed=True, CUDA_initialized=False,
        manifest_SHA='f' * 64, source_SHA=NATIVE_SHA, candidate_pins=contract['candidate_pins'],
        offline_named_mapping_verified=True, actual_runtime_order_readback=False,
        offline_objective_contract=reference_bundle['objective_contract'],
        original_physics_and_success_unchanged=True, finalization_lifecycle_CPU_passed=True,
        partial_mask_objective_actual_CPU_admitted=True, ascent_phase_mask_and_own_step_support_loss_CPU_passed=True,
        **{k: ready_spec[k] for k in ('reference_artifact_SHA', 'adapter_CPU_report_SHA', 'objective_contract_SHA')})
    case('typed_ready_all_original_guards_synthetic_positive', lambda: ready_value(ready_spec, sdk_fixture, unit_fixture, contract))
    def root_ready_compatibility():
        protocol_path = T / 'H1_STEP270_THREE_GPU_NATIVE_CONTINUATION_RESOURCE_V86_20261026/mixed86_protocol_v1.py'
        module_spec = importlib.util.spec_from_file_location('pure_root86_ready_synthetic_fixture', protocol_path)
        module = importlib.util.module_from_spec(module_spec); module_spec.loader.exec_module(module)
        owner_spec = dict(ready_spec, finite_method_test=True, h1_step270_method_test=True)
        value = ready_value(ready_spec, sdk_fixture, unit_fixture, contract)
        envelope = dict(value=value, SHA=module.digest(value), actual_CPU_waited_EXIT0=True)
        row = dict(key='e2', phase='ready', original_error=False, manifest_SHA=owner_spec['manifest_SHA'], closed_source_CPU=envelope)
        assert module.native_valid_ready(row, owner_spec)
        value['source_SHA'] = BOOTSTRAP_SHA; envelope['SHA'] = module.digest(value)
        assert not module.native_valid_ready(row, owner_spec)
    case('actual_root86_pure_ready_positive_and_bootstrap_relabel_rejection', root_ready_compatibility)
    sdk_bad = deepcopy(sdk_fixture); sdk_bad['new_reward_integration_CPU']['actual_installed_sampled_excess_SDK_compute_tested'] = False
    case('ready_cannot_skip_original_actual_SDK_V8_check', lambda: ready_value(ready_spec, sdk_bad, unit_fixture, contract), True)
    unit_bad = deepcopy(unit_fixture); unit_bad['actual_runtime_order_readback'] = True
    case('ready_cannot_claim_fresh_runtime_order_from_CPU', lambda: ready_value(ready_spec, sdk_fixture, unit_bad, contract), True)
    for relative in ('../escaped.json', '/abs.py', 'source\\escape.py', 'C:/outside.py'):
        case('path_containment_' + relative, lambda relative=relative: contained(B, relative), True)
    case('duplicate_import_and_producer_exact_module', lambda: require(H(B / 'native_continuation_v1.py') == H(B / 'source/native_continuation_v1.py'), 'module mismatch'))
    # Tiny in-memory tensors only. Saved history has one row to avoid creating
    # the actual20k native histories; physical saved phase still has its exactN.
    bootstrap = dict(actor_state_dict={'distribution.std_param': torch.full((6,), .3)},
        critic_state_dict={str(i): torch.zeros(1) for i in range(8)},
        optimizer_state_dict=dict(state={i: dict(step=torch.tensor(BOOTSTRAP_ADAM), exp_avg=torch.zeros(1), exp_avg_sq=torch.zeros(1)) for i in range(17)},
            param_groups=[dict(params=list(range(17)), lr=.0001)]))
    bootstrap['actor_state_dict'].update({str(i): torch.zeros(1) for i in range(8)})
    s = {k: {} for k in REQUIRED_ORIGINAL_GROUPS}; s.update(deepcopy(bootstrap))
    for name in ('sensor_DR_state', 'feedback_delay_state', 'physical_action_delay_state', 'spring_pressure_state', 'gas_damping_state'):
        s[name] = dict(n=20000)
    s['chassis_PD_state'] = {name: dict(num_envs=20000) for name in ('COM', 'PD')}
    phase = dict(version=270, num_envs=20000, geometry=dict(height=.270, edge_x=.35, depth=.8, width=1.2),
        tensors=dict(previous_front=torch.zeros(20000, 2)), goal=dict(success=torch.zeros(20000, dtype=torch.bool)))
    s['H1_step270_task_state'] = dict(version=270, phase=phase)
    s['H1_step270_runtime_contract'] = dict(original_D0_D7_STD_optimizer_save_chain_retained=True)
    final = metadata['final']['final']
    pub = dict(native_iteration=68, world_updates=680, policy_updates=58,
        run_token=final['run_token'], save_token=final['save_token'], producer=deepcopy(binding['producer']),
        history_shape=[1, 2, 3], episode_step_shape=[1])
    s['UniSuperMimic_publication'] = pub
    s['UniSuperMimic_test_contract'] = deepcopy(NATIVE_CONTRACT)
    s['UniSuperMimic_obs_history'] = torch.zeros(1, 2, 3)
    s['UniSuperMimic_bridge_ep_step'] = torch.zeros(1, dtype=torch.long)
    tiny_opt = dict(state={0: dict(step=torch.tensor(1.), exp_avg=torch.zeros(1), exp_avg_sq=torch.zeros(1))}, param_groups=[dict(params=[0])])
    native = dict(iteration=68, wall_time=1., sim_steps=34020000, args={}, saved_at=1.,
        **{k: {'weight': torch.zeros(1)} for k in ('wm', 'pi', 'critic')},
        **{k: deepcopy(tiny_opt) for k in ('opt_wm', 'opt_pi', 'opt_v')})
    s['UniSuperMimic_H1_test'] = native
    check = lambda ck: validate_whole_native(ck, bootstrap, binding, metadata['final'], validate_new_phase, verify_native)
    case('whole_native_three_optimizers_and_frozen17Adam_positive', lambda: check(s))
    for name, mutate in (
        ('missing_WM', lambda x: x['UniSuperMimic_H1_test'].pop('wm')),
        ('missing_native_optimizer', lambda x: x['UniSuperMimic_H1_test']['opt_pi'].update(state={})),
        ('native_nonfinite', lambda x: x['UniSuperMimic_H1_test']['wm']['weight'].fill_(float('nan'))),
        ('bootstrap_changed', lambda x: x['actor_state_dict']['distribution.std_param'].fill_(.4)),
        ('wrong_baseline_Pi', lambda x: x['UniSuperMimic_publication'].update(policy_updates=59)),
        ('lost_D0_D7', lambda x: x.pop('sensor_global_rng_state')),
        ('wrong_phase_count', lambda x: x['H1_step270_task_state']['phase'].update(num_envs=128))):
        wrong = deepcopy(s); mutate(wrong)
        case('whole_native_reject_' + name, lambda wrong=wrong: check(wrong), True)
    @dataclass
    class TinyCfg:
        hist: int = 2
        wm_window: int = 2
        warmup_steps: int = 48
    learner = SimpleNamespace(cfg=TinyCfg(), iteration=0, wall_time=0., sim_steps=0,
        buffer=SimpleNamespace(size=0, ptr=0), obs_hist=torch.ones(1, 2, 3))
    for mod, opt in (('wm', 'opt_wm'), ('pi', 'opt_pi'), ('critic', 'opt_v')):
        module = torch.nn.Linear(1, 1, bias=False)
        optimizer = torch.optim.Adam(module.parameters(), lr=.001)
        module.weight.grad = torch.ones_like(module.weight)
        optimizer.step(); optimizer.zero_grad()
        setattr(learner, mod, module); setattr(learner, opt, optimizer)
    restore_ck = deepcopy(s); restore_native = restore_ck['UniSuperMimic_H1_test']
    restore_native['args'] = asdict(learner.cfg)
    for name in ('wm', 'pi', 'critic', 'opt_wm', 'opt_pi', 'opt_v'):
        restore_native[name] = deepcopy(getattr(learner, name).state_dict())
    bridge = SimpleNamespace(wm_updates=0, pi_updates=0, ep_step=torch.zeros(1, dtype=torch.long), state='old')
    proof = dict(source_SHA=NATIVE_SHA, new_physical_episode_zeroes_goal_credit=True,
        not_PhysX_exact_resume=True, complete_D0_D7_original_proof=dict(new_physical_episode=True))
    admission = admit()
    def restore_case():
        receipt = restore_legacy85_new_episode(restore_ck, learner, bridge, admission, proof, verify_native)
        assert receipt['restored_iteration'] == 68 and receipt['restored_policy_updates'] == 58
        assert bridge.window_start_pi_updates == 58 and bridge.state is None and not learner.obs_hist.any()
        assert receipt['fresh_replay_refill_steps'] == 48 and not receipt['replay_restored']
    case('frozen_restore_tiny_native_new_episode_positive', restore_case)
    case('restore_used_learner_rejected', lambda: restore_legacy85_new_episode(restore_ck, learner, bridge, admission, proof, verify_native), True)
    # CPU actual-entry source APIs are exercised on synthetic bootstrap tensors
    # only; a network constructor is not a policy forward.
    def installed_rsl_synthetic():
        from tensordict import TensorDict
        from rsl_rl.models import MLPModel
        from rsl_rl.algorithms import PPO
        obs = TensorDict(dict(policy=torch.zeros(1, 35), critic=torch.zeros(1, 38)), batch_size=[1])
        groups = dict(actor=['policy'], critic=['critic'])
        actor = MLPModel(obs, groups, 'actor', 6, hidden_dims=[256,128,64], activation='elu',
            distribution_cfg=dict(class_name='rsl_rl.modules.distribution:GaussianDistribution', init_std=.3, std_type='scalar'))
        critic = MLPModel(obs, groups, 'critic', 1, hidden_dims=[256,128,64], activation='elu')
        opt = torch.optim.Adam(list(actor.parameters()) + list(critic.parameters()), lr=.0001)
        ck = dict(actor_state_dict=actor.state_dict(), critic_state_dict=critic.state_dict(), optimizer_state_dict=opt.state_dict())
        assert len(ck['actor_state_dict']) == 9 and len(ck['critic_state_dict']) == 8
        assert PPO.load(SimpleNamespace(actor=actor, critic=critic, optimizer=opt, rnd=None), ck, None, True)
    case('actual_installed_RSL_API_synthetic_constructor_load_no_forward', installed_rsl_synthetic)
    for p in B.rglob('*.py'):
        case('parse_' + p.relative_to(B).as_posix(), lambda p=p: ast.parse(p.read_text('utf8')))
    assert not torch.cuda.is_initialized()
    result = dict(epoch=time.time(), schema='mod4.native86.typed_source_worker.synthetic_CPU.v1',
        passed=all(row['passed'] for row in cases), count=len(cases), passed_count=sum(row['passed'] for row in cases),
        cases=cases, CPU_only=True, CUDA_initialized=False, real_PT_NPZ_read_hash_copy=False,
        real_policy_inference=False, remote_GPU_ledger_lock_Task_GO=False,
        actual_installed86_SDK_source_CPU=False, contract_SHA=H(B / 'NATIVE86_SOURCE_CONTRACT_ACTUAL.json'),
        native_baseline=dict(iteration=68, world_updates=680, policy_updates=58),
        git='pending parent ordinary supplement archive')
    destination = D / 'reports' / ('NATIVE86_TYPED_SOURCE_SYNTHETIC_CPU_ATTEMPT_' + str(time.time_ns()) + '.json')
    with destination.open('x', encoding='utf8') as stream:
        json.dump(result, stream, indent=2, allow_nan=False)
    print(json.dumps(dict(passed=result['passed'], count=result['count'], passed_count=result['passed_count'], report=str(destination))))
    if not result['passed']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
