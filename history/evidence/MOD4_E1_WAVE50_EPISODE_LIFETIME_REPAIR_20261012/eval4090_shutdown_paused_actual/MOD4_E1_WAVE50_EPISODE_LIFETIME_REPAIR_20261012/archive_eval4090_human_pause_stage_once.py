from pathlib import Path
import os,sys,json,time,hashlib,importlib,subprocess,traceback
from datetime import datetime,timezone,timedelta
import archive_full153_player_lifetime459_stage_once as inherited
D=Path(__file__).resolve().parent;R=D/'reports';W=D.parent;REPO=W/'polar-rl-train'
archive=inherited.archive
archive.FOLDERS=(D,W/'MOD4_E1_WAVE50_ROUTE_SECOND_BOUNDED_20261012',W/'MOD4_E1_WAVE50_ROUTE_LIFECYCLE_REPAIR_20261012',inherited.StablePlayer())
ID='lifetime459-final-eval4090-raw-saved-human-shutdown-paused'
DEST=REPO/'history/evidence'/D.name/'eval4090_shutdown_paused_actual'
h=lambda b:hashlib.sha256(b).hexdigest()

def save(name,v):
 p=R/name;assert not p.exists();p.write_bytes(json.dumps(v,ensure_ascii=False,indent=2).encode());return p

