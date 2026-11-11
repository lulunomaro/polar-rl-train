"""Archive the realcar debug release and full binary payload through existing recorder."""
from pathlib import Path
import sys,json,hashlib
R=Path('D:/claude2/fangzhen/_mod4v2_src_20261106');B=R/'deliveries/MOD4V3_R1_005M_REALCAR_DEBUG_20261112';A=B.parent/(B.name+'.zip');receipt=B.parent/(B.name+'_VALIDATION.json')
sys.path.insert(0,'D:/claude2/fangzhen/tmp/step7_archive_helper');import record_experiment as rec
files=[p.relative_to(R).as_posix() for p in B.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ('.pyc','.partial','.obj','.exp')];files += [A.relative_to(R).as_posix(),receipt.relative_to(R).as_posix(),Path(__file__).relative_to(R).as_posix(),'README.md','docs/DR_TRAINING_INDEX_20261111.md'];binary=[f for f in files if f.endswith(('.pt','.ts','.onnx','.npz','.npy'))];text=[f for f in files if f not in binary];original=rec.git;id='mod4-realcar-debug-package-01'
def git(*args):
 if args[0]=='add':
  matches=list((R/'history/experiments').glob('*-'+id+'.json'));assert len(matches)==1;record=matches[0];data=json.loads(record.read_text(encoding='utf-8'))
  for f in binary:data['source_and_evidence_sha256'][f]=hashlib.sha256((R/f).read_bytes()).hexdigest()
  data['artifact_storage']='Full originalPT, ONNX, TorchScript, actor weights, goldens, actual plant and releaseZIP are ordinary Git blobs. Hardware calibration is explicitly unverified; no actual robot actuation or acceptance.';record.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
  return original('add','--sparse','-f',*args[1:],*binary)
 return original(*args)
rec.git=git;sys.argv=['record_experiment.py','--id',id,'--title','Deliver MOD4v3 frozen R1 policy and full electrical debug package','--kind','deployment','--note-file',str(B/'REPORT.md'),'--validation','Exact005m SHA;800 native interface vectors+4096 actor vectors;C Windows/Linux;8 ONNX closed-loop cases;1024 fast-envelope cases;cleanZIP extraction;unverified hardware gate correctly blocked;full binaries saved','--files',*text];rec.main()
