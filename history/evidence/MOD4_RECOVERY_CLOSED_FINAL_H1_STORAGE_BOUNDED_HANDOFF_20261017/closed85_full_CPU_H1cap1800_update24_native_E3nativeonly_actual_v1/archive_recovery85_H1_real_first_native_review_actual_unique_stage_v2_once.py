"""One unique actual new closed-source/storage-bounded/native-review stage; never rerun."""
from pathlib import Path
import os,sys,time,json,hashlib,importlib.util,importlib,traceback
B=Path(__file__).resolve().parent;W=B.parent;R=B/'reports';REPO=W/'polar-rl-train'
BASE='7402ceb0cbe0f5de7f7424ac9690a95c655f4785';ID='recovery85-final-h1-storage-bounded-native-review';TAG='trial-20261017-'+ID
TITLE='Close recovery85 and restore verified H1 PPO within storage limits'
DEST=REPO/'history/evidence'/B.name/'closed85_full_CPU_H1cap1800_update24_native_E3nativeonly_actual_v1'
sp=importlib.util.spec_from_file_location('previous_G_git_pure_functions_only',W/'MOD4_HOST72_THREE_GPU_SINGLE_PPO_7H_20261016/archive_three_gpu_single_PPO_seven_hour_stage_once.py');g=importlib.util.module_from_spec(sp);sp.loader.exec_module(g)
MSG=B/'ACTUAL_M_ANNOTATED_TAG_MESSAGE_UTF8.txt';NOTEFILE=B/'RECOVERY85_CLOSED_H1_STORAGE_BOUND_NATIVE_REVIEW_ACTUAL_STAGE_NOTE.txt'
def git(*args):
 if args[:2]==('tag','-a'):
  assert args[2]==TAG and args[3]=='-m' and MSG.read_text('utf8')==args[4];return g.git('tag','-a',TAG,'-F',str(MSG))
 if args and args[0]=='push':return g.git('push','--atomic','origin','HEAD:main','refs/tags/'+TAG)
 return g.git(*args)
