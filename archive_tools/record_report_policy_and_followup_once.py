"""Preserve the human's record-every-report requirement and recent report gaps.

No remote training/ledger operation. On success print the verified Git result;
do not generate another post-commit report file needing recursive commits.
"""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys,time
REPO=Path(__file__).resolve().parents[1];W=REPO.parent
sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
ID='all-trials-report-policy-and-terrain-followup-receipts'
tag='trial-'+time.strftime('%Y%m%d')+'-'+ID
def git(*a):return subprocess.check_output(['git','-C',str(REPO),*a],text=True,encoding='utf8').strip()
assert not git('tag','--list',tag),'Already recorded; do not repeat'
assert not git('diff','--cached','--name-only'),'Unrelated staging exists'
folder=REPO/'history/evidence/ALL_REPORTS_GIT_POLICY_20261009';assert not folder.exists();folder.mkdir(parents=True)
entries=[];files=['AGENTS.md','README.md','docs/ALL_TRIALS_AND_REPORTS_GIT_POLICY.md','docs/NEXT_AI_GIT_WORKFLOW.md','archive_tools/record_report_policy_and_followup_once.py']
hashbytes=lambda b:hashlib.sha256(b).hexdigest()
roots=['RM2026_TERRAIN_AUDIT_20261009','MOD4_RM_TERRAIN_CURRICULUM_REVISION_20261009']
for root in roots:
 d=W/root;assert d.is_dir()
 existing=REPO/'history/evidence'/root
 for src in sorted(d.rglob('*')):
  if not src.is_file() or '__pycache__' in src.parts:continue
  if src.suffix.lower() not in {'.md','.json','.jsonl','.txt','.csv','.tsv','.log'}:continue
  before=src.stat();raw=src.read_bytes();after=src.stat()
  assert before.st_size==after.st_size and before.st_mtime_ns==after.st_mtime_ns,'Moving report; capture separately'
  original_sha=hashbytes(raw);rel=src.relative_to(d)
  row=dict(source_path=str(src),source_relative_path=rel.as_posix(),stage=root,bytes=len(raw),sha256=original_sha,stable_during_capture=True)
  candidates=[existing/rel,existing/src.name]
  archived=next((x for x in candidates if x.is_file() and hashbytes(x.read_bytes())==original_sha),None)
  if archived is not None:
   row.update(archive_path=archived.relative_to(REPO).as_posix(),archive_sha256=original_sha,status='existing_Git_exact_SHA_reference')
   assert git('ls-files','--',row['archive_path'])==row['archive_path']
  else:
   text=raw.decode('utf8');clean,count=redact(text);capture=clean.encode('utf8')
   assert len(capture)<=50_000_000,'Large raw must be indexed separately'
   dst=folder/root/rel;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(capture)
   assert hashbytes(dst.read_bytes())==hashbytes(capture)
   path=dst.relative_to(REPO).as_posix();files.append(path)
   row.update(archive_path=path,archive_sha256=hashbytes(capture),status='complete_text_report' if count==0 else 'complete_report_with_credential_redaction',redactions=count)
  entries.append(row)
workspace_rules=folder/'WORKSPACE_AGENTS.md';shutil.copyfile(W/'AGENTS.md',workspace_rules);files.append(workspace_rules.relative_to(REPO).as_posix())
monitor=W/'MOD4_REPORT_GIT_POLICY_20261009/MONITOR_POLICY_VERIFIED.json';assert monitor.is_file()
copy=folder/'MONITOR_POLICY_VERIFIED.json';shutil.copyfile(monitor,copy);files.append(copy.relative_to(REPO).as_posix())
manifest=dict(epoch=time.time(),human_request='记住我们的所有试错，所有报告都得git来记录',
 scope='Recent RM geometry audit and terrain curriculum revision saved report files; not a claim of complete all-machine historical audit',
 report_count=len(entries),existing_exact_SHA_reference_count=sum(x['status']=='existing_Git_exact_SHA_reference' for x in entries),
 newly_archived_count=sum(x['status']!='existing_Git_exact_SHA_reference' for x in entries),reports=entries,
 all_selected_saved_reports_accounted_for=True,production_runtime_GPU_PPO_canonical_writes=0,new_budget_seconds=0)
dest=folder/'REPORT_CAPTURE_INDEX.json';dest.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8');files.append(dest.relative_to(REPO).as_posix())
note='''# Human requires every trial and every saved report in Git

The explicit human request is now recorded in workspace/repository AGENTS, a persistent project policy, the next-AI Git workflow and the active2h monitor. Success, failure, rejected approaches, rollback and reader/schema errors all keep their identities and evidence. All saved reports include metadata sync, final verification and later stage supplements; healthy polling without a new saved report does not need a separate trial. Existing exact-SHA reports are indexed by their tracked path rather than duplicated. No previous trial/tag is overwritten.

Backfill the saved reports from the recent RM field geometry audit and terrain curriculum revision, including pending/successful sync receipts, prior Git receipts and final verification. Preserve original snapshots as historical state; the report capture index gives source path/size/SHA, archive path/SHA, exact existing reference or complete/redacted text status. Credentials are never printed or archived, large weights/raw artifacts remain source SHA indices. This targeted backfill is not a claim that all historical reports on every host have been newly audited.

The persistent2h monitor settings and quiet health/pending intent remain, with explicit reporting coverage checks. This is a recording policy and report-completeness follow-up, no GPU/PPO/training process/production runtime/canonical/budget operation. Post-commit remote object verification is returned as tool output, avoiding an infinite chain of new verification files.
'''
nf=folder/'RECORD_NOTE.md';nf.write_text(note,encoding='utf8');files.append(nf.relative_to(REPO).as_posix())
cmd=[sys.executable,str(REPO/'archive_tools/record_experiment.py'),'--id',ID,'--title','Persist all-trials/report Git policy and backfill terrain audit follow-up reports','--kind','deployment',
 '--note-file',str(nf),'--files',*files,'--validation','Complete recent saved report manifest with SHA paths; credential redaction; persistent workspace/project/2h monitor rules; no training/runtime/GPU/PPO/canonical changes','--push']
p=subprocess.run(cmd,capture_output=True,text=True,encoding='utf8',errors='replace')
if p.returncode:
 # Preserve the actual error locally; the next repair must include this failed attempt.
 (W/'MOD4_REPORT_GIT_POLICY_20261009/RECORD_FAILED.json').write_text(json.dumps(dict(returncode=p.returncode,stdout=p.stdout,stderr=p.stderr,do_not_repeat_record=True),ensure_ascii=False,indent=2),encoding='utf8')
 raise RuntimeError('Recording failed; inspect existing objects/error, do not repeat record')
tag,head=p.stdout.strip().splitlines()[-1].split();obj=git('rev-parse',tag)
remote=dict(line.split('\t')[::-1] for line in git('ls-remote','origin','refs/heads/main','refs/tags/'+tag,'refs/tags/'+tag+'^{}').splitlines())
assert remote['refs/heads/main']==head and remote['refs/tags/'+tag]==obj and remote['refs/tags/'+tag+'^{}']==head
assert not git('status','--short'),'Remaining report/policy edits are not committed'
print(json.dumps(dict(tag=tag,commit=head,tagobject=obj,remote_main_tag_peeled_verified=True,
 report_count=manifest['report_count'],newly_archived_count=manifest['newly_archived_count'],existing_exact_SHA_reference_count=manifest['existing_exact_SHA_reference_count'],
 all_selected_saved_reports_accounted_for=True,push_pending=False,persistent_policy_and_monitor_updated=True,new_budget_seconds=0),ensure_ascii=True))
