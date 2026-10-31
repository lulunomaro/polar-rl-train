from pathlib import Path
import os
os.environ['CUDA_VISIBLE_DEVICES']=''
import ast,hashlib,json,sys,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports';D=N/'train_package'
with (R/'ROOT194_SOURCE_CPU_ONCE_CONSUMED.json').open('x') as f:json.dump(dict(epoch=time.time(),model_reads=0,CUDA=False),f)
sys.path.insert(0,str(D))
import torch
torch.set_num_threads(2)
from literal_original_methods import LiteralOriginalFudanRewardMethods as Original
from literal_original_config import LiteralOriginalConfig,class_to_dict
from jump194_boundary import LiteralJump194
from mod4_literal_math184_v2 import own_virtual_legs
groups=[]
try:
 upstream=T/'FUDAN_ORIGINAL_URDF_JUMP_FROM_SCRATCH_V183_20261031/upstream/jump/wheel_legged_gym/envs/base/legged_robot.py'
 a=upstream.read_text(encoding='utf8');b=(D/'literal_original_methods.py').read_text(encoding='utf8')
 ca=next(x for x in ast.parse(a).body if isinstance(x,ast.ClassDef) and x.name=='LeggedRobot')
 cb=next(x for x in ast.parse(b).body if isinstance(x,ast.ClassDef))
 methods={x.name:x for x in ca.body if isinstance(x,ast.FunctionDef)}
 checked=[]
 for f in cb.body:
  if not isinstance(f,ast.FunctionDef):continue
  assert ast.get_source_segment(b,f)==ast.get_source_segment(a,methods[f.name]),f.name
  checked.append(f.name)
 assert len(checked)==19
 cfgtext=(T/'FUDAN_ORIGINAL_URDF_JUMP_FROM_SCRATCH_V183_20261031/upstream/jump/wheel_legged_gym/envs/base/legged_robot_config.py').read_text(encoding='utf8')
 c=next(x for x in ast.parse(cfgtext).body if isinstance(x,ast.ClassDef) and x.name=='LeggedRobotCfg')
 rew=next(x for x in c.body if isinstance(x,ast.ClassDef) and x.name=='rewards')
 pure=(D/'literal_original_config.py').read_text(encoding='utf8')
 rp=next(x for x in next(x for x in ast.parse(pure).body if isinstance(x,ast.ClassDef)).body if isinstance(x,ast.ClassDef))
 assert ast.get_source_segment(cfgtext,rew)==ast.get_source_segment(pure,rp)
 groups.append(dict(name='literal19methods_and_full_reward_config_text',passed=True,methods=checked))
 bodies=['chassis','left_wheel','right_wheel']+['actual_unused_fixture_'+str(i) for i in range(28)]
 k=LiteralJump194(4,'cpu',.02,bodies)
 v=Original();v.num_envs=4;v.device='cpu';v.dt=.02;v.cfg=LiteralOriginalConfig();v.reward_scales=class_to_dict(v.cfg.rewards.scales)
 v.rew_buf=torch.zeros(4);v.base_air_time=torch.zeros(4);v.last_contacts=torch.zeros(4,2,dtype=torch.bool)
 v.contact_filt=torch.zeros_like(v.last_contacts);v.was_in_flight=torch.zeros(4,dtype=torch.bool)
 v.feet_indices=k.feet_indices;v.penalised_contact_indices=k.penalised_contact_indices;v._prepare_reward_function()
 rng=torch.random.get_rng_state().clone()
 for tick in range(18):
  root=torch.zeros(4,13);root[:,6]=1;root[:,2]=torch.tensor([.2,.35,.6,.7]);root[:,9]=torch.tensor([-.6,0.,.6,2.4])
  forces=torch.zeros(4,31,3)
  if tick%4 in (0,3):forces[:,1:3,2]=50.
  forces[3,0,0]=10.
  frame=dict(commands=torch.tensor([[0.,0.,.12,0.]]).expand(4,-1).clone(),root_states=root,
   base_lin_vel=torch.zeros(4,3),base_ang_vel=torch.zeros(4,3),projected_gravity=torch.tensor([[0.,0.,-1.]]).expand(4,-1),
   L0=torch.tensor([[.16,.16],[.31,.31],[.24,.2],[.3,.3]]),theta0=torch.zeros(4,2),
   torques=torch.full((4,6),tick*.25),actions=torch.full((4,6),tick*.01),last_actions=torch.zeros(4,6,2),contact_forces=forces)
  for name,x in frame.items():setattr(v,name,x.clone())
  v.check_jump();v.compute_reward();got=k.measured_step(frame,tick)
  assert torch.equal(got,v.rew_buf)
  for name in ('base_air_time','last_contacts','contact_filt','was_in_flight'):assert torch.equal(getattr(k,name),getattr(v,name)),name
  assert all(torch.equal(k.episode_sums[x],v.episode_sums[x]) for x in k.episode_sums)
  if tick==9:
   keep=[getattr(k,x).clone() for x in ('base_air_time','last_contacts','contact_filt','was_in_flight')]
   k.reset_sums(torch.tensor([1,3]))
   for value in v.episode_sums.values():value[[1,3]]=0
   assert all(torch.equal(getattr(k,x),y) for x,y in zip(('base_air_time','last_contacts','contact_filt','was_in_flight'),keep))
 groups.append(dict(name='literal_stateful_control_and_reset50',passed=True,paired_controls=18,paired_environments=4))
 assert max(abs(float(x)) for x in k.reward_scales.values())>0 and k.cfg.rewards.clip_single_reward==2.5
 assert k.cfg.rewards.only_positive_rewards is False and k.reward_scales==v.reward_scales
 groups.append(dict(name='all16scales_dt_once_and_per_term2p5_no_total_clip',passed=True,scales=class_to_dict(k.cfg.rewards.scales)))
 # Own hip-axis geometry, including world yaw and the original upside branch.
 names=['chassis','left_wheel','right_wheel'];anchor=torch.tensor([[0.,.1,0.],[0.,-.1,0.]])
 pos=torch.tensor([[[0.,0.,0.],[.1,.1,-.2],[.1,-.1,-.2]]])
 length,theta=own_virtual_legs(pos,torch.eye(3)[None],names,anchor)
 assert torch.allclose(length,torch.full_like(length,(.1**2+.2**2)**.5))
 assert torch.allclose(theta,torch.full_like(theta,torch.atan2(torch.tensor(.2),torch.tensor(.1))-torch.pi/2))
 groups.append(dict(name='own_hip_to_wheel_axis_FK_length_and_original_theta_branch',passed=True))
 assert torch.equal(torch.random.get_rng_state(),rng) and not torch.cuda.is_initialized()
 groups.append(dict(name='RNG_unchanged_no_model_no_CUDA',passed=True))
 result=dict(epoch=time.time(),passed=True,groups=groups,literal19_text_identity=True,model_reads=0,source_only_not_runtime_or_skill=True)
except BaseException:
 result=dict(epoch=time.time(),passed=False,groups=groups,error=traceback.format_exc());raise
finally:
 with (R/'ROOT194_NEW_LITERAL_JUMP50_SOURCE_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(result,f,indent=2)
print(json.dumps(dict(passed=True,groups=len(groups))))
