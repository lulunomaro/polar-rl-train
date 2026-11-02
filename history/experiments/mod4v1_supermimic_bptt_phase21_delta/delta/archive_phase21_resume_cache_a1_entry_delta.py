"""Append new cache/close/resume software, CPU failures and A1 entry metadata.
No remote/C/SDK work or selected checkpoint read/stat; no replay of old once.
"""
from pathlib import Path
import json,hashlib,sys,subprocess,datetime
R=Path(__file__).resolve().parent;REPO=Path(r'F:\RMPOLAR-RL\repo-lqr');REL=Path('history/experiments/mod4v1_supermimic_bptt_phase21_delta');D=REPO/REL
sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
import record_experiment
G=lambda *a:subprocess.run(['git','-C',str(REPO),*a],check=True,capture_output=True,text=True,encoding='utf-8').stdout.strip()
H=lambda raw:hashlib.sha256(raw).hexdigest()
assert G('branch','--show-current')=='mod4v1-experts-fulldr-rm70'and not G('status','--porcelain');assert not D.exists()
truth=json.loads((R/'reports/FIRST_NATIVE_WINDOW_CLOSED_TRUTH_V1.json').read_bytes());assert truth['total_verified_native_BPTT_steps']==4912 and truth['parent_exit']['original_cost_settled']
test=json.loads((R/'reports/LEGACY_A0_A1_FULL_RESUME_CPU_V2.json').read_bytes());assert test['returncode']==0 and test['receipt']['passed']and test['native_expert_BPTT_steps']==0
known={}
for part,commit in [('mod4v1_supermimic_bptt_phase18_sources','8e6160b8747af162b5a486b3f3aa1ad4782223fd'),('mod4v1_supermimic_bptt_phase19_delta','57626b09cbed02b5b2efabbfd0c0b632383bdce0'),('mod4v1_supermimic_bptt_phase20_delta','4afdba074f3d295cd78ed4bf46a5cc779ff97b70')]:
 for x in json.loads((REPO/'history/experiments'/part/'SOURCE_INDEX.json').read_bytes())['rows']:
  if x.get('archive_path')and x.get('source_sha256'):known[x['source_path']]={**x,'known_commit':x.get('referenced_commit')or commit}
D.mkdir(parents=True);rows=[];files=[];refs=0
for p in sorted(R.rglob('*'),key=str):
 row=dict(source_path=str(p))
 if p.suffix.lower()in('.pt','.pth','.ckpt','.onnx','.safetensors'):
  row.update(status='model_reference_only_no_stat_or_read',source_sha256=None);rows.append(row);continue
 if not p.is_file():continue
 try:
  before=p.stat();row.update(stat_bytes=before.st_size,mtime_ns=before.st_mtime_ns)
  if p.suffix.lower()in('.pyc','.npz','.npy','.usd','.usdc','.zip','.zst','.mp4','.png','.jpg','.jpeg','.stl','.bin','.partial')or'__pycache__'in p.parts or before.st_size>50_000_000:
   row.update(status='external_binary_large_or_unpublished_temporary_metadata_only_no_content_read',source_sha256=None);rows.append(row);continue
  raw=p.read_bytes();after=p.stat();row.update(bytes=len(raw),source_sha256=H(raw),unchanged_size_mtime_during_read=before.st_size==after.st_size and before.st_mtime_ns==after.st_mtime_ns)
 except FileNotFoundError:
  row.update(status='disappeared_during_point_in_time_scan_pending_next_append',source_sha256=None);rows.append(row);continue
 if not row['unchanged_size_mtime_during_read']:row['status']='moving_index_only_later_append'
 elif str(p)in known and known[str(p)]['source_sha256']==row['source_sha256']:
  old=known[str(p)];assert(REPO/old['archive_path']).is_file();row.update(status='unchanged_reference_existing_phase18_19_or20',archive_path=old['archive_path'],archive_sha256=old['archive_sha256'],referenced_commit=old['known_commit']);refs+=1
 else:
  try:text=raw.decode('utf-8')
  except UnicodeDecodeError:row['status']='nonUTF8_metadata_index_only'
  else:
   safe,n=redact(text);data=safe.encode('utf-8')if n else raw;dest=D/'delta'/p.relative_to(R);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data);name=dest.relative_to(REPO).as_posix();files.append(name);row.update(status='text_redacted'if n else'complete_new_or_changed_text',redactions=n,archive_path=name,archive_sha256=H(data))
 rows.append(row)
