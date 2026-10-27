"""Decoded new formal FINAL review hook; no model/file loading occurs here."""
from native88_gas400_migration_v1 import verify_saved_migration,verify_window,exact_plain,require,NATIVE_CONTRACT
def review_new_native88_decoded(full,formal,*,expected_role,parameter_contract_SHA,asset_report_SHA):
 publication=full['UniSuperMimic_publication'];w=publication['native88_migration_window']
 verify_saved_migration(full,publication);verify_window(w,require_new_pi=True)
 require(w['role']==expected_role and w['parameter_source_contract_SHA']==parameter_contract_SHA and w['actual_asset_composition_report_SHA']==asset_report_SHA,'new role/actual parameter source binding')
 require(full['UniSuperMimic_H1_test']['iteration']==w['counters']['native_iteration'],'saved native iteration/window mismatch')
 require(formal['passed'] is True and formal['trace_persisted'] is True and formal['primary_error'] is None and not formal['secondary_errors'],'original lifecycle must have formal success, not rc0')
 c=w['counters'];final=formal['final']
 require(formal['counters']=={k:final[k] for k in ('updates','world_updates','policy_updates')} and final['updates']==c['native_iteration'] and final['world_updates']==c['world_updates'] and final['policy_updates']==c['policy_updates'],'formal/global/window counters differ')
 require(exact_plain(final['native88_migration_window'],w) and final['verified_new_publication'] and final['original_full_save_chain_returned'],'formal atomic publication/window binding')
 return dict(passed=True,source=w['source'],new_world_updates=c['new_world_updates'],new_policy_updates=c['new_policy_updates'],completed_fresh_controls=c['completed_fresh_controls'],
  changed_plant_not_same_physics=True,full_native_architecture_finite_threeopts_and_frozen_RSL_still_require_original_fullCPU=True,not_a_whole_model_or_hardware_admission=True)
