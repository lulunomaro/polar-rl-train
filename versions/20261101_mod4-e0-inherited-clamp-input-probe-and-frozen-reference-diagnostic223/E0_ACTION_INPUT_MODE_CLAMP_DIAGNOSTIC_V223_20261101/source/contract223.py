"""New223 task has no learning, old active219 binding is forbidden."""
E0_PARENT='2df106412ade7c0993f5a51871a4505624600aac7489c011011d9fd24d3ca610'
KIND='NEW223_E0_FIXEDSI_INPUT_MODE_LEFT_CRANK_CLAMP_FLOW'
def validate_current_authority(c,binding,owner_identity=None,owner_current=None):
 assert binding['kind']=='FRESH_CNONE'and c['active_segment']is None
 assert c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026'and c['authorized_training_seconds']==2268000 and c['new_authority_budget_extensions']==[]
 return True
def validate_task(t):
 assert t['kind']==KIND and t['num_envs']==1 and t['controls_max']==32 and t['physics_callbacks_max']==256 and t['feedback_samples_max']==64
 assert t['model_SHA']=='e6291fc50e692b9921dfe8ddcbfcc678e9b5916441229c2fd7a4f2c2cc75a538'and t['model_iteration']==32341
 assert t['policy_hz']==50 and t['physics_dt']==.0025 and t['TGS']==[32,4]and t['feedback_hz']==100
 assert t['eval_yaw_range']==[0.,0.]and t['current_authority_binding']['kind']=='FRESH_CNONE'
 assert t['GPU_UUID']=='GPU-16828f91-2b45-b646-8dc0-9481138e2842'and t['target_host']=='72'
 assert t['model_path']=='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_E0_JUMP32066_GROUND10_THREE_HOUR_20261031v210/e0_72/production/model_final_complete.pt'
 assert t['model_byte_reads']==t['model_decodes']==1 and t['model_copies']==0
 assert t['no_optimizer_or_training_or_budget_write']and not t['training_reward_changed']
 return True
