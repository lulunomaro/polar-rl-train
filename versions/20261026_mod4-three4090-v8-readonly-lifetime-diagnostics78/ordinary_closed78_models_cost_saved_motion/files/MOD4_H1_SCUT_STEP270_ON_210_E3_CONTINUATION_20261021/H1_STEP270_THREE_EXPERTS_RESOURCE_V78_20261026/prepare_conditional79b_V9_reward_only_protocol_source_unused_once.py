"""Conditional source-only V9 alternative. No binding/installation while78 is active."""
from pathlib import Path
import ast,json,time
N=Path(__file__).resolve().parent;T=N.parent;A=T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V79_20261026';F=T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V79B_20261026';M=T/'H1_STEP270_FULL_PATH_CLEARANCE_CARRY_V9_MATH_PREPARATION_20261026'
assert not F.exists();F.mkdir();(F/'reports').mkdir();(F/'candidates').mkdir();made=[]
def put(p,s):
 ast.parse(s)
 with p.open('x',encoding='utf8',newline='\n') as f:f.write(s)
 made.append(str(p))
def once(s,old,new):
 assert s.count(old)==1,old
 return s.replace(old,new,1)
s=(A/'candidates/same_three_closed_source_V8_lifetime_diag_CPU_v1.py').read_text('utf8')
s=s.replace('AUTH_79_ACTUAL.json','AUTH_79B_ACTUAL.json').replace('actual_closed_three_same_V8_lifetime_diagnostic_continuation','actual_closed_three_H1_V9_carry_reward_continuation')
s=once(s," allowed={role}"," allowed={role}\n if key=='h1':allowed|={'h1_step270_path_reward_v1.py','step270_reward_installed_CPU_v1.py'}")
s=once(s,"and not spec.get('reward_migration')","and bool(spec.get('reward_migration'))==(key=='h1')")
s=once(s,"   else:assert H(B/name)==H(old/name)==digest","   else:assert H(old/name)==digest")
s=once(s,"  assert H(old/'h1_step270_path_reward_v1.py')==H(B/'h1_step270_path_reward_v1.py')==diag['unchanged_reward_SHA']","  assert H(old/'h1_step270_path_reward_v1.py')==diag['unchanged_reward_SHA']\n  v9=read(B/'H1_V9_FULL_PATH_CARRY_REWARD_SOURCE_AUTH_ACTUAL.json');assert v9['approved'] and v9['under_existing_H1_step270_repair_authorization']\n  assert set(v9['candidate_files'])=={'h1_step270_path_reward_v1.py','step270_reward_installed_CPU_v1.py'}\n  for name,digest in v9['candidate_files'].items():assert H(B/name)==digest and H(old/name)==v9['prior_files'][name]\n  assert cpu['new_reward_integration_CPU']['actual_installed_V9_carry_SDK_compute_tested']")
s=once(s,"  assert read(B/'job0/TASK.json')['reward_recipe_version']==read(old/'job0/TASK.json')['reward_recipe_version']=='step270_sampled_leg_excess_v8_reward_only'","  assert read(old/'job0/TASK.json')['reward_recipe_version']=='step270_sampled_leg_excess_v8_reward_only'\n  assert read(B/'job0/TASK.json')['reward_recipe_version']=='step270_full_path_clearance_carry_v9_reward_only'")
s=once(s,"  kind='closed_same_backend_production'","  kind='closed_same_backend_reward_migration'")
put(F/'candidates/closed_three_H1_V9_reward_CPU_v1.py',s)
put(F/'candidates/same_optimized_source_contract_metadata_candidate_v1.py',(A/'candidates/same_optimized_source_contract_metadata_candidate_v1.py').read_text('utf8'))
s=(A/'bind_complete78_sources_same_V8_lifetime_diag_unused_once.py').read_text('utf8').replace('2610v79','2610v79b').replace('AUTH_79_ACTUAL.json','AUTH_79B_ACTUAL.json').replace('actual_closed_three_same_V8_lifetime_diagnostic_continuation','actual_closed_three_H1_V9_carry_reward_continuation').replace('candidates/same_three_closed_source_V8_lifetime_diag_CPU_v1.py','candidates/closed_three_H1_V9_reward_CPU_v1.py')
s=once(s,"reward_migration=False,cross_host_qualified_source=False","reward_migration=key=='h1',cross_host_qualified_source=False")
needle="   assert H(out/'h1_step270_path_reward_v1.py')==diag['unchanged_reward_SHA']"
extra="""
   M=T/'H1_STEP270_FULL_PATH_CLEARANCE_CARRY_V9_MATH_PREPARATION_20261026';tested=read(M/'reports/V9_SAVED_ACTUAL_SDK_SOURCE_LOCAL_CPU_AND_EXACT_NEGATIVES_ACTUAL.json');assert tested['passed_local_CPU_with_previously_captured_actual_SDK_source']
   names=('h1_step270_path_reward_v1.py','step270_reward_installed_CPU_v1.py');prior_files={name:H(out/name) for name in names}
   for name in names:
    shutil.copy2(out/name,hist/(name+'.original_bytes.txt'));shutil.copy2(M/'candidate_v1'/name,out/name)
   put(out/'H1_V9_FULL_PATH_CARRY_REWARD_SOURCE_AUTH_ACTUAL.json',dict(epoch=time.time(),approved=True,under_existing_H1_step270_repair_authorization=True,explicit_human_approval_of_exact_formula=False,prior_files=prior_files,candidate_files={name:H(out/name) for name in names},saved_actual_SDK_local_CPU_report_SHA=H(M/'reports/V9_SAVED_ACTUAL_SDK_SOURCE_LOCAL_CPU_AND_EXACT_NEGATIVES_ACTUAL.json'),only_recipe_and_one_clearance_potential_expression=True,no_actor_action_command_physics_success_or_original_event_change=True,V8_sample_excess_gate_tuck_all_retained=True,fresh_actual_payload_SDK_source_CPU_still_required=True))
"""
s=once(s,needle,needle+extra.rstrip())
s=s.replace("reward_recipe_version='step270_sampled_leg_excess_v8_reward_only'","reward_recipe_version='step270_full_path_clearance_carry_v9_reward_only'")
put(F/'bind_complete78_sources_H1_V9_carry_reward_unused_once.py',s)
for source,target in [
 ('e2_target72_same_backend_install_source_v1.py','e2_target72_same_backend_install_source_v1.py'),
 ('deploy_actual_three_experts79_same_V8_lifetime_diag_original_writer_unused_once.py','deploy_actual_three_experts79b_H1_V9_carry_original_writer_unused_once.py'),
 ('collect_three_experts79_same_V8_lifetime_diag_first_PPO_finite_unused_once.py','collect_three_experts79b_H1_V9_carry_first_PPO_finite_unused_once.py'),
 ('collect_actual_three79_finals_original_cost_unused_once.py','collect_actual_three79b_finals_original_cost_unused_once.py'),
 ('review_three_expert_complete_models_original_cost_CPU_V4_unused_once.py','review_three_expert_complete_models_original_cost_CPU_V4_unused_once.py')]:
 s=(A/source).read_text('utf8').replace('2610v79','2610v79b').replace('V79_','V79B_')
 if source.startswith('deploy_'):
  needle="source=(P/'DEPLOYER_REUSED_H1_HELPER_EXACT_SOURCE.py').read_text('utf8');needle=\"assert not s.get('reward_migration') and valid_ready(row,s)\";assert source.count(needle)==1"
  s=once(s,needle,needle+"\n source=source.replace(needle,\"assert s['reward_migration'] and valid_ready(row,s)\",1)")
 if source.startswith(('collect_three_experts','review_three')):s=s.replace('step270_sampled_leg_excess_v8_reward_only','step270_full_path_clearance_carry_v9_reward_only')
 put(F/target,s)
with (F/'reports/CONDITIONAL79B_V9_REWARD_ONLY_PROTOCOL_SOURCE_NOT_INSTALLED_ACTUAL.json').open('x',encoding='utf8') as f:
 json.dump(dict(epoch=time.time(),source_only=True,created=made,no_payload_Task_controller_model_GO_fee=True,selection_requires_actual78_complete_models_normal_original_cost_and_event_diagnostic_review=True,not_selected_or_deployed_yet=True,V9_two_reward_AST_changes_only=True,original_H1_trace_counter_sampler_and_all_physics_actions_unchanged=True,original_controller_valid_ready_reward_migration_kind_retained=True,strict_actual_target_CPU_original_resources_required=True,local_reader_original_error={'name':'target_h1_step270_source_sdk_cpu_review.py','error':'rg os error2, guessed lower-case basename did not exist; actual target_H1_step270_source_sdk_cpu_review_v1.py was found locally','classification':'local source reader naming error; no training failure or remote action'}),f,indent=2)
print(json.dumps(dict(conditional79b_V9_source_only=True,created=len(made),not_selected=True)))
