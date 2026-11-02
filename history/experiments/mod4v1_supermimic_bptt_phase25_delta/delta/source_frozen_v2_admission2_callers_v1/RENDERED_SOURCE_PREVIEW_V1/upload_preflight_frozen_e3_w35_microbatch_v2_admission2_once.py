# NEW V2 ADMISSION2: source-preparation only until old zero-GO close + release; original ABI unchanged.
"""Upload pinned source ONLY and preflight new candidate-quality eval purpose.
No native parent/SDK/model/C/lock operations; native_root is already fully closed.
"""
from pathlib import Path
import json,sys,time,hashlib,shlex,posixpath

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

R=Path(__file__).resolve().parent;P=R/'payload_frozen_microbatch_v2';marker=R/'FROZEN_E3_W35_BATCH_V2_ADMISSION2_SOURCE_INPUT_ONCE.json';out=R/'reports/FROZEN_E3_W35_BATCH_V2_ADMISSION2_SOURCE_PREFLIGHT_V1.json';assert not marker.exists()and not out.exists();closed=json.loads((R/'reports/A1_ADMISSION2_QUALITY_BOUNDARY_CLOSED_TRUTH_V1.json').read_bytes());assert closed['all8_original_actual_wait_fullsave_semantic_success']and closed['actual_trained_roles']==['E3','W35'];native=closed['root'];old='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_NINE_N80_SINGLE_GPU_PARALLEL_V8_20261102_101426_1793585666425343700';stager=R/'source_stage_a1_microbatch_eval_v2/stage_a1_microbatch_eval_v2.py';b=stager.read_bytes();assert len(b)==32953 and hashlib.sha256(b).hexdigest()=='9c788fc5435dcbe2af25d13390c2fb008be77c23fbe83104b170d8091cb72952';idx=(P/'MICROBATCH_STAGE_INDEX_V2.json').read_bytes();assert len(idx)==4886 and hashlib.sha256(idx).hexdigest()=='69688e86528e400f188de3f147614cde5c66f86985adaceed805af800819dc50';manifest=json.loads((R/'reports/FROZEN_MICROBATCH14_LOCAL_SOURCE_PAYLOAD_V2.json').read_bytes());assert len(manifest['files'])==14

# New explicit outer purpose after the actual ZERO-GO V2 timeout; not an automatic retry or wait extension.
fence=_a2_load_fence(R,False)

run='MOD4V1_A1_FROZEN_E3_W35_BATCH_V2_ADMISSION2_'+time.strftime('%Y%m%d_%H%M%S')+'_'+str(time.time_ns());root='/home/lc01/Zonglin Li/zonglin2/tasks/'+run;input_root=root+'_SOURCE_INPUT';gpu='GPU-16828f91-2b45-b646-8dc0-9481138e2842';value=dict(kind='NEW_FROZEN_MICROBATCH_SOURCE_PREFLIGHT_NOT_ADMISSION',root=root,group_id=run,input_root=input_root,native_source_root=native,original_group_root=old,GPU_UUID=gpu,epoch=time.time(),not_yet_staged_or_dispatched=True);value.update(_a2_meta(fence));_a2_bind(value,fence);marker.write_text(json.dumps(value,indent=2),encoding='utf-8')
sys.path.insert(0,str(R.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
c=connect72();s=c.open_sftp()
def absent(p):
 try:s.lstat(p)
 except FileNotFoundError:return
 raise AssertionError('Fresh source/native path already exists: '+p)
def upload(p,raw):
 absent(p)
 with s.open(p,'wb')as f:f.write(raw)
try:
 absent(root);absent(input_root);s.mkdir(input_root);s.mkdir(input_root+'/source');pins=[]
 for e in manifest['files']:
  p=P/e['file'];raw=p.read_bytes();assert len(raw)==e['bytes']and hashlib.sha256(raw).hexdigest()==e['SHA'];name=p.name;assert'/'not in name and'\\'not in name;upload(input_root+'/source/'+name,raw);pins.append(dict(file='source/'+name,bytes=len(raw),SHA=e['SHA']))
 upload(input_root+'/MICROBATCH_STAGE_INDEX_V2.json',idx);upload(input_root+'/stage_a1_microbatch_eval_v2.py',b)
 argv=[input_root+'/stage_a1_microbatch_eval_v2.py','--original-group-root',old,'--source-dir',input_root+'/source','--source-index',input_root+'/MICROBATCH_STAGE_INDEX_V2.json','--native-root',native,'--new-root',root,'--group-id',run,'--gpu-uuid',gpu,'--preflight-only'];value.update(argv=argv,uploaded_sources=pins,stager_SHA=hashlib.sha256(b).hexdigest(),source_index_SHA=hashlib.sha256(idx).hexdigest());i,o,e=c.exec_command(shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -u -B '+' '.join(map(shlex.quote,argv)),timeout=240);i.close();text=o.read().decode();err=e.read().decode();rc=o.channel.recv_exit_status();value.update(returncode=rc,stdout=text,stderr=err);out.write_text(json.dumps(value,indent=2),encoding='utf-8');assert rc==0,err;v=json.loads(text);assert v['passed']is True and v['staged']is False and v['parent_launches']==0 and v['model_stat_hash_open_decode']==0;value['preflight']=v;out.write_text(json.dumps(value,indent=2),encoding='utf-8');print(json.dumps(dict(report=str(out),root=root,GPU_UUID=gpu,passed=True,source_files=v['files'],staged=False,parent_SDK_model_C_locks=0,native_closed_producer_steps={k:v['native_boundary']['producer_evidence'][k]['actual_BPTT_policy_steps']for k in('E3','W35')}),indent=2))
finally:s.close();c.close()
