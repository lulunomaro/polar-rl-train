from pathlib import Path
import ast,hashlib,json,time,traceback
B=Path(__file__).resolve().parent;L=B.parent;T=L.parent;R=B/'reports'
N=T/'MOD4_H1_FUDAN270_NATIVE_RESOURCE_V103_20261028';C=L/'TWO103_FUDAN270_ACTUAL_CPU_BOUND_ORIGINAL_OWNER_SOURCE_V3'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,s):
 with p.open('x',encoding='utf8') as f:f.write(s)
def put(name,v):
 with (R/name).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def rep(s,a,b,n=1):
 assert s.count(a)==n,(a,s.count(a),n);return s.replace(a,b)
def literal(s,name):return next(ast.literal_eval(x.value) for x in ast.parse(s).body if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in x.targets))
def assign(s,name,v):
 x=next(x for x in ast.parse(s).body if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in x.targets));lines=s.splitlines(keepends=True);return ''.join(lines[:x.lineno-1])+name+'='+repr(v)+'\n'+''.join(lines[x.end_lineno:])
def common(s):
 return s.replace('TWO101_PRODUCER_FIXED_NATIVE20_ORIGINAL_OWNER_SOURCE_V1','TWO103_FUDAN270_ACTUAL_CPU_BOUND_ORIGINAL_OWNER_SOURCE_V3').replace('TWO101_PRODUCER_FIXED_NATIVE20_FIRST_POLICY_OBSERVER_SOURCE_V1',B.name).replace('TWO101_CORRECT_NORMAL900_TWO_NATIVE20_COLLECTOR_SOURCE_V1',B.name).replace('TWO101','TWO103').replace('NEW101','NEW103').replace('NATIVE101','NATIVE103').replace('native101_','native103_').replace('closed101','closed103').replace('input_native99','input_native101')
