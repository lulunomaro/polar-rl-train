"""Ordinary supplement to existing annotated trial. Never rerecord/recommit."""
from pathlib import Path
import importlib.util,sys,json,time,hashlib,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';REPO=W/'polar-rl-train';BASE='0bd19a40d8b8d1788445375228a05dc52d7f95f9';DEST=REPO/'history/evidence'/D.name/'v3_full_native_numerical_references_v7_three_real_experts_ordinary_v1'
s=importlib.util.spec_from_file_location('actual_stage_pure_helpers',D/'archive_new_curb_approach_E3_recovery_actual_stage_once.py');g=importlib.util.module_from_spec(s);s.loader.exec_module(g);git=g.git;H=g.H
def main():
 assert git('rev-parse','HEAD')==BASE and not git('status','--porcelain') and not DEST.exists();old={}
 for line in git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags/').splitlines():
  x=line.split();old[x[0]]=(x[1],x[2] if len(x)>2 else x[1])
 assert len(old)==1358;prior={}
 for index in (REPO/'history/evidence'/D.name).rglob('REPORT_CAPTURE_INDEX.json'):
  for row in json.loads(index.read_bytes()).get('entries',[]):
   if row.get('Git_path'):prior[row['sha256']]=row
 sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
 DEST.mkdir();rows=[];files=[];deferred=[]
 for p in sorted(x for x in D.rglob('*') if x.is_file() and '__pycache__' not in x.parts):
  if p.suffix=='.partial':deferred.append(str(p));continue
  before=p.stat();size=before.st_size;large=size>8*1024*1024 or p.suffix.lower() in ('.pt','.pth','.npz','.npy','.usd','.usda','.usdc','.zip','.gz','.mp4','.dmp','.tar');raw=None
  if large:h=H(p)
  else:raw=p.read_bytes();h=hashlib.sha256(raw).hexdigest()
  after=p.stat();assert (before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns),'Mutable artifact at capture';row=dict(source_path=str(p.resolve()),bytes=size,sha256=h)
  if h in prior:
   previous=prior[h];assert H(REPO/previous['Git_path'])==previous['archived_sha256'];row.update(capture='same_SHA_existing_Git_reference',Git_path=previous['Git_path'],archived_sha256=previous['archived_sha256'])
  elif large:row.update(capture='large_actual_path_size_SHA_index_only',original_retained=True)
  else:
   try:text=raw.decode('utf8')
   except UnicodeDecodeError:row.update(capture='binary_actual_path_size_SHA_index_only',original_retained=True);rows.append(row);continue
   clean,n=redact(text);data=clean.encode('utf8') if n else raw;out=DEST/p.relative_to(D);out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data);rel=out.relative_to(REPO).as_posix();files.append(rel);row.update(capture='redacted_full' if n else 'complete_exact_bytes',Git_path=rel,archived_sha256=hashlib.sha256(data).hexdigest(),redactions=n)
  rows.append(row)
 index=DEST/'REPORT_CAPTURE_INDEX.json';index.write_text(json.dumps(dict(epoch=time.time(),entries=rows,existing_trial_no_new_record_or_tag=True,uncompleted_SFTP_partial_files_deferred=deferred,all_saved_success_false_reject_reader_sources_CPU_deploy_monitor_at_capture_included=True,later_results_require_supplement=True),indent=2),encoding='utf8');files.append(index.relative_to(REPO).as_posix());git('add','--',*files);git('commit','-m','Preserve full E3 numerical audit failures and corrections, V2/V4 saved costs and V7 distinct expert execution');head=git('rev-parse','HEAD');git('push','origin','HEAD');g.g.n.m.cap.a.gitio.g=git;g.g.n.m.cap.a.verify(rows,old,head,None,None);print(json.dumps(dict(ordinary_commit=head,no_new_trial_tag=True,actual_remote_main_all1358_tag_objects_peels_and_tracked_sources_verified=True,sources=len(rows),new_files=len(files),deferred=len(deferred))),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('V7_ORDINARY_GIT_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),only_existingobjects_after_commit_no_repeat_commit_record_or_tag=True),f,indent=2)
  raise
