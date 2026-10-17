"""Unique new actual closure/backend/parallel stage; old helpers are imported only as pure libraries."""
from pathlib import Path
import os,sys,json,time,hashlib,importlib.util,importlib,traceback
B=Path(__file__).resolve().parent;R=B/'reports';W=B.parent;REPO=W/'polar-rl-train';P=W/'MOD4_H1_HUMAN_REQUESTED_SAME_SCOPE_RESTART_20261017';A=W/'MOD4_H1_TARGET72_CLOSED_FINAL_E3_FROZEN_REVIEW_20261017'
BASE='8e0e9f9d782ec6d1b770839f3495cd5791d5cb75';ID='h1-final24-linux4090-parallel-frozen-training';TAG='trial-20261018-'+ID;TITLE='Continue H1 training alongside human-authorized Linux4090 frozen evaluation'
DEST=REPO/'history/evidence'/B.name/'actual_linux4090_parallel_training_frozen_v1';NOTE=B/'LINUX4090_PARALLEL_STAGE_NOTE_UTF8.txt';MSG=B/'LINUX4090_PARALLEL_ANNOTATED_TAG_MESSAGE_UTF8.txt'
sp=importlib.util.spec_from_file_location('prior_P_archive_pure_functions_not_main',P/'archive_human_requested_H1_native_reuse_finite_unique_stage_once.py');prev=importlib.util.module_from_spec(sp);sp.loader.exec_module(prev);rawgit=prev.rawgit;H=prev.H
def git(*args):
 if args[:2]==('tag','-a'):
  assert args[2]==TAG and args[3]=='-m' and MSG.read_text('utf8')==args[4];return rawgit('tag','-a',TAG,'-F',str(MSG))
 if args and args[0]=='push':return rawgit('push','--atomic','origin','HEAD:main','refs/tags/'+TAG)
 return rawgit(*args)
