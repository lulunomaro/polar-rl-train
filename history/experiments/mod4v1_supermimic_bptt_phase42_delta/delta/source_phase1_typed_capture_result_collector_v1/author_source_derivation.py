"""Reproducible SOURCE authoring only; never imports or executes an old producer.

Writes the NEW reader/CLI exclusively once. It is not a native entry or collector.
The complete V4 functions not listed below remain whole-source identical.
"""
from pathlib import Path
import ast
import json
import pprint

HERE = Path(__file__).resolve().parent
R = HERE.parent
OLD = R/'source_phase1_capture_result_collector_v4'


def replace_definition(source, name, new_source):
    tree = ast.parse(source)
    found = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name == name]
    assert len(found) == 1, name
    node = found[0]
    lines = source.splitlines(keepends=True)
    return ''.join(lines[:node.lineno-1])+new_source.rstrip()+'\n'+''.join(lines[node.end_lineno:])


WORKER_PROJECTION = '''def worker_projection(value):
    """Copy only path ancestors; never mutate the original whole parsed cache.

    Unlike V4's whitelist, all unknown metadata survives. Only these explicit
    typed payload fields are removed. Overflow is not rescued by more cropping.
    """
    if type(value) is not dict:
        return value
    require('_collector_typed_payload_projection' not in value, 'projection receipt namespace already occupied')
    result = dict(value); removed = []
    for path in TC.REMOVAL_PATHS:
        pieces = path.split('.'); original = value; target = result
        for key in pieces[:-1]:
            if type(original) is not dict or type(original.get(key)) is not dict:
                break
            child = original[key]
            if target.get(key) is child:
                target[key] = dict(child)
            original = child; target = target[key]
        else:
            if type(original) is dict and pieces[-1] in original:
                target.pop(pieces[-1], None); removed.append(path)
    result['_collector_typed_payload_projection'] = dict(
        kind='EXPLICIT_TYPED_PAYLOAD_METADATA_PROJECTION_V1',
        original_worker_payload_retained=False, projected_metadata_is_not_original_bytes=True,
        removed_paths=removed, allowed_removal_paths=list(TC.REMOVAL_PATHS),
        unknown_fields_retained=True, no_extra_overflow_cropping=True)
    return result
'''

