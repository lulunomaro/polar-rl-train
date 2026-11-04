"""Future read-only own-root metadata reader. Definitions only; no local collection.

The one terminal read of each own published FINAL includes its embedded capture
trace. It is hashed/parsed once, cached, and exported as a small metadata projection.
No source/metadata remote file is created, and no native lifecycle is controlled.
"""
from pathlib import Path, PurePosixPath
import hashlib
import importlib
import json
import os
import stat
import sys
import time

BASE = '/home/lc01/Zonglin Li/zonglin2'
PREFIX = 'MOD4V1_PHASE1_E3_PASSIVE_CAPTURE_V1_'
import typed_collector_contract as TC
PURPOSE = TC.PURPOSE
PARENT_SHA = 'd5575ff2e670fd18ea0a09d9f3d5c05c46bf606a027fcb84d97c6e34a88a2b41'
INDEX_SHA = TC.INDEX_SHA
SOURCE_VERSION = TC.SOURCE_VERSION
SOURCE_DERIVATION = TC.SOURCE_DERIVATION
CONTROLLER_SHA = '95952059e6e8640a5ba37e858ca29c5f313340e041260093ecc8aaf671665831'
OUTER = 'PHASE1_CAPTURE_PARENT_WAITED_ACTUAL_V1.json'
BIG = ('FINAL.json', 'TERMINAL_ROWS.json', 'cases/E3/FINAL.json')
SMALL = (
    'GROUP_PLAN.json', 'STAGE_COMPLETE_PHASE1_CAPTURE_V1.json',
    'PHASE1_CAPTURE_PARENT_DISPATCH_REQUEST_V1.json',
    'PHASE1_CAPTURE_PARENT_DISPATCH_RECEIPT_V1.json',
    'PHASE1_CAPTURE_PARENT_CONTROLLER_STARTED_V1.json', 'PARENT_STARTED.json',
    'ACTUAL_GROUP_ADMISSION.json', 'CHILDREN.json', 'GROUP_BARRIER_STATUS.json',
    'GROUP_EVAL_START.json', 'BOUNDED_ORIGINAL_RESOURCE_WAIT.json',
    'GROUP_ABORT.json', 'GROUP_STARTUP_ABORT.json', 'PARENT_ORIGINAL_ERROR.json',
    'PARENT_EXIT_SCOPE.json', 'PHASE1_CAPTURE_GROUP_CLOSED_SOURCE_GRADE_V1.json',
    'PHASE1_CAPTURE_PARENT_CONTROLLER_ERROR_V1.json', OUTER,
    'cases/E3/task.json', 'cases/E3/WORKER_SCENE_READY.json',
    'cases/E3/WORKER_EVAL_STARTED.json', 'cases/E3/PRE_CLOSE.json',
    'cases/E3/ENV_CLOSE_RETURNED_PHASE1_CAPTURE_V1.json',
    'cases/E3/APP_CLOSE_BINDING_PHASE1_CAPTURE_V1.json',
    'cases/E3/APP_FAST_CLOSE_INTENT_PHASE1_CAPTURE_V1.json',
    'cases/E3/APP_CLOSE_CALLED_PHASE1_CAPTURE_V1.json',
    'cases/E3/APP_CLOSE_RETURNED_PHASE1_CAPTURE_V1.json', 'cases/E3/WORKER_ERROR.json',
    'STAGE_ERROR_PHASE1_CAPTURE_V1.json', 'cases/E3/TYPED_CAPTURE_INCOMPLETE_V1.json')
LOGS = ('PHASE1_CAPTURE_CONTROLLER_STDOUT_STDERR.log',
        'PHASE1_CAPTURE_PARENT_FULL_STDOUT_STDERR.log', 'cases/E3/SDK_FULL_STDOUT_STDERR.log')
MUTABLE = {'GROUP_BARRIER_STATUS.json', 'BOUNDED_ORIGINAL_RESOURCE_WAIT.json'}
WORKER_KEYS = ('kind','purpose','integration','role','group_id','GPU_UUID','num_envs',
    'controls','requested_controls','physics_callbacks','feedback_samples','delay_calls',
    'passed_execution','execution_scope','policy_variant','model_PT_reads','training_updates',
    'optimizer_updates','learner_created','replay_created','teacher_created','actor35_source',
    'clean16_only','full_clean35','boundary','coverage','restore','interface_coverage_status',
    'inconclusive_reasons','gate1','exact','capture_interface_passed','paper_ready','stage2_GO',
    'skill_success_rate','overall_eight_pass_rate','reference_comparison')


def require(ok, message):
    if not ok:
        raise ValueError(message)


