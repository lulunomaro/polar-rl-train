"""New2050 typed Task/Ready/GO only; original accounting/HMAC are outside."""
import hashlib,json
SHA='aac0ef67b8dc7e2b616e45952bf71e09b1ffb24bfcb84644f4d68550ed228869';ADAM=41240;LR=0.00011390625000000006
KIND='MODEL2050_ORIGINAL_FUDAN_JUMP90_E0_GROUND10_400N50_FULLSTATE_V240'
READY_KIND='MODEL2050_LITERAL40050_ACTUAL_SOURCE_CPU_AND_NATIVE8_READY240'
def validate_schedule(c):
 assert set(c['experts'])=={'jump_72'}
 s=c['experts']['jump_72'];assert s['key']=='jump_72' and s['execution_backend']=='target72'
 assert s['source_SHA']==SHA and s['num_envs']==20000 and s['max_parent_seconds']==3900 and s['exit_headroom_seconds']==300
 assert s['literal_original_fudan_JUMP'] and s['ground_envs']==2000 and s['jump_envs']==18000
 return True
def valid_ready(row,spec):
 q=row.get('closed_source_CPU')or{};v=q.get('value')or{}
 return bool(row.get('key')==spec['key'] and row.get('manifest_SHA')==spec['manifest_SHA'] and row.get('phase')=='ready' and not row.get('original_error')
  and q.get('SHA')==hashlib.sha256(json.dumps(v,indent=2).encode()).hexdigest()
  and v.get('passed') and v.get('kind')==READY_KIND and v.get('source_SHA')==SHA and v.get('source_iteration')==2050 and v.get('Adam_step')==ADAM
  and v.get('source_LR')==LR and v.get('source_hidden')==[128,64,32] and v.get('source_ONNX_actor_identity_passed')
  and v.get('all_actor_critic_optimizer_tensors_finite') and v.get('actual_35_38_6_shapes') and v.get('source_CPU_report_SHA')==spec['source_CPU_report_SHA']
  and v.get('target_GPU0PT_actual_waited_RC')==0 and v.get('actual_native_controls')==8 and v.get('actual_physics_callbacks')==64 and v.get('actual_feedback_samples')==16
  and v.get('literal_reward_text_identity19') and v.get('manifest_SHA')==spec['manifest_SHA'] and v.get('target80_private_and_validation_EX_released')
  and v.get('ground_envs')==2000 and v.get('jump_envs')==18000 and v.get('fresh_CNone_CIM_resources_actual') and v.get('mimic_rad')==.01)
def flat_go_fields(s):
 return dict(role_key='jump_72',fullstate_reuse2050=True,source_model_SHA=SHA,source_iteration=2050,input_Adam=ADAM,source_saved_LR=LR,
  actor_obs=35,critic_obs=38,action_dim=6,hidden=[128,64,32],preserve_learned_STD=True,num_envs=20000,ground_envs=2000,jump_envs=18000,
  literal_original_fudan_JUMP=True,original_E0_ground_reward=True,physics_dt=.0025,TGS=[32,4],policy_hz=50,feedback_hz=100,nominal_gas_k_N_m=2000,
  discount_gamma=.9801,discount_lam=.9025,one_original_writer=True,new_target_D0_D7_physical_queues_and_reward_memory=True,
  source_ONNX_actor_identity_passed=True,full_actor_critic_STD_17Adam_restore_required=True,actual_H1_step270_scope_admitted=False)
def validate_go(g,run,t,now):
 assert t['kind']==KIND and t['source_SHA']==SHA and t['source_iteration']==2050 and t['source_Adam_step']==ADAM
 for key,value in flat_go_fields(t).items():assert g[key]==value, key
 assert g['run_id']==run and g['source_SHA']==SHA and g['max_parent_seconds']==3900 and g['exit_headroom_seconds']==300
 assert g['save_deadline']==g['learning_started_epoch']+3600 and g['nominal_end_epoch']==g['learning_started_epoch']+3900
 assert g['learning_started_epoch']<=now<g['save_deadline']
 return True
