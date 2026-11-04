"""One combined archive: current-nine assessment and late existing text reports.
No training, source tests, model/raw content reads, remote execution or old record replay.
"""
from pathlib import Path
import json,hashlib,sys,subprocess,datetime
W=Path(r'F:\RMPOLAR-RL');T=W/'mod4v1_experts_fulldr_rm70_20261101';R=W/'mod4v1_supermimic_bptt_20261102';A=W/'mod4v1_current_nine_assessment_20261104';REPO=W/'repo-lqr';REL=Path('history/experiments/mod4v1_current_nine_assessment_phase43');D=REPO/REL;prior='7a52d584eb1d680fd4d9c3b8dc43d103004fbade'
sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
import record_experiment
G=lambda *a:subprocess.run(['git','-C',str(REPO),*a],check=True,capture_output=True,text=True,encoding='utf8').stdout.strip();H=lambda b:hashlib.sha256(b).hexdigest()
assert G('branch','--show-current')=='mod4v1-experts-fulldr-rm70'and G('rev-parse','HEAD')==prior and not G('status','--porcelain')and not D.exists()
result=json.loads((A/'CURRENT_NINE_SUBJECT_COMPLETION_RESULTS.json').read_bytes());assert result['num_models']==9 and result['all_nine_execution_complete']and result['original_source_scope_qualification']and result['new_optimizer_updates']==0 and result['old_models_and_registry_unchanged'];assert result['all_nine_actual_control_overlap_seconds']>0
q=json.loads((A/'reports/COLLECTOR_START_MARKER_ERRATUM.json').read_bytes());assert q['physical_reruns']==0 and q['original_unchanged']and len(q['changes'])==4 and not q['original_producer_or_markers_modified']
old=json.loads((REPO/'history/experiments/mod4v1_supermimic_bptt_phase42_delta/SOURCE_INDEX.json').read_bytes());known={x['source_path']:x for x in old['rows']};D.mkdir(parents=True);rows=[];files=[];refs=0
model_suffix={'.pt','.pth','.ckpt','.onnx','.safetensors','.pt2','.pkl','.pickle'};binary_suffix={'.pdf','.gz','.tar','.pyc','.npz','.npy','.usd','.usdc','.zip','.zst','.mp4','.png','.jpg','.jpeg','.stl','.bin','.partial','.unpublished','.jsonl','.csv','.parquet'}
source_names=['stage_current_nine_assessment_20261104_once.py','dispatch_current_nine_assessment_20261104_once.py','collect_current_nine_assessment_20261104_once.py','qualify_current_nine_cached_metadata_once.py','analyze_current_nine_w35_once.py','publish_current_nine_assessment_once.py','archive_current_nine_assessment_phase43_once.py','push_current_nine_assessment_phase43_once.py']
paths=sorted(set(R.rglob('*'))|set(A.rglob('*'))|{T/n for n in source_names},key=str)
for p in paths:
 row=dict(source_path=str(p))
 if p.suffix.lower()in model_suffix:
  row.update(status='model_reference_only_no_stat_or_read',source_sha256=None);rows.append(row);continue
 if not p.is_file():continue
 st=p.stat();row.update(stat_bytes=st.st_size,mtime_ns=st.st_mtime_ns);prev=known.get(str(p))
 if p.suffix.lower()in binary_suffix or p.name=='source_archive'or'__pycache__'in p.parts or st.st_size>50_000_000:
  row.update(status='binary_raw_or_large_reference_only_no_content_read',source_sha256=None);rows.append(row);continue
 if prev and prev.get('archive_path')and prev.get('stat_bytes')==st.st_size and prev.get('mtime_ns')==st.st_mtime_ns:
  assert(REPO/prev['archive_path']).is_file();row.update(status='previous_archive_reference_matching_size_mtime_not_rehashed',archive_path=prev['archive_path'],archive_sha256=prev['archive_sha256'],previously_archived_source_sha256=prev.get('source_sha256'),referenced_commit=prev.get('referenced_commit')or prior,current_content_not_reread_or_requalified=True);rows.append(row);refs+=1;continue
 raw=p.read_bytes();after=p.stat();row.update(bytes=len(raw),source_sha256=H(raw),unchanged_size_mtime_during_read=st.st_size==after.st_size and st.st_mtime_ns==after.st_mtime_ns)
 if not row['unchanged_size_mtime_during_read']:row['status']='moving_text_reference_pending_later_append'
 elif prev and prev.get('archive_path')and prev.get('source_sha256')==row['source_sha256']:
  row.update(status='unchanged_bytes_reference_existing_archive',archive_path=prev['archive_path'],archive_sha256=prev['archive_sha256'],referenced_commit=prev.get('referenced_commit')or prior);refs+=1
 else:
  try:text=raw.decode('utf8')
  except UnicodeDecodeError:row['status']='nonUTF8_reference_only'
  else:
   safe,n=redact(text);data=safe.encode('utf8')if n else raw;dest=D/'delta'/p.relative_to(W);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data);name=dest.relative_to(REPO).as_posix();files.append(name);row.update(status='text_redacted'if n else'complete_new_or_changed_text',redactions=n,archive_path=name,archive_sha256=H(data))
 rows.append(row)