def main():
 assert not archive.gitio.g('status','--porcelain') and not archive.gitio.g('diff','--cached','--name-only')
 assert not archive.gitio.g('tag','--list','*'+ID) and not DEST.exists()
 for name in ('HUMAN_SHUTDOWN_PAUSE_METADATA_SYNCED.json','HUMAN_SHUTDOWN_MONITOR_ACTUAL_VERIFIED.json'):assert json.loads((R/name).read_bytes())['passed']
 latest=max(R.glob('HUMAN_SHUTDOWN_BACKUP_COMPLETE_[0-9]*.json'),key=lambda p:int(p.stem.rsplit('_',1)[1]));back=json.loads(latest.read_bytes());assert back['passed']
 S=Path(back['backup_directory']);safe=json.loads((S/'SHUTDOWN_SAFE_REMOTE_ACTUAL.json').read_bytes());manifest=json.loads((S/'BACKUP_COMPLETE_BYTEEXACT.json').read_bytes())
 assert safe['passed'] and manifest['passed'] and len(manifest['files'])==696 and sum(v['bytes'] for v in manifest['files'])==482335583
 assert safe['own_checkpoint']['sha256']=='d05c2f3ce1acc7988137f94a8853be0a6ac686d53225ef000821031bd1ffe64a'
 assert safe['all4_evaluation_actualcomplete_errorfree'] and safe['complete_behavior_review_pending']
 old=archive.gitio.refs();save('EVAL4090_SHUTDOWN_ARCHIVE_STARTED.json',dict(epoch=time.time(),trial_id=ID,prior_head=archive.gitio.g('rev-parse','HEAD'),old_tags=len(old)))
 note=D/'ACTUAL_EVAL4090_HUMAN_PAUSE_STAGE_REPORT.md';assert not note.exists()
 note.write_text('''# Source459 complete full-state save, independent4090 evaluation raw complete; human requested shutdown pause

Human reported poor manual50/70 performance and asked continued training, then explicitly authorized4090 evaluation while3060 unavailable and requested training/evaluation parallelism. Source459 first independent Wave-born20to40s lifetime300s window has naturally completed; sourceaccepted35b026 and1293c97 ancestor pinned, initial old35 fullactor-critic-std-optimizer/allD0D7/globalnamed/dictprivate CPUCUDA identity then explicit50-entry-direction-route-lifetime migration/CUDA diskroundtrip/sourceepisode+1. Eleven own startup receipts passed; ownmodel32264 SHA d05c2f3ce1acc7988137f94a8853be0a6ac686d53225ef000821031bd1ffe64a, actualfloatingCPU107 plus3bool/int fields, source459/104actualmodule snapshots+ownfreeze/PID3447391.6updates144controls2.88Msteps576callbacks,9actor changed/optimizerdelta120, complete health and PASSED saved, unique335.22595477104187s originalparent once settled. No oldstage/preflight/main/resume replay, no originalexpert/DR/reward/clock/hardware changes, not qualified50/70/MoE/permanentantiforgetting.

Only new frozen evaluation backend was ported to4090 Linux under human request. Originalterrain archive cef44c0 andretention8a964c1 bytes/source AST retained, singleabsolute USD path adapter disclosed. Original80terrain/flat88spin/world1500controls15s/seed20260928terrain-20261002retention/white_v3/2.5msx4TGS32-4 and physical/query1e-6/contact1N/COMhardware/health constraints unchanged. Four independentprivate eval4090-lifetime459-d05c jobs, noglobal154 claimed, each once oneevalchild/noPPO/canonicalwrite. Allfour actualcomplete/errorfree/raw generated; maxobservedGPU terrain5979MiB, retention3381/3385/3387MiB sampled2s notcontinuouspeak. Complete independent behavior/fullroute/query/contact/retention review is still pending, no scores or qualification inferred. Crosshost engine equivalence not certified.3060 worker/task/jobs not touched.

Secondsame-lifetime parallel training remained partial localpreparation. Original prepare_same_lifetime_parallel_second_once.py SyntaxError before targetroot/sourcefreeze/targetCPU/GPU/dispatch retained, oneunusedworker exists; controller/guard uncreated. Earlier CPUlookup importNone/filter/remote rg unavailable errors and sources preserved. Training/evaluation concurrency was not implemented or demonstrated, no memorybuffer/OS/driver/PhysX change.

Human latestrequest: pause training to shutdown/restart and save everything. Same mod4-10 automation setPAUSED/hourly sametarget; explicitresume required, noautomaticrestart. Actual fresh /proc parentguardiantrainer andfour eval children absent/exited, three flocklocks free, GPUcompute empty, canonical/controlleractive empty. No kill/signal/hotpatch/clearactive/ledgercopy/refund/extension/recharge/newPPO. Exact latestfullcheckpoint andall ownrun snapshots/startup/health/traces, source reports andall4090eval raw/probe/log/results copied into local immutable shutdown_backup_1791808183793797400,696files/482335583B actualsize-SHAbyteexact/fsync. Originalremote files retained. SHUTDOWN_SAFE_REMOTE_ACTUAL andBACKUP_COMPLETE_BYTEEXACT bindpaths/SHA; localhandoff statespendingbehaviorreview andsecondpartialbuilder. No secondcanonical authority created; actualledger unique segment, remaining snapshot and SHA indexed only.

Protectedcentralcurrent CAS marks humanpause, source459formalfinal and4090allcomplete/rawreviewpending; master/approvaltracks/RM004/canonicalbytes unchanged. Nativeautomation actualTOML PAUSED/hourly/target/prompt verified. Human mayshutdown/restart; noagent shutdown command, no otherAI orWASD GUI intervention. Explicitresume mustread freshstate, completebackedupfourcase fullreview then independentlyadmit reasonable bounded nextscope; never repeat consumedonce. OtherobservedE0/35/CURB20/SLOPE frozen, gateuntrained/S8specificapproval,0051188000s sevenextensions earlyonce.719cleanup/exactPIDkill authorizations consumed.

All newlysaved laterbig/fresh/formalfinal/fullCPU,4090backend source/runtimeadapter/resource/results, originalreader/builder failures andunusedpreparation, backupindices/pause/handoff/sync/monitor/Gitreceipts captured. LargePTNPZrawJSONUSDZIP indexed actualpath-size-SHA only, originals retained; credentials redacted/excluded. This newevaluation+shutdownsafe stage uses unique annotated record_experiment; verifyremote main/tag/peeled andalloldtags/trackedSHA. Stage receipt must be ordinarysupplement; pushfailonlyexistingobjects, do not rerecord/relabel/recommit orGPUreplay.
''',encoding='utf8')
 rows,files=archive.capture(DEST)
 sys.path.insert(0,str(REPO/'archive_tools'));rec=importlib.import_module('record_experiment');original=rec.git
 def short_git(*args):
  if args[:2]==('add','--'):
   r=subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=b''.join(v.encode()+bytes([0]) for v in args[2:]),capture_output=True,check=True);return r.stdout.decode().strip()
  return original(*args)
 rec.git=short_git;sys.argv=['record_experiment.py','--id',ID,'--title','Save complete lifetime459 and4090 evaluation raw; pause safely for human restart','--kind','evaluation','--note-file',str(note),'--files',*files,'--validation','Own107-floating fullstate/11startup/source459/unique335.225once final passed. Fourprivate4090cases complete raw backed up; behavioralreview pending. Freshownedprocesses exited/three flockfree/GPUempty/activeempty;696files482335583B byteexact localbackup. Originalparallelbuilder pretargetSyntaxError retained. Humanpause nativePAUSED andprotectedcentralCAS actualverified, noPPO/signal/budget/delete.','--push'];rec.main()
 tag='trial-'+datetime.now(timezone(timedelta(hours=8))).strftime('%Y%m%d')+'-'+ID;head=archive.gitio.g('rev-parse','HEAD');obj=archive.gitio.g('rev-parse',tag);archive.verify(rows,old,head,tag,obj)
 save('EVAL4090_SHUTDOWN_STAGE_GIT_RECORDED.json',dict(epoch=time.time(),commit=head,tag=tag,tagobject=obj,remote_main_tag_peeled_verified=True,all_old_tags_preserved=len(old),saved_sources=len(rows),push_pending=False,receipt_needs_ordinary_supplement=True))
 print(json.dumps(dict(passed=True,commit=head,tag=tag,tagobject=obj,remote_verified=True,sources=len(rows),old_tags=len(old))))

if __name__=='__main__':
 try:main()
 except BaseException:save('EVAL4090_SHUTDOWN_GIT_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),inspect_existingobjects_no_record_tag_commit_replay=True));raise
