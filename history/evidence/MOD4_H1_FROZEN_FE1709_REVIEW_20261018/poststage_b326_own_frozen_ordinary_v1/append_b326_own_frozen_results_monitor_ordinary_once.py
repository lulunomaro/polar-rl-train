"""Follow up the already recorded X stage; no tag and no old raw/model rehash."""
from pathlib import Path
import sys,json,time,hashlib,importlib.util,traceback
B=Path(__file__).resolve().parent;R=B/'reports';REPO=B.parent/'polar-rl-train';BASE='8ee2500f2e7a38efe660af7c8c5471f2f77bef67';DEST=REPO/'history/evidence'/B.name/'poststage_b326_own_frozen_ordinary_v1'
sp=importlib.util.spec_from_file_location('existing_stage_pure_functions_not_main',B/'archive_H1_final24_human4090_parallel_frozen_training_unique_stage_once.py');stage=importlib.util.module_from_spec(sp);sp.loader.exec_module(stage);git=stage.rawgit;H=stage.H
TEXT={'.py','.json','.jsonl','.txt','.md','.toml','.log','.csv','.tsv','.yaml','.yml','.xml','.ps1','.bat','.cmd','.sh','.ini','.cfg'}
def main():
 assert git('rev-parse','HEAD')==BASE and not git('status','--porcelain') and not DEST.exists()
 tags={}
 for line in git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags/').splitlines():
  x=line.split();tags[x[0]]=(x[1],x[2] if len(x)>2 else x[1])
 assert len(tags)==1373
 prior={};by_path={};indices=[]
 for idx in (REPO/'history/evidence'/B.name).rglob('REPORT_CAPTURE_INDEX.json'):
  indices.append(dict(Git_path=idx.relative_to(REPO).as_posix(),SHA=H(idx)));v=json.loads(idx.read_bytes())
  for row in v['entries']:
   by_path[row['source_path']]=row
   if row.get('Git_path'):prior[row['sha256']]=row
  for row in v.get('current_text_same_SHA_prior_references',[]):
   by_path[row['source_path']]=row;prior[row['sha256']]=row
 newlarge={}
 for name in ('LINUX_GPU1_B326_NATIVE120_COMPLETE_OR_PENDING_BOUND_COLLECTION_ACTUAL.json','LINUX_GPU1_B326_FULL1500_COMPLETE_OR_PENDING_BOUND_COLLECTION_ACTUAL.json'):
  p=R/name
  if p.exists():
   for row in json.loads(p.read_bytes())['files']:
    if row.get('local_path'):newlarge[str(Path(row['local_path']).resolve())]=row
 sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
 DEST.mkdir(parents=True);rows=[];files=[];references=[];binary_references=[];deferred=[]
 for p in sorted(x for x in B.rglob('*') if x.is_file() and '__pycache__' not in x.parts):
  path=str(p.resolve())
  if p.suffix=='.partial':deferred.append(path);continue
  if p.suffix.lower() not in TEXT:
   if path in by_path:
    old=by_path[path];assert p.stat().st_size==old['bytes'];binary_references.append(dict(source_path=path,bytes=old['bytes'],sha256=old['sha256'],capture='prior_actual_index_reference_no_rehash',original_retained=True));continue
   row=newlarge[path];assert row['twohost_complete_SHA'] and p.stat().st_size==row['bytes'];rows.append(dict(source_path=path,bytes=row['bytes'],sha256=row['SHA'],capture='new_twohost_actual_large_path_size_SHA_index_only',original_retained=True,complete_original_case_collection=str(R)));continue
  raw=p.read_bytes();digest=hashlib.sha256(raw).hexdigest()
  if digest in prior:
   ref=prior[digest];assert H(REPO/ref['Git_path'])==ref['archived_sha256'];references.append(dict(source_path=path,bytes=len(raw),sha256=digest,Git_path=ref['Git_path'],archived_sha256=ref['archived_sha256']));continue
  try:decoded=raw.decode('utf8');encoding='UTF8'
  except UnicodeDecodeError:decoded=raw.decode('utf8',errors='backslashreplace');encoding='non_UTF8_original_full_bytes_preserved'
  _,n=redact(decoded);assert n==0,'Explicit credential redaction required';dst=DEST/p.relative_to(B);dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(raw);rel=dst.relative_to(REPO).as_posix();files.append(rel);row=dict(source_path=path,bytes=len(raw),sha256=digest,capture='complete_exact_bytes',source_encoding=encoding,Git_path=rel,archived_sha256=H(dst));rows.append(row);prior[digest]=row
 index=DEST/'REPORT_CAPTURE_INDEX.json';index.write_text(json.dumps(dict(epoch=time.time(),entries=rows,current_text_same_SHA_prior_references=references,previous_complete_indices=indices,existing_large_actual_index_references_not_rehashed=binary_references,deferred=deferred,ordinary_followup_to_recorded_X_stage_no_new_trial_tag=True,all_new_success_failure_readers_workorder_monitor_receipts_captured=True,new_b326_frozen_only_no_paid_learning_or_budget_change=True,future_formal_reports_need_ordinary_supplement=True),indent=2),encoding='utf8');files.append(index.relative_to(REPO).as_posix());git('add','--',*files);git('commit','-m','Audit latest closed b326 H1 frozen source on authorized Linux4090 backend');head=git('rev-parse','HEAD');git('push','origin','HEAD:main');verify=stage.prev.prev.prev.prev.g.n.m.cap.a;verify.gitio.g=git;verify.verify(rows,tags,head);assert not git('status','--porcelain')
 print(json.dumps(dict(commit=head,ordinary_no_new_tag=True,remote_main_all1373_original_tags_objects_peels_new_tracked_SHA_verified=True,new_entries=len(rows),same_SHA_text_references=len(references),old_binary_artifacts_not_rehashed=len(binary_references),deferred=deferred)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('B326_FROZEN_ORDINARY_GIT_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),if_commit_exists_push_existing_objects_only_no_repeat_commit_tag_or_GPU=True),f,indent=2)
  raise
