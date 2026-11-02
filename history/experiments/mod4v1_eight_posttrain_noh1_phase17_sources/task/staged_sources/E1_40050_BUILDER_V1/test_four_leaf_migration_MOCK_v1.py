"""MOCK ONLY. No Torch, actualcheckpoint/model/SHA/stat/decode, SDK or RNG calls."""
from pathlib import Path
import ast,copy,hashlib,json,time,traceback
B=Path(__file__).resolve().parent;P=B/'e1_four_leaf_migration_v1.template.py'
class OpaqueMock:
 def __init__(self,name,shape=()):self.name=name;self.shape=shape

def fixture(role):
 x={k:OpaqueMock('MOCK_'+k) for k in ('sensor_DR_state','sensor_recipe','sensor_global_rng_state','sensor_command_DR_rng_state','sensor_physical_DR_rng_state','feedback_delay_state','gas_damping_state','gas_damping_recipe','chassis_PD_state','chassis_PD_recipe','E1_terrain_state','E1_retained_flat_command_state','E1_current_command_profile')}
 x.update(independent_terrain_expert=role,iter=12345,actor_state_dict={'distribution.std_param':OpaqueMock('MOCK_STD',(6,)),'mlp.0.weight':OpaqueMock('MOCK_ACTOR35',(256,35)),**{f'MOCK_ACTOR_{i}':OpaqueMock('MOCK_ACTOR_LEAF_'+str(i)) for i in range(7)}},critic_state_dict={'mlp.0.weight':OpaqueMock('MOCK_CRITIC38',(256,38)),**{f'MOCK_CRITIC_{i}':OpaqueMock('MOCK_CRITIC_LEAF_'+str(i)) for i in range(7)}},optimizer_state_dict=dict(state={i:dict(step=321,exp_avg=OpaqueMock('MOCK_ADAM_M_'+str(i)),exp_avg_sq=OpaqueMock('MOCK_ADAM_V_'+str(i))) for i in range(17)},param_groups=[dict(lr=.000123,params=list(range(17)))]),physical_action_delay_state=dict(n=20000,control_us=10000,history=OpaqueMock('MOCK_ALL20K_QUEUE_HISTORY',(20000,4)),timestamps=OpaqueMock('MOCK_ORIGINAL_TIMESTAMPS',(20000,)),rng=OpaqueMock('MOCK_PRIVATE_QUEUE_RNG')),physical_action_delay_recipe=dict(control_period_us=10000,physics_period_us=2500,actual_transition_delay_us=[0,2500,5000]),spring_pressure_state=dict(n=20000,factor=OpaqueMock('MOCK_FACTOR',(20000,2)),episode=OpaqueMock('MOCK_EPISODE',(20000,)),rng=[OpaqueMock('MOCK_PRIVATE_D5_0'),OpaqueMock('MOCK_PRIVATE_D5_1')]),spring_pressure_recipe=dict(nominal_stiffness_N_m=3500,actual_stiffness_bounds_N_m=[3150,3850],opaque_original_metadata=OpaqueMock('MOCK_RECIPE_META')),feedback_delay_recipe=dict(control_period_us=10000,delay_ms=[0,10],requested_delay_us=[0,10000]),UNKNOWN_EXTRA_FULLSTATE_DO_NOT_DROP=OpaqueMock('MOCK_VARIANT_SPECIFIC_EXTRA'))
 if role=='E1_CURB':x['E1_CURB_entry_direction_state']=OpaqueMock('MOCK_DIRECTION_ALL20K',(20000,));x['E1_CURB_entry_reset_identity']=dict(entry_map_sha='MOCK_ENTRY_MAP_NO_REAL_SOURCE')
 return x

