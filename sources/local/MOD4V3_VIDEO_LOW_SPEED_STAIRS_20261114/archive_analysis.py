"""Archive the video diagnosis and evidence through the existing trial recorder."""
from pathlib import Path
import sys,json,tempfile,datetime,hashlib
T=Path(__file__).resolve().parent;R=T.parents[2]
sys.path.insert(0,str(R.parent/'tmp/step7_archive_helper'));import record_experiment as rec
original=rec.git;NET=('-c','http.proxy=http://127.0.0.1:7897','-c','http.sslVerify=true')
def git(*args):
 if args[0]=='add':
  names=[x for x in args[1:] if x!='--']
  with tempfile.NamedTemporaryFile(mode='wb',dir=R.parent/'tmp',delete=False,prefix='video-analysis-add-') as f:
   for name in dict.fromkeys(names):f.write(name.encode('utf8')+b'\0')
   path=Path(f.name)
  try:return original('--literal-pathspecs',*NET,'add','--sparse','-f','--pathspec-from-file='+str(path),'--pathspec-file-nul')
  finally:path.unlink()
 if args[0]=='tag' and '-m' in args:
  i=args.index('-m')
  with tempfile.NamedTemporaryFile(mode='w',encoding='utf8',newline='\n',dir=R.parent/'tmp',delete=False,prefix='video-analysis-tag-') as f:f.write(args[i+1]);path=Path(f.name)
  try:return original(*NET,*args[:i],'-F',str(path),*args[i+2:])
  finally:path.unlink()
 return original(*NET,*args)
rec.git=git
assert git('branch','--show-current')=='mod4v1-experts-fulldr-rm70'
ID='video-rearward-stair-frame-analysis-01';date=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y%m%d');TAG='trial-'+date+'-'+ID
assert not git('tag','--list',TAG),'Existing objects must only resume push'
files=[x for x in sorted(T.rglob('*')) if x.is_file() and '__pycache__' not in x.parts and x.name not in {'archive.log','archive_error.log'}]
files += [R/'README.md',R/'docs/DR_TRAINING_INDEX_20261111.md',R/'sources/local/MOD4V3_DR_TRAINING_RECORDS_20261111/README.md']
main_before=git('ls-remote','origin','refs/heads/main').split()[0]
sys.argv=['record_experiment.py','--id',ID,'--title','Analyze body-supported rearward wheel swing from reference stair video','--kind','diagnostic','--note-file',str(T/'README.md'),'--validation','4302 original frames decoded with PTS; first two ascent transitions reviewed in consecutive frames;5 cycles compared on timeline; annotated key frames inspected;0.25x clip duration5.97s verified; current lift-times-retraction code and pinned MOD4/R3 guide geometry read only; no new training or reward edits','--files',*[x.relative_to(R).as_posix() for x in files]]
rec.main();head=git('rev-parse','HEAD');tag=git('rev-parse',TAG);assert git('rev-parse',TAG+'^{}')==head
git('push','--atomic','origin','HEAD','refs/tags/'+TAG)
refs={line.split()[1]:line.split()[0] for line in git('ls-remote','origin','refs/heads/mod4v1-experts-fulldr-rm70','refs/heads/main','refs/tags/'+TAG,'refs/tags/'+TAG+'^{}').splitlines()}
assert refs['refs/heads/mod4v1-experts-fulldr-rm70']==head and refs['refs/tags/'+TAG]==tag and refs['refs/tags/'+TAG+'^{}']==head
print(json.dumps(dict(commit=head,tag=TAG,remote_verified=True,archived_files=len(files),main_before=main_before,main_after=refs['refs/heads/main'],video_original='retained at supplied local path and SHA indexed; original not modified'),ensure_ascii=False,indent=2),flush=True)
