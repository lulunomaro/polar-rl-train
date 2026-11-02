"""Append V6 compatibility, real unused-root stage/dispatch and original wait.
No remote, SDK, original model/raw reads, ledger work or old once replay.
"""
from pathlib import Path
import json,hashlib,sys,subprocess,datetime
R=Path(__file__).resolve().parent;REPO=Path(r'F:\RMPOLAR-RL\repo-lqr');REL=Path('history/experiments/mod4v1_supermimic_bptt_phase22_delta');D=REPO/REL
sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
import record_experiment
G=lambda *a:subprocess.run(['git','-C',str(REPO),*a],check=True,capture_output=True,text=True,encoding='utf-8').stdout.strip()
H=lambda raw:hashlib.sha256(raw).hexdigest()
assert G('branch','--show-current')=='mod4v1-experts-fulldr-rm70'and G('rev-parse','HEAD')=='d31b5349abb5ee7c7f3dcbae7eec84c02aae761a'and not G('status','--porcelain');assert not D.exists()
pre=json.loads((R/'reports/A1_NATIVE_V6_ACTUAL_SOURCE_PREFLIGHT_V1.json').read_bytes());stage=json.loads((R/'reports/A1_NATIVE_V6_ACTUAL_NONPT_STAGE_V1.json').read_bytes());dispatch=json.loads((R/'reports/A1_NATIVE_V6_ORIGINAL_OWNER_DISPATCH_V1.json').read_bytes());assert all(x['returncode']==0 for x in(pre,stage,dispatch));assert dispatch['receipt']['actual_Popen_calls']==1 and stage['stage_complete']['selected_PT_stat_read_copy']==0
known={}
for part,commit in [('mod4v1_supermimic_bptt_phase18_sources','8e6160b8747af162b5a486b3f3aa1ad4782223fd'),('mod4v1_supermimic_bptt_phase19_delta','57626b09cbed02b5b2efabbfd0c0b632383bdce0'),('mod4v1_supermimic_bptt_phase20_delta','4afdba074f3d295cd78ed4bf46a5cc779ff97b70'),('mod4v1_supermimic_bptt_phase21_delta','d31b5349abb5ee7c7f3dcbae7eec84c02aae761a')]:
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
  if p.suffix.lower()in('.pyc','.npz','.npy','.usd','.usdc','.zip','.zst','.mp4','.png','.jpg','.jpeg','.stl','.bin','.partial','.unpublished')or'__pycache__'in p.parts or before.st_size>50_000_000:
   row.update(status='binary_large_or_unpublished_metadata_only_no_content_read',source_sha256=None);rows.append(row);continue
  raw=p.read_bytes();after=p.stat();row.update(bytes=len(raw),source_sha256=H(raw),unchanged_size_mtime_during_read=before.st_size==after.st_size and before.st_mtime_ns==after.st_mtime_ns)
 except FileNotFoundError:
  row.update(status='disappeared_during_capture_pending_next_append',source_sha256=None);rows.append(row);continue
 if not row['unchanged_size_mtime_during_read']:row['status']='moving_index_only_pending_later_append'
 elif str(p)in known and known[str(p)]['source_sha256']==row['source_sha256']:
  old=known[str(p)];assert(REPO/old['archive_path']).is_file();row.update(status='unchanged_reference_existing_phase18_through21',archive_path=old['archive_path'],archive_sha256=old['archive_sha256'],referenced_commit=old['known_commit']);refs+=1
 else:
  try:text=raw.decode('utf-8')
  except UnicodeDecodeError:row['status']='nonUTF8_metadata_index_only'
  else:
   safe,n=redact(text);data=safe.encode('utf-8')if n else raw;dest=D/'delta'/p.relative_to(R);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data);name=dest.relative_to(REPO).as_posix();files.append(name);row.update(status='text_redacted'if n else'complete_new_or_changed_text',redactions=n,archive_path=name,archive_sha256=H(data))
 rows.append(row)
