"""Archive the completed R1 startup/material diagnosis and immutable viewer snapshot."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(r'D:/claude2/fangzhen/_mod4v2_src_20261106');TRIAL=Path(__file__).resolve().parent
sys.path.insert(0,r'D:/claude2/fangzhen/tmp/step7_archive_helper');import record_experiment as rec
original=rec.git
mutable={'evidence/VIEWER.stdout.log','evidence/VIEWER.stderr.log','evidence/VIEWER_LATEST.json','viewer_generated_scene.xml'}
files=[p.relative_to(ROOT).as_posix() for p in TRIAL.rglob('*') if p.is_file() and p.suffix not in ('.pyc','.partial') and '__pycache__' not in p.parts and p.relative_to(TRIAL).as_posix() not in mutable]
files+=['docs/ROUGH_CURRICULUM_README_20261111.md','docs/DR_TRAINING_INDEX_20261111.md','docs/DR_TRAINING_RESUME_20261111.md']
binaries=[p for p in files if p.endswith(('.pt','.npz'))];text=[p for p in files if p not in binaries]
record=ROOT/'history/experiments/20261111-mod4-rough-start-material-diag-01.json'
def git(*args):
 if args[0]=='add':
  value=json.loads(record.read_text(encoding='utf8'))
  for path in binaries:value['source_and_evidence_sha256'][path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
  value['artifact_storage']='Exact raw NPZ kept as ordinary Git blobs. Referenced full MOD4 PT already preserved in prior commits; no new policy was trained. Live mutable viewer outputs excluded; immutable snapshot retained.'
  record.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
  return original('add','--sparse','-f',*args[1:],*binaries)
 return original(*args)
rec.git=git
sys.argv=['record_experiment.py','--id','mod4-rough-start-material-diag-01','--title','MOD4 isolate Rough slope start and wheel friction effects; preserve original R1 reward plan','--kind','diagnostic','--note-file',str(TRIAL/'REPORT.md'),'--validation','Two 2880env frozen-policy 5s paired runs completed; numerical0; exact raw endpoints/DR inputs/source hashes retained; wheel-friction-only input equality verified; next R1 -1.5e2 recommendation recorded but not launched; MuJoCo smoke failures retained','--files',*text]
rec.main()
