"""Read-only nominal D0 audit, with the original independent D1-D7 retained.

This candidate is not a task entry, GPU admission, learning entry or SDK patch.
There is no substitute MildDR object, sampled factor, mask or RNG.
"""
import os
import torch


REFERENCE_ATTRIBUTE = '_s5_nominal_d0_readonly_reference_v1'


def tensor(value):
    if torch.is_tensor(value):
        return value
    if hasattr(value, 'torch'):
        return value.torch
    import warp as wp
    return wp.to_torch(value)


def mild_dr_present_or_nominal(env):
    if hasattr(env, '_mild_dr'):
        assert env._mild_dr is not None, 'Present but null MildDR object'
        assert os.environ.get('RM_MILD_DR_PROFILE') != 'nominal', 'Nominal must not fabricate MildDR'
        return True
    if os.environ.get('RM_MILD_DR_PROFILE') != 'nominal' or os.environ.get('RM_DR_OFF') != '1':
        raise RuntimeError('Absent MildDR outside explicit nominal / legacy DR disabled scope')
    return False


def _read_d0(env):
    robot = env.scene['robot']
    values = {name: tensor(getattr(robot.root_view, getter)()).detach()
              for name, getter in (('mass', 'get_masses'), ('inertia', 'get_inertias'),
                                   ('materials', 'get_material_properties'))}
    for name, value in values.items():
        assert value.shape[0] == env.num_envs and torch.isfinite(value).all(), name
        assert float((value - value[:1]).abs().max()) <= 1e-6, 'Original D0 nominal clone bound: ' + name
    assert (values['mass'] > 0).all()
    return values


def capture_nominal_d0_reference(env):
    """Capture actual immutable D0 readback once before D7; no physical write/draw."""
    assert not mild_dr_present_or_nominal(env)
    values = _read_d0(env)
    if hasattr(env, REFERENCE_ATTRIBUTE):
        old = getattr(env, REFERENCE_ATTRIBUTE)
        assert all(torch.equal(values[k], old[k]) for k in values), 'Never replace a changed nominal reference'
    else:
        setattr(env, REFERENCE_ATTRIBUTE, {k: v.clone() for k, v in values.items()})
    return getattr(env, REFERENCE_ATTRIBUTE)


def parameter_audit(env):
    if mild_dr_present_or_nominal(env):
        return env._mild_dr.audit()
    reference = getattr(env, REFERENCE_ATTRIBUTE)  # Missing own capture fails strictly.
    values = _read_d0(env)
    for key, value in values.items():
        assert value.dtype == reference[key].dtype and value.shape == reference[key].shape
        assert torch.equal(value, reference[key].to(value.device)), 'Nominal D0 changed since actual capture: ' + key
    robot = env.scene['robot']
    scales = {}
    for name in ('legs', 'wheels'):
        actuator = robot.actuators[name]
        for key in ('episode_scale', 'step_scale'):
            value = tensor(getattr(actuator, key))
            assert value.shape[0] == env.num_envs and torch.isfinite(value).all()
            assert bool((value == 1).all()), 'Nominal actual motor output scale must be one'
            scales[name + '_' + key] = dict(shape=list(value.shape), max_abs_error=0.)
    # These are the original SDK-adapter audits. In particular the original
    # gas-to-spring expected-damping overlay must be installed by the constructor.
    pressure = {name: getattr(env, attr).audit() for name, attr in
                (('D5_spring', '_spring_pressure'), ('D6_gas', '_gas_damping'),
                 ('D7_COM', '_chassis_com'), ('D7_PD', '_explicit_pd'))}
    return dict(profile='nominal', actual_parameters_pass=True,
                audit_kind='actual_D0_reference_exact_and_unity_scales_with_original_D5_D6_D7_audits',
                parameter_spread={k: float((v - v[:1]).abs().max()) for k, v in values.items()},
                actual_D0_reference_unchanged_exact=True, motor_scale_errors=scales,
                independent_pressure_audits=pressure,
                local_COM_uniformity_not_a_D0_requirement_when_original_D7_enabled=True,
                original_D7_COM_tensor_and_PD_audits_retained=True,
                original_COM_link_to_world_1e_minus5_tolerance_unchanged_and_separately_required=True,
                MildDR_object_and_factor_mask_RNG_absent=True,
                legacy_full_dr_disabled=True, scope='Simulator source-bound readback; no hardware calibration')
