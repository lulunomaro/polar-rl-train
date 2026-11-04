"""Source-only pins and fail-closed runtime inspection; never imports target code.

All target reads are .py source bytes. No SDK, PT, process, locks or ledger access.
Run with the approved stdlib Python -B; output only inside this NEW directory.
"""
from __future__ import annotations
import ast
import hashlib
import inspect
import json
import marshal
from pathlib import Path
import sys
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
ROLES = ('E0', 'E2', 'E3', 'W35', 'CURB_PROTECTED878',
         'CURB_INDEPENDENT113', 'SLOPE135', 'SLOPE_INDEPENDENT50')
CHANNELS = {'base_ang_vel': 3, 'projected_gravity': 3,
            'leg_pos': 4, 'leg_vel': 4, 'wheel_vel': 2}
SCALES = {'base_ang_vel': .5, 'projected_gravity': 1.,
          'leg_pos': 1., 'leg_vel': .1, 'wheel_vel': .1}


def sha(path):
    path = Path(path)
    if path.suffix != '.py':
        raise ValueError('Only Python source is inspectable')
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _nodes(tree, prefix=''):
    for node in tree.body:
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            qual = prefix + node.name
            yield qual, node
            nested = qual + ('.<locals>.' if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) else '.')
            yield from _nodes(node, nested)


def pin(path, module, qualname):
    path = Path(path).resolve()
    text = path.read_text(encoding='utf-8')
    node = dict(_nodes(ast.parse(text)))[qualname]
    result = dict(module=module, qualname=qualname, source_path=str(path),
                  source_sha256=sha(path), definition_line=node.lineno,
                  end_line=node.end_lineno,
                  code_firstlineno=min([node.lineno] + [x.lineno for x in node.decorator_list]))
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        a = node.args
        result['parameters'] = [x.arg for x in a.posonlyargs + a.args]
        result['vararg'] = a.vararg.arg if a.vararg else None
        result['kwonly'] = [x.arg for x in a.kwonlyargs]
        result['kwarg'] = a.kwarg.arg if a.kwarg else None
        result['positional_default_expressions'] = [ast.unparse(x) for x in a.defaults]
    return result


def _source_class_chain(folder, module, name, seen=()):
    """Resolve only explicit local ImportFrom aliases and single inheritance."""
    path = folder / (module + '.py')
    if not path.is_file():
        return []  # SDK base: explicitly outside local task chain
    key = (module, name)
    if key in seen:
        raise ValueError('Cyclic local class chain')
    tree = ast.parse(path.read_text(encoding='utf-8'))
    imports = {a.asname or a.name: (n.module, a.name)
               for n in tree.body if isinstance(n, ast.ImportFrom) for a in n.names}
    classes = {n.name: n for n in tree.body if isinstance(n, ast.ClassDef)}
    if name not in classes:
        next_module, next_name = imports[name]
        return _source_class_chain(folder, next_module, next_name, seen + (key,))
    node = classes[name]
    chain = [pin(path, module, name)]
    if node.bases:
        if len(node.bases) != 1 or not isinstance(node.bases[0], ast.Name):
            raise ValueError('Review non-single/local inheritance explicitly')
        base = node.bases[0].id
        if base in classes:
            chain += _source_class_chain(folder, module, base, seen + (key,))
        elif base in imports:
            m, n = imports[base]
            chain += _source_class_chain(folder, m, n, seen + (key,))
    return chain


