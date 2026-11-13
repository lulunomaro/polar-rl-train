"""Current full-DR Flat policy on the R0 shallow SCUT terrain subset."""
import torch
from isaaclab.utils.warp import raycast_mesh
from .scut_flat_env import tensor
from .scut_flat_mixed_dr_env import ScutFlatMixedRemainingDREnv
from rough_r0_terrain import FAMILIES

class ScutRoughR0Env(ScutFlatMixedRemainingDREnv):
    rough_terrain=True
    enforce_closure_reset=True

    def __init__(self,cfg,meta,bank):
        self._r0_ready=False
        super().__init__(cfg,meta,bank)
        t=self.scene['terrain'];self.terrain=t
        self.flat_terrain_mask=t.r0_flat_mask
        self.terrain_family=t.r0_column_families[t.terrain_types]
        self.r0_direction=torch.zeros(self.num_envs,2,device=self.device)
        self.r0_progress_origin=torch.zeros_like(self.r0_direction)
        self.r0_progress_initialized=torch.zeros(self.num_envs,device=self.device,dtype=torch.bool)
        self.r0_signed_distance=torch.zeros(self.num_envs,device=self.device)
        self.r0_ground_min=torch.zeros(self.num_envs,device=self.device)
        self.r0_ground_max=torch.zeros_like(self.r0_ground_min)
        self.r0_boundary=torch.zeros(self.num_envs,device=self.device,dtype=torch.bool)
        self.r0_attempts=torch.zeros(7,4,device=self.device,dtype=torch.long)
        self.r0_success=torch.zeros_like(self.r0_attempts)
        self.r0_failures=torch.zeros_like(self.r0_attempts)
        self.r0_boundary_counts=torch.zeros_like(self.r0_attempts)
        self.r0_up=0;self.r0_down=0;self.r0_local_steps=0
        self._r0_ready=True
        assert torch.equal(t.r0_nominal_mask,self.full_dr.nominal_env_mask)
        self.done_totals['terrain_boundary']=0

    def _set_origins(self,ids):
        t=self.terrain
        pos=t.terrain_origins[t.terrain_levels[ids],t.terrain_types[ids]].clone()+t.r0_offsets[ids]
        starts=pos.clone();starts[:,2]+=5.
        down=torch.zeros_like(starts);down[:,2]=-1.
        hit=raycast_mesh(starts,down,t.r0_wp_mesh,max_dist=10.)[0]
        if not bool(torch.isfinite(hit).all()):raise ValueError('R0 reset ray missed')
        pos[:,2]=hit[:,2]
        t.env_origins[ids]=pos
        self.scene.env_origins[ids]=pos

    def _reset_idx(self,ids):
        ids=torch.as_tensor(ids,device=self.device,dtype=torch.long).flatten()
        if self._r0_ready:
            t=self.terrain
            if self.snapshots is not None:
                level=t.terrain_levels[ids];family=self.terrain_family[ids]
                steps=self.episode_length_buf[ids]
                attempted=(steps>=25)&(~self.flat_terrain_mask[ids])
                failed=self.reset_terminated[ids]
                crossed=(self.r0_signed_distance[ids]>=2.)&((self.r0_ground_max[ids]-self.r0_ground_min[ids])>=.003)
                eligible=attempted&(~failed)
                success=eligible&crossed
                index=family*4+level
                ones=torch.ones(len(ids),device=self.device,dtype=torch.long)
                for values,mask in ((self.r0_attempts,attempted),(self.r0_success,success),(self.r0_failures,attempted&failed),(self.r0_boundary_counts,self.r0_boundary[ids])):
                    values.view(-1).scatter_add_(0,index,ones*mask.long())
                up=success&(level<3)
                down=attempted&failed&(level>0)
                t.terrain_levels[ids]=(level+up.long()-down.long()).clamp(0,3)
                t.terrain_levels[ids[self.flat_terrain_mask[ids]]]=0
                self.r0_up+=int(up.sum());self.r0_down+=int(down.sum())
                self.done_totals['terrain_boundary']+=int(self.r0_boundary[ids].sum())
            self._set_origins(ids)
        super()._reset_idx(ids)
        if self._r0_ready:
            self.r0_direction[ids]=0.;self.r0_signed_distance[ids]=0.
            self.r0_progress_origin[ids]=self.view.data.root_pos_w[ids,:2]
            self.r0_progress_initialized[ids]=False
            self.r0_ground_min[ids]=self.scene.env_origins[ids,2]
            self.r0_ground_max[ids]=self.scene.env_origins[ids,2]
            self.r0_boundary[ids]=False

    def _get_dones(self):
        term,timeout=super()._get_dones()
        if not self._r0_ready:return term,timeout
        pos=self.view.data.root_pos_w
        yaw_quat=self.view.data.root_quat_w
        # Net horizontal displacement along the first valid straight-command direction.
        # qorder comes from the same existing runtime adapter used by the policy.
        from mod4v1_scut.math_ops import euler_xyz_from_quat
        yaw=euler_xyz_from_quat(yaw_quat)[2]
        sign=self.command[:,0].sign()
        direction=torch.stack((yaw.cos()*sign,yaw.sin()*sign),-1)
        straight=(self.command[:,0].abs()>=.5)&(self.command[:,2].abs()<=1.)
        begin=straight&(~self.r0_progress_initialized)
        self.r0_direction[begin]=direction[begin]
        self.r0_progress_origin[begin]=pos[begin,:2]
        self.r0_progress_initialized[begin]=True
        self.r0_signed_distance=((pos[:,:2]-self.r0_progress_origin)*self.r0_direction).sum(-1)
        ground=self.reward.ground_z_est
        self.r0_ground_min=torch.minimum(self.r0_ground_min,ground)
        self.r0_ground_max=torch.maximum(self.r0_ground_max,ground)
        center=self.terrain.terrain_origins[self.terrain.terrain_levels,self.terrain.terrain_types]
        self.r0_boundary.copy_((pos[:,:2]-center[:,:2]).abs().amax(-1)>4.)
        timeout|=self.r0_boundary&(~term)
        self.r0_local_steps+=1
        return term,timeout

    def terrain_summary(self):
        t=self.terrain;nominal=self.full_dr.nominal_env_mask;flat=self.flat_terrain_mask
        population=torch.bincount(self.terrain_family*4+t.terrain_levels,minlength=28).reshape(7,4)
        return dict(stage='MOD4-R0',families=list(FAMILIES),population_by_family_level=population.tolist(),attempts=self.r0_attempts.tolist(),success=self.r0_success.tolist(),failures=self.r0_failures.tolist(),boundary_counts=self.r0_boundary_counts.tolist(),level_up=self.r0_up,level_down=self.r0_down,local_policy_steps=self.r0_local_steps,max_level=3,groups=dict(nominal_flat=int((nominal&flat).sum()),nominal_rough=int((nominal&~flat).sum()),DR_flat=int((~nominal&flat).sum()),DR_rough=int((~nominal&~flat).sum())),signed_distance_mean=float(self.r0_signed_distance[~flat].mean()) if bool((~flat).any()) else 0.,ground_variation_mean=float((self.r0_ground_max-self.r0_ground_min)[~flat].mean()) if bool((~flat).any()) else 0.)

    def terrain_checkpoint_state(self):
        return dict(terrain_levels=self.terrain.terrain_levels,terrain_types=self.terrain.terrain_types,offsets=self.terrain.r0_offsets,flat_mask=self.flat_terrain_mask,local_policy_steps=self.r0_local_steps,attempts=self.r0_attempts,success=self.r0_success,failures=self.r0_failures,boundary_counts=self.r0_boundary_counts,level_up=self.r0_up,level_down=self.r0_down,signed_distance=self.r0_signed_distance,progress_origin=self.r0_progress_origin,progress_direction=self.r0_direction,progress_initialized=self.r0_progress_initialized,ground_min=self.r0_ground_min,ground_max=self.r0_ground_max)
