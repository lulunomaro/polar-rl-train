"""Repair two text-log index gaps losslessly; ordinary append, never reruns any case."""
from pathlib import Path
import os,sys,json,time,hashlib,base64,importlib.util,traceback
B=Path(__file__).resolve().parent;R=B/'reports';REPO=B.parent/'polar-rl-train';BASE='7d82ddaa1d498482274f92a40e4815ac0e0a0790';DEST=REPO/'history/evidence'/B.name/'poststage_mixed_encoding_worker_logs_full_exact_bytes_ordinary_v2';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
sp=importlib.util.spec_from_file_location('previous_ordinary_functions_only',B/'append_actual_stage_receipt_frozen_followup_monitor_ordinary_once.py');old=importlib.util.module_from_spec(sp);sp.loader.exec_module(old);git=old.git
def main():
 assert git('rev-parse','HEAD')==BASE and not git('status','--porcelain') and not DEST.exists();tags={}
 for line in git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags/').splitlines():
  s=line.split();tags[s[0]]=(s[1],s[2] if len(s)>2 else s[1])
 assert len(tags)==1371;index=REPO/'history/evidence'/B.name/'poststage_actual_frozen_followup_source_review_monitor_ordinary_v1/REPORT_CAPTURE_INDEX.json';prior=json.loads(index.read_bytes());gaps=[r for r in prior['entries'] if Path(r['source_path']).suffix=='.log' and not r.get('Git_path')];assert len(gaps)==2;sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
 captures=[];bindings=[];created=[]
 for n,row in enumerate(gaps):
  p=Path(row['source_path']);raw=p.read_bytes();assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['sha256']
  try:raw.decode('utf8')
  except UnicodeDecodeError as e:bad=dict(start=e.start,end=e.end,reason=e.reason)
  else:raise AssertionError('Original log unexpectedly became UTF8')
  for codec in ('utf8','cp936'):assert redact(raw.decode(codec,errors='backslashreplace'))[1]==0,'Credential-like content requires explicit redaction before full log capture'
  value=dict(original_path=str(p),original_bytes=len(raw),original_SHA=row['sha256'],encoding='base64 of exact original mixed-encoding bytes',payload_base64=base64.b64encode(raw).decode('ascii'),strict_UTF8_decode_original_error=bad,no_guess_or_lossy_encoding_rewrite=True,original_logs_retained_and_not_replayed=True,UTF8_and_CP936_backslashreplace_secret_scans_redactions0=True)
  q=R/('EXACT_MIXED_ENCODING_'+('FULL1500' if 'full1500' in str(p) else 'NATIVE120')+'_WORKER_LOG_BYTES.json')
  with q.open('x',encoding='utf8') as f:json.dump(value,f,indent=2)
  assert base64.b64decode(value['payload_base64'])==raw;created.append(q);bindings.append(dict(original_source_path=str(p),original_bytes=len(raw),original_SHA=row['sha256'],exact_bytes_wrapper_path=str(q),wrapper_SHA=H(q)))
 diagnostic=R/'FINAL_TEXT_CHECK_V1_MIXED_ENCODING_LOG_INDEX_REJECTION_AND_EXACT_BYTES_REPAIR_ACTUAL.json'
 with diagnostic.open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),original_final_check_error_type='AssertionError',original_assertion="assert row.get('Git_path'), str(p)",original_first_failure_path=gaps[1]['source_path'],original_inline_tool_check_not_a_saved_source_file=True,actual_cause='Two non-UTF8 mixed-encoding SDK worker logs were previously classified binary and indexed only',original_stage_and_ordinary_index_classification_preserved=True,new_lossless_full_bytes_wrappers=bindings,full_original_bytes_recoverable_and_SHA_verified=True,no_GPU_Task_native_or_raw_redownload=True,no_model_physics_reward_budget_or_outcome_change=True),f,indent=2)
 created += [diagnostic,Path(__file__).resolve()];DEST.mkdir(parents=True);rows=[];files=[]
 for p in created:
  raw=p.read_bytes();text=raw.decode('utf8');clean,n=redact(text);assert n==0;dst=DEST/p.relative_to(B);dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(raw);rel=dst.relative_to(REPO).as_posix();files.append(rel);rows.append(dict(source_path=str(p),bytes=len(raw),sha256=H(p),capture='complete_exact_bytes',Git_path=rel,archived_sha256=H(dst)))
 for binding in bindings:binding['wrapper_Git_path']=next(r['Git_path'] for r in rows if r['source_path']==binding['exact_bytes_wrapper_path'])
 idx=DEST/'REPORT_CAPTURE_INDEX.json';idx.write_text(json.dumps(dict(epoch=time.time(),entries=rows,full_log_encodings=bindings,previous_complete_index=str(index.relative_to(REPO)),all_saved_text_and_mixed_encoding_logs_fully_recoverable=True,ordinary_no_new_trial_tag_or_runtime=True),indent=2),encoding='utf8');files.append(idx.relative_to(REPO).as_posix());git('add','--',*files);git('commit','-m','Preserve exact bytes of mixed-encoding frozen E3 worker logs');head=git('rev-parse','HEAD');git('push','origin','HEAD:main');old.stage.prev.prev.g.n.m.cap.a.gitio.g=git;old.stage.prev.prev.g.n.m.cap.a.verify(rows,tags,head);print(json.dumps(dict(commit=head,ordinary_no_new_tag=True,all1371_original_tag_objects_peels_and_remote_main_verified=True,full_mixed_encoding_logs=len(bindings),exact_original_log_bytes_recoverable=True,source_entries=len(rows))),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('EXACT_LOG_BYTES_ORDINARY_V2_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),if_commit_exists_continue_existing_objects_only_no_rerun_record_tag_commit_or_GPU=True),f,indent=2)
  raise
