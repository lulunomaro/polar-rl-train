"""Archive new bounded40m stage; full PT blobs and immutable report snapshots via7897."""
from pathlib import Path
import argparse,datetime,hashlib,json,shutil,sys,tempfile
T=Path(__file__).resolve().parent;R=T.parents[2];E=T/'evidence'
p=argparse.ArgumentParser();p.add_argument('--phase',choices=['planned','launch','complete'],required=True);phase=p.parse_args().phase
sys.path.insert(0,str(R.parent/'tmp/step7_archive_helper'));import record_experiment as rec
original=rec.git;NET=('-c','http.proxy=http://127.0.0.1:7897','-c','http.sslVerify=true');binary=[]
date=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y%m%d');ID='rearward-supported-stairs-40m-'+phase+'-01';TAG='trial-'+date+'-'+ID;record=R/'history/experiments'/(date+'-'+ID+'.json')
def git(*args):
 if args[0]=='add':
  info=json.loads(record.read_text(encoding='utf8'))
  for name in binary:info['source_and_evidence_sha256'][name]=hashlib.sha256((R/name).read_bytes()).hexdigest()
  info['artifact_storage']='Human explicitly requested complete ordinary PT blobs; no LFS pointers. NPZ originals retained and indexed.';record.write_text(json.dumps(info,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
  names=[x for x in args[1:] if x!='--']+binary
  with tempfile.NamedTemporaryFile(mode='wb',dir=R.parent/'tmp',delete=False,prefix='rearward40m-add-') as f:
   for name in dict.fromkeys(names):f.write(name.encode('utf8')+b'\0')
   path=Path(f.name)
  try:return original('--literal-pathspecs',*NET,'add','--sparse','-f','--pathspec-from-file='+str(path),'--pathspec-file-nul')
  finally:path.unlink()
 if args[0]=='tag' and '-m' in args:
  i=args.index('-m')
  with tempfile.NamedTemporaryFile(mode='w',encoding='utf8',newline='\n',dir=R.parent/'tmp',delete=False,prefix='rearward40m-tag-') as f:f.write(args[i+1]);path=Path(f.name)
  try:return original(*NET,*args[:i],'-F',str(path),*args[i+2:])
  finally:path.unlink()
 return original(*NET,*args)
rec.git=git
assert git('branch','--show-current')=='mod4v1-experts-fulldr-rm70'
assert not git('tag','--list',TAG),'Existing archive must only resume push; do not record again'
if phase=='launch':
 snapshot=E/'launch_snapshot';snapshot.mkdir(exist_ok=False)
 for source in (E/'training').glob('*.json'):
  if source.name in ['LATEST_PROGRESS.json','FIRST_UPDATE.json','RESTORE.json','STARTUP.json','PPO_EFFECTIVE.json','ACTOR_UPDATE_SCOPE.json','TEACHER_KEEP_SCOPE.json','TEACHER_RETENTION_STARTUP.json']:
   shutil.copy2(source,snapshot/source.name)
files=[]
for path in sorted(T.rglob('*')):
 if not path.is_file() or any(part in {'__pycache__','kit_isolation','runtime','cache','tmp'} for part in path.relative_to(T).parts):continue
 rel=path.relative_to(T).as_posix()
 if rel.startswith('evidence/manual_low_speed/') and path.name in {'STATUS.json','trajectory.jsonl'}:continue
 if path.suffix in {'.pyc','.partial','.npz','.npy'} or path.name in {'monitor.log','monitor_error.log','pipeline.log','pipeline_error.log'} or path.name.startswith('ARCHIVE_') or path.name.endswith('_worker.log'):continue
 if rel in {'evidence/MONITOR_STATUS.json','evidence/MONITOR_LAST_ERROR.json','evidence/MODEL_COLLECTION.json','evidence/EVALUATION_QUEUE.json','evidence/INSPECTIONS.jsonl'} and phase=='launch':continue
 if phase=='launch' and rel.startswith(('evidence/training/','evidence/checkpoint_evals/','evidence/inspections/')):continue
 files.append(path)
for rel in ['README.md','docs/DR_TRAINING_INDEX_20261111.md','sources/local/MOD4V3_DR_TRAINING_RECORDS_20261111/README.md','sources/local/MOD4V3_DR_TRAINING_RECORDS_20261111/MODEL_REGISTRY.json']:
 if (R/rel).is_file():files.append(R/rel)
# The prior archive receipt is generated after its own commit; carry it here.
prior=T.parent/'MOD4V3_HIGH_STANCE_CONTINUE_2H_20261114'
for rel in ['evidence/PIPELINE_RECOVERY_R2_COMPLETE.json','evidence/PHYSICAL_RECOVERY_R2_COMPLETE.json','pipeline_recovery_r2.log','pipeline_recovery_r2_error.log','pipeline.log','pipeline_error.log']:
 if (prior/rel).is_file():files.append(prior/rel)
for rel in ['pipeline.log','pipeline_error.log']:
 if (T/rel).is_file():files.append(T/rel)
if phase=='complete':
 for name in ['ARCHIVE_LAUNCH.log','ARCHIVE_LAUNCH_ERROR.log','ARCHIVE_START_FOLLOWUP.log','ARCHIVE_START_FOLLOWUP_ERROR.log','ARCHIVE_FIRST5M.log','ARCHIVE_FIRST5M_ERROR.log','ARCHIVE_MANUAL_REPLAY.log','ARCHIVE_MANUAL_REPLAY_ERROR.log']:
  if (E/name).is_file():files.append(E/name)
binary[:]=[x.relative_to(R).as_posix() for x in files if x.suffix=='.pt'];text=[x.relative_to(R).as_posix() for x in files if x.suffix!='.pt']
main_before=git('ls-remote','origin','refs/heads/main').split()[0]
note=T/('FINAL_REPORT.md' if phase=='complete' else 'README.md')
sys.argv=['record_experiment.py','--id',ID,'--title','MOD4 video-supported rearward-wheel stairs40m '+phase,'--kind','training','--note-file',str(note),'--validation','One authorized2400s from frozen db6 comprehensive parent; upper-tread support verified before rearward/upward reward; low-speed0.35-0.75;30percent assisted stair starts separate from whole; old fast-stair BC disabled; fullDR/40-35-25 and retained parent/high-stance teacher kept;5m fullPT and checks; full actual status in README','--files',*text]
rec.main();head=git('rev-parse','HEAD');tag=git('rev-parse',TAG);assert git('rev-parse',TAG+'^{}')==head
git('push','--atomic','origin','HEAD','refs/tags/'+TAG)
refs={line.split()[1]:line.split()[0] for line in git('ls-remote','origin','refs/heads/mod4v1-experts-fulldr-rm70','refs/heads/main','refs/tags/'+TAG,'refs/tags/'+TAG+'^{}').splitlines()}
assert refs['refs/heads/mod4v1-experts-fulldr-rm70']==head and refs['refs/tags/'+TAG]==tag and refs['refs/tags/'+TAG+'^{}']==head
for name in binary:
 blob=git('rev-parse',head+':'+name);assert blob==git('hash-object','--no-filters',str(R/name)),name
print(json.dumps(dict(phase=phase,commit=head,tag=TAG,remote_verified=True,ordinary_full_PT_files=len(binary),main_before=main_before,main_after=refs['refs/heads/main']),indent=2),flush=True)
