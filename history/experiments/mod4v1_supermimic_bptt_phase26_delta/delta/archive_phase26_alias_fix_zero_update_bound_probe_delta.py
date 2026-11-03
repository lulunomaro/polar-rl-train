"""Archive actual quality diagnosis, all close/reader failures and new source fixes.
No remote/native/SDK/model/raw open or old trial replay. Point-in-time text delta.
"""
from pathlib import Path
import json,hashlib,sys,subprocess,datetime
R=Path(__file__).resolve().parent;REPO=Path(r'F:\RMPOLAR-RL\repo-lqr');REL=Path('history/experiments/mod4v1_supermimic_bptt_phase26_delta');D=REPO/REL
sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
import record_experiment
G=lambda *a:subprocess.run(['git','-C',str(REPO),*a],check=True,capture_output=True,text=True,encoding='utf-8').stdout.strip()
H=lambda raw:hashlib.sha256(raw).hexdigest()
assert G('branch','--show-current')=='mod4v1-experts-fulldr-rm70'and G('rev-parse','HEAD')=='8d2c00278fa7734144362074f990ab87d7061b5a'and not G('status','--porcelain');assert not D.exists()
quality=json.loads((R/'reports/QUALIFIED_E3_W35_REFERENCE_CANDIDATE_SCREEN_V1.json').read_bytes())
assert quality['qualified_reference_execution']and quality['qualified_candidate_execution']and quality['decision']=='KEEP_REGISTRY_V12_SCOPED_BEST_NO_CANDIDATE_PROMOTION'
assert quality['relative_improvement']is None and quality['matched_UID_pose_cohort']is None and quality['full_expert_pass_rate']is None and not quality['mother_checkpoint_registry_or_H1_mutated']and not quality['further_same_baseline_volume_scheduled_to_reach3000']
assert [(x['reference']['n'],x['reference']['N'],x['candidate']['n'],x['candidate']['N'])for x in quality['conditions']]==[(0,74,0,74),(19,63,10,69),(26,26,16,17)]
assert (R/'CURRENT_PROGRESS_v15_QUALIFIED_TEACHER_CANDIDATE_CLOSED_KEEP_MOTHERS.md').is_file()and(R/'QUALIFIED_QUALITY_COMPARISON_E3_W35_V1.md').is_file()
alias=json.loads((R/'reports/RESUME_ALIAS_CONTROL_FIX_ACTUAL_CPU_COMPARISON_V1.json').read_bytes());assert [x['suite_passed']for x in alias['cases']]==[False,True]and all(x['completed_negative_cases']==14 and x['start']==3 and x['end']==5 for x in alias['cases']);assert (R/'CURRENT_PROGRESS_v17_ROUND8_CPU_ALIAS_FIXED_BOUND_PROBE_ORIGINAL_WAIT.md').is_file();stage=json.loads((R/'reports/BOUND_ONLY_E3_W35_V1_ACTUAL_SOURCE_STAGE_V1.json').read_bytes());assert stage['returncode']==0 and stage['stage']['staged']and stage['stage']['parent_launches']==0
known={}
for part,commit in [('mod4v1_supermimic_bptt_phase18_sources','8e6160b8747af162b5a486b3f3aa1ad4782223fd'),('mod4v1_supermimic_bptt_phase19_delta','57626b09cbed02b5b2efabbfd0c0b632383bdce0'),('mod4v1_supermimic_bptt_phase20_delta','4afdba074f3d295cd78ed4bf46a5cc779ff97b70'),('mod4v1_supermimic_bptt_phase21_delta','d31b5349abb5ee7c7f3dcbae7eec84c02aae761a'),('mod4v1_supermimic_bptt_phase22_delta','53678ec8d2e05dcafb890a357078c25020101903'),('mod4v1_supermimic_bptt_phase23_delta','01232718ef0ae41207dc50315d1bdbdeaa1c60d9'),('mod4v1_supermimic_bptt_phase24_delta','60a5ee122fc45238d3c636383e0a2d5f71d0343e'),('mod4v1_supermimic_bptt_phase25_delta','8d2c00278fa7734144362074f990ab87d7061b5a')]:
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
  old=known[str(p)];assert(REPO/old['archive_path']).is_file();row.update(status='unchanged_reference_existing_phase18_through25',archive_path=old['archive_path'],archive_sha256=old['archive_sha256'],referenced_commit=old['known_commit']);refs+=1
 else:
  try:text=raw.decode('utf-8')
  except UnicodeDecodeError:row['status']='nonUTF8_metadata_index_only'
  else:
   safe,n=redact(text);data=safe.encode('utf-8')if n else raw;dest=D/'delta'/p.relative_to(R);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data);name=dest.relative_to(REPO).as_posix();files.append(name);row.update(status='text_redacted'if n else'complete_new_or_changed_text',redactions=n,archive_path=name,archive_sha256=H(data))
 rows.append(row)
