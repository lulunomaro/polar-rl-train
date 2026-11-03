"""ONE approved PH10 record and explicit ownrefs push; no original raw/source or robotics execution."""
from pathlib import Path
import ast,datetime,hashlib,importlib.util,io,json,os,re,subprocess,sys,traceback
WT=Path(r'F:\RMPOLAR-RL\repo-lqr-robust');C=WT/'history/experiments/mod4v1_robust_traditional_phase10';P=WT/'history/experiments/mod4v1_robust_traditional_phase10_SOURCE_PREPARATION';PENDING=WT/'history/experiments/mod4v1_robust_traditional_phase11_PENDING'
OWN=C.relative_to(WT).as_posix();SOURCE=P.relative_to(WT).as_posix();BRANCH='mod4v1-lqr-mpc-robust';BASE='7b7d2633a25dad356809a56ddfa2d546f1cded10';IDENT='mod4v1-robust-traditional-phase10';DATE='20261104';TAG='trial-'+DATE+'-'+IDENT;RECORD='history/experiments/'+DATE+'-'+IDENT+'.json'
HELPER_SHA='b2fd15dee16735721e18ed88b55e9e3159344f1d6f8095217f2db84852c2cd3e';SEAL_SHA='d8c45a30c8b31e2b9cef8f8d0fe09bb58d8f340ef56b8751626a0ec1cdccd0bb';INITIAL_MAIN='f483c4ef9a26e6cae07b0d823917c345bcfc91d9'
COPIES={'review_ph10_parent_snapshot_v1.py':'a197f19d5fb21e8022452a2968dc6559e8dc087dc83ef7830bc80a56a46d6a8a','PH10_PARENT_SNAPSHOT_REVIEW_V1.json':'285fb1eedcd9bfb433812dda2ff652c2c740d79fc1ce5e6969d8b19af0b3c793','ARCHIVE_PHASE10_PARENT_RECORD_AUTHORIZATION.json':'cec9ad1b6f1a933ec7ef32821782e7f1d6b8958bc030fef7254a057cd0a8ea09'}
# Read only the previously archived constant literal; never import or execute an old adapter.
old_ast=ast.parse((WT/'history/experiments/mod4v1_robust_traditional_phase9/record_phase9_adapter.py').read_text(encoding='utf-8'))
OLD_TAGS=ast.literal_eval(next(n.value for n in old_ast.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='OLD_TAGS'for t in n.targets)))
assert len(OLD_TAGS)==8
OLD_TAGS['trial-20261103-mod4v1-robust-traditional-phase9']=('47e9af16274fbf83ebc662c4134414968c2a6600',BASE)
os.environ['GIT_OPTIONAL_LOCKS']='0'
def sha(b):return hashlib.sha256(b).hexdigest()
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
 for t,(o,p)in OLD_TAGS.items():assert r.get('refs/tags/'+t)==o and r.get('refs/tags/'+t+'^{}')==p,('Prior tag changed',t)
