"""LQR-reference MDP for actual SuperMimic WM+imagination training."""
from pathlib import Path
import numpy as np
import torch
from supermimic_vendor_v2.geometry import unflatten_state,quat_to_mat,invariant_features,mat_to_quat

class LQRStepMDP:
    num_joints=30;action_dim=6;context_dim=40;obs_dim=108;goal_frame_dim=73;max_step_reward=1.
    def __init__(self,reference,joint_names,default_q,device):
        self.device=torch.device(device);data=np.load(reference);names=data['joint_names'].tolist()
        aliases={f'guide_roller_{i:02d}':f'guide_roller_spin_{i}' for i in range(8)};order=[names.index(aliases.get(n,n)) for n in joint_names]
        s=data['states'].copy();s[:,13:43]=s[:,13:43][:,order];s[:,43:73]=s[:,43:73][:,order]
        self.reference=torch.tensor(s,device=device);self.default_q=default_q.detach().clone();self.joint_names=list(joint_names)
        self.legs=torch.tensor([joint_names.index(n) for n in ['left_crank','left_hip','right_crank','right_hip']],device=device);self.wheels=torch.tensor([joint_names.index(n) for n in ['left_wheel_spin','right_wheel_spin']],device=device)
        self.qweights=torch.ones(30,device=device);self.qweights[self.wheels]=0
        for i,n in enumerate(joint_names):
            if n.startswith('guide_roller'):self.qweights[i]=0
    def to(self,device):
        self.device=torch.device(device)
        for k in ['reference','default_q','legs','wheels','qweights']:setattr(self,k,getattr(self,k).to(device))
        return self
    def goal(self,frames,num_frames):
        idx=frames.long()[...,None]+torch.arange(num_frames,device=frames.device);return self.reference[idx.clamp(0,len(self.reference)-1)].flatten(-2)
    def normalize_context(self,context):return context
    def add_noise(self,obs):return obs
    def obs35(self,state,previous_action,context):
        pos,rot,vel,omega,q,qd=state;rt=rot.transpose(-1,-2);ob=context[...,:35].clone()
        ob[...,4:7]=(rt@omega[...,None]).squeeze(-1)*.5
        ob[...,7:10]=-rot[...,2,:]
        ob[...,10:14]=(q-self.default_q)[...,self.legs]
        ob[...,14:16]=0;ob[...,16:20]=qd[...,self.legs]*.1;ob[...,20:22]=qd[...,self.wheels]*.1;ob[...,22:28]=previous_action
        ob[...,4:14]+=context[...,4:14];ob[...,16:22]+=context[...,16:22]
        return ob
    def obs(self,state,previous_action,context,frames):
        return torch.cat((invariant_features(state),self.obs35(state,previous_action,context)),-1)
    def reward(self,state,frames,action,previous_action):
        target=unflatten_state(self.goal(frames,1));p,r,v,w,q,qd=state;tp,tr,tv,tw,tq,tqd=target
        position=torch.exp(-8*(p-tp).square().sum(-1));rotation=torch.exp(-2*(r-tr).square().sum((-1,-2)))
        velocity=torch.exp(-.3*(v-tv).square().sum(-1));joint=torch.exp(-3*((q-tq).square()*self.qweights).sum(-1)/self.qweights.sum());jvel=torch.exp(-.03*((qd-tqd).square()*self.qweights).sum(-1)/self.qweights.sum())
        top=torch.sigmoid((p[...,0]-.15)*12)*torch.sigmoid((p[...,2]-.43)*18);upright=((r[...,2,2]+1)/2).clamp(0,1)
        reward=(.35*position+.2*rotation+.2*joint+.1*velocity+.05*jvel+.1*top)*upright-.001*(action-previous_action).square().mean(-1)
        return reward
    def soft_termination(self,state,frames):
        return torch.maximum(torch.sigmoid((.45-state[1][...,2,2])*15),torch.sigmoid((.12-state[0][...,2])*30))
    def critic_features(self,state,frames,context):return torch.cat((invariant_features(state),context,frames.float()[...,None]/250),-1)
    def valid_imagination_start(self,frames,horizon):return frames+horizon<len(self.reference)
