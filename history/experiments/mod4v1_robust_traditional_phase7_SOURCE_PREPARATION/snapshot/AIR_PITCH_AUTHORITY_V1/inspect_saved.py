"""Inspect saved responses/diagnostics only; no MuJoCo imports or queries."""
from pathlib import Path
import json
D=Path(__file__).resolve().parent
v=json.loads((D/'RESPONSES.json').read_text(encoding='utf-8'))
f=json.loads((D/v['rows'][0]['frame_diagnostic_file']).read_text(encoding='utf-8'))
print(json.dumps(dict(first_new_baseline_frame={k:f[k]for k in ('body_regular_xmat','body_inertia_ximat','gyro_site_xmat','XBODY_regular_local_accel6',
    'BODY_inertia_local_accel6','BODY_world_accel6','inertia_local_alpha_transformed_world','wrong_untransformed_BODY_local_vs_qacc_error',
    'corrected_frame_error','root_Jacobian_identity_error','state_force_checks')},
    consistency=dict(ncon=[r['ncon']for r in v['rows']],closure_max=max(r['eq_geometry_closure_max_m']for r in v['rows']),
        mimic_max=max(r['eq_mimic_position_max_rad']for r in v['rows']),eq_pos_max=max(r['eq_efc_position_max']for r in v['rows']),
        eq_acc_max=max(r['eq_acceleration_residual_max_mixed_units']for r in v['rows']),
        constraint_types=sorted({x for r in v['rows']for x in r['efc_types']}),constraint_states=sorted({x for r in v['rows']for x in r['efc_states']}),
        nefc=[r['nefc']for r in v['rows']],solver_niter=[r['solver_niter']for r in v['rows']]),
    cumulative_forward=v['cumulative_mj_forward_calls'],effective_forward=v['calls']['mj_forward']),indent=2))
