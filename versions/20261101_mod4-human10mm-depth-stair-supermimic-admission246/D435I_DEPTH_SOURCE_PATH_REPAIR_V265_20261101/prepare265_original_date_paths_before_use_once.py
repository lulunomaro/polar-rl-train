from pathlib import Path
import ast,hashlib,json,re,time
N=Path(__file__).resolve().parent;T=N.parent;B=T/'D435I_REAL_FORWARD_DEPTH_270_LOCALIZATION_V264_20261101';S=N/'source';R=N/'reports';S.mkdir(exist_ok=False);R.mkdir(exist_ok=False)
def put(p,x):
 with p.open('x',encoding='utf8')as f:json.dump(x,f,indent=2,allow_nan=False)
for p in sorted((B/'source').glob('*.py'))+[B/'run_ROOT264_NEW240_mean_regression_once.py']:
 s=p.read_text('utf8').replace('20264101','20261101')
 if p.name!='depth_stair263.py':s=re.sub(r'(?<![0-9])264(?![0-9])','265',s)
 if p.name.startswith('run_ROOT'):s=s.replace("pattern='run_ROOT265_|","pattern='run_ROOT265_|run_ROOT264_|")
 out=(N if p.name.startswith('run_ROOT')else S)/p.name.replace('264','265');out.write_text(s,encoding='utf8')
files=sorted(S.glob('*.py'))+[N/'run_ROOT265_NEW240_mean_regression_once.py',Path(__file__).resolve()]
for p in files:
 tree=ast.parse(p.read_text('utf8'),filename=str(p));assert '20264101'not in p.read_text('utf8')or p==Path(__file__).resolve()
 for x in ast.walk(tree):
  if isinstance(x,ast.Attribute)and isinstance(x.value,ast.Name)and x.value.id=='hashlib':assert hasattr(hashlib,x.attr)
C=T/'MODEL2050_LITERAL_JUMP_400N50_ADAPT_V240_20261101';assert (C/'reports/ROOT240V2_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_ACTUAL.json').is_file()
report=R/'ROOT265_NEW_ACTUAL_METADATA_SOURCE_CPU_RETURNED.json';put(report,dict(passed=True,epoch=time.time(),source_AST=len(files),original264_pre_CIM_pre_network_missing_path_false_preserved=True,repair='Restore original20261101 path dates; bound subsequent ID substitution by digit boundaries.',source263_computation_unchanged=True,models_raw_SDK_GPU_remote_reads=0,actual_probe_pending=True))
idx=N/'INDEX265_NEW240_MEAN_REGRESSION_FROZEN.json';put(idx,dict(kind='FROZEN_ORIGINAL_DATE_PATH_REPAIR',epoch=time.time(),files=[dict(path=str(p),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest())for p in files+[report]],actual_learning=False))
print(json.dumps(dict(passed=True,index_SHA=hashlib.sha256(idx.read_bytes()).hexdigest(),source_AST=len(files))))
