"""NEW268 synthetic interface purpose only; never opens a checkpoint/raw/SDK."""
from pathlib import Path
import os
os.environ['CUDA_VISIBLE_DEVICES'] = ''
import ast
import hashlib
import json
import sys
import time
import traceback

N = Path(__file__).resolve().parent
R = N / 'reports'
purpose = json.loads((R / 'FROZEN268_NEW_MEASURED224_SYNTHETIC_CPU_PURPOSE.json').read_bytes())
with (R / 'CONSUMED268_NEW_MEASURED224_SYNTHETIC_CPU_ONCE.json').open('x', encoding='utf8') as f:
    json.dump(dict(epoch=time.time(), purpose_ID=purpose['purpose_ID'],
                   models_raw_assets_SDK_GPU_remote=0, old_fixture_replays=0), f, indent=2)
groups = []
rejections = []
try:
    for row in purpose['source_files']:
        assert hashlib.sha256(Path(row['path']).read_bytes()).hexdigest() == row['SHA']
    for path in N.glob('*.py'):
        ast.parse(path.read_text(encoding='utf8'))
    sys.path[:0] = [str(N), purpose['source255_directory'], purpose['native_source_directory']]
    import torch
    torch.set_num_threads(2)
    from measured_state224_v268 import (MeasurementBinding268, MOTOR_NAMES_REWARD_ORDER,
        SCHEMA_ID, MEASUREMENT_KIND, pack_measured224, schema_metadata)
    from native_measured_depth_world_model50_v268 import MeasuredDepthTeacherWM50
    from native_depth_world_model50_v255 import DepthTeacherWM50, load_native_kernels
    from predicted_literal_frame268 import predicted_literal_frame
    rng = torch.get_rng_state().clone()
    joints = ['synthetic_joint_' + str(i) for i in range(30)]
    motor_ids = (9, 1, 27, 13, 4, 24)
    for name, index in zip(MOTOR_NAMES_REWARD_ORDER, motor_ids):
        joints[index] = name
    bodies = ['chassis', 'left_wheel', 'right_wheel'] + ['synthetic_link_' + str(i) for i in range(28)]
    binding = MeasurementBinding268(tuple(joints), tuple(bodies), motor_ids,
        'SYNTHETIC_CPU_BINDING_ONLY', 'a' * 64)
    m = MeasuredDepthTeacherWM50(purpose['native_source_directory'], 'cpu', binding=binding,
        seed=268, envs=2, window=32, batch=2, hidden=(32, 32), synthetic_CPU_test=True)
    layout = m.measured_layout
    geometry, world, replay = load_native_kernels(purpose['native_source_directory'])
    assert m.model.in_dim == 273 and m.model.out_dim == 223
    assert m.model.layout.auxiliary_dim == 151 and m.buffer.fields['s'][0] == 224
    assert type(m.model).step is world.AugmentedWheelLegWorldModel.step
    assert type(m.model).targets is world.AugmentedWheelLegWorldModel.targets
    assert type(m.model).state_error is world.AugmentedWheelLegWorldModel.state_error
    assert type(m).sample is DepthTeacherWM50.sample and type(m).update is DepthTeacherWM50.update
    assert type(m.buffer) is replay.ReplayBuffer
    groups.append(dict(name='new224_aux151_native_SE3_H32_loss_replay_inherited', passed=True,
                       input273_output223=True, context40=True))

    base = torch.zeros(2, 127)
    base[:, 2] = .25
    # Nonidentity root yaw90deg; native quaternion uses wxyz, not SDK xyzw.
    base[:, 3] = 2 ** -.5
    base[:, 6] = 2 ** -.5
    base[:, 7:10] = torch.tensor([.2, .3, .4])
    base[:, 10:13] = torch.tensor([.5, .6, .7])
    base[:, 73:127] = torch.arange(54, dtype=torch.float32) / 10
    force = (torch.arange(186, dtype=torch.float32).reshape(2, 31, 3) + 1) * .5
    lengths = torch.tensor([[.21, .24], [.27, .29]])
    angles = torch.tensor([[.1, -.2], [.3, -.4]])

    def meta(tick):
        return dict(kind=MEASUREMENT_KIND, state_schema=SCHEMA_ID,
            packed_quaternion='wxyz', contact_input_frame='WORLD',
            contact_body_order=bodies, binding_witness_SHA=binding.witness_SHA,
            virtual_leg_source='own_virtual_legs_MOD4_hip_anchor_to_wheel_origin_v2',
            physics_end_tick=tick)

    def pack(base0=base, **kwargs):
        fields = dict(L0=lengths, theta0=angles, contact_forces_world=force,
                      layout=layout, binding=binding, measurement=meta(0), synthetic_CPU_test=True)
        fields.update(kwargs)
        return pack_measured224(base0, **fields)

    packed = pack()
    assert torch.equal(packed[:, :127], base)
    assert torch.equal(packed[:, 127:129], lengths) and torch.equal(packed[:, 129:131], angles)
    expected_body = torch.einsum('nji,nkj->nki', layout.unpack(packed)[1], force) / 400.
    assert torch.equal(packed[:, 131:].reshape(2, 31, 3), expected_body)
    assert torch.allclose(layout.pack(layout.unpack(packed)), packed, atol=1e-6, rtol=1e-6)
    assert schema_metadata()['fields'][-1]['stop'] == 224
    groups.append(dict(name='explicit224_prefix_L0_theta_BODY400N_roundtrip', passed=True,
                       synthetic_measured_states=2, fabricated_effort6=0))

    state = layout.unpack(packed)
    previous = tuple(x.clone() for x in state)
    previous[0][:, :2] -= torch.tensor([.02, .04])
    commands = torch.tensor([[.5, .2, .13, 0.], [-.5, -.2, .14, 0.]])
    origins = torch.tensor([[3., 6., 0.], [9., 12., 0.]])
    frame = predicted_literal_frame(previous, state, commands, layout=layout,
        binding=binding, environment_origins=origins, synthetic_CPU_test=True)
    assert set(frame) == {'commands', 'root_states', 'base_lin_vel', 'base_ang_vel',
                         'projected_gravity', 'L0', 'theta0', 'torques', 'contact_forces'}
    assert torch.allclose(frame['contact_forces'], force, atol=3e-5, rtol=1e-6)
    assert torch.equal(frame['torques'], base[:, 91:121][:, list(motor_ids)])
    assert torch.allclose(frame['base_lin_vel'], torch.tensor([[2., -1., 0.]]).expand(2, -1), atol=1e-5)
    assert torch.allclose(frame['base_ang_vel'], torch.tensor([[.6, -.5, .7]]).expand(2, -1), atol=1e-6)
    assert torch.allclose(frame['projected_gravity'], torch.tensor([[0., 0., -1.]]).expand(2, -1), atol=1e-6)
    assert torch.equal(frame['root_states'][:, 3:7], geometry.mat_to_quat(state[1])[:, [1, 2, 3, 0]])
    assert torch.equal(frame['root_states'][:, 7:10], base[:, 7:10])
    assert torch.equal(frame['root_states'][:, :3], base[:, :3] + origins)
    x = packed.detach().clone().requires_grad_(True)
    frame_grad = predicted_literal_frame(previous, layout.unpack(x), commands,
        layout=layout, binding=binding, environment_origins=origins, synthetic_CPU_test=True)
    signal = sum(frame_grad[k].square().mean() for k in frame_grad if k != 'commands')
    grad, = torch.autograd.grad(signal, x)
    assert torch.isfinite(grad).all() and (grad[:, 127:].abs().sum(0) > 0).all()
    assert all(float(grad[:, 91 + i].abs().sum()) > 0 for i in motor_ids)
    groups.append(dict(name='predicted_frame_rotation_position_difference_effort_selection_and_gradient',
                       passed=True, reward_methods_or_weights_edited=False,
                       original259_frame_only_not_reward_replay=True))

    def reject(name, call):
        try:
            call()
        except (ValueError, TypeError):
            rejections.append(name)
        else:
            raise AssertionError('Invalid input accepted: ' + name)

    reject('missing_L0', lambda: pack(L0=None))
    reject('missing_contact_measurement', lambda: pack(contact_forces_world=None))
    reject('wrong_30body_force_width', lambda: pack(contact_forces_world=force[:, :30]))
    reject('old127_is_not224', lambda: layout.unpack(base))
    reject('old127_WM_checkpoint', lambda: m.require_checkpoint_schema({'protocol': {'state127': True}}))
    reject('wrong_motor_ID_order', lambda: MeasurementBinding268(tuple(joints), tuple(bodies),
        tuple(reversed(motor_ids)), binding.witness_kind, binding.witness_SHA).validate(synthetic_CPU_test=True))
    reject('synthetic_binding_not_actual', lambda: binding.validate())
    reject('missing_measurement_schema', lambda: pack(measurement={}))
    reject('xyzw_cannot_be_relabelled_native', lambda: pack(measurement={**meta(0), 'packed_quaternion': 'xyzw'}))
    bad_force = force.clone()
    bad_force[0, 0, 0] = float('nan')
    reject('nonfinite_force', lambda: pack(contact_forces_world=bad_force))

    xi31 = torch.tensor([1., .9] + [1.] * 6 + [0.] * 3 + [1.] * 10 +
                        [1.] * 2 + [1.] * 2 + [1.] * 2 + [0.] * 4).expand(2, -1).clone()
    depth9 = torch.tensor([1.25, .27, 0., 0., 1.5, 1.5, .9, .02, 1.]).expand(2, -1).clone()

    def row(t):
        b0, b1 = base.clone(), base.clone()
        b0[:, 0] = t * .005
        b1[:, 0] = (t + 1) * .005
        return dict(s=pack(b0, measurement=meta(t * 8)),
            s1=pack(b1, L0=lengths + (t + 1) * .0001, measurement=meta((t + 1) * 8)),
            a=torch.zeros(2, 6), a_prev=torch.zeros(2, 6), xi=torch.cat((xi31, depth9), -1),
            r=torch.zeros(2), f=torch.zeros(2, dtype=torch.long),
            ep_step=torch.full((2,), t, dtype=torch.int32), done=torch.tensor([t == 9, False]))

    def producer(t):
        return dict(kind='SYNTHETIC_CPU_INTERFACE_ONLY', plant='own_MOD4_live_USD',
            run_id='synthetic268', generation=1, source_admission_SHA='b' * 64,
            max_depth_age_seconds=.02, state_schema=SCHEMA_ID,
            binding_witness_SHA=binding.witness_SHA,
            measured_fields=['own_L0_theta4', 'contact_forces_BODY31x3'],
            s_physics_end_tick=t * 8, s1_physics_end_tick=(t + 1) * 8)

    snapshot = {k: v.clone() for k, v in m.model.state_dict().items()}
    reject('producer_old127_schema', lambda: m.add(row(0), physics_end_tick=8, physics_us=2500,
        feedback_samples=2, producer={**producer(0), 'state_schema': 'old127'}, synthetic_CPU_test=True))
    reject('gapped_measurement_endpoint', lambda: m.add(row(0), physics_end_tick=8, physics_us=2500,
        feedback_samples=2, producer={**producer(0), 's1_physics_end_tick': 16}, synthetic_CPU_test=True))
    old = row(0)
    old['s'] = old['s'][:, :127]
    reject('replay_127_width', lambda: m.add(old, physics_end_tick=8, physics_us=2500,
        feedback_samples=2, producer=producer(0), synthetic_CPU_test=True))
    reject('100Hz_not50Hz', lambda: m.add(row(0), physics_end_tick=4, physics_us=2500,
        feedback_samples=2, producer=producer(0), synthetic_CPU_test=True))
    assert m.controls == m.buffer.size == 0 and all(torch.equal(v, snapshot[k]) for k, v in m.model.state_dict().items())
    try:
        m.policy_imagination()
    except NotImplementedError:
        rejections.append('future_recorded_depth_not_Pi_imagination_input_EXPLICIT_PENDING')
    else:
        raise AssertionError('Unimplemented depth belief accepted as policy imagination')
    groups.append(dict(name='missing_legacy_binding_clock_nonfinite_rejected_before_norm_replay',
                       passed=True, rejected_count=len(rejections), cases=rejections))

    for t in range(32):
        m.add(row(t), physics_end_tick=(t + 1) * 8, physics_us=2500,
              feedback_samples=2, producer=producer(t), synthetic_CPU_test=True)
    sampled = m.sample()
    expected_mask = torch.cumprod(torch.cat((torch.ones(2, 1), 1 - sampled['done'].float()[:, :-1]), -1), -1)
    assert torch.equal(sampled['mask'], expected_mask)
    result = m.update()
    assert result['world_updates'] == 1 and result['policy_updates'] == 0
    assert result['window'] == 32 and result['preclip_grad_L2'] > 0
    checkpoint = m.checkpoint()
    m.require_checkpoint_schema(checkpoint)
    assert checkpoint['measured_binding'] == binding.metadata()
    assert checkpoint['complete_native_policy_conversion'] is False and checkpoint['replay_saved'] is False
    assert checkpoint['protocol']['policy_imagination_context_ready'] is False
    assert torch.equal(rng, torch.get_rng_state()) and not torch.cuda.is_initialized()
    groups.append(dict(name='new224_native_H32_WM_only_synthetic_update', passed=True,
                       synthetic_pairs=64, synthetic_WM_updates=1, result=result,
                       source127_models_read=0, serialization=0, policy_updates=0))
    report = dict(passed=True, epoch=time.time(), purpose_ID=purpose['purpose_ID'], groups=groups,
        reject_count=len(rejections), synthetic_envs=2, controls=32, measured_pairs=64,
        synthetic_WM_updates=1, actual_Pi_WM_updates=0, models_raw_assets_SDK_GPU_remote_Git=0,
        old255_259_fixtures_replayed=0, actual267_complete_assumed=False,
        actual_producer_or_skill_qualified=False, CUDA_initialized=False)
except BaseException:
    report = dict(passed=False, epoch=time.time(), purpose_ID=purpose['purpose_ID'],
        groups=groups, error=traceback.format_exc(),
        scope='New268 synthetic source-interface failure; no actual model/physics run')
    raise
finally:
    with (R / 'ACTUAL268_NEW_MEASURED224_SYNTHETIC_CPU_RETURNED.json').open('x', encoding='utf8') as f:
        json.dump(report, f, indent=2, allow_nan=False)
print(json.dumps(dict(passed=report['passed'], groups=len(groups), rejects=len(rejections),
                      synthetic_WM_updates=1, actual_Pi_WM_updates=0)))
