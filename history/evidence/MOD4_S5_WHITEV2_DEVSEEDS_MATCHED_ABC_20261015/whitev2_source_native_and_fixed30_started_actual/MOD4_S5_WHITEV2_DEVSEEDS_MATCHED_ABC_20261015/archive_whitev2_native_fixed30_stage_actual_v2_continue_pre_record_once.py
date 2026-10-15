"""Unique registered-white_v2 evaluation stage; no GPU or oldonce invocation."""
from pathlib import Path
import hashlib,importlib,json,subprocess,sys,time,traceback
from datetime import datetime,timezone,timedelta
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';REPO=W/'polar-rl-train';N=W/'MOD4_S5_DEVSEED03_WV3_MATCHED_ABC_20261015'
sys.path.insert(0,str(W/'MOD4_4090_WINDOWS_REPAIR_20261013'));import append_large_install_evidence_import_reviewed_git as cap
ID='s5-two-devseeds-reviewed-whitev2-frozen-abc-started';DEST=REPO/'history/evidence'/D.name/'whitev2_source_native_and_fixed30_started_actual';H=cap.sha_file
def g(*args):
 p=subprocess.run(['git','-c','http.sslBackend=schannel','-c','http.version=HTTP/1.1','-C',str(REPO),*args],capture_output=True,text=True,encoding='utf8',timeout=120);assert p.returncode==0,p.stderr;return p.stdout.strip()
cap.g=g;cap.a.gitio.g=g
def save(n,v):
 p=R/n;assert not p.exists();p.write_text(json.dumps(v,indent=2),encoding='utf8')

