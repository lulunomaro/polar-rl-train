"""Archive new SuperMimic sources/real failures/CPU checks; no hardware actions.
Use original record_experiment and exact-directory staging adapter on feature only.
Large artifacts/models are not opened. Dynamic text freezes at actual capture.
"""
from pathlib import Path
import json,hashlib,subprocess,sys,datetime
R=Path(__file__).resolve().parent;REPO=Path(r'F:\RMPOLAR-RL\repo-lqr');REL=Path('history/experiments/mod4v1_supermimic_bptt_phase18_sources');D=REPO/REL
sys.path.insert(0,str(REPO/'archive_tools'))
from capture_history import redact
import record_experiment
G=lambda *a:subprocess.run(['git','-C',str(REPO),*a],check=True,capture_output=True,text=True,encoding='utf-8').stdout.strip()
H=lambda raw:hashlib.sha256(raw).hexdigest()
assert G('branch','--show-current')=='mod4v1-experts-fulldr-rm70'and not G('status','--porcelain')
assert not D.exists();D.mkdir(parents=True);files=[];rows=[]
roots=[('supermimic',R)]
late=R.parent/'mod4v1_experts_fulldr_rm70_20261101/CURRENT_PROGRESS_v23_FINAL_REMOTE_VERIFIED_GOAL_CLOSE_AUTH_PENDING.md'
candidates=[(scope,p,p.relative_to(root))for scope,root in roots for p in root.rglob('*')if p.is_file()]
if late.is_file():candidates.append(('prior_goal_late_handoff',late,Path(late.name)))
for scope,p,relative in sorted(candidates,key=lambda x:str(x[1])):
 row=dict(source_path=str(p),scope=scope)
 if p.suffix.lower()in('.pt','.pth','.ckpt','.onnx','.safetensors'):
  row.update(status='model_reference_only_no_stat_or_read',source_sha256=None,SHA_note='Actualproducer/catalog identity only; archiver never opens weights');rows.append(row);continue
 before=p.stat();row.update(stat_bytes=before.st_size,mtime_ns=before.st_mtime_ns)
 if p.suffix.lower()in('.pyc','.npz','.npy','.usd','.usdc','.zip','.zst','.mp4','.png','.jpg','.jpeg','.stl','.bin')or'__pycache__'in p.parts or before.st_size>50_000_000:
  row.update(status='external_binary_or_large_artifact_metadata_only',source_sha256=None,SHA_note='Seeactualproducer/sourceindex for knownSHA; no originalbinary content read');rows.append(row);continue
 raw=p.read_bytes();after=p.stat();row.update(bytes=len(raw),source_sha256=H(raw),unchanged_size_mtime_during_read=before.st_size==after.st_size and before.st_mtime_ns==after.st_mtime_ns)
 if not row['unchanged_size_mtime_during_read']:row['status']='moving_index_only'
 else:
  try:text=raw.decode('utf-8')
  except UnicodeDecodeError:row['status']='nonUTF8_metadata_index_only'
  else:
   safe,n=redact(text);data=safe.encode('utf-8')if n else raw;dest=D/scope/relative;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data);rel=dest.relative_to(REPO).as_posix();row.update(status='text_redacted'if n else'complete_text',redactions=n,archive_path=rel,archive_sha256=H(data));files.append(rel)
 rows.append(row)
