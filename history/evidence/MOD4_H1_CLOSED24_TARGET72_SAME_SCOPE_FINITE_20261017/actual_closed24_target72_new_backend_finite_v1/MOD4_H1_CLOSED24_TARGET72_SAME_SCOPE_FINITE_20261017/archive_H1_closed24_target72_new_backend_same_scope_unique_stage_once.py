"""Unique actual new-backend H1 stage plus M closure; never repeat record/tag/commit."""
from pathlib import Path
import os,sys,json,time,hashlib,importlib.util,importlib,traceback
B=Path(__file__).resolve().parent;W=B.parent;R=B/'reports';M=W/'MOD4_RECOVERY_CLOSED_FINAL_H1_STORAGE_BOUNDED_HANDOFF_20261017';REPO=W/'polar-rl-train'
BASE='0506bb2462c1aabec22b264455709cab004dffde';ID='h1-closed24-target72-storage-safe-same-scope-finite-handoff';TAG='trial-20261017-'+ID;TITLE='Continue closed24 H1 on admitted72 GPU0 after storage-safe original handoff'
DEST=REPO/'history/evidence'/B.name/'actual_closed24_target72_new_backend_finite_v1';MSG=B/'ACTUAL_TARGET72_ANNOTATED_TAG_MESSAGE_UTF8.txt';NOTE=B/'H1_CLOSED24_TARGET72_ACTUAL_STAGE_NOTE.txt'
sp=importlib.util.spec_from_file_location('prior_M_actual_Git_pure_functions',M/'archive_recovery85_H1_real_first_native_review_actual_unique_stage_v2_once.py');prev=importlib.util.module_from_spec(sp);sp.loader.exec_module(prev);rawgit=prev.g.git;H=prev.g.H
def git(*args):
 if args[:2]==('tag','-a'):
  assert args[2]==TAG and args[3]=='-m' and MSG.read_text('utf8')==args[4];return rawgit('tag','-a',TAG,'-F',str(MSG))
 if args and args[0]=='push':return rawgit('push','--atomic','origin','HEAD:main','refs/tags/'+TAG)
 return rawgit(*args)