def build_manifest(root=ROOT):
    root = Path(root).resolve()
    bridge_path = root / 'source_runtime/native_supermimic_bridge.py'
    worker_path = root / 'source_native_v6_runtime_compat/_SOURCE_INPUT/sealed_source/worker_supermimic_bptt_app_close_candidate_v5.py'
    manifest = dict(kind='PASSIVE_SENSOR_SOURCE_API_V1', source_only=True,
                    native_enabled=False, exact=False, roles={},
                    bridge=pin(bridge_path, 'native_supermimic_bridge', 'NativeTaskBridge._termination_capture'),
                    worker=pin(worker_path, 'worker_supermimic_bptt_app_close_candidate_v5', 'main'))
    for role in ROLES:
        folder = root / 'discovery/reward_command_audit_v1' / role / 'runtime/isaac/mod4'
        if role in ('E0', 'E2', 'E3', 'W35'):
            entry = 'train_mod4v1_' + role.lower() + '.py'
        else:
            metadata = json.loads((folder.parents[2] / 'E1_CANONICAL_SOURCE_METADATA.json').read_text(encoding='utf-8'))
            entry = metadata['entry']
        tree = ast.parse((folder / entry).read_text(encoding='utf-8'))
        imports = {a.asname or a.name: (n.module, a.name)
                   for n in tree.body if isinstance(n, ast.ImportFrom) for a in n.names}
        env_module, env_name = imports['Mod4Env']
        chain = _source_class_chain(folder, env_module, env_name)
        reset = None
        for c in chain:
            try:
                reset = pin(c['source_path'], c['module'], c['qualname'] + '._reset_idx')
                break
            except KeyError:
                pass
        pins = {}
        for label, module, qual in (
            ('feedback', 'feedback_delay_runtime', 'feedback'),
            ('sensor_state', 'sensor_a0_runtime', 'state'),
            ('delay_state', 'feedback_delay_runtime', 'delay_state'),
            ('base_ang_vel', 'feedback_delay_runtime', 'base_ang_vel'),
            ('projected_gravity', 'feedback_delay_runtime', 'projected_gravity'),
            ('leg_pos', 'feedback_delay_runtime', 'leg_pos'),
            ('joint_vel', 'feedback_delay_runtime', 'joint_vel'),
            ('sensor_class', 'sensor_mild_math', 'SensorCorruption'),
            ('sensor_apply', 'sensor_mild_math', 'SensorCorruption.apply'),
            ('sensor_reset', 'sensor_mild_math', 'SensorCorruption.reset'),
            ('delay_class', 'feedback_delay_mild', 'FeedbackDelay'),
            ('delay_apply', 'feedback_delay_mild', 'FeedbackDelay.apply'),
            ('delay_reset', 'feedback_delay_mild', 'FeedbackDelay.reset'),
            ('sampling_update', 'feedback_delay_runtime', 'DelaySensorMod4Env._install_feedback_100hz_sampling.<locals>.update')):
            pins[label] = pin(folder / (module + '.py'), module, qual)
        pins['env_reset'] = reset
        sdk_path = root / 'discovery/sdk_reward_command_call_order_v1/envs/mdp/observations.py'
        sdk_pins = {name: pin(sdk_path, 'isaaclab.envs.mdp.observations', name)
                    for name in ('base_ang_vel', 'projected_gravity', 'joint_pos_rel', 'joint_vel_rel')}
        manifest['roles'][role] = dict(entry=pin(folder / entry, Path(entry).stem, 'build_env'),
                                      env_mro_local=chain, pins=pins, sdk_observation_pins=sdk_pins,
                                      task_source=dict(source_path=str(folder / 'mod4_task.py'), source_sha256=sha(folder / 'mod4_task.py')))
        manifest['roles'][role]['reset_chain'] = build_reset_chain_manifest(folder, chain, reset)
    manifest['source_revision'] = 2
    manifest['reset_binding_contract'] = 'FIXED_EXISTING_INSTANCE_WRAPPERS_THEN_CLASS_DESCRIPTOR_V2'
    manifest['sdk_references'] = [dict(source_path=str(p), source_sha256=sha(p)) for p in (
        root / 'discovery/sdk_reward_command_call_order_v1/envs/mdp/observations.py',
        root / 'discovery/sdk_reward_command_call_order_v1/envs/manager_based_rl_env.py',
        root / 'discovery/sdk_reset_cache_backend_v2/backend/articulation_data.py')]
    return manifest


def _code_key(code):
    """Ignore deployment path only; reject changed live bytecode/constant trees."""
    consts = tuple(_code_key(v) if isinstance(v, types.CodeType) else v for v in code.co_consts)
    return (code.co_name, code.co_qualname, code.co_argcount, code.co_posonlyargcount,
            code.co_kwonlyargcount, code.co_nlocals, code.co_flags, code.co_code,
            consts, code.co_names, code.co_varnames, code.co_freevars, code.co_cellvars,
            code.co_firstlineno, code.co_linetable, code.co_exceptiontable)


def _find_code(code, qualname):
    if code.co_qualname == qualname:
        return code
    for child in code.co_consts:
        if isinstance(child, types.CodeType):
            found = _find_code(child, qualname)
            if found is not None:
                return found
    return None


