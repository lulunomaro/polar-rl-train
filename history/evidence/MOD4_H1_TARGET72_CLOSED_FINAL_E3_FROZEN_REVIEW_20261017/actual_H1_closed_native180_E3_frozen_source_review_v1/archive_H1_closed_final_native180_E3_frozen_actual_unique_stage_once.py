"""Unique actual source-review/frozen stage. Never repeat record/tag/commit or runtime."""
from pathlib import Path
import os,sys,json,time,hashlib,importlib.util,importlib,traceback
B=Path(__file__).resolve().parent;W=B.parent;R=B/'reports';REPO=W/'polar-rl-train';O=W/'MOD4_H1_CLOSED24_TARGET72_SAME_SCOPE_FINITE_20261017'
BASE='d4c822827080834b114ecd0003f2e80acad927eb';ID='h1-closed24-native180-e3-public03-frozen-source-review';TAG='trial-20261017-'+ID;TITLE='Close target72 H1 final, verify new native180 and review frozen E3 public requests'
DEST=REPO/'history/evidence'/B.name/'actual_H1_closed_native180_E3_frozen_source_review_v1';NOTE=B/'ACTUAL_H1_FINAL_NATIVE_E3_FROZEN_STAGE_NOTE_UTF8.txt';MSG=B/'ACTUAL_ANNOTATED_STAGE_TAG_MESSAGE_UTF8.txt'
sp=importlib.util.spec_from_file_location('existing_O_archive_pure_functions',O/'archive_H1_closed24_target72_new_backend_same_scope_unique_stage_once.py');prev=importlib.util.module_from_spec(sp);sp.loader.exec_module(prev);rawgit=prev.rawgit;H=prev.H
def git(*args):
 if args[:2]==('tag','-a'):
  assert args[2]==TAG and args[3]=='-m' and MSG.read_text('utf8')==args[4];return rawgit('tag','-a',TAG,'-F',str(MSG))
 if args and args[0]=='push':return rawgit('push','--atomic','origin','HEAD:main','refs/tags/'+TAG)
 return rawgit(*args)
