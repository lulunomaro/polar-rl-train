"""One ordinary supplement of existing repair stage; never record/tag/GPU/hash replay."""
from pathlib import Path
import json,time,hashlib,importlib.util,sys,traceback
B=Path(__file__).resolve().parent;R=B/'reports';REPO=B.parent/'polar-rl-train';BASE='65d50827511b12e4da7e673d5c8392f2bbcb3b4c';DEST=REPO/'history/evidence'/B.name/'followup_public4_V2_first_update8_parallel';NOTE=B/'PUBLIC4_V2_FIRST_UPDATE8_FOLLOWUP_ORDINARY_NOTE_UTF8.txt'
sp=importlib.util.spec_from_file_location('consumed_unique_archive_pure_functions_only_not_main',B/'archive_post_power_mean_overflow_native_finite_unique_stage_once.py');u=importlib.util.module_from_spec(sp);sp.loader.exec_module(u);git=u.rawgit;H=u.H;TEXT=u.TEXT

def main():
 assert git('rev-parse','HEAD')==BASE and not git('status','--porcelain') and not DEST.exists()
 tags={}
 for line in git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags/').splitlines():
  x=line.split();tags[x[0]]=(x[1],x[2] if len(x)>2 else x[1])
 assert len(tags)==1374
 old=json.loads((u.DEST/'REPORT_CAPTURE_INDEX.json').read_bytes());prior={}
 for row in old['entries']:
  if row.get('Git_path'):prior[row['sha256']]=row
 note='Ordinary supplement of already uniquely recorded post-power H1 repair. Preserve global P1 complete closed final, once cost, readiness80to55 and strict0/0/0, and protected full b326 rollback to public4-only auxiliary candidate V2. New actual immutable first282a4687 complete CPU is normal-only update1 with zero public4 rows and zero auxiliaryloss: genuine PPO positive but not repair effectiveness. Later actual source diagnostic proves nonzero public4-row auxiliaryloss, and local real-network derivative audit shows possible shared-parameter normal coupling without claiming unique physical cause. An attempted update8 reader was cancelled only locally after source proved immutable saves only update1/every25/final with max24; no update8 checkpoint exists, no update8 CPU or GPU freeze executed, no production process signalled or live code changed. Preserve KeyboardInterrupt and all unused prepared helpers. Independent unused GPU1 normal-only first native120 then full1500 cases are recorded only where actually completed and independently CPU verified. Actual public4 finite final, whole-model CPU, original once cost/childrenout/canonicalNone/real locks, and final own-source frozen native/full are included only if corresponding actual reports exist. The normal-only first control cannot establish post-aux effects; final needs its own new native/full. Explicit full final FP32 CPU rawmean4.425e-4 originally fails1e-4 and remains false with trace. Independent remaining physics/source/phase checks all pass; separate diagnostic/reference precision repair evaluates original F32 weights/observations with Torch and NumPy FP64, full120000-row GPU error8.266e-5 and referencecross5.684e-13 with the same original absolute1e-4, four negative shape/nonfinite/injected-error cases reject. This is an explicit new auditor reference protocol, not relaxed tolerance or altered GPU policy; old FP32 false never overwritten. Actual first-valid-prefix events39takeoff12landing0recovery and267ordinary/61firstfail(60orientation1closure),79ready,19whole15s are preserved, not course graduation. All cases bind exact sourceSHA/manifest/backend/namespace/candidate, not Adam number alone. No old native/Task/once/completePT/raw replay. No extra budget, refund, clearactive, duplicate ledger or automatic next window. Training was not interrupted for evaluation. Original physics/hardware/query1e-6/COM1e-5/mimic.01/closure.002/H1actorCPU1e-4 and original gates retained. All successful/failed/local reader lookup/schema/CPU errors and prepared source are captured. Large originals only producer/twohost actual path size SHA, no Git-driven raw hash; partial/deferred explicit. Credentials redacted in capture only with original/archived SHA/count/reason, originals untouched. No new tag or repeated unique-stage/helper. Future formal reports need ordinary supplement; tool verification is final receipt without infinite HEAD-writeback.'
 with NOTE.open('x',encoding='utf8') as f:f.write(note)
 known={str(Path(r['source_path']).resolve()):dict(bytes=r['bytes'],SHA=r['sha256'],provenance='prior_unique_capture_index') for r in old['entries'] if r.get('capture','').startswith('actual_manifest')}
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
  with (R/('PUBLIC4_FOLLOWUP_ORDINARY_GIT_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),if_commit_exists_push_existing_objects_only_no_repeat_commit_or_stage_GPU=True),f,indent=2)
  raise
