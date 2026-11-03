"""Final saved-evidence packaging. Reads small/saved files; raw access is stat only."""
from pathlib import Path
import json,hashlib,re,ast
OUT=Path(__file__).resolve().parent
L=json.loads((OUT/'SOURCE_LOCK.json').read_bytes());S=json.loads((OUT/'SUMMARY.json').read_bytes());E=json.loads((OUT/'EXTRACTED.json').read_bytes())
def rec(p):
    p=p.resolve();b=p.read_bytes();return dict(path=str(p),bytes=len(b),SHA=hashlib.sha256(b).hexdigest())
def write(name,obj):
    with(OUT/name).open('x',encoding='utf-8',newline='\n')as f:json.dump(obj,f,ensure_ascii=False,allow_nan=False,separators=(',',':'));f.write('\n')
assert rec(OUT/'METHOD.json')['SHA']==L['method']['SHA']
for z in L['sources']:assert rec(Path(z['path']))['SHA']==z['SHA'],('source changed',z['path'])
rawstat=[]
for z in L['raw']:
    p=Path(z['path']);st=p.stat();assert(st.st_size,st.st_mtime_ns)==(z['bytes'],z['mtime_ns'])
    assert E['raw_opened'].count(str(p))==1 and E['row_counts'][str(p)]==z['maximum_rows']
    rawstat.append(dict(path=str(p),bytes=st.st_size,mtime_ns=st.st_mtime_ns,producer_SHA_not_recomputed=z['producer_SHA_not_recomputed'],analysis_content_opens=1,rows=E['row_counts'][str(p)]))
assert len(E['raw_opened'])==len(set(E['raw_opened']))==5 and E['total_rows']==19200
assert all(not p['mismatch_counts']for p in S['paired_prefix'].values())
facts=dict(kind='R62_TWO_SELECTED_TRAIN_PAIRS_REQUEST_LEVEL_SENSITIVITY_AND_PRIVATE_HARD_EVENT_NOT_UNIQUE_CAUSE',scope=dict(raw_streams=5,raw_rows=19200,raw_passes_per_stream=1,raw_hashes_recomputed=0,controller_replay_QA_physics_compile_Git_agents=0,no_new_gain_or_third_h=True,PH8_pending=True),prefix=S['paired_prefix'],cases={},pair_first_numeric_differences=S['pair_request_differences'])
for c,s in S['cases'].items():
    assert s['flight_request_validation_failures']==0 and s['flight_request_reconstruction_max_error_Nm']<=1e-9 and s['flight_goal_h_target_validation_max_error_rad']<=1e-12
    if s['new_air_ref']:assert s['first_anchor_continuity_error_rad']<=1e-12
    f=dict(first_flight=s['first_flight'],last_flight=s['last_flight'],first_capture=s['first_capture'],flight_rows=s['flight_rows'],observer_resume_s=s['observer_resume_s'],flight_request_validation_max_error_Nm=s['flight_request_reconstruction_max_error_Nm'],h_target_validation_max_error_rad=s['flight_goal_h_target_validation_max_error_rad'],anchor_reference_continuity_error_rad=s['first_anchor_continuity_error_rad'],flight_request_peak_coincidences=s['phase_requests']['predicted_flight_retract'],phase_requests=s['phase_requests'],flight_wheel_mean2=s['flight_wheel_mean2'],capture_first_0p2=s['capture_windows']['first_0p2'],result_unchanged=s['old_result_unchanged_facts'])
    if s['new_air_ref']:
        assert sum(s['effect_nonzero_per_axis'])==100
        f['h_limits']=dict(goal_below_low=s['raw_goal_clipped_low'],goal_above_high=s['raw_goal_clipped_high'],rate_active=s['h_rate_active_rows'],h_at_low=s['h_at_low_rows'],h_at_high=s['h_at_high_rows'])
        f['same_packet_request_masking']=dict(leg_order=['LH','LC','RH','RC'],nonzero_effects=s['effect_nonzero_per_axis'],fully=s['fully_masked_per_axis'],partially=s['partially_masked_per_axis'],transmitted=s['transmitted_per_axis'],all_four_fully_masked_times=s['all_four_legs_fully_masked_command_s'],meaning=s['masking_interpretation'])
    else:f['h_function']='ABSENT_BASELINE_NOT_A_LOGGED_ZERO'
    facts['cases'][c]=f
