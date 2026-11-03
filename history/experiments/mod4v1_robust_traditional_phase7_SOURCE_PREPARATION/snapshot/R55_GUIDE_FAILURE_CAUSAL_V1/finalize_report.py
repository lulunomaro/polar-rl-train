"""Finalize saved events only. No raw content, simulator, gain fitting or tests."""
from pathlib import Path
import hashlib,json,re
from urllib.parse import unquote
D=Path(__file__).resolve().parent;R=D.parent
load=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,v):
    with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(v,f,separators=(',',':'),allow_nan=False);f.write('\n')
m=load(D/'METHOD.json');lock=load(D/'SOURCE_LOCK.json');v=load(D/'EVENTS.json')
assert sha(D/'METHOD.json')==lock['method_SHA']==v['method_SHA']
assert sha(D/'SOURCE_LOCK.json')==v['source_lock_SHA'] and sha(D/'extract_events.py')==v['extractor_SHA']
assert len(v['raw_content_opens'])==len(set(v['raw_content_opens']))==4 and set(v['raw_content_opens'])==set(m['raw_paths'])
for s in lock['small']:
    p=R/s['path'];assert p.stat().st_size==s['bytes']and sha(p)==s['SHA'],('source changed',s['path'])
for c in lock['cases']:
    for r in c['raw']:
        st=(R/r['path']).stat();assert st.st_size==r['bytes']and st.st_mtime_ns==r['mtime_ns']
out=[]
for c in v['cases']:
    by={r['index']:r for r in c['control_neighbours']};keys=set()
    for tag in ('first_landing','guide_first'):
        j=c['events'][tag]['control_index'];keys.update(k for k in (j-1,j,j+1)if k in by)
    control=[]
    for j in sorted(keys):
        r=by[j];p=r['phase']
        control.append(dict(index=j,command_s=r['command_time_s'],control_post_s=r['control_post_time_s'],
            phase=p['phase'],landing_ref4=p['landing_position_ref4'],V1_legacy_target_q4=p['target_q4'],
            K_ff_eq_weight=p['landing_transition_weight'],wheel_observer_disabled_predicted=p['wheel_measurement_disabled_predicted'],
            sensor_end_label_s=r['sensor_end_label_s'],sensor_age_s=r['sensor_age_s'],estimated_pitch=r['estimated14'][2],
            estimated_vx=r['estimated14'][7],true_before_pitch=r['true_before']['pitch'],true_after_pitch=r['true_after']['pitch'],
            requested6=r['requested_tau6'],last_substep_stage_s=r['last_substep_stage_time_s'],last_substep_ctrl6=r['last_substep_bounded_ctrl6']))
    ev={}
    for tag,e in c['events'].items():
        if e is None:ev[tag]=None;continue
        ev[tag]=dict(stage_s=e['stage_time_s'],post_s=e['root_post_time_s'],root_PRE_xyz_m=e['root_PRE_xyz_m'],
            root_PRE_rotation_world_from_body33=e['root_PRE_world_from_body33'],root_PRE_rpy=e['root_PRE_rpy'],
            phase=e['phase'],control_index=e['control_index'],K_ff_eq_weight=e['landing_K_ff_eq_weight'],
            request_age_to_drive_stage_s=e['request_to_drive_stage_age_s'],main_N2=e['main_normal_N2'],guide_N=e['guide_normal_N'],
            hard_N=e['hard_normal_N'],total_N=e['total_environment_normal_N'],air_run_s=e['air_run_s'],
            positive_contacts=[{k:p[k]for k in ('robot_geom','environment_geom','normal_N','position_world_m')}for p in e['positive_contacts']],
            bounded_ctrl6_Nm=e['bounded_ctrl6_Nm'],main_rear_x_m=e['private_bounds']['exact_main_rear_x_m'],actual_active_q4_2k=None)
    assert c['guide_ticks']==m['recorded_guide_ticks_preserved'][c['case']] and not c['original_pass']
    out.append(dict(case=c['case'],original_pass=c['original_pass'],guide_ticks=c['guide_ticks'],
        first_bar=c['first_bar'],first_bar_individual_gt1N_ticks=c['first_bar_individual_gt1N_ticks'],
        first_air_start_s=c['first_air_run_start_stage_s'],air_confirm_POST_s=c['first_air_confirmation_post_s'],
        original_first_flight_main_rear_crossing_s=c['original_first_flight_main_rear_crossing_s'],
        events=ev,guide_episodes=c['guide_episodes'],timed_control_transitions=c['control_transitions'],
        landing_guide_neighbour_controls=control,DR_metadata_context_only=c['DR_metadata_context_only']))
