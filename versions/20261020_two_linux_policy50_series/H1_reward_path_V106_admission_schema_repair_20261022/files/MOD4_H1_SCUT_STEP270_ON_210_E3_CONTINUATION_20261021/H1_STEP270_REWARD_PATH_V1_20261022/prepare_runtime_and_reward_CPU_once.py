from pathlib import Path
import ast,hashlib,json,time,traceback,importlib.util,sys
import numpy as np
import torch
torch.set_num_threads(2)
B=Path(__file__).resolve().parent;T=B.parent;R=B/'reports';R.mkdir(exist_ok=True)
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(name,v):
 with (R/name).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,ensure_ascii=False)
def main():
 old=T/'H1_STEP270_E3_BOUNDED_TRACE_PAIR_V15_20261022/payloads/h1/h1_step270_sdk_runtime_candidate.py'
 s=old.read_text('utf8');assert H(old)=='352d614f4d85b77533cbe25f676aff49cb2750aecbd3474c0763cf6b73319610'
 replacements={
 "from step270_goal_and_scut_rates_candidate import Step270Events":"from step270_goal_and_scut_rates_candidate import Step270Events\nfrom h1_step270_path_reward_v1 import path_increment,configure as configure_path_reward",
 "crossing=(self.previous_front<edge)&(hi[:,:,0]>=edge);":"reward_previous_front=self.previous_front.clone();reward_edge_before=self.goal.edge.clone()\n        crossing=(self.previous_front<edge)&(hi[:,:,0]>=edge);",
 "self.last_measured=dict(step_wheel_min=lo.clone()":"reward=path_increment(previous_front=reward_previous_front,current_front=hi[:,:,0],wheel_bottom=lo[:,:,2],origin_x=orig[:,0],active=self.goal.attempt&~self.goal.landed,airborne=airborne,launched=self.goal.launched,clean_upright=(kw['nonwheel_max_N']<=1)&(kw['roll'].abs()<.3)&(kw['pitch'].abs()<.3),vx=root[:,7],takeoff=out['takeoff'],edge_event=self.goal.edge&~reward_edge_before,landing=out['landing'],recovery=out['recovery'],previous_joint_potential=self.last_measured.get('reward_joint_potential'))\n        self.progress_control+=reward['total']\n        self.last_measured=dict(reward_joint_potential=reward['next_joint_potential'].clone(),step_wheel_min=lo.clone()",
 "task.ground_height=ground_height\n    return configure_scene(cfg)":"configure_path_reward(cfg)\n    task.ground_height=ground_height\n    return configure_scene(cfg)"}
 for needle,new in replacements.items():assert s.count(needle)==1,needle;s=s.replace(needle,new)
 dest=B/'h1_step270_sdk_runtime_candidate.py';dest.write_text(s,encoding='utf8');ast.parse(s)
 # Strict source allowlist: reverse only these four replacements restores every
 # old AST node, including command publisher, events, resets, guards and saves.
 reverse=s
 for needle,new in reversed(list(replacements.items())):assert reverse.count(new)==1;reverse=reverse.replace(new,needle)
 assert ast.dump(ast.parse(reverse),include_attributes=False)==ast.dump(ast.parse(old.read_text('utf8')),include_attributes=False)
 spec=importlib.util.spec_from_file_location('reward',B/'h1_step270_path_reward_v1.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 rng=torch.get_rng_state().clone();tests=[]
 def row(label,prev,curr,h,oldjoint=None,active=True,**events):
  f=lambda v:torch.tensor([v],dtype=torch.float64)
  b=lambda v:torch.tensor([v],dtype=torch.bool)
  r=m.path_increment(previous_front=f([prev,prev]),current_front=f([curr,curr]),wheel_bottom=f([h,h]),origin_x=f(0),active=b(active),airborne=b(True),launched=b(True),clean_upright=b(True),vx=f(events.pop('vx',.8)),takeoff=b(events.pop('takeoff',False)),edge_event=b(events.pop('edge',False)),landing=b(events.pop('landing',False)),recovery=b(events.pop('recovery',False)),previous_joint_potential=None if oldjoint is None else f(oldjoint))
  assert all(torch.isfinite(v).all() for v in r.values());tests.append(dict(case=label,**{k:float(v) for k,v in r.items()}));return r
 assert float(row('uninitialized_reset_no_free_progress',-1e6,.2,.3)['total'])==0
 assert float(row('stationary_far_vertical_jump',0,0,.4,0)['total'])==0
 forward=row('forward_on_ground',0,.05,0,0);assert float(forward['total'])>0
 backward=row('reverse_on_ground',.05,0,0,0);assert abs(float(forward['total']+backward['total']))<1e-12
 high=row('forward_near_edge_clear',.2,.3,.27,.4)
 low=row('forward_near_edge_low',.2,.3,.10,.4*(.10/.27)**2)
 assert float(high['total'])>float(low['total'])>0
 back=row('reverse_same_clearance_cancels',.3,.2,.27,float(high['next_joint_potential']))
 assert abs(float(high['total']+back['total']))<1e-12
 assert float(row('normal_rows_zero',.2,.3,.27,.4,active=False)['total'])==0
 assert float(row('vertical_takeoff_no_forward_bonus',0,0,.3,0,takeoff=True,vx=0)['total'])==0
 assert float(row('forward_takeoff_small_bonus',0,0,.3,0,takeoff=True,vx=.8)['strict_events'])==.25
 for name,key,expected in [('actual_edge','edge',6),('actual_landing','landing',8),('actual_recovery','recovery',16)]:assert float(row(name,0,0,0,0,**{key:True})['strict_events'])==expected
 f=lambda v:torch.tensor([v],dtype=torch.float64);b=lambda v:torch.tensor([v])
 for name,vx,vy,request,expected in [('forward',.8,0,True,1),('reverse',-.8,0,True,0),('normal',.8,0,False,0)]:
  v=m.requested_forward_rate(request=b(request),attempt=b(True),landed=b(False),vx=f(vx),vy=f(vy),roll=f(0),pitch=f(0));assert float(v)==expected;tests.append(dict(case=name+'_dense',value=float(v)))
 # Run actual candidate configure against typed stand-ins; SDK isolation is
 # checked separately at installation, not claimed by these CPU stand-ins.
 import types
 fake=types.ModuleType('isaaclab.managers');fake.RewardTermCfg=lambda **kw:types.SimpleNamespace(**kw)
 saved=sys.modules.get('isaaclab.managers');sys.modules['isaaclab.managers']=fake
 cfg=types.SimpleNamespace(rewards=types.SimpleNamespace(**{k:types.SimpleNamespace(weight=v) for k,v in [('h1_control_events',1),('h1_scut_fudan_air_wheel_zero_torque',20),('h1_scut_fudan_leg_tuck',1.7),('h1_scut_fudan_wheel_below_base',2)]}))
 try:m.configure(cfg)
 finally:
  if saved is None:del sys.modules['isaaclab.managers']
  else:sys.modules['isaaclab.managers']=saved
 assert cfg.rewards.h1_control_events.weight==0 and cfg.rewards.h1_scut_fudan_air_wheel_zero_torque.weight==.5
 assert cfg.rewards.h1_step270_path_progress.weight==1 and cfg.rewards.h1_step270_requested_forward.weight==3
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 D=T/'H1_STEP270_REPLAY_DIAG_20261022_V105';a=np.load(D/'SELECTED_RECORDED_MOTION.npz');k=np.load(D/'RECORDED_KINEMATIC_RECONSTRUCTION.npz')
 replay=[]
 for eid in (1912,17789,16932):
  col=int(np.flatnonzero(a['env_ids']==eid)[0]);front=k['wheel_max'][:,col,:,0];bottom=k['wheel_min'][:,col,:,2];origin=float(a['env_origins'][col,0]);root=a['root13'][:,col];lastjoint=None;potential=0.;dense=0.
  for i in range(1,len(front)):
   assert a['episode'][i,col]==a['episode'][i-1,col] and not a['done'][i,col]
   f=lambda v:torch.as_tensor(v,dtype=torch.float64).reshape(1,-1)
   rr=m.path_increment(previous_front=f(front[i-1]),current_front=f(front[i]),wheel_bottom=f(bottom[i]),origin_x=torch.tensor([origin]),active=torch.tensor([bool(a['public_request'][i,col])]),airborne=torch.tensor([True]),launched=torch.tensor([True]),clean_upright=torch.tensor([True]),vx=torch.tensor([float(root[i,7])]),takeoff=torch.tensor([False]),edge_event=torch.tensor([False]),landing=torch.tensor([False]),recovery=torch.tensor([False]),previous_joint_potential=lastjoint)
   potential+=float(rr['total']);lastjoint=rr['next_joint_potential']
   # Diagnostic upper bound omits upright/sideways gates, and is labelled so.
   dense+=.01*3*max(0,min(1,float(root[i,7])/.8))*bool(a['public_request'][i,col])
  replay.append(dict(env_id=eid,path_reward_on_retained_motion=potential,forward_rate_upper_bound_contribution=dense,scope='47 intervals of the existing selected recording; reconstructed colliders; not new policy behavior or optimizer evidence'))
 put('REWARD_PATH_CPU_ACTUAL.json',dict(epoch=time.time(),passed=True,recipe=m.RECIPE,cases=tests,recorded_replay=replay,original_runtime=dict(path=str(old),SHA=H(old)),candidate_runtime=dict(path=str(dest),SHA=H(dest)),reward_module=dict(path=str(B/'h1_step270_path_reward_v1.py'),SHA=H(B/'h1_step270_path_reward_v1.py')),only_four_allowlisted_runtime_edits_AST_exact=True,goal_source_unchanged=True,checkpoint_schema_and_all17Adam_unchanged=True,derived_joint_potential_cache_not_physical_state=True,cache_first_callback_after_reset_has_zero_reward=True,no_new_actor_input_command_physics_guard_or_success_change=True,no_GPU_actor_optimizer_or_RNG=True,not_proof_of_270mm_success=True))
 put('LOCAL_READ_BASENAME_ERRORS_AND_UNUSED_DRAFT_ACTUAL.json',dict(epoch=time.time(),errors=[dict(path='H1_STEP270_E3_BOUNDED_TRACE_PAIR_V16_20261022/deploy_pair_from_actual_closed_unused_root_once.py',error='FileNotFound: guessed basename; actual is deploy_pair_new_original_writer_bounded_once.py; no helper executed'),dict(path='payloads/h1/h1_takeoff_progress_environment_v2.py',error='FileNotFound: actual file is nested job0/runtime/isaac/mod4; no helper executed')],unused_draft='h1_step270_path_reward_v1_UNUSED_TRANSPORT_DRAFT.py',reason='Before any CPU execution replaced height-weighted transport integral by bounded signed joint-potential difference to avoid height-dependent closed-loop farming; native xyzw quaternion formula reused instead of SDK wxyz helper.',no_remote_or_training_change=True))
 print(json.dumps(dict(passed=True,cases=len(tests),replay=replay,runtime_SHA=H(dest))))
if __name__=='__main__':
 try:main()
 except BaseException:
  put('REWARD_PATH_CPU_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_remote_GO=True));raise
