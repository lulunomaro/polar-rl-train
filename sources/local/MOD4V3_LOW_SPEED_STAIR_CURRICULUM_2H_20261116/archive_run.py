"""Archive this isolated training stage with full PT blobs and pinned evidence."""
from pathlib import Path
import sys,json,datetime,tempfile,hashlib,argparse,shutil
T=Path(__file__).resolve().parent;R=T.parents[2];E=T/'evidence'
p=argparse.ArgumentParser();p.add_argument('--phase',choices=['setup','contract-correction','launch','complete','followup'],required=True);phase=p.parse_args().phase
sys.path.insert(0,str(R.parent/'tmp/step7_archive_helper'));import record_experiment as rec
original=rec.git;NET=('-c','http.proxy=http://127.0.0.1:7897','-c','http.sslVerify=true');binary=[]
date=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y%m%d');ID='low-speed-stair-curriculum-2h-'+phase+'-01';tag='trial-'+date+'-'+ID;record=R/'history/experiments'/(date+'-'+ID+'.json')
def git(*args):
 if args[0]=='add':
  info=json.loads(record.read_text())
  for name in binary:info['source_and_evidence_sha256'][name]=hashlib.sha256((R/name).read_bytes()).hexdigest()
  info['artifact_storage']='Complete ordinary PT blobs; raw NumPy/runtime originals retained with SHA indices';record.write_text(json.dumps(info,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
  names=[v for v in args[1:]if v!='--']+binary
  with tempfile.NamedTemporaryFile(mode='wb',dir=R.parent/'tmp',delete=False,prefix='single-step-add-')as f:
   for name in dict.fromkeys(names):f.write(name.encode('utf8')+b'\0')
   path=Path(f.name)
  try:return original('--literal-pathspecs',*NET,'add','--sparse','-f','--pathspec-from-file='+str(path),'--pathspec-file-nul')
  finally:path.unlink()
 if args[0]=='tag'and'-m'in args:
  i=args.index('-m')
  with tempfile.NamedTemporaryFile(mode='w',encoding='utf8',newline='\n',dir=R.parent/'tmp',delete=False,prefix='single-step-tag-')as f:f.write(args[i+1]);path=Path(f.name)
  try:return original(*NET,*args[:i],'-F',str(path),*args[i+2:])
  finally:path.unlink()
 return original(*NET,*args)
rec.git=git;branch=git('branch','--show-current');assert branch=='mod4v1-experts-fulldr-rm70';assert not git('diff','--cached','--name-only')
main_before=git('ls-remote','origin','refs/heads/main').split()[0]
if not git('tag','--list',tag):
 snapshot=E/'snapshots'/phase;snapshot.mkdir(parents=True,exist_ok=True)
 for folder in ['training','inspections']:
  source=E/folder
  if source.exists():shutil.copytree(source,snapshot/folder,dirs_exist_ok=True,ignore=shutil.ignore_patterns('*.partial'))
 for name in ['monitor_run.log','monitor_run_error.log','finish_pipeline.log','finish_pipeline_error.log']:
  if(T/name).exists():shutil.copy2(T/name,snapshot/name)
 raw=[]
 for q in sorted(T.rglob('*')):
  if phase in ('setup','launch')and 'checkpoint_evals'in q.parts:continue
  if q.is_file()and q.suffix in {'.npz','.npy','.msh'}and not any(v in {'cache','runtime','kit_isolation'}for v in q.parts):
   raw.append(dict(path=str(q),bytes=q.stat().st_size,sha256=hashlib.sha256(q.read_bytes()).hexdigest(),storage='local original indexed; no large binary copy'))
 (E/'RAW_ARTIFACT_INDEX.json').write_text(json.dumps(raw,indent=2)+'\n',encoding='utf8')
 files=[]
 for q in sorted(T.rglob('*')):
  if not q.is_file():continue
  parts=q.relative_to(T).parts;rel=q.relative_to(T).as_posix()
  if any(part in {'__pycache__','kit_isolation','cache','tmp','runtime'}for part in parts)or q.suffix in {'.pyc','.partial','.npz','.npy','.msh'}:continue
  if q.name.startswith('ARCHIVE_')and q.name.endswith('.log'):continue
  if q.parent==T and q.name.endswith('.log'):continue
  if phase in ('setup','launch','followup')and(rel.startswith(('evidence/training/','evidence/inspections/'))or q.name in {'MONITOR_STATUS.json','MODEL_COLLECTION.json','EVALUATION_QUEUE.json','INSPECTIONS.jsonl'}):continue
  if phase in ('setup','launch')and rel.startswith('evidence/checkpoint_evals/'):continue
  if phase=='followup'and rel.startswith('evidence/checkpoint_evals/'):
   evaluation=E/'checkpoint_evals'/parts[2]/'EVALUATION.json'
   if not evaluation.exists()or not json.loads(evaluation.read_text()).get('complete'):continue
  if q.name.endswith('_evaluation_worker.log')and phase in ('setup','launch','followup'):continue
  files.append(q)
 for rel in ['AGENTS.md','docs/DR_TRAINING_INDEX_20261111.md','docs/NUMERICAL_AUDIT_AND_TRAINING_GUARDS_20261021.md']:
  if(R/rel).exists():files.append(R/rel)
 binary[:]=[q.relative_to(R).as_posix()for q in files if q.suffix=='.pt'];text=[q.relative_to(R).as_posix()for q in files if q.suffix!='.pt']
 sys.argv=['record_experiment.py','--id',ID,'--title','MOD4v3 per-env low-speed single-step curriculum two hours '+phase,'--kind','training','--note-file',str(T/('FINAL_REPORT.md'if phase=='complete'else'README.md')),'--validation','User originalNov9/10 explicitly cancelled2mm reset:diagnostic only,no reward,no batch stop;originalTGS32/4 and2.5ms restored;existing numerical,mimic,nonfinite,full-save and>1m catastrophe per-env protections retained; current c874 iter25362 student and retained teacher verified;35/78/6 and motors/fullDR/timing unchanged;per-env5to20cm course implemented;all obsolete gate/solver probes preserved;no PPO has launched and7200s budget unused during user-requested contract review','--files',*text]
 rec.main()
commit=git('rev-parse',tag+'^{}');assert git('rev-parse','HEAD')==commit
git('push','--atomic','origin','HEAD','refs/tags/'+tag)
refs={line.split()[1]:line.split()[0]for line in git('ls-remote','origin','refs/heads/'+branch,'refs/heads/main','refs/tags/'+tag,'refs/tags/'+tag+'^{}').splitlines()}
assert refs['refs/heads/'+branch]==commit and refs['refs/tags/'+tag+'^{}']==commit and refs['refs/tags/'+tag]==git('rev-parse',tag)and refs['refs/heads/main']==main_before
for name in binary:assert git('rev-parse',commit+':'+name)==git('hash-object','--no-filters',str(R/name))
print(json.dumps(dict(phase=phase,commit=commit,tag=tag,remote_verified=True,complete_PT_files=len(binary)),indent=2),flush=True)
