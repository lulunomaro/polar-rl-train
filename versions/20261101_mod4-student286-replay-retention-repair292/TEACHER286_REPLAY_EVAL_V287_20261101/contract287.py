def validate_task(t):
    assert t['kind']=='FROZEN286_FINAL_DEPTH_HELDOUT270_AND_GROUND_EVAL287'
    assert t['model_SHA']=='4ace1eec00c763c2e19a858e4a119953ec6b58debcd58fc362c7e281d5d9452d' and t['model_bytes']==32407215
    assert t['num_envs']==80 and t['seed']==9137 and t['max_controls']==400
    assert t['physics_dt']==.0025 and t['policy_hz']==50 and t['feedback_hz']==100 and t['TGS']==[32,4]
    assert t['closure_m']==.01 and t['mimic_rad']==.01
    assert t['optimizer_steps']==t['account_writes']==0 and t['model_byte_reads']==t['model_decodes']==1
    return True

def validate_current_authority(c,binding,owner_identity=None,owner_current=None):
    assert c['active_segment']is None and c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026'
    assert c['authorized_training_seconds']==2268000 and c['new_authority_budget_extensions']==[]
    return True
