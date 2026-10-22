"""Isolate actual task callback and SDK reward compute; no Kit, scene or GPU."""
from pathlib import Path
import ast,hashlib,importlib.util,types
import torch

def module(path,name):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def check(B,sdk_reward_path):
 B=Path(B);sdk_reward_path=Path(sdk_reward_path);rng=torch.get_rng_state().clone()
 reward=module(B/'h1_step270_path_reward_v1.py','path_reward_cpu')
 goal=module(B/'step270_goal_and_scut_rates_candidate.py','step_goal_cpu')
 tree=ast.parse((B/'h1_step270_sdk_runtime_candidate.py').read_text('utf8'))
 phase=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='Step270Phase')
 geometry=dict(height=.270,edge_x=.35,depth=.8,width=1.2)
 env=types.SimpleNamespace(num_envs=1,device='cpu',h1_body_names=['left_wheel','right_wheel'],step270_top_faces=torch.tensor([[7,8]]))
 data=types.SimpleNamespace(root_state_w=torch.tensor([[0.,0.,.5,0.,0.,0.,1.,0.,0.,0.,0.,0.,0.]]),body_pos_w=torch.zeros(1,2,3))
 env.scene=types.SimpleNamespace();env.scene={'robot':types.SimpleNamespace(data=data)}
 class Scene(dict):pass
 env.scene=Scene(env.scene);env.scene.env_origins=torch.zeros(1,3)
 lo=torch.zeros(1,2,3);hi=torch.zeros(1,2,3)
 def query(points,distance):return dict(hit=torch.ones(1,2,dtype=torch.bool),height=torch.full((1,2),.27),face_id=torch.full((1,2),7))
 ns=dict(torch=torch,Step270Events=goal.Step270Events,GEOMETRY=geometry,tensor=lambda v:v,wheel_bounds=lambda e:(lo,hi),mesh_query=lambda e:types.SimpleNamespace(cast=query),reference=lambda **kw:(None,torch.ones(1),None),path_increment=reward.path_increment)
 exec(compile(ast.Module(body=[phase],type_ignores=[]),'actual_runtime_Step270Phase','exec'),ns)
 p=ns['Step270Phase'](env);env.h1_phase=p;env.step_dt=.01
 events={k:0 for k in ('takeoff','landing','recovery')};total=0.
 for j in range(400):
  request=j>=100;p.request_for_action.fill_(request)
  if j<100:x=.0;z=.0;force=10.;vz=0.;speed=0.
  elif j<125:x=(j-100)*.015;z=.30;force=0.;vz=.3;speed=.8
  else:x=.60;z=.27;force=10.;vz=0.;speed=0.
  lo[:]=torch.tensor([x-.05,-.1,z]);hi[:]=torch.tensor([x+.05,.1,z+.08])
  data.root_state_w[:,0]=x;data.root_state_w[:,2]=z+.5;data.root_state_w[:,7]=speed;data.root_state_w[:,9]=vz
  out=p.physical(wheel_N=torch.full((1,2),force),all_min_clear_m=torch.tensor([0. if force else .30]),nonwheel_max_N=torch.zeros(1),root_vz=torch.tensor([vz]),root_planar_speed=torch.tensor([speed]),roll=torch.zeros(1),pitch=torch.zeros(1),yaw=torch.zeros(1))
  for k in events:events[k]+=int(out[k].sum())
  total+=float(p.progress_control);p.progress_control.zero_();p.age_control+=1
 assert events==dict(takeoff=1,landing=1,recovery=1) and bool(p.goal.success[0]) and bool(p.crossed.all())
 # Original strict event class must reject low clearance / missing top contact.
 # No reward is allowed to mutate these goal flags.
 assert goal.Contract().platform_top_m==.270 and goal.Contract().stable_callbacks==200
 p.reset(torch.tensor([0]));out=p.physical(wheel_N=torch.full((1,2),10.),all_min_clear_m=torch.zeros(1),nonwheel_max_N=torch.zeros(1),root_vz=torch.zeros(1),root_planar_speed=torch.zeros(1),roll=torch.zeros(1),pitch=torch.zeros(1),yaw=torch.zeros(1))
 assert not p.goal.success.any() and not p.crossed.any() and float(p.progress_control)==0
 # Run the actual installed SDK compute body against the two new terms.
 sdk=ast.parse(sdk_reward_path.read_text('utf8'));cls=next(n for n in sdk.body if isinstance(n,ast.ClassDef) and n.name=='RewardManager');fn=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='compute')
 ns2={'torch':torch};exec(compile(ast.Module(body=[fn],type_ignores=[]),str(sdk_reward_path),'exec'),ns2)
 p.progress_control.fill_(2.);p.request_for_action.fill_(True);p.goal.attempt.fill_(True);p.goal.landed.fill_(False);data.root_state_w[:,7]=.8
 terms=[types.SimpleNamespace(func=reward.measured_rate,weight=w,params={'name':name}) for name,w in [('path_progress',1.),('requested_forward',3.)]]
 manager=types.SimpleNamespace(_env=env,_term_names=['path','forward'],_term_cfgs=terms,_reward_buf=torch.zeros(1),_step_reward=torch.zeros(1,2),_episode_sums={'path':torch.zeros(1),'forward':torch.zeros(1)})
 result=ns2['compute'](manager,.01)
 assert torch.allclose(result,torch.tensor([2.03]),atol=1e-6,rtol=0) and torch.allclose(manager._step_reward.sum(-1)*.01,result)
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 return dict(passed=True,actual_runtime_class_CPU_callbacks=400,strict_events=events,strict_270mm_and_200callback_stability_preserved=True,reset_no_free_progress=True,actual_SDK_reward_compute_SHA=hashlib.sha256(sdk_reward_path.read_bytes()).hexdigest(),known_path2_forward_rate3_control_reward=float(result),no_Kit_PhysX_scene_actor_optimizer_RNG_or_GPU=True,synthetic_not_skill_evidence=True)
