"""Unified SCUT Rough-v0 course on current MOD4 full DR and fixed interface."""
import torch
from .scut_rough_r1_env import ScutRoughR1Env
from .scut_flat_mixed_dr_env import ScutFlatMixedRemainingDREnv
from .scut_flat_v2_env import ScutFlatV2Env
from rough_scut_v0_terrain import FAMILIES

HEIGHTS=((.22,.42),(.22,.42),(.22,.42),(.22,.42),(.24,.38),(.24,.38),(.20,.42),(.22,.42),(.20,.42))

class ScutUnifiedRoughV0Env(ScutRoughR1Env):
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
        bounds=self.command.new_tensor(HEIGHTS)[self.terrain_family[ids]]
        self.height[ids]=bounds[:,0]+torch.rand(len(ids),device=self.device)*(bounds[:,1]-bounds[:,0])

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
            self.r1_direction[ids]=0.;self.r1_signed_distance[ids]=0.
            self.r1_progress_origin[ids]=self.view.data.root_pos_w[ids,:2]
            self.r1_progress_initialized[ids]=False
            self.r1_ground_min[ids]=self.scene.env_origins[ids,2]
            self.r1_ground_max[ids]=self.scene.env_origins[ids,2]
            self.r1_boundary[ids]=False

    def terrain_summary(self):
        t=self.terrain;nominal=self.full_dr.nominal_env_mask;flat=self.flat_terrain_mask
        population=torch.bincount(self.terrain_family*10+t.terrain_levels,minlength=len(FAMILIES)*10).reshape(len(FAMILIES),10)
        return dict(stage='SCUT-Rough-v0-unified',families=list(FAMILIES),population_by_family_level=population.tolist(),attempts=self.r1_attempts.tolist(),success=self.r1_success.tolist(),failures=self.r1_failures.tolist(),boundary_counts=self.r1_boundary_counts.tolist(),level_up=0,level_down=0,local_policy_steps=self.r1_local_steps,max_level=9,level_sampling='all10 fixed rows from launch; no staged admission',groups=dict(nominal_flat=int((nominal&flat).sum()),nominal_rough=int((nominal&~flat).sum()),DR_flat=int((~nominal&flat).sum()),DR_rough=int((~nominal&~flat).sum())),signed_distance_mean=float(self.r1_signed_distance[~flat].mean()),ground_variation_mean=float((self.r1_ground_max-self.r1_ground_min)[~flat].mean()),progress_scope='2m signed traversal with terrain-height variation; not gyro pass metric')

    def terrain_checkpoint_state(self):
        state=super().terrain_checkpoint_state()
        state.update(course='SCUT-Rough-v0-unified',num_levels=10)
        return state

    def restore_terrain_curriculum(self,state):
        if int(state['attempts'].shape[-1])==10:
            return super().restore_terrain_curriculum(state)
        # The old four-row indices have different geometry. Keep the new unified
        # sampling and save the old counters as provenance, without re-labelling.
        self.parent_r1_terrain_state=state
        self.snapshots=None
        self.reset()
        return dict(parent_four_row_state_retained_as_provenance=True,new_unified_ten_row_population=True,old_levels_relabelled=False,full_ppo_restoration_separate=True)