def verify_callable(value, expected):
    """Read actual callable's module/code/source, without executing target functions."""
    fn = value.__func__ if inspect.ismethod(value) else value
    fn = inspect.unwrap(fn)
    if not inspect.isfunction(fn):
        raise ValueError('Expected a Python function: ' + expected['qualname'])
    code = fn.__code__
    path = Path(code.co_filename).resolve()
    if fn.__module__ != expected['module'] or fn.__qualname__ != expected['qualname']:
        raise ValueError('Function identity mismatch: ' + expected['qualname'])
    if sha(path) != expected['source_sha256'] or code.co_firstlineno != expected['code_firstlineno']:
        raise ValueError('Source hash/line mismatch: ' + expected['qualname'])
    compiled = compile(path.read_text(encoding='utf-8'), str(path), 'exec', dont_inherit=True, optimize=sys.flags.optimize)
    wanted = _find_code(compiled, expected['qualname'])
    if wanted is None or _code_key(code) != _code_key(wanted):
        raise ValueError('Live bytecode differs from pinned source: ' + expected['qualname'])
    args = list(code.co_varnames[:code.co_argcount])
    if args != expected['parameters']:
        raise ValueError('Signature parameter mismatch: ' + expected['qualname'])
    return dict(module=fn.__module__, qualname=fn.__qualname__, source_path=str(path),
                source_sha256=sha(path), code_firstlineno=code.co_firstlineno,
                signature=str(inspect.signature(fn, follow_wrapped=False)),
                defaults_identity=[id(v) for v in (fn.__defaults__ or ())],
                live_bytecode_matches_source=True)


def verify_class(cls, expected):
    if cls.__module__ != expected['module'] or cls.__qualname__ != expected['qualname']:
        raise ValueError('Class identity mismatch: ' + expected['qualname'])
    module = sys.modules.get(cls.__module__)
    if module is None or sha(module.__file__) != expected['source_sha256']:
        raise ValueError('Class module hash mismatch: ' + expected['qualname'])
    if module.__dict__.get(cls.__name__) is not cls:
        raise ValueError('Class differs from active module binding')
    return dict(module=cls.__module__, qualname=cls.__qualname__,
                source_path=str(Path(module.__file__).resolve()), source_sha256=sha(module.__file__))


def closure_functions(fn):
    """Walk only already-bound Python closure cells, never properties or SDK getters."""
    seen = set()
    stack = [fn]
    while stack:
        fn = stack.pop()
        if inspect.ismethod(fn):
            fn = fn.__func__
        if not inspect.isfunction(fn) or id(fn) in seen:
            continue
        seen.add(id(fn))
        yield fn
        for cell in fn.__closure__ or ():
            try:
                child = cell.cell_contents
            except ValueError:
                continue
            if inspect.isfunction(child) or inspect.ismethod(child):
                stack.append(child)


# Fixed SOURCE declarations: outer-to-inner. Runtime never generates expected pins.
_RESET_LAYERS = (
    ('_explicit_pd', 'explicit_pd_sdk_adapter', 'ExplicitPDSDK',
     'explicit_pd_sdk_adapter', 'ExplicitPDSDK'),
    ('_chassis_com', 'chassis_com_pose_roundtrip_sdk_adapter', 'ChassisCOMSDK',
     'chassis_com_pose_roundtrip_sdk_adapter', 'ChassisCOMSDK'),
    ('_gas_damping', 'gas_damping_sdk_adapter', 'GasDampingSDK',
     'gas_damping_sdk_adapter', 'GasDampingSDK'),
    ('_spring_pressure', 'spring_pressure_index_runtime', 'SpringPressureSDK',
     'spring_pressure_training_env', 'LearningSpringPressure'),
)


def _compiled_pin(path, module, qualname):
    p = pin(path, module, qualname)
    code = _find_code(compile(Path(path).read_text(encoding='utf-8'), str(path), 'exec',
                             dont_inherit=True, optimize=sys.flags.optimize), qualname)
    if code is None:
        raise ValueError('Missing compiled source function: ' + qualname)
    p['freevars'] = list(code.co_freevars)
    return p


