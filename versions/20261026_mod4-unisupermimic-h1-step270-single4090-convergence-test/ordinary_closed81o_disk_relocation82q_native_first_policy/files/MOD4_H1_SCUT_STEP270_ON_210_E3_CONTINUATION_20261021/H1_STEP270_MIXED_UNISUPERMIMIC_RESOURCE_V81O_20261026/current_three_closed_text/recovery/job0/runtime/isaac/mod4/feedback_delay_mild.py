"""D3 first candidate: per-episode0/10ms at100Hz. CPU math only until SDK reviewed."""
import torch
WIDTHS={'base_ang_vel':3,'projected_gravity':3,'leg_pos':4,'leg_vel':4,'wheel_vel':2}
class FeedbackDelay:
 def __init__(self,n,device,seed,enabled=True):
  assert n>0;self.n=n;self.device=device;self.enabled=enabled
  self.rng=torch.Generator(device=device).manual_seed(int(seed)+1400039)
  self.delay=torch.zeros(n,dtype=torch.long,device=device);self.episode=torch.zeros_like(self.delay);self.cache={}
 def reset(self,ids):
  ids=torch.as_tensor(ids,device=self.device,dtype=torch.long)
  assert ids.ndim==1 and len(torch.unique(ids))==len(ids) and bool(((ids>=0)&(ids<self.n)).all())
  if len(ids):
   self.delay[ids]=torch.randint(0,2,(len(ids),),device=self.device,generator=self.rng) if self.enabled else 0
   self.episode[ids]+=1
   for c in self.cache.values():c['last'][ids]=-1;c['sample_tick'][ids]=-1;c['ready'][ids]=False
 def apply(self,key,x,tick):
  assert key in WIDTHS and x.shape==(self.n,WIDTHS[key]) and bool(torch.isfinite(x).all()) and int(tick)==tick and tick>=0
  tick=int(tick)
  if not self.enabled:return x
  if key not in self.cache:
   self.cache[key]=dict(last=torch.full((self.n,),-1,dtype=torch.long,device=self.device),cur=torch.zeros_like(x),out=torch.zeros_like(x),sample_tick=torch.full((self.n,),-1,dtype=torch.long,device=self.device),ready=torch.zeros(self.n,dtype=torch.bool,device=self.device))
  c=self.cache[key];due=torch.where(c['last']!=tick)[0]
  if len(due):
   old=c['last'][due].clone();initial=old<0
   assert bool((initial|(old==tick-1)).all()),'Skipped/reversed feedback sample clock'
   prev=c['cur'][due].clone();prev[initial]=x[due][initial]
   delayed=(self.delay[due]==1)&~initial
   c['out'][due]=torch.where(delayed[:,None],prev,x[due]);c['cur'][due]=x[due]
   c['sample_tick'][due]=torch.where(delayed,old,torch.full_like(old,tick));c['last'][due]=tick;c['ready'][due]=~initial
  return c['out'].clone()
 def receipt(self,key,tick):
  c=self.cache[key];age=(int(tick)-c['sample_tick'])*10000
  assert bool(((age==0)|(age==10000)).all())
  return dict(control_period_us=10000,requested_delay_us=self.delay*10000,actual_sample_tick=c['sample_tick'].clone(),apply_tick=int(tick),actual_age_us=age.clone(),warmup_valid=c['ready'].clone(),warmup_uses_current_new_episode_sample=True,no_50Hz_sampling_claimed=True)
 def state_dict(self):
  return dict(version=1,n=self.n,enabled=self.enabled,delay=self.delay.clone(),episode=self.episode.clone(),rng=self.rng.get_state(),cache={k:{a:b.clone() for a,b in c.items()} for k,c in self.cache.items()})
 def load_state_dict(self,s):
  assert s['version']==1 and s['n']==self.n and s['enabled']==self.enabled and bool(((s['delay']==0)|(s['delay']==1)).all())
  assert set(s['cache']).issubset(WIDTHS)
  self.delay=s['delay'].to(self.device).clone();self.episode=s['episode'].to(self.device).clone();self.rng.set_state(s['rng'].cpu())
  self.cache={k:{a:b.to(self.device).clone() for a,b in c.items()} for k,c in s['cache'].items()}
