"""Archive actual closed evidence and one-hour continuation exactly once."""
from pathlib import Path
import json,time,hashlib,importlib.util,importlib,sys,traceback
B=Path(__file__).resolve().parent;R=B/'reports';REPO=B.parent/'polar-rl-train';HOUR=B/'hour1_h1_8a7c_v1'
BASE='3a210c3ff4700b4465a60e824c5c7a3ca3d7c007';ID='h1-8a7c-review-one-hour-continuation';TAG='trial-20261018-'+ID;TITLE='Continue H1 in one-hour blocks after closed 8a7c review'
DEST=REPO/'history/evidence'/B.name/'actual_H1_8a7c_review_one_hour_continuation';NOTE=B/'H1_8A7C_REVIEW_ONE_HOUR_CONTINUATION_NOTE_UTF8.txt';MSG=B/'H1_8A7C_REVIEW_ONE_HOUR_CONTINUATION_TAG_UTF8.txt'
sp=importlib.util.spec_from_file_location('previous_consumed_stage_pure_functions_only',B/'archive_ce3_original_fp32_native_reuse_training_unique_once.py');u=importlib.util.module_from_spec(sp);sp.loader.exec_module(u)
rawgit=u.rawgit;H=u.H;TEXT=u.TEXT
def git(*args):
 if args[:2]==('tag','-a'):
  assert args[2]==TAG and args[3]=='-m' and args[4]==MSG.read_text(encoding='utf8');return rawgit('tag','-a',TAG,'-F',str(MSG))
 if args and args[0]=='push':return rawgit('push','--atomic','origin','HEAD:main','refs/tags/'+TAG)
 return rawgit(*args)
def getknown(old):
 known={str(Path(r['source_path']).resolve()):dict(bytes=r['bytes'],SHA=r['sha256'],provenance='previous complete Git index') for r in old['entries'] if r.get('sha256') and Path(r['source_path']).suffix.lower() not in TEXT}
 def accept(path,row,proof):
  if not isinstance(path,str) or not isinstance(row.get('bytes'),int):return
  sha=row.get('SHA') or row.get('sha256');p=Path(path)
  if not isinstance(sha,str) or len(sha)!=64 or not p.is_file() or p.suffix.lower() in TEXT:return
  assert p.stat().st_size==row['bytes'],str(p)
  known[str(p.resolve())]=dict(bytes=row['bytes'],SHA=sha,provenance=str(proof))
 def visit(v,proof):
  if isinstance(v,list):
   for row in v:visit(row,proof)
  elif isinstance(v,dict):
   for key in ('local_path','path','source_path'):accept(v.get(key),v,proof)
   for row in v.values():
    if isinstance(row,(dict,list)):visit(row,proof)
 for p in B.rglob('*.json'):
  if '__pycache__' in p.parts:continue
  v=json.loads(p.read_bytes());visit(v,p)
  if isinstance(v,dict):
   for row in v.get('files',[]):
    if isinstance(row,dict) and isinstance(row.get('relative'),str):accept(str(p.parent/row['relative']),row,p)
 return known
