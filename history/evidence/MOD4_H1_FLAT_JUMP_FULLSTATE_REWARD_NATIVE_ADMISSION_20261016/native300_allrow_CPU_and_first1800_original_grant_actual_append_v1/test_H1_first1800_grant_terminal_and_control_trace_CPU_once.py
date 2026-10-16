"""CPU-only negative grants and stochastic-action transparency of the prepared trace."""
from pathlib import Path
import ast,json,time,hashlib,sys,types,importlib.util,os
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
D=Path(__file__).resolve().parent;P=D/'first1800_prepared_learning_v1';R=D/'reports';torch.set_num_threads(2)
def load(name,p):
 spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def main():
 assert not (R/'H1_FIRST1800_GRANT_TERMINAL_AND_TRACE_CPU_ACTUAL.json').exists();original_rng=torch.get_rng_state().clone();ns={};tree=ast.parse((P/'h1_first1800_original_canonical_owner_v1.py').read_text('utf8'));exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('ready','terminal')],type_ignores=[]),'actual_prepared_owner_functions','exec'),ns)
 cfg=dict(source_SHA='a'*64,native_CPU_report_SHA='b'*64,local_CPU_receipt_SHA='c'*64);good=dict(actual_native_CPU_local_model_admitted=True,source_SHA=cfg['source_SHA'],native_CPU_report_SHA=cfg['native_CPU_report_SHA'],local_CPU_receipt_SHA=cfg['local_CPU_receipt_SHA'],target_payload_exact=True,target_actual_validation_fcntl_held=True);assert ns['ready'](good,cfg)
 rejected=0
 for k in good:
  bad=dict(good);bad[k]=False if isinstance(bad[k],bool) else 'd'*64;assert not ns['ready'](bad,cfg),k;rejected+=1
 assert not ns['ready']({**good,'original_error':True},cfg);rejected+=1
 for row in (dict(returncode=0),dict(returncode=0,node_terminal_after_actual_children_exit=True),dict(returncode=None,node_terminal_after_actual_children_exit=True,actual_all_children_waited=True)):assert not ns['terminal'](row)
 assert ns['terminal'](dict(returncode=1,node_terminal_after_actual_children_exit=True,actual_all_children_waited=True))
 trace_module=load('owned_h1_trace_fixture',P/'h1_production_control_prefix_trace_v1.py');N=4;K=24;out=D/('CPU_TRACE_FIXTURE_'+str(time.time_ns()));out.mkdir();T=types.SimpleNamespace
 phase=T(request_for_action=torch.zeros(N,dtype=torch.bool),event_control=torch.zeros(N),takeoff_count=torch.zeros(N,dtype=torch.long),landing_count=torch.zeros(N,dtype=torch.long),recovery_count=torch.zeros(N,dtype=torch.long));robot=T(data=T(root_state_w=torch.zeros(N,13),joint_pos=torch.zeros(N,30),joint_vel=torch.zeros(N,30),applied_torque=torch.zeros(N,30)));env=T(h1_phase=phase,_sensor_mild=T(episode=torch.zeros(N,dtype=torch.long)),_integrated_contact=T(history=torch.zeros(N,3,2,3),impulse=torch.zeros(N,2)),h1_reward_readout_scale=.01,scene={'robot':robot});calls=dict(act=0,step=0,save=0);obs={'policy':torch.zeros(N,35),'critic':torch.zeros(N,38)}
 def term():return torch.zeros(N,dtype=torch.bool)
 def reward(dt):return torch.ones(N)
 env.termination_manager=T(compute=term);env.reward_manager=T(compute=reward,_term_names=['h1_control_events'],_step_reward=torch.zeros(N,1));env.action_manager=T(action=torch.zeros(N,6));old_module=sys.modules.get('mod4_task');sys.modules['mod4_task']=T(closure_errors=lambda e:{'closure':torch.zeros(N)},mimic_errors=lambda e:{'mimic':torch.zeros(N)})
 def act(o):calls['act']+=1;return torch.randn(N,6)
 def step(a):calls['step']+=1;env.action_manager.action.copy_(a.clamp(-6,6));env.termination_manager.compute();r=env.reward_manager.compute(.01);return obs,r,torch.zeros(N,dtype=torch.bool),{}
 def save(path):calls['save']+=1;torch.save({'exact_fixture_tensor':torch.ones(2)},path)
 vec=T(unwrapped=env,step=step);runner=T(env=vec,alg=T(act=act),save=save);trace=trace_module.H1ControlPrefixTrace(runner,out);trace.install();seeded=torch.get_rng_state().clone();baseline=[]
 for _ in range(K):baseline.append(torch.randn(N,6))
 expected_next=torch.get_rng_state().clone();torch.set_rng_state(seeded)
 try:
  actual=[]
  for _ in range(K):a=runner.alg.act(obs);actual.append(a.clone());vec.step(a)
  assert all(torch.equal(a,b) for a,b in zip(actual,baseline)) and torch.equal(torch.get_rng_state(),expected_next);assert calls==dict(act=24,step=24,save=1);assert trace.total==24 and len(trace.index)==1;trace.persist();assert len(trace.index)==1
 finally:
  if old_module is None:sys.modules.pop('mod4_task',None)
  else:sys.modules['mod4_task']=old_module
  torch.set_rng_state(original_rng)
 assert torch.equal(torch.get_rng_state(),original_rng) and not torch.cuda.is_initialized()
 files=[dict(path=str(q.resolve()),bytes=q.stat().st_size,SHA=hashlib.sha256(q.read_bytes()).hexdigest()) for q in out.iterdir() if q.is_file()];report=dict(epoch=time.time(),prepared_only_no_target_upload_GPU_or_learning=True,negative_ready_grants_rejected=rejected,terminal_requires_actual_all_own_children_waited_and_exit=True,original_error_exit_allowed_to_settle_actual_cost_not_mark_success=True,stochastic24draws_equal_without_trace=True,trace_actor_step_save_counts=calls,no_extra_observation_actor_draw_or_optimizer=True,global_CPU_RNG_restored=True,no_CUDA=True,fixture_is_mock_not_actual_RSL_or_SDK_native=True,fixture_files=files)
 (R/'H1_FIRST1800_GRANT_TERMINAL_AND_TRACE_CPU_ACTUAL.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(report))
if __name__=='__main__':main()
