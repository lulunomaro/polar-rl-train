"""Physical-time delay DR in the existing MOD4 PhysX/PPO environment.

Policy/PD clocks remain 20/10 ms. Only sensor slots 4:22 and execution
setpoints are delayed; raw policy actions and commands stay current.
"""
from __future__ import annotations
import os
import torch
from .scut_flat_env import tensor
from .scut_flat_obs_noise_env import ScutFlatObsNoiseEnv, ObservationNoiseDRStage4
from mod4v1_scut.config import observation_component


class PhysicalDelayDR(ObservationNoiseDRStage4):
    def summary(self):
        row = super().summary()
        row.update(profile="flat_physical_delay_dr_v1",
                   stage="existing parent DR plus physical-time per-episode action/sensor delays",
                   delay=self.env.physical_delay_summary(),
                   missing_dr=["full_SCUT_mass_COM_material_ranges"])
        return row

    def __init__(self, env):
        super().__init__(env)
        self.env = env


class ScutFlatPhysicalDelayEnv(ScutFlatObsNoiseEnv):
    # The repair entry point follows the current workspace closure contract.
    enforce_closure_reset = True

    def __init__(self, cfg, meta, bank):
        self._delay_ready = False
        self._delay_trace = []
        super().__init__(cfg, meta, bank)
        self._delay_dt = float(cfg.sim.dt)
        quantum_ms = float(os.environ.get("PHYSICAL_DELAY_QUANTUM_MS", "5"))
        quantum_ticks = round(quantum_ms / (1000 * self._delay_dt))
        if quantum_ticks < 1 or abs(quantum_ticks*self._delay_dt*1000-quantum_ms)>1e-6:
            raise ValueError("Delay quantum must be an integral positive number of physics steps")
        self._delay_quantum_ticks = quantum_ticks
        def options(kind):
            lo = float(os.environ.get(f"PHYSICAL_{kind}_DELAY_MIN_MS", "0"))
            hi = float(os.environ.get(f"PHYSICAL_{kind}_DELAY_MAX_MS", "5"))
            count = round((hi-lo)/quantum_ms)
            if lo < 0 or hi < lo or abs(count*quantum_ms-(hi-lo))>1e-6:
                raise ValueError(f"Invalid {kind} delay range")
            values = [round((lo+i*quantum_ms)/(1000*self._delay_dt)) for i in range(count+1)]
            if any(abs(v*self._delay_dt*1000-(lo+i*quantum_ms))>1e-6 for i,v in enumerate(values)):
                raise ValueError("Delay must align to physics time")
            return torch.tensor(values,device=self.device,dtype=torch.long)
        self._action_options = options("ACTION")
        self._sensor_options = options("SENSOR")
        n = self.num_envs
        self._execution_history = torch.zeros((int(self._action_options.max())+1,n,6),device=self.device)
        self._sensor_history = torch.zeros((int(self._sensor_options.max())+1,n,18),device=self.device)
        self._delay_env_ids = torch.arange(n,device=self.device)
        self._issued_targets = self.targets.clone()
        self._execution_pending = torch.ones(n,device=self.device,dtype=torch.bool)
        self._sensor_pending = self._execution_pending.clone()
        self._action_delay_ticks = torch.zeros((n,2),device=self.device,dtype=torch.long)
        self._sensor_delay_ticks = torch.zeros((n,4),device=self.device,dtype=torch.long)
        self._sensor_last_tick = -1
        self._sensor_sample_count = 0
        self._action_sample_count = 0
        self._trace_enabled = os.environ.get("PHYSICAL_DELAY_TRACE", "0") == "1"
        self._delay_ready = True
        self.full_dr = PhysicalDelayDR(self)
        self.mild_dr = self.full_dr
        self._mild_dr = self.full_dr
        self._resample_delays(torch.arange(n,device=self.device))

    def physical_delay_summary(self):
        return dict(physics_dt_ms=self._delay_dt*1000,policy_dt_ms=self.step_dt*1000,
                    pd_dt_ms=10.0,quantum_ms=self._delay_quantum_ticks*self._delay_dt*1000,
                    action_options_ms=(self._action_options*self._delay_dt*1000).tolist(),
                    sensor_options_ms=(self._sensor_options*self._delay_dt*1000).tolist(),
                    sampling="independent group lag at env reset; fixed within episode",
                    policy_sensor_slots=[4,22],policy_action_slots=[22,28],
                    previous_action="last raw clamped policy output; execution delay does not overwrite it",
                    critic="existing undelayed privileged stream",low_pass_filter=False,
                    buffer_time_is_not_pd_latency=True)

    def _resample_delays(self, ids):
        count = int(ids.numel())
        if not count:return
        for target, opts in ((self._action_delay_ticks,self._action_options),
                             (self._sensor_delay_ticks,self._sensor_options)):
            target[ids] = opts[torch.randint(len(opts),(count,target.shape[1]),device=self.device)]
        self._execution_pending[ids] = True
        self._sensor_pending[ids] = True

    def _gather(self,history, ticks, start, end):
        return history[ticks,self._delay_env_ids,start:end]

    def _sensor_frame(self):
        d=self.view.data;r=self.reward
        q=(d.joint_pos-d.default_joint_pos)[:,r._actuate_idx].clone();q[:,4:]=0.0
        v=d.joint_vel[:,r._actuate_idx]
        blocks=dict(root_ang_vel_b=d.root_ang_vel_b,projected_gravity_b=d.projected_gravity_b,
                    joint_pos=q,joint_vel_leg=v[:,:4],joint_vel_wheel=v[:,4:])
        return torch.cat([observation_component(r.cfg,k,x,"policy") for k,x in blocks.items()],-1)

    def _sample_sensors(self,tick):
        frame=self._sensor_frame()
        if tick!=self._sensor_last_tick:
            self._sensor_history[1:]=self._sensor_history[:-1].clone()
            self._sensor_history[0]=frame
            self._sensor_last_tick=tick
            self._sensor_sample_count+=1
        pending=self._sensor_pending
        if bool(pending.any()):
            self._sensor_history[:,pending]=frame[pending].unsqueeze(0)
            self._sensor_pending[pending]=False
        return frame

    def _pre_physics_step(self,actions):
        actions=actions.to(self.device).clamp(-6,6)
        super()._pre_physics_step(actions)
        if self._delay_ready:self._issued_targets.copy_(self.targets)

    def _apply_action(self):
        if self._delay_ready:
            tick=int(self._sim_step_counter)-1
            self._sample_sensors(tick)
            history=self._execution_history
            history[1:]=history[:-1].clone();history[0]=self._issued_targets
            pending=self._execution_pending
            if bool(pending.any()):
                history[:,pending]=self._issued_targets[pending].unsqueeze(0)
                self._execution_pending[pending]=False
            self.targets[:,:4]=self._gather(history,self._action_delay_ticks[:,0],0,4)
            self.targets[:,4:]=self._gather(history,self._action_delay_ticks[:,1],4,6)
            self._action_sample_count+=1
            if self._trace_enabled and len(self._delay_trace)<80:
                self._delay_trace.append(dict(tick=tick,time_ms=tick*self._delay_dt*1000,
                    pd_refresh=(int(self._sim_step_counter)-1)%4==0,
                    issued=self._issued_targets[0].tolist(),executed=self.targets[0].tolist(),
                    raw_action=self.actions[0].tolist(),action_ticks=self._action_delay_ticks[0].tolist()))
        super()._apply_action()

    def _get_observations(self):
        obs=super()._get_observations()
        if not self._delay_ready:return obs
        frame=self._sample_sensors(int(self._sim_step_counter))
        sensor=torch.cat([self._gather(self._sensor_history,self._sensor_delay_ticks[:,i],a,b)
                          for i,(a,b) in enumerate([(0,3),(3,6),(6,12),(12,18)])],-1)
        # Noise stays after the physical history read; critic sensors stay current.
        policy=obs["policy"].clone()
        policy[:,4:22]=sensor+(policy[:,4:22]-frame)
        obs["policy"]=policy
        return obs

    def _encode(self):
        obs = super()._encode()
        if not self._delay_ready:
            return obs
        # Preserve the 78-D critic layout, but report the DR that is applied.
        # The actor's 35-D input is unchanged.
        r = self.reward
        extra = obs["critic"][:, 39:].clone()
        gains = self.full_dr
        values = {
            "joint_stiffness": (slice(0, 6), torch.cat((60.0 * gains.leg_gain_scale,
                                                        torch.zeros_like(gains.wheel_gain_scale)), -1)),
            "joint_damping": (slice(6, 12), torch.cat((torch.full_like(gains.leg_gain_scale, 2.0),
                                                       0.6 * gains.wheel_gain_scale), -1)),
            "obs_delay_steps": (slice(18, 22), self._sensor_delay_ticks *
                                  (self._delay_dt / 0.005)),
            "act_delay_steps": (slice(22, 24), self._action_delay_ticks *
                                  (self._delay_dt / 0.005)),
            "body_mass_scale": (slice(32, 33), gains.factor[:, None]),
            "body_material": (slice(33, 39), torch.stack((gains.material_mu,
                gains.material_mu, torch.zeros_like(gains.material_mu),
                gains.material_mu, gains.material_mu, torch.zeros_like(gains.material_mu)), -1)),
        }
        for name, (slots, value) in values.items():
            extra[:, slots] = observation_component(r.cfg, name, value, "critic")
        obs["critic"] = torch.cat((obs["critic"][:, :39], extra), -1)
        r.cache_raw_observations(dict(policy=obs["policy"]),
                                dict(critic=obs["critic"][:, :39], extra=extra))
        return obs

    def _reset_idx(self,ids):
        super()._reset_idx(ids)
        if self._delay_ready:
            self._resample_delays(torch.as_tensor(ids,device=self.device,dtype=torch.long).flatten())
