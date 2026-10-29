"""Next E3-only metric contract; not an installer/runtime or a graduation gate."""
SOURCE_KIND='E3_97_thirteen_recipe_recovery_frozen_diagnostic_PENDING'
def phase_label(recipe,age_before,request_before):
 assert isinstance(recipe,int) and 0<=recipe<=12 and isinstance(age_before,int) and age_before>=0
 assert request_before==((recipe!=12) and age_before<300)
 if recipe==12:return 'original_recipe12_normal_zero_command_baseline'
 return 'original_fall_request_first3s' if request_before else 'original_post_request_soft_termination_unmasked'
def original_new_credit(credited_before,credited_terminal,episode_before,episode_terminal):
 assert episode_before==episode_terminal,'Only original terminal-before-autoreset endpoints can be paired'
 return bool(credited_terminal and not credited_before)
PENDING_EXECUTION=dict(num_envs=20000,requested_controls=600,warmup_controls=100,per_recipe_unique_env_and_population_controls=True,
 per_recipe_distinct_attempt_UID_and_request_exposure_required=True,source_phase_counter_public_hz=100,control_dt_s=.02,
 source_request_age_lt300_is3seconds=True,source_stable_counter_ge50_is_point5seconds=True,
 source_upright_gravity_z_lt=-.984807753,source_root_speed_lt=.03,source_angular_speed_lt=.2,
 preserve_original12_fall_recipes_and_recipe12_baseline=True,do_not_enable_extra_contact_queries=True,
 W35_or_E2_mode_labels_forbidden=True,skill_graduation=False,complete_WM_dataset=False,
 missing='E3-specific readonly runtime hook, final97 input replacement, target metadata/SDK binding, supervisor/secure entry and actual CUDA/native24 admission')
