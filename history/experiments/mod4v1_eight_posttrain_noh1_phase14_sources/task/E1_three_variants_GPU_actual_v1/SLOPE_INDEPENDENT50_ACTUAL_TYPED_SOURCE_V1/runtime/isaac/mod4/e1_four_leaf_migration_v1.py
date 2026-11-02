"""Pure complete-dict E1 original100Hz700N ->50Hz400N migration function.
NO load/save/hash/model/SDK/RNG calls. Returns a NEW root and three shallow
record copies; every other subtree object is retained by identity, including
unknown extra fields, all tensors/STD17Adam/privateRNG20k history/timestamps.
Migration receipt stays OUTSIDE the checkpoint. Actual source I/O is future.
"""
import math

FOUR_PATHS=(('physical_action_delay_state','control_us'),('physical_action_delay_recipe','control_period_us'),('spring_pressure_recipe','nominal_stiffness_N_m'),('spring_pressure_recipe','actual_stiffness_bounds_N_m'))
OLD_VALUES=(10000,10000,3500,[3150,3850])
NEW_VALUES=(20000,20000,2000,[1800,2200])
REQUIRED=('actor_state_dict','critic_state_dict','optimizer_state_dict','iter','sensor_DR_state','sensor_recipe','sensor_global_rng_state','sensor_command_DR_rng_state','sensor_physical_DR_rng_state','feedback_delay_state','feedback_delay_recipe','physical_action_delay_state','physical_action_delay_recipe','spring_pressure_state','spring_pressure_recipe','gas_damping_state','gas_damping_recipe','chassis_PD_state','chassis_PD_recipe','E1_terrain_state','E1_retained_flat_command_state','E1_current_command_profile','independent_terrain_expert')

def require(value,message):
 if not value:raise ValueError(message)

def leaf(root,path):
 for key in path:root=root[key]
 return root

def assert_only_four_paths(source,derived,*,reverse=False):
 """No tensor comparisons/dtype conversion: immutable unrelated objectidentity."""
 require(type(source) is dict and type(derived) is dict and set(source)==set(derived),'Original complete rootkey set required; no new metadata inside checkpoint')
 changed={p:(o,n) for p,o,n in zip(FOUR_PATHS,OLD_VALUES,NEW_VALUES)}
 def walk(a,b,path=()):
  if path in changed:
   old,new=changed[path];require(a==old and b==(old if reverse else new),'Incorrect fourleaf '+repr(path));return
  if a is b:return
  require(type(a) is dict and type(b) is dict and set(a)==set(b),'Unchanged subtree must retain original objectidentity '+repr(path))
  for k in a:walk(a[k],b[k],path+(k,))
 walk(source,derived);return True

def reverse_four_leaf_view(derived,original_values):
 require(set(original_values)==set(FOUR_PATHS),'Exactly fouroriginal leaves required')
 inverse=dict(derived)
 for key in {p[0] for p in FOUR_PATHS}:inverse[key]=dict(derived[key])
 for path in FOUR_PATHS:inverse[path[0]][path[1]]=original_values[path]
 return inverse

def migrate_complete_source(source,*,role,expected_num_envs=20000):
 """Call only with the future once-loaded COMPLETE dict. Never slices/lifts actor.
Future sourcepath/LR/iter are actual input facts, NOT selected by latest/rank.
This function itself does not stat/hash/decode/write PT and has no Torch import.
"""
 require(type(source) is dict and all(k in source for k in REQUIRED),'Complete original E1 fullstate dict required')
 require(role in ('E1_CURB','E1_SLOPE') and source['independent_terrain_expert']==role,'Exact E1role, not H1/flat/W35/native/student')
 require(expected_num_envs==20000 and source['spring_pressure_state']['n']==20000,'All original20k pressure history required')
 require(source['physical_action_delay_state']['n']==20000,'All20k queues required')
 require(len(source['actor_state_dict'])==9 and len(source['critic_state_dict'])==8,'Original actor9/critic8 state required')
 require(tuple(source['actor_state_dict']['distribution.std_param'].shape)==(6,),'Original learned STD6 required')
 require(tuple(source['actor_state_dict']['mlp.0.weight'].shape)==(256,35) and tuple(source['critic_state_dict']['mlp.0.weight'].shape)==(256,38),'Original actor35/cleancritic38 fixedSI interface')
 opt=source['optimizer_state_dict'];require(len(opt['state'])==17 and len(opt['param_groups'])==1,'Original17Adam and exact onegroup required')
 actual_lr=opt['param_groups'][0]['lr'];require(isinstance(actual_lr,(int,float)) and math.isfinite(actual_lr) and actual_lr>0,'Actual savedLR required; no arithmetic/default fill')
 require(source['feedback_delay_recipe']['control_period_us']==10000,'Feedback remains100Hz/10ms, NEVER20ms')
 before={p:leaf(source,p) for p in FOUR_PATHS}
 require(all(before[p]==v for p,v in zip(FOUR_PATHS,OLD_VALUES)),'Only original100Hz700N input; no repeat retyping')
 derived=dict(source)
 for key in {p[0] for p in FOUR_PATHS}:derived[key]=dict(source[key])
 for path,new in zip(FOUR_PATHS,NEW_VALUES):derived[path[0]][path[1]]=list(new) if isinstance(new,list) else new
 assert_only_four_paths(source,derived)
 inverse=reverse_four_leaf_view(derived,before);assert_only_four_paths(source,inverse,reverse=True)
 require(derived['feedback_delay_recipe'] is source['feedback_delay_recipe'] and derived['feedback_delay_state'] is source['feedback_delay_state'],'Original100Hz feedback recipe/history retained')
 receipt=dict(kind='E1_FOUR_LEAF_SOURCE_MIGRATION_FUNCTION_RECEIPT',role=role,changed_paths=[list(p) for p in FOUR_PATHS],four_changes=[dict(path=list(p),old=before[p],new=leaf(derived,p)) for p in FOUR_PATHS],all_other_subtrees_original_object_identity=True,reverse_four_leaf_proof=True,checkpoint_topkeys_unchanged=True,unknown_extra_fields_retained=True,actor_STD17Adam_global_named_private_RNG_and20k_history_queue_timestamps_unchanged=True,actual_saved_iteration=source['iter'],actual_saved_LR=actual_lr,source_Adam_steps_not_inferred=True,policy_hz=50,feedback_hz=100,feedback_recipe_and_0_10000us_delays_unchanged=True,physics_us=2500,full_restore_then_ONE_original_fresh_reset_required=True,PT_reads_stats_hashes_decodes_writes=0,new_skill_or_GPU_pass=False)
 return derived,receipt
