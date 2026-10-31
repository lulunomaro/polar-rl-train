"""One canonical owner; actual194 remainder plus E0_72 one-hour learning."""
import hashlib,json
E0='a92c9e8d7cb3dbda9828b6c37bb38dd63183818e91b1aa3f7746c2c46379c74a'
GPUS72={'GPU-16828f91-2b45-b646-8dc0-9481138e2842','GPU-c27eecbd-6838-7290-1cd2-37e34522213d'}
GPU210='GPU-937bdb0b-0d8f-aa3d-a10e-1b24969a5d4e'
def validate_schedule(cfg):
 s=cfg['experts'];assert set(s)=={'h1_210','e0_72'}
 e=s['e0_72'];h=s['h1_210']
 assert e['key']=='e0_72' and e['execution_backend']=='target72' and e['GPU_UUID'] in GPUS72
 assert e['max_parent_seconds']==3900 and e['exit_headroom_seconds']==300 and e['source_SHA']==E0
 assert e['source_iteration']==31984 and e['source_Adamstep']==641200
 assert h['key']=='h1_210' and h['execution_backend']=='source210' and h['GPU_UUID']==GPU210
 assert h['exit_headroom_seconds']==300 and 0<h['remaining_primary_seconds']<=7200
 assert h['max_parent_seconds']==h['remaining_primary_seconds']+300
 assert h['source_iteration']>=5000 and h['source_Adamstep']==100020+20*(h['source_iteration']-4999)
 assert h['old194_requested_seconds']==7200 and h['old194_used_seconds']+h['remaining_primary_seconds']==7200
 for key,v in s.items():
  assert v['key']==key and v['num_envs']==20000 and len(v['source_SHA'])==64
  assert v['literal_original_fudan_JUMP'] and v['no_reward_or_physics_change']
 return True
def valid_ready(row,spec):
 q=row.get('closed_source_CPU') or {};v=q.get('value') or {}
 return bool(row.get('key')==spec['key'] and row.get('phase')=='ready' and row.get('manifest_SHA')==spec['manifest_SHA'] and not row.get('original_error')
  and q.get('SHA')==hashlib.sha256(json.dumps(v,indent=2).encode()).hexdigest()
  and v.get('passed') and v.get('kind')=='LITERAL_JUMP_PARALLEL197_READY'
  and v.get('source_SHA')==spec['source_SHA'] and v.get('source_iteration')==spec['source_iteration'] and v.get('Adam_step')==spec['source_Adamstep']
  and v.get('all_actor_critic_optimizer_tensors_finite') and v.get('actual_35_38_6_shapes') and v.get('actual_original_JUMP19_text_identity')
  and v.get('source_fullstate_CPU_passed') and v.get('actual_target0PT_waited_RC')==0 and v.get('actual_target0PT_controls')==8
  and v.get('actual_target0PT_physics')==64 and v.get('actual_target0PT_feedback')==16 and v.get('target0PT_private_EX_released')
  and v.get('manifest_SHA')==spec['manifest_SHA'])
def flat_go_fields(spec):
 return dict(role_key=spec['key'],literal_original_fudan_JUMP=True,
  source_model_SHA=spec['source_SHA'],source_iteration=spec['source_iteration'],input_Adam=spec['source_Adamstep'],
  actor_obs=35,critic_obs=38,action_dim=6,num_envs=20000,preserve_learned_STD=True,
  physics_dt=.0025,TGS=[32,4],policy_hz=50,feedback_hz=100,nominal_gas_k_N_m=2000,
  discount_gamma=.9801,discount_lam=.9025,one_original_writer=True,
  full_actor_critic_STD_17Adam_restore_required=True,explicit_fresh_physics_replay_history=True,
  original194_remainder_seconds=spec.get('remaining_primary_seconds'),no_success_claim=True)
