from pathlib import Path
import sys,json,time,subprocess,importlib,traceback
from datetime import datetime,timezone,timedelta
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';REPO=W/'polar-rl-train'
sys.path.insert(0,str(W/'MOD4_SCUT_WAVE50_GATE_COMPARE_20261012'));import archive_actual_reference_stage_once as archive
archive.FOLDERS=(D,)
ID='local128-fullfinal-sameidentity-7200s-continue-started';DEST=REPO/'history/evidence'/D.name/'sameidentity_second7200_actual'
def save(name,v):
 p=R/name;assert not p.exists();p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf8')
def main():
 assert not archive.gitio.g('status','--porcelain') and not archive.gitio.g('tag','--list','*'+ID) and not DEST.exists()
 actual=max(R.glob('LOCAL_TRAINING_ACTUAL_[0-9]*.json'),key=lambda p:int(p.stem.rsplit('_',1)[1]));proof=json.loads(actual.read_bytes());assert proof['own_saved_positive_PPO_CPU']['passed'] and not proof['error']
 assert json.loads((R/'LOCAL_CONTINUE_HOURLY_MONITOR_ACTUAL_VERIFIED.json').read_bytes())['passed']
 old=archive.gitio.refs();save('LOCAL_CONTINUE_STAGE_ARCHIVE_STARTED.json',dict(epoch=time.time(),unique_trial_id=ID,prior_main=archive.gitio.g('rev-parse','HEAD'),old_tags=len(old),own_positive_PPO_ref=str(actual)))
 note=D/'ACTUAL_LOCAL128_SECOND_CONTINUE_STAGE_REPORT.md';assert not note.exists();note.write_text('''# Same local128 full-final Wave50 continuation actually learning

Human asked why training was not continued, after authorizing temporarylocaltraining and earlier uninterruptednormaltraining. Previous first1800s bounded localwindow ended normally; failuretoarrangecontinuation wasagentworkflowdecision, notGPUfailure orbudgetexhaustion. New independent localroot retains466runtime/asset files allactualoldbyteSHAexact, originalinstalledpackages/plantclockgeometryDRrewardLRcommands/hardwareunchanged. Same128/Windows5.1/0.54.4/TGS32-4/2.5msx4/35actor38critic6action, no extraSDK/native/PPO preflight/oldonce replay.

Selectedonlycomplete localv10 model32305 SHA97361dff5410a325094f8219d6afabe443dabd30331108bd27d4d73969ecfc89/1418935B/107floating/41updates984controls/12startup/full21NPZ audited/uniqueparent1830.2517688274384s. Originalparent/traineractualexit andsharedlocalOSlockfreebeforelaunch. Ancestororiginal459d05c/20k intact, first128 explicitprojection preserved/sourceoriginalIDs/selectedentry unchanged. Newsourceprooffulltree CPUdisk roundtrip andwrongassignmentdifference, finite107/independentstorage; newmaterialize stricter allterrain-entry-command-direction-route-lifetime exact beforeCPUCUDArestore/episode+1. NoPhysXexactresume/backendequivalence orqualified50 claim. Source checkpointnotcovered; newoutputseparate.

Onlynewthree localorchestratorchanges: exactv10final sourceproof binding, stricter sameidentityasserts, sharedpriorlocalOSlock andincludeallowntrainingcomponents inprelaunchsnapshot. New7200s inclloadlearnsaveexit/saveevery2updates/15sownedguardian, perupdatehealthv3/PPOtimeouts managercoverage unchanged. Actualstartup12markers CPUCUDA diskrestore andsameidentityepisode+1 passed, ownpositivePPO/actorchangedoptimizerdelta/107floating complete save actualverified before thisrecord. Activityisnotfuturefinal/50mmroutequalification. Futureownfullfinal/trace/actualexit/sharedlockfree/cost mustfullaudit; first1800+this7200 aretwo samebackend blocks, no blindthirdduration-only beforecompleteaudit.

ResourceactualRAM13.2GB/GPU9.38GBfree/durable96GB beforelaunch; newguard2x4xactualcompleted1800whole38,764,747B+2GiB. NoOSdriverGPUmemorybudgettuning/installedfilechanges/delete/kill/parallelGPU/eval/WASDGUI. ActualGPU5070TiLaptop12227MiB exact; noforeignprocessintervention. One sharedmsvcrtlock inoriginalTEMP root protects localGPUacrossbothroots. Remote4090/3060 remainexplicitlypaused/noSSH/ping/canonicalwrite. Sole0051188000s/7extensions earlyonce notcopied/cleared/refunded/extended; eachattempt actualparentloadlearnsaveexit cost preserved, canonicalreconciliation pending, localrecordsnotsecondbudgetauthority.

Existingmod4-10samehourlytarget updatedactualTOML tocurrentroot andpositiveownsave, healthyDONT_NOTIFY/meaningfulstagesonly. Humancontinuouslocalintentretained; donotselfinventonewindowauthorizationlimit requiringeachhumanprompt. Atsecondblockexit completefullstate/cost/dynamicfamilytraceaudit andnextnecessarybehavioradmission onlocalCPU/GPU whenidle mustguideapprovednextaxis; no blind thirdsame-scope/heightpromotion orqualification fromreward/rootproxy. Needed newphysicalevalcontractmustactualprepare, notfuturepass; no remoteauto-resume. OtherE0/accepted35/CURB20/SLOPE frozen, gateuntrained/S8specificapproval preserved.

Allnewsources/targetCPU/resource/466oldruntimeSHAs/dispatch/startup/ownsavedPPO/observer/preparedfuture/workorder/monitorandactualreceipts captured. Windowsfutureprogressfilelookupnotyetgenerated waslegitimatepending, nottrainingfailure. OriginalTEMPv8fsync/v9proof/nativeDLL/readererrors remainoldGit/raw, notrelabeled. Uniqueannotatedrecord_experiment actualremote main-tag-peeled/alloldtags/trackedSHA verified; laterreceiptordinarysupplement. Allweights/rawNPZ/USDZIP onlyactualpath-size-SHA originalsretained; credentialsexcluded. Runningreportsareactualcapturetime, futurefullfinalmustappendGit. Gitnottrainingdependency; pushfailurecontinueexistingobjectsnorererecord-tag-commit.
''',encoding='utf8')
 rows,files=archive.capture(DEST)
 sys.path.insert(0,str(REPO/'archive_tools'));rec=importlib.import_module('record_experiment');original=rec.git
 def short_git(*args):
  if args[:2]==('add','--'):
   p=subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=b''.join(v.encode()+bytes([0]) for v in args[2:]),capture_output=True,check=True);return p.stdout.decode().strip()
  return original(*args)
 rec.git=short_git;sys.argv=['record_experiment.py','--id',ID,'--title','Continue local128 Wave50 from audited full-final for bounded7200s actual PPO','--kind','training','--note-file',str(note),'--files',*files,'--validation','Exact466oldruntime/assetSHA reused; v10final107 source/PIDexit/sharedOSlock boundary verified. Stricter fullsamegeometry-entry-command-direction-route-lifetime CPUCUDA roundtrip/12startup/episode+1. OwnpositivePPO complete checkpoint CPUverified; resourceguard and samehourlylocalonly monitor actualTOML passed. Remote paused/canonical reconciliation pending. No GPU preflight replay/sourceoverwrite/installedpackage or physicalthreshold change.','--push'];rec.main()
 tag='trial-'+datetime.now(timezone(timedelta(hours=8))).strftime('%Y%m%d')+'-'+ID;head=archive.gitio.g('rev-parse','HEAD');obj=archive.gitio.g('rev-parse',tag);archive.verify(rows,old,head,tag,obj)
 save('LOCAL_CONTINUE_STAGE_GIT_RECORDED.json',dict(epoch=time.time(),passed=True,commit=head,tag=tag,tagobject=obj,remote_main_tag_peeled_verified=True,old_tags_preserved=len(old),sources=len(rows),future_reports_and_this_receipt_require_ordinary_supplement=True,push_pending=False))
 print(json.dumps(dict(passed=True,commit=head,tag=tag,tagobject=obj,sources=len(rows),old_tags=len(old))))
if __name__=='__main__':
 try:main()
 except BaseException:save('LOCAL_CONTINUE_STAGE_GIT_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),inspectexistingobjects_no_rerecord_tag_commit=True));raise
