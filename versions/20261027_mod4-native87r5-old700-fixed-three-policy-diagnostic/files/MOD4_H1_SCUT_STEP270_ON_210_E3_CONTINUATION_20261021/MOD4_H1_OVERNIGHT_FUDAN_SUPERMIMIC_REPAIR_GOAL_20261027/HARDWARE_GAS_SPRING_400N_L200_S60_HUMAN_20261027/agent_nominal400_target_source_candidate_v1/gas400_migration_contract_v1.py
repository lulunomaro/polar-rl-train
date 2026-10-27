"""Typed changed-plant transfer admission. Metadata only, no model or controller."""
def require(v,msg):
 if not v:raise ValueError(msg)
def declare_transfer(source,*,adaptation_controls,adaptation_world_updates):
 require(source['qualified_formal_R5_native'] is True and source['initial_whole_CPU_passed'] is True,'qualified each-own R5 source required')
 require(source['role'] in ('h1','recovery') and source['source_kind']=='R5_native127_obs86_static31_aux54','wrong source role/architecture')
 require(type(adaptation_controls) is int and adaptation_controls>0 and type(adaptation_world_updates) is int and adaptation_world_updates>0,'new plant adaptation counts must be explicitly declared, no oldglobal shortcut')
 for name in ('native_iteration','world_updates','policy_updates'):require(type(source[name]) is int and source[name]>0,'saved real positive source counters')
 return dict(kind='MOD4_GAS400_CHANGED_PLANT_NATIVE_ARCHITECTURE_TRANSFER_SOURCE_ONLY_V1',source=dict(source),
  nominal_force_N=400.,stiffness_N_m=2000.,damping_Ns_m=3.,damping_hardware_calibrated=False,force_curve_hardware_calibrated=False,
  q_upper_m=.020639440248416612,source_q_lower_preserved=True,reference_SHA='9223a53e7bf85a0dc3505cc46c0eb33d04fc35a9bf85e7ffe0e4fbd03e1e46c3',
  restore_native_WM_Pi_Critic_saved_normalizers_three_optimizers_global_counters=True,
  fresh_physical_episode_replay_history_required=True,old700N_environment_or_DR_restore=False,same_plant_exact_resume=False,
  original_clock_solver_geometry_reward_command_success_retained=True,
  explicit_world_model_adaptation=dict(required=True,controls_before_newPi=adaptation_controls,world_updates_before_newPi=adaptation_world_updates),
  old_positivePi_not_new_window_proof=True,global_counters_not_zeroed_to_fake_fresh=True,actual_SDK_resources_whole_source_CPU_PENDING=True,
  source_D0_D7_fullsave_chain_must_be_kept=True,new_output_must_save_new_gas_recipe_and_migration=True)
def validate_new_publication(transfer,publication,adaptation):
 """Future root calls only with actual new preupdate publication/evidence."""
 source=transfer['source'];required=transfer['explicit_world_model_adaptation']
 require(adaptation['actual_new_plant_backend_readback'] is True and adaptation['original_preload_target_active_before_first_newPi'] is True,'new actual plant/preload required')
 require(adaptation['complete_fresh_controls']>=required['controls_before_newPi'] and adaptation['new_world_updates']>=required['world_updates_before_newPi'],'new-plant WM adaptation incomplete')
 require(adaptation['zero_new_policy_updates_during_world_only_adaptation'] is True,'sourcepositive policy count is not adaptation policy activity')
 require(publication['world_updates']>=source['world_updates']+required['world_updates_before_newPi'] and publication['policy_updates']>source['policy_updates'] and publication['native_iteration']>=source['native_iteration'],'real new WM/Pi deltas required')
 require(publication['same_new_preupdate_SHA_and_bytes_and_before_control'] is True and publication['source_SHA']==source['SHA'],'new Pi must be same actual published new preupdate source/window')
 return dict(passed=True,new_policy_delta=publication['policy_updates']-source['policy_updates'],new_world_delta=publication['world_updates']-source['world_updates'],not_same_physics=True)
