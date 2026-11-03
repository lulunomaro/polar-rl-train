"""Independent SOURCE/AST audit. No target import, SDK, tensor, process or network.
Only .py sources, one sealed SOURCE API manifest and the allowed small scalar
aggregate are read. Only this NEW directory receives write-once audit output.
"""
from __future__ import annotations
import ast
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
TASKS = ROOT / 'discovery/reward_command_audit_v1'
MANIFEST = ROOT / 'source_phase1_passive_sensor_capture_v2/SOURCE_API_MANIFEST.json'
SCALAR = ROOT / 'reports/PHASE1_V4_A2_ACTUAL_QUEUE_SCALAR_DIAGNOSTIC_V1.json'
ROLES = ('E0', 'E2', 'E3', 'W35', 'CURB_PROTECTED878', 'CURB_INDEPENDENT113',
         'SLOPE135', 'SLOPE_INDEPENDENT50')
READ_PINS = {}


def raw(path):
    path = Path(path).resolve()
    assert path.is_relative_to(ROOT)
    assert path.suffix == '.py' or path in (MANIFEST, SCALAR)
    value = path.read_bytes()
    meta = dict(path=path.as_posix(), bytes=len(value), sha256=hashlib.sha256(value).hexdigest())
    if path.as_posix() in READ_PINS:
        assert READ_PINS[path.as_posix()] == meta, 'Source changed during audit'
    READ_PINS[path.as_posix()] = meta
    return value


def tree(path):
    return ast.parse(raw(path).decode('utf-8-sig'), filename=str(path))


def source_pin(path, node=None):
    raw(path)
    result = dict(READ_PINS[Path(path).resolve().as_posix()])
    if node is not None:
        result.update(line=node.lineno, end_line=node.end_lineno)
    return result


def expr(node):
    return ast.unparse(node)


def named(body, name, kind):
    return next(n for n in body if isinstance(n, kind) and n.name == name)


def call_rows(node):
    return sorted((dict(line=n.lineno, column=n.col_offset, call=expr(n))
                   for n in ast.walk(node) if isinstance(n, ast.Call)),
                  key=lambda r: (r['line'], r['column']))


def resolve_chain(folder, module, cls_name, seen=()):
    key = (module, cls_name)
    assert key not in seen, 'Local class cycle'
    path = folder / (module + '.py')
    if not path.is_file():
        return [], dict(module=module, class_name=cls_name, source='UNAVAILABLE_EXTERNAL_SDK')
    t = tree(path)
    imports = {a.asname or a.name: (n.module, a.name)
               for n in t.body if isinstance(n, ast.ImportFrom) for a in n.names}
    classes = {n.name: n for n in t.body if isinstance(n, ast.ClassDef)}
    if cls_name not in classes:
        assert cls_name in imports, key
        m, c = imports[cls_name]
        return resolve_chain(folder, m, c, seen + (key,))
    node = classes[cls_name]
    result = dict(module=module, class_name=cls_name, **source_pin(path, node))
    step = next((n for n in node.body if isinstance(n, ast.FunctionDef) and n.name == 'step'), None)
    if step is None:
        result['declared_step'] = None
    else:
        calls = call_rows(step)
        result['declared_step'] = dict(line=step.lineno, end_line=step.end_lineno,
                                      super_step_calls=[r for r in calls if r['call'].startswith('super().step(')],
                                      target_setters=[r for r in calls if 'set_joint_' in r['call'] and '_target(' in r['call']],
                                      counter_writes=[n.lineno for n in ast.walk(step)
                                          if isinstance(n, (ast.Assign, ast.AnnAssign, ast.AugAssign))
                                          and any(isinstance(x, ast.Attribute) and isinstance(x.ctx, ast.Store)
                                                  and x.attr == '_sim_step_counter' for x in ast.walk(n))])
        assert len(result['declared_step']['super_step_calls']) == 1
        assert not result['declared_step']['target_setters']
        assert not result['declared_step']['counter_writes']
    assert len(node.bases) == 1 and isinstance(node.bases[0], ast.Name)
    base = node.bases[0].id
    if base in classes:
        more, external = resolve_chain(folder, module, base, seen + (key,))
    else:
        assert base in imports, (module, cls_name, base)
        m, c = imports[base]
        more, external = resolve_chain(folder, m, c, seen + (key,))
    return [result] + more, external


