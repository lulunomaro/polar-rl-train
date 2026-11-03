"""Freeze small explicit inputs only, before the window scan; stdlib/no imports of project code."""
from pathlib import Path
import hashlib,json
D=Path(__file__).resolve().parent; R=D.parent

def digest(p):
    raw=p.read_bytes(); assert len(raw)<131072, ('small-input cap',str(p))
    return dict(path=str(p.relative_to(R)) if p.is_relative_to(R) else str(p),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())

def load(p): return json.loads(p.read_text(encoding='utf-8'))
def put(p,v):
    with p.open('x',encoding='utf-8',newline='\n') as f: json.dump(v,f,indent=2,allow_nan=False)

method=load(D/'METHOD.json'); assert len(method['trace_allowlist'])==4
sources=[R/x for x in [
'launch_r26_transitions_train.py','launch_r27_spin_stop_train.py',
'batches/r26_transitions26/PROTOCOL.json','batches/r27_spin_stop27/PROTOCOL.json',
'run_transition_case_v3.py','run_spin_stop_v1.py',
'batches/r26_transitions26/run_transition_case_v3.py','batches/r27_spin_stop27/run_spin_stop_v1.py',
'spin_stop_capture_v1.py','batches/r27_spin_stop27/spin_stop_capture_v1.py',
'spin_base_v1.py','spin_center_controller_v1.py','spin_center_torque_v2.py','ground_controller_v4.py',
'sensor_core_v4.py','physics_bridge.py','physics_bridge_v3.py','physics_bridge_v4_grade.py','transition_grader_v1.py']]
sources.append(R.parent/'traditional_control_20261101/control_core.py')
for trace in method['trace_allowlist']:
    case=Path(trace).parent.name; batch='r26_transitions26' if case.startswith('r26_') else 'r27_spin_stop27'
    sources.extend([R/'batches'/batch/(case+'.json'),R/'results'/case/'result.json',R/'results'/case/'SOURCE_MANIFEST.json'])
assert len(sources)==len(set(sources))
refs=[digest(p) for p in sources]; bypath={str(p.resolve()).casefold():x for p,x in zip(sources,refs)}
cases=[]; manifest_checks=0
for trace in method['trace_allowlist']:
    tp=R/trace; case=tp.parent.name; seed=int(case.rsplit('_',1)[1]); assert seed in (201,202)
    result=load(tp.parent/'result.json'); cfg=result['config']; manifest=load(tp.parent/'SOURCE_MANIFEST.json')
    batch='r26_transitions26' if case.startswith('r26_') else 'r27_spin_stop27'
    assert cfg==load(R/'batches'/batch/(case+'.json')) and cfg['case_id']==case and cfg['seed']==seed
    assert result['cohort']=='train' and result['complete'] and result['controls']==2600
    assert result['actual_feedback']=='sensors' and result['truth_used_for_control'] is False
    assert Path(result['trace_artifact']['path']).resolve()==tp.resolve()
    st=tp.stat(); assert st.st_size==result['trace_artifact']['bytes'] and st.st_size<12*1024*1024
    checked=[]
    for m in manifest['files']:
        k=str(Path(m['path']).resolve()).casefold()
        if k in bypath:
            assert bypath[k]['sha256']==m['SHA'] and bypath[k]['bytes']==m['bytes'], ('recorded source mismatch',m['path'])
            checked.append(bypath[k]['path']); manifest_checks+=1
    actual_runner=R/('run_transition_case_v3.py' if case.startswith('r26_') else 'run_spin_stop_v1.py')
    assert any(Path(m['path']).resolve()==actual_runner.resolve() for m in manifest['files'])
    assert str(actual_runner.relative_to(R)) in checked
    snapshot=R/'batches'/batch/actual_runner.name
    assert actual_runner.read_bytes()==snapshot.read_bytes(), ('batch/root runner mismatch',case)
    cases.append(dict(case=case,seed=seed,variant='R26_baseline' if case.startswith('r26_') else 'R27_both',trace=trace,
        raw_bytes=st.st_size,raw_mtime_ns=st.st_mtime_ns,producer_SHA_not_recomputed=result['trace_artifact']['SHA'],
        rows_expected=result['controls'],source_manifest_subset_checked=checked,
        original_transition_proposed_pass=result['transition_proposed_pass'],original_phase_metrics=result['phase_metrics'],
        original_wholecase_xy_displacement_m=result['xy_displacement_m'],
        motor_gain6=result['DR']['D0']['motor_gain6'],feedback_delay_us=result['DR']['D3']['requested_delay_us'],
        action_delay_us6=result['DR']['D4']['action_delay_us6']))
paired_DR={str(s):load(R/f'results/r26_spin_cycle_{s}/result.json')['DR']==load(R/f'results/r27_both_{s}/result.json')['DR'] for s in (201,202)}
lock=dict(kind='FOUR_TRAIN_PATHS_AND_SMALL_SOURCE_LOCK_BEFORE_WINDOW_EXTRACTION',method=digest(D/'METHOD.json'),
    small_inputs=refs,cases=cases,recorded_manifest_subset_checks=manifest_checks,paired_DR_receipts_equal=paired_DR,
    no_trace_opened_by_this_freezer=True,raw_archive_hashes_computed=0,no_global_tree_hash=True,
    heldout_or_other_TRAIN_trace_paths_allowed=False,project_modules_imported=[])
put(D/'SOURCE_LOCK.json',lock)
print(json.dumps(dict(small_inputs=len(refs),cases=[c['case'] for c in cases],recorded_source_checks=manifest_checks,
    paired_DR_receipts_equal=paired_DR,method_sha=lock['method']['sha256'],source_lock_sha=digest(D/'SOURCE_LOCK.json')['sha256'],raw_hashes=0),indent=2))
