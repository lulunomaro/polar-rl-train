E0_PARENT='2df106412ade7c0993f5a51871a4505624600aac7489c011011d9fd24d3ca610'
KIND='NEW228_E0_ORIGINAL_ACTION_TERM_OPTIMIZER_IDENTITY_0PT_METADATA'
def validate_task(t):
 assert t['kind']==KIND and t['num_envs']==1 and t['controls_max']==t['physics_callbacks_max']==t['feedback_samples_max']==0
 assert t['model_byte_reads']==t['model_decodes']==0 and t['no_optimizer_or_training_or_budget_write']and t['current_authority_binding']['kind']=='FRESH_CNONE'
 assert t['GPU_UUID']=='GPU-16828f91-2b45-b646-8dc0-9481138e2842'
 return True
def validate_current_authority(c,binding,owner_identity=None,owner_current=None):
 assert c['active_segment']is None and c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026'and c['authorized_training_seconds']==2268000 and c['new_authority_budget_extensions']==[]
 return True
