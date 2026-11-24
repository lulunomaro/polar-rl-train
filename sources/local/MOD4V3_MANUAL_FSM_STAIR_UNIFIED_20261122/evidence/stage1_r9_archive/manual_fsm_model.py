"""Pure obs35/history420 neural stair expert and frozen symmetric E0.

No world state, terrain label, distance, contact sensor or ray enters this module.
The same code executes on CPU and GPU.
"""
import torch
from torch import nn

def mirror_obs(x):
    y = x.clone()
    y[..., [1, 2, 4, 6, 8]] = -x[..., [1, 2, 4, 6, 8]]
    for a, b, width in ((10, 12, 2), (14, 15, 1), (16, 18, 2),
                        (20, 21, 1), (22, 24, 2), (26, 27, 1)):
        y[..., a:a+width] = x[..., b:b+width]
        y[..., b:b+width] = x[..., a:a+width]
    return y

def mirror_action(x):
    return x[..., [2, 3, 0, 1, 5, 4]]

def mlp():
    return nn.Sequential(nn.Linear(35, 256), nn.ELU(), nn.Linear(256, 128), nn.ELU(),
                         nn.Linear(128, 64), nn.ELU(), nn.Linear(64, 6))

def effective_height(h):
    # C1 saturation: identity below .38 m, zero derivative at .395 m.
    t = ((h - .38)/.03).clamp(0., 1.)
    return torch.where(h <= .38, h, .38 + .03*(t - .5*t.square()))

class SymmetricE0(nn.Module):
    def __init__(self):
        super().__init__()
        self.base = mlp()
        self.register_buffer('speeds', torch.tensor([1.8, 2., 2.4, 2.8, 3.]))
        self.register_buffer('heights', torch.tensor([.24, .28, .32, .35, .38, .39]))
        self.register_buffer('correction', torch.tensor([
            [0., .155, .368, .559, .650], [0., -.019, .060, .194, .246],
            [0., -.092, -.088, -.001, .044], [0., .053, .065, .208, .282],
            [0., .127, .107, .098, .138], [0., .125, .093, .046, .032]]))
        self.selected_calibration = None
        self.requires_grad_(False)

    @torch.no_grad()
    def load_e0(self, payload):
        state = payload.get('actor_state_dict', payload)
        self.base.load_state_dict({k.removeprefix('mlp.'):v for k,v in state.items() if k.startswith('mlp.')})
        return self

    def observation(self, obs):
        x = obs.clone()
        h = effective_height(x[..., 3]*.2)
        # SELECTED_E0's low-stance forward curve folds back above its measured
        # maximum. Raise into its measured full-speed stance instead of asking
        # the unchanged network for an extrapolated, slower command.
        speed_blend=((obs[...,0].abs()-2.2)/.4).clamp(0.,1.)
        floor=torch.where(speed_blend>0.,.24+.08*(speed_blend.square()*(3.-2.*speed_blend)),0.)
        h=torch.maximum(h,floor)
        x[..., 3] = 5.*h
        def bracket(value, grid):
            value = value.clamp(grid[0], grid[-1]).contiguous()
            low = (torch.searchsorted(grid, value)-1).clamp(0, len(grid)-2)
            return low, (value-grid[low])/(grid[low+1]-grid[low])
        i, u = bracket(x[..., 0], self.speeds)
        j, v = bracket(h, self.heights)
        low = torch.lerp(self.correction[j, i], self.correction[j, i+1], u)
        high = torch.lerp(self.correction[j+1, i], self.correction[j+1, i+1], u)
        demand = x[..., 0] + torch.lerp(low, high, v)
        gain = (h-.31).clamp_min(0.)*(1.10 + 30.*(h-.31).clamp_min(0.))
        x[..., 0] = 2.*demand/(1.+(1.+4.*gain*demand.abs()).sqrt())
        if self.selected_calibration is not None:
            speeds, heights, demands = self.selected_calibration
            i,u=bracket(obs[...,0].abs(),speeds)
            j,v=bracket(h,heights)
            low=torch.lerp(demands[j,i],demands[j,i+1],u)
            high=torch.lerp(demands[j+1,i],demands[j+1,i+1],u)
            fitted=torch.lerp(low,high,v)*obs[...,0].sign()
            x[...,0]=fitted
        # The measured .24 m reverse curve differs from forward at low speed.
        # Fade its correction out before the unchanged -1.5 m/s flat60 case.
        reverse=(obs[...,0]<0.).float()
        low_height=((.28-h)/.04).clamp(0.,1.)
        low_speed=((1.2-obs[...,0].abs())/.6).clamp(0.,1.)
        x[...,0]*=1.-.25*reverse*low_height*low_speed
        x[..., 28:35] = x.new_tensor([1., 0., 0., 0., 0., 0., 0.])
        return x

    def load_calibration(self, data):
        device=self.speeds.device
        self.selected_calibration=tuple(torch.tensor(data[k],dtype=torch.float32,device=device)
            for k in ('speeds','heights','raw_demands'))
        return self

    def forward(self, obs):
        x = self.observation(obs)
        raw = self.base(torch.cat((x, mirror_obs(x)), 0))
        a, reflected = raw.chunk(2, 0)
        return (.5*(a + mirror_action(reflected))).clamp(-6., 6.)

class HistoryEncoder(nn.Module):
    def __init__(self):
        super().__init__()
        self.temporal = nn.Sequential(nn.Conv1d(35, 64, 3, padding=1), nn.ELU(),
                                      nn.Conv1d(64, 64, 3, stride=2, padding=1), nn.ELU())
        self.project = nn.Sequential(nn.Linear(419, 128), nn.LayerNorm(128), nn.ELU())

    def forward(self, obs, hist):
        past = hist.reshape(-1, 12, 35).transpose(1, 2)
        return self.project(torch.cat((obs, self.temporal(past).flatten(1)), -1))

