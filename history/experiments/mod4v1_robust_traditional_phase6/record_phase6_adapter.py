"""ONE parent-approved PH6 original-helper record; exact own-dir blob guard."""
from pathlib import Path
import datetime,hashlib,importlib.util,io,json,os,re,subprocess,sys,traceback
WT=Path(r'F:\RMPOLAR-RL\repo-lqr-robust');C=WT/'history/experiments/mod4v1_robust_traditional_phase6';P=WT/'history/experiments/mod4v1_robust_traditional_phase6_SOURCE_PREPARATION';PENDING=WT/'history/experiments/mod4v1_robust_traditional_phase7_PENDING'
OWN=C.relative_to(WT).as_posix();SOURCE=P.relative_to(WT).as_posix();BRANCH='mod4v1-lqr-mpc-robust';BASE='0a21cdc6445268c05389103afea071836424b470';IDENT='mod4v1-robust-traditional-phase6';DATE='20261103';TAG='trial-'+DATE+'-'+IDENT;RECORD='history/experiments/'+DATE+'-'+IDENT+'.json'
HELPER_SHA='b2fd15dee16735721e18ed88b55e9e3159344f1d6f8095217f2db84852c2cd3e';SEAL_SHA='072211778f8f0f76195f76354ce59502aac9452d9b63ffb8496c9f31f163fb26';APPROVAL_SHA='af84e400e35ce6b94c60c2795a77297c02da7c257252fb8a5b48b03e6792dcaa';INITIAL_MAIN='54667e2924644affdb92b75d5df395ff0776e4dc'
OLD_TAGS={'trial-20261102-mod4v1-robust-traditional-phase1':('1064f48cc077fdd3eb6c89e554b58f5d82ee5980','93e0814f5d4dc165dda1f85f8ee12bc35be04d2f'),'trial-20261102-mod4v1-robust-traditional-phase2':('4ac41c1403a3daefa52acedbf659ee89120b6046','02b5ff84b905a4e40f207a44b0491aeff2f79b7e'),'trial-20261102-mod4v1-robust-traditional-phase3':('163d331cc4dade7bee2e870c7f2da852edec44ab','fa6838807f4d69d2b8ac52300d74ad40f365d2ed'),'trial-20261102-mod4v1-robust-traditional-phase4':('5aadabd68a83f1e4ef93dd2b18518128c46f87a9','db8fd0606e00a450504853181a6b4cdf66869d68'),'trial-20261103-mod4v1-robust-traditional-phase5':('0701622bb247649b33f78fa4627bfa3f7a1cbd9c',BASE)}
os.environ['GIT_OPTIONAL_LOCKS']='0'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def new(p,x):assert not p.exists(),str(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def cmd(*a,input=None):return subprocess.run(['git','-C',str(WT),*a],input=input,capture_output=True,check=True)
def text(*a):return cmd(*a).stdout.decode('utf-8').strip()
def paths(*a):return [x.decode('utf-8')for x in cmd(*a).stdout.split(b'\0')if x]
def guard():
 assert text('rev-parse','--show-toplevel').lower()=='f:/rmpolar-rl/repo-lqr-robust'
 assert text('symbolic-ref','--short','HEAD')==BRANCH
 assert text('rev-parse','--git-path','index').lower().replace('\\','/').endswith('/.git/worktrees/repo-lqr-robust/index')
 assert text('remote','get-url','origin')in('https://github.com/lulunomaro/polar-rl-train.git','https://github.com/lulunomaro/polar-rl-train')
def refs():
 names=['refs/heads/main','refs/heads/'+BRANCH,'refs/tags/'+TAG,'refs/tags/'+TAG+'^{}']
 for tag in OLD_TAGS:names+=['refs/tags/'+tag,'refs/tags/'+tag+'^{}']
 return {r:h for h,r in (x.split('\t')for x in text('ls-remote','origin',*names).splitlines())}
def oldrefs(r):
 for tag,(obj,commit)in OLD_TAGS.items():assert r.get('refs/tags/'+tag)==obj and r.get('refs/tags/'+tag+'^{}')==commit,(tag,r)
def frozen():
 assert sha((P/'REVIEW_INDEX.json').read_bytes())==SEAL_SHA
 approval=load(C/'PARENT_REVIEW_APPROVAL.json');assert sha((C/'PARENT_REVIEW_APPROVAL.json').read_bytes())==APPROVAL_SHA
 assert approval['decision']=='APPROVED_FOR_ONE_NEW_PHASE6_ARCHIVE_ONLY_AFTER_FINAL_NARROW_GATES' and approval['observed_HEAD']==BASE and approval['new_unique_id']==IDENT and approval['annotated_tag']==TAG
 for name,h in approval['reviewed_small_artifacts_SHA'].items():assert sha((P/name).read_bytes())==h,(name,'approved meta changed')
 idx=load(P/'REVIEW_INDEX.json');actual={p.relative_to(P).as_posix()for p in P.rglob('*')if p.is_file()and'__pycache__'not in p.parts};expected={e['relative']for e in idx['files']}|{'REVIEW_INDEX.json'};assert actual==expected,'Reviewed sourceprep pathset changed'
 for e in idx['files']:assert sha((P/e['relative']).read_bytes())==e['SHA'],e['relative']
 manifest=load(P/'FINAL_SOURCE_MANIFEST.json');g=load(P/'FINAL_GAPS_AND_EXCLUSIONS.json');assert g['unique_missing_saved_smalltext_version_count']==1 and len(g['current_raw_unknowns'])==7 and g['missing_smalltext_claims'][0]['expected_SHA']=='eea7bbf33028a3abaf697a3ec76c06fefdf53d68c8f551a6b9593fba157f048d'
 for e in manifest['entries']:
  low=e['path'].replace('\\','/').lower();assert not any(x in low for x in ('takeoff_window005','launch_manual_profile_train_v1','spin_stop_causal_v1')) and not any(int(n)>=54 for n in re.findall(r'(?<![a-z0-9])r(\d{2})(?=[^0-9]|$)',low))
 assert manifest['summary']['physical_result_files']==13 and manifest['summary']['recorded_physics_steps_actual']==182040
 assert load(P/'FINAL_CONSISTENCY_RECEIPT.json')['record_stage_commit_tag_push_Goal_actions']==0
 return manifest['summary'],len(actual)
def main():
 assert datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y%m%d')==DATE,'Use actual date; never backdate'
 guard();assert text('rev-parse','HEAD')==BASE and not text('diff','--name-only') and not text('diff','--cached','--name-only'),'Own base/tracked/staged changed; do not reset'
 helper=WT/'archive_tools/record_experiment.py';assert sha(helper.read_bytes())==HELPER_SHA
 assert not (WT/RECORD).exists()and not text('tag','--list',TAG)and not (PENDING/'ARCHIVE_PHASE6_RECEIPT.json').exists(),'Existing objects/record/receipt: inspect, never replay'
 summary,count=frozen();pre=refs();oldrefs(pre);assert pre.get('refs/heads/'+BRANCH)==BASE and 'refs/tags/'+TAG not in pre
 new(C/'PARENT_AUTHORITY_AND_FREEZE.json',{'id':IDENT,'parent_approval_SHA':APPROVAL_SHA,'original_parent_approval_path':r'F:\RMPOLAR-RL\mod4v1_lqr_mpc_robust_20261102\PH6_ARCHIVE_REVIEW_APPROVAL.json','original_record_helper_SHA':HELPER_SHA,'owned_branch':BRANCH,'base':BASE,'source_review_index_SHA':SEAL_SHA,'reviewed_meta':load(C/'PARENT_REVIEW_APPROVAL.json')['reviewed_small_artifacts_SHA'],'remote_pre_record':pre,'only_payload_directories':[OWN,SOURCE],'new_record':RECORD,'all_current_active_cutoff_excluded':True,'disclosed_gaps':'one historicalERROR_REPORTsavedSHA and7currentrawunknown(2conflictingexe+5staticJSONL); no perfectprovenance claim','postcommit_receipt':'PH7pending outside this trialtree','overall_Goal':'active'})
 plan=C/'STAGING_PLAN.json';selected=sorted({p.relative_to(WT).as_posix()for folder in(C,P)for p in folder.rglob('*')if p.is_file()and'__pycache__'not in p.parts}|{plan.relative_to(WT).as_posix()})
 for rel in selected:
  p=WT/rel;assert not p.is_symlink() and (rel.startswith(OWN+'/')or rel.startswith(SOURCE+'/')) and p.suffix.lower()not in('.exe','.dll','.o','.obj','.a','.lib','.bin','.pt','.pth','.onnx','.npz','.npy','.pem','.key','.usd','.usdc','.usda','.stl','.stp','.step','.zip','.7z','.jsonl'),rel
 new(plan,{'expected_selected_without_record':selected,'expected_new_record':RECORD,'only_allowed_new_roots':[OWN,SOURCE],'gates':['allA/noD/noForeign','every_staged_blobSHA','record_hashmap_exact','reviewed_sourcepathset_immutable'],'preselected_file_SHA_except_self':{p:sha((WT/p).read_bytes())for p in selected if p!=plan.relative_to(WT).as_posix()},'no_other_pending_directory_staged':True,'next_receipt_phase7pending':True})
 hashes={p:sha((WT/p).read_bytes())for p in selected};expected=set(selected)|{RECORD};verified={}
 sys.path.insert(0,str(WT/'archive_tools'));from capture_history import redact
 spec=importlib.util.spec_from_file_location('unchanged_original_recorder_for_phase6',helper);rec=importlib.util.module_from_spec(spec);spec.loader.exec_module(rec);assert rec.ROOT==WT;original=rec.git
 def check():
  nonlocal verified
  guard();assert set(paths('diff','--cached','--name-only','-z'))==expected,'Staged exact pathset mismatch'
  ns=paths('diff','--cached','--name-status','-z');assert len(ns)==2*len(expected)and all(ns[i]=='A'for i in range(0,len(ns),2)),'Not all-new additions'
  record=load(WT/RECORD);assert record['id']==DATE+'-'+IDENT and record['tag']==TAG and record['kind']=='diagnostic' and record['source_and_evidence_sha256']==hashes
  stage=cmd('ls-files','--stage','-z','--',OWN,SOURCE,RECORD).stdout.split(b'\0');items=[]
  for item in stage:
   if not item:continue
   head,name=item.split(b'\t',1);mode,oid,n=head.split();assert n==b'0'and mode in(b'100644',b'100755');items.append((name.decode('utf-8'),oid))
  assert {p for p,_ in items}==expected
  allhash={**hashes,RECORD:sha((WT/RECORD).read_bytes())};raw=io.BytesIO(cmd('cat-file','--batch',input=b''.join(oid+b'\n'for _,oid in items)).stdout)
  for name,oid in items:
   h=raw.readline().split();assert h[0]==oid and h[1]==b'blob';size=int(h[2]);blob=raw.read(size);assert raw.read(1)==b'\n'and sha(blob)==allhash[name],name
  frozen();verified={'expected_staged_count':len(expected),'exact_pathset':True,'all_A':True,'no_D_or_foreign':True,'every_blobSHA_frozen_or_selected':True,'record_source_map_exact':True,'SOURCE_REVIEW_INDEX_unchanged':SEAL_SHA};print('PH6_STAGED_EXACT_VERIFIED',json.dumps(verified),flush=True)
 def narrow(*args):
  if args and args[0]=='add':
   assert args[1]=='--'and args[2]==RECORD and set(args[3:])==set(selected),'Unexpected original-helper add argv'
   original('add','--force','--sparse','--',OWN,SOURCE,RECORD);check();return ''
  if args and args[0]=='commit':check()
  if args and args[0]=='push':raise AssertionError('No original-helper implicit/global push')
  if args[:2]==('tag','-a'):assert args[2]==TAG
  return original(*args)
 rec.git=narrow;sys.argv=[str(helper),'--id',IDENT,'--title','Archive reviewed MOD4v1 robust traditional phase6 through R53','--kind','diagnostic','--note-file',str(C/'NOTE.md'),'--validation','Parent-approved R53cutoff; exact source/cover/record allA/blobs verified;13existingphysicalresults182040steps; disclosed1historicaltext+7rawunknown; no newphysics.','--files',*selected];rec.main()
 commit=text('rev-parse','HEAD');obj=text('rev-parse','refs/tags/'+TAG);peeled=text('rev-parse','refs/tags/'+TAG+'^{}');assert text('cat-file','-t','refs/tags/'+TAG)=='tag'and peeled==commit and text('rev-parse',commit+'^')==BASE
 assert set(paths('diff-tree','--no-commit-id','--name-only','-r','-z',commit))==expected;assert not text('diff','--cached','--name-only')and not text('diff','--name-only');frozen();guard()
 prepush=refs();oldrefs(prepush);assert prepush.get('refs/heads/'+BRANCH)==BASE and 'refs/tags/'+TAG not in prepush,'Remote moved; do not overwrite'
 push=cmd('push','--atomic','origin','HEAD:refs/heads/'+BRANCH,'refs/tags/'+TAG+':refs/tags/'+TAG)
 post=refs();oldrefs(post);assert post.get('refs/heads/'+BRANCH)==commit and post.get('refs/tags/'+TAG)==obj and post.get('refs/tags/'+TAG+'^{}')==commit
 frozen();assert sha(helper.read_bytes())==HELPER_SHA and not text('diff','--cached','--name-only')and not text('diff','--name-only')
 stdout,n1=redact(push.stdout.decode('utf-8',errors='replace'));stderr,n2=redact(push.stderr.decode('utf-8',errors='replace'));status=text('status','--short')
 receipt={'status':'PH6_ONE_ORIGINAL_RECORD_COMMIT_ANNOTATEDTAG_ATOMIC_OWNREFS_REMOTE_VERIFIED','commit':commit,'parent':BASE,'branch':BRANCH,'tag':TAG,'tag_object':obj,'peeled_commit':peeled,'record':RECORD,'payload_directories':[OWN,SOURCE],'sourceprep_files':count,'selected_payload_without_record':len(selected),'exact_stage':verified,'original_helper_SHA_unchanged':HELPER_SHA,'review_index_SHA_unchanged':SEAL_SHA,'parent_approval_SHA':APPROVAL_SHA,'reviewed_source_summary':summary,'gap_boundary':'one inherited ERROR_REPORT savedSHA gap;7currentrawunknown, overlapold; unknown not rebuilt or archivehashed','remote_pre_record':pre,'remote_pre_push':prepush,'remote_post':post,'initial_main_probe':INITIAL_MAIN,'main_same_only_adjacent_push_window':prepush.get('refs/heads/main')==post.get('refs/heads/main'),'global_no_main_concurrency_NOT_claimed':True,'PH1_to_PH5_tag_objects_and_peeled_unchanged':True,'push_stdout_redacted':stdout,'push_stderr_redacted':stderr,'push_log_redactions':n1+n2,'owner_status_before_postreceipt':status,'other_pending_directories_untouched_not_staged':True,'receipt_git_status':'PHASE7_PENDING_POSTCOMMIT_NOT_IN_PHASE6_TREE','receipt_recursion_avoided':True,'sourceRoot_candidate_model_expertindex_main_otherrefs_mutated':False,'new_physics_unit_compile_oldonce_rawassethash_GPU_agents_realIO_goalactions':False,'recorded_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'overall_Goal_active':True}
 new(PENDING/'ARCHIVE_PHASE6_RECEIPT.json',receipt);print('PH6_REMOTE_VERIFIED_RECEIPT',json.dumps(receipt,ensure_ascii=False,indent=2),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  PENDING.mkdir(parents=True,exist_ok=True);n=1
  while(PENDING/f'ARCHIVE_PHASE6_OPERATION_FAILURE_{n:03d}.txt').exists():n+=1
  (PENDING/f'ARCHIVE_PHASE6_OPERATION_FAILURE_{n:03d}.txt').write_text(traceback.format_exc()+'\nFormal PH7pending report. Inspect existing record/commit/tag first; never replay successful record or recreate tag. Push failure resumes existingobjects only.\n',encoding='utf-8');raise
