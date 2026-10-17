"""One ordinary supplement of existing repair stage; never record/tag/GPU/hash replay."""
from pathlib import Path
import json,time,hashlib,importlib.util,sys,traceback
B=Path(__file__).resolve().parent;R=B/'reports';REPO=B.parent/'polar-rl-train';BASE='58e6480449f8e0b597abf942a5f039b7728784b7';DEST=REPO/'history/evidence'/B.name/'followup_ce3_same_candidate_next_finite_local_proposal_pending_grant';NOTE=B/'CE3_LOCAL_PROPOSAL_PENDING_GRANT_ORDINARY_NOTE_UTF8.txt'
sp=importlib.util.spec_from_file_location('consumed_unique_archive_pure_functions_only_not_main',B/'archive_post_power_mean_overflow_native_finite_unique_stage_once.py');u=importlib.util.module_from_spec(sp);sp.loader.exec_module(u);git=u.rawgit;H=u.H;TEXT=u.TEXT

def main():
 assert git('rev-parse','HEAD')==BASE and not git('status','--porcelain') and not DEST.exists()
 tags={}
 for line in git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags/').splitlines():
  x=line.split();tags[x[0]]=(x[1],x[2] if len(x)>2 else x[1])
 assert len(tags)==1374
 old=json.loads((REPO/'history/evidence'/B.name/'followup_public4_flight_orientation_recovery_source_CPU/REPORT_CAPTURE_INDEX.json').read_bytes());prior={}
 for row in old['entries']:
  if row.get('Git_path'):prior[row['sha256']]=row
 note='Ordinary same-stage local CPU preparation and pending explicit single finite-window question. Latest full ce3 actor9STD critic8 optimizer17 Adam646100 state copied exact; no b326 rollback, parameter reset or changed optimization/environment reward/physics/DR/hardware.478file proposal manifest+ZIP indexed, selected worker source filename/Adam expectations and native auditor precision reference changes explicit. CPU whole199tensor105float finite/9 source negatives/4 same1e-4 precision negatives, original FP32 false remains separate and no E3 tolerance exception. Four original controllers byteexact. Unused standalone historical credential-bearing migration tool omitted from new package after import AST proof; original source retained and SHA/reason indexed, no matched credentials printed. Human question UI delivery is not approval, no answer received at snapshot, CPU package does not authorize host upload/native/GPU/GO/accounting. Plan cap1800/headroom300/max24/free8GiB/25GiBstart uses original budget and only H1, E2E3holds. Newsource owns fresh20knative and full independent CPU required after explicit approval plus real OS/resource/original cost+locks handoff. Reserved namespace only, no deployer or targetroot created. Preserve local source lookup misses, all original closed finals/false/once costs/no automatic nextwindow. Same ACTIVEhourly monitor target; do not repeat question on unchanged pending. All new source/reports/workingplan/pending-question and appreceipts captured by original SHA references or complete redacted captures; all large weights/assets/ZIP/raw actual indexes only, no Git-driven rehash, GPU replay, new tag or repeated old helper.'
 with NOTE.open('x',encoding='utf8') as f:f.write(note)
 known={str(Path(r['source_path']).resolve()):dict(bytes=r['bytes'],SHA=r['sha256'],provenance='prior_unique_capture_index') for r in old['entries'] if r.get('sha256') and Path(r['source_path']).suffix.lower() not in TEXT}
 manifests=list(B.rglob('THREE_SLOT_COMPLETE_MANIFEST_V1.json'))+list(B.rglob('H1_*LINUX4090_MANIFEST_*.json'))+list(B.rglob('H1_MEANREPAIR_FIRST_FROZEN_COMPLETE_MANIFEST_V1.json'))
 for mf in manifests:
  for row in json.loads(mf.read_bytes()).get('files',[]):
   p=mf.parent/row['relative']
   if p.is_file() and p.suffix.lower() not in TEXT:known[str(p.resolve())]=dict(bytes=row['bytes'],SHA=row['SHA'],provenance=str(mf))
 for p in B.rglob('*COLLECTION_ACTUAL.json'):
  j=json.loads(p.read_bytes())
  for key in ('models','downloaded_models','downloaded_final_models','files'):
   for row in j.get(key,[]):
    if row.get('twohost_complete_SHA') and row.get('local_path'):known[str(Path(row['local_path']).resolve())]=dict(bytes=row['bytes'],SHA=row['SHA'],provenance=str(p))
 for p in B.rglob('*PREPARED_ACTUAL.json'):
  j=json.loads(p.read_bytes())
  for key in ('source','package'):
   row=j.get(key)
   if isinstance(row,dict) and row.get('path') and row.get('bytes') and row.get('SHA'):
    q=Path(row['path'])
    if q.is_file() and q.suffix.lower() not in TEXT:known[str(q.resolve())]=dict(bytes=row['bytes'],SHA=row['SHA'],provenance=str(p))
 sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
 DEST.mkdir(parents=True);rows=[];captured=0;deferred=[]
 for p in sorted(x for x in B.rglob('*') if x.is_file() and '__pycache__' not in x.parts):
  if p.suffix=='.partial':deferred.append(dict(path=str(p),bytes=p.stat().st_size,SHA=None,reason='Actual partial retained; not complete'));continue
  if p.suffix.lower() not in TEXT:
   q=known.get(str(p.resolve()))
   if q is None:deferred.append(dict(path=str(p),bytes=p.stat().st_size,SHA=None,reason='No actual producer hash yet; do not rehash solely for Git'));continue
   assert p.stat().st_size==q['bytes'];rows.append(dict(source_path=str(p.resolve()),bytes=q['bytes'],sha256=q['SHA'],capture='actual_large_index_only_no_Git_rehash',index_provenance=q['provenance'],original_retained=True));continue
  raw=p.read_bytes();digest=hashlib.sha256(raw).hexdigest()
  if digest in prior:
   q=prior[digest];rows.append(dict(source_path=str(p.resolve()),bytes=len(raw),sha256=digest,capture='existing_complete_Git_SHA_reference',Git_path=q['Git_path'],archived_sha256=q['archived_sha256'],redaction_count=q.get('redaction_count',0),redaction_reason=q.get('redaction_reason'),original_retained=True));continue
  try:text=raw.decode('utf8');encoding='utf8'
  except UnicodeDecodeError:text=raw.decode('latin1');encoding='latin1'
  safe,n=redact(text);archived=safe.encode(encoding) if n else raw;dst=DEST/p.relative_to(B);dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(archived);rel=dst.relative_to(REPO).as_posix();q=dict(source_path=str(p.resolve()),bytes=len(raw),sha256=digest,capture='complete_credential_redacted_bytes' if n else 'complete_exact_bytes',Git_path=rel,archived_bytes=len(archived),archived_sha256=H(dst),byte_preserving_decode=encoding,redaction_count=n,redaction_reason='Repository credential redaction rules in capture only; source untouched' if n else None,original_retained=True);rows.append(q);prior[digest]=q;captured+=1
 index=DEST/'REPORT_CAPTURE_INDEX.json';index.write_text(json.dumps(dict(epoch=time.time(),entries=rows,deferred=deferred,new_captured_texts=captured,ordinary_only_no_new_tag=True,no_large_rehash_or_GPU_or_budget_change=True),indent=2),encoding='utf8');git('add','--',DEST.relative_to(REPO).as_posix());git('commit','-F',str(NOTE));head=git('rev-parse','HEAD');git('push','origin','HEAD:main');v=u.old.prev.prev.prev.prev.g.n.m.cap.a;v.gitio.g=git;v.verify(rows,tags,head);assert len(git('tag','--list').splitlines())==1374
 print(json.dumps(dict(ordinary_commit=head,remote_main_all1374_old_tag_objects_peels_and_tracked_SHA_verified=True,entries=len(rows),new_texts=captured,deferred=deferred,no_new_tag_or_repeated_stage=True)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('CE3_LOCAL_PROPOSAL_PENDING_GRANT_ORDINARY_GIT_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),if_commit_exists_push_existing_objects_only_no_repeat_commit_or_stage_GPU=True),f,indent=2)
  raise
