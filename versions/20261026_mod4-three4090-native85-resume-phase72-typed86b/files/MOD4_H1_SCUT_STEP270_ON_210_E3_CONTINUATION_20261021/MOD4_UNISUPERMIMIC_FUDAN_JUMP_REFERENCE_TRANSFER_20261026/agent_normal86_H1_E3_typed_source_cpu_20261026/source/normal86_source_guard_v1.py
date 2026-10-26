"""Normal H1 PPO/E3 typed source admission; no I/O or torch import on import."""
from pathlib import Path, PurePosixPath
import ast
import hashlib
import json

SOURCES = dict(h1=dict(SHA='8bb9869ac683550c1e7be1c9dffae9a5eac022e0de0fc8f251cd2005cfa6d4c6',
    Adam=829700, updates=130, bytes=16868571, counts=[202,106], hz=100,
    GPU='GPU-937bdb0b-0d8f-aa3d-a10e-1b24969a5d4e', backend='source210'),
    recovery=dict(SHA='7f8f270c84b7e3d9e7efd0b1bd29d10d430a51bb976e1689222859f24e714d59',
    Adam=862540, updates=87, bytes=14716821, counts=[173,96], hz=50,
    GPU='GPU-c27eecbd-6838-7290-1cd2-37e34522213d', backend='target72'))
CONTROLLERS = frozenset(('three_slot_common_v1.py', 'forwarded_original_owner_control_v1.py', 'three_real_gpu_resource_v1.py'))
METADATA = frozenset(('job0/TASK.json',))
METADATA_SHA = 'c6e421115263e6bfd0fb31630882087fb644efbfb3a56bfbd39643c4478c891e'
FEE85 = 7299.1399965286255
BALANCE85 = 587957.6840648651


def require(value, message):
    if not value:
        raise RuntimeError(message)


