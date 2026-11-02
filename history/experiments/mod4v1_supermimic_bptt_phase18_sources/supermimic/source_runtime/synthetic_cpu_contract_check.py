"""EXPLICIT SYNTHETIC CPU software/autograd check, NOT expert training or physics.
No SDK, source checkpoints, GPU, canonical locks or original task pass claims.
"""
import os
os.environ['CUDA_VISIBLE_DEVICES']=''
from pathlib import Path
import json,tempfile,torch
from native_supermimic_bridge import OriginalTaskMdp,TeacherResidualPolicy,BridgeState
from ctx_reward_learner import ContextRewardLearner
from supermimic_vendor_v2.learner import SuperMimicConfig
from supermimic_vendor_v2.contract import SUPERMIMIC_STATE_KEY,SUPERMIMIC_TRANSITION_KEY
torch.set_num_threads(2);torch.manual_seed(37)
class FakeTeacher(torch.nn.Module):
 def __init__(self):super().__init__();self.net=torch.nn.Linear(35,6)
 def forward(self,obs,stochastic_output=False):return self.net(obs['policy'])
class Synthetic:
 def __init__(self):
  self.device=torch.device('cpu');self.num_envs=8;self.s=torch.zeros(8,73);self.s[:,2]=.25;self.s[:,3]=1.;self.a=torch.zeros(8,6);self.f=torch.zeros(8,dtype=torch.long);self.xi=torch.zeros(8,35);self.xi[:,:3]=torch.tensor([.3,0.,0.]);self.mdp=OriginalTaskMdp(35,self.s);self.state=None;self.calls=0
 @property
 def supermimic_mdp(self):return self.mdp
 def init_state(self):
  z=torch.zeros(8);self.state=BridgeState(info={SUPERMIMIC_STATE_KEY:dict(s=self.s.clone(),xi=self.xi.clone(),f=self.f.clone(),ep_step=self.f.to(torch.int32),a_prev=self.a.clone())},reward=z,terminated=z.bool(),truncated=z.bool(),obs={});return self.state
 @torch.no_grad()
 def step(self,a):
  old=self.state.info[SUPERMIMIC_STATE_KEY];a=a.clamp(-6,6);s1=old['s'].clone();s1[:,13:19]+=.02*a;s1[:,7:10]+=.01*a[:,:3];xi1=old['xi'].clone();xi1[:,4:10]=s1[:,13:19];xi1[:,22:28]=a;r=-(s1[:,13:19]-.2).square().sum(-1)-.001*a.square().sum(-1);done=torch.zeros(8,dtype=torch.bool);self.calls+=1;self.f+=1;t=dict(s=old['s'],s1=s1,a=a.clone(),a_prev=old['a_prev'],xi=old['xi'],xi1=xi1,xi1_valid=~done,r=r,f=old['f'],ep_step=old['ep_step'],done=done,term=done,trunc=done);self.state=BridgeState(info={SUPERMIMIC_STATE_KEY:dict(s=s1.clone(),xi=xi1.clone(),f=self.f.clone(),ep_step=self.f.to(torch.int32),a_prev=a.clone()),SUPERMIMIC_TRANSITION_KEY:t},reward=r,terminated=done,truncated=done,obs={});return self.state
e=Synthetic();e.init_state();teacher=FakeTeacher().requires_grad_(False);snapshot={k:v.detach().clone()for k,v in teacher.state_dict().items()}
class L(ContextRewardLearner):
 def _make_policy(self):return TeacherResidualPolicy(super()._make_policy(),teacher,e.mdp.actor_context_offset)
config=SuperMimicConfig(iterations=100,buffer_steps=16,utd=1.,horizon=3,goal_frames=1,hist=2,z_dim=4,wm_hidden=(16,),policy_hidden=(16,),critic_hidden=(16,),wm_window=2,wm_batches=1,wm_batch=8,pi_batch=8,lr=.001,warmup_steps=8,wm_only_iters=2,critic_epochs=1,critic_minibatches=1,ckpt_every=10000,log_every=10000,log_backend='none',amp='none',compile=False,seed=37)
with tempfile.TemporaryDirectory(prefix='synthetic_cpu_')as tmp:
 l=L(e,config,tmp,device='cpu',aux_hidden=(16,),aux_batch=8);l.collect(8)
 for _ in range(20):l.wm_update()
 for _ in range(3):l.policy_update()
 assert all(torch.equal(snapshot[k],v)for k,v in teacher.state_dict().items());assert not torch.cuda.is_initialized();assert l.counts.pi_optimizer_steps>0;assert l.counts.pi_bptt_optimizer_steps>0,l.last_bptt_receipt;print(json.dumps({'kind':'SYNTHETIC_CPU_ONLY_SOFTWARE_CONTRACT_AUTOGRAD_NOT_EXPERT_TRAINING','passed':True,'synthetic_counts':vars(l.counts),'synthetic_gradient_receipt':l.last_bptt_receipt,'native_expert_BPTT_updates_counted':0,'teacher_synthetic_unchanged':True,'SDK_GPU_source_model_raw_C_GO_operations':0}))
