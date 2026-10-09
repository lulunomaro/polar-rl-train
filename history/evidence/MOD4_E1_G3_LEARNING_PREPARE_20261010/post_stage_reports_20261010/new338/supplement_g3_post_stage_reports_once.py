"""Archive new same-stage reports without replaying experiments or changing tags."""
from pathlib import Path
import hashlib,json,subprocess,sys,time,os

D=Path(__file__).resolve().parent; W=D.parent; R=D/'reports'
G=W/'MOD4_E1_G3_35MM_SCOPE_PREPARE_20261010'; P=W/'polar-rl-train'
DEST=P/'history/evidence/MOD4_E1_G3_LEARNING_PREPARE_20261010'
INDEX=DEST/'REPORT_CAPTURE_INDEX.json'
H=lambda b:hashlib.sha256(b).hexdigest()
TAGS={
 'trial-20261010-e1-reviewed-35mm-full-contract-scope-and-short-observation-deployed':('66b327e5651152b4fb42b7e47c0aca40d8ffe47e','76669fb91d68789406f4b13cc2e289d98686d6a8'),
 'trial-20261010-e1-matched-retention-tradeoff-and-35mm-frozen-package-repair':('29e1064250c5aca5f3ca96d681159a69c6d7c98b','1926640c87e19d3f4418fb1b4f7ddebf2367d3b7')}

def git(*args):
 return subprocess.check_output(['git','-C',str(P),*args],encoding='utf8').strip()

def remote_proof():
 refs=['refs/heads/main']
 for tag in TAGS:refs.extend(['refs/tags/'+tag,'refs/tags/'+tag+'^{}'])
 remote={ref:sha for sha,ref in (row.split('\t') for row in git('ls-remote','origin',*refs).splitlines())}
 for tag,(commit,obj) in TAGS.items():
  assert git('rev-parse',tag)==obj and git('rev-parse',tag+'^{}')==commit
  assert remote['refs/tags/'+tag]==obj and remote['refs/tags/'+tag+'^{}']==commit
 assert remote['refs/heads/main']==git('rev-parse','HEAD')
 return remote

def save(name,value):
 p=R/name;assert not p.exists();p.write_bytes(json.dumps(value,ensure_ascii=False,indent=2).encode())

