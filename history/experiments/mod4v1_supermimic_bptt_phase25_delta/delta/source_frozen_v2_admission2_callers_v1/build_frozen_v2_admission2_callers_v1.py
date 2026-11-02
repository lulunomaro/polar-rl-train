"""Parent-run SOURCE builder only: emit four NEW callers, never execute them."""
import argparse
import ast
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SNAPSHOT = HERE / '_SOURCE_INPUT'
OLD_PREFIX = 'FROZEN_E3_W35_BATCH_V2_'
NEW_PREFIX = 'FROZEN_E3_W35_BATCH_V2_ADMISSION2_'
STAGE_PIN = (32953, '9c788fc5435dcbe2af25d13390c2fb008be77c23fbe83104b170d8091cb72952')
INDEX_PIN = (4886, '69688e86528e400f188de3f147614cde5c66f86985adaceed805af800819dc50')
PARENT_PIN = (8991, '9a943e730f66bfb1a68af35ddfa8118d6da605dc83f442e3c0b51c9c7ad8da7b')
TEMPLATES = (
    'upload_preflight_frozen_e3_w35_microbatch_v2_once.py',
    'stage_frozen_e3_w35_microbatch_v2_after_preflight_once.py',
    'dispatch_frozen_e3_w35_microbatch_v2_original_parent_once.py',
    'collect_frozen_e3_w35_microbatch_v2_metadata_once.py',
)
OUTPUTS = tuple(name.replace('_v2_', '_v2_admission2_') for name in TEMPLATES)
CLOSED_REL = 'reports/ACTUAL_FROZEN_E3_W35_BATCH_V2_20261103_012611/CLOSED_RESULT.json'
SOURCE_REPORT = 'FROZEN_E3_W35_BATCH_V2_ADMISSION2_CALLERS_SOURCE_V1.json'