def main():
 assert not (B/'FROZEN_UNUSED_FIRST_CLOSING_INITIAL_CPU_SOURCE_INDEX_V1.json').exists()
 public=json.loads((C/'reports/TWO103_ACTUAL_CPU_BOUND_SEALED_PUBLIC_REQUEST.json').read_bytes());assert public['no_GO'] and public['not_GPU_resource_admitted']
 before={'observer':L/'TWO101_PRODUCER_FIXED_NATIVE20_FIRST_POLICY_OBSERVER_SOURCE_V1/observe_two101_producer_fixed_actual20cm_first_policy_once.py','collector':L/'TWO101_CORRECT_NORMAL900_TWO_NATIVE20_COLLECTOR_SOURCE_V1/collect_TWO101_native20_formals_original_cost_correct_normal900_UNUSED_once.py'}
 s=before['observer'].read_text('utf8');remote=literal(s,'NATIVE')
 remote=rep(remote,"positive['native_actual_method']=='own_MOD4_native_flat20cm_same_nominal400'","positive['native_actual_method']=='own_MOD4_native_fudan270_same_nominal400'")
 remote=rep(remote,'mod4.native99_to_flat20.target100.objective_window.v1','mod4.native101_to_fudan270.target103.objective_window.v1')
 remote=rep(remote,"pre['actual_flat_command']['flat_task_command_zero'] and pre['flat_counter_installed_before_first_control'] and pre['actual_selected_flat_objective_class']=='OwnFlatJumpMdp'","pre['actual_fudan_step_command']['request_control_interval']==[200,500] and pre['original_exact270_counter_preserved'] and pre['actual_selected_flat_objective_class']=='OwnFudanStepMdp'")
 remote=rep(remote,"go['stance_reference_revision']==positive['producer']['stance_reference_revision']==spec['stance_reference_revision']","go['fudan_step_task']==positive['producer']['fudan_step_task']==spec['fudan_step_task']")
 remote=rep(remote,"  assert go['flat_jump_target_m']==positive['producer']['flat_jump_target_m']==positive['flat_real_physics_events']['height_m']==spec['flat_jump_target_m']==.20\n  assert positive['producer']['physical_initial_seed']==spec['native_seed'] and pre['actual_flat_counter_height_m']==pre['flat_goal_height_m']==.20", "  assert go['fudan_step_task']['step_top_z_m']==positive['fudan_real_reward_tracking']['step_top_z_m']==pre['actual_step_top_z_m']==.27\n  assert positive['producer']['physical_initial_seed']==spec['native_seed'] and pre['actual_fudan_step_command']['approach_command_m_s']==.5")
 # This exact small installed CPU artifact belongs to task geometry admission,
 # not a model/statistics reread or a manufactured successful jump example.
 needle="  assert not errors,errors\n";remote=rep(remote,needle,needle+"  bank=read(job/'job0/FUDAN103_ACTUAL_INSTALLED_OWN_BANK_FK_TARGET_BINDING_CPU.json');assert bank['passed_source_FK'] and bank['pose_count']==133 and bank['not_dynamic_feasibility_or_airborne_demonstration']\n")
 remote=rep(remote,'actual_precontrol=pre,node=ni','actual_precontrol=pre,installed_own_bank_FK_binding=bank,node=ni')
 ast.parse(remote);s=assign(s,'NATIVE',remote);s=common(s);ast.parse(s)
 write(B/'observe_TWO103_fudan270_first_NEW_native_policy_UNUSED_once.py',s)
 s=before['collector'].read_text('utf8');remote=literal(s,'CODE')
 remote=rep(remote,"  assert go[key]['flat_jump_target_m']==row['original_H1_events']['flat_real_physics_events']['height_m']==.20", "  assert go[key]['fudan_step_task']==row['producer']['fudan_step_task'] and go[key]['fudan_step_task']['step_top_z_m']==.27\n  assert row['original_H1_events']['fudan_real_reward_tracking']['step_top_z_m']==.27")
 remote=rep(remote,'mod4.native99_to_flat20.target100.objective_window.v1','mod4.native101_to_fudan270.target103.objective_window.v1')
 ast.parse(remote);s=assign(s,'CODE',remote);s=common(s)
 s=rep(s,'FIRST=L/'+repr(B.name+'/reports'),"FIRST=HERE/'reports'")
 ast.parse(s);write(B/'collect_TWO103_fudan270_formals_original_cost_normal900_UNUSED_once.py',s)
 # Keep each schema-specific NEW native formal reviewer, preserving every
 # strict module/norm/optimizer, RSL, recipe, original-cost and allout check.
 for mode in ['seed27','seed28']:
  p=L/('TWO101_TWO_NATIVE20_FORMAL_INITIAL_CPU_SOURCE_V1/review_NEW101_'+mode+'_formal_initial_whole_CPU_UNUSED_once.py');s=p.read_text('utf8')
  s=rep(s,"MOD4_H1_FLAT20_NATIVE_PRODUCER_FIX_RESOURCE_V101_20261028","MOD4_H1_FUDAN270_NATIVE_RESOURCE_V103_20261028")
  s=rep(s,"B=N/'payloads/"+mode+"'","B=N/'payloads_v4/"+mode+"'")
  s=rep(s," assert producer['flat_jump_target_m']==.20\n assert producer['input_start_mode']=='continue_warm99_height20' and producer['stance_reference_revision']==NATIVE_CONTRACT['stance_reference_revision']\n assert window['schema']=='mod4.native99_to_flat20.target100.objective_window.v1' and window['reference_SHA']==NATIVE_CONTRACT['stance_reference_revision']['reference_SHA']", " assert producer['fudan_step_task']==NATIVE_CONTRACT['fudan_step_task'] and producer['fudan_step_task']['step_top_z_m']==.27\n assert producer['input_start_mode']=='continue_qualified101_fudan270'\n assert window['schema']=='mod4.native101_to_fudan270.target103.objective_window.v1' and window['reference_SHA']==NATIVE_CONTRACT['reference_artifact_SHA']")
  s=common(s);ast.parse(s);write(B/('review_NEW103_'+mode+'_formal_initial_whole_CPU_UNUSED_once.py'),s)
 p=L/'TWO101_TWO_NATIVE20_FORMAL_INITIAL_CPU_SOURCE_V1/review_TWO101_NEW_native20_formals_one_shared_witness_initial_CPU_UNUSED_once.py';s=common(p.read_text('utf8')).replace('actual20cm_source_and_physical_seeds_bound','actual270mm_task_and_physical_seeds_bound')
 ast.parse(s);write(B/'review_TWO103_NEW_fudan270_formals_shared_witness_initial_CPU_UNUSED_once.py',s)
 files=[]
 for p in B.glob('*.py'):
  tree=ast.parse(p.read_bytes());entrycode=p.read_text('utf8')
  for node in tree.body:
   if isinstance(node,ast.Assign) and any(isinstance(x,ast.Name) and x.id in ('OWNER','NATIVE','CODE') for x in node.targets):ast.parse(ast.literal_eval(node.value))
  if p.name!=Path(__file__).name:
   assert 'mod4.native99_to_flat20.target100.objective_window.v1' not in entrycode and "['flat_jump_target_m']" not in entrycode and "['stance_reference_revision']" not in entrycode
  files.append(dict(path=str(p),bytes=p.stat().st_size,SHA=H(p)))
 put('FUDAN103_CLOSING_SOURCE_BINDINGS_AND_NO_EXECUTION_ACTUAL.json',dict(epoch=time.time(),prepared_source_only=True,actual_GPU_GO_exists=False,all_outer_and_embedded_remote_AST_passed=True,source_files_from_original_consumed101_only_read_not_executed={k:dict(path=str(v),SHA=H(v)) for k,v in before.items()},bound_run_id=public['run_id'],source_native_SHA=public['experts']['h1']['source_SHA'],new_models_not_read_or_transferred=True,normal900_local_remote_owner850_nodes180_total1140_preserved=True,two_NEW_native_formals_one_each_plus_one_shared_normal86_witness_ONLY_after_complete_actual_closure=True,native_critic_optimizer_20_times_globalPi_not_normal_PPO_rule=True,not_actual_policy_FINAL_cost_or_skill=True))
 with (B/'FROZEN_UNUSED_FIRST_CLOSING_INITIAL_CPU_SOURCE_INDEX_V1.json').open('x',encoding='utf8') as f:json.dump(dict(frozen=True,unused=True,files=files,report=dict(path=str(R/'FUDAN103_CLOSING_SOURCE_BINDINGS_AND_NO_EXECUTION_ACTUAL.json'),SHA=H(R/'FUDAN103_CLOSING_SOURCE_BINDINGS_AND_NO_EXECUTION_ACTUAL.json'))),f,indent=2)
 print(json.dumps(dict(prepared_source_only=True,new103_first_collector_reviewers_frozen=True,no_SDK_model_GPU_remote_or_GO=True)))
if __name__=='__main__':
 try:main()
 except BaseException:put('PREPARER103_CLOSING_SOURCE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_remote_or_model_or_GPU=True));raise
