"""One actual continuation stage; preserve all previous trials and reports."""
from pathlib import Path
import sys,json,time,hashlib,traceback,importlib.util,importlib
B=Path(__file__).resolve().parent;W=B.parent;R=B/'reports';T=W/'MOD4_THREE_GPU_REAL_TRAINING_HOUR_COHORT_20261018';REPO=W/'polar-rl-train';BASE='01326bef73b0590777819fdc5aa842f2751e2085';ID='three-gpu-second-hour-closed-source-continuation';TAG='trial-20261018-'+ID;TITLE='Continue all three original experts for one hour from their complete production finals';DEST=REPO/'history/evidence'/B.name/'actual_three_closed_source_next_hour';NOTE=B/'THREE_CLOSED_SOURCE_NEXT_HOUR_NOTE_UTF8.txt';MSG=B/'THREE_CLOSED_SOURCE_NEXT_HOUR_TAG_UTF8.txt'
sp=importlib.util.spec_from_file_location('consumed_prior_stage_pure_git_capture_only',T/'archive_three_real_gpu_training_hour_unique_once.py');stage=importlib.util.module_from_spec(sp);sp.loader.exec_module(stage);rawgit=stage.rawgit;H=stage.H;TEXT=stage.TEXT
def git(*args):
 if args[:2]==('tag','-a'):
  assert args[2]==TAG and args[3]=='-m' and args[4]==MSG.read_text('utf8');return rawgit('tag','-a',TAG,'-F',str(MSG))
 if args and args[0]=='push':return rawgit('push','--atomic','origin','HEAD:main','refs/tags/'+TAG)
 return rawgit(*args)
