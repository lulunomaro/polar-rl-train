"""ONE approved PH7 archive. Original recorder unchanged; no oldQA/raw/source read."""
from pathlib import Path
import datetime,hashlib,importlib.util,io,json,os,subprocess,sys,traceback
WT=Path(r'F:\RMPOLAR-RL\repo-lqr-robust');C=WT/'history/experiments/mod4v1_robust_traditional_phase7';P=WT/'history/experiments/mod4v1_robust_traditional_phase7_SOURCE_PREPARATION';PENDING=WT/'history/experiments/mod4v1_robust_traditional_phase8_PENDING'
OWN=C.relative_to(WT).as_posix();SOURCE=P.relative_to(WT).as_posix();BRANCH='mod4v1-lqr-mpc-robust';BASE='4e7a3fb9855657b5b501de08785f875b1e0bedfd';IDENT='mod4v1-robust-traditional-phase7';DATE='20261103';TAG='trial-'+DATE+'-'+IDENT;RECORD='history/experiments/'+DATE+'-'+IDENT+'.json'
HELPER_SHA='b2fd15dee16735721e18ed88b55e9e3159344f1d6f8095217f2db84852c2cd3e';SEAL_SHA='b00d4c7605031bd3bb81e912a09eee267ecf73c1282ba37b9fbee19eaee6c37d';INITIAL_MAIN='163aee7ab783703685f2e4dfcaa0e9aa450dd0bc'
COPIES={'PH7_ARCHIVE_REVIEW_APPROVAL.json':'5652dabf424181553c39b507fad9d9c6fb3086628e5d7a9b8c48c3f82d9f9810','PH7_PARENT_NUMERIC_CHECK.json':'828f2c938b8d491822861b1ae1fecc5a0c99f0952750f5bf0b28982ab624f0a2','review_ph7_parent_v1.py':'fc2406876b37c38c545a1356f6bac42b5933a6635c20d2faf0d91222e52b5571'}
OLD_TAGS={'trial-20261102-mod4v1-robust-traditional-phase1':('1064f48cc077fdd3eb6c89e554b58f5d82ee5980','93e0814f5d4dc165dda1f85f8ee12bc35be04d2f'),'trial-20261102-mod4v1-robust-traditional-phase2':('4ac41c1403a3daefa52acedbf659ee89120b6046','02b5ff84b905a4e40f207a44b0491aeff2f79b7e'),'trial-20261102-mod4v1-robust-traditional-phase3':('163d331cc4dade7bee2e870c7f2da852edec44ab','fa6838807f4d69d2b8ac52300d74ad40f365d2ed'),'trial-20261102-mod4v1-robust-traditional-phase4':('5aadabd68a83f1e4ef93dd2b18518128c46f87a9','db8fd0606e00a450504853181a6b4cdf66869d68'),'trial-20261103-mod4v1-robust-traditional-phase5':('0701622bb247649b33f78fa4627bfa3f7a1cbd9c','0a21cdc6445268c05389103afea071836424b470'),'trial-20261103-mod4v1-robust-traditional-phase6':('db83d307944644ccf46b4b43b79ffc5633d6897b',BASE)}
os.environ['GIT_OPTIONAL_LOCKS']='0'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def new(p,x):assert not p.exists(),str(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def cmd(*a,input=None):return subprocess.run(['git','-C',str(WT),*a],input=input,capture_output=True,check=True)
def text(*a):return cmd(*a).stdout.decode('utf-8').strip()
def paths(*a):return [x.decode('utf-8')for x in cmd(*a).stdout.split(b'\0')if x]
def guard():
 assert text('rev-parse','--show-toplevel').lower()=='f:/rmpolar-rl/repo-lqr-robust' and text('symbolic-ref','--short','HEAD')==BRANCH
 assert text('rev-parse','--git-path','index').lower().replace('\\','/').endswith('/.git/worktrees/repo-lqr-robust/index')
 assert text('remote','get-url','origin')in('https://github.com/lulunomaro/polar-rl-train.git','https://github.com/lulunomaro/polar-rl-train')
def refs():
 names=['refs/heads/main','refs/heads/'+BRANCH,'refs/tags/'+TAG,'refs/tags/'+TAG+'^{}']
 for t in OLD_TAGS:names+=['refs/tags/'+t,'refs/tags/'+t+'^{}']
 return {r:h for h,r in(x.split('\t')for x in text('ls-remote','origin',*names).splitlines())}
def oldrefs(r):
 for t,(obj,commit)in OLD_TAGS.items():assert r.get('refs/tags/'+t)==obj and r.get('refs/tags/'+t+'^{}')==commit,(t,r)
def review_freeze():
 # Only small review/approval files are rehashed here, NOT51oldresults or the
 # large original source manifests. Sealed expected payload SHAs come from INDEX
 # and are independently checked against every actual staged Git blob.
 assert sha((P/'REVIEW_INDEX.json').read_bytes())==SEAL_SHA
 for n,h in COPIES.items():assert sha((C/n).read_bytes())==h,(n,'parent copy changed')
 approval=load(C/'PH7_ARCHIVE_REVIEW_APPROVAL.json');assert approval['status']=='PARENT_REVIEW_APPROVED_ONE_NEW_PHASE7_ARCHIVE_ONLY' and approval['expected_parent_commit']==BASE and approval['unique_trial_id']==IDENT and approval['new_annotated_tag']==TAG
 for n,h in approval['parent_verified_smallfiles_SHA'].items():assert sha((P/n).read_bytes())==h,n
 idx=load(P/'REVIEW_INDEX.json');actual={p.relative_to(P).as_posix()for p in P.rglob('*')if p.is_file()and'__pycache__'not in p.parts};want={e['relative']for e in idx['files']}|{'REVIEW_INDEX.json'};assert actual==want,'Reviewed SOURCE file set changed'
 source_sha={SOURCE+'/'+e['relative']:e['SHA']for e in idx['files']};source_sha[SOURCE+'/REVIEW_INDEX.json']=SEAL_SHA
 assert idx['manifest']['SHA']==approval['manifest_producer_SHA_not_parent_large_rehash']
 rec=load(P/'FINAL_CONSISTENCY_RECEIPT.json');s=rec['summary'];assert rec['stage_record_commit_tag_push_calls']==0 and s['missing_saved_smalltext_unique']==1 and s['current_raw_unknowns']==2
 return s,source_sha

def main():
 assert datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y%m%d')==DATE,'Actual date only, no backdating'
 guard();assert text('rev-parse','HEAD')==BASE and not text('diff','--name-only') and not text('diff','--cached','--name-only'),'OwnHEAD/tracked/staged changed; never reset'
 helper=WT/'archive_tools/record_experiment.py';assert sha(helper.read_bytes())==HELPER_SHA
 assert not(WT/RECORD).exists()and not text('tag','--list',TAG)and not(PENDING/'ARCHIVE_PHASE7_RECEIPT.json').exists(),'Existing objects/record/receipt: inspect, never replay'
 summary,source_sha=review_freeze();pre=refs();oldrefs(pre);assert pre.get('refs/heads/'+BRANCH)==BASE and 'refs/tags/'+TAG not in pre
 new(C/'PARENT_AUTHORITY_AND_FREEZE.json',{'id':IDENT,'date':DATE,'source_review_index_SHA':SEAL_SHA,'original_helper_SHA':HELPER_SHA,'own_branch':BRANCH,'base':BASE,'parent_approval_and_numeric_evidence_copies_SHA':COPIES,'source_scope':'immutable throughR61+sealedAIR only, activeAIRref/R62 excluded','source_payload_SHA_source':'reviewedINDEX expected map, no duplicate large-manifest/51result revalidation','remote_pre_record':pre,'only_new_payload_dirs':[OWN,SOURCE],'new_record':RECORD,'gaps':'1savedhistoricaltextSHA missing;2currentexeSHAunknown with8historicalclaimrecords, no perfectprovenance or retroactiveexecutedSHA','postcommit_receipt':'PH8pending outside PH7tree','overall_Goal':'active'})
 plan=C/'STAGING_PLAN.json';cover=sorted({p.relative_to(WT).as_posix()for p in C.rglob('*')if p.is_file()and'__pycache__'not in p.parts}|{plan.relative_to(WT).as_posix()});selected=sorted(set(cover)|set(source_sha))
 for rel in selected:
  p=WT/rel;assert not p.is_symlink()and(rel.startswith(OWN+'/')or rel.startswith(SOURCE+'/'))and p.suffix.lower()not in('.exe','.dll','.o','.obj','.a','.lib','.bin','.pt','.pth','.onnx','.npz','.npy','.pem','.key','.usd','.usdc','.usda','.stl','.stp','.step','.zip','.7z','.jsonl'),rel
 new(plan,{'expected_source_file_SHA_from_review_index':source_sha,'preselected_cover_SHA_except_self':{p:sha((WT/p).read_bytes())for p in cover if p!=plan.relative_to(WT).as_posix()},'expected_selected_paths_without_record':selected,'new_record':RECORD,'only_new_roots':[OWN,SOURCE],'gates':['allA/noD/noForeign/exactpath','eachstagedblobvsreviewedsourceSHAorcoverSHA','record_hashmap_exact','commitparent/tree/tagtype/peel','onlyownbranch_newtag_atomic_nonforce'],'sourceprep_files':len(source_sha),'cover_files':len(cover),'receipt_must_be_PH8pending':True})
 hashes={**source_sha,**{p:sha((WT/p).read_bytes())for p in cover}};expected=set(selected)|{RECORD};verified={}
 sys.path.insert(0,str(WT/'archive_tools'));from capture_history import redact
 spec=importlib.util.spec_from_file_location('unchanged_original_recorder_for_phase7',helper);rec=importlib.util.module_from_spec(spec);spec.loader.exec_module(rec);assert rec.ROOT==WT;original=rec.git
 def check():
  nonlocal verified
  guard();assert set(paths('diff','--cached','--name-only','-z'))==expected,'Staged path mismatch'
  ns=paths('diff','--cached','--name-status','-z');assert len(ns)==2*len(expected)and all(ns[i]=='A'for i in range(0,len(ns),2)),'Not all additions'
  record=load(WT/RECORD);assert record['id']==DATE+'-'+IDENT and record['tag']==TAG and record['kind']=='diagnostic'and record['source_and_evidence_sha256']==hashes,'Record map mismatch'
  items=[]
  for item in cmd('ls-files','--stage','-z','--',OWN,SOURCE,RECORD).stdout.split(b'\0'):
   if not item:continue
   h,name=item.split(b'\t',1);mode,oid,stage=h.split();assert stage==b'0'and mode in(b'100644',b'100755');items.append((name.decode('utf-8'),oid))
  assert {n for n,_ in items}==expected
  stream=io.BytesIO(cmd('cat-file','--batch',input=b''.join(oid+b'\n'for _,oid in items)).stdout);hh={**hashes,RECORD:sha((WT/RECORD).read_bytes())}
  for name,oid in items:
   h=stream.readline().split();assert h[0]==oid and h[1]==b'blob';blob=stream.read(int(h[2]));assert stream.read(1)==b'\n'and sha(blob)==hh[name],name
  review_freeze();verified={'expected_staged_count':len(expected),'exact_paths':True,'all_A':True,'no_D_no_foreign_blob':True,'every_blob_SHA_matches_reviewed_source_or_cover':True,'record_source_hashmap_exact':True,'review_index_unchanged':SEAL_SHA};print('PH7_STAGED_EXACT_VERIFIED',json.dumps(verified),flush=True)
 def narrow(*args):
  if args and args[0]=='add':
   assert args[1]=='--'and args[2]==RECORD and set(args[3:])==set(selected),'Unexpected helper add argv'
   original('add','--force','--sparse','--',OWN,SOURCE,RECORD);check();return ''
  if args and args[0]=='commit':check()
  if args and args[0]=='push':raise AssertionError('No implicit/helper-global push')
  if args[:2]==('tag','-a'):assert args[2]==TAG
  return original(*args)
 rec.git=narrow;sys.argv=[str(helper),'--id',IDENT,'--title','Archive parent-reviewed MOD4v1 robust traditional phase7 through R61','--kind','diagnostic','--note-file',str(C/'NOTE.md'),'--validation','Immutable reviewedR61cutoff and sealedAIR; exactallA/source-cover-record blobSHAmap checkedtwice;51existingcases924000steps notnewtrials;1historicaltext+2rawunknown retained;noQA/PHY.','--files',*selected];rec.main()
 commit=text('rev-parse','HEAD');obj=text('rev-parse','refs/tags/'+TAG);peel=text('rev-parse','refs/tags/'+TAG+'^{}');assert text('cat-file','-t','refs/tags/'+TAG)=='tag'and peel==commit and text('rev-parse',commit+'^')==BASE
 assert set(paths('diff-tree','--no-commit-id','--name-only','-r','-z',commit))==expected and not text('diff','--cached','--name-only')and not text('diff','--name-only');review_freeze();guard()
 prepush=refs();oldrefs(prepush);assert prepush.get('refs/heads/'+BRANCH)==BASE and 'refs/tags/'+TAG not in prepush,'Remote changed; do not overwrite'
 push=cmd('push','--atomic','origin','HEAD:refs/heads/'+BRANCH,'refs/tags/'+TAG+':refs/tags/'+TAG);post=refs();oldrefs(post);assert post.get('refs/heads/'+BRANCH)==commit and post.get('refs/tags/'+TAG)==obj and post.get('refs/tags/'+TAG+'^{}')==commit
 review_freeze();assert sha(helper.read_bytes())==HELPER_SHA and not text('diff','--cached','--name-only')and not text('diff','--name-only')
 stdout,n1=redact(push.stdout.decode('utf-8',errors='replace'));stderr,n2=redact(push.stderr.decode('utf-8',errors='replace'))
 receipt={'status':'PH7_SINGLE_ORIGINAL_HELPER_RECORD_COMMIT_ANNOTATEDTAG_ATOMIC_OWNREFS_REMOTE_VERIFIED','commit':commit,'parent':BASE,'branch':BRANCH,'tag':TAG,'tag_object':obj,'peeled_commit':peel,'record':RECORD,'sourceprep_payload_directory':SOURCE,'sourceprep_files':len(source_sha),'cover_directory':OWN,'cover_files':len(cover),'selected_payload_without_record':len(selected),'exact_stage':verified,'source_review_index_SHA_unchanged':SEAL_SHA,'original_helper_SHA_unchanged':HELPER_SHA,'parent_copied_evidence_SHA':COPIES,'reviewed_source_summary':summary,'disclosed_gaps':'1historicalFSM ERROR_REPORT savedversion gap;2exe unknownproducerSHA with8duplicate historicalclaims; no perfectprovenance claim','remote_pre_record':pre,'remote_pre_push':prepush,'remote_post':post,'initial_main_probe':INITIAL_MAIN,'main_same_only_adjacent_push_window':prepush.get('refs/heads/main')==post.get('refs/heads/main'),'whole_archive_main_unchanged_NOT_claimed':True,'PH1_to_PH6_tag_object_and_peeled_unchanged':True,'push_stdout_redacted':stdout,'push_stderr_redacted':stderr,'push_log_redactions':n1+n2,'owner_status_before_postreceipt':text('status','--short'),'old_pending_directories_untouched_unstaged':True,'sourceRoot_model_candidate_oldscore_expertindex_main_otherrefs_mutated':False,'new_physics_oldQA_compile_once_agents_GPU_raw_asset_hash_realIO_environment_Goal_actions':False,'no_51case_or_large_manifest_repeat_revalidation':'originalhelper reads selectedarchivepayload torecordSHA; actualstagedblobs verifiedvsINDEX; no sourceRoot/results/largeassets reopened','receipt_git_status':'PHASE8_PENDING_POSTCOMMIT_NOT_IN_PHASE7_TREE','receipt_recursion_avoided':True,'overall_Goal_active':True,'recorded_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 new(PENDING/'ARCHIVE_PHASE7_RECEIPT.json',receipt);print('PH7_REMOTE_VERIFIED_RECEIPT',json.dumps(receipt,ensure_ascii=False,indent=2),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  PENDING.mkdir(parents=True,exist_ok=True);n=1
  while(PENDING/f'ARCHIVE_PHASE7_OPERATION_FAILURE_{n:03d}.txt').exists():n+=1
  (PENDING/f'ARCHIVE_PHASE7_OPERATION_FAILURE_{n:03d}.txt').write_text(traceback.format_exc()+'\nFormal PH8pending operation report. Inspect existing record/commit/tag before continuing; never replay successful record/tag. Push failure resumes same existingobjects only.\n',encoding='utf-8');raise