class StairHead(nn.Module):
    def __init__(self):
        super().__init__()
        self.obs = nn.Linear(35, 256)
        self.context = nn.Linear(128, 256, bias=False)
        self.head = nn.Sequential(nn.ELU(), nn.Linear(256, 128), nn.ELU(),
                                  nn.Linear(128, 64), nn.ELU(), nn.Linear(64, 6))

    def forward(self, obs, latent):
        return self.head(self.obs(obs)+self.context(latent))

class StairExpert(nn.Module):
    def __init__(self):
        super().__init__()
        self.history_encoder = HistoryEncoder()
        self.head = StairHead()

    def raw(self, x):
        obs, hist = x[..., :35], x[..., 35:]
        return self.head(obs, self.history_encoder(obs, hist))

    def forward(self, x):
        reflected = torch.cat((mirror_obs(x[..., :35]),
                               mirror_obs(x[..., 35:].reshape(-1, 12, 35)).flatten(1)), -1)
        a, b = self.raw(torch.cat((x, reflected), 0)).chunk(2, 0)
        return .5*(a+mirror_action(b))

    def warm_soft_expert(self, payload, index=2):
        raw = {k.removeprefix('mlp.'):v for k,v in payload['actor_state_dict'].items() if k.startswith('mlp.')}
        self.history_encoder.load_state_dict({k.removeprefix('history_encoder.'):v for k,v in raw.items()
                                            if k.startswith('history_encoder.')})
        prefix = f'experts.{index}.'
        self.head.load_state_dict({k.removeprefix(prefix):v for k,v in raw.items() if k.startswith(prefix)})
        return self

class A1StairExpert(nn.Module):
    """Graduated a1acd1a8 climb head with its blind router removed entirely."""
    def __init__(self):
        super().__init__()
        self.register_buffer('mean',torch.zeros(35))
        self.register_buffer('scale',torch.ones(35))
        self.encoder=nn.Sequential(nn.Linear(420,128),nn.ELU(),nn.Linear(128,64),nn.ELU(),nn.Linear(64,16))
        self.head=nn.Sequential(nn.Linear(51,256),nn.ELU(),nn.Linear(256,128),nn.ELU(),
                                nn.Linear(128,64),nn.ELU(),nn.Linear(64,6))
    def raw(self,x):
        obs=x[:,:35].clone();hist=x[:,35:].reshape(-1,12,35).clone()
        obs[:,29]=1.;hist[:,:,29]=1.
        hn=((hist-self.mean)/self.scale).clamp(-10.,10.).flatten(1)
        z=self.encoder(hn)
        z=torch.cat((z[:,:3],z[:,3:5].sigmoid(),z[:,5:]),1)
        return self.head(torch.cat((obs,z),1))
    def forward(self,x):
        reflected=torch.cat((mirror_obs(x[:,:35]),mirror_obs(x[:,35:].reshape(-1,12,35)).flatten(1)),1)
        a,b=self.raw(torch.cat((x,reflected),0)).chunk(2,0)
        return .5*(a+mirror_action(b))
    def load_a1(self,payload):
        state=payload['actor_state_dict'];prefix='mlp.e1.'
        self.mean.copy_(state[prefix+'encoder.mean']);self.scale.copy_(state[prefix+'encoder.scale'])
        self.encoder.load_state_dict({k.removeprefix(prefix+'encoder.net.'):v for k,v in state.items()
                                      if k.startswith(prefix+'encoder.net.')})
        self.head.load_state_dict({k.removeprefix(prefix+'head.'):v for k,v in state.items() if k.startswith(prefix+'head.')})
        return self

def make_stair(payload):
    architecture=payload.get('architecture')
    if architecture=='cnn12_obs_linear_residual':model=ResidualStair()
    else:model=A1StairExpert() if architecture=='a1_head_only_z2' else StairExpert()
    model.load_state_dict(payload['stair'])
    return model

class ResidualStair(nn.Module):
    """One pure neural stair expert with an equivariant observation-linear residual."""
    def __init__(self):
        super().__init__();self.base=StairExpert();self.repair=nn.Linear(35,6)
        nn.init.zeros_(self.repair.weight);nn.init.zeros_(self.repair.bias)
    def forward(self,x):
        obs=x[:,:35]
        a,b=self.repair(torch.cat((obs,mirror_obs(obs)),0)).chunk(2,0)
        return self.base(x)+.5*(a+mirror_action(b))
    @torch.no_grad()
    def set_coordinates(self,theta):
        self.repair.weight.zero_();self.repair.bias.zero_()
        t=torch.as_tensor(theta,dtype=self.repair.weight.dtype,device=self.repair.weight.device)
        self.repair.bias.copy_(t[:3][[0,1,0,1,2,2]])
        for row in (0,2):
            self.repair.weight[row,[11,13]]=t[3]/2
            self.repair.weight[row,[17,19]]=t[5]/2
            self.repair.weight[row,7]=t[7]
        for row in (1,3):
            self.repair.weight[row,[11,13]]=t[4]/2
            self.repair.weight[row,[17,19]]=t[6]/2
            self.repair.weight[row,7]=t[8]
        for row in (4,5):
            self.repair.weight[row,7]=t[9];self.repair.weight[row,5]=t[10]
            self.repair.weight[row,0]=t[11]
            self.repair.weight[row,[20,21]]=-t[11]*.625/2

