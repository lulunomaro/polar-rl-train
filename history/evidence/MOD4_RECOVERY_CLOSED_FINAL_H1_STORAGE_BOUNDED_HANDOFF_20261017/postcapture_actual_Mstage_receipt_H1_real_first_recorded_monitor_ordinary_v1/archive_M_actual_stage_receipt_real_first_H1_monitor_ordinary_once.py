"""Ordinary append after the unique cleanup stage; no record/tag/runtime/deletion."""
from pathlib import Path
import sys,json,time,hashlib,importlib.util,traceback
B=Path(__file__).resolve().parent;R=B/'reports';REPO=B.parent/'polar-rl-train'
BASE='3e2b4649bdc2ae0c1f49d873fde5c8625996de3a'
DEST=REPO/'history/evidence'/B.name/'postcapture_actual_Mstage_receipt_H1_real_first_recorded_monitor_ordinary_v1'
sp=importlib.util.spec_from_file_location('cleanup_stage_functions_only_no_main',B/'archive_recovery85_H1_real_first_native_review_actual_unique_stage_v2_once.py');previous=importlib.util.module_from_spec(sp);sp.loader.exec_module(previous)
git=previous.g.git;H=previous.g.H
def main():
 assert git('rev-parse','HEAD')==BASE and not git('status','--porcelain') and not DEST.exists()
 old={}
 for line in git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags/').splitlines():
  r=line.split();old[r[0]]=(r[1],r[2] if len(r)>2 else r[1])
 assert len(old)==1369 and old['refs/tags/'+previous.TAG]==('498f3f169551bc09afa87c7cab3feb4577a2687c',BASE)
 prior={}
 for p in (REPO/'history/evidence'/B.name).rglob('REPORT_CAPTURE_INDEX.json'):
  for r in json.loads(p.read_bytes())['entries']:
   if r.get('Git_path'):prior[r['sha256']]=r
 sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
 DEST.mkdir(parents=True);rows=[];files=[]
 for p in sorted(x for x in B.rglob('*') if x.is_file() and '__pycache__' not in x.parts):
  raw=p.read_bytes();sha=hashlib.sha256(raw).hexdigest();row=dict(source_path=str(p.resolve()),bytes=len(raw),sha256=sha)
  if sha in prior:
   prev=prior[sha];assert H(REPO/prev['Git_path'])==prev['archived_sha256'];row.update(capture='same_SHA_previous_Git_capture_reference',Git_path=prev['Git_path'],archived_sha256=prev['archived_sha256'])
  elif p.suffix.lower() in ('.pt','.pth','.npz','.npy','.usd','.usda','.usdc','.zip','.tar','.gz','.mp4') or len(raw)>50_000_000:row.update(capture='large_artifact_path_size_SHA_index_only',local_original_retained=True)
  else:
   try:clean,n=redact(raw.decode('utf8'))
   except UnicodeDecodeError:row.update(capture='binary_path_size_SHA_index_only',local_original_retained=True);rows.append(row);continue
   data=clean.encode('utf8') if n else raw;dest=DEST/p.relative_to(B);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data);rel=dest.relative_to(REPO).as_posix();files.append(rel);row.update(capture='redacted_full' if n else 'complete_exact_bytes',Git_path=rel,archived_sha256=hashlib.sha256(data).hexdigest(),redactions=n)
  rows.append(row)
 index=DEST/'REPORT_CAPTURE_INDEX.json';index.write_text(json.dumps(dict(epoch=time.time(),entries=rows,ordinary_no_new_trial_or_tag=True,all_local_sources_reports_workorders_monitor_receipts_captured=True,all_current_M_local_originals_retained=True,prior_L_exact189_authorized_deletion_not_replayed_or_claimed_retained=True,no_delete_or_runtime_or_budget_action=True),indent=2),encoding='utf8');files.append(index.relative_to(REPO).as_posix())
 git('add','--',*files);git('commit','-m','Append verified H1 real first PPO and recovery85 stage receipt handoff monitor');head=git('rev-parse','HEAD');git('push','origin','HEAD:main');previous.g.n.m.cap.a.gitio.g=git;previous.g.n.m.cap.a.verify(rows,old,head)
 print(json.dumps(dict(commit=head,ordinary_no_new_trial_or_tag=True,actual_remote_main_all1369_original_tag_objects_peels_tracked_SHA_verified=True,source_entries=len(rows),new_capture_files=len(files),no_cleanup_replay_or_runtime_budget_change=True)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('M_REAL_H1_FIRST_POSTCAPTURE_ORDINARY_GIT_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),continue_existing_objects_if_commit_exists_no_record_tag_recommit_or_delete=True),f,indent=2)
  raise
