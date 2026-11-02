"""One causal test: identical R40 driving policy, restore stance only at stop."""
from pathlib import Path
import json,ast
from fresh_train_batch_v1 import launch
R=Path(__file__).resolve().parent
qa=json.loads((R/'ROUGH_WORLD_LEG_V3/preflight001/RESULT.json').read_bytes());assert qa['failures']==0
c=json.loads((R/'batches/r40_world_leg4/r40_world_d0_bar40.json').read_bytes())
name='r42_latched_d0_bar40';c['case_id']=name;c['cohort']='new_TRAIN_stop_only_intervention_not_holdout'
c['controller']['world_full_activation_m_s']=.4
for f in('run_world_leg_case_v3.py','ROUGH_WORLD_LEG_V3/controller.py',Path(__file__).name):ast.parse((R/f).read_bytes())
keys=['complete','stop_reason','controls','physics_callbacks','rough_case_pass','rough_progress_m','rough_max_y_m','max_pitch_abs','max_roll_abs','physics_nonwheel_contact_ticks',
      'tail_v_tracking_RMSE','tail_velocity_mean_m_s','tail_pitch_RMS','max_closure','max_mimic','trace_artifact']
launch(R,'r42_latched_capture1','run_world_leg_case_v3.py',[(name,c)],dict(kind='R42_NEW_NOMINAL_LATCHED_STOP_CAUSAL_CASE',
      existing_constant_gain_case='r40_world_d0_bar40',existing_startup_scheduled_case='r41_capture_d0_bar40',
      physical_drive_prefix_validation='compare_ALL_control_physics_fields_before_first_falling_forward_request_no_tolerance_relaxation',
      changed='only_after_first_drive_to_stop_edge_gain_tracks_shaped_stop',acceptance='unchanged_R22_R40_R41_fullrough_gate',
      old_once_not_replayed=True,no_truth_DR_control_input=True,no_model_collision_material_change=True,
      nominal_only=True,new_fullDR_holdout=False),keys,max_workers=1)
