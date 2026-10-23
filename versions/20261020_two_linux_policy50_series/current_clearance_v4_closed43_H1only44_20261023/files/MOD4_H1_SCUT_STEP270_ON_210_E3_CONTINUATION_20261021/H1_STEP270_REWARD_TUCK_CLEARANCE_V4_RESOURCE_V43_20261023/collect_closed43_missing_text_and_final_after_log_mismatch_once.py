"""Only missing closed43 text/final and one mismatched log snapshot; no GO or accounting write."""
from pathlib import Path, PurePosixPath
import base64, hashlib, importlib.util, json, time, traceback

N = Path(__file__).resolve().parent
R = N / 'reports'
H = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
read = lambda p: json.loads(Path(p).read_bytes())

def put(name, value):
    with (R / name).open('x', encoding='utf8') as f:
        json.dump(value, f, ensure_ascii=False, indent=2)

READ = r'''
from pathlib import Path
import base64, hashlib, json, os, psutil, time
q=v['q']; roots=(q['owner_root'],q['roots']['h1']); live=[]
for p in psutil.process_iter(['pid','cmdline','create_time']):
 try:
  if p.pid!=os.getpid() and any(a.startswith(tuple(r+'/' for r in roots)) for a in p.info['cmdline'] or []):live.append(p.info)
 except psutil.Error:pass
assert not live,live
p=Path(v['path']); assert str(p).startswith(q['roots']['h1']+'/') and p.name=='omni.processlifetime.log'
before=p.stat();raw=p.read_bytes();after=p.stat()
assert (before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns)
print(json.dumps(dict(epoch=time.time(),actual_own_processes_out=True,path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),stat=dict(device=after.st_dev,inode=after.st_ino,mtime_ns=after.st_mtime_ns,nlink=after.st_nlink),base64=base64.b64encode(raw).decode(),no_budget_GPU_model_or_raw_query=True)))
'''

def main():
    assert not (R/'H1_ONLY_COMPLETE_FINAL_ORIGINAL_COST_RETURNED_ACTUAL.json').exists()
    original=read(R/'H1_ONLY_CLOSED_CANONICAL_COST_ACTUAL.json')
    q=read(R/'H1_ONLY_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json')
    assert original['all_owner_H1_children_actual_out'] and original['cohort']['original_cost_settled']
    good=[];bad=[];missing=[]
    for row in original['text_files']:
        p=N/'current_pair_closed_text'/Path(*PurePosixPath(row['relative']).parts)
        if not p.exists():missing.append(row)
        elif p.stat().st_size==row['bytes'] and H(p)==row['SHA']:
            good.append(dict(row,local_path=str(p),previous_verified_transfer_retained=True))
        else:bad.append(dict(row,local_path=str(p),actual_bytes=p.stat().st_size,actual_SHA=H(p)))
    assert len(bad)==1 and bad[0]['relative']=='h1/job0/home/.nvidia-omniverse/logs/omni.processlifetime.log'
    put('CLOSED43_TEXT_LOG_MISMATCH_MISSING_ONLY_STARTED_ACTUAL.json',dict(epoch=time.time(),verified_existing=len(good),missing=len(missing),original_mismatch=bad,no_old_once_rerun=True,no_training_failure_or_refund_inferred=True))
    spec=importlib.util.spec_from_file_location('closed43_original_collector_source',N/'collect_selected_H1_final_unused_once.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    c=module.d.t.connect()
    try:
        fresh=module.d.code(c,module.d.t.PY,READ,dict(q=q,path=bad[0]['path']),timeout=60)
        raw=base64.b64decode(fresh.pop('base64'));assert len(raw)==fresh['bytes'] and hashlib.sha256(raw).hexdigest()==fresh['SHA']
        p=Path(bad[0]['local_path']).with_name('omni.processlifetime.fresh_after_original_mismatch.log')
        with p.open('xb') as f:f.write(raw)
        freshrow=dict(bad[0],bytes=fresh['bytes'],SHA=fresh['SHA'],local_path=str(p),fresh_single_remote_read_snapshot=fresh,original_expected_and_transferred_versions_preserved=True)
        freshrow.pop('actual_bytes');freshrow.pop('actual_SHA')
        put('CLOSED43_PROCESSLIFETIME_LOG_ORIGINAL_MISMATCH_AND_FRESH_SNAPSHOT_ACTUAL.json',dict(epoch=time.time(),original=bad[0],fresh=freshrow,cause='unknown; two byte versions retained, no training failure or permanent stability inferred'))
        final=original['cohort']['rows']['h1']['final'];assert final['passed'] and final['final']['updates']>0
        texts,models=module.capture(c,dict(text_files=missing),[final['final']],'h1')
    finally:c.close()
    alltexts=good+[freshrow]+texts
    assert len(alltexts)==len(original['text_files']) and len(models)==1
    result=dict(epoch=time.time(),actual_finite_transport_returned=True,source210=original,complete_models=dict(h1=models),all_texts=alltexts,original_canonical_cost_settled=True,E3_no_GO_or_cost_interval=True,not_skill_qualification=True,missing_only_collection=True,original_mismatched_log_preserved=True,log_snapshot_correction_receipt=str(R/'CLOSED43_PROCESSLIFETIME_LOG_ORIGINAL_MISMATCH_AND_FRESH_SNAPSHOT_ACTUAL.json'))
    put('H1_ONLY_COMPLETE_FINAL_ORIGINAL_COST_RETURNED_ACTUAL.json',result)
    put('CLOSED43_MISSING_ONLY_TEXT_FINAL_ACTUAL_RETURNED.json',dict(epoch=time.time(),passed=True,retained_existing_texts=len(good),new_missing_texts=len(texts),fresh_mismatched_log_versions_retained=True,complete_model=models[0],original_cost_reused_not_recharged=True))
    print(json.dumps(dict(closed=True,complete_models=1,missing_texts=len(texts),existing_retained=len(good),original_log_mismatch_preserved=True)))

if __name__=='__main__':
    try:main()
    except BaseException:
        put('CLOSED43_MISSING_ONLY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_rerun_refund_or_training_signal=True));raise