# Copied verbatim into each standalone caller AFTER namespace renaming. The old
# close/release references below deliberately remain historical V2, not A2 names.
FENCE_SOURCE = r'''
import hashlib, math
_A2_VERSION = 'V2_ADMISSION2'
_A2_PURPOSE = 'NEW_FROZEN_E3_W35_BATCH_V2_ADMISSION2_AFTER_CLOSED_ZERO_GO_TIMEOUT_V1'
_A2_PREFIX = 'MOD4V1_A1_FROZEN_E3_W35_BATCH_V2_ADMISSION2_'
_A2_TASKS = '/home/lc01/Zonglin Li/zonglin2/tasks/'
_A2_OLD_ROOT = _A2_TASKS + 'MOD4V1_A1_FROZEN_E3_W35_BATCH_V2_20261103_011752_1793639872103756500'
_A2_CLOSED_REL = 'reports/ACTUAL_FROZEN_E3_W35_BATCH_V2_20261103_012611/CLOSED_RESULT.json'
_A2_CLOSED_PIN = __CLOSED_PIN__
_A2_RELEASE_REL = 'reports/FROZEN_V2_RESOURCES_RELEASED_AFTER_ZERO_GO_TIMEOUT_V1.json'
_A2_STAGE_SHA = '9c788fc5435dcbe2af25d13390c2fb008be77c23fbe83104b170d8091cb72952'
_A2_INDEX_SHA = '69688e86528e400f188de3f147614cde5c66f86985adaceed805af800819dc50'
_A2_PARENT_SHA = '9a943e730f66bfb1a68af35ddfa8118d6da605dc83f442e3c0b51c9c7ad8da7b'

def _a2_need(ok, message):
    if not ok: raise ValueError(message)

def _a2_epoch(value):
    return type(value) in (int, float) and math.isfinite(value)

def _a2_check_closed(v):
    _a2_need(type(v) is dict and v.get('root') == _A2_OLD_ROOT and v.get('group_id') == _A2_OLD_ROOT.rsplit('/', 1)[1], 'exact historical zero-GO identity required')
    _a2_need(v.get('closed') is True and v.get('early_parent_dead') is False, 'old actual close required')
    top = v['top']; end = top['PARENT_EXIT_SCOPE.json']
    for name in ('ACTUAL_GROUP_ADMISSION.json', 'CHILDREN.json', 'GROUP_BARRIER_STATUS.json', 'GROUP_EVAL_START.json', 'TERMINAL_ROWS.json', 'FINAL.json'):
        _a2_need(name in top and top[name] is None, 'old batch was not zero-admission: ' + name)
    _a2_need(end.get('epoch') == 1793642078.162321 and _a2_epoch(end.get('epoch')), 'exact historical closed epoch required')
    _a2_need(end.get('all_own_children_waited') is True and end.get('child_waits') == []
             and end.get('original_single_GPU_private_EX_released') is True
             and end.get('original_global_finite_EX_released') is True, 'old actual wait/release boundary incomplete')
    _a2_need(type(end.get('canonical_writes')) is int and end['canonical_writes'] == 0
             and type(end.get('SDK_PT_opens_by_parent')) is int and end['SDK_PT_opens_by_parent'] == 0, 'old parent mutated/opened forbidden state')
    error = top['PARENT_ORIGINAL_ERROR.json']
    _a2_need(error.get('no_samepurpose_automatic_retry') is True
             and 'Originalresourcewait1800sexpiredwithoutSDK/model/foreignactions' in str(error.get('errors')), 'original timeout must remain visible')
    rows = v['rows']; _a2_need(type(rows) is list and len(rows) == 2 and [x.get('role') for x in rows] == ['E3', 'W35'], 'exact E3/W35 old rows required')
    for row in rows:
        _a2_need(row.get('status') == 'NOT_ADMITTED', 'old row was admitted')
        for name in ('FINAL', 'WORKER_SCENE_READY', 'WORKER_EVAL_STARTED', 'PROGRESS', 'WORKER_ERROR', 'A1_EVAL_PRIMARY_ERROR_V2'):
            _a2_need(name in row and row[name] is None, 'old role has actual work: ' + name)
    return end['epoch']

def _a2_check_release(w, *, closed_SHA, closed_epoch):
    _a2_need(type(w) is dict and w.get('kind') == 'READONLY_POST_FROZEN_V2_ZERO_ADMISSION_RESOURCE_RELEASE_WITNESS_NOT_ADMISSION', 'release witness kind differs')
    _a2_need(w.get('old_root') == _A2_OLD_ROOT and w.get('old_closed_epoch') == closed_epoch
             and w.get('old_closed_metadata_SHA') == closed_SHA, 'release witness bound to different close')
    _a2_need(w.get('observer_only') is True and w.get('old_parent_wait_not_extended') is True
             and w.get('resource_release_observed') is True and w.get('observer_timed_out') is False, 'positive original release witness required')
    a = w['actual']
    _a2_need(a.get('original_frozen_resources_observed_clear') is True
             and a.get('original_relevant_leases_clear') is True, 'original relevant resources were not observed clear')
    _a2_need(_a2_epoch(a.get('epoch')) and a['epoch'] > closed_epoch, 'release observation must be strictly after old actual close')
    _a2_need(a.get('actual_future_admission_not_guaranteed') is True
             and type(a.get('lock_acquisitions_Cwrites_models_raw_SDK_GPU_parent_or_signals')) is int
             and a['lock_acquisitions_Cwrites_models_raw_SDK_GPU_parent_or_signals'] == 0, 'witness is not a read-only non-admission observation')
    return a['epoch']

def _a2_load_fence(project, require_release):
    path = project / _A2_CLOSED_REL; raw = path.read_bytes()
    _a2_need((len(raw), hashlib.sha256(raw).hexdigest()) == _A2_CLOSED_PIN, 'historical closed metadata bytes changed')
    closed_epoch = _a2_check_closed(json.loads(raw))
    fence = dict(zero_GO_closed_metadata_SHA=_A2_CLOSED_PIN[1], zero_GO_closed_epoch=closed_epoch,
                 old_zero_GO_root=_A2_OLD_ROOT, release_verified=False, release_witness=None)
    if require_release:
        rp = project / _A2_RELEASE_REL; rb = rp.read_bytes(); _a2_need(len(rb) <= 1048576, 'release metadata oversized')
        w = json.loads(rb); observed_epoch = _a2_check_release(w, closed_SHA=_A2_CLOSED_PIN[1], closed_epoch=closed_epoch)
        fence.update(release_verified=True, release_witness=dict(path=str(rp), bytes=len(rb), SHA256=hashlib.sha256(rb).hexdigest(),
                     observed_epoch=observed_epoch, resource_release_observed=True, original_frozen_resources_observed_clear=True,
                     historical_snapshot_not_resource_ownership_or_future_admission=True))
    return fence

def _a2_meta(fence):
    return dict(codeVersion=_A2_VERSION, admission2_purpose=_A2_PURPOSE,
                source_stage_code_version='V2', original_actor_source_parent_ABI='V1_UNCHANGED',
                source_stage_bytes=32953, source_stage_SHA=_A2_STAGE_SHA,
                source_index_bytes=4886, source_index_SHA=_A2_INDEX_SHA, source_parent_SHA=_A2_PARENT_SHA,
                resource_witness_is_not_lease_or_original_gate_bypass=True, **fence)

def _a2_bind(report, fence):
    _a2_need(report.get('codeVersion') == _A2_VERSION and report.get('admission2_purpose') == _A2_PURPOSE, 'only this new Admission2 purpose accepted')
    gid = report.get('group_id'); root = report.get('root')
    _a2_need(type(gid) is str and gid.isascii() and gid.startswith(_A2_PREFIX) and len(gid) > len(_A2_PREFIX)
             and all(c.isalnum() or c == '_' for c in gid) and root == _A2_TASKS + gid and root != _A2_OLD_ROOT, 'new own root/group identity required')
    if 'input_root' in report: _a2_need(report['input_root'] == root + '_SOURCE_INPUT', 'new own source-input root differs')
    if 'argv' in report:
        source = root + '_SOURCE_INPUT'
        expected = [source + '/stage_a1_microbatch_eval_v2.py', '--original-group-root',
            _A2_TASKS + 'MOD4V1_NINE_N80_SINGLE_GPU_PARALLEL_V8_20261102_101426_1793585666425343700',
            '--source-dir', source + '/source', '--source-index', source + '/MICROBATCH_STAGE_INDEX_V2.json',
            '--native-root', _A2_TASKS + 'MOD4V1_A1_RAW35_V6_ADMISSION2_20261102_231937_1793632777470828000',
            '--new-root', root, '--group-id', gid, '--gpu-uuid', 'GPU-16828f91-2b45-b646-8dc0-9481138e2842']
        argv = report['argv']
        _a2_need(type(argv) is list and len(argv) == len(expected) + 1 and argv[:-1] == expected
                 and argv[-1] in ('--preflight-only', '--stage'), 'stage argv must bind exact new own source/root and unchanged native/GPU')
    _a2_need(report.get('zero_GO_closed_metadata_SHA') == fence['zero_GO_closed_metadata_SHA']
             and report.get('zero_GO_closed_epoch') == fence['zero_GO_closed_epoch'], 'purpose not bound to this old actual zero-GO close')
    _a2_need(report.get('source_stage_SHA') == _A2_STAGE_SHA and report.get('source_index_SHA') == _A2_INDEX_SHA
             and report.get('source_parent_SHA') == _A2_PARENT_SHA, 'original stage/index/parent pins differ')
    _a2_need(_a2_epoch(report.get('epoch')) and report['epoch'] > fence['zero_GO_closed_epoch'], 'new purpose predates historical close')
'''


