"""Archive this isolated experiment; static text commits, large originals SHA-indexed."""
from pathlib import Path
import sys,json,hashlib,shutil,time,argparse
T=Path(__file__).resolve().parent;R=T.parents[2]
def sha(f):
 h=hashlib.sha256()
 with f.open('rb')as s:
  for b in iter(lambda:s.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def prepare(phase):
 snap=T/'evidence'/(phase+'_snapshot');snap.mkdir(exist_ok=False);files=[];rows=[]
 for name in ['training','checkpoint_evals','inspections']:
  root=T/'evidence'/name
  if root.exists():
   for f in root.rglob('*.json'):
    dst=snap/f.relative_to(T/'evidence');dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(f,dst)
 live={'MONITOR_STATUS.json','MODEL_COLLECTION.json','EVALUATION_QUEUE.json','INSPECTIONS.jsonl','MONITOR_LAST_ERROR.json'}
 for name in live:
  f=T/'evidence'/name
  if f.exists():shutil.copy2(f,snap/name)
 for name in ['monitor_run.log','monitor_run_error.log']:
  f=T/name
  if f.exists():shutil.copy2(f,snap/name)
 for f in sorted(T.rglob('*')):
  if not f.is_file()or '__pycache__'in f.parts or f.suffix in ['.partial','.pyc']or f.name.startswith(('ARTIFACT_INDEX_','ARCHIVE_FILES_')):continue
  rel=f.relative_to(T);dynamic=rel.parts[0]=='evidence'and((len(rel.parts)>1 and rel.parts[1]in ['training','checkpoint_evals','inspections'])or f.name in live)
  eligible=not dynamic and f.suffix.lower()in ['.py','.md','.json','.yaml','.log','.jsonl']and f.stat().st_size<5_000_000
  if rel.as_posix()in ['monitor_run.log','monitor_run_error.log']:eligible=False
  rows.append(dict(path=str(f),bytes=f.stat().st_size,sha256=sha(f),storage='git_text'if eligible else'local_original_indexed',git_path=f.relative_to(R).as_posix()if eligible else None))
  if eligible:files.append(f.relative_to(R).as_posix())
 index=T/f'ARTIFACT_INDEX_{phase}.json';index.write_text(json.dumps(dict(phase=phase,snapshot_epoch=time.time(),large_originals_retained=True,artifacts=rows),ensure_ascii=False,indent=2)+'\n',encoding='utf8');files.extend([index.relative_to(R).as_posix(),'AGENTS.md']);listing=T/f'ARCHIVE_FILES_{phase}.json';files.append(listing.relative_to(R).as_posix());listing.write_text(json.dumps(sorted(set(files)),ensure_ascii=False,indent=2)+'\n',encoding='utf8');print('ARCHIVE_PREPARED',phase,len(files),flush=True)
def record(phase):
 sys.path.insert(0,str(R/'archive_tools'));import record_experiment as rec
 base=rec.git
 def git(*args):
  if args[:2]==('add','--'):
   batch=[];length=0
   for f in args[2:]:
    if length+len(f)+3>13000 and batch:base('add','-f','--sparse','--',*batch);batch=[];length=0
    batch.append(f);length+=len(f)+3
   if batch:base('add','-f','--sparse','--',*batch)
   return ''
  return base(*args)
 rec.git=git;files=json.loads((T/f'ARCHIVE_FILES_{phase}.json').read_text());note=T/('LAUNCH_REPORT.md'if phase=='launch'else'FINAL_REPORT.md');sys.argv=['record_experiment','--id','mod4v3-fixed200-settle-cruise-10m-'+phase+'-01','--title','MOD4v3 fixed200 settle-cruise10m '+phase+'; default c874 retained','--kind','training','--note-file',str(note),'--validation','Frozen student prefix reproduction; qualified teacher recovery only; semantic mass/initial gradient; independent student assessments separate','--files',*files,'--push'];rec.main()
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--phase',choices=['launch','complete'],required=True);p.add_argument('--record',action='store_true');a=p.parse_args();record(a.phase)if a.record else prepare(a.phase)
