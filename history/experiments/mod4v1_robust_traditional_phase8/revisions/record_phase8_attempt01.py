"""ONE parent-approved frozen PH8 archive; original helper unchanged, no robot work."""
from pathlib import Path
import ast,datetime,hashlib,importlib.util,io,json,os,subprocess,sys,traceback
WT=Path(r'F:\RMPOLAR-RL\repo-lqr-robust');C=WT/'history/experiments/mod4v1_robust_traditional_phase8';P=WT/'history/experiments/mod4v1_robust_traditional_phase8_SOURCE_PREPARATION';PENDING=WT/'history/experiments/mod4v1_robust_traditional_phase9_PENDING'
OWN=C.relative_to(WT).as_posix();SOURCE=P.relative_to(WT).as_posix();BRANCH='mod4v1-lqr-mpc-robust';BASE='223577994e0f750e0ae062ce9ffee204273c90a2';IDENT='mod4v1-robust-traditional-phase8';DATE='20261103';TAG='trial-'+DATE+'-'+IDENT;RECORD='history/experiments/'+DATE+'-'+IDENT+'.json'
HELPER_SHA='b2fd15dee16735721e18ed88b55e9e3159344f1d6f8095217f2db84852c2cd3e';SEAL_SHA='cf221aabc00e258dd66d40292f7ebec7ee88b6f24280e06756c5fba4976b758e';INITIAL_MAIN='0e9c71a06d802723185fa54b2410915d931e6925'
COPIES={'PH8_ARCHIVE_REVIEW_APPROVAL.json':'208437b29bed3d3fbf2999eb372ad55c9f7ac43658dd1b1e6a73fc35ec250786','PH8_PARENT_NUMERIC_CHECK.json':'901d244b41ff46dfb6e157032c8fd0b7101abfb0ac7f912d941a6428c10a765c','review_ph8_parent_numeric_v1.py':'1431a5ec6966aaff202e025201f193c588bf434c1f59a943f1babb7f00d16a8e'}
# Read only the previous adapter's literal old-ref data; never import/execute it.
oldtree=ast.parse((WT/'history/experiments/mod4v1_robust_traditional_phase7/record_phase7_adapter.py').read_text(encoding='utf-8'))
OLD_TAGS=next(ast.literal_eval(n.value)for n in oldtree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='OLD_TAGS'for t in n.targets))
OLD_TAGS['trial-20261103-mod4v1-robust-traditional-phase7']=('14ec4a088bd7959ef8811feded2c51e77c70f35d',BASE)
os.environ['GIT_OPTIONAL_LOCKS']='0'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def new(p,x):
 assert not p.exists(),str(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def cmd(*a,input=None):return subprocess.run(['git','-C',str(WT),*a],input=input,capture_output=True,check=True)
def text(*a):return cmd(*a).stdout.decode('utf-8').strip()
def paths(*a):return[x.decode('utf-8')for x in cmd(*a).stdout.split(b'\0')if x]
def guard():
 assert text('rev-parse','--show-toplevel').replace('\\','/').lower()=='f:/rmpolar-rl/repo-lqr-robust'
 assert text('symbolic-ref','--short','HEAD')==BRANCH
 assert text('rev-parse','--git-path','index').replace('\\','/').lower().endswith('/.git/worktrees/repo-lqr-robust/index')
 assert text('remote','get-url','origin')in('https://github.com/lulunomaro/polar-rl-train.git','https://github.com/lulunomaro/polar-rl-train')
def refs():
 names=['refs/heads/main','refs/heads/'+BRANCH,'refs/tags/'+TAG,'refs/tags/'+TAG+'^{}']
 for t in OLD_TAGS:names+=['refs/tags/'+t,'refs/tags/'+t+'^{}']
 return{line.split('\t')[1]:line.split('\t')[0]for line in text('ls-remote','origin',*names).splitlines()}
def oldrefs(r):
 for t,(obj,peeled)in OLD_TAGS.items():assert r.get('refs/tags/'+t)==obj and r.get('refs/tags/'+t+'^{}')==peeled,(t,r)
def frozen():
 assert sha((P/'REVIEW_INDEX.json').read_bytes())==SEAL_SHA
 for n,h in COPIES.items():assert sha((C/n).read_bytes())==h,n
 approval=load(C/'PH8_ARCHIVE_REVIEW_APPROVAL.json');num=load(C/'PH8_PARENT_NUMERIC_CHECK.json');idx=load(P/'REVIEW_INDEX.json')
 assert approval['status']=='PARENT_REVIEW_ACCEPTED_ONE_PHASE8_ARCHIVE_UNDER_ORIGINAL_HUMAN_GIT_STRATEGY'and approval['expected_parent_commit']==BASE
 op=approval['allowed_operation'];assert op['unique_record_id']==IDENT and op['annotated_tag']==TAG and op['original_record_helper_SHA']==HELPER_SHA
 assert approval['review_index_SHA']==SEAL_SHA and approval['review_handoff_SHA']==idx['handoff']['SHA']and approval['consistency_receipt_SHA']==idx['consistency']['SHA']
 assert num['status']=='PASS_PARENT_SIX_SAVED_SMALL_RESULTS_AND_GAPS_RECONCILIATION'and(num['physical_cases'],num['actual_controls'],num['actual_physics_steps'])==(6,4800,96000)
 for e in num['review_files']:assert sha((P/Path(e['path']).name).read_bytes())==e['SHA']
 assert num['unique_smalltext_saved_version_gaps']==2 and num['conflicting_binary_current_unknowns']==2
 expected={SOURCE+'/'+e['relative']:e['SHA']for e in idx['files']};expected[SOURCE+'/REVIEW_INDEX.json']=SEAL_SHA
 actual={p.relative_to(WT).as_posix()for p in P.rglob('*')if p.is_file()and '__pycache__'not in p.parts};assert set(expected)==actual,'Reviewed source file set changed'
 receipt_entries=[e for e in idx['files']if Path(e['relative']).name=='ARCHIVE_PHASE7_RECEIPT.json'];assert len(receipt_entries)==1
 prior=load(P/receipt_entries[0]['relative']);assert prior['commit']==BASE,'Previous postreceipt not in reviewed snapshot'
 consistency=load(P/'FINAL_CONSISTENCY_RECEIPT.json');assert consistency['record_stage_commit_tag_push_calls']==0 and consistency['summary']['smalltext_missing_saved_versions_unique']==2 and consistency['summary']['current_raw_unknowns']==2
 return idx,expected,approval,num,consistency,receipt_entries[0]
def main():
 assert datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y%m%d')==DATE,'Actual date only; no backdating'
 guard();assert text('rev-parse','HEAD')==BASE and not text('diff','--cached','--name-only')and not text('diff','--name-only'),'Owned state changed; do not reset'
 helper=WT/'archive_tools/record_experiment.py';assert sha(helper.read_bytes())==HELPER_SHA
 assert not(WT/RECORD).exists()and not text('tag','--list',TAG)and not(PENDING/'ARCHIVE_PHASE8_RECEIPT.json').exists(),'Objects/record/receipt already present: inspect, do not replay'
 idx,source_hashes,approval,num,consistency,previous_receipt=frozen();pre=refs();oldrefs(pre);assert pre.get('refs/heads/'+BRANCH)==BASE and'refs/tags/'+TAG not in pre
 new(C/'PARENT_AUTHORITY_AND_FREEZE.json',{'authority':'Explicit parent PH8 approval under original human all-trials policy','copied_parent_SHA':COPIES,'branch':BRANCH,'base':BASE,'record':RECORD,'tag':TAG,'helper_SHA':HELPER_SHA,'review_index_SHA':SEAL_SHA,'initial_main_probe':INITIAL_MAIN,'remote_pre_record':pre,'source_preparation_kept_readonly':True,'previous_postreceipt_archived_as_frozen_source_path':previous_receipt['relative'],'original_pending_not_independently_staged':True,'provenance_gaps':'2 saved smalltext versions;2 conflicting exe current SHA; no reconstruction or completeness inflation','allowed_roots':[OWN,SOURCE],'active_R63_and_postcut_excluded':True,'new_PHY_QA_Git_to_otherrefs_not_authorized':True})
 cover=sorted({p.relative_to(WT).as_posix()for p in C.rglob('*')if p.is_file()and '__pycache__'not in p.parts}|{OWN+'/STAGING_PLAN.json'})
 selected=sorted(set(source_hashes)|set(cover));expected=set(selected)|{RECORD}
 deny={'.exe','.dll','.o','.obj','.a','.lib','.bin','.pt','.pth','.onnx','.npz','.npy','.pem','.key','.usd','.usdc','.usda','.stl','.stp','.step','.zip','.7z','.jsonl','.pdf','.png','.jpg','.jpeg','.mp4'}
 for n in selected:assert n.startswith((OWN+'/',SOURCE+'/'))and not(WT/n).is_symlink()and Path(n).suffix.lower()not in deny,n
 new(C/'STAGING_PLAN.json',{'expected_payload_paths':selected,'generated_record':RECORD,'expected_staged_count':len(expected),'source_hash_map_from_immutable_review_index':source_hashes,'cover_SHA_except_plan_self':{p:sha((WT/p).read_bytes())for p in cover if not p.endswith('/STAGING_PLAN.json')},'checks':['exact staged/committed pathset','allA/noD/noForeign','every staged blob matches indexed source or chosen cover','original-helper record map exact','committed tree blobs match indexed source or chosen cover'],'outside_this_tree_formal_receipt':str(PENDING/'ARCHIVE_PHASE8_RECEIPT.json'),'no_raw_assets_original_manifest_or_case_reruns':True})
 hashes={**source_hashes,**{p:sha((WT/p).read_bytes())for p in cover}}
 sys.path.insert(0,str(WT/'archive_tools'));from capture_history import redact
 spec=importlib.util.spec_from_file_location('unchanged_ph8_original_recorder',helper);rec=importlib.util.module_from_spec(spec);spec.loader.exec_module(rec);assert rec.ROOT==WT;original=rec.git;validated_commit=[None]
 def blob_gate(objects,expected_hashes,label):
  assert set(objects)==expected,'Blob object pathset mismatch'
  stream=io.BytesIO(cmd('cat-file','--batch',input=('\n'.join(objects[n]for n in sorted(objects))+'\n').encode()).stdout)
  for name in sorted(objects):
   header=stream.readline().decode().split();assert len(header)==3 and header[0]==objects[name]and header[1]=='blob';raw=stream.read(int(header[2]));assert stream.read(1)==b'\n'and sha(raw)==expected_hashes[name],(label,name)
  assert not stream.read()
 def check():
  guard();assert set(paths('diff','--cached','--name-only','-z'))==expected,'Staged exact paths mismatch'
  ns=paths('diff','--cached','--name-status','-z');assert len(ns)==2*len(expected)and all(ns[i]=='A'for i in range(0,len(ns),2)),'Not all additions'
  record=load(WT/RECORD);assert record['id']==DATE+'-'+IDENT and record['tag']==TAG and record['kind']=='diagnostic'and record['source_and_evidence_sha256']==hashes,'Record map mismatch'
  objs={}
  for line in paths('ls-files','--stage','-z','--',OWN,SOURCE,RECORD):
   info,name=line.split('\t',1);mode,oid,stage=info.split();assert stage=='0'and mode in('100644','100755');objs[name]=oid
  blob_gate(objs,{**hashes,RECORD:sha((WT/RECORD).read_bytes())},'staged');frozen()
  print('PH8_STAGED_EXACT_VERIFIED',json.dumps({'expected_count':len(expected),'exact_paths':True,'allA':True,'noD_noForeign':True,'every_blob_SHA':True,'record_map_exact':True,'review_index_unchanged':SEAL_SHA}),flush=True)
 def committed():
  guard();commit=text('rev-parse','HEAD');assert text('rev-parse','HEAD^')==BASE
  assert set(paths('diff-tree','--no-commit-id','--name-only','-r','-z',commit))==expected,'Committed paths mismatch'
  objs={}
  for line in paths('ls-tree','-r','-z','HEAD','--',OWN,SOURCE,RECORD):
   info,name=line.split('\t',1);mode,typ,oid=info.split();assert mode in('100644','100755')and typ=='blob';objs[name]=oid
  blob_gate(objs,{**hashes,RECORD:sha((WT/RECORD).read_bytes())},'committed_tree');validated_commit[0]=commit
  print('PH8_COMMITTED_TREE_EXACT_VERIFIED',json.dumps({'count':len(expected),'parent':BASE,'every_tree_blob_SHA':True}),flush=True)
 def narrow(*args):
  if args and args[0]=='add':
   assert args[1]=='--'and args[2]==RECORD and set(args[3:])==set(selected),'Unexpected helper add argv'
   original('add','--force','--sparse','--',OWN,SOURCE,RECORD);check();return''
  if args and args[0]=='commit':check()
  if args and args[0]=='push':raise AssertionError('No helper implicit/global push')
  if args[:2]==('tag','-a'):assert args[2]==TAG;committed()
  return original(*args)
 rec.git=narrow;sys.argv=[str(helper),'--id',IDENT,'--title','Archive parent-reviewed MOD4v1 robust traditional phase8 closed R62 and insights','--kind','diagnostic','--note-file',str(C/'NOTE.md'),'--validation','Frozen six-case R62/nominal2of2 selected1of4 old2of4; saved failures and two text gaps/two exe unknowns; exact reviewed archive blobs, no new robotics work','--files',*selected];rec.main()
 guard();commit=text('rev-parse','HEAD');assert commit==validated_commit[0]and text('cat-file','-t',TAG)=='tag'and text('rev-parse',TAG+'^{}')==commit;tagobj=text('rev-parse',TAG)
 assert not text('diff','--cached','--name-only')and not text('diff','--name-only');frozen();assert sha(helper.read_bytes())==HELPER_SHA
 prepush=refs();oldrefs(prepush);assert prepush.get('refs/heads/'+BRANCH)==BASE and'refs/tags/'+TAG not in prepush,'Remote moved: never overwrite'
 push=cmd('push','--atomic','origin','HEAD:refs/heads/'+BRANCH,'refs/tags/'+TAG+':refs/tags/'+TAG)
 post=refs();oldrefs(post);assert post.get('refs/heads/'+BRANCH)==commit and post.get('refs/tags/'+TAG)==tagobj and post.get('refs/tags/'+TAG+'^{}')==commit
 frozen();assert sha(helper.read_bytes())==HELPER_SHA and not text('diff','--cached','--name-only')and not text('diff','--name-only')
 stdout,n1=redact(push.stdout.decode('utf-8'));stderr,n2=redact(push.stderr.decode('utf-8'))
 receipt={'status':'PH8_ONE_ORIGINAL_RECORD_COMMIT_ANNOTATEDTAG_ATOMIC_OWNREFS_REMOTE_VERIFIED','branch':BRANCH,'commit':commit,'parent':BASE,'tag':TAG,'tag_object':tagobj,'peeled_commit':commit,'record':RECORD,'source_payload_files':len(source_hashes),'cover_files':len(cover),'selected_payload_files_excluding_record':len(selected),'expected_staged_count':len(expected),'two_staged_gates':{'exact_paths':True,'allA':True,'noD_noForeign':True,'each_blob_SHA':True,'record_map_exact':True},'committed_tree_blob_paths_SHA_and_parent_verified':True,'original_helper_SHA_unchanged':HELPER_SHA,'review_index_SHA_unchanged':SEAL_SHA,'parent_copied_SHA':COPIES,'source_preparation_historical_summary':consistency['summary'],'parent_independent_check_summary':{k:num[k]for k in('physical_cases','actual_controls','actual_physics_steps','nominal_pass','selected_TRAIN_pass','same_four_old_baseline_pass','unique_smalltext_saved_version_gaps','conflicting_binary_current_unknowns')},'source_1360verification_is_child_saved_not_new_parent_or_archive_replay':True,'disclosed_gaps':'2unique historical savedtext versions;2current conflicted exe hashes/eight duplicateclaims; no reconstructed evidence','PH7postreceipt_in_frozen_source':previous_receipt,'original_pending5_6_7_8_untouched_unstaged':True,'remote_pre_record':pre,'remote_immediate_pre_push':prepush,'remote_post_push':post,'initial_main_probe':INITIAL_MAIN,'main_same_only_adjacent_push_window':prepush.get('refs/heads/main')==post.get('refs/heads/main'),'whole_archive_main_unchanged_NOT_claimed':True,'PH1_to_PH7_tag_object_and_peeled_unchanged':True,'push_stdout_redacted':stdout,'push_stderr_redacted':stderr,'push_log_redactions':n1+n2,'owner_status_before_postreceipt':text('status','--short'),'sourceRoot_model_controller_oldscore_expertindex_main_otherrefs_mutated':False,'new_PHY_QA_unit_compile_once_GPU_agents_raw_PDF_ZIP_asset_hash_environment_realIO_Goal_actions':False,'active_R63_and_all_postcut_not_in_PH8':True,'receipt_git_status':'PHASE9_PENDING_POSTCOMMIT_NOT_IN_PHASE8_TREE','receipt_recursion_avoided':True,'overall_Goal_active':True,'recorded_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 new(PENDING/'ARCHIVE_PHASE8_RECEIPT.json',receipt);print('PH8_REMOTE_VERIFIED_RECEIPT',json.dumps(receipt,ensure_ascii=False,indent=2),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  PENDING.mkdir(parents=True,exist_ok=True);n=1
  while(PENDING/f'ARCHIVE_PHASE8_OPERATION_FAILURE_{n:03d}.txt').exists():n+=1
  (PENDING/f'ARCHIVE_PHASE8_OPERATION_FAILURE_{n:03d}.txt').write_text(traceback.format_exc()+'\nFormal PH9pending operation failure. Inspect existing record/commit/tag first; never replay successful recorder or recreate tag. Push failure continues same existing objects only.\n',encoding='utf-8');raise