P=S['new4606_physics'];facts['new4606_physics']=dict(first_qualified_air=P['first_qualified_air'],first_landing_after_qualified_air=P['first_landing_after_qualified_air'],hard_ticks=P['hard_ticks'],guide_ticks=P['guide_ticks'],hard_events=P['hard_events'],window=[{k:r[k]for k in ['sample_index','stage_s','root_post_s','root_pitch_pre','root_roll_pre','hard_normal_N','all_normal_N','control_k','command_s','stage_age_from_request_s','landing_weight','observer_disabled','observer_until_s','actual_bounded_tau6_Nm']}for r in P['first_hard_window']])
facts['unknowns_and_limits']=S['unknowns']
write('FACTS.json',facts)
text=(OUT/'REPORT.md').read_text(encoding='utf-8');lines=len(text.splitlines());assert lines<=100
links=[]
for target in re.findall(r'\]\(<([^>]+)>\)',text):
    p=(OUT/target.split('#',1)[0]).resolve()
    assert p.is_file()or p==OUT/'RECEIPT.json',('missing link',target)
    links.append(dict(target=target,resolved=str(p)))
# Static import inventory of the NEW analysis helpers, not runtime project imports.
imports={}
for name in ['freeze_sources.py','extract_once.py','summarize_saved.py','finalize_saved.py']:
    tree=ast.parse((OUT/name).read_text(encoding='utf-8'));roots=[]
    for n in ast.walk(tree):
        if isinstance(n,ast.Import):roots.extend(a.name.split('.')[0]for a in n.names)
        elif isinstance(n,ast.ImportFrom):roots.append(n.module.split('.')[0])
    assert set(roots)<={'pathlib','json','hashlib','math','struct','traceback','collections','re','ast'}
    imports[name]=sorted(set(roots))
artnames=['REPORT.md','FACTS.json','SUMMARY.json','EXTRACTED.json','METHOD.json','SOURCE_LOCK.json','RAW_PASS_STARTED.json','freeze_sources.py','extract_once.py','summarize_saved.py','finalize_saved.py','freeze_01.log','extract_01.log','saved_summary_01.log']
receipt=dict(status='SEALED_SINGLE_PASS_TWO_TRAIN_REQUEST_ALGEBRA_AND_PRIVATE_EVENT_NOT_UNIQUE_CAUSE_OR_CONTROLLER_QUALIFICATION',report_lines=lines,report=rec(OUT/'REPORT.md'),facts=rec(OUT/'FACTS.json'),small_sources_unchanged=len(L['sources']),selected_manifest_SHA_matches=len(L['selected_manifest_matches']),sources=L['sources'],raw_stat_checks_only=rawstat,raw_total_rows=19200,raw_content_opens_total=5,raw_rehash_or_archive_copies=0,source_method=rec(OUT/'METHOD.json'),links=links,analysis_helper_imports=imports,artifacts=[rec(OUT/n)for n in artnames],execution=dict(structured_raw_extractions=1,saved_only_summary_runs=1,physics_model_forward_integrator_controller_replay_old_QA_compile_Git_agents=0,no_parameter_or_hypothesis_or_gate_changes=True),qualified=False,default_core_002_still_readonly_off=True,PH8_pending=True)
write('RECEIPT.json',receipt)
assert all(Path(z['resolved']).is_file()for z in links)
print(json.dumps(dict(status=receipt['status'],lines=lines,sources_unchanged=len(L['sources']),manifest_matches=len(L['selected_manifest_matches']),raw_rows=19200,raw_opens=5,report=receipt['report'],facts=receipt['facts'],receipt=rec(OUT/'RECEIPT.json')),indent=2))
