"""All original D0-D7 validators retained; explicitly validate new WAVE50 terrain too."""
import supervise_e1_command_retention_episode_reviewed_once as inherited
s=inherited.s
validate_delay_state=inherited.validate_delay_state
PhysicsActionQueue=inherited.PhysicsActionQueue
validate_saved_pressure=inherited.validate_saved_pressure
validate_saved_damping=inherited.validate_saved_damping
validate_saved_chassis_pd=inherited.validate_saved_chassis_pd
def fullsave(path,count=20000,require_action=True,require_spring=True,require_gas=True,require_d7=True,require_e1=True):
    import torch
    ck=torch.load(path,map_location='cpu',weights_only=False);info=s.q.base.checkpoint(path)
    assert info['finite_tensors']>=84 and ck['actor_state_dict']['mlp.0.weight'].shape==(256,35) and ck['critic_state_dict']['mlp.0.weight'].shape==(256,38)
    assert ck['optimizer_state_dict']['state'] and ck['sensor_DR_state']['n']==count and ck['sensor_recipe']['profile']=='noise_bias_mild_v1'
    assert ck['sensor_global_rng_state']['cuda'] and ck['sensor_command_DR_rng_state'] and ck['sensor_physical_DR_rng_state']
    d=type('DelaySchema',(),dict(n=count,enabled=True))();validate_delay_state(d,ck['feedback_delay_state'])
    assert ck['feedback_delay_recipe']['profile']=='control_0_10ms_v1'
    if require_action:
        q=PhysicsActionQueue(count,'cpu',0);saved=ck['physical_action_delay_state']
        # CUDA and CPU generators serialize different formats. Check all queue
        # schemas on CPU without asking a CPU generator to consume CUDA bytes;
        # exact CUDA RNG restoration is proved by the real startup contract.
        for r in saved['rng'].values():assert r.dtype==torch.uint8 and r.ndim==1 and r.numel()>0
        schema=dict(saved,rng={k:g.get_state() for k,g in q.rng.items()});q.validate_state(schema)
        assert ck['physical_action_delay_recipe']['profile']=='physical_target_0_2500_5000us_v1'
    else:assert 'physical_action_delay_state' not in ck
    if require_spring:
        validate_saved_pressure(ck['spring_pressure_state'],count)
        assert ck['spring_pressure_recipe']['profile']=='gas_stiffness_independent_episode_090_110_v1'
    else:assert 'spring_pressure_state' not in ck
    if require_gas:
        validate_saved_damping(ck['gas_damping_state'],count)
        assert ck['gas_damping_recipe']['profile']=='gas_damping_independent_episode_090_110_v1'
    else:assert 'gas_damping_state' not in ck
    if require_d7:
        validate_saved_chassis_pd(ck['chassis_PD_state'],count);assert ck['chassis_PD_recipe']['COM_profile']=='chassis_link_local_independent_xyz_5mm_v1' and ck['chassis_PD_recipe']['PD_profile']=='explicit_motor_PD_independent_095_105_v1'
    else:assert 'chassis_PD_state' not in ck
    if require_e1:
        from g3_terrain_checkpoint import validate
        from e1_terrain_state import validate as old_validate
        from g2_terrain_checkpoint import validate as previous_G2_validate
        from g4_current_state import validate as WAVE50_validate
        validator=WAVE50_validate if ck['E1_terrain_state']['profile']=='mod4_G4_CAD_derived_50mm_v1' else (validate if ck['E1_terrain_state']['profile']=='mod4_G3_CAD_derived_35mm_v1' else (previous_G2_validate if ck['E1_terrain_state']['profile']=='mod4_G2_CAD_derived_20mm_v1' else old_validate))
        validator(ck['E1_terrain_state'],count)
        if 'E1_retained_flat_command_state' in ck:
            from retention_command_state import validate as command_validate
            command_validate(ck['E1_retained_flat_command_state'],count)
            assert ck['E1_terrain_state_legacy_command_ranges_are_noneligible_gentle_only']
    else:assert 'E1_terrain_state' not in ck
    return info
