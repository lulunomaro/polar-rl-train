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
PURPOSE = 'NEW_PASSIVE_INTERFACE_PROBE_NO_TRAIN'
PARENT_SHA = 'd5575ff2e670fd18ea0a09d9f3d5c05c46bf606a027fcb84d97c6e34a88a2b41'
INDEX_SHA = 'cdb2ca55c08a544cd01e462b7ce27261900f3b6ebaffb4784350717f756b7cf7'
SOURCE_VERSION = 2
SOURCE_DERIVATION = dict(kind='PHASE1_CAPTURE_RESULT_COLLECTOR_DERIVATION_V2',
    base_collector_seal_SHA256='c6847784e4733f53767dc20f064b584eecda02f1046d88855f25d8e8381eca6c',
    worker_source_version=2,worker_index_SHA256=INDEX_SHA,
    worker_seal_SHA256='caacf07e8bc46bd2cc5f4fa14138782430d86de4f6382bbb35adcdcde5d469d5',
    typed_API_version=1,wire_V1_namespace_preserved=True,ROOT_PREFIX_V1_preserved=True,
    producer_grade_preserved=True,binding_epoch_not_removed=True)
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
    'cases/E3/APP_CLOSE_RETURNED_PHASE1_CAPTURE_V1.json', 'cases/E3/WORKER_ERROR.json')
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
    if type(value) is not dict:
        return value
    return {key:value[key] for key in WORKER_KEYS if key in value}


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
    """Allowlisted metadata only. Big terminal files have one read attempt each."""
    def __init__(self, root):
        self.root = Path(root); self.cache = {}; self.info = {}; self.signatures = {}; self.errors = []

    def path(self, name):
        require(name in SMALL+BIG+LOGS or name == 'CAPTURE_SOURCE_INDEX.json', 'nonmetadata alias rejected')
        path = self.root/name
        require(path.resolve().is_relative_to(self.root.resolve()), 'own metadata resolves outside root')
        require(not path.is_symlink(), 'metadata symlink rejected')
        return path

    def read(self, name, *, terminal=False):
        require(name in SMALL+BIG, 'metadata alias rejected')
        if name in BIG:
            require(terminal, 'big FINAL reads only at terminal/cap')
            if name in self.info and self.info[name].get('read_count', 0):
                return self.cache.get(name)
        try:
            path = self.path(name); st = path.stat()
            require(stat.S_ISREG(st.st_mode), 'metadata is not regular')
            signature = (st.st_size, st.st_mtime_ns)
            if name in self.cache and self.signatures[name] == signature:
                return self.cache[name]
            if name in self.cache and name not in MUTABLE:
                raise ValueError('immutable metadata changed after observation: '+name)
            maximum = 64*1024*1024 if name in BIG else 8*1024*1024 if name == 'GROUP_PLAN.json' else 2*1024*1024
            require(st.st_size <= maximum, 'bounded metadata exceeded: '+name)
            previous = self.info.get(name, {}).get('read_count', 0)
            self.info[name] = dict(status='READ_ATTEMPTED', read_count=previous+1, bytes=st.st_size)
            with path.open('rb') as stream:
                raw = stream.read(maximum+1)
            require(len(raw) <= maximum and len(raw) == st.st_size, 'metadata changed during bounded read')
            value = json.loads(raw)
            self.info[name].update(status='READ', SHA256=hashlib.sha256(raw).hexdigest(),
                whole_JSON_read=True, new_capture_trace_fields_parsed=name in BIG,
                trace_payload_exported=False)
            self.cache[name] = value; self.signatures[name] = signature
            return value
        except FileNotFoundError:
            self.info.setdefault(name, dict(status='MISSING',read_count=0,bytes=None,SHA256=None))
        except Exception as exc:
            self.errors.append(dict(file=name, error=type(exc).__name__+': '+str(exc)))
            self.info.setdefault(name, dict(read_count=0,bytes=None,SHA256=None))['status'] = 'ERROR'
        return None

    def tail(self, name, maximum=16384):
        try:
            path = self.path(name); st = path.stat()
            require(stat.S_ISREG(st.st_mode), 'log is not regular')
            with path.open('rb') as stream:
                stream.seek(max(0,st.st_size-maximum)); raw = stream.read(maximum)
            return dict(bytes_read=len(raw), source_bytes=st.st_size, tail=raw.decode('utf-8','replace'))
        except FileNotFoundError:
            return dict(bytes_read=0,source_bytes=None,tail=None)
        except Exception as exc:
            return dict(bytes_read=None,source_bytes=None,tail=None,error=type(exc).__name__+': '+str(exc))


