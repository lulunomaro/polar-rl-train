"""Original helper exactly once; reviewed SOURCE_PREP+cover+one receipt+record.
No SourceRoot/expert/main write. Frozen reviewed metadata never edited.
"""
from pathlib import Path
import datetime,hashlib,importlib.util,io,json,os,re,subprocess,sys,traceback
WT=Path(r'F:\RMPOLAR-RL\repo-lqr-robust');C=WT/'history/experiments/mod4v1_robust_traditional_phase4';P=WT/'history/experiments/mod4v1_robust_traditional_phase4_SOURCE_PREPARATION';PENDING=WT/'history/experiments/mod4v1_robust_traditional_phase5_PENDING';EXTRA='history/experiments/mod4v1_robust_traditional_phase4_PENDING/ARCHIVE_PHASE3_RECEIPT.json'
OWN=C.relative_to(WT).as_posix();SOURCE=P.relative_to(WT).as_posix();BRANCH='mod4v1-lqr-mpc-robust';BASE='fa6838807f4d69d2b8ac52300d74ad40f365d2ed';IDENT='mod4v1-robust-traditional-phase4';TAG='trial-20261102-'+IDENT;RECORD='history/experiments/20261102-'+IDENT+'.json'
HELPER_SHA='b2fd15dee16735721e18ed88b55e9e3159344f1d6f8095217f2db84852c2cd3e';SEAL_SHA='9e24aeb19164896b9ca6ae9c72957168ab9ad6a954fa0a9f18580730583aa53d';INITIAL_MAIN='f30410178844fbd6d122922f218831b1ac095821'
OLD_TAGS={'trial-20261102-mod4v1-robust-traditional-phase1':('1064f48cc077fdd3eb6c89e554b58f5d82ee5980','93e0814f5d4dc165dda1f85f8ee12bc35be04d2f'),'trial-20261102-mod4v1-robust-traditional-phase2':('4ac41c1403a3daefa52acedbf659ee89120b6046','02b5ff84b905a4e40f207a44b0491aeff2f79b7e'),'trial-20261102-mod4v1-robust-traditional-phase3':('163d331cc4dade7bee2e870c7f2da852edec44ab',BASE)}
os.environ['GIT_OPTIONAL_LOCKS']='0'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def new(p,obj):assert not p.exists(),str(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def cmd(*a,input=None):return subprocess.run(['git','-C',str(WT),*a],input=input,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)
def text(*a):return cmd(*a).stdout.decode('utf-8').strip()
def paths(*a):return [v.decode('utf-8') for v in cmd(*a).stdout.split(b'\0') if v]
def guard():
    assert text('rev-parse','--show-toplevel').lower()=='f:/rmpolar-rl/repo-lqr-robust' and text('symbolic-ref','--short','HEAD')==BRANCH
    assert text('rev-parse','--git-path','index').lower().replace('\\','/').endswith('/.git/worktrees/repo-lqr-robust/index')
    assert text('remote','get-url','origin') in ['https://github.com/lulunomaro/polar-rl-train.git','https://github.com/lulunomaro/polar-rl-train']
def refs():
    patterns=['refs/heads/main','refs/heads/'+BRANCH,'refs/tags/'+TAG,'refs/tags/'+TAG+'^{}']
    for t in OLD_TAGS:patterns+=['refs/tags/'+t,'refs/tags/'+t+'^{}']
    out=text('ls-remote','origin',*patterns);return dict((v.split('\t')[1],v.split('\t')[0]) for v in out.splitlines() if v)
def old_refs(r):
    for t,(obj,commit) in OLD_TAGS.items():assert r.get('refs/tags/'+t)==obj and r.get('refs/tags/'+t+'^{}')==commit

def frozen():
    assert sha((P/'REVIEW_INDEX.json').read_bytes())==SEAL_SHA
    idx=load(P/'REVIEW_INDEX.json');expected={e['relative']:e for e in idx['files']};actual={p.relative_to(P).as_posix() for p in P.rglob('*') if p.is_file() and '__pycache__' not in p.parts};assert actual==set(expected)|{'REVIEW_INDEX.json'}
    for rel,e in expected.items():assert sha((P/rel).read_bytes())==e['SHA'],'Frozen source-prep byte changed: '+rel
    gap=load(P/'FINAL_REVIEW_GAPS.json');assert len(gap['actual_missing_saved_smalltext_version_claims'])==1 and len(gap['raw_unknowns_unchanged'])==15 and gap['actual_missing_saved_smalltext_version_claims'][0]['expected_SHA']=='eea7bbf33028a3abaf697a3ec76c06fefdf53d68c8f551a6b9593fba157f048d'
    m=load(P/'FINAL_SOURCE_MANIFEST.json')
    for e in m['entries']:
        low=e['source_relative'].lower();assert not any(k in low for k in ('world_leg','minihop_audit_v2','power_allocator','continuation_stage1_delivery')) and not any(int(n)>39 for n in re.findall(r'(?<![a-z0-9])r(\d{2})(?=[^0-9]|$)',low))
    extra=(WT/EXTRA).resolve();entry=next(e for e in m['entries'] if Path(e['path']).resolve()==extra);assert sha(extra.read_bytes())==entry['source_SHA'] and load(extra)['commit']==BASE
    return len(actual),m['summary'],sha(extra.read_bytes())

def main():
    assert datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y%m%d')=='20261102','Do not backdate tag'
    guard();assert text('rev-parse','HEAD')==BASE and not text('diff','--cached','--name-only') and not text('diff','--name-only')
    assert sha((WT/'archive_tools/record_experiment.py').read_bytes())==HELPER_SHA
    nfiles,source_summary,extraSHA=frozen();pre=refs();old_refs(pre);assert len(pre.get('refs/heads/main',''))==40 and pre.get('refs/heads/'+BRANCH)==BASE and 'refs/tags/'+TAG not in pre and not text('tag','--list',TAG) and not (WT/RECORD).exists(),'Baseline/tag/record changed: never reset/overwrite/replay'
    new(C/'PARENT_AUTHORITY_AND_FREEZE.json',{'authority':'Parent reviewed complete REVIEW_HANDOFF/FINAL_REVIEW_GAPS361lines/FINAL_CONSISTENCY_RECEIPT; accepts1historicaltextSHA gap15unknownraw, approvesnewPH4trial/atomic ownrefs only','owner_branch':BRANCH,'base':BASE,'tag':TAG,'record':RECORD,'allowed_directories':[OWN,SOURCE],'extra_single_file':EXTRA,'extra_SHA':extraSHA,'source_prep_REVIEW_INDEX_SHA':SEAL_SHA,'source_preparation_file_count':nfiles,'helper_actual_path':'archive_tools/record_experiment.py','helper_SHA':HELPER_SHA,'parent_helper_short_name':'record_trial.py resolved only by exact approved originalSHA','initial_main_probe':INITIAL_MAIN,'remote_pre_record':pre,'postcommit_receipt':str(PENDING/'ARCHIVE_PHASE4_RECEIPT.json'),'missing_provenance_not_claimed_complete':True})
    plan=C/'STAGING_PLAN.json';assert not plan.exists();selected=sorted([p.relative_to(WT).as_posix() for d in (C,P) for p in d.rglob('*') if p.is_file() and not p.is_symlink() and '__pycache__' not in p.parts]+[EXTRA,plan.relative_to(WT).as_posix()])
    for rel in selected:
        assert rel==EXTRA or rel.startswith(OWN+'/') or rel.startswith(SOURCE+'/')
        assert Path(rel).suffix.lower() not in {'.exe','.dll','.o','.obj','.a','.lib','.bin','.pt','.pth','.onnx','.npz','.npy','.pem','.key','.usd','.usdc','.usda','.stl','.stp','.step','.zip','.7z','.jsonl'}
    new(plan,{'expected_staged_paths':sorted(selected+[RECORD]),'selected_files':selected,'allowed_payload_roots':[OWN,SOURCE],'extra_exact_file':EXTRA,'record':RECORD,'source_frozen_review_SHA':SEAL_SHA,'allA_noD_noForeign_eachBlobSHA_required':True,'no_glob_add_no_global_push':True,'inmemory_argv_narrow_add_operands':[OWN,SOURCE,EXTRA,RECORD],'laterreceipt':'phase5_PENDING, not this commit'})
    hashes={p:sha((WT/p).read_bytes()) for p in selected};expected=set(selected+[RECORD]);verified={};sys.path.insert(0,str(WT/'archive_tools'));from capture_history import redact
    spec=importlib.util.spec_from_file_location('one_original_phase4_recorder',WT/'archive_tools/record_experiment.py');rec=importlib.util.module_from_spec(spec);spec.loader.exec_module(rec);assert rec.ROOT==WT;original=rec.git
    def check():
        guard();frozen();actual=set(paths('diff','--cached','--name-only','-z'));assert actual==expected,{'missing':sorted(expected-actual),'foreign':sorted(actual-expected)}
        ns=paths('diff','--cached','--name-status','-z');assert len(ns)==2*len(expected) and all(ns[i]=='A' for i in range(0,len(ns),2));record=load(WT/RECORD);assert record['tag']==TAG and record['id']=='20261102-'+IDENT and record['kind']=='diagnostic' and record['source_and_evidence_sha256']==hashes
        hs={**hashes,RECORD:sha((WT/RECORD).read_bytes())};objects=[]
        for v in cmd('ls-files','--stage','-z','--',OWN,SOURCE,EXTRA,RECORD).stdout.split(b'\0'):
            if not v:continue
            info,path=v.split(b'\t',1);mode,oid,stage=info.split();assert stage==b'0' and mode in (b'100644',b'100755');objects.append((path.decode(),oid.decode()))
        assert {p for p,o in objects}==expected;buf=io.BytesIO(cmd('cat-file','--batch',input=('\n'.join(o for p,o in objects)+'\n').encode()).stdout)
        for path,oid in objects:
            got,kind,size=buf.readline().split();assert got.decode()==oid and kind==b'blob';raw=buf.read(int(size));assert buf.read(1)==b'\n' and sha(raw)==hs[path],path
        verified.update(expected_staged_count=len(expected),exact_paths=True,allA=True,noD_noForeign=True,allblobSHA_match_frozen_or_selected=True,record_map_exact=True,review_index_unchanged=SEAL_SHA)
        print('PH4_STAGED_EXACT_VERIFIED',json.dumps(verified),flush=True)
    def narrow(*args):
        if args and args[0]=='add':
            assert args[1]=='--' and args[2]==RECORD and set(args[3:])==set(selected)
            original('add','--force','--sparse','--',OWN,SOURCE,EXTRA,RECORD);check();return ''
        if args and args[0]=='commit':check()
        if args and args[0]=='push':raise AssertionError('No helper global/implicit push')
        if args[:2]==('tag','-a'):assert args[2]==TAG
        return original(*args)
    rec.git=narrow;sys.argv=[str(WT/'archive_tools/record_experiment.py'),'--id',IDENT,'--title','Archive reviewed MOD4v1 traditional phase4 source through R39','--kind','diagnostic','--note-file',str(C/'NOTE.md'),'--validation','Reviewed source-prep immutable;1historicaltextgap15rawunknown disclosed; exactallA paths/blobSHA; R40plus/WORLDLEG/v2/POWER/newCONT excluded; no rawhash/physics/test; laterreceiptphase5pending.','--files',*selected]
    rec.main();commit=text('rev-parse','HEAD');obj=text('rev-parse','refs/tags/'+TAG);peeled=text('rev-parse','refs/tags/'+TAG+'^{}');assert peeled==commit and text('cat-file','-t','refs/tags/'+TAG)=='tag' and text('rev-parse',commit+'^')==BASE
    guard();frozen();assert set(paths('diff-tree','--no-commit-id','--name-only','-r','-z',commit))==expected and not text('diff','--cached','--name-only') and not text('diff','--name-only')
    prepush=refs();old_refs(prepush);assert prepush.get('refs/heads/'+BRANCH)==BASE and 'refs/tags/'+TAG not in prepush
    push=cmd('push','--atomic','origin','HEAD:refs/heads/'+BRANCH,'refs/tags/'+TAG+':refs/tags/'+TAG);post=refs();old_refs(post);assert post.get('refs/heads/'+BRANCH)==commit and post.get('refs/tags/'+TAG)==obj and post.get('refs/tags/'+TAG+'^{}')==commit
    frozen();assert sha((WT/'archive_tools/record_experiment.py').read_bytes())==HELPER_SHA;status=text('status','--short');assert not status,status
    stdout,n1=redact(push.stdout.decode('utf-8','replace'));stderr,n2=redact(push.stderr.decode('utf-8','replace'))
    receipt={'status':'PH4_RECORDED_COMMITTED_ANNOTATEDTAG_ATOMIC_OWNREFS_PUSH_VERIFIED','commit':commit,'branch':BRANCH,'tag':TAG,'tag_object':obj,'peeled_commit':peeled,'remote_pre_record':pre,'remote_pre_push':prepush,'remote_post':post,'initial_main_probe':INITIAL_MAIN,'main_same_only_immediate_push_window':post.get('refs/heads/main')==prepush.get('refs/heads/main'),'global_no_concurrent_main_change_NOT_claimed':True,'PH1_PH2_PH3_refs_unchanged':True,'staged_exact':verified,'record':RECORD,'payload_directories':[OWN,SOURCE],'extra_PH3_receipt_directly_committed':EXTRA,'helper_SHA_unmodified':HELPER_SHA,'source_prep_REVIEW_INDEX_SHA_unmodified':SEAL_SHA,'source_prep_files':nfiles,'selected_payload_files_without_record':len(selected),'source_summary':source_summary,'final_missing_history':'one ERROR_REPORT.md historicalSHA missing/15rawunknown preserved; no completeprovenance claim','sourceRoot_expertindex_main_otherrefs_written':False,'new_physics_tests_rawhashes_GPU_agents_realIO_goalactions':False,'push_stdout_redacted':stdout,'push_stderr_redacted':stderr,'push_log_redactions':n1+n2,'owner_status_before_postreceipt':status,'receipt_git_status':'PHASE5_PENDING_POSTCOMMIT_NOT_IN_PHASE4_TREE','receipt_recursion_avoided':True,'recorded_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'overall_Goal_active':True}
    new(PENDING/'ARCHIVE_PHASE4_RECEIPT.json',receipt);print('PH4_REMOTE_VERIFIED_RECEIPT',json.dumps(receipt,ensure_ascii=False,indent=2),flush=True)
if __name__=='__main__':
    try:main()
    except BaseException:
        PENDING.mkdir(parents=True,exist_ok=True);n=1
        while (PENDING/f'ARCHIVE_PHASE4_OPERATION_FAILURE_{n:03d}.txt').exists():n+=1
        (PENDING/f'ARCHIVE_PHASE4_OPERATION_FAILURE_{n:03d}.txt').write_text(traceback.format_exc()+'\nFormal report phase5pending. Inspect existing objects before follow-up; do not replay successful record/tag.\n',encoding='utf-8');raise
