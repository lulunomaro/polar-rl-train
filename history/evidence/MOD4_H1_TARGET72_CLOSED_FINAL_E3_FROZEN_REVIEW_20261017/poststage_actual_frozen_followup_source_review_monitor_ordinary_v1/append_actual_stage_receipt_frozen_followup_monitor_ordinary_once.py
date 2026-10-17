"""Ordinary supplement only; unique stage/tag already consumed, never re-records runtime."""
from pathlib import Path
import os,sys,json,time,hashlib,importlib.util,traceback
B=Path(__file__).resolve().parent;R=B/'reports';REPO=B.parent/'polar-rl-train';BASE='0001cab6f0ed97d318d0fa3e4851cac93a5fbe39';DEST=REPO/'history/evidence'/B.name/'poststage_actual_frozen_followup_source_review_monitor_ordinary_v1'
sp=importlib.util.spec_from_file_location('current_unique_stage_functions_only',B/'archive_H1_closed_final_native180_E3_frozen_actual_unique_stage_once.py');stage=importlib.util.module_from_spec(sp);sp.loader.exec_module(stage);git=stage.rawgit;H=stage.H
def main():
 assert git('rev-parse','HEAD')==BASE and not git('status','--porcelain') and not DEST.exists();old={}
 for line in git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags/').splitlines():
  s=line.split();old[s[0]]=(s[1],s[2] if len(s)>2 else s[1])
 assert len(old)==1371 and old['refs/tags/'+stage.TAG]==('f36b2d58280b18bbfbd62ad6a3207e554c906ba7',BASE);prior={}
 for p in (REPO/'history/evidence'/B.name).rglob('REPORT_CAPTURE_INDEX.json'):
  for row in json.loads(p.read_bytes())['entries']:
   if row.get('Git_path'):prior[row['sha256']]=row
 sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
 DEST.mkdir(parents=True);rows=[];files=[];deferred=[]
 for p in sorted(x for x in B.rglob('*') if x.is_file() and '__pycache__' not in x.parts):
  if p.suffix=='.partial':deferred.append(str(p));continue
  with p.open('rb') as f:
   st=os.fstat(f.fileno());large=p.suffix.lower() in ('.pt','.pth','.npz','.npy','.usd','.usda','.usdc','.zip','.tar','.gz','.mp4','.dmp') or (st.st_size>8*1024**2 and p.suffix.lower() not in ('.json','.jsonl','.txt','.md','.py','.toml','.log'));h=hashlib.sha256();raw=None
   if large:
    for chunk in iter(lambda:f.read(4194304),b''):h.update(chunk)
   else:raw=f.read();h.update(raw)
   en=os.fstat(f.fileno());assert (st.st_size,st.st_mtime_ns)==(en.st_size,en.st_mtime_ns)
  digest=h.hexdigest();row=dict(source_path=str(p.resolve()),bytes=st.st_size,sha256=digest)
  if digest in prior:
   ref=prior[digest];assert H(REPO/ref['Git_path'])==ref['archived_sha256'];row.update(capture='same_SHA_original_Git_reference',Git_path=ref['Git_path'],archived_sha256=ref['archived_sha256'])
  elif large:row.update(capture='large_artifact_actual_path_size_SHA_index_only',original_retained=True)
  else:
   try:clean,n=redact(raw.decode('utf8'))
   except UnicodeDecodeError:row.update(capture='binary_actual_path_size_SHA_index_only',original_retained=True);rows.append(row);continue
   data=clean.encode('utf8') if n else raw;dest=DEST/p.relative_to(B);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data);rel=dest.relative_to(REPO).as_posix();files.append(rel);row.update(capture='redacted_full' if n else 'complete_exact_bytes',Git_path=rel,archived_sha256=hashlib.sha256(data).hexdigest(),redactions=n)
  rows.append(row)
 index=DEST/'REPORT_CAPTURE_INDEX.json';index.write_text(json.dumps(dict(epoch=time.time(),entries=rows,deferred=deferred,ordinary_append_no_record_tag_or_runtime=True,all_saved_text_reports_full_bytes_even_over8MiB=True,all_followup_success_errors_sources_receipt_monitor_captured=True,large_model_raw_USD_ZIP_actual_index_only=True,future_saved_reports_need_ordinary_supplement=True),indent=2),encoding='utf8');files.append(index.relative_to(REPO).as_posix());git('add','--',*files);git('commit','-m','Append frozen E3 followup, E2 source diagnostics and actual H1 handoff monitor');head=git('rev-parse','HEAD');git('push','origin','HEAD:main');stage.prev.prev.g.n.m.cap.a.gitio.g=git;stage.prev.prev.g.n.m.cap.a.verify(rows,old,head);print(json.dumps(dict(commit=head,ordinary_no_new_tag=True,actual_remote_main_all1371_original_tag_objects_peels_tracked_SHA_verified=True,source_entries=len(rows),capture_files=len(files),deferred=deferred)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('H1_E3_POSTSTAGE_ORDINARY_GIT_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),if_commit_exists_continue_existing_objects_only_no_record_tag_recommit_or_runtime_replay=True),f,indent=2)
  raise
