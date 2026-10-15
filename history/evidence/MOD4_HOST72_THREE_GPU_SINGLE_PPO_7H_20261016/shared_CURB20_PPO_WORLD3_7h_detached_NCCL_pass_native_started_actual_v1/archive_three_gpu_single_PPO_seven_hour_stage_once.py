"""One actual assignment/upload/resource-rejection stage; never rerun after record."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import hashlib,importlib,importlib.util,json,subprocess,sys,time,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';REPO=W/'polar-rl-train'
BASE='892911867d23f8539c6645f58096cd63d949d7be'
ID='three-gpu-one-ppo-seven-hour-durable-dispatch-nccl'
DEST=REPO/'history/evidence'/D.name/'shared_CURB20_PPO_WORLD3_7h_detached_NCCL_pass_native_started_actual_v1'
s=importlib.util.spec_from_file_location('two_E1_tasks_archive_pure_helpers',W/'MOD4_S5_NOMINAL_AUDIT_SOURCE_ADAPTER_CPU_20261015/archive_nominal_isolated_source_target_native_and_unused29_stage_once.py');n=importlib.util.module_from_spec(s);s.loader.exec_module(n)
def git(*args):
 if args and args[0]=='add':
  files=[v for v in args[1:] if v!='--'];r=subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=('\0'.join(files)+'\0').encode('utf8'),capture_output=True)
  assert r.returncode==0,r.stderr.decode('utf8','replace');return r.stdout.decode('utf8','replace').strip()
 return n.git(*args)
def H(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 return h.hexdigest()
NOTE="Human explicitly ordered one task on all three4090s synchronously training the same PPO for seven continuous hours, allowed coexistence with other compute, and asked remote persistence because the laptop will power off. This overrides the previous two independent1800s assignments and busy-resource hold, not the no-deletion/host72root/systemdriver/other-process boundaries. Unified task is original E1_CURB20 entry20mm/150mm mirrored geometry from protected complete3c97 source, original actor9/critic8/17Adam and D0-D7/noise/rewardhardware/physics preserved. Per-rank20000 envs gives60000 global explicitly, not a claim global20000. All ranks first strictrestore original state/sourceepisode+1, then ranks1/2 explicitly fork private/global RNG streams; first factors from source reset remain shared, no strictPhysX or independentinitialfactor claim. Original RSL5 multiGPU NCCL gradient reduction, synchronized adaptiveKL/LR, original returns/GAE/timeout/clip/epochs/minibatches are used; distributed advantage normalization remains the framework's per-rank default. Not three independent policies or mixture/gate/jump/S8.\n\nComplete422file package with exact source/assets/optimizer and manifest uploaded/verified at original210 durable newroot and72 ownedROOT/tasks/newroot. Three actual physicalUUIDs checked by live NCCL allreduce1+2+3=6, three shared fixture Adamresults identical, eachprobeEXIT0. Fixture is not MOD4 PPO. Source owner395924 detached and original twofcntl held, authenticated finite node72agent detached with HMAC capability only in inheritedstdin memory, never stored in logs/config/argv/Git. No SSHcredential stored. Actual rank0worker396065 and rank1/2workers3067619/3067626 created under the new roots after successfulprobe; original original20k robot construction/native/fullstate underway at capture. ActualsavedPPO not yet claimed. Source/target original SDK not modified, owned headlesslauncher onlysupportedlaunchconfig, no driverguard bypass. Raw prefix chunks and exact original model/state saved before learning, originalhealthguards unchanged.\n\nRemote finite automaticchain NCCL to allrank sourcefullrestore/native120/480callbacks/exactactorcriticoptimizer, then source originalcanonical owner starts one25200s shared-job wall interval, sends authenticatedstart/deadline, uses actualsingle RSL5 PPO allreduce. Firstupdate/every25update/end savesallrank fullstates, comparesactorSHA/criticSHA/Adamstep exact, collectiveMAXstop and barriertiming preservescompletedupdates. Remote sourceparent, nodeagent and absolute per-rank deadline keep running after laptop shutdown. Existing local hourlymonitor is supplemental, not runtime dependency. Human new concurrent shared-job accounting contract records originalsolecanonical oneparent wall interval<=25200s, nominal threeGPU resource75600s separatemetadata, no perrankduplicatecharge/newledger/budgetextension/refund/clearactive/tail. Native0PPOpreflight uncharged, save/exit120s headroom. Actual learning begin/startsave and originalcost/exit/locks lateractualoverride snapshot; no promise startup or improvement from preparedsource. Latest fresh actualallthreeGPUs were free but user permits coexistence, no otherjob stopped or altered.\n\nPreserve first local preparation reader LookupError utf8-sig, independentV2 utf-8-sig repair reusing originalcopiedpayload, original source SyntaxWarning docstring, noGPUretry or overwritingfalse. Existing independent-assignmentstage892911/annotatedtrial verifiedremote all1349oldtags/875sources, never repeat oldrecord/runtime. Existing original35 actualseed60928 correction and alloriginalS3/S5 residuals/source/cost limits remain. Allnewsource/package/deploy/NCCL/nativepending/snapshots/workorder/monitor/reader errors captured; largePTNPZUSDtar path-size-SHA indexes and originalsretained, no credentials or capability included. Newstageuniqueannotatedtrial once, lateractualnative/PPO/receipt/error ordinarysupplements. Pushfailurecontinueexistingobjects, no repeatrecord/tag/commit/runtime. Git does not block remote sevenhour job."
def main():
 assert git('rev-parse','HEAD')==BASE and not git('status','--porcelain') and not git('tag','--list','*'+ID) and not DEST.exists()
 assert json.loads((R/'TARGET_THREE_RANK_EXTRACT_ACTUAL.json').read_bytes())['rc']==0
 assert json.loads((R/'SOURCE_THREE_RANK_EXTRACT_ACTUAL.json').read_bytes())['rc']==0
 old={}
 for line in git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags/').splitlines():
  v=line.split();old[v[0]]=(v[1],v[2] if len(v)>2 else v[1])
 assert len(old)==1350
 sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
 note=D/'THREE_GPU_ONE_PPO_7H_REMOTE_NCCL_ACTUAL_STAGE_NOTE.txt'
 with note.open('x',encoding='utf8') as f:f.write(NOTE)
 DEST.mkdir(parents=True);rows=[];files=[]
 for p in sorted(x for x in D.rglob('*') if x.is_file() and '__pycache__' not in x.parts):
  h=H(p);size=p.stat().st_size;row=dict(source_path=str(p.resolve()),bytes=size,sha256=h)
  if size>8*1024*1024 or p.suffix.lower() in ('.pt','.pth','.npz','.npy','.usd','.zip','.gz','.mp4','.dmp'):
   row.update(capture='large_or_binary_actual_path_size_SHA_index_only',original_retained=True)
  else:
   raw=p.read_bytes()
   try:clean,count=redact(raw.decode('utf8'))
   except UnicodeDecodeError:
    row.update(capture='binary_actual_path_size_SHA_index_only',original_retained=True);rows.append(row);continue
   data=clean.encode('utf8') if count else raw;out=DEST/p.relative_to(D);out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data);rel=out.relative_to(REPO).as_posix();files.append(rel)
   row.update(capture='redacted_full' if count else 'complete_exact_bytes',Git_path=rel,archived_sha256=hashlib.sha256(data).hexdigest(),redactions=count)
  rows.append(row)
 index=DEST/'REPORT_CAPTURE_INDEX.json';index.write_text(json.dumps(dict(epoch=time.time(),entries=rows,all_saved_stage_success_rejection_false_unused_reader_errors_workorders_monitor_at_snapshot_captured=True,credentials_excluded=True,large_originals_retained=True,later_reports_require_ordinary_supplement=True),indent=2),encoding='utf8');files.append(index.relative_to(REPO).as_posix())
 rec=importlib.import_module('record_experiment');rec.git=git
 sys.argv=['record_experiment.py','--id',ID,'--title','Launch durable three-GPU single PPO seven-hour chain; verify real cross-node NCCL and retain native pending','--kind','diagnostic','--note-file',str(note),'--files',*files,'--validation','422file bothnodes sourceSHA exact; actual3GPU NCCL allreduce and shared fixture optimizer exact/EXIT0, durable originalowner andnodeagent detached, robot native constructing. No PPOpositive inferred. Human WORLD3 onejob sevenhour contract/originalsolecanonical and allrank exactstate proof required.','--push']
 rec.main();head=git('rev-parse','HEAD');tag='trial-'+datetime.now(timezone(timedelta(hours=8))).strftime('%Y%m%d')+'-'+ID;obj=git('rev-parse',tag)
 n.m.cap.g=git;n.m.cap.a.gitio.g=git;n.m.cap.a.verify(rows,old,head,tag,obj)
 print(json.dumps(dict(commit=head,tag=tag,object=obj,actual_remote_main_tag_peel_all1350_oldtags_and_tracked_SHA_verified=True,sources=len(rows),PPO_status_at_capture='native_pending_not_inferred_positive')),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('THREE_GPU_SINGLE_PPO_STAGE_GIT_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x') as f:json.dump(dict(error=traceback.format_exc(),resume_existing_capture_objects_not_record_tag_commit=True),f,indent=2)
  raise
