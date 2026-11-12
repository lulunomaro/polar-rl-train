"""Unified SCUT Rough-v1 course on current MOD4 full DR and fixed interface."""
import math,json
from pathlib import Path
from copy import deepcopy
import torch
from .scut_rough_r1_env import ScutRoughR1Env
from .scut_flat_mixed_dr_env import ScutFlatMixedRemainingDREnv
from .scut_flat_v2_env import ScutFlatV2Env
from .scut_rough_r2_env import ScutRoughR2Env,configuration_r2
from .scut_flat_env import tensor
from .scut_flat_rewards import make_reward_class
from isaaclab.utils.math import quat_from_euler_xyz
from rough_scut_v1_terrain import FAMILIES

HEIGHTS=((.22,.34),(.22,.32),(.24,.32),(.22,.42),(.22,.34),(.24,.32),(.22,.42),(.24,.32),(.20,.42),(.22,.42),(.24,.32))

class ScutUnifiedRoughV1GroundEnv(ScutRoughR1Env):
    """All terrain levels together; no R0/R1 command caps or staged promotion."""
    enforce_closure_reset=True
    def __init__(self,cfg,meta,bank):
        self._scut_ready=False
        super().__init__(cfg,meta,bank)
        self.command_vx=(-2.2,2.2)
        self.height_range=(.20,.42)
        self.r1_attempts=torch.zeros(len(FAMILIES),10,device=self.device,dtype=torch.long)
        self.r1_success=torch.zeros_like(self.r1_attempts)
        self.r1_failures=torch.zeros_like(self.r1_attempts)
        self.r1_boundary_counts=torch.zeros_like(self.r1_attempts)
        self._scut_ready=True

    def _sample_command(self,ids):
        ScutFlatV2Env._sample_command(self,ids)
        if not getattr(self,'_scut_ready',False):return
        ids=torch.as_tensor(ids,device=self.device,dtype=torch.long).flatten()
        n=len(ids)
        if not n:return
        def uniform(lo,hi):return torch.empty(n,device=self.device).uniform_(lo,hi)
        vx=uniform(-2.2,2.2);wz=uniform(*self.command_wz)
        sign=torch.where(torch.rand(n,device=self.device)<.5,-1.,1.)
        mode=torch.rand(n,device=self.device)
        mode=torch.where(self.episode_length_buf[ids]*self.step_dt>=5.,mode,torch.ones_like(mode))
        standing=torch.rand(n,device=self.device)<self.standing_fraction
        heading=(torch.rand(n,device=self.device)<self.heading_fraction)&~standing
        low=mode<.15;high=(mode>=.15)&(mode<.30)
        fast=(mode>=.30)&(mode<.60);stop=torch.zeros(n,device=self.device,dtype=torch.bool)
        gyro=low|high
        vx[gyro]=uniform(-.1,.1)[gyro]
        wz[low]=uniform(2*math.pi,3.25*math.pi)[low]*sign[low]
        wz[high]=uniform(3.25*math.pi,4.5*math.pi)[high]*sign[high]
        vx[fast]=uniform(2.,2.2)[fast]*sign[fast]
        wz[fast]=uniform(-2*math.pi,2*math.pi)[fast]
        standing[gyro|fast]=False;standing[stop]=True;heading[gyro|fast|stop]=False
        vx[standing]=0.;wz[standing]=0.
        fam=self.terrain_family[ids]
        # Saved per-terrain dash commands, clipped to the current2.2m/s contract.
        for f,lo,hi in ((0,.5,1.5),(4,1.5,2.2),(7,1.5,2.2),(10,2.,2.2)):
            mask=fam==f;vx[mask]=uniform(lo,hi)[mask]*sign[mask]
            wz[mask]=uniform(-.1,.1)[mask];heading[mask]=False;standing[mask]=False
        for f in (2,5):
            mask=fam==f;vx[mask]=uniform(-2.2,2.2)[mask]
            if f==5:wz[mask]=uniform(-math.pi,math.pi)[mask]
            standing[mask]=False
        self.command[ids,0]=vx;self.command[ids,1]=0.;self.command[ids,2]=wz
        self.heading_env[ids]=heading;self.standing_env[ids]=standing
        self.heading_target[ids]=torch.where(heading,uniform(*self.heading_range),0.)
        bounds=self.command.new_tensor(HEIGHTS)[fam]
        self.height[ids]=bounds[:,0]+torch.rand(n,device=self.device)*(bounds[:,1]-bounds[:,0])
        self.command_timer[ids]=uniform(*self.command_resample)

    def _reset_idx(self,ids):
        ids=torch.as_tensor(ids,device=self.device,dtype=torch.long).flatten()
        ready=getattr(self,'_scut_ready',False)
        if ready:
            if self.snapshots is not None:
                level=self.terrain.terrain_levels[ids];family=self.terrain_family[ids]
                attempted=(self.episode_length_buf[ids]>=25)&(~self.flat_terrain_mask[ids])
                failed=self.reset_terminated[ids]
                crossed=(self.r1_signed_distance[ids]>=2.)&((self.r1_ground_max[ids]-self.r1_ground_min[ids])>=.003)
                success=attempted&(~failed)&crossed
                index=family*10+level
                ones=torch.ones(len(ids),device=self.device,dtype=torch.long)
                for values,mask in ((self.r1_attempts,attempted),(self.r1_success,success),(self.r1_failures,attempted&failed),(self.r1_boundary_counts,self.r1_boundary[ids])):
                    values.view(-1).scatter_add_(0,index,ones*mask.long())
                self.done_totals['terrain_boundary']+=int(self.r1_boundary[ids].sum())
            self._set_origins(ids)
        ScutFlatMixedRemainingDREnv._reset_idx(self,ids)
        if ready:
            fam=self.terrain_family[ids]
            axis=ids[(fam==0)|(fam==4)|(fam==7)|(fam==10)]
            if len(axis):
                root=tensor(self.robot.data.default_root_state)[axis].clone()
                root[:,:3]+=self.scene.env_origins[axis]
                ground=self.reset_modes[axis]>0
                root[ground,2]=self.scene.env_origins[axis[ground],2]+.25
                yaw=torch.randint(0,2,(len(axis),),device=self.device,generator=self.reset_generator)*math.pi
                root[:,3:7]=quat_from_euler_xyz(torch.zeros_like(yaw),torch.zeros_like(yaw),yaw)
                root[:,7:]=0.
                self.robot.write_root_state_to_sim(root,env_ids=axis)
        if ready:
            self.r1_direction[ids]=0.;self.r1_signed_distance[ids]=0.
            self.r1_progress_origin[ids]=self.view.data.root_pos_w[ids,:2]
            self.r1_progress_initialized[ids]=False
            self.r1_ground_min[ids]=self.scene.env_origins[ids,2]
            self.r1_ground_max[ids]=self.scene.env_origins[ids,2]
            self.r1_boundary[ids]=False

    def terrain_summary(self):
        t=self.terrain;nominal=self.full_dr.nominal_env_mask;flat=self.flat_terrain_mask
        population=torch.bincount(self.terrain_family*10+t.terrain_levels,minlength=len(FAMILIES)*10).reshape(len(FAMILIES),10)
        return dict(stage='SCUT-Rough-v1-unified',families=list(FAMILIES),population_by_family_level=population.tolist(),attempts=self.r1_attempts.tolist(),success=self.r1_success.tolist(),failures=self.r1_failures.tolist(),boundary_counts=self.r1_boundary_counts.tolist(),level_up=0,level_down=0,local_policy_steps=self.r1_local_steps,max_level=9,level_sampling='all10 fixed rows from launch; no staged admission',groups=dict(nominal_flat=int((nominal&flat).sum()),nominal_rough=int((nominal&~flat).sum()),DR_flat=int((~nominal&flat).sum()),DR_rough=int((~nominal&~flat).sum())),signed_distance_mean=float(self.r1_signed_distance[~flat].mean()),ground_variation_mean=float((self.r1_ground_max-self.r1_ground_min)[~flat].mean()),progress_scope='2m signed traversal with terrain-height variation; not gyro pass metric')

    def terrain_checkpoint_state(self):
        state=super().terrain_checkpoint_state()
        state.update(course='SCUT-Rough-v1-unified',num_levels=10)
        return state

    def restore_terrain_curriculum(self,state):
        if state.get('course')=='SCUT-Rough-v1-unified' and tuple(state['attempts'].shape)==(len(FAMILIES),10):
            return super().restore_terrain_curriculum(state)
        self.parent_terrain_state=state
        self.snapshots=None
        self.reset()
        return dict(parent_terrain_state_retained_as_provenance=True,new_rough_v1_population=True,old_levels_relabelled=False,full_ppo_restoration_separate=True)

