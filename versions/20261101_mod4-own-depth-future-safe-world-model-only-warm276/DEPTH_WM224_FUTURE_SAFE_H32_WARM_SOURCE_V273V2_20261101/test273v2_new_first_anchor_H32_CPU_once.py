"""New source integration only:99 synthetic pairs, one WM-only optimizer step."""
from pathlib import Path
from dataclasses import replace
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
purpose = json.loads((R / 'FROZEN273V2_NEW_FIRST_ANCHOR_H32_SYNTHETIC_CPU_PURPOSE.json').read_bytes())
with (R / 'CONSUMED273V2_NEW_FIRST_ANCHOR_H32_CPU_ONCE.json').open('x', encoding='utf8') as f:
    json.dump(dict(epoch=time.time(), purpose_ID=purpose['purpose_ID'], actual_models_raw_SDK_GPU_remote=0,
                   old_fixture_replays=0), f, indent=2)
groups, refused = [], []
try:
    for row in purpose['source_files']:
        assert hashlib.sha256(Path(row['path']).read_bytes()).hexdigest() == row['SHA']
    for p in N.glob('*.py'):
        ast.parse(p.read_text(encoding='utf8'))
    sys.path[:0] = [str(N)] + purpose['import_directories']
    import torch
    torch.set_num_threads(2)
    from measured_state224_v268 import MeasurementBinding268, MOTOR_NAMES_REWARD_ORDER, SCHEMA_ID
    from observed_support_context271 import Producer271, CurrentDepthPacket271, FRAME, make_anchor
    from future_safe_wm_warm273 import FutureSafeWarmWM273, FrozenTeacherContract273, context_from_start_anchor273
    rng = torch.get_rng_state().clone()
    joints = ['synthetic_joint_' + str(i) for i in range(30)]
    motor_ids = (8, 1, 27, 13, 4, 24)
    for name, i in zip(MOTOR_NAMES_REWARD_ORDER, motor_ids):
        joints[i] = name
    bodies = ('chassis', 'left_wheel', 'right_wheel') + tuple('synthetic_link_' + str(i) for i in range(28))
    binding = MeasurementBinding268(tuple(joints), bodies, motor_ids, 'SYNTHETIC_CPU_BINDING_ONLY', 'a' * 64)
    teacher = FrozenTeacherContract273('d' * 64, 'e' * 64, True)
    m = FutureSafeWarmWM273(purpose['native_source_directory'], 'cpu', teacher_contract=teacher,
        binding=binding, seed=273, envs=3, batch=4, hidden=(32, 32), synthetic_CPU_test=True)
    # Nonzero synthetic output weights make sensitivity to context observable;
    # this is NOT a production initialization change or an actor/head edit.
    with torch.no_grad():
        m.model.net[-1].weight.fill_(.001)
    origins = torch.tensor([[3., 6., 0.], [9., 12., 0.], [15., 18., 0.]])
    xi31 = torch.tensor([1., .9] + [1.] * 6 + [0.] * 3 + [1.] * 10 +
                        [1.] * 2 + [1.] * 2 + [1.] * 2 + [0.] * 4).repeat(3, 1)
    packets = []
    rows = []

    def make_row(t):
        s = torch.zeros(3, 224)
        s[:, 2] = .27
        s[:, 3] = 1.  # native wxyz
        s[:, 0] = t * .003
        s[:, 7] = .15
        s[:, 127:129] = .24
        s1 = s.clone()
        s1[:, 0] += .003
        s1[:, 127] += .0001
        found = torch.tensor([True, False, True])
        f = torch.tensor([[1., .27, .1, 0., .8, 1.2, .85, 0., 1.]]).repeat(3, 1)
        f[:, 0] -= t * .003
        f[:, 3] = torch.atan2(f[:, 2], f[:, 0])
        control = torch.full((3,), 1. + t * .02)
        sensor = control.clone()
        if t == 0:
            sensor[2] -= .25  # observed but stale start -> no anchor, no zero fill
        f[:, 7] = control - sensor
        f[1, :7] = 0.
        f[1, 8] = 0.
        floor = torch.tensor([.035, float('nan'), .045])
        T = torch.eye(4).repeat(3, 1, 1)
        T[:, :2, 3] = s[:, :2] + origins[:, :2]
        p = Producer271('SYNTHETIC_CPU_CURRENT_DEPTH263_PACKET_ONLY', 'own_MOD4_live_USD',
            'synthetic273', 'generation273', 'f' * 64, 'D435i_front_fixed', (2, 5, 8), (11, 19, 23))
        packet = CurrentDepthPacket271(p, 'packet273_' + str(t), found, f, floor, sensor,
            control, sensor.clone(), s[:, :13].clone(), origins.clone(), T, FRAME, 'native_wxyz')
        transition = dict(s=s, s1=s1, a=torch.zeros(3, 6), a_prev=torch.zeros(3, 6),
            xi=torch.cat((xi31, f), -1), r=torch.zeros(3), f=torch.zeros(3, dtype=torch.long),
            ep_step=torch.full((3,), t, dtype=torch.int32), done=torch.tensor([t == 9, False, False]))
        producer = dict(kind='SYNTHETIC_CPU_INTERFACE_ONLY', plant='own_MOD4_live_USD',
            run_id=p.run_id, generation=p.generation, source_admission_SHA=p.source_admission_SHA,
            state_schema=SCHEMA_ID, binding_witness_SHA=binding.witness_SHA,
            measured_fields=['own_L0_theta4', 'contact_forces_BODY31x3'],
            s_physics_end_tick=t * 8, s1_physics_end_tick=(t + 1) * 8)
        return transition, packet, producer

    for t in range(33):
        row, packet, producer = make_row(t)
        m.add(row, actual_anchor=packet, physics_end_tick=(t + 1) * 8, physics_us=2500,
            feedback_samples=2, producer=producer, synthetic_CPU_test=True)
        rows.append(row)
        packets.append(packet)
    assert m.ready_for_update()
    assert torch.isnan(m.anchors.data['visible_floor_z_m'][:33, 1]).all()
    assert not m.anchors.data['valid_anchor'][:33, 1].any()
    assert not m.anchors.data['valid_anchor'][0, 2] and torch.isnan(m.anchors.data['corners_world'][0, 2]).all()
    batch = m.sample()
    assert batch['supported_start_candidates'] == 3 and 'xi' not in batch
    assert all(r['environment_id'] in (2, 8) for r in batch['anchor']['scope_records'])
    assert len(batch['anchor']['scope_records']) == 4  # sampling with replacement, true IDs preserved
    groups.append(dict(name='complete_current_packet_replay_unknown_mask_uniform_supported_starts_true_scope',
        passed=True, synthetic_pairs=99, supported_start_candidates=3, sampled_true_scopes=batch['anchor']['scope_records']))

    loss0, prediction0, contexts0 = m.rollout_loss(batch, capture_context=True)
    # Starts may be at rows0 or1. Corrupt ONLY later replay packet/depth inputs;
    # measured physical targets/actions stay the original supervised labels.
    m.buffer.data['xi'][2:33, :, 31:].add_(1000.)
    for name in ('feature9', 'visible_floor_z_m', 'T_world_heading', 'sensor_pose_native13', 'corners_world'):
        m.anchors.data[name][2:33].add_(1000.)
    sampling_rng = m.generator.get_state().clone()
    # Capture this sample's exact starts again by using its already gathered
    # immutable first-anchor; no later record can replace it inside a rollout.
    loss1, prediction1, contexts1 = m.rollout_loss(batch, capture_context=True)
    assert torch.equal(contexts0, contexts1) and torch.equal(loss0, loss1)
    assert all(torch.equal(a, b) for a, b in zip(prediction0, prediction1))
    # Re-gather the original selected first slots, proving storage lookup also
    # sees only first packets after later packet corruption.
    slots = torch.tensor([r['slot'] for r in batch['anchor']['scope_records']])
    envs = torch.tensor([{2: 0, 8: 2}[r['environment_id']] for r in batch['anchor']['scope_records']])
    first_again = m.anchors.gather(slots, envs)
    state0 = m.measured_layout.unpack(batch['s'][:, 0])
    assert torch.equal(context_from_start_anchor273(first_again, state0, 0, m.native_geometry), contexts0[:, 0])
    assert torch.equal(sampling_rng, m.generator.get_state())
    # Check this NEW batching adapter against271's admitted one-env projection.
    for j, record in enumerate(batch['anchor']['scope_records']):
        env = int(envs[j])
        p = packets[record['slot']]
        sub = replace(p, producer=replace(p.producer, environment_ids=(record['environment_id'],),
            episode_ids=(record['episode_id'],)), **{k: getattr(p, k)[env:env+1] for k in (
                'found', 'feature9', 'visible_floor_z_m', 'sensor_time_s', 'control_time_s',
                'sensor_pose_time_s', 'sensor_pose_native13', 'environment_origins_world', 'T_world_heading')})
        anchor = make_anchor(sub, static31_raw=xi31[env:env+1], geometry=m.native_geometry, synthetic_CPU_test=True)
        current = tuple(v[j:j+1] for v in state0)
        expected = anchor.context40(current, producer=sub.producer, imagination_step=0, geometry=m.native_geometry)['context40_raw']
        assert torch.allclose(expected, contexts0[j:j+1, 0], atol=1e-6, rtol=1e-6)
    shifted = {**batch['anchor'], 'corners_world': batch['anchor']['corners_world'] + torch.tensor([.1, 0., 0.])}
    assert not torch.equal(context_from_start_anchor273(shifted, state0, 0, m.native_geometry), contexts0[:, 0])
    groups.append(dict(name='H32_forward_context_depends_only_on_first_anchor_predicted_state_not_future_depth',
        passed=True, future_context_and_loss_exactly_unchanged=True, first_anchor_matters=True,
        vectorized_scope_matches_admitted271=True, future_packet_rows_perturbed=31))

    expected_mask = torch.cumprod(torch.cat((torch.ones(4, 1), 1-batch['done'].float()[:, :-1]), -1), -1)
    assert torch.equal(batch['mask'], expected_mask)
    scale = torch.maximum(m.model.out_norm.std(), m.floor)
    error = (m.model.state_error(prediction0, m.measured_layout.unpack(batch['s1'])) / scale).square().mean(-1)
    assert torch.equal(loss0, (error * expected_mask).sum() / 4)
    for p in m.model.parameters():
        p.grad = None
    loss0.backward()
    assert all(p.grad is None or torch.isfinite(p.grad).all() for p in m.model.parameters())
    assert sum(float(p.grad.abs().sum()) for p in m.model.parameters() if p.grad is not None) > 0
    update = m.update()
    assert update['world_updates'] == 1 and update['actual_WM_updates'] == 0
    assert update['WM_optimizer_count'] == 1 and update['policy_updates'] == update['critic_updates'] == 0
    checkpoint = m.checkpoint()
    assert checkpoint['teacher_and_Pi_updates'] == 0 and checkpoint['complete_three_optimizer_conversion'] is False
    assert checkpoint['anchor_replay_saved'] is False and checkpoint['protocol']['WM_supervised_future_depth_input'] is False
    groups.append(dict(name='native_time_sum_loss_done_mask_finite_gradient_one_WM_Adam_step_checkpoint',
        passed=True, synthetic_update=update, real_teacher_or_Pi_updates=0))

    def reject(name, call):
        try:
            call()
        except (ValueError, TypeError):
            refused.append(name)
        else:
            raise AssertionError('Bad273 input accepted: ' + name)

    row, packet, producer = make_row(33)
    before = {k: v.clone() for k, v in m.model.state_dict().items()}
    bad_floor = packet.visible_floor_z_m.clone()
    bad_floor[0] = float('nan')
    def add(packet0=packet, producer0=producer):
        return m.add(row, actual_anchor=packet0, physics_end_tick=272, physics_us=2500,
            feedback_samples=2, producer=producer0, synthetic_CPU_test=True)
    reject('found_support_missing_floor', lambda: add(replace(packet, visible_floor_z_m=bad_floor)))
    reject('different_run_scope', lambda: add(replace(packet, producer=replace(packet.producer, run_id='another'))))
    reject('future_actual_packet', lambda: add(replace(packet, sensor_time_s=packet.control_time_s+.01)))
    validity = m.anchors.data['valid_anchor'].clone()
    m.anchors.data['valid_anchor'][:2].zero_()
    assert not m.ready_for_update()
    reject('no_real_supported_H32_start', m.sample)
    m.anchors.data['valid_anchor'].copy_(validity)
    assert m.controls == 33 and all(torch.equal(v, before[k]) for k, v in m.model.state_dict().items())
    assert torch.equal(rng, torch.get_rng_state()) and not torch.cuda.is_initialized()
    groups.append(dict(name='new_packet_missing_future_foreign_no_anchor_refusals_before_mutation',
        passed=True, rejections=refused))
    report = dict(passed=True, epoch=time.time(), purpose_ID=purpose['purpose_ID'], groups=groups,
        refusals=len(refused), synthetic_envs=3, synthetic_controls=33, pairs=99, synthetic_WM_updates=1,
        actual_Pi_WM_updates=0, old268_271_fixtures_replayed=0,
        model_raw_asset_reads=0, SDK_GPU_remote_Git_GO=0, CUDA_initialized=False,
        actual_current_packet_runtime_or_Pi_qualified=False)
except BaseException:
    report = dict(passed=False, epoch=time.time(), purpose_ID=purpose['purpose_ID'], groups=groups,
        error=traceback.format_exc(), scope='NEW273 synthetic source integration only; no actual model or physical case')
    raise
finally:
    with (R / 'ACTUAL273V2_NEW_FIRST_ANCHOR_H32_CPU_RETURNED.json').open('x', encoding='utf8') as f:
        json.dump(report, f, indent=2, allow_nan=False)
print(json.dumps(dict(passed=report['passed'], groups=len(groups), refusals=len(refused), synthetic_WM_updates=1,
                      actual_Pi_WM_updates=0)))
