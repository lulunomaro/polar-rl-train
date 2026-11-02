"""Append real first-native-fullsave/CPU-resume/measurement-source evidence.
Reference unchanged phase18 text by original SHA; no model/raw/hardware access.
"""
from pathlib import Path
import json,hashlib,sys,subprocess,datetime
R=Path(__file__).resolve().parent;REPO=Path(r'F:\RMPOLAR-RL\repo-lqr');REL=Path('history/experiments/mod4v1_supermimic_bptt_phase19_delta');D=REPO/REL
sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
import record_experiment
G=lambda *a:subprocess.run(['git','-C',str(REPO),*a],check=True,capture_output=True,text=True,encoding='utf-8').stdout.strip()
H=lambda raw:hashlib.sha256(raw).hexdigest()
assert G('branch','--show-current')=='mod4v1-experts-fulldr-rm70'and not G('status','--porcelain');assert not D.exists()
assert (R/'reports/FIRST_E0_E2_NATIVE_COMPLETE_CHECKPOINT_RECEIPTS_V1.json').exists()
prior_index=REPO/'history/experiments/mod4v1_supermimic_bptt_phase18_sources/SOURCE_INDEX.json';prior=json.loads(prior_index.read_bytes());known={x['source_path']:x for x in prior['rows']if x.get('archive_path')and x.get('source_sha256')}
D.mkdir(parents=True);rows=[];files=[];refs=0
for p in sorted((p for p in R.rglob('*')if p.is_file()),key=str):
 row=dict(source_path=str(p))
 if p.suffix.lower()in('.pt','.pth','.ckpt','.onnx','.safetensors'):row.update(status='model_reference_only_no_stat_or_read',source_sha256=None);rows.append(row);continue
 before=p.stat();row.update(stat_bytes=before.st_size,mtime_ns=before.st_mtime_ns)
 if p.suffix.lower()in('.pyc','.npz','.npy','.usd','.usdc','.zip','.zst','.mp4','.png','.jpg','.jpeg','.stl','.bin')or'__pycache__'in p.parts or before.st_size>50_000_000:row.update(status='external_binary_or_large_metadata_only_no_content_read',source_sha256=None);rows.append(row);continue
 raw=p.read_bytes();after=p.stat();row.update(bytes=len(raw),source_sha256=H(raw),unchanged_size_mtime_during_read=before.st_size==after.st_size and before.st_mtime_ns==after.st_mtime_ns)
 if not row['unchanged_size_mtime_during_read']:row['status']='moving_index_only'
 elif str(p)in known and known[str(p)]['source_sha256']==row['source_sha256']:
  old=known[str(p)];assert (REPO/old['archive_path']).is_file();row.update(status='unchanged_reference_existing_phase18',archive_path=old['archive_path'],archive_sha256=old['archive_sha256'],referenced_commit='8e6160b8747af162b5a486b3f3aa1ad4782223fd');refs+=1
 else:
  try:text=raw.decode('utf-8')
  except UnicodeDecodeError:row['status']='nonUTF8_metadata_index_only'
  else:
   safe,n=redact(text);data=safe.encode('utf-8')if n else raw;dest=D/'delta'/p.relative_to(R);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data);name=dest.relative_to(REPO).as_posix();files.append(name);row.update(status='text_redacted'if n else'complete_new_or_changed_text',redactions=n,archive_path=name,archive_sha256=H(data))
 rows.append(row)
