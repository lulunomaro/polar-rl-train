# NEW V2 ADMISSION2: source-preparation only until old zero-GO close + release; original ABI unchanged.
"""Dispatch exactly one fresh original-gated E3/W35 frozen-quality parent.
Original privateEX/finiteEX/canonical-readiness gates remain in pinned parent.
This dispatcher does not read/write C, acquire locks, open models or import SDK.
"""
from pathlib import Path
import json,sys,shlex,time

import hashlib, math
_A2_VERSION = 'V2_ADMISSION2'
_A2_PURPOSE = 'NEW_FROZEN_E3_W35_BATCH_V2_ADMISSION2_AFTER_CLOSED_ZERO_GO_TIMEOUT_V1'
_A2_PREFIX = 'MOD4V1_A1_FROZEN_E3_W35_BATCH_V2_ADMISSION2_'
_A2_TASKS = '/home/lc01/Zonglin Li/zonglin2/tasks/'
_A2_OLD_ROOT = _A2_TASKS + 'MOD4V1_A1_FROZEN_E3_W35_BATCH_V2_20261103_011752_1793639872103756500'
_A2_CLOSED_REL = 'reports/ACTUAL_FROZEN_E3_W35_BATCH_V2_20261103_012611/CLOSED_RESULT.json'
_A2_CLOSED_PIN = (40716, '8fdf76f57d7f3cb73417504d9c5a0123632656af2c9a5e8cf16bfb6d076df3f6')
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

R=Path(__file__).resolve().parent;marker=R/'FROZEN_E3_W35_BATCH_V2_ADMISSION2_PARENT_DISPATCH_ONCE.json';out=R/'reports/FROZEN_E3_W35_BATCH_V2_ADMISSION2_ACTUAL_PARENT_DISPATCH_V1.json';assert not marker.exists()and not out.exists();stage=json.loads((R/'reports/FROZEN_E3_W35_BATCH_V2_ADMISSION2_ACTUAL_SOURCE_STAGE_V1.json').read_bytes());assert stage['returncode']==0 and stage['stage']['staged']and stage['stage']['parent_launches']==0;root=stage['root'];gid=stage['group_id'];expected=stage['stage_complete_SHA'];assert root.endswith('/'+gid)and gid.startswith('MOD4V1_A1_FROZEN_E3_W35_BATCH_V2_ADMISSION2_')
fence=_a2_load_fence(R,True);_a2_bind(stage,fence)
code='''from pathlib import Path
import json,time,os,subprocess,hashlib
root=Path(ROOT);expected=EXPECTED;assert root.name==__GROUP_ID__ and root.parent==Path('/home/lc01/Zonglin Li/zonglin2/tasks');raw=(root/'STAGE_COMPLETE_MICROBATCH_V2.json').read_bytes();assert hashlib.sha256(raw).hexdigest()==expected;stage=json.loads(raw);assert stage['staged']and stage['parent_launches']==0
for name in('PARENT_STARTED.json','PARENT_EXIT_SCOPE.json','PARENT_ORIGINAL_ERROR.json','FINAL.json','PARENT_FROZEN_MICROBATCH_DISPATCH_ONCE.json'):assert not(root/name).exists(),name
plan=json.loads((root/'GROUP_PLAN.json').read_bytes());assert plan['group_id']==root.name and plan['requested_roles']==['E3','W35']and plan['kind']=='A1_FROZEN_EVAL_MICROBATCH_GROUP_PLAN_V1'and plan['comparison']is None and plan['overall_eight_pass_rate']is None
parent=root/'single_gpu_e3_w35_a1_frozen_parent_v1.py';rawparent=parent.read_bytes();assert len(rawparent)==8991 and hashlib.sha256(rawparent).hexdigest()=='9a943e730f66bfb1a68af35ddfa8118d6da605dc83f442e3c0b51c9c7ad8da7b'
# Standard original resources belong to supervisor, never this dispatcher.
request=dict(kind='NEW_FROZEN_MICROBATCH_DISPATCH_NOT_RESOURCE_OR_SKILL_ADMISSION',epoch=time.time(),group_id=root.name,requested_roles=['E3','W35'],stage_complete_SHA=expected,source_parent_SHA=hashlib.sha256(rawparent).hexdigest(),original_single_GPU_private_EX_global_finite_EX_C_readonly_gates_unchanged=True,controller_C_locks_model_SDK_operations=0)
request.update(__A2_META__)
p=root/'PARENT_FROZEN_MICROBATCH_DISPATCH_ONCE.json'
with p.open('x')as f:json.dump(request,f,indent=2);f.flush();os.fsync(f.fileno())
log=(root/'PARENT_FROZEN_MICROBATCH_STDOUT_STDERR.log').open('xb');child=subprocess.Popen(['/home/lc01/Zonglin Li/zonglin2/run-python.sh','-u','-B',str(parent)],cwd=str(root),stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True);log.close();stat=Path('/proc')/str(child.pid)/'stat';text=stat.read_text();f=text[text.rfind(')')+2:].split();request.update(actual_Popen_calls=1,parent=dict(pid=child.pid,linux_start_ticks=f[19],state=f[0],observed_epoch=time.time()),not_yet_scene_ready_or_actual_frozen_result=True);(root/'PARENT_FROZEN_MICROBATCH_DISPATCH_RECEIPT.json').write_text(json.dumps(request,indent=2));print(json.dumps(request))
'''.replace('ROOT',repr(root)).replace('EXPECTED',repr(expected)).replace('__GROUP_ID__',repr(gid)).replace('__A2_META__',repr(_a2_meta(fence)))
import ast
ast.parse(code)
marker.write_text(json.dumps(dict(root=root,group_id=gid,epoch=time.time(),**_a2_meta(fence),purpose='Once original frozen supervisor, not resource gate bypass'),indent=2),encoding='utf-8');sys.path.insert(0,str(R.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
c=connect72()
try:
 i,o,e=c.exec_command(shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -u -B -c '+shlex.quote(code),timeout=45);i.close();text=o.read().decode();err=e.read().decode();rc=o.channel.recv_exit_status();value=dict(root=root,group_id=gid,epoch=time.time(),returncode=rc,stdout=text,stderr=err);value.update(_a2_meta(fence));out.write_text(json.dumps(value,indent=2),encoding='utf-8');assert rc==0,err;value['receipt']=json.loads(text);out.write_text(json.dumps(value,indent=2),encoding='utf-8');print(json.dumps(value,indent=2))
finally:c.close()
