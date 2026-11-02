"""Use UNMODIFIED recorder; only replace its single git-add operand list.
Validate exact owned staged set and every staged blob before commit. Push only
explicit owned branch/tag refspecs. No original checkout/index write command.
"""
from pathlib import Path
import datetime,hashlib,importlib.util,io,json,os,subprocess,sys,traceback
WT=Path(r'F:\RMPOLAR-RL\repo-lqr-robust');P=WT/'history/experiments/mod4v1_robust_traditional_phase1'
TASK=Path(r'F:\RMPOLAR-RL\mod4v1_lqr_mpc_robust_20261102')
BRANCH='mod4v1-lqr-mpc-robust';BASE='6d04141cb75c83220c60033c7e56b4f8174e507a'
IDENT='mod4v1-robust-traditional-phase1';TAG='trial-20261102-'+IDENT
RECORD='history/experiments/20261102-'+IDENT+'.json';OWN=P.relative_to(WT).as_posix()
HELPER_HASH='b2fd15dee16735721e18ed88b55e9e3159344f1d6f8095217f2db84852c2cd3e'
MAIN_PRE='938b9ee8458f09a47e369995c8bfb1064b052a1f'
os.environ['GIT_OPTIONAL_LOCKS']='0'

def sha(b):return hashlib.sha256(b).hexdigest()
def cmd(*args,input=None):return subprocess.run(['git','-C',str(WT),*args],input=input,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)
def text(*args):return cmd(*args).stdout.decode('utf-8').strip()
def paths(*args):return [x.decode('utf-8') for x in cmd(*args).stdout.split(b'\0') if x]
def refs():
    out=text('ls-remote','origin','refs/heads/main','refs/heads/'+BRANCH,'refs/tags/'+TAG,'refs/tags/'+TAG+'^{}')
    return dict((line.split('\t')[1],line.split('\t')[0]) for line in out.splitlines() if line)
def branch_guard():
    assert text('rev-parse','--show-toplevel').lower()=='f:/rmpolar-rl/repo-lqr-robust'
    assert text('symbolic-ref','--short','HEAD')==BRANCH
    assert text('rev-parse','--git-path','index').lower().replace('\\','/').endswith('/.git/worktrees/repo-lqr-robust/index')

