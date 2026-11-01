from pathlib import Path
import ast,hashlib,json,time
N=Path(__file__).resolve().parent;T=N.parent;B=T/'D435I_RAY_DEPTH_USD_MESH_BINDING_V257_20261101';S=N/'source';R=N/'reports';S.mkdir(exist_ok=False);R.mkdir(exist_ok=False)
def put(p,x):
 with p.open('x',encoding='utf8')as f:json.dump(x,f,indent=2,allow_nan=False)
for p in sorted((B/'source').glob('*.py'))+[B/'run_ROOT257_NEW240_mean_regression_once.py']:
 s=p.read_text('utf8')
 if p.name!='depth_stair247.py':s=s.replace('257','258').replace('sha258','sha256')
 if p.name.startswith('run_ROOT'):s=s.replace("pattern='run_ROOT258_|","pattern='run_ROOT258_|run_ROOT257_|")
 out=(N if p.name.startswith('run_ROOT')else S)/p.name.replace('257','258');out.write_text(s,encoding='utf8')
files=sorted(S.glob('*.py'))+[N/'run_ROOT258_NEW240_mean_regression_once.py',Path(__file__).resolve()]
for p in files:
 tree=ast.parse(p.read_text('utf8'),filename=str(p))
 for n in ast.walk(tree):
  if isinstance(n,ast.Attribute)and isinstance(n.value,ast.Name)and n.value.id=='hashlib':assert hasattr(hashlib,n.attr),(p,n.attr)
assert hashlib.sha256(b'abc').hexdigest()=='ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad'
report=R/'ROOT258_NEW_ACTUAL_METADATA_SOURCE_CPU_RETURNED.json';put(report,dict(passed=True,epoch=time.time(),source_AST=len(files),original257_pre_CIM_pre_network_hash_name_error_preserved=True,repair='Restore hashlib.sha256 API; independent258 namespace. Source-ID replacement had changed API spelling.',model_raw_SDK_GPU_remote_reads=0,actual_probe_pending=True))
idx=N/'INDEX258_NEW240_MEAN_REGRESSION_FROZEN.json';put(idx,dict(kind='FROZEN_HASH_API_REPAIR_EXPLICIT_USD_MESH_SENSOR',epoch=time.time(),files=[dict(path=str(p),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest())for p in files+[report]],actual_learning=False))
print(json.dumps(dict(passed=True,index_SHA=hashlib.sha256(idx.read_bytes()).hexdigest(),source_AST=len(files))))
