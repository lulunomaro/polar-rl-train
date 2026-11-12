"""Record the user-authorized complete snapshot, including actual PT/data bytes."""
from pathlib import Path
import sys,json,hashlib,tempfile,subprocess
P=Path(__file__).resolve().parents[1];R=P.parents[1]
assert (R/'.git').exists()
sys.path.insert(0,str(R.parent/'tmp/step7_archive_helper'))
import record_experiment as rec
original=rec.git
ID='mod4-best-manual-stairs-01';TAG='trial-20261112-'+ID
record=R/'history/experiments'/('20261112-'+ID+'.json')
def included(f):
 if not f.is_file() or '__pycache__' in f.parts or f.suffix in {'.pyc','.partial'}:return False
 rel=f.relative_to(P).as_posix()
 if rel.startswith('viewer/mesh/') or (rel.startswith('viewer/scene_') and rel.endswith('.xml')):return False
 if rel.startswith('viewer/') and ('_hf' in f.name or f.name.endswith('STATUS.json') or f.suffix=='.log' or f.name=='full_map_scene.xml'):return False
 return True
paths=[f for f in P.rglob('*') if included(f)]
# The payload checksum list precedes the Git sync receipt appended after upload.
manifest=P/'SHA256SUMS.txt'
manifest.write_text(''.join(hashlib.sha256(f.read_bytes()).hexdigest()+'  '+f.relative_to(P).as_posix()+'\n' for f in sorted(paths) if f!=manifest),encoding='utf8')
paths=[f for f in P.rglob('*') if included(f)]
files=[f.relative_to(R).as_posix() for f in paths]+['README.md','docs/DR_TRAINING_INDEX_20261111.md']
binary=[f for f in files if Path(f).suffix.lower() in {'.pt','.pth','.onnx','.npz','.npy'}]
text=[f for f in files if f not in binary]
def wrapped(*args):
 if args[0]=='add':
  data=json.loads(record.read_text(encoding='utf8'))
  for f in binary:data['source_and_evidence_sha256'][f]=hashlib.sha256((R/f).read_bytes()).hexdigest()
  data['artifact_storage']='User explicitly requested the currently playing full PT and all training/replay data in Git. Binary PT and required source tile arrays are stored as ordinary full blobs; no LFS pointer or external-path-only substitute.'
  data['selected_model_sha256']='7cc1fc6deeee3d3aba8ae8d2da31dce200079fb229a145f1cbb1cd3bfabea103'
  record.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
  names=[x for x in args[1:] if x!='--']+binary
  with tempfile.NamedTemporaryFile(mode='wb',prefix='nov12-named-model-git-',dir=R.parent/'tmp',delete=False) as stream:
   for name in names:stream.write(name.encode('utf8')+b'\0')
   pathspec=Path(stream.name)
  try:return original('--literal-pathspecs','-c','http.proxy=http://127.0.0.1:7897','-c','http.sslVerify=true','add','--sparse','-f','--pathspec-from-file='+str(pathspec),'--pathspec-file-nul')
  finally:pathspec.unlink()
 return original('-c','http.proxy=http://127.0.0.1:7897','-c','http.sslVerify=true',*args)
rec.git=wrapped
sys.argv=['record_experiment.py','--id',ID,'--title','Archive Nov12 selected best model, full training recipe and manual stair replay','--kind','evaluation','--note-file',str(P/'ARCHIVE_NOTE.md'),'--validation','Same full120m PT/iteration24482; 0.365m and0.40m height ramps plus2.2m/s nominal run-up climb two16.5cm stairs; portable package reproduces ascent and platform stop without reset; original failures and fullDR PhysX results retained; manual keyboard/height reaches actual actor input','--files',*text]
rec.main()
source=wrapped('rev-parse','HEAD')
model='deliveries/MOD4V3_BEST_MANUAL_STAIRS_20261112/model/training_checkpoint.pt'
raw=subprocess.run(['git','-C',str(R),'show',source+':'+model],capture_output=True,check=True).stdout
assert len(raw)==(R/model).stat().st_size and hashlib.sha256(raw).hexdigest()=='7cc1fc6deeee3d3aba8ae8d2da31dce200079fb229a145f1cbb1cd3bfabea103'
print(json.dumps(dict(commit=source,tag=TAG,files=len(files),full_model_bytes=len(raw),model_sha256=hashlib.sha256(raw).hexdigest(),ordinary_PT_blob=True)),flush=True)
