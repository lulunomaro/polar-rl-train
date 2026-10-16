"""Append to the recorded U trial; never create a second trial or tag."""
from pathlib import Path
import sys,time,json,hashlib,importlib.util,traceback
N=Path(__file__).resolve().parent;W=N.parent;REPO=W/'polar-rl-train';R=N/'reports';BASE='82cf3e7ee3bd22f9c37c53790e7ae4689995fcb7';DEST=REPO/'history/evidence'/N.name/'postcapture_actual_network_unknown_monitorV3_Gitreceipt_ordinary_v1'
sp=importlib.util.spec_from_file_location('existing_archive_functions_only',W/'MOD4_HOST72_THREE_GPU_SINGLE_PPO_7H_20261016/archive_three_gpu_single_PPO_seven_hour_stage_once.py');g=importlib.util.module_from_spec(sp);sp.loader.exec_module(g);git=g.git;H=g.H
def main():
 assert git('rev-parse','HEAD')==BASE and not git('status','--porcelain') and not DEST.exists();old={}
 for line in git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags/').splitlines():
  a=line.split();old[a[0]]=(a[1],a[2] if len(a)>2 else a[1])
 assert len(old)==1361 and old['refs/tags/trial-20261017-unified-three-independent-h1-e2-e3-original-handoff']==('7a5b5757bf2bddbb2536aca3f41bef8a04d3e9f0',BASE);prior={}
 for index in (REPO/'history/evidence'/N.name).rglob('REPORT_CAPTURE_INDEX.json'):
  for row in json.loads(index.read_bytes()).get('entries',[]):prior[row['sha256']]=row
 sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
 DEST.mkdir(parents=True);rows=[];files=[];deferred=[]
 for p in sorted(x for x in N.rglob('*') if x.is_file() and '__pycache__' not in x.parts):
  if p.suffix=='.partial':deferred.append(str(p));continue
  before=p.stat();large=before.st_size>8*1024*1024 or p.suffix.lower() in ('.pt','.pth','.npz','.npy','.usd','.usda','.usdc','.zip','.gz','.mp4','.dmp','.tar');raw=None
  if large:h=H(p)
  else:raw=p.read_bytes();h=hashlib.sha256(raw).hexdigest()
  after=p.stat();assert (before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns),str(p);row=dict(source_path=str(p.resolve()),bytes=before.st_size,sha256=h)
  if h in prior:
   prev=prior[h];row.update(capture='same_SHA_previous_Git_capture_reference',original_retained=True)
   if prev.get('Git_path'):assert H(REPO/prev['Git_path'])==prev['archived_sha256'];row.update(Git_path=prev['Git_path'],archived_sha256=prev['archived_sha256'])
  elif large:row.update(capture='large_actual_path_size_SHA_index_only',original_retained=True)
  else:
   try:text=raw.decode('utf8')
   except UnicodeDecodeError:row.update(capture='binary_actual_path_size_SHA_index_only',original_retained=True);rows.append(row);continue
   clean,n=redact(text);data=clean.encode('utf8') if n else raw;out=DEST/p.relative_to(N);out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data);rel=out.relative_to(REPO).as_posix();files.append(rel);row.update(capture='redacted_full' if n else 'complete_exact_bytes',Git_path=rel,archived_sha256=hashlib.sha256(data).hexdigest(),redactions=n)
  rows.append(row)
 index=DEST/'REPORT_CAPTURE_INDEX.json';index.write_text(json.dumps(dict(epoch=time.time(),entries=rows,ordinary_no_new_trial_tag=True,all_originals_retained=True,deferred=deferred,current_remote_PIDs_FINAL_cost_OSlocks_unknown_due_dual_connect_TimeoutError=True,complete_immutable_first_CPU_pending0_not_failed_tensor_audit=True,later_results_ordinarysupplement=True),indent=2),encoding='utf8');files.append(index.relative_to(REPO).as_posix());git('add','--',*files);git('commit','-m','Archive three-slot actual network handoff and verified unique-stage receipt');head=git('rev-parse','HEAD');git('push','origin','HEAD:main');g.n.m.cap.a.gitio.g=git;g.n.m.cap.a.verify(rows,old,head);print(json.dumps(dict(commit=head,ordinary_no_new_tag=True,actual_remote_main_all1361_original_tag_objects_peels_tracked_SHA_verified=True,source_entries=len(rows),new_capture_files=len(files),deferred=deferred)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('POSTCAPTURE_ORDINARY_GIT_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),if_committed_continue_existingobjects_only_no_new_record_tag_commit=True),f,indent=2)
  raise
