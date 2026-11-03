"""Archive actual quality diagnosis, all close/reader failures and new source fixes.
No remote/native/SDK/model/raw open or old trial replay. Point-in-time text delta.
"""
from pathlib import Path
import json,hashlib,sys,subprocess,datetime
R=Path(__file__).resolve().parent;REPO=Path(r'F:\RMPOLAR-RL\repo-lqr');REL=Path('history/experiments/mod4v1_supermimic_bptt_phase27_delta');D=REPO/REL
sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
import record_experiment
G=lambda *a:subprocess.run(['git','-C',str(REPO),*a],check=True,capture_output=True,text=True,encoding='utf-8').stdout.strip()
H=lambda raw:hashlib.sha256(raw).hexdigest()
assert G('branch','--show-current')=='mod4v1-experts-fulldr-rm70'and G('rev-parse','HEAD')=='9d828219f6bf389318edd311ad340e9d74f97ebd'and not G('status','--porcelain');assert not D.exists()
quality=json.loads((R/'reports/QUALIFIED_E3_W35_REFERENCE_CANDIDATE_SCREEN_V1.json').read_bytes())
assert quality['qualified_reference_execution']and quality['qualified_candidate_execution']and quality['decision']=='KEEP_REGISTRY_V12_SCOPED_BEST_NO_CANDIDATE_PROMOTION'
assert quality['relative_improvement']is None and quality['matched_UID_pose_cohort']is None and quality['full_expert_pass_rate']is None and not quality['mother_checkpoint_registry_or_H1_mutated']and not quality['further_same_baseline_volume_scheduled_to_reach3000']
assert [(x['reference']['n'],x['reference']['N'],x['candidate']['n'],x['candidate']['N'])for x in quality['conditions']]==[(0,74,0,74),(19,63,10,69),(26,26,16,17)]
assert (R/'CURRENT_PROGRESS_v15_QUALIFIED_TEACHER_CANDIDATE_CLOSED_KEEP_MOTHERS.md').is_file()and(R/'QUALIFIED_QUALITY_COMPARISON_E3_W35_V1.md').is_file()
alias=json.loads((R/'reports/RESUME_ALIAS_CONTROL_FIX_ACTUAL_CPU_COMPARISON_V1.json').read_bytes());assert [x['suite_passed']for x in alias['cases']]==[False,True]and all(x['completed_negative_cases']==14 and x['start']==3 and x['end']==5 for x in alias['cases']);assert (R/'CURRENT_PROGRESS_v17_ROUND8_CPU_ALIAS_FIXED_BOUND_PROBE_ORIGINAL_WAIT.md').is_file();stage=json.loads((R/'reports/BOUND_ONLY_E3_W35_V1_ACTUAL_SOURCE_STAGE_V1.json').read_bytes());assert stage['returncode']==0 and stage['stage']['staged']and stage['stage']['parent_launches']==0
zero=json.loads((R/'reports/BOUND_ONLY_E3_W35_V1_ZERO_ADMISSION_CLOSED_TRUTH_V1.json').read_bytes());assert zero['actual_workers_created']==0 and zero['all_own_wait_and_original_EX_released']and zero['actual_parent_returncode']==1 and zero['skill_pass_rate']is None;assert (R/'CURRENT_PROGRESS_v19_BOUND_ZERO_GO_CLOSED_NEW_ADMISSION2_STAGED.md').is_file()
known={}
for part,commit in [('mod4v1_supermimic_bptt_phase18_sources','8e6160b8747af162b5a486b3f3aa1ad4782223fd'),('mod4v1_supermimic_bptt_phase19_delta','57626b09cbed02b5b2efabbfd0c0b632383bdce0'),('mod4v1_supermimic_bptt_phase20_delta','4afdba074f3d295cd78ed4bf46a5cc779ff97b70'),('mod4v1_supermimic_bptt_phase21_delta','d31b5349abb5ee7c7f3dcbae7eec84c02aae761a'),('mod4v1_supermimic_bptt_phase22_delta','53678ec8d2e05dcafb890a357078c25020101903'),('mod4v1_supermimic_bptt_phase23_delta','01232718ef0ae41207dc50315d1bdbdeaa1c60d9'),('mod4v1_supermimic_bptt_phase24_delta','60a5ee122fc45238d3c636383e0a2d5f71d0343e'),('mod4v1_supermimic_bptt_phase25_delta','8d2c00278fa7734144362074f990ab87d7061b5a'),('mod4v1_supermimic_bptt_phase26_delta','9d828219f6bf389318edd311ad340e9d74f97ebd')]:
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
  if p.suffix.lower()in('.pyc','.npz','.npy','.usd','.usdc','.zip','.zst','.mp4','.png','.jpg','.jpeg','.stl','.bin','.partial','.unpublished','.jsonl','.csv','.parquet')or'__pycache__'in p.parts or before.st_size>50_000_000:
   row.update(status='binary_large_raw_or_unpublished_metadata_only_no_content_read',source_sha256=None);rows.append(row);continue
  raw=p.read_bytes();after=p.stat();row.update(bytes=len(raw),source_sha256=H(raw),unchanged_size_mtime_during_read=before.st_size==after.st_size and before.st_mtime_ns==after.st_mtime_ns)
 except FileNotFoundError:
  row.update(status='disappeared_during_capture_pending_next_append',source_sha256=None);rows.append(row);continue
 if not row['unchanged_size_mtime_during_read']:row['status']='moving_index_only_pending_later_append'
 elif str(p)in known and known[str(p)]['source_sha256']==row['source_sha256']:
  old=known[str(p)];assert(REPO/old['archive_path']).is_file();row.update(status='unchanged_reference_existing_phase18_through26',archive_path=old['archive_path'],archive_sha256=old['archive_sha256'],referenced_commit=old['known_commit']);refs+=1
 else:
  try:text=raw.decode('utf-8')
  except UnicodeDecodeError:row['status']='nonUTF8_metadata_index_only'
  else:
   safe,n=redact(text);data=safe.encode('utf-8')if n else raw;dest=D/'delta'/p.relative_to(R);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data);name=dest.relative_to(REPO).as_posix();files.append(name);row.update(status='text_redacted'if n else'complete_new_or_changed_text',redactions=n,archive_path=name,archive_sha256=H(data))
 rows.append(row)