(D/'.gitattributes').write_text('* -text\n',encoding='utf8')
(D/'SOURCE_INDEX.json').write_text(json.dumps(dict(captured_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),prior_phase42_commit=prior,prior_references=refs,existing_stat_references_not_new_content_proofs=True,model_raw_native_CPU_or_old_once_replays=0,rows=rows,late_followups='Remote verification is retained as tool output rather than another unarchived formal report. Any future newly saved reports append honestly; no endless health-only trial loop.'),indent=2),encoding='utf8')
note='''# Phase43 — one actual current-nine original-subject frozen assessment

Human replaced the legacy SuperMimic rebuild with one frozen assessment of the nine current normalized expert lineages, own original subjects only. Token budget100M is a ceiling, not a target. No new agents, Source audits, learning, model promotion or nine-by-nine cross-task matrix. The legacy persistent goal remains paused during manual execution of this direct request; no old training is rearmed.

Registryv12 scoped best selects four 20-PPO candidates E0/C878/C113/S135, mothers E2/E3/W35/S50 and frozen H1. Original proven V8 evaluator and original resource owner were reused. New root contains4025 non-model runtime files, oneGPU4090, N80 each720total, seed20260928. All original physics/fullDR/speeds/thresholds/locks/reserve/deadlines stay fixed. Models each physically read/hash/decoded once for the actual new functional evaluation, no live critic/optimizer or20k state slicing. No model or trajectory opens for this Git archive.

Actual control window2026-11-04 09:13:31–09:29:10 UTC+8; all-nine real-control overlap137.31s. All nine original control windows completed, nine children actualwait0, original parent actual outer Popenwait0, EX resources released, errors[]. Closed logs have no scanned PhysX/CUDA/contact-capacity errors. W35543new rows and schema were physically read once for original moving/standing grading; no dropped rows.

Original conditional results: S135 up27/27 down27/27 stand26/26; C878 up26/27 down27/27 stand26/26; C113 up22/27 down27/27 stand26/26. E3 first-episode recovery0/74, normal6 separate. H1 original270mm natural events64ready/42launched/0landed/0success over20s. E2 original joint world signed2pi bounds0/187 with43partialcycles and reference/cache semantics caveat. W35 moving18/61, standing26/26, partial183/45. E0 continuous MAE.0383/.0475m/s/.1011rad/s with0/80 physical terminations; no authoritative whole-profile binary rate. S50 own-axis20s descriptive facts only; no borrowed S135 predicate or invented fullramp rate. None proves all-expert90 orRM70 hardware qualification.

The initial new local collector incorrectly demanded WORKER_EVAL_STARTED from all workers. The four original E1 workers do not emit that file. Its false report is preserved, not promoted as an original producer failure. A separate cached-metadata correction used unchanged original parent all-nine-complete result, group_barrier, full actor/physics/feedback counts, timestamps, PRE_CLOSE and actualwaits; it fabricated no marker and reran zero physics. Both original reader false and correction are archived.

This combined snapshot includes late existing source-only history fixes, wire audit and partial stopped legacy Source artifacts afterPhase42 without adopting or executing them. Previously archived unchanged-size/mtime text is referenced with explicit no-new-content-hash status, not claimed a fresh byte proof. All new text is archived/redacted; model suffixes are skipped beforestat/read; binary/raw indexed without content. Prior failures and costs remain. No legacy training continuation, ledger manipulation, foreign signal, main push or reset. One feature-only annotated trial; exact remote branch/tag/peeled and read-onlymain are verified afterward as tool output.
'''
(D/'NOTE.md').write_text(note,encoding='utf8');files +=[(REL/n).as_posix()for n in('.gitattributes','SOURCE_INDEX.json','NOTE.md')]
original_git=record_experiment.git
def exact_short_git(*a):
 if len(a)>=2 and a[:2]==('add','--'):
  dest=a[2];selected=set(a[3:]);assert selected==set(files)and all(Path(x).is_relative_to(REL)for x in selected);value=original_git('add','--',dest,REL.as_posix());assert set(original_git('diff','--cached','--name-only').splitlines())==selected|{dest};return value
 return original_git(*a)
record_experiment.git=exact_short_git
sys.argv=['record_experiment.py','--id','mod4v1-current-nine-original-subject-assessment-phase43','--title','One current MOD4v1 nine-expert original-subject assessment','--kind','evaluation','--note-file',str(D/'NOTE.md'),'--validation','nine-current-best-models;actual-original-fullDR-N80;one-GPU720env;all-nine-control-complete;actual-inner-outer-waits-and-EXrelease;initial-E1-marker-reader-error-preserved-cached-correction-zero-rerun;original-direction-standing-recovery-partial-denominators;E0-S50-binary-rules-null;H1-models-registry-budget-unchanged;no-training-no-legacy-rebuild;late-existing-text-combined;modelraw-skipped','--files',*files]
record_experiment.main();print(json.dumps(dict(commit=G('rev-parse','HEAD'),branch=G('branch','--show-current'),entries=len(rows),previous_archive_references=refs,new_text_files=len(files),status=G('status','--porcelain')),indent=2))
