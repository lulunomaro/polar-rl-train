from archive_cleanup_failed446_resource449_stage_once import *

def main():
    assert not archive.gitio.g('status','--porcelain') and not archive.gitio.g('diff','--cached','--name-only')
    snapshot=max(R.glob('RESOURCE_REVIEWED_ACTUAL_[0-9]*.json'),key=lambda p:int(p.stem.rsplit('_',1)[1]))
    v=json.loads(snapshot.read_bytes());assert v['source_count']==449 and v['reports'].get('E1_ATTENTION.json') is None
    save('HOURLY_RESOURCE449_ACTIVE_SNAPSHOT_OBSERVER_REVIEW.json',dict(epoch=time.time(),healthy_actual_active_snapshot=str(snapshot),status_probe_wrong_workspace_cwd_git_not_repository_retained=True,correct_repo=str(REPO),no_training_Git_budget_monitor_mutation_by_probe=True,no_new_real_stage_or_trial_needed=True))
    old=archive.gitio.refs();dest=REPO/'history/evidence'/D.name/'hourly_active_snapshot_20261012T0902_ordinary_supplement'
    rows,files=archive.capture(dest)
    subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=b''.join(p.encode()+bytes([0]) for p in files),capture_output=True,check=True)
    archive.gitio.g('commit','-m','Archive hourly own449 activity snapshot and observer cwd error')
    archive.gitio.g('push','origin','HEAD');head=archive.gitio.g('rev-parse','HEAD');archive.verify(rows,old,head)
    print(json.dumps(dict(commit=head,remote_main_verified=True,all_old_tags_preserved=len(old),saved_evidence_sources=len(rows),no_new_record_tag_or_GPU_replay=True)))

if __name__=='__main__':
    try:main()
    except BaseException:save('HOURLY_0902_GIT_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),continue_existing_objects_only_no_record_commit_tag_replay=True));raise
