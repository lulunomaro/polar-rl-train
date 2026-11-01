KIND='NEW258_D435I_IDEAL_FORWARD_RAY_DEPTH_12CONTROLS_ZERO_PT'
PARENT_SHA='aac0ef67b8dc7e2b616e45952bf71e09b1ffb24bfcb84644f4d68550ed228869'
def validate_current_authority(c,binding,owner_identity=None,owner_current=None):
 assert binding['kind']=='FRESH_CNONE' and c['active_segment'] is None
 assert c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026' and c['authorized_training_seconds']==2268000 and c['new_authority_budget_extensions']==[]
 return True
def qualified240(closing,cpu):
 assert closing['passed_collection']and closing['owner_closed']['canonical_None']and closing['owner_closed']['shared_locks_free']and cpu['passed']
 q=cpu['roles']['jump_72'];r=closing['roles']['jump_72'];f=closing['formals']['jump_72']
 assert q['passed']and q['actor35_critic38_STD6']and q['hidden']==[128,64,32]and q['complete_task_DR_and_persistent_ground_JUMP_state']
 assert q['save_at_or_after_requested_deadline']and not cpu['CUDA_initialized']and cpu['NEW_formal_reads']==1 and cpu['old_model_reads']==0
 assert q['SHA']==f['SHA']==r['formal']['SHA']and q['bytes']==f['bytes']==r['formal']['bytes']and f['two_host_SHA_equal']and f['transfers']==1
 assert q['saved_iteration']==2050+q['new_PPO_updates']and q['Adam17_step']==41240+20*q['new_PPO_updates']and q['new_PPO_updates']>0
 assert r['qualified_formal']and r['private_EX_free']and r['actual_material_limit_error_count']==0
 assert q['actual_GO']['source_model_SHA']==PARENT_SHA and r['formal']['source_SHA']==PARENT_SHA
 return dict(SHA=q['SHA'],bytes=q['bytes'],iteration=q['saved_iteration'],Adam17=q['Adam17_step'],path=r['formal']['path'],source_parent_SHA=PARENT_SHA)
def validate_task(t):
 assert t['closure_threshold_m']==.01 and t['mimic_threshold_rad']==.01 and t['human_requested_closure_change']
 assert t['kind']==KIND and t['num_envs']==1 and t['controls_per_case_max']==12 and t['controls_max']==12
 q=t['actual_closed240_qualification'];assert t['model_SHA']==q['SHA']and t['model_bytes']==q['bytes']and t['model_path']==q['path']
 assert t['model_iteration']==q['iteration']and t['actual_17Adam_step']==q['Adam17']and t['source_parent_SHA']==PARENT_SHA
 assert t['model_SHA']!=PARENT_SHA and len(t['model_SHA'])==64 and t['model_iteration']>2050 and t['source240_formal_CPU_actual_passed']
 assert t['policy_hz']==50 and t['physics_dt']==.0025 and t['TGS']==[32,4]and t['feedback_hz']==100
 assert t['GPU_UUID']=='GPU-16828f91-2b45-b646-8dc0-9481138e2842' and t['current_authority_binding']['kind']=='FRESH_CNONE'
 assert t['model_byte_reads']==t['model_decodes']==0 and t['model_copies']==0
 assert t['no_optimizer_or_training_or_budget_write']and not t['training_reward_changed']
 assert [(x['name'],x['env'])for x in t['cases']]==[('sensor_zero_action',0)]
 return True
