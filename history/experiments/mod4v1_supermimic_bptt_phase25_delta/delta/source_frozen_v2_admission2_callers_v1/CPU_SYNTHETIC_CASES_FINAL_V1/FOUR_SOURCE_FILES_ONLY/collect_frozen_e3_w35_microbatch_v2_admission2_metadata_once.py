# NEW V2 dependency-complete evaluation purpose; do not replay consumed failedV1.
# NEW V2 ADMISSION2 own metadata observer; original ABI unchanged.
"""Single observer: published own frozen-eval JSON, then closed own logs once.
Never models/raw JSONL/SDK/GPU/C; no signal/resource mutations or work replay.
"""
from pathlib import Path
import sys,json,time,shlex

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
    _a2_need(type(gid) is str and gid.startswith(_A2_PREFIX) and len(gid) > len(_A2_PREFIX)
             and all(c.isalnum() or c == '_' for c in gid) and root == _A2_TASKS + gid and root != _A2_OLD_ROOT, 'new own root/group identity required')
    if 'input_root' in report: _a2_need(report['input_root'] == root + '_SOURCE_INPUT', 'new own source-input root differs')
    _a2_need(report.get('zero_GO_closed_metadata_SHA') == fence['zero_GO_closed_metadata_SHA']
             and report.get('zero_GO_closed_epoch') == fence['zero_GO_closed_epoch'], 'purpose not bound to this old actual zero-GO close')
    _a2_need(report.get('source_stage_SHA') == _A2_STAGE_SHA and report.get('source_index_SHA') == _A2_INDEX_SHA
             and report.get('source_parent_SHA') == _A2_PARENT_SHA, 'original stage/index/parent pins differ')
    _a2_need(_a2_epoch(report.get('epoch')) and report['epoch'] > fence['zero_GO_closed_epoch'], 'new purpose predates historical close')

