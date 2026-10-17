"""Ordinary evidence append after the one real backend stage; no new record/tag/runtime."""
from pathlib import Path
import os,sys,json,time,hashlib,importlib.util,traceback
B=Path(__file__).resolve().parent;W=B.parent;R=B/'reports';M=W/'MOD4_RECOVERY_CLOSED_FINAL_H1_STORAGE_BOUNDED_HANDOFF_20261017';REPO=W/'polar-rl-train';BASE='8691d3f9201452d6a3ca2f2bc795ab92b6e9b973';DEST=REPO/'history/evidence'/B.name/'poststage_native_first_current_handoff_monitor_ordinary_v1'
sp=importlib.util.spec_from_file_location('existing_target72_stage_Git_functions_only',B/'archive_H1_closed24_target72_new_backend_same_scope_unique_stage_once.py');prev=importlib.util.module_from_spec(sp);sp.loader.exec_module(prev);git=prev.rawgit;H=prev.H
def main():
 assert git('rev-parse','HEAD')==BASE and not git('status','--porcelain') and not DEST.exists();old={}
 for line in git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags/').splitlines():
  s=line.split();old[s[0]]=(s[1],s[2] if len(s)>2 else s[1])
 assert len(old)==1370 and old['refs/tags/'+prev.TAG]==('c5afc999d60f6b83c12859899ccbaca670db2a73',BASE);prior={}
 for name in (M.name,B.name):
  for p in (REPO/'history/evidence'/name).rglob('REPORT_CAPTURE_INDEX.json'):
   for row in json.loads(p.read_bytes())['entries']:
    if row.get('Git_path'):prior[row['sha256']]=row
 sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
 DEST.mkdir(parents=True);rows=[];files=[];deferred=[]
 for root in (M,B):
  for p in sorted(x for x in root.rglob('*') if x.is_file() and '__pycache__' not in x.parts):
   if p.suffix=='.partial':deferred.append(str(p));continue
   with p.open('rb') as f:
    st=os.fstat(f.fileno());large=st.st_size>8*1024**2 or p.suffix.lower() in ('.pt','.pth','.npz','.npy','.usd','.usda','.usdc','.zip','.tar','.gz','.mp4','.dmp');h=hashlib.sha256();raw=None
    if large:
     for x in iter(lambda:f.read(4194304),b''):h.update(x)
    else:raw=f.read();h.update(raw)
    en=os.fstat(f.fileno());assert (st.st_size,st.st_mtime_ns)==(en.st_size,en.st_mtime_ns)
   sha=h.hexdigest();row=dict(source_path=str(p.resolve()),bytes=st.st_size,sha256=sha)
   if sha in prior:
    ref=prior[sha];assert H(REPO/ref['Git_path'])==ref['archived_sha256'];row.update(capture='same_SHA_prior_Git_reference',Git_path=ref['Git_path'],archived_sha256=ref['archived_sha256'])
   elif large:row.update(capture='large_artifact_actual_path_size_SHA_index_only',original_retained=True)
   else:
    try:clean,n=redact(raw.decode('utf8'))
    except UnicodeDecodeError:row.update(capture='binary_actual_path_size_SHA_index_only',original_retained=True);rows.append(row);continue
    data=clean.encode('utf8') if n else raw;dest=DEST/root.name/p.relative_to(root);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data);rel=dest.relative_to(REPO).as_posix();files.append(rel);row.update(capture='redacted_full' if n else 'complete_exact_bytes',Git_path=rel,archived_sha256=hashlib.sha256(data).hexdigest(),redactions=n)
   rows.append(row)
 index=DEST/'REPORT_CAPTURE_INDEX.json';index.write_text(json.dumps(dict(epoch=time.time(),entries=rows,deferred=deferred,ordinary_append_no_record_tag_or_runtime_action=True,all_M_followup_target72_actual_sources_reports_workorders_monitor_receipts_captured=True,original_models_and_raw_retained_except_original_authorized_L189=True,future_FINAL_or_saved_receipts_need_ordinary_supplement=True),indent=2),encoding='utf8');files.append(index.relative_to(REPO).as_posix());git('add','--',*files);git('commit','-m','Append target72 H1 finite-chain evidence and current handoff monitor');head=git('rev-parse','HEAD');git('push','origin','HEAD:main');prev.prev.g.n.m.cap.a.gitio.g=git;prev.prev.g.n.m.cap.a.verify(rows,old,head);print(json.dumps(dict(commit=head,ordinary_no_new_trial_tag=True,actual_remote_main_all1370_original_tags_object_peels_tracked_SHA_verified=True,source_entries=len(rows),capture_files=len(files),deferred=deferred)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('H1_TARGET72_POSTSTAGE_ORDINARY_GIT_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),if_commit_exists_continue_existing_objects_only_no_record_tag_recommit_or_runtime_retry=True),f,indent=2)
  raise