def build_reset_chain_manifest(folder, env_chain, endpoint):
    """Per-role SOURCE analysis only; source/constructor failure stays UNKNOWN."""
    result = dict(kind='FIXED_RESET_COMPOSITION_SOURCE_V2', status='UNKNOWN',
                  live_binding='UNKNOWN', source_only=True, layers=[],
                  constructor_order=[], endpoint=endpoint)
    try:
        if endpoint is None:
            raise ValueError('Missing source class reset descriptor')
        positions = {p['qualname']: i for i, p in enumerate(env_chain)}
        if not (positions['ChassisPDMod4Env'] < positions['GasDampingMod4Env'] < positions['SpringPressureMod4Env']):
            raise ValueError('Unreviewed constructor inheritance order')
        # Read/parse each role's own constructor. No cross-role expected-pin copy.
        specs = (
            ('spring_pressure_training_env', 'SpringPressureMod4Env', [('self._spring_pressure', 'LearningSpringPressure')]),
            ('gas_damping_training_env', 'GasDampingMod4Env', [('self._gas_damping', 'GasDampingSDK')]),
            ('chassis_pd_training_env', 'ChassisPDMod4Env', [('self._chassis_com', 'ChassisCOMSDK'), ('self._explicit_pd', 'ExplicitPDSDK')]),
        )
        for module, cls, assignments in specs:
            path = folder / (module + '.py')
            tree = ast.parse(path.read_text(encoding='utf-8'))
            nodes = dict(_nodes(tree))
            ctor = nodes[cls + '.__init__']
            first = ctor.body[0]
            if not isinstance(first, ast.Expr) or not isinstance(first.value, ast.Call) or ast.unparse(first.value.func) != 'super().__init__':
                raise ValueError('Constructor must execute original super first: ' + module)
            imports = {a.asname or a.name: (n.module, a.name)
                       for n in tree.body if isinstance(n, ast.ImportFrom) for a in n.names}
            found = []
            for n in ctor.body:
                if isinstance(n, ast.Assign) and isinstance(n.value, ast.Call):
                    for target in n.targets:
                        if ast.unparse(target) in {x[0] for x in assignments}:
                            found.append((ast.unparse(target), ast.unparse(n.value.func)))
            if found != assignments:
                raise ValueError('Constructor adapter assignments/order changed: ' + module)
            for attr, alias in assignments:
                spec = next(x for x in _RESET_LAYERS if attr == 'self.' + x[0])
                wanted_alias = (spec[3], spec[4])
                if alias in imports:
                    if imports[alias] != wanted_alias:
                        raise ValueError('Adapter constructor import alias changed')
                elif module != spec[3] or alias != spec[4] or alias not in nodes:
                    raise ValueError('Unresolved adapter constructor')
            result['constructor_order'].append(dict(pin=pin(path, module, cls + '.__init__'),
                                                     assignments=[list(x) for x in found]))
        for attr, module, cls, adapter_module, adapter_class in _RESET_LAYERS:
            path = folder / (module + '.py')
            qual = cls + '.__init__.<locals>.reset_idx'
            node = dict(_nodes(ast.parse(path.read_text(encoding='utf-8'))))[qual]
            body = [ast.unparse(x) for x in node.body]
            if body != ['original(ids)', 'adapter.reset(ids)']:
                raise ValueError('Original wrapper composition changed: ' + qual)
            wrapper = _compiled_pin(path, module, qual)
            if wrapper['parameters'] != ['this', 'ids'] or wrapper['freevars'] != ['adapter', 'original']:
                raise ValueError('Unreviewed wrapper signature/freevars')
            adapter_mro = _source_class_chain(folder, adapter_module, adapter_class)
            descriptors = []
            for owner in adapter_mro:
                for name in ('__init__', 'reset'):
                    try:
                        method = _compiled_pin(owner['source_path'], owner['module'], owner['qualname'] + '.' + name)
                    except KeyError:
                        continue
                    descriptors.append(dict(owner=owner['qualname'], name=name, pin=method))
            result['layers'].append(dict(env_attribute=attr, function=wrapper,
                adapter_mro_local=adapter_mro, adapter_descriptors=descriptors,
                required_instance_fields=['env', 'robot', 'component'],
                binding='types.MethodType(function, SAME_ENV)',
                closure_original='NEXT_BOUND_METHOD_SAME_ENV',
                closure_adapter='EXACT_EXISTING_ENV_ATTRIBUTE_INSTANCE'))
        result['endpoint'] = _compiled_pin(endpoint['source_path'], endpoint['module'], endpoint['qualname'])
        result['status'] = 'SOURCE_CONFIRMED_LIVE_UNKNOWN'
    except (KeyError, ValueError, OSError) as error:
        result['source_error'] = type(error).__name__ + ': ' + str(error)[:480]
        result['layers'] = []  # A partial chain is never admitted.
    return result