def main():
 assert git('rev-parse','HEAD')==BASE and not git('status','--porcelain') and not DEST.exists() and not git('tag','--list',TAG)
 closed=json.loads((R/'RECOVERY_CLOSED85_COMPLETE_MODEL_CPU_COST_EXIT_ORIGINAL_HANDOFF_ACTUAL.json').read_bytes());assert closed['passed_full_model_CPU'];dispatch=json.loads((R/'H1_BOUNDED_NEW_NATIVE_AND_RECOVERY85_NATIVE_ONLY_CHAIN_DETACHED_ACTUAL.json').read_bytes());assert dispatch['recovery_native_only_zero_GO_PPO_charge'];assert (R/'H1_NEW_NATIVE_FIRST_AND_RECOVERY85_NATIVE_ONLY_COMPLETE_OR_PENDING_BOUND_COLLECTION_ACTUAL.json').is_file()
 old={}
 for line in git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags/').splitlines():
  r=line.split();old[r[0]]=(r[1],r[2] if len(r)>2 else r[1])
 assert len(old)==1368
 proofpath=R/'NEW_H1_FIRST_AND_RECOVERY85_NATIVE_ONLY_COMPLETE_MODELS_LOCAL_CPU_V3_ACTUAL.json';cpu=json.loads(proofpath.read_bytes()) if proofpath.is_file() else None
 note='''Continue the existing approved master after actual recovery final85/full-source freeze and human-authorized storage reclaim. Prior owner718138 and all children truly out/EXIT0, original canonicalNone and two realfcntl free, actual3338.325126171112s once settled, remaining510180.53749489784s only that snapshot. Complete14715029B finalSHA8043c7fbcd8abf2690672aa956fcfae0c17c24172fc6baaef0e75e5e44a1c208 is twohostSHA/local173tensor96float CPU finite, all17Adam655960->657660 and actor9inclSTD/critic8 all changed.85updates/40.8M productionenvsteps is not self-rescue qualification. No old first/native/raw rehash or task replay for collection.

Windows D actual36.9644GB free after the distinct already-recorded189-file cleanup exceeds original25GiB but not the prior H1 whole-hour49.5GB output. New H1 grant is finite1800s including productionloadlearnsaveSDKclosechildwait/ownerterminal, headroom300, maximum24 completed PPO updates, own completed-update saved-stop if Dfree<8GiB. Engineering estimate33.715GB includes conservative.6GiB/update,native8GiB,package/model1GiB,reserve8GiB, below actual free; estimate is not a guarantee. Original25GiB/GPU/RAM guards remain. Source fullH1closed121 SHA3f7feb09c0034d0d902526c2f03a36e84db37d3d93b68b380a2ed844eb063a75/Adam643700/199tensor105float must pass its own new20knative180/720 and independent3.6Mpolicy14.4Mphysical CPU before its own actual GO. H1 common cap only3600->1800, production wrapper only new cap24/storage own saved-stop; rewards, public requests, commands, DRdraws, physics, hardware, STD and original24controlupdate/PPO parameters unchanged. Actual source/target manifests/AST/full sourcefinite/installedRSL5runner-PPO/SDKmathSHA passed before detachedowner734415/H1node734424 under new owned short roots T3_1710v10hr. Post-listener fresh identity and signed ACK precede node registration. Never hotpatch old code or extend old grants.

Latest recovery source85 goes only to its own newnative336/fullCPU finite parent3179169 on host72, no production learning GO or canonical charge. Native-only parent runs actual original worker/coreCPU, waits children/releases own privateGPUfcntl, finite7200s ownprefix stop on limit, no signals/other-task changes. Its owner-cohort terminal records the paid admission sender itself, not false native-parent exit; separate unpaid nativeparent identity explicitly retained. E2 paid learning remains behavior-review hold after fixed10122/fixed1050/fixed1121of64; no new E2worker/GO. Source original writer charges only real H1 interval once; same1188000s/330h/sevenextensions, no refund/tail/clearactive/newledger/newbudget. Native-only work is0PPO0charge. No all-three-PPO/sustained100percent or physical-skill PASS claim from dispatch, metadata or future schedule.

Actual new local signedHTTP ownerloop with mockfcntl proves only H1 canGO1800, two holds zeroGOzerocharge, old3600/wrongnative-source cases rejected, actual1801>1800 staysfalse/no refund. Actual native-parent mockflow1positive2negative retains failedGPU/CPU states and waits/releases own children/lock; fixtures are not GPU/SDK/Linux proof. Complete immutable readerV1 unexecuted retained; independentV2 separately reports native admission versus first missing, no false native-to-PPO promotion. Frozen E3 source85 actor9STD/public03 components prepared onCPU: two once ticks, whole6clip/actualprevious6/selectedreset,14negative source/mode/shape/STD/nonfinite/tick tests,RNGunchanged0CUDA0optimizer. Proposed104env13legalposes/public3-300-normal only components/recipe, not a complete3060package/native/full or self-rescue score. Original E2 pinned projection math ideal fullcycle±4x4directions yieldsV.5 with2Vcos/bodyvy0; halving factor would.25, not robot closedloop or actual live rewardmanager cause proof. No reward/LR/STD/threshold edits.

All local missing inherited script/path guesses are retained as lookup errors, not GPU faults; actual H1 payload lives F/payload_v3/h1, not K/h1. All new source/model/cost/CPU mocks/admission/dispatch/errors/components/workorder/monitor/app receipt and finitecollector snapshot are captured. Collector is one sourceconnection<=600s metadata-only polling, then only missing new immutable/native completePT, then one host72 connection, no repeated oldraw/PT hash; actualCIMalive exclusive transport only, not an extra permanent monitor. Remote native/CPU/finite savedexit independent of laptop/heartbeat. Missing first or CPU is pending, never mislabeled failure or PASS.

Same existing mod4-10 ACTIVE/hourly/target only; no newmonitor/watchers/budget. Original K/L/stages/trials/once untouched, exact189 authorized cleanup never replayed and old raw indexes are historical. All future saved reports ordinarysupplement. New unique record_experiment annotatedtag exact title+note file-F once, remote main/tag/peel/all1368oldtagobjects and trackedSHA verified. Pushfail continues existingobjects only, no rerecord/retag/recommit/runtime retry. Credentials/HMAC only SSHstdin+childstdin-memory, no cfgargv/log/disk/Git; old N temporaryargv exposure remains disclosed.72 newwrites onlyzonglin2, sourceowned/mnt; no deletes except prior exact authorizedLstage,no driverglibc/profile/installedSDK/oldenv/otherAI change. Protect all ancestorfalse/failedprefix/E0/W35/gate148/f51650mm26of26/heldout61011-12. No H2H3/70/fullS8/newgate/scopeexpansion, no teacher/futurecontact/liveheadingcorrection/extraforce/weightaverage. query1e-6/COM1e-5/mimic.01/closure2mm selectedreset and unknown/nonfinite/missingcallback durable save-stop unchanged. Public source is not loadedDLL/cookedShapeLocal/manifold/hardware-calibration/deadline proof.

Actual complete collection/local model CPU status at stage capture:
'''+json.dumps(dict(local_model_CPU=cpu,prior_final_SHA=closed['complete_final']['SHA'],new_dispatch_epoch=dispatch['epoch']),ensure_ascii=False)
 with NOTEFILE.open('x',encoding='utf8',newline='\n') as f:f.write(note)
 with MSG.open('x',encoding='utf8',newline='\n') as f:f.write(TITLE+'\n\n'+note)
 sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
 DEST.mkdir(parents=True);rows=[];files=[];deferred=[]
 for p in sorted(x for x in B.rglob('*') if x.is_file() and '__pycache__' not in x.parts):
  if p.suffix=='.partial':deferred.append(str(p));continue
  with p.open('rb') as f:
   before=os.fstat(f.fileno());large=before.st_size>8*1024*1024 or p.suffix.lower() in ('.pt','.pth','.npz','.npy','.usd','.usda','.usdc','.zip','.gz','.tar','.mp4','.dmp')
   if large:
    h=hashlib.sha256()
    for block in iter(lambda:f.read(4*1024*1024),b''):h.update(block)
    sha=h.hexdigest();raw=None
   else:raw=f.read();sha=hashlib.sha256(raw).hexdigest()
   after=os.fstat(f.fileno());assert (before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns)
  row=dict(source_path=str(p.resolve()),bytes=before.st_size,sha256=sha)
  if large:row.update(capture='large_artifact_actual_path_size_SHA_index_only',original_retained=True)
  else:
   try:clean,n=redact(raw.decode('utf8'))
   except UnicodeDecodeError:row.update(capture='binary_actual_path_size_SHA_index_only',original_retained=True);rows.append(row);continue
   data=clean.encode('utf8') if n else raw;dest=DEST/p.relative_to(B);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data);rel=dest.relative_to(REPO).as_posix();files.append(rel);row.update(capture='redacted_full' if n else 'complete_exact_bytes',Git_path=rel,archived_sha256=hashlib.sha256(data).hexdigest(),redactions=n)
  rows.append(row)
 index=DEST/'REPORT_CAPTURE_INDEX.json';index.write_text(json.dumps(dict(epoch=time.time(),entries=rows,deferred=deferred,all_local_sources_reports_errors_unused_readers_workorders_monitor_receipts_captured=True,large_originals_retained=True,earlier_L_exact189_intentional_remote_deletion_not_claimed_retained=True,later_finite_collection_CPU_FINAL_or_receipts_need_ordinary_supplement=True),indent=2),encoding='utf8');files.append(index.relative_to(REPO).as_posix())
 rec=importlib.import_module('record_experiment');rec.git=git;sys.argv=['record_experiment.py','--id',ID,'--title',TITLE,'--kind','training','--note-file',str(NOTEFILE),'--files',*files,'--validation','Actual closed85 fullCPU/cost3338.325126/out/locks;H1new1800-update24 storage guard and native-only E3 parent CPU;targetSHA/RSL/SDK admission;detached new roots, actual model status only per bound collection;no E2paid learning or new budget.','--push'];rec.main();head=git('rev-parse','HEAD');obj=git('rev-parse',TAG);g.n.m.cap.a.gitio.g=git;g.n.m.cap.a.verify(rows,old,head,TAG,obj)
 print(json.dumps(dict(commit=head,tag=TAG,object=obj,actual_remote_main_tag_peel_all1368_original_tag_objects_peels_tracked_SHA_verified=True,total_tags=1369,source_entries=len(rows),new_capture_files=len(files),deferred=deferred,no_new_budget_or_old_once_replay=True)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('M_UNIQUE_STAGE_GIT_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),if_commit_exists_continue_existingobjects_only_no_record_tag_recommit_or_runtime_replay=True),f,indent=2)
  raise