def audit_role(role, prior):
    folder = TASKS / role / 'runtime/isaac/mod4'
    entry = Path(prior['entry']['source_path'])
    assert entry.parent == folder
    assert source_pin(entry)['sha256'] == prior['entry']['source_sha256']
    entry_tree = tree(entry)
    aliases = {a.asname or a.name: (n.module, a.name)
               for n in entry_tree.body if isinstance(n, ast.ImportFrom) for a in n.names}
    module, cls = aliases['Mod4Env']
    chain, external = resolve_chain(folder, module, cls)
    assert [(n['module'], n['class_name']) for n in chain] == [
        (n['module'], n['qualname']) for n in prior['env_mro_local']]
    assert all(n['sha256'] == p['source_sha256'] for n, p in zip(chain, prior['env_mro_local']))
    assert chain[-1]['module'] == 'mod4_env' and chain[-1]['class_name'] == 'Mod4Env'
    assert external == dict(module='isaaclab.envs', class_name='ManagerBasedRLEnv', source='UNAVAILABLE_EXTERNAL_SDK')
    task_file = folder / 'mod4_task.py'
    t = tree(task_file)
    ec = named(t.body, 'EventCfg', ast.ClassDef)
    registration = next(n for n in ec.body if isinstance(n, ast.Assign)
                        and any(isinstance(x, ast.Name) and x.id == 'gas_spring_preload' for x in n.targets))
    assert isinstance(registration.value, ast.Call)
    kw = {n.arg: n.value for n in registration.value.keywords}
    assert expr(kw['func']) == 'skills.gas_spring_preload' and ast.literal_eval(kw['mode']) == 'step'
    cfg = named(t.body, 'Mod4EnvCfg', ast.ClassDef)
    events = next(n for n in cfg.body if isinstance(n, ast.AnnAssign)
                  and isinstance(n.target, ast.Name) and n.target.id == 'events')
    assert expr(events.value) == 'EventCfg()'
    step = named(named(tree(folder / 'mod4_env.py').body, 'Mod4Env', ast.ClassDef).body, 'step', ast.FunctionDef)
    calls = call_rows(step)
    event_call = next(r for r in calls if r['call'].startswith('self.event_manager.apply('))
    assert "mode='step'" in event_call['call']
    super_call = next(r for r in calls if r['call'].startswith('super().step('))
    assert event_call['line'] < super_call['line']
    return dict(status='SOURCE_CONFIRMED_RUNTIME_BINDING_UNKNOWN', entry=source_pin(entry),
                own_local_MRO=chain, SDK_terminal=external,
                gas_registration=dict(**source_pin(task_file, registration), expression=expr(registration)),
                cfg_events=dict(**source_pin(task_file, events), expression=expr(events)),
                event_before_SDK_step=dict(**source_pin(folder / 'mod4_env.py', step),
                                           event_call=event_call, super_call=super_call))