def _plain_instance_dict(value):
    """Read object memory only: no __getattr__, properties, or SDK accessors."""
    d = object.__getattribute__(value, '__dict__')
    if type(d) is not dict:
        raise ValueError('Expected ordinary instance memory')
    return d


def _closure_values(fn):
    result = {}
    for name, cell in zip(fn.__code__.co_freevars, fn.__closure__ or ()):
        try:
            result[name] = cell.cell_contents
        except ValueError:
            raise ValueError('Empty closure cell: ' + name) from None
    return result


def _verify_raw_function(fn, expected, owner_class=None):
    # Reset wrappers have no __wrapped__; do not unwrap an unknown outer function.
    if type(fn) is not types.FunctionType or '__wrapped__' in fn.__dict__:
        raise ValueError('Require raw, unwrapped pinned reset function')
    receipt = verify_callable(fn, expected)
    if list(fn.__code__.co_freevars) != expected['freevars']:
        raise ValueError('Reset closure variable set differs')
    module = sys.modules.get(expected['module'])
    if module is None or fn.__globals__ is not module.__dict__:
        raise ValueError('Reset function globals differ from active module')
    if sha(module.__file__) != expected['source_sha256']:
        raise ValueError('Reset active module source hash differs')
    # Fixed reset wrappers/descriptors have only constant False defaults or none.
    wanted_defaults = tuple(ast.literal_eval(s) for s in expected['positional_default_expressions'])
    if (fn.__defaults__ or ()) != wanted_defaults or fn.__kwdefaults__:
        raise ValueError('Reset function default arguments differ')
    cells = _closure_values(fn)
    if owner_class is not None:
        expected_cells = {'__class__'} if '__class__' in expected['freevars'] else set()
        if set(cells) != expected_cells or ('__class__' in cells and cells['__class__'] is not owner_class):
            raise ValueError('Reset descriptor __class__ closure differs')
    receipt['freevars'] = list(fn.__code__.co_freevars)
    receipt['raw_function_verified_without_unwrap'] = True
    return receipt


def _observed_function(value, env, slot_adapter=None):
    """Bounded diagnostic metadata, never repr of objects/tensors/state."""
    fn = value.__func__ if type(value) is types.MethodType else value
    row = dict(is_bound_method=type(value) is types.MethodType,
               bound_self_is_env=type(value) is types.MethodType and value.__self__ is env,
               callable_type=type(value).__module__ + '.' + type(value).__qualname__)
    if type(fn) is not types.FunctionType:
        return row
    code = fn.__code__
    row.update(module=fn.__module__, qualname=fn.__qualname__, co_filename=code.co_filename,
               co_firstlineno=code.co_firstlineno, freevars=list(code.co_freevars),
               parameters=list(code.co_varnames[:code.co_argcount]), has_wrapped='__wrapped__' in fn.__dict__)
    try:
        row['source_sha256'] = sha(code.co_filename)
    except (OSError, ValueError):
        row['source_sha256'] = 'UNKNOWN'
    try:
        cells = _closure_values(fn)
        row['closure_names'] = list(cells)
        adapter = cells.get('adapter')
        row['closure_adapter_is_expected_env_slot'] = slot_adapter is not None and adapter is slot_adapter
        row['closure_adapter_env_is_env'] = adapter is not None and _plain_instance_dict(adapter).get('env') is env
        original = cells.get('original')
        row['closure_original_is_bound_same_env'] = type(original) is types.MethodType and original.__self__ is env
    except (AttributeError, TypeError, ValueError):
        row['closure_metadata'] = 'UNKNOWN'
    return row


def diagnose_reset_chain(env, spec, max_nodes=6):
    """Read-only on-demand diagnosis; bounded fixed metadata, no callbacks/files writes."""
    if not 1 <= max_nodes <= 8:
        raise ValueError('Reset diagnostic node bound invalid')
    memory = _plain_instance_dict(env)
    current = memory.get('_reset_idx')
    if current is None:
        for cls in type(env).__mro__:
            if '_reset_idx' in vars(cls):
                current = types.MethodType(vars(cls)['_reset_idx'], env)
                break
    observed, seen = [], set()
    for i in range(max_nodes):
        layers = spec.get('layers', [])
        slot = layers[i]['env_attribute'] if i < len(layers) else None
        adapter = memory.get(slot) if slot else None
        row = _observed_function(current, env, adapter)
        row['expected_env_attribute'] = slot
        observed.append(row)
        fn = current.__func__ if type(current) is types.MethodType else current
        if type(fn) is not types.FunctionType or id(fn) in seen:
            break
        seen.add(id(fn))
        cells = _closure_values(fn)
        if 'original' not in cells:
            break
        current = cells['original']
    return dict(kind='READ_ONLY_BOUNDED_RESET_BINDING_DIAGNOSTIC_V2', source_only=True,
                native_enabled=False, exact=False, expected_status=spec.get('status', 'UNKNOWN'),
                expected=[dict(env_attribute=x['env_attribute'], function=x['function']) for x in spec.get('layers', [])],
                expected_endpoint=spec.get('endpoint'), observed=observed,
                max_nodes=max_nodes, no_task_function_called=True,
                no_SDK_getter_called=True, no_RNG_accessor_called=True)


