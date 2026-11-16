"""Archive all controlled comparisons, calibration failures, reports and source."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import sys,json,tempfile,ast
A=Path(__file__).resolve().parent;R=A.parents[2]
sys.path.insert(0,str(R.parent/'tmp/step7_archive_helper'));import record_experiment as rec
original=rec.git;NET=('-c','http.proxy=http://127.0.0.1:7897','-c','http.sslVerify=true')
DAY=datetime.now(timezone(timedelta(hours=8))).strftime('%Y%m%d');ID='scut-mod4-matched-pitch-compare-01';TAG='trial-'+DAY+'-'+ID

def git(*args):
 if args[0]=='add':
  names=[v for v in args[1:]if v!='--']
  with tempfile.NamedTemporaryFile(mode='wb',dir=R.parent/'tmp',delete=False,prefix='pitch-compare-add-')as f:
   for name in dict.fromkeys(names):f.write(name.encode('utf8')+b'\0')
   temp=Path(f.name)
  try:return original('--literal-pathspecs',*NET,'add','--sparse','-f','--pathspec-from-file='+str(temp),'--pathspec-file-nul')
  finally:temp.unlink()
 if args[0]=='tag'and'-m'in args:
  i=args.index('-m')
  with tempfile.NamedTemporaryFile(mode='w',encoding='utf8',newline='\n',dir=R.parent/'tmp',delete=False,prefix='pitch-compare-tag-')as f:f.write(args[i+1]);temp=Path(f.name)
  try:return original(*NET,*args[:i],'-F',str(temp),*args[i+2:])
  finally:temp.unlink()
 return original(*NET,*args)
rec.git=git;branch=git('branch','--show-current');assert branch=='mod4v1-experts-fulldr-rm70';main=git('ls-remote','origin','refs/heads/main').split()[0]
if not git('tag','--list',TAG):
 assert git('rev-parse','HEAD')=='212b9d4ba3899b7ea0d1b36f9cdf697d688af657','Review concurrent branch change'
 assert not git('diff','--cached','--name-only')
 assert json.loads((A/'evidence/VERIFICATION.json').read_text())['passed']
 for p in A.glob('*.py'):ast.parse(p.read_text(encoding='utf-8-sig'))
 files=[]
 for p in A.rglob('*'):
  if not p.is_file()or'__pycache__'in p.parts or p.suffix.lower()in['.npz','.npy','.msh','.pt','.pyc']:continue
  files.append(p)
 for rel in ['AGENTS.md','docs/DR_TRAINING_INDEX_20261111.md','sources/local/MOD4V3_LOW_PITCH_ADOPTION_AUDIT_20261116/REPORT.md','sources/local/SCUT_ORIGINAL_PITCH_AUDIT_20261116/README.md']:files.append(R/rel)
 sys.argv=['record_experiment.py','--id',ID,'--title','华南虎与11月16日低俯仰模型：同材料同实速详细对照','--kind','evaluation','--note-file',str(A/'REPORT.md'),'--validation','Frozen SCUTd19492be and adoptedMOD4v3c874a1af;common terrains/materials/time schedule;11 attained-speed pairs within0.02m/s and16 exact-command pairs;13 unmatched conditions and all hard-contact early resets retained;native plants/motors/clocks/solver and2mm guard;704raw arrays indexed;memory repair resumes unfinished cases only;no training/default/export change','--files',*[p.relative_to(R).as_posix()for p in files]]
 rec.main()
commit=git('rev-parse',TAG+'^{}');assert git('rev-parse','HEAD')==commit
git('push','--atomic','origin','HEAD','refs/tags/'+TAG)
refs={line.split()[1]:line.split()[0]for line in git('ls-remote','origin','refs/heads/main','refs/heads/'+branch,'refs/tags/'+TAG,'refs/tags/'+TAG+'^{}').splitlines()}
assert refs['refs/heads/main']==main and refs['refs/heads/'+branch]==commit and refs['refs/tags/'+TAG+'^{}']==commit and refs['refs/tags/'+TAG]==git('rev-parse',TAG)
print(json.dumps(dict(commit=commit,tag=TAG,remote_branch_tag_and_peeled_verified=True,remote_main_unchanged=True,adopted_model_tag_retained=git('rev-parse','11月16日俯仰较低模型^{}'),reports_archived=True,raw_npz_uploaded=False),ensure_ascii=False,indent=2),flush=True)