(D/'.gitattributes').write_text('* -text\n',encoding='utf-8');(D/'SOURCE_INDEX.json').write_text(json.dumps(dict(captured_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),prior_phase18_commit='8e6160b8747af162b5a486b3f3aa1ad4782223fd',unchanged_reference_count=refs,rows=rows,not_captured_yet='Files first created/changed after this exact capture are nextappend pending.'),indent=2),encoding='utf-8')
note='''# Phase19 — actual first native full saves, CPU full-resume test, measurement observer source

Goal goal-1c14ef7d-c888-4287-83bf-c008d54545fb revision9 remains active. Human18:48 allowed low-load shared GPUs even with other processes; future-unused-window source8tests and goalchange already in phase18, active owner not hotpatched. Currenttwo4090 original admission naturally completed before old1800wait expired, E0/E2 actually training from18:47:28/29, H1frozen.

## New actual native checkpoint evidence
Published originalproducer receipts at1793617116.129/1793617164.774 eachverifiedH16BPTT400/iter500, WM2000/aux2000/critic1600. OriginalN1024freshDR/noPPOoptresume. E0 ownnewcomplete247769249B SHAacab98ca2e58bb262fbb358a06ac373ed613fa68ac530fefe1861663e31de33f; E2 247769185B SHAcb5f227c493c51eaa655cd96886cfc7a3b867c93dbdcca41e8688a60a01809a4. Newmodels/critic/aux/4optimizer/replay/RNG/history fullsaved; teacher sourceeachonephysicalopen/hash/decode and frozen unchanged. Temporal future->a0 and WMpath future->s1->a0 finite/nonzero, actualopt/parameterprobe changed. First-save reader onlyproducerJSON, no modelstat/open/hash, no SDK/C/GPUoperations; separatepurpose from maincounter/close watcher. Reader RC0, windows stillactive/notclosed/notsettled yet. Each400 saved is not3000/skill80or90/realfieldgraduation.

## New CPU-only software complete-resume evidence
Synthetic FakeEnv/FakeTeacher, noSDK/GPU/selectedPT/C/GO. Natural train2 verified synthetic steps, fullweights_only ownnewpayloadsave/load includingNumPy RNG. Ten checks pass: explicitreset declaration required, allfourmodels/norms/allfouroptimizers restore, Python/NumPy/TorchCPU RNG exact, counters/iteration/collectfraction/pendingtransaction/replay restore, declaredstream_cut+freshobs_hist, continues2->3 notzero, CUDAuninitialized. Nativeexpertcount0fromsoftwaretest; actualnative physicalresume is not claimed tested. Coreload supports allow_environment_reset=True; futureworker interface for continuation stillrequiresnewunusedversion if anyfinitewindowendsbelow3000.

## E2/W35 measurement source
New independent source_measurement_review_v1 observer/UID ledger and native_validation_observer_entry, noautomatic hookinstall/environment calls, originalpredicate thresholds/conditionaldenominators preserved, moving/standing separate, originalgetter/mixedphase left intact fordiagnostics. StdlibCPU synthetic43pass, notnative validation. root_pos_w aliases root_link_pos_w actorframe inavailablebasesource; root_state_w linkpose+COMvelocity, actualbackend/cache liveverification stillnull. Source/provenance missingfacts staynull, nox8 orspeedproxy/UIDcohortguess. Source-only finalsealfiles are included onlyifactuallycreatedbeforecapture; lateonesnextappend. No activeworker/core/phase18source patched.

Priorphase18 commit8e6160b8747af162b5a486b3f3aa1ad4782223fd/tagobject5d36089e5be76616b4c2dbae12014467f6769b28 remotelyexactverified, mainreadonly1044a69... independentlyadvances. Thisdelta indexes unchangedsource SHA tocommittedpriorpaths ratherthan duplicating them, savesallneworchangedreports/code/failure/handoff pointintime. No model/oldraw rereads orphysicalonce replays forGit. Only feature+uniqueannotatedtrial, remoteverification mustfollowpush. Goalquantityandallroles>=90unmet, leaveactive; E0/S50originalbinarypredicategaps notinvented.
'''
(D/'NOTE.md').write_text(note,encoding='utf-8');files +=[(REL/n).as_posix()for n in('.gitattributes','SOURCE_INDEX.json','NOTE.md')]
original_git=record_experiment.git
def exact_short_git(*a):
 if len(a)>=2 and a[:2]==('add','--'):
  dest=a[2];selected=set(a[3:]);assert selected==set(files)and all(Path(x).is_relative_to(REL)for x in selected)
  v=original_git('add','--',dest,REL.as_posix());assert set(original_git('diff','--cached','--name-only').splitlines())==selected|{dest};return v
 return original_git(*a)
record_experiment.git=exact_short_git
sys.argv=['record_experiment.py','--id','mod4v1-supermimic-native-firstsave-measurement-phase19','--title','Record actual native H16 BPTT first complete saves and full-resume software evidence','--kind','training','--note-file',str(D/'NOTE.md'),'--validation','E0E2actualnativeeach400verifiedH16policyBPTT-fullnewcheckpointproducerreceipts-4optsreplayRNGhist-teacherfrozen;CPUsyntheticfullresume10checks-nativecount0;measurementobserver43synthetic-notruntimegapfix;phase18remoteexact-unchangedSHArefs;Goalrev9active-not3000or90percent;noactivehotpatch/PTrawSDKrerunforGit','--files',*files]
record_experiment.main();print(json.dumps(dict(commit=G('rev-parse','HEAD'),branch=G('branch','--show-current'),entries=len(rows),unchanged_references=refs,new_text_files=len(files),status=G('status','--porcelain')),indent=2))
