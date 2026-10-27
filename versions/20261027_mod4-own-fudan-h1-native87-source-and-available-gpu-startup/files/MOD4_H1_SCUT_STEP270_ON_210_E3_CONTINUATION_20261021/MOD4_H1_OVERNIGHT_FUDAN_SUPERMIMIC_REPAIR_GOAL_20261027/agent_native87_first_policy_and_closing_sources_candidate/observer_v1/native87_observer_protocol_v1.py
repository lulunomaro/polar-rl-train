"""Pure native87 first-positive metadata contract, never reads a checkpoint."""
SOURCE_SHA='0c1edb9603c1cb84fbb894d242dae1b6a7c87fe3237d658dbc486ccbbad3d394'
KIND='MOD4_H1_NATIVE87_POLICY_ONLY_SOURCE_SDK_CPU_PRECONTROL_V2'
def require(v,message):
 if not v:raise ValueError(message)
def validate_first_positive(first,index,pre,go,spec):
 require(go['source_SHA']==go['bootstrap_SHA']==spec['source_SHA']==SOURCE_SHA and go['bootstrap_Adam']==832460,'qualified normal source')
 require(go['source_qualification_kind']==KIND and go['native_continuation_restore_required'] is False,'fresh native scope')
 require(go['manifest_SHA']==spec['manifest_SHA'] and go['seed']==spec['seed'] and go['num_envs']==4096,'role/config binding')
 require(first['policy_updates']>0 and first['world_updates']>0 and first['updates']>0,'new native Pi>0 required')
 require(first['original_source_actor_frozen_not_PPO_learning'] is True and first['not_PPO_or_production_source'] is True,'native distinct from frozen PPO')
 require(first['native_actual_method']=='own_MOD4_converted_Fudan_jump_native_v3','method provenance')
 matches=[r for r in index['preupdate_full_sources'] if all(r.get(k)==first.get(k) for k in ('path','SHA','bytes','before_control'))]
 require(len(matches)==1 and first['before_control']>0 and index['controls']>=first['before_control'],'same actual preupdate source/control receipt')
 require(matches[0]['no_optimizer_call'] is True,'preupdate trace source')
 require(pre['actual_GPU_runtime_readback_passed'] is True and pre['before_first_native_physical_control_and_Pi'] is True,'actual GPU precontrol evidence')
 require(pre['actual_environment_count']==4096 and pre['actual_static_context_dim']==31 and pre['actual_dynamic_aux_dim']==54 and pre['packed_state_dim']==127 and pre['actor_obs_dim']==86 and pre['goal_frame_dim']==146,'actual new dimensions')
 require(pre['source_SHA']==SOURCE_SHA and pre['actual_reference_SHA']==spec['reference_artifact_SHA'],'source/reference binding')
 require(pre['actual_physics_dt']==.0025 and pre['actual_control_dt']==.01 and pre['actual_solver']==[1,32,4],'original solver clock')
 require(pre['legacy_native86_model_or_optimizer_loaded'] is False and pre['new_native_model_initialization'] is True,'fresh architecture')
 require(len(pre['actual_joint_names'])==30 and len(set(pre['actual_joint_names']))==30 and len(pre['actual_body_names'])==31,'actual names')
 bootstrap=pre['actual_source_policy_bootstrap']
 require(bootstrap['policy_actor9_critic8_STD6_17Adam832460_exact'] is True and bootstrap['old20k_environmental_state_restored'] is False,'whole frozen source and fresh physical state')
 return True
