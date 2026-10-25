"""Archive this research review once; no T2-z execution, downloads or training."""
from pathlib import Path
import hashlib,json,subprocess,sys,time,traceback
Q=Path(__file__).resolve().parent;T=Q.parent;W=T.parent;R=Q/'reports';G=W/'polar-rl-train';S=W/'MOD4_REPLAY_WASTE_AUDIT_CLEANUP_AUTHORIZED_20261025'
D=G/'versions/20261025_t2z_future_training_feasibility_review';ID='mod4-t2z-future-training-feasibility-review';TAG='trial-20261025-'+ID
H=lambda x:hashlib.sha256(x).hexdigest()
def git(*args,input=None):
    q=subprocess.run(['git','-C',str(G),*args],input=input,capture_output=True);assert q.returncode==0,q.stderr.decode('utf8','replace');return q.stdout.decode().rstrip('\r\n')
def put(p,v):
    with p.open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def main():
    cfg=json.loads((R/'ROOT_FEASIBILITY_UNIQUE_ARCHIVE_CONFIGURATION_ACTUAL.json').read_bytes())
    assert git('rev-parse','HEAD')==cfg['base_HEAD'] and not git('status','--porcelain') and not git('tag','--list',TAG) and not D.exists()
    tags=git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags');assert len(tags.splitlines())==1436
    assert (R/'FEASIBILITY_REVIEW_ACTUAL.md').is_file() and (R/'SOURCES_AND_COMPATIBILITY_ACTUAL.json').is_file()
    put(R/'FEASIBILITY_ARCHIVE_STARTED_ACTUAL.json',dict(epoch=time.time(),base_HEAD=cfg['base_HEAD'],old_tag_count=1436,no_training_or_model_download=True))
    sys.path.insert(0,str(T/'H1_STEP270_TUCK_V3_FIRST_CLOSED39_REPLAY_20261023'));from capture_index_ordered_parts_v1 import read_capture_index
    prior_path=G/'versions/20261025_obsolete_expert_replay_storage_pruning/COMPLETE_FILE_CAPTURE_INDEX.json';prior=read_capture_index(prior_path,G);assert prior['entries']
    sys.path.insert(0,str(G/'archive_tools'));from capture_history import redact
    D.mkdir();entries=[];files={}
    def add(p,raw):
        p.parent.mkdir(parents=True,exist_ok=True)
        with p.open('xb') as f:f.write(raw)
        files[p.relative_to(G).as_posix()]=H(raw)
    source_paths=sorted(p for p in Q.rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    source_paths += [S/'reports'/name for name in cfg['cleanup_ordinary_supplement_reports']]
    for p in source_paths:
        raw=p.read_bytes();assert len(raw)<49_000_000;clean,n=redact(raw.decode('utf8'));data=clean.encode();dest=D/'files'/p.relative_to(W);add(dest,data);entries.append(dict(path=str(p),bytes=len(raw),SHA=H(raw),archive=dest.relative_to(G).as_posix(),archive_SHA=H(data),mode='redacted' if n else 'full',redaction_count=n,original_retained=True))
    add(D/'COMPLETE_FILE_CAPTURE_INDEX.json',json.dumps(dict(epoch=time.time(),kind='primary_source_T2z_future_training_feasibility_only',entries=entries,previous_cleanup_capture=dict(path=prior_path.relative_to(G).as_posix(),SHA=H(prior_path.read_bytes()),complete_entries=len(prior['entries'])),cleanup_supplements_are_ordinary_same_stage_no_new_cleanup_tag=True,no_model_data_download_install_inference_or_training=True),ensure_ascii=False,indent=2).encode())
    import record_experiment as rec
    def recgit(*args):
        if args[:2]==('add','--'):return git('add','--pathspec-from-file=-','--pathspec-file-nul',input=b'\0'.join(x.encode() for x in args[2:])+b'\0')
        if args[:2]==('tag','-a'):return git('tag','-a',TAG,'-F',str(R/'ROOT_ACTUAL_FEASIBILITY_STAGE_NOTE.md'))
        if args and args[0]=='push':return git('push','--atomic','origin','HEAD:main','refs/tags/'+TAG)
        return git(*args)
    rec.git=recgit;sys.argv=['record_experiment.py','--id',ID,'--title','Review T2-z primary sources for future MOD4 dynamics adaptation and retain disk attribution supplement','--kind','diagnostic','--note-file',str(R/'ROOT_ACTUAL_FEASIBILITY_STAGE_NOTE.md'),'--files',*files,'--validation','Read-only primary-source code/config/paper review, exact source revision and compatibility constraints; no T2-z experiment or adoption claim. Cleanup disk-attribution reader correction added as ordinary evidence, no repeated cleanup record.','--push'];rec.main()
    head=git('rev-parse','HEAD');remote={x.split()[1]:x.split()[0] for x in git('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines()};assert remote['refs/heads/main']==head and remote['refs/tags/'+TAG]==git('rev-parse',TAG) and remote['refs/tags/'+TAG+'^{}']==head
    for line in tags.splitlines():
        a=line.split();assert remote[a[0]]==a[1]
        if len(a)>2:assert remote[a[0]+'^{}']==a[2]
    for rel,sha in files.items():assert H(subprocess.check_output(['git','-C',str(G),'show',head+':'+rel]))==sha
    assert len(git('tag','--list').splitlines())==1437 and not git('status','--porcelain')
    print(json.dumps(dict(remote_main=head,tag=TAG,tag_object=git('rev-parse',TAG),peeled=head,total_tags=1437,all1436_old_objects_and_peels_preserved=True,full_new_texts_verified=len(entries),new_blobs_verified=len(files),workingtree_clean=True,no_experiment_run=True)),flush=True)
if __name__=='__main__':
    try:main()
    except BaseException:
        put(R/('ARCHIVE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(epoch=time.time(),error=traceback.format_exc(),resume_existing_objects_only_no_repeat_record_or_tag=True));raise
