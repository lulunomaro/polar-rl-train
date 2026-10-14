"""Synthetic CPU tests for observer phase and single policy-call contracts.

This executes only selected observer definitions, never imports Isaac/Kit/Warp.
It is observer validation, not physical backend admission.
"""
from pathlib import Path
import ast,json,time,hashlib,sys,types
import numpy as np,torch
D=Path(__file__).resolve().parent;R=D/'reports';P=D/'payload';torch.set_num_threads(1)
out=R/'OBSERVER_SYNTHETIC_CPU_PHASE_CALL_PASSED.json';assert not out.exists()
source=P/'retention_native_witness_v3.py'
tree=ast.parse(source.read_text(encoding='utf8'));nodes=[n for n in tree.body if isinstance(n,(ast.ClassDef,ast.FunctionDef)) and n.name in ('Witness','build_observed_frozen_policy')]
tensor=lambda v:v;cpu=lambda v:v.detach().cpu().numpy().copy();js=lambda v:v.detach().cpu().tolist()
class Force:
 def __init__(self,t):self.t=t
 def view(self,*args):return self
wp=types.SimpleNamespace(vec3=object(),to_torch=lambda v:v.t)
def hardware(e):
 return dict(arrays={k:np.zeros((2,6),dtype=np.float32) for k in ('cached_pre_actuator_velocity','actual_applied_effort','torque_speed_lower','torque_speed_upper')},COM_frame_error_m=0.,mass_weighted_COM_world=np.zeros((2,3),dtype=np.float32))
def params(e):return dict(synthetic=True)
def query(e,phase):return dict(synthetic=True,phase=phase)
env=types.SimpleNamespace(num_envs=2)
data=types.SimpleNamespace(root_state_w=torch.zeros((2,13)),joint_pos=torch.zeros((2,30)),heading_w=torch.zeros(2),joint_vel=torch.zeros((2,30)),applied_torque=torch.zeros((2,30)),body_link_pose_w=torch.zeros((2,2,7)),body_com_pose_b=torch.zeros((2,2,7)),body_com_vel_w=torch.zeros((2,2,6)),body_link_vel_w=torch.zeros((2,2,6)))
actuator=types.SimpleNamespace(**{k:torch.ones((2,4)) for k in ('_vel_at_effort_lim','_saturation_effort','velocity_limit','effort_limit')})
robot=types.SimpleNamespace(data=data,find_bodies=lambda *a,**k:([0,1],None),actuators={'legs':actuator,'wheels':actuator})
class Scene:
 def __getitem__(self,key):return robot
scene=Scene();scene.sensors={'wheel_contact':types.SimpleNamespace(data=types.SimpleNamespace(net_forces_w=torch.zeros((2,2,3))))};env.scene=scene
force=torch.zeros((2,2,3));force[:,:,2]=torch.tensor([[4.,-5.],[0.,3.]])
cap=types.SimpleNamespace(dt=.0025,impulse=torch.zeros((2,2)),history=torch.zeros((2,3,2,3)),sensor=types.SimpleNamespace(contact_view=types.SimpleNamespace(get_net_contact_forces=lambda **k:Force(force))))
def capture(dt):cap.impulse+=torch.clamp(force[:,:,2],min=0)*dt
cap.capture=capture;env._integrated_contact=cap
tm=types.SimpleNamespace(active_terms=('ordinary','time_out'),terminated=torch.tensor([True,False]),time_outs=torch.tensor([False,False]),get_term_cfg=lambda n:types.SimpleNamespace(time_out=n=='time_out'),get_term=lambda n:torch.tensor([True,False]) if n=='ordinary' else torch.zeros(2,dtype=torch.bool),compute=lambda *a,**k:None)
env.termination_manager=tm;env._physics_action_delay=types.SimpleNamespace(calls={'legs':0,'wheels':0})
cmd=types.SimpleNamespace(command=torch.zeros((2,3)));env.command_manager=types.SimpleNamespace(get_term=lambda name:cmd)
env.action_manager=types.SimpleNamespace(action=torch.zeros((2,6)),get_term=lambda n:types.SimpleNamespace(processed_actions=torch.zeros((2,4))))
env._synthetic_closure=torch.full((2,),.003);env._synthetic_mimic=torch.full((2,),.002)
task=types.ModuleType('mod4_task');task.closure_errors=lambda e:{'closure':e._synthetic_closure};task.mimic_errors=lambda e:{'mimic':e._synthetic_mimic};sys.modules['mod4_task']=task
def step(action):
 cap.impulse.zero_();env.action_manager.action=action.clone()
 for _ in range(4):cap.capture(.0025)
 data.root_state_w[:,0]=.01;tm.compute()
 data.root_state_w[0,0]=99.;env._synthetic_closure=torch.zeros(2);env._synthetic_mimic=torch.zeros(2)
 return None,None,tm.terminated,None
