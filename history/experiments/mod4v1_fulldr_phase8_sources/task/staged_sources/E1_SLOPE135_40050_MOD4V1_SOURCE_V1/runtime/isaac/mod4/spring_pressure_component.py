"""D5 first engineering pressure: independent episode factors for two gas springs.

This component contains no SDK, policy, physical parameter writes or launch
authority. Nominal stiffness/preload/damping stay external and unchanged.
It is not a hardware force-stroke calibration.
"""
import torch

class SpringPressure:
    def __init__(self,n,device,seed,enabled=True):
        if not isinstance(n,int) or n<=0:raise ValueError('positive environment count required')
        self.n=n;self.device=torch.device(device);self.enabled=bool(enabled)
        self.factor=torch.ones((n,2),device=self.device)
        self.episode=torch.zeros((n,),device=self.device,dtype=torch.long)
        self.rng=[torch.Generator(device=self.device).manual_seed(int(seed)+offset) for offset in (790103,790123)]
    def reset(self,ids):
        ids=torch.as_tensor(ids,device=self.device,dtype=torch.long)
        if ids.ndim!=1 or ids.numel()==0 or ids.unique().numel()!=ids.numel() or bool(((ids<0)|(ids>=self.n)).any()):
            raise ValueError('unique selected environment ids required')
        for column,rng in enumerate(self.rng):
            values=.9+.2*torch.rand((ids.numel(),),device=self.device,generator=rng) if self.enabled else torch.ones((ids.numel(),),device=self.device)
            self.factor[ids,column]=values
        self.episode[ids]+=1
    def actual_stiffness(self,nominal):
        nominal=torch.as_tensor(nominal,device=self.device,dtype=self.factor.dtype)
        if nominal.shape!=(2,) or not torch.isfinite(nominal).all() or not bool((nominal>0).all()):
            raise ValueError('two finite positive nominal stiffness values inN/m required')
        return self.factor*nominal
    def state_dict(self):
        return dict(version=1,n=self.n,enabled=self.enabled,rng_device_type=self.device.type,
            factor=self.factor.clone(),episode=self.episode.clone(),rng=[g.get_state().clone() for g in self.rng],
            scope='Independent per-episode engineering stiffness factor.9–1.1; preload/damping unchanged; nothardware calibrated')
    def load_state_dict(self,state):
        if state['version']!=1 or state['n']!=self.n or state['enabled']!=self.enabled or state['rng_device_type']!=self.device.type:
            raise ValueError('scope/device RNG codec differs; actualCUDA resume must be independently verified')
        f=state['factor'];e=state['episode'];streams=state['rng']
        if f.shape!=(self.n,2) or e.shape!=(self.n,) or len(streams)!=2 or not torch.isfinite(f).all() or bool(((f<.9)|(f>1.1)).any()) or bool((e<0).any()):
            raise ValueError('invalid saved pressure state')
        if not self.enabled and not torch.equal(f,torch.ones_like(f)):raise ValueError('off must be exact unity')
        self.factor.copy_(f.to(self.device));self.episode.copy_(e.to(self.device))
        for g,saved in zip(self.rng,streams):g.set_state(saved.cpu())