def need(ok, message):
    if not ok: raise ValueError(message)


def H(raw): return hashlib.sha256(raw).hexdigest()


def read_small(path):
    need(path.suffix in ('.py', '.json'), 'explicit small source/metadata only')
    raw = path.read_bytes(); need(len(raw) <= 262144, 'bounded source/metadata exceeded')
    return raw


def load_inputs(snapshot=SNAPSHOT):
    pins = json.loads(read_small(snapshot / 'INPUT_PINS.json'))
    values = {}
    for row in pins['files']:
        raw = read_small(snapshot / row['relative'])
        need((len(raw), H(raw)) == (row['bytes'], row['SHA256']), 'snapshot changed: ' + row['relative'])
        values[row['relative']] = raw
    need(tuple(name for name in TEMPLATES if name in values) == TEMPLATES, 'exact four templates required')
    need((len(values['source_stage_a1_microbatch_eval_v2/stage_a1_microbatch_eval_v2.py']), H(values['source_stage_a1_microbatch_eval_v2/stage_a1_microbatch_eval_v2.py'])) == STAGE_PIN, 'V2 stager pin differs')
    need((len(values['payload_frozen_microbatch_v2/MICROBATCH_STAGE_INDEX_V2.json']), H(values['payload_frozen_microbatch_v2/MICROBATCH_STAGE_INDEX_V2.json'])) == INDEX_PIN, 'V2 index pin differs')
    return pins, values


def fence_source(closed_raw):
    return FENCE_SOURCE.replace('__CLOSED_PIN__', repr((len(closed_raw), H(closed_raw))))


