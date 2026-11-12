"""One combined continuation: full remaining ranges and MOD4-feasible resets."""
from pathlib import Path
import json
import math
import torch
import warp as wp
from isaaclab.utils.math import quat_from_euler_xyz
from mod4v1_scut.config import observation_component
from .scut_flat_env import tensor
from .scut_flat_velocity_push_env import ScutVelocityPushDR, ScutFlatVelocityPushEnv


class RemainingDR(ScutVelocityPushDR):
    native_spring_damping = True

    def __init__(self, env):
        super().__init__(env)
        n, j = env.num_envs, len(self.robot.joint_names)
        self.startup_com_delta = torch.empty((n, 3), device=self.device).uniform_(-1., 1.)
        self.startup_com_delta *= self.startup_com_delta.new_tensor([.04, .02, .02])
        self.kp_scale = torch.ones((n, j), device=self.device)
        self.kd_scale = torch.ones_like(self.kp_scale)
        self.gain_last_step = torch.zeros(n, dtype=torch.long, device=self.device)
        self.gain_count = torch.zeros_like(self.gain_last_step)
        self.gain_generator = torch.Generator(device=self.device).manual_seed(int(env.cfg.seed)+2121)
        self.passive_joint_ids = sorted(set(self.passive_joint_ids + [i for i,n in enumerate(self.robot.joint_names) if n.endswith("_f3r1_joint")]))
        self._startup_friction_ready = False
        all_ids = torch.arange(n, device=self.device)
        self._add_joint_friction(all_ids, self.leg_active_joint_ids, (.25, 1.), (.25, 1.), (.05, .2))
        self._add_joint_friction(all_ids, self.wheel_joint_ids, (.05, .25), (0., 0.), (0., .01))
        self._add_joint_friction(all_ids, self.passive_joint_ids, (.05, .1), (0., 0.), (.01, .025))
        self._startup_friction_ready = True
        self.startup_joint_friction = tensor(self.robot.root_view.get_dof_friction_properties()).clone().to(self.device)
        self.nominal_joint_damping = tensor(self.robot.data.default_joint_damping).clone().to(self.device)
        self.nominal_joint_stiffness = tensor(self.robot.data.default_joint_stiffness).clone().to(self.device)
        self.spring_damping_scale = torch.ones((n, len(env.gas_ids)), device=self.device)
        env._leg_damping_scale = torch.ones((n, 4), device=self.device)

    def _add_joint_friction(self, ids, joint_ids, static_range, dynamic_range, viscous_range):
        if getattr(self, "_startup_friction_ready", False):
            return
        super()._add_joint_friction(ids, joint_ids, static_range, dynamic_range, viscous_range)

    def __call__(self, env, env_ids):
        ids = (torch.arange(env.num_envs, device=self.device) if env_ids is None else
               torch.as_tensor(env_ids, device=self.device, dtype=torch.long).flatten())
        # Parent material/mass/effort lifecycle remains intact. COM reasserts its startup sample;
        # the override above prevents reset from resampling startup joint friction.
        # Parent spring sampler uses a scalar buffer, so restore its full buffer afterwards.
        saved_spring = self.spring_damping_scale
        self.spring_damping_scale = torch.ones(env.num_envs, device=self.device)
        super().__call__(env, ids)
        self.spring_damping_scale = saved_spring
        step = int(env._sim_step_counter)//int(env.cfg.decimation)
        chosen = ids[(self.gain_count[ids] == 0) | (step-self.gain_last_step[ids] >= 720)]
        if chosen.numel():
            shape = (len(chosen), self.kp_scale.shape[1])
            self.kp_scale[chosen] = torch.empty(shape, device=self.device).uniform_(.75, 1.25, generator=self.gain_generator)
            self.kd_scale[chosen] = torch.empty(shape, device=self.device).uniform_(.75, 1.25, generator=self.gain_generator)
            self.spring_damping_scale[chosen] = torch.empty((len(chosen), len(env.gas_ids)), device=self.device).uniform_(.5, 1.5, generator=self.gain_generator)
            self.gain_last_step[chosen] = step
            self.gain_count[chosen] += 1
            # Implicit non-motor damping gets scaled natively. Gas stiffness is plant-owned.
            native_damping = self.nominal_joint_damping[chosen]*self.kd_scale[chosen]
            native_damping[:, env.active_ids] = 0.
            native_damping[:, env.gas_ids] = 3.*self.spring_damping_scale[chosen]
            self.robot.write_joint_damping_to_sim_index(damping=native_damping, env_ids=chosen)
            for actuator in self.robot.actuators.values():
                jids = actuator.joint_indices
                values = native_damping[:, jids]
                if torch.is_tensor(actuator.damping): actuator.damping[chosen] = values
                else: tensor(actuator.damping)[chosen] = values
        # Parent mild gain sampling never overwrites the actual eligible-reset gain sample.
        self.leg_gain_scale[ids] = self.kp_scale[ids][:, env.active_ids[:4]]
        self.wheel_gain_scale[ids] = self.kd_scale[ids][:, env.active_ids[4:]]
        env._leg_damping_scale[ids] = self.kd_scale[ids][:, env.active_ids[:4]]

    def summary(self):
        row = super().summary()
        row.update(profile="step7_remaining_full_ranges_mod4_reset_v1", missing_dr=[],
            nominal_fraction_target="no nominal gain mixture; reference full gain ranges",
            base_com_delta_m={"x": [-.04,.04], "y": [-.02,.02], "z": [-.02,.02]},
            base_com_sampling="startup; fixed across reset; nominal + immutable sample",
            pd_gains={"kp_scale": [.75,1.25], "kd_scale": [.75,1.25],
                "sampling": "first reset and eligible reset after720 global policy steps",
                "leg_explicit": "Kp60*scale,Kd2*scale; wheelKd0.6*scale; original DC envelope",
                "passive": "native nominal damping * scale; zero stiffness remains zero",
                "gas": "plant stiffness2000 retained; native damping3*[.5,1.5]; no second damping torque"},
            joint_friction_sampling="startup independently by selected joint; fixed across resets",
            spring_damping_scale_range=[.5,1.5],
            reset_distribution=self.env.reset_distribution_summary())
        return row

    def checkpoint_state(self):
        e = self.env
        return {"scope": "recorded DR samples/timers; continuation still fresh physical episode",
            "com_delta": self.startup_com_delta, "joint_friction": self.startup_joint_friction,
            "kp_scale": self.kp_scale, "kd_scale": self.kd_scale,
            "gain_last_step": self.gain_last_step, "gain_count": self.gain_count,
            "spring_damping_scale": self.spring_damping_scale,
            "body_mass_scale": self.body_mass_scale, "effort_scale": self.effort_scale,
            "material_samples": self.startup_materials, "material_bucket_ids": self.material_bucket_ids,
            "velocity_push_count": e.velocity_push_count, "velocity_push_time_left": e.velocity_push_time_left,
            "velocity_push_last_delta": e.velocity_push_last_delta,
            "external_timer": e._external_timer, "external_hold": e._external_hold,
            "action_delay_ticks": e._action_delay_ticks, "sensor_delay_ticks": e._sensor_delay_ticks,
            "reset_modes": e.reset_modes, "reset_count_by_mode": e.reset_count_by_mode}


