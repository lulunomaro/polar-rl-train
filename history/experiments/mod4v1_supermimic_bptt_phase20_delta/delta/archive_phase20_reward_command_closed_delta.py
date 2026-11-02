"""Append reward/command audits, all CPU attempts, and true closed native results.
No selected models/raw/SDK/remote/canonical reads; only local saved text evidence.
"""
from pathlib import Path
import json,hashlib,sys,subprocess,datetime
R=Path(__file__).resolve().parent;REPO=Path(r'F:\RMPOLAR-RL\repo-lqr');REL=Path('history/experiments/mod4v1_supermimic_bptt_phase20_delta');D=REPO/REL
sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
import record_experiment
G=lambda *a:subprocess.run(['git','-C',str(REPO),*a],check=True,capture_output=True,text=True,encoding='utf-8').stdout.strip()
H=lambda raw:hashlib.sha256(raw).hexdigest()
assert G('branch','--show-current')=='mod4v1-experts-fulldr-rm70'and not G('status','--porcelain');assert not D.exists()
truth=json.loads((R/'reports/FIRST_NATIVE_WINDOW_CLOSED_TRUTH_V1.json').read_bytes());assert truth['total_verified_native_BPTT_steps']==4912 and truth['parent_exit']['original_cost_settled'];test=json.loads((R/'reports/COMMAND_CANDIDATE_CORE_INTEGRATION_CPU_V3.json').read_bytes());assert test['returncode']==0 and test['receipt']['passed']and test['native_expert_BPTT_steps']==0
known={}
for part,commit in [('mod4v1_supermimic_bptt_phase18_sources','8e6160b8747af162b5a486b3f3aa1ad4782223fd'),('mod4v1_supermimic_bptt_phase19_delta','57626b09cbed02b5b2efabbfd0c0b632383bdce0')]:
 for x in json.loads((REPO/'history/experiments'/part/'SOURCE_INDEX.json').read_bytes())['rows']:
  if x.get('archive_path')and x.get('source_sha256'):known[x['source_path']]={**x,'known_commit':x.get('referenced_commit')or commit}
D.mkdir(parents=True);rows=[];files=[];refs=0
for p in sorted((p for p in R.rglob('*')if p.is_file()),key=str):
 row=dict(source_path=str(p))
 if p.suffix.lower()in('.pt','.pth','.ckpt','.onnx','.safetensors'):row.update(status='model_reference_only_no_stat_or_read',source_sha256=None);rows.append(row);continue
 before=p.stat();row.update(stat_bytes=before.st_size,mtime_ns=before.st_mtime_ns)
 if p.suffix.lower()in('.pyc','.npz','.npy','.usd','.usdc','.zip','.zst','.mp4','.png','.jpg','.jpeg','.stl','.bin')or'__pycache__'in p.parts or before.st_size>50_000_000:row.update(status='external_binary_or_large_metadata_only_no_content_read',source_sha256=None);rows.append(row);continue
 raw=p.read_bytes();after=p.stat();row.update(bytes=len(raw),source_sha256=H(raw),unchanged_size_mtime_during_read=before.st_size==after.st_size and before.st_mtime_ns==after.st_mtime_ns)
 if not row['unchanged_size_mtime_during_read']:row['status']='moving_index_only_later_append'
 elif str(p)in known and known[str(p)]['source_sha256']==row['source_sha256']:
  old=known[str(p)];assert(REPO/old['archive_path']).is_file();row.update(status='unchanged_reference_existing_phase18_or19',archive_path=old['archive_path'],archive_sha256=old['archive_sha256'],referenced_commit=old['known_commit']);refs+=1
 else:
  try:text=raw.decode('utf-8')
  except UnicodeDecodeError:row['status']='nonUTF8_metadata_index_only'
  else:
   safe,n=redact(text);data=safe.encode('utf-8')if n else raw;dest=D/'delta'/p.relative_to(R);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data);name=dest.relative_to(REPO).as_posix();files.append(name);row.update(status='text_redacted'if n else'complete_new_or_changed_text',redactions=n,archive_path=name,archive_sha256=H(data))
 rows.append(row)
