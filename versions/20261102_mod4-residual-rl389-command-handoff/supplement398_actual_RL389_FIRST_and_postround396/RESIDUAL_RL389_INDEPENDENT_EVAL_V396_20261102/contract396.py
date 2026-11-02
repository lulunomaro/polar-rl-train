def validate_task(t):
    assert t['kind']=='FROZEN389_RESIDUAL_RL_EVAL396' and t['num_envs']==80
    assert len(t['model_SHA'])==64 and t['model_bytes']>0 and t['expected_Pi_updates']>0
    assert t['seed']==9137 and t['max_controls']==400 and t['closure_m']==.01 and t['mimic_rad']==.01
    assert t['optimizer_steps']==t['account_writes']==0 and t['model_byte_reads']==t['model_decodes']==1
    return True
def validate_current_authority(c,binding,owner_identity=None,owner_current=None):
    assert c['active_segment'] is None and c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026'
    assert c['authorized_training_seconds']==2268000 and c['new_authority_budget_extensions']==[]
    return True
