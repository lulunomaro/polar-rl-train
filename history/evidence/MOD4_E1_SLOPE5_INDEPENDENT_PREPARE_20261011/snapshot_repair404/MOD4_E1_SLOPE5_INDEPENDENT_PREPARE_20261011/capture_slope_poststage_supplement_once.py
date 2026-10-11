from archive_slope_scope_stage_once import *
def main():
 assert not g('status','--porcelain');git=json.loads((R/'STAGE_GIT_RECORDED.json').read_bytes());assert git['remote_main_tag_peeled_verified']
 save('POSTSTAGE_SUPPLEMENT_STARTED.json',dict(epoch=time.time(),original_stage_commit=git['commit'],original_tagobject=git['tagobject'],ordinary_supplement_only=True))
 dest=DEST/'supplement_native_preflight_monitor_20261011';entries,files=capture(dest)
 stdin='\0'.join(files)+'\0';p=subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=stdin,capture_output=True,text=True,encoding='utf8');assert p.returncode==0,p.stderr
 run=subprocess.run(['git','-C',str(REPO),'commit','-m','Archive slope5 native admission, preflight snapshots, metadata and monitor receipts'],capture_output=True,text=True,encoding='utf8');assert run.returncode==0,run.stderr
 commit=g('rev-parse','HEAD');run=subprocess.run(['git','-C',str(REPO),'push','origin','main'],capture_output=True,text=True,encoding='utf8')
 if run.returncode:save('SUPPLEMENT_PUSH_ERROR.json',dict(commit=commit,returncode=run.returncode,stdout=run.stdout,stderr=run.stderr,only_continue_original_objects_no_new_commit=True));raise RuntimeError('Original supplement push pending')
 remote={x.split()[1]:x.split()[0] for x in g('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines()};assert remote['refs/heads/main']==commit and remote['refs/tags/'+git['tag']]==git['tagobject'] and remote['refs/tags/'+git['tag']+'^{}']==git['commit']
 tracked=set(g('ls-tree','-r','--name-only','HEAD').splitlines());assert set(files)<=tracked and not g('status','--porcelain')
 for row in entries:
  if row.get('Git_path'):assert H((REPO/row['Git_path']).read_bytes())==row['archived_sha256']
 # Final tool output only avoids an unbounded chain of report-about-report commits.
 print(json.dumps(dict(commit=commit,original_stage_tag=git['tag'],original_tagobject=git['tagobject'],remote_main_tag_peeled_verified=True,new_files=len(files),same_SHA_refs=sum(x['capture']=='existing_same_SHA_Git_reference' for x in entries),large_indices=sum('index_only' in x['capture'] for x in entries),all_saved_reports_through_this_snapshot_tracked=True,push_pending=False,worktree_clean=True,later_real_training_results_need_next_supplement=True)))
if __name__=='__main__':main()
