"""GPU Isaac transition bridge: real terminal states and live DR feedback."""
from dataclasses import dataclass
import torch
from supermimic_vendor_v2.contract import SUPERMIMIC_STATE_KEY as SK,SUPERMIMIC_TRANSITION_KEY as TK
from supermimic_vendor_v2.geometry import unflatten_state,flatten_state
from lqr_reference_mdp import LQRStepMDP

@dataclass
class BridgeState:
    info:dict
    reward:torch.Tensor
    terminated:torch.Tensor
    truncated:torch.Tensor
    obs:dict

class StepBridge:
    def __init__(self,env,reference):
        self.env=env;self.device=torch.device(env.device);self.num_envs=env.num_envs;self.ep_step=torch.zeros(env.num_envs,device=self.device,dtype=torch.long)
        self.mdp=LQRStepMDP(reference,env.scene['robot'].joint_names,env.scene['robot'].data.default_joint_pos[0],env.device)
        self.state=None;self.action=torch.zeros(env.num_envs,6,device=self.device);self.terminal=None;env.capture_terminal=self.capture_terminal
        self.total=0;self.episodes=0;self.successes=0;self.stable=torch.zeros(env.num_envs,device=self.device);self.cross=torch.zeros(env.num_envs,device=self.device,dtype=torch.bool);self.airborne=torch.zeros_like(self.cross);self.max_footprint=torch.zeros(env.num_envs,device=self.device)
        self.wheels=[env.scene['robot'].body_names.index(n) for n in ['left_wheel','right_wheel']]
        self.ep_returns=torch.zeros(env.num_envs,device=self.device)
    @property
    def supermimic_mdp(self):return self.mdp
    def pack(self):
        r=self.env.scene['robot'];root=r.data.root_state_w.clone();root[:,:3]-=self.env.scene.env_origins
        # Installed 6.1.14 root_state_w has xyzw; explicit simulator conversion is validated below.
        root[:,3:7]=root[:,[6,3,4,5]]
        return torch.cat((root,r.data.joint_pos.clone(),r.data.joint_vel.clone()),-1)
    def context(self):
        obs=self.cached_observation['policy'].clone();assert obs.shape[-1]==35
        # Physical sensor corruption is represented as a fixed per-transition context
        # offset, while the imagined body/joint state supplies fresh noiseless values.
        zero=torch.zeros(self.num_envs,40,device=self.device);zero[:,:4]=obs[:,:4];zero[:,28:35]=obs[:,28:35]
        clean=self.mdp.obs35(unflatten_state(self.pack()),self.action,zero)
        residual=obs-clean
        return torch.cat((residual,torch.zeros(self.num_envs,5,device=self.device)),-1),obs
    def capture_terminal(self,ids):
        if self.terminal is not None:self.terminal[ids]=self.pack()[ids]
    def info(self):
        s=self.pack();ctx,obs=self.context()
        # Preserve command,height,mode in context. MDP calculates continuous groups.
        ctx[:,:4]=obs[:,:4];ctx[:,28:35]=obs[:,28:35]
        return {SK:{'s':s,'xi':ctx,'f':self.ep_step.clone(),'a_prev':self.action.clone(),'ep_step':self.ep_step.clone()}}
    def init_state(self):
        self.cached_observation,_=self.env.reset();z=torch.zeros(self.num_envs,device=self.device);self.state=BridgeState(self.info(),z,z.bool(),z.bool(),{});return self.state
    @torch.no_grad()
    def step(self,action):
        previous=self.state.info[SK];a=action.clamp(-6,6);self.terminal=self.pack().clone();self.action=a.clone()
        self.cached_observation,_,term,trunc,extra=self.env.step(a);done=term|trunc;post=self.pack();s1=post.clone();s1[done]=self.terminal[done]
        frames=previous['f']+1;reward=self.mdp.reward(unflatten_state(s1),frames,a,previous['a_prev'])
        self.ep_returns+=reward
        robot=self.env.scene['robot'];pos=robot.data.body_pos_w[:,self.wheels]-self.env.scene.env_origins[:,None,:]
        sensor=self.env.scene.sensors['wheel_contact'];force=sensor.data.net_forces_w.norm(dim=-1)
        air=(force<1).all(-1)&(pos[:,:,2].min(-1).values>.075);self.airborne|=air
        footprint=pos[:,:,0].min(-1).values-.0625;self.cross|=self.airborne&(footprint>0)&(pos[:,:,2].min(-1).values>.33)
        top=(force>1).all(-1)&(pos[:,:,2]>.327).all(-1)&(footprint>0)
        root=unflatten_state(post);body_contact=self.env.scene.sensors['chassis_contact'].data.net_forces_w.norm(dim=-1).max(-1).values
        stable=top&self.cross&(root[1][:,2,2]>.95)&(root[2].norm(dim=-1)<.3)&(root[3].norm(dim=-1)<.5)&(body_contact<1)
        self.stable=torch.where(stable,self.stable+.02,torch.zeros_like(self.stable))
        ep_good=self.stable>=.5;new_good=ep_good&(~getattr(self,'success_latched',torch.zeros_like(ep_good)));self.successes+=int(new_good.sum());self.success_latched=getattr(self,'success_latched',torch.zeros_like(ep_good))|ep_good
        self.total+=self.num_envs;self.episodes+=int(done.sum());length=self.ep_step+1
        trans={'s':previous['s'],'s1':s1,'xi':previous['xi'],'f':previous['f'],'ep_step':previous['ep_step'],'a_prev':previous['a_prev'],'a':a,'r':reward,'done':done,'term':term,'ep_len':length[done].float(),'ep_ret_norm':self.ep_returns[done]/length[done].clamp(min=1)}
        if not bool(done.any()):
            trans.pop('ep_len');trans.pop('ep_ret_norm')
        self.ep_step+=1;self.ep_step[done]=0;self.action[done]=0;self.stable[done]=0;self.airborne[done]=False;self.cross[done]=False;self.success_latched[done]=False;self.ep_returns[done]=0
        info=self.info();info[TK]=trans;self.state=BridgeState(info,reward,term,trunc,{});return self.state
    def metrics(self):return {'physical_transitions':self.total,'finished_episodes':self.episodes,'training_progress_events_not_strict_success':self.successes,'strict_success_evaluated':False,'max_current_stable_s':float(self.stable.max()),'cross_current_envs':int(self.cross.sum())}
