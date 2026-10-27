"""NEW bounded CPU metadata/source checks. No actor even with tiny weights.

SpyPolicy below is a state-container constructor spy with no forward method.
It never imports or constructs the actual policy, WM, learner, optimizer or SDK.
"""
from pathlib import Path
import ast,copy,hashlib,io,json,sys,traceback
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE));OUT=HERE/'SOURCE_CPU_ACTUAL.json'
assert not OUT.exists(),'this source-purpose CPU entry is already consumed'
with (HERE/'SOURCE_CPU_ENTRY_CONSUMED_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(source_only=True,no_models=True),f)
checks=[]
def ok(name,value=True):
 assert value,name;checks.append(name)
def refuse(name,f):
 try:f()
 except (ValueError,KeyError,AssertionError):ok(name);return
 raise AssertionError('negative case accepted: '+name)
def tree(path):return ast.parse(Path(path).read_bytes())
def function(t,name):return next(n for n in t.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name==name)
try:
 import torch
 import native87R5_frozen_acceptance_contract_v1 as c
 import native87R5_frozen_acceptance_driver_v1 as d
 from native87R5_frozen_single_sdk_entry_unused_once import validate_evidence,contained
 from native87R5_eval_environment_v1 import environment
 T=HERE.parents[1];N=T/'H1_STEP270_THREE_GPU_OWN_FUDAN_NATIVE_V87_20261027';B=N/'payloads_r5/h1'
 # Strict closed native role fixtures, not runtime reports or qualification.
 finals={k:dict(SHA=ch*64,bytes=111,formal_manifest_passed=True,twohost_complete_SHA=True,policy_updates=6,world_updates=700,updates=70) for k,ch in [('h1','a'),('recovery','b')]}
 models={k:dict(passed=True,source_SHA=c.SOURCE_SHA,frozen_bootstrap=dict(Adam=832460),native_fullstate_finite=True,NATIVE_CONTRACT_strict_type_and_values=True,native_modules=dict(WM_Pi_Critic_strict_CPU_state_load=True),final=v) for k,v in finals.items()}
 cpu=dict(original_fees=dict(passed=True),original_canonical_cost_settled=True,models=models,initial_model_load_records=[dict(role=k+'_native_FINAL',producer_SHA=v['SHA'],completed=True,initial_load_attempted=True) for k,v in finals.items()])
 collection=dict(authority72=dict(all_authority72_owner_children_actual_out=True,canonical_active_segment=None,canonical_path=c.CANONICAL,original_locks=[dict(actual_fcntl_free=True)]*2),native_H1_method_fullstate={k:[v] for k,v in finals.items()},nodes={k:dict(node_terminal=dict(row=dict(terminal_all_own_children_waited=True,original_error=False,errors=[],final=dict(passed=True,final=dict(SHA=v['SHA']))))) for k,v in finals.items()})
 def event(recovery=0,landing=0,cross=0):return dict(schema='completed_control_goal_events_v1',diagnostic_valid=True,num_envs=4096,environment_control_transitions=100*4096,complete_control_rows=100,events=dict(recovery_count=recovery,landing_count=landing,takeoff_count=999),both_leading_edges_cross_event_count=cross)
 ok('zero_or_missing_events_fixed_h1_diagnostic',c.select_source(cpu,collection,{})['selected_key']=='h1')
 ok('takeoff_alone_does_not_select_recovery',c.select_source(cpu,collection,dict(recovery=event()))['selected_key']=='h1')
 ok('original_recovery_priority_predeclared',c.select_source(cpu,collection,dict(h1=event(0,20,100),recovery=event(1,0,0)))['selected_key']=='recovery')
 ok('exact_tie_prefers_h1',c.select_source(cpu,collection,{k:event(1,1,1) for k in models})['selected_key']=='h1')
 bad=event(1);bad['num_envs']=20000
 ok('wrong_event_denominator_diagnostic_only',c.select_source(cpu,collection,dict(recovery=bad))['selected_key']=='h1')
 badcpu=copy.deepcopy(cpu);badcpu['original_fees']['passed']=False
 refuse('unsettled_fees_refused',lambda:c.select_source(badcpu,collection,{}))
 badcpu=copy.deepcopy(cpu);badcpu['initial_model_load_records']=[]
 refuse('missing_initial_whole_FINAL_CPU_refused',lambda:c.select_source(badcpu,collection,{}))
 badcol=copy.deepcopy(collection);badcol['native_H1_method_fullstate']['h1'][0]['formal_manifest_passed']=False
 refuse('partial_not_formal_FINAL_refused',lambda:c.select_source(cpu,badcol,{}))
 one=copy.deepcopy(cpu);one['models'].pop('h1')
 refuse('zero_event_missing_h1_does_not_switch_source',lambda:c.select_source(one,collection,{}))
 ok('independent_event_qualified_recovery_retained',c.select_source(one,collection,dict(recovery=event(1)))['selected_key']=='recovery')
 # Load/architecture/normalizer interface only; there is no actor forward.
 class SpyPolicy:
  calls=[]
  def __init__(self,obs,goal,**kw):self.__class__.calls.append((obs,goal,kw));self.state={}
  def load_state_dict(self,saved,strict):assert strict;self.state={k:v.clone() for k,v in saved.items()}
  def state_dict(self):return self.state
  def to(self,device):assert device=='cpu';return self
  def eval(self):return self
  def parameters(self):return []
 saved={p+'.'+k:torch.zeros(dim) if k=='mean' else torch.ones(dim) for p,dim in [('obs_norm',86),('goal_norm',1460)] for k in ('mean','var')}
 saved.update({'obs_norm.count':torch.tensor(4096.),'goal_norm.count':torch.tensor(4096.)})
 ck=dict(UniSuperMimic_test_contract=d.CONTRACT,UniSuperMimic_publication=dict(policy_updates=6),UniSuperMimic_H1_test=dict(args=dict(hist=10,goal_frames=10,z_dim=32,amp='none',test_hidden_dims=None,policy_hidden=[2048,1024,512,256]),pi=saved))
 before=torch.get_rng_state().clone();pi=d.make_frozen_policy(ck,SpyPolicy,'cpu')
 ok('Pi_only_constructor_shape_saved_norm_literal',SpyPolicy.calls[-1]==(86,1460,dict(hist=10,z_dim=32,num_joints=6,hidden=[2048,1024,512,256])) and d.literal(pi.state_dict(),saved))
 ok('loader_constructor_restores_CPU_rng',torch.equal(before,torch.get_rng_state()))
 bad=copy.deepcopy(ck);bad['UniSuperMimic_test_contract']['obs_dim']=128
 refuse('old_native86_contract_refused_before_Pi_constructor',lambda:d.make_frozen_policy(bad,SpyPolicy,'cpu'))
 bad=copy.deepcopy(ck);bad['UniSuperMimic_H1_test']['pi']['goal_norm.mean']=torch.zeros(73)
 refuse('old_goal_normalizer_refused',lambda:d.make_frozen_policy(bad,SpyPolicy,'cpu'))
 bad=copy.deepcopy(ck);bad['UniSuperMimic_H1_test']['pi']['obs_norm.var'][0]=float('nan')
 refuse('nonfinite_saved_norm_refused',lambda:d.make_frozen_policy(bad,SpyPolicy,'cpu'))
 h=torch.arange(860.).reshape(1,10,86);obs=torch.arange(86.).reshape(1,86)
 ok('fresh_history_all_ten_padding_original_collect_semantics',torch.equal(d.fresh_history(h,obs,torch.tensor([0])),obs[:,None].expand_as(h)))
 ok('history_shift_exact_original_collect_semantics',torch.equal(d.fresh_history(h,obs,torch.tensor([1])),torch.cat((h[:,1:],obs[:,None]),1)))
 # Newly obtained actual SDK source, no SDK import or scene construction.
 term=N/'saved_actual_SDK_source/termination_manager_actual_for_future_frozen_N1_87.py.txt'
 contract=d.termination_cache_contract(term)
 ok('actual_TerminationManager_SHA_and_cached_get_term_AST',contract['available'] and contract['values_attribute']=='_term_dones' and contract['source_SHA']=='cb6333f11fa6472f7d8034bae9835714e83ae3edde97894b767f1351a7eea99d')
 from types import SimpleNamespace
 matrix=torch.tensor([[True,False]])
 env=SimpleNamespace(termination_manager=SimpleNamespace(_term_names=['closure','time_out'],_term_dones=matrix))
 frame=d.ActualFrames(env,io.StringIO(),lambda x:x,contract)
 ok('cached_exact_terms_without_recompute',frame.terms()['values']==dict(closure=True,time_out=False))
 env.termination_manager._term_dones=torch.zeros(2,2,dtype=torch.bool)
 refuse('wrong_actual_term_cache_shape_refused',frame.terms)
 ok('original_environment_function_AST_exact',ast.dump(function(tree(B/'three_slot_common_v1.py'),'environment'))==ast.dump(function(tree(HERE/'native87R5_eval_environment_v1.py'),'environment')))
 # Compare contract by the exact dict keyword AST without importing fullsave.
 scope={};assignment=next(n for n in tree(B/'source/native_finalization_own_v3.py').body if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='NATIVE_CONTRACT' for x in n.targets));exec(compile(ast.Module(body=[assignment],type_ignores=[]),'native_contract_AST_only','exec'),scope)
 ok('strict_native127_contract_values_match_pinned_finalization',d.literal(d.CONTRACT,scope['NATIVE_CONTRACT']))
 allcode='\n'.join((HERE/f).read_text('utf8') for f in ['native87R5_frozen_single_sdk_entry_unused_once.py','native87R5_frozen_acceptance_driver_v1.py'])
 calls=[n for n in ast.walk(ast.parse(allcode)) if isinstance(n,ast.Call)]
 badcalls=[n for n in calls if (isinstance(n.func,ast.Attribute) and (n.func.attr in ('collect','learn','train','wm_update','policy_update','backward','zero_grad') or (n.func.attr=='update' and isinstance(n.func.value,ast.Attribute) and n.func.value.attr in ('obs_norm','goal_norm')))) or (isinstance(n.func,ast.Name) and n.func.id in ('SuperMimicLearner','WorldModel','OnPolicyRunner'))]
 ok('no_learner_collect_optimizer_WM_training_calls',not badcalls)
 run=function(tree(HERE/'native87R5_frozen_acceptance_driver_v1.py'),'run_single_case')
 breaks=[n for n in ast.walk(run) if isinstance(n,ast.If) and any(isinstance(x,ast.Break) for x in n.body)]
 ok('only_original_done_stops_control_loop',len(breaks)==1 and ast.unparse(breaks[0].test)=='bool(done[0])')
 ok('fixed500control_loop_no_retry',any(isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='range' and len(n.args)==1 and isinstance(n.args[0],ast.Constant) and n.args[0].value==500 for n in ast.walk(run)))
 ok('all_eval_Python_AST_parse',all(isinstance(tree(p),ast.Module) for p in HERE.glob('*.py')))
 refuse('path_escape_refused',lambda:contained(HERE,'../forbidden'))
 ok('no_actual_model_policy_SDK_or_CUDA_executed',not torch.cuda.is_initialized())
 result=dict(passed=True,checks=len(checks),check_names=checks,only_new_purpose_metadata_and_source_API_CPU=True,fixture_only=True,actual_N1_SDK_or_physics_or_policy_forward_executed=False,real_model_opened_or_hashed=False,actual_frozen_acceptance='PENDING formalR5_FINAL+wholeCPU+originalfeeallout+freshN1SDK+newpurposeeval',errors=[])
 with OUT.open('x',encoding='utf8') as f:json.dump(result,f,indent=2,allow_nan=False)
 print(json.dumps(dict(passed=True,checks=len(checks),fixture_only=True)))
except BaseException:
 with (HERE/'SOURCE_CPU_ORIGINAL_ERROR.json').open('x',encoding='utf8') as f:json.dump(dict(passed=False,checks=checks,error=traceback.format_exc(),fixture_only=True),f,indent=2)
 raise
