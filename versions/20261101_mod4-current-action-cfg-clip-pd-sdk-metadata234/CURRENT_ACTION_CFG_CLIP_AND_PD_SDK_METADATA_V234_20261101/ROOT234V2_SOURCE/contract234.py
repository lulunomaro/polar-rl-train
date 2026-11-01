KIND='NEW234_CURRENT_ACTION_CFG_CLIP_PD_DC_METADATA'
E0_PARENT='2df106412ade7c0993f5a51871a4505624600aac7489c011011d9fd24d3ca610'
def validate_current_authority(c,binding,owner_identity=None,owner_current=None):
 assert binding['kind']=='FRESH_CNONE'and c['active_segment']is None
 assert c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026'and c['authorized_training_seconds']==2268000 and c['new_authority_budget_extensions']==[]
 return True
def validate_task(t):
 assert t['kind']==KIND and t['num_envs']==1 and t['controls_max']==t['physics_callbacks_max']==t['feedback_samples_max']==0
 assert t['model_byte_reads']==t['model_decodes']==0 and t['current_authority_binding']['kind']=='FRESH_CNONE'
 assert t['GPU_UUID']=='GPU-16828f91-2b45-b646-8dc0-9481138e2842' and t['SDK_source_files_byte_reads_max']==16 and t['extra_get_dof_limits']==1
 assert t['no_optimizer_or_training_or_budget_write']and not t['training_reward_changed']
 return True
