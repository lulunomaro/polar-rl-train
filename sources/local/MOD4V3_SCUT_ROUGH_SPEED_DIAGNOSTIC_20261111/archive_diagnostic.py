"""Archive this diagnostic with exact reference PT and replay raw bytes."""
from pathlib import Path
import json,hashlib,sys
ROOT=Path(r'D:/claude2/fangzhen/_mod4v2_src_20261106');TRIAL=Path(__file__).resolve().parent
sys.path.insert(0,r'D:/claude2/fangzhen/tmp/step7_archive_helper');import record_experiment as rec
original=rec.git
files=[p.relative_to(ROOT).as_posix() for p in TRIAL.rglob('*') if p.is_file() and p.suffix not in ('.pyc','.partial') and '__pycache__' not in p.parts]
files+=['docs/ROUGH_CURRICULUM_README_20261111.md']
binaries=[p for p in files if p.endswith(('.pt','.npz'))];text=[p for p in files if p not in binaries]
record=ROOT/'history/experiments/20261111-mod4-scut-rough-speed-diagnostic-01.json'
def git(*args):
 if args[0]=='add':
  value=json.loads(record.read_text(encoding='utf8'))
  for path in binaries:value['source_and_evidence_sha256'][path]=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
  value['artifact_storage']='Complete original SCUT PT and raw replay NPZ retained as ordinary Git blobs; previous MOD4 PT already archived by exact SHA.'
  record.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
  return original('add','--sparse','-f',*args[1:],*binaries)
 return original(*args)
rec.git=git
sys.argv=['record_experiment.py','--id','mod4-scut-rough-speed-diagnostic-01','--title','MOD4 measure SCUT reference policy transfer and current fullDR Rough speed errors','--kind','diagnostic','--note-file',str(TRIAL/'REPORT.md'),'--validation','Both frozen-weight level0/3 replays complete with saved raw endpoints, matched DR, pre-reset masks and actual velocity metrics; no optimizer or training; reference transfer limitations explicit','--files',*text]
rec.main()
