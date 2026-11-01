"""Saved failed235 closure and necessary NEW source-read purpose;no model IO."""
from pathlib import Path
from e2_solo_contract import SHA,BYTES,MODEL
import json

PURPOSE_PREFIX='ROOT_E2_MIMIC01_V3_'

def prior_failed_closed(closed,order):
 assert closed['passed_collection'] is True and closed['new_PPO_updates']==0 and closed['qualified_formal'] is False and closed['formal_transfer']==0
 assert closed['original_FIRST_false_preserved'] is True and closed['run_id']==order['run_id']
 o=closed['owner_closed'];n=closed['node_result']
 assert o['passed'] and o['canonical_None'] and o['shared_locks_free'] and o['original_owner_out_or_original_nonexecuting_zombie']
 assert o['cohort_final']['original_cost_settled'] and o['owner_exit']['original_cost_settled'] and o['owner_exit']['own_original_two_fcntl_released_if_held']
 assert set(o['original_independent_raw_fees'])=={'e2'} and o['raw_fee_sum_once']==sum(o['original_independent_raw_fees'].values())
 assert n['key']=='e2' and n['qualified_formal'] is False and n['formal'] is None and n['final'] is None
 assert n['node_out_or_nonexecuting_original_zombie'] and n['private_EX_free'] and n['original_node_exit']['all_own_children_waited'] and n['original_node_exit']['private_EX_released'] and n['original_node_exit']['terminal_owner_ack']
 assert n['original_node_terminal']['row']['original_error'] is True
 errors=[json.loads(x['UTF8']) for x in n['full_UTF8'] if Path(x['path']).name=='ORIGINAL_E2_PPO_ERROR.json']
 assert len(errors)==1;error=errors[0];cache=error['source_cache']
 assert error['actual_new_PPO_updates']==0 and "terminations.mimic.params['threshold']==.01" in error['error']
 assert cache['source_SHA']==SHA and cache['source_bytes']==BYTES and cache['selected_source_path']==MODEL
 assert cache['source_physical_byte_opens']==cache['source_decodes']==1
 assert order['kind']=='CURRENT_ACTUAL235_V2_ZERO_PPO_ORIGINAL_MIMIC05_VS_REQUIRED01_FAILURE_CLOSED'
 assert order['actual_new_PPO_updates']==0 and order['original_owner_closed'] and order['original_node_wait0_and_private_EX_free'] and order['all_root_SSH_closed_session_restored']
 assert order['source_read_counts']==cache and order['source_guard_mismatch']['original_source_mimic_radians']==.05 and order['source_guard_mismatch']['required_current_plan_mimic_radians']==.01
 return dict(kind='ROOT_ACTUAL235_FAILED_CLOSED_READ_CONSUMED_SCOPE',run_id=closed['run_id'],closed_epoch=closed['epoch'],
  original_FIRST_false_preserved=True,actual_new_PPO_updates=0,qualified_formal=False,source_cache=cache,
  allownwaited_private_shared_free=True,canonical_None_historical=True,raw_original_fee_SUMONCE=o['raw_fee_sum_once'],
  old_mimic_radians=.05,new_planned_mimic_radians=.01,closure_m=.002,all_other_physics_reward_commands_motors_unchanged=True)

def new_read_admission(scope,purpose_id,new_run):
 assert purpose_id.startswith(PURPOSE_PREFIX) and len(purpose_id)>len(PURPOSE_PREFIX) and new_run!=scope['run_id']
 return dict(kind='NECESSARY_E2_GUARD01_V3_NEW_SOURCE_READ_PURPOSE',purpose_id=purpose_id,run_id=new_run,
  prior_case=scope,prior_selected_source_read_and_decode_consumed=True,
  reason='Fix inherited .05 to required planned .01 before constructor;prior actual235 failed before native24/PPO',
  maximum_NEW_selected_source_bytepass=1,maximum_NEW_selected_source_decode=1,
  installer_selected_model_stat_hash_copy_open_decode=0,CPU_old_model_reads=0,
  V3_actual_native24_under_mimic01_required_before_PPO=True,legacy232_not_mimic01_proof=True)

def validate_repair_task(task,evidence,go):
 a=evidence['guard01_repair_admission'];p=a['prior_case']
 assert a['kind']=='NECESSARY_E2_GUARD01_V3_NEW_SOURCE_READ_PURPOSE' and a['prior_selected_source_read_and_decode_consumed']
 assert a['maximum_NEW_selected_source_bytepass']==a['maximum_NEW_selected_source_decode']==1
 assert a['purpose_id']==task['new_selected_source_read_purpose_id']==go['new_selected_source_read_purpose_id']
 assert a['run_id']==task['run_id']==go['run_id'] and a['run_id']!=p['run_id']
 assert p['source_cache']['source_physical_byte_opens']==p['source_cache']['source_decodes']==1 and p['actual_new_PPO_updates']==0
 assert evidence['fresh_actual']['checked_epoch']>=p['closed_epoch']
 assert task['planned_mimic_threshold_radians']==go['planned_mimic_threshold_radians']==.01
 assert task['original_inherited_mimic_threshold_radians']==go['original_inherited_mimic_threshold_radians']==.05
 assert task['closure_threshold_m']==go['closure_threshold_m']==.002
 assert task['explicit_mimic_guard_tightening'] and go['explicit_mimic_guard_tightening']
 return True