def main():
 assert not (R/'SUPPLEMENT_STARTED.json').exists() and not git('diff','--cached','--name-only')
 prior_head=git('rev-parse','HEAD');remote_proof()
 save('SUPPLEMENT_STARTED.json',dict(epoch=time.time(),same_stage_report_supplement=True,prior_head=prior_head,no_new_trial_or_tag=True,no_GPU_PPO_or_budget_mutation=True,continue_existing_objects_if_push_pending=True))
 a=json.loads(sorted(R.glob('G3_ACTUAL_*.json'))[-1].read_bytes())
 assert not a['reports'].get('E1_ATTENTION.json') and a['canonical']['authorized']==828000
 big=a['reports']['g3_discard20k_PASSED.json'];small=a['reports']['g3_discard128_PASSED.json']
 assert big['actual_updates']==4 and big['actual_environment_steps']==1920000 and big['discarded_preflight']
 assert small['actual_updates']==2 and small['actual_environment_steps']==6144 and small['discarded_preflight']
 for item in (big,small):
  h=item['health'];assert h['actual_physics_callbacks']==h['expected_physics_callbacks'] and not h['nonfinite_observed'] and not h['unknown_task_reset_events'] and h['stop_reason'] is None and len(item['unique_completed_segment'])==1
 latest=sorted(R.glob('G3_ACTUAL_*.json'))[-1]
 tail=max(0,a['epoch']-a['canonical']['active_segment']['accounted_through_epoch']) if a['canonical']['active_segment'] else 0
 save('G3_PREFLIGHT_AND_FORMAL_DISPATCH_VERIFIED.json',dict(epoch=time.time(),actual_snapshot=dict(source=str(latest.resolve()),bytes=latest.stat().st_size,sha256=H(latest.read_bytes())),small_discarded_full_PPO=small,big_discarded_full_PPO=big,formal_actual_process=a['actual'],formal_state=a['reports']['E1_STATE.json'],active_health_may_be_prior_discard_not_formal=True,formal_startup_and_own_final_require_own_run_receipts=True,formal_127_behavior_pending=True,no_extra_PPO_after_single300s=True,remaining_after_snapshot_tail=a['canonical']['remaining']-tail,new_budget_seconds=0,not_full35mm_or_RM_graduation=True))
 index=json.loads(INDEX.read_bytes());old_index=json.loads((P/'history/evidence/MOD4_E1_G3_35MM_SCOPE_PREPARE_20261010/REPORT_CAPTURE_INDEX.json').read_bytes())
 known={}
 known_large={}
 for ix in (old_index,index):
  for row in ix['reports_and_implementation']+ix.get('prior_identical_reports_reused',[]):known[(row['source'],row['sha256'])]=row
  for row in ix['large_originals_index_only']:known_large[(row.get('source',row.get('path')),row['sha256'])]=row
 sys.path.insert(0,str(P/'archive_tools'));from capture_history import redact
 rows=[];large=[];files=[];scan=[]
 for root,prefix in ((G,'frozen35mm'),(D,'new338')):
  for p in sorted(root.rglob('*')):
   if not p.is_file() or '__pycache__' in p.parts:continue
   b=p.read_bytes();source=str(p.resolve());sha=H(b);scan.append((source,sha))
   if (source,sha) in known or (source,sha) in known_large:continue
   if p.suffix.lower() in ('.npz','.pt','.zip','.usd','.npy') or len(b)>50_000_000:
    large.append(dict(source=source,bytes=len(b),sha256=sha,index_only=True,original_retained=True));continue
   if p.suffix.lower() not in ('.py','.json','.md','.txt','.log','.xml'):continue
   try:text=b.decode('utf8');encoding='utf8'
   except UnicodeDecodeError:text=b.decode('gb18030');assert text.encode('gb18030')==b;encoding='gb18030_lossless'
   clean,n=redact(text);raw=clean.encode();assert redact(clean)[0]==clean
   out=DEST/'post_stage_reports_20261010'/prefix/p.relative_to(root);assert not out.exists();out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(raw)
   gp=out.relative_to(P).as_posix();files.append(gp)
   rows.append(dict(source=source,bytes=len(b),sha256=sha,Git_path=gp,archived_bytes=len(raw),archived_sha256=H(raw),capture='redacted_full' if n else ('byteexact_full' if encoding=='utf8' else 'lossless_UTF8_full'),source_encoding=encoding,redactions=n))
 # Only genuine path/size/previous CPU-verified hash indices for preflight weights.
 sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'));from reuse_authorized_session_transport import recover
 sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
 secret,_=recover('RM_SSH_PASSWORD');assert secret;os.environ['RM_SSH_PASSWORD']=secret;c=connect()
 try:
  with c.open_sftp() as f:
   for item in (small,big):
    cp=item['checkpoint'];size=f.stat(cp['path']).st_size;assert size>0
    large.append(dict(source=cp['path'],bytes=size,sha256=cp['sha256'],SHA_from_actual_own_CPU96_verified_receipt=True,discarded_preflight=True,index_only=True,original_retained=True))
 finally:c.close();os.environ.pop('RM_SSH_PASSWORD',None)
 index['reports_and_implementation'].extend(rows);index['large_originals_index_only'].extend(large)
 covered=set(known)|set(known_large)|{(x['source'],x['sha256']) for x in rows+large}
 assert all(pair in covered for pair in scan)
 index.setdefault('same_stage_supplements',[]).append(dict(epoch=time.time(),prior_head=prior_head,new_report_source_rows=len(rows),new_large_indices=len(large),all_saved_G_and_L_current_files_covered=True,current_phase=a['reports']['E1_STATE.json']['phase'],later_formal_final127_and_receipts_require_followup=True,original_archived_variants_preserved=True))
 INDEX.write_bytes(json.dumps(index,ensure_ascii=False,indent=2).encode());files.append(INDEX.relative_to(P).as_posix())
 subprocess.run(['git','-C',str(P),'add','--',*files],check=True)
 assert set(git('diff','--cached','--name-only').splitlines())==set(files)
 subprocess.run(['git','-C',str(P),'commit','-m','Record G3 native and discarded PPO receipts plus formal dispatch and monitor reports'],check=True,capture_output=True)
 head=git('rev-parse','HEAD')
 subprocess.run(['git','-C',str(P),'push','origin','HEAD:refs/heads/main'],check=True,capture_output=True)
 remote=remote_proof();tracked=set(git('ls-tree','-r','--name-only',head).splitlines())
 assert set(files).issubset(tracked) and not git('diff','--cached','--name-only')
 for row in index['reports_and_implementation']:
  assert row['Git_path'] in tracked and H((P/row['Git_path']).read_bytes())==row['archived_sha256']
 print(json.dumps(dict(commit=head,remote_main_verified=remote['refs/heads/main'],both_original_annotated_tags_and_peeled_commits_unchanged=True,push_pending=False,new_reports_and_source_rows=len(rows),new_large_indices=len(large),all_saved_G_and_L_reports_current_SHA_covered=True,all_archive_tracked_SHA_verified=True,formal_127_behavior_pending=True,no_new_training_or_budget_write=True)))

if __name__=='__main__':main()