def main():
 assert git('rev-parse','HEAD')==BASE and not git('status','--porcelain') and not git('tag','--list',TAG) and not DEST.exists() and not NOTE.exists()
 current=json.loads((HOUR/'reports/H1_ONE_HOUR_CHAIN_CURRENT_READONLY_ACTUAL.json').read_bytes());assert current['actual_transport_returned'] and current['owner']['rows']['OWNER_CURRENT.json']['go']=={}
 spec=json.loads((HOUR/'reports/H1_ONE_HOUR_SOURCE_TIMING_CPU_PREPARED_ACTUAL.json').read_bytes());assert spec['training_block_GO_to_save_seconds']==3600 and spec['total_cap_including_exit_reserve_seconds']==3900 and spec['arbitrary24_update_stop_removed']
 tags={}
 for line in git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags/').splitlines():
  x=line.split();tags[x[0]]=(x[1],x[2] if len(x)>2 else x[1])
 assert len(tags)==1376
 old=json.loads((REPO/'history/evidence'/B.name/'followup_ce3_fp32_stage_receipt_app_readback/REPORT_CAPTURE_INDEX.json').read_bytes());prior={r['sha256']:r for r in old['entries'] if r.get('Git_path')};known=getknown(old)
 note='Human requested one full training hour before audit and objected to agent-added gates and attribution. Agent owns the plan and fixes; no repeated technical approval question. Existing ce3 original-FP32 finite task actually closed24updates/576controls/11.52Menvsteps: complete8a7c730d97acf9db8e4ab2f89390fd9302bdf4b9186eee3c92ae287d2a199bc2/16644723B,199tensor105float finite,actor9STDcritic8 all17changed,Adam646100to646580. Original owner102842/node19262/worker19267 outEXIT0/canonicalNone/two originalfcntl and targetprivate/sharedfree; original actual cost1447.706059217453seconds chargedonce,remaining500486.60042381287 only snapshot. Its own frozen80 native120/full1500 actually completed and all files collected. Agent mistakenly reintroduced originalFP32 frozen rounding rejection despite existingV3 repair; preserve originalFP32 nativefalse .0001182556 and restore existingbyteexact dualFP64V3 reference; nativepasses3.846780789e-5. Full rawFP32false .0003662109 and dualFP64false .0001195088618 both retained, no threshold widening or rowwise choice. Independent allrowCPU diagnostic completed all other originalsource/phase/physical/query/COM/hardware/mimic/closure checks; executedclip6 reference max4.26907654e-5 and only one dual64 raw-overbound row has identical saturated execution. Raw-referencefalse remainsfalse and is not invented physicaltermination. Descriptive original firstvalid42takeoff/6landing/1recovery,206ordinary0trunc;59orientationfirstfail pitch55roll4,landed recoveryruns338/0/24/0/0/0 against unchanged200callback. Not coursegraduation/statisticalcausality. Preserve allfailed readertrace/nativeFP32/fullV3 errors,FileExists localcollectorcollision,V2wrongnativeroot localCtrlC KeyboardInterrupt,V3 actualfullfbound/26files,allunexecutedhelpers andoriginalreports. No remoteGPUsignalSTOP/livepatch or oldcase replay. New hour1_h1_8a7c_v1 complete source8a/owned24/Adam646580, sourcecore and installedRSL5/SDKmath/runtimeassets manifest CPU actualpassed. Only duration changes: GO-to-save3600seconds,lifecyclecap3900 with300saveSDKclosechildwaitreserve,remove arbitrary24update cutoff viaH1_MAX_COMPLETE_UPDATES=None. Original25GiBstart/free8GiBcompleteupdatesavedstop/GPU/RAM/physicalhardguards retained. CPUtests24/25/100/10000notearlystop andinvalidstate negatives; PPOcandidatepublic4-only.001clip6/LRadaptive/learnableinheritedSTD/reward/command/DR/RNG/hardware/CAD unchanged. Fresh actual oldcost/out/canonicalNone/locks/resource checks then new originalowner110623/create1792311677.47 and72GPU0node22089/create1792311679.18 native22092/create1792311679.58 in H1h1_1810p4. Latestcurrent onlynative/noerrors/goempty/nativeCPUnull, not learning yet. Own20knative180 and original independentCPU then remoteoriginalowner production finitechain; independentlaptop/hourly. Noheavyfirst/frozenbehavior audit midhour; save1/every25/stop continues. PreparedpostsaveonlymissingFINAL/cost/out/locksreader anddynamicNfinal/Adam646580+20N frozenpreparer unexecuted. Actualcollectorreturned/freshlocalCIMknownfinite0; noGittraininghostSSH/newwatcher or duplicateprocess. E2E3reviewholds0workerGOcharge,210D21626707968below25GiB noGPUworker,3060SSHrestored but nofreshdesktopMSVCRTadmission,Laptoppaused; no3cardPPOclaim. Sameoriginal1188000seconds budgetonewriteractualintervalonce, noledgercopy/clear/refund/doublecharge/totalincrease. User-hour cadence applies originalscope with safe save/cost/locks handoff, nothotextension or E2E3holdremoval. Same mod4-10ACTIVEhourly/originaltarget updatedV12 andactualreadback exact; no secondmonitor. All originalscope/hardguards/ancestorfalse/unknown/sourceSDKnotbinary/authorednotcookedShape remain. Capture every saved source/report/error/workorder/appreceipt exact or credential-redactedwithoriginalSHA; all PT/raw/USD/ZIPlargeonlyexistingproducerpathsizeSHA,retainoriginals,partialexplicitdeferred. No archival GPU replay/hash/budgetmutation. One actualstage record_experiment and-F annotatedtrial only; prior1376tagobjects/peels/tracked verify, pushfailonlyexistingobjects. Poststageformalreceiptordinaryonly, no infiniteHEADwriteback.'
 for p,s in ((NOTE,note),(MSG,TITLE+'\n\n'+note)):
  with p.open('x',encoding='utf8') as f:f.write(s)
 sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
 DEST.mkdir(parents=True);rows=[];files=[];deferred=[];captured=0
 for p in sorted(x for x in B.rglob('*') if x.is_file() and '__pycache__' not in x.parts):
  if p.suffix=='.partial':deferred.append(dict(path=str(p),bytes=p.stat().st_size,SHA=None,reason='Actual partial retained'));continue
  if p.suffix.lower() not in TEXT:
   r=known.get(str(p.resolve()))
   if r is None:deferred.append(dict(path=str(p),bytes=p.stat().st_size,SHA=None,reason='No existing producer hash; no archival rehash'));continue
   assert p.stat().st_size==r['bytes'];rows.append(dict(source_path=str(p.resolve()),bytes=r['bytes'],sha256=r['SHA'],capture='actual_large_index_only',index_provenance=r['provenance'],original_retained=True));continue
  raw=p.read_bytes();sha=hashlib.sha256(raw).hexdigest()
  if sha in prior:
   r=prior[sha];rows.append(dict(source_path=str(p.resolve()),bytes=len(raw),sha256=sha,capture='existing_complete_Git_SHA_reference',Git_path=r['Git_path'],archived_sha256=r['archived_sha256'],redaction_count=r.get('redaction_count',0),redaction_reason=r.get('redaction_reason'),original_retained=True));continue
  try:txt=raw.decode('utf8');enc='utf8'
  except UnicodeDecodeError:txt=raw.decode('latin1');enc='latin1'
  safe,n=redact(txt);data=safe.encode(enc) if n else raw;dst=DEST/p.relative_to(B);dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(data);rel=dst.relative_to(REPO).as_posix();r=dict(source_path=str(p.resolve()),bytes=len(raw),sha256=sha,capture='complete_credential_redacted_bytes' if n else 'complete_exact_bytes',Git_path=rel,archived_bytes=len(data),archived_sha256=H(dst),byte_preserving_decode=enc,redaction_count=n,redaction_reason='Capture only credential redaction; original retained' if n else None,original_retained=True);rows.append(r);prior[sha]=r;files.append(rel);captured+=1
 index=DEST/'REPORT_CAPTURE_INDEX.json';index.write_text(json.dumps(dict(epoch=time.time(),entries=rows,deferred=deferred,new_texts=captured,one_hour_implemented_not_mid_hour_audit=True,no_GPU_or_account_mutation_for_archive=True),indent=2),encoding='utf8');files.append(index.relative_to(REPO).as_posix())
 rec=importlib.import_module('record_experiment');rec.git=git;sys.argv=['record_experiment.py','--id',ID,'--title',TITLE,'--kind','training','--note-file',str(NOTE),'--files',*files,'--validation','Closed24 complete model and originalcost/out/locks; completed newsource80env frozen physical/executedaction CPU while rawreferencefalse preserved; onehour3600+300,no24cutoff CPU andactualnewnative dispatch.','--push'];rec.main();head=git('rev-parse','HEAD');obj=git('rev-parse',TAG)
 v=u.m.m.u.u.old.prev.prev.prev.prev.g.n.m.cap.a;v.gitio.g=rawgit;v.verify(rows,tags,head,TAG,obj);assert len(git('tag','--list').splitlines())==1377
 print(json.dumps(dict(commit=head,tag=TAG,object=obj,remote_main_tag_peeled_all1376_old_tags_and_tracked_SHA_verified=True,total_tags=1377,entries=len(rows),new_texts=captured,deferred=deferred)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('H1_ONE_HOUR_UNIQUE_GIT_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),if_committed_push_existing_objects_only_no_repeat_record_tag_GPU=True),f,indent=2)
  raise
