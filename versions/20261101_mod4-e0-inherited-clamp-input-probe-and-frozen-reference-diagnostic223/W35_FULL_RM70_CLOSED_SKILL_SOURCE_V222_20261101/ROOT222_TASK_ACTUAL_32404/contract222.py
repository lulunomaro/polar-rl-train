"""Immutable newW35 model and bounded skill-only Task;no old active binding."""
def validate_task(t):
 assert t['kind']=='NEW222_W35_CLOSED_FULL_RM70_SKILL_ONLY'and t['model_SHA']=='343e0fd8f4950ffea2b09808a3bf88d9dd68e14b06f84c7bdaad462dbc8a51bd'
 assert t['model_iteration']==32404 and t['num_envs']==20000 and t['controls_max']==1600 and t['physics_max']==12800 and t['feedback_max']==3200
 assert t['worker_seconds']==1680 and t['parent_seconds']==1800 and t['GPU_UUID']=='GPU-c27eecbd-6838-7290-1cd2-37e34522213d'
 assert t['no_new_learning_or_GO']and t['model_physical_byte_reads']==t['model_decodes']==1 and t['model_copies']==0
 return True
def validate_current_authority(c,binding,owner_identity=None,owner_current=None):
 assert c['active_segment']is None and c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026'and c['authorized_training_seconds']==2268000 and c['new_authority_budget_extensions']==[]
 return True