def main():
 assert git('rev-parse','HEAD')==BASE and not git('status','--porcelain') and not git('tag','--list',TAG) and not DEST.exists()
 final=json.loads((P/'reports/HUMAN_REQUESTED_H1_COMPLETE_FINAL_FULL_CPU_COST_EXIT_ACTUAL.json').read_bytes());assert final['passed_whole_final_model_local_CPU'] and final['actual_duration_bound_passed']
 first=json.loads((B/'paid_d723_v4/reports/PARALLEL_D723_H1_IMMUTABLE_FIRST_COMPLETE_LOCAL_CPU_V2_ACTUAL.json').read_bytes());assert first['passed_real_immutable_first_complete_local_CPU']
 native=json.loads((R/'H1_FE1709_LINUX72_120_ALL_PHYSICAL_PUBLIC04_SOURCE_CPU_ACTUAL.json').read_bytes());assert native['passed_complete_data_and_source_CPU']
 tags={}
 for line in git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags/').splitlines():
  x=line.split();tags[x[0]]=(x[1],x[2] if len(x)>2 else x[1])
 assert len(tags)==1372
 note='''Human confirmed3060 machine powered off and unavailable and explicitly authorized selecting any4090 for frozen evaluation concurrently with training, without interrupting training. No more3060 retry or wait. This supersedes the old3060-only routing, not physics/reward/budget constraints.72GPU0 continues H1 paid learning,72GPU1 performs pinned-fe1709 frozen evaluation with its own Linux SDK fingerprints and private fcntl. Original globalvalidation lock is briefly checked exactly as existing perGPU resource acquisition, not held to serialize the other GPU. No other job is killed, signalled or modified.210D21.6GB remains below25GiB and no210GPUworker/Cwrite/additionalcleanup is authorized.

Prior P actual H1 finite segment fully closed24updates/576controls11.52Menvsteps. Full d7238b885879705fa8312758337bf0b6ca1d97c2f906df51b72c27b475e7786a/16643699B all199tensor105float finite, actor9includingSTD/critic8 all17changed,17Adam644660to645140. Originalowner787613/node/children actualout EXIT0,canonicalNone/originaltwofcntl and targetprivate/sharedfree.1474.6476094722748s once settled<=1800; remaining506379.3127942085s is only actual snapshot. No refund,clearactive,newledger,duplicate charge or budget increase.

Latest d723 then completed its own actual72GPU0 native180/720/all3.6Mpolicy14.4Mphysical independentCPU and twohost completePT/local199tensor105float/source9STD8critic17Adam645140 exact. Nativeparent3195219/worker3195222 actualout,zeroPPOzerocharge. New paid namespace H1r_1810v4 reuses only this exact source/backend/runtime/native proof after currentOSresource and oldpaid fullclose. New strict validator positive/11negatives retained. Original sourceowner797931/create1792254856.51 and72node3196574/worker3196580/create1792254861.69; actualGO1792254860.4717388,1800cap/300headroom/max24updates/free8GiB fullupdate savedstop,25GiBstart unchanged. Actual first completePTs confirm645140to645160/all17changes/startupcoreliteralexact/sourceepisode+1/phaseage0,not jump qualification or futureFINAL guarantee. Source construction/load/save/SDKclose/childwait/ownerterminal remains original charged interval. E2/E3 paid holds remain0GO0worker, not training on three GPUs. New source reuse CPU preparer V1wrongreportlookup,V2already-reuse-nodeassert,V3historicalfilenamecollision and V4success are all preserved with partialpackages. First CPU reader wrongimportdepth and V2fix retained; no remote work occurred for these reader/preparer errors.

Pinned frozen source is fe1709/Adam644660/owned24, not d723. Fresh80/20260928/white_v3/normal100-public4next80-normal/zero twist, actual published perenv0/4/no hidden phase or envID,35obs/whole6clip6/previousactual6/selectedreset,onlyactor9STD loaded. Original H1 environment/phase/seven masked rewards/prelaunch physical source remain exact. No20kDRstate forced into80. Everycallback all80body31/authored34/query1e-6/contact integration/COM1e-5/torquespeedhardware/mimic.01/closure.002/unknown-nonfinite-missingcallbacks failedprefix retained. OriginalH1strict actorCPUmean1e-4, authoredgeometry1e-6,event1e-6 preserved; no E3exception substituted.

Original WindowsV1 targetconnecttimeout beforeTask/root/GPU and independent22/3389timeout remain. V1observer frame-cleared-before-originalreward bug was reproduced CPU; V2fixed frame lifetime but fixture decimalFP32literal assertion failed; V3used exact actualsource FP32expression with sourcephysics/reward unchanged. LinuxV4 changes only backendworker/parent/readonlybinaryfingerprint adapter, ownheadless launcher/perGPUfcntl. ActualLinuxmath and installedRSLrunner/PPO fileSHA pinned; rsl-rl distributionmetadata lookup is missing and explicitly recorded, not invented; sourcefiles verified independently. First V4CPUmetadata failure retained. V2finisher admittedsource/backend and ran native120, but parent was not detached and original launcher timedout30s/killedparent. V4actual80/120/480 complete data and55MBraw metadata retained, originalparent timeout is not EXIT0/nativeparentqualification. No oldworker was relaunched or hotpatched.

After V4actualallout, newV5 namespace fixes parent detach using original proven fork/setsid/stdin redirect pattern, unchangedphysics/controller/source. NewV5ownnative120/480/all9600actor38400physical complete data independently CPU passed with actualchildEXIT0/parentchildout/privatefcntlFree. MissingEXIT_NATURAL remains disclosed. Native actorCPUmax6.103515625e-5,geometry3.270129012022949e-8,impulse2.956390381392282e-7,phase7.450580596923828e-9,0ordinary0trunc;0takeoff/landing/recovery is not skillPASS. Reader callback-index variable shadowed collectiondict causing TypeError after phaseaudit; V2only binds a distinct callback variable and passes all saved data. New unused full1500/6000cb namespace is admitted only after actual nativeCPU/out/lockfree, rechecks sourceSDK/resource, no native/raw replay. Full result and any error/CPUfollowup are exactly what current reports show, never inferred from dispatch.

One bounded collector at a time owns210/72/249transport only while actualCIMcreationargv alive; rootlocalreports only then; handback actual, no newwatcher/5minSSH/secondmonitor. BothGPU ownfiniteworkers independent of laptop/heartbeat. Same existingmod4-10 ACTIVEhourlytarget only. E2fixed1093/64,10122/64,1050/64,1121/64 and directvy rewardsource diagnosis remain reviewhold; E3original0/96fullstable with57upright50/noreset15s,normal8/8 and39closure failures remain no blindpaid addition. H1sourceoldnative/proxy not jump skill. Originalmaster812a4b+004005/RM003002001/1188000s330h7extensions,20k/originalsource60928-statesunchanged/frozenrecipe20260928/24/LR1e-4adaptiveKEEPSTD1/35-38-6/.0025x4TGS32/4/100Hz/history5msbin3/D0D7white_v3+noise/hardware unchanged. No oldgrant hotextend/newbudget/teacher/terraintruth/futurecontact/correctionforce/NCCL/average/newgate/H2H3/S8/70/yaw6/8/10. All ancestorsfalse/heldouts/SDK-not-binary/cookedShape/COM/hardwaredeadline limits preserved. CredentialHMACstdinmemory only; oldNargvdisclosure retained, no claim of OSauditabsence.

All successes/failures/partialpackages/unusedreaders/newports/source/lookupmiss/workorders/monitorappreceipt/fulltextJSON included. LargePTNPZUSDZIP/tar/raw only actualpathsizeSHA, originals retained except previously authorized exact189deletionhistorical. Priorstage helpers and all once objects remain consumed. New unique stage uses exact title+note file-F once. Pushfailure continues existingobjects, not repeat record/tag/commit. Futureformal reports/receipt supplement ordinary. Current actual first/native CPU reports follow:
'''+json.dumps(dict(first=first,native=native,latest_d723_frozen_native_CPU=json.loads((R/'H1_D723_LINUX72_120_ALL_PHYSICAL_PUBLIC04_SOURCE_CPU_ACTUAL.json').read_bytes()),latest_d723_full_CPU=json.loads((R/'H1_D723_LINUX72_1500_ALL_PHYSICAL_PUBLIC04_SOURCE_CPU_ACTUAL.json').read_bytes()) if (R/'H1_D723_LINUX72_1500_ALL_PHYSICAL_PUBLIC04_SOURCE_CPU_ACTUAL.json').exists() else None,new_current_paid_final_CPU=json.loads((B/'paid_d723_v4/reports/PARALLEL_D723_H1_COMPLETE_FINAL_FULL_CPU_COST_EXIT_ACTUAL.json').read_bytes()) if (B/'paid_d723_v4/reports/PARALLEL_D723_H1_COMPLETE_FINAL_FULL_CPU_COST_EXIT_ACTUAL.json').exists() else None),ensure_ascii=False)
 for p,s in ((NOTE,note),(MSG,TITLE+'\n\n'+note)):
  with p.open('x',encoding='utf8',newline='\n') as f:f.write(s)
 sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
 prior={}
 for root in (P,A,W/'MOD4_H1_CLOSED24_TARGET72_SAME_SCOPE_FINITE_20261017',W/'MOD4_RECOVERY_CLOSED_FINAL_H1_STORAGE_BOUNDED_HANDOFF_20261017'):
  target=REPO/'history/evidence'/root.name
  for idx in target.rglob('REPORT_CAPTURE_INDEX.json'):
   for row in json.loads(idx.read_bytes())['entries']:
    if row.get('Git_path'):prior[row['sha256']]=row
 DEST.mkdir(parents=True);rows=[];files=[];deferred=[]
 for root in (B,P):
  for p in sorted(x for x in root.rglob('*') if x.is_file() and '__pycache__' not in x.parts):
   if p.suffix=='.partial':deferred.append(str(p));continue
   raw=p.read_bytes();digest=hashlib.sha256(raw).hexdigest();row=dict(source_path=str(p.resolve()),bytes=len(raw),sha256=digest)
   if digest in prior:
    ref=prior[digest];assert H(REPO/ref['Git_path'])==ref['archived_sha256'];row.update(capture='same_SHA_prior_or_current_Git_reference',Git_path=ref['Git_path'],archived_sha256=ref['archived_sha256'])
   elif p.suffix.lower() in ('.pt','.pth','.npz','.npy','.usd','.usda','.usdc','.zip','.tar','.gz','.mp4','.dmp','.png','.jpg','.stl','.obj','.bin','.dll','.so'):
    row.update(capture='large_actual_path_size_SHA_index_only',original_retained=True)
   else:
    try:decoded=raw.decode('utf8');encoding='UTF8'
    except UnicodeDecodeError:decoded=raw.decode('utf8',errors='backslashreplace');encoding='non_UTF8_original_full_bytes_preserved'
    clean,n=redact(decoded);assert n==0,'Credential redaction required';dst=DEST/root.name/p.relative_to(root);dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(raw);rel=dst.relative_to(REPO).as_posix();files.append(rel);row.update(capture='complete_exact_bytes',source_encoding=encoding,Git_path=rel,archived_sha256=H(dst));prior[digest]=row
   rows.append(row)
 index=DEST/'REPORT_CAPTURE_INDEX.json';index.write_text(json.dumps(dict(epoch=time.time(),entries=rows,deferred=deferred,all_saved_sources_errors_CPU_and_monitor_receipts=True,large_artifacts_index_only=True,future_saved_reports_need_ordinary_supplement=True),indent=2),encoding='utf8');files.append(index.relative_to(REPO).as_posix())
 rec=importlib.import_module('record_experiment');rec.git=git;sys.argv=['record_experiment.py','--id',ID,'--title',TITLE,'--kind','training','--note-file',str(NOTE),'--files',*files,'--validation','Actual Pfinal24 complete CPU/cost/out;newd723 native180 allrowCPU;newH1finiteGO first645160 fullCPU;human4090parallel evaluation newLinuxbackend/native120 allrowCPU;full1500 actual report status;strictguards and oldfalse retained.','--push'];rec.main()
 head=git('rev-parse','HEAD');obj=git('rev-parse',TAG);verifier=prev.prev.prev.prev.g.n.m.cap.a;verifier.gitio.g=git;verifier.verify(rows,tags,head,TAG,obj)
 print(json.dumps(dict(commit=head,tag=TAG,object=obj,actual_remote_main_tag_peel_all1372_old_objects_and_tracked_SHA_verified=True,total_tags=1373,source_entries=len(rows),capture_files=len(files),deferred=deferred)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('LINUX4090_PARALLEL_UNIQUE_GIT_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),if_commit_exists_continue_existing_objects_only_no_repeat_record_tag_commit_or_GPU=True),f,indent=2)
  raise
