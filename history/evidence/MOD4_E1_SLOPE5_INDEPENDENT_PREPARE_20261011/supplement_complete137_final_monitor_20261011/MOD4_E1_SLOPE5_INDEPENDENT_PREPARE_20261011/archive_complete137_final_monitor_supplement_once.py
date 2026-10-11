"""Append all stage-aftercare reports to ordinary Git; final verification is tool output."""
from archive_slope_scope_stage_once import *
import traceback

def main():
    before=g('rev-parse','HEAD');assert before=='a63f54c091882daa6063c50d621dd328adc8d613'
    assert not g('status','--porcelain')
    assert json.loads((R/'COMPLETE137_FINAL_MONITOR_GIT_METADATA_SYNCED.json').read_bytes())['metadata_synced']
    tags={x.split('|')[0]:(x.split('|')[1],x.split('|')[2] or x.split('|')[1]) for x in g('for-each-ref','--format=%(refname)|%(objectname)|%(*objectname)','refs/tags').splitlines()}
    remote={x.split()[1]:x.split()[0] for x in g('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines()};assert remote['refs/heads/main']==before
    for t,(o,c) in tags.items():assert remote[t]==o and remote.get(t+'^{}',c)==c
    save('COMPLETE137_FINAL_SUPPLEMENT_STARTED.json',dict(epoch=time.time(),prior_main=before,ordinary_supplement=True,all_saved_final_monitor_Git_receipts_sync_source_captured=True,no_new_record_or_tag=True,final_verification_tool_output_only=True))
    entries,files=capture(DEST/'supplement_complete137_final_monitor_20261011')
    assert files
    p=subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],input='\0'.join(files)+'\0',capture_output=True,text=True,encoding='utf8');assert p.returncode==0,p.stderr
    g('commit','-m','Record complete slope137 final monitor, Git receipts and preserved pre-record transport rejection')
    head=g('rev-parse','HEAD')
    try:g('push','origin','HEAD:main')
    except BaseException:print(json.dumps(dict(push_pending=True,original_commit=head,do_not_recommit_or_retag=True,error=traceback.format_exc())));raise
    remote={x.split()[1]:x.split()[0] for x in g('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines()};assert remote['refs/heads/main']==head
    for t,(o,c) in tags.items():assert remote[t]==o and remote.get(t+'^{}',c)==c
    assert not g('status','--porcelain')
    tracked=set(g('ls-tree','-r','--name-only','HEAD').splitlines());assert set(files)<=tracked
    for row in entries:
        if row.get('Git_path'):
            assert row['Git_path'] in tracked
            assert H((REPO/row['Git_path']).read_bytes())==row['archived_sha256']
    indexed={(row['source_path'],row['sha256']) for row in entries}
    actual=[p for scope in (PRE,D) for p in scope.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
    missing=[str(p) for p in actual if (str(p.resolve()),H(p.read_bytes())) not in indexed];assert not missing,missing
    print(json.dumps(dict(commit=head,remote_main_verified=True,push_pending=False,all_old_tag_objects_and_peeled_unchanged=True,tag_count=len(tags),new_files=len(files),saved_scope_files_verified=len(actual),all_saved_reports_sources_monitors_receipts_errors_in_Git_or_large_original_SHA_index=True,tracked_archive_SHA_exact=True,working_tree_clean=True,final_verification_not_saved_as_new_report=True)))

if __name__=='__main__':main()
