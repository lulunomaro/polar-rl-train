"""NEW purpose: complete ONLY the V1 frozen-dataclass mutation-reader case."""
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
purpose = json.loads((R / 'FROZEN271V2_ONLY_UNFINISHED_CLONE_AGE_CPU_PURPOSE.json').read_bytes())
with (R / 'CONSUMED271V2_UNFINISHED_CLONE_AGE_CPU_ONCE.json').open('x', encoding='utf8') as f:
    json.dump(dict(epoch=time.time(), purpose_ID=purpose['purpose_ID'], old_fixture_replays=0), f)
try:
    for row in purpose['source_files']:
        assert hashlib.sha256(Path(row['path']).read_bytes()).hexdigest() == row['SHA']
    for p in N.glob('*.py'):
        ast.parse(p.read_text(encoding='utf8'))
    sys.path[:0] = [str(N), purpose['source255_directory'], purpose['native_source_directory']]
    import torch
    torch.set_num_threads(2)
    from native_depth_world_model50_v255 import load_native_kernels
    from observed_support_context271 import Producer271, CurrentDepthPacket271, make_anchor, FRAME
    geometry, _, _ = load_native_kernels(purpose['native_source_directory'])
    rng = torch.get_rng_state().clone()
    producer = Producer271('SYNTHETIC_CPU_CURRENT_DEPTH263_PACKET_ONLY', 'own_MOD4_live_USD',
        'synthetic271v2', 'synthetic271v2', 'c' * 64, 'D435i_front_fixed', (1, 6), (8, 12))
    root = torch.zeros(2, 13)
    root[:, 2] = .27
    root[:, 3] = 1.
    origins = torch.tensor([[3., 6., 0.], [9., 12., 0.]])
    T = torch.eye(4).repeat(2, 1, 1)
    T[:, :2, 3] = origins[:, :2]
    control = torch.full((2,), 10.)
    sensor = control - .2
    age = control - sensor
    feature9 = torch.tensor([[1., .27, .1, 0., .8, 1.2, .85, 0., 1.]]).repeat(2, 1)
    feature9[:, 3] = torch.atan2(feature9[:, 2], feature9[:, 0])
    feature9[:, 7] = age
    floor = torch.tensor([.035, .045])
    packet = CurrentDepthPacket271(producer, 'synthetic_packet271v2', torch.ones(2, dtype=torch.bool),
        feature9, floor, sensor, control, sensor.clone(), root, origins, T, FRAME, 'native_wxyz')
    static31 = torch.ones(2, 31)
    anchor = make_anchor(packet, static31_raw=static31, geometry=geometry, synthetic_CPU_test=True)
    state = (root[:, :3].clone(), torch.eye(3).repeat(2, 1, 1), torch.zeros(2, 3),
        torch.zeros(2, 3), torch.zeros(2, 30), torch.zeros(2, 30), torch.zeros(2, 151))

    def context(step=0):
        return anchor.context40(state, producer=producer, imagination_step=step, geometry=geometry)

    baseline = context()
    baseline_raw = baseline['context40_raw'].clone()
    baseline_corners = baseline['support_corners_world'].clone()
    final = context(32)
    assert torch.allclose(final['belief_age_seconds'], torch.full((2,), .84), atol=1e-6)
    assert final['metadata']['current_or_future_camera'] is False
    # Mutate the original buffer via its Tensor method; no assignment to a
    # frozen dataclass field. V1 += performed that forbidden assignment.
    packet.feature9[:, :7].add_(5.)
    packet.visible_floor_z_m.add_(5.)
    packet.environment_origins_world.add_(5.)
    packet.T_world_heading.add_(5.)
    static31.add_(3.)
    baseline['support_corners_world'].add_(5.)
    after = context()
    assert torch.equal(after['context40_raw'], baseline_raw)
    assert torch.equal(after['support_corners_world'], baseline_corners)
    assert torch.equal(rng, torch.get_rng_state()) and not torch.cuda.is_initialized()
    result = dict(passed=True, epoch=time.time(), purpose_ID=purpose['purpose_ID'],
        groups=[dict(name='V1_unfinished_only_clone_isolation_age_point84_RNG', passed=True)],
        synthetic_envs=2, source_module_changed=False, previous_four_groups_replayed=0,
        previous_23_rejections_replayed=0, old_once_replayed=0,
        real_model_raw_asset_reads=0, SDK_GPU_remote_Git=0, NN_models_constructed=0,
        actual_Pi_WM_updates=0, CUDA_initialized=False,
        limits='Only new synthetic completion proof; actual Pi context/runtime still pending')
except BaseException:
    result = dict(passed=False, epoch=time.time(), purpose_ID=purpose['purpose_ID'],
        error=traceback.format_exc(), original271_false_preserved=True)
    raise
finally:
    with (R / 'ACTUAL271V2_UNFINISHED_CLONE_AGE_CPU_RETURNED.json').open('x', encoding='utf8') as f:
        json.dump(result, f, indent=2, allow_nan=False)
print(json.dumps(dict(passed=result['passed'], new_completion_groups=1, old_fixture_replayed=0)))
