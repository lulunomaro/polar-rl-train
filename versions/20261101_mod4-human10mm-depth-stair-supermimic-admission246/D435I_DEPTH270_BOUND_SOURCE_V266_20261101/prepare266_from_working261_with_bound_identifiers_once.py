from pathlib import Path
import ast,hashlib,json,re,time
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;B=T/'D435I_RAY_DEPTH_ORIGINAL_JUMP_AUDIT_V261_20261101';C=T/'DEPTH_HORIZONTAL_SUPPORT_PIXEL_CENTER_V263_20261101';S=N/'source';R=N/'reports';S.mkdir(exist_ok=False);R.mkdir(exist_ok=False)
def put(p,x):
 with p.open('x',encoding='utf8')as f:json.dump(x,f,indent=2,allow_nan=False)
assert json.loads((C/'reports/ROOT263_NEW_ANALYTIC_SURFACE_LOCALIZATION_CPU_RETURNED.json').read_bytes())['passed']
for p in sorted((B/'source').glob('*.py'))+[B/'run_ROOT261_NEW240_mean_regression_once.py']:
 if p.name=='depth_stair247.py':continue
 s=re.sub(r'(?<![0-9])261(?![0-9])','266',p.read_text('utf8'))
 if p.name.startswith('evaluate'):
  s=s.replace('from depth_stair247 import target_from_depth','from depth_stair263 import target_from_depth')
  needle='result=target_from_depth(image,K,T,sensor_time=(i+1)*.02,control_time=(i+1)*.02)';assert s.count(needle)==1
  s=s.replace(needle,needle[:-1]+',pixel_center_offset=.5)\n  assert result[\'found\'] and abs(result[\'step_height_m\']-.27)<.02, result')
  s=s.replace('real_sim_depth_frames=True,','real_sim_depth_frames=True,localization_checked_against_270mm_fixture=True,visible_surface_distance_not_certified_true_front_edge=True,')
 if p.name.startswith('run_ROOT'):s=s.replace("pattern='run_ROOT266_|","pattern='run_ROOT266_|run_ROOT265_|run_ROOT264_|read262_|run_ROOT261_|")
 out=(N if p.name.startswith('run_ROOT')else S)/p.name.replace('261','266');out.write_text(s,encoding='utf8')
(S/'depth_stair263.py').write_bytes((C/'depth_stair263.py').read_bytes())
files=sorted(S.glob('*.py'))+[N/'run_ROOT266_NEW240_mean_regression_once.py',Path(__file__).resolve()]
for p in files:
 tree=ast.parse(p.read_text('utf8'),filename=str(p))
 for x in ast.walk(tree):
  if isinstance(x,ast.Attribute)and isinstance(x.value,ast.Name)and x.value.id=='hashlib':assert hasattr(hashlib,x.attr)
for p in (T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py',T/'MODEL2050_LITERAL_JUMP_400N50_ADAPT_V240_20261101/reports/ROOT240V2_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_ACTUAL.json'):assert p.is_file(),str(p)
report=R/'ROOT266_NEW_ACTUAL_METADATA_SOURCE_CPU_RETURNED.json';put(report,dict(passed=True,epoch=time.time(),source_AST=len(files),original264265_pre_network_path_errors_preserved=True,repair='Derive again from actual working261; ID substitutions bounded by digit boundaries so original2026 date paths are untouched.',source263_SHA=hashlib.sha256((C/'depth_stair263.py').read_bytes()).hexdigest(),models_raw_SDK_GPU_remote_reads=0,actual_probe_pending=True))
idx=N/'INDEX266_NEW240_MEAN_REGRESSION_FROZEN.json';put(idx,dict(kind='FROZEN_BOUND_SOURCE_DEPTH270_CASE',epoch=time.time(),files=[dict(path=str(p),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest())for p in files+[report]],actual_learning=False))
print(json.dumps(dict(passed=True,index_SHA=hashlib.sha256(idx.read_bytes()).hexdigest(),source_AST=len(files))))
