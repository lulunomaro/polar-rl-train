from pathlib import Path
import hashlib,json,os,subprocess,sys,time,traceback
S=Path(__file__).resolve().parent;W=S.parent;R=S/'reports';G=W/'polar-rl-train';T=W/'MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021';B=T/'H1_STEP270_REWARD_PATH_V1_20261022';BR=B/'reports'
D=G/'versions/20261022_host72_closed_tasks_cleanup_V112'
BASE='4798271e303f8605e82e5d8043b526c38c2defbb';ID='host72-approved-closed-task-retention-cleanup-v112';TAG='trial-20261022-'+ID
H=lambda b:hashlib.sha256(b).hexdigest()
def git(*args,input=None):
    p=subprocess.run(['git','-C',str(G),*args],input=input,capture_output=True)
    assert p.returncode==0,p.stderr.decode('utf8','replace')
    return p.stdout.decode('utf8').rstrip('\r\n')
def put(p,v):
    with Path(p).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def main():
    result=json.loads((R/'EXACT_ACTION_READBACK_AND_AUTHORIZED_SCOPE_CPU_VERIFIED_ACTUAL.json').read_bytes())
    assert result['passed'] and result['actual_cleanup_process_out']
    assert git('rev-parse','HEAD')==BASE and not git('status','--porcelain') and not D.exists()
    tags=git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags');assert len(tags.splitlines())==1422 and not git('tag','--list',TAG)
    put(R/'UNIQUE_ARCHIVE_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,base_HEAD=BASE,unique_new_cleanup_trial=TAG,original_reward_trial_not_repeated=True,no_training_host_GPU_or_budget_access=True))
    sys.path.insert(0,str(G/'archive_tools'));from capture_history import redact
    sources={p for p in S.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    sources|={p for p in B.glob('*V112*.py') if p.is_file()}
    sources|={p for p in BR.glob('V112*') if p.is_file()}
    sources.add(T/'reports/NEXT_ACTUAL_HUMAN_APPROVED_OLD72_CLEANUP256GB_RETURNED_V112_WORK_ORDER.json')
    D.mkdir(parents=True);entries=[];newfiles={};splits=[]
    def add(p,raw):
        p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw);newfiles[p.relative_to(G).as_posix()]=H(raw)
    for p in sorted(sources):
        assert p.resolve().is_relative_to(W.resolve()) and p.suffix.lower() not in ('.pt','.npz','.zip','.usd','.png','.gif','.so','.pyd','.pyc')
        raw=p.read_bytes();text=raw.decode('utf8');clean,n=redact(text);data=clean.encode('utf8');dest=D/'files'/p.relative_to(W)
        row=dict(path=str(p),bytes=len(raw),source_SHA=H(raw),source_mtime_ns=p.stat().st_mtime_ns,redaction_count=n,redaction_reason='credential capture-only redaction' if n else None)
        if len(data)>49_000_000:
            parts=[];offset=0;joined=hashlib.sha256()
            while offset<len(data):
                end=min(offset+24_000_000,len(data))
                while end<len(data) and data[end]&0xc0==0x80:end-=1
                assert end>offset;block=data[offset:end];block.decode('utf8');part=dest.with_name(dest.name+'.utf8part'+str(len(parts)).zfill(4)+'.txt');add(part,block);parts.append(dict(path=part.relative_to(G).as_posix(),bytes=len(block),SHA=H(block)));joined.update(block);offset=end
            assert joined.hexdigest()==H(data)
            desc=dict(source_path=str(p),source_bytes=len(raw),source_SHA=H(raw),archive_bytes=len(data),archive_SHA=H(data),ordered_UTF8_parts=parts,full_reassembly_SHA_verified=True)
            dest=dest.with_name(dest.name+'.ordered_parts.json');add(dest,json.dumps(desc,ensure_ascii=False,indent=2).encode('utf8'));row.update(mode='full_ordered_UTF8_parts',archive=dest.relative_to(G).as_posix(),archive_SHA=H(data));splits.append(desc)
        else:
            add(dest,data);row.update(mode='redacted' if n else 'full',archive=dest.relative_to(G).as_posix(),archive_SHA=H(data))
        entries.append(row)
    add(D/'COMPLETE_CAPTURE_INDEX.json',json.dumps(dict(epoch=time.time(),stage=ID,entries=entries,actual_cleanup=result,all_preapproval_source_proposals_errors_explicit_reply_and1619_full_audit_texts_preserved=True,no_model_raw_binary_rehash_or_download_for_Git=True,unique_new_human_approved_storage_repair=True),ensure_ascii=False,indent=2).encode('utf8'))
    add(D/'TRIAL_NOTE.md',(S/'TRIAL_NOTE.md').read_bytes())
    # The policy recorder commits its note/index once. The full evidence is appended in one ordinary commit to avoid Windows argument-length limits.
    args=[sys.executable,'-B',str(G/'archive_tools/record_experiment.py'),'--id',ID,'--title','Reclaim host72 storage under explicit old-window retention approval','--kind','repair','--note-file',str(D/'TRIAL_NOTE.md'),'--files',(D/'TRIAL_NOTE.md').relative_to(G).as_posix(),(D/'COMPLETE_CAPTURE_INDEX.json').relative_to(G).as_posix(),'--validation','Exact full-SHA duplicate identity, authorized old retention scope,1619 full audit reports and actual process exit verified; no training or budget change.']
    p=subprocess.run(args,capture_output=True,text=True);assert p.returncode==0,p.stdout+p.stderr
    tag_commit=git('rev-parse',TAG+'^{}');tag_object=git('rev-parse',TAG);assert git('rev-parse','HEAD')==tag_commit
    paths=list(newfiles);git('add','--pathspec-from-file=-','--pathspec-file-nul',input=b'\0'.join(x.encode('utf8') for x in paths)+b'\0')
    git('commit','-m','Archive complete approved cleanup inventory, sources, action receipts and monitor readback')
    head=git('rev-parse','HEAD');git('push','--atomic','origin','HEAD:main','refs/tags/'+TAG)
    remote={x.split()[1]:x.split()[0] for x in git('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines()}
    assert remote['refs/heads/main']==head and remote['refs/tags/'+TAG]==tag_object and remote['refs/tags/'+TAG+'^{}']==tag_commit
    current=git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags');assert len(current.splitlines())==1423
    oldrows={x.split()[0]:x for x in tags.splitlines()};newrows={x.split()[0]:x for x in current.splitlines()}
    for ref,row in oldrows.items():
        assert newrows[ref]==row;a=row.split();assert remote[ref]==a[1]
        if len(a)>2:assert remote[ref+'^{}']==a[2]
    z=subprocess.run(['git','-C',str(G),'cat-file','--batch'],input=''.join(head+':'+p+'\n' for p in newfiles).encode(),capture_output=True,check=True);offset=0
    for p,sha in newfiles.items():
        end=z.stdout.index(b'\n',offset);a=z.stdout[offset:end].split();assert a[1]==b'blob';size=int(a[2]);offset=end+1;assert H(z.stdout[offset:offset+size])==sha;offset+=size+1
    for desc in splits:
        joined=hashlib.sha256();size=0
        for part in desc['ordered_UTF8_parts']:
            raw=(G/part['path']).read_bytes();assert H(raw)==part['SHA'];joined.update(raw);size+=len(raw)
        assert size==desc['archive_bytes'] and joined.hexdigest()==desc['archive_SHA']
    assert not git('status','--porcelain')
    print(json.dumps(dict(remote_main=head,unique_cleanup_trial_tag=TAG,tag_object=tag_object,tag_peeled_commit=tag_commit,all_original1422_tag_objects_and_peels_unchanged=True,total_tags=1423,captured_full_text_files=len(entries),new_Git_files=len(newfiles),full_large_text_logs_split=len(splits),all_blobs_and_reassemblies_verified=True,actual_freed_bytes=result['actual_freed_bytes'],free_after=result['free_after'],record_experiment_ran_exactly_once=True)),flush=True)
if __name__=='__main__':
    try:main()
    except BaseException:
        put(R/('UNIQUE_ARCHIVE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(error=traceback.format_exc(),HEAD=git('rev-parse','HEAD'),tag=git('rev-parse','--verify','--quiet',TAG) if git('tag','--list',TAG) else None,resume_existing_objects_only_no_record_rerun=True));raise