def main():
 assert git('rev-parse','HEAD')==BASE and not git('status','--porcelain') and not git('tag','--list',TAG) and not DEST.exists()
 closed=json.loads((R/'TARGET72_H1_COMPLETE_CLOSED_FINAL_FULL_CPU_COST_EXIT_ORIGINAL_HANDOFF_ACTUAL.json').read_bytes());native=json.loads((R/'LATEST_H1_NATIVE180_TWO_COMPLETE_MODELS_SOURCE_EXACT_LOCAL_CPU_V2_ACTUAL.json').read_bytes());assert closed['passed_whole_final_model_local_CPU'] and native['passed_complete_native180_allrow_remote_and_full_model_local_CPU']
 nativeE3=json.loads((R/'E3_CLOSED85_120_ALL_PHYSICAL_PUBLIC03_SOURCE_CPU_ACTUAL.json').read_bytes());assert nativeE3['passed_complete_data_and_source_CPU'];fullpath=R/'E3_CLOSED85_1500_ALL_PHYSICAL_PUBLIC03_SOURCE_CPU_ACTUAL.json';full=json.loads(fullpath.read_bytes()) if fullpath.is_file() else None
 old={}
 for line in git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags/').splitlines():
  s=line.split();old[s[0]]=(s[1],s[2] if len(s)>2 else s[1])
 assert len(old)==1370;prior={}
 for name in (O.name,'MOD4_RECOVERY_CLOSED_FINAL_H1_STORAGE_BOUNDED_HANDOFF_20261017','MOD4_V8_FINALS_E2_FROZEN_REGRESSION_RECOVERY_ONLY_HANDOFF_20261017','MOD4_TWO72_CLOSED_SOURCES_HEALTHY_NEXT_BLOCK_20261017'):
  for p in (REPO/'history/evidence'/name).rglob('REPORT_CAPTURE_INDEX.json'):
   for row in json.loads(p.read_bytes())['entries']:
    if row.get('Git_path'):prior[row['sha256']]=row
 note='''H1 previously ran on72GPU0 under sole original owner741739. Actual complete final24/576controls/11.52Mproductionenvsteps,16643507B SHAfe1709ec470aa4995e0b271947b65135d2e0bd43bec26b28316a451c5f1fa49e,199tensor105float finite; actor9 including learnableSTD and critic8 all17 changed,17Adam644180->644660. Parent/node/allchildren actualout/EXIT0, original canonicalNone and two real originalfcntl plus target private/sharedvalidation locks free. Actual1495.706130027771s charged once <=1800, remaining507853.9604036808 only snapshot. No old first/native/raw downloaded or rehashed for this closure. Learning evidence is not jump qualification.

Only after actual closure, new same-source72GPU0 native-only parent3184603 root /home/lc01/Zonglin Li/zonglin2/tasks/H1n_1710v2 actually target manifest/source/RSL5/SDKmath CPU admitted, source fe1709/Adam644660. Original physical/runtime/lib/assets manifest bytes exact, only exact Adam expectations and native-only parent contract changed. Own native180/720callbacks/all3.6Mpolicy14.4Mphysical independentCPU passed, startup and native complete twohostSHA/local199tensor105float finite/coreactor9STDcritic8/all17Adam644660 literalexact, initialepisode source+1/phaseage0. CPUmean max2.288818359375e-5 not bitexact, originalquery0/impulse4.76837158203125e-7/8witnessgeometry3.4522330050190675e-8/sourceevents0/0/0, prelaunch credit568.9021333076605 is not jump success. Own parent/worker/CPU actualout/EXIT0/privatefcntl released, originalcanonicalNone/two original locks and target private/sharedvalidation realfree. Native-only0PPO0charge/no writer/GO, no automatic paid continuation. Source210 remains21.6GB below25GiB, no extra cleanup or readonlyC writing, no guard reduction. Three4090 compute empty in actual final read, never allthreePPO/100percent claim.

Interruption left original native collector STARTED but no formal completion report; later actualCIM proves absent, not naturalEXIT0 or GPU failure. New missing-only V2 reader failed before SSH on missing G dependency path, source/error retained. Independent V3 fixed pure import only, one source then one72 read returned actual terminal and only two missing complete full PTs; old completePT/raw not re-collected and no native/Task replay. Prepared unexecuted V1 model reader wrongly conflated finalepisode and initialepisode and could include a phase-only PT; preserved unused, actual independent V2 binds exact returned two full PTs and checks startup source+1 only. Task inherited legacyGPU210 and exact_closed_source_updates121 labels stay original in live files/PT; actual new exact_closed_source_owned_updates24/sourceSHA/Adam/manifest execution_backend target72/realUUID16828f91 resource receipts distinguish execution. No live mutation to conceal labels.

E3 actual closed85/Adam657660/SHA8043c7fbcd8abf2690672aa956fcfae0c17c24172fc6baaef0e75e5e44a1c208 frozen source is unchanged. New104 fresh white_v3/seed20260928 legalbank recipe arange%13, eight normal recipe12 and96 rescue roll/pitch±30/60/90, public0/3 vector perenv, rescue300control thennormal/selectednewfallreset. Only actor9STD frozen, no critic/optimizer/gate/20k typedDRrestore. CPU actually executed original source fall placement, q30bank/quaternion/phase0/300/selectedreset plus once/history/clip6/sourceexact0RNG0CUDA. V1 full573file package prepared, V2 explicit DR/pre-reset stable/credited readbacks and104-ray shape extension preserve actor/reset/phase/hardguards; actual query104 plus4missing/badnormal/offset/duplicate negative cases and lossless NaN partialphysical prefix fixture passed. No E2 signed4 admission reused for E3 source.

First3060 attempt rejected exact old desktop PID/create/argv identity before newroot/lease/Task/GPU. Actual readonly current four desktop publisher signatures/process-parent-exeSHA and children inspected, no UI/signals/process changes; new guard exercises its actual equality assertion24tamperedidentity negatives and keeps unknowncompute rejection. CPUfixture V1 attempted parsing indented if/elif fragment standalone and failed IndentationError; original partial transport/source/error retained, V2 extracts actual assertion line only. New unused V3 namespace under D:/MOD4_async_eval/MOD4_H1_TARGET72_CLOSED_FINAL_E3_FROZEN_REVIEW_20261017/E3_CLOSED85_FROZEN_V3 uses sealed V2 payload; actual current resources/MSVCRT/SDK-DLL/source full173tensor96float/actor9STD CPU validated before native120/104env/480callbacks. All raw twohost complete, all saved35/action6/history/phase/contactintegral/torquespeed/COM/query/dualFP64authoredgeometry CPU passed, parent/child/launcher out/MSVCRTfree. Native raw72294156B SHA7ffbd3c2d3bf6b4337b585967577f512866613d655a57e3a71e503d281427d95;268ordinary/0trunc reflects real selectedresets, not self-rescue qualification. GPUfloatgeometry original1e-6false2.7547662829752184e-6 preserved; two independentCPUFP64 reference residual6.940559238444166e-13 uses existingE3 engineeringprotocol, physicalquery1e-6/COM1e-5/mimic.01/closure2mm not relaxed. OriginalidealZ0false28 and missingEXIT_NATURAL retained. Original shape source is not cookedShapeLocal/manifold/binary or physicalhardware proof.

After actual ownnative120 allrowCPU/out/lockfree, new unusedfull1500/6000cb dispatched with same sealed source/payload, original strict failedprefix/no unknown/nonfinite/missingcallbacks guards. Full result at capture is appended below, no prepared/dispatched or model save substituted for skillPASS. Old E2 fixed1093/64,10122/64,1050/64,1121/64 preserved with all descriptive matchinginitial boundaries; E2 paid behavior reviewhold unchanged. E3 paid hold until actual frozen residual/source review. No blind paid-loop continuation, reward/LR/STD/threshold change, H2H3/70/±6-8-10/fullS8/newgate/teacher/hidden truth/livecorrectiveheading/extra force/NCCL/averaging.

Solecanonical1188000s330h/sevenextensions unchanged, no duplicate charge/copycanonical/newledger/clearactive/refund/tail/automaticgrant. NativeCPU/frozen zeroPPO zerocharge, Windows9400.8606925 pending and512unknown separate.20k60928/24/LR1e-4adaptiveKEEPSTD1/35-38-6/.0025x4TGS32/4/100Hz/history5msbin3/D0D7white_v3+noise/rewardhardware maintained.72writes onlyzonglin2, no driver/glibc/profile/SDK/oldenvironment/otherAI mutation, 3060 frozenonly/LaptopGPUpaused. Credentials/HMAC only stdin-memory, oldN temporaryargv exposure remains disclosed. All ancestorsfalse/failedprefix/E0/W35/gate148/f51650mm26/26/CURB/H1old25 preserved;S3/S5 notgraduated/heldoutsnotuned/sourceSDK not binary/cooked/hardwarecalibration/deadline proof. Same existing mod4-10 hourly target only, meaningful results notify, unchangedpending quiet. Future saved reports ordinarysupplement; original uniqueO and all oldonce/record/tag/helpers consumed.

Actual full1500 CPU result at stage capture:\n'''+json.dumps(full,ensure_ascii=False)
 for p,text in ((NOTE,note),(MSG,TITLE+'\n\n'+note)):
  with p.open('x',encoding='utf8',newline='\n') as f:f.write(text)
 sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
 DEST.mkdir(parents=True);rows=[];files=[];deferred=[]
 for p in sorted(x for x in B.rglob('*') if x.is_file() and '__pycache__' not in x.parts):
  if p.suffix=='.partial':deferred.append(str(p));continue
  with p.open('rb') as f:
   st=os.fstat(f.fileno());large=p.suffix.lower() in ('.pt','.pth','.npz','.npy','.usd','.usda','.usdc','.zip','.tar','.gz','.mp4','.dmp') or (st.st_size>8*1024**2 and p.suffix.lower() not in ('.json','.jsonl','.txt','.md','.py','.toml','.log'));h=hashlib.sha256();raw=None
   if large:
    for chunk in iter(lambda:f.read(4194304),b''):h.update(chunk)
   else:raw=f.read();h.update(raw)
   en=os.fstat(f.fileno());assert (st.st_size,st.st_mtime_ns)==(en.st_size,en.st_mtime_ns)
  digest=h.hexdigest();row=dict(source_path=str(p.resolve()),bytes=st.st_size,sha256=digest)
  if digest in prior:
   ref=prior[digest];assert H(REPO/ref['Git_path'])==ref['archived_sha256'];row.update(capture='same_SHA_prior_Git_reference',Git_path=ref['Git_path'],archived_sha256=ref['archived_sha256'])
  elif large:row.update(capture='large_artifact_actual_path_size_SHA_index_only',original_retained=True)
  else:
   try:clean,n=redact(raw.decode('utf8'))
   except UnicodeDecodeError:row.update(capture='binary_actual_path_size_SHA_index_only',original_retained=True);rows.append(row);continue
   data=clean.encode('utf8') if n else raw;dest=DEST/p.relative_to(B);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data);rel=dest.relative_to(REPO).as_posix();files.append(rel);row.update(capture='redacted_full' if n else 'complete_exact_bytes',Git_path=rel,archived_sha256=hashlib.sha256(data).hexdigest(),redactions=n)
  rows.append(row)
 index=DEST/'REPORT_CAPTURE_INDEX.json';index.write_text(json.dumps(dict(epoch=time.time(),entries=rows,deferred=deferred,all_saved_text_reports_full_bytes_even_over8MiB=True,large_model_USD_raw_ZIP_only_actual_path_size_SHA=True,all_actual_success_failure_prepared_unused_CPU_readers_and_receipts_captured=True,future_saved_reports_need_ordinary_append=True),indent=2),encoding='utf8');files.append(index.relative_to(REPO).as_posix())
 rec=importlib.import_module('record_experiment');rec.git=git;sys.argv=['record_experiment.py','--id',ID,'--title',TITLE,'--kind','evaluation','--note-file',str(NOTE),'--files',*files,'--validation','Actual H1final24 fullCPU1495.706130s once/out/locks;native180twofullmodels allrowCPU0PPO;E3public03 native120fullsourceCPU actual104/480 and independent49,920physicalrows,full1500actual report if present;all old false unchanged.','--push'];rec.main();head=git('rev-parse','HEAD');obj=git('rev-parse',TAG);prev.prev.g.n.m.cap.a.gitio.g=git;prev.prev.g.n.m.cap.a.verify(rows,old,head,TAG,obj);print(json.dumps(dict(commit=head,tag=TAG,object=obj,actual_remote_main_tag_peel_all1370_old_objects_tracked_SHA_verified=True,total_tags=1371,source_entries=len(rows),capture_files=len(files),deferred=deferred)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('H1_E3_UNIQUE_GIT_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),if_commit_exists_continue_existing_objects_only_no_rerecord_retag_recommit_or_runtime_replay=True),f,indent=2)
  raise
