"""Unbound77 same-V8 and fresh76 saved diagnostics; no model/remote/GPU action."""
from pathlib import Path
import ast,json,shutil,time,traceback
P=Path(__file__).resolve().parent;T=P.parent;R=P/'reports'
F=T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V77_20261026';U=T/'H1_STEP270_CLOSED76_SAVED_REPLAY_AFTER_V8_20261026'
oldU=T/'H1_STEP270_CLOSED75_SAVED_REPLAY_AFTER_V8_20261026'
def put(p,v):
    with Path(p).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def write(p,s):
    ast.parse(s)
    with Path(p).open('x',encoding='utf8') as f:f.write(s)
def patch(s,a,b):
    assert s.count(a)==1,a
    return s.replace(a,b,1)
def main():
    first=json.loads((R/'THREE_EXPERT_ACTUAL_GO_POSITIVE_PPO_UUID_CREATE_ARGV_VERIFIED_ACTUAL.json').read_bytes())
    assert first['passed'] and first['actual_finite_returned'] and not F.exists() and not U.exists()
    (F/'reports').mkdir(parents=True);(F/'candidates').mkdir();(U/'reports').mkdir(parents=True)
    before=(P/'candidates/same_three_closed_source_same_V8_CPU_v1.py').read_text('utf8')
    guard=patch(before,'THREE_EXPERT_SAME_V8_CONTINUATION_AUTH_76_ACTUAL.json','THREE_EXPERT_SAME_V8_CONTINUATION_AUTH_77_ACTUAL.json')
    write(F/'candidates/same_three_closed_source_same_V8_CPU_v1.py',guard)
    assert guard.replace('AUTH_77_ACTUAL','AUTH_76_ACTUAL')==before
    shutil.copy2(P/'candidates/same_optimized_source_contract_metadata_candidate_v1.py',F/'candidates/same_optimized_source_contract_metadata_candidate_v1.py')
    s=(P/'bind_complete75_sources_same_V8_unused_once.py').read_text('utf8').replace('H1_STEP270_THREE_EXPERTS_RESOURCE_V75_20261026','H1_STEP270_THREE_EXPERTS_RESOURCE_V76_20261026').replace('2610v76','2610v77').replace('AUTH_76_ACTUAL','AUTH_77_ACTUAL').replace('latest75_original_cost_closure','latest76_original_cost_closure').replace('actual75_original_models_cost_allout','actual76_original_models_cost_allout').replace('actual_closed75_report_SHA','actual_closed76_report_SHA').replace('bound_actual75_sources','bound_actual76_sources').replace('before actual75','before actual76')
    write(F/'bind_complete76_sources_same_V8_unused_once.py',s)
    s=(P/'deploy_actual_three_experts76_same_V8_original_writer_unused_once.py').read_text('utf8').replace('H1_STEP270_THREE_EXPERTS_RESOURCE_V76_20261026','H1_STEP270_THREE_EXPERTS_RESOURCE_V77_20261026').replace('H1_STEP270_THREE_EXPERTS_RESOURCE_V75_20261026','H1_STEP270_THREE_EXPERTS_RESOURCE_V76_20261026').replace('after75 closes','after76 closes').replace('no_active75_hotpatch','no_active76_hotpatch')
    a='needle="assert s[\'reward_migration\'] and valid_ready(row,s)";assert source.count(needle)==1;source=source.replace(needle,"assert not s.get(\'reward_migration\') and valid_ready(row,s)",1)'
    b='needle="assert not s.get(\'reward_migration\') and valid_ready(row,s)";assert source.count(needle)==1'
    s=patch(s,a,b);write(F/'deploy_actual_three_experts77_same_V8_original_writer_unused_once.py',s)
    s=(P/'e2_target72_same_backend_install_source_v1.py').read_text('utf8').replace('2610v76','2610v77').replace('2610v75','2610v76').replace('complete75','complete76')
    write(F/'e2_target72_same_backend_install_source_v1.py',s)
    for old,new in [('collect_three_experts76_same_V8_first_PPO_finite_unused_once.py','collect_three_experts77_same_V8_first_PPO_finite_unused_once.py'),('collect_actual_three76_finals_original_cost_unused_once.py','collect_actual_three77_finals_original_cost_unused_once.py'),('review_three_expert_complete_models_original_cost_CPU_V3_unused_once.py','review_three_expert_complete_models_original_cost_CPU_V3_unused_once.py')]:
        s=(P/old).read_text('utf8').replace('H1_STEP270_THREE_EXPERTS_RESOURCE_V76_20261026','H1_STEP270_THREE_EXPERTS_RESOURCE_V77_20261026');write(F/new,s)
    for old,new in [('extract_closed75_last_two_saved_prefixes_CPU_unused_once.py','extract_closed76_last_two_saved_prefixes_CPU_unused_once.py'),('reconstruct_closed75_saved_motion_USD_CPU_unused_once.py','reconstruct_closed76_saved_motion_USD_CPU_unused_once.py'),('analyze_render_closed75_saved_step_timing_CPU_unused_once.py','analyze_render_closed76_saved_step_timing_CPU_unused_once.py'),('analyze_closed75_sampled_excess_selected_CPU_unused_once.py','analyze_closed76_sampled_excess_selected_CPU_unused_once.py')]:
        s=(oldU/old).read_text('utf8').replace('H1_STEP270_THREE_EXPERTS_RESOURCE_V75_20261026','H1_STEP270_THREE_EXPERTS_RESOURCE_V76_20261026').replace('H1_STEP270_CLOSED75_SAVED_ONLY_20261026','H1_STEP270_CLOSED76_SAVED_ONLY_20261026').replace('2610v75','2610v76').replace('CLOSED75','CLOSED76').replace('Closed75','Closed76').replace('closed75','closed76').replace('Unused75','Unused76').replace('New75','New76').replace('new75','new76').replace('complete75','complete76')
        write(U/new,s)
    s=(P/'analyze_saved75_leading_edge_vs_complete_footprint_CPU_unused_once.py').read_text('utf8').replace("U=T/'H1_STEP270_CLOSED75_SAVED_REPLAY_AFTER_V8_20261026'","U=N").replace('CLOSED75','CLOSED76').replace('SAVED75','SAVED76').replace('small75 arrays','small76 arrays')
    write(U/'analyze_saved76_leading_edge_vs_complete_footprint_CPU_unused_once.py',s)
    previous=T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V75_20261026'
    s=(previous/'read_closed75_saved_text_throughput_and_health_unused_once.py').read_text('utf8').replace('closed75','closed76').replace('Closed75','Closed76').replace('CLOSED75','CLOSED76').replace('current75','current76').replace('original75','original76')
    write(P/'read_closed76_saved_text_throughput_and_health_unused_once.py',s)
    s=(previous/'read_closed75_other_expert_task_metrics_text_CPU_unused_once.py').read_text('utf8').replace('Closed75','Closed76').replace('CLOSED75','CLOSED76').replace('New75','New76')
    s=patch(s,"for key in ('e2','recovery'):","for key in ('h1','e2','recovery'):")
    s=patch(s,'Episode_Reward/e3_upright_peak_and_recovery','Episode_Reward/(?:e3_upright_peak_and_recovery|h1_[^:]+)')
    s=s.replace('not_E3_fall_recovery_success_or_E2_directional_full_course_acceptance','not_H1_jump_E3_recovery_or_E2_full_course_acceptance')
    write(P/'read_closed76_three_expert_task_metrics_text_CPU_unused_once.py',s)
    wrapper=T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v119.py'
    s=wrapper.with_name('same_authorized_session_compressed_transport_v118.py').read_text('utf8');anchor="        'collect_actual_three76_finals_original_cost_unused_once.py',"
    names=['extract_closed76_last_two_saved_prefixes_CPU_unused_once.py','deploy_actual_three_experts77_same_V8_original_writer_unused_once.py','collect_three_experts77_same_V8_first_PPO_finite_unused_once.py','collect_actual_three77_finals_original_cost_unused_once.py']
    s=patch(s,anchor,anchor+'\n'+''.join('        '+repr(n)+',\n' for n in names).rstrip('\n'));write(wrapper,s)
    put(F/'reports/SOURCE_ONLY77_SAME_V8_UNBOUND_PROTOCOL_ACTUAL.json',{'epoch':time.time(),'source_only':True,'source_SHA_Adam_None_until_complete76':True,'no_payload_Task_controller_model_GO_or_fee':True,'strict_guard_exact76_except_new77_auth_filename':True,'previous76_helper_not_rewritten_again':True,'E2_exact77_and76_owned_namespace_updates_only':True,'fresh_full_installed_SDK_CPU_source_and_original_resources_still_required':True,'transport119_exact_new_basenames':names})
    put(U/'reports/SOURCE_ONLY76_NEW_SAVED_DATA_DIAGNOSTICS_PROTOCOL_ACTUAL.json',{'epoch':time.time(),'source_only':True,'wait_complete76_CPU_original_cost_allout':True,'last_two_actual_retained_prefixes_only':True,'V8_selected_scalar_check_and_original_complete_footprint_geometry_descriptive_only':True,'no_new_training_gate_policy_physics_GPU_or_old_raw_reexecution':True})
    print(json.dumps({'source_only77_prepared':True,'new76_saved_diagnostics_prepared':True,'new_transport119':str(wrapper),'no_payload_or_GO':True}))
if __name__=='__main__':
    try:main()
    except BaseException:
        put(R/('SOURCE_ONLY77_PREPARATION_V2_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),{'epoch':time.time(),'error':traceback.format_exc(),'no_same_once_retry_or_remote_action':True});raise
