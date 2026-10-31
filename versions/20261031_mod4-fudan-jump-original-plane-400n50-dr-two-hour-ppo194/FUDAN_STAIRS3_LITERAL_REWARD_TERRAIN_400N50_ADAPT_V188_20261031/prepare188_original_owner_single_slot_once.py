from pathlib import Path
import ast,hashlib,json,shutil,time
N=Path(__file__).resolve().parent;T=N.parent;old=T/'MOD4_DELIVERED_FUDAN_JUMP4999_REUSE_RESOURCE_V186_20261031/control';D=N/'control';D.mkdir()
for name in ['forwarded_original_owner_control_v1.py','OWNER72_CONTROL_DEPENDENCIES_BINDING_ACTUAL.json','single_writer72_authority_V85M_source.py']:
 shutil.copyfile(old/name,D/name)
for src,dst in [('three_slot_common_v1.py','three_slot_common_v1.py'),('reuse186_finite_owner_authority72_v1.py','stairs188_finite_owner_authority72.py'),('reuse186_fullstate_slot_node_v1.py','stairs188_fullstate_slot_node.py')]:
 text=(old/src).read_text(encoding='utf8').replace('reuse186_protocol_v1','stairs188_protocol')
 text=text.replace('Linux_ONE186_DELIVERED_MODEL4999_FULLSTATE_REUSE_','Linux_ONE188_FUDAN_STAIRS3_LITERAL40050_')
 text=text.replace('human_requested_single_delivered_PPO_continuation','human_requested_literal_STAIRS3_reward_terrain_400N50_adaptation')
 text=text.replace("creation=p.create_time(),argv=p.cmdline(),root=p.cwd()","creation=p.create_time(),exe=p.exe(),argv=p.cmdline(),root=p.cwd()")
 ast.parse(text);(D/dst).write_text(text,encoding='utf8')
protocol='''"""One human-selected literalSTAIRS3/fullstate4999/400N50 slot, sole72 owner."""
import hashlib,json
def validate_schedule(cfg):
 s=cfg['experts'];assert set(s)=={'h1_210'};s=s['h1_210']
 assert s['key']=='h1_210' and s['execution_backend']=='source210' and s['max_parent_seconds']==3900 and s['exit_headroom_seconds']==300
 assert s['source_SHA']=='5932295297ed93b65fd88fe142d6fc66099c0a936f23091a79a3b2752c51dfa4' and s['num_envs']==20000
 assert s['literal_stairs3_400N50'] and s['no_comparison_arms']
 return True
def valid_ready(row,spec):
 q=row.get('closed_source_CPU') or {};v=q.get('value') or {}
 return bool(row.get('key')==spec['key'] and row.get('manifest_SHA')==spec['manifest_SHA'] and row.get('phase')=='ready' and not row.get('original_error')
  and q.get('SHA')==hashlib.sha256(json.dumps(v,indent=2).encode()).hexdigest()
  and v.get('passed') and v.get('kind')=='STAIRS3_LITERAL_400N50_ACTUAL_CPU_NATIVE8_AND_DELIVERY4999_FULLSTATE_REUSE'
  and v.get('source_SHA')==spec['source_SHA'] and v.get('source_iteration')==4999 and v.get('Adam_step')==100020
  and v.get('all_actor_critic_optimizer_tensors_finite') and v.get('actual_35_38_6_shapes') and v.get('target_CPU_actual_waited_RC')==0
  and v.get('target_GPU0PT_actual_waited_RC')==0 and v.get('actual_native_controls')==8 and v.get('actual_physics_callbacks')==64
  and v.get('literal_reward_text_identity31') and v.get('manifest_SHA')==spec['manifest_SHA'] and v.get('target64_private_EX_released'))
def flat_go_fields(spec):
 return dict(fullstate_reuse4999=True,literal_stairs3_400N50=True,source_model_SHA=spec['source_SHA'],actor_obs=35,critic_obs=38,action_dim=6,num_envs=20000,
  source_iteration=4999,input_Adam=100020,preserve_learned_STD=True,original_STAIRS3_reward_and_terrain=True,physics_dt=.0025,TGS=[32,4],
  policy_hz=50,feedback_hz=100,nominal_gas_k_N_m=2000,discount_gamma=.9801,discount_lam=.9025,no_comparison_arms=True,
  explicit_new_D0_D7_RNG_history_and_physics=True,actual_H1_step270_scope_admitted=False)
'''
ast.parse(protocol);(D/'stairs188_protocol.py').write_text(protocol,encoding='utf8')
# Canonical location, two original fcntls, signature and raw charge arithmetic
# are inherited literally. Only task readiness/GO typing and own identities differ.
a=ast.parse((old/'three_slot_common_v1.py').read_bytes());b=ast.parse((D/'three_slot_common_v1.py').read_bytes())
for name in ['authenticated_row','charge_values']:
 x=next(x for x in a.body if isinstance(x,ast.FunctionDef) and x.name==name);y=next(x for x in b.body if isinstance(x,ast.FunctionDef) and x.name==name)
 assert ast.dump(x,include_attributes=False)==ast.dump(y,include_attributes=False)
rows=[dict(relative=p.name,local_path=str(p),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(D.iterdir()) if p.is_file()]
(N/'CONTROL188_MANIFEST.json').write_text(json.dumps(dict(files=rows),indent=2),encoding='utf8')
with (N/'reports/ROOT188_ORIGINAL_AUTH_AND_RAW_FEE_FUNCTIONS_LITERAL_REUSED.json').open('x',encoding='utf8') as f:
 json.dump(dict(epoch=time.time(),passed=True,original_authenticated_row_and_charge_values_AST_literal=True,canonical_budget_copy_or_write=False,source_only=True,one_slot3900_save3600_exit300=True,roles=['h1_210'],files=rows),f,indent=2)
