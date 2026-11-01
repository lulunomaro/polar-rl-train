from pathlib import Path
import ast,hashlib,json,time
N=Path(__file__).resolve().parent;T=N.parent;B=T/'D435I_FORWARD_RAY_DEPTH_ZERO_PT_V254_20261101';S=N/'source';R=N/'reports'
S.mkdir(exist_ok=False);R.mkdir(exist_ok=False)
def put(p,x):
 with p.open('x',encoding='utf8')as f:json.dump(x,f,indent=2,allow_nan=False)
def change(s,a,b):
 assert s.count(a)==1,(a,s.count(a));return s.replace(a,b)
e=json.loads((B/'reports/ROOT254_NEW240_MEAN_REGRESSION_PARENT_OR_ORIGINAL_ERROR_RETURNED_ACTUAL.json').read_bytes())
original_error=next(x['UTF8']for x in e['full_UTF8']if x['path'].endswith('/ORIGINAL254_ERROR.json'))
assert 'No sensor prims matched: /World/envs/env_.*/Robot/chassis' in original_error
actual_source=T/'MODEL2050_LITERAL_JUMP_400N50_ADAPT_V240_20261101/package/payload/job0/runtime/isaac/mod4/mod4_task.py'
binding=actual_source.read_text('utf8');assert 'prim_path="{ENV_REGEX_NS}/Robot/links/chassis"'in binding
for p in B.joinpath('source').glob('*.py'):
 s=p.read_text('utf8').replace('254','256')if p.name!='depth_stair247.py'else p.read_text('utf8')
 if p.name.startswith('evaluate'):
  assert s.count("cfg.scene.robot.prim_path+'/chassis'")==2
  s=s.replace("cfg.scene.robot.prim_path+'/chassis'","cfg.scene.robot.prim_path+'/links/chassis'")
 if p.name=='contract254.py':
  s=change(s,"assert [(x['name'],x['env'])for x in t['cases']]==[('standing',0),('forward',0),('reverse',0),('literal_jump',1)]","assert [(x['name'],x['env'])for x in t['cases']]==[('sensor_zero_action',0)]")
 (S/p.name.replace('254','256')).write_text(s,encoding='utf8')
s=(B/'run_ROOT254_NEW240_mean_regression_once.py').read_text('utf8').replace('254','256')
s=change(s,"pattern='run_ROOT256_|","pattern='run_ROOT256_|run_ROOT254_|")
s=change(s,"cases=[dict(name='standing',env=0,vx=0.,height=.25),dict(name='forward',env=0,vx=.3,height=.25),dict(name='reverse',env=0,vx=-.3,height=.25),dict(name='literal_jump',env=1,vx=0.,height=.135)]","cases=[dict(name='sensor_zero_action',env=0)]")
s=s.replace('Sensor-only10env/12controls96physics24feedback','Sensor-only1env/12controls96physics24feedback')
s=change(s,'"""ROOT freshclosed240 deterministic short regression; one NEWformal GPU read."""','"""ROOT model-free ray depth admission; bind current actual Robot/links/chassis."""')
(N/'run_ROOT256_NEW240_mean_regression_once.py').write_text(s,encoding='utf8')
files=sorted(S.glob('*.py'))+[N/'run_ROOT256_NEW240_mean_regression_once.py',Path(__file__).resolve()]
for p in files:ast.parse(p.read_text('utf8'),filename=str(p))
report=R/'ROOT256_NEW_ACTUAL_METADATA_SOURCE_CPU_RETURNED.json'
put(report,dict(passed=True,epoch=time.time(),source_AST=len(files),actual_binding_source=dict(path=str(actual_source),SHA=hashlib.sha256(binding.encode()).hexdigest(),chassis_contact_path='{ENV_REGEX_NS}/Robot/links/chassis'),original254_false_preserved=True,original_error=original_error,physical_reward_sensor_algorithm_unchanged=True,models_raw_SDK_GPU_remote_reads=0,actual_probe_pending=True))
idx=N/'INDEX256_NEW240_MEAN_REGRESSION_FROZEN.json';put(idx,dict(kind='FROZEN_ACTUAL_CHASSIS_LINK_RAY_SENSOR_BINDING',epoch=time.time(),files=[dict(path=str(p),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest())for p in files+[report]],actual_learning=False))
print(json.dumps(dict(passed=True,index_SHA=hashlib.sha256(idx.read_bytes()).hexdigest(),source_AST=len(files))))
