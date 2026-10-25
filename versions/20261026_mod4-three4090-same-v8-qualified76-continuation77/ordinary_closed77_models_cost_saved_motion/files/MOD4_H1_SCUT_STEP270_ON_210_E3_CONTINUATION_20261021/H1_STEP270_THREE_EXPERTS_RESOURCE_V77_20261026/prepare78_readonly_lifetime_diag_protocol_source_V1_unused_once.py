"""Source-only78 protocol: same V8 training with exact read-only accounting hooks, after77 closure."""
from pathlib import Path
import ast,json,shutil,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports';F=T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V78_20261026'
M=T/'H1_STEP270_LIFETIME_GOAL_ACCOUNTING_DIAGNOSTIC_PREPARATION_20261026'
def put(p,v):
    with Path(p).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def write(p,s):
    ast.parse(s)
    with Path(p).open('x',encoding='utf8') as f:f.write(s)
def patch(s,a,b):
    assert s.count(a)==1,a
    return s.replace(a,b,1)
try:
    local=json.loads((M/'reports/READONLY_LIFETIME_TRACE_SOURCE_V3_CPU_ACTUAL.json').read_bytes());assert local['passed_local_source_CPU_only'] and not F.exists()
    (F/'reports').mkdir(parents=True);(F/'candidates').mkdir()
    guard=(N/'candidates/same_three_closed_source_same_V8_CPU_v1.py').read_text('utf8')
    guard=patch(guard,'THREE_EXPERT_SAME_V8_CONTINUATION_AUTH_77_ACTUAL.json','THREE_EXPERT_V8_LIFETIME_DIAG_CONTINUATION_AUTH_78_ACTUAL.json')
    guard=patch(guard,"auth['kind']=='actual_closed_three_same_V8_continuation'","auth['kind']=='actual_closed_three_V8_lifetime_diagnostic_continuation'")
    guard=patch(guard," allowed={role}\n if key=='recovery'", " allowed={role}\n if key=='h1':allowed|={'h1_production_control_prefix_trace_v1.py','sampling_acceleration_installed_CPU_v2.py'}\n if key=='recovery'")
    guard=patch(guard," assert not {name for name in after if name.endswith('.py') and name not in before}"," assert not {name for name in after if name.endswith('.py') and name not in before and not (key=='h1' and name=='h1_lifetime_goal_counter_v1.py')}")
    guard=patch(guard,"  for name,digest in v8['candidate_files'].items():assert H(B/name)==digest", "  for name,digest in v8['candidate_files'].items():assert H((old if name in ('h1_production_control_prefix_trace_v1.py','sampling_acceleration_installed_CPU_v2.py') else B)/name)==digest\n  diag=read(B/'H1_READONLY_LIFETIME_DIAGNOSTIC_SOURCE_AUTH_ACTUAL.json');assert diag['approved'] and diag['no_reward_actor_command_PPO_physics_or_success_change']\n  assert set(diag['candidate_files'])=={'h1_production_control_prefix_trace_v1.py','sampling_acceleration_installed_CPU_v2.py','h1_lifetime_goal_counter_v1.py'}\n  for name,digest in diag['candidate_files'].items():assert H(B/name)==digest\n  assert H(old/'h1_production_control_prefix_trace_v1.py')==diag['base_trace_SHA'] and H(old/'sampling_acceleration_installed_CPU_v2.py')==diag['base_sampler_checker_SHA']\n  assert H(old/'h1_step270_path_reward_v1.py')==H(B/'h1_step270_path_reward_v1.py')==diag['unchanged_reward_SHA']")
    guard=patch(guard,"  kind='closed_same_backend_production'","  assert cpu['sampling_acceleration_CPU']['lifetime_goal_diagnostic_CPU']['passed']\n  kind='closed_same_backend_production'")
    write(F/'candidates/same_three_closed_source_V8_lifetime_diag_CPU_v1.py',guard)
    shutil.copy2(N/'candidates/same_optimized_source_contract_metadata_candidate_v1.py',F/'candidates/same_optimized_source_contract_metadata_candidate_v1.py')
    s=(N/'bind_complete76_sources_same_V8_unused_once.py').read_text('utf8').replace('H1_STEP270_THREE_EXPERTS_RESOURCE_V76_20261026','H1_STEP270_THREE_EXPERTS_RESOURCE_V77_20261026').replace('2610v77','2610v78').replace('latest76_original_cost_closure','latest77_original_cost_closure').replace('actual76_original_models_cost_allout','actual77_original_models_cost_allout').replace('actual_closed76_report_SHA','actual_closed77_report_SHA').replace('bound_actual76_sources','bound_actual77_sources').replace('before actual76','before actual77')
    s=s.replace('same_three_closed_source_same_V8_CPU_v1.py','same_three_closed_source_V8_lifetime_diag_CPU_v1.py').replace('THREE_EXPERT_SAME_V8_CONTINUATION_AUTH_77_ACTUAL.json','THREE_EXPERT_V8_LIFETIME_DIAG_CONTINUATION_AUTH_78_ACTUAL.json').replace("kind='actual_closed_three_same_V8_continuation'","kind='actual_closed_three_V8_lifetime_diagnostic_continuation'").replace('same_V8_reward_and_trace_retained=True','same_V8_reward_and_original_trace_semantics_retained=True')
    anchor="   for name,digest in v8['candidate_files'].items():assert H(out/name)==digest"
    addition="\n   M=T/'H1_STEP270_LIFETIME_GOAL_ACCOUNTING_DIAGNOSTIC_PREPARATION_20261026';checked=read(M/'reports/READONLY_LIFETIME_TRACE_SOURCE_V3_CPU_ACTUAL.json');assert checked['passed_local_source_CPU_only']\n   base_trace=H(out/'h1_production_control_prefix_trace_v1.py');base_sampler=H(out/'sampling_acceleration_installed_CPU_v2.py')\n   names=('h1_production_control_prefix_trace_v1.py','sampling_acceleration_installed_CPU_v2.py','h1_lifetime_goal_counter_v1.py')\n   for name in names:\n    if (out/name).exists():shutil.copy2(out/name,hist/(name+'.original_bytes.txt'))\n    shutil.copy2(M/'candidate_v3'/name,out/name)\n   put(out/'H1_READONLY_LIFETIME_DIAGNOSTIC_SOURCE_AUTH_ACTUAL.json',dict(epoch=time.time(),approved=True,under_existing_H1_repair_readonly_evidence_scope=True,explicit_human_approval_of_exact_hook=False,base_trace_SHA=base_trace,base_sampler_checker_SHA=base_sampler,unchanged_reward_SHA=H(out/'h1_step270_path_reward_v1.py'),candidate_files={name:H(out/name) for name in names},local_CPU_report_SHA=H(M/'reports/READONLY_LIFETIME_TRACE_SOURCE_V3_CPU_ACTUAL.json'),no_reward_actor_command_PPO_physics_or_success_change=True,actual_installed_SDK_source_CPU_still_required=True,not_frozen_evaluation_or_new_task_authorization=True))"
    s=patch(s,anchor,anchor+addition)
    write(F/'bind_complete77_sources_V8_lifetime_diag_unused_once.py',s)
    s=(N/'deploy_actual_three_experts77_same_V8_original_writer_unused_once.py').read_text('utf8').replace('H1_STEP270_THREE_EXPERTS_RESOURCE_V77_20261026','H1_STEP270_THREE_EXPERTS_RESOURCE_V78_20261026').replace('H1_STEP270_THREE_EXPERTS_RESOURCE_V76_20261026','H1_STEP270_THREE_EXPERTS_RESOURCE_V77_20261026').replace('after76 closes','after77 closes').replace('no_active76_hotpatch','no_active77_hotpatch')
    write(F/'deploy_actual_three_experts78_V8_lifetime_diag_original_writer_unused_once.py',s)
    s=(N/'e2_target72_same_backend_install_source_v1.py').read_text('utf8').replace('2610v77','2610v78').replace('2610v76','2610v77').replace('complete76','complete77');write(F/'e2_target72_same_backend_install_source_v1.py',s)
    s=(N/'collect_three_experts77_same_V8_first_PPO_finite_unused_once.py').read_text('utf8').replace('H1_STEP270_THREE_EXPERTS_RESOURCE_V77_20261026','H1_STEP270_THREE_EXPERTS_RESOURCE_V78_20261026')
    anchor="task=json.loads((H/'job0/TASK.json').read_bytes());assert task['reward_recipe_version']=='step270_sampled_leg_excess_v8_reward_only'"
    addition="\ndiag_path=H/'job0/production/control_prefix_raw/CONTROL_LIFETIME_GOAL_EVENTS_ACTUAL.json'\ntry:diag=dict(present=diag_path.is_file(),value=json.loads(diag_path.read_bytes()) if diag_path.is_file() else None)\nexcept (OSError,ValueError) as error:diag=dict(present=False,read_error=type(error).__name__+': '+str(error),not_a_training_failure=True)"
    s=patch(s,anchor,anchor+addition)
    s=patch(s,'V8_runtime_term_present_in_original_trace_index=True,','V8_runtime_term_present_in_original_trace_index=True,lifetime_goal_diagnostic_first_snapshot=diag,')
    write(F/'collect_three_experts78_V8_lifetime_diag_first_PPO_finite_unused_once.py',s)
    s=(N/'collect_actual_three77_finals_original_cost_unused_once.py').read_text('utf8').replace('H1_STEP270_THREE_EXPERTS_RESOURCE_V77_20261026','H1_STEP270_THREE_EXPERTS_RESOURCE_V78_20261026');write(F/'collect_actual_three78_finals_original_cost_unused_once.py',s)
    s=(N/'review_three_expert_complete_models_original_cost_CPU_V3_unused_once.py').read_text('utf8')
    anchor='    assert not torch.cuda.is_initialized()'
    addition="    diagpath=N/'current_three_closed_text/h1/job0/production/control_prefix_raw/CONTROL_LIFETIME_GOAL_EVENTS_ACTUAL.json'\n    diagnostic=dict(present=diagpath.is_file(),expected_complete_control_rows=models['h1']['updates']*24,not_a_model_training_or_skill_gate=True)\n    if diagpath.is_file():\n        try:\n            value=read(diagpath);diagnostic['value']=value;diagnostic['complete_closed_window_accounting_valid']=(value.get('schema')=='completed_control_goal_events_v1' and value.get('diagnostic_valid') is True and value.get('complete_control_rows')==models['h1']['updates']*24 and value.get('environment_control_transitions')==models['h1']['updates']*24*20000)\n        except (OSError,ValueError) as error:diagnostic.update(complete_closed_window_accounting_valid=False,read_error=str(error))\n    models['h1']['lifetime_goal_event_diagnostic']=diagnostic\n"
    s=patch(s,anchor,addition+anchor);write(F/'review_three_expert_complete_models_original_cost_CPU_V4_unused_once.py',s)
    put(F/'reports/SOURCE_ONLY78_READONLY_LIFETIME_DIAG_PROTOCOL_ACTUAL.json',{'epoch':time.time(),'source_only':True,'source_SHA_Adam_None_until_complete77':True,'no_payload_Task_controller_model_GO_or_fee':True,'same_V8_reward_and_physics':True,'only_H1_trace_sampler_checker_and_one_exact_counter_module_admitted':True,'original_approvals_retained_new_separate_auth':True,'local_counter_source_CPU_V3_passed_actual_target_CPU_still_required':True,'counter_output_is_diagnostic_not_frozen_skill_or_new_training_gate':True})
    print(json.dumps({'source_only78_protocol_ready':True,'no_payload_or_GO':True,'counter_candidate_version':3}))
except BaseException:
    put(R/('SOURCE_ONLY78_PROTOCOL_V1_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),{'epoch':time.time(),'error':traceback.format_exc(),'no_same_once_retry_or_remote_training_change':True});raise
