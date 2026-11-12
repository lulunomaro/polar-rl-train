"""Record source-only diagnosis and full original replay data, without a training run."""
from pathlib import Path
import sys,json,hashlib,tempfile
T=Path(__file__).resolve().parent;R=T.parents[2];ID='mod4-stair-speed-causal-audit-01';TAG='trial-20261112-'+ID
sys.path.insert(0,str(R.parent/'tmp/step7_archive_helper'));import record_experiment as rec
original=rec.git;record=R/'history/experiments'/('20261112-'+ID+'.json')
files=[f.relative_to(R).as_posix() for f in T.rglob('*') if f.is_file() and '__pycache__' not in f.parts and f.suffix not in ('.pyc','.partial')]
files+=['README.md','docs/DR_TRAINING_INDEX_20261111.md','sources/local/MOD4V3_SCUT_STAIR_LIFT_20M_20261112/README.md']
binary=[p for p in files if Path(p).suffix.lower() in ('.npz','.npy','.pt','.pth')];text=[p for p in files if p not in binary]
def git(*args):
 if args[0]=='add':
  data=json.loads(record.read_text(encoding='utf8'))
  for file in binary:data['source_and_evidence_sha256'][file]=hashlib.sha256((R/file).read_bytes()).hexdigest()
  data['artifact_storage']='Full original diagnostic NPZ trajectories stored as ordinary Git blobs; checkpoints already stored in earlier authorized full-PT trial. No source/reward/plant/PT modified and no optimizer constructed.'
  record.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
  names=[s for s in args[1:] if s!='--']+binary
  with tempfile.NamedTemporaryFile(mode='wb',prefix='speed-audit-git-',dir=R.parent/'tmp',delete=False) as f:
   for name in names:f.write(name.encode('utf8')+b'\0')
   spec=Path(f.name)
  try:return original('--literal-pathspecs','-c','http.proxy=http://127.0.0.1:7897','-c','http.sslVerify=true','add','--sparse','-f','--pathspec-from-file='+str(spec),'--pathspec-file-nul')
  finally:spec.unlink()
 return original('-c','http.proxy=http://127.0.0.1:7897','-c','http.sslVerify=true',*args)
rec.git=git
sys.argv=['record_experiment.py','--id',ID,'--title','Diagnose nominal forward overspeed with93frozen replays and leg-wheel channel swaps','--kind','diagnostic','--note-file',str(T/'REPORT.md'),'--validation','93frozen nominal MuJoCo cases,0resets,maxclosure0.100858mm; exact2.5/10/20ms; control-output swaps identify leg branch; common-input wheel target nearunchanged; highheight improves/lowheight regresses; square penalty intact; history and reward math retained; nativefullDR and PPO ablation not performed; no training','--files',*text]
rec.main();print(json.dumps(dict(commit=git('rev-parse','HEAD'),tag=TAG,files=len(files),binary_full_trajectory_files=binary)),flush=True)
