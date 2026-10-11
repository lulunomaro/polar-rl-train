"""Independent reader: fixed mesh assignment, dynamically queried current family."""
from wave_io import *
import ast

def main():
    old=D/'review_wave368_full_training_trace_actual.py';tree=ast.parse(old.read_text(encoding='utf8'))
    code=next(x.value for x in ast.walk(tree) if isinstance(x,ast.Constant) and isinstance(x.value,str) and x.value.startswith('from pathlib import Path\nimport json,hashlib,numpy'))
    before="  assert np.array_equal(x[:,:,10],np.broadcast_to(family,x[:,:,10].shape))\n  y=x[:,ids,:];c=y[:,:,7];assert np.max(abs(y[:,:,8:10]))<=1e-6 and np.max(abs(c))<=.300001"
    after="  assert np.isin(x[:,:,10],np.arange(-1,5)).all()\n  changed_family_controls+=int((x[:,:,10]!=family[None,:]).sum())\n  current_wave=x[:,:,10]==4;y=x[:,ids,:];c=x[:,:,7][current_wave]\n  assert np.max(abs(x[:,:,8:10][current_wave]))<=1e-6 and np.max(abs(c))<=.300001"
    assert code.count(before)==1;code=code.replace(before,after)
    code=code.replace('family_counts=None;speed_max=0.;','changed_family_controls=0;family_counts=None;speed_max=0.;')
    code=code.replace('command_integral+=abs(c).sum(0)*.01;','command_integral+=abs(y[:,:,7]).sum(0)*.01;')
    code=code.replace("assert hist.sum()==total*2820;","")
    code=code.replace("actual_family_enum_counts=family_counts,", "initial_family_enum_counts=family_counts,dynamic_current_family_changed_control_count=changed_family_controls,static_geometry_assignment_not_mutated=True,dynamic_family_semantics='eligibility queries current root cell; source retention_flat_runtime.py lines44-64 and97-100',")
    code=code.replace('per_environment_nominal_abs_command_integral_m_range=', 'initial_Wave_cohort_command_integral_including_actual_family_changes_m_range=')
    code=code.replace('same_control_prereset_minus_before_root_x_sum_range_m=', 'initial_Wave_cohort_same_control_prereset_minus_before_root_x_sum_range_m=')
    own=json.loads(sorted(R.glob('WAVE_OWN_FORMAL_CPU_ACTUAL_[0-9]*.json'))[-1].read_bytes());assert own['passed'] and own['closeout_ready']
    compact=dict(checkpoint=own['own_checkpoint'],source_SHA=own['source_SHA'],controls=own['health']['control_steps'])
    code=code.replace('COMPACT_TOKEN',repr(json.dumps(compact)))
    source=D/'inherited_source/isaac/mod4/retention_flat_runtime.py'
    save('WAVE368_DYNAMIC_FAMILY_READER_SCHEMA_REVIEW.json',dict(epoch=time.time(),original_reader_path=str(old),original_reader_SHA=H(old.read_bytes()),original_failure_retained=True,
        source_path=str(source),source_SHA=H(source.read_bytes()),
        actual_semantics='Mesh assignment is fixed. Command family is refreshed from current root cell each control; it is not a fixed per-environment label.',
        correction='Count signedgentle/standing only at actual current-family4 controls; initial2820 cohort root displacement is separately labelled and may enter other cells.',
        no_geometry_command_or_runtime_validator_change=True,no_GPU_replay=True))
    save('WAVE_TRACE_SEARCH_PATH_READER_ERRORS.json',dict(epoch=time.time(),attempted_missing_files=['inherited_source/e1_retained_command_state_runtime.py','inherited_source/e1_current_command_profile.py','inherited_source/train_e1_retention_episode_reviewed_resume_ppo.py','inherited_source/e1_retention_training_runtime.py'],error='rg explicit guessed paths did not exist; rg --files located retention_flat_runtime.py and retention_command_state.py.',evidence_kind='reader error description; no fabricated raw transcript',no_GPU_or_physical_failure=True))
    n,w=io.connect_both()
    try:
        v=run(n,code);p=save('WAVE368_FULL_TRAINING_TRACE_ACTUAL_'+str(time.time_ns())+'.json',v)
        print(json.dumps(dict(report=str(p),passed=True,controls=v['actual_controls'],Wave_histogram=v['Wave_beforephysics_negative_positive_standing_control_counts'],dynamic_family_changes=v['dynamic_current_family_changed_control_count'])))
    finally:io.cleanup(n,w)

if __name__=='__main__':
    try:main()
    except BaseException:save('WAVE368_DYNAMIC_FAMILY_READER_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_GPU_or_PPO_replay=True));raise