def H(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def read(path):
    return json.loads(Path(path).read_bytes())


def contained(B, relative):
    require(isinstance(relative, str) and relative, 'Empty relative path')
    rel = PurePosixPath(relative)
    require(not rel.is_absolute() and '..' not in rel.parts and ':' not in relative
        and '\\' not in relative and rel.as_posix() == relative, 'Invalid relative path')
    B = Path(B).resolve(); p = B.joinpath(*rel.parts)
    require(p.resolve().is_relative_to(B), 'Path escaped payload')
    cursor = p
    while cursor != B:
        require(not cursor.is_symlink(), 'Symlink in payload')
        cursor = cursor.parent
    return p


def index(rows):
    result = {}
    for row in rows:
        require(row['relative'] not in result, 'Duplicate manifest row')
        require(type(row['bytes']) is int and row['bytes'] >= 0, 'Invalid byte count')
        require(isinstance(row['SHA'], str) and len(row['SHA']) == 64 and all(c in '0123456789abcdef' for c in row['SHA']), 'Invalid SHA')
        result[row['relative']] = row
    return result


def identity(spec, key=None):
    key = key or spec['key']; require(key in SOURCES, 'Normal role must be h1 or recovery')
    pin = SOURCES[key]
    require(spec['key'] == key and spec.get('normal86_continuation') is True, 'Normal86 role absent')
    require(not spec.get('native_continuation') and not spec.get('finite_method_test'), 'Native role cannot be relabelled normal')
    require(spec['source_SHA'] == pin['SHA'] and spec['source_Adamstep'] == pin['Adam'], 'Normal qualified source differs')
    require(spec['GPU_UUID'] == pin['GPU'] and spec['execution_backend'] == pin['backend'], 'Normal backend/GPU differs')
    require(spec['policy_hz'] == spec['source_policy_hz'] == pin['hz'], 'Normal clock differs')
    return key


def allowed_overlay_paths(key):
    common = {'normal86_source_guard_v1.py', 'normal86_closed_source_CPU_v1.py',
        'NORMAL86_SOURCE_BINDING_ACTUAL.json', 'NORMAL86_ORIGINAL_COMPLETE_MANIFEST.json',
        'normal86_metadata/SOURCE_ORIGIN_CPU_ACTUAL.json', 'normal86_metadata/SOURCE_ORIGIN_NODE_TERMINAL_ACTUAL.json',
        'normal86_metadata/SOURCE_ORIGIN_NODE_EXIT_ACTUAL.json', 'normal86_metadata/SOURCE_ORIGIN_FINAL_ACTUAL.json',
        'normal86_metadata/CURRENT85_CPU_ACTUAL.json', 'normal86_metadata/CURRENT85_COLLECTOR_ACTUAL.json'}
    if key == 'h1':
        return common | {'closed_production_continuation_CPU_v2.py', 'h1_step270_production_worker_v1.py',
                         'target_normal86_h1_source_sdk_cpu_review_v1.py', 'OWNER72_CONTROL_DEPENDENCIES_BINDING_ACTUAL.json'}
    return common | {'original_account_policy50_source_CPU.py', 'recovery_worker.py',
        'target_normal86_recovery_source_sdk_cpu_review_v1.py', 'normal86_metadata/SOURCE_ORIGIN_POLICY50_CLOCK_ACTUAL.json'}


def validate_inventory(m, old, contract):
    key = contract['key']; require(key in SOURCES, 'Invalid normal contract key')
    pin = SOURCES[key]; current, baseline, overlay = index(m['files']), index(old['files']), index(contract['overlay_files'])
    require(set(overlay) == allowed_overlay_paths(key), 'Exact normal overlay path set differs')
    require(not contract.get('removed_files'), 'Original file removals forbidden')
    replacements = index(contract.get('controller_replacements', []))
    require(set(replacements) <= CONTROLLERS, 'Unapproved controller replacement')
    meta = index(contract.get('metadata_replacements', [])); require(set(meta) <= METADATA, 'Unapproved metadata replacement')
    additions = index(contract.get('controller_additions', [])); require(set(additions) <= {'mixed86_protocol_v1.py'}, 'Unapproved controller addition')
    for rel, before in baseline.items():
        require(rel in current, 'Original row omitted: ' + rel)
        if rel in overlay:
            require(current[rel] == overlay[rel], 'Exact normal source replacement differs: ' + rel)
        elif rel in replacements or rel in meta:
            review = (replacements if rel in replacements else meta)[rel]
            require(review['original_SHA'] == before['SHA'] and current[rel]['SHA'] == review['SHA']
                    and current[rel]['bytes'] == review['bytes'], 'Reviewed replacement differs: ' + rel)
        else:
            require(current[rel] == before, 'Protected original differs: ' + rel)
    for rel, row in {**overlay, **additions}.items():
        require(current.get(rel) == row, 'Exact added source row differs: ' + rel)
    source = 'job0/source/' + m['source_filename']
    require(set(current) - set(baseline) - set(overlay) - set(additions) == {source, 'NORMAL86_SOURCE_CONTRACT_ACTUAL.json'}, 'Unapproved added inventory')
    require(source not in baseline and current[source]['SHA'] == pin['SHA'] and current[source]['bytes'] == pin['bytes'], 'New qualified source pin differs')
    require(m['key'] == key and m['source_SHA'] == pin['SHA'] and m['source_Adamstep'] == pin['Adam'], 'Normal manifest source differs')
    require(Historical_source_row_present(old, current), 'Historical input PT row lost')
    return current


def Historical_source_row_present(old, current):
    rel = 'job0/source/' + old['source_filename']
    previous = next(r for r in old['files'] if r['relative'] == rel)
    return current.get(rel) == previous


def check_payload(B, key, spec=None):
    B = Path(B).resolve(); m = read(B / 'THREE_SLOT_COMPLETE_MANIFEST_V1.json')
    contract = read(B / 'NORMAL86_SOURCE_CONTRACT_ACTUAL.json')
    require(contract['key'] == key, 'Payload role differs')
    require(H(B / 'NORMAL86_ORIGINAL_COMPLETE_MANIFEST.json') == contract['original_manifest_SHA'], 'Original manifest SHA differs')
    rows = validate_inventory(m, read(B / 'NORMAL86_ORIGINAL_COMPLETE_MANIFEST.json'), contract)
    for rel, row in rows.items():
        p = contained(B, rel)
        require(p.is_file() and p.stat().st_size == row['bytes'] and H(p) == row['SHA'], 'Installed file differs: ' + rel)
        if p.suffix == '.py':
            ast.parse(p.read_text('utf8'), filename=rel)
    require({p.relative_to(B).as_posix() for p in B.rglob('*.py')} == {r for r in rows if r.endswith('.py')}, 'Unapproved Python file')
    require(H(B / 'NORMAL86_SOURCE_BINDING_ACTUAL.json') == contract['binding_SHA'], 'Typed binding SHA differs')
    require((B / 'same_optimized_source_contract_metadata_candidate_v1.py').stat().st_size == 2536
            and H(B / 'same_optimized_source_contract_metadata_candidate_v1.py') == METADATA_SHA, 'Original metadata helper differs')
    if spec is not None:
        identity(spec, key)
        require(spec['manifest_SHA'] == H(B / 'THREE_SLOT_COMPLETE_MANIFEST_V1.json'), 'Spec manifest differs')
        require(spec['normal_source_contract_SHA'] == H(B / 'NORMAL86_SOURCE_CONTRACT_ACTUAL.json'), 'Spec typed source contract differs')
        if key == 'h1':
            require(spec['owner_control_dependency_binding_SHA'] == H(B / 'OWNER72_CONTROL_DEPENDENCIES_BINDING_ACTUAL.json'), 'H1 source210 control dependency binding differs')
    return contract


def read_bound_metadata(B):
    binding = read(Path(B) / 'NORMAL86_SOURCE_BINDING_ACTUAL.json'); result = {}
    for name, row in binding['metadata'].items():
        path = contained(B, row['relative'])
        require(path.suffix == '.json' and path.stat().st_size == row['bytes'] and H(path) == row['SHA'], 'Metadata pin differs: ' + name)
        result[name] = read(path)
    return binding, result


def validate_origin(binding, data):
    key = binding['key']; pin = SOURCES[key]
    require(binding['schema'] == 'mod4.normal86.typed_origin_binding.v1', 'Typed origin schema differs')
    require(binding['source_SHA'] == pin['SHA'] and binding['source_Adamstep'] == pin['Adam'], 'Typed origin identity differs')
    proof = data['source_cpu']; require(proof['passed'] is True, 'Origin CPU not qualified')
    require(proof['all_owner_nodes_children_actual_out'] and proof['original_canonical_cost_settled']
            and proof['all_original_private_shared_locks_free'], 'Origin allout/cost incomplete')
    model = proof['models'][key]; final = model['final']
    require(model['updates'] == pin['updates'] and model['Adam'] == pin['Adam'] and model['counts'] == pin['counts'], 'Origin CPU counters/schema differ')
    changed=model['all17_changed']
    require(len(changed['actor_state_dict']) == 9 and len(changed['critic_state_dict']) == 8
            and 'distribution.std_param' in changed['actor_state_dict'], 'Origin normal learned17 tensors incomplete')
    require(final['SHA'] == pin['SHA'] and final['bytes'] == pin['bytes'] and final['twohost_complete_SHA'], 'Origin complete FINAL differs')
    cost = model['actual_cost']; require(cost['actual_returncode'] == 0 and cost['duration_bound_passed'] and 0 < cost['charged_seconds'] <= 3900, 'Origin cost invalid')
    terminal, exited = data['source_terminal']['row'], data['source_exit']
    require(terminal['terminal_all_own_children_waited'] and terminal['returncode'] == 0 and not terminal['original_error'] and not terminal['errors'], 'Origin node terminal incomplete')
    require(exited['actual_all_own_children_waited'] and exited['validation_fcntl_released_if_acquired'], 'Origin node exit incomplete')
    require(terminal['final']['passed'] and terminal['final']['final']['SHA'] == final['SHA']
            and data['source_final'] == terminal['final'], 'Origin formal FINAL not bound')
    if key == 'recovery':
        clock = data['source_clock']
        require(clock['policy_hz'] == 50 and clock['physics_dt_s'] == .0025 and clock['decimation'] == 8,
                'Origin E3 clock differs')
        require(set(proof['models']) == {'recovery'} and proof['native_method']['not_production_H1_or_E2_source'], 'Native diagnostic confused with normal source')
    # Latest resources/accounting are a different evidence object. Do not
    # manufacture three current normal models from a native/E3 pair closure.
    latest, collector = data['latest_cpu'], data['latest_collector']
    require(latest['passed'] and set(latest['models']) == {'recovery'}, 'Latest85 normal source schema differs')
    require(latest['native_method']['not_production_H1_or_E2_source'], 'Latest native role lost')
    require(latest['all_owner_nodes_children_actual_out'] and latest['original_canonical_cost_settled']
            and latest['all_original_private_shared_locks_free'], 'Latest85 closure incomplete')
    require(latest['actual_cost_sumonce'] == FEE85 and latest['remaining_actual_snapshot'] == BALANCE85, 'Latest85 original cost snapshot differs')
    require(collector['actual_finite_transport_returned'] and collector['original_canonical_cost_settled'], 'Latest collector incomplete')
    a = collector['authority72']
    require(a['all_authority72_owner_children_actual_out'] and a['cohort']['original_cost_settled'] and a['owner_exit']['original_cost_settled'], 'Sole72 original closure incomplete')
    require(len(a['original_locks']) == 2 and all(row['actual_fcntl_free'] for row in a['original_locks']), 'Sole72 original locks not free')
    experts = a['original_segment']['experts']
    require(set(experts) == {'e2', 'recovery'} and all(row['duration_bound_passed'] and 0 < row['charged_seconds'] <= 3900 for row in experts.values()), 'Latest85 original charged slots differ')
    require(abs(sum(row['charged_seconds'] for row in experts.values()) - FEE85) < 1e-5
            and a['original_canonical_remaining'] == BALANCE85, 'Latest85 fee sum/snapshot differs')
    return dict(passed=True, key=key, source_SHA=pin['SHA'], source_Adamstep=pin['Adam'],
        source_origin_individually_qualified=True, latest85_pair_independent_cost_allout=True,
        no_new_83B_healthy_three_claim=True, no_live_retired210_account_read=True)


def exact_worker_delta(before, after, key):
    """Normalize only reviewed source guard + E3 filename/Adam edits."""
    expected = before
    if key == 'h1':
        marker = "assert H(src)==go['source_SHA'];assert not (J/phase).exists()"
        replacement = "assert H(src)==go['source_SHA'];from normal86_source_guard_v1 import check_payload,validate_task_go;check_payload(B,'h1');validate_task_go(task,go,'h1',H(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'));assert not (J/phase).exists()"
        require(expected.count(marker) == 1, 'H1 worker marker count')
        expected = expected.replace(marker, replacement)
    else:
        require(expected.count("src=J/'source/RECOVERY_auto_source.pt'") == 1, 'E3 fixed source path count')
        expected = expected.replace("src=J/'source/RECOVERY_auto_source.pt'", "src=J/'source'/task['source_filename']")
        require(expected.count('assert steps=={860800+20*updates}') == 1, 'E3 old Adam assertion count')
        expected = expected.replace('assert steps=={860800+20*updates}', 'assert steps=={862540+20*updates}')
        marker = "assert H(src)==task['source_SHA']"
        require(expected.count(marker) == 1, 'E3 source guard marker count')
        replacement = marker + ";from normal86_source_guard_v1 import check_payload,validate_task_go;check_payload(B,'recovery');validate_task_go(task,json.loads((J/'GO_PRODUCTION.json').read_bytes()),'recovery',H(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json')) if not native else None"
        expected = expected.replace(marker, replacement)
    require(ast.dump(ast.parse(expected)) == ast.dump(ast.parse(after)), 'Unapproved normal worker AST change')
    return dict(passed=True, only_source_admission_and_declared_E3_source_binding_delta=True)


def validate_task_go(task, go, key, manifest_SHA):
    identity(task, key)
    require(go['source_SHA'] == SOURCES[key]['SHA'] and go['manifest_SHA'] == manifest_SHA, 'Normal GO source/manifest differs')
    require(not go.get('native_continuation_restore_required') and go['max_parent_seconds'] == 3900
            and go['exit_headroom_seconds'] == 300 and go['save_deadline'] < go['nominal_end_epoch'], 'Normal bounded GO differs')
    return True


def complete_installed_CPU(B, m, s, original_cpu):
    """Append after the complete original target CPU script; reuse its one load."""
    import torch
    B = Path(B); key = m['key']; pin = SOURCES[key]
    check_payload(B, key)
    binding, data = read_bound_metadata(B); origin = validate_origin(binding, data)
    require(original_cpu['passed_CPU_only'] and original_cpu['source_SHA'] == pin['SHA']
            and original_cpu['all17Adam'] == pin['Adam'], 'Original installed CPU source differs')
    require(len(original_cpu['actual_RSL_sources']) == 2
            and original_cpu['actual_SDK_math']['SHA'] == m['expected_actual_SDK_math_SHA'], 'Original RSL/SDK checks absent')
    require('UniSuperMimic_H1_test' not in s and 'UniSuperMimic_publication' not in s, 'Native checkpoint cannot enter normal PPO role')
    require(len(s['actor_state_dict']) == 9 and len(s['critic_state_dict']) == 8
            and tuple(s['actor_state_dict']['distribution.std_param'].shape) == (6,), 'Normal PPO core layout differs')
    require(len(s['optimizer_state_dict']['state']) == 17
        and {int(v['step']) for v in s['optimizer_state_dict']['state'].values()} == {pin['Adam']}, 'Normal17Adam differs')
    if key == 'h1':
        require(s['owned_H1_completed_updates'] == 130 and s['failed_partial_prefix'] is False, 'H1 formal normal FINAL differs')
        require(original_cpu['new_reward_integration_CPU']['actual_installed_sampled_excess_SDK_compute_tested']
                and original_cpu['boundary_repair_integration_CPU']['passed'], 'Original H1 V8/boundary CPU absent')
        sampler = original_cpu['sampling_acceleration_CPU']
        require(sampler['passed'] and sampler['V8_reward_publication_AST']['passed']
                and sampler['lifetime_goal_diagnostic_CPU']['passed'] and sampler['landing_event_journal_CPU']['passed'], 'Original H1 trace/retention diagnostics absent')
    else:
        require(s['E3_production_updates'] == 87 and original_cpu['source_schema_counts'] == [173,96], 'Normal E3 source schema differs')
        clock = s['policy_clock']; require(clock['policy_hz'] == 50 and clock['physics_dt_s'] == .0025 and clock['decimation'] == 8, 'Saved E3 clock differs')
        require('E3_public_recovery_state' in s and 'E3_reset_contract' in s, 'Saved E3 complete phase/reset groups absent')
        sampler = original_cpu['sampling_acceleration_CPU']
        require(sampler['passed'] and sampler['fresh_bank_physical_read_count'] == 1, 'Original E3 cache/source checks absent')
    # Installed RSL CPU strict-load roundtrip, using only the already-read
    # dictionary. No actor forward, scene, reset, sampling or optimizer step.
    from tensordict import TensorDict
    from rsl_rl.models import MLPModel
    from rsl_rl.algorithms import PPO
    def exact(a,b):
        if torch.is_tensor(a):
            return torch.is_tensor(b) and a.shape == b.shape and a.dtype == b.dtype and torch.equal(a,b)
        if isinstance(a,dict):
            return isinstance(b,dict) and set(a)==set(b) and all(exact(a[k],b[k]) for k in a)
        if isinstance(a,(list,tuple)):
            return type(a) is type(b) and len(a)==len(b) and all(exact(x,y) for x,y in zip(a,b))
        return type(a) is type(b) and a==b
    env = read(B / 'job0/original_run_manifest.json')['env']
    hidden = [int(v) for v in env['RM_HIDDEN_DIMS'].split(',')]
    with torch.random.fork_rng(devices=[]):
        obs = TensorDict(dict(policy=torch.zeros(1,35), critic=torch.zeros(1,38)), batch_size=[1]); groups=dict(actor=['policy'],critic=['critic'])
        actor = MLPModel(obs,groups,'actor',6,hidden_dims=hidden,activation='elu',distribution_cfg=dict(class_name='rsl_rl.modules.distribution:GaussianDistribution',init_std=float(env['RM_INIT_STD']),std_type='scalar'))
        critic = MLPModel(obs,groups,'critic',1,hidden_dims=hidden,activation='elu')
        opt = torch.optim.Adam(list(actor.parameters()) + list(critic.parameters()),lr=.0001)
        from types import SimpleNamespace
        require(PPO.load(SimpleNamespace(actor=actor,critic=critic,optimizer=opt,rnd=None),s,None,True), 'Installed RSL load failed')
        for name, obj in (('actor_state_dict',actor),('critic_state_dict',critic),('optimizer_state_dict',opt)):
            require(exact(obj.state_dict(),s[name]), 'Installed RSL literal roundtrip differs: ' + name)
    require(not torch.cuda.is_initialized(), 'CPU review initialized CUDA')
    result = dict(passed=True, actual_installed_CPU_passed=True, actual_H1_or_E3_source_SDK_CPU_passed=True,
        key=key, source_SHA=pin['SHA'], all17Adam=pin['Adam'], source_updates=pin['updates'],
        manifest_SHA=H(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'), original_installed_CPU=original_cpu,
        original_installed_CPU_script_prefix_retained=True, RSL_strict_load_literal_roundtrip_CPU=True,
        origin=origin, normal_PPO_not_native=True, no_policy_forward_scene_optimizer_step_or_GO=True,
        CUDA_initialized=False)
    with (B/'NORMAL86_INSTALLED_SOURCE_SDK_CPU_ADMITTED_ACTUAL.json').open('x',encoding='utf8') as stream:
        json.dump(result,stream,indent=2,allow_nan=False)
    return result


def ready_value(spec, fresh, binding_SHA):
    key = identity(spec); pin = SOURCES[key]
    require(fresh['passed'] and fresh['actual_installed_CPU_passed'] and not fresh['CUDA_initialized']
            and fresh['actual_H1_or_E3_source_SDK_CPU_passed'], 'Fresh installed normal86 CPU absent')
    require(fresh['key'] == key and fresh['source_SHA'] == pin['SHA'] and fresh['all17Adam'] == pin['Adam']
            and fresh['manifest_SHA'] == spec['manifest_SHA'], 'Fresh normal CPU identity differs')
    require(fresh['origin']['passed'] and fresh['RSL_strict_load_literal_roundtrip_CPU'] and fresh['normal_PPO_not_native'], 'Fresh normal qualification incomplete')
    return dict(kind='closed_same_backend_production' if key=='h1' else 'closed_same_backend_policy50_production',
        key=key, passed=True, source_SHA=pin['SHA'], source_Adam=pin['Adam'], GPU_UUID=pin['GPU'], execution_backend=pin['backend'],
        all_source_model_runtime_finite_CPU=True, old_complete_production_checkpoint_actual_EXIT0=True,
        same_active_runtime_assets_and_PPO_AST=True, same_physics_assets_and_PPO_AST=True,
        source_original_cost_settled=True, explicit_policy_clock_50Hz_admitted=key=='recovery',
        same_clock_closed_production=True, source_cost_original_account_ready=True,
        source_account_reconciliation_receipt_SHA=binding_SHA,
        original_clip6_query_COM_closure_mimic_hardware_savedstop_guards_retained=True,
        actual_installed_normal86_CPU=True, source_origin_typed_and_current85_cost_separate=True,
        sole72_authority=True, not_skill_graduation=True)
