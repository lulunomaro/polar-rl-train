from pathlib import Path
import importlib.util,json,sys,time,traceback
B=Path(__file__).resolve().parent;T=B.parent;W=T.parent;R=B/'reports'
def put(n,v):
    with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
CODE=r'''
from pathlib import Path
from collections import defaultdict,Counter
import json,os,shutil,stat,time
base=Path('/home/lc01/Zonglin Li/zonglin2/tasks');assert base.resolve(strict=True)==base
started=time.time();files=[];links=[];errors=[];markers=[]
for folder,dirs,names in os.walk(base,followlinks=False):
    assert time.time()-started<180,'Bounded metadata inventory elapsed'
    for name in list(dirs):
        p=Path(folder)/name
        if p.is_symlink():links.append(dict(path=str(p),kind='directory_symlink_not_followed'));dirs.remove(name)
    for name in names:
        p=Path(folder)/name
        try:
            s=p.lstat()
            if stat.S_ISLNK(s.st_mode):links.append(dict(path=str(p),kind='file_symlink_not_followed'));continue
            if not stat.S_ISREG(s.st_mode):continue
            rel=p.relative_to(base).as_posix()
            row=dict(path=str(p),relative=rel,bytes=s.st_size,allocated_bytes=s.st_blocks*512,mtime_ns=s.st_mtime_ns,inode=s.st_ino,device=s.st_dev,nlink=s.st_nlink)
            files.append(row)
            if name in ('NODE_EXIT_ACTUAL.json','OWNER_EXIT_ACTUAL.json','FINAL.json','FINAL_ACTUAL.json','THREE_SLOT_COMPLETE_MANIFEST_V1.json','CONTROL_VALID_PREFIX_INDEX_ACTUAL.json','PREFIX_PAIR_RETENTION_HISTORY_ACTUAL.json') and s.st_size<8*1024**2:
                try:markers.append(dict(path=str(p),bytes=s.st_size,value=json.loads(p.read_bytes())))
                except Exception as e:errors.append(dict(path=str(p),read_error=repr(e)))
        except Exception as e:errors.append(dict(path=str(p),stat_error=repr(e)))
groups=defaultdict(lambda:dict(files=0,logical_bytes=0,allocated_bytes=0,suffixes=Counter()))
seen=set()
for row in files:
    g=groups[row['relative'].split('/')[0]];g['files']+=1;g['logical_bytes']+=row['bytes'];g['suffixes'][Path(row['path']).suffix.lower()]+=row['bytes']
    key=(row['device'],row['inode'])
    if key not in seen:g['allocated_bytes']+=row['allocated_bytes'];seen.add(key)
disk=shutil.disk_usage(base)
print(json.dumps(dict(epoch=time.time(),root=str(base),elapsed=time.time()-started,files=files,symlinks=links,errors=errors,small_saved_markers=markers,
  groups=groups,filesystem=dict(total=disk.total,used=disk.used,free=disk.free),
  only_metadata_and_existing_small_JSON_no_NPZ_PT_USD_binary_read_or_hash=True,
  no_training_GPU_actor_optimizer_peer_identity_or_budget_access=True,
  no_delete_move_hardlink_permission_change_or_new_remote_file=True)))
'''
try:
    put('V112_HUMAN_CLOSED_TASKS_CLEANUP_QUESTION_SCOPE_ACTUAL.json',dict(epoch=time.time(),
      exact_human_question='旧训练任务：526.4GB 一点能清理的都没有？',
      actual_scope='Read-only exact file inventory and existing small closure/producer manifests to identify reviewable redundant or disposable candidates. No deletion.',
      existing_originals_future_only_retention_scope_preserved=True,
      local_read_error=dict(operation='Initial local legacy inventory report read',actual_error='File not found: H1_STEP270_REWARD_PATH_V1_20261022/reports/V101_CLOSED72_E3_INTERMEDIATE_PT_READONLY_CANDIDATES_ACTUAL.json; actual report is T/reports/',no_remote_call_or_training_effect=True)))
    sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
    sp=importlib.util.spec_from_file_location('memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
    secret=m.recover()
    try:c=d.connect72(secret)
    finally:secret=None
    try:v=d.code(c,d.PY72,CODE,{},timeout=210)
    finally:c.close()
    put('V112_HOST72_TASKS_EXACT_FILES_AND_SMALL_CLOSED_MANIFESTS_READONLY_ACTUAL.json',v)
    from collections import Counter
    suffix=Counter()
    for row in v['files']:suffix[Path(row['path']).suffix.lower()]+=row['bytes']
    print(json.dumps(dict(files=len(v['files']),errors=v['errors'],filesystem=v['filesystem'],largest_suffixes=suffix.most_common(12),largest_groups=sorted([(k,x['allocated_bytes']) for k,x in v['groups'].items()],key=lambda x:-x[1])[:12],small_manifests=len(v['small_saved_markers']))))
except BaseException:
    put('V112_TASKS_READONLY_INVENTORY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc()));raise
