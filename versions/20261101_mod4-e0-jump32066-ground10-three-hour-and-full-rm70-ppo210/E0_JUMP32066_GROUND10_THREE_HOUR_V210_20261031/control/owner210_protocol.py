"""One genuine mixed E0 continuation; original canonical accounting is external."""
import hashlib,json
SHA='2df106412ade7c0993f5a51871a4505624600aac7489c011011d9fd24d3ca610'
GPUS72={'GPU-16828f91-2b45-b646-8dc0-9481138e2842','GPU-c27eecbd-6838-7290-1cd2-37e34522213d'}

def validate_schedule(cfg):
 assert set(cfg['experts'])=={'e0_72'}
 e=cfg['experts']['e0_72']
 assert e['key']=='e0_72' and e['execution_backend']=='target72' and e['GPU_UUID'] in GPUS72
 assert e['source_SHA']==SHA and e['source_iteration']==32066 and e['source_Adamstep']==642840
 assert e['max_parent_seconds']==11100 and e['exit_headroom_seconds']==300 and e['num_envs']==20000
 assert e['ground_envs']==2000 and e['jump_envs']==18000
 assert e['literal_original_fudan_JUMP'] and e['original_E0_ground_reward'] and e['no_physics_change']
 return True

def valid_ready(row,spec):
 q=row.get('closed_source_CPU') or {};v=q.get('value') or {}
 return bool(row.get('key')==spec['key'] and row.get('phase')=='ready' and row.get('manifest_SHA')==spec['manifest_SHA'] and not row.get('original_error')
  and q.get('SHA')==hashlib.sha256(json.dumps(v,indent=2).encode()).hexdigest()
  and v.get('passed') and v.get('kind')=='MIX210_READY'
  and v.get('source_SHA')==spec['source_SHA'] and v.get('source_iteration')==32066 and v.get('Adam_step')==642840
  and v.get('all_actor_critic_optimizer_tensors_finite') and v.get('actual_35_38_6_shapes') and v.get('actual_original_JUMP19_text_identity')
  and v.get('source_fullstate_CPU_passed') and v.get('actual_target0PT_waited_RC')==0 and v.get('actual_target0PT_controls')==8
  and v.get('actual_target0PT_physics')==64 and v.get('actual_target0PT_feedback')==16 and v.get('target0PT_private_EX_released')
  and v.get('ground_envs')==2000 and v.get('jump_envs')==18000 and v.get('actual_target0PT_ground_envs')==8 and v.get('actual_target0PT_jump_envs')==72
  and v.get('manifest_SHA')==spec['manifest_SHA'])

def flat_go_fields(spec):
 return dict(role_key='e0_72',literal_original_fudan_JUMP=True,original_E0_ground_reward=True,
  source_model_SHA=SHA,source_iteration=32066,input_Adam=642840,
  actor_obs=35,critic_obs=38,action_dim=6,num_envs=20000,preserve_learned_STD=True,
  ground_envs=2000,jump_envs=18000,physics_dt=.0025,TGS=[32,4],policy_hz=50,feedback_hz=100,nominal_gas_k_N_m=2000,
  discount_gamma=.9801,discount_lam=.9025,one_original_writer=True,
  full_actor_critic_STD_17Adam_restore_required=True,explicit_fresh_physics_replay_history=True,
  frozen_original_E0_reference_immutable=True,no_success_claim=True)
