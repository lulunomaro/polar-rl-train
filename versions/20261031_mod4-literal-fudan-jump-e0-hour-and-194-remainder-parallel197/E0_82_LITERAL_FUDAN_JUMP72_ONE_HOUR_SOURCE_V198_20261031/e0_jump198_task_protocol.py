"""E0 role typing only. No owner, budget writer, source reward or physical edit."""
SOURCE_SHA='a92c9e8d7cb3dbda9828b6c37bb38dd63183818e91b1aa3f7746c2c46379c74a'
ROLE='e0_72'
def validate_go(go,run_id,task,now):
    assert go['role_key']==ROLE and go['run_id']==run_id
    assert go['source_model_SHA']==task['source_SHA']==SOURCE_SHA
    assert go['literal_original_fudan_JUMP'] is True
    assert go['max_parent_seconds']==3900 and go['exit_headroom_seconds']==300
    assert go['save_deadline']==go['learning_started_epoch']+3600 and go['nominal_end_epoch']==go['learning_started_epoch']+3900
    assert go['save_deadline']>now
    assert task['source_iteration']==31984 and task['source_Adam_step']==641200
    assert task['actor_obs']==35 and task['critic_obs']==38 and task['action_dim']==6
    assert task['policy_hz']==50 and task['physics_dt']==.0025 and task['decimation']==8 and task['TGS']==[32,4]
    assert task['gas_nominal_k']==2000 and task['reward_weights_and_functions_no_edits'] is True
    return True
