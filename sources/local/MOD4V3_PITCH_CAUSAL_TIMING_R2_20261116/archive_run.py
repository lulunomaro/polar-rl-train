"""Archive new bounded40m stage; full PT blobs and immutable report snapshots via7897."""
from pathlib import Path
import argparse,datetime,hashlib,json,shutil,sys,tempfile
T=Path(__file__).resolve().parent;R=T.parents[2];E=T/'evidence'
p=argparse.ArgumentParser();p.add_argument('--phase',choices=['queued','launch','followup','fivemin-eval','reward-catalog','evaluation-repair','fivemin-eval','reward-catalog','complete','closure'],required=True);phase=p.parse_args().phase
sys.path.insert(0,str(R.parent/'tmp/step7_archive_helper'));import record_experiment as rec
original=rec.git;NET=('-c','http.proxy=http://127.0.0.1:7897','-c','http.sslVerify=true');binary=[]
date=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y%m%d');ID='pitch-causal-timing-r2-'+phase+'-01';TAG='trial-'+date+'-'+ID;record=R/'history/experiments'/(date+'-'+ID+'.json')
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
 snapshot=E/('launch_snapshot' if phase=='launch' else 'checkpoint20m_snapshot');snapshot.mkdir(exist_ok=False)
 for source in (E/'training').glob('*.json'):
  if source.name in ['LATEST_PROGRESS.json','FIRST_UPDATE.json','RESTORE.json','STARTUP.json','PPO_EFFECTIVE.json','ACTOR_UPDATE_SCOPE.json','TEACHER_KEEP_SCOPE.json','TEACHER_RETENTION_STARTUP.json'] or (phase=='checkpoint20m' and source.name.startswith('PERIODIC_020')):
   shutil.copy2(source,snapshot/source.name)
if phase=='checkpoint20m':
 evaluation=E/'checkpoint_evals/model_020m';assert json.loads((evaluation/'EVALUATION.json').read_text())['complete']
 shutil.copytree(evaluation,snapshot/'checkpoint_evaluation')
 for file in (E/'inspections').glob('INSPECTION_020M.json'):shutil.copy2(file,snapshot/file.name)
if phase in ('followup','fivemin-eval'):
 snapshot=E/(phase+'_snapshot');snapshot.mkdir(exist_ok=False)
 for source in (E/'training').glob('*.json'):shutil.copy2(source,snapshot/source.name)
if phase in ('followup','fivemin-eval'):
 source=E/'checkpoint_evals/model_005m'
 if (source/'EVALUATION.json').exists() and json.loads((source/'EVALUATION.json').read_text()).get('complete'):
  shutil.copytree(source,snapshot/'model_005m_evaluation')
if phase=='evaluation-repair':
 snapshot=E/'evaluation_repair_snapshot';snapshot.mkdir(exist_ok=False)
 for name in ['model_035m','model_035m_importfix01']:
  shutil.copytree(E/'checkpoint_evals'/name,snapshot/name)
 for name in ['PERIODIC_035M.json','RESTORE.json','PPO_EFFECTIVE.json','LATEST_PROGRESS.json']:
  shutil.copy2(E/'training'/name,snapshot/name)
# Keep NumPy originals in place and index their exact bytes; PTs remain ordinary Git blobs.
numpy_artifacts=[dict(path=x.relative_to(R).as_posix(),bytes=x.stat().st_size,sha256=hashlib.sha256(x.read_bytes()).hexdigest())for x in T.rglob('*')if x.is_file()and x.suffix in {'.npz','.npy'}and not any(v in {'__pycache__','cache','runtime'}for v in x.relative_to(T).parts)]
if numpy_artifacts:(E/('NUMPY_ARTIFACTS_'+phase+'.json')).write_text(json.dumps(dict(artifacts=numpy_artifacts,storage='Originals retained locally; complete PTs are committed separately'),indent=2)+'\n',encoding='utf8')
if phase=='complete':
 final=json.loads((E/'training/FINAL.json').read_text());plan=json.loads((T/'PLAN.json').read_text());aggregate=plan['cumulative_training_seconds_before']+final['elapsed_seconds'];note='2026-11-16 MOD4v3俯仰修复分段40分钟轮结束：R2实际 '+str(round(final['elapsed_seconds'],3))+'秒；两段合计 '+str(round(aggregate,3))+'秒；综合默认保持db6，结果见 '+(T/'FINAL_REPORT.md').relative_to(R).as_posix()+'。'
 for rel in ['README.md','docs/DR_TRAINING_INDEX_20261111.md']:
  path=R/rel
  if note not in path.read_text(encoding='utf8'):
   with path.open('a',encoding='utf8')as out:out.write('\n'+note+'\n')
