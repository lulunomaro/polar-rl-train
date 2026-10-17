"""Ordinary supplement only; never record/tag this stage again."""
from pathlib import Path
import os,sys,time,json,hashlib,importlib.util,traceback
F=Path(__file__).resolve().parent;W=F.parent;REPO=W/'polar-rl-train';R=F/'reports';BASE='39bd29af20ec6e192c4550aba43827539753b59c';DEST=REPO/'history/evidence'/F.name/'postcapture_v8_finals_fixed105_regression_recovery_only_monitor_receipt_ordinary_v1'
sp=importlib.util.spec_from_file_location('existing_G_archive_functions_only',W/'MOD4_HOST72_THREE_GPU_SINGLE_PPO_7H_20261016/archive_three_gpu_single_PPO_seven_hour_stage_once.py');g=importlib.util.module_from_spec(sp);sp.loader.exec_module(g);git=g.git;H=g.H
def main():
 assert git('rev-parse','HEAD')==BASE and not git('status','--porcelain') and not DEST.exists();old={}
 for line in git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags/').splitlines():
  a=line.split();old[a[0]]=(a[1],a[2] if len(a)>2 else a[1])
 assert len(old)==1367 and old['refs/tags/trial-20261017-v8-finals-fixed105-regression-recovery-only-original-handoff']==('f110b4df2978c869f56a5722ad84d8b8b3cc759e',BASE);prior={}
 for index in [p for name in (F.name,'MOD4_V7_FINALS_AND_CLOSED101_FROZEN_RESIDUAL_20261017','MOD4_TWO72_CLOSED_SOURCES_HEALTHY_NEXT_BLOCK_20261017','MOD4_TWO72_V5_FINALS_SIGNED4_FROZEN_AND_HEALTHY_HANDOFF_20261017','MOD4_TWO72_V6_FINALS_LATEST101_FROZEN_SAME_SCOPE_HANDOFF_20261017') for p in (REPO/'history/evidence'/name).rglob('REPORT_CAPTURE_INDEX.json')]:
  for row in json.loads(index.read_bytes()).get('entries',[]):
   if row.get('Git_path'):prior[row['sha256']]=row
 sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
 DEST.mkdir(parents=True);rows=[];files=[];deferred=[]
 for p in sorted(x for root in (F,) for x in root.rglob('*') if x.is_file() and '__pycache__' not in x.parts):
  if p.suffix=='.partial':deferred.append(str(p));continue
  with p.open('rb') as f:
   before=os.fstat(f.fileno());large=before.st_size>8*1024*1024 or p.suffix.lower() in ('.pt','.pth','.npz','.npy','.usd','.usda','.usdc','.zip','.gz','.mp4','.dmp','.tar');raw=None
   if large:
    h=hashlib.sha256()
    for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    digest=h.hexdigest()
   else:raw=f.read();digest=hashlib.sha256(raw).hexdigest()
   after=os.fstat(f.fileno());assert (before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns)
  row=dict(source_path=str(p.resolve()),bytes=before.st_size,sha256=digest)
  if digest in prior:
   prev=prior[digest];row.update(capture='same_SHA_previous_Git_capture_reference',original_retained=True)
   if prev.get('Git_path'):assert H(REPO/prev['Git_path'])==prev['archived_sha256'];row.update(Git_path=prev['Git_path'],archived_sha256=prev['archived_sha256'])
  elif large:row.update(capture='large_actual_path_size_SHA_index_only',original_retained=True)
  else:
   try:text=raw.decode('utf8')
   except UnicodeDecodeError:row.update(capture='binary_actual_path_size_SHA_index_only',original_retained=True);rows.append(row);continue
   clean,n=redact(text);data=clean.encode('utf8') if n else raw;out=DEST/p.relative_to(W);out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data);rel=out.relative_to(REPO).as_posix();files.append(rel);row.update(capture='redacted_full' if n else 'complete_exact_bytes',Git_path=rel,archived_sha256=hashlib.sha256(data).hexdigest(),redactions=n)
  rows.append(row)
 index=DEST/'REPORT_CAPTURE_INDEX.json';index.write_text(json.dumps(dict(epoch=time.time(),entries=rows,ordinary_no_new_trial_or_tag=True,deferred=deferred,all_originals_retained=True,ongoing_finite_collector_future_complete_models_and_CPU_or_cost_need_later_actual_ordinarysupplement=True,not_future_PPO_or_FINAL_or_all_three_active_claim=True),indent=2),encoding='utf8');files.append(index.relative_to(REPO).as_posix());git('add','--',*files);git('commit','-m','Append recovery-only monitor and verified frozen regression handoff receipt');head=git('rev-parse','HEAD');git('push','origin','HEAD:main');g.n.m.cap.a.gitio.g=git;g.n.m.cap.a.verify(rows,old,head);print(json.dumps(dict(commit=head,ordinary_no_new_tag=True,actual_remote_main_all1367_original_tag_objects_peels_tracked_SHA_verified=True,source_entries=len(rows),new_capture_files=len(files),deferred=deferred)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('K_RECOVERY_ONLY_POSTCAPTURE_ORDINARY_GIT_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),if_committed_continue_existingobjects_only_no_new_commit_record_tag=True),f,indent=2)
  raise
