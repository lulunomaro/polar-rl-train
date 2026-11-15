"""Second round: fixed20pct nominal environments beside unchanged full-range DR."""
import torch
import warp as wp
from .scut_flat_env import tensor
from .scut_flat_remaining_dr_env import RemainingDR,ScutFlatRemainingDREnv

class MixedRemainingDR(RemainingDR):
    def __init__(self,env):
        super().__init__(env)
        self.nominal_env_mask=torch.arange(env.num_envs,device=self.device)%5==4
        ids=self.nominal_env_mask.nonzero().flatten()
        self.body_mass_scale[ids]=1.;self.total_mass_scale[ids]=1.
        self.startup_com_delta[ids]=0.
        self.startup_materials[ids.cpu()]=self.materials[ids.cpu()]
        for values in self.material_bucket_ids.values():values[ids.cpu()]=-1
        fr=self.startup_joint_friction
        fr[ids,:,0]=self.static_friction_default[ids]
        fr[ids,:,1]=(self.dynamic_friction_default if self.dynamic_friction_default is not None else self.static_friction_default)[ids]
        if self.viscous_friction_default is None:fr[ids,:,2]=0.
        else:fr[ids,:,2]=self.viscous_friction_default[ids]
        self.robot.write_joint_friction_coefficient_to_sim(joint_friction_coeff=fr[ids,:,0],joint_dynamic_friction_coeff=fr[ids,:,1],joint_viscous_friction_coeff=fr[ids,:,2],joint_ids=self.joint_ids,env_ids=ids)
        self._write_body_mass_inertia(ids)
        self._write_startup_materials(ids)

    def __call__(self,env,env_ids):
        super().__call__(env,env_ids)
        ids=torch.arange(env.num_envs,device=self.device) if env_ids is None else torch.as_tensor(env_ids,device=self.device,dtype=torch.long).flatten()
        ids=ids[self.nominal_env_mask[ids]]
        if not ids.numel():return
        self.kp_scale[ids]=1.;self.kd_scale[ids]=1.;self.spring_damping_scale[ids]=1.
        self.leg_gain_scale[ids]=1.;self.wheel_gain_scale[ids]=1.;env._leg_damping_scale[ids]=1.
        self.effort_scale[ids]=1.;self.torque_noise_scale[ids]=0.
        # Parent resets also randomize unselected colliders. Nominal means every shape.
        cpu_ids=ids.to(device="cpu",dtype=torch.int32)
        materials=tensor(self.robot.root_view.get_material_properties()).clone().cpu()
        materials[cpu_ids.long()]=self.materials[cpu_ids.long()]
        self.robot.root_view.set_material_properties(wp.from_torch(materials.contiguous(),dtype=wp.float32),wp.from_torch(cpu_ids,dtype=wp.int32))
        native=self.nominal_joint_damping[ids].clone();native[:,env.active_ids]=0.;native[:,env.gas_ids]=3.
        self.robot.write_joint_damping_to_sim_index(damping=native,env_ids=ids)
        for actuator in self.robot.actuators.values():tensor(actuator.damping)[ids]=native[:,actuator.joint_indices]

    def summary(self):
        row=super().summary()
        row.update(profile="remaining_dr_fixed20pct_nominal_v2",nominal_fraction_target=.2,sampling_mixture={"nominal_envs":int(self.nominal_env_mask.sum()),"fullDR_envs":int((~self.nominal_env_mask).sum()),"assignment":"fixed envID modulo5==4","DR_range_reduction":False,"reset_distribution":"same MOD4 feasible normal/ground distribution for both groups","nominal":"asset parameters;gains/effort1;zero delay/noise/wrench/push"})
        return row

    def checkpoint_state(self):
        row=super().checkpoint_state();row["nominal_env_mask"]=self.nominal_env_mask
        return row

class ScutFlatMixedRemainingDREnv(ScutFlatRemainingDREnv):
    body_mass_dr_class=MixedRemainingDR

    def __init__(self,cfg,meta,bank):
        super().__init__(cfg,meta,bank)
        ids=self.full_dr.nominal_env_mask.nonzero().flatten()
        self._resample_delays(ids)
        self.velocity_push_time_left[ids]=1e9
        self._external_timer[ids]=1e9

    def _resample_delays(self,ids):
        super()._resample_delays(ids)
        dr=getattr(self,"full_dr",None)
        if hasattr(dr,"nominal_env_mask"):
            selected=ids[dr.nominal_env_mask[ids]]
            self._action_delay_ticks[selected]=0;self._sensor_delay_ticks[selected]=0

    def _reset_idx(self,ids):
        super()._reset_idx(ids)
        dr=getattr(self,"full_dr",None)
        if hasattr(dr,"nominal_env_mask") and getattr(self,"_velocity_push_ready",False):
            ids=torch.as_tensor(ids,device=self.device,dtype=torch.long).flatten()
            selected=ids[dr.nominal_env_mask[ids]]
            self.velocity_push_time_left[selected]=1e9;self._external_timer[selected]=1e9
            self._external_force[selected]=0.;self._external_torque[selected]=0.;self._external_hold[selected]=0

    def _update_external_wrench(self):
        dr=getattr(self,"full_dr",None)
        if hasattr(dr,"nominal_env_mask"):self._external_timer[dr.nominal_env_mask]=1e9
        super()._update_external_wrench()

    def _get_observations(self):
        obs=super()._get_observations()
        dr=getattr(self,"full_dr",None)
        if hasattr(dr,"nominal_env_mask"):
            clean=self._encode()["policy"]
            obs["policy"][dr.nominal_env_mask]=clean[dr.nominal_env_mask]
        return obs
