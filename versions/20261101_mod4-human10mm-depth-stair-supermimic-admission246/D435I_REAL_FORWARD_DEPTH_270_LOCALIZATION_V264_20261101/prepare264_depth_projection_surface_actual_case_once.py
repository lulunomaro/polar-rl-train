from pathlib import Path
import ast,hashlib,json,time
N=Path(__file__).resolve().parent;T=N.parent;B=T/'D435I_RAY_DEPTH_ORIGINAL_JUMP_AUDIT_V261_20261101';C=T/'DEPTH_HORIZONTAL_SUPPORT_PIXEL_CENTER_V263_20261101';S=N/'source';R=N/'reports';S.mkdir(exist_ok=False);R.mkdir(exist_ok=False)
def put(p,x):
 with p.open('x',encoding='utf8')as f:json.dump(x,f,indent=2,allow_nan=False)
assert json.loads((C/'reports/ROOT263_NEW_ANALYTIC_SURFACE_LOCALIZATION_CPU_RETURNED.json').read_bytes())['passed']
for p in sorted((B/'source').glob('*.py'))+[B/'run_ROOT261_NEW240_mean_regression_once.py']:
 if p.name=='depth_stair247.py':continue
 s=p.read_text('utf8').replace('261','264')
 if p.name.startswith('evaluate'):
  assert s.count('from depth_stair247 import target_from_depth')==1;s=s.replace('from depth_stair247 import target_from_depth','from depth_stair263 import target_from_depth')
  needle='result=target_from_depth(image,K,T,sensor_time=(i+1)*.02,control_time=(i+1)*.02)';assert s.count(needle)==1
  s=s.replace(needle,needle[:-1]+',pixel_center_offset=.5)\n  assert result[\'found\'] and abs(result[\'step_height_m\']-.27)<.02, result')
  s=s.replace('real_sim_depth_frames=True,','real_sim_depth_frames=True,localization_checked_against_270mm_fixture=True,visible_surface_distance_not_certified_true_front_edge=True,')
 if p.name.startswith('run_ROOT'):s=s.replace("pattern='run_ROOT264_|","pattern='run_ROOT264_|read262_|run_ROOT261_|")
 out=(N if p.name.startswith('run_ROOT')else S)/p.name.replace('261','264');out.write_text(s,encoding='utf8')
(S/'depth_stair263.py').write_bytes((C/'depth_stair263.py').read_bytes())
files=sorted(S.glob('*.py'))+[N/'run_ROOT264_NEW240_mean_regression_once.py',Path(__file__).resolve()]
for p in files:
 tree=ast.parse(p.read_text('utf8'),filename=str(p))
 for n in ast.walk(tree):
  if isinstance(n,ast.Attribute)and isinstance(n.value,ast.Name)and n.value.id=='hashlib':assert hasattr(hashlib,n.attr)
report=R/'ROOT264_NEW_ACTUAL_METADATA_SOURCE_CPU_RETURNED.json';put(report,dict(passed=True,epoch=time.time(),source_AST=len(files),actual261_depth_success_but_wrong_localization_preserved=True,source263_SHA=hashlib.sha256((C/'depth_stair263.py').read_bytes()).hexdigest(),fix='SDK actual +.5 pixel center and observed horizontal support normals; same real depth sensor/physical mesh.',models_raw_SDK_GPU_remote_reads=0,actual_probe_pending=True,visible_extent_not_full_footprint_or_exact_front_edge=True))
idx=N/'INDEX264_NEW240_MEAN_REGRESSION_FROZEN.json';put(idx,dict(kind='FROZEN_REAL_DEPTH_270MM_SURFACE_LOCALIZATION_CASE',epoch=time.time(),files=[dict(path=str(p),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest())for p in files+[report]],actual_learning=False))
print(json.dumps(dict(passed=True,index_SHA=hashlib.sha256(idx.read_bytes()).hexdigest(),source_AST=len(files))))
