"""Continue the NEW join after Windows resolved a simulated Linux path locally.
Do not regenerate files or repeat E0/source fixtures. Actual remote worker is
unchanged; this fixture supplies explicit POSIX lexical paths for its one check.
"""
from pathlib import Path,PurePosixPath
import ast,copy,hashlib,importlib.util,json,os,sys,time,types
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports';C=N/'control_v2'
S=T/'W35_FULL_RM70_EXPERT_NORMALIZATION_SOURCE_V208_20261031'
def read(p):return json.loads(p.read_bytes())
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def load(name,p):
 q=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(q);q.loader.exec_module(m);return m
put('ROOT210_V2_JOIN_ORIGINAL_WINDOWS_PATH_FALSE_AND_REPAIR.json',dict(epoch=time.time(),original_attempt='prepare210_two_actual_ready_roles_v2_once.py',
 original_error='Windows Path.resolve applied to simulated /home/... before comparison with lexical Linux job path; W35 validate.out assertion',
 original_E0_join_and4_ready_negatives_already_passed=True,actual_remote_GPU_model_or_GO_actions=0,
 fix='Fixture-only PurePosixPath plus explicit resolve callback; remote worker source and its physical/path guard unchanged'))
sys.path.insert(0,str(C));proto=load('parallel210_join_continuation',C/'parallel210_protocol_v2.py')
s=read(N/'SCHEDULE_V2_PUBLIC.json');spec=s['experts']['w35_72'];task=read(N/'w35_package/TASK.json');r=read(N/'ADMISSION210_READY_W35.json')
assert proto.validate_schedule(s)
row=dict(key='w35_72',phase='ready',manifest_SHA=spec['manifest_SHA'],original_error=False,closed_source_CPU=dict(value=r,SHA=hashlib.sha256(json.dumps(r,indent=2).encode()).hexdigest()))
assert proto.valid_ready(row,spec)
g=proto.flat_go_fields(spec);g.update(run_id=s['run_id'],learning_started_epoch=100.,save_deadline=3700.,nominal_end_epoch=4000.,max_parent_seconds=3900,exit_headroom_seconds=300)
worker=S/'adapter_v3/worker_full208_v3.py';fn=next(x for x in ast.parse(worker.read_bytes()).body if isinstance(x,ast.FunctionDef) and x.name=='validate')
scope=dict(KIND=task['kind'],SHA=task['source_SHA'],BYTES=17619013,ADAM=648360,ITER=32336,LR=task['source_LR'],GENERATION='MOD4_SINGLE_WRITER72_20261026',os=os,time=types.SimpleNamespace(time=lambda:101.))
exec(compile(ast.Module(body=[fn],type_ignores=[]),str(worker),'exec'),scope)
old=os.environ.get('CUDA_VISIBLE_DEVICES');os.environ['CUDA_VISIBLE_DEVICES']=task['GPU_UUID']
try:
 job=PurePosixPath(spec['job_root']);args=types.SimpleNamespace(mode='train',num_envs=20000,run_id=s['run_id'],out=types.SimpleNamespace(resolve=lambda:job/'production'))
 scope['validate'](task,g,args,job);negatives=0
 for k,v in [('source_SHA','0'*64),('actual_target0PT_waited_RC',1),('source_fullstate_CPU_passed',False),('actual_target0PT_physics',0)]:
  bad=copy.deepcopy(r);bad[k]=v;br=copy.deepcopy(row);br['closed_source_CPU']=dict(value=bad,SHA=hashlib.sha256(json.dumps(bad,indent=2).encode()).hexdigest());assert not proto.valid_ready(br,spec);negatives+=1
finally:
 if old is None:os.environ.pop('CUDA_VISIBLE_DEVICES',None)
 else:os.environ['CUDA_VISIBLE_DEVICES']=old
put('ROOT210_TWO_ACTUAL_READY_ROLES_OWNER_WORKER_JOIN_CPU_ACTUAL.json',dict(epoch=time.time(),passed=True,roles=['e0_72','w35_72'],ready_negatives_total=4+negatives,
 E0_learning_seconds=10800,W35_learning_seconds=3600,original_raw_charge_HMAC_body_twofcntl_unchanged=True,source_model_or_raw_reads=0,
 target0PT_not_replayed=True,fullstate_GPU_and_first_actual_update_pending=True,one_role210_launch_UNUSED_superseded_before_GO=True,
 Windows_fixture_false_preserved=True,remote_worker_path_guard_unchanged=True))
print(json.dumps(dict(passed=True,roles=2,source_or_model_reads=0,ready_rejections=8)))
