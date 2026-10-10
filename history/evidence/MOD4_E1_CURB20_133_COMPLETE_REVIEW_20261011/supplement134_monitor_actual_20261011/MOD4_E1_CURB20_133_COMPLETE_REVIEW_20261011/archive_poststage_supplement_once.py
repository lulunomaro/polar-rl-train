"""Ordinary supplement for stage receipt,134 pending snapshot and actual monitor metadata."""
from archive_complete133_slope134_stage_once import *

def main():
 assert not g('status','--porcelain') and not (R/'POSTSTAGE_SUPPLEMENT_STARTED.json').exists()
 assert json.loads((R/'POSTSTAGE134_GIT_MONITOR_METADATA_SYNCED.json').read_bytes())['metadata_synced']
 stage=json.loads((R/'STAGE_GIT_RECORDED.json').read_bytes());assert g('rev-parse','HEAD')==stage['commit']
 save('POSTSTAGE_SUPPLEMENT_STARTED.json',dict(epoch=time.time(),stage_commit=stage['commit'],ordinary_supplement_not_new_trial=True))
 entries,files=capture(DEST/'supplement134_monitor_actual_20261011')
 pathspec='\0'.join(files)+'\0'
 run=subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=pathspec.encode(),capture_output=True);assert run.returncode==0,run.stderr.decode(errors='replace')
 run=subprocess.run(['git','-C',str(REPO),'commit','-m','Archive slope134 actual pending snapshot and verified monitor metadata'],capture_output=True,text=True,encoding='utf8');assert run.returncode==0,run.stderr
 commit=g('rev-parse','HEAD')
 run=subprocess.run(['git','-C',str(REPO),'push','origin','HEAD'],capture_output=True,text=True,encoding='utf8')
 if run.returncode:
  save('POSTSTAGE_SUPPLEMENT_PUSH_ERROR.json',dict(commit=commit,returncode=run.returncode,stdout=run.stdout,stderr=run.stderr,continue_original_objects_only=True));raise RuntimeError('Continue original supplemental commit push only')
 remote={x.split()[1]:x.split()[0] for x in g('ls-remote','origin','refs/heads/main','refs/tags/'+stage['tag'],'refs/tags/'+stage['tag']+'^{}').splitlines()}
 assert remote['refs/heads/main']==commit and remote['refs/tags/'+stage['tag']]==stage['tagobject'] and remote['refs/tags/'+stage['tag']+'^{}']==stage['commit']
 tracked=set(g('ls-tree','-r','--name-only','HEAD').splitlines());assert set(files)<=tracked
 for row in entries:
  if row.get('Git_path'):assert H((REPO/row['Git_path']).read_bytes())==row['archived_sha256']
 assert not g('status','--porcelain')
 # Final verification is tool output: do not create an endless new receipt loop.
 print(json.dumps(dict(commit=commit,remote_main_verified=True,original_stage_tag_and_peeled_unchanged=True,new_files=len(files),all_current_saved_reports_sources_and_monitor_index_verified=True,push_pending=False,working_tree_clean=True)))

if __name__=='__main__':
 try:main()
 except BaseException:
  if not (R/'POSTSTAGE_SUPPLEMENT_ERROR.json').exists():save('POSTSTAGE_SUPPLEMENT_ERROR.json',dict(error=traceback.format_exc(),do_not_recommit_or_retag=True))
  raise
