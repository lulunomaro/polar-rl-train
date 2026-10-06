"""Independent actor feedback corruption; no simulator or global RNG use."""
import math
import torch

CHANNELS={'base_ang_vel':(3,.125,101),'projected_gravity':(3,.025,203),
          'leg_pos':(4,.005,307),'leg_vel':(4,.25,409),'wheel_vel':(2,.5,503)}
EPISODE_LEG_BIAS_RAD=.0075
PROFILES=('off','noise_bias_mild_v1')

class SensorCorruption:
    def __init__(self,num_envs,device,seed,profile):
        assert profile in PROFILES and num_envs>0
        self.n=num_envs;self.device=device;self.profile=profile
        self.bias=torch.zeros((num_envs,4),device=device)
        self.episode=torch.zeros(num_envs,dtype=torch.long,device=device)
        self.bias_rng=torch.Generator(device=device).manual_seed(int(seed)+913007)
        self.noise_rng={k:torch.Generator(device=device).manual_seed(int(seed)+913007+v[2]) for k,v in CHANNELS.items()}
        self.cache={};self.draw_counts={k:0 for k in CHANNELS}

    def reset(self,ids):
        ids=torch.as_tensor(ids,device=self.device,dtype=torch.long)
        if not ids.numel():return
        if self.profile=='off':self.bias[ids]=0.
        else:self.bias[ids]=(2*torch.rand((len(ids),4),device=self.device,generator=self.bias_rng)-1)*EPISODE_LEG_BIAS_RAD
        self.episode[ids]+=1
        for last,_ in self.cache.values():last[ids]=-1

    def apply(self,key,value,tick):
        assert key in CHANNELS and value.shape==(self.n,CHANNELS[key][0])
        assert bool(torch.isfinite(value).all()),'Nonfinite real sensor input'
        if self.profile=='off':return value
        if key not in self.cache:
            self.cache[key]=(torch.full((self.n,),-1,dtype=torch.long,device=self.device),torch.zeros_like(value))
        last,noise=self.cache[key];due=torch.where(last!=int(tick))[0]
        if len(due):
            noise[due]=(2*torch.rand((len(due),value.shape[1]),device=self.device,generator=self.noise_rng[key])-1)*CHANNELS[key][1]
            last[due]=int(tick);self.draw_counts[key]+=len(due)
        return value+noise+(self.bias if key=='leg_pos' else 0.)

    def receipt(self):
        return dict(profile=self.profile,raw_pre_scale_uniform_bounds={k:v[1] for k,v in CHANNELS.items()},
            raw_units={'base_ang_vel':'rad/s','projected_gravity':'dimensionless','leg_pos':'rad','leg_vel':'rad/s','wheel_vel':'rad/s'},
            episode_leg_encoder_bias_bound_rad=EPISODE_LEG_BIAS_RAD,wheel_position_slots_remain_zero=True,
            wheel_position_zero_bias_not_claimed_as_actor_feedback=True,noise_draw_counts=dict(self.draw_counts),
            max_abs_actual_bias_rad=float(self.bias.abs().max()),bias_finite=bool(torch.isfinite(self.bias).all()),
            observation_delay_control_steps=0,action_delay_control_steps=0,engineering_pressure_not_hardware_calibration=True)
