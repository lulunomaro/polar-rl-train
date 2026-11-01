"""NEW271 synthetic packet/pose context math only; no replay/model/data loads."""
from pathlib import Path
from dataclasses import replace
import os
os.environ['CUDA_VISIBLE_DEVICES'] = ''
import ast
import hashlib
import json
import math
import sys
import time
import traceback

N = Path(__file__).resolve().parent
R = N / 'reports'
purpose = json.loads((R / 'FROZEN271_NEW_STATIC_SUPPORT_CONTEXT_SYNTHETIC_CPU_PURPOSE.json').read_bytes())
with (R / 'CONSUMED271_NEW_STATIC_SUPPORT_CONTEXT_CPU_ONCE.json').open('x', encoding='utf8') as f:
    json.dump(dict(epoch=time.time(), purpose_ID=purpose['purpose_ID'], models_raw_assets_SDK_GPU_remote=0,
                   old_fixture_replays=0), f, indent=2)
groups, rejected = [], []
try:
    for row in purpose['source_files']:
        assert hashlib.sha256(Path(row['path']).read_bytes()).hexdigest() == row['SHA']
    for path in N.glob('*.py'):
        ast.parse(path.read_text(encoding='utf8'))
    sys.path[:0] = [str(N), purpose['source255_directory'], purpose['native_source_directory']]
    import torch
    torch.set_num_threads(2)
    from native_depth_world_model50_v255 import load_native_kernels, normalize_context40
    from observed_support_context271 import Producer271, CurrentDepthPacket271, make_anchor, FRAME
    geometry, _, _ = load_native_kernels(purpose['native_source_directory'])
    rng = torch.get_rng_state().clone()
    n = 2
    producer = Producer271('SYNTHETIC_CPU_CURRENT_DEPTH263_PACKET_ONLY', 'own_MOD4_live_USD',
        'synthetic271', 'synthetic_generation271', 'b' * 64, 'D435i_front_fixed', (2, 5), (11, 19))
    root = torch.zeros(n, 13)
    root[:, :3] = torch.tensor([[.3, .4, .27], [.5, -.1, .3]])
    root[:, 3] = 1.
    origins = torch.tensor([[3., 6., 0.], [9., 12., 0.]])
    T = torch.eye(4).repeat(n, 1, 1)
    T[:, :2, 3] = root[:, :2] + origins[:, :2]
    sensor = torch.tensor([9.95, 9.95])
    control = torch.tensor([10., 10.])
    age = control - sensor
    f = torch.tensor([[1., .27, .1, 0., .8, 1.2, .85, 0., 1.]]).repeat(n, 1)
    f[:, 3] = torch.atan2(f[:, 2], f[:, 0])
    f[:, 7] = age
    packet = CurrentDepthPacket271(producer, 'synthetic_current_packet271', torch.ones(n, dtype=torch.bool),
        f, torch.tensor([.035, .045]), sensor, control, sensor.clone(), root, origins, T, FRAME, 'native_wxyz')
    static31 = torch.tensor([1., .9] + [1.] * 6 + [0.] * 3 + [1.] * 10 +
                            [1.] * 2 + [1.] * 2 + [1.] * 2 + [0.] * 4).repeat(n, 1)

    def build(packet0=packet, static=static31, **kwargs):
        return make_anchor(packet0, static31_raw=static, geometry=geometry, synthetic_CPU_test=kwargs.get('synthetic', True))

    anchor = build()

    def state(position=None, yaw=None, aux_width=151):
        p = root[:, :3].clone() if position is None else position
        yaw = torch.zeros(n) if yaw is None else yaw
        zero, one = torch.zeros_like(yaw), torch.ones_like(yaw)
        c, s = torch.cos(yaw), torch.sin(yaw)
        rotation = torch.stack((c, -s, zero, s, c, zero, zero, zero, one), -1).reshape(n, 3, 3)
        return (p, rotation, torch.zeros(n, 3), torch.zeros(n, 3), torch.zeros(n, 30),
                torch.zeros(n, 30), torch.zeros(n, aux_width))

    def context(state0=None, step=0, producer0=producer, **kwargs):
        return anchor.context40(state() if state0 is None else state0, producer=producer0,
            imagination_step=step, geometry=geometry, **kwargs)

    initial = context()
    assert torch.allclose(initial['raw9'], f, atol=1e-6, rtol=1e-6)
    assert torch.equal(initial['context40_raw'][:, :31], static31)
    assert torch.allclose(initial['support_corners_world'][..., 2],
                          (packet.visible_floor_z_m + f[:, 1])[:, None].expand(n, 4), atol=1e-6)
    frozen_geometry = initial['support_corners_world'].clone()
    stationary = context(step=32)
    assert torch.allclose(stationary['raw9'][:, :7], initial['raw9'][:, :7], atol=1e-6)
    assert torch.allclose(stationary['raw9'][:, 7], age + .64, atol=1e-6)
    assert stationary['metadata']['current_or_future_camera'] is False
    assert stationary['metadata']['complete_footprint_certified'] is False
    assert stationary['metadata']['observed_range_lower_bound_only'] is True
    groups.append(dict(name='single_current_packet_world_rectangle_nonzero_floor_stationary_H32_belief_age',
        passed=True, observed_floor_not_default_zero=True, future_camera_claim=False))

    moved = root[:, :3].clone()
    moved[:, 0] += .2
    forward = context(state(moved), step=10)
    assert torch.allclose(forward['raw9'][:, 0], f[:, 0] - .2, atol=1e-6)
    assert torch.allclose(forward['raw9'][:, 2], f[:, 2], atol=1e-6)
    turned = context(state(yaw=torch.full((n,), math.pi / 2)), step=20)
    assert torch.allclose(turned['raw9'][:, 0], torch.full((n,), -.3), atol=2e-6)
    assert torch.allclose(turned['raw9'][:, 2], torch.full((n,), -1.6), atol=2e-6)
    assert torch.allclose(turned['raw9'][:, 4], f[:, 5], atol=2e-6)
    assert torch.allclose(turned['raw9'][:, 5], f[:, 4], atol=2e-6)
    assert torch.equal(turned['support_corners_world'], frozen_geometry)
    # Arbitrary root height does not change the measured floor-relative step.
    moved_z = moved.clone()
    moved_z[:, 2] += .5
    height_shift = context(state(moved_z), step=10)
    assert torch.allclose(height_shift['raw9'], forward['raw9'], atol=1e-6)
    raw = forward['context40_raw'].clone()
    normalized = normalize_context40(raw)
    assert torch.allclose(normalized[:, 31:], raw[:, 31:] / raw.new_tensor([4., .4, 2., math.pi, 2., 4., 1., .2, 1.]))
    assert torch.equal(forward['context40_raw'], raw)
    groups.append(dict(name='forward_yaw90_height_semantics_raw40_single_existing_normalization',
        passed=True, normalization_in_builder=0, future_depth_inputs=0))

    position = (root[:, :3] + torch.tensor([.12, -.08, 0.])).requires_grad_(True)
    yaw = torch.tensor([.23, -.31], requires_grad=True)
    differentiable = context(state(position, yaw), step=24)
    signal = (differentiable['raw9'][:, 0] + 2 * differentiable['raw9'][:, 2]
        + .3 * differentiable['raw9'][:, 3] + .7 * differentiable['raw9'][:, 4]
        + .4 * differentiable['raw9'][:, 5]).sum()
    grad_p, grad_yaw = torch.autograd.grad(signal, (position, yaw))
    assert torch.isfinite(grad_p).all() and torch.isfinite(grad_yaw).all()
    assert (grad_p[:, :2].abs().sum(-1) > 0).all() and (grad_yaw.abs() > 0).all()
    assert (grad_p[:, 2] == 0).all()  # Step height is floor-relative, not root clearance.
    groups.append(dict(name='native_predicted_XY_yaw_autograd_without_future_sensor_truth', passed=True,
        gradient_XY=grad_p[:, :2].tolist(), gradient_yaw=grad_yaw.tolist(),
        rootZ_gradient_not_claimed=True, actual_Pi_BPTT_updates=0))

    def reject(name, call):
        try:
            call()
        except (ValueError, TypeError):
            rejected.append(name)
        else:
            raise AssertionError('Invalid input accepted: ' + name)

    reject('missing_visible_floor', lambda: build(replace(packet, visible_floor_z_m=None)))
    reject('missing_sensor_pose', lambda: build(replace(packet, sensor_pose_native13=None)))
    reject('missing_actual_producer', lambda: build(replace(packet, producer=None)))
    reject('not_found', lambda: build(replace(packet, found=torch.zeros(n, dtype=torch.bool))))
    reject('future_actual_packet', lambda: build(replace(packet, sensor_time_s=control + .01)))
    reject('stale_actual_packet', lambda: build(replace(packet, sensor_time_s=control - .21)))
    reject('future_depth_packet_sequence', lambda: build([packet, packet]))
    reject('foreign_plant', lambda: build(replace(packet, producer=replace(producer, plant='foreign_plant'))))
    bad_T = T.clone()
    bad_T[:, 0, 3] += .5
    reject('transform_pose_origin_mismatch', lambda: build(replace(packet, T_world_heading=bad_T)))
    reject('SDK_xyzw_not_native_wxyz', lambda: build(replace(packet, pose_quaternion_order='xyzw')))
    reject('missing_actual_env_origin', lambda: build(replace(packet, environment_origins_world=None)))
    reject('future_feature_sequence', lambda: build(replace(packet, feature9=f[None])))
    reject('feature_age_disagrees', lambda: build(replace(packet, feature9=f + torch.tensor([0., 0., 0., 0., 0., 0., 0., .01, 0.]))))
    reject('sensor_pose_timestamp_mismatch', lambda: build(replace(packet, sensor_pose_time_s=sensor - .01)))
    reject('nonfinite_floor', lambda: build(replace(packet, visible_floor_z_m=torch.full((n,), float('nan')))))
    reject('different_run', lambda: context(producer0=replace(producer, run_id='another_run')))
    reject('different_generation', lambda: context(producer0=replace(producer, generation='another_generation')))
    reject('different_episode', lambda: context(producer0=replace(producer, episode_ids=(12, 19))))
    reject('future_depth_argument_forbidden', lambda: context(future_depth=f))
    reject('beyond_H32_scope', lambda: context(step=33))
    reject('legacy_aux54_is_not224_prediction', lambda: context(state(aux_width=54)))
    reject('missing_static31', lambda: build(static=None))
    reject('synthetic_packet_not_actual', lambda: build(synthetic=False))
    assert len(rejected) == 23
    groups.append(dict(name='missing_future_stale_foreign_scope_legacy_fields_rejected', passed=True,
        count=len(rejected), cases=rejected))

    # New admission at the largest fresh packet age; belief age may exceed.2.
    old_sensor = control - .2
    boundary_f = f.clone()
    boundary_f[:, 7] = control - old_sensor
    boundary_anchor = build(replace(packet, sensor_time_s=old_sensor,
        sensor_pose_time_s=old_sensor.clone(), feature9=boundary_f))
    boundary = boundary_anchor.context40(state(), producer=producer, imagination_step=32, geometry=geometry)
    assert torch.allclose(boundary['belief_age_seconds'], torch.full((n,), .84), atol=1e-6)
    initial_raw = initial['context40_raw'].clone()
    packet.feature9[:, :7] += 5.
    packet.visible_floor_z_m += 5.
    static31 += 3.
    after_mutation = context()
    assert torch.allclose(after_mutation['context40_raw'], initial_raw, atol=1e-6)
    initial['support_corners_world'] += 5.
    assert torch.equal(context()['support_corners_world'], frozen_geometry)
    assert torch.equal(rng, torch.get_rng_state()) and not torch.cuda.is_initialized()
    groups.append(dict(name='fresh_point2_admission_belief_point84_immutable_clones_private_RNG',
        passed=True, belief_age_is_not_camera_freshness=True, normalization_count=0))
    report = dict(passed=True, epoch=time.time(), purpose_ID=purpose['purpose_ID'], groups=groups,
        rejects=len(rejected), synthetic_envs=2, actual_controls=0, real_model_raw_asset_reads=0,
        SDK_GPU_remote_Git=0, old_fixtures_replayed=0, actual_Pi_WM_updates=0,
        actual_future_safe_Pi_runtime_qualified=False, actual267_floor_missing=True,
        CUDA_initialized=False, no_NN_model_constructed=True)
except BaseException:
    report = dict(passed=False, epoch=time.time(), purpose_ID=purpose['purpose_ID'],
        groups=groups, error=traceback.format_exc(), scope='New271 synthetic context source only; no actual physical/model failure')
    raise
finally:
    with (R / 'ACTUAL271_NEW_STATIC_SUPPORT_CONTEXT_CPU_RETURNED.json').open('x', encoding='utf8') as f:
        json.dump(report, f, indent=2, allow_nan=False)
print(json.dumps(dict(passed=report['passed'], groups=len(groups), rejects=len(rejected), actual_Pi_WM_updates=0)))
