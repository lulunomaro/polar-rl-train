"""Archive this fixed-weight test and all real failures using the existing recorder."""
from pathlib import Path
import sys,json,hashlib
R=Path('D:/claude2/fangzhen/_mod4v2_src_20261106');B=Path(__file__).resolve().parent
sys.path.insert(0,'D:/claude2/fangzhen/tmp/step7_archive_helper');import record_experiment as rec
original=rec.git
files=[p.relative_to(R).as_posix() for p in B.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ('.pyc','.partial')]
files+=['README.md','docs/ROUGH_CURRICULUM_README_20261111.md'];binary=[f for f in files if f.endswith(('.npz','.npy','.pt'))];other=[f for f in files if f not in binary]
experiment_id='mod4-ground-stand-probe-01'
def git(*args):
 if args[0]=='add':
  records=list((R/'history/experiments').glob('*-'+experiment_id+'.json'));assert len(records)==1;record=records[0];data=json.loads(record.read_text(encoding='utf-8'))
  for f in binary:data['source_and_evidence_sha256'][f]=hashlib.sha256((R/f).read_bytes()).hexdigest()
  data['artifact_storage']='Full trajectoryNPZ, videos, screenshots, raw failures and exact executed source are ordinary Git blobs. Existing parentPT already retained in Git; no policy training or export.';record.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
  return original('add','--sparse','-f',*args[1:],*binary)
 return original(*args)
rec.git=git
sys.argv=['record_experiment.py','--id',experiment_id,'--title','Record MOD4 belly-ground stand tests and real failures','--kind','evaluation','--note-file',str(B/'REPORT.md'),'--validation','Frozen005m SHA;8 feasible leg poses,40 paired nominal/fullDR starts; explicit safety censored samples; separate posthoc height/pose and original contact score;5 powered controls; actualPhysX traces and verified videos','--files',*other]
rec.main()
