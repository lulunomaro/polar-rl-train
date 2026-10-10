"""Capture all new reports/errors/sources with one unique annotated stage."""
from pathlib import Path
import contextlib,hashlib,io,json,subprocess,sys,time,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';P=W/'polar-rl-train';L=W/'MOD4_E1_G3_LEARNING_PREPARE_20261010';H=lambda b:hashlib.sha256(b).hexdigest()
ID='e1-35mm-regression-scut-retention-audit-and-paired-route-diagnosis'
def git(*a):return subprocess.check_output(['git','-C',str(P),*a],encoding='utf8').strip()
def save(n,v):
 p=R/n;assert not p.exists();p.write_bytes(json.dumps(v,ensure_ascii=False,indent=2).encode())
def main():
 assert not (R/'ARCHIVE_STARTED.json').exists() and not git('diff','--cached','--name-only')
 assert not git('status','--porcelain'), 'Do not include unrelated changes'
 review=json.loads((L/'reports/CANDIDATE_127_REVIEW_1791592441.json').read_bytes());assert review['review_complete']
 assert json.loads((R/'MATCHED_RETENTION_METADATA_SYNCED.json').read_bytes())['canonical_bytes_preserved']
 assert json.loads((R/'PAIRED_APPROACH_PUBLISHED.json').read_bytes())['no_4090_PPO_or_learning_launch']
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
 for root,prefix in ((D,'stage'),(L,'g3_learning_poststage')):
  for p in sorted(root.rglob('*')):
   if not p.is_file() or '__pycache__' in p.parts:continue
   b=p.read_bytes();source=str(p.resolve());h=H(b);old=prior.get((source,h))
   if old:
    reuse.append(dict(source=source,bytes=len(b),sha256=h,Git_path=old['Git_path'],already_recorded=True));continue
   oldlarge=prior_large.get((source,h))
   if oldlarge:
    reuse.append(dict(source=source,bytes=len(b),sha256=h,large_index=oldlarge['index_Git_path'],already_recorded=True));continue
   if p.suffix.lower() in ('.npz','.pt','.zip','.usd','.npy','.pyc') or len(b)>50_000_000:
    if p.suffix.lower()!='.pyc':large.append(dict(source=source,bytes=len(b),sha256=h,index_only=True,original_retained=True))
    continue
   if p.suffix.lower() not in ('.py','.json','.md','.txt','.log','.xml','.yaml','.yml'):continue
   try:s=b.decode('utf8');encoding='utf8'
   except UnicodeDecodeError:s=b.decode('gb18030');assert s.encode('gb18030')==b;encoding='gb18030_lossless'
   clean,n=redact(s);raw=clean.encode();relative=p.relative_to(root)
   if relative.parts[0]=='scut_source':relative=Path('scut')/Path(*relative.parts[1:]);folder=dest
   else:folder=dest/prefix
   out=folder/relative;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(raw);assert redact(clean)[0]==clean
   gp=out.relative_to(P).as_posix();files.append(gp);rows.append(dict(source=source,bytes=len(b),sha256=h,Git_path=gp,archived_bytes=len(raw),archived_sha256=H(raw),capture='redacted_full' if n else ('byteexact_full' if encoding=='utf8' else 'lossless_UTF8_full'),source_encoding=encoding,redactions=n))
 for job in json.loads((R/'PAIRED_APPROACH_PUBLISHED.json').read_bytes())['jobs']:
  for kind,item in job['artifacts'].items():large.append(dict(source=item['path'],bytes=item['bytes'],sha256=item['sha256'],index_only=True,original_retained=True,actual_delivered_SHA_verified=True,kind=kind))
 idx=dest/'REPORT_CAPTURE_INDEX.json';idx.write_bytes(json.dumps(dict(epoch=time.time(),reports_and_implementation=rows,large_originals_index_only=large,prior_identical_reports_reused=reuse,all_saved_stage_and_new_L_reports_accounted=True,actual127_complete_review_preserved=True,SCUT_public_source_pin='1a26356d6f591734d4f6f666f5cead1a6925da67',oldfalse_raw_cost_and_all_refusals_preserved=True,paired128_current_stage_actual_only=True,new_command_CPU_candidate_not_SDK_PPO_admitted=True,no_new_learning_or_budget_extension=True,credentials_excluded=True,later_results_sync_monitor_receipts_require_supplement=True),ensure_ascii=False,indent=2).encode());files.append(idx.relative_to(P).as_posix())
 args=[sys.executable,str(P/'archive_tools/record_experiment.py'),'--id',ID,'--title','Review E1 regression and SCUT retention sampling; deploy paired frozen route diagnostic','--kind','repair','--note-file',str(D/'REPORT.md'),'--files',*files,'--validation','127 complete4case bridgebytes/fullNPZ/root30q-recipes/contact-COM/hardware originaltolerances; world62to56/64,negative4pi5to2/8,35mm forwardfull17to13/27 preserved; SCUT current pinned public implementation plus actualJuly30params distinct proof levels;128 newapproach040 only/15s/full10wave/twowheel200mmsupport/samepairedinitials/noPPO,281manifestSHAexact/only2memberschanged;20s predeployreject,CRCreader/locklocatorrefusals and independent repairs preserved; CPU command sampler/math/named RNG disk verified only; central master-RM-approval-tracks-canonical byteexact/new0; all saved reports captured byindex, priorSHArefs reused and largeNPZZIPweights indexonly','--push']
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
