"""One explicit human-approved ce3 native/finite stage; never repeat old record/tag."""
from pathlib import Path
import json,time,hashlib,importlib.util,importlib,sys,traceback
B=Path(__file__).resolve().parent;R=B/'reports';E=B/'proposal_ce3_same_candidate_finite_v1';REPO=B.parent/'polar-rl-train'
BASE='ffaf64fe3d51178f82fd9188104422331690a4df';ID='human-approved-ce3-public4-single-finite-native180';TAG='trial-20261018-'+ID
TITLE='Run one human-approved H1 continuation from ce3 with fresh native admission'
DEST=REPO/'history/evidence'/B.name/'actual_human_approved_ce3_single_finite';NOTE=B/'HUMAN_APPROVED_CE3_SINGLE_FINITE_STAGE_NOTE_UTF8.txt';MSG=B/'HUMAN_APPROVED_CE3_SINGLE_FINITE_TAG_MESSAGE_UTF8.txt'
sp=importlib.util.spec_from_file_location('prior_repair_stage_functions_only_not_main',B/'archive_post_power_mean_overflow_native_finite_unique_stage_once.py');u=importlib.util.module_from_spec(sp);sp.loader.exec_module(u);rawgit=u.rawgit;H=u.H;TEXT=u.TEXT

def git(*args):
 if args[:2]==('tag','-a'):
  assert args[2]==TAG and args[3]=='-m' and args[4]==MSG.read_text('utf8');return rawgit('tag','-a',TAG,'-F',str(MSG))
 if args and args[0]=='push':return rawgit('push','--atomic','origin','HEAD:main','refs/tags/'+TAG)
 return rawgit(*args)

