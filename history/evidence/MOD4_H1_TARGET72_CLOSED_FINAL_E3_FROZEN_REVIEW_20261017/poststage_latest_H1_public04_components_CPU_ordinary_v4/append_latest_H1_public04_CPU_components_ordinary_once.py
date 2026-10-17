"""Only new source-review texts/receipts; never hashes old model/raw or reruns helpers."""
from pathlib import Path
import sys,json,time,hashlib,importlib.util,traceback
B=Path(__file__).resolve().parent;R=B/'reports';REPO=B.parent/'polar-rl-train'
BASE='6a5ab9d756f005b559ba718cecf95cdaf23d2c2e'
DEST=REPO/'history/evidence'/B.name/'poststage_latest_H1_public04_components_CPU_ordinary_v4'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
sp=importlib.util.spec_from_file_location('old_ordinary_pure_functions_not_main',B/'append_actual_stage_receipt_frozen_followup_monitor_ordinary_once.py')
old=importlib.util.module_from_spec(sp);sp.loader.exec_module(old);git=old.git
TEXT={'.py','.json','.jsonl','.txt','.md','.toml','.log','.csv','.tsv','.yaml','.yml','.xml','.ps1','.bat','.cmd','.sh','.ini','.cfg'}
def main():
 assert git('rev-parse','HEAD')==BASE and not git('status','--porcelain') and not DEST.exists()
 tags={}
 for line in git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags/').splitlines():
  s=line.split();tags[s[0]]=(s[1],s[2] if len(s)>2 else s[1])
 assert len(tags)==1371
 prior={};by_path={};lossless={};indices=[]
 for index in (REPO/'history/evidence'/B.name).rglob('REPORT_CAPTURE_INDEX.json'):
  value=json.loads(index.read_bytes());indices.append(dict(Git_path=index.relative_to(REPO).as_posix(),SHA=H(index)))
  for row in value['entries']:
   if row.get('Git_path'):prior[row['sha256']]=row
   by_path.setdefault(row['source_path'],[]).append(row)
  for row in value.get('full_log_encodings',[]):lossless[row['original_source_path']]=row
 sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
 report=json.loads((R/'LATEST_H1_CLOSED24_FROZEN_PUBLIC04_SOURCE_COMPONENTS_CPU_PREPARED_ACTUAL.json').read_bytes())
 assert report['passed_source_actor_and_original_clock_components_CPU']
 DEST.mkdir(parents=True);rows=[];files=[];references=[];binary_skipped=[]
 for p in sorted(x for x in B.rglob('*') if x.is_file() and '__pycache__' not in x.parts):
  path=str(p.resolve())
  if p.suffix.lower() not in TEXT:
   assert path in by_path,'New non-text artifact requires an explicit actual path/size/SHA index: '+path
   binary_skipped.append(path);continue
  raw=p.read_bytes();digest=hashlib.sha256(raw).hexdigest()
  if digest in prior:
   row=prior[digest];assert H(REPO/row['Git_path'])==row['archived_sha256']
   references.append(dict(source_path=path,bytes=len(raw),sha256=digest,Git_path=row['Git_path'],archived_sha256=row['archived_sha256']));continue
  try:text=raw.decode('utf8')
  except UnicodeDecodeError:
   bind=lossless[path];assert bind['original_SHA']==digest and bind['original_bytes']==len(raw)
   references.append(dict(source_path=path,bytes=len(raw),sha256=digest,lossless_wrapper_Git_path=bind['wrapper_Git_path']));continue
  clean,n=redact(text);assert n==0,'New source-review file requires explicit credential redaction before archive: '+path
  dst=DEST/p.relative_to(B);dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(raw)
  rel=dst.relative_to(REPO).as_posix();files.append(rel);rows.append(dict(source_path=path,bytes=len(raw),sha256=digest,capture='complete_exact_bytes',Git_path=rel,archived_sha256=H(dst)))
 assert any(Path(row['source_path']).name==Path(__file__).name for row in rows)
 index=DEST/'REPORT_CAPTURE_INDEX.json'
 index.write_text(json.dumps(dict(epoch=time.time(),entries=rows,previous_complete_indices=indices,current_text_same_SHA_prior_references=references,
   existing_nontext_artifacts_not_rehashed_or_recollected=binary_skipped,new_large_artifacts_none=True,
   latest_H1_source_public04_components_CPU_only_no_GPU_Task_paid_trial_or_new_tag=True,all_new_source_negative_read_errors_work_order_monitor_receipts_captured=True,
   ordinary_append_to_existing_source_review_stage=True,future_saved_reports_need_new_ordinary_supplement=True),indent=2),encoding='utf8')
 files.append(index.relative_to(REPO).as_posix());git('add','--',*files)
 git('commit','-m','Prepare latest H1 frozen public04 source components and existing monitor handoff')
 head=git('rev-parse','HEAD');git('push','origin','HEAD:main')
 old.stage.prev.prev.g.n.m.cap.a.gitio.g=git;old.stage.prev.prev.g.n.m.cap.a.verify(rows,tags,head)
 assert not git('status','--porcelain')
 print(json.dumps(dict(commit=head,ordinary_no_new_tag=True,remote_main_all1371_original_tag_objects_peels_and_new_tracked_SHA_verified=True,new_source_entries=len(rows),same_SHA_text_references=len(references),old_binary_artifacts_not_rehashed=len(binary_skipped),no_GPU_or_PPO_or_budget_change=True)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('LATEST_H1_PUBLIC04_CPU_ORDINARY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),if_commit_exists_continue_existing_objects_only_no_repeat_commit_or_old_helper=True,no_training_or_budget_mutation=True),f,indent=2)
  raise
