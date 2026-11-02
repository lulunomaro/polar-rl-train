"""Source candidate: restore CURB113 original inward reset-axis semantics.
Call only AFTER the sole original fresh reset, BEFORE first policy/WM sample.
No extra reset, observation sampling, physics setter, RNG draw, or model access.
Not installed into any active or pending role by this source file alone.
"""
def bind_original_command_after_fresh_reset(env,role,obs,axis_module=None):
    if role!='CURB_INDEPENDENT113':
        return obs,dict(role=role,extra_axis_binding_required=False)
    if getattr(env,'_supermimic_original_axis_bound_v2',False):
        raise RuntimeError('Original independent axis already bound once')
    if not hasattr(env,'_rough_spawn_xy'):
        raise RuntimeError('Original sole fresh reset must establish rough spawn before axis binding')
    import torch
    if not isinstance(obs,dict)or'policy'not in obs or obs['policy'].shape!=(env.num_envs,35):
        raise ValueError('Exact original35 policy observation required')
    # Check source contract rather than inventing an observation scale or corruption.
    cfg=env.cfg.observations.policy.commands
    if cfg.func.__name__!='generated_commands'or cfg.params!={'command_name':'twist'}:
        raise ValueError('Original command observation contract changed')
    for field in ('noise','clip','scale','modifiers'):
        if getattr(cfg,field,None) is not None:
            raise ValueError('Command observation has transform requiring a new explicit adapter: '+field)
    if env.observation_manager.active_terms['policy'][0]!='commands':
        raise ValueError('Original command first-three slot ordering required')
    if 'critic'in obs and env.observation_manager.active_terms['critic'][0]!='commands':
        raise ValueError('Original critic command ordering required')
    if axis_module is None:
        import independent_expert_axis_v1 as axis_module
    before_rng=torch.get_rng_state().clone()
    state=axis_module.bind_after_restore(env,'CURB20')
    if not torch.equal(before_rng,torch.get_rng_state()):
        raise RuntimeError('Original source axis binder unexpectedly drew CPU RNG')
    command=env.command_manager.get_term('twist').command.detach()
    output=dict(obs)
    for group in ('policy','critic'):
        if group not in output:continue
        previous=output[group];current=previous.clone();current[...,:3]=command
        assert torch.equal(current[...,3:],previous[...,3:])
        output[group]=current
    env._supermimic_original_axis_bound_v2=True
    return output,dict(role=role,extra_axis_binding_required=True,original_function='independent_expert_axis_v1.bind_after_restore(env,CURB20)',binding_after_single_fresh_reset_before_first_action=True,command_only_first3_resynced_no_sensor_noise_redraw=True,extra_reset_or_physics_or_model_operations=0,target_envs=int(state['target'].sum()),original_private_RNG_draws_unchanged=state['original_private_RNG_draws_unchanged'],new_reward_or_command_range=False,runtime_validation='PENDING_UNUSED_ROLE_NATIVE_ADMISSION')
