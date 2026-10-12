from archive_independent449_final153_repair_stage_once import *

def main():
    assert not archive.gitio.g('status','--porcelain') and not archive.gitio.g('diff','--cached','--name-only')
    old=archive.gitio.refs();dest=REPO/'history/evidence'/D.name/'hourly153_pending_20261012T1004_ordinary_supplement'
    rows,files=archive.capture(dest)
    subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=b''.join(p.encode()+bytes([0]) for p in files),capture_output=True,check=True)
    archive.gitio.g('commit','-m','Archive hourly153 healthy pending collection and unchanged partial actual review')
    archive.gitio.g('push','origin','HEAD');head=archive.gitio.g('rev-parse','HEAD');archive.verify(rows,old,head)
    print(json.dumps(dict(commit=head,remote_main_verified=True,all_old_tags_preserved=len(old),saved_evidence_sources=len(rows),healthy_pending_no_new_trial_or_GPU_replay=True)))

if __name__=='__main__':
    try:main()
    except BaseException:save('HOURLY153_1004_GIT_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),continue_existing_objects_only_no_record_tag_commit_replay=True));raise
