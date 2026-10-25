"""Actual CPU source/RewardManager-interface checks; never load an actor, scene or GPU."""
from pathlib import Path
import ast,hashlib,importlib.util,json,sys,time,traceback,types
import numpy as np
import torch
S=Path(__file__).resolve().parent;T=S.parent;C=S/'candidate_v4';R=S/'reports'
P=T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V74B_20261026/payloads/h1'
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def put(p,v):
 with Path(p).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def main():
 torch.set_num_threads(2);rng=torch.get_rng_state().clone();sys.path.insert(0,str(C))
 checker=load('V8_reward_CPU_checker',C/'step270_reward_installed_CPU_v1.py')
 reference=P/'reference_sources/V5_h1_step270_path_reward_v1.py'
 reward_result=checker.check(C,reference_path=reference)
 assert reward_result['sampled_excess_CPU']['passed'] and not reward_result['actual_installed_sampled_excess_SDK_compute_tested']
 sampler=load('V8_sampler_CPU_checker',C/'sampling_acceleration_installed_CPU_v2.py')
 sampling_result=sampler.check(C,'h1');assert sampling_result['passed'] and sampling_result['V8_reward_publication_AST']['passed']
 reward=load('V8_actual_reward_functions',C/'h1_step270_path_reward_v1.py')
 trace_text=(C/'h1_production_control_prefix_trace_v1.py').read_text('utf8');tree=ast.parse(trace_text)
 cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='H1ControlPrefixTrace')
 install=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='install')
 step=next(n for n in install.body if isinstance(n,ast.FunctionDef) and n.name=='step')
 n=20000;actions=torch.zeros(n,6);actions[:,0]=106.;actions[:,4]=1000.;before=actions.clone()
 env=types.SimpleNamespace(num_envs=n,device=torch.device('cpu'),h1_stepping=False)
 recorded_errors=[];persist=[];forwarded=[]
 witness=types.SimpleNamespace(env=env,frame=None,observed={'policy35':torch.zeros(n,35),'critic38':torch.zeros(n,38)},rows=[],total=0,folder=Path('CPU_fixture_no_files_written'),persist=lambda:persist.append(True))
 result_holder={}
 def original_step(value):
  assert value is actions and torch.equal(value,before)
  assert env._h1_sampled_actions_for_reward.data_ptr()!=actions.data_ptr() and torch.equal(env._h1_sampled_actions_for_reward,actions)
  forwarded.append(value.data_ptr());env.h1_stepping=True
  try:
   excess=reward.sampled_leg_action_excess_rate(env)
   expected=torch.full((n,),2500.);assert torch.equal(excess,expected)
   witness.frame={'executed6':value.clamp(-6.,6.)}
   result=({'policy':torch.zeros(n,35)},torch.full((n,),.5)-.001*.01*excess,torch.zeros(n,dtype=torch.bool),{})
   result_holder['value']=result;return result
  finally:env.h1_stepping=False
 ns={'self':witness,'old_step':original_step,'torch':torch,'np':np,'time':time,'traceback':traceback,'put':lambda p,v:recorded_errors.append((str(p),v))}
 exec(compile(ast.fix_missing_locations(ast.Module(body=[step],type_ignores=[])),str(C/'h1_production_control_prefix_trace_v1.py'),'exec'),ns)
 result=ns['step'](actions)
 assert result is result_holder['value'] and len(forwarded)==1 and torch.equal(actions,before)
 assert env._h1_sampled_actions_for_reward is None and witness.total==1 and len(witness.rows)==1
 assert np.array_equal(witness.rows[0]['raw_sampled6'],before.numpy()) and np.array_equal(witness.rows[0]['executed6'],before.clamp(-6.,6.).numpy())
 assert np.allclose(witness.rows[0]['total_reward'],.475,atol=1e-7,rtol=0)
 def failed_original(value):
  assert value is actions and env._h1_sampled_actions_for_reward is not None
  raise RuntimeError('Expected_CPU_fixture_old_step_error')
 ns['old_step']=failed_original
 try:ns['step'](actions)
 except RuntimeError as exc:assert str(exc)=='Expected_CPU_fixture_old_step_error'
 else:raise AssertionError('Expected failure did not propagate')
 assert env._h1_sampled_actions_for_reward is None and len(recorded_errors)==1 and len(persist)==1 and witness.total==1
 # Reject unrelated reward changes and any change to the original forwarded action.
 fixtures=S/'negative_source_fixtures_v4';fixtures.mkdir();negative=[]
 base=(C/'h1_step270_path_reward_v1.py').read_text('utf8')
 for name,text in [('weight',base.replace('sampled_leg_action_excess_weight=-.001','sampled_leg_action_excess_weight=-.002')),('physical_gate',base.replace('takeoff_gate_full_front_x_m=.25','takeoff_gate_full_front_x_m=.20')),('wrong_action_slice',base.replace('raw[:,:4].abs()','raw[:,4:].abs()'))]:
  assert text!=base;p=fixtures/('reward_'+name+'.py');p.write_text(text,'utf8')
  try:checker.allowlist(p,reference)
  except AssertionError:negative.append('reward_'+name)
  else:raise AssertionError(name)
 for name,text in [('forward',trace_text.replace('old_step(actions)','old_step(actions.clamp(-5.,5.))')),('missing_clear',trace_text.replace('self.env._h1_sampled_actions_for_reward=None','self.env._h1_sampled_actions_for_reward=raw'))]:
  assert text!=trace_text;p=fixtures/('trace_'+name+'.py');p.write_text(text,'utf8')
  try:sampler.validate_V8_trace_reward_publication_only(p)
  except AssertionError:negative.append('trace_'+name)
  else:raise AssertionError(name)
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 report=dict(epoch=time.time(),passed_CPU_source_only=True,reward_CPU=reward_result,sampling_CPU=sampling_result,
  trace_forward_and_readonly_raw_wiring=dict(passed=True,environments=n,same_original_actions_object_values_and_output_tuple=True,actual_execution_clip6_retained_in_fixture=True,only_new_manager_reward_difference=True,raw_field_cleared_on_success_and_expected_error=True,original_failed_control_not_claimed_complete=True,no_file_PT_or_policy_forward=True),
  negative_source_cases_rejected=negative,all_prior_reward_phase_target_release_overdrive_and_lossless_tests_retained=True,
  actual_installed_SDK_reward_and_new_term_compute_still_pending=True,actual_GPU_learning_effect_pending=True,
  no_current74_or_old_root_training_change=True,candidate_files={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in C.glob('*.py')},
  no_actor_model_optimizer_scene_PhysX_GPU_remote_or_budget_action=True)
 put(R/'V8_SAMPLED_LEG_EXCESS_AND_TRACE_CPU_V4_ACTUAL.json',report)
 print(json.dumps(dict(passed_CPU_source_only=True,trace_environments=n,negative_cases=len(negative),actual_installed_SDK_and_learning_still_pending=True)))
if __name__=='__main__':
 try:main()
 except BaseException:
  put(R/('V8_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(epoch=time.time(),error=traceback.format_exc(),no_same_once_retry_or_training_action=True));raise
