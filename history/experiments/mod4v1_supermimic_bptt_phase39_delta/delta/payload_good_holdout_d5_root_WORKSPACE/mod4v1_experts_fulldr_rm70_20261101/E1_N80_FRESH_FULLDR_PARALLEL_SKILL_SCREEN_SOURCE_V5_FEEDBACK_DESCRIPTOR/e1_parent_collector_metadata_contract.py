"""Optionalpuremetadata validation helper; parentownsactualall9collector.
No model/raw access, no claimskillgraduation fromexecutionPASS.
"""
def validate_e1_closed_metadata(role,final,pre_close,actual_parent_wait,contracts,worker_error=None):
    if worker_error is not None:return dict(role=role,status='FAILED_ORIGINAL_WORKER_ERROR',error=worker_error,skill_graduated=False)
    if final is None or pre_close is None:return dict(role=role,status='INCOMPLETE_METADATA_NOT_PASS',skill_graduated=False)
    c=contracts[role];n=c['controls'];assert final['role']==role and final['passed_execution'] is True
    assert (final['controls'],final['physics'],final['feedback'],final['actor_calls'])==(n,n*8,n*2,n)
    assert final['saved20k_DR_physically_applied'] is False and final['state_projection_or_slicing'] is False and final['whole20k_savedrestore_claim'] is False
    assert final['optimizer_updates']==0 and final['env_close_returned'] is True
    source=final['source_cache'];assert source['source_SHA']==c['source']['SHA'] and source['source_bytes']==c['source']['bytes']
    assert (source['physical_byte_opens'],source['SHA_calls'],source['decodes'])==(1,1,1)
    assert source['entire_original_root_and_nested_identity_preserved'] and source['live_actor_STD_loaded']
    for name in ('fresh_fullDR_before','fresh_fullDR_after'):
        audit=final[name];assert audit['fresh_N80_D0_D7_enabled'] and audit['actual_parameters']['actual_parameters_pass']
        assert audit['one_explicit_fresh_reset']==1 and audit['saved20k_history_physically_applied'] is False
    assert actual_parent_wait['actual_waited'] is True and actual_parent_wait['returncode']==0
    return dict(role=role,status='CLOSED_EXECUTION_AND_SCOPE_METADATA_PASS',metrics=final['metrics'],scope=c['scope'],group_id=final['group_id'],actual_parent_wait=actual_parent_wait,no_new_aggregate_graduation_rate=True,skill_graduated='PARENT_ORIGINAL_SCOPE_REVIEW_REQUIRED_NOT_INFERRED')
