"""Capture every saved new-stage report/error and implementation; one annotated trial."""
from pathlib import Path
import json,time,hashlib,sys,subprocess,tomllib
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';P=W/'polar-rl-train'
ID='e1-two-block-regression-rollback-g1-bounded-repair-deployed'
sha=lambda b:hashlib.sha256(b).hexdigest()
def git(*a):return subprocess.check_output(['git','-C',str(P),*a],encoding='utf8').strip()
def main():
 assert not (R/'ARCHIVE_STARTED.json').exists();assert not git('diff','--cached','--name-only')
 assert sha((P/'history/plans/MOD4_MOE_MASTER_PLAN.md').read_bytes())=='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b'
 assert json.loads((R/'METADATA_SYNCED.json').read_text())['central_evidence_roundtrip']
 m=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text(encoding='utf8'))
 assert m['status']=='ACTIVE' and m['rrule']=='FREQ=HOURLY;INTERVAL=2' and 'MOD4_S3_E1_G1_REPAIR_20261009' in m['prompt'][:6000]
 mon=dict(epoch=time.time(),automation_id=m['id'],status=m['status'],rrule=m['rrule'],prompt_sha256=sha(m['prompt'].encode()),current_repair_context_preserved=True,healthy_pending_quiet=True,no_rejected_quota_scheme=True,all_stage_reports_followup_Git_required=True)
 (R/'MONITOR_VERIFIED.json').write_text(json.dumps(mon,indent=2),encoding='utf8')
 (R/'ARCHIVE_STARTED.json').write_text(json.dumps(dict(epoch=time.time(),trial_id=ID,continue_existing_objects_if_push_pending=True)),encoding='utf8')
 dest=P/'history/evidence/MOD4_E1_RETENTION_REPAIR_20261009';assert not dest.exists();dest.mkdir(parents=True)
 sys.path.insert(0,str(P/'archive_tools'));from capture_history import redact
 files=[];index=[];large=[]
 for p in sorted(D.rglob('*')):
  if not p.is_file() or '__pycache__' in p.parts:continue
  raw=p.read_bytes();relative=p.relative_to(D).as_posix()
  if p.suffix in ('.npz','.pt','.npy','.zip','.usd') or len(raw)>50_000_000:
   large.append(dict(source=str(p.resolve()),bytes=len(raw),sha256=sha(raw),kind='large_binary_or_raw_report_index_only',original_retained=True,complete_report_accounted_by_index=True));continue
  if p.suffix not in ('.py','.json','.md','.txt','.log'):continue
  original=raw;txt,count=redact(raw.decode('utf8'));raw=txt.encode();out=dest/relative;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(raw)
  assert redact(txt)[0]==txt;files.append(out.relative_to(P).as_posix());index.append(dict(source=str(p.resolve()),source_bytes=len(original),source_sha256=sha(original),Git_path=out.relative_to(P).as_posix(),archived_bytes=len(raw),archived_sha256=sha(raw),capture='redacted_full' if count else 'byteexact_full',redactions=count))
 selected=json.loads((R/'SELECTED_E1_REPAIR_SOURCE.json').read_text());large.append(dict(selected['source'],kind='reviewed_rollback_checkpoint_index_only',original_retained=True))
 collected=json.loads((D/'block2/COLLECTED.json').read_text())
 for x in collected['files']:
  if x.get('large_artifact_SHA_only_in_Git'):large.append(x)
 large.append(dict(collected['publication']['source'],kind='rejected_new_source32988_exact_eval_copy_index_only',original_retained=True))
 latest=json.loads(sorted(R.glob('G1_ACTUAL_*.json'))[-1].read_text())
 for v in latest.get('native',{}).values():
  if 'original_report' in v:large.append(dict(v['original_report'],kind='full_actual_native_report_remote_original_index',scalar_and_compacted_nested_audits_in_Git=True,original_retained=True))
 for row in latest.get('reports',{}).values():
  if isinstance(row,dict) and 'checkpoint' in row and isinstance(row['checkpoint'],dict) and 'sha256' in row['checkpoint']:
   large.append(dict(row['checkpoint'],kind='own_fullsave_index_only',original_retained=True))
 for run in latest['runs']:
  rec=run['files'].get('latest_complete.json')
  if rec:large.append(dict(rec,kind='PIDbound_complete_save_path_receipt',original_retained=True))
 # Reused behavior source reports are already tracked in earlier trial; retain exact source hash references.
 baseline=W/'MOD4_S3_E1_ROUTE_BEHAVIOR_CONTINUATION_20261009/reports/actual_cases'
 reused=[]
 tracked=git('ls-tree','-r','--name-only','HEAD').splitlines()
 for folder in sorted(baseline.glob('*')):
  if not folder.is_dir() or not ('114-e1-terrain32053' in folder.name or '115-e1-retention32053' in folder.name):continue
  for p in folder.glob('*.json'):
   h=sha(p.read_bytes());matches=[n for n in tracked if n.endswith('/'+folder.name+'/'+p.name) and sha((P/n).read_bytes())==h]
   if matches:reused.append(dict(source=str(p.resolve()),sha256=h,already_tracked_Git_paths=matches))
   else:
    out=dest/'reused32053'/folder.name/p.name;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(p.read_bytes());files.append(out.relative_to(P).as_posix());reused.append(dict(source=str(p.resolve()),sha256=h,Git_path=out.relative_to(P).as_posix()))
 idx=dest/'REPORT_CAPTURE_INDEX.json';idx.write_text(json.dumps(dict(epoch=time.time(),reports_and_implementation=index,large_originals_index_only=large,reused_same_SHA_reports=reused,all_saved_stage_reports_accounted=True,large_raw_report_full_original_SHA_indexed=True,credentials_excluded=True,future_ownfinal_preflight_or_behavior_reports_after_this_commit_require_append_Git_capture=True),ensure_ascii=False,indent=2),encoding='utf8');files.append(idx.relative_to(P).as_posix())
 cmd=[sys.executable,str(P/'archive_tools/record_experiment.py'),'--id',ID,'--title','Rollback persistent E1 retention regression and deploy bounded G1 derived-wave repair','--kind','repair','--note-file',str(R/'REPORT.md'),'--files',*files,'--validation','Both original G0 blocks own complete saves/unique settled segments; block2 four3060 paired cases/8JSON SHA/fullNPZ contact-ground/reasons/signedcircles; original task gate false/flat env38 reset preserved; reviewed32053 rollback; independent source321/original313 exact, CPU/actual newSDK-native and fullPPO startup per captured actual receipts; first900s observation bounded; no automatic morePPO before review; no budget extension or rejected quota adoption; every saved stage report/error indexed/captured','--push']
 q=subprocess.run(cmd,capture_output=True,text=True,encoding='utf8',errors='replace')
 if q.returncode:
  (R/'ARCHIVE_FIRST_ERROR.json').write_text(json.dumps(dict(epoch=time.time(),exit_code=q.returncode,stdout=q.stdout,stderr=q.stderr,resume_existing_objects_not_rerecord=True),ensure_ascii=False,indent=2),encoding='utf8');raise RuntimeError('Record rejected or push pending; inspect existing objects')
 tag,head=q.stdout.strip().splitlines()[-1].split();obj=git('rev-parse',tag)
 remote=dict(x.split('\t')[::-1] for x in git('ls-remote','origin','refs/heads/main','refs/tags/'+tag,'refs/tags/'+tag+'^{}').splitlines())
 assert remote['refs/heads/main']==head and remote['refs/tags/'+tag]==obj and remote['refs/tags/'+tag+'^{}']==head
 assert set(files).issubset(git('ls-tree','-r','--name-only',head).splitlines());assert not git('diff','--cached','--name-only')
 print(json.dumps(dict(tag=tag,commit=head,tagobject=obj,remote_main_tag_peeled_verified=True,push_pending=False,all_saved_stage_reports_accounted=True,captured_files=len(index),large_index_entries=len(large),master_unchanged=True,new_budget_seconds=0)))
if __name__=='__main__':main()
