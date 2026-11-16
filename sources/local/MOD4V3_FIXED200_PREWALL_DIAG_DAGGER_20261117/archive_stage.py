"""Archive all real attempts and reports; large originals retained by SHA index."""
from pathlib import Path
import json,hashlib,sys,argparse,datetime
T=Path(__file__).resolve().parent;R=T.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def prepare():
 rows=[];files=[]
 for p in sorted(T.rglob('*')):
  if not p.is_file()or '__pycache__'in p.parts or p.name in ['ARTIFACT_INDEX.json','ARCHIVE_FILES.json']:continue
  text=p.suffix.lower()in ['.py','.md','.json','.yaml','.xml','.log','.jsonl','.txt']and p.stat().st_size<5_000_000
  rows.append(dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p),storage='git_text'if text else'local_original_indexed',git_path=p.relative_to(R).as_posix()if text else None))
  if text:files.append(p.relative_to(R).as_posix())
 idx=T/'ARTIFACT_INDEX.json';idx.write_text(json.dumps(dict(recorded_at=datetime.datetime.now().astimezone().isoformat(),artifacts=rows,all_large_originals_retained=True,failed_attempts_included=True,PPO_updates=0,offline_fit_steps=64),ensure_ascii=False,indent=2)+'\n',encoding='utf-8');files.extend([idx.relative_to(R).as_posix(),'AGENTS.md',(T/'ARCHIVE_FILES.json').relative_to(R).as_posix()]);(T/'ARCHIVE_FILES.json').write_text(json.dumps(sorted(set(files)),ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print('ARCHIVE_PREPARED',len(files))
def record():
 sys.path.insert(0,str(R/'archive_tools'));import record_experiment as rec
 original=rec.git
 def git(*args):
  if args[:2]==('add','--'):
   batch=[];size=0
   for p in args[2:]:
    if size+len(p)+3>12000 and batch:original('add','-f','--sparse','--',*batch);batch=[];size=0
    batch.append(p);size+=len(p)+3
   if batch:original('add','-f','--sparse','--',*batch)
   return ''
  return original(*args)
 rec.git=git
 files=json.loads((T/'ARCHIVE_FILES.json').read_text(encoding='utf-8'))
 sys.argv=['record_experiment','--id','mod4v3-fixed200-prewall-diagnosis-01','--title','MOD4v3 prewall diagnosis:24of30 teacher recoveries, offline64 probe rejected','--kind','diagnostic','--note-file',str(T/'REPORT.md'),'--validation','0 PPO; 10 archived rollouts audited; exact live prefixes; 30 teacher attempts/24 qualified; normalized35D and offline gradients;64 offline Adam steps; independent student0of5; all protected SHA unchanged','--files',*files,'--push']
 rec.main()
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--record',action='store_true');a=p.parse_args();record()if a.record else prepare()