def main():
 raw=P.read_bytes();ns={'__name__':'pure_mock_migration_only'};exec(compile(raw,str(P),'exec'),ns);migrate=ns['migrate_complete_source'];rows=[]
 for role in ('E1_CURB','E1_SLOPE'):
  source=fixture(role);before=dict(source);typed,receipt=migrate(source,role=role)
  assert set(typed)==set(source) and all(source[k] is before[k] for k in source)
  assert source['physical_action_delay_state']['control_us']==10000 and source['spring_pressure_recipe']['nominal_stiffness_N_m']==3500
  assert typed['feedback_delay_recipe'] is source['feedback_delay_recipe'] and typed['feedback_delay_recipe']['requested_delay_us']==[0,10000]
  assert typed['physical_action_delay_state']['history'] is source['physical_action_delay_state']['history'] and typed['physical_action_delay_state']['timestamps'] is source['physical_action_delay_state']['timestamps']
  assert typed['optimizer_state_dict'] is source['optimizer_state_dict'] and typed['actor_state_dict'] is source['actor_state_dict'] and typed['UNKNOWN_EXTRA_FULLSTATE_DO_NOT_DROP'] is source['UNKNOWN_EXTRA_FULLSTATE_DO_NOT_DROP']
  negative=[]
  def rejected(label,data):
   try:migrate(data,role=role)
   except ValueError:negative.append(dict(name=label,rejected=True));return
   raise AssertionError('Negative MOCK unexpectedly accepted '+label)
  rejected('repeat_typed40050_not_original',typed)
  broken=dict(source);broken['feedback_delay_recipe']={**source['feedback_delay_recipe'],'control_period_us':20000};rejected('feedback_cannot_be20ms',broken)
  broken=dict(source);broken['physical_action_delay_state']={**source['physical_action_delay_state'],'n':80};rejected('no20k_to80_slice',broken)
  broken=dict(source);broken['optimizer_state_dict']={**source['optimizer_state_dict'],'state':{i:object() for i in range(16)}};rejected('no16Adam',broken)
  broken=dict(source);broken['independent_terrain_expert']='H1_NORMAL';rejected('no_foreign_factory_role',broken)
  altered=dict(typed);altered['UNKNOWN_EXTRA_FULLSTATE_DO_NOT_DROP']=OpaqueMock('replacement')
  try:ns['assert_only_four_paths'](source,altered)
  except ValueError:negative.append(dict(name='unknownextra_replacement_not_ignored',rejected=True))
  else:raise AssertionError('Unknownextra mutation missed')
  rows.append(dict(role=role,MOCK_NOT_ACTUAL_CHECKPOINT=True,passed=True,receipt=receipt,full20k_scope_is_symbolic_mock_shape_not_realweights=True,negative_cases=negative,all_original_objects_and_unknownextras_retained=True))
 astree=ast.parse(raw);imports=[n.module for n in ast.walk(astree) if isinstance(n,ast.ImportFrom)]+[a.name for n in ast.walk(astree) if isinstance(n,ast.Import) for a in n.names];assert imports==['math']
 report=dict(kind='E1_FOUR_LEAF_MIGRATION_MOCK_ONLY_NOT_ACTUAL_GPU_OR_PT',passed=True,rows=rows,source_path=str(P),source_SHA=hashlib.sha256(raw).hexdigest(),source_AST_SHA=hashlib.sha256(ast.dump(astree,include_attributes=False).encode()).hexdigest(),mock_values_not_real_saved_iter_LR_Adam=True,real_PT_stat_or_reads_or_hash_or_decode=0,Torch_or_SDK_or_SSH_GPU_budget_operations=0)
 with (B/'FOUR_LEAF_MIGRATION_MOCK_PROOF_v1.json').open('x',encoding='utf-8') as f:json.dump(report,f,indent=2)
 print(json.dumps(dict(status='MOCK_ONLY_PASS_NO_ACTUAL_CHECKPOINT',roles=len(rows),negative_cases=sum(len(r['negative_cases']) for r in rows),report=str(B/'FOUR_LEAF_MIGRATION_MOCK_PROOF_v1.json')),indent=2))
if __name__=='__main__':
 try:main()
 except BaseException:
  with (B/('MIGRATION_MOCK_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf-8') as f:json.dump(dict(error=traceback.format_exc(),MOCK_only=True,real_PT_SDK_operations=0),f,indent=2)
  raise
