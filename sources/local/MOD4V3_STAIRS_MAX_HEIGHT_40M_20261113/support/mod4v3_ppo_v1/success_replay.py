"""Completed whole-two-step experience only; training data, no policy interface change."""
import torch

class SuccessfulStairReplay:
    def __init__(self,env,spec):
        self.spec=dict(spec);self.device=env.device;self.ids=env.continuous_stair_mask.nonzero().flatten()
        self.n=len(self.ids);self.limit=int(spec['max_episode_frames']);self.capacity=int(spec['capacity_per_stratum'])
        self.obs=torch.zeros(self.limit,self.n,35,device=self.device);self.actions=torch.zeros(self.limit,self.n,6,device=self.device)
        self.phase=torch.zeros(self.limit,self.n,dtype=torch.bool,device=self.device)
        self.length=torch.zeros(self.n,dtype=torch.long,device=self.device);self.waiting=torch.zeros(self.n,dtype=torch.bool,device=self.device);self.overflow=self.waiting.clone()
        self.bank_obs=torch.zeros(4,self.capacity,35,device=self.device);self.bank_actions=torch.zeros(4,self.capacity,6,device=self.device)
        self.bank_episode=torch.full((4,self.capacity),-1,dtype=torch.long,device=self.device);self.bank_frame=torch.full((4,self.capacity),-1,dtype=torch.long,device=self.device)
        self.counts=[0]*4;self.write=[0]*4;self.episodes=[];self.accepted=0;self.rejected_done=0;self.overflows=0;self.sampled=[0]*4
        self.pending=None

    def before_step(self,env,observations,action,iteration):
        ids=self.ids;full=env.stair_up[ids]&(env.stair_initial_stage[ids]==0)
        eligible=full&(env.episode_length_buf[ids]*env.step_dt>=3.)&(~self.waiting)
        too_long=eligible&(~self.overflow)&(self.length>=self.limit)
        self.overflows+=int(too_long.sum());self.overflow|=too_long
        take=(eligible&(~self.overflow)).nonzero().flatten();positions=self.length[take].clone()
        if take.numel():
            self.obs[positions,take]=observations['policy'][ids[take]]
            self.actions[positions,take]=action[ids[take]].clamp(-6,6)
            self.length[take]+=1
        self.pending=(take,positions,env.stair_stage[ids].clone(),full.clone(),int(iteration))

    def after_step(self,env,term,timeout):
        take,positions,previous,full,iteration=self.pending;ids=self.ids;done=(term|timeout)[ids]
        if take.numel():
            current=env.stair_stage[ids[take]]
            self.phase[positions,take]=(previous[take]==1)|((previous[take]==0)&(current>=1)&(~done[take]))
        completed=full&(env.stair_goal_hold[ids]>=.3)&(~done)&(~self.waiting)&(~self.overflow)&(self.length>0)
        for j in completed.nonzero().flatten().tolist():
            count=int(self.length[j]);nominal=bool(env.full_dr.nominal_env_mask[ids[j]])
            episode=self.accepted;self.accepted+=1;phase=self.phase[:count,j]
            for transition in (False,True):
                group=2*int(nominal)+int(transition);frames=(phase==transition).nonzero().flatten();k=len(frames)
                if not k:continue
                target=(torch.arange(k,device=self.device)+self.write[group])%self.capacity
                self.bank_obs[group,target]=self.obs[frames,j];self.bank_actions[group,target]=self.actions[frames,j]
                self.bank_episode[group,target]=episode;self.bank_frame[group,target]=frames
                self.write[group]=(self.write[group]+k)%self.capacity;self.counts[group]=min(self.capacity,self.counts[group]+k)
            self.episodes.append(dict(episode_id=episode,env=int(ids[j]),source_iteration=iteration,nominal=nominal,frames=count,transition_frames=int(phase.sum()),height_cmd=float(env.stair_height[ids[j]]),speed_cmd=float(env.stair_speed[ids[j]]),first_landing_s=float(env.stair_first_time[ids[j]]),second_landing_s=float(env.stair_second_time[ids[j]]),first_to_second_s=float(env.stair_second_time[ids[j]]-env.stair_first_time[ids[j]])))
            self.episodes=self.episodes[-4096:];self.waiting[j]=True;self.length[j]=0
        self.rejected_done+=int((done&full&(~self.waiting)&(self.length>0)).sum())
        self.length[done]=0;self.waiting[done]=False;self.overflow[done]=False;self.pending=None

    def sample(self,count):
        assert sum(self.counts)>0
        observations=[];actions=[]
        transition=int(round(count*float(self.spec['transition_fraction'])))
        for phase,requested in [(1,transition),(0,count-transition)]:
            available=[g for g in (phase,phase+2) if self.counts[g]]
            if not available:available=[g for g in range(4) if self.counts[g]]
            for i,group in enumerate(available):
                size=requested//len(available)+int(i<requested%len(available))
                if not size:continue
                idx=torch.randint(self.counts[group],(size,),device=self.device)
                observations.append(self.bank_obs[group,idx]);actions.append(self.bank_actions[group,idx]);self.sampled[group]+=size
        return torch.cat(observations),torch.cat(actions)

    def summary(self):
        return dict(enabled=True,strata=['DR_other','DR_second_step_transition','nominal_other','nominal_second_step_transition'],frames_by_stratum=list(self.counts),sampled_by_stratum=list(self.sampled),accepted_whole_two_step_episodes=self.accepted,accepted_DR=sum(not x['nominal'] for x in self.episodes),accepted_nominal=sum(x['nominal'] for x in self.episodes),rejected_failed_or_timeout_episodes=self.rejected_done,overflow_discarded_episodes=self.overflows,capacity_per_stratum=self.capacity,last_successes=self.episodes[-8:],source='actual completed successful on-policy episodes; executed clipped actions',inflight_not_restored='physical episodes start fresh on full PPO resume')

    def state_dict(self):
        return dict(version=1,counts=list(self.counts),write=list(self.write),accepted=self.accepted,rejected_done=self.rejected_done,overflows=self.overflows,sampled=list(self.sampled),episodes=list(self.episodes),bank_obs=self.bank_obs.detach().cpu(),bank_actions=self.bank_actions.detach().cpu(),bank_episode=self.bank_episode.detach().cpu(),bank_frame=self.bank_frame.detach().cpu())

    def load_state_dict(self,state):
        assert state['version']==1
        for name in ['bank_obs','bank_actions','bank_episode','bank_frame']:
            value=state[name];assert value.shape==getattr(self,name).shape;getattr(self,name).copy_(value.to(self.device))
        for name in ['counts','write','accepted','rejected_done','overflows','sampled','episodes']:setattr(self,name,state[name])
