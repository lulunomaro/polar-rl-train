from pathlib import Path
import ast,hashlib,json,time
N=Path(__file__).resolve().parent;T=N.parent;S=N/'source';R=N/'reports';R.mkdir(exist_ok=True)
B=T/'MODEL2050_HUMAN_CLOSURE10MM_REGRESSION_V246_20261101'
def put(p,x):
 with p.open('x',encoding='utf8')as f:json.dump(x,f,indent=2,allow_nan=False)
def replace(s,a,b):assert s.count(a)==1,(a,s.count(a));return s.replace(a,b)
# Reuse qualified source-package provenance; never access the actual checkpoint.
c=(B/'source/contract246.py').read_text('utf8').replace('NEW246_HUMAN_CLOSURE10MM_QUALIFIED240_MEAN_GROUND_JUMP_REGRESSION','NEW250_D435I_FRONT_DEPTH_CAMERA_12CONTROLS_ZERO_PT')
c=replace(c,"t['controls_per_case_max']==500 and t['controls_max']==2000","t['controls_per_case_max']==12 and t['controls_max']==12")
c=replace(c,"t['model_byte_reads']==t['model_decodes']==1","t['model_byte_reads']==t['model_decodes']==0")
(S/'contract250.py').write_text(c,encoding='utf8')
parent=(B/'source/target246_single_N1_parent_UNUSED.py').read_text('utf8').replace('246','250')
parent=replace(parent,'evaluate250_NEW240_mean_regression_UNUSED_once.py','evaluate250_front_depth_zero_PT_UNUSED_once.py')
parent=parent.replace('model_byte_reads_by_worker_max=1,model_decodes_max=1','model_byte_reads_by_worker_max=0,model_decodes_max=0').replace('controls_max=2000,physics_max=16000','controls_max=12,physics_max=96').replace('NN_actor_only=True','NN_actor_only=False').replace('geometry_queries_max=2','geometry_queries_max=0').replace('timeout=1800','timeout=900')
(S/'target250_single_N1_parent_UNUSED.py').write_text(parent,encoding='utf8')
(S/'depth_stair247.py').write_bytes((T/'DEPTH_STAIR_TARGET_OBSERVATION_SOURCE_V247_20261101/depth_stair247.py').read_bytes())
caller=(B/'run_ROOT246_NEW240_mean_regression_once.py').read_text('utf8').replace('246','250')
caller=replace(caller,"pattern='run_ROOT250_|","pattern='run_ROOT250_|read248_|run_ROOT246_|")
caller=caller.replace('MOD4_MODEL2050_TRAINED240_MEAN_REGRESSION250_20261101','MOD4_D435I_FRONT_DEPTH_ZERO_PT250_20261101')
caller=caller.replace('controls_per_case_max=500,controls_max=2000,physics_callbacks_max=16000,feedback_samples_max=4000','controls_per_case_max=12,controls_max=12,physics_callbacks_max=96,feedback_samples_max=24')
caller=caller.replace('worker_seconds=1680,parent_wait_seconds=1800','worker_seconds=720,parent_wait_seconds=900').replace('model_byte_reads=1,model_decodes=1','model_byte_reads=0,model_decodes=0').replace('GPU_model_byte_read_decode_max=1','GPU_model_byte_read_decode_max=0')
caller=caller.replace("evaluate250_NEW240_mean_regression_UNUSED_once.py","evaluate250_front_depth_zero_PT_UNUSED_once.py")
caller=caller.replace('controls_max=2000,physics_max=16000,feedback_max=4000','controls_max=12,physics_max=96,feedback_max=24').replace('loaded_geometry_queries=2','loaded_geometry_queries=0')
caller=caller.replace('timeout=2400','timeout=1140').replace("scope='Four controlled first episodes max10s each, fresh10env ownD0-D7; original disjointE0ground/literalJUMPrewards and all original physicalguards. No full270 or population grade.'","scope='Sensor-only10env/12controls96physics24feedback, no PT/actor/optimizer. D435i front-fixed provisional virtual mount and real84x48 image-plane depth, physical270mm static stair fixture. Not learned navigation or training.'")
(N/'run_ROOT250_NEW240_mean_regression_once.py').write_text(caller,encoding='utf8')
files=sorted(S.glob('*.py'))+[N/'run_ROOT250_NEW240_mean_regression_once.py',Path(__file__).resolve()]
for p in files:ast.parse(p.read_text('utf8'),filename=str(p))
assert 'model_byte_reads=0,model_decodes=0'in caller and 'model_byte_reads_by_worker_max=0,model_decodes_max=0'in parent
assert "ENABLE_CAMERAS='1'"in(S/'evaluate250_front_depth_zero_PT_UNUSED_once.py').read_text('utf8')
report=R/'ROOT250_NEW_ACTUAL_METADATA_SOURCE_CPU_RETURNED.json';put(report,dict(passed=True,epoch=time.time(),source_AST=len(files),model_SDK_GPU_remote_reads=0,actual_installed_camera_API_provenance=str(T/'D435I_FRONT_FIXED_SDK_SOURCE_V248_20261101/reports/ROOT248_ACTUAL_CURRENT_CAMERA_SDK_SOURCE_OR_ORIGINAL_ERROR.json'),scope='Before-use camera0PT caller checks; real sensor image stillpending.'))
idx=N/'INDEX250_NEW240_MEAN_REGRESSION_FROZEN.json';put(idx,dict(epoch=time.time(),kind='FROZEN_D435I_FRONT_FIXED_SENSOR_ONLY_ZERO_PT_SOURCE',files=[dict(path=str(p),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest())for p in files+[report]],actual_learning=False))
print(json.dumps(dict(passed=True,index_SHA=hashlib.sha256(idx.read_bytes()).hexdigest(),source_AST=len(files),model_or_SDK=0)))
