"""NEW synthetic source/counter/restore integration. No actor/WM forward or PT."""
from pathlib import Path
from dataclasses import dataclass,asdict
from copy import deepcopy
from types import SimpleNamespace as S
import ast,hashlib,json,sys,traceback
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE));T=HERE.parents[1];B=T/'H1_STEP270_THREE_GPU_OWN_FUDAN_NATIVE_V87_20261027/payloads_r5/h1'
def put(name,value):
 with (HERE/name).open('x',encoding='utf8') as f:json.dump(value,f,indent=2,allow_nan=False)
checks=[]
def ok(name,v=True):assert v,name;checks.append(name)
def refuse(name,f):
 try:f()
 except (ValueError,AssertionError,KeyError):ok(name);return
 raise AssertionError('negative unexpectedly accepted '+name)
def func(path,name,cls=None):
 tree=ast.parse(path.read_bytes());body=tree.body if cls is None else next(x.body for x in tree.body if isinstance(x,ast.ClassDef) and x.name==cls)
 return next(x for x in body if isinstance(x,ast.FunctionDef) and x.name==name)
put('SOURCE_CPU_ENTRY_CONSUMED_ACTUAL.json',dict(purpose='new native88 migration integration source only',no_original_fixture_or_model_or_control=True))
try:
 import torch
 import native88_gas400_migration_v1 as m
 from native88_typed_window_reviewer_v1 import review_new_native88_decoded
 from native88_gas400_migration_v1 import install_restored_window,verify_saved_migration,verify_window,RequireNewWindowFinal
 def literal(a,b):
  if torch.is_tensor(a):return torch.is_tensor(b) and a.shape==b.shape and a.dtype==b.dtype and torch.equal(a,b)
  if isinstance(a,dict):return isinstance(b,dict) and set(a)==set(b) and all(literal(a[k],b[k]) for k in a)
  if isinstance(a,(tuple,list)):return type(a) is type(b) and len(a)==len(b) and all(literal(x,y) for x,y in zip(a,b))
  return type(a) is type(b) and a==b
 @dataclass
 class Config:
  seed:int;hist:int=10;goal_frames:int=10;no_critic:bool=False;warmup_steps:int=64;wm_only_iters:int=64;wm_batches:int=10
 class StateContainer(torch.nn.Module):
  def __init__(self,width):
   super().__init__();self.weight=torch.nn.Parameter(torch.ones(1));self.register_buffer('normalizer_mean',torch.arange(float(width)));self.register_buffer('normalizer_var',torch.ones(width));self.register_buffer('normalizer_count',torch.tensor(100.))
  def forward(self,*a,**k):raise AssertionError('FORWARD FORBIDDEN IN THIS SOURCE FIXTURE')
 def learner(seed):
  x=S(cfg=Config(seed),env=S(num_envs=4096),buffer=S(size=0),obs_hist=torch.zeros(4096,10,86),iteration=0,sim_steps=0,wall_time=0.)
  for name,width in [('wm',167),('pi',1460),('critic',1625)]:setattr(x,name,StateContainer(width))
  for name,group in [('opt_wm','wm'),('opt_pi','pi'),('opt_v','critic')]:
   opt=torch.optim.Adam(getattr(x,group).parameters(),lr=.0001);parameter=next(getattr(x,group).parameters());opt.state[parameter]=dict(step=torch.tensor(12.),exp_avg=torch.full_like(parameter,.1),exp_avg_sq=torch.full_like(parameter,.2));setattr(x,name,opt)
  return x
 scope={};tree=ast.parse((B/'source/native_finalization_own_v3.py').read_bytes());a=next(n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='NATIVE_CONTRACT' for x in n.targets));exec(compile(ast.Module(body=[a],type_ignores=[]),'old_contract_AST_only','exec'),scope);oldcontract=scope['NATIVE_CONTRACT']
 summaries={}
 for role in ('h1','recovery'):
  source=m.SOURCES[role];original=learner(source['seed']);cfg=asdict(original.cfg)
  native={key:deepcopy(getattr(original,key).state_dict()) for key in ('wm','pi','critic','opt_wm','opt_pi','opt_v')};native.update(iteration=source['updates'],sim_steps=1234567,wall_time=123.5,args=cfg,saved_at='SYNTHETIC_NEW_PURPOSE')
  full=dict(UniSuperMimic_test_contract=oldcontract,UniSuperMimic_H1_test=native,UniSuperMimic_publication=dict(native_iteration=source['updates'],world_updates=source['world_updates'],policy_updates=source['policy_updates'],history_shape=[4096,10,86],episode_step_shape=[4096],producer=dict(reference_artifact_SHA=m.REFERENCE_SHA,method='MOD4_own_Fudan_native_v3',native_architecture_fresh=True,bootstrap_Adam=832460)))
  target=learner(source['seed']);bridge=S(wm_updates=0,pi_updates=0,ep_step=torch.zeros(4096,dtype=torch.int32));trace=S(total=0)
  history=target.obs_hist;episode=bridge.ep_step;rng=torch.get_rng_state().clone()
  window,proof=install_restored_window(target,bridge,trace,full,key=role,source_SHA=source['SHA'],expected_source_contract=oldcontract,expected_args=cfg,parameter_contract_SHA='a'*64,asset_report_SHA='b'*64)
  ok(role+'_all_modules_norms_threeopts_literal_restored',all(literal(getattr(target,k).state_dict(),native[k]) for k in ('wm','pi','critic','opt_wm','opt_pi','opt_v')))
  ok(role+'_saved_global_iteration_WM_Pi_time_sim_steps_preserved',target.iteration==source['updates'] and bridge.wm_updates==source['world_updates'] and bridge.pi_updates==source['policy_updates'] and target.sim_steps==1234567 and target.wall_time==123.5)
  ok(role+'_fresh_history_episode_replay_no_RNG_change',target.obs_hist is history and bridge.ep_step is episode and not bool(history.any()) and not bool(episode.any()) and target.buffer.size==0 and torch.equal(rng,torch.get_rng_state()))
  initial=window.snapshot();zero_receipt=dict(SHA='d'*64,bytes=123,native88_migration_window=initial)
  ok(role+'_old_positivePi_prefix_not_first_newPi',not window.qualifies_preupdate(zero_receipt,dict(SHA='d'*64,bytes=123,before_control=0)))
  calls=[]
  class FakePublisher:
   def __call__(self,*a,**kw):calls.append('complete_fullsave_called');return zero_receipt
  refuse(role+'_zero_newPi_FINAL_refused_after_protected_fullsave',lambda:RequireNewWindowFinal(FakePublisher())('NO_REAL_FILE'))
  ok(role+'_fullsave_not_skipped_by_delta_guard',calls==['complete_fullsave_called'])
  # Source-counter simulation only, no collect/step/optimizer or model call.
  trace.total=64;target.sim_steps+=64*4096
  window.preload_evidence=dict(actual_original_preload_active=True,observed_before_original_write=True,fixture_only=True)
  for iteration in range(64):
   n=2 if iteration%2==0 else 3;trace.total+=n;target.sim_steps+=n*4096
   for _ in range(10):bridge.wm_updates+=1;window.completed_world_update()
   assert window.allow_policy_update(target.iteration) is False
   target.iteration+=1
  ok(role+'_64_new_window_iterations_world_only_despite_oldglobal',window.new_wm==640 and window.new_pi==0 and bridge.pi_updates==source['policy_updates'])
  trace.total+=2;target.sim_steps+=2*4096
  for _ in range(10):bridge.wm_updates+=1;window.completed_world_update()
  window.before_policy_update();bridge.pi_updates+=1;window.completed_policy_update();target.iteration+=1
  w=window.snapshot();verify_window(w,require_new_pi=True)
  ok(role+'_first_newPi_after226_controls_650WM_newiteration64',w['first_new_policy_update']==dict(native_iteration=source['updates']+64,window_iteration=64,completed_fresh_controls=226,new_world_updates=650,new_policy_updates=1))
  producer=dict(initial_native_source=window.source,gas400_parameter_source_contract_SHA='a'*64,actual_gas400_asset_composition_report_SHA='b'*64,native_architecture_fresh=False,method='MOD4_own_Fudan_native88_nominal400_changed_plant')
  pub=dict(native88_migration_window=w,native_iteration=target.iteration,world_updates=bridge.wm_updates,policy_updates=bridge.pi_updates,producer=producer)
  saved=dict(UniSuperMimic_publication=pub,UniSuperMimic_changed_plant_migration=w,UniSuperMimic_test_contract=m.NATIVE_CONTRACT,UniSuperMimic_H1_test=dict(iteration=target.iteration),spring_pressure_recipe=dict(nominal_stiffness_N_m=2000,actual_stiffness_bounds_N_m=[1800,2200]))
  receipt=dict(SHA='d'*64,bytes=123,updates=target.iteration,world_updates=bridge.wm_updates,policy_updates=bridge.pi_updates,native88_migration_window=w,verified_new_publication=True,original_full_save_chain_returned=True)
  ok(role+'_first_new_preupdate_requires_sameSHA_bytes_control',window.qualifies_preupdate(receipt,dict(SHA='d'*64,bytes=123,before_control=226)))
  ok(role+'_stale216_prefix_not_relabelled',not window.qualifies_preupdate(receipt,dict(SHA='d'*64,bytes=123,before_control=216)))
  formal=dict(passed=True,trace_persisted=True,primary_error=None,secondary_errors=[],final=receipt,counters={k:receipt[k] for k in ('updates','world_updates','policy_updates')})
  review=review_new_native88_decoded(saved,formal,expected_role=role,parameter_contract_SHA='a'*64,asset_report_SHA='b'*64)
  ok(role+'_saved_window_publisher_formal_reviewer_bound',review['new_world_updates']==650 and review['new_policy_updates']==1)
  bad=deepcopy(saved);bad['spring_pressure_recipe']['nominal_stiffness_N_m']=3500;refuse(role+'_old700_recipe_in_newsave_refused',lambda:verify_saved_migration(bad,pub))
  bad=deepcopy(saved);bad['UniSuperMimic_test_contract']['original_physics_and_success_unchanged']=True;refuse(role+'_old_samephysics_true_contract_refused',lambda:verify_saved_migration(bad,pub))
  bad=deepcopy(w);bad['first_new_policy_update']['new_world_updates']=639;refuse(role+'_insufficient639WM_firstPi_refused',lambda:verify_window(bad,True))
  other='recovery' if role=='h1' else 'h1';refuse(role+'_wrong_role_native_source_refused',lambda:m.validate_role_source(role,m.SOURCES[other]['SHA'],source))
  summaries[role]=dict(source=source,first_new_policy=w['first_new_policy_update'],fixture_only=True)
 # Full body/source comparisons: dynamics/actuation/loss/RNG/save errors untouched.
 old=B/'source/supermimic_wheel_leg_v3/learner.py';new=HERE/'vendor_candidate/supermimic_wheel_leg_v3/learner.py'
 for name in ('collect','wm_update','policy_update','lr_at','_checkpoint'):ok(name+'_original_AST_exact',ast.dump(func(old,name,'SuperMimicLearner'))==ast.dump(func(new,name,'SuperMimicLearner')))
 nt=func(new,'train','SuperMimicLearner');ot=func(old,'train','SuperMimicLearner');changed=[]
 for node in ast.walk(nt):
  if isinstance(node,ast.If) and ast.unparse(node.test)=='self.native88_migration.allow_policy_update(iteration)':node.test=ast.parse('iteration >= self.cfg.wm_only_iters',mode='eval').body;changed.append(1)
 ok('train_only_phase_predicate_changed_remainder_AST_exact',len(changed)==1 and ast.dump(nt)==ast.dump(ot))
 oldfinal=B/'source/native_finalization_own_v3.py';newfinal=HERE/'native_finalization_own88_gas400.py'
 for name in ('run_native_lifecycle','error_record','emit_error','assert_finite','atomic_json'):
  ok(name+'_original_AST_exact',ast.dump(func(oldfinal,name))==ast.dump(func(newfinal,name)))
 oldhandlers=[ast.dump(x) for x in ast.walk(ast.parse(oldfinal.read_bytes())) if isinstance(x,ast.ExceptHandler)]
 newhandlers=[ast.dump(x) for x in ast.walk(ast.parse(newfinal.read_bytes())) if isinstance(x,ast.ExceptHandler)]
 ok('all_publisher_lifecycle_error_handlers_AST_exact',oldhandlers==newhandlers)
 ok('control_bridge_byteexact',hashlib.sha256((HERE/'native_wheel_leg_bridge_v4.py').read_bytes()).hexdigest()==hashlib.sha256((B/'source/native_wheel_leg_bridge_v4.py').read_bytes()).hexdigest())
 entry=(HERE/'native_own_fudan88_gas400_training_v2.py').read_text('utf8');ok('newentry_restores_before_publisher_and_train',entry.index('install_restored_window(')<entry.index('publisher=NativeCheckpointPublisher(')<entry.index('return run_native_lifecycle('))
 ok('newentry_newnativeSHA_distinct_frozenRSL_bootstrap',"source_SHA=task['source_SHA'],frozen_RSL_bootstrap_SHA=BOOTSTRAP_SHA" in entry)
 ok('newentry_FINAL_and_firstpositive_use_new_window_guards','save=RequireNewWindowFinal(publisher)' in entry and "holder['window'].qualifies_preupdate" in entry)
 task=dict(source_SHA=m.SOURCES['h1']['SHA'],source_progress={k:m.SOURCES['h1'][k] for k in ('updates','world_updates','policy_updates')},native_seed=27,source_Adamstep=832460,native_reference_SHA=m.REFERENCE_SHA,changed_plant700_to_nominal400=True,gas400_parameter_source_contract_SHA='a'*64,actual_gas400_asset_composition_report_SHA='b'*64)
 go=dict(task,source_qualification_kind=m.KIND,max_parent_seconds=3900,exit_headroom_seconds=300)
 refuse('physics_change_alone_cannot_GO_known_misaligned_objective',lambda:m.assert_declared_admission('h1',task,go))
 for p in HERE.rglob('*.py'):ast.parse(p.read_bytes())
 ok('final_all_source_AST_and_no_CUDA_or_model_forward',not torch.cuda.is_initialized())
 put('SOURCE_CPU_NATIVE88_INTEGRATION_ACTUAL.json',dict(passed=True,checks=len(checks),check_names=checks,source_summaries=summaries,synthetic_only=True,no_actor_or_WM_forward_no_optimizer_step_no_physics=True,no_real_checkpoint_or_asset_opened=True,actual_SDK_source_resources_and_objective_admission_pending=True,not_a_GO_or_training_gain_claim=True))
 print(json.dumps(dict(passed=True,checks=len(checks),synthetic_only=True)))
except BaseException:
 put('ORIGINAL_NATIVE88_INTEGRATION_CPU_ERROR_ACTUAL.json',dict(error=traceback.format_exc(),checks=checks,partial_results_retained=True));raise
