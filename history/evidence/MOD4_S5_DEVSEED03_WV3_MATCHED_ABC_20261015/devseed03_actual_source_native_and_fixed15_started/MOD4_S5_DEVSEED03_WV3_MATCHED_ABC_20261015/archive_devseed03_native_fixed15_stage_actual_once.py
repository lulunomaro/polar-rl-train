"""Unique new actual second-development-seed evaluation stage; never rerun."""
from pathlib import Path
import hashlib,importlib,json,subprocess,sys,time,traceback
from datetime import datetime,timezone,timedelta
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';REPO=W/'polar-rl-train'
sys.path.insert(0,str(W/'MOD4_4090_WINDOWS_REPAIR_20261013'))
import append_large_install_evidence_import_reviewed_git as cap
ID='s5-fourdomain-complete-devseed03-abc-native-started'
DEST=REPO/'history/evidence'/D.name/'devseed03_actual_source_native_and_fixed15_started'
H=cap.sha_file
def save(n,v):
 p=R/n;assert not p.exists();p.write_text(json.dumps(v,indent=2),encoding='utf8')

NOTE='Approved master812a4b/004005/RM003 fixed. First S5 seed20261002 white_v3 four-domain existing-policy matched cellset completed. Prior newA six native/full closed+twohostSHA+wholephysical/source9 CPU, exactoldB/C firstphysicsrootq30/allparams/staticrecipesassignment/capturedRNGqueues-loadedDLL pairs. First35mm A/B/C each27/27forwardreverse ordinary0. Flat -1.5 errors A.07586278/B.02264930/C.02222891; +1.5 A.04719228/B.03994397/C.04752084, oldstrictfalse preserved. Pure+4pi each8/8, negativeA0/8ordinary1 vsB/C8/8ordinary0; originalspin/legacyfalse retained. WorldA63/64 (env49 cross.0513491289 vs.05), B/C64/64. Wholevalidprefix/cycles/tails/actiontorquejump/switch/latency/cost reported independently, noarchitecturewinner/statisticalsignificance/allskill/S5overall/hardware/50/70 graduation. SingleW35 highspeedretention is outside its low-speed35terrain registry; no ancestry-cost balance claim. OldAfinite43924 actualCIMabsent andlocalhandoff, oldallcasesconsumed. CompleteoldA/raw review archived ordinary2a88da56b1a289d9539ab151af3575c7359d7edf, no repeatrecord.\n\nNew namespace MOD4_S5_DEVSEED03_WV3_MATCHED_ABC_20261015 explicitly changes only approved developmentseed20261003 whilewhite_v3 held fixed. Heldout20261011/12 untouched. WholeE0b109/94float/W35b026/102float/gate02718c/194tensor113float CPU actualfinite/sourceSHA verified; notGPU20kDR restore. SameSingle35, PairRouter, trainedgate loader andobserveradapter bytes, identicalnormal35/history/reset/whole6/noactionfusion. Evaluationmode is leaseconfig, not inferenceenvID/terraintruth. OnlyA runsactor9 andSTD; B/C runtwooriginalexperts+trainedgate with unchangedSTD/weights. No teacher/liveheadingposition correction/hysteresis. CPUactual80/88saved35 cache/selectedreset/whole6choice allpassed noCPU RNGadvance/CUDA/optimizer. PhysicalthreeV8 mainloops exactoriginalbytes, worker ASTinverse exactlyold exceptseed/namespace/declaredmode/source metadata; witness ASTinverse exact exceptrouteradapter import andaccurate metadata. Originalquery1e-6/contactintegral/COMhardware/DCbounds/allvalidprefix/Plane-source-only/DLLlimits/oldfalse/missingEXIT_NATURAL retained.\n\nNewZIP27621044B SHA99c64b2d1a169f6535ad8a6e806f4a477b32cb65d8cfcc6082be925f6e841a9b/manifest83e11ad09de33910442f86e4d5d7085f1c8c00f636d194981b1c19b6e3e80f27 actualupload/targetCPU40package+476sharedsource+SDKstub-binding passed. Firstownsingleflatnative120x80/480actualcomplete/wholephysical/source9STDinitialfinal/every savedCPUmean/historyreset admitted, ordinary0; CPUvsGPUmeanmax6.866455078125e-5 separatelynonbitexact. EXIT0/actualparentchildout/sharedmsvcrtfree, missingEXITNATURAL preserved besidewholedata+cleared closure. Then ownnewAflatfull1500 actuallydispatched, allfuturefull9 andpairresults notinferred.\n\nExactlyfinite15: perkind flat/spin/world single-native120+single-full1500, pairgate-native120 thenrule-full1500+gate-full1500; allownactualdata/source/physical/EXIT0/lockfree before next and3samekind actualinitialpairs before credit. Pairnativebinds samefrozenpair source/runtime/seed03/profile acrossB/C declaredmode, singles ownnative distinct. AllnewunusedTask/lease/attempt/once names. Actualhiddenfinitecoordinator24348/create1792041319.320 argv run_devseed03_ABC_fixed15_case_batch_once.py --execute-root-fixed15-new-devseed-cases, scriptSHAaaf7c4149a77d4de343e8260c9a619be8050050576957a62df8300c73b7e1d09. OnlyactualCIMcreationargv alive ownssequential210/249; root/agents localreports+CIM only, noextraSSHowner/watchers/retry/signal/oldcaseGPU replay. LatestownCURRENT/error/complete overrides snapshots. Rootreclaims afteractualallcomplete+CIMabsence. NoextraPPO orcanonicalbudget transaction. Single firstS4 learning148/2668.750717s remainsonce settled, nosecondgatewindow. LaptopGPU paused/Linux4090repairtraining authorized/3060evalonly, protected50f516 andallexperts intact.\n\nInitialouterPythonwriter nestedtriplequote SyntaxError occurred atparsebeforeanyfilewrite andfollowingCPU command sawfileabsent. Originalerrorreport retained; independentapply_patch wrotefirstvalidprepare, whichcompleted once, noGPU/network atthisfailure. Alloldfailedsource/schema/reader statuses retained. Newactualstage usesoneunique annotatedtrial; laterfullresults/Gitreceipt/monitor changes ordinarysupplement. CaptureonlyCPUadmittedrawdirectories, pendingSFTP temporarypaths deferred; bigPT/NPZ/USD/ZIP/dump/rawJSON realpath-size-SHA only, originalsretain/credentialsredacted. Gitdoesnotblockruntime. Same mod4-10 ACTIVEhourlytarget updatedby native tool andactualTOMLUTF8verified; healthyunchanged quiet. Onlynewresults/failure/actionnotify. Nextfutureprofiles nominal/white_v2/combinedDR/truetaskswitch stillgaps, nofuturepassed or productionMoEwinner. Pushfail onlyexistingobjects, neverrecord/tag/commit replay.\n'
def capture_saved_completed_and_metadata(dest):
 prior=cap.a.prior_index();sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
 allowed=set()
 for p in list(R.glob('*_S5_SINGLE_CONTROL_CPU_ADMITTED.json'))+list(R.glob('*_S4_ROUTING_CPU_ADMITTED.json')):
  v=json.loads(p.read_bytes());q=R/(v['case']+'_ORIGINAL_PHYSICAL_CPU_REVIEW.json')
  if v['passed'] and q.exists() and json.loads(q.read_bytes())['result']['data']['complete_data_contract']:allowed.add(v['case'])
 assert 's5_dev03_single_eval_flat_120_v1' in allowed and not dest.exists();dest.mkdir(parents=True)
 paths=sorted(p for p in D.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.partial');rows=[];files=[];deferred=[]
 for p in paths:
  relative=p.relative_to(D)
  if relative.parts[0]=='actual_collections' and relative.parts[1] not in allowed:
   deferred.append(str(p));continue
  size=p.stat().st_size;large=p.suffix.lower() in ('.pt','.pth','.npz','.npy','.usd','.zip','.whl','.dmp') or size>8000000
  if large:
   before=p.stat();sha=H(p);after=p.stat();assert (before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns),'Incomplete or mutable artifact during capture';row=dict(source_path=str(p.resolve()),bytes=size,sha256=sha)
  else:
   raw=p.read_bytes();sha=hashlib.sha256(raw).hexdigest();row=dict(source_path=str(p.resolve()),bytes=len(raw),sha256=sha)
  if sha in prior:
   x=prior[sha];assert H(REPO/x['Git_path'])==x['archived_sha256'];row.update(capture='same_SHA_existing_Git_reference',Git_path=x['Git_path'],archived_sha256=x['archived_sha256'])
  elif large:row.update(capture='large_actual_path_size_SHA_index_only',original_retained=True,streaming_hash_without_GB_memory=True)
  else:
   try:txt=raw.decode('utf8');enc='utf8'
   except UnicodeDecodeError:txt=raw.decode('latin1');enc='latin1_byte_preserving'
   clean,n=redact(txt);b=clean.encode('utf8') if n else raw;out=dest/D.name/relative;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(b);name=out.relative_to(REPO).as_posix();files.append(name);row.update(capture='redacted_full' if n else 'complete_exact_bytes',Git_path=name,archived_sha256=hashlib.sha256(b).hexdigest(),encoding=enc,redactions=n)
  rows.append(row)
 out=dest/'REPORT_CAPTURE_INDEX.json';out.write_text(json.dumps(dict(epoch=time.time(),entries=rows,all_saved_source_and_metadata_reports_present_at_snapshot_captured=True,all_complete_data_cases_included=sorted(allowed),incomplete_or_not_CPU_admitted_SFTP_collection_paths_deferred=deferred,later_complete_data_and_new_reports_require_ordinary_supplement=True,large_originals_retained=True,credentials_excluded=True),indent=2),encoding='utf8');files.append(out.relative_to(REPO).as_posix());return rows,files
def main():
 assert cap.g('rev-parse','HEAD')=='2a88da56b1a289d9539ab151af3575c7359d7edf' and not cap.g('status','--porcelain') and not cap.g('tag','--list','*'+ID) and not DEST.exists()
 for name,key in [('DEVSEED03_ABC_UPLOAD_TARGET_CPU_ACTUAL.json','actual_targetCPU'),('DEVSEED03_FIXED15_MONITOR_TOML_UTF8_ACTUAL_VERIFIED.json','passed')]:assert json.loads((R/name).read_bytes())[key]
 source=json.loads((R/'s5_dev03_single_eval_flat_120_v1_S5_SINGLE_CONTROL_CPU_ADMITTED.json').read_bytes());assert source['source9_STD_initial_final_exact'] and source['passed']
 physical=json.loads((R/'s5_dev03_single_eval_flat_120_v1_ORIGINAL_PHYSICAL_CPU_REVIEW.json').read_bytes())['result'];assert physical['data']['complete_data_contract']
 old=cap.a.gitio.refs();save('DEVSEED03_NATIVE_AND_FIXED15_STAGE_GIT_STARTED_ACTUAL.json',dict(epoch=time.time(),id=ID,previous_main=cap.g('rev-parse','HEAD'),oldtags=len(old),live_finite_not_signalled_or_blocked=True))
 note=D/'ACTUAL_DEVSEED03_ABC_NATIVE_AND_FIXED15_STAGE_NOTE.txt';assert not note.exists()
 note.write_text(NOTE,encoding='utf8');rows,files=capture_saved_completed_and_metadata(DEST);sys.path.insert(0,str(REPO/'archive_tools'));rec=importlib.import_module('record_experiment')
 def g(*args):
  if args[:2]==('add','--'):
   p=subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=b''.join(x.encode()+b'\0' for x in args[2:]),capture_output=True,check=True);return p.stdout.decode().strip()
  return cap.g(*args)
 rec.git=g;sys.argv=['record_experiment.py','--id',ID,'--title','Complete first S5 four-domain comparison and start second development-seed frozen A/B/C cells','--kind','evaluation','--note-file',str(note),'--files',*files,'--validation','Priorseed02 allsix A +oldB/C complete exactinitialpairs, full4domain tails/cost actualCPU andformerownerCIMabsent ordinary2a88. Newseed03white_v3 sourceE094/W35102/gate194-113 wholeCPU; actual80/88 shared35 whole6/cache/reset noRNG/CUDA/optimizer. Mainloops byteexact, worker/witness ASTinverse exact exceptdeclaredseed/namespace/evaladapter metadata. Package99c64b2/manifest83e11ad/40+476source/SDKstub-binding actualtargetSHA. OwnAflatnative120/480 wholephysical/source9 initialfinal/allCPUmeans/EXIT0/PIDout/sharedmsvcrtfree admitted; newfull1500 pending. Actualfixed15 owner24348/CIMargv-script bound, noextraPPO/budget/oldcase replay. Source-onlyPlane/missingEXIT/false/fullprefix limits retained. Samehourlymonitor nativeupdate UTF8exact.','--push'];rec.main()
 tag='trial-'+datetime.now(timezone(timedelta(hours=8))).strftime('%Y%m%d')+'-'+ID;head=cap.g('rev-parse','HEAD');obj=cap.g('rev-parse',tag);cap.a.verify(rows,old,head,tag,obj)
 v=dict(epoch=time.time(),commit=head,tag=tag,tagobject=obj,actual_remote_main_tag_peeled_and_alloldtags_verified=True,oldtags_preserved=len(old),actual_tracked_SHA_verified=True,saved_sources=len(rows),new_actual_stage_recorded_once=True,large_originals_retained=True,later_Git_receipt_and_new_finite_results_require_ordinary_supplement=True);save('DEVSEED03_NATIVE_AND_FIXED15_STAGE_GIT_RECORDED_ACTUAL.json',v);print(json.dumps(v))
if __name__=='__main__':
 try:main()
 except BaseException:
  save('DEVSEED03_STAGE_ARCHIVE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),continue_existingobjects_only_if_record_executed=True,no_record_tag_commit_replay=True));raise