def load_metadata_closure(root):
    """Real full runtime -> core -> AppV6 -> Base, no AST subset/stub/native main."""
    root = Path(root)
    require(root.is_dir() and not root.is_symlink(), 'own root must be the actual staged directory')
    raw = (root/'CAPTURE_SOURCE_INDEX.json').read_bytes()
    require(len(raw) <= 2*1024*1024 and hashlib.sha256(raw).hexdigest() == INDEX_SHA, 'current index pin differs')
    index = json.loads(raw); rows = index['original17']+index['new_sources']+index['dependency_sources']
    require(len(rows) == 27, 'whole 27 source aliases required')
    for row in rows:
        alias = row['install_relative']; p = root/alias
        require(not p.is_symlink() and p.resolve().is_relative_to(root.resolve()), 'source alias escapes root')
        data = p.read_bytes()
        require((len(data),hashlib.sha256(data).hexdigest()) == (row['bytes'],row['SHA256']), 'source pin differs: '+alias)
    control = (root/'phase1_capture_parent_actual_wait_controller_v1.py').read_bytes()
    require((len(control),hashlib.sha256(control).hexdigest()) == (3824,CONTROLLER_SHA), 'controller pin differs')
    sys.dont_write_bytecode = True; sys.path.insert(0,str(root))
    forbidden = {'torch','isaaclab','isaacsim','omni','pxr','carb','warp','rsl_rl','tensordict'}
    def guard(event, args):
        if event == 'import' and str(args[0]).split('.')[0] in forbidden:
            raise ValueError('native import in metadata closure: '+str(args[0]))
        if event in ('subprocess.Popen','os.system','socket.connect','os.kill','os.killpg',
                     'os.remove','os.rename','os.mkdir','os.rmdir','os.link','os.symlink','os.truncate'):
            raise ValueError('lifecycle/network/mutation operation in metadata reader')
        if event == 'open':
            if len(args)>1 and type(args[1]) is str and any(c in args[1] for c in 'wax+'):
                raise ValueError('remote reader never writes files')
            if len(args)>2 and type(args[2]) is int and args[2] & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND):
                raise ValueError('remote reader never opens writable descriptors')
    sys.addaudithook(guard)
    contract = importlib.import_module('phase1_capture_contract')
    runtime = importlib.import_module('phase1_capture_runtime')
    require(Path(runtime.__file__).resolve() == root/'phase1_capture_runtime.py'
            and Path(contract.__file__).resolve() == root/'phase1_capture_contract.py', 'runtime/contract module alias differs')
    runtime.validate_installed_root(root,runtime.HERE)
    core = runtime.core(); app = runtime._pinned_module('app_close_semantics_v5',runtime.APP_PIN); base = app._base
    require(Path(core.__file__).resolve() == root/'a1_frozen_eval_runtime_v2.py'
            and Path(app.__file__).resolve() == root/'app_close_semantics_v5.py'
            and Path(base.__file__).resolve() == root/'resume_runtime_contracts_v3.py', 'full App/Base closure origin differs')
    require(not any(m.split('.')[0] in forbidden for m in sys.modules), 'native module unexpectedly loaded')
    return dict(index=index, contract=contract, runtime=runtime, core=core, app=app,
        receipt=dict(source_aliases=27, original17=17, full_AppV6_Base_imported=True,
                     native_modules_loaded=[], worker_or_parent_main_called=False))


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


def remote_main(dispatch, *, cap_seconds=6000, interval_seconds=20):
    value = dict(kind='PHASE1_CAPTURE_OWN_METADATA_PACKET_V1',documents={},file_metadata={},
        source_version=SOURCE_VERSION,source_derivation=SOURCE_DERIVATION,
        closure=None,metadata_validation={},collector_errors=[],log_tails={},watch=None)
    reader = None
    try:
        validate_dispatch(dispatch); reader = MetadataReader(dispatch['root']); closure = None
        try:
            closure = load_metadata_closure(dispatch['root']); value['closure'] = closure['receipt']
        except Exception as exc:
            value['collector_errors'].append(dict(type=type(exc).__name__,message='metadata source closure: '+str(exc)))
        value['watch'] = watch(reader,cap_seconds=cap_seconds,interval_seconds=interval_seconds)
        if closure is not None:
            value['metadata_validation'] = validate_terminal_cache(reader,dispatch,closure)
    except Exception as exc:
        value['collector_errors'].append(dict(type=type(exc).__name__,message=str(exc)))
    if reader is not None:
        value['documents'] = {name:project(name,item) for name,item in reader.cache.items()}
        value['file_metadata'] = reader.info
        value['collector_errors'].extend(reader.errors)
        value['log_tails'] = {name:reader.tail(name) for name in LOGS}
    print(json.dumps(value,allow_nan=False,separators=(',',':')))
    return value
