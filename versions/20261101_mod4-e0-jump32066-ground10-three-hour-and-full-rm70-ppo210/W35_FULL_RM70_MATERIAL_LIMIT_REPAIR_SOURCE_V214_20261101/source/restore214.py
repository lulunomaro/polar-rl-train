"""Model-free same20k own-state physical setter coverage before one new reset."""
import copy
from material214 import phase,own_mild_state,restore_own_mild_state,log
from usd214 import material_census


def own_restore_and_new_episode(env,t):
    import warp as wp
    from mild_dr214 import tensor
    if env.num_envs!=20000:raise ValueError('This64K capacity purpose needs the original20k scale')
    phase('BEFORE_OWN_20K_STATE_SNAPSHOT',terrain=material_census(env.sim.stage))
    mild=own_mild_state(t,env._mild_dr)
    adapters={
        'D1_D2_sensor':env._sensor_mild,
        'D3_feedback':env._feedback_delay_mild,
        'D4_action_queue':env._physics_action_delay,
        'D5_spring':env._spring_pressure,
        'D6_damping':env._gas_damping,
        'D7_COM':env._chassis_com,
        'D7_PD':env._explicit_pd}
    saved={name:copy.deepcopy(adapter.state_dict())for name,adapter in adapters.items()}
    command=env.command_manager.get_term('twist')
    command_saved=copy.deepcopy(command.state_dict_retention())
    named={name:value.get_state().clone()for name,value in vars(command).items()if isinstance(value,t.Generator)}
    cpu=t.random.get_rng_state().clone();cuda=[s.clone()for s in t.cuda.get_rng_state_all()]
    phase('BEFORE_OWN_SAME_VALUE_MILD_MATERIAL_REAPPLY',terrain=material_census(env.sim.stage))
    restore_own_mild_state(t,wp,env._mild_dr,mild,tensor)
    phase('AFTER_OWN_SAME_VALUE_MILD_MATERIAL_REAPPLY',terrain=material_census(env.sim.stage))
    # These original load methods perform the same existing physical parameter
    # setters as their corresponding real checkpoint resume. No actor/PT exists.
    for name,adapter in adapters.items():
        phase('BEFORE_OWN_'+name+'_LOAD')
        adapter.load_state_dict(saved[name])
        phase('AFTER_OWN_'+name+'_LOAD')
    command.load_state_retention(command_saved)
    for name,state in named.items():getattr(command,name).set_state(state.cpu())
    t.random.set_rng_state(cpu.cpu());t.cuda.set_rng_state_all([s.cpu()for s in cuda])
    # Original fresh-scene queue rebase,not a policy or new health rule.
    assert int(env._sim_step_counter)==0
    for group in env._physics_action_delay.queue.groups.values():group['last_apply_tick'].fill_(-1)
    episode=env._e1_episode.clone()
    phase('BEFORE_ORIGINAL_NEW_EPISODE_RESET',terrain=material_census(env.sim.stage))
    obs,info=env.reset()
    assert t.equal(env._e1_episode,episode+1)
    actual=env._mild_dr.audit()
    assert actual['actual_parameters_pass'] is True
    phase('AFTER_ORIGINAL_NEW_EPISODE_RESET',terrain=material_census(env.sim.stage),
        original_parameter_audit_passed=True,actual_cached_mu_min=float(env._mild_dr.mu.min()),
        actual_cached_mu_max=float(env._mild_dr.mu.max()))
    return obs,info,dict(num_envs=20000,source_PT_opens=0,own_same_population_only=True,
        original_DR_component_load_methods=list(adapters),
        original_named_and_global_RNG_restored_before_new_episode=True,
        extra_same_value_mild_material_reapply_explicitly_probe_only=True,
        original_physical_parameter_audit_passed=True,
        original_episode_incremented_once=True,
        material_allocation_success_requires_parent_log_check=True,
        original_source_fullPPO_resume_or_native24_not_claimed=True)
