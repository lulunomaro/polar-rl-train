KIND='NEW230_CANDIDATE225_STAND_FORWARD_REVERSE_LITERAL_JUMP_REGRESSION'
def validate_current_authority(c,binding,owner_identity=None,owner_current=None):
 assert binding['kind']=='FRESH_CNONE' and c['active_segment'] is None
 assert c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026' and c['authorized_training_seconds']==2268000 and c['new_authority_budget_extensions']==[]
 return True
def validate_task(t):
 assert t['kind']==KIND and t['num_envs']==10 and t['controls_per_case_max']==500 and t['controls_max']==2000
 assert t['model_SHA']=='17696bc47c494ba84a0bd872c4e9be9595410045e90f9abd1a1949d701e9cbaf' and t['model_bytes']==22956985
 assert t['model_iteration']==32341 and t['actual_17Adam_step']==648340
 assert t['policy_hz']==50 and t['physics_dt']==.0025 and t['TGS']==[32,4] and t['feedback_hz']==100
 assert t['GPU_UUID']=='GPU-16828f91-2b45-b646-8dc0-9481138e2842' and t['current_authority_binding']['kind']=='FRESH_CNONE'
 assert t['model_byte_reads']==t['model_decodes']==1 and t['model_copies']==1
 assert t['no_optimizer_or_training_or_budget_write'] and not t['training_reward_changed']
 assert [(x['name'],x['env']) for x in t['cases']]==[('standing',0),('forward',0),('reverse',0),('literal_jump',1)]
 return True
