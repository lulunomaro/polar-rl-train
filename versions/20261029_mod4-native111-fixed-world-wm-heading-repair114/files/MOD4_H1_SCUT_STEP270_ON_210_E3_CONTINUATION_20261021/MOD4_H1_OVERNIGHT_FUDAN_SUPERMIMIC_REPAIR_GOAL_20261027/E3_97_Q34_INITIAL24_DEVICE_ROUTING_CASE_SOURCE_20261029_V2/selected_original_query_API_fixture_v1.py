"""Actual selected hook/source lifecycle on fresh CPU synthetic API, not SDK."""
from pathlib import Path
from types import SimpleNamespace
import ast,hashlib,importlib.util,json,time,traceback
B=Path(__file__).resolve().parent;L=B.parent
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def put(n,v):
 with (B/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def run_selected_fixture(J):
 assert Path(J).resolve()==B.resolve()
 import torch as t
 assert not t.cuda.is_initialized();rng=t.get_rng_state().clone()
 mf=B/'E3_SOURCE210_COMPLETE_INPUT_MANIFEST_V1.json';m=json.loads(mf.read_bytes());r={x['relative']:x for x in m['files']}
 paths={k:(B/k if (B/k).is_file() else Path(v['local_path'])) for k,v in r.items() if k.endswith('.py')}
 source=paths['runtime/isaac/mod4/mod4_task.py'].read_bytes();runtime=paths['runtime/isaac/mod4/e3_recovery_runtime_v1.py'].read_bytes();phase=paths['runtime/isaac/mod4/e3_public_recovery_phase_v1.py'].read_bytes()
 for rel,raw in [('runtime/isaac/mod4/mod4_task.py',source),('runtime/isaac/mod4/e3_recovery_runtime_v1.py',runtime),('runtime/isaac/mod4/e3_public_recovery_phase_v1.py',phase)]:assert hashlib.sha256(raw).hexdigest()==r[rel]['SHA']
 helper=load('_fresh_E3_existing_query_observer',B/'e3_declared_fall_existing_query_observer_v1.py')
 calls=dict(place_geometry=0,joint_write=0,root_write=0,publish=0,apply=0,pos_read=0,quat_read=0,anchor_rot=0)
 n=20000
 class Data:
  def __init__(self):
   self.root_state_w=t.zeros(n,13);self.root_state_w[:,6]=1
   self.pos=t.zeros(n,31,3);self.quat=t.zeros(n,31,4);self.quat[:,:,3]=1
  @property
  def body_pos_w(self):calls['pos_read']+=1;return self.pos
  @property
  def body_quat_w(self):calls['quat_read']+=1;return self.quat
 data=Data()
 def joint(q,dq,env_ids):calls['joint_write']+=1
 def root(x,env_ids):calls['root_write']+=1;data.root_state_w[env_ids]=x
 robot=SimpleNamespace(data=data,joint_names=['j'+str(i) for i in range(30)],write_joint_state_to_sim=joint,write_root_state_to_sim=root)
 quat=t.zeros(13,4);quat[:,3]=1
 cache=SimpleNamespace(pick=34,source_sha=helper.BANK_SHA,_q=t.zeros(30),_quat=quat,_minimum=-t.ones(13)*.25,_initial=t.ones(13))
 def geometry(recipe,names):
  calls['place_geometry']+=1;return cache._q[None].repeat(len(recipe),1),cache._quat[recipe],cache._minimum[recipe],cache._initial[recipe]
 cache.selected_geometry=geometry
 qresult={}
 def apply(key,tick):
  calls['apply']+=1;v=t.zeros(n,4 if key=='legs' else 2);qresult[(key,tick)]=v;return v
 queue=SimpleNamespace(apply=apply)
 scope={'torch':t};ptree=ast.parse(phase);pc=next(x for x in ptree.body if isinstance(x,ast.ClassDef) and x.name=='RecoveryPhase');exec(compile(ast.Module(body=[pc],type_ignores=[]),str(paths['runtime/isaac/mod4/e3_public_recovery_phase_v1.py']),'exec'),scope);p=scope['RecoveryPhase'](n,'cpu')
 rt=ast.parse(runtime);cls=next(x for x in rt.body if isinstance(x,ast.ClassDef) and x.name=='RecoveryEnv');fn=next(x for x in cls.body if isinstance(x,ast.FunctionDef) and x.name=='place_declared_fall')
 runtime_scope={'torch':t,'tensor':lambda v:v};exec(compile(ast.Module(body=[fn],type_ignores=[]),str(paths['runtime/isaac/mod4/e3_recovery_runtime_v1.py']),'exec'),runtime_scope)
 class Env:pass
 Env.place_declared_fall=runtime_scope['place_declared_fall'];e=Env();e.num_envs=n;e.physics_dt=.0025;e.step_dt=.02;e.device='cpu';e.scene=SimpleNamespace(env_origins=t.zeros(n,3))
 class Scene:
  env_origins=t.zeros(n,3)
  def __getitem__(self,name):assert name=='robot';return robot
 e.scene=Scene();e.recovery=p;e._spring_pressure=SimpleNamespace(ids=[0,1]);e._e3_fixed_reset_cache=cache;e._rescue_reset_q=t.zeros(n,30);e._sim_step_counter=0;e.episode_length_buf=t.zeros(n,dtype=t.long);e._physics_action_delay=SimpleNamespace(queue=queue);e.e3_shapes=[None]*34
 e.publish=lambda:calls.__setitem__('publish',calls['publish']+1)
 def rotate(q,v):
  calls['anchor_rot']+=1;u=q[:,:3];return v+2*t.cross(u,t.cross(u,v,dim=-1)+q[:,3:4]*v,dim=-1)
 def anchors(env):return [('synthetic_closed_loop',0,1,t.zeros(3),t.zeros(3))]
 task_scope={'__name__':'_fresh_original_task','torch':t,'quat_apply':rotate,'_closure_cache':anchors};ctree=ast.parse(source);cf=next(x for x in ctree.body if isinstance(x,ast.FunctionDef) and x.name=='closure_errors');exec(compile(ast.Module(body=[cf],type_ignores=[]),str(paths['runtime/isaac/mod4/mod4_task.py']),'exec'),task_scope)
 task=SimpleNamespace(**task_scope);oldplace=Env.place_declared_fall;oldclosure=task.closure_errors
 # install expects module __dict__ / original globals; use a real module container.
 import types
 task=types.ModuleType('_fresh_original_task');task.__dict__.update(task_scope)
 # Recompile in its actual module global dict, as the real task does.
 exec(compile(ast.Module(body=[cf],type_ignores=[]),str(paths['runtime/isaac/mod4/mod4_task.py']),'exec'),task.__dict__);oldclosure=task.closure_errors
 registry={}
 def factory(env):
  obj=helper.ExistingQueryObserver(env,t,B/'FRESH_CPU_INITIAL24_QUERY_INTEGRATION_OUTPUT',None,lambda pos,quat,shapes:t.zeros(len(pos),34));registry[id(env)]=obj;return obj
 finish,proof,bind=helper.install_before_resume(Env,task,source,factory)
 ids=t.arange(n);result=e.place_declared_fall(ids);assert result is None and calls['place_geometry']==calls['joint_write']==calls['root_write']==calls['publish']==1
 obj=registry[id(e)];assert obj.gas_limits is None
 limits=t.tensor([-.0267046843609,.020639440248416612]).expand(n,2,2).clone();bind(e,limits);assert t.equal(obj.gas_limits,limits)
 for tick in range(2):
  for key in ('legs','wheels'):assert queue.apply(key,tick) is qresult[(key,tick)]
 e._sim_step_counter=8;first=task.closure_errors(e);second=task.closure_errors(e)
 assert calls['pos_read']==calls['quat_read']==2 and calls['anchor_rot']==4
 assert t.equal(first['synthetic_closed_loop'],second['synthetic_closed_loop']) and not first['synthetic_closed_loop'].any()
 assert sum(x['event']=='ORIGINAL_CLOSURE_QUERY_CACHED_INPUT_AND_RESULT' for x in obj.rows)==1
 # Original writer exception propagates; telemetry invalid cannot replace it.
 oldroot=obj.original_root
 def fails(*a,**kw):raise RuntimeError('synthetic ORIGINAL root writer failure')
 obj.original_root=fails
 try:e.place_declared_fall(t.tensor([0]))
 except RuntimeError as exc:assert str(exc)=='synthetic ORIGINAL root writer failure'
 else:raise AssertionError('Original writer error swallowed')
 assert obj.current_place is None;obj.original_root=oldroot
 # A diagnostic evaluator error does NOT alter original numeric result/error flow.
 def bad_eval(*a):raise ValueError('synthetic DIAGNOSTIC-only failure')
 obj.evaluator=bad_eval;e._sim_step_counter=16;value=task.closure_errors(e);assert not value['synthetic_closed_loop'].any() and obj.errors
 rows=finish();assert not rows[0]['diagnostic_valid'] and rows[0]['errors'];assert Env.place_declared_fall is oldplace and task.closure_errors is oldclosure and robot.write_joint_state_to_sim is joint and robot.write_root_state_to_sim is root and queue.apply is apply
 assert t.equal(rng,t.get_rng_state()) and not t.cuda.is_initialized()
 from diagnostic_device_route_fixture_v2 import run_device_route_fixture,validate_index_route_source
 route_proof=run_device_route_fixture(helper,t)
 route_source_proof=validate_index_route_source(Path(helper.__file__).read_bytes())
 proof=dict(device_route_source_guard=route_source_proof,device_routing_fresh_CPU_and_label_proxy=route_proof,passed=True,scope='fresh CPU synthetic selected hook and actual original source function, NOT SDK/PhysX',closure_overlay_inverse_AST=proof,original_place_function_source_SHA=r['runtime/isaac/mod4/e3_recovery_runtime_v1.py']['SHA'],original_closure_module_SHA=r['runtime/isaac/mod4/mod4_task.py']['SHA'],original_place_geometry_joint_root_publish_each_once=True,selected_only_write_rows=True,actual_getter_reads_once_per_original_query=True,no_extra_query_callback=True,original_queue_apply_result_object_identity=True,original_writer_exception_propagated=True,diagnostic_exception_invalid_explicit_and_original_numeric_result_unchanged=True,all_methods_restored=True,no_RNG_draw=True,no_NPZ_model_SDK_remote_or_GPU_read=True,call_counts=calls)
 put('ACTUAL_INITIAL24_SELECTED_QUERY_API_FIXTURE.json',proof)
 return proof
 print(json.dumps(dict(passed=True,scope='CPU synthetic/source only',closure_queries=calls['pos_read'],no_extra_getter=True,all_restored=True)))
