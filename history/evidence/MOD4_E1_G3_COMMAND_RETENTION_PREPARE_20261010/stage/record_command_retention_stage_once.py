"""Capture all new reports/errors/sources with one unique annotated stage."""
from pathlib import Path
import contextlib,hashlib,io,json,subprocess,sys,time,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';P=W/'polar-rl-train';L=W/'MOD4_E1_G3_LEARNING_PREPARE_20261010';H=lambda b:hashlib.sha256(b).hexdigest()
ID='e1-flat-command-retention-admitted-and-strict-rng-ownership-repaired'
def git(*a):return subprocess.check_output(['git','-C',str(P),*a],encoding='utf8').strip()
def save(n,v):
 p=R/n;assert not p.exists();p.write_bytes(json.dumps(v,ensure_ascii=False,indent=2).encode())
def main():
 assert not (R/'ARCHIVE_STARTED.json').exists() and not git('diff','--cached','--name-only')
 assert not git('status','--porcelain'), 'Do not include unrelated changes'
 assert json.loads((R/'NAMED_OWNED_REPAIR_TARGET_CPU_ADMITTED.json').read_bytes())['passed']
 assert json.loads((R/'NAMED_SCHEMA_FAILURE_ACTUAL_DECISION.json').read_bytes())['canonical_active_empty']
 head=git('rev-parse','HEAD');tags=['trial-20261010-e1-reviewed-35mm-full-contract-scope-and-short-observation-deployed','trial-20261010-e1-matched-retention-tradeoff-and-35mm-frozen-package-repair']
 refs=['refs/heads/main']+sum((['refs/tags/'+t,'refs/tags/'+t+'^{}'] for t in tags),[])
 remote=dict(x.split('\t')[::-1] for x in git('ls-remote','origin',*refs).splitlines());assert remote['refs/heads/main']==head
 originals={t:dict(commit=git('rev-parse',t+'^{}'),tagobject=git('rev-parse',t)) for t in tags}
 for t,v in originals.items():assert remote['refs/tags/'+t]==v['tagobject'] and remote['refs/tags/'+t+'^{}']==v['commit']
 save('ARCHIVE_STARTED.json',dict(epoch=time.time(),trial_id=ID,prior_remote_main=head,original_tags=originals,do_not_repeat_record_if_push_pending=True))
 # Multiple prior indices include post-stage supplements; choose byte-exact existing content.
 prior={};prior_large={}
 for p in (P/'history/evidence').rglob('*CAPTURE_INDEX*.json'):
  try:v=json.loads(p.read_bytes())
  except (ValueError,UnicodeDecodeError):continue
  for row in v.get('reports_and_implementation',[]):
   if row.get('source') and row.get('sha256') and row.get('Git_path'):
    q=P/row['Git_path']
    if q.is_file():prior[(row['source'],row['sha256'])]=row
  for row in v.get('large_originals_index_only',[]):
   if row.get('source') and row.get('sha256'):prior_large[(row['source'],row['sha256'])]=dict(row,index_Git_path=p.relative_to(P).as_posix())
 dest=P/'history/evidence'/D.name;assert not dest.exists();dest.mkdir(parents=True)
 sys.path.insert(0,str(P/'archive_tools'));from capture_history import redact
 rows=[];large=[];reuse=[];files=[]
 for root,prefix in ((D,'stage'),):
  for p in sorted(root.rglob('*')):
   if not p.is_file() or '__pycache__' in p.parts:continue
   b=p.read_bytes();source=str(p.resolve());h=H(b);old=prior.get((source,h))
   if old:
    reuse.append(dict(source=source,bytes=len(b),sha256=h,Git_path=old['Git_path'],already_recorded=True));continue
   oldlarge=prior_large.get((source,h))
   if oldlarge:
    reuse.append(dict(source=source,bytes=len(b),sha256=h,large_index=oldlarge['index_Git_path'],already_recorded=True));continue
   if p.suffix.lower() in ('.npz','.pt','.zip','.usd','.npy','.pyc') or len(b)>50_000_000 or ('remote_evidence' in p.parts and len(b)>2_000_000):
    if p.suffix.lower()!='.pyc':large.append(dict(source=source,bytes=len(b),sha256=h,index_only=True,original_retained=True))
    continue
   if p.suffix.lower() not in ('.py','.json','.md','.txt','.log','.xml','.yaml','.yml') and 'remote_evidence' not in p.parts:continue
   try:s=b.decode('utf8');encoding='utf8'
   except UnicodeDecodeError:s=b.decode('gb18030');assert s.encode('gb18030')==b;encoding='gb18030_lossless'
   clean,n=redact(s);raw=clean.encode();relative=p.relative_to(root)
   if relative.parts[0]=='scut_source':relative=Path('scut')/Path(*relative.parts[1:]);folder=dest
   else:folder=dest/prefix
   out=folder/relative;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(raw);assert redact(clean)[0]==clean
   gp=out.relative_to(P).as_posix();files.append(gp);rows.append(dict(source=source,bytes=len(b),sha256=h,Git_path=gp,archived_bytes=len(raw),archived_sha256=H(raw),capture='redacted_full' if n else ('byteexact_full' if encoding=='utf8' else 'lossless_UTF8_full'),source_encoding=encoding,redactions=n))
 for p in sorted(R.glob('*ACTUAL_*.json')):
  v=json.loads(p.read_bytes())
  large.extend(dict(source=x['path'],bytes=x['bytes'],sha256=x['sha256'],index_only=True,original_retained=True) for x in v.get('large_trace_originals',[]))
 for p in sorted(R.glob('REMOTE_EVIDENCE_COLLECTED_*.json')):
  v=json.loads(p.read_bytes())
  large.extend(dict(source=x['source'],bytes=x['bytes'],sha256=x['sha256'],index_only=True,original_retained=True,actual_remote_bytes_SHA_verified=True) for x in v['files'] if x.get('raw_data_index_only'))
 idx=dest/'REPORT_CAPTURE_INDEX.json';idx.write_bytes(json.dumps(dict(epoch=time.time(),reports_and_implementation=rows,large_originals_index_only=large,prior_identical_reports_reused=reuse,all_saved_new_scope_reports_sources_and_rejections_accounted=True,original348_signature_and353_assignment_and355_named_schema_failures_preserved=True,SCUT_previous_complete_source_review_reused_without_research_replay=True,no_permanent_anti_forgetting_claim=True,new_command_only_verified_plane_scope=True,new_budget_seconds=0,credentials_excluded=True,later_formal_behavior_sync_monitor_receipts_require_supplement=True),ensure_ascii=False,indent=2).encode());files.append(idx.relative_to(P).as_posix())
 args=[sys.executable,str(P/'archive_tools/record_experiment.py'),'--id',ID,'--title','Admit E1 conditional flat command retention and repair strict RNG ownership','--kind','repair','--note-file',str(D/'REPORT.md'),'--files',*files,'--validation','Original355 native10x300/20k24+120 and128x2 actualpassed; source348 SDK signature/353 assignment/355 strict named RNG refusals fully retained; source360 original355 byteexact plus property-owned private generator and explicit saved state, old named restore unchanged; new5 CPU ownership/disk/unknown-schema checks targetTorch2.10; numerical sampling/eligibility/35mm geometry/5family quotas/reward/LR/hardware/clock/allD0D7 unchanged; oldnative/small/clock exactreuse no replay; only new reviewed fullrestore20kx4 and300s boundedformal; actualsource freeze/ownPID/uniquecanonical noextension; future129 terrain-oldskill actualcomplete review mandatory; all savedreports/scripts/errors and largeoriginals indexed; remote main/tag/peeled verified','--push']
 # Use the installed record_experiment.main unmodified. Windows supports only
 # 32KiB argv: transport the one git-add path list through NUL-delimited stdin.
 # All credential validation, unique experiment, commit/tag/push logic remains
 # the original tool; every other git call retains its original implementation.
 import record_experiment as recorder
 original_git=recorder.git
 def pathspec_git(*a):
  if a and a[0]=='add':
   assert a[1]=='--';payload=b'\0'.join(x.encode('utf8') for x in a[2:])+b'\0'
   run=subprocess.run(['git','-C',str(P),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=payload,capture_output=True,check=True)
   return run.stdout.decode('utf8').strip()
  return original_git(*a)
 recorder.git=pathspec_git;output=io.StringIO();oldargv=sys.argv;sys.argv=args[1:]
 try:
  with contextlib.redirect_stdout(output):recorder.main()
 except Exception:
  save('ARCHIVE_ERROR.json',dict(epoch=time.time(),stdout=output.getvalue(),error=traceback.format_exc(),record_may_have_committed_do_not_repeat=True));raise
 finally:recorder.git=original_git;sys.argv=oldargv
 tag,commit=output.getvalue().strip().splitlines()[-1].split();obj=git('rev-parse',tag);r=dict(x.split('\t')[::-1] for x in git('ls-remote','origin','refs/heads/main','refs/tags/'+tag,'refs/tags/'+tag+'^{}',*refs[1:]).splitlines())
 assert r['refs/heads/main']==commit and r['refs/tags/'+tag]==obj and r['refs/tags/'+tag+'^{}']==commit
 for t,v in originals.items():assert r['refs/tags/'+t]==v['tagobject'] and r['refs/tags/'+t+'^{}']==v['commit']
 assert set(files).issubset(git('ls-tree','-r','--name-only',commit).splitlines()) and not git('diff','--cached','--name-only')
 result=dict(tag=tag,commit=commit,tagobject=obj,remote_main_tag_peeled_verified=True,push_pending=False,reports_captured=len(rows),large_indices=len(large),prior_identical_refs=len(reuse),original_two_tags_unchanged=True)
 # Saved receipt will be included in the one post-stage supplement, not an endless validation chain.
 save('STAGE_GIT_RECORDED.json',result);print(json.dumps(result))
if __name__=='__main__':
 try:main()
 except Exception:
  p=R/'ARCHIVE_CALL_ERROR.json'
  if not p.exists():p.write_bytes(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),no_repeat_of_any_committed_record=True),indent=2).encode())
  raise