(D/'.gitattributes').write_text('* -text\n',encoding='utf-8');(D/'SOURCE_INDEX.json').write_text(json.dumps(dict(captured_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),prior_phase21_commit='d31b5349abb5ee7c7f3dcbae7eec84c02aae761a',unchanged_reference_count=refs,rows=rows,not_captured_yet='All first-created or changed later source/progress/final/handoffs remain pending next append.'),indent=2),encoding='utf-8')
note='''# Phase22 — V6 two compatibility fixes, actual new-root stage/dispatch, original resource wait

Goal goal-1c14ef7d-c888-4287-83bf-c008d54545fb revision10 ACTIVE; H1 frozen. Eight per-role3000 real verified policyBPTT and original90% remain unproven. HistoricalA0 E02520/E22392 total4912 complete saves remain separate, not transferred toA1. ActualV5 two pre-reset/teacher/learner startup errors, six neveradmitted, truewait/cost/leases/71.64120578765869expertseconds stay preserved withoutrefund/retry.

## Narrow source-supported compatibility only
PoseV4 allows exact nativefloat negativeinfinity BUFFER stale marker written by ORIGINAL active D7 ChassisCOMSDK; finiteclock/NaN/+inf/wrapped/future/other-negative rejection, original8stamps=-1 onlyafteroriginalfullstatewrite, source/MRO/data pin andgravity1e-3 stay.66stdlib shadow checks, not native proof. AppV6 supports only two source-published exact SimulationApp exportmodule aliases, producer/validator use actualalias consistently and record actualmodule/type/MRO/helperSHA. Original48933B/6af537.../close848/exactclass-MRO/self-func/plainbool/zeroargclose/FINAL/error/actualwait rules stay;80stdlib alias/behavior checks. Historical V5 actual timestamp/module was not published and is not retrofilled. Stage/dispatcher37stdlib/fake/mock checks; originalworker/owner/shim and other12of14 actualsource PINs remain byteidentical. No reward/speed/DR/physics/acceptance weakening or E2sensor-exact/tracking/bound/anchor arm.

## Actual parent pack and new purpose, not the child ZIP identity
Parent fourteenfile source input182131B/index4078B SHAf12617c45596c752de12050e17132d9dfab0aea8ed1336abe23d8e0ce256fa90; child ZIP/index31a8 has distinct metadata/identity and was not claimed uploaded. Real newroot MOD4V1_A1_RAW35_V6_20261102_223443_1793630083698851500 plus separate_SOURCE_INPUT. Actual source-only preflightRC0 and actualnonPTstageRC0 with19aliases/all8staticbank-preserving role manifests. OriginalSCHEDULEconfig beforeownerimport. Stager9c68/dispatcher7eca require NEW V6 root/index/parentpurpose and preserveoriginalC/resource/reserve/3900max3600save300headroom1800preGO. StageSHA44cf78a22d8dea3fa8a08700ae39d39f79996f82195c0dfe8f04b387f026e5db; no modelstat/read/copy/SDK/C/GO in stage.

Actualoriginal-parent dispatchPopen1, parent1488631/startticks137182064 at22:40:38. Queue is NOT actualGO/training. Last captured read-only resource diagnosis22:45:17: otheroriginalcanonicalowner Linux_LQR_MPC_DEPTH_STUDENT389_1793628650726363806, parent1486968 holds bothauthorityEX; GPU1privateEX1486977. GPU0free24203MiB/util0, GPU1free19645MiB/util7/compute1486992uses4550MiB. Lowcompute admission alreadyallowsapps but does not bypass foreigncanonical/privatelease. Own boundedwait Errno11/partial0/PTSDKGOCwritesFalse. No foreignsignal/lockclear/newledger/extension. Remaining338462.91543388367 is an observedsummary, never canonicalwriteback. Later own watcher metadata copied at exactcapture may supersede this snapshot; absence ofproducer counts staysnull, noCPU/oldA0counter substitution. Onlyone current V6 ownpublished-metadata observer; ownclosedstdout copied once after actualclosure. Do not restart/replay consumedroots/once for Git.

## Separate software/measurement work
A0/A1 full learner reset-resume actualTorchCPU V2 and A1N80mean actualTorchCPU exact reference/error0.0 proof remain softwareonly/native0. Frozenhelper requiresactualsuccessfulA1FINAL, embeds source teacher+residual, onlypiGPU, fullN1024rootCPU untouched/no replay/RNG/historyslice or motherPTreopen; originalnoisydelayed35 and trueepisode masks. New source-only independent evaluator integration and bounded E0/S50 originalbinaryauthority search are pending/archived onlyasactuallypresent. Originalaccepted thresholds/conditionaldenominators/UID/reference/cohort gaps stay; noMAE/nofall/S135proxyinvented. Pairedmother/candidate reset protocol mustmatch before comparison.

All actual failures, source/test histories, sealednew sources, parent mapping, point-in-time stage/dispatch/wait and handoffs captured/referenced; later mutable progress/source/close pending nextappend. Phase21 feature/trial remoteexactverified d31b5349.../annotatede5c08c..., mainf304...read-only then independentlyadvances. Feature+uniqueannotatedtrial only; no physical or model/raw reads for archive.
'''
(D/'NOTE.md').write_text(note,encoding='utf-8');files +=[(REL/n).as_posix()for n in('.gitattributes','SOURCE_INDEX.json','NOTE.md')]
original_git=record_experiment.git
def exact_short_git(*a):
 if len(a)>=2 and a[:2]==('add','--'):
  dest=a[2];selected=set(a[3:]);assert selected==set(files)and all(Path(x).is_relative_to(REL)for x in selected)
  value=original_git('add','--',dest,REL.as_posix());assert set(original_git('diff','--cached','--name-only').splitlines())==selected|{dest};return value
 return original_git(*a)
record_experiment.git=exact_short_git
sys.argv=['record_experiment.py','--id','mod4v1-supermimic-v6-compat-staged-original-wait-phase22','--title','Record narrow SDK compatibility sources, actual fresh V6 entry and original lock wait','--kind','training','--note-file',str(D/'NOTE.md'),'--validation','V6Pose66-App80-Stage37CPUonly;only2of14pinschanged;originalphysicsDRrewardthresholdsCreservelocksfinitelimitsunchanged;actualfreshpreflightstagePopen1-notGOclaim;waitothercanonicalparent1486968-nointerference;oldA04912notspliced;Goalrev10active-no90claim','--files',*files]
record_experiment.main();print(json.dumps(dict(commit=G('rev-parse','HEAD'),branch=G('branch','--show-current'),entries=len(rows),unchanged_references=refs,new_text_files=len(files),status=G('status','--porcelain')),indent=2))
