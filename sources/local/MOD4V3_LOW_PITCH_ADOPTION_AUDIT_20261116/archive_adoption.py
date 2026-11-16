"""Record explicit human adoption, full PT blob, and frozen SCUT reward audit."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import argparse,ast,hashlib,json,sys,tempfile
A=Path(__file__).resolve().parent;R=A.parents[2];D=R/'deliveries/MOD4V3_LOW_PITCH_20261116'
sys.path.insert(0,str(R.parent/'tmp/step7_archive_helper'));import record_experiment as rec
NET=('-c','http.proxy=http://127.0.0.1:7897','-c','http.sslVerify=true');original=rec.git
DAY=datetime.now(timezone(timedelta(hours=8))).strftime('%Y%m%d');ID='low-pitch-adoption-scut-audit-01';TRIAL='trial-'+DAY+'-'+ID;NAME='11月16日俯仰较低模型';ALIAS='best-20261116-low-pitch-c874a1af';record=R/'history/experiments'/(DAY+'-'+ID+'.json');binary=[(D/'model_full_ppo.pt').relative_to(R).as_posix()]
def git(*args):
 if args[0]=='add':
  info=json.loads(record.read_text(encoding='utf8'))
  for name in binary:info['source_and_evidence_sha256'][name]=hashlib.sha256((R/name).read_bytes()).hexdigest()
  info['artifact_storage']='User-authorized complete ordinary PT blob; archived trajectories remain indexed original NPZ; no new training or rollout';info['human_model_name']=NAME
  record.write_text(json.dumps(info,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
  names=[v for v in args[1:]if v!='--']+binary
  with tempfile.NamedTemporaryFile(mode='wb',dir=R.parent/'tmp',delete=False,prefix='low-pitch-add-')as f:
   for name in dict.fromkeys(names):f.write(name.encode('utf8')+b'\0')
   temp=Path(f.name)
  try:return original('--literal-pathspecs',*NET,'add','--sparse','-f','--pathspec-from-file='+str(temp),'--pathspec-file-nul')
  finally:temp.unlink()
 if args[0]=='tag'and'-m'in args:
  i=args.index('-m')
  with tempfile.NamedTemporaryFile(mode='w',encoding='utf8',newline='\n',dir=R.parent/'tmp',delete=False,prefix='low-pitch-tag-')as f:f.write(args[i+1]);temp=Path(f.name)
  try:return original(*NET,*args[:i],'-F',str(temp),*args[i+2:])
  finally:temp.unlink()
 return original(*NET,*args)
rec.git=git;branch=git('branch','--show-current');assert branch=='mod4v1-experts-fulldr-rm70'
main_before=git('ls-remote','origin','refs/heads/main').split()[0]
if not git('tag','--list',TRIAL):
 assert git('rev-parse','HEAD')=='b7cd7041146291bc21fc56a17e97aaaca69b4629','Review concurrent HEAD change before adoption archive'
 assert not git('diff','--cached','--name-only'),'Preserve existing staged work'
 verification=json.loads((A/'evidence/VERIFICATION.json').read_text());assert verification['passed']
 files=[p for folder in [A,D]for p in folder.rglob('*')if p.is_file()and'__pycache__'not in p.parts and p.suffix not in ['.pt','.npz','.npy','.pyc']]
 files+=[R/'AGENTS.md',R/'docs/DR_TRAINING_INDEX_20261111.md',R/'sources/local/MOD4V3_DR_TRAINING_RECORDS_20261111/MODEL_REGISTRY.json',R/'deliveries/CURRENT_COMPREHENSIVE_MODEL.json',R/'deliveries/MOD4V3_BEST_COMPREHENSIVE_20261113/README.md']
 sys.argv=['record_experiment.py','--id',ID,'--title',NAME,'--kind','evaluation','--note-file',str(A/'REPORT.md'),'--validation','Explicit human adoption of5m c874a1af/iter25362;complete ordinary PT and17 optimizer states;35/78/6 interface;11 integrity/readback checks passed;8 archived paired trajectories;actual effective speed-square ratio240;no new training,rollout,asset or reward change;old db6 rollback retained','--files',*[p.relative_to(R).as_posix()for p in files]]
 rec.main()
commit=git('rev-parse',TRIAL+'^{}');assert git('rev-parse','HEAD')==commit
for label in [NAME,ALIAS]:
 if not git('tag','--list',label):
  git('check-ref-format','refs/tags/'+label);git('tag','-a',label,commit,'-m',NAME+'\n\nUser-adopted full PPO c874a1af,iteration25362; complete5m checkpoint. Current comprehensive default; db6 retained for rollback. '+TRIAL)
 assert git('rev-parse',label+'^{}')==commit
refs_to_push=['HEAD']+['refs/tags/'+v for v in [TRIAL,NAME,ALIAS]]
git('push','--atomic','origin',*refs_to_push)
patterns=['refs/heads/'+branch,'refs/heads/main']+[v for tag in [TRIAL,NAME,ALIAS]for v in ['refs/tags/'+tag,'refs/tags/'+tag+'^{}']]
remote={line.split()[1]:line.split()[0]for line in git('ls-remote','origin',*patterns).splitlines()}
assert remote['refs/heads/main']==main_before and remote['refs/heads/'+branch]==commit
for label in [TRIAL,NAME,ALIAS]:
 assert remote['refs/tags/'+label]==git('rev-parse',label) and remote['refs/tags/'+label+'^{}']==commit
for file in binary:assert git('rev-parse',commit+':'+file)==git('hash-object','--no-filters',str(R/file))
print(json.dumps(dict(model_name=NAME,commit=commit,trial_tag=TRIAL,model_tag=NAME,ascii_alias=ALIAS,remote_branch_verified=True,remote_main_unchanged=True,all_annotated_tags_and_peeled_verified=True,full_PT_blob_verified=True),ensure_ascii=False,indent=2),flush=True)
