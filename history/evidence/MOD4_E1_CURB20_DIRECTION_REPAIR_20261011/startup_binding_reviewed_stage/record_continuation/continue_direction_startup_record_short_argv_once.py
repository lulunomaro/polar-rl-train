from direction_io import *
import subprocess, importlib
sys.path.insert(0,str(W/'MOD4_E1_CURB20_ENTRY_REPAIR_20261011'))
import archive_entry_native_stage_once as old
REPO=W/'polar-rl-train'
DEST=REPO/'history/evidence'/D.name/'startup_binding_reviewed_stage'
ID='curb20-direction-prelearn-startup-binding-repaired'

def main():
    previous=old.refs()
    assert old.g('rev-parse','HEAD')=='554bae6594abfed327a5a1f19c4bc3a07fc053a6'
    assert not old.g('tag','--list','*'+ID)
    assert not old.g('diff','--cached','--name-only')
    assert not (REPO/'history/experiments'/('20261011-'+ID+'.json')).exists()
    assert DEST.exists() and not (R/'DIRECTION_STARTUP_STAGE_GIT_RECORDED.json').exists()
    error=save('DIRECTION_STARTUP_RECORD_WINDOWS_ARGV_REJECTED.json',dict(epoch=time.time(),error_type='OSError',winerror=206,message='The filename or extension is too long',failed_operation='subprocess.Popen record_experiment.py with hundreds of --files path arguments',record_process_started=False,commit_or_tag_created=False,prior_main=old.g('rev-parse','HEAD'),existing_capture_preserved=True,no_GPU_or_budget_change=True))
    sys.path.insert(0,str(REPO/'archive_tools'))
    from capture_history import redact
    extra=[]
    for p in (error,Path(__file__)):
        raw=p.read_bytes();clean,n=redact(raw.decode('utf8'));data=clean.encode('utf8') if n else raw
        out=DEST/'record_continuation'/p.name
        assert not out.exists();out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data)
        extra.append(dict(source_path=str(p.resolve()),bytes=len(raw),sha256=H(raw),Git_path=out.relative_to(REPO).as_posix(),archived_sha256=H(data),redactions=n))
    idx=DEST/'RECORD_CONTINUATION_CAPTURE_INDEX.json';assert not idx.exists()
    idx.write_text(json.dumps(dict(epoch=time.time(),entries=extra,original_capture_unchanged=True,only_unexecuted_record_continued=True),ensure_ascii=False,indent=2),encoding='utf8')
    files=[p.relative_to(REPO).as_posix() for p in sorted(DEST.rglob('*')) if p.is_file()]
    rec=importlib.import_module('record_experiment');original_git=rec.git
    def short_git(*args):
        if args[:2]==('add','--'):
            p=subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=b''.join(s.encode('utf8')+b'\0' for s in args[2:]),capture_output=True,check=True)
            return p.stdout.decode('utf8').strip()
        return original_git(*args)
    rec.git=short_git
    sys.argv=[str(REPO/'archive_tools/record_experiment.py'),'--id',ID,'--title','Repair CURB20 prelearning episode command state binding in isolated source423','--kind','repair','--note-file',str(R/'DIRECTION_STARTUP_STAGE_REPORT.md'),'--files',*files,'--validation','Original421 SDK/native PASSED exact SHA reused; failedsmall beforecontrol/PPO and unique cost preserved. Isolated423 startup binding precedes manifest without reset/RNG/validator changes. Small/big fullPPO PASSED; fresh same-scope strict state restore and formal own receipts are separately retained. Windows argv206 blocked record process before launch; original capture preserved and unexecuted record continued through in-process argparse and NUL stdin git pathspec. No old record/tag/commit replay or production changes.','--push']
    try:
        rec.main()
    except Exception as e:
        save('DIRECTION_STARTUP_SHORT_ARGV_RECORD_ERROR.json',dict(epoch=time.time(),error_type=type(e).__name__,message=str(e),continue_original_objects_only=True))
        raise
    tag='trial-20261011-'+ID;head=old.g('rev-parse','HEAD');obj=old.g('rev-parse',tag)
    remote={x.split()[1]:x.split()[0] for x in old.g('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines()}
    assert remote['refs/heads/main']==head and remote['refs/tags/'+tag]==obj and remote['refs/tags/'+tag+'^{}']==head
    for name,(o,c) in previous.items():assert remote[name]==o and remote.get(name+'^{}',c)==c
    save('DIRECTION_STARTUP_STAGE_GIT_RECORDED.json',dict(epoch=time.time(),tag=tag,commit=head,tagobject=obj,remote_main_tag_peeled_verified=True,push_pending=False,old_tags_preserved=len(previous),captured_files=len(files),original_windows_argv_error_preserved=True))
    print(json.dumps(dict(tag=tag,commit=head,tagobject=obj,remote_verified=True,captured_files=len(files))))

if __name__=='__main__':main()
