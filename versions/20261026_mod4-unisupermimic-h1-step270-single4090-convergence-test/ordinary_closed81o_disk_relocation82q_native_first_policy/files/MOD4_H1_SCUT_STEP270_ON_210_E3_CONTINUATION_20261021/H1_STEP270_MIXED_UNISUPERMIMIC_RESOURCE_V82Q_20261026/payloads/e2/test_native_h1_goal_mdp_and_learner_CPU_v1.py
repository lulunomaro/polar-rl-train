"""Synthetic tensor contract test only; no Isaac scene or real local policy rollout."""
from pathlib import Path
from dataclasses import dataclass
import json
import sys
import time
import traceback
import torch

H=Path(__file__).resolve().parent
sys.path.insert(0,str(H/'source'))
from h1_supermimic_bridge_v1 import H1GoalMdp
from supermimic_vendor_v2.learner import SuperMimicConfig,SuperMimicLearner
from supermimic_vendor_v2.geometry import unflatten_state
from supermimic_vendor_v2.contract import SUPERMIMIC_STATE_KEY,SUPERMIMIC_TRANSITION_KEY

@dataclass
class State:
    info:dict
    reward:torch.Tensor
    terminated:torch.Tensor
    truncated:torch.Tensor
    obs:dict

class FakeTensorEnv:
    def __init__(self):
        self.num_envs=4;self.device=torch.device('cpu');self.state=None;self.calls=0
        self.mdp=H1GoalMdp(torch.zeros(30),.31)
    @property
    def supermimic_mdp(self):return self.mdp
    def init_state(self):
        s=torch.zeros(4,73);s[:,2]=.31;s[:,3]=1.
        info=dict(s=s,xi=torch.zeros(4,49),f=torch.tensor([0,95,110,160]),a_prev=torch.zeros(4,6),ep_step=torch.zeros(4,dtype=torch.int32))
        zero=torch.zeros(4);self.state=State({SUPERMIMIC_STATE_KEY:info},zero,zero.bool(),zero.bool(),{});return self.state
    def before_action(self):self.calls+=1
    def step(self,actions):
        a=actions.clamp(-6,6);old=self.state.info[SUPERMIMIC_STATE_KEY];s1=old['s'].clone()
        s1[:,:3]+=a[:,:3]*.0001;s1[:,13:43]+=a.repeat(1,5)*.0001
        r=self.mdp.reward(unflatten_state(s1),old['f']+1,a,old['a_prev']);done=torch.zeros(4,dtype=torch.bool)
        transition=dict(s=old['s'],s1=s1,a=a,a_prev=old['a_prev'],xi=old['xi'],r=r,f=old['f'],ep_step=old['ep_step'],done=done)
        current=dict(s=s1,xi=old['xi'],f=old['f']+1,a_prev=a,ep_step=old['ep_step']+1)
        self.state=State({SUPERMIMIC_STATE_KEY:current,SUPERMIMIC_TRANSITION_KEY:transition},r,done,done,{})
        return self.state

try:
    torch.set_num_threads(2)
    env=FakeTensorEnv()
    cfg=SuperMimicConfig(iterations=1,buffer_steps=32,utd=1.,horizon=4,goal_frames=1,hist=2,wm_window=2,wm_batches=1,wm_batch=8,pi_batch=8,warmup_steps=12,wm_only_iters=0,critic_epochs=1,critic_minibatches=2,amp='none',compile=False,test_hidden_dims=(32,32),log_backend='tensorboard')
    out=H/'reports/CPU_NATIVE_TENSOR_FIXTURE_V1';assert not out.exists()
    learner=SuperMimicLearner(env,cfg,out,device='cpu',backend='synthetic_tensor_unit_only')
    learner.collect(12)
    assert env.calls==12 and learner.buffer.data['s'].shape[-1]==73 and learner.buffer.data['a'].shape[-1]==6
    wm=[]
    for _ in range(3):wm.append([float(x) for x in learner.wm_update()])
    pi=[float(x) for x in learner.policy_update()]
    assert all(torch.isfinite(torch.tensor(x)).all() for x in wm+[pi])
    assert learner.pi.dec[-1].out_features==6 and learner.wm.out_dim==72 and learner.wm.in_dim==128
    assert not torch.cuda.is_initialized()
    result=dict(epoch=time.time(),passed=True,synthetic_tensor_only_not_robot_rollout=True,native_upstream_collect_WM_policy_and_critic_update_executed=True,actions6_states30_observation128_goal73=True,pre_action_audit_hook_called_once_per_collect=True,WM_update_results=wm,policy_update_result=pi,CUDA_initialized=False,real_H1_physics_task_success_not_tested=True)
    with (H/'reports/NATIVE_H1_GOAL_MDP_AND_LEARNER_CPU_V1_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(result,f,indent=2)
    print(json.dumps(result))
except BaseException:
    with (H/'reports'/('NATIVE_H1_GOAL_MDP_CPU_V1_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),not_actual_robot_training=True),f,indent=2)
    raise