(D/'.gitattributes').write_text('* -text\n',encoding='utf-8');(D/'SOURCE_INDEX.json').write_text(json.dumps(dict(captured_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),prior_phase19_commit='57626b09cbed02b5b2efabbfd0c0b632383bdce0',unchanged_reference_count=refs,rows=rows,not_captured_yet='Files first created/changed after this exact point-in-time capture, especially ongoing bridge/reset/full-resume source_v2 reviews, are pending nextappend.'),indent=2),encoding='utf-8')
note='''# Phase20 — reward/command audits, all synthetic attempts, actual native close/error truth

Goal goal-1c14ef7d-c888-4287-83bf-c008d54545fb rev10 remains ACTIVE, H1 frozen. Original contracts/budget/locks/DR/400N/k2000/d3/50Hz100Hz/.0025/TGS32,4/.01m/.01rad remain. Human19:15 asked reward/command robustness. Full eight source/config join, SDK step/reward-command order, separate reward and raw35/command audits, candidates/diffs, disabled per-role ablations. No claimed skill improvement or new90% predicate.

## Actual native results, not RC0-as-success
Original first owner naturally completed all8 waits, accounted all cost, released all leases. E0 verified2520 (iter2620), E2 verified2392 (fullcheckpoint iter2492); complete new models/critic/aux/4opts/replay/RNG/history retained. Finite3600save stop, neither3000. Six remaining roles hit bridge.init_state quaternion/gravity guard BEFORE learner instantiation or first policy action: WORKER_ERROR, rawcountsnull/FINALnull; inferred BPTT0. All8 processRC0 does NOT mean8 successful experts. Owner source only checksrc; worker source does raise, SDK close masking is only a hypothesis. Metadata reclassification is6startupfail+2savedtraining, total4912 verified policyBPTT, GO-to-wait7603.138181686401 expertseconds. Full errors/logs/wait and originalproducer SHA/bytes/path retained; no models opened for archive.

## Audit and software evidence
Reward62stdlib pass, command37stdlib pass, original measurement final46stdlib pass (late phase19seal nowappend). Raw35/command strictUnknown/components TorchCPU22pass: H16future->s1->a0 causal VJP nonzero but optimizer0/native0. C113 exactoriginalbind candidate CPU13pass; afterONEfreshreset onlycommand[:3] sync, noextraRNG/reset/observation sample, not deployed. Sourcefound missingbind never reached a policyaction in failed C113actualstartup.

Candidate actualcore integration V1 and V2 both fail missingrich BEFORE algorithm test, preserved independent reports/markers. V3 explicitly adds existing sealed E0sm_deps AFTER launcher, immutablecandidate/test SHA same, realvendor+candidatecore H16/hist10 actualsyntheticWM20aux20policy3critic3, all3future->s1->a0 andparameterchange finite/nonzero, teacherfrozen, actor35, CUDAfalse, native0. Toy2x100Hznoise/lag tape is notactualsensor amplitude/frame/timestamp proof.

## Risks and next stage
Currentresidual fullctx includesSIMprivileged state/DR/contact/delay; raw35fresh migration is newlineage0, notoldAdam slicing/countsumming. E2originalvx2Vcos/yaw4 shortH16held maxanalyticalerror1.1943908827m/s, notruntimemeasurement. W35BODYvx[-.3,.3]/negativeaxis/standing/exposure preserved. Active reward gateoff, alive/term/basecontact/height-square weights0; SCUT expdenominatorstd notstd². Standing/height/action tradeoff andE3gravity-axiscost inversion counterexamples sourceonly. OriginalE0/S50binarypredicate gapnull; no all-expert90 claim.

Post-reset derivedcache source chain under NEW source_bridge_reset_cache_review_v2: Physxposesetter omits8derivedtimestamps; actualpreviousworker binding/stamps/rootcause stillunknown, noquat/tolerance weakening. New source_resume_runtime_v2 being prepared for truefulllearnerresume plusdeclaredfreshenvironment/streamcut, actualteacherGPUidentitycheck, C113originalaxis andfailclosed owner semantics. Theseongoing dirs captured ONLYwhatactuallyexistsatpointintime; laterfilesnextappend. No unchangedphysical retries/foreignlocks/ledgercopies/extensions forGit. Currentownnativeworkersclosed, nextcorrectedunusedwindow notyetadmitted.

Priorphase18/19 remoteexactverified; mainindependentlyadvances, verifycurrentreadonlymain afterfeature+uniqueannotatedtrial push. AllRtextnew/changed/failures/candidates/handoffs atcapture appended, unchangedSHA referenced inpriorarchive. No credentials, selectedweights, large/rawcontent added. Laterverification/handoff/newsource areexplicitpendingnextappend, notclaimedarchived.
'''
(D/'NOTE.md').write_text(note,encoding='utf-8');files +=[(REL/n).as_posix()for n in('.gitattributes','SOURCE_INDEX.json','NOTE.md')]
original_git=record_experiment.git
def exact_short_git(*a):
 if len(a)>=2 and a[:2]==('add','--'):
  dest=a[2];selected=set(a[3:]);assert selected==set(files)and all(Path(x).is_relative_to(REL)for x in selected)
  value=original_git('add','--',dest,REL.as_posix());assert set(original_git('diff','--cached','--name-only').splitlines())==selected|{dest};return value
 return original_git(*a)
record_experiment.git=exact_short_git
sys.argv=['record_experiment.py','--id','mod4v1-supermimic-reward-command-closed-truth-phase20','--title','Record eight-source reward-command audits, synthetic candidate gradients, native saves and six startup failures','--kind','training','--note-file',str(D/'NOTE.md'),'--validation','actualnativeE02520E22392fullsave-sixstartupERRORcountsnullRC0notpass-allwaitsettledreleased;reward62command37measurement46CPU;Torchcomponents22-C113bind13-coreH16synthetic3native0;allmissingrichattemptsretained;originalphysicsDRpredicateunchanged;newcache-resume-source-notyetnative;Goalrev10active','--files',*files]
record_experiment.main();print(json.dumps(dict(commit=G('rev-parse','HEAD'),branch=G('branch','--show-current'),entries=len(rows),unchanged_references=refs,new_text_files=len(files),status=G('status','--porcelain')),indent=2))