def configuration_scut_v1():
    cfg=configuration_r2()
    reference=json.loads((Path(__file__).resolve().parents[1]/'rough_scut_v1_reference.json').read_text())
    cfg.airborne_state_machine_cfg=deepcopy(reference['airborne_state_machine_cfg'])
    cfg.airborne_state_machine_cfg['enter']['wheel_radius']=.0625
    cfg.ctrl_mode_obs_enabled=False
    cfg.jump_takeoff_state_machine_cfg['enabled']=False
    cfg.rewards.update(reference['airborne_reward_weights'])
    return cfg

class ScutUnifiedRoughV1Env(ScutRoughR2Env,ScutUnifiedRoughV1GroundEnv):
    air_reset_fraction=.40
    r2_drop_range=(.08,.30)
    def _make_reward(self,meta):
        return make_reward_class(meta,cfg_factory=configuration_scut_v1)(self.view,self.num_envs,self.device)

    def _reset_idx(self, ids):
        ids = torch.as_tensor(ids, device=self.device, dtype=torch.long).flatten()
        if self._r2_ready:
            failed = torch.zeros(self.num_envs, device=self.device, dtype=torch.bool)
            failed[ids] = self.r2_air_reset[ids] & ~self.r2_recovered[ids] & (self.episode_length_buf[ids] > 0)
            cancelled = torch.zeros_like(failed)
            cancelled[ids] = self.r2_air_reset[ids] & (self.episode_length_buf[ids] == 0)
            before = self.r2_counts[:,0].clone()
            self._r2_count(cancelled, 0)
            self.r2_counts[:,0] = 2*before-self.r2_counts[:,0]
            self._r2_count(failed, 5)
        ScutUnifiedRoughV1GroundEnv._reset_idx(self,ids)
        if not self._r2_ready or not ids.numel():
            return
        for buf in (self.r2_air_reset, self.r2_cleared, self.r2_landed,
                    self.r2_recovered, self.r2_tracked):
            buf[ids] = False
        self.r2_contact_step[ids] = -1
        self.r2_stable_steps[ids] = 0
        self.r2_track_steps[ids] = 0
        self.r2_drop[ids] = 0.
        self.r2_peak_force[ids] = 0.
        level = self.terrain.terrain_levels[ids]
        family = self.terrain_family[ids]
        eligible = (family==3)|(family==6)|(family==8)|(family==9)
        selected = eligible & (torch.rand(len(ids), device=self.device, generator=self.reset_generator) < self.air_reset_fraction)
        if self.r2_force_air:
            selected[:] = True
        air = ids[selected]
        if not air.numel():
            return
        n = len(air)
        gen = self.reset_generator
        choices=(self._bank_h<=.34).nonzero().flatten()
        pick = choices[torch.randint(len(choices), (n,), device=self.device, generator=gen)]
        q = self._bank_q[pick][:, self._bank_ids].clone()
        root = tensor(self.robot.data.default_root_state)[air].clone()
        root[:, :3] += self.scene.env_origins[air]
        requested_height=torch.empty(n,device=self.device).uniform_(.12,.42,generator=gen)
        local_height=torch.maximum(requested_height,self._bank_h[pick]+.08)
        drop=local_height-self._bank_h[pick]
        root[:,2]=self.scene.env_origins[air,2]+local_height
        def uniform(lo, hi):
            return torch.empty(n, device=self.device).uniform_(lo, hi, generator=gen)
        root[:, 3:7] = quat_from_euler_xyz(uniform(-.1,.1), uniform(-.2,.2), uniform(-math.pi,math.pi))
        root[:, 7:] = 0.
        root[:,7]=uniform(-2.2,2.2);root[:,8]=uniform(-.5,.5)
        root[:,10]=uniform(-.05,.05);root[:,11]=uniform(-.1,.1);root[:,12]=uniform(-.5,.5)
        self.robot.write_root_state_to_sim(root, env_ids=air)
        self.robot.write_joint_state_to_sim(q, torch.zeros_like(q), env_ids=air)
        self.actions[air] = 0.
        self.torque[air] = 0.
        self.zero_torque_remaining[air] = 0
        # Replacing a ground reset also removes its 1.5s command override.
        self.command[air] = self._ground_original_command[air]
        self.heading_env[air] = self._ground_original_heading[air]
        self._ground_command_until[air] = 150
        self._ground_original_command[air]=self.command[air]
        self._ground_original_heading[air]=self.heading_env[air]
        self._ground_reset_command[air,0]=uniform(-2.2,2.2)
        self._ground_reset_command[air,1]=0.
        self._ground_reset_command[air,2]=uniform(-math.pi/2,math.pi/2)
        self.command[air]=self._ground_reset_command[air]
        self.height[air]=uniform(.20,.42)
        self.heading_env[air]=False
        self.reset_count_by_mode -= torch.bincount(self.reset_modes[air], minlength=3)
        self.reset_modes[air] = -1  # air is reported separately, not as ground
        self.r2_air_reset[air] = True
        self.r2_drop[air] = drop
        starts = torch.zeros_like(self.r2_air_reset)
        starts[air] = True
        self._r2_count(starts, 0)
        self._execution_pending[air] = True
        self._sensor_pending[air] = True
        self.reward.reset(air)
        self.reward.command.copy_(self.command)
        self.reward.height_cmd.copy_(self.height)
        request = getattr(self.reward, 'airborne_force_enter_request', None)
        if request is None:
            request = torch.zeros(self.num_envs, device=self.device, dtype=torch.bool)
            self.reward.airborne_force_enter_request = request
        request[air] = True
        self.reward._invalidate_step_caches()

    def r2_summary(self):
        row=super().r2_summary()
        row.update(stage='SCUT-Rough-v1-unified',reference_air_probability=.4,eligible_families=[FAMILIES[i] for i in (3,6,8,9)],active_jump=False,reset_height='local ground + max(uniform(.12,.42), feasible_bank_support+.08); feasible support<=.34',air_command_hold_s=3.,no_landing_admission_threshold=True)
        return row