def frozen():
 assert sha((P/'REVIEW_INDEX.json').read_bytes())==SEAL_SHA,'Reviewed INDEX changed'
 for n,h in COPIES.items():assert sha((C/n).read_bytes())==h,('Parent copy changed',n)
 a=load(C/'ARCHIVE_PHASE10_PARENT_RECORD_AUTHORIZATION.json');num=load(C/'PH10_PARENT_SNAPSHOT_REVIEW_V1.json')
 assert a['status']=='PARENT_APPROVES_ONE_ORIGINAL_HELPER_RECORD_AND_OWN_REFS_ONLY_AFTER_SOURCE_SNAPSHOT_REVIEW'
 assert a['expected_parent']==BASE and a['trial_label']==IDENT and a['new_annotated_tag']==TAG and a['branch']==BRANCH and Path(a['repo'])==WT
 assert num['status']=='PASS_PARENT_INDEPENDENT_SNAPSHOT_NUMERICS_AND_EXISTING_COPY_RECEIPT_BINDINGS'
 assert(num['controls'],num['controlled_steps'],num['controlled_formal_results'],num['software_error_without_result_backfill'],num['passive_steps_separate'])==(2101,42020,3,1,12000)
 assert num['controlled_full_duration_completions']==num['original_formal_passes']==0 and num['V6_logical_main_compile1_original_gate_false']
 assert num['original_sealed_manifest_and_unknown4_kept_unchanged'] and len(num['additional_existing_library_copy_producer_bindings'])==2
 assert sorted((x['bytes'],x['raw_producer_SHA'])for x in num['additional_existing_library_copy_producer_bindings'])==[(34756,'ace29e114d892a48a473cc3421f0c22d16841c1316313746650b8f441749413a'),(13294064,'ba416f23efb992105c36b67d9002d8142e38877d1010c0e0a1d0f74b83325ab7')]
 assert all(x['current_payload_rehashed']is False and x['current_payload_or_ABI_newly_validated']is False for x in num['additional_existing_library_copy_producer_bindings'])
 idx=load(P/'REVIEW_INDEX.json');source={SOURCE+'/'+e['relative']:e['SHA']for e in idx['files']};source[SOURCE+'/REVIEW_INDEX.json']=SEAL_SHA
 actual={p.relative_to(WT).as_posix()for p in P.rglob('*')if p.is_file()and '__pycache__'not in p.parts};assert actual==set(source),'Frozen SOURCE pathset changed'
 for n,h in {'REVIEW_HANDOFF.md':'b4ee35ba31961b84a6cf0c0f072756ad11389d863121352d96268e87ed5cf952','FINAL_CONSISTENCY_RECEIPT.json':'a023349fedd157e61d31b894bfe522ad4cc3593391ee925d32f5b9a91b6d2555','CASE_RECONCILIATION.json':'793d8b34bf66018205427c3b631c8ca3ea5380df2041dc765ff454106ab53f7c'}.items():assert sha((P/n).read_bytes())==h,n
 cons=load(P/'FINAL_CONSISTENCY_RECEIPT.json');s=cons['summary'];assert cons['record_stage_commit_tag_push_calls']==0 and cons['authority_SHA']=='e09f31aa7a53997dd9733f1894e3c9ec85d099052050d08662e89821bbc2e2ab'
 assert s==num['PH10_entry_summary'] and(s['source_entries'],s['new_text_copies'],s['prior_Git_text_references'],s['raw_metadata_only'],s['raw_existing_producerSHA_known'],s['current_raw_unknowns'])==(3048,1603,1022,423,419,4)
 assert s['current_missing_saved_smalltext_unique']==1 and s['controlled_actual_controls']==2101 and s['controlled_actual_steps']==42020 and s['passive_actual_steps']==12000
 for name in source:
  low=name.lower();assert not any(x in low for x in('startup_support_geometry_v1','mod4_deployment_abi_scope_static_v7','takeoff_momentum_capture_method_v1'))
  assert not any(int(x)>=4 for x in re.findall(r'startup_stand_v(\d+)',low))
  assert not any(int(x)>=7 for x in re.findall(r'mod4_deployment_target_compile_v(\d+)',low))
 prev=[e for e in idx['files']if Path(e['relative']).name=='ARCHIVE_PHASE9_RECEIPT.json'];assert len(prev)==1
 assert load(P/prev[0]['relative'])['commit']==BASE,'Captured PH9 receipt mismatch'
 return idx,source,a,num,cons,prev[0]
