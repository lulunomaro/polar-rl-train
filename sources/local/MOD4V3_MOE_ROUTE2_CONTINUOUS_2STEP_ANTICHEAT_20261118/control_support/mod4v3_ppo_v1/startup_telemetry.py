"""Read-only episode accounting, sampled before native autoresets."""
import torch
class StartupTelemetry:
    def __init__(self,env):
        self.env=env;n=env.num_envs;dev=env.device
        self.seen=torch.zeros(n,dtype=torch.bool,device=dev)
        self.saved=torch.zeros_like(self.seen)
        self.low=torch.zeros_like(self.seen)
        self.minimum=torch.full((n,),float('inf'),device=dev)
        self.initial=torch.zeros(n,device=dev);self.last=torch.zeros(n,device=dev);self.peak=torch.zeros(n,device=dev)
        self.rows=[];self.height_sum=0.;self.height_max=0.;self.samples=0
    def observe(self,p,done):
        e=self.env;active=e.continuous_stair_mask;age=p['episode_age'];first=active&(age<=1.+1e-5)
        beginning=first&(~self.seen);self.initial[beginning]=p['forward_position'][beginning]
        self.seen|=first;self.minimum[first]=torch.minimum(self.minimum[first],p['actual_height'][first])
        self.peak[first]=torch.maximum(self.peak[first],p['actual_vx'][first].abs());self.last[first]=p['forward_position'][first]
        self.low|=first&(p['actual_height']<.22)
        amount=p['penalties'][active,5];self.height_sum+=float(amount.sum());self.height_max=max(self.height_max,float(amount.max()));self.samples+=int(active.sum())
        finish=active&self.seen&(~self.saved)&((age>=1.-1e-5)|done)
        for i in finish.nonzero().flatten().tolist():
            self.rows.append(dict(nominal=bool(e.full_dr.nominal_env_mask[i]),minimum_height_first1s_m=float(self.minimum[i]),collapsed_below22cm=bool(self.low[i]),displacement_sampled_first1s_m=float(self.last[i]-self.initial[i]),peak_abs_forward_speed_first1s_m_s=float(self.peak[i])))
        self.saved|=finish
        self.seen[done]=False;self.saved[done]=False;self.low[done]=False;self.minimum[done]=float('inf');self.peak[done]=0.
    def finish(self):
        out=dict(measurement='first1s pre-autoreset samples; displacement from first sampled step',height_aux_penalty_sum=self.height_sum,height_aux_max_per_step=self.height_max,height_aux_mean_per_E1_step=self.height_sum/max(self.samples,1),E1_policy_samples=self.samples,first1s_episodes=len(self.rows),rows=self.rows)
        for group,nominal in [('DR',False),('nominal',True)]:
            r=[x for x in self.rows if x['nominal']==nominal];vals=[x['minimum_height_first1s_m']for x in r];speeds=[x['peak_abs_forward_speed_first1s_m_s']for x in r]
            out[group]=dict(episodes=len(r),collapsed=sum(x['collapsed_below22cm']for x in r),collapse_rate=sum(x['collapsed_below22cm']for x in r)/max(len(r),1),minimum_height_m=min(vals)if vals else None,median_minimum_height_m=sorted(vals)[len(vals)//2]if vals else None,maximum_first1s_speed=max(speeds)if speeds else None)
        return out
