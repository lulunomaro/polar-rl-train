"""Zero requested controls are a restore contract, never a physics-health pass."""
import math
def verify_zero_control_restore(h,actual_buffers_finite,reset_q_error):
    assert h['version']==3 and h['control_steps']==0
    assert h['actual_physics_callbacks']==h['expected_physics_callbacks']==0
    assert h['integrity_task_reset_events']==h['unknown_task_reset_events']==0
    assert h['nonfinite_observed'] is False and h['stop_reason'] is None
    assert h['termination_reason_coverage_exact'] is True
    assert actual_buffers_finite is True and reset_q_error==0.0
    # Unobserved peaks stay NaN. They are not rewritten to measured zero/pass.
    return dict(zero_control_restore_state_integrity=True,requested_controls=0,callbacks=0,
        actual_live_buffers_finite=True,actual_reset_q30_exact=True,
        original_max_closure=h['max_closure_error_m'],original_max_mimic=h['max_mimic_error_rad'],
        perstep_closure_mimic_not_observed=math.isnan(h['max_closure_error_m']) and math.isnan(h['max_mimic_error_rad']),
        positive_control_physics_certification=False)
