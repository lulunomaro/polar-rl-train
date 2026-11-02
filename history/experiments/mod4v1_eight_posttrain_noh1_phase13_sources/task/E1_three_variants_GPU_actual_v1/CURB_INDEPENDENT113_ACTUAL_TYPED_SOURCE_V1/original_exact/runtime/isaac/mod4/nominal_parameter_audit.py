"""Actual nominal parameter readback for frozen evaluators only.

No writes, no randomization and no assertion about measured real hardware.
Uniformity across clones plus explicit disabled legacy/white DR is reported.
"""
import os
import torch
from mild_dr import tensor


def parameter_audit(env):
    if hasattr(env, '_mild_dr'):
        return env._mild_dr.audit()
    if os.environ.get('RM_MILD_DR_PROFILE') != 'nominal' or os.environ.get('RM_DR_OFF') != '1':
        raise RuntimeError('Missing DR audit object outside explicit nominal evaluation')
    robot = env.scene['robot']
    values = {
        'mass': tensor(robot.root_view.get_masses()),
        'inertia': tensor(robot.root_view.get_inertias()),
        'materials': tensor(robot.root_view.get_material_properties()),
        'local_com': tensor(robot.data.body_com_pos_b),
    }
    spread = {}
    raw = {}
    for key, value in values.items():
        if not torch.isfinite(value).all():
            raise RuntimeError('Nonfinite nominal ' + key)
        spread[key] = float((value - value[:1]).abs().max())
        raw[key + '_env0'] = value[0].detach().cpu().tolist()
    scales = {}
    gains = {}
    for name in ('legs', 'wheels'):
        actuator = robot.actuators[name]
        for key in ('episode_scale', 'step_scale'):
            value = getattr(actuator, key, None)
            error = 0. if value is None else float((tensor(value) - 1.).abs().max())
            if error != 0.:
                raise RuntimeError('Nominal motor output scale is not one')
            scales[name + '_' + key + '_error'] = error
        gains[name] = {key: tensor(getattr(actuator, key))[0].detach().cpu().tolist()
                       for key in ('stiffness', 'damping')}
    # Clone invariant checks, not a comparison with an independently measured robot.
    passed = all(value <= 1e-6 for value in spread.values())
    if not passed:
        raise RuntimeError('Nominal clone parameters differ: ' + str(spread))
    return {'profile': 'nominal', 'actual_parameters_pass': passed,
            'audit_kind': 'read_only_uniform_clone_parameters_and_unity_motor_scales',
            'parameter_spread': spread, 'motor_scale_errors': scales,
            'body_names': list(robot.body_names), 'nominal_actuator_pd_env0': gains,
            'raw_readback': raw, 'legacy_full_dr_disabled': True,
            'scope': 'Actual simulator readback; not a measured real-robot calibration'}
