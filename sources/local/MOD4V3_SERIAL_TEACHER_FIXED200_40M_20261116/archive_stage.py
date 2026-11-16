"""Freeze reports/source and index large originals; record unique launch/completion stages."""
from pathlib import Path
import sys,json,hashlib,shutil,subprocess,argparse,time
T=Path(__file__).resolve().parent;R=T.parents[2]
def sha(f):
 h=hashlib.sha256()
 with f.open('rb')as stream:
  for b in iter(lambda:stream.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def prepare(phase):
 snap=T/'evidence'/(phase+'_snapshot');snap.mkdir(parents=True,exist_ok=False)
 for folder in ['training','inspections','checkpoint_evals']:
  source=T/'evidence'/folder
  for f in sorted(source.rglob('*.json'))if source.exists()else[]:
   dest=snap/f.relative_to(T/'evidence');dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(f,dest)
 for name in ['TRAIN_LAUNCH.json','COLLECTOR_LAUNCH.json','FINISHER_LAUNCH.json','MODEL_COLLECTION.json','MONITOR_STATUS.json','MONITOR_COMPLETE.json','EVALUATION_QUEUE.json','TRAINING_STARTED_CONFIRMED.json','FINAL_STATUS.json','LOCAL_PREFLIGHT.json','UPLOADED_INPUTS.json']:
  f=T/'evidence'/name
  if f.exists():shutil.copy2(f,snap/name)
 for name in ['monitor_run.log','monitor_run_error.log']:
  f=T/name
  if f.exists():shutil.copy2(f,snap/name)
 rows=[];files=[]
 for f in sorted(T.rglob('*')):
  if not f.is_file()or '__pycache__'in f.parts or f.suffix in ['.partial','.pyc']or f.name.startswith(('ARTIFACT_INDEX_','ARCHIVE_FILES_')):continue
  rel=f.relative_to(T);is_live=rel.parts[0]=='evidence'and len(rel.parts)>1 and rel.parts[1]in ['training','inspections','checkpoint_evals']
  if is_live:continue
  eligible=f.suffix.lower()in ['.py','.md','.json','.yaml','.log']and f.name!='STEP_DIAGNOSTICS.json'and f.stat().st_size<8_000_000
  if rel.as_posix()in ['monitor_run.log','monitor_run_error.log','finish_pipeline.log','finish_pipeline_error.log']:eligible=False
  rows.append(dict(path=str(f),bytes=f.stat().st_size,sha256=sha(f),storage='git_text'if eligible else'local_original_indexed',git_path=f.relative_to(R).as_posix()if eligible else None))
  if eligible:files.append(f.relative_to(R).as_posix())
 index=T/f'ARTIFACT_INDEX_{phase}.json';index.write_text(json.dumps(dict(snapshot_epoch=time.time(),phase=phase,artifacts=rows,large_originals_retained=True),ensure_ascii=False,indent=2)+'\n',encoding='utf8');files.append(index.relative_to(R).as_posix())
 files+=['AGENTS.md','sources/local/MOD4V3_SERIAL_LQR_SKILL_TEACHER_20261116/README.md','sources/local/MOD4V3_SERIAL_LQR_SKILL_TEACHER_20261116/MEMORY_ENTRY.md']
 listing=T/f'ARCHIVE_FILES_{phase}.json';files.append(listing.relative_to(R).as_posix());files=sorted(set(files));listing.write_text(json.dumps(files,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print('ARCHIVE_PREPARED',phase,len(files),flush=True)
def record(phase):
 sys.path.insert(0,str(R/'archive_tools'));import record_experiment as rec
 original=rec.git
 def git(*args):
  if args[:2]==('add','--'):
   batch=[];length=0
   for f in args[2:]:
    if length+len(f)+3>13000 and batch:original('add','-f','--sparse','--',*batch);batch=[];length=0
    batch.append(f);length+=len(f)+3
   if batch:original('add','-f','--sparse','--',*batch)
   return ''
  return original(*args)
 rec.git=git;files=json.loads((T/f'ARCHIVE_FILES_{phase}.json').read_text());note=T/('LAUNCH_REPORT.md'if phase=='launch'else'FINAL_REPORT.md')
 sys.argv=['record_experiment','--id','serial-fixed200-teacher-40m-'+phase+'-01','--title','MOD4v3: fixed200mm native-teacher40m '+phase+'; c874 default retained','--kind','training','--note-file',str(note),'--validation','Actual native PPO/Adam updates and fixed200 cooked geometry; qualified teacher2500frames; failures retained; independent student scores separate','--files',*files,'--push'];rec.main()
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--phase',choices=['launch','complete'],required=True);p.add_argument('--record',action='store_true');a=p.parse_args();record(a.phase)if a.record else prepare(a.phase)
