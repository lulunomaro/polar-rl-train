"""Resume already-created ordinary objects; verify them and append the original push error."""
from pathlib import Path
import hashlib,json,subprocess,sys,time,traceback
C=Path(__file__).resolve().parent;W=C.parent;G=W/'polar-rl-train';R=C/'reports'
BASE='4d76444081f2342da85d49332595d296c1b6e733';ORIGINAL='77d3803c4829d1ad1f63985fa9ea4ed4605a7eb8'
DEST=G/'versions/20261020_two_linux_policy50_series/current_clearance_v4_closed44_H1only45_20261023/POST_PUSH_RECOVERY'
H=lambda b:hashlib.sha256(b).hexdigest()

def git(*args,input=None):
    p=subprocess.run(['git','-C',str(G),*args],input=input,capture_output=True)
    assert p.returncode==0,p.stderr.decode('utf8','replace')
    return p.stdout.decode('utf8').rstrip('\r\n')

def put(p,v):
    with p.open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)

def remote():
    return {x.split()[1]:x.split()[0] for x in git('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines()}

def verify_tags(tags,refs):
    assert len(tags.splitlines())==1427
    for line in tags.splitlines():
        a=line.split();assert refs[a[0]]==a[1]
        if len(a)>2:assert refs[a[0]+'^{}']==a[2]

def verify_blobs(head,paths):
    rows={p:H((G/p).read_bytes()) for p in paths}
    z=subprocess.run(['git','-C',str(G),'cat-file','--batch'],input=''.join(head+':'+p+'\n' for p in paths).encode(),capture_output=True,check=True)
    offset=0
    for p,sha in rows.items():
        end=z.stdout.index(b'\n',offset);a=z.stdout[offset:end].split();assert a[1]==b'blob';size=int(a[2]);offset=end+1
        assert H(z.stdout[offset:offset+size])==sha;offset+=size+1
    return rows

def main():
    assert git('rev-parse','HEAD')==ORIGINAL and not git('status','--porcelain') and not DEST.exists()
    put(R/'CLOSED44_EXISTING_OBJECT_PUSH_RECOVERY_STARTED_ACTUAL.json',dict(epoch=time.time(),original_existing_commit=ORIGINAL,no_original_archive_rerun_or_new_trial=True))
    tags=git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags')
    refs=remote();assert refs['refs/heads/main']==ORIGINAL;verify_tags(tags,refs)
    paths=git('diff','--name-only',BASE,ORIGINAL).splitlines();original_blobs=verify_blobs(ORIGINAL,paths)
    splits=[]
    for p in (DEST.parent/'files').rglob('*.ordered_parts.json'):
        d=json.loads(p.read_bytes());joined=hashlib.sha256();total=0
        for part in d['ordered_UTF8_parts']:
            raw=(G/part['path']).read_bytes();assert H(raw)==part['SHA'];raw.decode('utf8');joined.update(raw);total+=len(raw)
        assert total==d['archived_bytes'] and joined.hexdigest()==d['archived_SHA'];splits.append(str(p.relative_to(G)))
    errors=sorted(R.glob('append_current_clearance_v4_closed44_H1only45_ordinary_once_ORIGINAL_ERROR_*.json'));assert len(errors)==1
    result=dict(epoch=time.time(),passed=True,original_existing_ordinary_commit=ORIGINAL,base=BASE,remote_original_commit_verified=True,all_original_new_Git_blobs_verified=len(original_blobs),full_large_text_ordered_parts_verified=splits,total_old_tags=1427,all_tag_objects_and_peels_remote_exact=True,original_push_failure=str(errors[0]),existing_object_retry_succeeded_without_record_or_tag=True,nonfatal_retry_push_stderr_verbatim="remote: warning: See https://gh.io/lfs for more information.\nremote: warning: File versions/20261020_two_linux_policy50_series/current_clearance_v4_closed44_H1only45_20261023/COMPLETE_FILE_CAPTURE_INDEX.json is 78.44 MB; this is larger than GitHub's recommended maximum file size of 50.00 MB\nremote: warning: GH001: Large files detected. You may want to try Git Large File Storage - https://git-lfs.github.com.\n",no_binary_model_raw_GPU_training_host_or_ledger_access=True)
    report=R/'CLOSED44_EXISTING_OBJECT_PUSH_RECOVERY_VERIFIED_BEFORE_ERROR_SUPPLEMENT_ACTUAL.json';put(report,result)
    source_paths=[errors[0],R/'CLOSED44_EXISTING_OBJECT_PUSH_RECOVERY_STARTED_ACTUAL.json',report,Path(__file__).resolve()]
    DEST.mkdir();entries=[];added={};sys.path.insert(0,str(G/'archive_tools'));from capture_history import redact
    for p in source_paths:
        raw=p.read_bytes();text=raw.decode('utf8');clean,n=redact(text);data=clean.encode('utf8');target=DEST/p.name;target.write_bytes(data)
        rel=target.relative_to(G).as_posix();added[rel]=H(data);entries.append(dict(path=str(p),bytes=len(raw),SHA=H(raw),archive=rel,archive_SHA=H(data),redaction_count=n,mode='redacted' if n else 'full',original_retained=True))
    manifest=DEST/'SUPPLEMENT_INDEX.json';manifest.write_text(json.dumps(dict(epoch=time.time(),entries=entries,ordinary_error_receipt_followup_only=True,original_commit_retained=ORIGINAL,no_new_trial_or_repeated_capture=True),ensure_ascii=False,indent=2),encoding='utf8');added[manifest.relative_to(G).as_posix()]=H(manifest.read_bytes())
    git('add','--pathspec-from-file=-','--pathspec-file-nul',input=b'\0'.join(x.encode() for x in added)+b'\0')
    git('commit','-m','Preserve V4 window44 Git TLS push error and existing-object recovery verification')
    head=git('rev-parse','HEAD');attempts=[]
    for i in range(3):
        p=subprocess.run(['git','-C',str(G),'push','origin','HEAD:main'],capture_output=True)
        attempts.append(dict(attempt=i+1,returncode=p.returncode,stderr=p.stderr.decode('utf8','replace')))
        if p.returncode==0:break
        if i<2:time.sleep(3)
    assert p.returncode==0,attempts
    refs=remote();assert refs['refs/heads/main']==head;verify_tags(tags,refs)
    assert git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags')==tags
    assert git('merge-base',ORIGINAL,head)==ORIGINAL
    verify_blobs(head,list(added));assert not git('status','--porcelain')
    print(json.dumps(dict(remote_main=head,original_ordinary_commit=ORIGINAL,original_new_blobs_verified=len(original_blobs),large_text_parts_verified=len(splits),error_followup_files=len(added),all_old_1427_tag_objects_and_peels_unchanged=True,no_record_or_tag_or_original_helper_rerun=True,all_reports_and_original_push_error_archived=True)),flush=True)

if __name__=='__main__':
    try:main()
    except BaseException:
        put(R/('CLOSED44_EXISTING_PUSH_RECOVERY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(epoch=time.time(),error=traceback.format_exc(),HEAD=git('rev-parse','HEAD'),resume_existing_objects_only=True));raise