READER = '''class MetadataReader:
    """Bounded whole bytes once, with post-read and cached signature observations.

    A changed/disappeared immutable file is an error; no reopen/hash/parse repair.
    Original bytes SHA is never a digest of the exported metadata projection.
    """
    def __init__(self, root):
        self.root = Path(root); self.cache = {}; self.info = {}; self.signatures = {}; self.errors = []

    def path(self, name):
        require(name in SMALL+BIG+LOGS or name == 'CAPTURE_SOURCE_INDEX.json', 'nonmetadata alias rejected')
        return safe_source_path(self.root, name)

    def observe_cached(self, name):
        path = self.path(name); st = path.stat()
        require(stat.S_ISREG(st.st_mode), 'metadata is not regular')
        require((st.st_size, st.st_mtime_ns) == self.signatures.get(name),
                'immutable metadata changed after sole cached read: '+name)
        self.info[name]['cached_signature_observed_unchanged'] = True
        return self.cache.get(name)

    def read(self, name, *, terminal=False):
        require(name in SMALL+BIG, 'metadata alias rejected')
        if name in BIG:
            require(terminal, 'big FINAL reads only at terminal/cap')
        try:
            if name in BIG and self.info.get(name, {}).get('read_count', 0):
                require(name in self.cache, 'sole immutable read failed; no retry: '+name)
                return self.observe_cached(name)
            path = self.path(name); st = path.stat()
            require(stat.S_ISREG(st.st_mode), 'metadata is not regular')
            signature = (st.st_size, st.st_mtime_ns)
            if name in self.cache and self.signatures[name] == signature:
                return self.cache[name]
            if name in self.cache and name not in MUTABLE:
                raise ValueError('immutable metadata changed after observation: '+name)
            self.info.setdefault(name, dict(read_count=0, bytes=st.st_size, SHA256=None))
            self.info[name]['published_regular_file_observed'] = True
            maximum = TC.BIG_LIMIT if name in BIG else TC.PLAN_LIMIT if name == 'GROUP_PLAN.json' else TC.SMALL_LIMIT
            require(st.st_size <= maximum, 'bounded metadata exceeded: '+name)
            previous = self.info.get(name, {}).get('read_count', 0)
            self.info[name] = dict(status='READ_ATTEMPTED', read_count=previous+1, bytes=st.st_size, published_regular_file_observed=True)
            with path.open('rb') as stream:
                raw = stream.read(maximum+1)
            after = path.stat()
            require(len(raw) <= maximum and len(raw) == st.st_size
                    and (after.st_size, after.st_mtime_ns) == signature,
                    'metadata changed during sole whole bounded read: '+name)
            value = json.loads(raw)
            self.info[name].update(status='READ', SHA256=hashlib.sha256(raw).hexdigest(),
                whole_JSON_read=True, new_capture_trace_fields_parsed=name in BIG,
                trace_payload_exported=False, SHA256_is_whole_original_bytes=True,
                exported_projection_is_not_original_bytes=name in BIG,
                post_read_signature_observed_unchanged=True)
            self.cache[name] = value; self.signatures[name] = signature
            return value
        except FileNotFoundError:
            if name in self.cache:
                self.errors.append(dict(file=name, error='immutable metadata disappeared after sole cached read'))
                self.info[name]['status'] = 'ERROR'
            else:
                self.info.setdefault(name, dict(status='MISSING', read_count=0, bytes=None, SHA256=None))
        except Exception as exc:
            self.errors.append(dict(file=name, error=type(exc).__name__+': '+str(exc)))
            self.info.setdefault(name, dict(read_count=0, bytes=None, SHA256=None))['status'] = 'ERROR'
        return None

    def tail(self, name, maximum=16384):
        try:
            path = self.path(name); st = path.stat()
            require(stat.S_ISREG(st.st_mode), 'log is not regular')
            with path.open('rb') as stream:
                stream.seek(max(0, st.st_size-maximum)); raw = stream.read(maximum)
            return dict(bytes_read=len(raw), source_bytes=st.st_size, tail=raw.decode('utf-8', 'replace'))
        except FileNotFoundError:
            return dict(bytes_read=0, source_bytes=None, tail=None)
        except Exception as exc:
            return dict(bytes_read=None, source_bytes=None, tail=None, error=type(exc).__name__+': '+str(exc))
'''

