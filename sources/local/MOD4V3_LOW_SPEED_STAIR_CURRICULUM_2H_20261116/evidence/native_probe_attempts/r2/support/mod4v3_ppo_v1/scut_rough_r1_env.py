"""Current full-DR Flat policy on the R1 shallow SCUT terrain subset."""
import torch
from isaaclab.utils.warp import raycast_mesh
from .scut_flat_env import tensor
from .scut_flat_mixed_dr_env import ScutFlatMixedRemainingDREnv
from rough_r1_terrain import FAMILIES

class ScutRoughR1Env(ScutFlatMixedRemainingDREnv):
    rough_terrain=True
    enforce_closure_reset=True

    def __init__(self,cfg,meta,bank):
        self._r1_ready=False
        super().__init__(cfg,meta,bank)
        t=self.scene['terrain'];self.terrain=t
        self.flat_terrain_mask=t.r1_flat_mask
        self.terrain_family=t.r1_column_families[t.terrain_types]
        self.r1_direction=torch.zeros(self.num_envs,2,device=self.device)
        self.r1_progress_origin=torch.zeros_like(self.r1_direction)
        self.r1_progress_initialized=torch.zeros(self.num_envs,device=self.device,dtype=torch.bool)
        self.r1_signed_distance=torch.zeros(self.num_envs,device=self.device)
        self.r1_ground_min=torch.zeros(self.num_envs,device=self.device)
        self.r1_ground_max=torch.zeros_like(self.r1_ground_min)
        self.r1_boundary=torch.zeros(self.num_envs,device=self.device,dtype=torch.bool)
        self.r1_attempts=torch.zeros(len(FAMILIES),4,device=self.device,dtype=torch.long)
        self.r1_success=torch.zeros_like(self.r1_attempts)
        self.r1_failures=torch.zeros_like(self.r1_attempts)
        self.r1_boundary_counts=torch.zeros_like(self.r1_attempts)
        self.r1_up=0;self.r1_down=0;self.r1_local_steps=0
        self._r1_ready=True
        assert torch.equal(t.r1_nominal_mask,self.full_dr.nominal_env_mask)
        self.done_totals['terrain_boundary']=0

    def _sample_command(self, ids):
        super()._sample_command(ids)
        if not getattr(self, '_r1_ready', False):
            return
        ids=torch.as_tensor(ids,device=self.device,dtype=torch.long).flatten()
        ids=ids[~self.flat_terrain_mask[ids]]
        if not ids.numel():return
        n=len(ids);level=self.terrain.terrain_levels[ids]
        cap=self.command.new_tensor([1.,1.25,1.5,2.2])[level]
        mode=torch.rand(n,device=self.device);sign=torch.where(torch.rand(n,device=self.device)<.5,-1.,1.)
        straight=mode<.6;turn=(mode>=.6)&(mode<.8);spin=mode>=.8
        vx=(.5+torch.rand(n,device=self.device)*(cap-.5))*sign
        wz=torch.zeros(n,device=self.device)
        wz[turn]=torch.empty(int(turn.sum()),device=self.device).uniform_(-1.,1.)
        vx[spin]=0.;wz[spin]=torch.empty(int(spin.sum()),device=self.device).uniform_(1.2,3.)*sign[spin]
        self.command[ids,0]=vx;self.command[ids,1]=0.;self.command[ids,2]=wz
        self.heading_env[ids]=False;self.standing_env[ids]=False;self.heading_target[ids]=0.

    def _set_origins(self,ids):
        t=self.terrain
        pos=t.terrain_origins[t.terrain_levels[ids],t.terrain_types[ids]].clone()+t.r1_offsets[ids]
        starts=pos.clone();starts[:,2]+=5.
        down=torch.zeros_like(starts);down[:,2]=-1.
        hit=raycast_mesh(starts,down,t.r1_wp_mesh,max_dist=10.)[0]
        if not bool(torch.isfinite(hit).all()):raise ValueError('R1 reset ray missed')
        pos[:,2]=hit[:,2]
        t.env_origins[ids]=pos
        self.scene.env_origins[ids]=pos

    def _reset_idx(self,ids):
        ids=torch.as_tensor(ids,device=self.device,dtype=torch.long).flatten()
        if self._r1_ready:
            t=self.terrain
            if self.snapshots is not None:
                level=t.terrain_levels[ids];family=self.terrain_family[ids]
                steps=self.episode_length_buf[ids]
                attempted=(steps>=25)&(~self.flat_terrain_mask[ids])
                failed=self.reset_terminated[ids]
                crossed=(self.r1_signed_distance[ids]>=2.)&((self.r1_ground_max[ids]-self.r1_ground_min[ids])>=.003)
                eligible=attempted&(~failed)
                success=eligible&crossed
                index=family*4+level
                ones=torch.ones(len(ids),device=self.device,dtype=torch.long)
                for values,mask in ((self.r1_attempts,attempted),(self.r1_success,success),(self.r1_failures,attempted&failed),(self.r1_boundary_counts,self.r1_boundary[ids])):
                    values.view(-1).scatter_add_(0,index,ones*mask.long())
                up=success&(level<3)
                down=attempted&failed&(level>0)
                t.terrain_levels[ids]=(level+up.long()-down.long()).clamp(0,3)
                t.terrain_levels[ids[self.flat_terrain_mask[ids]]]=0
                self.r1_up+=int(up.sum());self.r1_down+=int(down.sum())
                self.done_totals['terrain_boundary']+=int(self.r1_boundary[ids].sum())
            self._set_origins(ids)
        super()._reset_idx(ids)
        if self._r1_ready:
            self.r1_direction[ids]=0.;self.r1_signed_distance[ids]=0.
            self.r1_progress_origin[ids]=self.view.data.root_pos_w[ids,:2]
            self.r1_progress_initialized[ids]=False
            self.r1_ground_min[ids]=self.scene.env_origins[ids,2]
            self.r1_ground_max[ids]=self.scene.env_origins[ids,2]
            self.r1_boundary[ids]=False

    def _get_dones(self):
        term,timeout=super()._get_dones()
        if not self._r1_ready:return term,timeout
        pos=self.view.data.root_pos_w
        yaw_quat=self.view.data.root_quat_w
        # Net horizontal displacement along the first valid straight-command direction.
        # qorder comes from the same existing runtime adapter used by the policy.
        from mod4v1_scut.math_ops import euler_xyz_from_quat
        yaw=euler_xyz_from_quat(yaw_quat)[2]
        sign=self.command[:,0].sign()
        direction=torch.stack((yaw.cos()*sign,yaw.sin()*sign),-1)
        straight=(self.command[:,0].abs()>=.5)&(self.command[:,2].abs()<=1.)
        begin=straight&(~self.r1_progress_initialized)
        self.r1_direction[begin]=direction[begin]
        self.r1_progress_origin[begin]=pos[begin,:2]
        self.r1_progress_initialized[begin]=True
        self.r1_signed_distance=((pos[:,:2]-self.r1_progress_origin)*self.r1_direction).sum(-1)
        ground=self.reward.ground_z_est
        self.r1_ground_min=torch.minimum(self.r1_ground_min,ground)
        self.r1_ground_max=torch.maximum(self.r1_ground_max,ground)
        center=self.terrain.terrain_origins[self.terrain.terrain_levels,self.terrain.terrain_types]
        self.r1_boundary.copy_((pos[:,:2]-center[:,:2]).abs().amax(-1)>4.)
        timeout|=self.r1_boundary&(~term)
        self.r1_local_steps+=1
        return term,timeout

    def terrain_summary(self):
        t=self.terrain;nominal=self.full_dr.nominal_env_mask;flat=self.flat_terrain_mask
        population=torch.bincount(self.terrain_family*4+t.terrain_levels,minlength=len(FAMILIES)*4).reshape(len(FAMILIES),4)
        return dict(stage='MOD4-R1',families=list(FAMILIES),population_by_family_level=population.tolist(),attempts=self.r1_attempts.tolist(),success=self.r1_success.tolist(),failures=self.r1_failures.tolist(),boundary_counts=self.r1_boundary_counts.tolist(),level_up=self.r1_up,level_down=self.r1_down,local_policy_steps=self.r1_local_steps,max_level=3,groups=dict(nominal_flat=int((nominal&flat).sum()),nominal_rough=int((nominal&~flat).sum()),DR_flat=int((~nominal&flat).sum()),DR_rough=int((~nominal&~flat).sum())),signed_distance_mean=float(self.r1_signed_distance[~flat].mean()) if bool((~flat).any()) else 0.,ground_variation_mean=float((self.r1_ground_max-self.r1_ground_min)[~flat].mean()) if bool((~flat).any()) else 0.)

    def terrain_checkpoint_state(self):
        return dict(terrain_levels=self.terrain.terrain_levels,terrain_types=self.terrain.terrain_types,offsets=self.terrain.r1_offsets,flat_mask=self.flat_terrain_mask,local_policy_steps=self.r1_local_steps,attempts=self.r1_attempts,success=self.r1_success,failures=self.r1_failures,boundary_counts=self.r1_boundary_counts,level_up=self.r1_up,level_down=self.r1_down,signed_distance=self.r1_signed_distance,progress_origin=self.r1_progress_origin,progress_direction=self.r1_direction,progress_initialized=self.r1_progress_initialized,ground_min=self.r1_ground_min,ground_max=self.r1_ground_max)

    def restore_terrain_curriculum(self, state):
        """Continue saved levels and totals, starting fresh physical episodes."""
        t=self.terrain
        for target,key in ((t.terrain_levels,'terrain_levels'),(t.terrain_types,'terrain_types'),(t.r1_offsets,'offsets'),(self.flat_terrain_mask,'flat_mask'),(self.r1_attempts,'attempts'),(self.r1_success,'success'),(self.r1_failures,'failures'),(self.r1_boundary_counts,'boundary_counts')):
            value=state[key].to(device=target.device,dtype=target.dtype)
            if value.shape!=target.shape:raise ValueError('R1 resume shape mismatch: '+key)
            target.copy_(value)
        self.terrain_family=t.r1_column_families[t.terrain_types]
        self.r1_local_steps=int(state['local_policy_steps'])
        self.r1_up=int(state['level_up']);self.r1_down=int(state['level_down'])
        # The checkpoint has no live solver state; abandon unfinished episode
        # distances instead of counting the restored reset as a curriculum attempt.
        self.snapshots=None
        self.reset()
        return dict(levels_and_types_restored=True,offsets_and_flat_mask_restored=True,cumulative_counters_restored=True,local_policy_steps=self.r1_local_steps,physics='fresh episodes; no partial-episode progress restored',population_by_family_level=self.terrain_summary()['population_by_family_level'])