def assertions_and_key_pins():
    folder = TASKS / 'E3/runtime/isaac/mod4'
    defs = [
        (ROOT/'source_phase1_actuation_capture_v1/actuation_tap.py', 'ActuationTap.__init__'),
        (ROOT/'source_phase1_actuation_capture_v1/actuation_tap.py', 'ActuationTap._patch'),
        (ROOT/'source_phase1_capture_evidence_verifier_v1/capture_evidence_verifier_v1.py', 'integer'),
        (ROOT/'source_phase1_capture_evidence_verifier_v1/capture_evidence_verifier_v1.py', 'actuation_component'),
        (ROOT/'discovery/sdk_reward_command_call_order_v1/envs/manager_based_rl_env.py', 'ManagerBasedRLEnv.step'),
        (folder/'mod4_env.py', 'Mod4Env.step'),
        (folder/'skills_isaac.py', 'gas_spring_preload'),
        (folder/'action_delay_sdk_adapter.py', 'PhysicalActionDelayAdapter._wrap'),
        (folder/'mod4v1_fresh_dr_guard.py', 'configure_new_task'),
        (folder/'e3_recovery_runtime_v1.py', 'configure'),
        (folder/'e3_recovery_runtime_v1.py', 'RecoveryEnv.step'),
        (folder/'train_mod4v1_e3.py', 'build_env'),
        (folder/'mild_dr.py', 'configure'),
        (folder/'explicit_pd_sdk_adapter.py', 'ExplicitPDSDK.apply'),
        (folder/'spring_pressure_training_env.py', 'LearningSpringPressure.apply'),
        (folder/'gas_damping_sdk_adapter.py', 'GasDampingSDK.apply'),
        (ROOT/'source_phase1_capture_worker_v4/phase1_capture_observer.py', 'verify_actuation_binding'),
    ]
    pins = []
    for path, qual in defs:
        node = tree(path)
        for name in qual.split('.'):
            try:
                node = named(node.body, name, (ast.ClassDef, ast.FunctionDef))
            except StopIteration as exc:
                raise AssertionError(f'Missing exact source definition: {path}:{qual}') from exc
        pins.append(dict(qualname=qual, **source_pin(path, node)))
    tap_path = defs[0][0]
    tap = raw(tap_path).decode('utf-8')
    critical_tap = ['seq = tap.sequence;tap.sequence += 1',
                   'tick = counter-1 if kind in ("term_apply","target_write") and type(counter) is int else counter',
                   'event["parent_term_apply_seq"] = tap.context[-1] if tap.context else None',
                   'if kind=="term_apply":tap.context.append(seq)',
                   'if kind=="term_apply":tap.context.pop()',
                   'specs.append((asset,name,"target_write",group))']
    assert all(line in tap for line in critical_tap)
    core = raw(defs[4][0]).decode('utf-8').splitlines()
    assert 'self.action_manager.process_action(' in core[192]
    assert 'self._sim_step_counter += 1' in core[214]
    assert 'self.action_manager.apply_action()' in core[216]
    assert 'self._sim_step_counter += self.cfg.decimation' in core[202]
    adapter = raw(folder/'action_delay_sdk_adapter.py').decode('utf-8').splitlines()
    assert 'adapter.queue.submit(' in adapter[36] and 'int(adapter.env._sim_step_counter)' in adapter[36]
    assert 'tick=int(adapter.env._sim_step_counter)-1' in adapter[40]
    assert 'value=adapter.queue.apply(key,tick)' in adapter[42]
    assert 'try:original_apply()' in adapter[44]
    setters = []
    for path in sorted(folder.glob('*.py')):
        t = tree(path)
        calls = [n for n in ast.walk(t) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                 and n.func.attr.startswith('set_joint_') and n.func.attr.endswith('_target')]
        if calls:
            for n in sorted(calls, key=lambda x: x.lineno):
                setters.append(dict(**source_pin(path, n), expression=expr(n),
                    reachable_registered_precontrol_event=path.name == 'skills_isaac.py' and n.lineno == 474,
                    standalone_probe_main_guard=path.name == 'probe_mimic.py'))
    assert [(Path(n['path']).name,n['line']) for n in setters] == [
        ('probe_mimic.py',114),('probe_mimic.py',115),('probe_mimic.py',116),('skills_isaac.py',474)]
    return pins, setters


