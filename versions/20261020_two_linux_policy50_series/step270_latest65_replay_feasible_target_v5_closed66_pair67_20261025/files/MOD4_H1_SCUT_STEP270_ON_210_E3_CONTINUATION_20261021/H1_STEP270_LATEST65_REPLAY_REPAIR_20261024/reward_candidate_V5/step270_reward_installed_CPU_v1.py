"""New reward-only term checks. Prior V4/native/query evidence is reused."""
from pathlib import Path
import ast,hashlib,importlib.util,json,sys,types
import torch
def load(path,name):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def check(B,sdk_reward_path=None):
 B=Path(B);rng=torch.get_rng_state().clone()
 reward=load(B/'h1_step270_path_reward_v1.py','airborne_target_v5_cpu')
 order=['left_crank','left_hip','right_crank','right_hip']
 lower=torch.tensor([-1.2,-.5,-1.2,-.5]);upper=torch.tensor([.9,.5,.9,.5])
 pure=reward.infeasible_leg_target_cost
 a=torch.tensor([[0.,0.,0.,0.],[2.,0.,2.,0.],[4.,0.,4.,0.],[6.,0.,6.,0.],[-6.,0.,-6.,0.],[0.,6.,0.,6.]])
 before=a.clone()
 cost=pure(raw_actions=a,scale=.5,offset=torch.zeros_like(a),lower=lower,upper=upper,diff_min=-1.0843,diff_max=.85)
 assert cost[0]==0 and 0<cost[1]<cost[2]<cost[3] and (cost[4:]>0).all() and torch.equal(a,before)
 grad=a[3:4].clone().requires_grad_();pure(raw_actions=grad,scale=.5,offset=0.,lower=lower,upper=upper,diff_min=-1.0843,diff_max=.85).sum().backward()
 assert (grad.grad[:,[0,2]]>0).all()
 # The wrapper reads the delayed term, never the unrelated current actor input.
 n=10;raw=a[3].repeat(n,1);term=types.SimpleNamespace(raw_actions=raw,_scale=.5,_offset=torch.zeros(n,4),_joint_names=order,diff_min=-1.0843,diff_max=.85)
 phase=types.SimpleNamespace(attempt=torch.ones(n,dtype=torch.bool),air_ticks=torch.ones(n,dtype=torch.long),landed=torch.zeros(n,dtype=torch.bool),crossed=torch.zeros(n,2,dtype=torch.bool),last_measured={'step_wheel_min':torch.zeros(n,2,3)},request_for_action=torch.ones(n,dtype=torch.bool))
 phase.last_measured['step_wheel_min'][:,:,2]=.02
 phase.air_ticks[0]=0;phase.attempt[1]=False;phase.landed[2]=True;phase.crossed[3]=True;phase.last_measured['step_wheel_min'][4,0,2]=0.;phase.request_for_action[5]=False;phase.crossed[6,0]=True
 phase.last_measured['step_wheel_min'][7,:,2]=.0001
 env=types.SimpleNamespace(h1_phase=phase,action_manager=types.SimpleNamespace(get_term=lambda name:term if name=='legs' else None),current_actor_input=torch.zeros(n,6),num_envs=n)
 task=types.ModuleType('mod4_task');task.LEG_ORDER=order;task.CONTRACT={'joints':{name:{'limits_si':[float(lower[i]),float(upper[i])]} for i,name in enumerate(order)}}
 adapter=types.ModuleType('h1_takeoff_progress_environment_v2');adapter.tensor=lambda x:x.torch if hasattr(x,'torch') else x
 manager=types.ModuleType('isaaclab.managers');manager.RewardTermCfg=lambda **kw:types.SimpleNamespace(**kw)
 saved={m.__name__:sys.modules.get(m.__name__) for m in (task,adapter,manager)}
 for m in (task,adapter,manager):sys.modules[m.__name__]=m
 try:
  snapshot={k:v.clone() for k,v in vars(phase).items() if isinstance(v,torch.Tensor)};raw_before=raw.clone();offset_before=term._offset.clone()
  actual=reward.airborne_leg_target_overdrive_rate(env)
  expected=torch.tensor([0.,0.,0.,0.,0.,float(cost[3]),float(cost[3]),0.,float(cost[3]),float(cost[3])])
  assert torch.allclose(actual,expected,atol=1e-6,rtol=0)
  assert torch.equal(raw,raw_before) and torch.equal(term._offset,offset_before) and all(torch.equal(getattr(phase,k),v) for k,v in snapshot.items())
  terms=types.SimpleNamespace()
  for name in ('h1_control_events','h1_scut_fudan_air_wheel_zero_torque','h1_scut_fudan_leg_tuck','h1_scut_fudan_wheel_below_base','h1_scut_fudan_push_vz'):setattr(terms,name,types.SimpleNamespace(weight=1.,func=lambda env:None,params={}))
  reward.configure(types.SimpleNamespace(rewards=terms));cfg=terms.h1_step270_airborne_leg_target_overdrive
  assert cfg.func is reward.airborne_leg_target_overdrive_rate and cfg.weight==-.05 and cfg.params=={}
  assert terms.h1_scut_fudan_leg_tuck.weight==1.7
  sdk_actual=None
  if sdk_reward_path is not None:
   p=Path(sdk_reward_path);tree=ast.parse(p.read_text('utf8'));cls=next(x for x in tree.body if isinstance(x,ast.ClassDef) and x.name=='RewardManager');fn=next(x for x in cls.body if isinstance(x,ast.FunctionDef) and x.name=='compute');ns={'torch':torch}
   exec(compile(ast.Module(body=[fn],type_ignores=[]),str(p),'exec'),ns)
   rm=types.SimpleNamespace(_env=env,_term_names=['overdrive'],_term_cfgs=[cfg],_reward_buf=torch.zeros(n),_step_reward=torch.zeros(n,1),_episode_sums={'overdrive':torch.zeros(n)})
   sdk_actual=ns['compute'](rm,.01);assert torch.allclose(sdk_actual,expected*(-.05)*.01,atol=1e-7,rtol=0)
  count=20000
  many=torch.linspace(-6,6,count)[:,None].repeat(1,4)
  out=pure(raw_actions=many,scale=.5,offset=torch.zeros_like(many),lower=lower,upper=upper,diff_min=-1.0843,diff_max=.85)
  assert out.shape==(count,) and out.dtype==torch.float32 and torch.isfinite(out).all() and (out>=0).all()
 finally:
  for name,m in saved.items():
   if m is None:sys.modules.pop(name,None)
   else:sys.modules[name]=m
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 return dict(passed=True,new_airborne_infeasible_target_reward_only=True,weight=-.05,original_tuck_weight=1.7,cost_examples=cost.tolist(),phase_cases=['ground_zero','no_attempt_zero','landed_zero','both_crossed_zero','one_wheel_ground_zero','request_expired_still_active','one_crossed_still_active','near_ground_zero','airborne_active','airborne_active'],synthetic_scalar_gradient_points_back_toward_feasible_targets=True,applied_delayed_action_read_without_mutation=True,vectorized_float32_environments=20000,actual_SDK_reward_compute_tested=sdk_reward_path is not None,actual_SDK_compute_control_rewards=sdk_actual.tolist() if sdk_actual is not None else None,previous_V4_native_query_strict_goal_evidence_reused_not_reexecuted=True,no_actor_optimizer_RNG_GPU_command_goal_action_or_physics_write=True,not_policy_outcome_or_skill_proof=True)