files=[]
for path in sorted(T.rglob('*')):
 if not path.is_file() or any(part in {'__pycache__','kit_isolation','runtime','cache','tmp'} for part in path.relative_to(T).parts):continue
 rel=path.relative_to(T).as_posix()
 if rel.startswith('evidence/manual_low_speed/') and path.name in {'STATUS.json','trajectory.jsonl'}:continue
 if path.suffix in {'.pyc','.partial','.npz','.npy'} or path.name in {'monitor.log','monitor_error.log','pipeline.log','pipeline_error.log'} or path.name.startswith('ARCHIVE_') or path.name.endswith('_worker.log'):continue
 if rel in {'evidence/MONITOR_STATUS.json','evidence/MONITOR_LAST_ERROR.json','evidence/MODEL_COLLECTION.json','evidence/EVALUATION_QUEUE.json','evidence/INSPECTIONS.jsonl'} and phase in ('queued','launch','followup','fivemin-eval','reward-catalog','evaluation-repair'):continue
 if phase in ('queued','launch','followup','fivemin-eval','reward-catalog','evaluation-repair') and rel.startswith(('evidence/training/','evidence/checkpoint_evals/','evidence/inspections/')):continue
 files.append(path)
for rel in ['README.md','docs/DR_TRAINING_INDEX_20261111.md']:
 if (R/rel).is_file():files.append(R/rel)
for rel in ['pipeline.log','pipeline_error.log','pipeline_recovery_r1.log','pipeline_recovery_r1_error.log']:
 if (T/rel).is_file():files.append(T/rel)
if phase in ('complete','closure'):
 for name in ['ARCHIVE_LAUNCH.log','ARCHIVE_LAUNCH_ERROR.log','ARCHIVE_START_FOLLOWUP.log','ARCHIVE_START_FOLLOWUP_ERROR.log','ARCHIVE_FIRST5M.log','ARCHIVE_FIRST5M_ERROR.log','ARCHIVE_MANUAL_REPLAY.log','ARCHIVE_MANUAL_REPLAY_ERROR.log','ARCHIVE_STRENGTHEN_FOLLOWUP.log','ARCHIVE_STRENGTHEN_FOLLOWUP_ERROR.log','ARCHIVE_EVALUATION_REPAIR.log','ARCHIVE_EVALUATION_REPAIR_ERROR.log']:
  if (E/name).is_file():files.append(E/name)
files.append(R/'AGENTS.md')
binary[:]=[x.relative_to(R).as_posix() for x in files if x.suffix=='.pt'];text=[x.relative_to(R).as_posix() for x in files if x.suffix!='.pt']
main_before=git('ls-remote','origin','refs/heads/main').split()[0]
note=T/('FINAL_REPORT.md' if phase in ('complete','closure') else 'README.md')
sys.argv=['record_experiment.py','--id',ID,'--title','MOD4v3 causal pitch prediction repair '+phase,'--kind','training','--note-file',str(note),'--validation','Same original2400s authorization across1019s phase1 and1380s R2 cap; full PPO restored from phase1 final; actual SDK reward-age mismatch and float32 boundary fixed using issuance clock/integer50Hz ticks; frozen db6 remains default; 300s complete PPO checkpoints and original fixed pitch/flat60/stairs/descent suites; preserve2048 mixed tasks/fullDR/35-78-6/2mm and motor envelopes; no promotion inferred','--files',*text]
rec.main();head=git('rev-parse','HEAD');tag=git('rev-parse',TAG);assert git('rev-parse',TAG+'^{}')==head
git('push','--atomic','origin','HEAD','refs/tags/'+TAG)
refs={line.split()[1]:line.split()[0] for line in git('ls-remote','origin','refs/heads/mod4v1-experts-fulldr-rm70','refs/heads/main','refs/tags/'+TAG,'refs/tags/'+TAG+'^{}').splitlines()}
assert refs['refs/heads/mod4v1-experts-fulldr-rm70']==head and refs['refs/tags/'+TAG]==tag and refs['refs/tags/'+TAG+'^{}']==head
for name in binary:
 blob=git('rev-parse',head+':'+name);assert blob==git('hash-object','--no-filters',str(R/name)),name
print(json.dumps(dict(phase=phase,commit=head,tag=TAG,remote_verified=True,ordinary_full_PT_files=len(binary),main_before=main_before,main_after=refs['refs/heads/main']),indent=2),flush=True)