(D/'.gitattributes').write_text('* -text\n',encoding='utf-8');(D/'SOURCE_INDEX.json').write_text(json.dumps(dict(captured_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),prior_phase26_commit='9d828219f6bf389318edd311ad340e9d74f97ebd',unchanged_reference_count=refs,rows=rows,not_captured_yet='Late bound-probe admission/closure/grade and handoffs remain pending next append; no physical or CPU purpose replay for Git.'),indent=2),encoding='utf-8')
note='# Phase27 — preserve actual bound zero-admission timeout; new source admission ready\n\nOriginal skill quality remains primary. The qualified historical teacher/candidate comparison still E3 recovery0/74 each, normal6 firstphysicalterm0/6 vs6/6 separately; W35 moving19/63 vs10/69 and standing26/26 vs16/17, unequal natural cohorts/partials retained. Keep mothers/Registryv12/H1, no80/90/multi-seed/causal/hardware claim and no blind unchanged baseline volume.\n\nThe FIRST ZERO_UPDATE bound-only new original parent actually completed its original1800 preGO wait with TimeoutError because another canonical original owner remained active. Actual parent1524136 closed epoch1793682736.3700466 and external real Popen.wait returned1 at1793682736.3889406 with no controller errors. ACTUAL_GROUP_ADMISSION/CHILDREN/controlled start/FINAL are null; both roles NOT_ADMITTED/scene-ready and FINAL null, SDK/selected model opens0, actual workers0, child_waits empty, original GPU-private/finite EX released and Cwrites0. Exact closedmetadata45316B fa9f99ff72cf9f0856b943d83a52aacbe3cb506e864714e61ba33c3d3a9521c2. This is a resource-admission failure and no new skill score, not0% skill and not a relabelled successful probe. All original errors retained; no old root/stage/parent/observer replay.\n\nA separate bounded readonly post-timeout release observer starts only after verified old zeroGO closure and external actual wait; cap1800/20s, existing project C summary/known kernel lease rows and hardware gates only when all clear. No lock acquisition, Cwrite, model/SDK/GPU task, native parent, foreign signal or old-parent deadline extension. Positive release witness is historical evidence, not a future admission lease; original new parent must recheck actual gates. Owner_run_id missing in a console field is not proof active_segment is empty.\n\nNEW Admission2 purposes use explicit distinct local markers/reports/run/root and prior closed zeroGO proof. Parent Popen requires positive postclosure release witness bound to that closedSHA and original epoch; static preflight/stage may be prepared in advance without resource or model operations. Same exact17 source indexd051/helper3375/runtimee6b6/parent63ea/stager74f52, zero optimization updates, originalraw35/hist10/trueTTr/frozen weights and norm, originalN80/seed/control counts/DR/physics/speed/predicates/privateEX/finiteEX/Creadonly/1800/close/waits preserved. New root MOD4V1_BOUND_ONLY_E3_W35_PROBE_V1_ADMISSION2_20261103_131547_1793682947729489800 source preflight/stage actuallyRC0/3603files, stageb1d88c0084f3219051f4e8a28c395bed990e65fd25934ab98570ec5b5b31eaa1. At handoffv19 no new parent/model/SDK/skill; later actual evidence captured independently, not promised here. Only its own NEW qualified closed W35 data may be streamed once for original moving/standing grade; old raw never re-opened for labels/status/Git. Zero-update clipping effects cannot be called training gains.\n\nPriorPhase26 CPU control/repair and actual14negatives remain preserved: old811 expectedstrictRC1, new20fd whole-ingresscopyRC0/actual3to5/decodedroot values+versions immutable, software-only/no nativeGPUrestore or expert skill evidence. Core not installed to native legacy continuation. v18 source/capture remote verification and v19 closure/newpurposes retained. All late original observations, source builders/callers/guards/failures are archived at capture. Model suffixes skipped before stat/read; raw/binary/large references only, no trial, CPU or physics replay for Git. Main readonly; next results and mutable metadata changes after capture pending next append. Goal remains active.\n'
(D/'NOTE.md').write_text(note,encoding='utf-8');files +=[(REL/n).as_posix()for n in('.gitattributes','SOURCE_INDEX.json','NOTE.md')]
original_git=record_experiment.git
def exact_short_git(*a):
 if len(a)>=2 and a[:2]==('add','--'):
  dest=a[2];selected=set(a[3:]);assert selected==set(files)and all(Path(x).is_relative_to(REL)for x in selected)
  value=original_git('add','--',dest,REL.as_posix());assert set(original_git('diff','--cached','--name-only').splitlines())==selected|{dest};return value
 return original_git(*a)
record_experiment.git=exact_short_git
sys.argv=['record_experiment.py','--id','mod4v1-supermimic-bound-zero-go-timeout-new-admission-staged-phase27','--title','Preserve actual original bound zeroGO timeout and prepare fresh release-gated source admission','--kind','evaluation','--note-file',str(D/'NOTE.md'),'--validation','quality-first-keep-mothers;actual-original1800-zeroGO-no-modelSDK-skill-null;actual-external-parent-wait-RC1-and-originalEXreleased;no-oldpurpose-replay;new-readonly-release-witness-not-admission;new17-source-admission2-staged0parent;original-physicsDR-predicate-resource-budget-preserved;no-modelraw-Git-reads','--files',*files]
record_experiment.main();print(json.dumps(dict(commit=G('rev-parse','HEAD'),branch=G('branch','--show-current'),entries=len(rows),unchanged_references=refs,new_text_files=len(files),status=G('status','--porcelain')),indent=2))
