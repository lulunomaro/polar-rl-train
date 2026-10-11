"""Capture stage-aftercare once; tool-output final verification avoids receipt recursion."""
from archive_budget005_once import *


def main():
 assert not g('status','--porcelain')
 assert json.loads((R/'FINAL_MONITOR_GIT_METADATA_SYNCED.json').read_bytes())['metadata_synced']
 tags=refs();before=g('rev-parse','HEAD')
 save('FINAL_SUPPLEMENT_STARTED.json',dict(epoch=time.time(),prior_main=before,ordinary_supplement=True,
  all_saved_Git_and_monitor_sync_receipts_captured=True,no_new_record_or_tag=True,final_verification_tool_output_only=True))
 entries,files=capture(DEST/'supplement_final_monitor_Git_20261011')
 run=subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],
    input='\0'.join(files)+'\0',capture_output=True,text=True,encoding='utf8')
 assert run.returncode==0,run.stderr
 g('commit','-m','Record seventh budget extension monitor and central Git receipt aftercare')
 head=g('rev-parse','HEAD')
 try:g('push','origin','HEAD:main')
 except BaseException:
  print(json.dumps(dict(push_pending=True,original_commit=head,no_recommit_retag=True,error=traceback.format_exc())));raise
 remote={line.split()[1]:line.split()[0] for line in g('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines()}
 assert remote['refs/heads/main']==head
 for name,(obj,peeled) in tags.items():assert remote[name]==obj and remote.get(name+'^{}',peeled)==peeled
 tracked=set(g('ls-tree','-r','--name-only','HEAD').splitlines());assert set(files)<=tracked
 for row in entries:
  if row.get('Git_path'):assert row['Git_path'] in tracked and H((REPO/row['Git_path']).read_bytes())==row['archived_sha256']
 indexed={(row['source_path'],row['sha256']) for row in entries}
 actual=[p for p in D.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
 assert all((str(p.resolve()),H(p.read_bytes())) in indexed for p in actual)
 assert not g('status','--porcelain')
 print(json.dumps(dict(commit=head,remote_main_verified=True,push_pending=False,
    all_old_tag_objects_and_peeled_unchanged=True,tag_count=len(tags),saved_scope_files_verified=len(actual),
    all_saved_reports_sources_approvals_receipts_monitors_in_Git=True,working_tree_clean=True,
    final_verification_not_saved_as_new_report=True)))


if __name__=='__main__':main()