def main():
 assert git('rev-parse','HEAD')==BASE and not git('status','--porcelain') and not git('tag','--list',TAG) and not DEST.exists();closed=json.loads((R/'M_H1_CLOSED24_FULL_MODEL_CPU_RECOVERY_NATIVE_COMPLETE_ORIGINAL_HANDOFF_ACTUAL.json').read_bytes());dispatch=json.loads((R/'H1_TARGET72_NEW_NATIVE_THEN_ORIGINAL_FINITE_PPO_DETACHED_ACTUAL.json').read_bytes());assert closed['H1_full_final_CPU_passed'] and dispatch['H1_72GPU0_new_native180_full_CPU_before_any_GO']
 old={}
 for line in git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags/').splitlines():
  s=line.split();old[s[0]]=(s[1],s[2] if len(s)>2 else s[1])
 assert len(old)==1369;prior={}
 for p in (REPO/'history/evidence'/M.name).rglob('REPORT_CAPTURE_INDEX.json'):
  for row in json.loads(p.read_bytes())['entries']:
   if row.get('Git_path'):prior[row['sha256']]=row
 cp=R/'H1_TARGET72_NATIVE_FIRST_COMPLETE_MODELS_LOCAL_CPU_ACTUAL.json';cpu=json.loads(cp.read_bytes()) if cp.is_file() else None
 note='''Human asked when training resumes. Actual prior H1 model_update24.pt is complete16643251B SHA c5f1f7a6d8eb4a05a2301e116d3c75ce496c61f73f4e0a283dfe6bfb87de5a51,199tensor105float/model-runtime finite, all17Adam643700->644180, actor9 including learnableSTD and critic8 all changed.24updates/576controls11.52Menvsteps is learning evidence, not jump qualification. Source owner734415/all nodes and children actualout/EXIT0, original canonicalNone and both realfcntl free, actual830.87096118927s once settled. M E3 source85 ownnative336 complete14713776B SHA298df263ef0924330c3d28dcd49ed0c92dba4328a261a15889cfdd8fdbbc4826 is twohostSHA/local173tensor96float/coreactor9STDcritic8/17Adam657660 exact and actual independent6.72Mactor26.88Mphysical CPU passed; parent allchildrenwaited/out/privateGPUlock released. This was0PPO0charge and not self-rescue skill qualification. Only missing final/nativecomplete collected, no old completePT/raw rehash or task replay.

Source210 Dfree actual21627129856B about21.6GB is now below unchanged25GiB GPU-start guard, after the preceding real H1 outputs. No further deletion/cleanup, no writing/remounting readonlyWindowsC, no tmpfs or lowering guard. Existing exact189-file human cleanup remains historical, no automatic cleanup extension. To use an already free authorized GPU without blind E2/self-rescue continuation, same approved H1 flat public-request skill moves to72GPU0 UUID16828f91 under new owned shortroot H124_1710b72. This is a fresh backend requiring its own20knative180/720callbacks/3.6Mpolicy14.4Mphysical independentCPU before original paidGO; old210weight/native admission not reused fornewclosed24 weights. No newskill, reward, command, LR, STD, DRdraw, reset, physics, energy, hardware or threshold change.

New source fullclosed24/Adam644180 byteguard preserved all199tensor105float. Two H1 wrappers change only exact sourceAdam643700->644180/reportlabels; original runtime/lib/assets/originalmanifest all byteSHA exact. Actual RSL5 on_policy_runner/PPO and installedSDKmath SHA identical between backends and actually checked on72 before launch. Common only H1 GPU routing UUID210->72GPU0, existing1800cap/max24updates/300headroom/own8GiB saved-stop and original25GiB GPU/RAM/disk admission unchanged. Private-resource selector uses explicit target72 backend rather than keyh1=source assumption, binds72ownedstate/GPU0 lock and real last same-GPU E2closed112 out/EXIT0; actual private/sharedvalidation lock availability/unknowncompute rejection and targetdurable space checked before newdirectory. Original source210 owner remains metadata-only>1GiB/canonicalfs>512MiB, solecanonical1188000/330h/sevenextensions and actual independent H1 interval once; never a second writer/newledger/refund/tail/clearactive or newbudget. Later actualoverrun/false preserved, schedule not guaranteedFINAL.

Actual new owner741739 under /mnt/mod4_linux_durable_20261013/H124_1710b72/owner and targetH1node3181133 under /home/lc01/Zonglin Li/zonglin2/tasks/H124_1710b72 dispatched only after targetfullsourceCPU, oldowner settlement/twofcntl actualhandoff, listenerready+signedtwoholdACK. E2 remains behavioral reviewhold after sourcefixed10122/64->1050->1121, no new E2policy paidworker. E3 remains frozen self-rescue reviewhold before any paidworker, prepared104env public03 components are not3060physicalqualification. GPU0 is temporarily H1 rather than E2;210GPU remains idle for disk,72GPU1 idle after native-only completion; never allthreePPO or100percent claim.

Original Windows localpreparer failed only because fcntl is absent on Windows after preparing staticpayload/closedmodelCPU; source/trace retained and no SSH/GPU occurred. New V2 staticreader mocks only import, forbids flock, consumes preparedfiles and exercises actualmanifestvalidator with six wrongUUID/cap/manifest/key negatives. It is notLinuxOSlock proof; Linux actual checks are independent. No installs or live-code hotpatch. Bounded finitecollector one sourceconnection<=900s metadata polls actualauthenticatedowner, then one72connection only newnative/immutablefirst/startup0 completePTs; actualCIMalive exclusiveallhosttransport, no newmonitor/watcher/5minSSH. Collector return hands transportback, not permanentPID owner. Missingfirst stayspending; complete newfirst needs twohost fullSHA/localalltensorfinite/sourcecorestartup literalexact/all17Adam644180->644200/actor9STDcritic8 actualchanges/sourceepisode+1/phaseage0, never GO/metadata/native substituted forPPO.

All success/failure/unusedreader/source/closure/accounting/CPUvalidation/dispatch/monitor/receipt captured; M unique stage and old once/tasks/native/record/helper remain consumed. Unique record_experiment annotatedtrial exact title+note file-F once, atomic existingobjects push and remote main/tag/peel/all1369oldtagobjects plus trackedSHA. Pushfail continue existingobjects, never rerecord/retag/recommit or runtime replay. Models/PT/NPZ/USD/ZIP indexed only actualpathsizeSHA with originals retained except prior explicit189deletion. Credentials/HMAC onlySSHstdin+childstdin-memory, no cfgargv/log/disk/Git; oldN temporaryargv exposure remains disclosed.72writes onlyzonglin2, sourceowned/mnt, nootherAI/systemSDK/driver/glibc/profile change. All strictquery1e-6/COM1e-5/mimic.01/closure2mm ordinaryselectedreset/nonfiniteunknownmissingcallbacks durable save-stop, sourcephaseV2/8typed/globalnamed/privateCUDA/seven actualstartupmarkers preserved. E0/W35/gate148/f51650mm26/26, heldout61011/12/allancestorsfalse retained. No H2H3/70/fullS8/newgate/NCCL/teacher/futurecontact/liveheadingcorrection/extra force/average. PublicSDKsource not loadedDLL/cookedShapeLocal/manifold/hardwarecalibration/deadline proof. Same existingmod4-10 ACTIVEhourlytarget only, no extra automation orautomaticbudget. Future completeFINAL/cost/out/locks and savedreports ordinarysupplement, not course complete.

Actual full-model CPU evidence at stage capture:
'''+json.dumps(cpu,ensure_ascii=False)
 for p,s in ((NOTE,note),(MSG,TITLE+'\n\n'+note)):
  with p.open('x',encoding='utf8',newline='\n') as f:f.write(s)
 sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
 DEST.mkdir(parents=True);rows=[];files=[];deferred=[]
 for root in (M,B):
  for p in sorted(x for x in root.rglob('*') if x.is_file() and '__pycache__' not in x.parts):
   if p.suffix=='.partial':deferred.append(str(p));continue
   with p.open('rb') as f:
    st=os.fstat(f.fileno());large=st.st_size>8*1024**2 or p.suffix.lower() in ('.pt','.pth','.npz','.npy','.usd','.usda','.usdc','.zip','.tar','.gz','.mp4','.dmp');h=hashlib.sha256();raw=None
    if large:
     for block in iter(lambda:f.read(4194304),b''):h.update(block)
    else:raw=f.read();h.update(raw)
    en=os.fstat(f.fileno());assert (st.st_size,st.st_mtime_ns)==(en.st_size,en.st_mtime_ns)
   sha=h.hexdigest();row=dict(source_path=str(p.resolve()),bytes=st.st_size,sha256=sha)
   if sha in prior:
    ref=prior[sha];assert H(REPO/ref['Git_path'])==ref['archived_sha256'];row.update(capture='same_SHA_original_M_Git_reference',Git_path=ref['Git_path'],archived_sha256=ref['archived_sha256'])
   elif large:row.update(capture='large_artifact_actual_path_size_SHA_index_only',original_retained=True)
   else:
    try:clean,n=redact(raw.decode('utf8'))
    except UnicodeDecodeError:row.update(capture='binary_actual_path_size_SHA_index_only',original_retained=True);rows.append(row);continue
    data=clean.encode('utf8') if n else raw;dest=DEST/root.name/p.relative_to(root);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data);rel=dest.relative_to(REPO).as_posix();files.append(rel);row.update(capture='redacted_full' if n else 'complete_exact_bytes',Git_path=rel,archived_sha256=hashlib.sha256(data).hexdigest(),redactions=n)
   rows.append(row)
 index=DEST/'REPORT_CAPTURE_INDEX.json';index.write_text(json.dumps(dict(epoch=time.time(),entries=rows,deferred=deferred,all_M_followup_and_new_target72_sources_reports_errors_receipts_captured=True,large_originals_retained_except_prior_explicit_L189_deletion=True,future_collection_FINAL_cost_receipts_need_ordinary_supplement=True),indent=2),encoding='utf8');files.append(index.relative_to(REPO).as_posix())
 rec=importlib.import_module('record_experiment');rec.git=git;sys.argv=['record_experiment.py','--id',ID,'--title',TITLE,'--kind','training','--note-file',str(NOTE),'--files',*files,'--validation','Actual H1closed24 fullCPU/cost830.870961/out/locks;E3native336fullCPUcoreexact0PPO;new72H1 complete source/RSL/SDK/native-then-finite chain;no reward or budget change.','--push'];rec.main();head=git('rev-parse','HEAD');obj=git('rev-parse',TAG);prev.g.n.m.cap.a.gitio.g=git;prev.g.n.m.cap.a.verify(rows,old,head,TAG,obj);print(json.dumps(dict(commit=head,tag=TAG,object=obj,actual_remote_main_tag_peel_all1369_old_tag_objects_and_tracked_SHA_verified=True,total_tags=1370,source_entries=len(rows),capture_files=len(files),deferred=deferred)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('H1_TARGET72_UNIQUE_GIT_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),if_commit_exists_continue_existing_objects_only_no_record_tag_recommit_or_runtime_replay=True),f,indent=2)
  raise