(D/'.gitattributes').write_text('* -text\n',encoding='utf-8')
(D/'SOURCE_INDEX.json').write_text(json.dumps(dict(captured_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),rows=rows,scope='Point-in-time all new SuperMimic saved source/report/failedpreGO/missingconfigrepair/resourcewait/DRquestion/CPUautograd; prior finalPPO phase17 referenced, no selectedweights/raw/C content reads.'),ensure_ascii=False,indent=2),encoding='utf-8')
note='''# Phase18 — new SuperMimic BPTT sources, original resource wait, synthetic CPU gradient evidence

Direct human request 2026-11-02 17:41: replace previous finite20PPO with actual learned-world-model SuperMimic temporal BPTT, eight nonH1 experts each >=3000 verified policy updates and own original skill >=90% after independent validation;80% intermediate floor. H1 remains frozen. Goal goal-1c14ef7d-c888-4287-83bf-c008d54545fb remains active; no completion claim.

## Algorithm and plant
Existing SuperMimic vendor + sealed ContextRewardLearner real originalenv reward/done/context heads; frozen original35->6 teacher from Registry12 scoped best and zero-init residual/student. New actor/WM/critic/aux optimizers; no PPO optimizer-resume or N80 history projection. Fresh N1024, H16, buffer128,hist10,batch512,lr1e-4,UTD.4,WM-only100 separately counted. Verified policy count requires actualopt posthook/finite nonzero parametergradient/parameterchange plus temporal future->a0 AND future->s1->a0 world-model VJP. This is learned world-model BPTT, not differentiable PhysX, not BC/PPO relabel. Complete ownlearner/4optimizers/replay/RNG/history/counters checkpoints; environment resume explicitly original fresh episode (no bitwise PhysX warmstart).

Original MOD4v1 USD2c421a8e/contractbae3203a,400N/k2000/d3,policy50Hz/feedback100Hz/physics.0025/TGS32,4/closure.01m/mimic.01rad and original existing D0-D7 unchanged. Original two authorityEX/privateGPU EX/finiteSH, fixed originalcanonical b.charge_values, strictreserve86412.86069250107,3900max/3600save/300headroom/1800bounded preGO wait. No new ledger/extension/refund/clamp/foreign lock clear/signals or GPU0 use under another writer.

## Actual attempts and limitations
All eight nonPT source bundles staged in new root MOD4V1_SUPERMIMIC_BPTT8_V1_20261102_181251_1793614371303119100, selected teacher checkpoints untouched by staging. Initial parent1475369 failed importing original helper missing SCHEDULE_PUBLIC config, before OWNER_STARTED/locks/GO/PT/SDK/canonicalwrites. Actual closedstderr preserved. Dedicated source repair proved originalparent gone and allroleGO absent, added only original SCHEDULE_PUBLIC nonledger config, left helper+owner source unchanged; new parent1475630 creation1793614676.22. This is not physical training retry.

At actual18:44:58 exact1475630 live in original preGO wait with partiallocks0/GOallabsent; other original LQR parent1474033 holds authority, GPU1 compute1474057; GPU0 idle does not grant a second canonicalwriter. Snapshot remaining351927.3099360466. Metadata current/exit supersedes this timestamp; active-goal progress not assumed from source readiness. Host GUI restart lost local observer; exact localprocess check found it absent then restored one publishedmetadata observer, not duplicate workers.

CPU software check actualRC0, FakeEnv/FakeTeacher, CUDA invisible/noSDK/sourcePT/GPU/C/GO:3 actual synthetic verified policy optimizer steps,20WM/20aux/3critic. H3 temporalgrad.01789972745/WM-pathgrad.00389033556 finite, parameterprobe delta.00332109234, syntheticteacher unchanged. **These synthetic3 do not count toward any native expert: native count0 at snapshot.** Source28tests and acceptance54synthetic checks are not native skill evidence.

Actual later metadata supersedes waiting snapshot: original1475630 naturally acquired alloriginalleases before1800timeout; E0 worker1477022 and E2 worker1477031 created18:47:28/29 and originalnative N1024/teacher sourceidentity/DR startup succeeded. FIRST_NATIVE_START_AND_SHARED_GPU_REQUEST_V1.json at producer1793616613 records each20 VERIFIED H16 actualnative policyBPTT,480WM/480aux/80critic; temporal+WM-path gradients finite/nonzero and changedparameter probes. Each364realcontrolcalls/372736envtransitions/2912physicscallbacks/728feedbacksamples. These are separate from syntheticCPU3, not90percent skill evidence. No duplicate physicallaunch or restart.

User direct18:48 permits low-load shared GPUs even with otherpersoncompute. Goalrevision9 captures this. Future-only shared_gpu_admission_v1.py and supermimic_original_owner_shared_v2.py prepared;8stdlibfixture/ASTchecks pass, only compute-app exclusion changed, originalfree>15669MiB/util<=30/RAM>64GiB/disk>50GiB/locks/accounting unchanged. Not uploaded/executed/hotpatched currentowner. The actualcurrentwindow admitted before this policy, do not claim it was a shared-GPU run.

Acceptance review preserves original role predicates/thresholds/denominators, moving separate from standing and UID/episode/reference joins. E2 worldgetter/phase, E3 firstepisode credit, W35 moving/reference/UIDcohorts, E0/S50 unknown original binary accepted predicates remain explicit gaps. Newsource measurement review, if captured partial, is not proof of runtimefix. No rates invented, no90%/hardware/fullskill graduation or statistical regression claim. Prior8actual20PPO and8ownscope evals fully closed in phase17; newgoal does not rerun them for archival.

Latest human DR question answered without changing physics: mass/inertia allbodies share one perenv densityfactor[.9,1.1], not independent link mass factors; COM random only chassisxyz±5mm, not all legs/link COM. MOD4v1 newnominalCOM is not randomizedcoverage.

All original and repaired source versions/errors/resources/handoffs and saved reports captured point-in-time with bytes/SHA and redaction index; binary/large artifacts kept at actual producers with known catalog identities only. Feature mod4v1-experts-fulldr-rm70 and unique annotated trial only; remote main/tagobject/peeled must be verified after push. Late reports generated after this capture remain nextappend pending, never rerun native/once for Git.
'''
(D/'NOTE.md').write_text(note,encoding='utf-8');files +=[(REL/n).as_posix()for n in('.gitattributes','SOURCE_INDEX.json','NOTE.md')]
original_git=record_experiment.git
def exact_short_git(*args):
 if len(args)>=2 and args[:2]==('add','--'):
  dest=args[2];selected=set(args[3:]);assert selected==set(files)and all(Path(f).is_relative_to(REL)for f in selected)
  out=original_git('add','--',dest,REL.as_posix());staged=set(original_git('diff','--cached','--name-only').splitlines());assert staged==selected|{dest};return out
 return original_git(*args)
record_experiment.git=exact_short_git
sys.argv=['record_experiment.py','--id','mod4v1-supermimic-bptt-original-wait-phase18','--title','Record new SuperMimic BPTT sources original-resource wait and CPU gradient evidence','--kind','training','--note-file',str(D/'NOTE.md'),'--validation','EightnonH1sourcebundlessealed;initialmissingSCHEDULEpreGOfailureanddedicatedsourcerepairpreserved;originalwaitthenactualE0E2nativeeach20verifiedH16WMpathBPTT-N1024separateCPU3;humanlowloadGPUsharingfuturev2source8checks-onlycomputeexclusionchanged-noactivehotpatch;originalplantbudgetlocksunchanged;acceptancegapsnull-Goalrev9active;no90percentclaim/noPTrawSDKrerunforGit','--files',*files]
record_experiment.main()
print(json.dumps(dict(commit=G('rev-parse','HEAD'),branch=G('branch','--show-current'),source_entries=len(rows),text_files=len(files),status=G('status','--porcelain')),indent=2))
