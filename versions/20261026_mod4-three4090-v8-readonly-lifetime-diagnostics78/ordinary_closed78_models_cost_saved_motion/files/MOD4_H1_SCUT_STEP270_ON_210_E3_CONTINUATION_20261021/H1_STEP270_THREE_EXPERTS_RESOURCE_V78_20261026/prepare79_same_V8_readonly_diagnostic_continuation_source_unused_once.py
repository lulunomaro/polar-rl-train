"""Source-only preparation. Do not bind or deploy until complete78 models/cost/allout."""
from pathlib import Path
import ast,hashlib,json,time
N=Path(__file__).resolve().parent;T=N.parent;F=T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V79_20261026'
assert not F.exists();F.mkdir();(F/'reports').mkdir();(F/'candidates').mkdir()
made=[]
def put(p,s):
 ast.parse(s)
 with p.open('x',encoding='utf8',newline='\n') as f:f.write(s)
 made.append(dict(path=str(p),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest()))
def once(s,old,new):
 assert s.count(old)==1,old
 return s.replace(old,new,1)
s=(N/'candidates/same_three_closed_source_V8_lifetime_diag_CPU_v1.py').read_text('utf8')
s=s.replace('AUTH_78_ACTUAL.json','AUTH_79_ACTUAL.json').replace('actual_closed_three_V8_lifetime_diagnostic_continuation','actual_closed_three_same_V8_lifetime_diagnostic_continuation')
s=once(s," if key=='h1':allowed|={'h1_production_control_prefix_trace_v1.py','sampling_acceleration_installed_CPU_v2.py'}\n",'')
s=once(s," and not (key=='h1' and name=='h1_lifetime_goal_counter_v1.py')",'')
old="  for name,digest in v8['candidate_files'].items():assert H((old if name in ('h1_production_control_prefix_trace_v1.py','sampling_acceleration_installed_CPU_v2.py') else B)/name)==digest\n"
s=once(s,old,'')
old="  assert H(old/'h1_production_control_prefix_trace_v1.py')==diag['base_trace_SHA'] and H(old/'sampling_acceleration_installed_CPU_v2.py')==diag['base_sampler_checker_SHA']\n"
new="  assert H(B/'H1_READONLY_LIFETIME_DIAGNOSTIC_SOURCE_AUTH_ACTUAL.json')==H(old/'H1_READONLY_LIFETIME_DIAGNOSTIC_SOURCE_AUTH_ACTUAL.json')\n  for name,digest in v8['candidate_files'].items():\n   if name=='h1_production_control_prefix_trace_v1.py':assert digest==diag['base_trace_SHA']\n   elif name=='sampling_acceleration_installed_CPU_v2.py':assert digest==diag['base_sampler_checker_SHA']\n   else:assert H(B/name)==H(old/name)==digest\n  for name,digest in diag['candidate_files'].items():assert H(B/name)==H(old/name)==digest\n  from h1_lifetime_goal_counter_v1 import ORIGINAL_V8_TRACE_SHA\n  assert ORIGINAL_V8_TRACE_SHA==diag['base_trace_SHA']\n"
s=once(s,old,new)
put(F/'candidates/same_three_closed_source_V8_lifetime_diag_CPU_v1.py',s)
put(F/'candidates/same_optimized_source_contract_metadata_candidate_v1.py',(N/'candidates/same_optimized_source_contract_metadata_candidate_v1.py').read_text('utf8'))
s=(N/'bind_complete77_sources_V8_lifetime_diag_unused_once.py').read_text('utf8')
s=s.replace('V77_','V78_').replace('complete77','complete78').replace('latest77','latest78').replace('actual77','actual78').replace('2610v78','2610v79').replace('AUTH_78_ACTUAL.json','AUTH_79_ACTUAL.json').replace('actual_closed_three_V8_lifetime_diagnostic_continuation','actual_closed_three_same_V8_lifetime_diagnostic_continuation')
start=s.index("  if key=='h1':\n   v8=")
end=s.index("  if key=='recovery':",start)
s=s[:start]+"  if key=='h1':\n   diag=read(out/'H1_READONLY_LIFETIME_DIAGNOSTIC_SOURCE_AUTH_ACTUAL.json');assert diag['approved'] and diag['no_reward_actor_command_PPO_physics_or_success_change']\n   for name,digest in diag['candidate_files'].items():assert H(out/name)==digest\n   assert H(out/'h1_step270_path_reward_v1.py')==diag['unchanged_reward_SHA']\n"+s[end:]
put(F/'bind_complete78_sources_same_V8_lifetime_diag_unused_once.py',s)
for source,target in [
 ('e2_target72_same_backend_install_source_v1.py','e2_target72_same_backend_install_source_v1.py'),
 ('deploy_actual_three_experts78_V8_lifetime_diag_original_writer_unused_once.py','deploy_actual_three_experts79_same_V8_lifetime_diag_original_writer_unused_once.py'),
 ('collect_three_experts78_V8_lifetime_diag_first_PPO_finite_unused_once.py','collect_three_experts79_same_V8_lifetime_diag_first_PPO_finite_unused_once.py'),
 ('collect_actual_three78_finals_original_cost_unused_once.py','collect_actual_three79_finals_original_cost_unused_once.py'),
 ('review_three_expert_complete_models_original_cost_CPU_V4_unused_once.py','review_three_expert_complete_models_original_cost_CPU_V4_unused_once.py')]:
 s=(N/source).read_text('utf8').replace('2610v78','2610v79').replace('2610v77','2610v78').replace('V78_','V79_').replace('V77_','V78_').replace('before77','before78').replace('after77','after78').replace('from complete77','from complete78').replace('actual77','actual78').replace('active77','active78')
 put(F/target,s)
with (F/'reports/SOURCE_ONLY79_SAME_V8_LIFETIME_DIAG_CONTINUATION_PREPARED_ACTUAL.json').open('x',encoding='utf8') as f:
 json.dump(dict(epoch=time.time(),source_only=True,created=made,no_payload_Task_controller_model_GO_fee=True,qualified_source_SHA_Adam_None_until_complete78=True,H1_all_trace_counter_checker_reward_bytes_unchanged_from_actual78=True,only_guard_role_auth_and_E3_exact_saved_Adam_assert_may_change=True,previous78_original_auths_exact_bytes_retained=True,not_actual_target_SDK_admission_or_training=True,decision_to_continue_requires_completed78_actual_evidence=True),f,indent=2)
print(json.dumps(dict(source_only79=True,created=len(made),no_payload_Task_GO=True)))
