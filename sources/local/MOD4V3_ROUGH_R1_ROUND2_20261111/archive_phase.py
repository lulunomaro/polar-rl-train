"""Record the authorized R1 round2 and exact full PPO PT through the existing recorder."""
from pathlib import Path
import sys,json,hashlib,argparse
R=Path(r'D:/claude2/fangzhen/_mod4v2_src_20261106');T=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('phase');p.add_argument('--title',required=True);a=p.parse_args()
sys.path.insert(0,r'D:/claude2/fangzhen/tmp/step7_archive_helper');import record_experiment as rec
original=rec.git
mutable={'evidence/monitor.log','evidence/monitor_error.log','evidence/LATEST_PROGRESS.json'} if a.phase=='start' else set()
files=[f.relative_to(R).as_posix() for f in T.rglob('*') if f.is_file() and '__pycache__' not in f.parts and f.suffix not in ('.pyc','.partial') and f.relative_to(T).as_posix() not in mutable]
files+=['README.md','docs/ROUGH_CURRICULUM_README_20261111.md','docs/DR_TRAINING_INDEX_20261111.md','docs/DR_TRAINING_RESUME_20261111.md','sources/local/MOD4V3_DR_TRAINING_RECORDS_20261111/README.md','sources/local/MOD4V3_DR_TRAINING_RECORDS_20261111/MODELS.md','sources/local/MOD4V3_DR_TRAINING_RECORDS_20261111/MODEL_REGISTRY.json']
files=list(dict.fromkeys(files));binary=[f for f in files if f.endswith(('.pt','.npz'))];text=[f for f in files if f not in binary]
id='mod4-rough-r1-round2-'+a.phase+'-01';record=R/'history/experiments'/('20261111-'+id+'.json')
def git(*args):
 if args[0]=='add':
  data=json.loads(record.read_text(encoding='utf-8'))
  for f in binary:data['source_and_evidence_sha256'][f]=hashlib.sha256((R/f).read_bytes()).hexdigest()
  data['artifact_storage']='User requires full PT bytes committed as ordinary Git blobs; historical binary ignore overridden for explicit artifacts only. Active monitor streams excluded at start and included at completion.'
  record.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
  return original('add','--sparse','-f',*args[1:],*binary)
 return original(*args)
rec.git=git
sys.argv=['record_experiment.py','--id',id,'--title',a.title,'--kind','training' if a.phase=='start' else 'evaluation','--note-file',str(T/'REPORT.md'),'--validation','Exact parentSHA; original -1.5e² and exponent1.2; full PPO/terrain resume; full PT/checkpoints and actual evidence; compare frozen-weight conditions without new graduation thresholds','--files',*text]
rec.main()
