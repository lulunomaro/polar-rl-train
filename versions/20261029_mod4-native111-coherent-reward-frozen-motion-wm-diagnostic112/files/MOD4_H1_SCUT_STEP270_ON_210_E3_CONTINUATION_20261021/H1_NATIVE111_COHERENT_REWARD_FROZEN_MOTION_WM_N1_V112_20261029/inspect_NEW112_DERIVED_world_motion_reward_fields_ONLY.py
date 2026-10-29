from pathlib import Path
import json
S=Path(__file__).resolve().parent;R=S/"reports"
a=json.loads((R/"NEW112_ACTUAL20S_MOTION_CONTACT_CLOCK_AND_CONTIGUOUS_WM_ANALYSIS_ACTUAL.json").read_bytes())
d=json.loads((R/"NEW112_DERIVED_CONTROL_CURVES_FOR_PLOT_ONLY.json").read_bytes())["rows"]
print(json.dumps(dict(core={k:a[k] for k in ["controls","physics_callbacks","original_termination_terms","root_start_xyz","root_final_terminal_xyz","root_net_forward_m","root_x_range_m","both_wheel_simultaneous_peak_m","airborne_both_above5mm_callbacks","contiguous_actual_action_WM","actual_request_motion"]},flight_segments=len(a["above5mm_clean_contact_flight_segments"]),objective_keys=list(d[210]["actual_task_reward_objective"]),example_objective=d[210]["actual_task_reward_objective"],max_frozen_sensitivity=[{k:x[k] for k in ["start_control","tail_to_reward_grad_norm_ratio","predicted32_max_both_wheel_bottom_m"]} for x in a["frozen_first_action_sensitivity"]]),indent=2)[:16000])