def _plain_bound_member(obj, name):
    """Resolve Python instance/function slots only, without running a descriptor."""
    memory = _plain_instance_dict(obj)
    if name in memory:
        return memory[name]
    for cls in type(obj).__mro__:
        value = vars(cls).get(name)
        if type(value) is types.FunctionType:
            return types.MethodType(value, obj)
        if name in vars(cls):
            return None  # A property/unknown descriptor is not invoked.
    return None


def diagnose_preflight_bindings(env, bridge, module, role_api, bridge_pin):
    """SOURCE/identity diagnostics only; no SDK getter or observation is executed."""
    out = dict(kind='READ_ONLY_PREFLIGHT_BINDING_METADATA_V2', native_enabled=False,
               exact=False, source_only=True, live_capture_calls='UNKNOWN',
               expected_reset_status=role_api.get('reset_chain', {}).get('status', 'UNKNOWN'),
               expected_bridge=bridge_pin, no_task_function_called=True,
               no_SDK_getter_called=True, no_RNG_accessor_called=True)
    try:
        memory = _plain_instance_dict(env)
        out['environment_MRO'] = [dict(module=c.__module__, qualname=c.__qualname__)
                                  for c in type(env).__mro__[:16]]
        out['existing_component_fields'] = {k: k in memory for k in
            ('_sensor_mild', '_feedback_delay_mild', '_explicit_pd', '_chassis_com', '_gas_damping', '_spring_pressure')}
        out['functions'] = {}
        def observed(label, value, expected=None):
            out['functions'][label] = dict(expected=expected, observed=_observed_function(value, env))
        for attr, label in (('_sensor_mild', 'sensor'), ('_feedback_delay_mild', 'delay')):
            component = memory.get(attr)
            if component is not None:
                for name in ('apply', 'reset'):
                    observed(label + '_' + name, _plain_bound_member(component, name), role_api['pins'].get(label + '_' + name))
        for name in ('feedback', 'sensor_state', 'delay_state', 'base_ang_vel', 'projected_gravity', 'leg_pos', 'joint_vel'):
            observed(name, vars(module).get(name), role_api['pins'].get(name))
        scene = memory.get('scene')
        if scene is not None:
            update = _plain_bound_member(scene, 'update')
            out['scene_update_closure_functions'] = []
            for i, fn in enumerate(closure_functions(update)):
                if i >= 8:
                    break
                out['scene_update_closure_functions'].append(_observed_function(fn, env))
        termination = memory.get('termination_manager')
        if termination is not None:
            observed('terminal_compute', _plain_bound_member(termination, 'compute'), bridge_pin)
        out['bridge_real_is_env'] = _plain_instance_dict(bridge).get('real') is env
        out['reset'] = diagnose_reset_chain(env, role_api.get('reset_chain', {}))
    except (AttributeError, KeyError, TypeError, ValueError, OSError) as error:
        out['diagnostic_incomplete_reason'] = type(error).__name__ + ': ' + str(error)[:320]
    return out


class ResetBindingMismatch(ValueError):
    def __init__(self, detail, diagnostic):
        self.diagnostic = diagnostic
        # Metadata only; native worker trace can publish observed alongside expected.
        super().__init__('Reset composition mismatch: ' + detail + '; diagnostic=' +
                         json.dumps(diagnostic, separators=(',', ':'), ensure_ascii=False))


