"""Training-only limited-domain sampling; deployment still consumes just 35.

All five physical terrain families remain unchanged. Only complete 24-control
and bootstrap sequences in the approved flat/W35 domains enter gate/critic
updates. Background health is still enforced for every physical environment.
The label selects training samples, never experts/actions or inference inputs.
"""
import torch
from rsl_rl.storage import RolloutStorage
from s4_rsl5_frozen_pair_learner_v1 import S4RecordedChoicePPO

DOMAIN='s4_training_supported_domain'
PROFILE='S4_E0_flat_W35_low_straight_supported24_and_bootstrap_v1'

def domain_label(value,n):
    assert value.shape==(n,1) and torch.isfinite(value).all()
    assert ((value==0)|(value==1)).all(), 'Training domain label must be explicit binary metadata'
    return value[:,0].bool()

class SupportedSequenceStorage(RolloutStorage):
    def __init__(self,*a,**kw):
        super().__init__(*a,**kw);self.bootstrap_supported=None;self.last_selection=None

    def mini_batch_generator(self,num_mini_batches,num_epochs=8):
        assert self.step==self.num_transitions_per_env and self.bootstrap_supported is not None
        n=self.num_envs;t=self.num_transitions_per_env
        labels=self.observations[DOMAIN]
        assert labels.shape==(t,n,1) and ((labels==0)|(labels==1)).all()
        keep=labels[:,:,0].bool().all(0)&self.bootstrap_supported
        select=keep[None,:].expand(t,n).flatten().nonzero()[:,0]
        count=len(select);size=count//num_mini_batches
        assert size>1, 'Insufficient complete supported sequences; no fallback to background'
        order=torch.randperm(size*num_mini_batches,device=self.device)
        obs=self.observations.flatten(0,1)[select]
        actions=self.actions.flatten(0,1)[select]
        values=self.values.flatten(0,1)[select];returns=self.returns.flatten(0,1)[select]
        assert all(torch.isfinite(x).all() for x in (self.actions,self.values,self.returns,self.actions_log_prob,*self.distribution_params))
        # Recompute the original global advantage normalization on ONLY the
        # selected sample set. Unselected returns cannot affect its mean/std.
        advantages=returns-values
        advantages=(advantages-advantages.mean())/(advantages.std()+1e-8)
        old_logp=self.actions_log_prob.flatten(0,1)[select]
        params=tuple(p.flatten(0,1)[select] for p in self.distribution_params)
        self.last_selection=dict(profile=PROFILE,physical_envs=n,physical_controls=t,
            complete_supported_envs=int(keep.sum()),eligible_samples=count,
            actual_samples_per_epoch=size*num_mini_batches,excluded_envs=int((~keep).sum()),
            selected_whole_rollout_and_bootstrap=True,domain_is_actor_input=False)
        for epoch in range(num_epochs):
            for i in range(num_mini_batches):
                ix=order[i*size:(i+1)*size]
                yield RolloutStorage.Batch(observations=obs[ix],actions=actions[ix],values=values[ix],
                    advantages=advantages[ix],returns=returns[ix],old_actions_log_prob=old_logp[ix],
                    old_distribution_params=tuple(p[ix] for p in params))

    def clear(self):
        super().clear();self.bootstrap_supported=None

class SupportedDomainPPO(S4RecordedChoicePPO):
    def __init__(self,*a,**kw):
        super().__init__(*a,**kw)
        assert self.normalize_advantage_per_mini_batch is False
        st=self.storage;assert DOMAIN in st.observations.keys()
        self.storage=SupportedSequenceStorage('rl',st.num_envs,st.num_transitions_per_env,
            st.observations[0].clone(),st.actions_shape,st.device)

    def act(self,obs):
        domain_label(obs[DOMAIN],obs.batch_size[0])
        return super().act(obs)

    def compute_returns(self,last_obs):
        self.storage.bootstrap_supported=domain_label(last_obs[DOMAIN],self.storage.num_envs).clone()
        # Original temporal return/timeout equations; only the generator's
        # selected sample normalization differs from all-background training.
        return super().compute_returns(last_obs)

    def save(self):
        ck=super().save()
        ck['S4_supported_training_exposure']=dict(profile=PROFILE,
            only_complete24_and_supported_bootstrap=True,other_families_physical_health_not_ignored=True,
            training_metadata_not_deployment_input=True,expert_choice_not_overridden_by_domain=True,
            original_commands_geometry_DR_reward_clock_unchanged=True,
            last_selection=self.storage.last_selection)
        return ck

    def load(self,ck,load_cfg=None,strict=True):
        state=ck['S4_supported_training_exposure']
        assert state['profile']==PROFILE and state['only_complete24_and_supported_bootstrap'] is True
        result=super().load(ck,load_cfg,strict)
        self.storage.last_selection=state['last_selection']
        return result

    def import_untrained_native_integration(self,ck):
        assert 'S4_supported_training_exposure' not in ck
        assert ck['S4_native_integration_checkpoint_not_production_learning_source'] is True
        assert ck['S4_GPU_learning_admitted'] is False and not ck['optimizer_state_dict']['state']
        return S4RecordedChoicePPO.load(self,ck,None,True)

def actual_supported_domain(env):
    """Privileged TRAINING label, independent of gate scores or chosen expert."""
    term=env.command_manager.get_term('twist');command=term.command
    assert command.shape==(env.num_envs,3) and torch.isfinite(command).all()
    # Current geometric flat eligibility already checks real authored root and
    # wheel rays, cell clearance and full link extent. It is not a name-only label.
    flat=term.eligible_flat.clone()
    wave=(term.family==4)&(command[:,0].abs()<=.300001)&(command[:,1:3].abs().amax(-1)<=1e-6)
    assert env.scene.terrain.retention_assignment_sha=='21b1f52b348ecaf6d33993bfc5b540cf15ed4baf4b1a3d484790f062c6cf2bac'
    assert getattr(env,'_s4_original35_supported_identity_verified',False) is True
    assert getattr(term,'_retention_resampling',False) is False
    return (flat|wave).float()[:,None]

def bind_original35_supported_identity(env):
    """One startup identity check, never repeated mesh/NPZ hashing each tick."""
    from g3_terrain_checkpoint import current_state
    identity=current_state(env)
    assert identity['profile']=='mod4_G3_CAD_derived_35mm_v1'
    assert identity['geometry_triangles_sha256']=='05a70e57eae5cd7a502324ad7c256ff2722b7043869b72524c6eb4516af6b419'
    assert env.scene.terrain.retention_assignment_sha=='21b1f52b348ecaf6d33993bfc5b540cf15ed4baf4b1a3d484790f062c6cf2bac'
    env._s4_original35_supported_identity_verified=True
    return identity