NOTE='Approved master812a4b/004005/RM003 fixed. White_v3 seed20261003 actual15 scopes (6native+9full), nine fullinitial pairs and source/data/actualEXIT0-parentchildout-msvcrtfree completed; coordinator24348 actualCIMabsent androotactualhandoff. Unique15parent2010.3804142475128s frozen0PPO noledger. Secondseed flaterrors -1.5 A.0754636675/B.0220948271/C.0226360038; +1.5 A.0591100082/B.0507649705/C.0590341538. Pure+4pi A7/8 B/C8/8, -4pi A0/8 B/C8/8, ordinary0. WorldA62 (20,49failed), B64, C62 (20,40failed). Ccross.0571814/.0514259 failoriginal.05; strictfalse andallvalidprefix unchanged. Bothdevseeds worldA125/128 B128/128 C126/128 descriptiveonly, notnewgraduationline/statisticalsignificance/globalarchitecturewinner. Cworld2069switches, E0/W35[16148,115852], failed20/40 W35selections1387/1398 outsideitsregisterednecessarycommandcondition becauseyaw2; offline observedresponse, notinferenceoracle oruniquephysicalcause. RuleB reference/fallback forobservedcells, C frozencontinuesremainingfairconditions; noadditionalgatePPO. SingleW35 highspeed stress notlow-speedterrainregistryqualification ormatchedmixedancestrycost. Wholeoriginalstate/params/recipesassignment/RNGqueues/loadedDLL exactpair andwholeCPU tails/cost/jumps/latency actual; originalhardware/source-onlyPlane/missingEXITNATURAL boundaries retained.\n\nPreviouscomplete15ordinarycommit1877c052ae41c667e5b65a9ec799d4178430f05e after5ea wascommittedonce. OpenSSLpushTLSunexpectedEOF failed; V1oldrefshelper wronglyrequiredunpublishedHEAD==remotemain andfailedbeforepush, V2rawrefsreadagainTLSfailedbeforepush. Allsources/errorreports kept. IndependentV3 command-localSchannel (certificateverification kept/noglobalconfig) readsrawremote/localall1345tag object+peeled map inonebatch, pushesexistingHEAD only, actualremote main/all1345oldtags/tracked1882sources verified. No commit/tag/record repeated; noGittask touchedGPU/runtime/budget. Thisnewstage appends previousNmetadataerrors/source/recoveryreceipt only; original15rawalreadyin1877 index not recollected/rehashed forduplicateGit.\n\nNewnamespace MOD4_S5_WHITEV2_DEVSEEDS_MATCHED_ABC_20261015 freezesexactE0b109/W35b026/gate02718c source148 (94/102/113floating, gate194tensors), onlyregisteredwhite_v2 profile (.925-1.075mass/inertia and6motor, mu.75-1,20%nominal) atbothapproveddevelopmentseeds02/03. D1-D7/noise/delay/reward/hardware/commands/geometry/clock remainoriginal. ExactMildDR.__call__ AST executedinCPUmocksetter forN80/88 bothseeds pairedwithwhite_v3: formulas/ranges/nominalmask/draworder/nextdrawstatespassed/globalCPU RNGunchanged/noCUDA/optimizer; this isnotGPUreadback. ThreeV8physicalmainloopbytes/allSingle35/PairRouter/controladapterbytesunchanged, workerASTinverse exceptdeclaredprofile/twoseeds/namespace, witness onlyexplicitprofilemetadata. Deploynormal35/actualpreviousclipped6/normalmode/selectedreset/whole6 thenclip6/no averaging/oracle/teacher/hysteresis/liveheading-position correction unchanged. Evaluationmode isconfig notpolicyinput. WholeCPU not20kGPUtrainingrestore, Aonlyactor9/STD, B/C18expert+6gate readbackrequired. NewZIP27621067B SHAf2d5c80e5984fd854953fb8e761fa8ba6d34bb0d890b7222a255156c62addbc2/manifeste9ba5d92c478528434ed3cb7014f66b562b3af86c6d81ffd3231229d009861b4, 40package+476sharedsource/SDKstub-binding actualupload/targetCPUsha.\n\nOwnfirstAflatnative120x80/480callbacks completeclosed/allwholephysical/query1e-6/contactintegralCOMhardware/source9STDinitialfinal/every savedCPUmeans/historyreset passed/ordinary0. CPUvsGPUmean6.103515625e-5 distinctnonbitexact; missingEXIT_NATURAL staysmissing besidewholedata+EXIT0+cleared+actualPIDout-msvcrtfree. Fixed30sequentialnewunusedcases only: eachseed02/03-kindflat/spin/world A-native120+full1500, C-native120 thenBfull1500+Cfull1500, fullsamekindinitial3pairs beforecredit. Each ownphysical/sourceCPU/twohostSHA/EXIT0/PIDout-lockfree before next, fullnativeproof explicitseed/profile/kind/sourcebackend binding. Currentlaterownfulls notfuturepassed, latestCURRENT/COMPLETE/ORIGINAL_ERROR alwayspriority. Coordinator29884/create1792046882.973 argv run_whitev2_ABC_fixed30_case_batch_once.py --execute-root-fixed30-new-whitev2-cases exclusivelyowns210/249 whileactualCIMcreationargv alive. Root/agents localreports+CIMonly, nosecondconnection/observer/coordinator/oldcaseGPU/native/once replay. Rootreclaims afteractualcompleteandCIMabsence. NoextraPPO/budget/canonicalcopy-clear-refund-tail-recharge/extension; firstgate2668.750717s once settled. LaptopGPUpaused/Linux4090repairtrainingauthorized/3060evalonly, allancestors/f516protected, nohardwareSDKdriver mutation/kill/delete/otherAI-WASDGUI.\n\nNominalnotGPUdispatched: sourceconfigure returnsno_mild_dr butexistingfactorparams/private_rng/chassis_pd_audit demandit; nominaluniformCOMaudit mustrespectunchangedD7COMpressure. Independentreadonlymetadata/audit API compatibility andstrictD0nominal-vsD1D7 scope withnegatives/native/source/resource required, nofakeRNG/audittree orlowerCOMthreshold. CombinationDR/real within-episode tasktransitions/matchedsingleancestry/hardware remainfuturegaps. HumanaskedplanpositionandETA: answeredcurrentS5faircontrol, lowstairsfirstadmission/trialestimated12-24hplanningconditionalgeometry/contact/reset/source/resource/budget; notnewlearning/budgetgrant. JumpairborneE5/S8 laterseparate executableplan/reset/landing approval andnoreliabledate. Do notmisinterpretquestionasS8launchpermission. Noarbitrary27/27or90/95/100gates, limitedpracticalcloseout allowed, notallS3/S5/50/70qualified.\n\nAllsavedsource/success/failure/false/readers/lookupmisses/TLS/schema/cost/rawindexes/workorders/humanplanningnote/monitor/Gitreceipt captured. Newrealstageoneannotatedtrial; laterordinarysupplement, pushfailsresumeexistingobjects only. Bigoriginals indexedpath-sizeSHA, credentials excluded, incompletedatasets deferred, Gitnotruntime dependency. Sameactivehourlymod4-10/target unchanged, nativeupdateUTF8verified, healthyunchanged quiet, meaningfulresult/failure/actiononlynotify. Noadditionalmonitor orautomaticbudget. Lateractualremote tools determinearchive state, notthisnote.\n'
def capture_saved_completed_and_metadata(dest):
 prior=cap.a.prior_index();sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
 allowed=set()
 for p in list(R.glob('*_S5_SINGLE_CONTROL_CPU_ADMITTED.json'))+list(R.glob('*_S4_ROUTING_CPU_ADMITTED.json')):
  v=json.loads(p.read_bytes());q=R/(v['case']+'_ORIGINAL_PHYSICAL_CPU_REVIEW.json')
  if v['passed'] and q.exists() and json.loads(q.read_bytes())['result']['data']['complete_data_contract']:allowed.add(v['case'])
 assert 's5_wv2_s20261002_single_eval_flat_120_v1' in allowed and not dest.exists();dest.mkdir(parents=True)
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
def capture_previous_scope_metadata_only(dest):
 prior=cap.a.prior_index();sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
 assert not dest.exists();dest.mkdir(parents=True);rows=[];files=[]
 paths=sorted(set([*N.glob('*.py'),*N.glob('*.txt'),*(p for p in (N/'reports').rglob('*') if p.is_file())]))
 for p in paths:
  if p.suffix=='.partial':continue
  raw=p.read_bytes();sha=hashlib.sha256(raw).hexdigest();row=dict(source_path=str(p.resolve()),bytes=len(raw),sha256=sha)
  if sha in prior:
   old=prior[sha];assert H(REPO/old['Git_path'])==old['archived_sha256'];row.update(capture='same_SHA_existing_Git_reference',Git_path=old['Git_path'],archived_sha256=old['archived_sha256'])
  elif len(raw)>8000000:row.update(capture='large_actual_path_size_SHA_index_only',original_retained=True)
  else:
   try:txt=raw.decode('utf8')
   except UnicodeDecodeError:txt=raw.decode('latin1')
   clean,k=redact(txt);b=clean.encode('utf8') if k else raw;out=dest/N.name/p.relative_to(N);out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(b);name=out.relative_to(REPO).as_posix();files.append(name);row.update(capture='redacted_full' if k else 'complete_exact_bytes',Git_path=name,archived_sha256=hashlib.sha256(b).hexdigest(),redactions=k)
  rows.append(row)
 p=dest/'REPORT_CAPTURE_INDEX.json';p.write_text(json.dumps(dict(epoch=time.time(),entries=rows,metadata_and_original_TLS_reader_failures_and_own_resume_receipt_included=True,already_archived_actual15raw_not_rehashed_or_recollected=True),indent=2),encoding='utf8');files.append(p.relative_to(REPO).as_posix());return rows,files

