"""Static genuine E0-three-hour and fullRM70-one-hour roles, one writer."""
import hashlib,json
from owner210_protocol import flat_go_fields as e0_fields
E0='2df106412ade7c0993f5a51871a4505624600aac7489c011011d9fd24d3ca610'
W35='ad504fec819b22f10fd1caf7befc59c1988c7609fe15373ab8851ef95942df3f'
GPUS={'GPU-16828f91-2b45-b646-8dc0-9481138e2842','GPU-c27eecbd-6838-7290-1cd2-37e34522213d'}

def validate_schedule(cfg):
 assert set(cfg['experts'])=={'e0_72','w35_72'}
 s=cfg['experts'];e=s['e0_72'];w=s['w35_72']
 assert e['source_SHA']==E0 and e['source_iteration']==32066 and e['source_Adamstep']==642840
 assert e['max_parent_seconds']==11100 and e['ground_envs']==2000 and e['jump_envs']==18000
 assert w['source_SHA']==W35 and w['source_iteration']==32336 and w['source_Adamstep']==648360
 assert w['max_parent_seconds']==3900 and w['source_kind']=='MOD4_W35_FULL_RM70_208_V3'
 assert w['actual_scene211_passed'] and w['actual_robot212_passed'] and w['original_full_RM70_CAD_geometry']
 assert e['GPU_UUID']!=w['GPU_UUID'] and {e['GPU_UUID'],w['GPU_UUID']}==GPUS
 for k,v in s.items():
  assert v['key']==k and v['execution_backend']=='target72' and v['num_envs']==20000
  assert v['exit_headroom_seconds']==300 and v['no_physics_change']
 return True

def valid_ready(row,spec):
 q=row.get('closed_source_CPU') or {};v=q.get('value') or {}
 base=bool(row.get('key')==spec['key'] and row.get('phase')=='ready' and row.get('manifest_SHA')==spec['manifest_SHA'] and not row.get('original_error')
  and q.get('SHA')==hashlib.sha256(json.dumps(v,indent=2).encode()).hexdigest()
  and v.get('passed') and v.get('source_SHA')==spec['source_SHA'] and v.get('source_iteration')==spec['source_iteration'] and v.get('Adam_step')==spec['source_Adamstep']
  and v.get('all_actor_critic_optimizer_tensors_finite') and v.get('actual_35_38_6_shapes') and v.get('source_fullstate_CPU_passed')
  and v.get('actual_target0PT_waited_RC')==0 and v.get('actual_target0PT_controls')==8 and v.get('actual_target0PT_physics')==64
  and v.get('actual_target0PT_feedback')==16 and v.get('target0PT_private_EX_released') and v.get('manifest_SHA')==spec['manifest_SHA'])
 if not base:return False
 if spec['key']=='e0_72':
  return bool(v.get('kind')=='MIX210_READY' and v.get('actual_original_JUMP19_text_identity') and v.get('ground_envs')==2000 and v.get('jump_envs')==18000
   and v.get('actual_target0PT_ground_envs')==8 and v.get('actual_target0PT_jump_envs')==72)
 return bool(v.get('kind')=='MOD4_W35_FULL_RM70_208_V3' and v.get('actual_scene211_passed') and v.get('actual_robot212_passed')
  and v.get('original_full_RM70_CAD_geometry') and v.get('SDK_xyzw_selected') and v.get('original_guard_and400N50DR'))

def flat_go_fields(spec):
 if spec['key']=='e0_72':return e0_fields(spec)
 return dict(role_key='w35_72',GPU_UUID=spec['GPU_UUID'],authority_generation='MOD4_SINGLE_WRITER72_20261026',
  source_qualification_kind='MOD4_W35_FULL_RM70_208_V3',source_model_SHA=W35,source_iteration=32336,input_Adam=648360,
  actor_obs=35,critic_obs=38,action_dim=6,num_envs=20000,preserve_learned_STD=True,
  physics_dt=.0025,TGS=[32,4],policy_hz=50,feedback_hz=100,nominal_gas_k_N_m=2000,discount_gamma=.9801,discount_lam=.9025,
  one_original_writer=True,full_actor_critic_STD_17Adam_restore_required=True,explicit_fresh_physics_replay_history=True,
  genuine_W35_full_original_RM70_course=True,not_a_native_SuperMimic_conversion=True,no_success_claim=True)
