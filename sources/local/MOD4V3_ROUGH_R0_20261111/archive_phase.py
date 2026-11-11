"""Append already-produced R0 reports and full PT bytes with one phase tag."""
from pathlib import Path
import json,hashlib,subprocess,sys,argparse
ROOT=Path(r'D:/claude2/fangzhen/_mod4v2_src_20261106')
TRIAL=ROOT/'sources/local/MOD4V3_ROUGH_R0_20261111'
p=argparse.ArgumentParser();p.add_argument('phase');p.add_argument('--title',required=True);a=p.parse_args()
sys.path.insert(0,r'D:/claude2/fangzhen/tmp/step7_archive_helper')
import record_experiment as rec
original=rec.git
notes=TRIAL/'REPORT.md'
files=['README.md','docs/ROUGH_CURRICULUM_README_20261111.md','docs/DR_TRAINING_INDEX_20261111.md','docs/DR_TRAINING_RESUME_20261111.md','sources/local/MOD4V3_DR_TRAINING_RECORDS_20261111/README.md','sources/local/MOD4V3_DR_TRAINING_RECORDS_20261111/MODELS.md','sources/local/MOD4V3_DR_TRAINING_RECORDS_20261111/MODEL_REGISTRY.json']+[f.relative_to(ROOT).as_posix() for f in TRIAL.rglob('*') if f.is_file() and '__pycache__' not in f.parts and f.suffix!='.pyc']
pts=[f for f in files if f.endswith('.pt')];text=[f for f in files if not f.endswith('.pt')]
record=ROOT/'history/experiments'/('20261111-mod4-rough-r0-'+a.phase+'-01.json')
def git(*args):
 if args[0]=='add':
  value=json.loads(record.read_text(encoding='utf8'))
  for path in pts:value['source_and_evidence_sha256'][path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
  value['full_PT_storage']='User explicitly requires ordinary full PT Git blobs; historical ignore overridden only for listed PT'
  record.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
  return original('add','--sparse','-f',*args[1:],*pts)
 return original(*args)
rec.git=git
sys.argv=['record_experiment.py','--id','mod4-rough-r0-'+a.phase+'-01','--title',a.title,'--kind','evaluation','--note-file',str(notes),'--validation','Actual saved reports and complete PPO PT hashes preserved; raw failures and nominal/DR/engine distinction retained; no additional training budget','--files',*text]
rec.main()
