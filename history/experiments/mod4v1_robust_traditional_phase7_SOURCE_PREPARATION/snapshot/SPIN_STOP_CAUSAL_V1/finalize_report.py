"""Saved-evidence finalization only: no trace contents, models, controllers or executables."""
from pathlib import Path
from urllib.parse import unquote
import hashlib,json,re
D=Path(__file__).resolve().parent; R=D.parent
load=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,v):
    with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(v,f,separators=(',',':'),allow_nan=False);f.write('\n')
method=load(D/'METHOD.json'); lock=load(D/'SOURCE_LOCK.json'); w=load(D/'WINDOWS.json')
assert sha(D/'METHOD.json')==lock['method']['sha256']==w['method_sha256']
assert sha(D/'SOURCE_LOCK.json')==w['source_lock_sha256']
assert sha(D/'extract_windows.py')==w['extractor_sha256']
assert [c['case'] for c in w['cases']]==[c['case'] for c in lock['cases']]
for r in lock['small_inputs']:
    p=Path(r['path']); p=p if p.is_absolute() else R/p
    assert p.stat().st_size==r['bytes'] and sha(p)==r['sha256'], ('small input changed',str(p))
for c in lock['cases']:
    st=(R/c['trace']).stat()
    assert st.st_size==c['raw_bytes'] and st.st_mtime_ns==c['raw_mtime_ns']
# Invert the two representation-only edits to prove the first algorithm source is preserved exactly.
cur=(D/'extract_windows.py').read_text(encoding='utf-8')
a=cur.index('# Representation-only revision:'); b=cur.index('result=dict(',a)
restored=cur[:a]+cur[b:]
packed="""raw_hashes_computed=0,trace_paths_opened=method['trace_allowlist'],cases=packed_cases,
    encoding='segments and snapshots are lossless ordered arrays using these global field schemas',
    segment_stat_fields=stat_fields,snapshot_fields=snapshot_fields,"""
original="raw_hashes_computed=0,trace_paths_opened=method['trace_allowlist'],cases=cases,"
assert restored.count(packed)==1
restored=restored.replace(packed,original)
assert restored.encode('utf-8')==(D/'revisions/extract_attempt_01/extract_windows.py').read_bytes()
assert "('summary cap', 111180)" in (D/'revisions/extract_attempt_01/extract_01.log').read_text(encoding='utf-8')
assert (D/'WINDOWS.json').stat().st_size<=method['output_limits']['window_summary_bytes']
rows=[]
for c in w['cases']:
    for stop in c['stops']:
        tail=dict(zip(w['segment_stat_fields'],stop['segments']['tail']))
        whole=dict(zip(w['segment_stat_fields'],stop['segments']['whole_stop']))
        rows.append(dict(case=c['case'],phase=stop['phase'],t0_s=stop['t0_control_s'],end_s=stop['end_s'],
            n_stop=whole['n'],n_tail=tail['n'],xy_true_displacement_m=stop['xy_true_displacement_m'],
            last1s_true_mean=[x[0] for x in tail['true']],last1s_estimate_mean=[x[0] for x in tail['estimated']],
            last1s_residual_source_mean=[x[0] if x is not None else None for x in tail['residual_source']],
            last1s_pitch_residual_now_mean=tail['residual_now'][1][0],
            delays_s=dict(shaped_zero=stop['first_shaped_zero_s'],gain1p5=stop['first_gain_1p5_s'],
                mix_positive=stop['first_mix_positive_s'],mix_full=stop['first_mix_full_s']),
            wheel_request_minus_last_ctrl_RMS=whole['request_minus_last_ctrl_RMS'],
            wheel_request_abs_max=[max(abs(x[2]),abs(x[3])) for x in whole['request_wheels']],
            wheel_last_ctrl_abs_max=[max(abs(x[2]),abs(x[3])) for x in whole['last_ctrl_wheels']],
            request_absolute_peak_coincidences=whole['request_absolute_peak_coincidences'],
            last_ctrl_absolute_peak_coincidences=whole['last_ctrl_absolute_peak_coincidences'],
            centering_active_samples=whole['centering_active_samples'],original_phase_metrics=stop['original_phase_metrics'],
            post_truth_tail_threshold_break_counts=stop['tail_post_criterion_break_counts']))
