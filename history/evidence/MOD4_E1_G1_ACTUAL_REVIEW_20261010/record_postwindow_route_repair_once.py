"""Capture all actual attempts/reports, preserving source bytes or redaction/index evidence."""
from pathlib import Path
import json,time,hashlib,sys,subprocess,tomllib
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';P=W/'polar-rl-train'
ID='e1-g1-postwindow-regression-and-complete-wave-route-evaluator-repaired';H=lambda b:hashlib.sha256(b).hexdigest()
def git(*a):return subprocess.check_output(['git','-C',str(P),*a],encoding='utf8').strip()
def main():
 assert not (R/'ARCHIVE_STARTED.json').exists() and not git('diff','--cached','--name-only')
 assert H((P/'history/plans/MOD4_MOE_MASTER_PLAN.md').read_bytes())=='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b'
 assert json.loads((R/'POSTWINDOW_METADATA_SYNCED.json').read_bytes())['central_evidence_roundtrip']
 mon=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text(encoding='utf8'))
 assert mon['status']=='ACTIVE' and mon['rrule']=='FREQ=HOURLY;INTERVAL=2' and 'E1_FULL_ROUTE_REVIEW' in mon['prompt'][:9000]
 (R/'MONITOR_VERIFIED.json').write_text(json.dumps(dict(epoch=time.time(),automation_id=mon['id'],status=mon['status'],rrule=mon['rrule'],prompt_sha256=H(mon['prompt'].encode()),actual_postwindow_and_new_route_worker_context=True,healthy_pending_quiet=True,new_budget_seconds=0),indent=2),encoding='utf8')
 (R/'ARCHIVE_STARTED.json').write_text(json.dumps(dict(epoch=time.time(),trial_id=ID,continue_existing_objects_if_push_pending=True)),encoding='utf8')
 dest=P/'history/evidence/MOD4_E1_G1_ACTUAL_REVIEW_20261010';assert not dest.exists();dest.mkdir(parents=True)
 sys.path.insert(0,str(P/'archive_tools'));from capture_history import redact
 files=[];rows=[];large=[]
 sources=[(p,p.relative_to(D).as_posix()) for p in sorted(D.rglob('*')) if p.is_file() and '__pycache__' not in p.parts]
 prior=W/'MOD4_E1_RETENTION_REPAIR_20261009/reports/G1_ACTUAL_1791562685.json';sources.append((prior,'post_previous_stage/'+prior.name))
 for p,rel in sources:
  raw=p.read_bytes();original=raw
  if p.suffix in ('.npz','.pt','.npy','.zip','.usd') or len(raw)>50_000_000:
   large.append(dict(source=str(p.resolve()),bytes=len(raw),sha256=H(raw),kind='large_original_index_only',original_retained=True));continue
  if p.suffix not in ('.py','.json','.md','.txt','.log','.xml'):continue
  text,n=redact(raw.decode('utf8'));raw=text.encode();out=dest/rel;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(raw)
  assert redact(text)[0]==text;files.append(out.relative_to(P).as_posix());rows.append(dict(source=str(p.resolve()),source_bytes=len(original),source_sha256=H(original),Git_path=out.relative_to(P).as_posix(),archived_bytes=len(raw),archived_sha256=H(raw),capture='redacted_full' if n else 'byteexact_full',redactions=n))
 review=json.loads((R/'STAGE_REVIEW.json').read_bytes());large.append(dict(review['own_complete_source']['checkpoint'],kind='actual_formal_own_final_model32098_index',original_retained=True))
 collected=json.loads((R/'COLLECTED_1791563939.json').read_bytes())
 for publication in collected['publications']:large.append(dict(publication['source'],kind='actual_frozen_checkpoint_source_index',original_retained=True))
 for item in collected['files']:
  if item.get('large_artifact_SHA_only_in_Git') or str(item.get('name','')).endswith('.npz'):large.append(item)
 # Already tracked baseline source comparisons are referenced by actual byte SHA.
 baseline=W/'MOD4_S3_E1_ROUTE_BEHAVIOR_CONTINUATION_20261009/reports/actual_cases';tracked=git('ls-tree','-r','--name-only','HEAD').splitlines();refs=[]
 for folder in baseline.glob('*115-e1-retention32053-*'):
  for p in folder.glob('*.json'):
   raw=p.read_bytes();h=H(raw);matches=[n for n in tracked if n.endswith('/'+folder.name+'/'+p.name) and H((P/n).read_bytes())==h]
   if matches:refs.append(dict(source=str(p.resolve()),bytes=len(raw),sha256=h,already_tracked_Git_paths=matches))
   else:
    out=dest/'reused32053'/folder.name/p.name;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(raw);files.append(out.relative_to(P).as_posix());refs.append(dict(source=str(p.resolve()),bytes=len(raw),sha256=h,Git_path=out.relative_to(P).as_posix()))
 idx=dest/'REPORT_CAPTURE_INDEX.json';idx.write_text(json.dumps(dict(epoch=time.time(),reports_and_implementation=rows,large_originals_index_only=large,reused_same_SHA_reports=refs,all_saved_stage_reports_accounted=True,credentials_excluded=True,all_future_actual_behavior_or_sync_reports_require_followup_Git_capture=True),ensure_ascii=False,indent=2),encoding='utf8');files.append(idx.relative_to(P).as_posix())
 cmd=[sys.executable,str(P/'archive_tools/record_experiment.py'),'--id',ID,'--title','Audit failed G1 retention repair and restore actual complete-wave frozen evaluation','--kind','repair','--note-file',str(R/'REPORT.md'),'--files',*files,'--validation','Actual own321/CPU96/62freeze/PID final and original uniquely settled920.402443409s; five completed117/118 cases and10 bridge-byte JSON proofs with raw NPZ SHA; persistent19/64world and +1.5overspeed preserved; original80 route missing wave coverage;119 original dtype failure and neverrun candidate retained; installed SDK sources exactSHA, CPU proxy-error reproduction and zero-copy Torch fix; original worker/children actually exited/sharedlockfree before new frozen authority;120 immutable fullroute pair actual scope per reports, not claimed until complete; no PPO/canonical/runtime hotpatch/extension; all errors/reports indexed','--push']
 q=subprocess.run(cmd,capture_output=True,text=True,encoding='utf8',errors='replace')
 if q.returncode:
  (R/'ARCHIVE_ERROR.json').write_text(json.dumps(dict(epoch=time.time(),code=q.returncode,stdout=q.stdout,stderr=q.stderr,continue_existing_objects_not_rerecord=True),indent=2),encoding='utf8');raise RuntimeError('Inspect existing objects before continuing')
 tag,head=q.stdout.strip().splitlines()[-1].split();obj=git('rev-parse',tag);remote=dict(x.split('\t')[::-1] for x in git('ls-remote','origin','refs/heads/main','refs/tags/'+tag,'refs/tags/'+tag+'^{}').splitlines())
 assert remote['refs/heads/main']==head and remote['refs/tags/'+tag]==obj and remote['refs/tags/'+tag+'^{}']==head
 assert set(files).issubset(git('ls-tree','-r','--name-only',head).splitlines()) and not git('diff','--cached','--name-only')
 print(json.dumps(dict(tag=tag,commit=head,tagobject=obj,remote_main_tag_peeled_verified=True,push_pending=False,captured_files=len(rows),large_indices=len(large),all_saved_stage_reports_Git_recorded=True,new_budget_seconds=0)))
if __name__=='__main__':main()