summary=dict(kind='SMALL_PRIVATE_EVENT_SUMMARY_NOT_UNIQUE_CAUSE_NOT_NEW_SCORE_OR_CONTROL_PERMISSION',
    detailed_events_SHA=sha(D/'EVENTS.json'),time_semantics='PRE rotation/root/contact/drive share stage; POST separate; 100Hz command and later last-substep ctrl distinct',
    cases=out,unknown=m['unknowns'],single_pass_each_raw=True,PH7_pending=True,outside_current_PH6_cutoff=True)
put(D/'SUMMARY.json',summary)
text=(D/'REPORT.md').read_text(encoding='utf-8');n=len(text.splitlines());assert n<=m['report_max_lines']
links=re.findall(r'\]\(<([^>]+)>\)',text)
for target in links:
    name,_,frag=unquote(target).partition('#');p=Path(name);assert p.is_absolute()
    if p==D/'RECEIPT.json':continue
    assert p.is_file(),('bad link',name)
    if frag:
        r=re.fullmatch(r'L(\d+)(?:-L(\d+))?',frag);assert r
        lo=int(r[1]);hi=int(r[2]or r[1]);assert 1<=lo<=hi<=len(p.read_text(encoding='utf-8').splitlines())
files=['METHOD.json','SOURCE_LOCK.json','REPORT.md','SUMMARY.json','EVENTS.json','freeze_sources.py','extract_events.py',
       'inspect_saved.py','finalize_report.py','freeze_01.log','extract_01.log','saved_facts.log']
r=dict(status='SEALED_TWO_TRAIN_SINGLE_PASS_PRIVATE_EVENT_ANALYSIS_NOT_UNIQUE_CAUSE_OR_CONTROL_QUALIFICATION',
    report_lines=n,verified_report_links=len(links),small_inputs_unchanged=len(lock['small']),producer_manifest_matches=len(lock['actual_manifest_matches']),
    raw_paths=v['raw_content_opens'],content_passes_per_file=1,trace_rows_per_case=[c['trace_rows']for c in v['cases']],
    physics_rows_per_case=[c['physics_rows']for c in v['cases']],total_rows=33600,original_guide_ticks_preserved=[c['guide_ticks']for c in v['cases']],
    original_passes_preserved=[c['original_pass']for c in v['cases']],raw_identity='producer SHA recorded only, size/mtime stable',
    raw_archival_hashes_recomputed=0,project_imports=0,model_constructions=0,physics_steps=0,mesh_assets_read=0,
    compiles=0,old_QA_runs=0,Git_actions=0,agents_started=0,other_TRAIN_or_heldout_raw_opened=0,
    two_kHz_true_active_q='UNKNOWN_NOT_RECONSTRUCTED',DR_values_used_as_controller_inputs=False,
    controller_changes=False,score_changes=False,new_contact_permission=False,output_byte_cap_or_rescan_retry=False,
    PH7_pending=True,outside_current_PH6_cutoff=True,
    files=[dict(path=f,bytes=(D/f).stat().st_size,SHA=sha(D/f))for f in files])
put(D/'RECEIPT.json',r)
print(json.dumps(dict(status=r['status'],report_lines=n,summary_bytes=(D/'SUMMARY.json').stat().st_size,
    small_sources_unchanged=len(lock['small']),producer_matches=len(lock['actual_manifest_matches']),guide_ticks=r['original_guide_ticks_preserved'],
    raw_passes_per_file=1,physics=0,report_SHA=sha(D/'REPORT.md'),summary_SHA=sha(D/'SUMMARY.json'),receipt_SHA=sha(D/'RECEIPT.json')),indent=2))
