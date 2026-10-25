"""Record this actual cleanup once, with complete metadata/intent/action/error texts."""
from pathlib import Path
import hashlib,json,os,subprocess,sys,time,traceback
S=Path(__file__).resolve().parent;W=S.parent;R=S/'reports';G=W/'polar-rl-train';T=W/'MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021';B=T/'H1_STEP270_REWARD_PATH_V1_20261022'
ID='mod4-obsolete-expert-replay-storage-pruning';TAG='trial-20261025-'+ID;BASE='054d89431e881eaa0460676ba4f52e9db8ddb1a3'
D=G/'versions/20261025_obsolete_expert_replay_storage_pruning'
H=lambda raw:hashlib.sha256(raw).hexdigest()
def git(*args,input=None):
    q=subprocess.run(['git','-C',str(G),*args],input=input,capture_output=True);assert q.returncode==0,q.stderr.decode('utf8','replace');return q.stdout.decode('utf8').rstrip('\r\n')
def put(p,v):
    with p.open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def main():
    assert not D.exists() and not git('tag','--list',TAG) and git('rev-parse','HEAD')==BASE and not git('status','--porcelain')
    tags=git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags');assert len(tags.splitlines())==1435
    summary=json.loads((R/'ALL_ACTUAL_REPLAY_CACHE_CLEANUP_INDEPENDENT_CPU_SUMMARY_ACTUAL.json').read_bytes());assert summary['passed']
    put(R/'UNIQUE_CLEANUP_ARCHIVE_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),base_HEAD=BASE,old_tag_count=1435,ID=ID))
    sys.path.insert(0,str(T/'H1_STEP270_TUCK_V3_FIRST_CLOSED39_REPLAY_20261023'));from capture_index_ordered_parts_v1 import read_capture_index,write_capture_index
    prior_path=G/'versions/20261020_two_linux_policy50_series/post67_precision_benchmark_failed_closed_CPU_fixed_disk25_20261025/COMPLETE_FILE_CAPTURE_INDEX.json'
    prior=read_capture_index(prior_path,G);prior_ref=dict(path=prior_path.relative_to(G).as_posix(),descriptor_SHA=H(prior_path.read_bytes()),complete_entries=len(prior['entries']),source_commit=BASE);del prior
    sys.path.insert(0,str(G/'archive_tools'));from capture_history import redact
    D.mkdir();entries=[];newfiles={};splits=[]
    def add(p,data):
        p.parent.mkdir(parents=True,exist_ok=True)
        with p.open('xb') as f:f.write(data)
        newfiles[p.relative_to(G).as_posix()]=H(data)
    extras=[T/name for name in json.loads((R/'THIS_STAGE_EXTERNAL_SOURCE_PATHS_ACTUAL.json').read_bytes())['relative_to_T']]
    paths=sorted(set([p for p in S.rglob('*') if p.is_file() and '__pycache__' not in p.parts]+extras))
    for p in paths:
        st=p.stat();dest=D/'files'/p.relative_to(W);row=dict(path=str(p),bytes=st.st_size,source_mtime_ns=st.st_mtime_ns,original_retained=True)
        if st.st_size<=49_000_000:
            raw=p.read_bytes();text=raw.decode('utf8');clean,n=redact(text);data=clean.encode('utf8');add(dest,data);row.update(SHA=H(raw),archive_SHA=H(data),mode='redacted' if n else 'full',redaction_count=n)
        else:
            original=hashlib.sha256();archived=hashlib.sha256();parts=[];n=0;total=0
            with p.open('rb') as f:
                pending=b''
                while True:
                    chunk=f.read(24_000_000)
                    if not chunk and not pending:break
                    raw=pending+chunk;end=len(raw)
                    if chunk:
                        # Keep a possible partial UTF8 character for the next block.
                        while end and raw[end-1]&0xc0==0x80:end-=1
                        if end and raw[end-1]&0x80:end-=1
                    block=raw[:end] if chunk else raw;pending=raw[end:] if chunk else b''
                    if not block:continue
                    original.update(block);clean,count=redact(block.decode('utf8'));n+=count;data=clean.encode('utf8');archived.update(data);total+=len(data)
                    part=dest.with_name(dest.name+'.utf8part'+str(len(parts)).zfill(4)+'.txt');add(part,data);parts.append(dict(path=part.relative_to(G).as_posix(),bytes=len(data),SHA=H(data)))
            desc=dict(original_path=str(p),original_bytes=st.st_size,original_SHA=original.hexdigest(),archived_bytes=total,archived_SHA=archived.hexdigest(),ordered_UTF8_parts=parts,full_reassembled_SHA_verified=True,redaction_count=n)
            dest=dest.with_name(dest.name+'.ordered_parts.json');add(dest,json.dumps(desc,ensure_ascii=False,indent=2).encode());row.update(SHA=original.hexdigest(),archive_SHA=archived.hexdigest(),mode='full_ordered_UTF8_parts',redaction_count=n);splits.append(desc)
        assert p.stat().st_size==st.st_size and p.stat().st_mtime_ns==st.st_mtime_ns
        row['archive']=dest.relative_to(G).as_posix();entries.append(row)
    index=dict(epoch=time.time(),kind='human_lower_threshold_obsolete_expert_replay_cleanup_actual',entries=entries,previous_complete_capture=prior_ref,cleanup_result=summary,historical_inventories_do_not_assert_deleted_raw_still_exists=True,all_original_failed_attempts_and_lower_threshold_authorizations_preserved=True,no_raw_model_rehash_or_training_for_archival=True)
    write_capture_index(D/'COMPLETE_FILE_CAPTURE_INDEX.json',index,add,splits,G)
    add(D/'EXTERNAL_REPLAY_DISPOSITION_INDEX.json',json.dumps(summary['external_replay_disposition'],ensure_ascii=False,indent=2).encode())
    import record_experiment as rec
    def recgit(*args):
        if args[:2]==('add','--'):return git('add','--pathspec-from-file=-','--pathspec-file-nul',input=b'\0'.join(x.encode() for x in args[2:])+b'\0')
        if args[:2]==('tag','-a'):return git('tag','-a',TAG,'-F',str(R/'ACTUAL_CLEANUP_UNIQUE_STAGE_NOTE.md'))
        if args and args[0]=='push':return git('push','--atomic','origin','HEAD:main','refs/tags/'+TAG)
        return git(*args)
    rec.git=recgit
    sys.argv=['record_experiment.py','--id',ID,'--title','Prune obsolete expert replay originals and closed task caches under lowered human retention threshold','--kind','diagnostic','--note-file',str(R/'ACTUAL_CLEANUP_UNIQUE_STAGE_NOTE.md'),'--files',*newfiles,'--validation','Three GPT-6.1 Sol xhigh agents audited saved metadata; exact per-file identity and closure guards, immutable intents/actions, retained first/last/anomaly representatives, original errors preserved; independent receipt-set verification; no training or canonical accounting change.','--push'];rec.main()
    head=git('rev-parse','HEAD');remote={x.split()[1]:x.split()[0] for x in git('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines()}
    assert remote['refs/heads/main']==head and remote['refs/tags/'+TAG]==git('rev-parse',TAG) and remote['refs/tags/'+TAG+'^{}']==head
    for line in tags.splitlines():
        a=line.split();assert remote[a[0]]==a[1]
        if len(a)>2:assert remote[a[0]+'^{}']==a[2]
    assert len(git('tag','--list').splitlines())==1436
    for rel,sha in newfiles.items():
        p=subprocess.Popen(['git','-C',str(G),'show',head+':'+rel],stdout=subprocess.PIPE,stderr=subprocess.PIPE);h=hashlib.sha256()
        while True:
            block=p.stdout.read(8*1024**2)
            if not block:break
            h.update(block)
        assert p.wait()==0 and h.hexdigest()==sha
    for desc in splits:
        h=hashlib.sha256();size=0
        for x in desc['ordered_UTF8_parts']:
            data=(G/x['path']).read_bytes();assert H(data)==x['SHA'];h.update(data);size+=len(data)
        assert size==desc['archived_bytes'] and h.hexdigest()==desc['archived_SHA']
    assert not git('status','--porcelain')
    print(json.dumps(dict(remote_main=head,tag=TAG,tag_object=git('rev-parse',TAG),peeled=head,total_tags=1436,all1435_old_objects_and_peels_unchanged=True,source_text_entries=len(entries),new_Git_files=len(newfiles),large_complete_texts=len(splits),all_committed_blobs_and_lossless_parts_verified=True,workingtree_clean=True,no_archive_driven_raw_PT_hash_or_hostquery=True)),flush=True)
if __name__=='__main__':
    try:main()
    except BaseException:
        put(R/('ARCHIVE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(epoch=time.time(),error=traceback.format_exc(),HEAD=git('rev-parse','HEAD'),resume_existing_objects_only_never_re_record_or_re_tag=True));raise