(D/'.gitattributes').write_text('* -text\n',encoding='utf-8');(D/'SOURCE_INDEX.json').write_text(json.dumps(dict(captured_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),prior_phase25_commit='8d2c00278fa7734144362074f990ab87d7061b5a',unchanged_reference_count=refs,rows=rows,not_captured_yet='Late bound-probe admission/closure/grade and handoffs remain pending next append; no physical or CPU purpose replay for Git.'),indent=2),encoding='utf-8')
note='# Phase26 — whole-resume CPU alias fixed; new ZERO_UPDATE bound-only probe\n\nQuality remains primary. The previously qualified original teacher/candidate single-seed original-scope comparison is unchanged: E3 recovery0/74 each, separate normal6 physicalterm0/6 vs6/6; W35 moving19/63 vs10/69, standing26/26 vs16/17, all partials and unequal cohorts exposed. Keep Registryv12 mothers and H1, no independent multi-seed80/90, hardware or causal claim. Good C878/S135 sources are kept rather than perturbed to fill a training-count quota; C113 targets ascending failures, E0/E2/S50 measurement gaps remain explicit.\n\nPreserve old actual CPU V1 local-pin prelaunch error, actual positive3-to5 with optimizer decoded-root alias, and its negative-fixture ordering failure. NEW CPU V2 fixes only that fixture; all14 negative cases complete and real same-view full four-model/four-optimizer/replay/RNG restoration continues3-to5, but old811 loader still changes retained decoded optimizer values/versions and correctly returns1. NEW CPU V3 changes only import copy plus whole deepcopy at load ingress; protected original remainder/module AST identical. Same3-to5 and all14 negatives pass, source decoded values/versions and raw bytes remain unchanged, single own synthetic checkpoint open/hash/decode, no reread. Both are real Torch CPU software evidence, not native expert updates, original selected PT reads, GPU restore or skill improvement. Core20fd not installed in native training; legacy continuation remains unselected.\n\nNew bound-only native source17 contains complete canonical runtime7a092, helper3375, route0f24, runtimee6b6, parent63ea and AppV6-to-base closure. Same learned parameters; only teacher+.05*tanh(delta), thenclip6. Original raw35 noisy/delayed sensors, hist10/goal3/true term|trunc, strict load after ctor zero, one fresh cache build, full CPU/pi/teacher/RMS/source guards, original control loops/DR/physics/predicates preserved. CapabilityTrue is not actual admission. Optional action statistics defaultFalse. Earlier source-only helper math was actually verified on CPU; independent recovery reviewer checked all17 source pins273460B and actual source inventory without rerunning old tests. Old/source-agent failures and incomplete-finalization provenance preserved.\n\nNew root MOD4V1_BOUND_ONLY_E3_W35_PROBE_V1_20261103_123731_1793680651375185300 source preflight/stage succeeded3603 files, stage1a40a9f2c84eeac6bd84ce90a3121ebc904017e401837ea0046e11d689eecd72. Original-gated parent1524136/startticks142230922 and independent actual-wait controller1524129 were launched once. Initial original preGO wait is genuine, not native skill execution: 12:45:45 readonly snapshot shows other LQR owner1523782 holds both authority EX and GPU1 privateEX; free GPU0 does not authorize canonical/lock takeover. Remaining300795.843419075 and reserve86412.86069250107 are readonly snapshots, not copied ledgers. Original1800wait/resources/finally/actualwait remain unchanged, no foreign signals, extension, refunds or training. The observer captures later phase changes independently; point-in-time archive does not claim later actual qualification or grade. New grade source waits for qualified closure and will stream ONLY this new W35 artifact once.\n\nAll source files, schemas, methods, actual receipts, errors, handoffs and mutable published metadata are frozen at capture. Model suffixes skipped before stat/read, raw/binary/large only metadata and existing producer references; no PT/raw reopened for Git, no once/native/grade reruns. New reports after capture remain pending next append; main readonly and unchanged by this archive. Goal active; ZERO_UPDATE clipping effects will not be called training benefit.\n'
(D/'NOTE.md').write_text(note,encoding='utf-8');files +=[(REL/n).as_posix()for n in('.gitattributes','SOURCE_INDEX.json','NOTE.md')]
original_git=record_experiment.git
def exact_short_git(*a):
 if len(a)>=2 and a[:2]==('add','--'):
  dest=a[2];selected=set(a[3:]);assert selected==set(files)and all(Path(x).is_relative_to(REL)for x in selected)
  value=original_git('add','--',dest,REL.as_posix());assert set(original_git('diff','--cached','--name-only').splitlines())==selected|{dest};return value
 return original_git(*a)
record_experiment.git=exact_short_git
sys.argv=['record_experiment.py','--id','mod4v1-supermimic-whole-resume-alias-fixed-zero-update-bound-probe-phase26','--title','Validate whole-resume CPU alias fix and stage an independent zero-update bound-only quality probe','--kind','evaluation','--note-file',str(D/'NOTE.md'),'--validation','quality-first-keep-mothers;CPU-control-RC1-fixed-RC0-14negative-real3to5-whole-root-immutable;new17-source-pinned-original-physicsDR-predicate-resources;bound-probe0updates-new-stage-parent-actualwait-original-preGO;no90-no-causal-or-hardware-claim;preserve-all-errors;no-modelraw-Git-reads','--files',*files]
record_experiment.main();print(json.dumps(dict(commit=G('rev-parse','HEAD'),branch=G('branch','--show-current'),entries=len(rows),unchanged_references=refs,new_text_files=len(files),status=G('status','--porcelain')),indent=2))
