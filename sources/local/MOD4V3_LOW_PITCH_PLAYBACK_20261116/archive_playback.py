"""Record the launched native MuJoCo player and its frozen ready-state evidence."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import sys,json,tempfile,ast
A=Path(__file__).resolve().parent;R=A.parents[2];D=R/'deliveries/MOD4V3_LOW_PITCH_20261116'
sys.path.insert(0,str(R.parent/'tmp/step7_archive_helper'));import record_experiment as rec
original=rec.git;NET=('-c','http.proxy=http://127.0.0.1:7897','-c','http.sslVerify=true');DAY=datetime.now(timezone(timedelta(hours=8))).strftime('%Y%m%d');ID='low-pitch-mujoco-playback-01';TAG='trial-'+DAY+'-'+ID

def git(*args):
 if args[0]=='add':
  with tempfile.NamedTemporaryFile(mode='wb',dir=R.parent/'tmp',delete=False,prefix='low-pitch-playback-add-')as f:
   for v in args[1:]:
    if v!='--':f.write(v.encode('utf8')+b'\0')
   temp=Path(f.name)
  try:return original('--literal-pathspecs',*NET,'add','--sparse','-f','--pathspec-from-file='+str(temp),'--pathspec-file-nul')
  finally:temp.unlink()
 if args[0]=='tag'and'-m'in args:
  i=args.index('-m')
  with tempfile.NamedTemporaryFile(mode='w',encoding='utf8',newline='\n',dir=R.parent/'tmp',delete=False,prefix='low-pitch-playback-tag-')as f:f.write(args[i+1]);temp=Path(f.name)
  try:return original(*NET,*args[:i],'-F',str(temp),*args[i+2:])
  finally:temp.unlink()
 return original(*NET,*args)
rec.git=git;branch=git('branch','--show-current');assert branch=='mod4v1-experts-fulldr-rm70';main=git('ls-remote','origin','refs/heads/main').split()[0]
if not git('tag','--list',TAG):
 assert git('rev-parse','HEAD')=='fad7e1b1f67a5fffd7b7874d17b96ea6140fa0c4';assert not git('diff','--cached','--name-only')
 ast.parse((D/'play_mujoco.py').read_text(encoding='utf-8-sig'));files=[p for p in A.rglob('*')if p.is_file()and'__pycache__'not in p.parts]
 files +=[D/'play_mujoco.py',D/'.gitignore',D/'README.md']
 sys.argv=['record_experiment.py','--id',ID,'--title','播放11月16日俯仰较低模型：MuJoCo WASD','--kind','evaluation','--note-file',str(A/'README.md'),'--validation','User-requested visible native MuJoCo playback;adopted5m c874a1af/iter25362 SHA readback;viewer.is_running andTk visible true;real-time body pitch/rate shown;original MOD4v3 plant/native contacts and2.5ms/100Hz legs/400Hz wheels/50Hz policy;hard input changes;no training/export/default change;live viewer preserved','--files',*[p.relative_to(R).as_posix()for p in files]];rec.main()
commit=git('rev-parse',TAG+'^{}');assert git('rev-parse','HEAD')==commit;git('push','--atomic','origin','HEAD','refs/tags/'+TAG)
refs={line.split()[1]:line.split()[0]for line in git('ls-remote','origin','refs/heads/main','refs/heads/'+branch,'refs/tags/'+TAG,'refs/tags/'+TAG+'^{}').splitlines()};assert refs['refs/heads/main']==main and refs['refs/heads/'+branch]==commit and refs['refs/tags/'+TAG+'^{}']==commit and refs['refs/tags/'+TAG]==git('rev-parse',TAG)
print(json.dumps(dict(commit=commit,tag=TAG,remote_verified=True,viewer_kept_running=True),ensure_ascii=False,indent=2),flush=True)
