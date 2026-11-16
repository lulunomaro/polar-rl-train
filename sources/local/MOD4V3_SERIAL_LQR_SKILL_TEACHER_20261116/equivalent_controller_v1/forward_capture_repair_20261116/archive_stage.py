from pathlib import Path
import sys,json,hashlib,subprocess,importlib.util
P=Path(__file__).resolve().parent;R=P.parent.parents[3];NL=chr(10)
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
 return h.hexdigest()
def eligible(p):return p.suffix.lower()in('.py','.md','.json','.log')and p.name!='STEP_DIAGNOSTICS.json'and '__pycache__'not in p.parts
if '--record'not in sys.argv:
 rows=[]
 for p in sorted(P.rglob('*')):
  if not p.is_file()or p.name in ['ARTIFACT_INDEX.json','ARCHIVE_FILES.json']:continue
  rows.append(dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p),storage='git_text'if eligible(p)else'local_raw_indexed',git_path=p.relative_to(R).as_posix()if eligible(p)else None))
 (P/'ARTIFACT_INDEX.json').write_text(json.dumps(dict(artifacts=rows,self_index='This index and archive file list are recorded directly by record_experiment hashes.'),ensure_ascii=False,indent=2)+NL,encoding='utf8')
 files=[p.relative_to(R).as_posix()for p in sorted(P.rglob('*'))if p.is_file()and eligible(p)]
 extras=['AGENTS.md','sources/local/MOD4V3_SERIAL_LQR_SKILL_TEACHER_20261116/README.md','sources/local/MOD4V3_SERIAL_LQR_SKILL_TEACHER_20261116/MEMORY_ENTRY.md']+[str((P.parent/rel).relative_to(R).as_posix())for rel in ['run_teacher.py','sim/controller.py','sim/step_climb.py']]
 files=sorted(set(files+extras+[(P/'ARCHIVE_FILES.json').relative_to(R).as_posix()]))
 (P/'ARCHIVE_FILES.json').write_text(json.dumps(files,ensure_ascii=False,indent=2)+NL,encoding='utf8')
 print(json.dumps(dict(indexed=len(rows),selected=len(files),raw_mb=round(sum(q['bytes']for q in rows if q['storage']=='local_raw_indexed')/1e6,1))))
else:
 sys.path.insert(0,str(R/'archive_tools'));import record_experiment as rec
 original=rec.git
 def git(*args):
  if args[:2]==('add','--'):
   batches=[];batch=[];length=0
   for path in args[2:]:
    if length+len(path)+3>13000 and batch:batches.append(batch);batch=[];length=0
    batch.append(path);length+=len(path)+3
   if batch:batches.append(batch)
   for batch in batches:original('add','-f','--sparse','--',*batch)
   return ''
  return original(*args)
 rec.git=git
 files=json.loads((P/'ARCHIVE_FILES.json').read_text(encoding='utf8'))
 sys.argv=['record_experiment','--id','serial-capture-five-start-repair-01','--title','MOD4v3: five-start stability 5/5; retain unresolved wait loss and recoil','--kind','repair','--note-file',str(P/'REPORT.md'),'--validation','56 native teacher rollouts; final five-start stability 5/5; pre-capture traces identical; recoil remains; optimizer steps 0','--files',*files,'--push']
 rec.main()