class ScutFlatRemainingDREnv(ScutFlatVelocityPushEnv):
    body_mass_dr_class = RemainingDR
    ground_reset_fraction = .50  # saved ground modes .3+.2; air modes disabled in reference

    def __init__(self, cfg, meta, bank):
        self._remaining_reset_ready = False
        super().__init__(cfg, meta, bank)
        data = json.loads((Path(__file__).with_name("remaining_reset_bank.json")).read_text())
        self.reset_bank_info = data["summary"]
        self._reset_q_bank = torch.tensor(data["positions"], device=self.device)
        self._reset_qd_front = torch.tensor(data["velocity_front_tangent"], device=self.device)
        self._reset_qd_rear = torch.tensor(data["velocity_rear_tangent"], device=self.device)
        self._reset_lengths = torch.tensor(data["lengths"], device=self.device)
        self._reset_angles = torch.tensor(data["angles"], device=self.device)
        self._reset_native_names = data["joint_names"]
        self._reset_cols = [self._reset_native_names.index(n) for n in self.robot.joint_names]
        self._reset_modes_bank = [torch.tensor(data["mode_indices"][key],device=self.device,dtype=torch.long)
                                  for key in ["normal","ground_positive","ground_negative"]]
        self.reset_modes = torch.zeros(self.num_envs,device=self.device,dtype=torch.long)
        self.reset_count_by_mode = torch.zeros(3,device=self.device,dtype=torch.long)
        self.reset_length_samples = torch.zeros((self.num_envs,2),device=self.device)
        self.reset_angle_samples = torch.zeros_like(self.reset_length_samples)
        self._ground_command_until = torch.zeros(self.num_envs,device=self.device,dtype=torch.long)
        self._ground_original_command = self.command.clone()
        self._ground_original_heading = self.heading_env.clone()
        self._ground_reset_command = self.command.clone()
        self._remaining_reset_ready = True

    def reset_distribution_summary(self):
        return {"mode_probabilities": {"normal": .5, "ground_positive": .3, "ground_negative": .2},
            "ground_mode_per_leg": "independent conditional positive.6/negative.4",
            "leg_length_normal_m": [.13,.32], "leg_angle_normal_rad": [-math.pi/2,3*math.pi/4],
            "ground_length_m": self.reset_bank_info.get("ground_effective_length_m"),
            "joint_position_source": "MOD4 original exact linkage solver; bank generated only on physical feasible branch",
            "velocity_leg_active_rad_s": [-math.pi/2,math.pi/2], "velocity_wheel_rad_s": [-50.,50.],
            "passive_velocity": "closure-consistent kinematic tangent, not independently random joint velocities",
            "wheel_angle_rad": [-2*math.pi,2*math.pi], "ground_root_height_m": .25,
            "zero_torque_ground_s": .2, "ground_command_override_s": 1.5,
            "ground_command_range": {"vx":[-1.,1.],"vy":[0.,0.],"wz":[-1.,1.]}, "bank": self.reset_bank_info,
            "source_link_lengths_copied": False}

    def _reset_idx(self, ids):
        super()._reset_idx(ids)
        if not self._remaining_reset_ready:
            return
        ids = torch.as_tensor(ids,device=self.device,dtype=torch.long).flatten()
        n = len(ids)
        if not n:return
        gen = self.reset_generator
        samples = torch.rand(n,device=self.device,generator=gen)
        ground = samples >= .5
        mode = torch.zeros((n,2),device=self.device,dtype=torch.long)
        mode[ground] = torch.where(torch.rand((int(ground.sum()),2),device=self.device,generator=gen)<.6,1,2)
        self.reset_modes[ids] = torch.where(ground,mode[:,0],0)
        self.reset_count_by_mode.add_(torch.bincount(self.reset_modes[ids],minlength=3))
        q = tensor(self.robot.data.default_joint_pos)[ids].clone()
        qd = torch.zeros_like(q)
        lengths = torch.zeros((n,2),device=self.device);angles=lengths.clone()
        for sideidx,side in enumerate(["left","right"]):
            choice = torch.zeros(n,device=self.device,dtype=torch.long)
            for k,options in enumerate(self._reset_modes_bank):
                mask=mode[:,sideidx]==k
                choice[mask]=options[torch.randint(len(options),(int(mask.sum()),),device=self.device,generator=gen)]
            selected_q = self._reset_q_bank[choice][:,self._reset_cols]
            selected_vf = self._reset_qd_front[choice][:,self._reset_cols]
            selected_vr = self._reset_qd_rear[choice][:,self._reset_cols]
            cols=[i for i,name in enumerate(self.robot.joint_names) if name.startswith(side+"_") and "guide" not in name]
            q[:,cols]=selected_q[:,cols]
            vf=torch.empty((n,1),device=self.device).uniform_(-math.pi/2,math.pi/2,generator=gen)
            vr=torch.empty((n,1),device=self.device).uniform_(-math.pi/2,math.pi/2,generator=gen)
            qd[:,cols]=selected_vf[:,cols]*vf+selected_vr[:,cols]*vr
            lengths[:,sideidx]=self._reset_lengths[choice];angles[:,sideidx]=self._reset_angles[choice]
        for jid in self.full_dr.wheel_joint_ids:
            q[:,jid]=torch.empty(n,device=self.device).uniform_(-2*math.pi,2*math.pi,generator=gen)
            qd[:,jid]=torch.empty(n,device=self.device).uniform_(-50.,50.,generator=gen)
        self.reset_length_samples[ids]=lengths;self.reset_angle_samples[ids]=angles
        root=tensor(self.robot.data.default_root_state)[ids].clone()
        root[:,:3]+=self.scene.env_origins[ids]
        # Flat reference default root height; explicit ground mode uses .25m.
        root[ground,2]=self.scene.env_origins[ids[ground],2]+.25
        roll=torch.empty(n,device=self.device).uniform_(-.15,.15,generator=gen)
        pitch=torch.empty(n,device=self.device).uniform_(-.15,.15,generator=gen)
        yaw=torch.empty(n,device=self.device).uniform_(-math.pi,math.pi,generator=gen)
        root[:,3:7]=quat_from_euler_xyz(roll,pitch,yaw);root[:,7:]=0.
        self.robot.write_root_state_to_sim(root,env_ids=ids)
        self.robot.write_joint_state_to_sim(q,qd,env_ids=ids)
        self.actions[ids]=0.;self.torque[ids]=0.
        self.zero_torque_remaining[ids]=torch.where(ground,10,0)
        self._ground_command_until[ids]=torch.where(ground,75,0)
        self._ground_original_command[ids]=self.command[ids]
        self._ground_original_heading[ids]=self.heading_env[ids]
        self._ground_reset_command[ids]=0.
        self._ground_reset_command[ids,0]=torch.empty(n,device=self.device).uniform_(-1.,1.,generator=gen)
        self._ground_reset_command[ids,2]=torch.empty(n,device=self.device).uniform_(-1.,1.,generator=gen)
        self.command[ids[ground]]=self._ground_reset_command[ids[ground]]
        self.heading_env[ids[ground]]=False
        self._execution_pending[ids]=True;self._sensor_pending[ids]=True
        self.reward.reset(ids)
        self.reward.command.copy_(self.command);self.reward.height_cmd.copy_(self.height)
        self.reward._invalidate_step_caches()

    def _pre_physics_step(self, actions):
        super()._pre_physics_step(actions)
        if self._remaining_reset_ready:
            active=self.episode_length_buf < self._ground_command_until
            pending=self._ground_command_until > 0
            expired=pending & ~active
            self.command[expired]=self._ground_original_command[expired]
            self.heading_env[expired]=self._ground_original_heading[expired]
            self._ground_command_until[expired]=0
            self.command[active]=self._ground_reset_command[active]
            self.reward.command.copy_(self.command)

    def _encode(self):
        obs=super()._encode()
        dr=getattr(self,"full_dr",None)
        if hasattr(dr,"kd_scale") and getattr(self,"_delay_ready",False):
            kd=torch.cat((2.*dr.kd_scale[:,self.active_ids[:4]],.6*dr.kd_scale[:,self.active_ids[4:]]),-1)*dr.effort_scale
            extra=obs["critic"][:,39:].clone()
            extra[:,6:12]=observation_component(self.reward.cfg,"joint_damping",kd,"critic")
            obs["critic"]=torch.cat((obs["critic"][:,:39],extra),-1)
            self.reward.cache_raw_observations(dict(policy=obs["policy"]),dict(critic=obs["critic"][:,:39],extra=extra))
        return obs
