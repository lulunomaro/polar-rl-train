"""Independent saved-metadata assertions, supplementary to original physical gates."""
import numpy as np


AUDIT_KIND='actual_D0_reference_exact_and_unity_scales_with_original_D5_D6_D7_audits'


def audit(probe):
    witness=probe['native_readonly_witness']
    assert witness['DR_profile']=='nominal'
    n=witness['fixture_envs']
    optional_legacy_fields_absent=False
    if witness['kind']=='flat':
        initial_optional=probe['mild_initial_parameters'];final_optional=probe['mild_final_parameters']
        if initial_optional is None or final_optional is None:
            assert initial_optional is None and final_optional is None
            optional_legacy_fields_absent=True
            # These original optional fields deliberately describe MildDR, which
            # does not exist in nominal. Do not invent an initial audit object.
            rows=[probe['chassis_PD_audit']['parameter_auditor']]
        else:
            rows=[initial_optional,final_optional]
    else:
        rows=[probe['initial_parameter_audit'],probe['final_parameter_audit']]
    for value in rows:
        assert value['profile']=='nominal' and value['actual_parameters_pass'] is True
        assert value['audit_kind']==AUDIT_KIND
        for key in ('actual_D0_reference_unchanged_exact','original_D7_COM_tensor_and_PD_audits_retained',
                    'MildDR_object_and_factor_mask_RNG_absent','legacy_full_dr_disabled'):
            assert value[key] is True,key
        pressure=value['independent_pressure_audits']
        assert set(pressure)=={'D5_spring','D6_gas','D7_COM','D7_PD'}
        assert all(pressure[k]['enabled'] is True for k in pressure)
        assert pressure['D5_spring']['D6_gas_damping_varies_separately'] is True
    initial=witness['first_physics_initial']['physical_parameters']
    final=witness['final_physical_parameters']
    for params in (initial,final):
        assert all(params[key] is None for key in ('mild_factor','mild_nominal','mild_mu','mild_outputs'))
        assert not any(k.startswith('_mild_dr') for k in params['actual_captured_RNG_bytes'])
        for name in ('legs','wheels'):
            for key in ('episode_scale','step_scale'):
                value=np.asarray(params['motors'][name][key])
                assert value.shape[0]==n and np.isfinite(value).all() and np.all(value==1)
    for key in ('mass','inertia','materials'):
        a=np.asarray(initial[key]);b=np.asarray(final[key])
        assert a.shape[0]==n and a.shape==b.shape and np.isfinite(a).all() and np.isfinite(b).all()
        assert np.array_equal(a,b),key
        assert np.max(np.abs(a-a[:1]))<=1e-6,key
    return dict(legacy_optional_flat_MildDR_fields_absent=optional_legacy_fields_absent,
                independent_initial_final_witness_parameters_used=True,
                own_nominal_audit_from_actual_chassis_PD_report_used_when_legacy_absent=optional_legacy_fields_absent,
                no_missing_initial_audit_fabricated=True,
                D0_nominal_initial_final_readback_exact=True,actual_motor_output_scales_unity=True,
                absent_MildDR_fields_null_and_no_fake_RNG=True,original_D5_D6_D7_audits_retained=True,
                COM_not_falsely_required_uniform_across_D7_clones=True,
                original_COM_query_contact_hardware_gates_separately_required=True)
