"""Counterexamples run against the actual pinned native termination body; no simulator/PPO."""
from pathlib import Path
import ast,inspect,json,math,os,sys,textwrap,types
import torch
T=Path(__file__).resolve().parent;R=T.parents[2]
D=R/'sources/local/MOD4V3_CONTINUOUS_STAIRS_200MM_2H_20261113/dependencies'
os.environ['MOD4_SCUT_SOURCE_PATHS']=str(D/'SOURCE_PATHS.local.json')
sys.path.insert(0,str(D/'package'))
from mod4v1_scut.rewards import ScutRewards as Base
from mod4v1_scut.math_ops import euler_xyz_from_quat,wrap_to_pi
p=T/'support/mod4v3_ppo_v1/stair_training_repair.py'
tree=ast.parse(p.read_text(encoding='utf8'));unit=ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)],type_ignores=[]);ast.fix_missing_locations(unit)
ns=dict(ast=ast,inspect=inspect,textwrap=textwrap,types=types,torch=torch,euler_xyz_from_quat=euler_xyz_from_quat,wrap_to_pi=wrap_to_pi)
exec(compile(unit,str(p),'exec'),ns)
S=types.SimpleNamespace

def fixture(repaired):
 n=5;data=S(root_quat_w=torch.zeros(n,4),root_lin_vel_b=torch.zeros(n,3),root_ang_vel_b=torch.zeros(n,3));data.root_quat_w[:,0]=1.
 cfg=S(termination_duration_enabled=True,termination_duration_steps=10,termination_roll_deg=40.,termination_pitch_deg=40.,play=False)
 r=S(num_envs=n,device='cpu',cfg=cfg,robot=S(data=data),joint_vel=torch.zeros(n,6),_actuate_idx=list(range(6)),_reset_contact_link_idx=list(range(9)),_guide_link_idx=list(range(1,9)),contact_sensor=S(data=S(net_forces_w=torch.zeros(n,9,3))),max_episode_length=1000,episode_length_buf=torch.zeros(n,dtype=torch.long),_numerical_safety_reset_buf=torch.zeros(n,dtype=torch.bool),_terminate_on_obs_outlier=False,_value_debug_step=0,state_machine_manager=S(apply_done_masks=lambda env,t,o:(t,o)))
 r._get_dones=types.MethodType(Base._get_dones,r);r._apply_termination_duration=types.MethodType(Base._apply_termination_duration,r)
 if repaired:
  ns['install_native_done_repair'](r);r._stair_course_mask[:4]=True;r._stair_guide_allowed[0]=True
 return r
old=fixture(False);new=fixture(True);history=[]
for step in range(15):
 for r in (old,new):
  f=r.contact_sensor.data.net_forces_w;f.zero_();f[0,1,0]=2.;f[1,0,0]=2.;f[2,1,0]=2.
  r.robot.data.root_quat_w.zero_();r.robot.data.root_quat_w[:,0]=1.
  if step<5:f[3:5,0,0]=2.
  else:r.robot.data.root_quat_w[3:5,0]=math.cos(math.radians(45)/2);r.robot.data.root_quat_w[3:5,2]=math.sin(math.radians(45)/2)
 old_done=old._get_dones()[0];new_done=new._get_dones()[0]
 history.append(dict(step=step+1,old=old_done.tolist(),repaired=new_done.tolist()))
 if step==8:assert not bool(new_done.any())
 if step==9:
  assert old_done.tolist()==[True,True,True,True,True]
  assert new_done.tolist()==[False,True,True,False,True]
 if step==14:assert new_done.tolist()==[False,True,True,True,True]
new.robot.data.root_lin_vel_b[0,0]=float('nan')
assert bool(new._get_dones()[0][0]),'Numerical safety must bypass ordinary dwell'
hits=torch.tensor([[[-.1,0.,0.],[0.,0.,0.],[.1,0.,.2]]])
chosen=ns['wheel_center_ground'](hits,torch.zeros(1,2),torch.zeros(1));assert chosen.item()==0. and hits[:,:,2].mean().item()>0.
result=dict(passed=True,native_body_used=True,guide_allowed_only_near_ascending_edge=True,chassis_and_nonexempt_guide_contact_preserved=True,separate_contact_orientation_timers=True,nonstair_combined_timer_preserved=True,numerical_immediate_preserved=True,wheel_center_riser_counterexample=dict(old_grid_mean_m=float(hits[:,:,2].mean()),corrected_m=float(chosen.item())),history=history,no_optimizer_updates=True)
(T/'evidence/COUNTEREXAMPLE_CHECKS.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:v for k,v in result.items() if k!='history'}))