CLOSURE = '''def safe_source_path(root, name):
    require(type(name) is str and name and not name.startswith('/') and ':' not in name
            and chr(92) not in name and all(p not in ('', '.', '..') for p in name.split('/')),
            'exact own relative SOURCE or metadata path required')
    root = Path(root); path = root/name
    require(root.is_dir() and not root.is_symlink(), 'actual nonlink own root required')
    for item in (path, *path.parents):
        require(not item.is_symlink(), 'SOURCE/metadata symlink component rejected')
    require(path.resolve().is_relative_to(root.resolve()), 'own alias escapes root')
    return path


def whole_source(root, alias, expected):
    path = safe_source_path(root, alias)
    require(path.is_file() and path.stat().st_size <= TC.SMALL_LIMIT, 'bounded whole SOURCE file required: '+alias)
    raw = path.read_bytes()
    require((len(raw), hashlib.sha256(raw).hexdigest()) == tuple(expected), 'whole SOURCE hardpin differs: '+alias)
    return raw


def verify_installed_sources(root):
    """SOURCE-only finite identity check, deliberately not static-baseline admission."""
    raw = whole_source(root, 'CAPTURE_SOURCE_INDEX.json', (TC.INDEX_BYTES, INDEX_SHA))
    index = json.loads(raw)
    abi_raw = whole_source(root, 'PRODUCER_ABI.json', TC.ABI_PIN)
    rows = TC.finite_rows(index, json.loads(abi_raw))
    receipts = []
    for alias, expected in sorted(rows.items()):
        data = whole_source(root, alias, expected)
        receipts.append(dict(relative=alias, bytes=len(data), SHA256=hashlib.sha256(data).hexdigest()))
    whole_source(root, 'phase1_capture_parent_actual_wait_controller_v1.py', (3824, CONTROLLER_SHA))
    return dict(index=index, source_files=receipts, source_aliases=34, overlay_source_aliases=32,
                independent_bootstrap_source_aliases=2, full_static_baseline_verified_by_this_finite_check=False)


def import_complete_metadata_modules(root, verified):
    """Normal complete-module imports; SOURCE fixtures do not call remote ROOT admission."""
    root = Path(root).resolve()
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(root))
    contract = importlib.import_module('phase1_capture_contract')
    runtime = importlib.import_module('phase1_capture_runtime')
    require(Path(runtime.__file__).resolve() == root/'phase1_capture_runtime.py'
            and Path(contract.__file__).resolve() == root/'phase1_capture_contract.py', 'runtime/contract alias differs')
    core = runtime.core(); app = runtime._pinned_module('app_close_semantics_v5', runtime.APP_PIN); base = app._base
    require(Path(core.__file__).resolve() == root/'a1_frozen_eval_runtime_v2.py'
            and Path(app.__file__).resolve() == root/'app_close_semantics_v5.py'
            and Path(base.__file__).resolve() == root/'resume_runtime_contracts_v3.py', 'whole App/Base closure origin differs')
    require(base is sys.modules.get('resume_runtime_contracts_v3'), 'actual Base module object differs')
    forbidden = {'torch', 'numpy', 'isaaclab', 'isaacsim', 'omni', 'pxr', 'carb', 'warp', 'rsl_rl', 'tensordict'}
    require(not any(m.split('.')[0] in forbidden for m in sys.modules), 'native module unexpectedly loaded')
    return dict(index=verified['index'], contract=contract, runtime=runtime, core=core, app=app,
        receipt=dict(source_aliases=34, overlay_source_aliases=32, independent_bootstrap_source_aliases=2,
                     original17=17, full_AppV6_Base_imported=True, source_files=verified['source_files'],
                     full_static_baseline_is_not_finite34=True, native_modules_loaded=[],
                     worker_or_parent_main_called=False, AST_cropped_runtime_or_stub=False))


def install_remote_readonly_guard():
    forbidden = {'torch', 'numpy', 'isaaclab', 'isaacsim', 'omni', 'pxr', 'carb', 'warp', 'rsl_rl', 'tensordict'}
    def guard(event, args):
        if event == 'import' and str(args[0]).split('.')[0] in forbidden:
            raise ValueError('native import in metadata closure: '+str(args[0]))
        if event in ('subprocess.Popen', 'os.system', 'socket.connect', 'socket.connect_ex',
                     'os.kill', 'os.killpg', 'os.remove', 'os.rename', 'os.mkdir', 'os.rmdir',
                     'os.link', 'os.symlink', 'os.truncate', 'fcntl.flock'):
            raise ValueError('lifecycle/network/mutation operation in metadata reader')
        if event == 'open':
            if len(args)>1 and type(args[1]) is str and any(c in args[1] for c in 'wax+'):
                raise ValueError('remote reader never writes files')
            if len(args)>2 and type(args[2]) is int and args[2] & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND):
                raise ValueError('remote reader never opens writable descriptors')
            if args and isinstance(args[0], (str, bytes)):
                p = os.fsdecode(args[0]).lower().replace(chr(92), '/')
                if p.endswith(('.pt', '.pth', '.npz', '.npy', '.jsonl', '.lock')) or '/budgets/' in p:
                    raise ValueError('model/raw/lock/budget read rejected in metadata reader')
    sys.addaudithook(guard)


def load_metadata_closure(root):
    """Future remote production path: full typed34, full modules, original ROOT gate."""
    verified = verify_installed_sources(root)
    install_remote_readonly_guard()
    closure = import_complete_metadata_modules(root, verified)
    closure['runtime'].validate_installed_root(Path(root), closure['runtime'].HERE)
    return closure
'''

