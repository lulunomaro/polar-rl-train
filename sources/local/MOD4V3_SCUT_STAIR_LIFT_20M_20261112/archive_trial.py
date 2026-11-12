"""Archive this authorized20m experiment, full checkpoint bytes and all results."""
from pathlib import Path
import sys,json,hashlib,tempfile,subprocess
T=Path(__file__).resolve().parent;R=T.parents[2]
sys.path.insert(0,str(R.parent/'tmp/step7_archive_helper'));import record_experiment as rec
original=rec.git;ID='mod4-stair-lift-20m-01';TAG='trial-20261112-'+ID
record=R/'history/experiments'/('20261112-'+ID+'.json')
mutable={'evidence/monitor.log','evidence/monitor_error.log','evidence/LATEST_PROGRESS.json'}
files=[p.relative_to(R).as_posix() for p in T.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ('.pyc','.partial') and p.relative_to(T).as_posix() not in mutable]
files+=['README.md','docs/DR_TRAINING_INDEX_20261111.md','docs/ROUGH_CURRICULUM_README_20261111.md','sources/local/MOD4V3_DR_TRAINING_RECORDS_20261111/README.md','sources/local/MOD4V3_DR_TRAINING_RECORDS_20261111/MODELS.md','sources/local/MOD4V3_DR_TRAINING_RECORDS_20261111/MODEL_REGISTRY.json']
binary=[p for p in files if Path(p).suffix.lower() in ('.pt','.npz','.npy','.pth','.onnx')];text=[p for p in files if p not in binary]
def git(*args):
 if args[0]=='add':
  data=json.loads(record.read_text(encoding='utf8'))
  for p in binary:data['source_and_evidence_sha256'][p]=hashlib.sha256((R/p).read_bytes()).hexdigest()
  data['artifact_storage']='User explicitly requires every saved complete PT stored as ordinary full Git blobs, plus source, recipe, reports and failed original evidence. No frozen-best replacement inferred.'
  record.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
  names=[x for x in args[1:] if x!='--']+binary
  with tempfile.NamedTemporaryFile(mode='wb',prefix='stair-lift-git-',dir=R.parent/'tmp',delete=False) as stream:
   for name in names:stream.write(name.encode('utf8')+b'\0')
   spec=Path(stream.name)
  try:return original('--literal-pathspecs','-c','http.proxy=http://127.0.0.1:7897','-c','http.sslVerify=true','add','--sparse','-f','--pathspec-from-file='+str(spec),'--pathspec-file-nul')
  finally:spec.unlink()
 return original('-c','http.proxy=http://127.0.0.1:7897','-c','http.sslVerify=true',*args)
rec.git=git
sys.argv=['record_experiment.py','--id',ID,'--title','Record20m stair-height-guidance continuation and paired replay results','--kind','training','--note-file',str(T/'REPORT.md'),'--validation','Exact7cc1 parent full PPO restore;1200s authorized limit, actual635.524s last confirmed; first/5m/10m full PT SHA/readback;2.5ms timing and2mm per-env guard; nominal MuJoCo comparisons completed;15/20/final and nativefullDR explicitly pending SSH; original failures preserved; no promotion','--files',*text]
rec.main();commit=git('rev-parse','HEAD');weights={}
for p in (T/'weights').glob('*.pt'):
 name=p.relative_to(R).as_posix();blob=subprocess.run(['git','-C',str(R),'show',commit+':'+name],capture_output=True,check=True).stdout;expected=hashlib.sha256(p.read_bytes()).hexdigest();assert hashlib.sha256(blob).hexdigest()==expected and len(blob)==p.stat().st_size;weights[p.name]=dict(bytes=len(blob),sha256=expected)
print(json.dumps(dict(commit=commit,tag=TAG,files=len(files),full_PT_blobs=weights)),flush=True)
