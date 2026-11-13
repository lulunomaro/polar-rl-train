"""Archive new bounded2h stage; full PT blobs and immutable report snapshots via7897."""
from pathlib import Path
import argparse,datetime,hashlib,json,shutil,sys,tempfile
T=Path(__file__).resolve().parent;R=T.parents[2];E=T/'evidence'
p=argparse.ArgumentParser();p.add_argument('--phase',choices=['review005'],required=True);phase=p.parse_args().phase
sys.path.insert(0,str(R.parent/'tmp/step7_archive_helper'));import record_experiment as rec
original=rec.git;NET=('-c','http.proxy=http://127.0.0.1:7897','-c','http.sslVerify=true');binary=[]
date=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y%m%d');ID='stairs-phase-height-repair-2h-'+phase+'-01';TAG='trial-'+date+'-'+ID;record=R/'history/experiments'/(date+'-'+ID+'.json')
def git(*args):
 if args[0]=='add':
  info=json.loads(record.read_text(encoding='utf8'))
  for name in binary:info['source_and_evidence_sha256'][name]=hashlib.sha256((R/name).read_bytes()).hexdigest()
  info['artifact_storage']='Human explicitly requested complete ordinary PT blobs; no LFS pointers. NPZ originals retained and indexed.';record.write_text(json.dumps(info,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
  names=[x for x in args[1:] if x!='--']+binary
  with tempfile.NamedTemporaryFile(mode='wb',dir=R.parent/'tmp',delete=False,prefix='stair2h-add-') as f:
   for name in dict.fromkeys(names):f.write(name.encode('utf8')+b'\0')
   path=Path(f.name)
  try:return original('--literal-pathspecs',*NET,'add','--sparse','-f','--pathspec-from-file='+str(path),'--pathspec-file-nul')
  finally:path.unlink()
 if args[0]=='tag' and '-m' in args:
  i=args.index('-m')
  with tempfile.NamedTemporaryFile(mode='w',encoding='utf8',newline='\n',dir=R.parent/'tmp',delete=False,prefix='stair2h-tag-') as f:f.write(args[i+1]);path=Path(f.name)
  try:return original(*NET,*args[:i],'-F',str(path),*args[i+2:])
  finally:path.unlink()
 return original(*NET,*args)
rec.git=git
assert git('branch','--show-current')=='mod4v1-experts-fulldr-rm70'
assert not git('tag','--list',TAG),'Existing archive must only resume push; do not record again'
point=E/'checkpoint_evals/model_005m'
result=json.loads((point/'EVALUATION.json').read_text());assert result['complete']
weight=T/'weights/model_005m.pt';assert hashlib.sha256(weight.read_bytes()).hexdigest()==result['sha256']
files=[T/'archive_checkpoint_review.py',T/'README.md',T/'CHECKPOINT005_REVIEW.md',E/'CHECKPOINT005_ARTIFACT_INDEX.json',E/'CHECKPOINT005_REVIEW.json',E/'inspections/INSPECTION_005M.json',E/'training/PPO_UPDATE_WITH_TEACHER.py',weight]
files += [x for x in sorted(point.rglob('*')) if x.is_file() and x.suffix in {'.json','.log','.xml','.py'}]
binary[:]=[x.relative_to(R).as_posix() for x in files if x.suffix=='.pt'];text=[x.relative_to(R).as_posix() for x in files if x.suffix!='.pt']
main_before=git('ls-remote','origin','refs/heads/main').split()[0]
note=T/'CHECKPOINT005_REVIEW.md'
sys.argv=['record_experiment.py','--id',ID,'--title','MOD4 first5m high-stance10of10 flat60of60 and complete PPO','--kind','evaluation','--note-file',str(note),'--validation','Complete original5min saved PPO blob; same fixed flat60+straight5+oblique20+descent5 protocol; actual high-stance result and all failures retained;7200s run continues unchanged','--files',*text]
rec.main();head=git('rev-parse','HEAD');tag=git('rev-parse',TAG);assert git('rev-parse',TAG+'^{}')==head
git('push','--atomic','origin','HEAD','refs/tags/'+TAG)
refs={line.split()[1]:line.split()[0] for line in git('ls-remote','origin','refs/heads/mod4v1-experts-fulldr-rm70','refs/heads/main','refs/tags/'+TAG,'refs/tags/'+TAG+'^{}').splitlines()}
assert refs['refs/heads/mod4v1-experts-fulldr-rm70']==head and refs['refs/tags/'+TAG]==tag and refs['refs/tags/'+TAG+'^{}']==head
for name in binary:
 blob=git('rev-parse',head+':'+name);assert blob==git('hash-object','--no-filters',str(R/name)),name
print(json.dumps(dict(phase=phase,commit=head,tag=TAG,remote_verified=True,ordinary_full_PT_files=len(binary),main_before=main_before,main_after=refs['refs/heads/main']),indent=2),flush=True)