REMOTE_MAIN = '''def encoded_packet(value):
    raw = (json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False)+'\\n').encode('utf-8')
    require(len(raw) <= TC.EXPORT_LIMIT, 'complete metadata packet including LF exceeds16MiB; no extra cropping')
    return raw


def remote_main(dispatch, *, cap_seconds=6000, interval_seconds=20):
    validate_dispatch(dispatch)
    reader = MetadataReader(dispatch['root']); closure = None; validation = None
    try:
        closure = load_metadata_closure(reader.root)
    except Exception as exc:
        reader.errors.append(dict(check='real_complete_typed_metadata_import', error=type(exc).__name__+': '+str(exc)))
    observed = watch(reader, cap_seconds=cap_seconds, interval_seconds=interval_seconds)
    if closure is not None:
        try:
            TC.validate_materialization(reader.cache.get(TC.COMPLETE), reader.cache.get('GROUP_PLAN.json'), reader.info, dispatch)
            validation = validate_terminal_cache(reader, dispatch, closure)
            validation['typed_materialization_raw_plan_binding'] = True
        except Exception as exc:
            validation = dict(errors=[dict(check='original_cached_metadata_predicates', error=type(exc).__name__+': '+str(exc))])
    for name in tuple(reader.cache):
        if name not in MUTABLE:
            reader.read(name, terminal=name in BIG)  # signature only for cached immutable bytes
    documents = {name: project(name, value) for name, value in reader.cache.items()}
    for name in BIG:
        if name in reader.info:
            reader.info[name]['explicit_payload_removal_paths'] = list(TC.REMOVAL_PATHS)
            reader.info[name]['projection_digest_is_not_whole_original_digest'] = True
    packet = dict(kind='PHASE1_TYPED_CAPTURE_OWN_METADATA_PACKET_V1', source_version=SOURCE_VERSION,
        source_derivation=SOURCE_DERIVATION, documents=documents, file_metadata=reader.info,
        collector_errors=reader.errors, metadata_validation=validation,
        closure=closure['receipt'] if closure is not None else None, watch=observed,
        log_tails={name: reader.tail(name) for name in LOGS},
        trace_payload_exported=False, whole_original_bytes_hash_before_projection=True,
        projected_metadata_is_not_original_bytes=True, no_remote_writes=True,
        source_grade_is_not_SDK_quality_or_scientific_proof=True)
    sys.stdout.write(encoded_packet(packet).decode('utf-8'))
'''


