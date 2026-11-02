"""Exactly one approved original-helper PH5 record; exact own-dir blob guard."""
from pathlib import Path
import datetime,hashlib,importlib.util,io,json,os,re,subprocess,sys,traceback
WT=Path(r'F:\RMPOLAR-RL\repo-lqr-robust');C=WT/'history/experiments/mod4v1_robust_traditional_phase5';P=WT/'history/experiments/mod4v1_robust_traditional_phase5_SOURCE_PREPARATION';PENDING=WT/'history/experiments/mod4v1_robust_traditional_phase6_PENDING'
OWN=C.relative_to(WT).as_posix();SOURCE=P.relative_to(WT).as_posix();BRANCH='mod4v1-lqr-mpc-robust';BASE='db8fd0606e00a450504853181a6b4cdf66869d68';IDENT='mod4v1-robust-traditional-phase5';DATE='20261103';TAG='trial-'+DATE+'-'+IDENT;RECORD='history/experiments/'+DATE+'-'+IDENT+'.json'
HELPER_SHA='b2fd15dee16735721e18ed88b55e9e3159344f1d6f8095217f2db84852c2cd3e';SEAL_SHA='8e886a23edf130db10a6a55cde37b25bd0ad28556bfcdff7e3e3807018a441bb';INITIAL_MAIN='70cf50fd3c2fbb0a19b62e1e672372bdd6c29327'
OLD_TAGS={'trial-20261102-mod4v1-robust-traditional-phase1':('1064f48cc077fdd3eb6c89e554b58f5d82ee5980','93e0814f5d4dc165dda1f85f8ee12bc35be04d2f'),'trial-20261102-mod4v1-robust-traditional-phase2':('4ac41c1403a3daefa52acedbf659ee89120b6046','02b5ff84b905a4e40f207a44b0491aeff2f79b7e'),'trial-20261102-mod4v1-robust-traditional-phase3':('163d331cc4dade7bee2e870c7f2da852edec44ab','fa6838807f4d69d2b8ac52300d74ad40f365d2ed'),'trial-20261102-mod4v1-robust-traditional-phase4':('5aadabd68a83f1e4ef93dd2b18518128c46f87a9',BASE)}
os.environ['GIT_OPTIONAL_LOCKS']='0'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def new(p,x):assert not p.exists(),str(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def cmd(*a,input=None):return subprocess.run(['git','-C',str(WT),*a],input=input,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)
def text(*a):return cmd(*a).stdout.decode('utf-8').strip()
def paths(*a):return[x.decode('utf-8')for x in cmd(*a).stdout.split(b'\0')if x]
def guard():
 assert text('rev-parse','--show-toplevel').lower()=='f:/rmpolar-rl/repo-lqr-robust'and text('symbolic-ref','--short','HEAD')==BRANCH
 assert text('rev-parse','--git-path','index').lower().replace('\\','/').endswith('/.git/worktrees/repo-lqr-robust/index')
 assert text('remote','get-url','origin')in['https://github.com/lulunomaro/polar-rl-train.git','https://github.com/lulunomaro/polar-rl-train']
def refs():
 pats=['refs/heads/main','refs/heads/'+BRANCH,'refs/tags/'+TAG,'refs/tags/'+TAG+'^{}']
 for t in OLD_TAGS:pats+=['refs/tags/'+t,'refs/tags/'+t+'^{}']
 return {x.split('\t')[1]:x.split('\t')[0]for x in text('ls-remote','origin',*pats).splitlines()if x}
def oldrefs(r):
 for t,(obj,commit)in OLD_TAGS.items():assert r.get('refs/tags/'+t)==obj and r.get('refs/tags/'+t+'^{}')==commit

def frozen():
 assert sha((P/'REVIEW_INDEX.json').read_bytes())==SEAL_SHA
 idx=load(P/'REVIEW_INDEX.json');expected={e['relative']:e for e in idx['files']};actual={x.relative_to(P).as_posix()for x in P.rglob('*')if x.is_file()and'__pycache__'not in x.parts};assert actual==set(expected)|{'REVIEW_INDEX.json'}
 for rel,e in expected.items():assert sha((P/rel).read_bytes())==e['SHA'],'Frozen snapshot changed: '+rel
 g=load(P/'FINAL_GAPS_AND_EXCLUSIONS.json');assert g['unique_missing_smalltext_count']==1 and len(g['current_PH5_raw_unknowns'])==2 and len(g['inherited_PH4_gaps']['prior_unknown_raw_entries_not_rehashed_or_repaired'])==15
 assert g['actual_smalltext_version_claims_missing'][0]['expected_SHA']=='eea7bbf33028a3abaf697a3ec76c06fefdf53d68c8f551a6b9593fba157f048d'
 m=load(P/'FINAL_SOURCE_MANIFEST.json')
 for e in m['entries']:
  low=e['path'].lower();assert not any(s in low for s in('pc3_candidate_bundle_v1','manual_first_bar','moving_hop','movinghop'))and not any(int(n)>=48 for n in re.findall(r'(?<![a-z0-9])r(\d{2})(?=[^0-9]|$)',low))
 assert m['summary']['H5_pass40_fail24_complete64'] and m['summary']['physical_result_files']==99 and m['summary']['software_ERROR_files']==1
 return len(actual),m['summary']

def main():
 assert datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y%m%d')==DATE,'Never backdate archive'
 guard();assert text('rev-parse','HEAD')==BASE and not text('diff','--cached','--name-only')and not text('diff','--name-only')
 assert sha((WT/'archive_tools/record_experiment.py').read_bytes())==HELPER_SHA
 count,summary=frozen();pre=refs();oldrefs(pre);assert pre.get('refs/heads/'+BRANCH)==BASE and'refs/tags/'+TAG not in pre and not text('tag','--list',TAG)and not(WT/RECORD).exists(),'Unexpected existing record/ref: stop, do not replay'
 new(C/'PARENT_AUTHORITY_AND_FREEZE.json',{'authority':'Parent read reviewed PH5cutoff/SHA/cases/gaps, approved ONE PH5diagnostic commit+atomicOWNrefs; sourceprep immutable; noPH1-4re-record','owner_branch':BRANCH,'base':BASE,'helper_actual_path':'archive_tools/record_experiment.py','helper_SHA':HELPER_SHA,'review_SHA':SEAL_SHA,'sourceprep_files':count,'allowed_directories':[OWN,SOURCE],'record':RECORD,'tag':TAG,'helper_id_without_date':IDENT,'actual_record_id':DATE+'-'+IDENT,'phase4_receipt':'already source-snapshotted, originalpendingpath NOT separatelystaged','missing_history':'1savedtextSHA gap;2currentrawunknown overlap prior15; not gapfree','initial_main':INITIAL_MAIN,'remote_pre_record':pre,'no_new_candidate_or_scope':True,'postcommit_receipt':str(PENDING/'ARCHIVE_PHASE5_RECEIPT.json')})
 plan=C/'STAGING_PLAN.json';selected=sorted([x.relative_to(WT).as_posix()for d in(C,P)for x in d.rglob('*')if x.is_file()and not x.is_symlink()and'__pycache__'not in x.parts]+[plan.relative_to(WT).as_posix()])
 for rel in selected:
  assert rel.startswith(OWN+'/')or rel.startswith(SOURCE+'/')
  assert Path(rel).suffix.lower()not in{'.exe','.dll','.o','.obj','.a','.lib','.bin','.pt','.pth','.onnx','.npz','.npy','.pem','.key','.usd','.usdc','.usda','.stl','.stp','.step','.zip','.7z','.jsonl'}
 new(plan,{'expected_staged_paths':sorted(selected+[RECORD]),'selected_files':selected,'allowed_directories':[OWN,SOURCE],'record':RECORD,'sourceprep_review_SHA':SEAL_SHA,'each_selected_byte_SHA_map':'original helper record and staged blob validation','allA_noD_noForeign':True,'narrow_git_add_operands':[OWN,SOURCE,RECORD],'not_staged_original_pending_receipt':'history/experiments/mod4v1_robust_traditional_phase5_PENDING/ARCHIVE_PHASE4_RECEIPT.json','later_receipt':'phase6_PENDING not thiscommit'})
 hashes={p:sha((WT/p).read_bytes())for p in selected};expected=set(selected+[RECORD]);verified={};sys.path.insert(0,str(WT/'archive_tools'));from capture_history import redact
 spec=importlib.util.spec_from_file_location('one_original_phase5_recorder',WT/'archive_tools/record_experiment.py');rec=importlib.util.module_from_spec(spec);spec.loader.exec_module(rec);assert rec.ROOT==WT;original=rec.git
 def check():
  guard();frozen();actual=set(paths('diff','--cached','--name-only','-z'));assert actual==expected,{'missing':sorted(expected-actual),'foreign':sorted(actual-expected)}
  ns=paths('diff','--cached','--name-status','-z');assert len(ns)==2*len(expected)and all(ns[i]=='A'for i in range(0,len(ns),2));record=load(WT/RECORD);assert record['tag']==TAG and record['id']==DATE+'-'+IDENT and record['kind']=='diagnostic'and record['source_and_evidence_sha256']==hashes
  hs={**hashes,RECORD:sha((WT/RECORD).read_bytes())};objects=[]
  for v in cmd('ls-files','--stage','-z','--',OWN,SOURCE,RECORD).stdout.split(b'\0'):
   if not v:continue
   info,path=v.split(b'\t',1);mode,oid,stage=info.split();assert stage==b'0'and mode in(b'100644',b'100755');objects.append((path.decode(),oid.decode()))
  assert{p for p,o in objects}==expected;buf=io.BytesIO(cmd('cat-file','--batch',input=('\n'.join(o for p,o in objects)+'\n').encode()).stdout)
  for path,oid in objects:
   got,kind,size=buf.readline().split();assert got.decode()==oid and kind==b'blob';raw=buf.read(int(size));assert buf.read(1)==b'\n'and sha(raw)==hs[path],path
  verified.update(expected_staged_count=len(expected),exact_paths=True,allA=True,noD_noForeign=True,each_blob_SHA_frozen_or_selected_exact=True,record_source_map_exact=True,review_index_unchanged=SEAL_SHA);print('PH5_STAGED_EXACT_VERIFIED',json.dumps(verified),flush=True)
 def narrow(*args):
  if args and args[0]=='add':assert args[1]=='--'and args[2]==RECORD and set(args[3:])==set(selected);original('add','--force','--sparse','--',OWN,SOURCE,RECORD);check();return''
  if args and args[0]=='commit':check()
  if args and args[0]=='push':raise AssertionError('No helper implicit/global push')
  if args[:2]==('tag','-a'):assert args[2]==TAG
  return original(*args)
 rec.git=narrow;sys.argv=[str(WT/'archive_tools/record_experiment.py'),'--id',IDENT,'--title','Archive reviewed MOD4v1 traditional phase5 through R47 and completed H5','--kind','diagnostic','--note-file',str(C/'NOTE.md'),'--validation','Accepted immutable PH5source scope,100protocolcases99physical1zero-stepERROR,H5complete64pass40fail24;1776textSHApairs;1historicaltextgap/unknownraw;exactallA/stagedblobSHA; noR48/CB1/MANUAL/movinghop/rawhash/tests; postreceiptphase6pending.','--files',*selected]
 rec.main();commit=text('rev-parse','HEAD');obj=text('rev-parse','refs/tags/'+TAG);peeled=text('rev-parse','refs/tags/'+TAG+'^{}');assert peeled==commit and text('cat-file','-t','refs/tags/'+TAG)=='tag'and text('rev-parse',commit+'^')==BASE
 guard();frozen();assert set(paths('diff-tree','--no-commit-id','--name-only','-r','-z',commit))==expected and not text('diff','--cached','--name-only')and not text('diff','--name-only')
 prepush=refs();oldrefs(prepush);assert prepush.get('refs/heads/'+BRANCH)==BASE and'refs/tags/'+TAG not in prepush
 push=cmd('push','--atomic','origin','HEAD:refs/heads/'+BRANCH,'refs/tags/'+TAG+':refs/tags/'+TAG);post=refs();oldrefs(post);assert post.get('refs/heads/'+BRANCH)==commit and post.get('refs/tags/'+TAG)==obj and post.get('refs/tags/'+TAG+'^{}')==commit
 frozen();assert sha((WT/'archive_tools/record_experiment.py').read_bytes())==HELPER_SHA;status=text('status','--short');assert all(line.startswith('?? history/experiments/mod4v1_robust_traditional_phase5_PENDING/')for line in status.splitlines()),status
 stdout,n1=redact(push.stdout.decode('utf-8','replace'));stderr,n2=redact(push.stderr.decode('utf-8','replace'))
 receipt={'status':'PH5_ORIGINAL_RECORD_COMMIT_ANNOTATEDTAG_ATOMIC_OWNREFS_REMOTE_VERIFIED','commit':commit,'parent':BASE,'branch':BRANCH,'tag':TAG,'tag_object':obj,'peeled_commit':peeled,'record':RECORD,'payload_directories':[OWN,SOURCE],'sourceprep_files':count,'selected_payload_files_without_record':len(selected),'exact_staged':verified,'sourceprep_REVIEW_INDEX_SHA_unchanged':SEAL_SHA,'original_helper_SHA_unchanged':HELPER_SHA,'source_summary':summary,'missing_provenance_disclosed':'1historicalERROR_REPORTSHA gap;2currentrawunknown overlap prior15 unknowns; no repair','remote_pre_record':pre,'remote_pre_push':prepush,'remote_post':post,'initial_main_probe':INITIAL_MAIN,'main_same_only_immediate_push_window':prepush.get('refs/heads/main')==post.get('refs/heads/main'),'global_no_main_concurrent_changes_NOT_claimed':True,'PH1_PH2_PH3_PH4_tag_objects_peeled_unchanged':True,'push_stdout_redacted':stdout,'push_stderr_redacted':stderr,'push_log_redactions':n1+n2,'owner_status_before_new_postreceipt':status,'old_pending_receipt_not_staged':'same bytes already archived inside PH5snapshot; original localpendingpath untouched','receipt_git_status':'PHASE6_PENDING_POSTCOMMIT_NOT_IN_PHASE5_TREE','receipt_recursion_avoided':True,'sourceRoot_model_candidate_expertindex_main_otherrefs_mutated':False,'new_physics_unit_compile_once_assetsrawhash_GPU_agents_realIO_goalactions':False,'recorded_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'overall_Goal_active':True}
 new(PENDING/'ARCHIVE_PHASE5_RECEIPT.json',receipt);print('PH5_REMOTE_VERIFIED_RECEIPT',json.dumps(receipt,ensure_ascii=False,indent=2),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  PENDING.mkdir(parents=True,exist_ok=True);n=1
  while(PENDING/f'ARCHIVE_PHASE5_OPERATION_FAILURE_{n:03d}.txt').exists():n+=1
  (PENDING/f'ARCHIVE_PHASE5_OPERATION_FAILURE_{n:03d}.txt').write_text(traceback.format_exc()+'\nPH6pending formal report. Inspect existing commit/tag/record first; never replay successful record/tag.\n',encoding='utf-8');raise
