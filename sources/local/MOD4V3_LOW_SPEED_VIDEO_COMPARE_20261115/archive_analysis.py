"""Archive the video diagnosis and evidence through the existing trial recorder."""
from pathlib import Path
import sys,json,tempfile,datetime,hashlib
T=Path(__file__).resolve().parent;R=T.parents[2]
sys.path.insert(0,str(R.parent/'tmp/step7_archive_helper'));import record_experiment as rec
original=rec.git;NET=('-c','http.proxy=http://127.0.0.1:7897','-c','http.sslVerify=true')
def git(*args):
 if args[0]=='add':
  info=json.loads(record.read_text(encoding='utf8'))
  for name in binary:info['source_and_evidence_sha256'][name]=hashlib.sha256((R/name).read_bytes()).hexdigest()
  info['artifact_storage']='Human-authorized complete ordinary PT body; diagnostic NPZ originals retained with SHA index';record.write_text(json.dumps(info,ensure_ascii=False,indent=2)+chr(10),encoding='utf8')
  names=[x for x in args[1:] if x!='--']+binary
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
ID='low-speed-video-vs-policy40m-01';date=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y%m%d');TAG='trial-'+date+'-'+ID
record=R/'history/experiments'/(date+'-'+ID+'.json')
assert not git('tag','--list',TAG),'Existing objects must only resume push'
files=[x for x in sorted(T.rglob('*')) if x.is_file() and '__pycache__' not in x.parts and x.name not in {'archive.log','archive_error.log'} and x.suffix not in {'.pt','.npz','.npy','.partial','.pyc'}]
files += [R/'README.md',R/'docs/DR_TRAINING_INDEX_20261111.md',R/'sources/local/MOD4V3_DR_TRAINING_RECORDS_20261111/README.md']
binary=[x.relative_to(R).as_posix()for x in(T/'weights').glob('*.pt')]
main_before=git('ls-remote','origin','refs/heads/main').split()[0]
sys.argv=['record_experiment.py','--id',ID,'--title','Compare reference rearward wheel-lift video with40m low-speed stair student','--kind','diagnostic','--note-file',str(T/'README.md'),'--validation','Original video key frames reviewed;30m detailed replays exactly reproduce saved original trace columns;40m0.4/0.6whole and late-assisted first-start replays retain same physics/controller/guards; measured body-relative wheel rearward6-8cm but max world axle height8.5-9.7cm; late rearward pose drops wheels to ground within0.5s; real contact force groups logged; full ordinary PT body and diagnostic NPZ SHA index; no training recipe changes; authorized two-hour owner continues','--files',*[x.relative_to(R).as_posix() for x in files]]
rec.main();head=git('rev-parse','HEAD');tag=git('rev-parse',TAG);assert git('rev-parse',TAG+'^{}')==head
git('push','--atomic','origin','HEAD','refs/tags/'+TAG)
refs={line.split()[1]:line.split()[0] for line in git('ls-remote','origin','refs/heads/mod4v1-experts-fulldr-rm70','refs/heads/main','refs/tags/'+TAG,'refs/tags/'+TAG+'^{}').splitlines()}
assert refs['refs/heads/mod4v1-experts-fulldr-rm70']==head and refs['refs/tags/'+TAG]==tag and refs['refs/tags/'+TAG+'^{}']==head
for name in binary:assert git('rev-parse',head+':'+name)==git('hash-object','--no-filters',str(R/name))
print(json.dumps(dict(commit=head,tag=TAG,remote_verified=True,archived_files=len(files),main_before=main_before,main_after=refs['refs/heads/main'],video_original='retained at supplied local path and SHA indexed; original not modified',ordinary_full_PT_files=len(binary)),ensure_ascii=False,indent=2),flush=True)