def main():
 assert g('rev-parse','HEAD')=='1877c052ae41c667e5b65a9ec799d4178430f05e' and not g('status','--porcelain') and not g('tag','--list','*'+ID) and not DEST.exists()
 for name,key in [('WHITEV2_ABC_UPLOAD_TARGET_CPU_ACTUAL.json','actual_targetCPU'),('WHITEV2_FIXED30_MONITOR_TOML_UTF8_ACTUAL_VERIFIED.json','passed')]:assert json.loads((R/name).read_bytes())[key]
 assert json.loads((N/'reports/COMPLETE15_EXISTING_ORDINARY_PUSH_RESUMED_REMOTE_V3_ACTUAL.json').read_bytes())['actual_remote_main_all1345_oldtags_and_trackedSHA_verified']
 assert json.loads((R/'s5_wv2_s20261002_single_eval_flat_120_v1_S5_SINGLE_CONTROL_CPU_ADMITTED.json').read_bytes())['source9_STD_initial_final_exact']
 local={}
 for line in g('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags/').splitlines():
  values=line.split();local[values[0]]=(values[1],values[2] if len(values)>2 else values[1])
 assert len(local)==1345;old=local
 save('WHITEV2_NATIVE_FIXED30_STAGE_GIT_STARTED_ACTUAL.json',dict(epoch=time.time(),id=ID,previous_main=g('rev-parse','HEAD'),oldtags=len(old),pre_record_tag_map='localrefs bound to previousactualremote1877 proof; no freshremote assertion before firstrecord',no_signal_or_runtime_dependency=True))
 note=D/'ACTUAL_WHITEV2_TWO_DEVSEEDS_FROZEN_ABC_STAGE_NOTE.txt';assert not note.exists();note.write_text(NOTE,encoding='utf8')
 rows,files=capture_saved_completed_and_metadata(DEST);r,f=capture_previous_scope_metadata_only(DEST/'prior_dev03_git_recovery_metadata');rows+=r;files+=f
 sys.path.insert(0,str(REPO/'archive_tools'));rec=importlib.import_module('record_experiment')
 def git(*args):
  if args[:2]==('add','--'):
   p=subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=b''.join(x.encode()+b'\0' for x in args[2:]),capture_output=True,check=True);return p.stdout.decode().strip()
  return g(*args)
 rec.git=git;sys.argv=['record_experiment.py','--id',ID,'--title','Audit both white_v3 development seeds and start registered white_v2 frozen A/B/C comparisons','--kind','evaluation','--note-file',str(note),'--files',*files,'--validation','Actualprevious15 closed/9strictinitialpairs/2seedtailcost/sourceCPU allcomplete; ruleworld128/128 vslearnedgate126/128, originalfalse/fullprefix retained. Existing1877push resumed withSchannel certificateverification, all1345oldtags/tracked1882sources actualverified, TLSandreaderfailures appended. Originalwhite_v2sampler AST CPU N80/88 twoseeds formulas/ranges/draworder/globalRNG passed, mocknotGPU. Threephysicalmainloops/controladapters exact, worker/witnessASTinverse onlydeclaredprofile/seed/namespace. NewZIPf2d5c80/manifeste9ba5d9/40+476actualtargetCPU SHA. Ownwv2Aflatnative120/480 wholephysical/source9/std/allrowCPU/EXIT0/PIDout/sharedlockfree passed, laterfulls pendingactual. Fixed30owner29884 actualCIMargv/script source bound, oldscopes notGPUreplayed/noextraPPO/canonicalchange. SamehourlymonitorUTF8 verified; nominal API gap notlaunched, stairs ETAplanningnotgrant/S8jump notauthorized.','--push'];rec.main()
 tag='trial-'+datetime.now(timezone(timedelta(hours=8))).strftime('%Y%m%d')+'-'+ID;head=g('rev-parse','HEAD');obj=g('rev-parse',tag);cap.a.verify(rows,old,head,tag,obj)
 v=dict(epoch=time.time(),commit=head,tag=tag,tagobject=obj,actual_remote_main_tag_peeled_alloldtags_trackedSHA_verified=True,oldtags_preserved=len(old),saved_sources=len(rows),stage_recorded_once=True,original_TLS_reader_failures_and_recovery_receipt_appended=True,large_originals_retained=True,later_Gitreceipt_and_finite_results_require_ordinary_supplement=True);save('WHITEV2_NATIVE_FIXED30_STAGE_GIT_RECORDED_ACTUAL.json',v);print(json.dumps(v))
if __name__=='__main__':
 try:main()
 except BaseException:save('WHITEV2_STAGE_ARCHIVE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),resume_existing_objects_only_ifrecordexecuted=True,no_record_tag_commit_replay=True));raise
