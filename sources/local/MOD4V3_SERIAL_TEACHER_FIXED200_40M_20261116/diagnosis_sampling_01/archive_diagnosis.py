from pathlib import Path
import sys,json,hashlib
D=Path(__file__).resolve().parent;T=D.parent;R=T.parents[2]
if '--record'not in sys.argv:
 rows=[];files=[]
 for f in sorted(D.rglob('*')):
  if not f.is_file()or f.name in ['ARTIFACT_INDEX.json','ARCHIVE_FILES.json']or '__pycache__'in f.parts:continue
  eligible=f.suffix in ['.py','.md','.json','.log'];rows.append(dict(path=str(f),bytes=f.stat().st_size,sha256=hashlib.sha256(f.read_bytes()).hexdigest(),storage='git_text'if eligible else'local_raw_indexed'))
  if eligible:files.append(f.relative_to(R).as_posix())
 (D/'ARTIFACT_INDEX.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf8');files+=[(D/'ARTIFACT_INDEX.json').relative_to(R).as_posix(),(D/'ARCHIVE_FILES.json').relative_to(R).as_posix(),'AGENTS.md',(T/'README.md').relative_to(R).as_posix(),(T/'diagnosis_retention_01/REPORT.md').relative_to(R).as_posix(),'sources/local/MOD4V3_SERIAL_LQR_SKILL_TEACHER_20261116/MEMORY_ENTRY.md'];files=sorted(set(files));(D/'ARCHIVE_FILES.json').write_text(json.dumps(files,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print('DIAGNOSTIC_ARCHIVE_PREPARED',len(files))
else:
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
 rec.git=git;files=json.loads((D/'ARCHIVE_FILES.json').read_text());sys.argv=['record_experiment','--id','serial-fixed200-sampling-audit-01','--title','Audit underweighted contact transition and state coverage after fixed20040m close','--kind','diagnostic','--note-file',str(D/'REPORT.md'),'--validation','Frozen dataset semantic sampling and per-phase errors; existing student rollouts;0 new rollouts/optimizer; actual40m safe close; c874 default unchanged','--files',*files,'--push'];rec.main()
