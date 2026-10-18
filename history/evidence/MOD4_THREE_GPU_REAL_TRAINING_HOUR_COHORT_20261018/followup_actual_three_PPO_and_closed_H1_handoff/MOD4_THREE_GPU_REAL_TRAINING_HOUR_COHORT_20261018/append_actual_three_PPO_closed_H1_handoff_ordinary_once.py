"""One ordinary followup to the already recorded three-GPU training stage; no trial/tag replay."""
from pathlib import Path
import sys,json,time,hashlib,traceback,importlib.util
B=Path(__file__).resolve().parent;W=B.parent;R=B/'reports';P=W/'MOD4_POST_POWER_RESTORE_H1_SATURATION_REPAIR_20261018';REPO=W/'polar-rl-train'
BASE='c012186b8da995b92cbc40ba4382752b8b760012';DEST=REPO/'history/evidence'/B.name/'followup_actual_three_PPO_and_closed_H1_handoff';NOTE=B/'ACTUAL_THREE_PPO_CLOSED_H1_ORDINARY_NOTE_UTF8.txt'
sp=importlib.util.spec_from_file_location('consumed_three_card_stage_pure_capture_functions_only',B/'archive_three_real_gpu_training_hour_unique_once.py');u=importlib.util.module_from_spec(sp);sp.loader.exec_module(u);git=u.rawgit;H=u.H;TEXT=u.TEXT
def main():
 assert git('rev-parse','HEAD')==BASE and not git('status','--porcelain') and not DEST.exists() and not NOTE.exists()
 tags={}
 for line in git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags/').splitlines():
  x=line.split();tags[x[0]]=(x[1],x[2] if len(x)>2 else x[1])
 assert len(tags)==1379
 indices=[REPO/'history/evidence/MOD4_THREE_GPU_UTILIZATION_STORAGE_RECOVERY_20261018/followup_hour2_production_fe778_full_actual/REPORT_CAPTURE_INDEX.json',REPO/'history/evidence'/B.name/'actual_three_real_gpu_hour/REPORT_CAPTURE_INDEX.json'];prior={};known={}
 for p in indices:
  for row in json.loads(p.read_bytes())['entries']:
   if row.get('Git_path') and row.get('archived_sha256'):prior[row['sha256']]=row
   elif row.get('sha256') and Path(row['source_path']).suffix.lower() not in TEXT:known[str(Path(row['source_path']).resolve())]=dict(bytes=row['bytes'],sha256=row['sha256'],index_provenance=str(p))
 def accept(path,row,proof):
  if not isinstance(path,str):return
  p=Path(path);sha=row.get('SHA') or row.get('sha256');size=row.get('bytes')
  if p.is_file() and p.suffix.lower() not in TEXT and isinstance(sha,str) and len(sha)==64 and isinstance(size,int) and p.stat().st_size==size:known[str(p.resolve())]=dict(bytes=size,sha256=sha,index_provenance=str(proof))
 def visit(v,proof):
  if isinstance(v,list):
   for x in v:visit(x,proof)
  elif isinstance(v,dict):
   for key in ('local_path','path','source_path'):accept(v.get(key),v,proof)
   for x in v.values():
    if isinstance(x,(dict,list)):visit(x,proof)
 for root in (B,P):
  for p in root.rglob('*.json'):
   if '__pycache__' in p.parts:continue
   if 'reports' in p.parts or p.name=='THREE_SLOT_COMPLETE_MANIFEST_V1.json':
    v=json.loads(p.read_bytes());visit(v,p)
    if p.name=='THREE_SLOT_COMPLETE_MANIFEST_V1.json':
     for row in v['files']:accept(str(p.parent/row['relative']),row,p)
 assert json.loads((R/'THREE_REAL_GPU_ACTUAL_PPO_LEARNING_METADATA_VERIFIED_OR_PENDING.json').read_bytes())['three_actual_PPO_learning_verified']
 note='''Three4090 actual independent PPO training, ordinary followup to unique c012186/tagc8415fb; no new experiment/tag. Latesthuman requires all threecards actuallearning, maximum meaningfuluse. Actual19:15metadata verified every slot has trueoriginalGO, productionpositive update1 and matchingGPUUUID workercompute: source210E2 PID137700/create1792321637.84, 72GPU0H1 PID29872/create1792321639.53, 72GPU1E3 PID29881/create1792321640.14. Oneoriginalowner137670/create1792321634.46, independentGO19:07:18 each save3600 lifecycle3900exit300, no24updatecutoff and noheavy midhourPT/behavioraudit. MetadataonlynotwholemodelCPU, not100percentconstantutilization orskillgraduation. ThreefirstAdam666800/649500/657680 actualproducerlogs, completefirstPTnotdownloaded. PreviousH1hour2 actualcomplete74updates35.52Menvsteps/new9c9a7912/16644979B/Adam649480, local199tensor105float wholemodel/runtimefinite/all17actorSTDcritic actualchanges pass; original124906allout/EXIT0/canonicalNone/twooriginalfcntl/targetprivate sharedfree;3660.3592863082886seconds chargedonce/remaining493184.631070137 readonlysnapshot. FirstfinalcollectorSSH10054 preserved, V2onlymissingcompletefinal successful noGPU/native/oldPTreplay. AIremoved redundantstandalone native forjustclosedhealthycheckpoint samebackend/runtime: H1closedproductioncontinuationkind/sourceCPUproofexplicit, nativeCPU None/nativeGPUwaitfalse/sourceNativeCPUhashnull, sourcefullCPU/currenttargetwholemanifest/installedRSLSDKmath/runtimeassets/oldhealthyFINAL EXIT0andcostonce/PPOworkerASTonlyfilenameAdamchanges/8negativecases actualpassed. Neverfakeanothernativequalification, retainalloldfalse. E2E3strictsame-sourcebackendGPU ownnative proofsremain; oldV1unusedfutureH1nativebuilder/deployer preserved unused. NewcontrollersV2 syncedbeforeanynode/no livehotpatch; originalV1remotecontrollersandmanifest backedup. All3 originalreward/LR/learnableSTD/targets/resetDRphysicsCADthresholds unchanged, H1existingpublic4onlyaux.001 retained. Originalaccount/chargeASTexact, oneoriginaltwofcntlwriter independentactualintervalsumonce/noledgercopyclearactiverefunddoublechargeorbudgetincrease;1188000seconds330h7extensions. ActualGPUcomputeusertrainingnotfrozen/native. Newafterhourfinalmissingcollector+wholeCPUreader preparedonlyASTpass, bindnewowner137670 and3sources; no executionorfutureFINALclaim.3060singlecurrentreadonlyV1localimporterror/V2SSHtimeout preserved,noGPUandnotblock4090. Readonlylocalwrongcontroller/workerpathlookupmiss preserved inlocalhandoffreport, noGPUerror. Existingmod4-10ACTIVEhourlyoriginaltarget updatedV17 andactualappTOMLreadbackexact, nosecondmonitor/watchers/autobudget. Allsource/errors/unusedhelpers/workorders/appreceiptsandstageactualremote receipt archived, credentialredactioncaptureonlywithoriginalarchivedSHA/reason, largePTNPZUSDZIPrawproducerpathsizeSHAonlyretainoriginals, noarchivehashGPUreplay ortrainingstop. Old81+189cleanupconsume/Creadonly/sourceDspaceguard maintained. Finalgitverificationtooloutputreceipt avoids endlessformalHEADwriteback. Pushfailureonlyexistingobjects,norepeatcommitrecordtaghelper.'''
 with NOTE.open('x',encoding='utf8') as f:f.write(note)
 sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
 DEST.mkdir(parents=True);entries=[];deferred=[];captured=0
 for root in (P,B):
  for p in sorted(x for x in root.rglob('*') if x.is_file() and '__pycache__' not in x.parts):
   if p.suffix=='.partial':deferred.append(dict(path=str(p),bytes=p.stat().st_size,SHA=None,reason='Actual partial retained'));continue
   if p.suffix.lower() not in TEXT:
    row=known.get(str(p.resolve()))
    if row is None:deferred.append(dict(path=str(p),bytes=p.stat().st_size,SHA=None,reason='No existing producer checksum; no archival rehash'));continue
    assert p.stat().st_size==row['bytes'];entries.append(dict(source_path=str(p.resolve()),bytes=row['bytes'],sha256=row['sha256'],capture='actual_large_index_only',index_provenance=row.get('index_provenance','prior complete index'),original_retained=True));continue
   raw=p.read_bytes();sha=hashlib.sha256(raw).hexdigest()
   if sha in prior:
    row=prior[sha];entries.append(dict(source_path=str(p.resolve()),bytes=len(raw),sha256=sha,capture='existing_complete_Git_SHA_reference',Git_path=row['Git_path'],archived_sha256=row['archived_sha256'],redaction_count=row.get('redaction_count',0),redaction_reason=row.get('redaction_reason'),original_retained=True));continue
   try:txt=raw.decode('utf8');enc='utf8'
   except UnicodeDecodeError:txt=raw.decode('latin1');enc='latin1'
   safe,n=redact(txt);data=safe.encode(enc) if n else raw;dst=DEST/root.name/p.relative_to(root);dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(data);row=dict(source_path=str(p.resolve()),bytes=len(raw),sha256=sha,capture='complete_credential_redacted_bytes' if n else 'complete_exact_bytes',Git_path=dst.relative_to(REPO).as_posix(),archived_bytes=len(data),archived_sha256=H(dst),redaction_count=n,redaction_reason='Capture-only credential-like literal redaction; original retained' if n else None,original_retained=True);entries.append(row);prior[sha]=row;captured+=1
 (DEST/'REPORT_CAPTURE_INDEX.json').write_text(json.dumps(dict(epoch=time.time(),entries=entries,deferred=deferred,new_texts=captured,prior_complete_indices=[p.relative_to(REPO).as_posix() for p in indices],ordinary_only_no_new_tag=True),indent=2),'utf8');git('add','--',DEST.relative_to(REPO).as_posix());git('commit','-F',str(NOTE));head=git('rev-parse','HEAD');git('push','origin','HEAD:main');v=u.u.u.m.m.u.u.old.prev.prev.prev.prev.g.n.m.cap.a;v.gitio.g=git;v.verify(entries,tags,head);assert len(git('tag','--list').splitlines())==1379
 print(json.dumps(dict(ordinary_commit=head,remote_main_all1379tag_objects_peels_tracked_SHA_verified=True,entries=len(entries),new_texts=captured,deferred=deferred)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('THREE_PPO_ORDINARY_GIT_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),if_committed_only_push_existing_objects_no_repeat_commit_or_tag=True),f,indent=2)
  raise
