from pathlib import Path
import sys,json,hashlib,datetime
T=Path(__file__).resolve().parent;X=T.parent;R=X.parents[2]
sys.path.insert(0,str(X));from common import guard,put,sha
files=[];rows=[]
for p in sorted(T.rglob('*')):
 if not p.is_file()or p.name in ['ARTIFACT_INDEX.json','ARCHIVE_FILES.json']:continue
 text=p.suffix.lower()in ['.py','.md','.json','.xml','.yaml','.log']and p.stat().st_size<5_000_000
 rows.append(dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size,storage='git_text'if text else'local_original_indexed'))
 if text:files.append(p.relative_to(R).as_posix())
put(T/'PROTECTED_VERIFICATION.json',dict(sha256=guard(),all_unchanged=True,PPO_updates=0,optimizer_updates=0))
files.append((T/'PROTECTED_VERIFICATION.json').relative_to(R).as_posix());put(T/'ARTIFACT_INDEX.json',dict(recorded_at=datetime.datetime.now().astimezone().isoformat(),artifacts=rows,PPO_updates=0,optimizer_updates=0,scope='3s paired diagnostics, not full stair scores'));files.extend([(T/'ARTIFACT_INDEX.json').relative_to(R).as_posix(),'AGENTS.md'])
sys.path.insert(0,str(R/'archive_tools'));import record_experiment as rec
original=rec.git
def git(*args):
 if args[:2]==('add','--'):
  batch=[];count=0
  for f in args[2:]:
   if count+len(f)+3>12000 and batch:original('add','-f','--sparse','--',*batch);batch=[];count=0
   batch.append(f);count+=len(f)+3
  if batch:original('add','-f','--sparse','--',*batch)
  return ''
 return original(*args)
rec.git=git
sys.argv=['record_experiment','--id','mod4v3-scut-mode-input-contrast-01','--title','MOD4v3 paired mode intervention isolates stair-conditioned startup regression','--kind','diagnostic','--note-file',str(T/'REPORT.md'),'--validation','8x3s independent paired normal/stair rollouts;0 optimizer/PPO;SCUT frozen35DMLP anddisabledFSM verified;all protectedSHA unchanged','--files',*files,'--push'];rec.main()
