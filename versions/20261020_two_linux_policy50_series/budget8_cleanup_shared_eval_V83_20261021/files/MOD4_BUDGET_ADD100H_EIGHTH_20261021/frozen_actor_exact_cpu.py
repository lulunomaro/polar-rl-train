"""Source-exact mean-action kernel only. This is not a simulator or skill admission."""
import hashlib
from pathlib import Path
import torch
import torch.nn.functional as F

class FrozenActor:
    def __init__(self,path,expected_sha,expected_Adam):
        path=Path(path);assert hashlib.sha256(path.read_bytes()).hexdigest()==expected_sha
        s=torch.load(path,map_location='cpu',weights_only=False)
        assert s['policy_clock']['policy_hz']==50
        assert len(s['actor_state_dict'])==9 and len(s['critic_state_dict'])==8
        assert len(s['optimizer_state_dict']['state'])==17 and {int(x['step']) for x in s['optimizer_state_dict']['state'].values()}=={expected_Adam}
        self.weights={k:x.detach().clone() for k,x in s['actor_state_dict'].items()}
        assert all(torch.isfinite(x).all() for x in self.weights.values())
        self.initial={k:x.clone() for k,x in self.weights.items()}
        self.optimizer_updates=0

    @torch.inference_mode()
    def mean(self,obs):
        assert obs.ndim==2 and obs.shape[-1]==35 and torch.isfinite(obs).all()
        x=obs
        for n in (0,2,4,6):
            x=F.linear(x,self.weights[f'mlp.{n}.weight'],self.weights[f'mlp.{n}.bias'])
            if n!=6:x=F.elu(x)
        assert x.shape==(len(obs),6) and torch.isfinite(x).all()
        return x

    def exact(self):
        return self.optimizer_updates==0 and all(torch.equal(x,self.initial[k]) for k,x in self.weights.items())
