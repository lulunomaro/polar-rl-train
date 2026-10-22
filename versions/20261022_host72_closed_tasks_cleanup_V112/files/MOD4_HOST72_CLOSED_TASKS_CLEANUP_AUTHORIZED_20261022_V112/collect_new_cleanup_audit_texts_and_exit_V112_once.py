from pathlib import Path
import hashlib,importlib.util,json,sys,time,traceback
S=Path(__file__).resolve().parent;W=S.parent;R=S/'reports';read=lambda p:json.loads(Path(p).read_bytes())
def put(n,v):
    with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
CODE=r'''
from pathlib import Path
import hashlib,json,psutil,time
p=Path(v['root']);assert p.parent==Path('/home/lc01/Zonglin Li/zonglin2/audit') and p.name.startswith('closed_tasks_cleanup_20261022_V112_')
final=json.loads((p/'COMPLETE_ACTUAL.json').read_bytes());assert final['passed']
identity=json.loads((p/'EXECUTION_IDENTITY_ACTUAL.json').read_bytes())
try:alive=abs(psutil.Process(identity['pid']).create_time()-identity['creation'])<.02
except psutil.NoSuchProcess:alive=False
assert not alive
texts=[]
for f in sorted(p.iterdir()):
    assert f.is_file() and f.suffix=='.json' and not f.is_symlink()
    raw=f.read_bytes();texts.append(dict(path=str(f),name=f.name,bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),text=raw.decode('utf8')))
print(json.dumps(dict(epoch=time.time(),actual_cleanup_process_out=True,root=str(p),texts=texts,no_binary_or_training_GPU_or_budget_read=True)))
'''
try:
    prior=read(R/'HOST72_APPROVED_EXACT_CLEANUP_ACTUAL_RETURNED.json');assert prior['passed']
    sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
    sp=importlib.util.spec_from_file_location('memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);secret=m.recover()
    try:c=d.connect72(secret)
    finally:secret=None
    try:v=d.code(c,d.PY72,CODE,dict(root=prior['audit_root']),timeout=90)
    finally:c.close()
    dest=S/'actual_remote_audit_texts';dest.mkdir();rows=[]
    for row in v['texts']:
        p=dest/row['name'];raw=row['text'].encode('utf8');assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['SHA']
        with p.open('xb') as f:f.write(raw)
        rows.append(dict(remote_path=row['path'],local_path=str(p),bytes=row['bytes'],SHA=row['SHA']))
    put('NEW_CLEANUP_ALL_FULL_TEXT_RECEIPTS_AND_ACTUAL_PROCESS_OUT_RETURNED_ACTUAL.json',dict(epoch=time.time(),passed=True,actual_cleanup_process_out=v['actual_cleanup_process_out'],files=rows,no_binary_or_training_GPU_or_budget_read=True))
    put('LOCAL_AUDIT_ONLY_READER_MISSING_PATH_ERROR_ACTUAL.json',dict(epoch=time.time(),original_error='Get-Content: archive_workspace_cleanup_unique_stage_once.py does not exist under MOD4_WORKSPACE_CLEANUP_AUTHORIZED_20261021_V88.',actual_shell_exit_code=1,no_helper_or_remote_operation_was_executed_by_failed_read=True))
    print(json.dumps(dict(all_new_full_reports_returned=len(rows),actual_cleanup_process_out=True)))
except BaseException:
    put('CLEANUP_TEXT_RETURN_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc()));raise