def render_callers(values):
    block = fence_source(values[CLOSED_REL])
    results = {}; all_ops = {}
    for index, name in enumerate(TEMPLATES):
        text = values[name].decode('utf-8'); ops = []
        def edit(old, new, count=1):
            nonlocal text
            need(text.count(old) == count, 'source edit anchor count differs: ' + name + ': ' + old[:100])
            text = text.replace(old, new); ops.append((old, new, count))
        edit(OLD_PREFIX, NEW_PREFIX, text.count(OLD_PREFIX))
        if index < 3:
            edit('# NEW V2 dependency-complete evaluation purpose; do not replay consumed failedV1.',
                 '# NEW V2 ADMISSION2: source-preparation only until old zero-GO close + release; original ABI unchanged.')
        else:
            edit('"""Single observer:', '# NEW V2 ADMISSION2 own metadata observer; original ABI unchanged.\n"""Single observer:')
        edit('R=Path(__file__).resolve().parent;', block + '\nR=Path(__file__).resolve().parent;')
        if index == 0:
            prior = next(line for line in text.splitlines(True) if line.startswith('prior_pointer='))
            edit(prior, 'fence=_a2_load_fence(R,False)\n')
            edit('# Previous physical V1 is consumed and fully waited; V2 changes one missing source dependency.',
                 '# New explicit outer purpose after the actual ZERO-GO V2 timeout; not an automatic retry or wait extension.')
            edit("marker.write_text(json.dumps(value,indent=2)", "value.update(_a2_meta(fence));_a2_bind(value,fence);marker.write_text(json.dumps(value,indent=2)")
        elif index == 1:
            edit(";argv=list(p['argv']);", ";fence=_a2_load_fence(R,False);_a2_bind(p,fence);argv=list(p['argv']);")
            edit(";marker.write_text(json.dumps(v,indent=2)", ";v.update(_a2_meta(fence));_a2_bind(v,fence);marker.write_text(json.dumps(v,indent=2)")
            edit('STAGE_COMPLETE_MICROBATCH_V1.json', 'STAGE_COMPLETE_MICROBATCH_V2.json')
            edit("v.update(stage=stage,stage_complete_bytes=len(raw),stage_complete_SHA=hashlib.sha256(raw).hexdigest())",
                 "v.update(stage=stage,stage_complete_bytes=len(raw),stage_complete_SHA=hashlib.sha256(raw).hexdigest(),stage_complete_receipt_name='STAGE_COMPLETE_MICROBATCH_V2.json',stager_bytes=32953,stager_SHA=_A2_STAGE_SHA)")
            edit("stage_complete_SHA=v['stage_complete_SHA'],source_files=stage['source_files']",
                 "stage_complete_SHA=v['stage_complete_SHA'],stager_bytes=v['stager_bytes'],stager_SHA=v['stager_SHA'],source_files=stage['source_files']")
        elif index == 2:
            edit('FROZEN_E3_W35_BATCH_V2_ADMISSION2_ACTUAL_SOURCE_STAGE_RECEIPT_CORRECTED_V2.json',
                 'FROZEN_E3_W35_BATCH_V2_ADMISSION2_ACTUAL_SOURCE_STAGE_V1.json')
            edit("\ncode='''", "\nfence=_a2_load_fence(R,True);_a2_bind(stage,fence)\ncode='''")
            edit("\np=root/'PARENT_FROZEN_MICROBATCH_DISPATCH_ONCE.json'",
                 "\nrequest.update(__A2_META__)\np=root/'PARENT_FROZEN_MICROBATCH_DISPATCH_ONCE.json'")
            edit(".replace('__GROUP_ID__',repr(gid))", ".replace('__GROUP_ID__',repr(gid)).replace('__A2_META__',repr(_a2_meta(fence)))")
            edit("epoch=time.time(),purpose='Once original frozen supervisor, not resource gate bypass'",
                 "epoch=time.time(),**_a2_meta(fence),purpose='Once original frozen supervisor, not resource gate bypass'")
            edit("stderr=err);out.write_text", "stderr=err);value.update(_a2_meta(fence));out.write_text")
        else:
            edit("assert d['returncode']==0;m=d['receipt'];",
                 "assert d['returncode']==0;fence=_a2_load_fence(R,False);_a2_bind(d,fence);m=d['receipt'];assert m['codeVersion']==_A2_VERSION and m['admission2_purpose']==_A2_PURPOSE and m['release_verified']is True;fence.update(release_verified=True,release_witness=m['release_witness']);")
            edit('one_published_metadata_observer=True)', 'one_published_metadata_observer=True,**_a2_meta(fence))')
            edit('model_raw_JSONL_SDK_GPU_C_operations=0)', 'model_raw_JSONL_SDK_GPU_C_operations=0);value.update(_a2_meta(fence))')
        ast.parse(text, filename=OUTPUTS[index])
        restored = undo(text, ops)
        need(restored == values[name].decode('utf-8'), 'whitelist inverse did not restore original bytes')
        need(ast.dump(ast.parse(restored), include_attributes=False) == ast.dump(ast.parse(values[name]), include_attributes=False), 'whole-template normalized AST differs')
        results[OUTPUTS[index]] = text
        all_ops[OUTPUTS[index]] = ops
    return results, all_ops