def build():
    old_manifest = json.loads(raw(MANIFEST))
    role_result = {r:audit_role(r, old_manifest['roles'][r]) for r in ROLES}
    assert len({r['event_before_SDK_step']['sha256'] for r in role_result.values()}) == 1
    pins, setters = assertions_and_key_pins()
    aggregate = json.loads(raw(SCALAR))
    locator = aggregate['receipt']['locator'] if 'receipt' in aggregate else aggregate.get('locator')
    assert type(locator) is dict, 'Allowed scalar layout changed'
    frame = next(n for n in locator['frames'] if n['function'] == 'actuation_component')
    event = {name:v['value'] for name,v in frame['event'].items()}
    assert event == dict(seq=0, kind='target_write', group='legs', tick=-1)
    assert frame['window_control_index']['value'] == 0
    pure = ROOT/'source_phase1_capture_evidence_verifier_v1/capture_evidence_verifier_v1.py'
    assert source_pin(pure)['sha256'] == locator['expected_pure_SHA256'] == '2b4ae157a54ea59711556cb8dc02c18151db54afc5b5d0dcff95bc0c5a86e979'
    for path, before in list(READ_PINS.items()):
        assert source_pin(Path(path)) == before
    return dict(kind='UNPARENTED_TARGET_WRITER_INDEPENDENT_SOURCE_AUDIT_V1', source_only=True,
        catalog_selection=dict(matching_skill=None,reason='Available Office/ACL catalog has no RL/source audit skill',
                               tools=['read','glob','grep','approved Python314 -B stdlib/AST']),
        native_enabled=False, exact=False, status='SOURCE_CHECKS_PASS_ACTUAL_CALLER_UNKNOWN',
        allowed_actual_scalar=dict(aggregate=source_pin(SCALAR), control_index=0, **event,
            direct_caller='UNKNOWN', actual_joint_ids='UNKNOWN', actual_target_width='UNKNOWN',
            actual_parent_field='NOT_EXPORTED_IN_ALLOWED_SCALAR', proves_queue_apply_negative_one=False,
            gate1=locator['gate1'], stage2_GO=locator['stage2_GO']),
        source_implications=dict(
            seq_zero_has_no_prior_tapped_term_apply=True,
            parent_none_in_current_C1_model='DERIVED_IF_CURRENT_SOURCE_IS_ACTUAL_BINDING_NOT_DIRECTLY_EXPORTED',
            counter_zero='DERIVED_FROM_C1_TARGET_TICK_MINUS_ONE_RULE_AND_TYPED_MINUS_ONE_NOT_DIRECT_COUNTER_EXPORT',
            gas_preload_registered_in_cfg=True,
            gas_event_called_before_process_and_counter_increment='CONDITIONAL_ON_ORIGINAL_EVENTMANAGER_DISPATCH_AND_LIVE_BINDING',
            setter_method_does_not_identify_control_group=True,
            gas_as_actual_seq_zero_caller='UNKNOWN'),
        role_MRO_and_event_registration=role_result,
        exact_function_pins=pins,
        E3_direct_setter_inventory=setters,
        source_inventory_scope='All E3 runtime/isaac/mod4/*.py AST direct calls; not dynamic SDK setters',
        missing_SDK_source=['event_manager.py','action_manager.py','joint_actions.py','articulation target setter implementation','ManagerBasedEnv counter initialization/reset implementation'],
        unavailable_SDK_search='glob exact file names and grep class/functions over R *.py found only fake target setters; no target modules imported',
        obligations_unchanged=['real queue submit/apply ticks and nonnegative integer range','8 apply callbacks per group per control',
                               '0/1/2 physics tick lag and exact queue transition','same original action/call/RNG/queue/reset order',
                               'physical DR/H1/mothers/acceptance','native/actor35/physical readback remain unproven'],
        whole_actual_FINAL_opened=False, raw_trace_opened=False, target_code_imported_or_executed=False,
        source_reads_unchanged=True,
        audit_input_pins=[READ_PINS[p] for p in sorted(READ_PINS) if not p.endswith('.py')])


def main():
    result = build()
    target = HERE/'SOURCE_AUDIT.json'
    with target.open('x', encoding='utf-8') as stream:
        json.dump(result, stream, indent=2, ensure_ascii=False)
        stream.write('\n')
    print(json.dumps(dict(status=result['status'], roles=len(result['role_MRO_and_event_registration']),
                         exact_functions=len(result['exact_function_pins']),
                         E3_direct_setter_calls=len(result['E3_direct_setter_inventory']),
                         native_enabled=False, exact=False, output=str(target)), indent=2))


if __name__ == '__main__':
    main()
