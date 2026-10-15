"""Unique real S5 A-retention stage; never touches the live finite/GPU owner."""
from pathlib import Path
import hashlib,importlib,json,subprocess,sys,time,traceback
from datetime import datetime,timezone,timedelta
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';REPO=W/'polar-rl-train'
sys.path.insert(0,str(W/'MOD4_4090_WINDOWS_REPAIR_20261013'))
import append_large_install_evidence_import_reviewed_git as cap
ID='s5-single-w35-retention-a-native-and-matched-cells-started'
DEST=REPO/'history/evidence'/D.name/'single_A_native_flat_and_finite_started_actual'
H=cap.sha_file
def save(n,v):
 p=R/n;assert not p.exists();p.write_text(json.dumps(v,indent=2),encoding='utf8')
def capture_saved_completed_and_metadata(dest):
 prior=cap.a.prior_index();sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
 allowed=set()
 for p in R.glob('*_S5_SINGLE_CONTROL_CPU_ADMITTED.json'):
  v=json.loads(p.read_bytes());q=R/(v['case']+'_ORIGINAL_PHYSICAL_CPU_REVIEW.json')
  if v['passed'] and q.exists() and json.loads(q.read_bytes())['result']['data']['complete_data_contract']:allowed.add(v['case'])
 assert 's5_single_W35_flat_120_v1' in allowed and not dest.exists();dest.mkdir(parents=True)
 paths=sorted(p for p in D.rglob('*') if p.is_file() and '__pycache__' not in p.parts);rows=[];files=[];deferred=[]
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
 assert not cap.g('status','--porcelain') and not cap.g('tag','--list','*'+ID) and not DEST.exists()
 for n,k in [('S5_SINGLE_A_UPLOAD_TARGET_CPU_ACTUAL.json','actual_targetCPU'),('S5_SINGLE_A_FIXED_SIX_MONITOR_TOML_UTF8_ACTUAL_VERIFIED.json','passed')]:assert json.loads((R/n).read_bytes())[k]
 assert json.loads((R/'s5_single_W35_flat_120_v1_S5_SINGLE_CONTROL_CPU_ADMITTED.json').read_bytes())['source9_STD_initial_final_exact']
 old=cap.a.gitio.refs();save('S5_SINGLE_A_NATIVE_AND_FINITE_STAGE_GIT_STARTED_ACTUAL.json',dict(epoch=time.time(),id=ID,previous_main=cap.g('rev-parse','HEAD'),oldtags=len(old),live_finite_not_signalled_or_blocked=True))
 note=D/'ACTUAL_S5_SINGLE_A_NATIVE_AND_FIXED_SIX_STAGE_NOTE.txt';assert not note.exists();note.write_text('''Fill only missing single-W35 A counterparts of the complete S4 ruleB/gateC original V8 cells.

Approved master812a4b/004005/RM003 unchanged. Existing first S5 original35 matchedcell already actualcomplete: A singleW35, B ruleE0/W35, C gate148 each27/27forwardreverseordinary0, no architecture winner inferred. All original false/validprefix/costs remain. New namespace does not rerun original35 or old B/C cases. One complete originalW35b026/17615538B/102floating/N20k source; only actor9/STD executes, no gate or secondexpert forward. Single35 component bytes identical to admitted first35 singlecell. Actual80/88saved35 all6mean/caching/selectedreset and8badinput CPU math passed without globalCPU RNG advances/CUDA/optimizer. New package a620c943 SHA, manifest9be8a587,30package+476sharedsource/installedSDKstub-binding actually SHA checked on targetCPU. Whole source CPU validation is not20kGPUenvironmentrestore.

Three flat/spin/world physicalmainloops remain originalV8 byteexact. Witness changes only declared singleadapter import and truthful source metadata. Original representedPlane1e-6, contactintegral/COMhardware, allvalidprefix/strictfalse/signedcircle/yawtol remain. Native actorgetter/read-onlyUSD/public110.1source reference is not installedbinarybitexact or directshapeLocal read/calibratedphysicalCOM. No teacher/terrain-envID/heading-position correction, action blending or hiddenRNG exposure change. Same normal35 actualpreviousclipped6/reset semantics. New first flatnative120x80/480callbacks errorfree wholephysical/source9initialfinal/every savedCPUmean reviewed: ordinary0/trunc0, sourceCPUvsGPUmeanmax6.866455078125e-5 separatelynonbitexact, rawSHA75621cbd80d4d296011a912295e28317e4642bbadc39ad4ca0f3594bb00fa881. OriginalEXIT0/PIDout/sharedmsvcrtfree; originalEXIT_NATURAL staysmissing beside independentwholedata+cleared closure. Nativeunique30.011537551879883s frozen0PPO no canonical charge.

Exactly fixedsix newunused cases: eachkind native120 then full1500/6000cb, sequential actualexit/sharedOSlockfree/twohostSHA/wholeCPUsource9/physics before next. Complete newA matches alreadylocal actual B and C firstphysicsrootq30/params/staticrecipes/capturedRNGqueues/loadedDLL before credit. OldB/C data not GPUreplayed or recollected just to rebuildhash. Actual hidden finitecoordinator43924/create2026-10-15T12:20:46.712924+08 argv and scriptSHA bc1b0c0302e4e5ddd9d68981c0f045fd0d11535c357afb475dcbd66c51ce9b0c proved. It exclusively owns sequential210/249 while actualcreationargv alive; root/agents localCIM/reports only. Launcher redirectedhandles/closefds/CREATE_NO_WINDOW, actualreceipt returned immediately. Firstnewflatfull1500 genuinely dispatched after ownnative admission; futurefull/othernative/pairs/qualification never inferred. ActualCURRENT/COMPLETE/ORIGINAL_ERROR and laterCIM override snapshots. No secondcoordinator/watcher/signal/retry or consumedcase replay. Root only reclaims transport after actualfiniteabsence.

All new cases frozen0PPO; no secondgatewindow, budget extension/copy/clearactive/refund/tail or installedSDK-driver mutation. Firstgate148 learning/2668.750717s already once settled; laptopGPU remainspaused/Linux repairtraining authorized/3060evaluationonly. Protected50f51626/26 and allotheroriginalexpert/ancestor/false/cost sources intact. Allfour-domain A/B/C support/cost/switch/latency review still requires future actualcomplete evidence. Not S5 overall, allskill/hardware/50/70 qualification or mathematical optimum. Later seconddevseed/profile/truechanges scope stays separate; heldout not tuning data.

This realnewtarget/deployment/native stage is recorded once with annotatedtrial. Snapshot captures all saved source/metadata reports and only alreadycomplete+CPUadmitted dataset directories; liveSFTP temporary/unadmitted datasets are explicitly deferred, not hashed as complete. All future completed raw/source/errors/CPU comparisons/currentupdates and Gitreceipt require ordinarysupplements; originals retained. BigPT/NPZ/USD/ZIP/rawdump actualpath-size-SHA only, credentials excluded. Git does not block or alter livefinite/GPU/budget. Same mod4-10 ACTIVE hourly target/quiethealthy and exclusiveowner updated through native tool and actualTOML UTF8verified. Pushfailure resumes existingobjects, never repeatsrecord/tag/commit.
''',encoding='utf8')
 rows,files=capture_saved_completed_and_metadata(DEST);sys.path.insert(0,str(REPO/'archive_tools'));rec=importlib.import_module('record_experiment')
 def g(*args):
  if args[:2]==('add','--'):
   x=subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=b''.join(s.encode()+b'\0' for s in args[2:]),check=True,capture_output=True);return x.stdout.decode().strip()
  return cap.g(*args)
 rec.git=g;sys.argv=['record_experiment.py','--id',ID,'--title','Start missing S5 single-policy retention counterparts after own native admission','--kind','evaluation','--note-file',str(note),'--files',*files,'--validation','Complete source102/actor9/std and original80/88saved35 CPU cached-action-reset/negatives; actualtarget30+476source/SDKstub-bindingSHA. Original3mainloopbytes unchanged. Ownnewflatnative120/480 wholephysical/query/contactCOMhardware/source9initialfinal/allrowCPU passed andactualexit/sharedlockfree before newflatfull1500. Actualfinite6 soletransportownerCIM/argv/script bound, allfuturefull3/pairs pending. NoPPO/budget/oldGPUreplay, originalfalse/missingEXIT/source-onlylimits kept, existinghourlymonitorUTF8verified.','--push'];rec.main()
 tag='trial-'+datetime.now(timezone(timedelta(hours=8))).strftime('%Y%m%d')+'-'+ID;head=cap.g('rev-parse','HEAD');obj=cap.g('rev-parse',tag);cap.a.verify(rows,old,head,tag,obj)
 result=dict(epoch=time.time(),commit=head,tag=tag,tagobject=obj,actual_remote_main_tag_peeled_and_oldtags_verified=True,oldtags_preserved=len(old),actual_tracked_SHA_verified=True,saved_sources=len(rows),large_originals_retained=True,stage_capture_native_admitted_finite_full_results_follow_later_actual=True,later_Git_receipt_and_new_results_require_ordinary_supplement=True)
 save('S5_SINGLE_A_NATIVE_AND_FINITE_STAGE_GIT_RECORDED_ACTUAL.json',result);print(json.dumps(result))
if __name__=='__main__':
 try:main()
 except BaseException:
  save('S5_SINGLE_A_NATIVE_STAGE_ARCHIVE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),continue_existingobjects_only_if_record_already_executed=True,no_record_tag_commit_replay=True));raise
