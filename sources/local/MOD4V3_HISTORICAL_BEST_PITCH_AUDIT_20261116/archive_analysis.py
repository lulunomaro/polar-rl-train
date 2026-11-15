"""Record and push this frozen historical-model pitch evaluation; no training."""
from pathlib import Path
import sys,json,tempfile,datetime
A=Path(__file__).resolve().parent;R=A.parents[2]
sys.path.insert(0,str(R.parent/'tmp/step7_archive_helper'))
import record_experiment as rec
original=rec.git
NET=('-c','http.proxy=http://127.0.0.1:7897','-c','http.sslVerify=true')
def git(*args):
 if args[0]=='add':
  names=[v for v in args[1:]if v!='--']
  with tempfile.NamedTemporaryFile(mode='wb',dir=R.parent/'tmp',delete=False,prefix='historical-pitch-add-')as f:
   for name in dict.fromkeys(names):f.write(name.encode('utf8')+b'\0')
   path=Path(f.name)
  try:return original('--literal-pathspecs',*NET,'add','--sparse','-f','--pathspec-from-file='+str(path),'--pathspec-file-nul')
  finally:path.unlink()
 if args[0]=='tag'and'-m'in args:
  i=args.index('-m')
  with tempfile.NamedTemporaryFile(mode='w',encoding='utf8',newline='\n',dir=R.parent/'tmp',delete=False,prefix='historical-pitch-tag-')as f:f.write(args[i+1]);path=Path(f.name)
  try:return original(*NET,*args[:i],'-F',str(path),*args[i+2:])
  finally:path.unlink()
 return original(*NET,*args)
rec.git=git
branch=git('branch','--show-current');assert branch=='mod4v1-experts-fulldr-rm70'
assert not git('diff','--cached','--name-only'),'Preserve unrelated staging; do not proceed with a mixed commit'
id='historical-best-pitch-audit-01';date=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y%m%d');tag='trial-'+date+'-'+id
main_before=git('ls-remote','origin','refs/heads/main').split()[0]
if git('tag','--list',tag):
 commit=git('rev-parse',tag+'^{}');assert git('rev-parse','HEAD')==commit,'Existing archive tag must be resumed explicitly if HEAD moved'
else:
 files=[p.relative_to(R).as_posix()for p in sorted(A.rglob('*'))if p.is_file()and p.suffix not in {'.npz','.npy','.pyc'}and'__pycache__'not in p.parts]
 files.append('docs/DR_TRAINING_INDEX_20261111.md')
 sys.argv=['record_experiment.py','--id',id,'--title','Compare pitch of Nov12 and Nov13 named best MOD4v3 models','--kind','evaluation','--note-file',str(A/'README.md'),'--validation','Frozen Nov12 7cc1 weight SHA verified; eight matched nominal start-stop episodes completed without resets; reuse original db6 baseline with identical trajectory code and guard; report actual entry speed to avoid a same-speed braking claim; zero PPO updates and no promotion; raw NumPy retained with SHA indices','--files',*files]
 rec.main();commit=git('rev-parse','HEAD');assert git('rev-parse',tag+'^{}')==commit
expected_tag=git('rev-parse',tag)
git('push','--atomic','origin','HEAD','refs/tags/'+tag)
refs={line.split()[1]:line.split()[0]for line in git('ls-remote','origin','refs/heads/'+branch,'refs/heads/main','refs/tags/'+tag,'refs/tags/'+tag+'^{}').splitlines()}
assert refs['refs/heads/'+branch]==commit
assert refs['refs/tags/'+tag]==expected_tag and refs['refs/tags/'+tag+'^{}']==commit
assert refs['refs/heads/main']==main_before
assert not git('status','--porcelain','--',A.relative_to(R).as_posix())
print(json.dumps(dict(commit=commit,tag=tag,remote_branch_and_annotated_tag_verified=True,remote_main_unchanged=True,audit_workspace_clean=True),indent=2),flush=True)
