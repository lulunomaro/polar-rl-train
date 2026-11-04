"""Once-authorized finite PH11 captured-source archive. No source capture, binary assets or robotics execution."""
from pathlib import Path
import os,sys,json,hashlib,datetime,subprocess,importlib.util,traceback
WT=Path(r'F:\RMPOLAR-RL\repo-lqr-robust');OWN='history/experiments/mod4v1_robust_traditional_phase11';SOURCE=OWN+'_SOURCE_PREPARATION';C=WT/OWN;P=WT/SOURCE
PENDING=WT/'history/experiments/mod4v1_robust_traditional_phase12_PENDING';RECORD='history/experiments/20261104-mod4v1-robust-traditional-phase11.json'
BASE='e176d2a6401fafb9d618a042acba8190023c3273';BRANCH='mod4v1-lqr-mpc-robust';IDENT='mod4v1-robust-traditional-phase11';DATE='20261104';TAG='trial-'+DATE+'-'+IDENT
AUTH_SHA='d3784cc6dada8fc4f41234c986010a84769ecbefd34314c4c77bfcdba08689b2';HELPER_SHA='b2fd15dee16735721e18ed88b55e9e3159344f1d6f8095217f2db84852c2cd3e'
INITIAL_MAIN='b77112990fbcd1869f79031b170556f5ca39e5b7';os.environ['GIT_OPTIONAL_LOCKS']='0'
def sha(b):return hashlib.sha256(b).hexdigest()
def load(p):return json.loads(p.read_bytes())
def new(p,v):
 assert not p.exists(),str(p);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf-8',newline='\n')as f:json.dump(v,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
def cmd(*a,input=None):return subprocess.run(['git','-C',str(WT),*a],input=input,capture_output=True,check=True)
def text(*a):return cmd(*a).stdout.decode('utf-8').strip()
def paths(*a):return[x.decode('utf-8')for x in cmd(*a).stdout.split(b'\0')if x]
def guard():
 assert text('rev-parse','--show-toplevel').replace('\\','/').lower()=='f:/rmpolar-rl/repo-lqr-robust'
 assert text('symbolic-ref','--short','HEAD')==BRANCH
 assert text('rev-parse','--git-path','index').replace('\\','/').lower().endswith('/.git/worktrees/repo-lqr-robust/index')
 assert text('remote','get-url','origin')in('https://github.com/lulunomaro/polar-rl-train.git','https://github.com/lulunomaro/polar-rl-train')
def hook_isolation():
 d=C/'empty_hooks_DISABLED_FOR_THIS_OPERATION';assert not d.exists();d.mkdir();assert not list(d.iterdir())
 n=int(os.environ.get('GIT_CONFIG_COUNT','0'));os.environ['GIT_CONFIG_COUNT']=str(n+1);os.environ['GIT_CONFIG_KEY_'+str(n)]='core.hooksPath';os.environ['GIT_CONFIG_VALUE_'+str(n)]=str(d)
 assert text('config','--get','core.hooksPath')==str(d)
 return dict(mode='process-local appended core.hooksPath; no global/config file or hooks executed',path=str(d))
