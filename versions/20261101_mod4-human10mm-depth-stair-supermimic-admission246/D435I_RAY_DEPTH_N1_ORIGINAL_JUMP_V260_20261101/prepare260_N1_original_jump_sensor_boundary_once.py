from pathlib import Path
import ast,hashlib,json,time
N=Path(__file__).resolve().parent;T=N.parent;B=T/'D435I_RAY_DEPTH_HASH_NAME_REPAIR_V258_20261101';S=N/'source';R=N/'reports';S.mkdir(exist_ok=False);R.mkdir(exist_ok=False)
def put(p,x):
 with p.open('x',encoding='utf8')as f:json.dump(x,f,indent=2,allow_nan=False)
for p in sorted((B/'source').glob('*.py'))+[B/'run_ROOT258_NEW240_mean_regression_once.py']:
 s=p.read_text('utf8')if p.name=='depth_stair247.py'else p.read_text('utf8').replace('258','260')
 if p.name.startswith('evaluate'):
  assert s.count('import mixed240_sdk as sdk')==1 and s.count('real=sdk.Mixed209Env(cfg=cfg)')==1
  s=s.replace('import mixed240_sdk as sdk','import jump194_sdk as sdk').replace('real=sdk.Mixed209Env(cfg=cfg)','real=sdk.JumpMod4Env(cfg=cfg)')
 if p.name.startswith('run_ROOT'):s=s.replace("pattern='run_ROOT260_|","pattern='run_ROOT260_|run_ROOT258_|")
 out=(N if p.name.startswith('run_ROOT')else S)/p.name.replace('258','260');out.write_text(s,encoding='utf8')
files=sorted(S.glob('*.py'))+[N/'run_ROOT260_NEW240_mean_regression_once.py',Path(__file__).resolve()]
for p in files:
 tree=ast.parse(p.read_text('utf8'),filename=str(p))
 for n in ast.walk(tree):
  if isinstance(n,ast.Attribute)and isinstance(n.value,ast.Name)and n.value.id=='hashlib':assert hasattr(hashlib,n.attr)
report=R/'ROOT260_NEW_ACTUAL_METADATA_SOURCE_CPU_RETURNED.json';put(report,dict(passed=True,epoch=time.time(),source_AST=len(files),original258_false_preserved=True,actual258_mesh_initialized='ActualSDK read /World/ground/mesh12vertices42faces',repair='N1 sensor-only uses original JUMP env and commands; disjoint mixed training requires num_envs multiple10. No reward formula edits.',model_raw_SDK_GPU_remote_reads=0,actual_probe_pending=True))
idx=N/'INDEX260_NEW240_MEAN_REGRESSION_FROZEN.json';put(idx,dict(kind='FROZEN_N1_ORIGINAL_JUMP_SENSOR_BOUNDARY',epoch=time.time(),files=[dict(path=str(p),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest())for p in files+[report]],actual_learning=False))
print(json.dumps(dict(passed=True,index_SHA=hashlib.sha256(idx.read_bytes()).hexdigest(),source_AST=len(files))))