R=Path(__file__).resolve().parent;guard=R/'FROZEN_E3_W35_BATCH_V2_ADMISSION2_OBSERVER_STARTED_ONCE.json';assert not guard.exists();d=json.loads((R/'reports/FROZEN_E3_W35_BATCH_V2_ADMISSION2_ACTUAL_PARENT_DISPATCH_V1.json').read_bytes());assert d['returncode']==0;fence=_a2_load_fence(R,False);_a2_bind(d,fence);m=d['receipt'];assert m['codeVersion']==_A2_VERSION and m['admission2_purpose']==_A2_PURPOSE and m['release_verified']is True;fence.update(release_verified=True,release_witness=m['release_witness']);root=d['root'];pid=m['parent']['pid'];ticks=str(m['parent']['linux_start_ticks']);folder=R/'reports'/('ACTUAL_FROZEN_E3_W35_BATCH_V2_ADMISSION2_'+time.strftime('%Y%m%d_%H%M%S'));folder.mkdir();pointer=R/'FROZEN_E3_W35_BATCH_V2_ADMISSION2_LATEST_METADATA_WATCH.json';guard.write_text(json.dumps(dict(root=root,folder=str(folder),epoch=time.time(),one_published_metadata_observer=True,**_a2_meta(fence)),indent=2),encoding='utf-8');sys.path.insert(0,str(R.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
c=connect72();s=c.open_sftp();last=None
roots=('PARENT_STARTED.json','BOUNDED_ORIGINAL_RESOURCE_WAIT.json','ACTUAL_GROUP_ADMISSION.json','CHILDREN.json','GROUP_BARRIER_STATUS.json','GROUP_EVAL_START.json','TERMINAL_ROWS.json','FINAL.json','GROUP_ABORT.json','PARENT_ORIGINAL_ERROR.json','PARENT_EXIT_SCOPE.json');case_names=('WORKER_SCENE_READY.json','WORKER_EVAL_STARTED.json','PROGRESS.json','FINAL.json','WORKER_ERROR.json','A1_EVAL_PRIMARY_ERROR_V2.json')
def get(rel):
 try:
  with s.open(root+'/'+rel,'rb')as f:raw=f.read()
 except FileNotFoundError:return None
 assert len(raw)<16*1024**2;return json.loads(raw)
def own_alive():
 code="from pathlib import Path;import json;p=Path('/proc/%d/stat');t=p.read_text()if p.exists()else '';f=t[t.rfind(')')+2:].split()if t else [];print(json.dumps(dict(alive=bool(f)and f[0]not in('Z','X')and f[19]==%r)))"%(pid,ticks);i,o,e=c.exec_command(shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B -c '+shlex.quote(code),timeout=30);i.close();text=o.read().decode();err=e.read().decode();assert o.channel.recv_exit_status()==0,err;return json.loads(text)['alive']
try:
 until=time.monotonic()+7200
 while time.monotonic()<until:
  top={n:get(n)for n in roots};exit_value=top['PARENT_EXIT_SCOPE.json'];started=top['PARENT_STARTED.json'];admit=top['ACTUAL_GROUP_ADMISSION.json'];earlydead=not started and not own_alive();rows=[]
  for role in('E3','W35'):
   values={n:get('cases/'+role+'/'+n)for n in case_names};final=values['FINAL.json'];error=values['WORKER_ERROR.json']or values['A1_EVAL_PRIMARY_ERROR_V2.json']
   status='ACTUAL_FROZEN_WORKER_ERROR'if error else('FROZEN_FINAL_AWAITING_ACTUAL_PARENT_WAIT'if final else('ACTUAL_FROZEN_EVALUATING'if values['WORKER_EVAL_STARTED.json']else('SCENE_READY_WAITING_ORIGINAL_BARRIER'if values['WORKER_SCENE_READY.json']else('SDK_OR_CACHE_STARTUP'if admit else'NOT_ADMITTED'))))
   rows.append(dict(role=role,status=status,**{n[:-5]:v for n,v in values.items()}))
  value=dict(kind='OWN_ACTUAL_FROZEN_QUALITY_METADATA_NOT_GRADUATION',epoch=time.time(),root=root,group_id=d['group_id'],top=top,rows=rows,closed=bool(exit_value),early_parent_dead=earlydead,waiting_original_resources=bool(top['BOUNDED_ORIGINAL_RESOURCE_WAIT.json'])and not admit and not exit_value,model_raw_JSONL_SDK_GPU_C_operations=0);value.update(_a2_meta(fence))
  target=folder/'CURRENT_METADATA.json';temp=folder/'CURRENT_METADATA.json.partial';assert target.parent==temp.parent==folder;temp.write_text(json.dumps(value,indent=2),encoding='utf-8');temp.replace(target);pointer.write_text(json.dumps(dict(root=root,folder=str(folder),current=str(target),closed=bool(exit_value),early_parent_dead=earlydead),indent=2),encoding='utf-8');signature=(bool(exit_value),bool(admit),earlydead,tuple((r['status'],(r['PROGRESS']or{}).get('control',0)//200)for r in rows))
  if signature!=last:print('FROZEN_QUALITY_ACTUAL_STATUS '+json.dumps(dict(root=root,closed=bool(exit_value),waiting_original_resources=value['waiting_original_resources'],early_parent_dead=earlydead,parent_error=bool(top['PARENT_ORIGINAL_ERROR.json']),rows=[dict(role=r['role'],status=r['status'],controls=(r['FINAL']or{}).get('controls'))for r in rows])),flush=True);last=signature
  if exit_value or earlydead:
   if exit_value:assert exit_value['all_own_children_waited']is True
   names=['GROUP_PLAN.json','STAGE_COMPLETE_MICROBATCH_V2.json','PARENT_FROZEN_MICROBATCH_DISPATCH_RECEIPT.json','PARENT_FROZEN_MICROBATCH_STDOUT_STDERR.log']+list(roots)
   if exit_value:
    for role in('E3','W35'):
     try:children=s.listdir(root+'/cases/'+role)
     except FileNotFoundError:children=[]
     names+=['cases/'+role+'/'+n for n in children if'/'not in n and'\\'not in n and(n.endswith('.json')or n=='SDK_FULL_STDOUT_STDERR.log')]
   copied=[]
   for rel in dict.fromkeys(names):
    assert not Path(rel).is_absolute()and'..'not in Path(rel).parts
    try:
     with s.open(root+'/'+rel,'rb')as f:raw=f.read()
    except FileNotFoundError:continue
    assert len(raw)<32*1024**2;dest=folder/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw);copied.append(dict(relative=rel,bytes=len(raw)))
   value['copied_files']=copied;(folder/'CLOSED_RESULT.json').write_text(json.dumps(value,indent=2),encoding='utf-8');(R/'FROZEN_E3_W35_BATCH_V2_ADMISSION2_LATEST_CLOSED_RESULT_PATH.json').write_text(json.dumps(dict(root=root,path=str(folder/'CLOSED_RESULT.json'),early_parent_dead=earlydead),indent=2),encoding='utf-8');print('FROZEN_QUALITY_CLOSED_RESULT '+str(folder/'CLOSED_RESULT.json'),flush=True);break
  time.sleep(20)
 else:raise TimeoutError('Own metadata observation cap, native evaluation not signalled or replayed')
finally:s.close();c.close()