summary=dict(kind='SMALL_DESCRIPTIVE_TRAIN_SUMMARY_NOT_A_NEW_SCORE',vector_order=w['numeric_vector_order'],
    raw_trace_allowlist=method['trace_allowlist'],windows_sha256=sha(D/'WINDOWS.json'),
    paired_DR_receipts_equal=lock['paired_DR_receipts_equal'],
    parent_supplied_overall_context_not_recomputed={'R26':'0/8','R27_both':'2/8'},
    original_selected_transition_results={c['case']:c['original_transition_proposed_pass'] for c in w['cases']},
    transitions={c['case']:c['transitions'] for c in w['cases']},stops=rows,unknown=w['unknown'])
put(D/'SUMMARY.json',summary)
assert (D/'SUMMARY.json').stat().st_size<16384
text=(D/'REPORT.md').read_text(encoding='utf-8'); lines=len(text.splitlines())
assert lines<=method['output_limits']['report_lines']
links=re.findall(r'\]\(<([^>]+)>\)',text)
for target in links:
    name,_,fragment=unquote(target).partition('#'); p=Path(name)
    assert p.is_absolute()
    if p==D/'RECEIPT.json':continue
    assert p.is_file(), ('missing live report link',name)
    if fragment:
        matches=re.fullmatch(r'L(\d+)(?:-L(\d+))?',fragment); assert matches
        lo=int(matches[1]); hi=int(matches[2] or matches[1]); assert 1<=lo<=hi<=len(p.read_text(encoding='utf-8').splitlines())
files=['REPORT.md','SUMMARY.json','WINDOWS.json','METHOD.json','SOURCE_LOCK.json','freeze_sources.py',
       'extract_windows.py','inspect_saved.py','finalize_report.py','freeze_01.log','extract_01.log','extract_02.log','saved_facts.log',
       'revisions/extract_attempt_01/extract_windows.py','revisions/extract_attempt_01/extract_01.log']
receipt=dict(status='SEALED_READ_ONLY_FOUR_TRAIN_STOP_ANALYSIS_NOT_CAUSAL_IDENTIFICATION_OR_NEW_QUALIFICATION',
    report_lines=lines,report_links_verified=len(links),small_inputs_unchanged=32,recorded_manifest_subset_checks=lock['recorded_manifest_subset_checks'],
    unique_trace_paths=method['trace_allowlist'],unique_trace_count=4,new_scan_attempts=2,total_trace_rows_read_by_scans=20800,
    canonical_scan_rows=sum(c['scanned_rows'] for c in w['cases']),retained_rows_per_case=[c['retained_rows'] for c in w['cases']],
    source_timestamp_pair_misses=sum(c['source_pair_misses'] for c in w['cases']),
    raw_SHA_recomputed=False,raw_identity='producer SHA recorded only; current size/mtime stable',
    first_attempt=dict(status='FAILED_OUTPUT_SIZE_ONLY',output_bytes=111180,cap_bytes=98304,no_WINDOW_file_written=True),
    second_attempt=dict(status='SUCCESS',output_bytes=(D/'WINDOWS.json').stat().st_size,
        representation_only_inverse_restores_first_source_exactly=True,arithmetic_windows_statistics_thresholds_and_cap_unchanged=True),
    new_physics_steps=0,model_constructions=0,compiled_sources=0,old_QA_runs=0,controller_implementations=0,
    heldout_or_other_TRAIN_traces_opened=0,agents_started=0,parent_R52_interactions=0,
    scores_regraded=False,control_permission_added=False,hardware_qualification=False,
    files=[dict(path=f,bytes=(D/f).stat().st_size,sha256=sha(D/f)) for f in files])
put(D/'RECEIPT.json',receipt)
assert (D/'RECEIPT.json').stat().st_size<12288
print(json.dumps(dict(status=receipt['status'],report_lines=lines,small_inputs_unchanged=32,manifest_checks=receipt['recorded_manifest_subset_checks'],
    summary_bytes=(D/'SUMMARY.json').stat().st_size,windows_bytes=(D/'WINDOWS.json').stat().st_size,
    source_pair_misses=receipt['source_timestamp_pair_misses'],report_sha=sha(D/'REPORT.md'),summary_sha=sha(D/'SUMMARY.json'),
    receipt_sha=sha(D/'RECEIPT.json'),raw_hashes=0,old_QA=0,physics=0),indent=2))
