"""Real saved small-row ABI check only; no original raw re-extraction or runtime claim."""
from pathlib import Path
import importlib.util,json,sys,time
import numpy as np
N=Path(__file__).resolve().parent;T=N.parent;U=T/'H1_STEP270_CLOSED79C_SAVED_REPLAY_AFTER_V8_20261026';M=T/'H1_STEP270_READONLY_LANDING_JOURNAL_PREPARATION_20261026';C=M/'candidate_v1'
sys.path.insert(0,str(C));spec=importlib.util.spec_from_file_location('real_saved_row_journal_CPU',C/'h1_lifetime_goal_counter_v1.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
with np.load(U/'SELECTED_RECORDED_MOTION.npz',allow_pickle=False) as z:
 data={k:z[k] for k in mod.LandingEventJournal.FIELDS};ids=z['env_ids'];n=len(ids)
before={k:v.copy() for k,v in data.items()};reset=data['done'][0].astype(bool);initial={k:np.where(reset,0,data[k][0]) for k in mod.EVENTS};cross=data['step_wheel_crossed'][0].copy();cross[reset]=False
counter=mod.LifetimeGoalCounter(initial,cross)
for i in range(1,48):assert counter.complete({k:v[i] for k,v in data.items()})
assert counter.snapshot()['diagnostic_valid'] and counter.landing_journal.snapshot()['diagnostic_valid']
assert all(np.array_equal(data[k],a) for k,a in before.items())
source=json.loads((U/'reports/CLOSED79C_RECORDED_MOTION_SOURCE_CPU_ACTUAL.json').read_bytes());selected_landing=int(np.maximum(np.diff(data['landing_count'].astype(np.int64),axis=0),0).sum())
result=dict(epoch=time.time(),passed_existing_small_saved_row_ABI_CPU=True,scope='New79c selected91 derived arrays only; row0 supplies known selected-reset-adjusted baseline and rows1..47 are processed. Not original20k raw, full window, runtime journal or new physics.',selected_environments=n,processed_controls=47,actual_field_shapes={k:list(v.shape) for k,v in data.items()},original_counter=counter.snapshot(),optional_journal=counter.landing_journal.snapshot(),all_actual_input_arrays_unchanged=True,no_missing_fields_or_type_errors=True,full20k_last48_original_landing_delta=source['recorded_event_counter_positive_increments']['landing_count'],selected_landing_delta=selected_landing,selection_gap_requires_direct_landing_selection_not_zeroing_global_counts=True,no_journal_binary_saved_or_GPU_policy_model_raw_or_remote_action=True)
with (M/'reports/LANDING_JOURNAL_REAL79C_SMALL_SELECTED_ROW_ABI_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(result,f,indent=2)
notice=dict(epoch=time.time(),actual_source_scope=source['scope'],full20k_last48_landing_delta=source['recorded_event_counter_positive_increments']['landing_count'],selected91_landing_delta=selected_landing,not_all_landing_events_in_old_height_selection=True,full79c_lifetime_landing12_not_erased=True,old_reconstruction_field_recorded_crossed_any_means_any_wheel=True,footprint_reader_same_label_means_both_wheels_any_frame=True,geometry_crossing_not_original_callback_dual_cross_truth=True,inherited_footprint_report_basename='SAVED76_LEADING_EDGE_VS_COMPLETE_WHEEL_FOOTPRINT_DESCRIPTIVE_CPU_ACTUAL.json',basename_historical_but_actual_folder_inputs_and_scope_are79c=True,old_fields_reports_and_values_retained=True,no_original_raw_or_model_reread_or_reextraction=True,new80_direct_landing_journal_source_only_not_installed_yet=True)
with (N/'reports/ACTUAL79C_SMALL_SELECTION_COVERAGE_AND_CROSS_FIELD_LABEL_SCOPE_NOTICE_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(notice,f,indent=2)
print(json.dumps(dict(real_saved_CPU_row_ABI=True,environments=n,controls=47,selected_landing_delta=selected_landing,full20k_last48_landing=notice['full20k_last48_landing_delta'])))
