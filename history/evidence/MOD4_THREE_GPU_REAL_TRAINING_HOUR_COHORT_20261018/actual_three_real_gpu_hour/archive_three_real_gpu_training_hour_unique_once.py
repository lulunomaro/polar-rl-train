"""One actual stage for native preparation and explicit three-card learning continuation, never repeat."""
from pathlib import Path
import sys,json,time,hashlib,traceback,importlib,importlib.util
B=Path(__file__).resolve().parent;W=B.parent;R=B/'reports';REPO=W/'polar-rl-train';S=W/'MOD4_THREE_GPU_UTILIZATION_STORAGE_RECOVERY_20261018'
BASE='51bfb9576e188b64f0ad87ff5110456e731c15db';ID='three-gpu-real-training-one-hour-independent-experts';TAG='trial-20261018-'+ID;TITLE='Resume actual training on three GPUs in original one-hour expert slots';DEST=REPO/'history/evidence'/B.name/'actual_three_real_gpu_hour';NOTE=B/'THREE_REAL_GPU_TRAINING_HOUR_NOTE_UTF8.txt';MSG=B/'THREE_REAL_GPU_TRAINING_HOUR_TAG_UTF8.txt'
sp=importlib.util.spec_from_file_location('previous_consumed_archive_pure_git_functions_only',S/'archive_three_gpu_storage_linux_experts_hour_unique_once.py');u=importlib.util.module_from_spec(sp);sp.loader.exec_module(u);rawgit=u.rawgit;H=u.H;TEXT=u.TEXT
def git(*args):
 if args[:2]==('tag','-a'):
  assert args[2]==TAG and args[3]=='-m' and args[4]==MSG.read_text('utf8');return rawgit('tag','-a',TAG,'-F',str(MSG))
 if args and args[0]=='push':return rawgit('push','--atomic','origin','HEAD:main','refs/tags/'+TAG)
 return rawgit(*args)
