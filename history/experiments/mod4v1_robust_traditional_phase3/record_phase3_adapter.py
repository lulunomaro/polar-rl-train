"""One original-recorder call, exact two-dir+record add, ownrefs atomic push.
Frozen SOURCE_PREPARATION is NEVER edited. Postcommit reports go PH4pending.
"""
from pathlib import Path
import datetime,hashlib,importlib.util,io,json,os,subprocess,sys,traceback
WT=Path(r'F:\RMPOLAR-RL\repo-lqr-robust');C=WT/'history/experiments/mod4v1_robust_traditional_phase3';P=WT/'history/experiments/mod4v1_robust_traditional_phase3_SOURCE_PREPARATION';PENDING=WT/'history/experiments/mod4v1_robust_traditional_phase4_PENDING'
BRANCH='mod4v1-lqr-mpc-robust';BASE='02b5ff84b905a4e40f207a44b0491aeff2f79b7e';IDENT='mod4v1-robust-traditional-phase3';TAG='trial-20261102-'+IDENT;RECORD='history/experiments/20261102-'+IDENT+'.json';OWN=C.relative_to(WT).as_posix();SOURCE=P.relative_to(WT).as_posix()
HELPER_SHA='b2fd15dee16735721e18ed88b55e9e3159344f1d6f8095217f2db84852c2cd3e';SEAL_SHA='0cb056859139876713515c41498097e838892d98a0a311630b547fa21f46fa70';INITIAL_MAIN='013ee164aa11762e075152befcb7e1ecb2314f63'
OLD_TAGS={'trial-20261102-mod4v1-robust-traditional-phase1':('1064f48cc077fdd3eb6c89e554b58f5d82ee5980','93e0814f5d4dc165dda1f85f8ee12bc35be04d2f'),'trial-20261102-mod4v1-robust-traditional-phase2':('4ac41c1403a3daefa52acedbf659ee89120b6046',BASE)}
os.environ['GIT_OPTIONAL_LOCKS']='0'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def cmd(*a,input=None):return subprocess.run(['git','-C',str(WT),*a],input=input,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)
def text(*a):return cmd(*a).stdout.decode('utf-8').strip()
def paths(*a):return [x.decode('utf-8') for x in cmd(*a).stdout.split(b'\0') if x]
def new(p,obj):assert not p.exists(),str(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def branch_guard():
    assert text('rev-parse','--show-toplevel').lower()=='f:/rmpolar-rl/repo-lqr-robust'
    assert text('symbolic-ref','--short','HEAD')==BRANCH
    assert text('rev-parse','--git-path','index').lower().replace('\\','/').endswith('/.git/worktrees/repo-lqr-robust/index')
    assert text('remote','get-url','origin') in ['https://github.com/lulunomaro/polar-rl-train.git','https://github.com/lulunomaro/polar-rl-train']
def refs():
    patterns=['refs/heads/main','refs/heads/'+BRANCH,'refs/tags/'+TAG,'refs/tags/'+TAG+'^{}']
    for tag in OLD_TAGS:patterns += ['refs/tags/'+tag,'refs/tags/'+tag+'^{}']
    s=text('ls-remote','origin',*patterns);return dict((x.split('\t')[1],x.split('\t')[0]) for x in s.splitlines() if x)
def old_refs_unchanged(r):
    for tag,(obj,commit) in OLD_TAGS.items():assert r.get('refs/tags/'+tag)==obj and r.get('refs/tags/'+tag+'^{}')==commit

def verify_frozen_source():
    assert sha((P/'FINAL_INDEX.json').read_bytes())==SEAL_SHA
    index=json.loads((P/'FINAL_INDEX.json').read_text(encoding='utf-8'));files={e['relative']:e for e in index['files']}
    current={p.relative_to(P).as_posix() for p in P.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    assert current==set(files)|{'FINAL_INDEX.json'},'Source-prep added/removed file after seal'
    for rel,e in files.items():assert sha((P/rel).read_bytes())==e['SHA'],'Sealed source byte changed: '+rel
    assert json.loads((P/'COMPLETION_VERIFICATION_RECEIPT.json').read_text(encoding='utf-8'))['Git_stage_commit_tag_push_record_calls']==0
    return index,len(current)

def main():
    assert datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y%m%d')=='20261102','Tag date must reflect actual date; do not backdate'
    branch_guard();assert text('rev-parse','HEAD')==BASE
    assert not text('diff','--cached','--name-only') and not text('diff','--name-only')
    assert sha((WT/'archive_tools/record_experiment.py').read_bytes())==HELPER_SHA
    source_index,source_file_count=verify_frozen_source();pre=refs();assert len(pre.get('refs/heads/main',''))==40
    assert pre.get('refs/heads/'+BRANCH)==BASE and 'refs/tags/'+TAG not in pre and not text('tag','--list',TAG) and not (WT/RECORD).exists(),'Ownbase/tag/record already changed; inspect, never replay/overwrite'
    old_refs_unchanged(pre)
    new(C/'PRECOMMIT_AUTHORITY.json',{'written_approval':'one new PH3 trial/commit/atomic ownbranch+newtag only on existing sealed R34SOURCE_PREP; source history not edited','owner_branch':BRANCH,'base':BASE,'owned_payload_roots':[OWN,SOURCE],'record':RECORD,'tag':TAG,'initial_main_probe':INITIAL_MAIN,'pre_record_remote':pre,'record_helper_SHA':HELPER_SHA,'source_prep_FINAL_INDEX_SHA':SEAL_SHA,'source_preparation_files':source_file_count,'not_expanding_cutoff_or_admitting_active_source':True,'postcommit_receipt_PH4pending':str(PENDING/'ARCHIVE_PHASE3_RECEIPT.json')})
    plan=C/'STAGING_PLAN.json';assert not plan.exists()
    selected=sorted(p.relative_to(WT).as_posix() for root in (C,P) for p in root.rglob('*') if p.is_file() and not p.is_symlink() and '__pycache__' not in p.parts);selected=sorted(selected+[plan.relative_to(WT).as_posix()])
    for rel in selected:
        assert rel.startswith(OWN+'/') or rel.startswith(SOURCE+'/')
        assert Path(rel).suffix.lower() not in {'.exe','.dll','.o','.obj','.lib','.a','.bin','.pt','.pth','.onnx','.npz','.npy','.pem','.key','.usd','.usdc','.usda','.stl','.stp','.step','.zip','.7z','.jsonl'},'Original raw/binary should be metadata only'
    new(plan,{'selected_payload_roots':[OWN,SOURCE],'selected_files':selected,'record':RECORD,'expected_staged_paths':sorted(selected+[RECORD]),'original_helper_add_only_intercepted_in_memory':True,'add_command_operands':[OWN,SOURCE,RECORD],'source_prep_FINAL_INDEX_SHA_unchanged':SEAL_SHA,'allA_noD_noForeign_eachBlobSHA_required':True,'no_root_source_or_other_worktree_write':True,'postcommit_reports':'PH4pending, no recursive new trial'})
    expected_sha={rel:sha((WT/rel).read_bytes()) for rel in selected};expected_set=set(selected+[RECORD]);verification={}
    sys.path.insert(0,str(WT/'archive_tools'));from capture_history import redact
    spec=importlib.util.spec_from_file_location('one_original_phase3_recorder',WT/'archive_tools/record_experiment.py');rec=importlib.util.module_from_spec(spec);spec.loader.exec_module(rec);assert rec.ROOT==WT;original_git=rec.git
    def validate_staged():
        branch_guard();verify_frozen_source();actual=set(paths('diff','--cached','--name-only','-z'));assert actual==expected_set,{'missing':sorted(expected_set-actual),'foreign':sorted(actual-expected_set)}
        ns=paths('diff','--cached','--name-status','-z');assert len(ns)==2*len(expected_set) and all(ns[i]=='A' for i in range(0,len(ns),2)),ns[:10]
        record=json.loads((WT/RECORD).read_text(encoding='utf-8'));assert record['tag']==TAG and record['id']=='20261102-'+IDENT and record['kind']=='diagnostic' and record['source_and_evidence_sha256']==expected_sha
        all_hashes={**expected_sha,RECORD:sha((WT/RECORD).read_bytes())};objects=[]
        for line in cmd('ls-files','--stage','-z','--',OWN,SOURCE,RECORD).stdout.split(b'\0'):
            if not line:continue
            info,path=line.split(b'\t',1);mode,oid,stage=info.split();assert stage==b'0' and mode in (b'100644',b'100755');objects.append((path.decode('utf-8'),oid.decode()))
        assert {p for p,o in objects}==expected_set;buf=io.BytesIO(cmd('cat-file','--batch',input=('\n'.join(o for p,o in objects)+'\n').encode()).stdout)
        for path,oid in objects:
            got,typ,size=buf.readline().split();assert got.decode()==oid and typ==b'blob';raw=buf.read(int(size));assert buf.read(1)==b'\n';assert sha(raw)==all_hashes[path],path
        verification.update(expected_staged_count=len(expected_set),exact_path_set=True,all_A=True,no_D_no_foreign_blob=True,each_blob_SHA256_matches_sealed_or_selected_bytes=True,record_source_hash_map_exact=True,source_prep_FINAL_INDEX_unmodified=SEAL_SHA)
        print('PH3_STAGED_EXACT_VERIFIED',json.dumps(verification),flush=True)
    def narrow_git(*args):
        if args and args[0]=='add':
            assert args[1]=='--' and args[2]==RECORD and set(args[3:])==set(selected),'Unexpected original recorder add shape'
            original_git('add','--force','--sparse','--',OWN,SOURCE,RECORD);validate_staged();return ''
        if args and args[0]=='commit':validate_staged()
        if args and args[0]=='push':raise AssertionError('Helper implicit push is not used')
        if args[:2]==('tag','-a'):assert args[2]==TAG
        return original_git(*args)
    rec.git=narrow_git
    sys.argv=[str(WT/'archive_tools/record_experiment.py'),'--id',IDENT,'--title','Archive sealed MOD4v1 traditional phase3 source through R34','--kind','diagnostic','--note-file',str(C/'NOTE.md'),'--validation','Exact frozen SOURCE_PREP+cover+newrecord allA path/blobSHA verified; R34cutoff unchanged; no rawread/physics/test; all Goal/hardware qualifiers preserved; postreceipt PH4pending.','--files',*selected]
    rec.main()
    commit=text('rev-parse','HEAD');tag_obj=text('rev-parse','refs/tags/'+TAG);peeled=text('rev-parse','refs/tags/'+TAG+'^{}');assert text('cat-file','-t','refs/tags/'+TAG)=='tag' and peeled==commit and text('rev-parse',commit+'^')==BASE
    branch_guard();assert text('rev-parse','refs/heads/'+BRANCH)==commit;assert set(paths('diff-tree','--no-commit-id','--name-only','-r','-z',commit))==expected_set;assert not text('diff','--cached','--name-only') and not text('diff','--name-only');verify_frozen_source()
    pre_push=refs();old_refs_unchanged(pre_push);assert pre_push.get('refs/heads/'+BRANCH)==BASE and 'refs/tags/'+TAG not in pre_push,'Own refs changed concurrently; never force'
    push=cmd('push','--atomic','origin','HEAD:refs/heads/'+BRANCH,'refs/tags/'+TAG+':refs/tags/'+TAG)
    post=refs();old_refs_unchanged(post);assert post.get('refs/heads/'+BRANCH)==commit and post.get('refs/tags/'+TAG)==tag_obj and post.get('refs/tags/'+TAG+'^{}')==commit
    verify_frozen_source();assert sha((WT/'archive_tools/record_experiment.py').read_bytes())==HELPER_SHA
    status_before_receipt=text('status','--short');assert not status_before_receipt,status_before_receipt
    stdout,n1=redact(push.stdout.decode('utf-8','replace'));stderr,n2=redact(push.stderr.decode('utf-8','replace'))
    receipt={'status':'PH3_COMMIT_AND_ATOMIC_OWN_BRANCH_TAG_PUSH_REMOTE_VERIFIED','commit':commit,'branch':BRANCH,'tag':TAG,'tag_object':tag_obj,'peeled_commit':peeled,'initial_main_probe':INITIAL_MAIN,'remote_pre_record':pre,'remote_pre_push':pre_push,'remote_post':post,'main_same_only_immediate_push_window':post.get('refs/heads/main')==pre_push.get('refs/heads/main'),'main_unchanged_entire_archive_NOT_claimed':True,'initial_to_current_main_change_preserved':post.get('refs/heads/main')!=INITIAL_MAIN,'old_PH1_PH2_refs_unchanged':True,'staged_verification':verification,'helper_SHA_unmodified':HELPER_SHA,'record':RECORD,'payload_roots':[OWN,SOURCE],'source_prep_FINAL_INDEX_SHA_unmodified':SEAL_SHA,'source_payload_files':source_file_count,'selected_files_without_record':len(selected),'source_summary':json.loads((P/'FINAL_SOURCE_MANIFEST.json').read_text(encoding='utf-8'))['summary'],'sourceRoot_or_expert_index_main_writes':False,'new_physics_tests_rawhashes_GPU_agents_realIO':False,'push_stdout_redacted':stdout,'push_stderr_redacted':stderr,'push_log_redactions':n1+n2,'owner_status_before_postreceipt':status_before_receipt,'receipt_git_status':'PH4_PENDING_POSTCOMMIT_NOT_IN_PHASE3_TREE','receipt_recursion_avoided':True,'recorded_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'overall_Goal_active':True}
    new(PENDING/'ARCHIVE_PHASE3_RECEIPT.json',receipt)
    print('PH3_REMOTE_VERIFIED_RECEIPT',json.dumps(receipt,ensure_ascii=False,indent=2),flush=True)
if __name__=='__main__':
    try:main()
    except BaseException:
        PENDING.mkdir(parents=True,exist_ok=True);n=1
        while (PENDING/f'ARCHIVE_PHASE3_OPERATION_FAILURE_{n:03d}.txt').exists():n+=1
        (PENDING/f'ARCHIVE_PHASE3_OPERATION_FAILURE_{n:03d}.txt').write_text(traceback.format_exc()+'\nFormal report PH4pending. Inspect existing commit/tag before any follow-up; never replay successful record/tag.\n',encoding='utf-8');raise