def main():
 assert git('rev-parse','HEAD')==BASE and not git('status','--porcelain') and not git('tag','--list',TAG) and not DEST.exists()
 grant=json.loads((E/'reports/HUMAN_EXPLICIT_CE3_SINGLE_FINITE_APPROVAL_ACTUAL.json').read_bytes());dispatch=json.loads((E/'reports/HUMAN_APPROVED_CE3_OWN_NEW_NATIVE_SINGLE_FINITE_CHAIN_DETACHED_ACTUAL.json').read_bytes());assert grant['explicit_human_grant_received'] and grant['actual_human_answer']=='批准这一有限段' and grant['no_following_window_authorization'];assert dispatch['source_SHA']==grant['source_SHA'] and dispatch['source_Adam']==646100
 tags={}
 for line in git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags/').splitlines():
  x=line.split();tags[x[0]]=(x[1],x[2] if len(x)>2 else x[1])
 assert len(tags)==1374
 old=json.loads((REPO/'history/evidence'/B.name/'followup_ce3_same_candidate_next_finite_local_proposal_pending_grant/REPORT_CAPTURE_INDEX.json').read_bytes());prior={r['sha256']:r for r in old['entries'] if r.get('Git_path')}
 note='''Actual human answer to the concrete prepared next-segment question was 批准这一有限段. This explicitly authorizes ONE H1 same-public4-only-V2 continuation from full ce3c69bbcf56bd6c884681f23f527b9fe9e1884a7b5444ff90d3f7a2e28b2d90/owned24/Adam646100,72GPU0,at most24updates and1800seconds including load-learn-fullsave-SDKclose-childwait-ownerterminal,300headroom/free8GiB complete-update savedstop/25GiB start. Original1188000seconds/330hours/sevenextensions remains unchanged. It does not authorize a following paid window. No rollback to b326, parameter or STD reset, new auxiliary coefficient, reward/LR/action/CAD/physics/DR/hardware threshold change. Public4-only .001 overflow mean loss remains explicit optimization candidate, original other PPO terms exact, shared normal indirect effects not guaranteed. E2/E3 stay signed preGO review holds,0worker/GO/charge. New models may be frozen on independent4090 without stopping healthy training; old ce3 frozen case is consumed and never replayed.

Existing478file prepared package was consumed after new full manifest source hashes; the proposal preparer and all old Task/native/full/once/helper/tag were not rerun. Fresh target actual resources,durable space, previous P2 actual exit/terminal source metadata,no surviving old processes,privateGPU/sharedvalidation realfcntl free and selectedGPU compute empty were checked. Target whole source199tensor105floatfinite,17Adam646100,actual installed RSLrunner/PPO and SDKmath SHA and owned class public4 gradient CPU passed. Original source D is genuinely mounted and used only for metadata owner, not mislabelled as GPU storage admission. Original P2 closed cost settled/canonicalNone/two realfcntl free and oldowner process creation out checked before new namespace. An initial local git command used workspace instead of repo and failed locally; it was corrected without host effects.

Original new deployer stopped BEFORE ANY owner/node/native/GO because the previously prepared target manifest did not include the source-only listener helper at its expected local path. Exact FileNotFoundError source/trace preserved. Target full package and three source controller files had uploaded, new source root existed but had no owner identity/current/console. This was not a GPU fault and no paid charge had started. New V2 finisher read actual source/target preowner partial state, no actual processes/native/GO,old cost settled/canonicalNone/two original realfcntl and sameGPU private/shared free,port free; verified all three uploaded sourcefile hashes then uploaded ONLY missing original listener helper after comparing byteSHA to actual previously tested originalO. Four source files SHA/AST were checked, no live controller change or blind original deployer rerun. Only then original owner/listener actualready/signed E2E3holds and H1node were launched. New unique owner81434/create1792297628.59 at /mnt/mod4_linux_durable_20261013/H1cq_1810p3/owner and node16510/create1792297630.24/nativeworker16513/create1792297630.68 at72zonglin2/tasks/H1cq_1810p3 are snapshots, not permanentactive or futureFINAL. Original four controllers unchanged. Original selected workers spawn own NEW source20knative180/720/3.6Mpolicy14.4Mphysical; all independent CPU must truly pass before originalwriter one finiteGO. Native owner alive/canonicalNone/locksnotyetheld is normal0PPO state, not authority for a second writer.

Native allmean audit uses originalF32weights/observations with independent TorchFP64+NumPyFP64 at same original absolute1e-4, originalFP32 failure/diagnostic preserved separately, otherquery1e-6/COM1e-5/closure.002/mimic.01/geometry1e-6/event1e-6 unchanged. Earlier ce3full39/12/0 and full267ordinary/61firstfail(60orientation,1closure),ready79/80,0recovery remain original frozen source results only, not this continuation qualification. Prepared future sourcebound first/native/final/model-cost readers and final-source frozen builder are not evidence of execution. First expected all17Adam646100to646120/twohostcompletePT/full199tensor105floatfinite/startupcore exact/sourceepisode+1/phaseage0/all17changes; under original100normal-first recipe first update is normal-only, not evidence of public4aux effect. Native/pending/GO/rollingmetadata never substitute full first/final or jump qualification.

Local bounded collector owns all transport ONLY while actual CIM creation+argv alive. Absolute-workspace filter initially missed a relative script argv; corrected exact basename+actual exe/creation query found the collector, no overlapping host connection was made. Known finite collector63304/create2026-10-18T12:27:34.261371+08:00 reads target sameconnection at most900seconds metadata then only missing new native initial/final/startup/first PT and one originalsource/account readonly read. Raw and complete oldPT are not rehashed/downloaded for Git; no native/Task replay. Actual return hands transport back, no secondwatcher/monitor/5minSSH. Remote finite chain runs independent of Laptop/hourly. Later actual collection/CPU/GO/FINAL/cost/out/locks reports are authoritative and pending is pending; budget is charged only by the one original writer after trueGO once actual interval, no duplicateledger/canonicalcopy/clearactive/refund/tail/automaticgrant.

Same mod4-10 ACTIVEhourly target01a07a2d-9036-7531-a012-692df9f56353 updated to actual approval and active native finite chain, old pending approval text is historical. Notify meaningful new complete first/final/frozen/repair/regression/necessary human action only, quiet unchanged/pending.210singleD last21.6GB below25GiB noGPUworker,WindowsCreadonly and prior exact189 cleanup consumed, no new cleanup.3060SSH restored but no fresh signeddesktop/MSVCRT GPU admission,LaptopGPUpaused. No claim all3PPO or100percent. All originalmaster/ancestorfalse/heldout/budget/hardguards and publicSDK-notbinary/authored-notcookedShapeLocal/COM-notcalibrated/host-notboarddeadline limits preserved. Credentials/HMAC stdin-memory only, historicalNargv disclosure retained, no OSauditabsence claim. Git archives all success/failure/source/preparedunusedreaders/workorders/monitor/appreceipts; PTNPZUSDZIPraw only actual path-size-SHA indexes, originalsretained,partialdeferred. No archival GPU replay/runtime mutation/account change. This new stage uses record_experiment exactly once and exact-title-plus-note-F annotatedtag; poststage formal receipts/results ordinary supplements, pushfail existingobjects only. Latest toolverification is finalreceipt, no infinite receipt loop.'''
 for p,value in ((NOTE,note),(MSG,TITLE+'\n\n'+note)):
  with p.open('x',encoding='utf8') as f:f.write(value)
 known={str(Path(r['source_path']).resolve()):dict(bytes=r['bytes'],SHA=r['sha256'],provenance='prior_complete_Git_index') for r in old['entries'] if r.get('sha256') and Path(r['source_path']).suffix.lower() not in TEXT}
 for mf in list(B.rglob('THREE_SLOT_COMPLETE_MANIFEST_V1.json'))+list(B.rglob('H1_*LINUX4090_MANIFEST_*.json'))+list(B.rglob('H1_MEANREPAIR_FIRST_FROZEN_COMPLETE_MANIFEST_V1.json')):
  for r in json.loads(mf.read_bytes()).get('files',[]):
   p=mf.parent/r['relative']
   if p.is_file() and p.suffix.lower() not in TEXT:known[str(p.resolve())]=dict(bytes=r['bytes'],SHA=r['SHA'],provenance=str(mf))
 for p in B.rglob('*COLLECTION_ACTUAL.json'):
  v=json.loads(p.read_bytes())
  for key in ('models','downloaded_models','downloaded_final_models','files'):
   for r in v.get(key,[]):
    if r.get('twohost_complete_SHA') and r.get('local_path'):known[str(Path(r['local_path']).resolve())]=dict(bytes=r['bytes'],SHA=r['SHA'],provenance=str(p))
 for p in B.rglob('*PREPARED_ACTUAL.json'):
  v=json.loads(p.read_bytes())
  for key in ('source','package'):
   r=v.get(key)
   if isinstance(r,dict) and r.get('path') and r.get('bytes') and r.get('SHA'):
    q=Path(r['path'])
    if q.is_file() and q.suffix.lower() not in TEXT:known[str(q.resolve())]=dict(bytes=r['bytes'],SHA=r['SHA'],provenance=str(p))
 sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
 DEST.mkdir(parents=True);rows=[];files=[];captured=0;deferred=[]
 for p in sorted(x for x in B.rglob('*') if x.is_file() and '__pycache__' not in x.parts):
  if p.suffix=='.partial':deferred.append(dict(path=str(p),bytes=p.stat().st_size,SHA=None,reason='Actual partial retained, not complete'));continue
  if p.suffix.lower() not in TEXT:
   r=known.get(str(p.resolve()))
   if r is None:deferred.append(dict(path=str(p),bytes=p.stat().st_size,SHA=None,reason='No existing actual producer hash; no Git rehash'));continue
   assert p.stat().st_size==r['bytes'];rows.append(dict(source_path=str(p.resolve()),bytes=r['bytes'],sha256=r['SHA'],capture='actual_large_index_only',index_provenance=r['provenance'],original_retained=True));continue
  raw=p.read_bytes();sha=hashlib.sha256(raw).hexdigest()
  if sha in prior:
   r=prior[sha];rows.append(dict(source_path=str(p.resolve()),bytes=len(raw),sha256=sha,capture='existing_complete_Git_SHA_reference',Git_path=r['Git_path'],archived_sha256=r['archived_sha256'],redaction_count=r.get('redaction_count',0),redaction_reason=r.get('redaction_reason'),original_retained=True));continue
  try:text=raw.decode('utf8');encoding='utf8'
  except UnicodeDecodeError:text=raw.decode('latin1');encoding='latin1'
  safe,n=redact(text);archived=safe.encode(encoding) if n else raw;dst=DEST/p.relative_to(B);dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(archived);rel=dst.relative_to(REPO).as_posix();r=dict(source_path=str(p.resolve()),bytes=len(raw),sha256=sha,capture='complete_credential_redacted_bytes' if n else 'complete_exact_bytes',Git_path=rel,archived_bytes=len(archived),archived_sha256=H(dst),byte_preserving_decode=encoding,redaction_count=n,redaction_reason='Capture-only repository credential redaction; source unchanged' if n else None,original_retained=True);rows.append(r);prior[sha]=r;files.append(rel);captured+=1
 index=DEST/'REPORT_CAPTURE_INDEX.json';index.write_text(json.dumps(dict(epoch=time.time(),entries=rows,deferred=deferred,new_texts=captured,explicit_human_one_grant=True,all_old_false_and_new_partial_source_error_preserved=True,no_large_Git_rehash_or_GPU_or_account_change=True),indent=2),encoding='utf8');files.append(index.relative_to(REPO).as_posix())
 rec=importlib.import_module('record_experiment');rec.git=git;sys.argv=['record_experiment.py','--id',ID,'--title',TITLE,'--kind','training','--note-file',str(NOTE),'--files',*files,'--validation','Actual human one finite grant; complete source manifest SDK CPU; preowner missing-listener refusal retained and source-bound partial finisher verified no process/GO then actual ready owner+node own native; full native/first/final only actual source-bound reports, unchanged original guards and ledger.','--push'];rec.main();head=git('rev-parse','HEAD');obj=git('rev-parse',TAG);v=u.old.prev.prev.prev.prev.g.n.m.cap.a;v.gitio.g=git;v.verify(rows,tags,head,TAG,obj);assert len(git('tag','--list').splitlines())==1375
 print(json.dumps(dict(commit=head,tag=TAG,object=obj,remote_main_tag_peeled_all1374_old_tags_and_tracked_SHA_verified=True,total_tags=1375,entries=len(rows),new_texts=captured,deferred=deferred)),flush=True)

if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('CE3_APPROVED_UNIQUE_GIT_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),if_commit_exists_push_existingobjects_only_no_record_tag_GPU_rerun=True),f,indent=2)
  raise
