"""One ordinary receipt/native-first supplement of the already recorded approved stage."""
from pathlib import Path
import json,time,hashlib,importlib.util,sys,traceback
B=Path(__file__).resolve().parent;R=B/'reports';E=B/'proposal_ce3_same_candidate_finite_v1';REPO=B.parent/'polar-rl-train'
BASE='9b2d0d79df95bf47acf430a99c25fdea6b19c4ae';DEST=REPO/'history/evidence'/B.name/'followup_approved_ce3_native_first_actual';NOTE=B/'APPROVED_CE3_NATIVE_FIRST_ORDINARY_NOTE_UTF8.txt'
sp=importlib.util.spec_from_file_location('recorded_ce3_stage_functions_only_not_main',B/'archive_human_approved_ce3_single_finite_unique_stage_once.py');u=importlib.util.module_from_spec(sp);sp.loader.exec_module(u);git=u.rawgit;H=u.H;TEXT=u.TEXT

def main():
 assert git('rev-parse','HEAD')==BASE and not git('status','--porcelain') and not DEST.exists() and not NOTE.exists()
 collection=json.loads((E/'reports/CE3_OWN_NATIVE_FIRST_COMPLETE_OR_PENDING_BOUND_COLLECTION_ACTUAL.json').read_bytes());assert collection['actual_transport_returned']
 tags={}
 for line in git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags/').splitlines():
  x=line.split();tags[x[0]]=(x[1],x[2] if len(x)>2 else x[1])
 assert len(tags)==1375
 old=json.loads((REPO/'history/evidence'/B.name/'actual_human_approved_ce3_single_finite/REPORT_CAPTURE_INDEX.json').read_bytes());prior={r['sha256']:r for r in old['entries'] if r.get('Git_path')}
 note='Ordinary supplement of already recorded human-approved ce3 one finite segment. Original explicit approval, source646100/cap1800/headroom300/max24/start25GiB/free8GiB/originalbudget and all guards retained, no next paid window. Capture actual bounded native/first collection, complete PT twohost path-size-SHA indices, independent source-bound CPU if executed or original CPU error/pending, exact local CIM and monitor/app/unique-stage receipt. A first under100normal schedule is genuine PPO but not public4aux effect; native/metadata/prepared/GO not wholefirst/final or jump qualification. All prior failures and relative-argv CIM lookup correction, immutable TASK pending/645140 historical labels and actual newsource646100/grant split retained. Current counts/results and future cost/exit only actual reports, no invented pass or nominal-time shutdown. Unique trial9b2d0d79/tagobject6aaf7329 and all1374older tags remain immutable. This is ordinary, no newtag/record/repeatedoldhelper/GPUreplay/hostconnection/budgetchange. All text exact or credential-redacted captures with original and archived SHA; large PTZIPraw actual indices only; source originals retained. Tool remote verification final receipt, no infinite receipt commits.'
 note+=' Actual completed override: first900s collection ended normally with only two full nativePT and independent nativeCPU still running. New V2 same-scope bounded missing-only reader reused those two PT without remote hash/download or native replay, then observed original dualFP64 CPU refusal max0.00015978302720753845 greater than original0.0001 and native node originalerror. No production startup/first/GO ever existed. Original owner81434, nativeworker16513, CPU and node16510 truly out; source COHORT_FINAL goempty, canonicalNone, both original realfcntl and targetprivate/shared free confirmed. Original remaining501934.3064830303 unchanged and no new paid ledger segment or charge. Two full local native models199tensor105floatfinite/sourceactor9STDcritic8optimizer17 Adam646100 exact/initial episode+1 age0 passed separately, not native admission. Entire existing saved3.6Mpolicy/14.4Mphysical CPU diagnostic retained strict64false max0.0005902470755358991, originalFP324096 diagnosticmax0.000072479248046875 and all other original physical/source/phase guards passed. A new separate verification copied actual originalO formal H1 native FP32 reader exactly except source filename/Adam/report namespace and truly audited ALL existing rows using original120000row FP32 batches, same absolute0.0001; it passed with max0.000072479248046875, impulse9.5367431640625e-7, geometry4.82019929526345e-8/query0. The original dual64 failed report and failednode classification are never overwritten, original admitted filename remains absent. SourceGPU model/runtime/SDK/physics/optimizer/STD/LR/guards unchanged and no GPU replay. Native12261takeoff632landing0recovery are20k source-native observations, not new80env frozen or PPO skill. Because the prepared approved proposal explicitly used dualFP64 reference, a protocol change is NOT silently substituted: concrete originalFP32 original-code pass and source-bound plan prepared, one async question asks whether restore originalFP32 reference for the SAME already approved but never started1800/300/max24 segment or retainFP64/noPPO. This is not a repeated training budget authorization, acceptedUIonly/no human protocol answer at snapshot. No new protocol-bound deployer/namespace/GO created and no nextwindow authority. Same hourly monitor updated V9 and exactTOML/appreceipt, original paid approval preserved, protocol question pendingquiet/no repeats. All known finite exactargvCIM0 after natural return, no permanent GPUidle claim. Future explicit human protocol decision and fresh source-bound strict native reuse/current resources/real locks handoff required; no old helper/task/native/paidwindow replay.'
 with NOTE.open('x',encoding='utf8') as f:f.write(note)
 known={str(Path(r['source_path']).resolve()):dict(bytes=r['bytes'],SHA=r['sha256'],provenance='prior_complete_stage_index') for r in old['entries'] if r.get('sha256') and Path(r['source_path']).suffix.lower() not in TEXT}
 for p in B.rglob('*COLLECTION_ACTUAL.json'):
  v=json.loads(p.read_bytes())
  for key in ('models','downloaded_models','downloaded_final_models','files'):
   for r in v.get(key,[]):
    if r.get('twohost_complete_SHA') and r.get('local_path'):known[str(Path(r['local_path']).resolve())]=dict(bytes=r['bytes'],SHA=r['SHA'],provenance=str(p))
 sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
 DEST.mkdir(parents=True);rows=[];captured=0;deferred=[]
 for p in sorted(x for x in B.rglob('*') if x.is_file() and '__pycache__' not in x.parts):
  if p.suffix=='.partial':deferred.append(dict(path=str(p),bytes=p.stat().st_size,SHA=None,reason='Actual partial not complete'));continue
  if p.suffix.lower() not in TEXT:
   r=known.get(str(p.resolve()))
   if r is None:deferred.append(dict(path=str(p),bytes=p.stat().st_size,SHA=None,reason='No existing actual producer hash; no archival rehash'));continue
   assert p.stat().st_size==r['bytes'];rows.append(dict(source_path=str(p.resolve()),bytes=r['bytes'],sha256=r['SHA'],capture='actual_large_index_only',index_provenance=r['provenance'],original_retained=True));continue
  raw=p.read_bytes();sha=hashlib.sha256(raw).hexdigest()
  if sha in prior:
   r=prior[sha];rows.append(dict(source_path=str(p.resolve()),bytes=len(raw),sha256=sha,capture='existing_complete_Git_SHA_reference',Git_path=r['Git_path'],archived_sha256=r['archived_sha256'],redaction_count=r.get('redaction_count',0),redaction_reason=r.get('redaction_reason'),original_retained=True));continue
  try:text=raw.decode('utf8');enc='utf8'
  except UnicodeDecodeError:text=raw.decode('latin1');enc='latin1'
  safe,n=redact(text);archived=safe.encode(enc) if n else raw;dst=DEST/p.relative_to(B);dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(archived);rel=dst.relative_to(REPO).as_posix();r=dict(source_path=str(p.resolve()),bytes=len(raw),sha256=sha,capture='complete_credential_redacted_bytes' if n else 'complete_exact_bytes',Git_path=rel,archived_bytes=len(archived),archived_sha256=H(dst),byte_preserving_decode=enc,redaction_count=n,redaction_reason='Capture-only credential redaction; original unchanged' if n else None,original_retained=True);rows.append(r);prior[sha]=r;captured+=1
 (DEST/'REPORT_CAPTURE_INDEX.json').write_text(json.dumps(dict(epoch=time.time(),entries=rows,deferred=deferred,new_texts=captured,ordinary_only_no_new_tag=True,no_archival_GPU_or_account_change=True),indent=2),encoding='utf8');git('add','--',DEST.relative_to(REPO).as_posix());git('commit','-F',str(NOTE));head=git('rev-parse','HEAD');git('push','origin','HEAD:main');v=u.u.old.prev.prev.prev.prev.g.n.m.cap.a;v.gitio.g=git;v.verify(rows,tags,head);assert len(git('tag','--list').splitlines())==1375
 print(json.dumps(dict(ordinary_commit=head,remote_main_all1375_old_tag_objects_peels_and_tracked_SHA_verified=True,entries=len(rows),new_texts=captured,deferred=deferred,no_new_tag_or_repeat_record=True)),flush=True)

if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('CE3_APPROVED_NATIVE_FIRST_ORDINARY_GIT_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),existing_commit_push_only_no_repeat_record_or_GPU=True),f,indent=2)
  raise