def main():
 assert rawgit('rev-parse','HEAD')==BASE and not rawgit('status','--porcelain') and not rawgit('tag','--list',TAG) and not DEST.exists() and not NOTE.exists();oldindex=REPO/'history/evidence'/S.name/'followup_hour2_production_fe778_full_actual/REPORT_CAPTURE_INDEX.json';old=json.loads(oldindex.read_bytes());prior={r['sha256']:r for r in old['entries'] if r.get('Git_path') and r.get('archived_sha256')};known={};tags={}
 for line in rawgit('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags/').splitlines():
  x=line.split();tags[x[0]]=(x[1],x[2] if len(x)>2 else x[1])
 assert len(tags)==1378
 def accept(path,row,proof):
  if not isinstance(path,str) or not isinstance(row.get('bytes'),int):return
  p=Path(path);sha=row.get('SHA') or row.get('sha256')
  if p.is_file() and p.suffix.lower() not in TEXT and isinstance(sha,str) and len(sha)==64 and p.stat().st_size==row['bytes']:known[str(p.resolve())]=dict(bytes=row['bytes'],SHA=sha,provenance=str(proof))
 def visit(v,proof):
  if isinstance(v,list):
   for x in v:visit(x,proof)
  elif isinstance(v,dict):
   for key in ('path','local_path','source_path'):accept(v.get(key),v,proof)
   for x in v.values():
    if isinstance(x,(list,dict)):visit(x,proof)
 for p in B.rglob('*.json'):
  if '__pycache__' in p.parts:continue
  v=json.loads(p.read_bytes())
  if 'reports' in p.parts:visit(v,p)
  if p.name=='THREE_SLOT_COMPLETE_MANIFEST_V1.json':
   for row in v['files']:accept(str(p.parent/row['relative']),row,p)
 e=json.loads((R/'E2_SOURCE210_NATIVE_COMPLETE_OR_PENDING_CPU_METADATA_ACTUAL.json').read_bytes());assert e['rows']['NATIVE_ONLY_PARENT_EXIT_ACTUAL.json']['passed_native_CPU'];assert json.loads((R/'E2_E3_COMPLETE_LEARNING_PAYLOADS_PREUPLOADED_CPU_READY_ACTUAL.json').read_bytes())['finite_transport_returned']
 note='Latest human explicitly requires all three cards participate in actualtraining and maximum meaningful compute use, superseding previoussameexpert E2E3paidreviewholds. Technicalchoice andexecutionagentresponsibility,no repeatedtechnicalapprovalattribution. OriginalH1E2E3scopes,parameters,reward,LR,learnableinheritedSTD,physics,CAD,commandtargets,thresholds and1188000seconds330h7extensions budgetunchanged. CurrentH1hour2originalowner124906/GPU0worker27620 true18:04GO saveplanned19:04 continueshealthy,notstopped/hotextended. Prepare nextsafeactualsavedout/accountonce/canonicalNone/real2fcntl boundary, latestH1fullsource mustnotrollbackfe778. E2newsource21020kfullstate sourceca6fc/owned112/Adam666780 actualnative144/576 performedonce parent131630/worker131644, sixcompletechunks/all2.88Mpolicy rows originalFP32CPUmax7.62939453125e-5,contactimpulse4.76837158e-7,sourceactor9STDcritic8/17Adam literalexact,569519moving4samples,full20kD0D7typedrestore,workerandparentactualEXIT0/out/lockfree. Native0PPO0charge,notskill. Newsourcebackendnativewasunused,notreplayoldfrozen/native. PreserveV1deployer missingroleKeyError beforeanychild; V2onlyexplicitrole onalreadyinstalledunusedtargetactualoutproof, no duplicateupload ornative. E3existing source8043/owned85/Adam657660 itsownsame72GPU1native336/1344/6.72Mpolicy passedoriginalCPU/report6057250... andcompletePT298df... actualwholelocalcore9STD8critic17Adamliteralexact/runtimefiniteCPU; source20kstate/nativeadvancedruntime retained, notfresh80 evalproof. Strictsource/backend/GPU/runtimeasset/Adam/control/EXIT/wait/reportSHA reusepositive12negativecases, noreplaynative/raw oroldPTdownload. OriginalE3FP32enclosure anddual64geometryprotocolkept,notH1exception. V1CPUreportlocalWindowsCRLFhashmismatchbeforeremote preserved; V2exactLinuxLFbytehash restored, oldfailurekept. Excludeonlyunimportedhistoricalstandalonemigrationtool,selectedruntimeassetSHAexact. FutureE3workeronlyaddsoriginalfree8GiBcompleteupdate savedstop, nativebranchASTexact andPPO/reward/STD/LRunchanged. CommonthreeGPUmap nowH1=72GPU016828f91,E2=210937bdb0b,E3=72GPU1c27eecbd, caps3900eachwith3600GOtosave300exit; originalowneraccountingcodebyteexact oneoriginaltwofcntlwriter/independentactualintervalsumonce. Pureoverlapfixture24to36to46seconds prevents terminalE2doublecharge; initialWindowsfcntlimportfailurepreserved,explicitimportshimfixturesnotactualkernellockproof. Existingready/HMAC/manifest/time/run/proof17negativecases pass withoutHTTP/GPU/canonicalIO. E2E3paidpayloadsactuallyuploadedunusedT3h_1810v1/e2pandrecoveryroots; completecurrenttargetmanifests/source175tensor98floator173/96finite/actualinstalledRSLrunnerPPO+SDKmathCPU andoriginalnativereuseCPUbothactualpassed. Preuploaderreturned,noowner/node/GOornewlearningyet. No threePPOclaim fromnative/prepared. H1nextcompletehourcollectorandCPUarepreparedonly; nextpayloadbuilderbindsactualsavednewH1SHA/Adam,three-slotdeployerpreparedbutnotexecutedbeforecurrenthourfinal/out/costonce/locks. NewownerD/T3h_1810v1/owner onlyafterold124906allout; newH1targetT3h_1810v1/h1 ownnewsource20knative180/originalCPU thenGO while E2E3independently reuseexactownnative thenGO. PreservecurrentH1hourlycadence nohalfhourearlystop/no24updatecutoff,rollout20kx24unchanged,hard25GiBstart/free8GiBcompleteupdatesavedstop/GPU/RAM/physicalguards. No newtotalbudget/ledgercopy/clearactive/doublecharge/refund/tail/otherjobsignal/lockdeletion/systemchange. Originalmasters/allancestorfalse/failedprefix/E2signedandE3strict0with57upright/normal8/closure39 retained,notgraduation oruniquephysicalcause. Sameoriginalmod4-10ACTIVEhourlytarget updatedV16andappTOMLreadbackexact; no secondmonitor/watchers5minSSH/autobudget. EachfiniteactualCIMaliveonlyexclusivealltransport andactualreturned; noGittraininghostSSH. Credentials/HMAConlystdinmemorynotargvlogsfiles. Capture allsources/reports/errors/unusedpreparedhelpers/workingorders/appreceipts exactorcredential-redactedoriginalSHA, largePTNPZUSDZIPrawonlyactualproducerpathsizeSHAretainoriginals, noarchiveGPUreplay/hash. Old189/new81cleanupalreadyconsume,reclaimedDspaceguardretained,nofurtherdeletion. One unique record_experiment/-Fannotatedtrial preserves1378oldtagobjectspeels/tracked; pushfailureonlyexistingobjects. LateractualGO/firstmetadata/completeFINAL/source/error/appreceiptsordinaryonly,norepeatrecord/tag/commit orendlessHEADwriteback.'
 for p,t in ((NOTE,note),(MSG,TITLE+'\n\n'+note)):
  with p.open('x',encoding='utf8') as f:f.write(t)
 sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
 DEST.mkdir(parents=True);entries=[];files=[];deferred=[];captured=0
 for p in sorted(x for x in B.rglob('*') if x.is_file() and '__pycache__' not in x.parts):
  if p.suffix=='.partial':deferred.append(dict(path=str(p),bytes=p.stat().st_size,SHA=None,reason='Actual partial retained'));continue
  if p.suffix.lower() not in TEXT:
   row=known.get(str(p.resolve()))
   if row is None:deferred.append(dict(path=str(p),bytes=p.stat().st_size,SHA=None,reason='No current producer checksum; no archival rehash'));continue
   entries.append(dict(source_path=str(p.resolve()),bytes=row['bytes'],sha256=row['SHA'],capture='actual_large_index_only',index_provenance=row['provenance'],original_retained=True));continue
  raw=p.read_bytes();sha=hashlib.sha256(raw).hexdigest()
  if sha in prior:
   row=prior[sha];entries.append(dict(source_path=str(p.resolve()),bytes=len(raw),sha256=sha,capture='existing_complete_Git_SHA_reference',Git_path=row['Git_path'],archived_sha256=row['archived_sha256'],redaction_count=row.get('redaction_count',0),redaction_reason=row.get('redaction_reason'),original_retained=True));continue
  try:txt=raw.decode('utf8');enc='utf8'
  except UnicodeDecodeError:txt=raw.decode('latin1');enc='latin1'
  safe,n=redact(txt);data=safe.encode(enc) if n else raw;dst=DEST/p.relative_to(B);dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(data);rel=dst.relative_to(REPO).as_posix();row=dict(source_path=str(p.resolve()),bytes=len(raw),sha256=sha,capture='complete_credential_redacted_bytes' if n else 'complete_exact_bytes',Git_path=rel,archived_bytes=len(data),archived_sha256=H(dst),redaction_count=n,redaction_reason='Capture-only credential-like literal redaction; original retained' if n else None,original_retained=True);entries.append(row);prior[sha]=row;files.append(rel);captured+=1
 index=DEST/'REPORT_CAPTURE_INDEX.json';index.write_text(json.dumps(dict(epoch=time.time(),entries=entries,deferred=deferred,new_texts=captured,prior_complete_index=oldindex.relative_to(REPO).as_posix(),not_three_PPO_yet_currentH1healthy_others_ready=True),indent=2),'utf8');files.append(index.relative_to(REPO).as_posix());rec=importlib.import_module('record_experiment');rec.git=git;sys.argv=['record_experiment.py','--id',ID,'--title',TITLE,'--kind','training','--note-file',str(NOTE),'--files',*files,'--validation','Actual E2 newsource210 native144 full20k originalCPU passed; existing E3sameGPU native336 fullPT core andstrictreuseCPU; both targetlearningpackagespreuploaded currentSDK; original3intervalaccounting andnegativeprotocolCPU; currentH1 notinterrupted, futureactualGO pending savedhandoff.','--push'];rec.main();head=rawgit('rev-parse','HEAD');obj=rawgit('rev-parse',TAG);v=u.u.m.m.u.u.old.prev.prev.prev.prev.g.n.m.cap.a;v.gitio.g=rawgit;v.verify(entries,tags,head,TAG,obj);assert len(rawgit('tag','--list').splitlines())==1379;print(json.dumps(dict(commit=head,tag=TAG,object=obj,total_tags1379=True,remote_main_tag_peel_all1378oldtags_and_tracked_SHA_verified=True,entries=len(entries),new_texts=captured,deferred=deferred)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('THREE_REAL_GPU_UNIQUE_GIT_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),if_committed_only_push_existingobjects_no_repeat_record_tag=True),f,indent=2)
  raise