def verify_existing_reset_chain(env, spec):
    """Verify every existing bound wrapper, then the actual MRO class descriptor.

    Expected pins must come from the sealed NEW SOURCE manifest. Never learn pins
    from live objects; never invoke/replace a reset, adapter, RNG or SDK getter.
    """
    try:
        if spec.get('status') != 'SOURCE_CONFIRMED_LIVE_UNKNOWN' or len(spec['layers']) != 4:
            raise ValueError('Role reset composition SOURCE proof is UNKNOWN')
        memory = _plain_instance_dict(env)
        current = memory.get('_reset_idx')
        if type(current) is not types.MethodType:
            raise ValueError('Missing installed original bound reset wrapper')
        layers, seen = [], set()
        for layer in spec['layers']:
            if type(current) is not types.MethodType or current.__self__ is not env:
                raise ValueError('Reset layer is not bound to the same environment')
            fn = current.__func__
            if id(fn) in seen:
                raise ValueError('Duplicate/cyclic reset wrapper function')
            seen.add(id(fn))
            receipt = _verify_raw_function(fn, layer['function'])
            cells = _closure_values(fn)
            if set(cells) != {'adapter', 'original'}:
                raise ValueError('Reset wrapper closure pollution')
            adapter = cells['adapter']
            if memory.get(layer['env_attribute']) is not adapter or adapter is None:
                raise ValueError('Reset closure adapter differs from existing env slot: ' + layer['env_attribute'])
            adapter_memory = _plain_instance_dict(adapter)
            if any(x not in adapter_memory for x in layer['required_instance_fields']) or adapter_memory['env'] is not env:
                raise ValueError('Reset adapter initialization/env memory binding differs')
            classes = type(adapter).__mro__
            expected_classes = layer['adapter_mro_local']
            if len(classes) != len(expected_classes) + 1 or classes[-1] is not object:
                raise ValueError('Reset adapter class inheritance differs')
            class_receipts = [verify_class(c, p) for c, p in zip(classes, expected_classes)]
            class_map = {(c.__module__, c.__qualname__): c for c in classes[:-1]}
            descriptors = []
            for p in layer['adapter_descriptors']:
                owner = class_map[(p['pin']['module'], p['owner'])]
                method = vars(owner).get(p['name'])
                descriptors.append(_verify_raw_function(method, p['pin'], owner))
            if 'reset' in adapter_memory:
                raise ValueError('Reset adapter method replaced on instance')
            original = cells['original']
            if type(original) is not types.MethodType or original.__self__ is not env:
                raise ValueError('Reset closure original differs from SAME_ENV bound method')
            layers.append(dict(env_attribute=layer['env_attribute'], function=receipt,
                               adapter_MRO=class_receipts, adapter_descriptors=descriptors,
                               closure_adapter_is_existing_env_slot=True,
                               closure_original_same_env=True))
            current = original
        endpoint = spec['endpoint']
        if type(current) is not types.MethodType or current.__self__ is not env:
            raise ValueError('Reset terminal descriptor bound to foreign environment')
        owner = next((c for c in type(env).__mro__ if '_reset_idx' in vars(c)), None)
        if owner is None or current.__func__ is not vars(owner)['_reset_idx']:
            raise ValueError('Reset chain does not end at actual first MRO class descriptor')
        owner_receipt = verify_class(owner, dict(endpoint, qualname=endpoint['qualname'].rsplit('.', 1)[0]))
        terminal = _verify_raw_function(current.__func__, endpoint, owner)
        return dict(kind='FIXED_EXISTING_RESET_COMPOSITION_VERIFIED_V2',
                    layers=layers, terminal_descriptor=terminal, terminal_owner=owner_receipt,
                    no_original_function_called=True, no_original_binding_changed=True,
                    native_enabled=False, exact=False)
    except (AttributeError, KeyError, TypeError, ValueError, OSError) as error:
        try:
            diagnostic = diagnose_reset_chain(env, spec)
        except (AttributeError, KeyError, TypeError, ValueError, OSError) as diagnostic_error:
            diagnostic = dict(kind='RESET_DIAGNOSTIC_UNAVAILABLE', reason=type(diagnostic_error).__name__,
                              native_enabled=False, exact=False)
        raise ResetBindingMismatch(str(error), diagnostic) from error


if __name__ == '__main__':
    # Explicit NEW output, not a raw per-tick log.
    out = HERE / 'SOURCE_API_MANIFEST.json'
    if out.exists():
        raise SystemExit('Manifest already exists; review before regenerating')
    out.write_text(json.dumps(build_manifest(), indent=2, ensure_ascii=False), encoding='utf-8')
    print(str(out))
