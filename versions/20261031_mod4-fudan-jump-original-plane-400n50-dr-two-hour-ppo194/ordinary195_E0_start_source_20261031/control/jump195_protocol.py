"""One human-selected literalJUMP195/fullstate31984/400N50 slot, sole72 owner."""
import hashlib,json
def validate_schedule(cfg):
 s=cfg['experts'];assert set(s)=={'h1_210'};s=s['h1_210']
 assert s['key']=='h1_210' and s['execution_backend']=='source210' and s['max_parent_seconds']==3900 and s['exit_headroom_seconds']==300
 assert s['source_SHA']=='a92c9e8d7cb3dbda9828b6c37bb38dd63183818e91b1aa3f7746c2c46379c74a' and s['num_envs']==20000
 assert s['literal_jump195_400N50'] and s['no_comparison_arms']
 return True
def valid_ready(row,spec):
 q=row.get('closed_source_CPU') or {};v=q.get('value') or {}
 return bool(row.get('key')==spec['key'] and row.get('manifest_SHA')==spec['manifest_SHA'] and row.get('phase')=='ready' and not row.get('original_error')
  and q.get('SHA')==hashlib.sha256(json.dumps(v,indent=2).encode()).hexdigest()
  and v.get('passed') and v.get('kind')=='JUMP195_LITERAL_400N50_ACTUAL_CPU_NATIVE8_AND_DELIVERY31984_FULLSTATE_REUSE'
  and v.get('source_SHA')==spec['source_SHA'] and v.get('source_iteration')==31984 and v.get('Adam_step')==641200
  and v.get('all_actor_critic_optimizer_tensors_finite') and v.get('actual_35_38_6_shapes') and v.get('target_CPU_actual_waited_RC')==0
  and v.get('target_GPU0PT_actual_waited_RC')==0 and v.get('actual_native_controls')==8 and v.get('actual_physics_callbacks')==64
  and v.get('literal_reward_text_identity19') and v.get('manifest_SHA')==spec['manifest_SHA'] and v.get('target64_private_EX_released'))
def flat_go_fields(spec):
 return dict(fullstate_reuse31984=True,literal_jump195_400N50=True,source_model_SHA=spec['source_SHA'],actor_obs=35,critic_obs=38,action_dim=6,num_envs=20000,
  source_iteration=31984,input_Adam=641200,preserve_learned_STD=True,original_JUMP195_reward_and_terrain=True,physics_dt=.0025,TGS=[32,4],
  policy_hz=50,feedback_hz=100,nominal_gas_k_N_m=2000,discount_gamma=.9801,discount_lam=.9025,no_comparison_arms=True,
  explicit_new_D0_D7_RNG_history_and_physics=True,actual_H1_step270_scope_admitted=False)
