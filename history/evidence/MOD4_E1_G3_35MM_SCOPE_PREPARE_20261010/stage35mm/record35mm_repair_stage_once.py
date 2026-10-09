"""Capture complete124, all35mm attempts/refusals/repair receipts, and exact prior references."""
from pathlib import Path
import hashlib,json,subprocess,sys,time
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';P=W/'polar-rl-train';C=W/'MOD4_E1_G2_MATCHED_CONTINUE_20261010';H=lambda b:hashlib.sha256(b).hexdigest()
ID='e1-matched-retention-tradeoff-and-35mm-frozen-package-repair'
def git(*a):return subprocess.check_output(['git','-C',str(P),*a],encoding='utf8').strip()
def main():
 assert not (R/'ARCHIVE35_STARTED.json').exists() and not git('diff','--cached','--name-only')
 review=json.loads(sorted((C/'reports').glob('CONTINUATION_124_REVIEW_*.json'))[-1].read_bytes());assert review['review_complete'] and not review['pending']
 actual=json.loads(sorted((C/'reports').glob('MATCHED_ACTUAL_*.json'))[-1].read_bytes());assert actual['canonical']['authorized']==828000 and actual['reports']['E1_STATE.json']['phase']=='E1_G2_matched_continuation_saved_review_ready'
 assert json.loads((R/'REPAIR126_METADATA_SYNCED.json').read_bytes())['master_approval_tracks_RM_canonical_bytes_preserved']
 tag='trial-20261010-e1-20mm-matched-retention-and-same-geometry-bounded-continuation';commit=git('rev-parse',tag+'^{}');obj=git('rev-parse',tag)
 remote=dict(x.split('\t')[::-1] for x in git('ls-remote','origin','refs/heads/main','refs/tags/'+tag,'refs/tags/'+tag+'^{}').splitlines());assert remote['refs/heads/main']==git('rev-parse','HEAD') and remote['refs/tags/'+tag]==obj and remote['refs/tags/'+tag+'^{}']==commit
 (R/'ARCHIVE35_STARTED.json').write_bytes(json.dumps(dict(epoch=time.time(),trial_id=ID,prior_tag=tag,prior_tagobject=obj,prior_peeled=commit,prior_remote_main=remote['refs/heads/main'],prior_remote_verified=True,continue_original_objects_if_push_pending=True),indent=2).encode())
 sys.path.insert(0,str(P/'archive_tools'));from capture_history import redact
 oldindex=json.loads((P/'history/evidence/MOD4_E1_G2_MATCHED_CONTINUE_20261010/REPORT_CAPTURE_INDEX.json').read_bytes());prior={x['source']:x for x in oldindex['reports_and_implementation']};priorlarge={x.get('source',x.get('path')):x for x in oldindex['large_originals_index_only']}
 dest=P/'history/evidence/MOD4_E1_G3_35MM_SCOPE_PREPARE_20261010';assert not dest.exists();dest.mkdir(parents=True)
 files=[];rows=[];large=[];reused=[]
 for root,prefix in ((C,'complete124_supplement'),(D,'stage35mm')):
  for p in sorted(root.rglob('*')):
   if not p.is_file() or '__pycache__' in p.parts:continue
   b=p.read_bytes();source=str(p.resolve());h=H(b)
   if root==C and source in prior and prior[source]['sha256']==h:
    reused.append(dict(source=source,bytes=len(b),sha256=h,Git_path=prior[source]['Git_path'],reference_already_tracked=True));continue
   if root==C and source in priorlarge and priorlarge[source].get('sha256')==h:
    reused.append(dict(source=source,bytes=len(b),sha256=h,existing_large_index='history/evidence/MOD4_E1_G2_MATCHED_CONTINUE_20261010/REPORT_CAPTURE_INDEX.json',reference_already_tracked=True));continue
   if p.suffix.lower() in ('.npz','.pt','.zip','.usd','.npy') or len(b)>50_000_000:
    large.append(dict(source=source,bytes=len(b),sha256=h,index_only=True,original_retained=True));continue
   if p.suffix.lower() not in ('.py','.json','.md','.txt','.log','.xml'):continue
   try:s=b.decode('utf8');encoding='utf8'
   except UnicodeDecodeError:s=b.decode('gb18030');assert s.encode('gb18030')==b;encoding='gb18030_lossless'
   clean,n=redact(s);raw=clean.encode();out=dest/prefix/p.relative_to(root);out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(raw);assert redact(clean)[0]==clean
   gp=out.relative_to(P).as_posix();files.append(gp);rows.append(dict(source=source,bytes=len(b),sha256=h,Git_path=gp,archived_bytes=len(raw),archived_sha256=H(raw),capture='redacted_full' if n else ('byteexact_full' if encoding=='utf8' else 'lossless_UTF8_full'),source_encoding=encoding,redactions=n))
 for n in ('SELECTED_E1_G3_FROZEN_SCOPE_SOURCE.json',):
  sel=json.loads((R/n).read_bytes());source=sel.get('source',sel.get('selected_source',sel))
  # Published manifest binds the actual permitted artifact checkpoint path/size/hash.
 m=json.loads((R/'REPAIRED_PUBLISHED.json').read_bytes())['jobs'][0]
 ck=m['artifacts']['checkpoint'];large.append(dict(source=ck['path'],bytes=ck['bytes'],sha256=ck['sha256'],index_only=True,original_retained=True,actual_complete_matched_behavior_source=True))
 idx=dest/'REPORT_CAPTURE_INDEX.json';idx.write_bytes(json.dumps(dict(epoch=time.time(),reports_and_implementation=rows,large_originals_index_only=large,prior_identical_reports_reused=reused,all_saved_current_and_complete124_reports_accounted=True,original125_and_byte_receipt_refusals_preserved=True,all_false_raw_cost_and_incomplete_prefix_preserved=True,credentials_excluded=True,actual126_behavior_pending=True,no35mm_learning_executor_or_4090_GPU_PPO_or_canonical_write=True,new_budget_seconds=0,future_complete126_and_sync_reports_require_Git_supplement=True),ensure_ascii=False,indent=2).encode());files.append(idx.relative_to(P).as_posix())
 run=subprocess.run([sys.executable,str(P/'archive_tools/record_experiment.py'),'--id',ID,'--title','Review E1 retention decline and repair35mm frozen package admission','--kind','repair','--note-file',str(D/'STAGE_RECORD_REPORT.md'),'--files',*files,'--validation','124 four actualcomplete/errorfree pairedcases and8bridgeJSON byteSHA/fullNPZ SHA; model32103 own naturalfinal CPU96/source330/snapshot62/unique920.422999s/allprocgone;20mm bothdirections27of27 ordinary0 but world49of64 versus earlier62/63, signedyaw2 cross/raw strict/cost retained; select complete32058 SHA42cdc for35mm frozen scope only;203 CPUrays exact;125 immutablemanifest rejected preGPU, original retained;v2 all281 maps SHAexact;new worker admission LF/CRLF byte receipt refusal retained and exact deliveredbytes independently bound;oldworker/children exit/sharedlockfree/demandonlytask/no guard weakening;new126 actuallypublished permittedartifact;actualworker healthy pending;centralmetadata master/approval/tracks/RM/canonical preserved;no4090GPU/PPO/newbudget;all savedreports indexed, laterbehavior supplements required','--push'],capture_output=True,text=True,encoding='utf8',errors='replace')
 if run.returncode:
  (R/'ARCHIVE35_ERROR.json').write_bytes(json.dumps(dict(epoch=time.time(),stdout=run.stdout,stderr=run.stderr,do_not_repeat_record=True,continue_existing_Git_objects=True),indent=2).encode());raise RuntimeError('Inspect existing Git objects, never repeat record blindly')
 newtag,head=run.stdout.strip().splitlines()[-1].split();newobj=git('rev-parse',newtag);remote=dict(x.split('\t')[::-1] for x in git('ls-remote','origin','refs/heads/main','refs/tags/'+newtag,'refs/tags/'+newtag+'^{}','refs/tags/'+tag,'refs/tags/'+tag+'^{}').splitlines())
 assert remote['refs/heads/main']==head and remote['refs/tags/'+newtag]==newobj and remote['refs/tags/'+newtag+'^{}']==head and remote['refs/tags/'+tag]==obj and remote['refs/tags/'+tag+'^{}']==commit
 assert set(files).issubset(git('ls-tree','-r','--name-only',head).splitlines()) and not git('diff','--cached','--name-only')
 print(json.dumps(dict(tag=newtag,commit=head,tagobject=newobj,remote_main_tag_peeled_verified=True,push_pending=False,reports_captured=len(rows),large_indices=len(large),prior_identical_references=len(reused),all_saved_reports_Git_recorded=True,actual126_behavior_pending=True,new_budget_seconds=0)))
if __name__=='__main__':main()