def main():
 assert datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y%m%d')==DATE,'Actual date only; no backdating'
 guard();assert text('rev-parse','HEAD')==BASE and not paths('diff','--cached','--name-only','-z')and not text('diff','--name-only'),'Own branch/index/tracked state changed; no reset'
 assert not(WT/RECORD).exists()and not text('tag','--list',TAG)and not(PENDING/'ARCHIVE_PHASE11_RECEIPT.json').exists(),'Existing record/tag/receipt: inspect, never replay'
 helper=WT/'archive_tools/record_experiment.py';assert sha(helper.read_bytes())==HELPER_SHA
 auth_path=C/'ARCHIVE_PHASE11_PARENT_RECORD_AUTHORIZATION.json';assert sha(auth_path.read_bytes())==AUTH_SHA;a=load(auth_path)
 assert a['approved']is True and a['kind']=='FINITE_PH11_RECORD_ONLY_CAPTURED_CLOSED_V4_V5_GEOMETRY_C7_C17_NOT_GOAL_COMPLETION'and a['expected_parent']==BASE and a['branch']==BRANCH and a['identity']==IDENT and a['tag']==TAG and a['original_helper_rec_main_calls']==1
 copied={auth_path.name:AUTH_SHA}
 for e in a['extra_operation_cover']:
  p=C/Path(e['path']).name;assert p.stat().st_size==e['bytes']and sha(p.read_bytes())==e['SHA'];copied[p.name]=e['SHA']
 assert len(copied)==12
 review=load(C/'PH11_PARENT_INDEX_REVIEW_V2.json');assert sha((C/'PH11_PARENT_INDEX_REVIEW_V2.json').read_bytes())==a['parent_index_review']['SHA']
 assert review['status']=='PASS_PARENT_CAPTURED_TEXT_INDEX_IDENTITIES_AND_FINITE_ALLOWLIST_NOT_FRESH_LIVE_SOURCE'and review['parent']==BASE and review['branch']==BRANCH
 sourcehash={e['relative']:e['SHA']for e in load(P/'REVIEW_INDEX.json')['files']}
 sourcehash.update({SOURCE+'/INDEX.json':a['source_INDEX_SHA'],SOURCE+'/REVIEW_INDEX.json':a['source_REVIEW_INDEX_SHA'],SOURCE+'/RECEIPT.json':a['source_RECEIPT_SHA']})
 allowed=set(review['allowed_sourceprep_relative_paths']);assert len(sourcehash)==len(allowed)==856 and set(sourcehash)==allowed
 ledger=SOURCE+'/GIT_READONLY_LEDGER.jsonl';assert[x for x in allowed if x.endswith('.jsonl')]==[ledger]and len((WT/ledger).read_bytes().splitlines())==18
 actual={x.relative_to(WT).as_posix()for x in P.rglob('*')if x.is_file()};assert actual==allowed,'SOURCE pathset changed; no recapture'
 for p,h in sourcehash.items():assert p.startswith(SOURCE+'/')and not(WT/p).is_symlink()and sha((WT/p).read_bytes())==h,('Captured payload changed',p)
 receipt=load(P/'RECEIPT.json');case=load(P/'CASE_RECONCILIATION.json')
 assert (review['cases'],review['controls'],review['physics_steps'],review['formalFalse'],review['complete10s'],review['old_gate_true'])==(2,381,7620,2,0,0)
 assert review['original_full_live_source_after']=='UNKNOWN_NOT_REACHED_NOT_REFRESHED'
 extra=a['only_previous_postreceipt'];assert extra=='history/experiments/mod4v1_robust_traditional_phase11_PENDING/ARCHIVE_PHASE10_RECEIPT.json'
 snapshot=SOURCE+'/snapshot/@repo/'+extra;assert snapshot in sourcehash and sha((WT/extra).read_bytes())==sourcehash[snapshot]
 previous=load(WT/extra);tag10='refs/tags/trial-20261104-mod4v1-robust-traditional-phase10'
 def maps(v):
  if isinstance(v,dict):
   if v.get(tag10)=='38e3bd31b6d54cf3f05ea78cd936256ec299cdcb'and v.get(tag10+'^{}')==BASE:yield v
   for z in v.values():yield from maps(z)
  elif isinstance(v,list):
   for z in v:yield from maps(z)
 oldmap=next(maps(previous));old={k:v for k,v in oldmap.items()if k.startswith('refs/tags/')};assert len(old)==20 and all(len(v)==40 for v in old.values())
 expected_tags={('refs/tags/trial-'+('20261102'if n<=4 else'20261103'if n<=9 else'20261104')+'-mod4v1-robust-traditional-phase'+str(n))+s for n in range(1,11)for s in('','^{}')};assert set(old)==expected_tags
 def refs():return{p[1]:p[0]for p in(x.split()for x in text('ls-remote','origin','refs/heads/main','refs/heads/'+BRANCH,'refs/tags/'+TAG,'refs/tags/'+TAG+'^{}',*sorted(old)).splitlines())}
 def oldrefs(v):assert all(v.get(k)==h for k,h in old.items()),'Prior annotated tag changed; stop'
 def frozen_small():
  for name,h in copied.items():assert sha((C/name).read_bytes())==h
  assert sha(helper.read_bytes())==HELPER_SHA
  for name,key in(('INDEX.json','source_INDEX_SHA'),('REVIEW_INDEX.json','source_REVIEW_INDEX_SHA'),('RECEIPT.json','source_RECEIPT_SHA')):assert sha((P/name).read_bytes())==a[key]
  assert {x.relative_to(WT).as_posix()for x in P.rglob('*')if x.is_file()}==allowed
 r0=refs();oldrefs(r0);assert r0.get('refs/heads/'+BRANCH)==BASE and'refs/tags/'+TAG not in r0,'Remote moved or PH11 exists; stop'
 hooks=hook_isolation()
 new(C/'PARENT_AUTHORITY_AND_FREEZE.json',dict(status='ONE_PARENT_AUTHORIZED_CAPTURED_VERSION_ONLY_ORIGINAL_LIVE_AFTER_UNKNOWN',parent=BASE,authority_SHA=AUTH_SHA,parent_copies=copied,source_paths=856,sourcehash=sourcehash,exact_previous_postreceipt=dict(path=extra,SHA=sourcehash[snapshot],saved_snapshot=snapshot),old_tags_expected=old,remote_pre_record=r0,initial_main_probe=INITIAL_MAIN,helper_SHA=HELPER_SHA,hooks=hooks,no_active_source_or_new_robotics_reads=True,old_failures_unknowns_and_qualification_unchanged=True,record=RECORD,overall_Goal_active=True))
 plan=OWN+'/STAGING_PLAN.json';cover=sorted({x.relative_to(WT).as_posix()for x in C.rglob('*')if x.is_file()}|{plan});assert not(WT/plan).exists()
 selected=sorted(allowed|set(cover)|{extra});expected=set(selected)|{RECORD};assert len(cover)==16
 for p in selected:
  q=WT/p;assert q.is_relative_to(WT)and not q.is_symlink()
  assert q.suffix.lower()not in('.exe','.dll','.o','.obj','.lib','.a','.axf','.bin','.pt','.pth','.onnx','.npz','.npy','.pem','.key','.usd','.usda','.usdc','.stl','.stp','.step','.zip','.7z')
  if q.suffix.lower()=='.jsonl':assert p==ledger
  assert p.startswith(SOURCE+'/')or p.startswith(OWN+'/')or p==extra
 new(WT/plan,dict(status='FINITE_PATH_AND_FROZEN_HASH_PREREGISTRATION_NOT_WHOLE_HISTORY_OR_PENDING',selected=selected,new_record=RECORD,total_staged_count=len(expected),source_paths=sorted(allowed),source_expected_SHA=sourcehash,cover_hash_except_plan={p:sha((WT/p).read_bytes())for p in cover if p!=plan},exact_previous_postreceipt=extra,own_ledger_only_jsonl=dict(path=ledger,SHA=sourcehash[ledger],lines=18),add_method='Literal NUL pathspec via stdin, avoids Windows argv limit; no broad directory staging',postreceipt_excluded=a['postreceipt_outside_own_commit'],original_live_source_after='UNKNOWN_NOT_REACHED_NOT_REFRESHED'))
 hashes={**sourcehash,**{p:sha((WT/p).read_bytes())for p in cover},extra:sourcehash[snapshot]};assert set(hashes)==set(selected)
 for p,h in hashes.items():assert sha((WT/p).read_bytes())==h,('Pre-helper actual owned byte mismatch',p)
 print('PH11_PREHELPER_EXACT_PAYLOAD_VERIFIED',json.dumps(dict(source_files=len(allowed),cover_files=len(cover),exact_previous_postreceipt=1,selected_without_record=len(selected),total_staged=len(expected),original_live_source_after='UNKNOWN_NOT_REACHED_NOT_REFRESHED')),flush=True)
 sys.path.insert(0,str(WT/'archive_tools'));from capture_history import redact
 spec=importlib.util.spec_from_file_location('original_ph11_recorder',helper);rec=importlib.util.module_from_spec(spec);spec.loader.exec_module(rec);assert rec.ROOT==WT;original=rec.git;validations=[]
 def blob_gate(objects,hs,label):
  out=cmd('cat-file','--batch',input=('\n'.join(o for p,o in objects)+'\n').encode()).stdout;i=0
  for p,oid in objects:
   j=out.index(b'\n',i);head=out[i:j].split();assert head[0].decode()==oid and head[1]==b'blob';n=int(head[2]);b=out[j+1:j+1+n];assert len(b)==n and out[j+1+n:j+2+n]==b'\n'and sha(b)==hs[p],(label,p);i=j+2+n
  assert i==len(out)
 def check():
  guard();assert text('rev-parse','HEAD')==BASE;assert set(paths('diff','--cached','--name-only','-z'))==expected,'Foreign/missing staged path'
  ns=paths('diff','--cached','--name-status','-z');assert len(ns)==2*len(expected)and all(ns[i]=='A'for i in range(0,len(ns),2)),'Not allA'
  z=load(WT/RECORD);assert z['id']==DATE+'-'+IDENT and z['tag']==TAG and z['kind']=='diagnostic'and z['source_and_evidence_sha256']==hashes,'Original record map differs'
  objects=[]
  for row in paths('ls-files','--stage','-z','--',OWN,SOURCE,extra,RECORD):
   h,p=row.split('\t',1);mode,oid,stage=h.split();assert mode in('100644','100755')and stage=='0';objects.append((p,oid))
  assert {p for p,o in objects}==expected;hs={**hashes,RECORD:sha((WT/RECORD).read_bytes())};blob_gate(objects,hs,'Staged everyblob');frozen_small()
  v=dict(paths=len(expected),exact_paths=True,ALL_A=True,no_D_noForeign=True,every_blob_SHA_matches_preregistered=True,record_map_exact=True,source_REVIEW_INDEX_unchanged=a['source_REVIEW_INDEX_SHA']);validations.append(v);print('PH11_STAGED_EXACT_VERIFIED',json.dumps(v),flush=True)
 def committed():
  assert text('rev-parse','HEAD^')==BASE and set(paths('diff-tree','--no-commit-id','--name-only','-r','-z','HEAD'))==expected
  ns=paths('diff-tree','--no-commit-id','--name-status','-r','-z','HEAD');assert len(ns)==2*len(expected)and all(ns[i]=='A'for i in range(0,len(ns),2))
  objects=[]
  for row in paths('ls-tree','-r','-z','HEAD','--',OWN,SOURCE,extra,RECORD):
   h,p=row.split('\t',1);mode,kind,oid=h.split();assert mode in('100644','100755')and kind=='blob';objects.append((p,oid))
  assert {p for p,o in objects}==expected;blob_gate(objects,{**hashes,RECORD:sha((WT/RECORD).read_bytes())},'Committed everyblob')
  print('PH11_COMMITTED_TREE_EXACT_VERIFIED',len(objects),flush=True)
 def narrow(*args):
  if args and args[0]=='add':
   assert args[1]=='--'and args[2]==RECORD and set(args[3:])==set(selected)
   z=load(WT/RECORD);assert z['source_and_evidence_sha256']==hashes
   cmd('add','--force','--sparse','--pathspec-from-file=-','--pathspec-file-nul',input=b'\0'.join((':(literal)'+p).encode('utf-8')for p in sorted(expected))+b'\0');check();return''
  if args and args[0]=='commit':check()
  if args and args[0]=='push':raise AssertionError('No helper implicit/global push')
  if args[:2]==('tag','-a'):assert args[2]==TAG;committed()
  return original(*args)
 rec.git=narrow;sys.argv=[str(helper),'--id',IDENT,'--title','Archive parent-reviewed finite PH11 captured startup failures and oldBSP link evidence','--kind','diagnostic','--note-file',str(C/'NOTE.md'),'--validation','Finite immutable captured snapshot; source-after UNKNOWN; V4/V5 failed381/7620; oldBSP diagnostic link not hardware; exact additions and everyblob verified.','--files',*selected];rec.main()
 commit=text('rev-parse','HEAD');tagobj=text('rev-parse','refs/tags/'+TAG);assert text('cat-file','-t','refs/tags/'+TAG)=='tag'and text('rev-parse','refs/tags/'+TAG+'^{}')==commit and text('rev-parse','HEAD^')==BASE
 assert len(validations)==2 and not text('diff','--cached','--name-only')and not text('diff','--name-only');frozen_small();guard()
 pre=refs();oldrefs(pre);assert pre.get('refs/heads/'+BRANCH)==BASE and'refs/tags/'+TAG not in pre,'Remote moved; stop, never overwrite'
 push=cmd('push','--atomic','origin','HEAD:refs/heads/'+BRANCH,'refs/tags/'+TAG+':refs/tags/'+TAG)
 post=refs();oldrefs(post);assert post.get('refs/heads/'+BRANCH)==commit and post.get('refs/tags/'+TAG)==tagobj and post.get('refs/tags/'+TAG+'^{}')==commit
 frozen_small();assert not text('diff','--cached','--name-only')and not text('diff','--name-only');owner_status=text('status','--short');logs,count=redact(push.stdout.decode('utf-8',errors='replace')+'\n'+push.stderr.decode('utf-8',errors='replace'))
 result=dict(status='PH11_ONE_ORIGINAL_HELPER_RECORD_COMMIT_ANNOTATEDTAG_ATOMIC_OWNREFS_REMOTE_VERIFIED',recorded_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),commit=commit,parent=BASE,branch=BRANCH,tag=TAG,tag_object=tagobj,peeled_commit=commit,record=RECORD,source_payload_files=856,cover_files=len(cover),exact_prior_postreceipt_files=1,total_staged_committed_files=len(expected),dual_staged_gates=validations,committed_parent_pathset_ALLA_and_every_blob_SHA_verified=True,original_helper_SHA=HELPER_SHA,original_helper_calls=1,source_INDEX_SHA=a['source_INDEX_SHA'],source_REVIEW_INDEX_SHA=a['source_REVIEW_INDEX_SHA'],source_RECEIPT_SHA=a['source_RECEIPT_SHA'],parent_copy_hashes=copied,original_full_live_source_after='UNKNOWN_NOT_REACHED_NOT_REFRESHED',captured_text_files=798,captured_text_bytes=17739938,prior_refs_declared=240,raw_metadata_paths_declared=582,closed_case_controls381_physics7620_bothFalse=True,original_gates_failures_unknowns_no_startup_or_hardware_graduation=True,remote_pre_record=r0,remote_immediate_before_push=pre,remote_after_push=post,initial_main_probe=INITIAL_MAIN,main_same_only_adjacent_push_window=pre.get('refs/heads/main')==post.get('refs/heads/main'),whole_archive_main_unchanged_NOT_claimed=True,prior_PH1_to_PH10_tag_objects_and_peels_unchanged=True,push_log=logs,push_log_redactions=count,hooks_isolated_process_only=hooks,source_or_model_or_oldscore_or_expertindex_main_foreignrefs_mutated=False,new_capture_model_FK_PHY_oldQA_ARM_rawpayloadhash_Gitforeign_agents_Mnemon_Goal_calls=0,worker_only_no_new_execution_claim_not_parallel_session_claim=True,owner_status_before_postreceipt=owner_status,exact_postreceipt_path=a['postreceipt_outside_own_commit'],receipt_git_status='PHASE12_PENDING_POSTCOMMIT_NOT_IN_PHASE11_TREE',no_recursive_receipt_trial=True,overall_Goal_active=True)
 new(WT/a['postreceipt_outside_own_commit'],result);print('PH11_REMOTE_VERIFIED',json.dumps(dict(commit=commit,tag=TAG,tag_object=tagobj,peeled=commit,files=len(expected),receipt=str(WT/a['postreceipt_outside_own_commit']),main_pre=pre.get('refs/heads/main'),main_post=post.get('refs/heads/main'),owner_status_before_postreceipt=owner_status)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException as ex:
  PENDING.mkdir(parents=True,exist_ok=True);i=1
  while(PENDING/f'ARCHIVE_PHASE11_OPERATION_FAILURE_{i:03d}.txt').exists():i+=1
  detail=traceback.format_exc()
  if isinstance(ex,subprocess.CalledProcessError):detail+='\nstdout:\n'+(ex.stdout or b'').decode('utf-8',errors='replace')+'\nstderr:\n'+(ex.stderr or b'').decode('utf-8',errors='replace')
  try:
   sys.path.insert(0,str(WT/'archive_tools'));from capture_history import redact
   detail,_=redact(detail)
  except Exception:detail=traceback.format_exc()+'\nOriginal operation failed; unredacted process output not persisted.'
  detail+='\nFirst real error STOP. Formal PH12pending. Inspect existing record/commit/tag before any further action; never rerun successful helper/tag. No reset/force/replay.\n'
  with(PENDING/f'ARCHIVE_PHASE11_OPERATION_FAILURE_{i:03d}.txt').open('x',encoding='utf-8')as f:f.write(detail)
  with(PENDING/f'ARCHIVE_PHASE11_OPERATION_FAILURE_SOURCE_{i:03d}.py').open('xb')as f:f.write(Path(__file__).read_bytes())
  raise