def main():
    branch_guard();assert text('rev-parse','HEAD')==BASE
    assert text('remote','get-url','origin') in ['https://github.com/lulunomaro/polar-rl-train.git','https://github.com/lulunomaro/polar-rl-train']
    pre=refs();assert pre.get('refs/heads/main')==MAIN_PRE,'Remote main changed since initial baseline; investigate rather than misreport'
    assert 'refs/heads/'+BRANCH not in pre and 'refs/tags/'+TAG not in pre,'Owned refs already exist; never overwrite'
    assert not text('diff','--cached','--name-only') and not text('diff','--name-only')
    assert sha((WT/'archive_tools/record_experiment.py').read_bytes())==HELPER_HASH
    assert not (WT/RECORD).exists() and not text('tag','--list',TAG)
    seal=json.loads((P/'SEAL.json').read_text(encoding='utf-8'));manifest=json.loads((P/'manifest.json').read_text(encoding='utf-8'))
    assert sha((P/'manifest.json').read_bytes())==seal['manifest_sha256']
    # Administrative evidence IDs augment, never rewrite, the original per-case
    # registry or any archived attempt/source/result.
    evidence=[]
    for e in manifest['entries']:
        if e.get('archive_path') and any(w in e['source_relative'].lower() for w in ['attempt','error','failure','revisions/','jerk_failure']):
            evidence.append({'evidence_id':e['source_relative'],'archive_path':e['archive_path'],'sha256':e['archive_sha256'],'actual_status':'Preserved verbatim in linked source/log/report; no filename-based pass inference'})
    eid=P/'HISTORICAL_ATTEMPT_EVIDENCE_IDS.json';assert not eid.exists();eid.write_text(json.dumps({'source_file_ids':evidence,'independent_case_ids_file':'CASE_AND_ATTEMPT_REGISTRY.json','not_new_trials':True},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    plan=P/'STAGING_PLAN.json';assert not plan.exists()
    selected=sorted(p.relative_to(WT).as_posix() for p in P.rglob('*') if p.is_file() and not p.is_symlink())
    selected=sorted(selected+[plan.relative_to(WT).as_posix()])
    for name in selected:
        assert name.startswith(OWN+'/')
        assert Path(name).suffix.lower() not in {'.pt','.pth','.onnx','.npz','.npy','.pem','.key','.exe','.obj','.stl','.usd','.zip','.bin'}
        assert not name.endswith('/trace.jsonl')
    plan.write_text(json.dumps({'owned_directory':OWN,'record':RECORD,'expected_selected_files':selected,'expected_staged_files':sorted(selected+[RECORD]),'git_add_adapter':'Exact owned directory plus record with --force --sparse to preserve reports and no foreign additions','required_checks':['exact staged path set','all paths added, no deletion/foreign path','each staged blob SHA256 equals selected working byte SHA256','record source hashes match exactly','own branch/index guard','remote baseline and post branch/tag object/peeled/main comparison'],'post_commit_receipt_pending_phase2':str(TASK/'ARCHIVE_PHASE1_RECEIPT.json')},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    expected_sha={name:sha((WT/name).read_bytes()) for name in selected};expected_set=set(selected+[RECORD]);verification={}
    sys.path.insert(0,str(WT/'archive_tools'));from capture_history import redact
    spec=importlib.util.spec_from_file_location('unmodified_phase1_recorder',WT/'archive_tools/record_experiment.py');rec=importlib.util.module_from_spec(spec);spec.loader.exec_module(rec)
    assert rec.ROOT==WT
    original_git=rec.git
    def validate_staged():
        branch_guard();actual=set(paths('diff','--cached','--name-only','-z'));assert actual==expected_set,{'missing':sorted(expected_set-actual),'unexpected':sorted(actual-expected_set)}
        ns=paths('diff','--cached','--name-status','-z');assert len(ns)==2*len(expected_set) and all(ns[i]=='A' for i in range(0,len(ns),2)),ns[:10]
        record=json.loads((WT/RECORD).read_text(encoding='utf-8'));assert record['kind']=='diagnostic' and record['tag']==TAG
        assert record['source_and_evidence_sha256']==expected_sha
        all_hashes={**expected_sha,RECORD:sha((WT/RECORD).read_bytes())}
        index_rows=cmd('ls-files','--stage','-z','--',OWN,RECORD).stdout.split(b'\0');objects=[]
        for line in index_rows:
            if not line:continue
            info,path=line.split(b'\t',1);mode,oid,stage=info.split();assert stage==b'0';objects.append((path.decode('utf-8'),oid.decode()))
        assert {p for p,o in objects}==expected_set
        payload=('\n'.join(o for p,o in objects)+'\n').encode();buf=io.BytesIO(cmd('cat-file','--batch',input=payload).stdout)
        for path,oid in objects:
            got,typ,size=buf.readline().split();assert got.decode()==oid and typ==b'blob';raw=buf.read(int(size));assert buf.read(1)==b'\n';assert sha(raw)==all_hashes[path],path
        verification.update(expected_staged_count=len(expected_set),exact_path_set=True,no_deletions_or_foreign_paths=True,all_staged_blob_sha256_match=True,record_hash_mapping_exact=True)
        print('STAGED_EXACT_VERIFIED',json.dumps(verification),flush=True)
    def adapter(*args):
        if args and args[0]=='add':
            assert args[1]=='--' and args[2]==RECORD and set(args[3:])==set(selected),'Unexpected recorder add shape'
            original_git('add','--force','--sparse','--',OWN,RECORD)
            validate_staged();return ''
        if args and args[0]=='commit':validate_staged()
        if args and args[0]=='push':raise AssertionError('Push uses explicit controlled owned refs after recorder, not helper implicit HEAD destination')
        if args[:2]==('tag','-a'):assert args[2]==TAG
        return original_git(*args)
    rec.git=adapter
    sys.argv=[str(WT/'archive_tools/record_experiment.py'),'--id',IDENT,'--title','Archive MOD4v1 robust traditional-control phase1 through R03','--kind','diagnostic','--note-file',str(P/'NOTE.md'),'--validation','Sealed text hashes and exact owned staged set verified; no simulation rerun; R04/R05/active MPC and synchronization receipt pending phase2.','--files',*selected]
    rec.main()
    commit=text('rev-parse','HEAD');tag_object=text('rev-parse','refs/tags/'+TAG);peeled=text('rev-parse','refs/tags/'+TAG+'^{}');assert text('cat-file','-t','refs/tags/'+TAG)=='tag' and peeled==commit
    branch_guard();assert text('rev-parse','refs/heads/'+BRANCH)==commit
    assert not text('diff','--cached','--name-only') and not text('diff','--name-only')
    # Exactly these two refs, no force, no main or expert branch destination.
    push=cmd('push','--atomic','origin','HEAD:refs/heads/'+BRANCH,'refs/tags/'+TAG+':refs/tags/'+TAG)
    post=refs();assert post.get('refs/heads/'+BRANCH)==commit and post.get('refs/tags/'+TAG)==tag_object and post.get('refs/tags/'+TAG+'^{}')==commit
    assert post.get('refs/heads/main')==MAIN_PRE,'Record observed remote-main mismatch; archive command never targeted it'
    stdout,n1=redact(push.stdout.decode('utf-8','replace'));stderr,n2=redact(push.stderr.decode('utf-8','replace'))
    status=text('status','--short');assert not status,status
    # Read refs only from the independently active original session, never status
    # or any write/restore command there.
    original=Path(r'F:\RMPOLAR-RL\repo-lqr')
    def old_read(*args):return subprocess.run(['git','-C',str(original),*args],check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).stdout.decode().strip()
    receipt={'status':'COMMITTED_AND_PUSHED_OWN_BRANCH_AND_ANNOTATED_TAG_VERIFIED','phase':'mod4v1_robust_traditional_phase1','commit':commit,'branch':BRANCH,'tag':TAG,'tag_object':tag_object,'peeled_commit':peeled,'remote_pre':pre,'remote_post':post,'remote_main_unchanged':post['refs/heads/main']==MAIN_PRE,'staged_validation':verification,'record_helper_sha256':HELPER_HASH,'record_helper_unmodified':True,'record':RECORD,'owned_directory':OWN,'selected_file_count':len(selected),'source_text_files':len([e for e in manifest['entries'] if e.get('archive_path')]),'source_text_bytes':sum(e.get('archive_bytes',0) for e in manifest['entries']),'raw_index_only':manifest['summary']['raw_index_only_files'],'raw_known_existing_producer_sha':manifest['summary']['raw_known_producer_sha'],'external_authority_indexes':manifest['summary']['external_authority_index_entries'],'source_case_count':30,'new_physics_steps':0,'new_test_runs':0,'credentials_redacted_in_push_log':n1+n2,'push_stdout':stdout,'push_stderr':stderr,'new_worktree_status':status,'other_active_session_branch_observed':old_read('symbolic-ref','--short','HEAD'),'other_active_session_HEAD_observed':old_read('rev-parse','HEAD'),'other_index_not_a_write_target':True,'recorded_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'phase1_source_snapshot_seal':seal,'future_pending':'R04/R05 and future sources/reports, active portable_mpc_qp_v1, post-commit receipt and other new files; goal stays active','this_persisted_receipt_git_status':'PHASE2_PENDING_POST_COMMIT_REPORT_NOT_IN_PHASE1_COMMIT','receipt_recursion_avoided':True}
    dest=TASK/'ARCHIVE_PHASE1_RECEIPT.json';assert not dest.exists();dest.write_text(json.dumps(receipt,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    print('FINAL_PHASE1_RECEIPT',json.dumps(receipt,ensure_ascii=False,indent=2),flush=True)
if __name__=='__main__':
    try:main()
    except BaseException:
        failure=TASK/'ARCHIVE_PHASE1_OPERATION_FAILURE_001.txt'
        if not failure.exists():failure.write_text(traceback.format_exc()+'\nPost-seal report is phase2pending. Do not replay successful record/tag; inspect existing objects first.\n',encoding='utf-8')
        raise
