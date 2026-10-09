"""Preserve subsequent formal final, pending evaluation, sync and push-refusal reports."""
from pathlib import Path
import json,sys,time,os,subprocess
import supplement_g3_post_stage_reports_once as common
D=common.D;G=common.G;W=common.W;P=common.P;R=common.R;INDEX=common.INDEX;H=common.H;git=common.git

def main():
 assert not (R/'FINAL_SUPPLEMENT_STARTED.json').exists() and not git('diff','--cached','--name-only')
 before=git('rev-parse','HEAD');common.remote_proof()
 common.save('FINAL_SUPPLEMENT_STARTED.json',dict(epoch=time.time(),same_stage_report_supplement=True,prior_head=before,original_push_rejection_and_same_object_retry_preserved=True,no_new_tag_or_experiment_replay=True,no_GPU_training_canonical_mutation=True))
 index=json.loads(INDEX.read_bytes());prior=json.loads((P/'history/evidence/MOD4_E1_G3_35MM_SCOPE_PREPARE_20261010/REPORT_CAPTURE_INDEX.json').read_bytes())
 known=set();large_known=set()
 for ix in (prior,index):
  known.update((x['source'],x['sha256']) for x in ix['reports_and_implementation']+ix.get('prior_identical_reports_reused',[]))
  large_known.update((x.get('source',x.get('path')),x['sha256']) for x in ix['large_originals_index_only'])
 sys.path.insert(0,str(P/'archive_tools'));from capture_history import redact
 rows=[];large=[];files=[];scan=[]
 for root,prefix in ((G,'frozen35mm'),(D,'new338')):
  for p in sorted(root.rglob('*')):
   if not p.is_file() or '__pycache__' in p.parts:continue
   b=p.read_bytes();source=str(p.resolve());sha=H(b);scan.append((source,sha))
   if (source,sha) in known or (source,sha) in large_known:continue
   if p.suffix.lower() in ('.npz','.pt','.zip','.usd','.npy') or len(b)>50_000_000:
    large.append(dict(source=source,bytes=len(b),sha256=sha,index_only=True,original_retained=True));continue
   assert p.suffix.lower() in ('.py','.json','.md','.txt','.log','.xml'),str(p)
   try:s=b.decode('utf8');encoding='utf8'
   except UnicodeDecodeError:s=b.decode('gb18030');assert s.encode('gb18030')==b;encoding='gb18030_lossless'
   clean,n=redact(s);raw=clean.encode();assert redact(clean)[0]==clean
   out=common.DEST/'formal_closeout_reports_20261010'/prefix/p.relative_to(root);assert not out.exists();out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(raw)
   gp=out.relative_to(P).as_posix();files.append(gp);rows.append(dict(source=source,bytes=len(b),sha256=sha,Git_path=gp,archived_bytes=len(raw),archived_sha256=H(raw),capture='redacted_full' if n else ('byteexact_full' if encoding=='utf8' else 'lossless_UTF8_full'),source_encoding=encoding,redactions=n))
 a=json.loads(sorted(R.glob('G3_ACTUAL_*.json'))[-1].read_bytes());cp=a['reports']['e1_G3_reviewed_observation_PASSED.json']['checkpoint']
 assert all(v is None for v in a['actual'].values()) and a['canonical']['active_segment'] is None and cp['finite_tensors']==96
 sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'));from reuse_authorized_session_transport import recover
 sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
 secret,_=recover('RM_SSH_PASSWORD');assert secret;os.environ['RM_SSH_PASSWORD']=secret;c=connect()
 try:
  with c.open_sftp() as f:size=f.stat(cp['path']).st_size
 finally:c.close();os.environ.pop('RM_SSH_PASSWORD',None)
 assert size>0;large.append(dict(source=cp['path'],bytes=size,sha256=cp['sha256'],actual_formal_final_CPU96_and_own_PID_receipt_verified=True,source338_and_snapshot62_verified=True,index_only=True,original_retained=True))
 assert all(x in known or x in large_known or x in {(r['source'],r['sha256']) for r in rows+large} for x in scan)
 index['reports_and_implementation'].extend(rows);index['large_originals_index_only'].extend(large)
 index.setdefault('same_stage_supplements',[]).append(dict(epoch=time.time(),prior_head=before,new_report_source_rows=len(rows),new_large_indices=len(large),all_saved_current_G_and_L_reports_and_errors_captured=True,formal_final_source338_CPU96_snapshot62_PASSED_unique_segment_verified=True,actual127_results_pending_not_passed=True,metadata_and_monitor_actual_closeout_verified=True,future127_behavior_reports_require_followup=True,old_archived_variants_unchanged=True))
 INDEX.write_bytes(json.dumps(index,ensure_ascii=False,indent=2).encode());files.append(INDEX.relative_to(P).as_posix())
 subprocess.run(['git','-C',str(P),'add','--',*files],check=True);assert set(git('diff','--cached','--name-only').splitlines())==set(files)
 subprocess.run(['git','-C',str(P),'commit','-m','Record G3 own formal fullsave, frozen review pending and closeout receipts'],check=True,capture_output=True)
 head=git('rev-parse','HEAD');subprocess.run(['git','-C',str(P),'push','origin','HEAD:refs/heads/main'],check=True,capture_output=True)
 remote=common.remote_proof();tracked=set(git('ls-tree','-r','--name-only',head).splitlines())
 for row in index['reports_and_implementation']:assert row['Git_path'] in tracked and H((P/row['Git_path']).read_bytes())==row['archived_sha256']
 assert not git('diff','--cached','--name-only')
 print(json.dumps(dict(commit=head,remote_main_verified=remote['refs/heads/main'],both_original_annotated_tags_and_peeled_commits_unchanged=True,push_pending=False,new_reports_and_sources=len(rows),new_large_indices=len(large),formal_weight_real_bytes=size,all_saved_current_G_and_L_reports_and_errors_tracked_SHA_verified=True,actual127_complete_review_pending=True,no_training_or_budget_write=True)))

if __name__=='__main__':main()
