from pathlib import Path
import ast,copy,hashlib,importlib.util,json,os,time,traceback,types,shutil
import torch
M=Path(__file__).resolve().parent;R=M/'reports'
def put_report(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
try:
 p=M/'mixed_precision_step_benchmark_runtime_v7.py';sp=importlib.util.spec_from_file_location('v7_cpu',p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
 runtime=ast.parse(p.read_text('utf8'));run=next(n for n in runtime.body if isinstance(n,ast.FunctionDef) and n.name=='run')
 log_node=next(n for n in ast.walk(run) if isinstance(n,ast.FunctionDef) and n.name=='log')
 log_source=ast.unparse(log_node)
 results=[]
 for host in ['210','72']:
  capture=json.loads((R/f'ACTUAL_RSL_RUNNER_LOGGER_SOURCE_AND_RESOURCE_{host}_ACTUAL.json').read_bytes());src=capture['sources'][0]
  tree=ast.parse(src['text']);cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='OnPolicyRunner');learn=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='learn');learn_source=ast.unparse(learn)
  logger_source=capture['sources'][1]['text'];lc=next(n for n in ast.parse(logger_source).body if isinstance(n,ast.ClassDef) and n.name=='Logger');logger=copy.deepcopy(next(n for n in lc.body if isinstance(n,ast.FunctionDef) and n.name=='log'));logger.body=ast.parse('self.actual_log_calls.append(dict(it=it, collect_time=collect_time, learn_time=learn_time))').body
  synthetic_time=[0.]
  def synthetic_seconds():synthetic_time[0]+=.01;return synthetic_time[0]
  ns=dict(torch=torch,time=types.SimpleNamespace(time=synthetic_seconds),os=os,check_nan=lambda *args:None)
  exec(compile(ast.Module(body=[learn],type_ignores=[]),'ACTUAL_INSTALLED_RUNNER_LEARN','exec'),ns)
  ls=dict(torch=torch);exec(compile(ast.fix_missing_locations(ast.Module(body=[logger],type_ignores=[])),'ACTUAL_LOGGER_SIGNATURE_STUB','exec'),ls)
  class Env:
   device='cpu';max_episode_length=2000;episode_length_buf=torch.zeros(2,dtype=torch.int64)
   def get_observations(self):return torch.zeros((2,8))
   def step(self,action):
    state['env_calls']+=1;state['env_s']+=.2
    return self.get_observations(),torch.zeros(2),torch.zeros(2,dtype=torch.bool),{}
  class Alg:
   learning_rate=.0001
   def train_mode(self):pass
   def act(self,obs):
    if state['cycle_start'] is None:state['cycle_start']=time.perf_counter()
    state['act_calls']+=1;state['act_s']+=.01
    return torch.zeros((2,6))
   def process_env_step(self,*args):pass
   def compute_returns(self,*args):pass
   def update(self):self.steps+=20;state['update_s']=.1;return {}
   def get_policy(self):return types.SimpleNamespace(output_std=torch.ones(6))
  alg=Alg();alg.steps=790000
  alg.actor=alg.critic=types.SimpleNamespace(state_dict=lambda:{'cpu_synthetic_finite':torch.ones(1)})
  alg.optimizer=types.SimpleNamespace(state_dict=lambda:{'state':{i:{'step':alg.steps} for i in range(17)}})
  alg._benchmark_scaler=types.SimpleNamespace(get_scale=lambda:1.)
  logger=types.SimpleNamespace(writer=None,actual_log_calls=[],init_logging_writer=lambda:None,process_env_step=lambda *args:None)
  logger.log=types.MethodType(ls['log'],logger)
  state=dict(mode='fp32',act_s=0.,env_s=0.,act_calls=0,env_calls=0,cycle_start=None,cycle_end=None,update_s=0.)
  class BlockComplete(Exception):pass
  # Compile the exact V7 nested log body, including timing rows/reset/finite/stop handling.
  factory='def factory():\n completed=0\n'+ '\n'.join(' '+x for x in log_source.splitlines())+'\n return log\n'
  writes=[];rows=[]
  scope=dict(sync=lambda:None,time=time,original_log=logger.log,actual_logger_timing=m.actual_logger_timing,mode_state=state,alg=alg,finite_tree=m.finite_tree,task={'source_Adamstep':790000},WARMUP_UPDATES=2,NUM_UPDATES=6,profile=types.SimpleNamespace(sums={},counts={}),rows=rows,put=lambda p,v:writes.append((str(p),copy.deepcopy(v))),dest=M/'CPU_STUB_NEVER_CREATED',out=M,key='h1' if host=='210' else 'recovery',mode='fp32',mode_results=[],compare={},shutil=shutil,go={'save_deadline':time.time()+3900},BlockComplete=BlockComplete)
  exec(factory,scope);logger.log=scope['factory']()
  runner=types.SimpleNamespace(env=Env(),alg=alg,logger=logger,device='cpu',is_distributed=False,current_learning_iteration=0,cfg={'num_steps_per_env':24,'algorithm':{'rnd_cfg':None},'save_interval':50})
  try:ns['learn'](runner,7,True)
  except BlockComplete:pass
  assert len(rows)==len(logger.actual_log_calls)==6
  assert rows[-1]['actual17Adam_steps']==[790120] and rows[-1]['expected_Adam_without_skipped_FP16_steps']==790120
  assert [r['warmup'] for r in rows]==[True,True,False,False,False,False]
  assert all(r['collection_s']>=0 and r['original_logger_learning_s']>=0 and r['all_source_model_optimizer_tensors_finite'] for r in rows)
  assert state['act_calls']==state['env_calls']==0 and not torch.cuda.is_initialized()
  assert not (M/'CPU_STUB_NEVER_CREATED').exists()
  results.append(dict(host=host,actual_runner_source_SHA=src['SHA'],actual_logger_source_SHA=capture['sources'][1]['SHA'],actual_runner_learn_and_V7_log_body_executed=True,CPU_stub_env_not_physics=True,complete_iterations=6,act_env_calls_per_iteration=24,expected_17Adam_clock_verified=True,actual_collect_time_keyword_ABI=True,no_CUDA_or_model_PT_or_raw_read=True))
 put_report('V7_ACTUAL_INSTALLED_RSL_RUNNER_LEARN_LOGGER_CPU_INTEGRATION_V2_ACTUAL.json',dict(epoch=time.time(),passed=True,results=results,source_SHA=hashlib.sha256(p.read_bytes()).hexdigest(),not_GPU_timing_or_numerical_acceptance=True))
 print(json.dumps(dict(passed=True,actual_runner_ABI_cases=results)))
except BaseException:
 put_report('V7_ACTUAL_RSL_CPU_INTEGRATION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc()));raise