def derive_once():
    contract_path = HERE/'typed_collector_contract.py'
    text = contract_path.read_text(encoding='utf-8')
    finite = json.loads((R/'source_phase1_typed_native_capture_v1/FINITE_SOURCE_BUNDLE.json').read_bytes())
    rows = tuple(dict(relative=row['install_relative'], bytes=row['bytes'], SHA256=row['SHA256'])
                 for row in finite['full_module_files'])
    assert len(rows) == 34 and text.count('FINITE_ROWS = ()') == 1
    contract_path.write_text(text.replace('FINITE_ROWS = ()', 'FINITE_ROWS = '+pprint.pformat(rows, width=110)), encoding='utf-8', newline='\n')
    source = (OLD/'remote_metadata_reader.py').read_text(encoding='utf-8')
    start = source.index('PURPOSE = '); end = source.index('CONTROLLER_SHA = ', start)
    source = source[:start]+"import typed_collector_contract as TC\nPURPOSE = TC.PURPOSE\nPARENT_SHA = 'd5575ff2e670fd18ea0a09d9f3d5c05c46bf606a027fcb84d97c6e34a88a2b41'\nINDEX_SHA = TC.INDEX_SHA\nSOURCE_VERSION = TC.SOURCE_VERSION\nSOURCE_DERIVATION = TC.SOURCE_DERIVATION\n"+source[end:]
    source = source.replace("'cases/E3/APP_CLOSE_RETURNED_PHASE1_CAPTURE_V1.json', 'cases/E3/WORKER_ERROR.json')",
                            "'cases/E3/APP_CLOSE_RETURNED_PHASE1_CAPTURE_V1.json', 'cases/E3/WORKER_ERROR.json',\n    'STAGE_ERROR_PHASE1_CAPTURE_V1.json', 'cases/E3/TYPED_CAPTURE_INCOMPLETE_V1.json')")
    source = replace_definition(source, 'worker_projection', WORKER_PROJECTION)
    source = replace_definition(source, 'MetadataReader', READER)
    source = replace_definition(source, 'load_metadata_closure', CLOSURE)
    source = replace_definition(source, 'remote_main', REMOTE_MAIN)
    with (HERE/'remote_metadata_reader.py').open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(source)
    cli = (OLD/'collect_capture_result.py').read_text(encoding='utf-8')
    cli = cli.replace('from remote_metadata_reader import (', 'import typed_collector_contract as TC\nfrom remote_metadata_reader import (')
    changes = {
        "'PHASE1_PASSIVE_CAPTURE_E3_ONLY_PLAN_V1'": 'TC.PLAN_KIND',
        "'PHASE1_CAPTURE_CLOSED_SOURCE_GRADE_V1'": 'TC.GRADE_KIND',
        "'PHASE1_PASSIVE_CAPTURE_GROUP_FINAL_V1'": 'TC.GROUP_FINAL_KIND',
        "'PHASE1_PASSIVE_CAPTURE_COMMON_START_V1'": 'TC.COMMON_START_KIND',
        "'PHASE1_PASSIVE_CAPTURE_E3_N80_TASK_V1'": 'TC.TASK_KIND',
        "'PHASE1_PASSIVE_CAPTURE_E3_N80_FINAL_V1'": 'TC.FINAL_KIND',
        "'PHASE1_CAPTURE_RESULT_COLLECTION_CLOSED_V1'": "'PHASE1_TYPED_CAPTURE_RESULT_COLLECTION_CLOSED_V1'",
        "'PHASE1_CAPTURE_OWN_METADATA_PACKET_V1'": "'PHASE1_TYPED_CAPTURE_OWN_METADATA_PACKET_V1'",
        "closure.get('source_aliases') == 27": "type(closure.get('source_aliases')) is int and closure['source_aliases'] == 34\n        and type(closure.get('overlay_source_aliases')) is int and closure['overlay_source_aliases'] == 32\n        and type(closure.get('independent_bootstrap_source_aliases')) is int and closure['independent_bootstrap_source_aliases'] == 2",
        "('original_capture_plan','original_capture_preclose','original_app_close_metadata')": "('original_capture_plan','original_capture_preclose','original_app_close_metadata','typed_materialization_raw_plan_binding')",
    }
    for old, new in changes.items():
        assert old in cli, old
        cli = cli.replace(old, new)
    needle = "    check('materialization_is_not_admission',"
    assert cli.count(needle) == 1
    cli = cli.replace(needle, "    try:\n        TC.validate_materialization(stage, plan, infos, dispatch)\n        check('actual_typed_materialization_and_raw_plan_binding', True)\n    except Exception as exc:\n        check('actual_typed_materialization_and_raw_plan_binding', False)\n        errors.append(dict(check='actual_typed_materialization_and_raw_plan_binding', error=type(exc).__name__+': '+str(exc)))\n"+needle)
    cli = cli.replace("and ready.get('role') == 'E3' and started.get('role') == 'E3')",
        "and ready.get('role') == 'E3' and started.get('role') == 'E3'\n        and ready.get('kind') == 'PHASE1_TYPED_NATIVE_CAPTURE_SOURCE_V1'\n        and started.get('kind') == 'PHASE1_TYPED_NATIVE_CAPTURE_SOURCE_V1')")
    cli = cli.replace("and worker.get('passed_execution') is True and controls == task.get('controls') and controls in (64,128)",
        "and worker.get('passed_execution') is True and controls == task.get('controls') and controls in (64,128)\n        and worker.get('typed_producer_schema') == TC.SCHEMA and task.get('typed_producer_schema') == TC.SCHEMA")
    cli = cli.replace("'GROUP_ABORT.json','GROUP_STARTUP_ABORT.json','PHASE1_CAPTURE_PARENT_CONTROLLER_ERROR_V1.json'))]",
        "'GROUP_ABORT.json','GROUP_STARTUP_ABORT.json','PHASE1_CAPTURE_PARENT_CONTROLLER_ERROR_V1.json',\n        'STAGE_ERROR_PHASE1_CAPTURE_V1.json','TYPED_CAPTURE_INCOMPLETE_V1.json'))]")
    cli = cli.replace("    source = (HERE/'remote_metadata_reader.py').read_text(encoding='utf-8')",
        "    contract_source = (HERE/'typed_collector_contract.py').read_text(encoding='utf-8')\n    source = (HERE/'remote_metadata_reader.py').read_text(encoding='utf-8')\n    source = 'import types,sys\\n_m=types.ModuleType(\\\"typed_collector_contract\\\");sys.modules[_m.__name__]=_m\\nexec('+repr(contract_source)+',_m.__dict__)\\n'+source")
    for name in ('remote_metadata_reader.py',):
        ast.parse((HERE/name).read_text(encoding='utf-8'))
    ast.parse(cli)
    with (HERE/'collect_capture_result.py').open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(cli)
    print('NEW SOURCE derivation created; no old functions executed; no tests or collection run')


if __name__ == '__main__':
    derive_once()