def main():
 assert rawgit('rev-parse','HEAD')==BASE and not rawgit('status','--porcelain') and not DEST.exists() and not NOTE.exists() and not rawgit('tag','--list',TAG)
 assert json.loads((R/'THREE_REAL_GPU_ACTUAL_PPO_LEARNING_METADATA_VERIFIED_OR_PENDING.json').read_bytes())['three_actual_PPO_learning_verified'];tags={}
 for line in rawgit('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags/').splitlines():
  x=line.split();tags[x[0]]=(x[1],x[2] if len(x)>2 else x[1])
 assert len(tags)==1379;oldindex=REPO/'history/evidence'/T.name/'followup_actual_three_PPO_and_closed_H1_handoff/REPORT_CAPTURE_INDEX.json';prior={};known={}
 for row in json.loads(oldindex.read_bytes())['entries']:
  if row.get('Git_path') and row.get('archived_sha256'):prior[row['sha256']]=row
  elif row.get('sha256') and Path(row['source_path']).suffix.lower() not in TEXT:known[str(Path(row['source_path']).resolve())]=dict(bytes=row['bytes'],SHA=row['sha256'],index_provenance=str(oldindex))
 def accept(path,row,proof):
  if not isinstance(path,str):return
  p=Path(path);sha=row.get('SHA') or row.get('sha256');size=row.get('bytes')
  if p.is_file() and p.suffix.lower() not in TEXT and isinstance(sha,str) and len(sha)==64 and isinstance(size,int) and p.stat().st_size==size:known[str(p.resolve())]=dict(bytes=size,SHA=sha,index_provenance=str(proof))
 def visit(v,proof):
  if isinstance(v,list):
   for x in v:visit(x,proof)
  elif isinstance(v,dict):
   for key in ('path','local_path','source_path'):accept(v.get(key),v,proof)
   for x in v.values():
    if isinstance(x,(dict,list)):visit(x,proof)
 for root in (T,B):
  for p in root.rglob('*.json'):
   if '__pycache__' in p.parts:continue
   if 'reports' in p.parts or p.name=='THREE_SLOT_COMPLETE_MANIFEST_V1.json':
    v=json.loads(p.read_bytes());visit(v,p)
    if p.name=='THREE_SLOT_COMPLETE_MANIFEST_V1.json':
     for row in v['files']:accept(str(p.parent/row['relative']),row,p)
 note='''Actual three-expert next hour, same original scopes and total budget, sourcefullcheckpoints continued without redundant standalone native. Previousfirstthree-cardhour137670 fully closed: H173updates35.04Menvsteps/2e335f6f/16645043B/Adam650940/199tensor105float; E2241updates115.68Menvsteps/f71cc7c3/14615208B/Adam671600/175tensor98float; E395updates45.6Menvsteps/1c5750e1/14715157B/Adam659560/173tensor96float. TwohostcompleteSHA/localwholemodelruntimefinite/all17Adam expected20perupdate/allactor9STDcritic8actualchanges CPU passed. Originalowner/nodes/allchildren EXIT0/out/canonicalNone/twooriginalfcntl/allGPUprivate/sharedfree; actualH13652.5389671325684/E23619.406264781952/E33634.4983172416687secs independentintervalsum10906.443549156189 once, remaining482278.18752098083 readonlysnapshot. No doublecharge/refund/clearactive/accountcopy. Newgenericclosedsource continuation explicitlysourceproduction, notfake native336/144/H1nativequalification. E3productionloader sourcepath only changed to actualnewproductionfullPT, expectedAdam bindingupdated; normalizing allowedloaderblock plusfilenameAdam exactly restores oldworker AST. H1E2onlyfilenameAdam changes. Runtimeassets/lib fullmanifest byteexact, source19/17Adam/STD inherited withtyped20kstate/phase/RNG; originalPPO reward LR learnedSTD targets physics CAD hardware thresholds preserved. Genericproof33negativecases CPU reject; originalowner account/charge AST exact andnodebytesexact, onlyclosedreadyexpertkey generalized h1toe2recovery. Currenttargetactualsourcefullschema/RSLinstalled5+SDKmath/currentGPU/private/shared/RAM/durable25GiB/oldhealthyFINAL EXIT0 andsourceboundproofpassed all3. Same3900caps/saveGO3600/exit300/no24updatecutoff, original20k24rollout andfree8GiBcompleteupdatesavedstop. Latesthuman requiresall3actualtraining, AItechnicalresponsibility no repeatedtechnicalapproval. Neworiginalowner150567 sourceD/T3h2_1810v2/owner, E2node150572,72H1node32508,E3node32525, actualGO/productionpositiveupdateandmatching3GPUcompute verified metadata only; no midhourPTdownload/heavyCPUorbehavioraudit. Newfuturefinalcollector/reviewer bound150567 andactualnewroots preparedASTonlynotexecuted/nofutureFINALclaim. Preserve localPowerShell nestedquote parsererror beforePython/noGPU, separateexactPython helperpreparer fixed. Existingmod4-10ACTIVEhourlyoriginaltarget nextworkorder/appreceipt/readback included, nosecondmonitor/watcher/5minpoll/autobudget/otherjobstop/lockdeletion/systemchange. Original330h7extensions/oneoriginalwriter2fcntl/independentintervalsumonce andancestorfalse/failedprefix/E0W35gate148f516CURB27.5/S3S5notgraduated/heldoutnotune/sourceSDKnotbinary/cookedshape/COMlimits retained. Current3060readonlytimeout originalkept no furtherattempt/GPU, Laptoppaused; sourceD43GB usable original25GiBguardnotblocked,81and189cleanupconsume/Creadonly. AllnewTclosure/source/CPU/cost/reader reports plusUpreparer/worker/controller/CPUnegative/source proofs/actualdeploy/metadata/workorders/monitor/appreceipts preservedGit exactorcredentialcapture-redacted originalarchivedSHAreason. PTNPZUSDZIPraw onlyactualproducerpathsizeSHA indexes originalsretained/noarchivehashorreplay. Unique record_experiment exactnote/Fannotatedtag once; verifyremote main/newtagpeel/all1379oldobjectspeels/tracked. Laterreceiptsformal reportsordinarysupplementonly, nohelperrecordtagrepeat/noendlessHEADwriteback; pushfail existingobjects only.'''
 for p,s in ((NOTE,note),(MSG,TITLE+'\n\n'+note)):
  with p.open('x',encoding='utf8') as f:f.write(s)
 sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
 DEST.mkdir(parents=True);entries=[];files=[];deferred=[];newtexts=0
 for root in (T,B):
  for p in sorted(x for x in root.rglob('*') if x.is_file() and '__pycache__' not in x.parts):
   if p.suffix=='.partial':deferred.append(dict(path=str(p),bytes=p.stat().st_size,SHA=None,reason='Actual partial retained'));continue
   if p.suffix.lower() not in TEXT:
    row=known.get(str(p.resolve()))
    if row is None:deferred.append(dict(path=str(p),bytes=p.stat().st_size,SHA=None,reason='No current producer SHA; no archive rehash'));continue
    assert p.stat().st_size==row['bytes'];entries.append(dict(source_path=str(p.resolve()),bytes=row['bytes'],sha256=row['SHA'],capture='actual_large_index_only',index_provenance=row.get('index_provenance','prior complete index'),original_retained=True));continue
   raw=p.read_bytes();sha=hashlib.sha256(raw).hexdigest()
   if sha in prior:
    row=prior[sha];entries.append(dict(source_path=str(p.resolve()),bytes=len(raw),sha256=sha,capture='existing_complete_Git_SHA_reference',Git_path=row['Git_path'],archived_sha256=row['archived_sha256'],redaction_count=row.get('redaction_count',0),redaction_reason=row.get('redaction_reason'),original_retained=True));continue
   try:txt=raw.decode('utf8');enc='utf8'
   except UnicodeDecodeError:txt=raw.decode('latin1');enc='latin1'
   safe,n=redact(txt);data=safe.encode(enc) if n else raw;dst=DEST/root.name/p.relative_to(root);dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(data);rel=dst.relative_to(REPO).as_posix();row=dict(source_path=str(p.resolve()),bytes=len(raw),sha256=sha,capture='complete_credential_redacted_bytes' if n else 'complete_exact_bytes',Git_path=rel,archived_bytes=len(data),archived_sha256=H(dst),redaction_count=n,redaction_reason='Capture-only credential-like literal redaction; original retained' if n else None,original_retained=True);entries.append(row);prior[sha]=row;files.append(rel);newtexts+=1
 index=DEST/'REPORT_CAPTURE_INDEX.json';index.write_text(json.dumps(dict(epoch=time.time(),entries=entries,deferred=deferred,new_texts=newtexts,prior_complete_index=oldindex.relative_to(REPO).as_posix()),indent=2),'utf8');files.append(index.relative_to(REPO).as_posix());rec=importlib.import_module('record_experiment');rec.git=git;sys.argv=['record_experiment.py','--id',ID,'--title',TITLE,'--kind','training','--note-file',str(NOTE),'--files',*files,'--validation','All3actualclosedfinalCPU/Adam/cost/out/fcntl; nextsamebackendfullsources33negativecases andwholeworkerAST/currenttargetRSLSDK/resourceCPU; actual3GO/positiveproductionupdates/matchingGPUcompute; originalbudgetaccountASTretained.','--push'];rec.main();head=rawgit('rev-parse','HEAD');obj=rawgit('rev-parse',TAG);v=stage.u.u.m.m.u.u.old.prev.prev.prev.prev.g.n.m.cap.a;v.gitio.g=rawgit;v.verify(entries,tags,head,TAG,obj);assert len(rawgit('tag','--list').splitlines())==1380;print(json.dumps(dict(commit=head,tag=TAG,object=obj,total_tags1380=True,remote_main_tag_peel_all1379oldtags_and_tracked_SHA_verified=True,entries=len(entries),new_texts=newtexts,deferred=deferred)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('NEXT_THREE_HOUR_UNIQUE_GIT_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),if_recorded_only_push_existingobjects_no_repeat_record_tag=True),f,indent=2)
  raise