def undo(text, ops):
    for old, new, count in reversed(ops):
        need(text.count(new) == count, 'inverse source whitelist anchor differs')
        text = text.replace(new, old)
    return text


def check_live_inputs(project, pins):
    need(str(project) == pins['project_root'], 'parent must use the exact original project root')
    for row in pins['files']:
        raw = read_small(project / row['relative'])
        need((len(raw), H(raw)) == (row['bytes'], row['SHA256']), 'old source/metadata changed; do not replay: ' + row['relative'])
    for row in pins['verified_unchanged_payload14']:
        path = Path(row['path']); need(path.is_relative_to(project), 'payload path escaped explicit project')
        raw = read_small(path)
        need((len(raw), H(raw)) == (row['bytes'], row['SHA256']), 'original fourteen source dependency differs')
    need(len(pins['verified_unchanged_payload14']) == 14, 'exact original fourteen required')


def emit_sources(sources, destination):
    targets = [destination / name for name in OUTPUTS]
    need(all(not p.exists() for p in targets), 'NEW caller filenames must all be absent before emission')
    result = []
    for name, text in sources.items():
        raw = text.encode('utf-8')
        with (destination / name).open('xb') as stream: stream.write(raw)
        result.append(dict(file=name, bytes=len(raw), SHA256=H(raw)))
    return result


def build(project, emit=False):
    project = Path(project).resolve(); pins, values = load_inputs()
    check_live_inputs(project, pins)
    sources, ops = render_callers(values)
    # Metadata validation only; this does NOT require a release witness in order
    # to prepare SOURCE. It never imports any generated caller or connector.
    ns = {}; exec(compile(fence_source(values[CLOSED_REL]), '<stdlib-fence-definitions>', 'exec'), ns)
    closed = json.loads(values[CLOSED_REL]); ns['_a2_check_closed'](closed)
    result = dict(kind='NEW_FROZEN_V2_ADMISSION2_FOUR_CALLERS_SOURCE_ONLY_V1',
        codeVersion='V2_ADMISSION2', project_root=str(project), emitted=emit,
        old_closed_metadata_SHA=H(values[CLOSED_REL]), old_closed_epoch=1793642078.162321,
        release_witness_required_only_at_actual_dispatch=True, actual_resource_release_or_admission=None,
        original_stage_PIN=STAGE_PIN, original_index_PIN=INDEX_PIN, original_parent_PIN=PARENT_PIN,
        fourteen_dependency_PINS_unchanged=True, original_actor_source_parent_ABI='V1_UNCHANGED',
        whitelist_inverse_bytes_and_whole_AST_equal=True,
        SSH_SDK_GPU_PT_raw_C_locks_Git_parent_or_caller_operations=0,
        caller_order=list(OUTPUTS), files=[dict(file=n, bytes=len(s.encode('utf-8')), SHA256=H(s.encode('utf-8'))) for n, s in sources.items()],
        source_edit_counts={n:len(o) for n,o in ops.items()})
    if emit:
        report = project / SOURCE_REPORT; need(not report.exists(), 'NEW source receipt must be absent')
        result['files'] = emit_sources(sources, project)
        with report.open('x', encoding='utf-8') as stream: json.dump(result, stream, indent=2); stream.write('\n')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project-root', required=True)
    parser.add_argument('--emit', action='store_true', help='Write four NEW source callers; never execute them')
    args = parser.parse_args()
    print(json.dumps(build(args.project_root, args.emit), indent=2))
