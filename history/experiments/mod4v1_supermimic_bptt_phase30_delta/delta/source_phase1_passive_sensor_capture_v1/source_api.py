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


if __name__ == '__main__':
    # Explicit NEW output, not a raw per-tick log.
    out = HERE / 'SOURCE_API_MANIFEST.json'
    if out.exists():
        raise SystemExit('Manifest already exists; review before regenerating')
    out.write_text(json.dumps(build_manifest(), indent=2, ensure_ascii=False), encoding='utf-8')
    print(str(out))