def validate_dispatch(value):
    require(type(value) is dict, 'dispatch must be mapping')
    root = value.get('root'); require(type(root) is str, 'dispatch root missing')
    path = PurePosixPath(root)
    require(str(path) == root and str(path.parent) == BASE+'/tasks'
            and path.name.startswith(PREFIX) and len(path.name) > len(PREFIX)
            and all(c.isascii() and (c.isalnum() or c in '_-') for c in path.name),
            'only the exact NEW own capture root is admitted')
    require(value.get('group_id') == path.name, 'dispatch group/root differ')
    for key in ('controller', 'parent'):
        row = value.get(key)
        require(type(row) is dict and type(row.get('pid')) is int and row['pid'] > 0
                and type(row.get('linux_start_ticks')) is str
                and row['linux_start_ticks'].isdigit(), key+' identity missing')
    require(value.get('parent_source_SHA') == PARENT_SHA, 'current parent source differs')
    require(type(value.get('actual_native_parent_Popen_calls')) is int
            and value['actual_native_parent_Popen_calls'] == 1
            and value.get('SDK_scene_or_skill_admission') is False, 'not the one original dispatch')
    digest = value.get('stage_receipt_SHA256')
    require(type(digest) is str and len(digest) == 64
            and all(c in '0123456789abcdef' for c in digest), 'stage SHA missing')
    require('purpose' not in value or value['purpose'] == PURPOSE, 'old purpose rejected')
    require('returncode' not in value or type(value['returncode']) is int
            and value['returncode'] == 0, 'dispatch transport failed; no replay')
    return value


def worker_projection(value):
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


def terminal_projection(rows):
    if type(rows) is not list:
        return rows
    return [dict(row, data=worker_projection(row.get('data'))) if type(row) is dict else row for row in rows]


def project(name, value):
    if name == 'cases/E3/FINAL.json':
        return worker_projection(value)
    if name == 'TERMINAL_ROWS.json':
        return terminal_projection(value)
    if name == 'FINAL.json' and type(value) is dict:
        return dict(value, terminal=terminal_projection(value.get('terminal')))
    return value


class MetadataReader:
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


def safe_source_path(root, name):
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


def validate_terminal_cache(reader, dispatch, closure):
    """Original metadata predicates; never feeds a projection to a raw/SHA grader."""
    result = {}; errors = []
    def check(label, operation):
        try:
            operation(); result[label] = True
        except Exception as exc:
            result[label] = False; errors.append(dict(check=label,error=type(exc).__name__+': '+str(exc)))
    cache = reader.cache; contract = closure['contract']
    if 'GROUP_PLAN.json' in cache:
        check('original_capture_plan',lambda:contract.validate_plan(cache['GROUP_PLAN.json'],closure['index']))
    task = cache.get('cases/E3/task.json'); final = cache.get('cases/E3/FINAL.json')
    if task is not None and final is not None:
        check('original_capture_preclose',lambda:contract.validate_preclose(final,task))
    binding = cache.get('cases/E3/APP_CLOSE_BINDING_PHASE1_CAPTURE_V1.json')
    if binding is not None:
        def binding_check():
            if binding.get('fast_shutdown') is True:
                closure['app']._validate_binding_receipt(binding)
                intent = cache.get('cases/E3/APP_FAST_CLOSE_INTENT_PHASE1_CAPTURE_V1.json')
                info = reader.info.get('cases/E3/FINAL.json',{})
                require(type(intent) is dict and intent.get('kind') == 'PINNED_PHASE1_CAPTURE_FAST_CLOSE_INTENT_V1'
                    and intent.get('binding') == binding and intent.get('final_SHA') == info.get('SHA256')
                    and intent.get('final_bytes') == info.get('bytes') and intent.get('original_env_close_returned') is True,
                    'fast intent/full FINAL hash differs')
            else:
                # This is the actual original returned-path validator with its real helper argument.
                closure['core']._validate_returned_app_binding(binding,closure['app'])
                returned = cache.get('cases/E3/APP_CLOSE_RETURNED_PHASE1_CAPTURE_V1.json')
                require(type(returned) is dict and returned.get('returned') is True
                    and returned.get('binding') == binding, 'returned App close receipt missing')
            env = cache.get('cases/E3/ENV_CLOSE_RETURNED_PHASE1_CAPTURE_V1.json')
            require(type(env) is dict and env.get('closed') is True, 'original env close receipt missing')
        check('original_app_close_metadata',binding_check)
    result['errors'] = errors
    result['source_grade_function_reexecuted'] = False
    result['producer_grade_preserved_separately'] = True
    return result


def watch(reader, *, cap_seconds=6000, interval_seconds=20, monotonic=time.monotonic, sleep=time.sleep):
    require(type(cap_seconds) in (int,float) and 0 < cap_seconds <= 6000, 'collector cap bounded by6000s')
    require(type(interval_seconds) in (int,float) and 0 < interval_seconds <= 20, 'metadata poll interval bounded')
    start = monotonic(); polls = 0
    while True:
        polls += 1
        for name in SMALL:
            reader.read(name)
        if OUTER in reader.cache:
            reason = 'OUTER_WAIT_FILE_PUBLISHED'; break
        remaining = cap_seconds-(monotonic()-start)
        if remaining <= 0:
            reason = 'COLLECTOR_CAP_ONLY_NO_NATIVE_TIMEOUT_OR_SIGNAL'; break
        sleep(min(interval_seconds,remaining))
    # One final small refresh covers files published in the same completion interval.
    for name in SMALL:
        reader.read(name)
    for name in BIG:
        reader.read(name,terminal=True)
    return dict(stop_reason=reason,polls=polls,collector_elapsed_seconds=monotonic()-start,
                collector_cap_seconds=cap_seconds,interval_seconds=interval_seconds,
                native_deadline_extended=False,parent_restarted=False,signals_sent=0,remote_writes=0)


def encoded_packet(value):
    raw = (json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False)+'\n').encode('utf-8')
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
