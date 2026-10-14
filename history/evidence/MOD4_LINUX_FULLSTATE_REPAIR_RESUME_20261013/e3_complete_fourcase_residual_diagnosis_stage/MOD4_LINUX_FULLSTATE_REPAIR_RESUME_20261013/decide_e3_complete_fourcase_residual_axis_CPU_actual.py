"""Complete actual scope decision. No blind third window or threshold change."""
from pathlib import Path
import json,hashlib,time
D=Path(__file__).resolve().parent;W=D.parent
def H(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 return h.hexdigest()
def main():
 out=D/'reports/E3_COMPLETE_FOURCASE_AND_RESIDUAL_SINGLE_AXIS_SCOPE_DECISION_ACTUAL.json';assert not out.exists()
 S=W/'MOD4_LINUX_LEFT_SECOND_SAMEIDENTITY_CPU_PREPARE_20261014';N=W/'MOD4_3060_LEFT_SECOND_FULL80_20261014';T=W/'MOD4_3060_LEFT_SECOND_RETENTION_20261014';Y=W/'MOD4_E3_WAVE_RESIDUAL_CPU_20261014';P=W/'MOD4_E3_POSITIVE_SPIN_RESIDUAL_CPU_20261014'
 files=dict(final=S/'reports/LEFT_SECOND_OWN_FORMAL_FINAL_CLOSEOUT_CPU_VERIFIED.json',local_CPU=S/'reports/LEFT_SECOND_OWN_POSITIVE_WEIGHT_LOCAL_CPU_VERIFIED_1791963221095120000.json',trace=D/'reports/LEFT_SECOND_FORMAL_FINAL_FULLTRACE_CPU_ACTUAL_1791963246377865600.json',wave=N/'reports/FULL80_ORIGINAL_1N_ROUTE_ALL_PREFIX_COMPLETE_ACTUAL_REVIEW.json',direct_wave=N/'reports/LEFT_REPAIR_DIRECT_ORIGINAL_FULL80_PREFIX_ACTUAL_REVIEW.json',retention=T/'reports/SECOND_E3_THREE_RETENTION_PAIRS_COMPLETE_ACTUAL_CPU_REVIEW.json',slot=T/'reports/SECOND_RETENTION_COMPLETE_ACTUAL_ROOT_TRANSPORT_HANDOFF.json',commands=S/'reports/LEFT_SECOND_COMPLETE_SAVED_COMMAND_EXPOSURE_CPU_ACTUAL.json',wave_residual=Y/'reports/E3_VS2B_REMAINING_FOUR_FULL_VALIDPREFIX_CPU_ACTUAL.json',gyro_math=Y/'reports/E3_ACTUAL_SAVED_VECTOR_GYRO_Z_SENSITIVITY_CPU_ACTUAL.json',frame_math=Y/'reports/E3_YAWPI_FRAME_FACTOR_MATH_ONLY_CPU_PASSED.json',spin_bound=P/'reports/E3_POSITIVE_SPIN_COMMON_VALID_PREFIX_AND_FULL_TRAINING_EXPOSURE_BOUND_CPU_ACTUAL.json',spin_command_math=P/'reports/FIXED_2B_E3_ACTOR35_COMMAND_YAW_SINGLE_AXIS_ACTUAL_CPU_REVIEW.json')
 values={k:json.loads(p.read_bytes()) for k,p in files.items()}
 f=values['final'];cpu=values['local_CPU'];wave=values['wave'];ret=values['retention'];cmd=values['commands']
 assert f['passed'] and f['own_final']['sha256']=='e3e825b1e24f11885f2f9d5b196d85cbce4a46363cd09b440e7efa2b846fd47c' and f['saved_updates']==191 and f['canonical_idle'] and f['two_actual_fcntl_free']
 assert cpu['passed'] and cpu['saved_state']['actual_fullsave']['floating_finite']==107 and cpu['saved_state']['actual_fullsave']['perenv']==99
 assert values['trace']['code']==0 and json.loads(values['trace']['stdout'])['passed']
 assert wave['passed'] and (wave['forward_complete'],wave['reverse_complete'],wave['ordinary'])==(24,26,1)
 assert ret['passed'] and ret['all_three_inherited_full1500_complete'] and not ret['pending']
 assert values['slot']['root_reclaimed_sole_sequential210_249_transport'] and values['slot']['current_actual_shared_slot_guard']['shared_OS_lock_free']
 assert cmd['passed_CPU_saved_command_counts'] and cmd['total_envsteps']==91680000
 assert sum(v['pure_yaw_positive']+v['pure_yaw_negative'] for v in cmd['histogram'].values())==0
 assert max(v['yaw_abs_max'] for v in cmd['histogram'].values())<=2.
 for kind,rows in ret['pairs'].items():assert rows['original_false_and_all_failed_prefix_kept']
 result=dict(epoch=time.time(),scope_id='e3_two_left_windows_complete_fourcase_audited_residual_direction_frame_and_command_domain',current_observed_terrain_priority_source=f['own_final'],whole195_107_99_20k_source_verified=True,actual_two_learning_windows_3600_each_complete=True,no_third_blind_sameaxis_duration=True,all_four_original_frozen_cases_complete_and_independently_admitted=True,terrain=dict(old_forward=22,new_forward=24,old_reverse=25,new_reverse=26,ordinary_before=0,ordinary_after=1,forward_improved=[21,72],reverse_improved=[70],no_transit_regressions=True,remaining_forward=[6,15,69],remaining_reverse=[67]),retention=ret['pairs'],native_shapeLocal_and_public_source_to_installed_DLL_bitexact_not_claimed=True,first_and_second_root_command_proxy_not_contact_or_causal_certificate=True,observed_current_training_domain=dict(actual_9168M_saved_steps=91680000,no_pure_yaw_commands=True,maximum_actual_command_yaw_rad_s=cmd['histogram']['0']['yaw_abs_max'],pure4pi_test_outside_this_saved_window_seen_domain=True,not_complete_ancestor_training_history_claim=True),diagnosis_bounds=[
 'Remaining forward6/15/69 sustained yaw and lateral drift, with doublewheel1N support mostly retained and hundreds of mm terminal deficit; lowering contact or200mm margin would not establish a physical remedy.',
 'Reverse67 has a basecontact ordinary termination atcontrol1161; preserve1161 valid controls and distinguish it from continuous yaw-only failures.',
 'Both successful and failed terrain samples show near100percent left CAD lower-limit projection; it cannot alone classify failures.',
 'Actual gyro-z one-coordinate CPU derivatives have similar signs and magnitudes in successes and failures. No CPU evidence of a residual-exclusive dead zone or general sign error; do not alter observations.',
 'Positive pure-spin env51 is continuous15s stall/low support;73/84 have bad_orientation resets. Wholefinal means and common valid prefixes must remain separate.',
 'No pure commands appear in the second91.68M saved training steps; maxyaw~2rad/s. Saved35-input yaw±1/2/4pi counterfactual shows extrapolated wheel clipping, not a physical or unique causal proof. Productioncommand/DR limits remain fixed.',
 ],next_authorized_work=dict(frozen_same_e3_yawpi_BODY_sign_flip_WORLD_direction_preserved_factor='actual math-only CPU passed; independent backend/sourcefreeze/fullfootprint-safeZ/query/contactCOMhardware new scope GPU native and fullbehavior still required',source_unchanged_weights=True,no_liveheading_position_correction_teacher_or_truthgate=True,no_removed_DR_or_changed_reward_hardware_clock_geometry=True,factor_root_pose_quaternion_is_explicit_change_not_root30_byteexact=True,no_GPU_factor_pass_yet=True,no_new_PPO_admission_or_training_started=True),evidence={k:dict(path=str(p.resolve()),bytes=p.stat().st_size,sha256=H(p)) for k,p in files.items()},qualified50=False,qualified70=False,all_skills_accepted=False,global_optimum_claimed=False,no_mechanical_27of27_or_percent_gate=True,no_SSH_GPU_RNG_signal_or_budget_transaction=True)
 out.write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(dict(decision=str(out),fourcase_complete=True,next_independent_frame_factor_not_GPU_yet=True,no_third_blind_PPO=True,qualified50=False)))
if __name__=='__main__':main()