env.step=step
scope=dict(Path=Path,hashlib=hashlib,json=json,time=time,math=__import__('math'),np=np,torch=torch,wp=wp,tensor=tensor,cpu=cpu,js=js,params=params,actual_substep_hardware_and_COM=hardware,plane_query_actual=query,CONTEXT={})
exec(compile(ast.fix_missing_locations(ast.Module(body=nodes,type_ignores=[])),str(source),'exec'),scope)
w=scope['Witness'](env,types.SimpleNamespace(output=str(R/'not_written.json'),steps=1));env._retention_native_witness=w
w.obs=np.zeros((2,35),dtype=np.float32);w.raw_action=np.full((2,6),7.,dtype=np.float32);env.step(torch.full((2,6),6.))
row=w.rows[0]
assert np.array_equal(row['root'][:,0],np.full(2,.01,dtype=np.float32)) and row['after_reset_root'][0,0]==99.
assert np.all(row['closure']==np.float32(.003)) and not row['post_reset_closure'].any()
assert np.all(row['mimic']==np.float32(.002)) and not row['post_reset_mimic'].any()
assert np.all(row['raw_actor_action']==7.) and np.all(row['vec_clipped_action']==6.) and np.all(row['processed_action']==6.)
assert float(row['independent_control_mean_load_error_N'])<1e-6 and len(w.sub)==4
saved=torch.load(D.parent/'MOD4_LINUX_FULLSTATE_REPAIR_RESUME_20261013/left_formal_final_actual/0_model_32635.pt',map_location='cpu',weights_only=False)
class Actor:
 def state_dict(self):return saved['actor_state_dict']
calls={'observations':0,'policy':0}
class Wrapped:
 def __init__(self):self.env=env
 def get_observations(self):calls['observations']+=1;return dict(policy=torch.zeros((2,35)))
def build_frozen(*args):
 actor=Actor();wrapped=Wrapped()
 def policy(values):
  actor.state_dict();calls['policy']+=1;return torch.full((2,6),8.)
 return wrapped,policy,wrapped
module=types.ModuleType('frozen_history_policy');module.build_frozen_policy=build_frozen;sys.modules['frozen_history_policy']=module
wrapped,policy,observer=scope['build_observed_frozen_policy'](None,str(D.parent/'MOD4_LINUX_FULLSTATE_REPAIR_RESUME_20261013/left_formal_final_actual/0_model_32635.pt'),'cpu')
obs=wrapped.get_observations();value=policy(obs)
assert calls=={'observations':1,'policy':1} and np.all(w.raw_action==8.) and w.obs.shape==(2,35)
report=dict(epoch=time.time(),passed_CPU_observer_fixture=True,source=str(source),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),physical_backend_pass_claimed=False,only_synthetic_no_Isaac_no_Warp_no_GPU_no_SSH=True,tests=['termination phase closure/mimic stays prereset when same-control reset changes data','raw policy output vs clipped incoming vs action manager distinctly captured','positive-only force integral rejects negative-force cancellation','exactly one observation and one policy call captured using named actor closure'],actual_fixture_call_counts=calls,all_future_GPU_admission_pending=True)
out.write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(report))
