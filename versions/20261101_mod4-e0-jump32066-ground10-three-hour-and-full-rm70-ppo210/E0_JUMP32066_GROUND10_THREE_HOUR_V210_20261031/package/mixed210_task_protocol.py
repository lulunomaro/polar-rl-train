"""Exact new mixed task/finite GO bounds, no SDK or account mutation."""
SHA='2df106412ade7c0993f5a51871a4505624600aac7489c011011d9fd24d3ca610'

def validate_go(go,run_id,task,now):
 assert task['kind']=='E0_JUMP32066_ORIGINAL_E0_GROUND10_LITERAL_JUMP90_400N50_THREE_HOUR_V210'
 assert task['source_SHA']==SHA and task['source_iteration']==32066 and task['source_Adam_step']==642840
 assert task['ground_envs']==2000 and task['jump_envs']==18000
 assert go['run_id']==run_id and go['role_key']=='e0_72' and go['source_model_SHA']==SHA
 assert go['source_iteration']==32066 and go['input_Adam']==642840
 assert go['ground_envs']==2000 and go['jump_envs']==18000 and go['num_envs']==20000
 assert go['actor_obs']==35 and go['critic_obs']==38 and go['action_dim']==6
 assert go['physics_dt']==.0025 and go['TGS']==[32,4] and go['policy_hz']==50 and go['feedback_hz']==100
 assert go['nominal_gas_k_N_m']==2000 and go['preserve_learned_STD']
 assert go['max_parent_seconds']==11100 and go['exit_headroom_seconds']==300
 assert go['save_deadline']==go['learning_started_epoch']+10800 and go['nominal_end_epoch']==go['learning_started_epoch']+11100
 assert go['learning_started_epoch']<=now<go['save_deadline']
 assert go['literal_original_fudan_JUMP'] and go['original_E0_ground_reward'] and go['one_original_writer']
 assert go['full_actor_critic_STD_17Adam_restore_required'] and go['explicit_fresh_physics_replay_history']
 return True