def main():
 assert datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y%m%d')==DATE,'Actual date only; never backdate'
 guard();assert text('rev-parse','HEAD')==BASE and not text('diff','--cached','--name-only')and not text('diff','--name-only'),'Owned HEAD or foreign changes; never reset'
 helper=WT/'archive_tools/record_experiment.py';assert sha(helper.read_bytes())==HELPER_SHA
 assert not(WT/RECORD).exists()and not text('tag','--list',TAG)and not(PENDING/'ARCHIVE_PHASE10_RECEIPT.json').exists(),'Existing objects: inspect, never replay recorder'
 idx,source_sha,a,num,cons,previous=frozen();pre=refs();oldrefs(pre);assert pre.get('refs/heads/'+BRANCH)==BASE and 'refs/tags/'+TAG not in pre,'Remote branch/tag changed'
 new(C/'PARENT_AUTHORITY_AND_FREEZE.json',dict(status='ONE_PHASE10_ARCHIVE_AFTER_PARENT_REVIEW',parent=BASE,branch=BRANCH,id=IDENT,tag=TAG,helper_SHA=HELPER_SHA,review_index_SHA=SEAL_SHA,parent_copies_SHA=COPIES,remote_pre_record=pre,allowed_roots=[OWN,SOURCE],new_record=RECORD,source_immutable_no_recapture=True,historical_collector_known_unknown=[419,4],two_library_copy_claims_supplemental_not_payload_hash=True,overall_Goal_active=True))
 plan=OWN+'/STAGING_PLAN.json';cover=sorted({p.relative_to(WT).as_posix()for p in C.rglob('*')if p.is_file()and '__pycache__'not in p.parts}|{plan});selected=sorted(set(source_sha)|set(cover));expected=set(selected)|{RECORD}
 assert set(cover)=={OWN+'/'+n for n in('NOTE.md','record_phase10_adapter.py',*COPIES,'PARENT_AUTHORITY_AND_FREEZE.json','STAGING_PLAN.json')},'Unexpected cover file'
 for n in selected:
  f=WT/n;assert n.startswith((OWN+'/',SOURCE+'/'))and not f.is_symlink()
  assert f.suffix.lower()not in{'.exe','.dll','.o','.obj','.a','.lib','.bin','.pt','.pth','.onnx','.npz','.npy','.pem','.key','.usd','.usdc','.usda','.stl','.stp','.step','.zip','.7z','.jsonl','.pdf','.png','.jpg','.jpeg','.mp4'},n
 new(WT/plan,dict(status='EXACT_PHASE10_ADDITIONS_PREREGISTERED_BEFORE_RECORDER',allowed_roots=[OWN,SOURCE],selected_paths=selected,new_record=RECORD,expected_staged_count=len(expected),source_SHA_from_reviewed_INDEX=source_sha,cover_SHA_except_plan_self={n:sha((WT/n).read_bytes())for n in cover if n!=plan},every_path_identity='source INDEX or new explicit cover, record generated by original helper',prior_postreceipt_only_frozen_source=previous,checks=['exactPaths','allA','noD','noForeign','everyStagedBlobSHA','recordMap','committedParentAllPathsAllBlobs','annotatedTag','atomicOwnRefs'],phase11_postreceipt_not_in_commit=True))
 hashes={**source_sha,**{n:sha((WT/n).read_bytes())for n in cover}}
 # Verify only the owned frozen archive payload before invoking the recorder; never reopen original sources/raw/assets.
 for n,h in hashes.items():assert sha((WT/n).read_bytes())==h,('Pre-helper frozen payload mismatch',n)
 print('PH10_PREHELPER_EXACT_PAYLOAD_VERIFIED',json.dumps(dict(source_files=len(source_sha),cover_files=len(cover),expected_paths=len(expected),original_raw_or_sourceRoot_read=False)),flush=True)
 sys.path.insert(0,str(WT/'archive_tools'));from capture_history import redact
 spec=importlib.util.spec_from_file_location('unchanged_original_ph10_recorder',helper);rec=importlib.util.module_from_spec(spec);spec.loader.exec_module(rec);assert rec.ROOT==WT;original=rec.git;checked_commit=[None];staged=[]
 def blob_gate(objects,hs,label):
  assert set(objects)==expected and set(hs)==expected,(label,'exact blob paths')
  names=sorted(objects);buf=io.BytesIO(cmd('cat-file','--batch',input=('\n'.join(objects[n]for n in names)+'\n').encode('ascii')).stdout)
  for n in names:
   header=buf.readline().decode('ascii').strip().split();assert len(header)==3 and header[1]=='blob',(label,n,header)
   size=int(header[2]);raw=buf.read(size);assert len(raw)==size and buf.read(1)==b'\n'and sha(raw)==hs[n],(label,'blob mismatch',n)
  assert not buf.read(),label
 def check():
  guard();assert set(paths('diff','--cached','--name-only','-z'))==expected,'Staged paths mismatch'
  ns=paths('diff','--cached','--name-status','-z');assert len(ns)==2*len(expected)and all(ns[i]=='A'for i in range(0,len(ns),2)),'Not all additions/noD'
  record=load(WT/RECORD);assert record['id']==DATE+'-'+IDENT and record['tag']==TAG and record['kind']=='diagnostic'and record['source_and_evidence_sha256']==hashes,'Record hash map mismatch'
  objects={}
  for line in paths('ls-files','--stage','-z','--',OWN,SOURCE,RECORD):
   row,n=line.split('\t',1);mode,oid,stage=row.split();assert stage=='0'and mode in('100644','100755');objects[n]=oid
  blob_gate(objects,{**hashes,RECORD:sha((WT/RECORD).read_bytes())},'staged');frozen();g=dict(count=len(expected),exact_paths=True,all_A=True,no_D_no_foreign=True,every_blob_SHA_exact=True,record_source_map_exact=True,review_index_unchanged=SEAL_SHA);staged.append(g);print('PH10_STAGED_EXACT_VERIFIED',json.dumps(g),flush=True)
 def committed():
  guard();commit=text('rev-parse','HEAD');assert text('rev-parse','HEAD^')==BASE
  assert set(paths('diff-tree','--no-commit-id','--name-only','-r','-z','HEAD'))==expected,'Committed path mismatch'
  statuses=paths('diff-tree','--no-commit-id','--name-status','-r','-z','HEAD');assert len(statuses)==2*len(expected)and all(statuses[i]=='A'for i in range(0,len(statuses),2))
  objects={}
  for line in paths('ls-tree','-r','-z','HEAD','--',OWN,SOURCE,RECORD):
   row,n=line.split('\t',1);mode,typ,oid=row.split();assert typ=='blob'and mode in('100644','100755');objects[n]=oid
  blob_gate(objects,{**hashes,RECORD:sha((WT/RECORD).read_bytes())},'committed-tree');checked_commit[0]=commit;print('PH10_COMMITTED_TREE_EXACT_VERIFIED',json.dumps(dict(commit=commit,parent=BASE,count=len(expected),every_tree_blob_SHA=True)),flush=True)
 def narrow(*args):
  if args and args[0]=='add':
   assert args[1]=='--'and args[2]==RECORD and set(args[3:])==set(selected)
   record=load(WT/RECORD);assert record['source_and_evidence_sha256']==hashes and record['tag']==TAG and record['id']==DATE+'-'+IDENT,'Pre-add original record map mismatch'
   original('add','--force','--sparse','--',OWN,SOURCE,RECORD);check();return''
  if args and args[0]=='commit':check()
  if args and args[0]=='push':raise AssertionError('No original helper implicit/global push')
  if args[:2]==('tag','-a'):assert args[2]==TAG;committed()
  return original(*args)
 rec.git=narrow;sys.argv=[str(helper),'--id',IDENT,'--title','Archive reviewed MOD4v1 startup V3B and deployment target V6 phase10','--kind','diagnostic','--note-file',str(C/'NOTE.md'),'--validation','Four controlled failed-prefix attempts 2101 controls 42020 prior steps and three passive12000 separate; one main TU three variants/no fulltarget; original failures/encoding/gaps preserved; staged and tree blobs exact; no robot rerun.','--files',*selected];rec.main()
 guard();commit=text('rev-parse','HEAD');tag_obj=text('rev-parse',TAG);assert checked_commit[0]==commit and text('cat-file','-t',TAG)=='tag'and text('rev-parse',TAG+'^{}')==commit
 assert not text('diff','--cached','--name-only')and not text('diff','--name-only');frozen();assert sha(helper.read_bytes())==HELPER_SHA
 prepush=refs();oldrefs(prepush);assert prepush.get('refs/heads/'+BRANCH)==BASE and 'refs/tags/'+TAG not in prepush,'Remote moved: no overwrite'
 push=cmd('push','--atomic','origin','HEAD:refs/heads/'+BRANCH,'refs/tags/'+TAG+':refs/tags/'+TAG)
 post=refs();oldrefs(post);assert post.get('refs/heads/'+BRANCH)==commit and post.get('refs/tags/'+TAG)==tag_obj and post.get('refs/tags/'+TAG+'^{}')==commit,'Remote verification failed'
 frozen();assert sha(helper.read_bytes())==HELPER_SHA and not text('diff','--cached','--name-only')and not text('diff','--name-only')
 stdout,n1=redact(push.stdout.decode('utf-8','replace'));stderr,n2=redact(push.stderr.decode('utf-8','replace'))
 receipt=dict(status='PH10_ONE_ORIGINAL_HELPER_RECORD_COMMIT_ANNOTATEDTAG_ATOMIC_OWNREFS_REMOTE_VERIFIED',recorded_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),commit=commit,parent=BASE,branch=BRANCH,tag=TAG,tag_object=tag_obj,peeled_commit=text('rev-parse',TAG+'^{}'),record=RECORD,source_payload_files=len(source_sha),cover_files=len(cover),selected_files_excluding_record=len(selected),total_staged_committed_paths=len(expected),double_staged_gates=staged,committed_parent_path_status_and_every_blob_gate=True,helper_unmodified_SHA=HELPER_SHA,review_index_unchanged_SHA=SEAL_SHA,parent_cover_copies_SHA=COPIES,source_preparation_historical_summary=cons['summary'],parent_library_claims_supplemental_not_current_verification=num['additional_existing_library_copy_producer_bindings'],original_collector419_known4_unknown_retained=True,disclosed_gaps='One saved historical FSM text version missing; two executables conflicting/current SHA unknown; raw/readable encoding independent; two old library copy claims supplemental only; no reconstruction/payloadhash/ABI upgrade',prior_PH9postreceipt_in_frozen_source=previous,remote_pre_record=pre,remote_immediate_pre_push=prepush,remote_post_push=post,initial_main_probe=INITIAL_MAIN,main_same_only_adjacent_push_window=prepush.get('refs/heads/main')==post.get('refs/heads/main'),whole_archive_main_unchanged_NOT_claimed=True,PH1_to_PH9_tag_objects_and_peels_unchanged=True,push_stdout_redacted=stdout,push_stderr_redacted=stderr,push_log_redactions=n1+n2,owner_status_before_postreceipt=text('status','--short'),old_pending5_to10_untouched_unstaged=True,sourceRoot_model_candidate_oldscore_expertindex_main_otherrefs_mutated=False,archive_worker_new_model_FK_PHY_oldQA_unit_compile_once_GPU_agents_rawhash_realIO_Goal_actions=False,parallel_parent_or_C_work_separate_not_whole_session_zero_claim=True,receipt_git_status='PHASE11_PENDING_POSTCOMMIT_NOT_IN_PHASE10_TREE',receipt_recursion_avoided=True,overall_Goal_active=True)
 new(PENDING/'ARCHIVE_PHASE10_RECEIPT.json',receipt);print('PH10_REMOTE_VERIFIED_RECEIPT',json.dumps(receipt,ensure_ascii=False,indent=2),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException as exc:
  PENDING.mkdir(parents=True,exist_ok=True);n=1
  while(PENDING/f'ARCHIVE_PHASE10_OPERATION_FAILURE_{n:03d}.txt').exists():n+=1
  detail=traceback.format_exc()
  if isinstance(exc,subprocess.CalledProcessError):detail+='\nCAPTURED_STDOUT\n'+(exc.stdout or b'').decode('utf-8','replace')+'\nCAPTURED_STDERR\n'+(exc.stderr or b'').decode('utf-8','replace')
  detail+='\nFormal PH11pending operation report. Inspect existing record/commit/tag; never replay successful record/tag; push failure resumes same existing objects only.\n'
  (PENDING/f'ARCHIVE_PHASE10_OPERATION_FAILURE_{n:03d}.txt').write_text(detail,encoding='utf-8');(PENDING/f'ARCHIVE_PHASE10_OPERATION_FAILURE_SOURCE_{n:03d}.py').write_bytes(Path(__file__).read_bytes());raise
