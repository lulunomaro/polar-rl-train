"""Source-only80: same V8 plus optional landing trajectories from existing copied CPU rows."""
from pathlib import Path
import ast,json,shutil,time
N=Path(__file__).resolve().parent;T=N.parent;F=T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V80_20261026';A=T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V79_20261026';M=T/'H1_STEP270_READONLY_LANDING_JOURNAL_PREPARATION_20261026'
assert not F.exists();F.mkdir();(F/'reports').mkdir();(F/'candidates').mkdir();made=[]
def put(p,s):
 ast.parse(s)
 with p.open('x',encoding='utf8',newline='\n') as f:f.write(s)
 made.append(str(p))
def once(s,a,b):
 assert s.count(a)==1,a
 return s.replace(a,b,1)
shutil.copy2(N/'payloads/h1/same_optimized_source_contract_metadata_candidate_v1.py',F/'candidates/same_optimized_source_contract_metadata_candidate_v1.py')
s=(N/'candidates/same_three_closed_source_V8_lifetime_diag_CPU_v1.py').read_text('utf8').replace('AUTH_79C_ACTUAL.json','AUTH_80_ACTUAL.json').replace('actual_closed_three_same_V8_lifetime_diagnostic_continuation','actual_closed_three_V8_landing_journal_continuation')
s=once(s,' allowed={role}'," allowed={role}\n if key=='h1':allowed|={'h1_lifetime_goal_counter_v1.py','sampling_acceleration_installed_CPU_v2.py'}")
s=once(s,"  for name,digest in diag['candidate_files'].items():assert H(B/name)==digest", "  for name,digest in diag['candidate_files'].items():assert H(old/name)==digest")
s=once(s,"  for name,digest in diag['candidate_files'].items():assert H(B/name)==H(old/name)==digest", "  for name,digest in diag['candidate_files'].items():\n   if name=='h1_production_control_prefix_trace_v1.py':assert H(B/name)==H(old/name)==digest\n  journal=read(B/'H1_READONLY_LANDING_JOURNAL_SOURCE_AUTH_ACTUAL.json');assert journal['approved'] and journal['no_reward_actor_command_physics_or_success_change']\n  assert H(old/'h1_lifetime_goal_counter_v1.py')==journal['base_counter_SHA'] and H(old/'sampling_acceleration_installed_CPU_v2.py')==journal['base_sampler_SHA']\n  assert set(journal['candidate_files'])=={'h1_lifetime_goal_counter_v1.py','sampling_acceleration_installed_CPU_v2.py','reference_sources/actual79c_counter_original_bytes.txt'}\n  for name,digest in journal['candidate_files'].items():assert H(B/name)==digest\n  assert H(B/'reference_sources/actual79c_counter_original_bytes.txt')==journal['base_counter_SHA']\n  assert cpu['sampling_acceleration_CPU']['landing_event_journal_CPU']['passed']")
put(F/'candidates/closed_three_V8_landing_journal_source_CPU_v1.py',s)
s=(N/'bind_complete78_sources_same_V8_exact_metadata_unused_once.py').read_text('utf8').replace('V78_','V79C_').replace('2610v79c','2610v80').replace('latest78','latest79c').replace('actual78','actual79c').replace('AUTH_79C_ACTUAL.json','AUTH_80_ACTUAL.json').replace('actual_closed77_report_SHA','actual_closed79c_report_SHA').replace('actual_closed_three_same_V8_lifetime_diagnostic_continuation','actual_closed_three_V8_landing_journal_continuation').replace('candidates/same_three_closed_source_V8_lifetime_diag_CPU_v1.py','candidates/closed_three_V8_landing_journal_source_CPU_v1.py')
needle="   assert H(out/'h1_step270_path_reward_v1.py')==diag['unchanged_reward_SHA']"
extra="""
   M=T/'H1_STEP270_READONLY_LANDING_JOURNAL_PREPARATION_20261026';tested=read(M/'reports/READONLY_LANDING_JOURNAL_CANDIDATE_V1_CPU_ACTUAL.json');assert tested['passed_local_CPU_source_only']
   names=('h1_lifetime_goal_counter_v1.py','sampling_acceleration_installed_CPU_v2.py','reference_sources/actual79c_counter_original_bytes.txt');base_counter=H(out/names[0]);base_sampler=H(out/names[1])
   for name in names:
    if (out/name).exists():shutil.copy2(out/name,hist/(Path(name).name+'.original_bytes.txt'))
    (out/name).parent.mkdir(parents=True,exist_ok=True);shutil.copy2(M/'candidate_v1'/name,out/name)
   put(out/'H1_READONLY_LANDING_JOURNAL_SOURCE_AUTH_ACTUAL.json',dict(epoch=time.time(),approved=True,under_existing_H1_repair_and_saved_control_evidence_scope=True,explicit_human_approval_of_exact_journal_parameters=False,base_counter_SHA=base_counter,base_sampler_SHA=base_sampler,candidate_files={name:H(out/name) for name in names},local_CPU_report_SHA=H(M/'reports/READONLY_LANDING_JOURNAL_CANDIDATE_V1_CPU_ACTUAL.json'),pre_controls=16,post_controls=64,case_cap=64,only_existing_copied_CPU_arrays=True,no_reward_actor_command_physics_or_success_change=True,optional_diagnostic_errors_not_training_gate=True,actual_new_payload_target_SDK_source_CPU_still_required=True))
"""
s=once(s,needle,needle+extra.rstrip());put(F/'bind_complete79c_sources_V8_readonly_landing_journal_unused_once.py',s)
for source,target in [
 ('e2_target72_same_backend_install_source_v1.py','e2_target72_same_backend_install_source_v1.py'),
 ('collect_three_experts79c_same_V8_lifetime_diag_first_PPO_finite_unused_once.py','collect_three_experts80_readonly_landing_journal_first_PPO_finite_unused_once.py'),
 ('collect_actual_three79c_finals_original_cost_unused_once.py','collect_actual_three80_finals_original_cost_unused_once.py'),
 ('review_three_expert_complete_models_original_cost_CPU_V4_unused_once.py','review_three_expert_complete_models_original_cost_CPU_V5_unused_once.py')]:
 s=(N/source).read_text('utf8').replace('V79C_','V80_').replace('2610v79c','2610v80').replace('2610v78','2610v79c').replace('from complete78','from complete79c')
 if source.startswith('collect_three_experts'):
  needle="compute=subprocess.check_output(['nvidia-smi'";assert s.count(needle)==2
  add="journal_path=H/'job0/production/control_prefix_raw/CONTROL_LANDING_EVENT_JOURNAL_ACTUAL.json'\ntry:journal=dict(present=journal_path.is_file(),value=json.loads(journal_path.read_bytes()) if journal_path.is_file() else None)\nexcept (OSError,ValueError) as error:journal=dict(present=False,read_error=type(error).__name__+': '+str(error),not_a_training_failure=True)\n"
  s=s.replace(needle,add+needle,1).replace('lifetime_goal_diagnostic_first_snapshot=diag,','lifetime_goal_diagnostic_first_snapshot=diag,landing_event_journal_first_snapshot=journal,',1)
 if source.startswith('review_'):
  needle="    assert not torch.cuda.is_initialized()"
  add="    jp=N/'current_three_closed_text/h1/job0/production/control_prefix_raw/CONTROL_LANDING_EVENT_JOURNAL_ACTUAL.json'\n    jd=dict(present=jp.is_file(),not_a_model_or_skill_gate=True)\n    if jp.is_file():\n        try:\n            jv=read(jp);jd.update(value=jv,complete_control_row_coverage_valid=jv.get('diagnostic_valid') is True and jv.get('completed_control_rows_seen')==models['h1']['updates']*24)\n        except (OSError,ValueError) as error:jd.update(read_error=str(error),complete_control_row_coverage_valid=False)\n    models['h1']['landing_event_journal_diagnostic']=jd\n"
  assert s.count(needle)==1;s=s.replace(needle,add+needle,1)
 put(F/target,s)
# Reuse the already reviewed standard wrapper, without replaying79 preGO partial inspection.
s=(A/'deploy_actual_three_experts79_same_V8_lifetime_diag_original_writer_unused_once.py').read_text('utf8').replace('V79_','V80_').replace('V78_','V79C_').replace('actual79','actual80').replace('active78','active79c')
put(F/'deploy_actual_three_experts80_V8_readonly_landing_journal_original_writer_unused_once.py',s)
with (F/'reports/SOURCE_ONLY80_READONLY_LANDING_JOURNAL_PROTOCOL_PREPARED_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),source_only=True,created=made,source_SHA_Adam_and_closing_None_until_complete79c=True,no_payload_Task_controller_model_GO_fee=True,metadata_helper_raw_bytes_inherited_from_actual79c=True,only_H1_counter_sampler_and_exact_oldcounter_reference_changed=True,original_trace_reward_action_PPO_physics_and_success_unchanged=True,new_journal_optional_not_a_model_or_success_gate=True,actual_new_payload_SDK_source_resources_and_original_valid_ready_required=True,old79_and79b_once_not_reused=True),f,indent=2)
print(json.dumps(dict(source_only80_journal_protocol=True,created=len(made),no_GO=True)))
