"""ONE parent-approved PH9 archive. No robotics, raw reads or old-helper edits."""
from pathlib import Path
import datetime,hashlib,importlib.util,io,json,os,subprocess,sys,traceback
WT=Path(r'F:\RMPOLAR-RL\repo-lqr-robust');C=WT/'history/experiments/mod4v1_robust_traditional_phase9';P=WT/'history/experiments/mod4v1_robust_traditional_phase9_SOURCE_PREPARATION';PENDING=WT/'history/experiments/mod4v1_robust_traditional_phase10_PENDING'
OWN=C.relative_to(WT).as_posix();SOURCE=P.relative_to(WT).as_posix();BRANCH='mod4v1-lqr-mpc-robust';BASE='662204600bf79ace36815db569a5d02f3b327981';IDENT='mod4v1-robust-traditional-phase9';DATE='20261103';TAG='trial-'+DATE+'-'+IDENT;RECORD='history/experiments/'+DATE+'-'+IDENT+'.json'
HELPER_SHA='b2fd15dee16735721e18ed88b55e9e3159344f1d6f8095217f2db84852c2cd3e';SEAL_SHA='6e76cd33edf5c6cb4c654174a6707b0fffea8fe8dad67c89197f81dda6e77635';INITIAL_MAIN='8654c630b403d717cc1cae707a7b7150946f9d9f'
COPIES={'PH9_ARCHIVE_REVIEW_APPROVAL.json':'e62ef27263e4a6f9db3ac1026f814721ecb28ac3839ec2baab5fc4860a6081cc','PH9_PARENT_NUMERIC_CHECK.json':'174b87bd520e20c62060b7a3e39ce78782ad27e4d5b7454ead7f3abb19953c24','review_ph9_parent_numeric_v1.py':'7d20391dc3cb4fcbaf0da8b82e9fc040b6f9ebee532a0f4a1dff245bc9d3dda2'}
# Explicit previously verified object/peel constants; no old adapter import/evaluation.
OLD_TAGS={'trial-20261102-mod4v1-robust-traditional-phase1':('1064f48cc077fdd3eb6c89e554b58f5d82ee5980','93e0814f5d4dc165dda1f85f8ee12bc35be04d2f'),'trial-20261102-mod4v1-robust-traditional-phase2':('4ac41c1403a3daefa52acedbf659ee89120b6046','02b5ff84b905a4e40f207a44b0491aeff2f79b7e'),'trial-20261102-mod4v1-robust-traditional-phase3':('163d331cc4dade7bee2e870c7f2da852edec44ab','fa6838807f4d69d2b8ac52300d74ad40f365d2ed'),'trial-20261102-mod4v1-robust-traditional-phase4':('5aadabd68a83f1e4ef93dd2b18518128c46f87a9','db8fd0606e00a450504853181a6b4cdf66869d68'),'trial-20261103-mod4v1-robust-traditional-phase5':('0701622bb247649b33f78fa4627bfa3f7a1cbd9c','0a21cdc6445268c05389103afea071836424b470'),'trial-20261103-mod4v1-robust-traditional-phase6':('db83d307944644ccf46b4b43b79ffc5633d6897b','4e7a3fb9855657b5b501de08785f875b1e0bedfd'),'trial-20261103-mod4v1-robust-traditional-phase7':('14ec4a088bd7959ef8811feded2c51e77c70f35d','223577994e0f750e0ae062ce9ffee204273c90a2'),'trial-20261103-mod4v1-robust-traditional-phase8':('ddcfcf6e1afc48490493529377d1263c8fe4ef08','662204600bf79ace36815db569a5d02f3b327981')}
os.environ['GIT_OPTIONAL_LOCKS']='0'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def new(p,x):
 assert not p.exists(),str(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8',newline='\n')
def cmd(*a,input=None):return subprocess.run(['git','-C',str(WT),*a],input=input,capture_output=True,check=True)
def text(*a):return cmd(*a).stdout.decode('utf-8').strip()
def paths(*a):return[x.decode('utf-8')for x in cmd(*a).stdout.split(b'\0')if x]
def guard():
 assert text('rev-parse','--show-toplevel').replace('\\','/').lower()=='f:/rmpolar-rl/repo-lqr-robust'
 assert text('symbolic-ref','--short','HEAD')==BRANCH
 assert text('rev-parse','--git-path','index').replace('\\','/').lower().endswith('/.git/worktrees/repo-lqr-robust/index')
 assert text('remote','get-url','origin')in('https://github.com/lulunomaro/polar-rl-train.git','https://github.com/lulunomaro/polar-rl-train')
def refs():
 wanted=['refs/heads/main','refs/heads/'+BRANCH,'refs/tags/'+TAG,'refs/tags/'+TAG+'^{}']
 for t in OLD_TAGS:wanted+=['refs/tags/'+t,'refs/tags/'+t+'^{}']
 return{r:h for h,r in(line.split('\t')for line in text('ls-remote','origin',*wanted).splitlines())}
def oldrefs(r):
 for t,(obj,peel)in OLD_TAGS.items():assert r.get('refs/tags/'+t)==obj and r.get('refs/tags/'+t+'^{}')==peel,('Old annotated tag moved',t)
def frozen():
 assert sha((P/'REVIEW_INDEX.json').read_bytes())==SEAL_SHA,'Reviewed INDEX changed'
 for n,h in COPIES.items():assert sha((C/n).read_bytes())==h,('Approval copy changed',n)
 approval=load(C/'PH9_ARCHIVE_REVIEW_APPROVAL.json');num=load(C/'PH9_PARENT_NUMERIC_CHECK.json')
 assert approval['status']=='PARENT_ACCEPTS_ONE_CLOSED_R63_PHASE9_ARCHIVE_UNDER_ORIGINAL_HUMAN_GIT_STRATEGY'and approval['expected_parent']==BASE
 op=approval['operation'];assert op['unique_record_id']==IDENT and op['annotated_tag']==TAG and op['helper_original_SHA']==HELPER_SHA
 assert approval['review_index_SHA']==SEAL_SHA and sha((P/'REVIEW_HANDOFF.md').read_bytes())==approval['handoff_SHA']and sha((P/'FINAL_CONSISTENCY_RECEIPT.json').read_bytes())==approval['consistency_SHA']
 assert num['status']=='PASS_PARENT_R63_SIX_SMALL_RESULT_GATE_AND_SENTINEL_RECONCILIATION'and(num['physical_cases'],num['actual_controls'],num['actual_physics_steps'])==(6,4800,96000)
 assert(num['nominal_pass'],num['selected_TRAIN_pass'],num['old_same_four_pass'],num['main_rear_firstflight_paired'])==(2,1,2,4)
 assert num['current_saved_text_gap_unique']==1 and num['inherited_prior_saved_text_gaps_unique']==2 and num['overlap_not_summed']and num['current_conflicting_binary_unknowns']==2 and num['deliberate_zero_SHA_negative_fixture_not_missing_source']
 for e in num['review_files']:assert sha((P/Path(e['path']).name).read_bytes())==e['SHA'],e['path']
 idx=load(P/'REVIEW_INDEX.json');source={SOURCE+'/'+e['relative']:e['SHA']for e in idx['files']};source[SOURCE+'/REVIEW_INDEX.json']=SEAL_SHA
 actual={p.relative_to(WT).as_posix()for p in P.rglob('*')if p.is_file()and '__pycache__'not in p.parts};assert actual==set(source),'Reviewed SOURCE file set changed'
 receipt_entries=[e for e in idx['files']if Path(e['relative']).name=='ARCHIVE_PHASE8_RECEIPT.json'];assert len(receipt_entries)==1
 previous=WT/SOURCE/receipt_entries[0]['relative'];assert load(previous)['commit']==BASE,'Prior receipt not exact PH8'
 consistency=load(P/'FINAL_CONSISTENCY_RECEIPT.json');assert consistency['record_stage_commit_tag_push_calls']==0
 assert consistency['summary']['current_missing_saved_smalltext_unique']==1 and consistency['summary']['current_raw_unknowns']==2
 return idx,source,approval,num,consistency,receipt_entries[0]
def main():
 assert datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y%m%d')==DATE,'Actual date only; no backdating'
 guard();assert text('rev-parse','HEAD')==BASE and not text('diff','--cached','--name-only')and not text('diff','--name-only'),'Owned state changed; never reset'
 helper=WT/'archive_tools/record_experiment.py';assert sha(helper.read_bytes())==HELPER_SHA
 assert not(WT/RECORD).exists()and not text('tag','--list',TAG)and not(PENDING/'ARCHIVE_PHASE9_RECEIPT.json').exists(),'Objects/record/receipt present: inspect, do not replay'
 idx,source_sha,approval,num,consistency,previous=frozen();pre=refs();oldrefs(pre);assert pre.get('refs/heads/'+BRANCH)==BASE and 'refs/tags/'+TAG not in pre
 new(C/'PARENT_AUTHORITY_AND_FREEZE.json',{'status':'ONE_PHASE9_ARCHIVE_AUTHORIZED_AFTER_PARENT_REVIEW','approval_copies_SHA':COPIES,'parent':BASE,'branch':BRANCH,'id':IDENT,'tag':TAG,'helper_SHA':HELPER_SHA,'review_index_SHA':SEAL_SHA,'source_frozen_no_recapture':True,'reviewed_source_count':len(source_sha),'remote_pre_record':pre,'allowed_roots':[OWN,SOURCE],'new_record':RECORD,'current_saved_text_gap_unique':1,'inherited_prior_gaps_unique':2,'overlap_not_summed':True,'current_unknown_exe':2,'deliberate_bad_SHA_fixture_not_missing_source':True,'all_new_momentum_collector_R64plus_excluded':True,'overall_Goal_active':True})
 plan=OWN+'/STAGING_PLAN.json';cover=sorted({p.relative_to(WT).as_posix()for p in C.rglob('*')if p.is_file()and '__pycache__'not in p.parts}|{plan});selected=sorted(set(source_sha)|set(cover));expected=set(selected)|{RECORD}
 for p in selected:
  f=WT/p;assert p.startswith((OWN+'/',SOURCE+'/'))and not f.is_symlink()
  assert f.suffix.lower()not in{'.exe','.dll','.o','.obj','.a','.lib','.bin','.pt','.pth','.onnx','.npz','.npy','.pem','.key','.usd','.usdc','.usda','.stl','.stp','.step','.zip','.7z','.jsonl','.pdf','.png','.jpg','.jpeg','.mp4'},p
 cover_no_plan={p:sha((WT/p).read_bytes())for p in cover if p!=plan}
 new(WT/plan,{'status':'EXACT_NEW_PHASE9_ADDITIONS_PREREGISTERED_BEFORE_ORIGINAL_RECORDER','allowed_roots':[OWN,SOURCE],'selected_paths':selected,'new_record':RECORD,'expected_staged_count':len(expected),'source_payload_SHA_from_reviewed_INDEX':source_sha,'cover_SHA_except_plan_self':cover_no_plan,'checks':['exactPaths','allA','noD','noForeign','everyStagedBlobSHA','recordMap','committedParentPathsAndEveryBlob','annotatedTag','atomicOwnedRefs'],'prior_postreceipt_only_source_snapshot':previous,'phase10_receipt_not_in_this_commit':True,'no_new_robotics_QA_or_raw_hashes':True})
 hashes={**source_sha,**{p:sha((WT/p).read_bytes())for p in cover}}
 sys.path.insert(0,str(WT/'archive_tools'));from capture_history import redact
 spec=importlib.util.spec_from_file_location('unchanged_phase9_original_recorder',helper);rec=importlib.util.module_from_spec(spec);spec.loader.exec_module(rec);assert rec.ROOT==WT;original=rec.git;checked_commit=[None];staged_checks=[]
 def blob_gate(objects,expected_hashes,label):
  assert set(objects)==expected and set(expected_hashes)==expected,(label,'exact blob path set')
  names=sorted(objects);buf=io.BytesIO(cmd('cat-file','--batch',input=('\n'.join(objects[n]for n in names)+'\n').encode('ascii')).stdout)
  for n in names:
   header=buf.readline().decode('ascii').strip().split();assert len(header)==3 and header[1]=='blob',(label,n,header)
   size=int(header[2]);raw=buf.read(size);assert len(raw)==size and buf.read(1)==b'\n';assert sha(raw)==expected_hashes[n],(label,'blob SHA',n)
  assert not buf.read(),label
 def check():
  guard();assert set(paths('diff','--cached','--name-only','-z'))==expected,'Staged exact paths mismatch'
  ns=paths('diff','--cached','--name-status','-z');assert len(ns)==2*len(expected)and all(ns[i]=='A'for i in range(0,len(ns),2)),'Not all additions/noD'
  record=load(WT/RECORD);assert record['id']==DATE+'-'+IDENT and record['tag']==TAG and record['kind']=='diagnostic'and record['source_and_evidence_sha256']==hashes,'Record hash map mismatch'
  allhash={**hashes,RECORD:sha((WT/RECORD).read_bytes())};objects={}
  for line in paths('ls-files','--stage','-z','--',OWN,SOURCE,RECORD):
   row,n=line.split('\t',1);mode,oid,stage=row.split();assert stage=='0'and mode in('100644','100755');objects[n]=oid
  blob_gate(objects,allhash,'staged');frozen();result={'count':len(expected),'exact_paths':True,'allA':True,'noD_noForeign':True,'every_blob_SHA':True,'record_map_exact':True,'review_index_unchanged':SEAL_SHA};staged_checks.append(result);print('PH9_STAGED_EXACT_VERIFIED',json.dumps(result),flush=True)
 def committed():
  guard();commit=text('rev-parse','HEAD');assert text('rev-parse','HEAD^')==BASE,'Commit parent mismatch';assert set(paths('diff-tree','--no-commit-id','--name-only','-r','-z','HEAD'))==expected,'Committed change paths mismatch'
  objects={}
  for line in paths('ls-tree','-r','-z','HEAD','--',OWN,SOURCE,RECORD):
   row,n=line.split('\t',1);mode,typ,oid=row.split();assert typ=='blob'and mode in('100644','100755');objects[n]=oid
  blob_gate(objects,{**hashes,RECORD:sha((WT/RECORD).read_bytes())},'committed-tree');checked_commit[0]=commit;print('PH9_COMMITTED_TREE_EXACT_VERIFIED',json.dumps({'commit':commit,'parent':BASE,'count':len(expected),'every_tree_blob_SHA':True}),flush=True)
 def narrow(*args):
  if args and args[0]=='add':
   assert args[1]=='--'and args[2]==RECORD and set(args[3:])==set(selected),'Unexpected original helper add argv'
   original('add','--force','--sparse','--',OWN,SOURCE,RECORD);check();return''
  if args and args[0]=='commit':check()
  if args and args[0]=='push':raise AssertionError('No helper implicit/global push')
  if args[:2]==('tag','-a'):assert args[2]==TAG;committed()
  return original(*args)
 rec.git=narrow;sys.argv=[str(helper),'--id',IDENT,'--title','Archive parent-reviewed MOD4v1 robust traditional phase9 closed R63','--kind','diagnostic','--note-file',str(C/'NOTE.md'),'--validation','Closed six R63 cases 4800 controls 96000 prior steps; nominal2of2 selected1of4 vs oldsame4 2of4; failures/gaps preserved; exact staged and tree blobs; no robot replay.','--files',*selected];rec.main()
 guard();commit=text('rev-parse','HEAD');tag_obj=text('rev-parse',TAG);assert checked_commit[0]==commit and text('cat-file','-t',TAG)=='tag'and text('rev-parse',TAG+'^{}')==commit
 assert not text('diff','--cached','--name-only')and not text('diff','--name-only');frozen();assert sha(helper.read_bytes())==HELPER_SHA
 prepush=refs();oldrefs(prepush);assert prepush.get('refs/heads/'+BRANCH)==BASE and 'refs/tags/'+TAG not in prepush,'Remote moved: no overwrite'
 push=cmd('push','--atomic','origin','HEAD:refs/heads/'+BRANCH,'refs/tags/'+TAG+':refs/tags/'+TAG)
 post=refs();oldrefs(post);assert post.get('refs/heads/'+BRANCH)==commit and post.get('refs/tags/'+TAG)==tag_obj and post.get('refs/tags/'+TAG+'^{}')==commit,'Remote objects not exact'
 frozen();assert sha(helper.read_bytes())==HELPER_SHA and not text('diff','--cached','--name-only')and not text('diff','--name-only')
 stdout,n1=redact(push.stdout.decode('utf-8','replace'));stderr,n2=redact(push.stderr.decode('utf-8','replace'))
 receipt={'status':'PH9_ONE_ORIGINAL_HELPER_RECORD_COMMIT_ANNOTATEDTAG_ATOMIC_OWNREFS_REMOTE_VERIFIED','recorded_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'commit':commit,'parent':BASE,'branch':BRANCH,'tag':TAG,'tag_object':tag_obj,'peeled_commit':text('rev-parse',TAG+'^{}'),'record':RECORD,'source_payload_files':len(source_sha),'cover_files':len(cover),'selected_files_excluding_record':len(selected),'total_staged_committed_paths':len(expected),'double_staged_gates':staged_checks,'committed_tree_parent_path_blob_gate_passed':True,'helper_unmodified_SHA':HELPER_SHA,'review_index_unchanged_SHA':SEAL_SHA,'parent_evidence_copies_SHA':COPIES,'source_preparation_historical_summary':consistency['summary'],'independent_parent_numeric_summary':{k:num[k]for k in('physical_cases','actual_controls','actual_physics_steps','nominal_pass','selected_TRAIN_pass','old_same_four_pass','main_rear_firstflight_paired','current_saved_text_gap_unique','inherited_prior_saved_text_gaps_unique','current_conflicting_binary_unknowns')},'source1259verification_child_saved_not_parent_or_archive_replay':True,'disclosed_gaps':'Current FSM savedtext version1 overlaps prior2; no reconstruction. Eight repeated binary claims concern two unknown-current executables. Deliberately wrong zero64 fixture preserved, not falsely missing real source.','prior_PH8postreceipt_in_frozen_source':previous,'old_pending5_to9_untouched_unstaged':True,'remote_pre_record':pre,'remote_immediate_pre_push':prepush,'remote_post_push':post,'initial_main_probe':INITIAL_MAIN,'main_same_only_adjacent_push_window':prepush.get('refs/heads/main')==post.get('refs/heads/main'),'whole_archive_main_unchanged_NOT_claimed':True,'PH1_to_PH8_tag_objects_and_peels_unchanged':True,'push_stdout_redacted':stdout,'push_stderr_redacted':stderr,'push_log_redactions':n1+n2,'owner_status_before_postreceipt':text('status','--short'),'sourceRoot_model_controller_scores_expertindex_main_otherrefs_mutated':False,'new_PHY_QA_unit_compile_once_GPU_agents_raw_PDF_ZIP_asset_hash_environment_realIO_Goal_actions':False,'new_momentum_method_collector_R64plus_excluded':True,'receipt_git_status':'PHASE10_PENDING_POSTCOMMIT_NOT_IN_PHASE9_TREE','receipt_recursion_avoided':True,'overall_Goal_active':True}
 new(PENDING/'ARCHIVE_PHASE9_RECEIPT.json',receipt);print('PH9_REMOTE_VERIFIED_RECEIPT',json.dumps(receipt,ensure_ascii=False,indent=2),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException as exc:
  PENDING.mkdir(parents=True,exist_ok=True);n=1
  while(PENDING/f'ARCHIVE_PHASE9_OPERATION_FAILURE_{n:03d}.txt').exists():n+=1
  detail=traceback.format_exc()
  if isinstance(exc,subprocess.CalledProcessError):
   detail+='\nCAPTURED_STDOUT\n'+(exc.stdout or b'').decode('utf-8','replace')+'\nCAPTURED_STDERR\n'+(exc.stderr or b'').decode('utf-8','replace')
  detail+='\nFormal PH10pending operation failure. Inspect existing record/commit/tag first; never replay successful record/tag; push failure continues existing objects only.\n'
  (PENDING/f'ARCHIVE_PHASE9_OPERATION_FAILURE_{n:03d}.txt').write_text(detail,encoding='utf-8');(PENDING/f'ARCHIVE_PHASE9_OPERATION_FAILURE_SOURCE_{n:03d}.py').write_bytes(Path(__file__).read_bytes());raise