(D/'.gitattributes').write_text('* -text\n',encoding='utf-8');(D/'SOURCE_INDEX.json').write_text(json.dumps(dict(captured_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),prior_phase20_commit='4afdba074f3d295cd78ed4bf46a5cc779ff97b70',unchanged_reference_count=refs,rows=rows,not_captured_yet='Anything first created or changed after this exact capture, including future native progress/close and later handoffs, is pending next append.'),indent=2),encoding='utf-8')
note='''# Phase21 — original-cache and App-close contracts, full learner reset-resume, A1 entry

Goal goal-1c14ef7d-c888-4287-83bf-c008d54545fb rev10 remains ACTIVE; H1 frozen. No claim that eight experts reached3000 or90%. Original2c/bae,400N/k2000/d3,50/100Hz,.0025,TGS32/4,.01m/.01rad,D0-D7,originalC/reserve/locks/finite3900-save3600-headroom300 remain unchanged.

## Prior actual window is preserved, not replayed
E0A0 verified2520/E2A02392 full checkpoints and six pre-learner quaternion/gravity errors, total4912, all original actualwait/cost/lease closure remain. Six processRC0 are not successful execution. No source PT/raw/SDK/canonical read for this archive.

## Actual new V5 entry also closed with two preserved startup errors
New root MOD4V1_A1_RAW35_V5_20261102_214635_1793627195384785900 was genuinely staged and dispatched once. Parent1486089 admitted E3/W35 at21:55:41/42. Both SDK constructs failed during pose-adapter install before the ONE explicit reset/teacher PT/learner/policy action. Producer counts/FINAL null; inferred A1BPTT0, not skill0%. Both processRC0 still correctly classified ERROR by the new semantic owner; remaining6 were never admitted. All actualwait/cost/lease closure complete;71.64120578765869 expertseconds GO-to-wait retained, no refunds. This is not merely a resource wait and not a successful cache fix.

Primary error NON_NATIVE_FINITE_TIMESTAMP for _root_link_vel_w. Source-only diagnosis: actual Warp default-1, but active original D7 ChassisCOMSDK constructor/reset/apply legitimately writes nativefloat negativeinfinity stale sentinels to this cache; prior actual value/type was not in the error and staysunknown. Secondary App exact-class mismatch recorded. Referenced isaacsim.expose_api has both standard and fallback simulation_app import paths; historical actual module notpublished. New V4/V6 timestamp/alias fixes are SOURCE-only atcapture unless separately published newruntime says otherwise; no oldroot/once retry or threshold/physics weakening.

## New software and all failures
Sealed source-only instance pose-cache adapterv3 validates actual bound backend/data source and only invalidates eight omitted derived timestamps after the one original fullstate writer returns.54stdlib tests are not native binding proof. Original xyzw conversion,1e-3 gravity guard,original sensor noise/delay/reset/physics unchanged. Runtime will still stop on actual binding/layout/guard errors.

Actual linked SimulationApp source48933B SHA6af5372bb0cdda6e665a30cd285ff724b3e5bd012dbdd4df458e0726173fc903 documents defaultfast_shutdown immediate nonreturn. NewV5 retains original app.close() and setting, never fabricates postreturn. Actualwait+validcompleteFINAL+noerrors+runtime-pinned fast-close intent after bridge/env closes may replace ONLY the missing-postApp lifecycle reason.73stdlib including six realCPUfake-child exit/return/error scenarios are software evidence, not historical actualclose cause/native proof. Bounded pose receipts first3/last/counters avoid unbounded per-reset JSON rewrites.

V2 full reset-resume actualTorchCPU test passed bothA0 andA1: fourmodels/fouroptimizers/norm/replay/RNG/counters/collect_fraction/pendingiteration preserved, explicit streamcut/freshhistory,3->4 verified H16/hist10 updates, WMaux20->21 andcritic3->4. One physical byte read/hash/decode per own synthetic PT. Real teacher weight/buffer corruption and crossview descriptor/schema/shape counterexamples blocked. Native0/originalteacherPT0. V1 fixture incorrectly expected constructorinit0; failure retained, V2 only corrects this to actualvendor constructorinit1 with no increase at load/collect. All oldcore/worker/contracts frozen.

## A1 is a distinct lineage
Future A1 raw35 fresh means actor uses only original noisy/delayed35+history/knowncommands, teacher frozen. WM/critic may retain simulation context. A0 updates/weights/Adam are not spliced into newA1. Legacy held command/aux sensor approximation, original reward and.05unbounded residual are explicit; not the E2 command-projection/sensor-exact/reward/bound/anchor ablation. C113 original after-reset axis binding is separate protocol restoration, no extrareset/observation RNG. Newentry sources/stage/admission/progress present atcapture are archived exactly as published; absence/pending is not claimed native execution. Original resource snapshots and foreign-owner waits do not authorize stealing canonical/private leases.

All new/changed source, fake/runtime errors, reader/path errors, test receipts, point-in-time native/stage metadata and handoffs are indexed. Unchanged text references prior18/19/20SHA. Later files/progress are pending nextappend. Feature+uniqueannotated trial only; currentremote main is read-only and independently advances. No physical reruns for Git.
'''
(D/'NOTE.md').write_text(note,encoding='utf-8');files +=[(REL/n).as_posix()for n in('.gitattributes','SOURCE_INDEX.json','NOTE.md')]
original_git=record_experiment.git
def exact_short_git(*a):
 if len(a)>=2 and a[:2]==('add','--'):
  dest=a[2];selected=set(a[3:]);assert selected==set(files)and all(Path(x).is_relative_to(REL)for x in selected)
  value=original_git('add','--',dest,REL.as_posix());assert set(original_git('diff','--cached','--name-only').splitlines())==selected|{dest};return value
 return original_git(*a)
record_experiment.git=exact_short_git
sys.argv=['record_experiment.py','--id','mod4v1-supermimic-raw35-resume-cache-entry-phase21','--title','Record full learner reset-resume software, bounded cache and fast-close contracts, distinct A1 entry','--kind','training','--note-file',str(D/'NOTE.md'),'--validation','prioractualnative4912preserved;A0A1H16CPUfullresume3to4-fourmodels4optsnormreplayRNG-teachercorruption-crossviewblocked-native0;V1fixtureerrorretained;posecache54-fastclose73sourceCPU-notnative;originalCphysicsDRthresholdsunchanged;newA1fresh0-notA0countsplice;actualstage/nativeonlypublishedpointintime;Goalrev10active','--files',*files]
record_experiment.main();print(json.dumps(dict(commit=G('rev-parse','HEAD'),branch=G('branch','--show-current'),entries=len(rows),unchanged_references=refs,new_text_files=len(files),status=G('status','--porcelain')),indent=2))
